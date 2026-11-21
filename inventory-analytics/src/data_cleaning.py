"""Data cleaning, validation, and stock reconciliation pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

import config


def load_raw_datasets(raw_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load all 6 raw CSV datasets."""
    src_dir = raw_dir or config.RAW_DATA_DIR
    names = [
        "products",
        "warehouses",
        "suppliers",
        "inventory_movements",
        "sales",
        "purchase_orders",
    ]
    return {name: pd.read_csv(src_dir / f"{name}.csv") for name in names}


def clean_products(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean and standardize products table."""
    out = df.copy()
    initial_rows = len(out)
    out = out.drop_duplicates(subset=["product_id"], keep="first")

    # Standardize category and subcategory text
    out["category"] = out["category"].astype(str).str.strip().str.title()
    # Fix "&" casing after title()
    out["category"] = out["category"].str.replace(" & ", " & ", regex=False)
    out["subcategory"] = out["subcategory"].astype(str).str.strip()

    # Fill missing brand from first token of product_name
    missing_brands = int(out["brand"].isna().sum())
    out["brand"] = out.apply(
        lambda r: str(r["product_name"]).split()[0] if pd.isna(r["brand"]) else str(r["brand"]).strip(),
        axis=1,
    )

    numeric_cols = ["unit_cost", "selling_price", "reorder_level", "safety_stock", "lead_time_days"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["product_id", "unit_cost", "selling_price", "supplier_id"])
    out["reorder_level"] = out["reorder_level"].fillna(20).astype(int)
    out["safety_stock"] = out["safety_stock"].fillna(10).astype(int)
    out["lead_time_days"] = out["lead_time_days"].fillna(7).astype(int)

    stats = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(out),
        "missing_brands_imputed": missing_brands,
    }
    return out.reset_index(drop=True), stats


def clean_warehouses(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean warehouses table."""
    out = df.copy().drop_duplicates(subset=["warehouse_id"], keep="first")
    out["warehouse_capacity"] = pd.to_numeric(out["warehouse_capacity"], errors="coerce").fillna(100000).astype(int)
    return out.reset_index(drop=True), {"initial_rows": len(df), "cleaned_rows": len(out)}


def clean_suppliers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean suppliers table."""
    out = df.copy().drop_duplicates(subset=["supplier_id"], keep="first")
    missing_ratings = int(out["supplier_rating"].isna().sum())
    median_rating = round(float(out["supplier_rating"].median()), 2)
    out["supplier_rating"] = pd.to_numeric(out["supplier_rating"], errors="coerce").fillna(median_rating)
    out["average_delivery_days"] = pd.to_numeric(out["average_delivery_days"], errors="coerce").fillna(10).astype(int)
    out["supplier_status"] = out["supplier_status"].fillna("Active").astype(str).str.strip()
    return out.reset_index(drop=True), {
        "initial_rows": len(df),
        "cleaned_rows": len(out),
        "missing_ratings_imputed": missing_ratings,
    }


def clean_purchase_orders(
    df: pd.DataFrame,
    valid_products: set[str],
    valid_warehouses: set[str],
    valid_suppliers: set[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean purchase orders and validate foreign keys."""
    out = df.copy()
    initial_rows = len(out)
    out = out.drop_duplicates(subset=["purchase_order_id"], keep="first")
    out = out[
        out["product_id"].isin(valid_products)
        & out["warehouse_id"].isin(valid_warehouses)
        & out["supplier_id"].isin(valid_suppliers)
    ].copy()

    for col in ["order_date", "expected_delivery_date", "actual_delivery_date"]:
        out[col] = pd.to_datetime(out[col], errors="coerce")

    out["quantity_ordered"] = pd.to_numeric(out["quantity_ordered"], errors="coerce").fillna(0).astype(int)
    out["quantity_received"] = pd.to_numeric(out["quantity_received"], errors="coerce").fillna(0).astype(int)
    out["purchase_cost"] = pd.to_numeric(out["purchase_cost"], errors="coerce").fillna(0.0).round(2)
    out = out[out["quantity_ordered"] > 0].copy()

    # Format dates back to ISO string (keep NaT as empty/NaN for pending POs)
    out["order_date"] = out["order_date"].dt.strftime("%Y-%m-%d")
    out["expected_delivery_date"] = out["expected_delivery_date"].dt.strftime("%Y-%m-%d")
    out["actual_delivery_date"] = out["actual_delivery_date"].dt.strftime("%Y-%m-%d")

    return out.reset_index(drop=True), {
        "initial_rows": initial_rows,
        "cleaned_rows": len(out),
    }


def clean_inventory_movements(
    df: pd.DataFrame,
    products_df: pd.DataFrame,
    valid_warehouses: set[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean inventory movements, deduplicate, impute unit_cost, and validate FKs."""
    out = df.copy()
    initial_rows = len(out)
    out = out.drop_duplicates(subset=["movement_id"], keep="first")
    dups_removed = initial_rows - len(out)

    valid_products = set(products_df["product_id"])
    out = out[
        out["product_id"].isin(valid_products) & out["warehouse_id"].isin(valid_warehouses)
    ].copy()

    cost_map = dict(zip(products_df["product_id"], products_df["unit_cost"]))
    missing_costs = int(out["unit_cost"].isna().sum())
    out["unit_cost"] = pd.to_numeric(out["unit_cost"], errors="coerce")
    out["unit_cost"] = out.apply(
        lambda r: cost_map.get(r["product_id"], 0.0) if pd.isna(r["unit_cost"]) else float(r["unit_cost"]),
        axis=1,
    ).round(2)

    out["movement_date"] = pd.to_datetime(out["movement_date"], errors="coerce")
    out = out.dropna(subset=["movement_date"])
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce").fillna(0).astype(int)
    out = out[out["quantity"] > 0].copy()
    out["movement_date"] = out["movement_date"].dt.strftime("%Y-%m-%d")

    return out.reset_index(drop=True), {
        "initial_rows": initial_rows,
        "cleaned_rows": len(out),
        "duplicates_removed": dups_removed,
        "missing_costs_imputed": missing_costs,
    }


def clean_sales(
    df: pd.DataFrame,
    products_df: pd.DataFrame,
    valid_warehouses: set[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean sales transactions: deduplicate, remove negative/outlier quantities, recompute revenue/profit."""
    out = df.copy()
    initial_rows = len(out)
    out = out.drop_duplicates(subset=["sales_id"], keep="first")
    dups_removed = initial_rows - len(out)

    valid_products = set(products_df["product_id"])
    out = out[
        out["product_id"].isin(valid_products) & out["warehouse_id"].isin(valid_warehouses)
    ].copy()

    out["sales_date"] = pd.to_datetime(out["sales_date"], errors="coerce")
    out = out.dropna(subset=["sales_date"])

    out["quantity_sold"] = pd.to_numeric(out["quantity_sold"], errors="coerce")
    invalid_neg = int((out["quantity_sold"] <= 0).sum())
    outliers_removed = int((out["quantity_sold"] > 500).sum())
    out = out[(out["quantity_sold"] > 0) & (out["quantity_sold"] <= 500)].copy()
    out["quantity_sold"] = out["quantity_sold"].astype(int)

    missing_discounts = int(out["discount"].isna().sum())
    out["discount"] = pd.to_numeric(out["discount"], errors="coerce").fillna(0.0).clip(0.0, 0.8)
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")

    cost_map = dict(zip(products_df["product_id"], products_df["unit_cost"]))
    out["total_revenue"] = (out["quantity_sold"] * out["unit_price"] * (1.0 - out["discount"])).round(2)
    out["profit"] = (
        out["total_revenue"] - (out["quantity_sold"] * out["product_id"].map(cost_map))
    ).round(2)
    out["sales_date"] = out["sales_date"].dt.strftime("%Y-%m-%d")

    return out.reset_index(drop=True), {
        "initial_rows": initial_rows,
        "cleaned_rows": len(out),
        "duplicates_removed": dups_removed,
        "invalid_negative_removed": invalid_neg,
        "outliers_removed": outliers_removed,
        "missing_discounts_imputed": missing_discounts,
    }


def reconcile_inventory_stock(movements_df: pd.DataFrame) -> pd.DataFrame:
    """Compute reconciled on-hand stock per (product_id, warehouse_id) from movements."""
    sign_map = {
        "Purchase": 1,
        "Return": 1,
        "Transfer In": 1,
        "Adjustment": 1,
        "Sale": -1,
        "Transfer Out": -1,
    }
    df = movements_df.copy()
    df["signed_qty"] = df["movement_type"].map(sign_map).fillna(0).astype(int) * df["quantity"]
    stock = (
        df.groupby(["product_id", "warehouse_id"], as_index=False)["signed_qty"]
        .sum()
        .rename(columns={"signed_qty": "current_stock"})
    )
    stock["current_stock"] = stock["current_stock"].clip(lower=0).astype(int)
    return stock


def run_cleaning_pipeline(
    raw_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """Run full cleaning & reconciliation pipeline and save processed CSVs."""
    raw = load_raw_datasets(raw_dir)
    out_dir = processed_dir or config.PROCESSED_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    products, p_stats = clean_products(raw["products"])
    warehouses, w_stats = clean_warehouses(raw["warehouses"])
    suppliers, sup_stats = clean_suppliers(raw["suppliers"])

    valid_p = set(products["product_id"])
    valid_w = set(warehouses["warehouse_id"])
    valid_s = set(suppliers["supplier_id"])

    purchase_orders, po_stats = clean_purchase_orders(raw["purchase_orders"], valid_p, valid_w, valid_s)
    movements, mov_stats = clean_inventory_movements(raw["inventory_movements"], products, valid_w)
    sales, sales_stats = clean_sales(raw["sales"], products, valid_w)
    current_stock = reconcile_inventory_stock(movements)

    cleaned = {
        "products": products,
        "warehouses": warehouses,
        "suppliers": suppliers,
        "purchase_orders": purchase_orders,
        "inventory_movements": movements,
        "sales": sales,
        "current_stock": current_stock,
    }
    for name, df in cleaned.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)

    audit = {
        "products": p_stats,
        "warehouses": w_stats,
        "suppliers": sup_stats,
        "purchase_orders": po_stats,
        "inventory_movements": mov_stats,
        "sales": sales_stats,
        "reconciled_pairs": len(current_stock),
        "negative_stock_pairs": int((current_stock["current_stock"] < 0).sum()),
    }
    return cleaned, audit


if __name__ == "__main__":
    cleaned_data, report = run_cleaning_pipeline()
    print("=== DATA CLEANING & RECONCILIATION AUDIT ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
