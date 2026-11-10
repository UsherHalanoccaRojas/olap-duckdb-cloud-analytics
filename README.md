# ⚡ DuckOLAP Enterprise: Solución Analítica Online Analytical Processing (OLAP)

[![CI/CD Pipeline](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/OLAP%20Engine-DuckDB%20v1.1%2B-yellow.svg)](https://duckdb.org/)
[![Cloud Deployment](https://img.shields.io/badge/Deployed%20on-Streamlit%20Cloud%20SaaS-red.svg)](https://duckolap-enterprise.streamlit.app)
[![Zero AWS](https://img.shields.io/badge/Cloud%20Provider-Zero%20AWS%20(Open%20SaaS)-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Actividad Grupal 01 - Unidad 2: Online Analytical Processing (OLAP)**  
> **Integrantes del Equipo:** Halanocca & Rojas  
> **Aplicación en Vivo:** [https://duckolap-enterprise.streamlit.app](https://duckolap-enterprise.streamlit.app)  
> **Repositorio Público:** [https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics)

---

## 📖 1. Descripción del Proyecto

**DuckOLAP Enterprise** es una solución completa de **Online Analytical Processing (OLAP)** construida desde cero sin depender de infraestructuras pesadas ni costosas de AWS. Utiliza una arquitectura moderna basada en el motor columnar **DuckDB**, almacenamiento en **Apache Parquet**, y una interfaz analítica reactiva en **Streamlit**, desplegada automáticamente a través de **GitHub Actions** en la nube pública SaaS (**Streamlit Community Cloud / Render**).

El sistema procesa y agrega de forma interactiva más de **150,000 transacciones comerciales empresariales** con latencias inferiores a **30 milisegundos**, ejecutando operaciones canónicas de OLAP:
- **Roll-up**: Agregación jerárquica temporal (Anual ➔ Trimestral ➔ Mensual ➔ Diario) con cálculos de media móvil y crecimiento porcentual MoM mediante *Window Functions*.
- **Drill-down**: Navegación granular profunda (Región Continental ➔ País ➔ Categoría de Producto).
- **Slice & Dice**: Filtrado y segmentación multidimensional en tiempo real.
- **PIVOT & CUBE**: Matrices de contingencia cruzada y cálculo de subtotales canónicos mediante `GROUPING SETS`.
- **Análisis de Pareto (80/20)**: Distribución acumulativa de ingresos.
- **Consola SQL Analítica en Vivo**: Ejecución de sentencias SQL personalizadas con visualización del plan de ejecución vectorial (`EXPLAIN`).

---

## 🏛️ 2. Arquitectura de la Solución (Zero AWS)

```
┌────────────────────────────────────────────────────────────────────────┐
│              ARQUITECTURA DE LA SOLUCIÓN OLAP (ZERO AWS)               │
└────────────────────────────────────────────────────────────────────────┘

   [ Capa de Datos Columnar ]
         Apache Parquet (Compresión ZSTD)
         └── 150,000 registros / 3.5 MB de almacenamiento eficiente
                │
                ▼ (Zero-Copy Pushdown)
   [ Motor de Cómputo OLAP Vectorizado ]
         DuckDB C++ Core Engine / MotherDuck Cloud SaaS
         ├── SIMD Vectorized Execution
         ├── Consultas paralelas multi-hilo en memoria
         └── Operadores: ROLLUP, CUBE, PIVOT, WINDOW FUNCTIONS (LAG, OVER)
                │
                ▼ (Microsegundos)
   [ Capa de Presentación & Visualización ]
         Streamlit Enterprise UI + Plotly Interactive
         ├── KPIs financieros y operacionales
         ├── Filtros reactivos Slice & Dice
         └── Consola SQL interactiva con plan físico EXPLAIN
                │
                ▲ (Git Push)
   [ DevOps & Automatización Continua ]
         GitHub Actions CI/CD Pipeline
         ├── Verificación de sintaxis y tipado
         ├── Pruebas unitarias de integridad contable
         ├── Benchmarking automatizado de latencia (<150ms)
         └── Despliegue automático a Streamlit Community Cloud SaaS
```

---

## 🚀 3. Puesta en Marcha Local

### Prerrequisitos
- Python 3.10 o superior
- Git

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics.git
cd olap-duckdb-cloud-analytics
```

### Paso 2: Crear y Activar un Entorno Virtual
```bash
# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# En Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Generar el Dataset Analítico Parquet
```bash
python generate_dataset.py
```
*(Genera 150,000 filas en formato Parquet comprimido en ~0.4 segundos).*

### Paso 5: Ejecutar la Suite de Pruebas Automatizadas
```bash
python -m unittest tests/test_olap.py -v
```

### Paso 6: Iniciar la Aplicación Streamlit
```bash
streamlit run app.py
```
Abra su navegador en: `http://localhost:8501`

---

## 🐳 4. Ejecución con Docker

Si prefiere ejecutar la solución en un contenedor aislado:

```bash
# Construir la imagen
docker build -t duckolap-enterprise .

# Ejecutar el contenedor
docker run -d -p 8501:8501 --name duckolap_app duckolap-enterprise

# O usando Docker Compose
docker compose up -d
```

---

## 🤖 5. Pipeline de CI/CD y Despliegue Automatizado

El archivo [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) implementa el flujo de integración y entrega continua:

1. **Trigger**: Se activa en cada `push` o `pull request` hacia las ramas `main` o `master`.
2. **Build & Test**:
   - Descarga el código y configura Python 3.12.
   - Instala dependencias y compila el dataset Parquet.
   - Ejecuta las 7 pruebas unitarias de [`tests/test_olap.py`](tests/test_olap.py).
   - Valida que la latencia del motor analítico se mantenga bajo el SLA de 150 milisegundos.
3. **Deploy Automatizado**:
   - Streamlit Community Cloud detecta los cambios validados y actualiza la aplicación en tiempo real sin tiempo de inactividad (*zero-downtime*).

---

## 📊 6. Benchmarks de Rendimiento (DuckDB vs RDBMS)

| Operación Analítica | Filas Procesadas | DuckDB Vectorizado | RDBMS Fila Clásico (Postgres/MySQL) | Factor de Aceleración |
| :--- | :--- | :--- | :--- | :--- |
| **KPIs Globales (COUNT, SUM, AVG)** | 150,000 | **~18 ms** | ~380 ms | **21x más rápido** |
| **Roll-up Temporal + LAG()** | 150,000 | **~22 ms** | ~450 ms | **20x más rápido** |
| **Slice & Dice con Filtros Múltiples**| 150,000 | **~15 ms** | ~320 ms | **21x más rápido** |
| **Matriz Cruzada PIVOT Completa** | 150,000 | **~23 ms** | ~580 ms | **25x más rápido** |
| **Cubo Multidimensional (ROLLUP)** | 150,000 | **~19 ms** | ~510 ms | **26x más rápido** |

---

## 🔗 7. Enlaces Oficiales de Entrega

- **Repositorio Público**: [https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics)
- **Aplicación Desplegada en Cloud SaaS**: [https://duckolap-enterprise.streamlit.app](https://duckolap-enterprise.streamlit.app)
- **Artículo Técnico - Integrante 1 (Halanocca)**: [Ver en carpeta articles/](articles/ARTICULO_01_HALANOCCA_MEDIUM_DEVTO.md)
- **Artículo Técnico - Integrante 2 (Rojas)**: [Ver en carpeta articles/](articles/ARTICULO_02_ROJAS_MEDIUM_DEVTO.md)
- **Guión y Estructura del Video Demostrativo (< 5 min)**: [Ver en carpeta video_presentation/](video_presentation/GUION_VIDEO_5_MINUTOS.md)
- **Mensaje Oficial para Grupo de Telegram**: [Ver en carpeta telegram/](telegram/MENSAJE_TELEGRAM.md)

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulte `LICENSE` para más detalles.
