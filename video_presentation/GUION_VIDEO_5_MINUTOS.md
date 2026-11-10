# 🎬 Guión Técnico y Storyboard del Video Demostrativo (< 5 Minutos)

**Proyecto:** DuckOLAP Enterprise - Solución OLAP con DuckDB y Streamlit (Zero AWS)  
**Actividad:** Actividad Grupal 01 - Unidad 2: Online Analytical Processing  
**Integrantes:** Halanocca & Rojas  
**Duración Total Estimada:** 4 minutos y 35 segundos (Límite máximo permitido: 5:00 minutos)  
**Plataforma de Publicación:** YouTube / LinkedIn / Facebook / TikTok  

---

## ⏱️ Estructura y Cronograma Segundo a Segundo

| Intervalo | Tiempo | Escena / Pantalla | Orador | Objetivo Principal |
| :--- | :--- | :--- | :--- | :--- |
| **0:00 - 0:35** | 35 seg | Diapositiva de Portada + Repositorio GitHub | Halanocca | Introducción, presentación del equipo y problema OLAP (Zero AWS). |
| **0:35 - 1:20** | 45 seg | Arquitectura Técnica + Archivo Parquet | Rojas | Explicación de la arquitectura: Parquet, DuckDB C++ y Streamlit SaaS. |
| **1:20 - 2:30** | 70 seg | Aplicación en Vivo: Tablero Ejecutivo y Slice & Dice | Halanocca | Demostración de KPIs, latencias de 18ms y filtros multidimensionales. |
| **2:30 - 3:30** | 60 seg | Aplicación en Vivo: Roll-up, Drill-down, Pivot y SQL | Rojas | Demostración de operaciones canónicas OLAP y consola SQL interactiva. |
| **3:30 - 4:15** | 45 seg | Terminal + GitHub Actions CI/CD | Halanocca & Rojas | Ejecución de tests automatizados, pipeline verde y despliegue continuo. |
| **4:15 - 4:35** | 20 seg | Pantalla Final con Enlaces y Artículos | Ambos | Conclusiones, artículos técnicos y despedida. |

---

## 🎙️ Guión Detallado y Acciones en Pantalla

### 🟢 Bloque 1: Introducción y Planteamiento del Reto (0:00 - 0:35)
- **Visual:** Grabación de pantalla completa. Se muestra el repositorio público en GitHub (`https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics`) con el archivo `README.md` y los badges de CI/CD.
- **Narración (Halanocca):**
  > *"¡Hola a todos! Bienvenidos a la presentación de nuestra solución para la Actividad Grupal 01 de la Unidad 2 sobre Procesamiento Analítico en Línea (OLAP). Somos el equipo conformado por Halanocca y Rojas.*  
  > *El objetivo de este proyecto fue diseñar e implementar una plataforma OLAP moderna, de alto rendimiento y capaz de procesar cientos de miles de transacciones analíticas en milisegundos, cumpliendo una regla de oro fundamental: **cero dependencias de AWS**.*  
  > *Acompáñennos a ver la arquitectura, la automatización y la aplicación funcionando en vivo."*

---

### 🟢 Bloque 2: Arquitectura de la Solución (Zero AWS) (0:35 - 1:20)
- **Visual:** Cambiar a la pestaña de Arquitectura o mostrar el diagrama conceptual de flujo de datos.
- **Narración (Rojas):**
  > *"Para lograr un rendimiento analítico de vanguardia sin pagar infraestructuras costosas en AWS, construimos una arquitectura basada en tres pilares:*  
  > *Primero: **Apache Parquet**, un formato columnar comprimido con ZSTD que reduce 150,000 registros transaccionales a tan solo 3.5 megabytes.*  
  > *Segundo: **DuckDB**, el motor analítico embebido escrito en C++ que ejecuta procesamiento vectorial con instrucciones SIMD a nivel de CPU. DuckDB lee directamente los archivos Parquet sin ingestión previa gracias a técnicas de Zero-Copy y Predicate Pushdown.*  
  > *Tercero: **Streamlit Community Cloud**, un proveedor SaaS público que aloja nuestra interfaz reactiva con despliegue continuo automatizado desde GitHub."*

---

### 🟢 Bloque 3: Demostración en Vivo - Tablero Ejecutivo y Slice & Dice (1:20 - 2:30)
- **Visual:** Mostrar la aplicación en producción en el navegador (`https://duckolap-enterprise.streamlit.app`). Pestaña **"Tablero Ejecutivo (KPIs)"**.
- **Acciones:**
  1. Señalar las tarjetas de métricas: Ingresos Netos ($3.6B), Utilidad Neta ($1.2B) y Transacciones (150,000).
  2. Destacar la insignia de latencia: **⚡ 18 ms**.
  3. Desplegar la barra lateral izquierda y modificar los filtros: desmarcar algunas regiones y cambiar categorías.
- **Narración (Halanocca):**
  > *"Aquí tenemos la aplicación en producción. En el Tablero Ejecutivo vemos los indicadores principales calculados al instante: más de 3,600 millones en ingresos y 150,000 transacciones.*  
  > *Observen la etiqueta de latencia: ¡apenas 18 milisegundos para consolidar todo el cubo!*  
  > *Ahora aplicamos la operación **Slice & Dice**: filtramos únicamente la región de Latinoamérica y el segmento Corporativo. Al instante, DuckDB recomputa las métricas y los gráficos de evolución temporal y distribución por canal se actualizan sin retraso alguno."*

---

### 🟢 Bloque 4: Operaciones OLAP Avanzadas y Consola SQL (2:30 - 3:30)
- **Visual:** Navegar a las pestañas **"Operaciones OLAP"**, **"Matriz PIVOT"** y **"Consola SQL"**.
- **Acciones:**
  1. Cambiar el selector de Roll-up de 'Mensual' a 'Trimestral' y 'Anual'. Mostrar el gráfico de Media Móvil y % MoM.
  2. Mostrar el gráfico Sunburst interactivo para el Drill-Down (Región ➔ País ➔ Categoría).
  3. Ir a la Consola SQL, seleccionar la consulta con `DENSE_RANK() OVER (PARTITION BY region)` y hacer clic en **"Ejecutar Consulta"**.
  4. Abrir el desplegable del plan físico `EXPLAIN`.
- **Narración (Rojas):**
  > *"En la pestaña de Operaciones OLAP demostramos el **Roll-up temporal**, donde agregamos a nivel anual, trimestral o mensual aplicando funciones de ventana con `LAG()` para calcular tasas de crecimiento intermensual.*  
  > *En el **Drill-down**, exploramos la jerarquía desde el continente hasta el país y la categoría mediante este gráfico Sunburst interactivo.*  
  > *Además, contamos con una **Matriz PIVOT** multidimensional y cálculo de subtotales con `ROLLUP`.*  
  > *Finalmente, en la Consola SQL interactiva, ejecutamos consultas analíticas complejas como el Top 3 de productos más rentables con `DENSE_RANK()`. Observen: resultado devuelto en 21 milisegundos y con el plan físico de ejecución vectorial disponible al usuario."*

---

### 🟢 Bloque 5: CI/CD, Tests Automatizados y Despliegue (3:30 - 4:15)
- **Visual:** Dividir pantalla o mostrar la pestaña de GitHub Actions en el repositorio web (`Actions`), mostrando los flujos de trabajo en color verde (Passing). Luego abrir una terminal y ejecutar las pruebas unitarias.
- **Acciones:**
  1. En la terminal ejecutar: `python -m unittest tests/test_olap.py -v`.
  2. Ver la salida con los 7 tests en estado `OK` (0.18s).
  3. Mostrar el archivo `.github/workflows/ci-cd.yml`.
- **Narración (Halanocca & Rojas):**
  > *(Halanocca): "La excelencia de este proyecto radica también en su ingeniería DevOps. En la terminal ejecutamos nuestra suite de pruebas unitarias con `unittest`... ¡7 pruebas aprobadas en 0.18 segundos! Verificamos consistencia contable, integridad del cubo y latencia máxima.*  
  > *(Rojas): Y en GitHub Actions, cada `git push` activa nuestro pipeline automatizado de CI/CD: instala dependencias, valida el dataset, ejecuta los tests de regresión y dispara la sincronización continua hacia Streamlit Community Cloud."*

---

### 🟢 Bloque 6: Conclusiones y Despedida (4:15 - 4:35)
- **Visual:** Mostrar la diapositiva final o la pestaña de Arquitectura con la tabla de enlaces oficiales y los dos artículos de Medium/Dev.to.
- **Narración (Ambos):**
  > *"En conclusión, hemos demostrado que es totalmente posible construir una solución OLAP de clase empresarial, rápida, automatizada y escalable sin incurrir en costos ni depender de AWS.*  
  > *Los enlaces al repositorio público, a la aplicación en vivo y a los dos artículos técnicos publicados por cada uno de nosotros se encuentran en la descripción del video y en nuestro archivo de entrega.*  
  > *¡Muchas gracias por su atención!"*

---

## 📋 Ficha de Metadatos para Publicación en YouTube / Redes

- **Título Sugerido:**  
  `Construcción de una Solución OLAP con DuckDB, Streamlit y CI/CD en la Nube Pública (Zero AWS) | Halanocca & Rojas`
- **Descripción:**
  ```text
  Presentación de la Solución Analítica Multidimensional (OLAP) para la Actividad Grupal 01 - Unidad 2.
  Integrantes: Halanocca & Rojas
  
  🔗 Enlaces del Proyecto:
  • Repositorio Público en GitHub: https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics
  • Aplicación Desplegada en Vivo (Streamlit SaaS): https://duckolap-enterprise.streamlit.app
  • Artículo Técnico 1 (Halanocca - DuckDB & Arquitectura OLAP): https://medium.com/@halanocca/solucion-olap-alto-rendimiento-duckdb-cloud
  • Artículo Técnico 2 (Rojas - CI/CD & Despliegue Cloud SaaS): https://dev.to/rojas/automatizacion-cicd-data-warehouse-olap-cloud-saas
  
  ⏱️ Marcas de Tiempo:
  0:00 Introducción y Reto OLAP (Zero AWS)
  0:35 Arquitectura del Sistema (Parquet + DuckDB + SaaS)
  1:20 Demostración: Tablero Ejecutivo y Slice & Dice (18ms)
  2:30 Operaciones OLAP: Roll-up, Drill-down, Pivot y SQL
  3:30 Automatización con GitHub Actions y Tests Unitarios
  4:15 Conclusiones y Enlaces Oficiales
  
  #DataEngineering #DuckDB #OLAP #Streamlit #CICD #Python #BigData
  ```
- **Hashtags:** `#OLAP #DuckDB #BigData #Streamlit #CloudAnalytics #DataEngineering #Python`
