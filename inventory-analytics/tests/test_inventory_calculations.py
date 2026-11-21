"""Unit tests for Inventory KPI calculations and zero-denominator safety."""

import unittest
import pandas as pd

import config
from src.inventory_calculations import safe_div, compute_all_kpis


class TestInventoryCalculations(unittest.TestCase):
    def test_safe_div_zero_denominator(self):
        self.assertEqual(safe_div(100.0, 0.0, default=0.0), 0.0)
        self.assertEqual(safe_div(100.0, 25.0), 4.0)

    def test_processed_kpis_consistency(self):
        products = pd.read_csv(config.PROCESSED_DATA_DIR / "products.csv")
        warehouses = pd.read_csv(config.PROCESSED_DATA_DIR / "warehouses.csv")
        suppliers = pd.read_csv(config.PROCESSED_DATA_DIR / "suppliers.csv")
        movements = pd.read_csv(config.PROCESSED_DATA_DIR / "inventory_movements.csv")
        sales = pd.read_csv(config.PROCESSED_DATA_DIR / "sales.csv")
        pos = pd.read_csv(config.PROCESSED_DATA_DIR / "purchase_orders.csv")
        stock = pd.read_csv(config.PROCESSED_DATA_DIR / "current_stock.csv")

        kpis = compute_all_kpis(products, warehouses, suppliers, movements, sales, pos, stock)
        self.assertEqual(kpis["total_products"], 500)
        self.assertGreater(kpis["total_inventory_value"], 0)
        self.assertGreater(kpis["total_sales_revenue"], 0)
        self.assertGreater(kpis["inventory_turnover_ratio"], 0)
        self.assertEqual(kpis["inventory_accuracy_pct"], 100.0)
        self.assertGreaterEqual(kpis["gross_profit_margin_pct"], 0)
        self.assertLessEqual(kpis["gross_profit_margin_pct"], 100)


if __name__ == "__main__":
    unittest.main()
