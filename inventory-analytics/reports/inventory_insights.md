# 16 Data-Backed Business Insights

All findings below are derived directly from the reconciled datasets (`data/exports/`).

1. **Overstocking Ties Up Majority of Capital:** Exactly **250 of 500 SKUs (50.0%)** are classified as Overstocked, holding **$5,187,237.91** (61.7% of total inventory value).
2. **Dead Stock Capital Blockage:** **34 SKUs** have recorded zero sales in the last 180 days, locking **$1,400,886.85** in non-moving capital—led by `PRD-0457` (*OptiGear Active Wi-Fi Camera 457*, 631 units, **$144,732.47**) and `PRD-0499` (*SoundCoreX Compact Laptop Stand 499*, 425 units, **$96,738.50**).
3. **Slow-Moving Inventory Exposure:** **94 SKUs (18.8%)** sold 5 or fewer units in the last 90 days while holding **$4,194,678.11** in stock value (49.9% of total inventory value).
4. **Top Revenue Drivers Are Running Low on Stock:** Four of the top 5 revenue-generating SKUs—`PRD-0331` ($284,509.71), `PRD-0307` ($242,321.48), `PRD-0301` ($233,386.38), and `PRD-0367` ($228,610.20)—are currently in **Low Stock** status.
5. **Immediate Restocking Requirement:** **114 SKUs** fall below target replenishment thresholds, requiring **8,829 units** of immediate restocking (7 SKUs are already in **Critical Stock**).
6. **Electronics Dominates Both Revenue and Capital:** Electronics generates **$9,492,255.06** in revenue (29.7% of total) and holds **$2,816,319.37** in inventory value (33.5% of total), with an average turnover of **6.15x**.
7. **Highest-Turnover Categories:** **Office & Stationery** achieves the highest average SKU turnover (**17.49x**) with **$5,796,936.91** in revenue, followed by **Health & Personal Care** (**14.79x**).
8. **East Coast Mega Hub Leads Sales:** `WH-002` (*East Coast Mega Hub*, Newark) generates the highest revenue (**$8,834,561.49**) and profit (**$2,860,521.50**), despite operating at the lowest capacity utilization (**12.94%**).
9. **Underutilized Warehouse Network:** Overall network capacity utilization is **17.01%** (94,423 units across 555,000 capacity), with `WH-004` (*Southern Distribution*, **20.93%**) and `WH-005` (*Southeast Regional Depot*, **20.21%**) highest, while `WH-005` generates the lowest revenue (**$2,994,245.63**).
10. **Warehouse-Level Stockout Concentration:** Across 2,500 SKU-warehouse pairs, **350 pairs (14.0%)** are at zero stock, concentrated most heavily in `WH-001` (97 stockout SKUs) and `WH-002` (95 stockout SKUs).
11. **Supplier OTD Performance Gap:** Network supplier On-Time Delivery is **69.55%** with an average lead time of **11.74 days**—well below a standard 85% SLA target.
12. **Chronically Delayed Suppliers:** Bottom 5 suppliers—`SUP-029` (*Nexus Partners*, **49.24%** OTD), `SUP-028` (*Vector Imports*, **53.49%**), `SUP-025` (*Zenith Logistics*, **54.71%**), `SUP-030` (*Evergreen Supply Co.*, **54.97%**), and `SUP-027` (*Bridge Distribution*, **55.33%**, 23.28-day avg lead time)—account for severe replenishment delays.
13. **Top-Performing Suppliers:** `SUP-016` (*Crest Imports*, **86.69%** OTD), `SUP-022` (*Liberty Imports*, **84.44%**), and `SUP-010` (*Sterling Imports*, **84.03%**) consistently outperform network averages.
14. **Strong Seasonality & Monthly Demand Shifts:** Monthly revenue peaked in **2025-01** (**$1,756,627.86**, 12,965 units) and reached its lowest point in **2026-10** (**$719,732.90**, 5,389 units), reflecting both seasonal demand waves and late-period stock depletion.
15. **Holding Cost Burden:** At an assumed 20% annual carrying cost rate, two-year holding cost reaches **$3,732,987.03**, representing **36.1%** of total gross profit ($10,352,286.90).
16. **Forecasting Model Benchmark:** Across walk-forward 3-month holdout testing, **Simple Exponential Smoothing (SES)** achieved the lowest average error (**MAE 10.98**, **RMSE 12.39**), outperforming SMA-3 (MAE 11.12, RMSE 12.61) and WMA-3 (MAE 11.46, RMSE 13.00).
