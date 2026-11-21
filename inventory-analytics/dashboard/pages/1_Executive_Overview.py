"""Page 1: Executive Overview."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card, render_sidebar_filters, apply_snapshot_filters

inject_theme()
data, source, kpis, snap, wh_sum, sup_sum, monthly, _ = get_dashboard_data()
filters = render_sidebar_filters(data, snap)
fsnap = apply_snapshot_filters(snap, data, filters)

st.title("Executive Overview")
r1 = st.columns(4)
kpi_card(r1[0], "Total Products", f"{kpis['total_products']:,}", "Active Catalog")
kpi_card(r1[1], "Total Inventory Qty", f"{kpis['total_inventory_quantity']:,}", "Units On Hand")
kpi_card(r1[2], "Total Inventory Value", f"${kpis['total_inventory_value']:,.0f}", "At Unit Cost")
kpi_card(r1[3], "Total Sales Revenue", f"${kpis['total_sales_revenue']:,.0f}", "24-Month Net")

r2 = st.columns(4)
kpi_card(r2[0], "Inventory Turnover", f"{kpis['inventory_turnover_ratio']:.2f}x", f"DIO {kpis['days_inventory_outstanding']:.0f}d")
kpi_card(r2[1], "Stockout Rate", f"{kpis['stockout_rate_pct']:.1f}%", "Product-Warehouse Zeroes")
kpi_card(r2[2], "Total Warehouses", f"{len(data['warehouses'])}", f"Util: {kpis['warehouse_capacity_utilization_pct']:.1f}%")
kpi_card(r2[3], "Total Suppliers", f"{len(data['suppliers'])}", f"OTD: {kpis['supplier_on_time_delivery_rate_pct']:.1f}%")

c1, c2 = st.columns(2)
with c1:
    fig_rev = px.line(monthly, x="year_month", y=["revenue", "profit"], title="Monthly Revenue & Gross Profit ($)", template="plotly_dark")
    st.plotly_chart(fig_rev, use_container_width=True)
with c2:
    cat_df = fsnap.groupby("category", as_index=False)["inventory_value"].sum()
    fig_cat = px.pie(cat_df, names="category", values="inventory_value", hole=0.45, title="Inventory Value by Category", template="plotly_dark")
    st.plotly_chart(fig_cat, use_container_width=True)

fig_wh = px.bar(wh_sum, x="warehouse_name", y=["inventory_value", "total_revenue"], barmode="group", title="Warehouse Comparison: Inventory Value vs Revenue", template="plotly_dark")
st.plotly_chart(fig_wh, use_container_width=True)
