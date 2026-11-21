# Inventory Analytics – End-to-End Inventory Management and Stock Optimization

## 1. Project Title
**Inventory Analytics – End-to-End Inventory Management and Stock Optimization**

## 2. Project Overview
An end-to-end retail inventory analytics solution combining **Python, Pandas, NumPy, PostgreSQL, SQL, Excel, Power BI, and Streamlit** to reconcile multi-warehouse stock movements, track 20 standardized inventory KPIs, forecast product demand, and optimize replenishment.

## 3. Business Problem
A multi-warehouse retail company faces simultaneous **stockouts on high-velocity products** (14.0% product-warehouse stockout rate) and **excess capital locked in slow-moving and dead stock** ($1.40M dead stock, 50.0% overstocked SKUs), compounded by inconsistent supplier on-time delivery (69.55% OTD).

## 4. Project Objectives
- Reconcile inventory movements (`Purchase`, `Sale`, `Return`, `Adjustment`, `Transfer In`, `Transfer Out`) with zero contradictions.
- Standardize 20 inventory KPIs across Python, SQL, Excel, Streamlit, and Power BI.
- Identify stockout risks, overstocked capital, dead stock, and delayed suppliers.
- Build a transparent walk-forward demand forecasting and reorder recommendation engine.

## 5. Technologies Used
- **Programming & Analysis:** Python 3.11+, Pandas, NumPy, SciPy, Statsmodels
- **Database:** PostgreSQL, SQL, SQLAlchemy, `psycopg2-binary`
- **Visualization & BI:** Matplotlib, Seaborn, Plotly, Streamlit, Microsoft Power BI (DAX, Power Query, Star Schema)
- **Spreadsheets & Testing:** Microsoft Excel (`openpyxl`), Jupyter Notebooks, `pytest`

## 6. Dataset Description
All datasets are **100% synthetic** (`seed=42`), covering **24 months (2024-11-01 to 2026-10-31)**:
- `products.csv` (500 SKUs, 6 categories, 18 subcategories)
- `warehouses.csv` (5 regional facilities, 555,000 total unit capacity)
- `suppliers.csv` (30 suppliers across 5 global regions)
- `inventory_movements.csv` (~22,958 raw / ~22,923 cleaned reconciled movements)
- `sales.csv` (~16,825 raw / ~16,771 cleaned transactions)
- `purchase_orders.csv` (4,864 purchase orders)

## 7. Project Folder Structure
```text
inventory-analytics/
├── data/               # raw/, processed/, exports/ (incl. powerbi/)
├── notebooks/          # 01_data_understanding through 05_business_insights
├── src/                # data_generation, data_cleaning, database, KPIs, analysis, forecasting, visualization
├── sql/                # create_tables, import_data, basic, intermediate, advanced, business_insights (34 queries)
├── excel/              # inventory_analysis_report.xlsx (10 worksheets)
├── dashboard/          # Streamlit app.py, components/, pages/ (6 pages), assets/
├── powerbi/            # data_model.md, dax_measures.md, dashboard_layout.md, theme.json
├── reports/            # figures/ (10 PNG charts) + 4 markdown reports
├── tests/              # Automated unit & integration tests
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── main.py
└── README.md
```

## 8. Data Cleaning Process
Implemented in `src/data_cleaning.py`:
- Deduplicated primary keys (`movement_id`, `sales_id`, `product_id`).
- Standardized category casing and whitespace; imputed missing `brand`, `supplier_rating` (median), `unit_cost` (product lookup), and `discount` (0.0).
- Removed invalid negative sales quantities (`<= 0`) and extreme corrupted outliers (`> 500`), then recomputed `total_revenue` and `profit`.
- Validated all primary/foreign keys and reconciled 2,500 product-warehouse stock balances (`0` negative balances).

## 9. Exploratory Data Analysis
Generated 10 publication-ready figures in `reports/figures/` covering category valuation, warehouse capacity, top 10 products, slow/dead stock capital, monthly revenue/profit trends, supplier OTD, purchase vs. sales, category turnover, stock health status, and category demand trends.

## 10. Inventory KPI Definitions
All 20 KPIs are implemented in `src/inventory_calculations.py`, `sql/`, `excel/inventory_analysis_report.xlsx`, and `powerbi/dax_measures.md`:
- **Inventory Value** = `Current Stock * Unit Cost` (**$8,403,023.94**)
- **Inventory Turnover Ratio** = `COGS / Average Inventory Value` (**2.31x**)
- **Days Inventory Outstanding** = `(Average Inventory Value / COGS) * 730` (**315.4 days**)
- **Gross Profit Margin** = `(Revenue - COGS) / Revenue` (**32.40%**)
- **Supplier On-Time Delivery Rate** = `On-Time POs / Total Delivered POs` (**69.55%**)
- **Reorder Point** = `Avg Daily Demand * Lead Time + Safety Stock`

## 11. PostgreSQL Database Design
Normalized 3NF schema in `sql/create_tables.sql` with primary keys, foreign keys, `CHECK` constraints, `NOT NULL` rules, and 7 performance indexes.

## 12. SQL Analysis
34 documented SQL queries across `basic_analysis.sql` (8), `intermediate_analysis.sql` (8), `advanced_analysis.sql` (8 window-function queries), and `business_insights.sql` (10 executive queries).

## 13. Excel Report
`excel/inventory_analysis_report.xlsx` contains 10 worksheets (`Executive Summary`, `Inventory Overview`, `Product Analysis`, `Warehouse Analysis`, `Supplier Performance`, `Sales Analysis`, `Stock Movement`, `Reorder Analysis`, `KPI Calculations`, `Raw Data`) with live Excel formulas, conditional formatting, status pills, and embedded charts.

## 14. Python Dashboard
6-page dark-navy Streamlit + Plotly dashboard (`dashboard/app.py`) with PostgreSQL connectivity and automatic CSV fallback, global sidebar filters, dynamic KPI cards, and CSV export buttons.

## 15. Power BI Dashboard
Complete Star Schema (`FactSales`, `FactInventoryMovements`, `FactPurchaseOrders`, `DimProduct`, `DimWarehouse`, `DimSupplier`, `DimDate`) exported to `data/exports/powerbi/`, paired with 19 DAX measures (`powerbi/dax_measures.md`), `theme.json`, and 5-page layout guide (`powerbi/dashboard_layout.md`).

## 16. Inventory Forecasting
`src/forecasting.py` benchmarks **SMA-3**, **WMA-3**, and **Simple Exponential Smoothing (SES)** using walk-forward validation on a 3-month holdout window (no future leakage). SES achieved the lowest average error (**MAE 10.98**, **RMSE 12.39**).

## 17. Key Business Insights
- **50.0% Overstock Rate** ($5.19M) coexists with **114 SKUs needing immediate reorder** (8,829 units).
- **$1.40M Dead Stock** across 34 SKUs with zero sales in 180 days.
- **4 of top 5 Electronics SKUs** are currently in Low Stock status.
- **5 delayed suppliers** drag network OTD down to **69.55%**.
- See `reports/inventory_insights.md` for all 16 data-backed insights.

## 18. Business Recommendations
See `reports/recommendations.md` for the 7 prioritized actions (immediate top-SKU POs, dead-stock liquidation, overstock PO freeze, inter-warehouse rebalancing, supplier SLA enforcement, SES dynamic ROPs, and warehouse consolidation).

## 19. Installation Instructions
```bash
git clone <your-repo-url>
cd inventory-analytics
python -m venv venv
# Windows 11:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

## 20. Environment Setup
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials (never commit .env)
```

## 21. Database Configuration
```bash
createdb -U postgres inventory_analytics
psql -U postgres -d inventory_analytics -f sql/create_tables.sql
psql -U postgres -d inventory_analytics -f sql/import_data.sql
```

## 22. How to Run the Project
```bash
# 1. Run end-to-end Python pipeline (generation, cleaning, KPIs, forecasts, charts, Power BI exports)
python main.py

# 2. Launch interactive Streamlit dashboard
streamlit run dashboard/app.py

# 3. Run automated test suite
pytest tests/ -v
```

## 23. Dashboard Screenshots & Analytical Figures
Analytical figures are stored in `reports/figures/`:
- `01_inventory_value_by_category.png`
- `02_stock_levels_by_warehouse.png`
- `03_top_10_selling_products.png`
- `04_slow_moving_and_dead_stock.png`
- `05_monthly_inventory_and_sales_trends.png`
- `06_supplier_delivery_performance.png`
- `07_purchase_vs_sales_analysis.png`
- `08_inventory_turnover_by_category.png`
- `09_stockout_status_breakdown.png`
- `10_product_demand_forecast_sample.png`

## 24. Project Results
- **$31.95M** 24-month revenue | **$10.35M** gross profit (32.40% margin)
- **$8.40M** ending inventory value | **2.31x** turnover | **100%** movement reconciliation accuracy
- **114 SKUs** flagged for **8,829 units** of replenishment; **$1.40M** dead stock identified for liquidation

## 25. Limitations
- Dataset is **synthetic** (generated with `seed=42`) rather than live ERP data.
- Power BI `.pbix` binary requires Windows Power BI Desktop to assemble from the provided `data/exports/powerbi/` star schema, `dax_measures.md`, and `theme.json`.
- Baseline forecasts (SMA/WMA/SES) do not incorporate external promotional calendars.

## 26. Future Improvements
- Add SARIMAX / Prophet seasonal models and safety-stock service-level optimization.
- Automate daily ERP/PostgreSQL ETL with Apache Airflow or Prefect.
- Add automated email/Slack reorder alerts for Critical Stock SKUs.

## 27. Author Information
Developed as a Senior Data Analyst & BI Portfolio Project.
