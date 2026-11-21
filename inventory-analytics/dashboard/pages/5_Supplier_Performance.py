"""Page 5: Supplier Performance."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card

inject_theme()
_, _, kpis, _, _, sup_sum, _, _ = get_dashboard_data()

st.title("Supplier Performance")
c1, c2, c3 = st.columns(3)
kpi_card(c1, "Network OTD Rate", f"{kpis['supplier_on_time_delivery_rate_pct']:.1f}%", "On-Time Delivered POs")
kpi_card(c2, "Avg Supplier Lead Time", f"{kpis['average_supplier_lead_time_days']:.1f} days", "Order to Delivery")
kpi_card(c3, "Total Purchase Spend", f"${sup_sum['total_purchase_spend'].sum():,.0f}", "Delivered PO Value")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.bar(sup_sum.sort_values("on_time_delivery_rate_pct"), x="on_time_delivery_rate_pct", y="supplier_name", orientation="h", color="supplier_status", title="Supplier On-Time Delivery Rate (%)", template="plotly_dark"), use_container_width=True)
with col2:
    st.plotly_chart(px.scatter(sup_sum, x="avg_actual_lead_days", y="supplier_rating", size="total_purchase_spend", color="supplier_status", hover_name="supplier_name", title="Lead Time vs Rating", template="plotly_dark"), use_container_width=True)

st.dataframe(sup_sum, use_container_width=True)
