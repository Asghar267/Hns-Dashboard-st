from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import pyodbc


def _build_conn_str() -> str:
    driver = os.environ.get("CALL_CENTER_DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.environ.get("CALL_CENTER_DB_SERVER", "103.86.55.34,50908")
    database = os.environ.get("CALL_CENTER_DB_NAME", "HNSYGCC")
    uid = os.environ.get("CALL_CENTER_DB_UID", "sa")
    pwd = os.environ.get("CALL_CENTER_DB_PWD", "123")
    timeout = int(os.environ.get("CALL_CENTER_DB_TIMEOUT", "30"))

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        f"Connection Timeout={timeout};"
    )


def _dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def _audit_counts(conn: pyodbc.Connection, start_date: str, end_date: str, cutoff_hour: int) -> pd.DataFrame:
    start_day = datetime.strptime(start_date, "%Y-%m-%d")
    end_day = datetime.strptime(end_date, "%Y-%m-%d")

    # Calendar day window (inclusive dates)
    cal_start = start_day.strftime("%Y-%m-%d 00:00:00")
    cal_end = (end_day + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")

    # Business cutoff window (04:00 -> next day 04:00)
    biz_start = (start_day + timedelta(hours=cutoff_hour)).strftime("%Y-%m-%d %H:%M:%S")
    biz_end = (end_day + timedelta(days=1, hours=cutoff_hour)).strftime("%Y-%m-%d %H:%M:%S")

    query = """
    WITH base AS (
        SELECT
            o.[datetime],
            CAST(ISNULL(o.isDelete, 0) AS INT) AS is_delete,
            UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '')) AS order_type,
            UPPER(ISNULL(LTRIM(RTRIM(o.orderStatus)), '')) AS order_status,
            UPPER(ISNULL(LTRIM(RTRIM(o.paymentStatus)), '')) AS payment_status,
            CAST(ISNULL(o.isReject, 0) AS INT) AS is_reject
        FROM dbo.orderMaster o
        WHERE o.[datetime] >= ? AND o.[datetime] < ?
    ),
    strict_excl AS (
        SELECT
            *,
            CASE
                WHEN is_reject = 1 OR order_status LIKE '%REJECT%' OR order_status LIKE '%CANCEL%' THEN 1
                WHEN order_status = 'BOOKED' AND payment_status IN ('NP', 'PREORDER') THEN 1
                ELSE 0
            END AS is_excluded_strict
        FROM base
    )
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN is_delete = 0 THEN 1 ELSE 0 END) AS non_deleted_rows,
        SUM(CASE WHEN is_delete = 1 THEN 1 ELSE 0 END) AS deleted_rows,
        SUM(CASE WHEN is_delete = 0 AND order_type = 'DELIVERY' THEN 1 ELSE 0 END) AS non_deleted_delivery_rows,
        SUM(CASE WHEN is_delete = 0 AND order_type <> 'DELIVERY' THEN 1 ELSE 0 END) AS non_deleted_non_delivery_rows,
        SUM(CASE WHEN is_delete = 0 AND is_excluded_strict = 1 THEN 1 ELSE 0 END) AS strict_excluded_rows,
        SUM(CASE WHEN is_delete = 0 AND is_excluded_strict = 0 THEN 1 ELSE 0 END) AS strict_included_rows
    FROM strict_excl;
    """

    cal = pd.read_sql(query, conn, params=[cal_start, cal_end])
    cal.insert(0, "window", "calendar_day")
    cal.insert(1, "start_ts", cal_start)
    cal.insert(2, "end_ts", cal_end)

    biz = pd.read_sql(query, conn, params=[biz_start, biz_end])
    biz.insert(0, "window", f"business_cutoff_{cutoff_hour:02d}00")
    biz.insert(1, "start_ts", biz_start)
    biz.insert(2, "end_ts", biz_end)

    return pd.concat([cal, biz], ignore_index=True)


def _boundary_orders(conn: pyodbc.Connection, start_date: str, end_date: str, cutoff_hour: int) -> pd.DataFrame:
    # These are the two boundary slices that differ between calendar-day and 04:00 cutoff windows.
    start_day = datetime.strptime(start_date, "%Y-%m-%d")
    end_day = datetime.strptime(end_date, "%Y-%m-%d")

    cal_start_gap_start = start_day.strftime("%Y-%m-%d 00:00:00")
    cal_start_gap_end = (start_day + timedelta(hours=cutoff_hour)).strftime("%Y-%m-%d %H:%M:%S")

    cal_end_gap_start = (end_day + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    cal_end_gap_end = (end_day + timedelta(days=1, hours=cutoff_hour)).strftime("%Y-%m-%d %H:%M:%S")

    q = """
    SELECT
        o.[datetime],
        o.orderNumber,
        o.orderTrackingId,
        o.orderType,
        o.orderStatus,
        o.paymentStatus,
        o.isDelete,
        o.isReject,
        o.subTotal,
        o.taxAmount,
        o.totalWithTax,
        o.deliveryCharges,
        o.netAmount,
        o.deleteReason
    FROM dbo.orderMaster o
    WHERE o.[datetime] >= ? AND o.[datetime] < ?
    ORDER BY o.[datetime], o.auto_id;
    """
    a = pd.read_sql(q, conn, params=[cal_start_gap_start, cal_start_gap_end])
    a.insert(0, "slice", f"{start_date} 00:00 -> {start_date} {cutoff_hour:02d}:00")
    b = pd.read_sql(q, conn, params=[cal_end_gap_start, cal_end_gap_end])
    b.insert(0, "slice", f"{(end_day + timedelta(days=1)).strftime('%Y-%m-%d')} 00:00 -> {(end_day + timedelta(days=1)).strftime('%Y-%m-%d')} {cutoff_hour:02d}:00")
    return pd.concat([a, b], ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit Call Center order count drift (calendar-day vs 04:00 cutoff).")
    ap.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--cutoff-hour", type=int, default=4)
    ap.add_argument("--out-csv", default="", help="Optional: write boundary orders to CSV")
    args = ap.parse_args()

    with pyodbc.connect(_build_conn_str()) as conn:
        counts = _audit_counts(conn, args.start_date, args.end_date, args.cutoff_hour)
        print("\nCOUNTS SUMMARY")
        print(counts.to_string(index=False))

        boundary = _boundary_orders(conn, args.start_date, args.end_date, args.cutoff_hour)
        print("\nBOUNDARY ORDERS (these explain calendar vs cutoff drift)")
        print(f"rows: {len(boundary)}")
        if len(boundary) > 0:
            show_cols = [
                "slice",
                "datetime",
                "orderNumber",
                "orderTrackingId",
                "orderType",
                "orderStatus",
                "paymentStatus",
                "isDelete",
                "isReject",
                "totalWithTax",
                "taxAmount",
                "deliveryCharges",
                "netAmount",
                "deleteReason",
            ]
            keep = [c for c in show_cols if c in boundary.columns]
            print(boundary[keep].to_string(index=False))

        if args.out_csv:
            boundary.to_csv(args.out_csv, index=False, encoding="utf-8")
            print(f"\nWROTE CSV: {args.out_csv}")


if __name__ == "__main__":
    main()

