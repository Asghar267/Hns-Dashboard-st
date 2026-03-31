"""
Pure QR logic helpers (no IO) for calculations and tests.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd


def apply_monthly_split_metrics(df: pd.DataFrame, commission_rate: float) -> pd.DataFrame:
    """Apply split and commission metrics to monthly aggregated dataframe."""
    out = df.copy()
    for col in ["total_sales_all", "total_sales_blinkco"]:
        out[col] = pd.to_numeric(out.get(col, 0), errors="coerce").fillna(0.0)
    for col in ["total_transactions_all", "total_transactions_blinkco"]:
        out[col] = pd.to_numeric(out.get(col, 0), errors="coerce").fillna(0).astype(int)

    out["total_sales_without_blinkco"] = (out["total_sales_all"] - out["total_sales_blinkco"]).clip(lower=0)
    out["total_transactions_without_blinkco"] = (
        out["total_transactions_all"] - out["total_transactions_blinkco"]
    ).clip(lower=0)
    denom = out["total_sales_all"].replace(0, pd.NA)
    out["blinkco_share_pct"] = (out["total_sales_blinkco"] / denom * 100).fillna(0).round(2)
    out["without_blinkco_share_pct"] = (out["total_sales_without_blinkco"] / denom * 100).fillna(0).round(2)
    out["diff_total_minus_blinkco"] = out["total_sales_all"] - out["total_sales_blinkco"]
    out["commission_total_sales"] = out["total_sales_all"] * (commission_rate / 100.0)
    out["commission_blinkco_sales"] = out["total_sales_blinkco"] * (commission_rate / 100.0)
    out["commission_without_blinkco_sales"] = out["total_sales_without_blinkco"] * (commission_rate / 100.0)
    return out


def add_employment_status(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    start_col: str = "employment_start_date",
    end_col: str = "employment_end_date",
) -> pd.DataFrame:
    """Mark active/inactive status in selected window."""
    out = df.copy()
    range_start = pd.to_datetime(start_date, errors="coerce")
    range_end = pd.to_datetime(end_date, errors="coerce")
    out[start_col] = pd.to_datetime(out.get(start_col), errors="coerce")
    out[end_col] = pd.to_datetime(out.get(end_col), errors="coerce")
    start_ok = out[start_col].isna() | (out[start_col] <= range_end)
    end_ok = out[end_col].isna() | (out[end_col] >= range_start)
    out["active_in_range"] = (start_ok & end_ok).fillna(True)
    out["employment_status"] = out["active_in_range"].map(lambda x: "Active" if bool(x) else "Inactive")
    return out


def split_reconciliation_metrics(split_df: pd.DataFrame) -> Dict[str, float]:
    """Return basic reconciliation metrics for split report."""
    if split_df is None or split_df.empty:
        return {"max_row_diff": 0.0, "total_diff": 0.0, "branch_vs_employee_diff": 0.0}

    calc = pd.to_numeric(split_df["total_sales_blinkco"], errors="coerce").fillna(0) + pd.to_numeric(
        split_df["total_sales_without_blinkco"], errors="coerce"
    ).fillna(0)
    total = pd.to_numeric(split_df["total_sales_all"], errors="coerce").fillna(0)
    row_diff = (total - calc).abs()
    total_diff = abs(total.sum() - calc.sum())

    by_employee = total.sum()
    by_branch = pd.to_numeric(split_df.groupby("shop_name")["total_sales_all"].sum(), errors="coerce").fillna(0).sum()
    branch_vs_employee_diff = abs(by_employee - by_branch)
    return {
        "max_row_diff": float(row_diff.max() if len(row_diff) else 0.0),
        "total_diff": float(total_diff),
        "branch_vs_employee_diff": float(branch_vs_employee_diff),
    }

