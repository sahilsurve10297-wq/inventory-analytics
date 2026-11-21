# Power BI Dashboard Layout & Recreation Guide

> **Environment Note**: Power BI Desktop is a Windows-only desktop application and is not installed in this Linux sandbox environment. Therefore, no `.pbix` binary file was fabricated. Instead, `data/exports/powerbi/` contains all 7 pre-cleaned star-schema CSVs, `theme.json` provides the dark navy/blue theme, `dax_measures.md` provides all 19 DAX measures, and this guide documents every page and visual for 1-click recreation in Power BI Desktop.

## Global Design & Interactivity
- **Theme**: Import `powerbi/theme.json` (`View` -> `Themes` -> `Browse for themes`).
- **Top Slicer Bar** (synced across all 5 pages): `DimDate[year_month]`, `DimWarehouse[warehouse_name]`, `DimProduct[category]`, `DimSupplier[supplier_name]`.
- **Drill-Through**: Configure a `Product Detail` drill-through target on Page 3 (`DimProduct[product_id]`).
- **Custom Tooltips**: Bind `Total Revenue`, `Total Stock Quantity`, `Inventory Turnover`, and `Stockout Rate` to chart tooltips.

## Page 1: Executive Summary
- **Top KPI Row (5 Cards)**: `Total Inventory Value`, `Total Stock Quantity`, `Total Revenue`, `Inventory Turnover`, `Stockout Rate`.
- **Left Visual**: Line & Clustered Column Chart — `DimDate[year_month]` vs. `Total Revenue` & `Monthly Sales Growth`.
- **Right Visual**: Donut Chart — `Total Inventory Value` by `DimProduct[category]`.
- **Bottom Table**: Category scorecard (`Total Products`, `Total Stock Quantity`, `Total Inventory Value`, `Total Revenue`, `Inventory Turnover`).

## Page 2: Inventory Performance
- **KPI Row**: `Overstock Rate`, `Dead Stock Value`, `Slow-Moving Inventory Value`, `Days Inventory Outstanding`.
- **Visual 1**: Stacked Bar Chart — `Total Inventory Value` by `DimProduct[category]`.
- **Visual 2**: Funnel / Bar Chart — SKU Count by Stock Health Status (`Critical Stock`, `Low Stock`, `Healthy Stock`, `Overstocked`, `Dead Stock`).
- **Visual 3**: Matrix — `DimProduct[category]` -> `DimProduct[subcategory]` showing `Total Stock Quantity`, `Total Inventory Value`, `Dead Stock Value`.

## Page 3: Product Analysis
- **Visual 1**: Horizontal Bar Chart — Top 10 Products by `Total Revenue`.
- **Visual 2**: Scatter Chart — `Inventory Turnover` (X) vs. `Total Profit` (Y), sized by `Total Inventory Value`.
- **Visual 3**: Table — Slow-moving & Dead Stock SKUs with conditional formatting on `Total Inventory Value`.
- **Visual 4**: Table — `Reorder Required Products` alert list (`Total Stock Quantity`, `reorder_level`, `safety_stock`).

## Page 4: Warehouse Analysis
- **Visual 1**: Clustered Bar Chart — `Total Stock Quantity` vs. `warehouse_capacity` by `DimWarehouse[warehouse_name]`.
- **Visual 2**: Gauge / KPI Cards — `Warehouse Capacity Utilization` per warehouse.
- **Visual 3**: Clustered Column Chart — `Total Revenue` and `Total Profit` by `DimWarehouse[warehouse_name]`.

## Page 5: Supplier and Procurement
- **KPI Row**: `Supplier On-Time Delivery Rate`, Average Lead Time, Total Purchase Spend.
- **Visual 1**: Horizontal Bar Chart — `Supplier On-Time Delivery Rate` by `DimSupplier[supplier_name]` with 85% reference line.
- **Visual 2**: Donut Chart — `FactPurchaseOrders` count by `order_status`.
- **Visual 3**: Scatter Chart — `average_delivery_days` vs. `supplier_rating`, sized by `purchase_cost`.
- **Visual 4**: Table — Supplier Scorecard ranking with conditional formatting on OTD%.
