"""
QR reconciliation checks:
1) total = blinkco + non-blinkco
2) employee-sum vs branch-sum
3) dashboard-vs-report-file parity (optional)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

import pandas as pd

from modules.qr_logic import split_reconciliation_metrics
from services.qr_commission_service import QRCommissionService


def _read_report(path: str) -> pd.DataFrame:
    if not path:
        return pd.DataFrame()
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def _normalize_for_parity(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    key_cols = ["employee_id", "shop_name"]
    for col in key_cols:
        if col not in out.columns:
            out[col] = ""
    for col in ["total_sales_all", "total_sales_blinkco", "total_sales_without_blinkco"]:
        out[col] = pd.to_numeric(out.get(col, 0), errors="coerce").fillna(0.0)
    return out[key_cols + ["total_sales_all", "total_sales_blinkco", "total_sales_without_blinkco"]]


def run_checks(
    start_date: str,
    end_exclusive: str,
    branches: List[int],
    mode: str,
    commission_rate: float,
    report_file: str = "",
) -> int:
    if str(mode).lower() == "unfiltered":
        mode = "Complete"

    svc = QRCommissionService()
    df_qr = svc.get_qr_commission_data(start_date, end_exclusive, branches, mode)
    df_total = svc.get_total_sales_data(start_date, end_exclusive, branches, mode)
    df_raw = svc.get_blink_raw_orders_for_qr_sales(start_date, end_exclusive, branches, mode)
    df_merged = svc.process_qr_data(df_qr, df_raw, commission_rate)

    if not df_merged.empty:
        blink = (
            df_merged.groupby(["employee_id", "employee_name", "shop_id", "shop_name"], as_index=False)
            .agg(total_sales_blinkco=("total_sale", "sum"), total_transactions_blinkco=("sale_id", "count"))
        )
    else:
        blink = pd.DataFrame(columns=["employee_id", "employee_name", "shop_id", "shop_name", "total_sales_blinkco", "total_transactions_blinkco"])
    split = svc.get_split_report(df_total, blink, commission_rate)

    print("=== QR Reconciliation ===")
    print(f"Rows: {len(split)}")
    metrics = split_reconciliation_metrics(split)
    print(f"max_row_diff: {metrics['max_row_diff']:.4f}")
    print(f"total_diff: {metrics['total_diff']:.4f}")
    print(f"branch_vs_employee_diff: {metrics['branch_vs_employee_diff']:.4f}")

    failures = []
    if metrics["max_row_diff"] > 0.01:
        failures.append(f"Row-level mismatch too high ({metrics['max_row_diff']:.4f})")
    if metrics["total_diff"] > 0.01:
        failures.append(f"Total mismatch too high ({metrics['total_diff']:.4f})")
    if metrics["branch_vs_employee_diff"] > 0.01:
        failures.append(f"Branch vs employee total mismatch ({metrics['branch_vs_employee_diff']:.4f})")

    if report_file:
        rep = _read_report(report_file)
        if rep.empty:
            failures.append("Report file loaded but empty")
        else:
            left = _normalize_for_parity(split)
            right = _normalize_for_parity(rep)
            merged = left.merge(
                right,
                on=["employee_id", "shop_name"],
                how="outer",
                suffixes=("_dashboard", "_report"),
            ).fillna(0)
            for c in ["total_sales_all", "total_sales_blinkco", "total_sales_without_blinkco"]:
                diff = (merged[f"{c}_dashboard"] - merged[f"{c}_report"]).abs().sum()
                print(f"report_parity_{c}_sum_abs_diff: {diff:.4f}")
                if diff > 0.01:
                    failures.append(f"Report parity mismatch in {c}: {diff:.4f}")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"- {f}")
        return 1

    print("\nPASS: all checks passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-exclusive", required=True, help="YYYY-MM-DD")
    parser.add_argument("--branches", required=True, help="comma-separated IDs, e.g. 2,3,4")
    parser.add_argument("--mode", default="Filtered", choices=["Filtered", "Complete", "Unfiltered"])
    parser.add_argument("--comm-rate", type=float, default=2.0)
    parser.add_argument("--report-file", default="")
    args = parser.parse_args()

    branches = [int(x.strip()) for x in args.branches.split(",") if x.strip()]
    return run_checks(
        start_date=args.start_date,
        end_exclusive=args.end_exclusive,
        branches=branches,
        mode=args.mode,
        commission_rate=args.comm_rate,
        report_file=args.report_file,
    )


if __name__ == "__main__":
    sys.exit(main())
