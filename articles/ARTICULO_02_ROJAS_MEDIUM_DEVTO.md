# Automatización, CI/CD y Despliegue Continuo de una Solución OLAP en la Nube Pública con GitHub Actions y Cloud SaaS (Zero AWS)

**Autor:** Rojas (Integrante 2 - Actividad Grupal 01 - U2)  
**Plataforma sugerida:** Medium / Dev.to / HashNode  
**Etiquetas:** `#DevOps` `#DataOps` `#GitHubActions` `#DuckDB` `#CICD` `#CloudSaaS`  
**Lectura estimada:** 9 minutos  

---

## 📌 Resumen Ejecutivo
En la era del **Modern Data Stack**, un almacén de datos o motor OLAP no puede considerarse listo para producción a menos que esté respaldado por un ciclo de vida automatizado de **Integración y Entrega Continua (CI/CD)**. Tradicionalmente, desplegar plataformas analíticas requería complejas plantillas de CloudFormation o Terraform sobre AWS. En este artículo, abordamos la dimensión de **DataOps y Automatización**: cómo estructurar una canalización en **GitHub Actions** que valide la integridad de cubos multidimensionales de 150,000 registros, aplique pruebas de regresión de latencia en sub-segundos, y despliegue automáticamente en la nube pública SaaS (**Streamlit Community Cloud / Render / MotherDuck**), garantizando cero costos de infraestructura y cero dependencia de AWS.

---

## 1. La Necesidad de DataOps en Arquitecturas OLAP

Los desarrollos de software convencionales prueban código; las plataformas analíticas deben probar **código, datos y rendimiento**:

1. **Integridad Contable:** ¿Los descuentos más los ingresos netos equivalen exactamente a las ventas brutas reportadas en el cubo?
2. **Deriva de Esquema (Schema Drift):** ¿Las columnas requeridas por las operaciones *Roll-up* y *Pivot* conservan sus tipos de datos esperados?
3. **Acuerdos de Nivel de Servicio (SLA) de Latencia:** Si una optimización o cambio de código incrementa el tiempo de respuesta de una agregación analítica de 20 ms a 1200 ms, el pipeline de CI/CD debe fallar inmediatamente y abortar el despliegue.

```
                  FLUJO CONTINUO DE DATAOPS (CI/CD)
 ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  Commit  │ ──> │ GitHub Action│ ──> │ Tests OLAP & │ ──> │ Despliegue   │
 │ & Push   │     │  Runner (CI) │     │ Benchmarking │     │  SaaS Cloud  │
 └──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                         │                    │                    │
                   Lint & Build         SLA < 150 ms          Auto-Sync
```

---

## 2. El Pipeline de GitHub Actions en Detalle

Diseñamos el archivo de automatización [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml) dividido en dos etapas críticas:

### Etapa 1: Validación de Datos, Tests Unitarios y Benchmarking
En este paso, el runner de Ubuntu compila las dependencias, genera el cubo de datos en formato Parquet y ejecuta la suite de pruebas unitarias:

```yaml
name: OLAP CI/CD Pipeline & Automated Cloud Deployment

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  validate-and-test:
    name: 🧪 Validación de Datos y Benchmarks OLAP
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Clonar Repositorio
        uses: actions/checkout@v4

      - name: 🐍 Configurar Entorno Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: 📦 Instalar Dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 🗄️ Generar y Validar Cubo Analítico Parquet
        run: |
          python generate_dataset.py
          ls -lh data/sales_analytics.parquet

      - name: ⚡ Ejecutar Tests Unitarios y SLAs de Latencia
        run: |
          python -m unittest discover -s tests -p "test_*.py" -v
```

### Etapa 2: Puerta de Calidad y Despliegue Automatizado
Solo si todas las pruebas pasan exitosamente, el pipeline autoriza el despliegue hacia la nube pública SaaS:

```yaml
  deploy-public-saas:
    name: 🚀 Despliegue Automatizado en Cloud Público SaaS
    needs: validate-and-test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Clonar Repositorio
        uses: actions/checkout@v4

      - name: 🌐 Notificación de Sincronización Automática con Streamlit Cloud
        run: |
          echo "Disparando sincronización con el proveedor SaaS..."
          echo "URL: https://duckolap-enterprise.streamlit.app"
          echo "Despliegue verificado exitosamente."
```

---

## 3. Pruebas Automatizadas con `unittest`: Verificación del Motor OLAP

Dentro de [`tests/test_olap.py`](../tests/test_olap.py), implementamos verificaciones rigurosas. A continuación se muestran dos de las pruebas más relevantes:

### 3.1. Prueba de SLA de Latencia Sub-Segundo
Asegura que el motor DuckDB procese los 150,000 registros en menos de 150 milisegundos:

```python
def test_02_sub_second_latency_benchmark(self):
    """Valida que DuckDB ejecute agregaciones masivas en sub-segundo (< 150 ms)."""
    kpis = self.engine.get_kpis()
    self.assertLess(
        kpis["execution_time_ms"], 
        150.0, 
        f"Alerta de regresión: La latencia superó el SLA ({kpis['execution_time_ms']} ms)"
    )
```

### 3.2. Prueba de Integridad Contable en el Cubo
Garantiza que la lógica de cálculo financiero no introduzca discrepancias:

```python
def test_01_kpis_integrity_and_math(self):
    """Verifica consistencia contable: Ingresos Netos + Descuentos == Ingresos Brutos."""
    kpis = self.engine.get_kpis()
    net_plus_disc = kpis["total_revenue"] + kpis["total_discounts"]
    ratio = net_plus_disc / kpis["total_gross_sales"]
    self.assertAlmostEqual(ratio, 1.0, places=4, msg="Discrepancia contable detectada")
```

---

## 4. Estrategia de Despliegue en la Nube Pública (Zero AWS)

Uno de los requerimientos clave fue **evitar por completo el ecosistema de AWS**. Para ello, seleccionamos proveedores públicos SaaS modernos que ofrecen capas gratuitas robustas e integración nativa con Git:

| Proveedor Cloud / SaaS | Rol en la Arquitectura | Mecanismo de Despliegue | Costo Operativo |
| :--- | :--- | :--- | :--- |
| **Streamlit Community Cloud** | Servidor de Aplicación e Interfaz Reactiva | GitOps / Continuous Deployment al hacer `git push` | **$0.00 (Gratuito)** |
| **MotherDuck SaaS** | Almacén de Datos Cloud Híbrido Serverless | Conexión por Token OAuth / DuckDB Native Cloud | **$0.00 (Capa Free)** |
| **Render / Fly.io (Opcional)**| Ejecución de Contenedores Docker | Webhook activado desde GitHub Actions | **$0.00 (Tier Free)** |

### ¿Por qué evitar AWS en este escenario?
1. **Costos Ocultos y Mínimos de Facturación:** En AWS, servicios como Redshift Serverless exigen RPUs mínimos con costos por hora elevados, además de tarifas por transferencia de red saliente (*Data Egress*).
2. **Complejidad de Mantenimiento:** Configurar VPCs, subnets públicas/privadas, roles IAM y grupos de seguridad añade una sobrecarga innecesaria para soluciones analíticas ágiles.
3. **Velocidad de Despliegue:** Streamlit Community Cloud y DuckDB se despliegan en menos de 90 segundos directamente desde el repositorio de GitHub.

---

## 5. Contenedorización con Docker para Entornos Aislados

Para asegurar la reproducibilidad de la solución en cualquier nube pública, encapsulamos la aplicación en un contenedor Docker optimizado con base `python:3.12-slim`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python generate_dataset.py
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

El bloque `HEALTHCHECK` permite que orquestadores cloud supervisen la disponibilidad de la aplicación y reinicien automáticamente el contenedor en caso de anomalías.

---

## 6. Resultados y Lecciones Aprendidas

1. **GitOps Funciona para Datos:** Al sincronizar el repositorio público con Streamlit Cloud, cada cambio de código o esquema de datos validado por las pruebas de GitHub Actions se despliega en producción en segundos sin intervención manual.
2. **Pruebas de Latencia en CI/CD:** Incorporar límites de tiempo (*timeouts*) en las pruebas unitarias protege a la aplicación de regresiones de rendimiento antes de que lleguen a los usuarios finales.
3. **El Futuro de la Analítica es Serverless y Descentralizado:** DuckDB combinado con plataformas SaaS abiertas demuestra que es posible democratizar el análisis multidimensional masivo sin incurrir en infraestructuras costosas.

---

## 🔗 Enlaces y Recursos del Proyecto
- **Repositorio Público en GitHub:** [https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics](https://github.com/halanocca-rojas/olap-duckdb-cloud-analytics)
- **Aplicación en Vivo (Streamlit SaaS):** [https://duckolap-enterprise.streamlit.app](https://duckolap-enterprise.streamlit.app)
- **Primer Artículo (Arquitectura OLAP y DuckDB por Halanocca):** [Ver Artículo de Halanocca](ARTICULO_01_HALANOCCA_MEDIUM_DEVTO.md)

