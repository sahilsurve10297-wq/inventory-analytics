"""Page 6: Stock Optimization & Forecasting."""

import plotly.express as px
import streamlit as st
from components.metrics import inject_theme, get_dashboard_data, kpi_card, render_sidebar_filters, apply_snapshot_filters

inject_theme()
data, _, kpis, snap, _, _, _, forecasts = get_dashboard_data()
filters = render_sidebar_filters(data, snap)
fsnap = apply_snapshot_filters(snap, data, filters)

st.title("Stock Optimization & Demand Forecasting")
reorder_df = fsnap[fsnap["suggested_reorder_qty"] > 0].sort_values("suggested_reorder_qty", ascending=False)
below_ss = fsnap[fsnap["current_stock"] < fsnap["safety_stock"]]

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "SKUs Needing Reorder", f"{len(reorder_df)}", f"{reorder_df['suggested_reorder_qty'].sum():,} units")
kpi_card(c2, "Below Safety Stock", f"{len(below_ss)}", "Immediate Risk")
kpi_card(c3, "Dead Stock SKUs", f"{(fsnap['stock_status'] == 'Dead Stock').sum()}", "Liquidation Candidates")
kpi_card(c4, "High Stockout Risk (30d)", f"{(forecasts['future_stockout_risk'] == 'High Risk').sum()}", "Forecasted < Lead Time")

st.subheader("Immediate Reorder Recommendations")
st.dataframe(reorder_df[["product_id", "product_name", "category", "current_stock", "safety_stock", "calculated_rop", "open_po_qty", "suggested_reorder_qty", "stock_status"]], use_container_width=True)
st.download_button("Download Reorder Plan (CSV)", reorder_df.to_csv(index=False).encode("utf-8"), "reorder_plan.csv", "text/csv")

st.subheader("30-Day Demand Forecast & Stockout Risk")
st.plotly_chart(px.histogram(forecasts, x="future_stockout_risk", color="future_stockout_risk", title="Forecasted 30-Day Stockout Risk Distribution", template="plotly_dark"), use_container_width=True)
st.dataframe(forecasts.sort_values("days_of_supply").head(50), use_container_width=True)
