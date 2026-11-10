"""
Pruebas Unitarias y Benchmarks Automatizados para el Motor OLAP DuckDB.
Ejecutables en entornos locales y en pipelines de CI/CD (GitHub Actions).
"""

import unittest
import os
import sys

# Agregar ruta base
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from olap_engine import OLAPEngine

class TestOLAPEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa el motor OLAP antes de ejecutar la suite."""
        parquet_path = os.path.join(os.path.dirname(__file__), "..", "data", "sales_analytics.parquet")
        cls.engine = OLAPEngine(parquet_path=parquet_path)

    def test_01_kpis_integrity_and_math(self):
        """Verifica integridad de datos y relaciones contables en métricas OLAP."""
        kpis = self.engine.get_kpis()
        
        self.assertGreater(kpis["total_transactions"], 0, "Debe haber transacciones")
        self.assertGreater(kpis["total_revenue"], 0, "El ingreso neto debe ser positivo")
        self.assertGreater(kpis["total_profit"], 0, "La utilidad debe ser positiva")
        
        # Validar consistencia contable con tolerancia por redondeo fila a fila
        net_plus_disc = kpis["total_revenue"] + kpis["total_discounts"]
        ratio = net_plus_disc / kpis["total_gross_sales"]
        self.assertAlmostEqual(ratio, 1.0, places=4, msg="La sumatoria contable debe coincidir con precisión del 99.999%")

    def test_02_sub_second_latency_benchmark(self):
        """Valida que DuckDB ejecute agregaciones masivas en sub-segundo (< 150 ms)."""
        kpis = self.engine.get_kpis()
        self.assertLess(kpis["execution_time_ms"], 150.0, f"Latencia excesiva: {kpis['execution_time_ms']} ms")

    def test_03_time_series_rollup(self):
        """Verifica la agregación ROLL-UP temporal y Window Functions."""
        df_months, latency = self.engine.get_time_series_rollup(level="month")
        
        self.assertGreater(len(df_months), 0)
        self.assertIn("period", df_months.columns)
        self.assertIn("revenue_moving_avg_3p", df_months.columns)
        self.assertIn("mom_growth_pct", df_months.columns)
        self.assertLess(latency, 200.0)

    def test_04_slice_and_dice_filtering(self):
        """Verifica el filtrado multidimensional Slice & Dice."""
        filters = {"region": ["Latinoamérica"]}
        df_sd, _ = self.engine.get_slice_and_dice(group_by_col="country", metric="total_revenue", filters=filters)
        
        # Verificar que solo contenga países de Latinoamérica
        latam_countries = {"Perú", "Colombia", "México", "Chile", "Brasil", "Argentina"}
        returned_countries = set(df_sd["dimension"].unique())
        self.assertTrue(returned_countries.issubset(latam_countries), "Solo deben figurar países de Latinoamérica")

    def test_05_pivot_matrix_computation(self):
        """Verifica que la matriz cruzada PIVOT se genere correctamente."""
        df_pivot, latency = self.engine.get_pivot_matrix(row_dim="category", col_dim="region", metric="net_revenue")
        
        self.assertGreater(len(df_pivot), 0)
        self.assertIn("category", df_pivot.columns)
        self.assertLess(latency, 200.0)

    def test_06_pareto_analysis_cumulative_100(self):
        """Verifica que la regla de Pareto acumule hasta el 100%."""
        df_pareto, _ = self.engine.get_pareto_analysis(dimension="category")
        
        self.assertGreater(len(df_pareto), 0)
        last_cumulative = df_pareto.iloc[-1]["cumulative_pct"]
        self.assertAlmostEqual(last_cumulative, 100.0, delta=0.5, msg="El acumulado final debe converger a 100%")

    def test_07_custom_sql_and_explain(self):
        """Verifica ejecución de consultas arbitrarias con plan físico EXPLAIN."""
        sql = "SELECT category, count(*) as n, sum(net_revenue) as rev FROM sales_cube GROUP BY 1 ORDER BY rev DESC"
        df, latency, plan = self.engine.execute_custom_query(sql)
        
        self.assertGreater(len(df), 0)
        self.assertTrue("HASH GROUP BY" in plan.upper() or "READ_PARQUET" in plan.upper(), "El plan físico debe reflejar agregación vectorial")
        self.assertLess(latency, 150.0)

if __name__ == "__main__":
    unittest.main()
