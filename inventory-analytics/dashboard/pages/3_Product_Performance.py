"""Page 3: Product Performance."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, render_sidebar_filters, apply_snapshot_filters

inject_theme()
data, _, _, snap, _, _, _, _ = get_dashboard_data()
filters = render_sidebar_filters(data, snap)
fsnap = apply_snapshot_filters(snap, data, filters)

st.title("Product Performance")
c1, c2 = st.columns(2)
with c1:
    top10 = fsnap.nlargest(10, "total_revenue")
    st.plotly_chart(px.bar(top10, y="product_name", x="total_revenue", orientation="h", title="Top 10 Products by Revenue", template="plotly_dark"), use_container_width=True)
with c2:
    bot10 = fsnap[fsnap["total_revenue"] > 0].nsmallest(10, "total_revenue")
    st.plotly_chart(px.bar(bot10, y="product_name", x="total_revenue", orientation="h", title="Bottom 10 Selling Products", template="plotly_dark"), use_container_width=True)

st.plotly_chart(
    px.scatter(fsnap, x="turnover_ratio", y="total_profit", size="inventory_value", color="category", hover_name="product_name", title="Product Profitability vs Inventory Turnover", template="plotly_dark"),
    use_container_width=True,
)
st.dataframe(fsnap[["product_id", "product_name", "category", "total_units_sold", "total_revenue", "total_profit", "turnover_ratio", "stock_status"]], use_container_width=True)
