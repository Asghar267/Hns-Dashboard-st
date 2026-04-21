from __future__ import annotations

import argparse

from modules.call_center_reconciliation import generate_call_center_reconciliation_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Call Center XLS vs DB reconciliation workbook.")
    parser.add_argument("--report-date", required=True, help="Report date in YYYY-MM-DD.")
    parser.add_argument("--xls-path", required=True, help="Path to CALLCENTER.xls file.")
    parser.add_argument("--cutoff-hour", type=int, default=4, help="Business day cutoff hour (default: 4).")
    parser.add_argument("--cutoff-minute", type=int, default=10, help="Business day cutoff minute (default: 10).")
    parser.add_argument("--output-dir", default="exports", help="Output directory for workbook.")
    args = parser.parse_args()

    result = generate_call_center_reconciliation_workbook(
        report_date=args.report_date,
        xls_path=args.xls_path,
        cutoff_hour=args.cutoff_hour,
        cutoff_minute=args.cutoff_minute,
        output_dir=args.output_dir,
    )
    print("Workbook generated:")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
