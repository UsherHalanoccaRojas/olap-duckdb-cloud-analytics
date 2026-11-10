# Dockerfile para DuckOLAP Enterprise (Producción Cloud SaaS)
FROM python:3.12-slim

# Metadatos del contenedor
LABEL maintainer="Equipo Halanocca & Rojas"
LABEL description="Solución OLAP con DuckDB y Streamlit desplegada en Cloud Público (Zero AWS)"

# Variables de entorno para Python y Streamlit
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y módulos
COPY . .

# Generar dataset en tiempo de construcción si no existe
RUN python generate_dataset.py

# Exponer el puerto estándar de la aplicación
EXPOSE 8501

# Healthcheck para monitorización de salud en la nube pública
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicio del servidor Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
