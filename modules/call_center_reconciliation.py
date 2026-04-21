from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import pyodbc


@dataclass(frozen=True)
class ReconciliationConfig:
    report_date: str
    xls_path: str
    cutoff_hour: int = 4
    cutoff_minute: int = 10
    output_dir: str = "exports"


def _build_conn_str() -> str:
    # Credentials are supplied via environment variables to avoid committing secrets.
    uid = os.environ.get("CALL_CENTER_DB_UID", "sa")
    pwd = os.environ.get("CALL_CENTER_DB_PWD", "")
    if not pwd:
        raise RuntimeError("Missing CALL_CENTER_DB_PWD environment variable for HNSYGCC connection.")
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.34,50908;"
        "DATABASE=HNSYGCC;"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )


def _compute_windows(report_date: str, cutoff_hour: int, cutoff_minute: int = 10) -> Tuple[datetime, datetime, datetime, datetime]:
    day_start = datetime.strptime(report_date, "%Y-%m-%d")
    day_end = day_start + timedelta(days=1)
    biz_start = day_start + timedelta(hours=cutoff_hour, minutes=cutoff_minute)
    biz_end = biz_start + timedelta(days=1)
    return day_start, day_end, biz_start, biz_end


def _fetch_db_orders(start_ts: datetime, end_ts: datetime) -> pd.DataFrame:
    query = """
    WITH base AS (
        SELECT
            o.auto_id,
            o.[datetime] AS order_datetime,
            CAST(o.orderNumber AS BIGINT) AS order_number,
            o.orderTrackingId AS tracking_id,
            ISNULL(NULLIF(LTRIM(RTRIM(o.orderStatus)), ''), '(blank)') AS order_status,
            ISNULL(NULLIF(LTRIM(RTRIM(o.paymentStatus)), ''), '(blank)') AS payment_status,
            ISNULL(NULLIF(LTRIM(RTRIM(o.orderType)), ''), '(blank)') AS order_type,
            ISNULL(osg.subgroupName, '(unknown)') AS subgroup_name,
            CAST(ISNULL(o.isDelete, 0) AS INT) AS is_delete,
            CAST(ISNULL(o.isReject, 0) AS INT) AS is_reject,
            CAST(ISNULL(o.subTotal, 0) AS DECIMAL(18, 2)) AS subtotal,
            CAST(ISNULL(o.taxAmount, 0) AS DECIMAL(18, 2)) AS tax_amount,
            CAST(ISNULL(o.deliveryCharges, 0) AS DECIMAL(18, 2)) AS delivery_charges,
            CAST(ISNULL(o.totalWithTax, 0) AS DECIMAL(18, 2)) AS total_with_tax,
            CAST(
                ISNULL(
                    CASE
                        WHEN ISNULL(o.discountAmount, 0) > 0 THEN o.discountAmount
                        WHEN ISNULL(o.totalDiscount, 0) > 0 THEN o.totalDiscount
                        ELSE 0
                    END,
                    0
                ) + ISNULL(o.voucherAmount, 0) AS DECIMAL(18, 2)
            ) AS total_discount,
            CAST(ISNULL(o.netAmount, 0) AS DECIMAL(18, 2)) AS db_net_amount,
            o.deleteReason
        FROM dbo.orderMaster o
        LEFT JOIN dbo.orderSubgroup osg
            ON osg.orderSubGroupId = o.orderSubgroupId
        WHERE o.[datetime] >= ? AND o.[datetime] < ?
    )
    SELECT
        *,
        CAST(total_with_tax - total_discount AS DECIMAL(18, 2)) AS parity_net_amount
    FROM base
    ORDER BY order_datetime, auto_id;
    """
    with pyodbc.connect(_build_conn_str()) as conn:
        return pd.read_sql(query, conn, params=[start_ts, end_ts])


def _normalize_xls(xls_path: str) -> pd.DataFrame:
    df = pd.read_excel(xls_path)
    cols = {str(c).strip().lower(): c for c in df.columns}

    def col(name: str) -> str:
        key = name.strip().lower()
        return cols.get(key, "")

    out = pd.DataFrame()
    out["mode"] = df[col("Mode")] if col("Mode") else ""
    out["subgroup_name"] = df[col("subgroup Name")] if col("subgroup Name") else ""
    out["order_number"] = pd.to_numeric(df[col("Order#")] if col("Order#") else None, errors="coerce")

    date_series = df[col("txt6")] if col("txt6") else pd.Series([None] * len(df))
    time_series = df[col("txt4")] if col("txt4") else pd.Series([None] * len(df))
    out["xls_datetime"] = pd.to_datetime(
        date_series.astype(str).str.strip() + " " + time_series.astype(str).str.strip(),
        errors="coerce",
    )

    out["gross"] = pd.to_numeric(df[col("Gross")] if col("Gross") else 0, errors="coerce").fillna(0.0)
    out["tax"] = pd.to_numeric(df[col("Tax")] if col("Tax") else 0, errors="coerce").fillna(0.0)
    out["service_charges"] = pd.to_numeric(df[col("Service Charges")] if col("Service Charges") else 0, errors="coerce").fillna(0.0)
    out["net_amount"] = pd.to_numeric(df[col("Net Amount")] if col("Net Amount") else 0, errors="coerce").fillna(0.0)
    out["discount"] = pd.to_numeric(df[col("Discount")] if col("Discount") else 0, errors="coerce").fillna(0.0)
    out["total_with_tax"] = pd.to_numeric(df[col("Total With Tax")] if col("Total With Tax") else 0, errors="coerce").fillna(0.0)

    out = out.sort_values(["order_number", "xls_datetime"], kind="stable").reset_index(drop=True)
    out["occurrence_index_within_order"] = out.groupby("order_number", dropna=False).cumcount() + 1
    out["match_key"] = (
        out["order_number"].fillna(-1).astype("Int64").astype(str)
        + "|"
        + out["occurrence_index_within_order"].astype(str)
    )
    return out


def _build_calendar_day_tab(db_all: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "order_datetime",
        "order_number",
        "tracking_id",
        "order_type",
        "subgroup_name",
        "order_status",
        "payment_status",
        "is_delete",
        "is_reject",
        "subtotal",
        "tax_amount",
        "delivery_charges",
        "total_with_tax",
        "total_discount",
        "parity_net_amount",
        "db_net_amount",
        "deleteReason",
    ]
    out = db_all.rename(columns={"deleteReason": "delete_reason"})
    cols[-1] = "delete_reason"
    return out[cols].copy()


def _build_business_day_tab(db_business: pd.DataFrame) -> pd.DataFrame:
    out = db_business.copy()
    out = out[(out["is_delete"] == 0) & (out["order_type"].str.upper() == "DELIVERY")]
    out = out.sort_values(["order_number", "order_datetime", "tracking_id"], kind="stable").reset_index(drop=True)
    out["occurrence_index_within_order"] = out.groupby("order_number", dropna=False).cumcount() + 1
    out["match_key"] = (
        out["order_number"].fillna(-1).astype("Int64").astype(str)
        + "|"
        + out["occurrence_index_within_order"].astype(str)
    )
    out["business_day"] = out["order_datetime"].dt.date
    return out[
        [
            "business_day",
            "order_datetime",
            "order_number",
            "occurrence_index_within_order",
            "match_key",
            "tracking_id",
            "order_type",
            "subgroup_name",
            "order_status",
            "payment_status",
            "is_delete",
            "is_reject",
            "subtotal",
            "tax_amount",
            "delivery_charges",
            "total_with_tax",
            "total_discount",
            "parity_net_amount",
            "db_net_amount",
            "deleteReason",
        ]
    ].rename(columns={"deleteReason": "delete_reason"})


def _build_diff_sheet(xls_norm: pd.DataFrame, db_business_aligned: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    db_cmp = db_business_aligned[
        [
            "match_key",
            "order_datetime",
            "order_number",
            "occurrence_index_within_order",
            "tracking_id",
            "subgroup_name",
            "order_status",
            "payment_status",
            "tax_amount",
            "delivery_charges",
            "parity_net_amount",
        ]
    ].copy()
    db_cmp = db_cmp.rename(
        columns={
            "order_datetime": "db_datetime",
            "tax_amount": "db_tax",
            "delivery_charges": "db_delivery",
            "parity_net_amount": "db_net_amount",
        }
    )

    xls_cmp = xls_norm[
        [
            "match_key",
            "xls_datetime",
            "order_number",
            "occurrence_index_within_order",
            "subgroup_name",
            "tax",
            "service_charges",
            "net_amount",
            "discount",
        ]
    ].copy()
    xls_cmp = xls_cmp.rename(
        columns={
            "tax": "xls_tax",
            "service_charges": "xls_delivery",
            "net_amount": "xls_net_amount",
            "discount": "xls_discount",
        }
    )

    merged = db_cmp.merge(xls_cmp, on="match_key", how="outer", suffixes=("_db", "_xls"), indicator=True)
    merged["net_delta"] = (merged["db_net_amount"].fillna(0) - merged["xls_net_amount"].fillna(0)).round(2)
    merged["tax_delta"] = (merged["db_tax"].fillna(0) - merged["xls_tax"].fillna(0)).round(2)
    merged["delivery_delta"] = (merged["db_delivery"].fillna(0) - merged["xls_delivery"].fillna(0)).round(2)

    missing_df = merged[merged["_merge"] == "left_only"].copy()
    missing_df["diff_type"] = "Missing in XLS"

    extra_df = merged[merged["_merge"] == "right_only"].copy()
    extra_df["diff_type"] = "Extra in XLS"

    tolerance = 0.5
    net_var = merged["net_delta"].abs() > tolerance
    tax_var = merged["tax_delta"].abs() > tolerance
    delivery_var = merged["delivery_delta"].abs() > tolerance
    variance_df = merged[
        (merged["_merge"] == "both")
        & (net_var | tax_var | delivery_var)
    ].copy()
    variance_df["diff_type"] = "Matched with amount variance"

    diff_rows = pd.concat([missing_df, extra_df, variance_df], ignore_index=True, sort=False)
    diff_rows = diff_rows[
        [
            "diff_type",
            "match_key",
            "order_number_db",
            "order_number_xls",
            "occurrence_index_within_order_db",
            "occurrence_index_within_order_xls",
            "db_datetime",
            "xls_datetime",
            "tracking_id",
            "subgroup_name_db",
            "subgroup_name_xls",
            "order_status",
            "payment_status",
            "db_net_amount",
            "xls_net_amount",
            "net_delta",
            "db_tax",
            "xls_tax",
            "tax_delta",
            "db_delivery",
            "xls_delivery",
            "delivery_delta",
            "xls_discount",
        ]
    ].rename(
        columns={
            "order_number_db": "db_order_number",
            "order_number_xls": "xls_order_number",
            "occurrence_index_within_order_db": "db_occurrence_index",
            "occurrence_index_within_order_xls": "xls_occurrence_index",
            "subgroup_name_db": "db_subgroup_name",
            "subgroup_name_xls": "xls_subgroup_name",
        }
    )

    summary = pd.DataFrame(
        [
            {"metric": "DB Business Day Row Count", "db_value": float(len(db_business_aligned)), "xls_value": float(len(xls_norm)), "delta": float(len(db_business_aligned) - len(xls_norm))},
            {"metric": "Net Amount", "db_value": float(db_business_aligned["parity_net_amount"].sum()), "xls_value": float(xls_norm["net_amount"].sum()), "delta": float(db_business_aligned["parity_net_amount"].sum() - xls_norm["net_amount"].sum())},
            {"metric": "Tax", "db_value": float(db_business_aligned["tax_amount"].sum()), "xls_value": float(xls_norm["tax"].sum()), "delta": float(db_business_aligned["tax_amount"].sum() - xls_norm["tax"].sum())},
            {"metric": "Delivery/Service Charges", "db_value": float(db_business_aligned["delivery_charges"].sum()), "xls_value": float(xls_norm["service_charges"].sum()), "delta": float(db_business_aligned["delivery_charges"].sum() - xls_norm["service_charges"].sum())},
            {"metric": "Missing in XLS", "db_value": float((merged["_merge"] == "left_only").sum()), "xls_value": 0.0, "delta": float((merged["_merge"] == "left_only").sum())},
            {"metric": "Extra in XLS", "db_value": 0.0, "xls_value": float((merged["_merge"] == "right_only").sum()), "delta": float(-(merged["_merge"] == "right_only").sum())},
            {"metric": "Matched with amount variance", "db_value": float(len(variance_df)), "xls_value": float(len(variance_df)), "delta": 0.0},
        ]
    )
    return summary, diff_rows


def generate_call_center_reconciliation_workbook(
    report_date: str,
    xls_path: str,
    cutoff_hour: int = 4,
    cutoff_minute: int = 10,
    output_dir: str = "exports",
) -> Dict[str, str]:
    cfg = ReconciliationConfig(
        report_date=report_date,
        xls_path=xls_path,
        cutoff_hour=cutoff_hour,
        cutoff_minute=cutoff_minute,
        output_dir=output_dir,
    )
    xls_file = Path(cfg.xls_path)
    if not xls_file.exists():
        raise FileNotFoundError(f"XLS file not found: {xls_file}")

    day_start, day_end, biz_start, biz_end = _compute_windows(cfg.report_date, cfg.cutoff_hour, cfg.cutoff_minute)
    db_calendar = _fetch_db_orders(day_start, day_end)
    db_business_all = _fetch_db_orders(biz_start, biz_end)
    db_business = _build_business_day_tab(db_business_all)
    db_calendar_tab = _build_calendar_day_tab(db_calendar)
    xls_norm = _normalize_xls(str(xls_file))
    summary, diff_rows = _build_diff_sheet(xls_norm, db_business)

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"call_center_reconciliation_{cfg.report_date}_cutoff{cfg.cutoff_hour:02d}{cfg.cutoff_minute:02d}_{ts}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        db_calendar_tab.to_excel(writer, sheet_name="DB Calendar Day", index=False)
        db_business.to_excel(writer, sheet_name="DB Business Day Cutoff", index=False)
        summary.to_excel(writer, sheet_name="XLS vs DB Diff", index=False, startrow=0)
        diff_rows.to_excel(writer, sheet_name="XLS vs DB Diff", index=False, startrow=len(summary) + 2)

    return {
        "output_path": str(out_path),
        "report_date": cfg.report_date,
        "cutoff_hour": f"{cfg.cutoff_hour:02d}:{cfg.cutoff_minute:02d}",
        "db_business_rows": str(len(db_business)),
        "xls_rows": str(len(xls_norm)),
    }
