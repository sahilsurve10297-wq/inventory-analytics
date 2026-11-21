"""Unit tests for data cleaning and inventory reconciliation."""

import unittest
import pandas as pd

from src.data_cleaning import (
    clean_products,
    clean_sales,
    reconcile_inventory_stock,
)


class TestDataCleaning(unittest.TestCase):
    def test_clean_products_standardizes_category_and_brand(self):
        df = pd.DataFrame([
            {
                "product_id": "PRD-0001",
                "product_name": "VoltEdge Pro Earbuds",
                "category": "electronics ",
                "subcategory": "Audio",
                "brand": None,
                "unit_cost": 50.0,
                "selling_price": 80.0,
                "reorder_level": 20,
                "safety_stock": 10,
                "lead_time_days": 5,
                "supplier_id": "SUP-001",
            }
        ])
        cleaned, stats = clean_products(df)
        self.assertEqual(cleaned.loc[0, "category"], "Electronics")
        self.assertEqual(cleaned.loc[0, "brand"], "VoltEdge")
        self.assertEqual(stats["missing_brands_imputed"], 1)

    def test_clean_sales_removes_negatives_and_outliers(self):
        prods = pd.DataFrame([{"product_id": "PRD-0001", "unit_cost": 20.0}])
        sales = pd.DataFrame([
            {"sales_id": "S1", "product_id": "PRD-0001", "warehouse_id": "WH-001", "sales_date": "2025-01-01", "quantity_sold": 5, "unit_price": 40.0, "discount": None, "total_revenue": 0, "profit": 0},
            {"sales_id": "S2", "product_id": "PRD-0001", "warehouse_id": "WH-001", "sales_date": "2025-01-02", "quantity_sold": -3, "unit_price": 40.0, "discount": 0.0, "total_revenue": 0, "profit": 0},
            {"sales_id": "S3", "product_id": "PRD-0001", "warehouse_id": "WH-001", "sales_date": "2025-01-03", "quantity_sold": 9999, "unit_price": 40.0, "discount": 0.0, "total_revenue": 0, "profit": 0},
        ])
        cleaned, stats = clean_sales(sales, prods, {"WH-001"})
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "total_revenue"], 200.0)
        self.assertEqual(cleaned.loc[0, "profit"], 100.0)
        self.assertEqual(stats["invalid_negative_removed"], 1)
        self.assertEqual(stats["outliers_removed"], 1)

    def test_reconcile_inventory_stock(self):
        mov = pd.DataFrame([
            {"product_id": "PRD-0001", "warehouse_id": "WH-001", "movement_type": "Purchase", "quantity": 100},
            {"product_id": "PRD-0001", "warehouse_id": "WH-001", "movement_type": "Sale", "quantity": 35},
            {"product_id": "PRD-0001", "warehouse_id": "WH-001", "movement_type": "Return", "quantity": 5},
            {"product_id": "PRD-0001", "warehouse_id": "WH-001", "movement_type": "Transfer Out", "quantity": 10},
        ])
        stock = reconcile_inventory_stock(mov)
        self.assertEqual(int(stock.loc[0, "current_stock"]), 60)


if __name__ == "__main__":
    unittest.main()
