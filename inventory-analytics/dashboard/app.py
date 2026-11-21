"""Inventory Analytics — Multi-Page Streamlit Dashboard."""

import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card, render_sidebar_filters, apply_snapshot_filters

st.set_page_config(
    page_title="Inventory Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

data, source, kpis, snap, wh_sum, sup_sum, monthly, forecasts = get_dashboard_data()
filters = render_sidebar_filters(data, snap)
filtered_snap = apply_snapshot_filters(snap, data, filters)

st.title("📦 Inventory Analytics & Stock Optimization")
st.caption(f"Data Source: **{source}** | Active SKUs in View: **{len(filtered_snap)}** of **{kpis['total_products']}**")

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Total Products", f"{len(filtered_snap):,}", "Active SKUs")
kpi_card(c2, "Inventory Value", f"${filtered_snap['inventory_value'].sum():,.0f}", f"{filtered_snap['current_stock'].sum():,} units")
kpi_card(c3, "Sales Revenue", f"${filtered_snap['total_revenue'].sum():,.0f}", f"Gross Margin {kpis['gross_profit_margin_pct']:.1f}%")
kpi_card(c4, "Inventory Turnover", f"{kpis['inventory_turnover_ratio']:.2f}x", f"DIO: {kpis['days_inventory_outstanding']:.0f} days")

st.info("Use the sidebar navigation to explore all 6 analytical pages: Executive Overview, Inventory Analysis, Product Performance, Warehouse Analysis, Supplier Performance, and Stock Optimization.")

st.download_button(
    "Download Filtered SKU Snapshot (CSV)",
    data=filtered_snap.to_csv(index=False).encode("utf-8"),
    file_name="filtered_inventory_snapshot.csv",
    mime="text/csv",
)
