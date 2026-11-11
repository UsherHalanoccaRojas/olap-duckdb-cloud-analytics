# Cómo Construir una Plataforma OLAP Sub-30ms en la Nube Pública con DuckDB, Apache Parquet y Streamlit (Sin AWS)

### Cómo diseñar un motor analítico multidimensional de 150,000 registros con ejecución vectorizada en C++, CI/CD en GitHub Actions y despliegue SaaS gratuito.

**Autores:** Halanocca, Yizuka & Gino  
**Etiquetas sugeridas en Medium:** `Data Engineering` · `DuckDB` · `OLAP` · `Python` · `Streamlit`

---

Cuando pensamos en **Online Analytical Processing (OLAP)** a escala, la respuesta automática suele ser levantar un clúster en la nube tradicional: Amazon Redshift, AWS EMR o Athena + S3. Sin embargo, para la gran mayoría de equipos de datos, startups y proyectos analíticos medianos, esa arquitectura introduce **costos mínimos fijos, tarifas de egreso, complejidad de IAM/VPC y latencias de red innecesarias**.

En este artículo te mostramos cómo construimos **DuckOLAP Enterprise**, una plataforma analítica multidimensional completa que procesa **150,000 transacciones comerciales** con latencias de **~15 a 25 milisegundos**, utilizando únicamente herramientas open source y nube pública SaaS (**Zero AWS**):

- **Motor de cómputo:** DuckDB (ejecución vectorizada en C++ con SIMD)
- **Almacenamiento columnar:** Apache Parquet comprimido con ZSTD
- **Capa visual e interactiva:** Streamlit + Plotly
- **CI/CD y despliegue continuo:** GitHub Actions + Streamlit Community Cloud + Docker

---

## 1. Por qué las bases OLTP sufren en analítica (y por qué DuckDB cambia las reglas)

Las bases transaccionales tradicionales (PostgreSQL, MySQL) almacenan datos **por filas**. Son excelentes para insertar o actualizar un pedido individual, pero cuando ejecutas una agregación analítica como:

```sql
SELECT region, category, SUM(net_revenue)
FROM sales_cube
GROUP BY region, category;
```

Un motor orientado a filas debe recorrer páginas completas leyendo columnas que no necesita (métodos de pago, fechas, métricas adicionales).

**DuckDB**, conocido como el *"SQLite para Analítica"*, invierte por completo este paradigma:

1. **Almacenamiento y lectura columnar:** Lee únicamente las columnas involucradas en la consulta (*Projection Pushdown*).
2. **Ejecución vectorizada (SIMD):** Procesa lotes de ~2,048 valores por ciclo de CPU en lugar de iterar fila por fila.
3. **Zero-Copy sobre Apache Parquet:** Consulta directamente archivos `.parquet` sin necesidad de un proceso ETL pesado para ingerir datos en otro servidor.

---

## 2. Arquitectura de la Solución (Zero AWS)

La solución sigue una arquitectura serverless desacoplada en cuatro capas:

```text
[ Capa de Almacenamiento Columnar ]
   Apache Parquet (Compresión ZSTD)
   └── 150,000 transacciones (~3.6 MB en disco)
          │
          ▼  Zero-Copy Parquet Pushdown
[ Motor de Cómputo OLAP Vectorizado ]
   DuckDB C++ Core Engine (In-Memory / MotherDuck SaaS)
   ├── Ejecución paralela multi-hilo (PRAGMA threads=4)
   └── Operadores: ROLLUP, PIVOT, WINDOW FUNCTIONS, EXPLAIN
          │
          ▼  Sub-30 ms
[ Capa de Presentación ]
   Streamlit + Plotly Interactive
   ├── Tablero Ejecutivo (KPIs en tiempo real)
   ├── Operaciones OLAP (Roll-up, Drill-down, Slice & Dice)
   ├── Matriz PIVOT, ROLLUP & Análisis Pareto (80/20)
   └── Consola SQL Analítica (solo lectura) + Plan EXPLAIN
          │
          ▲  Git Push
[ DataOps & CI/CD ]
   GitHub Actions ──▶ Tests unittest + SLA (<150 ms) ──▶ Streamlit Cloud
```

---

## 3. Generación del Cubo Analítico en Parquet con DuckDB

En lugar de usar `pandas` para generar y exportar el dataset (lo que consumiría mucha más memoria y tiempo), usamos directamente el motor SQL de DuckDB en `generate_dataset.py` para sintetizar 150,000 transacciones (años 2024–2025) y escribirlas comprimidas con **ZSTD**:

```python
con = duckdb.connect()
query = f"""
COPY (
    WITH base AS (
        SELECT
            i AS order_id,
            TIMESTAMP '2024-01-01 08:00:00'
                + INTERVAL ((i * 7) % 730) DAY AS order_timestamp,
            ...
        FROM range(1, {num_rows + 1}) t(i)
    )
    SELECT
        order_id,
        CAST(order_timestamp AS DATE) AS order_date,
        region,
        country,
        customer_segment,
        category,
        sales_channel,
        round(quantity * unit_price, 2) AS gross_sales,
        round(quantity * unit_price * discount_pct, 2) AS discount_amount,
        round(quantity * unit_price * (1 - discount_pct), 2) AS net_revenue,
        ...
    FROM base
) TO '{output_path}' (FORMAT PARQUET, COMPRESSION 'ZSTD');
"""
con.execute(query)
```

El resultado es un cubo analítico altamente comprimido de apenas **~3.6 MB** que se genera en menos de medio segundo y arranca al instante tanto en local como en contenedores Docker o Streamlit Cloud.

---

## 4. Implementando las Operaciones Canónicas de OLAP

Dentro de `olap_engine.py`, encapsulamos el motor en la clase `OLAPEngine`, exponiendo una vista `sales_cube` directamente sobre el archivo Parquet y validando dimensiones, métricas y consultas antes de ejecutarlas.

### 4.1. Roll-up Temporal con Window Functions

El **Roll-up** permite subir o bajar en la jerarquía temporal (`year`, `quarter`, `month`, `day`) y enriquecer la serie con media móvil de 3 periodos y variación porcentual respecto al periodo anterior usando `LAG()`:

```sql
WITH period_agg AS (
    SELECT
        DATE_TRUNC('month', order_date) AS period,
        COUNT(*) AS transactions,
        ROUND(SUM(net_revenue), 2) AS revenue,
        ROUND(SUM(net_profit), 2) AS profit
    FROM sales_cube
    GROUP BY 1
)
SELECT
    period,
    transactions,
    revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY period
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS revenue_moving_avg_3p,
    ROUND((revenue - LAG(revenue, 1) OVER (ORDER BY period)) /
        NULLIF(LAG(revenue, 1) OVER (ORDER BY period), 0) * 100, 2) AS mom_growth_pct
FROM period_agg
ORDER BY period ASC;
```

### 4.2. Drill-Down Jerárquico y Slice & Dice Seguro

Para el **Drill-down** navegamos desde la región continental hasta el país y la categoría de producto (`GROUP BY region, country, category`), alimentando un gráfico **Sunburst** interactivo en Plotly.

Para **Slice & Dice**, la barra lateral permite filtrar por rango de fechas, regiones, países, categorías, segmentos y canales. A nivel de backend, cada columna y métrica se valida contra listas blancas (`VALID_FILTER_COLS`, `VALID_DIMENSIONS`, `VALID_SLICE_METRICS`) y los literales se escapan adecuadamente para evitar inyección SQL.

### 4.3. Matriz PIVOT Nativa y Subtotales con ROLLUP

Una de las joyas sintácticas de DuckDB es su cláusula `PIVOT` nativa, que construye matrices cruzadas sin tener que encadenar decenas de `SUM(CASE WHEN ...)`:

```sql
PIVOT (
    SELECT category, region, net_revenue
    FROM sales_cube
)
ON region
USING ROUND(SUM(net_revenue), 2)
GROUP BY category
ORDER BY category ASC;
```

Además, combinamos esta vista con un cálculo canónico `GROUP BY ROLLUP (region, category)` usando `GROUPING()` para obtener subtotales regionales y el gran total global en una sola pasada sobre los datos, junto con un diagrama de **Pareto (80/20)** calculado con funciones de ventana acumulativas.

### 4.4. Consola SQL Analítica en Vivo con Plan Físico (`EXPLAIN`)

Para perfiles técnicos, incluimos una consola SQL interactiva protegida con validación de **solo lectura** (permitiendo `SELECT`, `WITH`, `PIVOT`, `EXPLAIN`, `DESCRIBE`, `SHOW` y bloqueando sentencias mutantes como `DROP`, `INSERT`, `COPY` o `ATTACH`).

Cada consulta muestra las filas resultantes, el tiempo exacto en milisegundos y el plan físico de ejecución generado por DuckDB (`READ_PARQUET` ➔ `HASH_GROUP_BY`), evidenciando cómo se ejecutan los operadores vectoriales.

---

## 5. DataOps: Pruebas Contables, SLA de Latencia y CI/CD

Un proyecto analítico no está completo sin pruebas automatizadas. En `tests/test_olap.py` validamos no solo el código, sino también **los datos y la latencia**:

- **Integridad contable:** Verifica que `total_revenue + total_discounts` coincida exactamente con `total_gross_sales`.
- **SLA de rendimiento:** Falla el pipeline si los KPIs globales superan los **150 ms** o si agregaciones complejas (`PIVOT`, `ROLLUP`, `Slice & Dice`) exceden los **200 ms**.
- **Consistencia de Pareto:** Confirma que el porcentaje acumulado converge al `100%`.
- **Seguridad y robustez:** Verifica que dimensiones inválidas y consultas destructivas lancen `ValueError`, y que filtros vacíos retornen `0` filas sin romper la interfaz.

Todo esto corre automáticamente en **GitHub Actions** (`.github/workflows/ci-cd.yml`) en cada `push` a `main`:

1. Configura Python 3.12 e instala dependencias.
2. Genera y verifica `data/sales_analytics.parquet`.
3. Ejecuta la suite `unittest` completa.
4. Sincroniza el despliegue continuo hacia **Streamlit Community Cloud** (y opcionalmente cualquier contenedor mediante el `Dockerfile` incluido).

---

## 6. Lecciones Aprendidas

1. **No necesitas un clúster distribuido para datos medianos:** Con formatos columnares modernos como Parquet y motores embebidos como DuckDB, cientos de miles (e incluso millones) de registros corren en milisegundos dentro de una instancia gratuita SaaS.
2. **Validar latencia en CI/CD evita regresiones silenciosas:** Tratar el tiempo de respuesta SQL como una aserción de test unitario mantiene el dashboard ágil conforme evoluciona el código.
3. **Arquitectura portable:** Gracias a `Dockerfile` y `docker-compose.yml`, la misma aplicación corre idéntica en local, en Streamlit Cloud o en Render/Fly.io, sin atarse a ningún proveedor cloud.

---

## 🔗 Repositorio del Proyecto

Puedes explorar el código fuente completo, la suite de pruebas, el pipeline de GitHub Actions y las instrucciones de despliegue en el repositorio oficial:

- **GitHub:** `olap-duckdb-cloud-analytics`

Si te resultó útil esta arquitectura Zero-AWS con DuckDB y Streamlit, ¡déjanos un aplauso en Medium y cuéntanos en los comentarios qué casos de uso analíticos estás resolviendo con motores columnares embebidos!

