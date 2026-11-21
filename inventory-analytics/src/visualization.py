"""Publication-quality static charts saved to reports/figures/."""

from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import config

NAVY = "#0F2744"
BLUE = "#1F6FEB"
TEAL = "#0EA5E9"
AMBER = "#F59E0B"
CORAL = "#EF4444"
GREEN = "#10B981"
SLATE = "#64748B"

sns.set_theme(style="whitegrid", font_scale=1.05)


def _save_fig(fig: plt.Figure, out_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def generate_all_charts(results: dict, cleaned: dict, figures_dir: Path | None = None) -> list[Path]:
    """Generate all 10 required analytical charts and save to reports/figures/."""
    out_dir = figures_dir or config.FIGURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    cat_df = results["category_summary"]
    wh_df = results["warehouse_summary"]
    snap_df = results["snapshot"]
    sup_df = results["supplier_summary"]
    monthly_df = results["monthly_trends"]
    sales_df = cleaned["sales"]

    # 1. Inventory Value by Category
    fig, ax = plt.subplots(figsize=(9, 5))
    d1 = cat_df.sort_values("inventory_value", ascending=True)
    ax.barh(d1["category"], d1["inventory_value"], color=BLUE)
    ax.set_title("Inventory Value by Product Category ($)", fontweight="bold", color=NAVY)
    ax.set_xlabel("Inventory Value ($)")
    for i, v in enumerate(d1["inventory_value"]):
        ax.text(v + max(d1["inventory_value"]) * 0.01, i, f"${v:,.0f}", va="center", fontsize=9)
    p = out_dir / "01_inventory_value_by_category.png"
    _save_fig(fig, p)
    saved.append(p)

    # 2. Stock Levels & Capacity by Warehouse
    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(wh_df))
    ax.bar(x, wh_df["total_stock_units"], width=0.45, label="Current Stock (Units)", color=NAVY)
    ax.bar([i + 0.45 for i in x], wh_df["warehouse_capacity"], width=0.45, label="Capacity (Units)", color=TEAL, alpha=0.55)
    ax.set_xticks([i + 0.225 for i in x])
    ax.set_xticklabels(wh_df["warehouse_name"], rotation=15, ha="right")
    ax.set_title("Stock Levels vs. Warehouse Capacity", fontweight="bold", color=NAVY)
    ax.set_ylabel("Units")
    ax.legend()
    p = out_dir / "02_stock_levels_by_warehouse.png"
    _save_fig(fig, p)
    saved.append(p)

    # 3. Top 10 Selling Products by Revenue
    fig, ax = plt.subplots(figsize=(10, 5.5))
    top10 = snap_df.nlargest(10, "total_revenue").sort_values("total_revenue", ascending=True)
    ax.barh(top10["product_name"], top10["total_revenue"], color=GREEN)
    ax.set_title("Top 10 Selling Products by Revenue ($)", fontweight="bold", color=NAVY)
    ax.set_xlabel("Total Revenue ($)")
    p = out_dir / "03_top_10_selling_products.png"
    _save_fig(fig, p)
    saved.append(p)

    # 4. Slow-Moving & Dead Stock Capital Blockage by Category
    fig, ax = plt.subplots(figsize=(9, 5))
    slow_cat = (
        snap_df[snap_df["is_slow_moving"] | (snap_df["stock_status"] == "Dead Stock")]
        .groupby("category", as_index=False)["inventory_value"]
        .sum()
        .sort_values("inventory_value", ascending=True)
    )
    ax.barh(slow_cat["category"], slow_cat["inventory_value"], color=AMBER)
    ax.set_title("Capital Blocked in Slow-Moving & Dead Stock by Category ($)", fontweight="bold", color=NAVY)
    ax.set_xlabel("Blocked Capital ($)")
    p = out_dir / "04_slow_moving_and_dead_stock.png"
    _save_fig(fig, p)
    saved.append(p)

    # 5. Monthly Revenue & Profit Trends
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly_df["year_month"], monthly_df["revenue"], marker="o", color=BLUE, linewidth=2.2, label="Monthly Revenue")
    ax.plot(monthly_df["year_month"], monthly_df["profit"], marker="s", color=GREEN, linewidth=2.0, label="Gross Profit")
    ax.set_title("Monthly Sales Revenue & Gross Profit Trend (24 Months)", fontweight="bold", color=NAVY)
    ax.set_ylabel("Amount ($)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    p = out_dir / "05_monthly_inventory_and_sales_trends.png"
    _save_fig(fig, p)
    saved.append(p)

    # 6. Supplier Delivery Performance (Bottom 10 vs Top 10 OTD)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sup_plot = pd.concat([sup_df.head(6), sup_df.tail(6)]).drop_duplicates("supplier_id").sort_values("on_time_delivery_rate_pct")
    colors = [CORAL if v < 75 else BLUE for v in sup_plot["on_time_delivery_rate_pct"]]
    ax.barh(sup_plot["supplier_name"], sup_plot["on_time_delivery_rate_pct"], color=colors)
    ax.axvline(85, color=SLATE, linestyle="--", linewidth=1.2, label="85% Target SLA")
    ax.set_title("Supplier On-Time Delivery Rate (%) — Best & Worst Performers", fontweight="bold", color=NAVY)
    ax.set_xlabel("On-Time Delivery Rate (%)")
    ax.legend()
    p = out_dir / "06_supplier_delivery_performance.png"
    _save_fig(fig, p)
    saved.append(p)

    # 7. Purchase vs Sales Quantities Monthly
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly_df["year_month"], monthly_df["units_purchased"], marker="^", color=NAVY, label="Units Purchased")
    ax.plot(monthly_df["year_month"], monthly_df["units_sold"], marker="o", color=TEAL, label="Units Sold")
    ax.set_title("Monthly Units Purchased vs. Units Sold", fontweight="bold", color=NAVY)
    ax.set_ylabel("Units")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    p = out_dir / "07_purchase_vs_sales_analysis.png"
    _save_fig(fig, p)
    saved.append(p)

    # 8. Inventory Turnover Comparison by Category
    fig, ax = plt.subplots(figsize=(9, 5))
    d8 = cat_df.sort_values("avg_turnover", ascending=True)
    ax.barh(d8["category"], d8["avg_turnover"], color=TEAL)
    ax.set_title("Average Inventory Turnover Ratio by Category", fontweight="bold", color=NAVY)
    ax.set_xlabel("Turnover Ratio (COGS / Inventory Value)")
    p = out_dir / "08_inventory_turnover_by_category.png"
    _save_fig(fig, p)
    saved.append(p)

    # 9. Stock Status Distribution (Stockout, Low, Healthy, Overstocked, Dead)
    fig, ax = plt.subplots(figsize=(8, 5))
    status_counts = snap_df["stock_status"].value_counts()
    palette = {
        "Critical Stock": CORAL,
        "Low Stock": AMBER,
        "Healthy Stock": GREEN,
        "Overstocked": BLUE,
        "Dead Stock": SLATE,
    }
    bar_colors = [palette.get(s, BLUE) for s in status_counts.index]
    ax.bar(status_counts.index, status_counts.values, color=bar_colors)
    ax.set_title("SKU Count by Stock Health Status", fontweight="bold", color=NAVY)
    ax.set_ylabel("Number of SKUs")
    p = out_dir / "09_stockout_status_breakdown.png"
    _save_fig(fig, p)
    saved.append(p)

    # 10. Top Category Monthly Demand Trend
    fig, ax = plt.subplots(figsize=(11, 5))
    s = sales_df.merge(cleaned["products"][["product_id", "category"]], on="product_id", how="left")
    s["year_month"] = pd.to_datetime(s["sales_date"]).dt.to_period("M").astype(str)
    cat_m = s.groupby(["year_month", "category"], as_index=False)["quantity_sold"].sum()
    for cat, grp in cat_m.groupby("category"):
        grp = grp.sort_values("year_month")
        ax.plot(grp["year_month"], grp["quantity_sold"], label=cat, linewidth=1.8)
    ax.set_title("Monthly Demand Trend by Product Category", fontweight="bold", color=NAVY)
    ax.set_ylabel("Units Sold")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(ncol=2, fontsize=8.5)
    p = out_dir / "10_product_demand_forecast_sample.png"
    _save_fig(fig, p)
    saved.append(p)

    return saved
