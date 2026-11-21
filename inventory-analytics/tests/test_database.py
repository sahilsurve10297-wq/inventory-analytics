"""Integration tests for database fallback, SQLite mirror, and SQL queries."""

from pathlib import Path
import unittest

import config
from src.database import load_data_with_fallback, build_sqlite_mirror


class TestDatabase(unittest.TestCase):
    def test_csv_fallback_loads_all_tables(self):
        data, source = load_data_with_fallback(config.PROCESSED_DATA_DIR)
        self.assertIn(source, ("PostgreSQL", "CSV Fallback"))
        for tbl in ["products", "warehouses", "suppliers", "inventory_movements", "sales", "purchase_orders", "current_stock"]:
            self.assertIn(tbl, data)
            self.assertGreater(len(data[tbl]), 0)

    def test_sqlite_mirror_executes_business_queries(self):
        conn = build_sqlite_mirror(config.PROCESSED_DATA_DIR)
        text = (config.SQL_DIR / "business_insights.sql").read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith("--")]
        stmts = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]
        self.assertGreaterEqual(len(stmts), 10)
        for stmt in stmts:
            rows = conn.execute(stmt).fetchall()
            self.assertIsInstance(rows, list)
        conn.close()


if __name__ == "__main__":
    unittest.main()
