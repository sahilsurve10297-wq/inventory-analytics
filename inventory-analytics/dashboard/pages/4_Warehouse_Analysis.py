"""Page 4: Warehouse Analysis."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card

inject_theme()
_, _, _, _, wh_sum, _, _, _ = get_dashboard_data()

st.title("Warehouse Analysis")
cols = st.columns(len(wh_sum))
for idx, (_, r) in enumerate(wh_sum.iterrows()):
    kpi_card(cols[idx], r["warehouse_name"], f"{r['capacity_utilization_pct']:.1f}%", f"Value: ${r['inventory_value']:,.0f}")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(px.bar(wh_sum, x="warehouse_name", y=["total_stock_units", "warehouse_capacity"], barmode="group", title="Stock Units vs Capacity", template="plotly_dark"), use_container_width=True)
with c2:
    st.plotly_chart(px.bar(wh_sum, x="warehouse_name", y=["total_revenue", "total_profit"], barmode="group", title="Warehouse Sales & Profit", template="plotly_dark"), use_container_width=True)

st.dataframe(wh_sum, use_container_width=True)
