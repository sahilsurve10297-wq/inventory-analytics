"""Page 2: Inventory Analysis."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card, render_sidebar_filters, apply_snapshot_filters

inject_theme()
data, _, kpis, snap, _, _, _, _ = get_dashboard_data()
filters = render_sidebar_filters(data, snap)
fsnap = apply_snapshot_filters(snap, data, filters)

st.title("Inventory Analysis")
c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Current Stock", f"{fsnap['current_stock'].sum():,}", "Units")
kpi_card(c2, "Inventory Value", f"${fsnap['inventory_value'].sum():,.0f}", "Filtered View")
kpi_card(c3, "Overstocked SKUs", f"{(fsnap['stock_status'] == 'Overstocked').sum()}", f"{kpis['overstock_rate_pct']:.1f}% Network")
kpi_card(c4, "Dead Stock Value", f"${fsnap.loc[fsnap['stock_status'] == 'Dead Stock', 'inventory_value'].sum():,.0f}", "Zero 180d Sales")

col_a, col_b = st.columns(2)
with col_a:
    st_df = fsnap.groupby("stock_status", as_index=False)["inventory_value"].sum()
    st.plotly_chart(px.bar(st_df, x="stock_status", y="inventory_value", color="stock_status", title="Inventory Value by Stock Status", template="plotly_dark"), use_container_width=True)
with col_b:
    cat_df = fsnap.groupby("category", as_index=False).agg(stock=("current_stock", "sum"), val=("inventory_value", "sum"))
    st.plotly_chart(px.bar(cat_df, x="category", y="val", title="Category Inventory Capital", template="plotly_dark"), use_container_width=True)

st.subheader("Slow-Moving & Overstocked Products")
slow_over = fsnap[fsnap["is_slow_moving"] | (fsnap["stock_status"] == "Overstocked")].sort_values("inventory_value", ascending=False)
st.dataframe(slow_over[["product_id", "product_name", "category", "current_stock", "inventory_value", "units_sold_90d", "stock_status"]], use_container_width=True)
st.download_button("Export Slow/Overstocked CSV", slow_over.to_csv(index=False).encode("utf-8"), "slow_overstocked.csv", "text/csv")
