"""
Script para generar el dataset analítico OLAP en formato columnar Parquet usando DuckDB.
Dataset: Global Enterprise Sales & Operational Analytics (150,000 transacciones)
Optimizado con compresión ZSTD / Snappy para consultas OLAP en sub-milisegundos.
"""

import os
import time
import duckdb

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PARQUET_PATH = os.path.join(DATA_DIR, "sales_analytics.parquet")

def generate_olap_dataset(num_rows: int = 150000, output_path: str = PARQUET_PATH) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    start_time = time.time()
    print(f"[*] Iniciando generación de {num_rows:,} registros analíticos con DuckDB...")

    con = duckdb.connect()

    query = f"""
    COPY (
        WITH base AS (
            SELECT 
                i AS order_id,
                -- Fechas distribuidas uniformemente entre 2024-01-01 y 2025-12-31
                TIMESTAMP '2024-01-01 08:00:00' 
                    + INTERVAL ((i * 7) % 730) DAY 
                    + INTERVAL ((i * 13) % 43200) SECOND AS order_timestamp,
                
                -- Dimensiones Geográficas
                CASE (abs(hash(i)) % 10)
                    WHEN 0 THEN 'Perú'
                    WHEN 1 THEN 'Colombia'
                    WHEN 2 THEN 'México'
                    WHEN 3 THEN 'Chile'
                    WHEN 4 THEN 'España'
                    WHEN 5 THEN 'Estados Unidos'
                    WHEN 6 THEN 'Brasil'
                    WHEN 7 THEN 'Argentina'
                    WHEN 8 THEN 'Alemania'
                    ELSE 'Japón'
                END AS country,
                
                -- Segmento de Cliente
                CASE ((abs(hash(i)) >> 3) % 4)
                    WHEN 0 THEN 'Corporativo / Enterprise'
                    WHEN 1 THEN 'Pymes y Startups'
                    WHEN 2 THEN 'Sector Público / Educación'
                    ELSE 'Consumidor Final (B2C)'
                END AS customer_segment,
                
                -- Categoría y Subcategoría de Producto
                CASE ((abs(hash(i)) >> 6) % 5)
                    WHEN 0 THEN 'Servidores & Cloud Hardware'
                    WHEN 1 THEN 'Laptops & Workstations'
                    WHEN 2 THEN 'Infraestructura de Red'
                    WHEN 3 THEN 'Licenciamiento Software & SaaS'
                    ELSE 'Periféricos & Almacenamiento'
                END AS category,
                
                -- Canal de Ventas
                CASE ((abs(hash(i)) >> 9) % 4)
                    WHEN 0 THEN 'Venta Directa Consultiva'
                    WHEN 1 THEN 'Portal Web Self-Service'
                    WHEN 2 THEN 'Canal de Distribución / Partners'
                    ELSE 'Marketplace B2B'
                END AS sales_channel,

                -- Método de Pago
                CASE ((abs(hash(i)) >> 12) % 4)
                    WHEN 0 THEN 'Transferencia Bancaria'
                    WHEN 1 THEN 'Tarjeta de Crédito Corporativa'
                    WHEN 2 THEN 'Línea de Crédito a 30 Días'
                    ELSE 'Pago Electrónico / Gateway'
                END AS payment_method,

                -- Cantidad adquirida (1 a 50 unidades)
                1 + ((abs(hash(i)) >> 15) % 40) AS quantity,

                -- Precio unitario base
                50.0 + round(((abs(hash(i)) >> 17) % 950) * 2.75, 2) AS unit_price,

                -- Porcentaje de descuento (0% a 25%)
                round(((abs(hash(i)) >> 21) % 6) * 0.05, 2) AS discount_pct,

                -- Días de entrega
                1 + ((abs(hash(i)) >> 24) % 15) AS delivery_days,

                -- Nivel de satisfacción (1 a 5)
                3 + ((abs(hash(i)) >> 27) % 3) AS customer_satisfaction

            FROM range(1, {num_rows + 1}) t(i)
        )
        SELECT 
            order_id,
            order_timestamp,
            CAST(order_timestamp AS DATE) AS order_date,
            YEAR(order_timestamp) AS order_year,
            QUARTER(order_timestamp) AS order_quarter,
            MONTH(order_timestamp) AS order_month,
            STRFTIME(order_timestamp, '%B') AS month_name,
            DAYOFWEEK(order_timestamp) AS day_of_week,
            
            -- Derivación de Región Continental
            CASE 
                WHEN country IN ('Perú', 'Colombia', 'México', 'Chile', 'Brasil', 'Argentina') THEN 'Latinoamérica'
                WHEN country IN ('Estados Unidos') THEN 'Norteamérica'
                WHEN country IN ('España', 'Alemania') THEN 'Europa'
                ELSE 'Asia-Pacífico'
            END AS region,
            
            country,
            customer_segment,
            category,
            sales_channel,
            payment_method,
            quantity,
            unit_price,
            discount_pct,
            
            -- Medidas Financieras (Métricas OLAP)
            round(quantity * unit_price, 2) AS gross_sales,
            round(quantity * unit_price * discount_pct, 2) AS discount_amount,
            round(quantity * unit_price * (1 - discount_pct), 2) AS net_revenue,
            
            -- Costos y Margen de Utilidad
            round((quantity * unit_price * 0.58), 2) AS cost_of_goods_sold,
            round((quantity * unit_price * (1 - discount_pct)) - (quantity * unit_price * 0.58), 2) AS net_profit,
            round((((quantity * unit_price * (1 - discount_pct)) - (quantity * unit_price * 0.58)) / 
                   NULLIF(quantity * unit_price * (1 - discount_pct), 0)) * 100, 2) AS profit_margin_pct,
            
            delivery_days,
            customer_satisfaction
        FROM base
    ) TO '{output_path.replace(os.sep, "/")}' (FORMAT PARQUET, COMPRESSION 'ZSTD');
    """

    con.execute(query)
    con.close()

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[+] Dataset generado exitosamente en: {output_path}")
    print(f"[+] Tamaño: {file_size_mb:.2f} MB | Filas: {num_rows:,} | Tiempo: {elapsed:.2f} segundos")
    return output_path

if __name__ == "__main__":
    generate_olap_dataset()
