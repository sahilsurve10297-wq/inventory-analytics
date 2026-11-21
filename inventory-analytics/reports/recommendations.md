# Actionable Business Recommendations

1. **Immediate Replenishment of Top-Selling Low/Critical SKUs:** Issue purchase orders for the **114 SKUs** below target stock (**8,829 total units**), prioritizing high-revenue Electronics (`PRD-0331`, `PRD-0307`, `PRD-0301`, `PRD-0367`) and the **7 Critical Stock** items to prevent lost sales.
2. **Liquidate $1.40M in Dead Stock:** Launch targeted clearance bundles, markdowns (20–35%), or B2B liquidation for the **34 Dead Stock SKUs** (starting with `PRD-0457` at $144.7K and `PRD-0499` at $96.7K) to free working capital and cut annual holding costs by ~$280K/year.
3. **Freeze Reorders on Overstocked SKUs:** Implement automated PO blocks for the **250 Overstocked SKUs** ($5.19M value) until on-hand quantities drop below `1.5x` reorder level.
4. **Rebalance Stock Across Warehouses:** Transfer slow-moving or excess units from `WH-004` and `WH-005` into high-velocity fulfillment centers (`WH-002` Newark and `WH-001` Chicago) where 95 and 97 SKUs are currently stocked out.
5. **Renegotiate or Reallocate Volume from Delayed Suppliers:** Place `SUP-029` (49.24% OTD), `SUP-028` (53.49% OTD), `SUP-025` (54.71% OTD), and `SUP-027` (23.28-day lead time) on formal SLA corrective plans, shifting volume toward `SUP-016` (86.69% OTD) and `SUP-022` (84.44% OTD).
6. **Adopt SES Dynamic Reorder Points:** Replace static reorder levels with monthly **Simple Exponential Smoothing (SES)** demand forecasts (lowest holdout RMSE of 12.39) plus supplier-specific lead-time buffers.
7. **Consolidate Underutilized Warehouse Space:** With network capacity utilization at **17.01%**, evaluate subleasing excess capacity at `WH-002` (12.94% utilized) or consolidating low-volume regional storage to reduce fixed facility overhead.
