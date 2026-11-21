"""PostgreSQL database connection, schema initialization, and CSV-fallback loader."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any
import pandas as pd

import config


def get_sqlalchemy_engine():
    """Create a SQLAlchemy engine for PostgreSQL using environment configuration."""
    from sqlalchemy import create_engine  # lazy import for portability

    return create_engine(config.get_database_url(), pool_pre_ping=True)


def test_postgres_connection() -> bool:
    """Return True if PostgreSQL is reachable, False otherwise."""
    try:
        from sqlalchemy import text

        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def initialize_postgres_schema(sql_path: Path | None = None) -> None:
    """Execute create_tables.sql against PostgreSQL."""
    from sqlalchemy import text

    schema_file = sql_path or (config.SQL_DIR / "create_tables.sql")
    ddl = schema_file.read_text(encoding="utf-8")
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        for stmt in [s.strip() for s in ddl.split(";") if s.strip()]:
            conn.execute(text(stmt))


def load_processed_to_postgres(processed_dir: Path | None = None) -> dict[str, int]:
    """Load cleaned CSV tables into PostgreSQL in foreign-key order."""
    src_dir = processed_dir or config.PROCESSED_DATA_DIR
    engine = get_sqlalchemy_engine()
    table_order = [
        "warehouses",
        "suppliers",
        "products",
        "purchase_orders",
        "inventory_movements",
        "sales",
    ]
    counts: dict[str, int] = {}
    for tbl in table_order:
        df = pd.read_csv(src_dir / f"{tbl}.csv")
        df.to_sql(tbl, engine, if_exists="append", index=False, method="multi", chunksize=1000)
        counts[tbl] = len(df)
    return counts


def load_data_with_fallback(processed_dir: Path | None = None) -> tuple[dict[str, pd.DataFrame], str]:
    """Load tables from PostgreSQL if available; otherwise fall back to processed CSVs."""
    src_dir = processed_dir or config.PROCESSED_DATA_DIR
    tables = [
        "products",
        "warehouses",
        "suppliers",
        "inventory_movements",
        "sales",
        "purchase_orders",
        "current_stock",
    ]
    if test_postgres_connection():
        try:
            engine = get_sqlalchemy_engine()
            data = {t: pd.read_sql_table(t, engine) for t in tables if t != "current_stock"}
            from src.data_cleaning import reconcile_inventory_stock

            data["current_stock"] = reconcile_inventory_stock(data["inventory_movements"])
            return data, "PostgreSQL"
        except Exception:
            pass

    data = {t: pd.read_csv(src_dir / f"{t}.csv") for t in tables}
    return data, "CSV Fallback"


def build_sqlite_mirror(processed_dir: Path | None = None) -> sqlite3.Connection:
    """Build an in-memory SQLite mirror of processed tables for local SQL QA."""
    src_dir = processed_dir or config.PROCESSED_DATA_DIR
    conn = sqlite3.connect(":memory:")
    for tbl in ["warehouses", "suppliers", "products", "purchase_orders", "inventory_movements", "sales"]:
        df = pd.read_csv(src_dir / f"{tbl}.csv")
        df.to_sql(tbl, conn, if_exists="replace", index=False)
    return conn
