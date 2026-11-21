"""End-to-end orchestrator for the Inventory Analytics pipeline."""

from __future__ import annotations

import config
from src.data_generation import generate_all_datasets
from src.data_cleaning import run_cleaning_pipeline
from src.analysis import run_full_analysis
from src.visualization import generate_all_charts


def main() -> None:
    print("1/4 Generating synthetic raw datasets...")
    generate_all_datasets(config.RAW_DATA_DIR)

    print("2/4 Running data cleaning and inventory reconciliation...")
    cleaned, audit = run_cleaning_pipeline(config.RAW_DATA_DIR, config.PROCESSED_DATA_DIR)
    print(f"    Reconciled {audit['reconciled_pairs']} product-warehouse pairs "
          f"(negative stock pairs: {audit['negative_stock_pairs']})")

    print("3/4 Computing 20 KPIs, EDA summaries, forecasts, and Power BI exports...")
    results = run_full_analysis(cleaned)
    kpis = results["kpis"]
    print(f"    Total Inventory Value: ${kpis['total_inventory_value']:,.2f} | "
          f"Revenue: ${kpis['total_sales_revenue']:,.2f} | "
          f"Turnover: {kpis['inventory_turnover_ratio']}x")

    print("4/4 Generating analytical charts in reports/figures/...")
    charts = generate_all_charts(results, cleaned, config.FIGURES_DIR)
    print(f"    Saved {len(charts)} charts.")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
