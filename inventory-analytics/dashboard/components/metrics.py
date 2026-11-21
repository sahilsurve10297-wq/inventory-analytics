"""Reusable Streamlit UI components and data loading helpers."""

from __future__ import annotations

import pathlib
import sys
import pandas as pd
import streamlit as st

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database import load_data_with_fallback
from src.inventory_calculations import compute_all_kpis, compute_product_inventory_snapshot
from src.analysis import build_warehouse_summary, build_supplier_summary, build_monthly_trends
from src.forecasting import evaluate_and_forecast_products


def inject_theme() -> None:
    css_path = ROOT_DIR / "dashboard" / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def kpi_card(col, label: str, value: str, subtitle: str = "") -> None:
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def get_dashboard_data():
    data, source = load_data_with_fallback()
    kpis = compute_all_kpis(
        data["products"], data["warehouses"], data["suppliers"],
        data["inventory_movements"], data["sales"], data["purchase_orders"], data["current_stock"],
    )
    snap = compute_product_inventory_snapshot(
        data["products"], data["current_stock"], data["sales"], data["purchase_orders"]
    )
    wh_sum = build_warehouse_summary(data["warehouses"], data["products"], data["current_stock"], data["sales"])
    sup_sum = build_supplier_summary(data["suppliers"], data["purchase_orders"])
    monthly = build_monthly_trends(data["sales"], data["inventory_movements"], data["products"])
    forecasts, _ = evaluate_and_forecast_products(data["sales"], snap)
    return data, source, kpis, snap, wh_sum, sup_sum, monthly, forecasts


def render_sidebar_filters(data: dict, snap: pd.DataFrame):
    st.sidebar.header("Global Filters")
    sales_dates = pd.to_datetime(data["sales"]["sales_date"])
    min_d, max_d = sales_dates.min().date(), sales_dates.max().date()
    date_range = st.sidebar.date_input("Sales Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    cats = ["All"] + sorted(data["products"]["category"].unique().tolist())
    sel_cat = st.sidebar.selectbox("Product Category", cats)

    whs = ["All"] + sorted(data["warehouses"]["warehouse_name"].unique().tolist())
    sel_wh = st.sidebar.selectbox("Warehouse", whs)

    sups = ["All"] + sorted(data["suppliers"]["supplier_name"].unique().tolist())
    sel_sup = st.sidebar.selectbox("Supplier", sups)

    statuses = ["All"] + sorted(snap["stock_status"].unique().tolist())
    sel_status = st.sidebar.selectbox("Stock Status", statuses)

    return {
        "date_range": date_range,
        "category": sel_cat,
        "warehouse": sel_wh,
        "supplier": sel_sup,
        "status": sel_status,
    }


def apply_snapshot_filters(snap: pd.DataFrame, data: dict, filters: dict) -> pd.DataFrame:
    df = snap.copy()
    if filters["category"] != "All":
        df = df[df["category"] == filters["category"]]
    if filters["supplier"] != "All":
        sup_id = data["suppliers"].loc[data["suppliers"]["supplier_name"] == filters["supplier"], "supplier_id"].iloc[0]
        df = df[df["supplier_id"] == sup_id]
    if filters["status"] != "All":
        df = df[df["stock_status"] == filters["status"]]
    return df
