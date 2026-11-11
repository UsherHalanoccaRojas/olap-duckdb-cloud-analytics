"""
DuckOLAP Enterprise: Solución Analítica Online Analytical Processing (OLAP)
Unidad 2 | Equipo: Halanocca, Yizuka & Gino
Tecnologías: DuckDB, Streamlit, Apache Parquet, MotherDuck Cloud SaaS, GitHub Actions (Zero AWS)
"""

import time
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from olap_engine import OLAPEngine

# Configuración de la página
st.set_page_config(
    page_title="DuckOLAP Enterprise | Solución OLAP Cloud",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una interfaz moderna y profesional
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5 0%, #00ACC1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 1rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 12px;
        background-color: #E3F2FD;
        color: #1565C0;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .badge-pill-green {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 12px;
        background-color: #E8F5E9;
        color: #2E7D32;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .kpi-card {
        background: #ffffff;
        padding: 16px 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        text-align: center;
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1a237e;
        margin-top: 4px;
    }
    .kpi-latency {
        font-size: 0.75rem;
        color: #00897b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar motor OLAP en cache
@st.cache_resource
def get_olap_engine():
    parquet_path = os.path.join(os.path.dirname(__file__), "data", "sales_analytics.parquet")
    if not os.path.exists(parquet_path):
        from generate_dataset import generate_olap_dataset
        generate_olap_dataset(num_rows=150000, output_path=parquet_path)
    return OLAPEngine(parquet_path=parquet_path)

engine = get_olap_engine()

# Encabezado Principal
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="main-title">⚡ DuckOLAP Enterprise Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Motor OLAP Multidimensional de Alto Rendimiento en la Nube Pública (Zero AWS)</div>', unsafe_allow_html=True)
    st.markdown("""
        <span class="badge-pill">🏛️ Arquitectura OLAP Cloud</span>
        <span class="badge-pill">👥 Autores: Halanocca, Yizuka & Gino</span>
        <span class="badge-pill-green">🚀 Motor: DuckDB C++ Vectorized + Parquet</span>
        <span class="badge-pill-green">☁️ Cloud SaaS: MotherDuck / Streamlit Cloud</span>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown("""
    <div style="text-align: right; padding-top: 10px;">
        <span style="font-size: 0.85rem; color: #666;">Volumen de Datos:</span><br>
        <strong style="font-size: 1.3rem; color: #2E7D32;">150,000 Transacciones</strong><br>
        <span style="font-size: 0.8rem; color: #888;">Compresión Columnar ZSTD</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Barra lateral para Operaciones Slice & Dice (Filtros Multidimensionales)
with st.sidebar:
    st.header("🎛️ Operaciones Slice & Dice")
    st.caption("Filtre dimensiones analíticas en tiempo real:")
    
    # Rango de fechas
    date_filter = st.date_input(
        "Rango de Fechas (Order Date)",
        value=[pd.to_datetime("2024-01-01"), pd.to_datetime("2025-12-31")]
    )
    
    # Dimensión Región
    regions_available = ["Latinoamérica", "Norteamérica", "Europa", "Asia-Pacífico"]
    selected_regions = st.multiselect("Región Continental", regions_available, default=regions_available)
    
    # Dimensión País (filtrado condicional)
    country_map = {
        "Latinoamérica": ["Perú", "Colombia", "México", "Chile", "Brasil", "Argentina"],
        "Norteamérica": ["Estados Unidos"],
        "Europa": ["España", "Alemania"],
        "Asia-Pacífico": ["Japón"]
    }
    allowed_countries = []
    for r in selected_regions:
        allowed_countries.extend(country_map.get(r, []))
        
    selected_countries = st.multiselect("Países", allowed_countries, default=allowed_countries)
    
    # Categoría
    categories = [
        "Servidores & Cloud Hardware", 
        "Laptops & Workstations", 
        "Infraestructura de Red", 
        "Licenciamiento Software & SaaS", 
        "Periféricos & Almacenamiento"
    ]
    selected_categories = st.multiselect("Categorías de Producto", categories, default=categories)
    
    # Segmento de Cliente
    segments = [
        "Corporativo / Enterprise", 
        "Pymes y Startups", 
        "Sector Público / Educación", 
        "Consumidor Final (B2C)"
    ]
    selected_segments = st.multiselect("Segmento de Cliente", segments, default=segments)
    
    # Canal de Ventas
    channels = [
        "Venta Directa Consultiva", 
        "Portal Web Self-Service", 
        "Canal de Distribución / Partners", 
        "Marketplace B2B"
    ]
    selected_channels = st.multiselect("Canal de Venta", channels, default=channels)
    
    st.markdown("---")
    st.subheader("⚙️ Configuración del Motor")
    cloud_mode = st.toggle("Modo Híbrido MotherDuck SaaS", value=False)
    if cloud_mode:
        if engine.is_cloud_connected:
            st.info("🌐 Conexión híbrida DuckDB + MotherDuck Cloud activada (SaaS OLAP Serverless).")
        else:
            st.warning("⚠️ Token `MOTHERDUCK_TOKEN` no configurado. Operando en fallback local DuckDB en memoria.")
    else:
        st.success("⚡ Motor local en memoria C++ Vectorizado (Sub-milisegundo).")

# Armar diccionario de filtros
filters = {}
if isinstance(date_filter, (list, tuple)) and len(date_filter) == 2:
    filters["order_date"] = (str(date_filter[0]), str(date_filter[1]))
filters["region"] = selected_regions
filters["country"] = selected_countries
filters["category"] = selected_categories
filters["customer_segment"] = selected_segments
filters["sales_channel"] = selected_channels

# Pestañas de Navegación del Sistema OLAP
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tablero Ejecutivo (KPIs)",
    "📈 Operaciones OLAP (Roll-up & Drill)",
    "🔀 Matriz PIVOT & CUBE",
    "💻 Consola SQL Analítica",
    "☁️ Arquitectura & Documentación"
])

# ==========================================
# TAB 1: TABLERO EJECUTIVO (KPIs)
# ==========================================
with tab1:
    kpis = engine.get_kpis(filters)
    if kpis["total_transactions"] == 0:
        st.warning("No hay transacciones para la combinación de filtros seleccionada. Ajuste los filtros en la barra lateral.")
    
    # Fila de tarjetas KPI
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Ingresos Netos</div>
            <div class="kpi-value">${kpis['total_revenue']:,.0f}</div>
            <div class="kpi-latency">⚡ {kpis['execution_time_ms']} ms latencia</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Utilidad Neta</div>
            <div class="kpi-value" style="color: #2E7D32;">${kpis['total_profit']:,.0f}</div>
            <div class="kpi-latency">Margen: {kpis['avg_profit_margin']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Transacciones</div>
            <div class="kpi-value">{kpis['total_transactions']:,}</div>
            <div class="kpi-latency">{kpis['total_units']:,.0f} unidades</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Ticket Promedio</div>
            <div class="kpi-value">${kpis['avg_ticket']:,.2f}</div>
            <div class="kpi-latency">Por pedido procesado</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Tiempo Entrega Prom.</div>
            <div class="kpi-value">{kpis['avg_delivery_days']:.1f} Días</div>
            <div class="kpi-latency">Satisfacción: {kpis['avg_satisfaction']:.1f} / 5.0 ⭐</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos de tendencias ejecutivas
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        df_time, t_ms = engine.get_time_series_rollup(level="month", filters=filters)
        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=df_time["period"], 
            y=df_time["revenue"], 
            name="Ingresos Mensuales", 
            marker_color="#1E88E5",
            opacity=0.75
        ))
        fig_time.add_trace(go.Scatter(
            x=df_time["period"], 
            y=df_time["revenue_moving_avg_3p"], 
            name="Media Móvil 3M (Window Function)", 
            line=dict(color="#FF6F00", width=3)
        ))
        fig_time.update_layout(
            title=f"Evolución Mensual de Ingresos y Tendencia Suavizada (DuckDB: {t_ms} ms)",
            xaxis_title="Periodo",
            yaxis_title="Monto ($)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
    with chart_col2:
        df_seg, s_ms = engine.get_slice_and_dice(group_by_col="customer_segment", metric="total_revenue", filters=filters)
        fig_seg = px.pie(
            df_seg, 
            names="dimension", 
            values="total_revenue", 
            hole=0.45,
            title=f"Distribución de Ingresos por Segmento (DuckDB: {s_ms} ms)",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_seg.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        st.plotly_chart(fig_seg, use_container_width=True)

# ==========================================
# TAB 2: OPERACIONES OLAP (ROLL-UP & DRILL)
# ==========================================
with tab2:
    st.subheader("🔄 Demostración Práctica de Operaciones Canónicas OLAP")
    st.write("""
    Las operaciones OLAP permiten a los analistas explorar datos multidimensionales navegando entre 
    diferentes niveles de agregación y granularidad conceptual.
    """)
    
    op_type = st.radio(
        "Seleccione la Operación OLAP a experimentar:",
        ["1. ROLL-UP (Subir en granularidad temporal)", "2. DRILL-DOWN (Bajar en jerarquía geográfica / producto)", "3. SLICE & DICE (Corte dimensional y ranking)"],
        horizontal=True
    )
    
    if "ROLL-UP" in op_type:
        col_r1, col_r2 = st.columns([1, 3])
        with col_r1:
            rollup_level = st.selectbox(
                "Nivel de Agregación Jerárquica (Roll-up):",
                ["year", "quarter", "month", "day"],
                index=2,
                format_func=lambda x: {"year": "Anual (Máximo Roll-up)", "quarter": "Trimestral", "month": "Mensual", "day": "Diario (Máximo Drill-down)"}[x]
            )
            st.info(f"**Concepto OLAP:**\nAl aplicar `DATE_TRUNC('{rollup_level}', order_date)`, el motor DuckDB vectorizado consolida los registros calculando sumatorias y tasas de cambio intermensual con `LAG()`.")
        
        with col_r2:
            df_roll, r_ms = engine.get_time_series_rollup(level=rollup_level, filters=filters)
            if df_roll.empty:
                st.warning("No hay datos temporales para los filtros seleccionados.")
            else:
                fig_roll = px.bar(
                    df_roll,
                    x="period",
                    y="revenue",
                    title=f"Resultado de ROLL-UP a nivel '{rollup_level}' ({len(df_roll)} filas devueltas en {r_ms} ms)",
                    color="profit",
                    color_continuous_scale="Viridis",
                    labels={"period": "Periodo Temporal", "revenue": "Ingresos ($)", "profit": "Utilidad Neta ($)"}
                )
                st.plotly_chart(fig_roll, use_container_width=True)
                
                with st.expander("Ver tabla de datos agregados y Window Functions"):
                    st.dataframe(df_roll, use_container_width=True)

    elif "DRILL-DOWN" in op_type:
        st.write("Navegación jerárquica: **Región Continental ➔ País ➔ Categoría de Producto**")
        df_drill, d_ms = engine.get_drill_down_hierarchy(filters=filters)
        if df_drill.empty:
            st.warning("No hay datos jerárquicos para los filtros seleccionados.")
        else:
            fig_sun = px.sunburst(
                df_drill,
                path=["region", "country", "category"],
                values="total_revenue",
                color="margin_pct",
                color_continuous_scale="RdYlGn",
                title=f"Exploración Jerárquica Sunburst (Drill-Down DuckDB en {d_ms} ms)",
                labels={"margin_pct": "Margen %"}
            )
            fig_sun.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_sun, use_container_width=True)
        
    elif "SLICE & DICE" in op_type:
        col_sd1, col_sd2 = st.columns([1, 2])
        with col_sd1:
            dim_choice = st.selectbox(
                "Dimensión para Corte y Agrupamiento:",
                ["category", "country", "sales_channel", "payment_method", "customer_segment"],
                format_func=lambda x: {
                    "category": "Categoría de Producto",
                    "country": "País Geográfico",
                    "sales_channel": "Canal de Venta",
                    "payment_method": "Método de Pago",
                    "customer_segment": "Segmento de Cliente"
                }[x]
            )
            metric_choice = st.selectbox(
                "Métrica de Ordenamiento:",
                ["total_revenue", "total_profit", "transactions", "total_units"],
                format_func=lambda x: {
                    "total_revenue": "Ingresos Netos ($)",
                    "total_profit": "Utilidad Neta ($)",
                    "transactions": "Número de Pedidos",
                    "total_units": "Unidades Vendidas"
                }[x]
            )
        
        with col_sd2:
            df_sd, sd_ms = engine.get_slice_and_dice(group_by_col=dim_choice, metric=metric_choice, filters=filters)
            if df_sd.empty:
                st.warning("No hay datos para Slice & Dice con los filtros actuales.")
            else:
                fig_bar = px.bar(
                    df_sd,
                    x="dimension",
                    y=metric_choice,
                    color="avg_margin_pct",
                    title=f"Slice & Dice sobre '{dim_choice}' (Ejecutado en {sd_ms} ms)",
                    text_auto=True,
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 3: MATRIZ PIVOT & CUBE
# ==========================================
with tab3:
    st.subheader("🔀 Matriz Cruzada Multidimensional (PIVOT) & Agregaciones CUBE")
    st.write("""
    DuckDB cuenta con sintaxis nativa de `PIVOT` y operadores `ROLLUP / CUBE / GROUPING SETS`, permitiendo
    generar tablas de doble entrada y subtotales en milisegundos sin necesidad de dependencias externas.
    """)
    
    col_pv1, col_pv2 = st.columns(2)
    with col_pv1:
        pivot_row = st.selectbox("Dimensión en Filas:", ["category", "customer_segment", "sales_channel"], index=0)
    with col_pv2:
        pivot_col = st.selectbox("Dimensión en Columnas:", ["region", "payment_method"], index=0)
        
    df_pivot, p_ms = engine.get_pivot_matrix(row_dim=pivot_row, col_dim=pivot_col, metric="net_revenue", filters=filters)
    
    st.markdown(f"**Matriz Pivotada de Ingresos Netos ($):** *(Calculada en {p_ms} ms)*")
    if df_pivot.empty:
        st.warning("No hay datos para construir la matriz PIVOT con los filtros actuales.")
    else:
        st.dataframe(
            df_pivot.fillna(0.0),
            use_container_width=True
        )
    
    st.markdown("---")
    st.subheader("🧊 Subtotales Multidimensionales (ROLLUP / GROUPING SETS)")
    st.caption("Cálculo canónico de subtotales jerárquicos por Región y Categoría en una sola pasada")
    df_cube, c_ms = engine.get_cube_rollup_query(filters=filters)
    if df_cube.empty:
        st.warning("No hay datos para el cálculo de ROLLUP.")
    else:
        st.markdown(f"**Cubo ROLLUP (Región ➔ Categoría):** *(Ejecutado en {c_ms} ms)*")
        st.dataframe(df_cube, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Análisis de Pareto (Ley 80/20)")
    st.caption("Cálculo acumulativo con Window Function `SUM() OVER (ORDER BY revenue DESC)`")
    df_pareto, par_ms = engine.get_pareto_analysis(dimension=pivot_row, filters=filters)
    if df_pareto.empty:
        st.warning("No hay datos para el análisis de Pareto.")
    else:
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=df_pareto["item"],
            y=df_pareto["revenue"],
            name="Ingresos ($)",
            marker_color="#0288D1",
            yaxis="y1"
        ))
        fig_pareto.add_trace(go.Scatter(
            x=df_pareto["item"],
            y=df_pareto["cumulative_pct"],
            name="% Acumulado (Pareto)",
            marker_color="#D32F2F",
            line=dict(width=3, dash="dot"),
            yaxis="y2"
        ))
        fig_pareto.update_layout(
            title=f"Diagrama de Pareto sobre {pivot_row} ({par_ms} ms)",
            yaxis=dict(title="Ingresos Netos ($)"),
            yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

# ==========================================
# TAB 4: CONSOLA SQL ANALÍTICA & BENCHMARKS
# ==========================================
with tab4:
    st.subheader("💻 Consola SQL Interactiva y Benchmarking de Rendimiento OLAP")
    st.write("""
    Escriba cualquier consulta SQL analítica sobre la vista `sales_cube` (150,000 registros en Parquet).
    DuckDB ejecutará la consulta con su motor vectorial C++ y reportará el tiempo exacto en milisegundos.
    """)
    
    # Presets de consultas analíticas avanzadas
    preset_choice = st.selectbox(
        "Cargar Consulta Predefinida de Ejemplo:",
        [
            "1. Top 3 Categorías más rentables por Región con DENSE_RANK()",
            "2. Cubo Multidimensional canónico con ROLLUP y GROUPING()",
            "3. Cuantiles y Percentiles de Ticket Promedio (PERCENTILE_CONT)",
            "4. Matriz de Retención y Volumen por Canal y Segmento",
            "5. Consulta Personalizada Libre"
        ]
    )
    
    default_queries = {
        "1. Top 3 Categorías más rentables por Región con DENSE_RANK()": """
SELECT 
    region,
    category,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    ROUND(SUM(net_profit), 2) AS total_profit,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(net_profit) DESC) AS rank_in_region
FROM sales_cube
GROUP BY region, category
QUALIFY rank_in_region <= 3
ORDER BY region, rank_in_region;
        """.strip(),
        
        "2. Cubo Multidimensional canónico con ROLLUP y GROUPING()": """
SELECT 
    COALESCE(region, '--- TOTAL GLOBAL ---') AS region,
    COALESCE(category, '--- SUB-TOTAL REGION ---') AS category,
    COUNT(*) AS transactions,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    ROUND(AVG(profit_margin_pct), 2) AS avg_margin
FROM sales_cube
GROUP BY ROLLUP (region, category)
ORDER BY 
    GROUPING(region), region, 
    GROUPING(category), category;
        """.strip(),

        "3. Cuantiles y Percentiles de Ticket Promedio (PERCENTILE_CONT)": """
SELECT 
    customer_segment,
    COUNT(*) AS total_orders,
    ROUND(AVG(net_revenue), 2) AS avg_ticket,
    ROUND(MEDIAN(net_revenue), 2) AS median_ticket,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY net_revenue), 2) AS p95_ticket,
    ROUND(MAX(net_revenue), 2) AS max_ticket
FROM sales_cube
GROUP BY customer_segment
ORDER BY avg_ticket DESC;
        """.strip(),

        "4. Matriz de Retención y Volumen por Canal y Segmento": """
SELECT 
    sales_channel,
    customer_segment,
    COUNT(*) AS orders,
    ROUND(SUM(quantity), 0) AS total_units,
    ROUND(SUM(net_revenue), 2) AS revenue,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_time,
    ROUND(AVG(customer_satisfaction), 2) AS avg_satisfaction_stars
FROM sales_cube
GROUP BY sales_channel, customer_segment
ORDER BY sales_channel, revenue DESC;
        """.strip(),

        "5. Consulta Personalizada Libre": """
SELECT 
    country, 
    COUNT(*) AS orders, 
    ROUND(SUM(net_revenue), 2) AS revenue 
FROM sales_cube 
GROUP BY country 
ORDER BY revenue DESC;
        """.strip()
    }
    
    current_sql = st.text_area("Sentencia SQL Analítica:", value=default_queries[preset_choice], height=160)
    
    col_btn, col_stats = st.columns([1, 3])
    with col_btn:
        execute_btn = st.button("🚀 Ejecutar Consulta", type="primary")
        
    if execute_btn or current_sql:
        try:
            df_result, q_ms, q_plan = engine.execute_custom_query(current_sql)
            with col_stats:
                st.success(f"✅ Consulta ejecutada exitosamente: **{len(df_result):,} filas** devueltas en **{q_ms} ms** (Motor Vectorizado C++ DuckDB)")
            
            st.dataframe(df_result, use_container_width=True)
            
            with st.expander("🔍 Ver Plan de Ejecución Físico (EXPLAIN Vectorized Query Plan)"):
                st.code(q_plan, language="text")
        except Exception as e:
            st.error(f"❌ Error al ejecutar consulta SQL: {str(e)}")

# ==========================================
# TAB 5: ARQUITECTURA & DOCUMENTACIÓN
# ==========================================
with tab5:
    st.subheader("🏛️ Arquitectura del Sistema OLAP & Enlaces de Entrega")
    st.markdown("""
    Esta solución implementa una arquitectura moderna de **Data Warehouse / OLAP Serverless** 
    que elimina la complejidad y costos asociados a clusters tradicionales o dependencias de AWS.
    """)
    
    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────────────────────────┐
    │              ARQUITECTURA DE LA SOLUCIÓN OLAP (ZERO AWS)               │
    └────────────────────────────────────────────────────────────────────────┘
    
       [ Capa de Almacenamiento Columnar ]
             Apache Parquet (ZSTD Compressed)
             └── Almacenamiento particionado eficiente por columnas
                    │
                    ▼
       [ Motor de Cómputo OLAP Vectorizado ]
             DuckDB (Core C++ Embeddable) / MotherDuck SaaS
             ├── Vectorized SIMD Execution Engine
             ├── Multi-core Parallel Scans & Aggregations
             ├── Zero-Copy Data Pushdown (Sin ingestión costosa)
             └── Operaciones: Roll-up, Drill-down, Slice&Dice, PIVOT, CUBE
                    │
                    ▼
       [ Capa de Presentación & Visualización Interactiva ]
             Streamlit Cloud SaaS + Plotly Interactive Engine
             ├── KPIs en tiempo real con latencias sub-30ms
             ├── Filtros multidimensionales reactivos
             └── Consola SQL interactiva con plan físico EXPLAIN
                    │
                    ▲
       [ DevOps: Automatización y Despliegue Continuo ]
             GitHub Actions CI/CD Pipeline
             ├── Validación de esquemas y tests unitarios
             ├── Pruebas de regresión y benchmarks de latencia
             └── Despliegue automatizado en Streamlit Community Cloud
    ```
    """)
    
    st.markdown("### 📋 Resumen de Recursos y Stack del Proyecto")
    st.info("""
    Componentes técnicos principales de **DuckOLAP Enterprise** (Zero AWS):
    """)
    
    st.markdown("""
    | Componente | Tecnología / Plataforma | Ubicación en el Repositorio | Descripción |
    | :--- | :--- | :--- | :--- |
    | **Motor Analítico OLAP** | DuckDB C++ Vectorizado | `olap_engine.py` | Roll-up, Drill-down, Slice & Dice, PIVOT, ROLLUP y Pareto |
    | **Generador de Cubo** | DuckDB + Apache Parquet (ZSTD) | `generate_dataset.py` | Genera 150,000 registros (~3.6 MB) |
    | **Interfaz Analítica** | Streamlit + Plotly | `app.py` | Dashboard interactivo y consola SQL con `EXPLAIN` |
    | **Suite de Pruebas** | Python `unittest` | `tests/test_olap.py` | Pruebas de integridad contable y SLA (< 150 ms) |
    | **CI/CD & Contenedores** | GitHub Actions + Docker | `.github/workflows/ci-cd.yml`, `Dockerfile` | Validación automática y despliegue en Streamlit Cloud |
    | **Artículo Técnico** | Medium | `articles/ARTICULO_MEDIUM_DUCKOLAP.md` | Guía arquitectónica y de implementación paso a paso |
    """)

# Pie de página
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #777; font-size: 0.85rem;">
    DuckOLAP Enterprise: Online Analytical Processing (OLAP) | © 2026 Equipo: Halanocca, Yizuka & Gino<br>
    Construido con Python, DuckDB, Streamlit, Parquet y Desplegado en Public Cloud SaaS (Zero AWS).
</div>
""", unsafe_allow_html=True)
