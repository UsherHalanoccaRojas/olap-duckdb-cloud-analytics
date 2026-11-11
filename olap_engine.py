"""
Motor Analítico OLAP (Online Analytical Processing) basado en DuckDB.
Provee operaciones OLAP fundamentales: Roll-up, Drill-down, Slice & Dice, Pivot, CUBE y Window Functions.
"""

import os
import re
import time
from typing import Dict, Any, List, Optional, Tuple
import duckdb
import pandas as pd

DEFAULT_PARQUET = os.path.join(os.path.dirname(__file__), "data", "sales_analytics.parquet")

VALID_FILTER_COLS = {
    "order_date", "region", "country", "category",
    "customer_segment", "sales_channel", "payment_method",
    "order_year", "order_quarter", "order_month",
}
VALID_DIMENSIONS = {
    "region", "country", "category",
    "customer_segment", "sales_channel", "payment_method",
}
VALID_SLICE_METRICS = {
    "total_revenue", "total_profit", "transactions", "total_units", "avg_margin_pct",
}
VALID_PIVOT_METRICS = {
    "net_revenue", "net_profit", "gross_sales", "quantity",
}
READ_ONLY_STARTS = ("SELECT", "WITH", "PIVOT", "UNPIVOT", "DESCRIBE", "SHOW", "SUMMARIZE", "EXPLAIN")
FORBIDDEN_SQL_PATTERN = re.compile(
    r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|COPY|INSTALL|LOAD|PRAGMA|CALL|EXPORT|IMPORT)\b",
    re.IGNORECASE,
)


def _escape_sql_literal(value: Any) -> str:
    return str(value).replace("'", "''")


class OLAPEngine:
    def __init__(self, parquet_path: str = DEFAULT_PARQUET, motherduck_token: Optional[str] = None):
        """
        Inicializa la conexión con DuckDB en memoria o apuntando a MotherDuck SaaS.
        """
        self.parquet_path = parquet_path.replace(os.sep, "/")
        self.motherduck_token = motherduck_token or os.getenv("MOTHERDUCK_TOKEN")
        self.is_cloud_connected = False

        if self.motherduck_token:
            try:
                self.con = duckdb.connect(f"md:?motherduck_token={self.motherduck_token}")
                self.is_cloud_connected = True
            except Exception:
                self.con = duckdb.connect(database=":memory:")
        else:
            self.con = duckdb.connect(database=":memory:")

        self._configure_engine()
        self._load_table()

    def _configure_engine(self):
        """Ajusta configuraciones avanzadas del motor DuckDB para analítica de alta concurrencia."""
        self.con.execute("PRAGMA threads=4;")
        self.con.execute("PRAGMA memory_limit='2GB';")
        self.con.execute("PRAGMA preserve_insertion_order=false;")

    def _load_table(self):
        """Crea una vista sobre el archivo Parquet para consultas sin copia de datos (Zero-Copy Pushdown)."""
        if not os.path.exists(self.parquet_path):
            from generate_dataset import generate_olap_dataset
            generate_olap_dataset(num_rows=150000, output_path=self.parquet_path)

        escaped_path = _escape_sql_literal(self.parquet_path)
        self.con.execute(f"""
            CREATE OR REPLACE VIEW sales_cube AS 
            SELECT * FROM read_parquet('{escaped_path}');
        """)

    def _build_where_clause(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """Construye dinámicamente cláusulas WHERE para operaciones Slice & Dice."""
        if not filters:
            return ""

        clauses = []
        for col, val in filters.items():
            if col not in VALID_FILTER_COLS:
                raise ValueError(f"Columna de filtro no permitida: {col}")
            if val is None or val == "Todos":
                continue
            if isinstance(val, list):
                if len(val) == 0:
                    clauses.append("1 = 0")
                else:
                    val_list = ", ".join([f"'{_escape_sql_literal(v)}'" for v in val])
                    clauses.append(f"{col} IN ({val_list})")
            elif isinstance(val, tuple) and len(val) == 2:
                # Rango de fechas o valores numéricos
                clauses.append(f"{col} BETWEEN '{_escape_sql_literal(val[0])}' AND '{_escape_sql_literal(val[1])}'")
            else:
                clauses.append(f"{col} = '{_escape_sql_literal(val)}'")

        return "WHERE " + " AND ".join(clauses) if clauses else ""

    def get_kpis(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calcula los Indicadores Clave de Desempeño (KPIs) a nivel de cubo OLAP."""
        where_clause = self._build_where_clause(filters)
        query = f"""
        SELECT 
            COUNT(*) AS total_transactions,
            COALESCE(SUM(quantity), 0) AS total_units,
            COALESCE(SUM(gross_sales), 0) AS total_gross_sales,
            COALESCE(SUM(discount_amount), 0) AS total_discounts,
            COALESCE(SUM(net_revenue), 0) AS total_revenue,
            COALESCE(SUM(net_profit), 0) AS total_profit,
            COALESCE(AVG(profit_margin_pct), 0) AS avg_profit_margin,
            COALESCE(AVG(net_revenue), 0) AS avg_ticket,
            COALESCE(AVG(delivery_days), 0) AS avg_delivery_days,
            COALESCE(AVG(customer_satisfaction), 0) AS avg_satisfaction
        FROM sales_cube
        {where_clause};
        """
        start = time.perf_counter()
        df = self.con.execute(query).df()
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        result = df.to_dict(orient="records")[0]
        result["execution_time_ms"] = round(elapsed_ms, 2)
        return result

    def get_time_series_rollup(self, level: str = "month", filters: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, float]:
        """
        Operación OLAP: ROLL-UP temporal con Window Functions (Moving Average y Crecimiento % MoM).
        """
        where_clause = self._build_where_clause(filters)
        
        date_trunc_expr = {
            "year": "DATE_TRUNC('year', order_date)",
            "quarter": "DATE_TRUNC('quarter', order_date)",
            "month": "DATE_TRUNC('month', order_date)",
            "day": "DATE_TRUNC('day', order_date)"
        }.get(level, "DATE_TRUNC('month', order_date)")

        query = f"""
        WITH period_agg AS (
            SELECT 
                {date_trunc_expr} AS period,
                COUNT(*) AS transactions,
                ROUND(SUM(net_revenue), 2) AS revenue,
                ROUND(SUM(net_profit), 2) AS profit,
                ROUND(SUM(quantity), 0) AS units_sold
            FROM sales_cube
            {where_clause}
            GROUP BY 1
        )
        SELECT 
            period,
            transactions,
            revenue,
            profit,
            units_sold,
            ROUND(AVG(revenue) OVER (
                ORDER BY period 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 2) AS revenue_moving_avg_3p,
            ROUND((revenue - LAG(revenue, 1) OVER (ORDER BY period)) / 
                NULLIF(LAG(revenue, 1) OVER (ORDER BY period), 0) * 100, 2) AS mom_growth_pct
        FROM period_agg
        ORDER BY period ASC;
        """
        start = time.perf_counter()
        df = self.con.execute(query).df()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return df, round(elapsed_ms, 2)

    def _run_timed_query(self, query: str) -> Tuple[pd.DataFrame, float]:
        """Ejecuta una consulta SQL y retorna el DataFrame junto con la latencia en ms."""
        start = time.perf_counter()
        df = self.con.execute(query).df()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return df, round(elapsed_ms, 2)

    def get_slice_and_dice(self, group_by_col: str, metric: str = "total_revenue", filters: Optional[Dict[str, Any]] = None, limit: int = 15) -> Tuple[pd.DataFrame, float]:
        """
        Operación OLAP: SLICE & DICE multidimensional por cualquier dimensión de negocio.
        """
        if group_by_col not in VALID_DIMENSIONS:
            raise ValueError(f"Dimensión no permitida: {group_by_col}")
        normalized_metric = "total_revenue" if metric == "net_revenue" else metric
        if normalized_metric not in VALID_SLICE_METRICS:
            raise ValueError(f"Métrica no permitida: {metric}")
        safe_limit = max(1, int(limit))

        where_clause = self._build_where_clause(filters)
        query = f"""
        SELECT 
            {group_by_col} AS dimension,
            COUNT(*) AS transactions,
            ROUND(SUM(net_revenue), 2) AS total_revenue,
            ROUND(SUM(net_profit), 2) AS total_profit,
            ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct,
            ROUND(SUM(quantity), 0) AS total_units
        FROM sales_cube
        {where_clause}
        GROUP BY 1
        ORDER BY {normalized_metric} DESC
        LIMIT {safe_limit};
        """
        return self._run_timed_query(query)

    def get_pivot_matrix(self, row_dim: str = "category", col_dim: str = "region", metric: str = "net_revenue", filters: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, float]:
        """
        Operación OLAP: PIVOT (Matriz cruzada multidimensional nativa en DuckDB).
        """
        if row_dim not in VALID_DIMENSIONS or col_dim not in VALID_DIMENSIONS:
            raise ValueError("Dimensión de PIVOT no permitida.")
        if metric not in VALID_PIVOT_METRICS:
            raise ValueError(f"Métrica de PIVOT no permitida: {metric}")

        where_clause = self._build_where_clause(filters)
        query = f"""
        PIVOT (
            SELECT {row_dim}, {col_dim}, {metric}
            FROM sales_cube
            {where_clause}
        )
        ON {col_dim}
        USING ROUND(SUM({metric}), 2)
        GROUP BY {row_dim}
        ORDER BY {row_dim} ASC;
        """
        return self._run_timed_query(query)

    def get_drill_down_hierarchy(self, filters: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, float]:
        """
        Operación OLAP: DRILL-DOWN Jerárquico (Región -> País -> Categoría de Producto).
        """
        where_clause = self._build_where_clause(filters)
        query = f"""
        SELECT 
            region,
            country,
            category,
            COUNT(*) AS order_count,
            ROUND(SUM(net_revenue), 2) AS total_revenue,
            ROUND(SUM(net_profit), 2) AS total_profit,
            ROUND(AVG(profit_margin_pct), 2) AS margin_pct
        FROM sales_cube
        {where_clause}
        GROUP BY region, country, category
        ORDER BY region, total_revenue DESC;
        """
        return self._run_timed_query(query)

    def get_pareto_analysis(self, dimension: str = "category", filters: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, float]:
        """
        Análisis Pareto (80/20) usando Window Functions avanzadas (SUM OVER ROWS).
        """
        if dimension not in VALID_DIMENSIONS:
            raise ValueError(f"Dimensión de Pareto no permitida: {dimension}")

        where_clause = self._build_where_clause(filters)
        query = f"""
        WITH ranked AS (
            SELECT 
                {dimension} AS item,
                SUM(net_revenue) AS revenue
            FROM sales_cube
            {where_clause}
            GROUP BY 1
        ),
        cumulative AS (
            SELECT 
                item,
                revenue,
                SUM(revenue) OVER () AS global_revenue,
                SUM(revenue) OVER (ORDER BY revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
            FROM ranked
        )
        SELECT 
            item,
            ROUND(revenue, 2) AS revenue,
            ROUND((revenue / NULLIF(global_revenue, 0)) * 100, 2) AS pct_of_total,
            ROUND((running_total / NULLIF(global_revenue, 0)) * 100, 2) AS cumulative_pct
        FROM cumulative
        ORDER BY revenue DESC;
        """
        return self._run_timed_query(query)

    def get_cube_rollup_query(self, filters: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, float]:
        """
        Operación OLAP: CUBE / ROLLUP canónico con GROUPING SETS.
        Demuestra la computación de sub-totales multidimensionales en una sola pasada.
        """
        where_clause = self._build_where_clause(filters)
        query = f"""
        SELECT 
            COALESCE(region, '--- TOTAL GLOBAL ---') AS region,
            COALESCE(category, '--- TOTAL REGION ---') AS category,
            COUNT(*) AS transactions,
            ROUND(SUM(net_revenue), 2) AS total_revenue,
            ROUND(AVG(profit_margin_pct), 2) AS avg_margin
        FROM sales_cube
        {where_clause}
        GROUP BY ROLLUP (region, category)
        ORDER BY 
            GROUPING(region), region, 
            GROUPING(category), category;
        """
        return self._run_timed_query(query)

    def execute_custom_query(self, sql_query: str, read_only: bool = True) -> Tuple[pd.DataFrame, float, str]:
        """
        Ejecuta consultas analíticas SQL con medición de latencia y plan EXPLAIN.
        Por defecto restringe la ejecución a sentencias de solo lectura.
        """
        cleaned = sql_query.strip()
        if not cleaned:
            raise ValueError("La consulta SQL no puede estar vacía.")

        if read_only:
            upper_sql = re.sub(r"(--[^\n]*|/\*.*?\*/)", " ", cleaned, flags=re.DOTALL).strip().upper()
            if not upper_sql.startswith(READ_ONLY_STARTS) or FORBIDDEN_SQL_PATTERN.search(upper_sql):
                raise ValueError("Solo se permiten consultas analíticas de lectura (SELECT, WITH, PIVOT, EXPLAIN, DESCRIBE, SHOW).")

        df, elapsed_ms = self._run_timed_query(cleaned)

        # Obtener plan de ejecución físico
        explain_query = f"EXPLAIN {cleaned}"
        try:
            explain_df = self.con.execute(explain_query).df()
            plan_str = explain_df.to_string()
        except Exception:
            plan_str = "Plan de ejecución no disponible para esta consulta."

        return df, elapsed_ms, plan_str

