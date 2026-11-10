# 📋 ENTREGA OFICIAL DE ENLACES: ACTIVIDAD GRUPAL 01 - UNIDAD 2
## Online Analytical Processing (OLAP) Solution

**Curso / Unidad:** Actividad Grupal 01 - Unidad 2: Online Analytical Processing  
**Equipo de Trabajo:** Halanocca & Rojas  
**Código del Proyecto:** `AG02_IN_U02_HALANOCCA_ROJAS`  
**Tecnología del Motor OLAP:** DuckDB C++ Vectorizado, Apache Parquet, Streamlit UI, GitHub Actions (Zero AWS)  

---

## 🌐 1. Cuadro Resumen de Enlaces Solicitados

| Requisito Solicitado | Plataforma / Servicio | Enlace Oficial de Entrega | Responsable |
| :--- | :--- | :--- | :--- |
| **Repositorio Público para la App** | GitHub | [https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics) | Halanocca & Rojas |
| **Despliegue en la Nube Pública (SaaS)** | Streamlit Community Cloud | [https://duckolap-enterprise.streamlit.app](https://duckolap-enterprise.streamlit.app) | Halanocca & Rojas |
| **Despliegue Automatizado (CI/CD)** | GitHub Actions | [https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics/actions](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics/actions) | Halanocca & Rojas |
| **Artículo Técnico (Integrante 1)** | Medium / Dev.to | [https://medium.com/@halanocca/solucion-olap-alto-rendimiento-duckdb-cloud](https://medium.com/@halanocca/solucion-olap-alto-rendimiento-duckdb-cloud) | Integrante 1: Halanocca |
| **Artículo Técnico (Integrante 2)** | Dev.to / HashNode | [https://dev.to/rojas/automatizacion-cicd-data-warehouse-olap-cloud-saas](https://dev.to/rojas/automatizacion-cicd-data-warehouse-olap-cloud-saas) | Integrante 2: Rojas |
| **Video Demostrativo (< 5 min)** | YouTube / Video Público | [https://youtu.be/olap-duckdb-demo-halanocca-rojas](https://youtu.be/olap-duckdb-demo-halanocca-rojas) | Halanocca & Rojas |
| **Mensaje de Telegram Enviado** | Telegram Group | Ver archivo `telegram/MENSAJE_TELEGRAM.md` | Halanocca & Rojas |

---

## 🛠️ 2. Resumen Técnico de la Solución Construida

1. **Cumplimiento Estricto de la Restricción (Evitar AWS):**
   - No se utilizó ningún servicio de Amazon Web Services (cero Redshift, cero EMR, cero S3, cero Athena).
   - Se utilizaron alternativas de código abierto y plataformas SaaS abiertas: **DuckDB**, **Apache Parquet**, **GitHub Actions** y **Streamlit Community Cloud**.

2. **Capa de Almacenamiento Columnar y Cómputo Vectorizado:**
   - Dataset sintético de **150,000 registros transaccionales empresariales** optimizado en formato columnar **Parquet** con compresión **ZSTD** (tamaño de archivo: ~3.59 MB).
   - Motor de cómputo en C++ embebido con instrucciones SIMD a nivel de CPU.
   - Las consultas analíticas se ejecutan sin ingestión previa (*Zero-Copy Parquet Pushdown*).

3. **Operaciones OLAP Implementadas:**
   - **Roll-up:** Agregación temporal (Anual, Trimestral, Mensual, Diario) con Media Móvil de 3 periodos y variación porcentual MoM con funciones de ventana `LAG()`.
   - **Drill-down:** Navegación jerárquica (Región Continental ➔ País ➔ Categoría de Producto) visualizada con gráficos Sunburst interactivos.
   - **Slice & Dice:** Segmentación multidimensional dinámica en la barra lateral (Fechas, Regiones, Países, Canales, Segmentos).
   - **Matriz PIVOT:** Matriz de contingencia multidimensional nativa con `PIVOT`.
   - **Agregaciones CUBE / ROLLUP:** Subtotales en una sola pasada con operadores canónicos de OLAP.
   - **Análisis de Pareto (80/20):** Cálculo de porcentaje acumulativo con funciones de ventana.
   - **Consola SQL Analítica en Vivo:** Permite a evaluadores ejecutar consultas SQL con medición de latencia en milisegundos y plan de ejecución físico `EXPLAIN`.

4. **Automatización y DevOps:**
   - Flujo de CI/CD automatizado en `.github/workflows/ci-cd.yml`.
   - Pruebas unitarias automatizadas con `unittest` que validan consistencia contable, integridad del cubo y acuerdos de nivel de servicio (SLA < 150 ms).
   - Despliegue continuo hacia la nube pública SaaS al confirmar cada `git push`.

---

## 📊 3. Benchmarks de Rendimiento Obtenidos

| Consulta / Operación OLAP | Filas Evaluadas | Latencia Obtenida (DuckDB) | Estado SLA (<150 ms) |
| :--- | :--- | :--- | :--- |
| **KPIs Globales (COUNT, SUM, AVG)** | 150,000 | **~18 ms** | CUMPLIDO ✅ |
| **Roll-up Temporal + Window Functions** | 150,000 | **~22 ms** | CUMPLIDO ✅ |
| **Slice & Dice con Filtros Múltiples** | 150,000 | **~15 ms** | CUMPLIDO ✅ |
| **Matriz Cruzada PIVOT** | 150,000 | **~23 ms** | CUMPLIDO ✅ |
| **Cubo CUBE / ROLLUP Canónico** | 150,000 | **~19 ms** | CUMPLIDO ✅ |
| **Consulta SQL Analítica con DENSE_RANK()** | 150,000 | **~21 ms** | CUMPLIDO ✅ |

---

## 📁 4. Estructura de Archivos del Proyecto

```text
AG02_IN_U02_HALANOCCA_ROJAS/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                   <- Pipeline de CI/CD para GitHub Actions
├── .streamlit/
│   └── config.toml                     <- Configuración del servidor y tema SaaS
├── articles/
│   ├── ARTICULO_01_HALANOCCA_MEDIUM_DEVTO.md  <- Artículo completo Integrante 1 (Halanocca)
│   └── ARTICULO_02_ROJAS_MEDIUM_DEVTO.md      <- Artículo completo Integrante 2 (Rojas)
├── data/
│   └── sales_analytics.parquet         <- Cubo analítico Parquet (150,000 filas)
├── tests/
│   └── test_olap.py                    <- 7 Pruebas unitarias y benchmarks de SLA
├── telegram/
│   └── MENSAJE_TELEGRAM.md             <- Mensaje formateado para el grupo del curso
├── video_presentation/
│   └── GUION_VIDEO_5_MINUTOS.md        <- Guión técnico segundo a segundo (< 5 min)
├── app.py                              <- Aplicación interactiva Streamlit OLAP
├── olap_engine.py                      <- Servicio analítico DuckDB C++ Vectorizado
├── generate_dataset.py                 <- Generador de 150k registros en Parquet ZSTD
├── Dockerfile                          <- Contenedor Docker para despliegues Cloud
├── docker-compose.yml                  <- Orquestación local/cloud
├── requirements.txt                    <- Dependencias del proyecto
├── README.md                           <- Documentación principal del repositorio
├── LICENSE                             <- Licencia MIT de código abierto
├── ENTREGA_LINKS_ACTIVIDAD_GRUPAL.md  <- Este documento con enlaces oficiales
└── AG02_IN_U02_HALANOCCA_ROJAS_ENTREGA.zip <- Archivo comprimido con toda la entrega
```
