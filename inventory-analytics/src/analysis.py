"""Exploratory data analysis, warehouse/supplier aggregations, and Power BI exports."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

import config
from src.inventory_calculations import (
    compute_all_kpis,
    compute_product_inventory_snapshot,
    safe_div,
)
from src.forecasting import evaluate_and_forecast_products


def build_warehouse_summary(
    warehouses: pd.DataFrame,
    products: pd.DataFrame,
    current_stock: pd.DataFrame,
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate stock, value, capacity utilization, sales, and profit by warehouse."""
    cost_map = dict(zip(products["product_id"], products["unit_cost"]))
    stock_df = current_stock.copy()
    stock_df["stock_value"] = stock_df["current_stock"] * stock_df["product_id"].map(cost_map)

    wh_stock = stock_df.groupby("warehouse_id", as_index=False).agg(
        total_stock_units=("current_stock", "sum"),
        inventory_value=("stock_value", "sum"),
        sku_count=("product_id", "nunique"),
        stockout_skus=("current_stock", lambda s: int((s == 0).sum())),
    )

    wh_sales = sales.groupby("warehouse_id", as_index=False).agg(
        units_sold=("quantity_sold", "sum"),
        total_revenue=("total_revenue", "sum"),
        total_profit=("profit", "sum"),
    )

    out = warehouses.merge(wh_stock, on="warehouse_id", how="left").merge(wh_sales, on="warehouse_id", how="left")
    for c in ["total_stock_units", "sku_count", "stockout_skus", "units_sold"]:
        out[c] = out[c].fillna(0).astype(int)
    for c in ["inventory_value", "total_revenue", "total_profit"]:
        out[c] = out[c].fillna(0.0).round(2)

    out["capacity_utilization_pct"] = (out["total_stock_units"] / out["warehouse_capacity"] * 100.0).round(2)
    return out.sort_values("inventory_value", ascending=False).reset_index(drop=True)


def build_supplier_summary(
    suppliers: pd.DataFrame,
    purchase_orders: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate PO volume, spend, on-time delivery rate, and actual lead time per supplier."""
    po = purchase_orders.copy()
    po["order_date"] = pd.to_datetime(po["order_date"])
    po["expected_delivery_date"] = pd.to_datetime(po["expected_delivery_date"])
    po["actual_delivery_date"] = pd.to_datetime(po["actual_delivery_date"])

    delivered = po[po["order_status"].isin(["Delivered", "Partial"])].copy()
    delivered["is_on_time"] = delivered["actual_delivery_date"] <= delivered["expected_delivery_date"]
    delivered["actual_lead_days"] = (delivered["actual_delivery_date"] - delivered["order_date"]).dt.days.clip(lower=0)
    delivered["delay_days"] = (delivered["actual_delivery_date"] - delivered["expected_delivery_date"]).dt.days

    sup_agg = delivered.groupby("supplier_id", as_index=False).agg(
        total_delivered_pos=("purchase_order_id", "count"),
        on_time_pos=("is_on_time", "sum"),
        delayed_pos=("is_on_time", lambda s: int((~s).sum())),
        avg_actual_lead_days=("actual_lead_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        total_purchase_spend=("purchase_cost", "sum"),
        total_units_received=("quantity_received", "sum"),
    )

    out = suppliers.merge(sup_agg, on="supplier_id", how="left")
    out["on_time_delivery_rate_pct"] = out.apply(
        lambda r: round(safe_div(r["on_time_pos"] * 100.0, r["total_delivered_pos"], 0.0), 2),
        axis=1,
    )
    out["avg_actual_lead_days"] = out["avg_actual_lead_days"].fillna(out["average_delivery_days"]).round(2)
    out["avg_delay_days"] = out["avg_delay_days"].fillna(0.0).round(2)
    out["total_purchase_spend"] = out["total_purchase_spend"].fillna(0.0).round(2)
    return out.sort_values("on_time_delivery_rate_pct", ascending=False).reset_index(drop=True)


def build_monthly_trends(
    sales: pd.DataFrame,
    movements: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Compute monthly revenue, profit, units sold, purchases, and net stock movement."""
    s = sales.copy()
    s["year_month"] = pd.to_datetime(s["sales_date"]).dt.to_period("M").astype(str)
    cost_map = dict(zip(products["product_id"], products["unit_cost"]))
    s["cogs"] = s["quantity_sold"] * s["product_id"].map(cost_map)

    m_sales = s.groupby("year_month", as_index=False).agg(
        units_sold=("quantity_sold", "sum"),
        revenue=("total_revenue", "sum"),
        cogs=("cogs", "sum"),
        profit=("profit", "sum"),
    )

    m = movements.copy()
    m["year_month"] = pd.to_datetime(m["movement_date"]).dt.to_period("M").astype(str)
    m_purch = (
        m[m["movement_type"] == "Purchase"]
        .groupby("year_month", as_index=False)["quantity"]
        .sum()
        .rename(columns={"quantity": "units_purchased"})
    )

    out = m_sales.merge(m_purch, on="year_month", how="outer").fillna(0).sort_values("year_month")
    out["revenue"] = out["revenue"].round(2)
    out["cogs"] = out["cogs"].round(2)
    out["profit"] = out["profit"].round(2)
    out["units_sold"] = out["units_sold"].astype(int)
    out["units_purchased"] = out["units_purchased"].astype(int)
    return out.reset_index(drop=True)


def export_powerbi_star_schema(cleaned: dict[str, pd.DataFrame], exports_dir: Path | None = None) -> None:
    """Export Power BI-ready star schema tables (Dim* and Fact*) to data/exports/."""
    out_dir = exports_dir or config.EXPORTS_DATA_DIR
    pbi_dir = out_dir / "powerbi"
    pbi_dir.mkdir(parents=True, exist_ok=True)

    # Dimension tables
    cleaned["products"].to_csv(pbi_dir / "DimProduct.csv", index=False)
    cleaned["warehouses"].to_csv(pbi_dir / "DimWarehouse.csv", index=False)
    cleaned["suppliers"].to_csv(pbi_dir / "DimSupplier.csv", index=False)

    # DimDate covering full range
    dates = pd.date_range(config.DATA_START_DATE, config.DATA_END_DATE, freq="D")
    dim_date = pd.DataFrame({
        "date_key": dates.strftime("%Y-%m-%d"),
        "year": dates.year,
        "quarter": "Q" + dates.quarter.astype(str),
        "month_num": dates.month,
        "month_name": dates.strftime("%B"),
        "year_month": dates.strftime("%Y-%m"),
        "day_of_week": dates.strftime("%A"),
        "is_weekend": dates.weekday >= 5,
    })
    dim_date.to_csv(pbi_dir / "DimDate.csv", index=False)

    # Fact tables
    cleaned["sales"].to_csv(pbi_dir / "FactSales.csv", index=False)
    cleaned["inventory_movements"].to_csv(pbi_dir / "FactInventoryMovements.csv", index=False)
    cleaned["purchase_orders"].to_csv(pbi_dir / "FactPurchaseOrders.csv", index=False)


def run_full_analysis(cleaned: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame | dict]:
    """Execute complete KPI, EDA, forecasting, and export pipeline."""
    exports_dir = config.EXPORTS_DATA_DIR
    exports_dir.mkdir(parents=True, exist_ok=True)

    kpis = compute_all_kpis(
        cleaned["products"],
        cleaned["warehouses"],
        cleaned["suppliers"],
        cleaned["inventory_movements"],
        cleaned["sales"],
        cleaned["purchase_orders"],
        cleaned["current_stock"],
    )
    snapshot = compute_product_inventory_snapshot(
        cleaned["products"],
        cleaned["current_stock"],
        cleaned["sales"],
        cleaned["purchase_orders"],
    )
    wh_summary = build_warehouse_summary(
        cleaned["warehouses"], cleaned["products"], cleaned["current_stock"], cleaned["sales"]
    )
    sup_summary = build_supplier_summary(cleaned["suppliers"], cleaned["purchase_orders"])
    monthly_trends = build_monthly_trends(
        cleaned["sales"], cleaned["inventory_movements"], cleaned["products"]
    )
    cat_summary = (
        snapshot.groupby("category", as_index=False)
        .agg(
            sku_count=("product_id", "count"),
            total_stock=("current_stock", "sum"),
            inventory_value=("inventory_value", "sum"),
            total_revenue=("total_revenue", "sum"),
            total_profit=("total_profit", "sum"),
            cogs=("cogs", "sum"),
            avg_turnover=("turnover_ratio", "mean"),
        )
        .sort_values("inventory_value", ascending=False)
        .reset_index(drop=True)
    )
    cat_summary["avg_turnover"] = cat_summary["avg_turnover"].round(2)

    forecast_df, eval_df = evaluate_and_forecast_products(cleaned["sales"], snapshot)

    # Save analytical exports
    with open(exports_dir / "kpi_summary.json", "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)
    snapshot.to_csv(exports_dir / "product_inventory_snapshot.csv", index=False)
    wh_summary.to_csv(exports_dir / "warehouse_summary.csv", index=False)
    sup_summary.to_csv(exports_dir / "supplier_summary.csv", index=False)
    monthly_trends.to_csv(exports_dir / "monthly_trends.csv", index=False)
    cat_summary.to_csv(exports_dir / "category_summary.csv", index=False)
    forecast_df.to_csv(exports_dir / "demand_forecasts.csv", index=False)
    eval_df.to_csv(exports_dir / "forecast_evaluation.csv", index=False)

    export_powerbi_star_schema(cleaned, exports_dir)

    return {
        "kpis": kpis,
        "snapshot": snapshot,
        "warehouse_summary": wh_summary,
        "supplier_summary": sup_summary,
        "monthly_trends": monthly_trends,
        "category_summary": cat_summary,
        "forecasts": forecast_df,
        "forecast_eval": eval_df,
    }
