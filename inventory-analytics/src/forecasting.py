"""Inventory demand forecasting and stockout risk module.

Implements transparent, no-leakage baseline forecasting methods:
- Simple Moving Average (SMA-3)
- Weighted Moving Average (WMA-3)
- Simple Exponential Smoothing (SES, alpha=0.35)
Evaluates walk-forward MAE and RMSE on a 3-month holdout window.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _sma_forecast(series: np.ndarray, window: int = 3) -> float:
    if len(series) == 0:
        return 0.0
    return float(np.mean(series[-window:]))


def _wma_forecast(series: np.ndarray, weights: tuple[float, ...] = (0.2, 0.3, 0.5)) -> float:
    if len(series) == 0:
        return 0.0
    if len(series) < len(weights):
        return float(np.mean(series))
    return float(np.dot(series[-len(weights):], weights))


def _ses_forecast(series: np.ndarray, alpha: float = 0.35) -> float:
    if len(series) == 0:
        return 0.0
    level = float(series[0])
    for val in series[1:]:
        level = alpha * float(val) + (1.0 - alpha) * level
    return level


def evaluate_and_forecast_products(
    sales: pd.DataFrame,
    snapshot: pd.DataFrame,
    holdout_months: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run walk-forward validation on monthly product demand and forecast next 30 days."""
    s = sales.copy()
    s["sales_date"] = pd.to_datetime(s["sales_date"])
    s["year_month"] = s["sales_date"].dt.to_period("M")

    all_months = sorted(s["year_month"].unique())
    monthly = (
        s.groupby(["product_id", "year_month"], as_index=False)["quantity_sold"]
        .sum()
    )

    pivot = monthly.pivot(index="product_id", columns="year_month", values="quantity_sold").fillna(0.0)
    for m in all_months:
        if m not in pivot.columns:
            pivot[m] = 0.0
    pivot = pivot[all_months]

    eval_rows = []
    forecast_rows = []

    for pid, row in pivot.iterrows():
        vals = row.values.astype(float)
        n = len(vals)
        split = max(3, n - holdout_months)

        # Walk-forward evaluation without future leakage
        sma_errs, wma_errs, ses_errs = [], [], []
        for t in range(split, n):
            hist = vals[:t]
            actual = vals[t]
            sma_errs.append(actual - _sma_forecast(hist))
            wma_errs.append(actual - _wma_forecast(hist))
            ses_errs.append(actual - _ses_forecast(hist))

        def metrics(errs: list[float]) -> tuple[float, float]:
            arr = np.array(errs, dtype=float)
            return float(np.mean(np.abs(arr))), float(np.sqrt(np.mean(arr ** 2)))

        sma_mae, sma_rmse = metrics(sma_errs)
        wma_mae, wma_rmse = metrics(wma_errs)
        ses_mae, ses_rmse = metrics(ses_errs)

        best_method = min(
            [("SMA-3", sma_rmse), ("WMA-3", wma_rmse), ("SES", ses_rmse)],
            key=lambda x: x[1],
        )[0]

        next_sma = _sma_forecast(vals)
        next_wma = _wma_forecast(vals)
        next_ses = _ses_forecast(vals)
        best_forecast = {"SMA-3": next_sma, "WMA-3": next_wma, "SES": next_ses}[best_method]

        eval_rows.append({
            "product_id": pid,
            "sma_mae": round(sma_mae, 2),
            "sma_rmse": round(sma_rmse, 2),
            "wma_mae": round(wma_mae, 2),
            "wma_rmse": round(wma_rmse, 2),
            "ses_mae": round(ses_mae, 2),
            "ses_rmse": round(ses_rmse, 2),
            "best_method": best_method,
        })

        forecast_rows.append({
            "product_id": pid,
            "forecast_30d_units": round(best_forecast, 1),
            "forecast_daily_demand": round(best_forecast / 30.0, 3),
            "best_method": best_method,
            "rmse": round(min(sma_rmse, wma_rmse, ses_rmse), 2),
        })

    eval_df = pd.DataFrame(eval_rows)
    fc_df = pd.DataFrame(forecast_rows)

    merged = snapshot[
        ["product_id", "product_name", "category", "current_stock", "safety_stock", "reorder_level", "lead_time_days", "unit_cost"]
    ].merge(fc_df, on="product_id", how="left")
    merged["forecast_30d_units"] = merged["forecast_30d_units"].fillna(0.0)
    merged["forecast_daily_demand"] = merged["forecast_daily_demand"].fillna(0.0)
    merged["days_of_supply"] = np.where(
        merged["forecast_daily_demand"] > 0,
        np.round(merged["current_stock"] / merged["forecast_daily_demand"], 1),
        999.0,
    )
    merged["future_stockout_risk"] = np.where(
        merged["days_of_supply"] < merged["lead_time_days"],
        "High Risk",
        np.where(merged["days_of_supply"] < (merged["lead_time_days"] + 14), "Medium Risk", "Low Risk"),
    )
    return merged, eval_df
