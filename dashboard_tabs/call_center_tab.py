"""
Call Center Sales Tab
Shows sales snapshot from HNSYGCC.orderMaster.
"""

from __future__ import annotations

import os
from calendar import monthrange
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import pyodbc
import streamlit as st

from modules.call_center_reconciliation import generate_call_center_reconciliation_workbook
from modules.database import pool
from modules.responsive import clamp_dataframe_height, get_responsive_context
from modules.utils import format_currency, format_percentage


class CallCenterTab:
    """Render call-center sales from HNSYGCC."""

    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.responsive = get_responsive_context()

    @staticmethod
    def _build_conn_str() -> str:
        driver = os.environ.get("CALL_CENTER_DB_DRIVER", "ODBC Driver 17 for SQL Server")
        server = os.environ.get("CALL_CENTER_DB_SERVER", "103.86.55.34,50908")
        database = os.environ.get("CALL_CENTER_DB_NAME", "HNSYGCC")
        uid = os.environ.get("CALL_CENTER_DB_UID", "sa")
        # Never hardcode passwords in the repo. Use environment variables for secrets.
        pwd = os.environ.get("CALL_CENTER_DB_PWD", "")
        if not pwd:
            raise RuntimeError("Missing CALL_CENTER_DB_PWD environment variable for HNSYGCC connection.")
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

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_summary(_self, start_date: str, end_date: str) -> pd.DataFrame:
        # "Strict/Realized" metrics intentionally exclude records that are operationally
        # visible in orderMaster but should not count as realized sales in dashboard totals.
        query = """
        WITH range_data AS (
            SELECT
                [datetime],
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                COALESCE(subTotal, 0) AS subtotal,
                COALESCE(taxAmount, 0) AS tax_amount,
                COALESCE(deliveryCharges, 0) AS delivery_charges,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        ),
        marked AS (
            SELECT
                [datetime],
                subtotal,
                tax_amount,
                delivery_charges,
                gross_before_discount,
                total_discount,
                net_amount,
                CASE
                    WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN 1
                    WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN 1
                    ELSE 0
                END AS is_excluded
            FROM range_data
        )
        SELECT
            SUM(CASE WHEN is_excluded = 0 THEN 1 ELSE 0 END) AS total_orders,
            SUM(CASE WHEN is_excluded = 0 THEN (gross_before_discount - total_discount) ELSE 0 END) AS total_net_sales,
            SUM(CASE WHEN is_excluded = 0 THEN net_amount ELSE 0 END) AS total_net_sales_with_delivery,
            SUM(CASE WHEN is_excluded = 0 THEN (subtotal - total_discount) ELSE 0 END) AS total_sales_wo_tax_delivery,
            SUM(CASE WHEN is_excluded = 0 THEN tax_amount ELSE 0 END) AS total_tax,
            SUM(CASE WHEN is_excluded = 0 THEN delivery_charges ELSE 0 END) AS total_delivery_charges,
            SUM(CASE WHEN is_excluded = 0 THEN total_discount ELSE 0 END) AS total_discount,
            AVG(CASE WHEN is_excluded = 0 THEN (gross_before_discount - total_discount) ELSE NULL END) AS avg_order_value,
            MIN(CASE WHEN is_excluded = 0 THEN [datetime] ELSE NULL END) AS first_order_ts,
            MAX(CASE WHEN is_excluded = 0 THEN [datetime] ELSE NULL END) AS last_order_ts
        FROM marked;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_summary_xls_aligned(_self, start_date: str, end_date: str, cutoff_hour: int = 4, cutoff_minute: int = 10) -> pd.DataFrame:
        # The reconciliation workbook groups business days using the same overnight cutoff
        # as the XLS export, so we query with timestamps instead of plain calendar dates.
        start_ts = f"{start_date} {cutoff_hour:02d}:{cutoff_minute:02d}:00"
        end_ts = (pd.Timestamp(end_date) + pd.Timedelta(days=1, hours=cutoff_hour, minutes=cutoff_minute)).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        WITH base AS (
            SELECT
                [datetime],
                CAST(ISNULL(subTotal, 0) AS DECIMAL(18, 2)) AS subtotal,
                CAST(ISNULL(taxAmount, 0) AS DECIMAL(18, 2)) AS tax_amount,
                CAST(ISNULL(deliveryCharges, 0) AS DECIMAL(18, 2)) AS delivery_charges,
                CAST(ISNULL(totalWithTax, 0) AS DECIMAL(18, 2)) AS total_with_tax,
                CAST(
                    ISNULL(
                        CASE
                            WHEN ISNULL(discountAmount, 0) > 0 THEN discountAmount
                            WHEN ISNULL(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + ISNULL(voucherAmount, 0) AS DECIMAL(18, 2)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
              AND ISNULL(isDelete, 0) = 0
              AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
        )
        SELECT
            COUNT(*) AS total_orders,
            SUM(subtotal) AS total_gross_sales,
            SUM(net_amount) AS total_net_sales_with_delivery,
            SUM(total_with_tax - total_discount) AS total_net_sales_xls,
            SUM(total_with_tax - total_discount) AS total_net_sales, -- Keep for compatibility
            SUM(subtotal - total_discount) AS total_sales_wo_tax_delivery,
            SUM(tax_amount) AS total_tax,
            SUM(delivery_charges) AS total_delivery_charges,
            SUM(total_discount) AS total_discount,
            AVG(total_with_tax - total_discount) AS avg_order_value,
            MIN([datetime]) AS first_order_ts,
            MAX([datetime]) AS last_order_ts
        FROM base;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_ts, end_ts])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_latest_snapshot(_self) -> pd.DataFrame:
        query = """
        WITH latest_day AS (
            SELECT CAST(MAX([datetime]) AS date) AS latest_day
            FROM dbo.orderMaster
            WHERE ISNULL(isDelete, 0) = 0
        )
        SELECT
            CAST(o.[datetime] AS date) AS sales_day,
            COUNT(*) AS total_orders,
            SUM(
                (
                    COALESCE(o.totalWithTax, 0)
                    + COALESCE(o.deliveryCharges, 0)
                    + COALESCE(o.extraCharges, 0)
                    + COALESCE(o.cardCharges, 0)
                ) - (
                    COALESCE(
                        CASE
                            WHEN COALESCE(o.discountAmount, 0) > 0 THEN o.discountAmount
                            WHEN COALESCE(o.totalDiscount, 0) > 0 THEN o.totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(o.voucherAmount, 0)
                )
            ) AS total_net_sales,
            SUM(
                COALESCE(
                    CASE
                        WHEN COALESCE(o.discountAmount, 0) > 0 THEN o.discountAmount
                        WHEN COALESCE(o.totalDiscount, 0) > 0 THEN o.totalDiscount
                        ELSE 0
                    END,
                    0
                ) + COALESCE(o.voucherAmount, 0)
            ) AS total_discount,
            SUM(
                COALESCE(o.totalWithTax, 0)
                + COALESCE(o.deliveryCharges, 0)
                + COALESCE(o.extraCharges, 0)
                + COALESCE(o.cardCharges, 0)
            ) AS gross_before_discount,
            SUM(
                COALESCE(o.subTotal, 0)
                - (
                    COALESCE(
                        CASE
                            WHEN COALESCE(o.discountAmount, 0) > 0 THEN o.discountAmount
                            WHEN COALESCE(o.totalDiscount, 0) > 0 THEN o.totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(o.voucherAmount, 0)
                )
            ) AS total_sales_wo_tax_delivery,
            SUM(COALESCE(o.subTotal, 0)) AS subtotal,
            SUM(COALESCE(o.taxAmount, 0)) AS tax_amount,
            SUM(COALESCE(o.deliveryCharges, 0)) AS delivery_charges,
            MIN(o.[datetime]) AS first_order_ts,
            MAX(o.[datetime]) AS last_order_ts
        FROM dbo.orderMaster o
        CROSS JOIN latest_day l
        WHERE CAST(o.[datetime] AS date) = l.latest_day
          AND ISNULL(o.isDelete, 0) = 0
        GROUP BY CAST(o.[datetime] AS date);
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn)

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_daily_sales(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                [datetime],
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                COALESCE(subTotal, 0) AS subtotal,
                COALESCE(taxAmount, 0) AS tax_amount,
                COALESCE(deliveryCharges, 0) AS delivery_charges,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        ),
        filtered AS (
            SELECT *
            FROM base
            WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
              AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        )
        SELECT
            CAST([datetime] AS date) AS sales_day,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(subtotal - total_discount) AS total_sales_wo_tax_delivery,
            SUM(tax_amount) AS total_tax,
            SUM(delivery_charges) AS total_delivery_charges,
            SUM(total_discount) AS total_discount,
                SUM(net_amount) AS total_net_with_delivery
        FROM filtered
        GROUP BY CAST([datetime] AS date)
        ORDER BY sales_day DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_daily_sales_xls_aligned(_self, start_date: str, end_date: str, cutoff_hour: int = 4, cutoff_minute: int = 10) -> pd.DataFrame:
        # Shift each timestamp backward by the cutoff window so post-midnight orders roll
        # into the prior business day before grouping.
        start_ts = f"{start_date} {cutoff_hour:02d}:{cutoff_minute:02d}:00"
        end_ts = (pd.Timestamp(end_date) + pd.Timedelta(days=1, hours=cutoff_hour, minutes=cutoff_minute)).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        WITH base AS (
            SELECT
                CAST(DATEADD(minute, ?, [datetime]) AS date) AS business_day,
                CAST(ISNULL(subTotal, 0) AS DECIMAL(18, 2)) AS subtotal,
                CAST(ISNULL(taxAmount, 0) AS DECIMAL(18, 2)) AS tax_amount,
                CAST(ISNULL(deliveryCharges, 0) AS DECIMAL(18, 2)) AS delivery_charges,
                CAST(ISNULL(totalWithTax, 0) AS DECIMAL(18, 2)) AS total_with_tax,
                CAST(
                    ISNULL(
                        CASE
                            WHEN ISNULL(discountAmount, 0) > 0 THEN discountAmount
                            WHEN ISNULL(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + ISNULL(voucherAmount, 0) AS DECIMAL(18, 2)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
              AND ISNULL(isDelete, 0) = 0
              AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
        )
        SELECT
            business_day AS sales_day,
            COUNT(*) AS total_orders,
            SUM(total_with_tax - total_discount) AS total_net_sales,
            SUM(subtotal - total_discount) AS total_sales_wo_tax_delivery,
            SUM(tax_amount) AS total_tax,
            SUM(delivery_charges) AS total_delivery_charges,
            SUM(total_discount) AS total_discount,
                SUM(net_amount) AS total_net_with_delivery
        FROM base
        GROUP BY business_day
        ORDER BY sales_day DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[-(cutoff_hour * 60 + cutoff_minute), start_ts, end_ts])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_order_type_breakdown(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                ISNULL(NULLIF(LTRIM(RTRIM(orderType)), ''), '(blank)') AS order_type,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT
            order_type,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
                SUM(net_amount) AS total_net_with_delivery
        FROM base
        WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
          AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        GROUP BY order_type
        ORDER BY total_net_sales DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_payment_status_breakdown(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                ISNULL(NULLIF(LTRIM(RTRIM(paymentStatus)), ''), '(blank)') AS payment_status,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT
            payment_status,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
                SUM(net_amount) AS total_net_with_delivery
        FROM base
        WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
          AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        GROUP BY payment_status
        ORDER BY total_orders DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_order_status_funnel(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) - (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS net_amount,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                NULLIF(LTRIM(RTRIM(dispatchTime)), '') AS dispatch_time
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT
            COUNT(*) AS booked_orders,
            SUM(CASE WHEN order_status_norm LIKE '%DISPATCH%' OR dispatch_time IS NOT NULL THEN 1 ELSE 0 END) AS dispatched_orders,
            SUM(CASE WHEN payment_status_norm = 'P' OR order_status_norm IN ('COMPLETED', 'DELIVERED', 'CLOSE', 'CLOSED', 'SERVED') THEN 1 ELSE 0 END) AS completed_orders,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN 1 ELSE 0 END) AS rejected_orders,
            SUM(net_amount) AS booked_sales,
            SUM(CASE WHEN order_status_norm LIKE '%DISPATCH%' OR dispatch_time IS NOT NULL THEN net_amount ELSE 0 END) AS dispatched_sales,
            SUM(CASE WHEN payment_status_norm = 'P' OR order_status_norm IN ('COMPLETED', 'DELIVERED', 'CLOSE', 'CLOSED', 'SERVED') THEN net_amount ELSE 0 END) AS completed_sales,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN net_amount ELSE 0 END) AS rejected_sales
        FROM base;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_branch_counter_drilldown(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                [datetime],
                ISNULL(branchId, -1) AS branch_id,
                ISNULL(counterId, -1) AS counter_id,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        ),
        filtered AS (
            SELECT *
            FROM base
            WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
              AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        )
        SELECT
            branch_id,
            counter_id,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
            SUM(net_amount) AS total_net_with_delivery,
            AVG(gross_before_discount - total_discount) AS avg_order_value,
            MIN([datetime]) AS first_order_ts,
            MAX([datetime]) AS last_order_ts
        FROM filtered
        GROUP BY branch_id, counter_id
        ORDER BY total_net_sales DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_area_sales(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                ISNULL(NULLIF(LTRIM(RTRIM(delvArea)), ''), '(blank)') AS delv_area,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        ),
        filtered AS (
            SELECT *
            FROM base
            WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
              AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        )
        SELECT
            delv_area,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
            AVG(gross_before_discount - total_discount) AS avg_order_value,
            SUM(net_amount) AS total_net_with_delivery
        FROM filtered
        GROUP BY delv_area
        ORDER BY total_net_sales DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_excluded_orders(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        WITH base AS (
            SELECT
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' THEN 1 ELSE 0 END) AS rejected_orders,
            SUM(CASE WHEN order_status_norm LIKE '%CANCEL%' THEN 1 ELSE 0 END) AS cancelled_orders,
            SUM(CASE WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN 1 ELSE 0 END) AS open_unpaid_orders,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN 1 ELSE 0 END) AS excluded_orders,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN (gross_before_discount - total_discount) ELSE 0 END) AS rejected_cancelled_sales,
            SUM(CASE WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN (gross_before_discount - total_discount) ELSE 0 END) AS open_unpaid_sales,
            SUM(
                CASE
                    WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%'
                      OR (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
                    THEN (gross_before_discount - total_discount)
                    ELSE 0
                END
            ) AS excluded_sales_total
        FROM base;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_deleted_orders(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = """
        SELECT
            [datetime],
            orderTrackingId,
            orderNumber,
            orderType,
            orderStatus,
            paymentStatus,
            branchId,
            counterId,
            customerId,
            waiterName,
            delvArea,
            subTotal,
            taxAmount,
            deliveryCharges,
            discountAmount,
            totalDiscount,
            voucherAmount,
            netAmount,
            deleteReason,
            deleteUserId
        FROM dbo.orderMaster
        WHERE CAST([datetime] AS date) BETWEEN ? AND ?
          AND ISNULL(isDelete, 0) = 1
        ORDER BY [datetime] DESC;
        """
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])

    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_call_center_target(_self, year: int, month: int) -> pd.DataFrame:
        query = """
        SELECT TOP 1
            target_year,
            target_month,
            sale_point,
            daily_target,
            monthly_target,
            status
        FROM dbo.call_center_targets
        WHERE target_year = ?
          AND target_month = ?
          AND sale_point = 'Call Center'
          AND ISNULL(status, 'Active') = 'Active'
        ORDER BY id DESC;
        """
        try:
            conn = pool.get_connection("kdsdb")
            return pd.read_sql(query, conn, params=[year, month])
        except Exception:
            return pd.DataFrame()

    def render(self) -> None:
        st.header("Call Center")
        st.caption(
            f"HNSYGCC call-center sales | Range: {self.start_date} to {self.end_date} | "
            f"Mode: {self.data_mode}"
        )
        cutoff_hour = 4
        cutoff_minute = 10
        metric_profile = st.radio(
            "Call Center Metric Profile",
            ["XLS-aligned (Default)", "Strict/Realized (Comparison)"],
            index=0,
            horizontal=True,
            key="call_center_metric_profile",
        )
        st.caption(
            f"XLS-aligned profile uses {cutoff_hour:02d}:{cutoff_minute:02d} cutoff business-day + DELIVERY + non-deleted rows. "
            "Strict/Realized is provided as read-only comparison."
        )

        recon_cols = st.columns([2, 1])
        with recon_cols[0]:
            xls_path = st.text_input(
                "CALLCENTER XLS Path",
                value=st.session_state.get("call_center_xls_path", "CALLCENTER.xls"),
                key="call_center_xls_path",
                help="Used by reconciliation workbook generation.",
            )
        with recon_cols[1]:
            st.caption(" ")
            if st.button("Generate Reconciliation Workbook", key="cc_generate_recon_btn", use_container_width=True):
                try:
                    result = generate_call_center_reconciliation_workbook(
                        report_date=self.end_date,
                        xls_path=xls_path,
                        cutoff_hour=cutoff_hour,
                        output_dir="exports",
                    )
                    output_path = Path(result["output_path"])
                    st.success(f"Reconciliation workbook generated: {output_path}")
                    st.caption(
                        f"Rows | DB Business Cutoff: {result['db_business_rows']} | XLS: {result['xls_rows']} | "
                        f"Date: {result['report_date']} | Cutoff: {result['cutoff_hour']}"
                    )
                except Exception as gen_err:
                    st.error(f"Reconciliation generation failed: {gen_err}")

        start_dt = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        target_year = end_dt.year
        target_month = end_dt.month

        try:
            latest_df = self._fetch_latest_snapshot()
            strict_summary_df = self._fetch_summary(self.start_date, self.end_date)
            strict_daily_df = self._fetch_daily_sales(self.start_date, self.end_date)
            aligned_summary_df = self._fetch_summary_xls_aligned(self.start_date, self.end_date, cutoff_hour=cutoff_hour, cutoff_minute=cutoff_minute)
            aligned_daily_df = self._fetch_daily_sales_xls_aligned(self.start_date, self.end_date, cutoff_hour=cutoff_hour, cutoff_minute=cutoff_minute)
            # Keep both profiles loaded so the toggle only swaps presentation, not the
            # rest of the downstream rendering and formatting pipeline.
            summary_df = aligned_summary_df if metric_profile.startswith("XLS-aligned") else strict_summary_df
            daily_df = aligned_daily_df if metric_profile.startswith("XLS-aligned") else strict_daily_df
            order_type_df = self._fetch_order_type_breakdown(self.start_date, self.end_date)
            payment_df = self._fetch_payment_status_breakdown(self.start_date, self.end_date)
            funnel_df = self._fetch_order_status_funnel(self.start_date, self.end_date)
            drilldown_df = self._fetch_branch_counter_drilldown(self.start_date, self.end_date)
            area_df = self._fetch_area_sales(self.start_date, self.end_date)
            excluded_df = self._fetch_excluded_orders(self.start_date, self.end_date)
            deleted_df = self._fetch_deleted_orders(self.start_date, self.end_date)
            target_df = self._fetch_call_center_target(target_year, target_month)
        except Exception as e:
            st.error(f"Failed to load Call Center sales: {e}")
            return

        if summary_df.empty:
            st.info("No sales data found for the selected range.")
            return

        summary_row = summary_df.iloc[0]
        latest_row = latest_df.iloc[0] if not latest_df.empty else {}

        primary_cols = st.columns(4)
        with primary_cols[0]:
            st.metric("Range Gross Sales", format_currency(float(summary_row.get("total_gross_sales", 0.0) or 0.0)), help="Total before discounts and tax")
        with primary_cols[1]:
            st.metric("Net Sales (Incl. Delv)", format_currency(float(summary_row.get("total_net_sales_with_delivery", 0.0) or 0.0)), help="Final payable amount (Matches other software)")
        with primary_cols[2]:
            st.metric("Net Sales (XLS Logic)", format_currency(float(summary_row.get("total_net_sales_xls", 0.0) or 0.0)), help="Subtotal + Tax - Discount")
        with primary_cols[3]:
            st.metric("Range Orders", f"{int(summary_row.get('total_orders', 0)):,}")

        st.markdown("---")
        
        secondary_cols = st.columns(5)
        with secondary_cols[0]:
            st.metric("Range Discounts", format_currency(float(summary_row.get("total_discount", 0.0) or 0.0)))
        with secondary_cols[1]:
            st.metric("Sales w/o Tax & Delivery", format_currency(float(summary_row.get("total_sales_wo_tax_delivery", 0.0) or 0.0)))
        with secondary_cols[2]:
            st.metric("Avg Order Value", format_currency(float(summary_row.get("avg_order_value", 0.0) or 0.0)))
        with secondary_cols[3]:
            st.metric("Total Tax", format_currency(float(summary_row.get("total_tax", 0.0) or 0.0)))
        with secondary_cols[4]:
            latest_ts = latest_row.get("last_order_ts") if isinstance(latest_row, pd.Series) else None
            st.metric("Latest Sale Time", str(latest_ts) if latest_ts is not None else "N/A")
        aux_cols = st.columns(1)
        with aux_cols[0]:
            st.metric("Total Delivery Charges", format_currency(float(summary_row.get("total_delivery_charges", 0.0) or 0.0)))

        strict_row = strict_summary_df.iloc[0] if not strict_summary_df.empty else pd.Series(dtype=object)
        st.caption(
            "Comparison (Strict/Realized): "
            f"Orders {int(strict_row.get('total_orders', 0) or 0):,} | "
            f"Net {format_currency(float(strict_row.get('total_net_sales', 0.0) or 0.0))} | "
            f"Tax {format_currency(float(strict_row.get('total_tax', 0.0) or 0.0))} | "
            f"Delivery {format_currency(float(strict_row.get('total_delivery_charges', 0.0) or 0.0))}"
        )

        if excluded_df is not None and not excluded_df.empty:
            ex = excluded_df.iloc[0]
            ex_cols = st.columns(4)
            with ex_cols[0]:
                st.metric("Rejected Orders (Excluded)", f"{int(ex.get('rejected_orders', 0) or 0):,}")
            with ex_cols[1]:
                st.metric("Cancelled Orders (Excluded)", f"{int(ex.get('cancelled_orders', 0) or 0):,}")
            with ex_cols[2]:
                st.metric("Total Excluded Sales", format_currency(float(ex.get("excluded_sales_total", 0.0) or 0.0)))
            with ex_cols[3]:
                st.metric("Open NP/PreOrder (Excluded)", f"{int(ex.get('open_unpaid_orders', 0) or 0):,}")
            st.caption(
                f"Rejected/Cancelled excluded sales: "
                f"{format_currency(float(ex.get('rejected_cancelled_sales', 0.0) or 0.0))} | "
                f"Open NP/PreOrder excluded sales: "
                f"{format_currency(float(ex.get('open_unpaid_sales', 0.0) or 0.0))}"
            )

        # Deleted rows are not part of either metric profile, but exposing them here helps
        # the team explain mismatches when source-system edits happen after the fact.
        deleted_count = int(len(deleted_df)) if deleted_df is not None else 0
        deleted_sales = float(pd.to_numeric(deleted_df.get("netAmount"), errors="coerce").fillna(0).sum()) if deleted_count else 0.0
        dcols = st.columns(2)
        with dcols[0]:
            st.metric("Deleted Orders (isDelete=1)", f"{deleted_count:,}")
        with dcols[1]:
            st.metric("Deleted Orders Sales", format_currency(deleted_sales))

        if deleted_count > 0:
            st.caption("Deleted Orders Details")
            show_deleted = deleted_df.copy()
            for col in [
                "subTotal",
                "taxAmount",
                "deliveryCharges",
                "discountAmount",
                "totalDiscount",
                "voucherAmount",
                "netAmount",
            ]:
                if col in show_deleted.columns:
                    show_deleted[col] = show_deleted[col].apply(lambda x: format_currency(float(x or 0)))
            st.dataframe(
                show_deleted,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=240, tablet=220, phone=200, kind="compact"),
            )

        st.markdown("---")
        st.subheader("Target Tracking")
        if target_df.empty:
            st.info(f"No Call Center target configured in KDS DB for {target_year}-{target_month:02d}.")
        else:
            trow = target_df.iloc[0]
            monthly_target = float(trow.get("monthly_target", 0.0) or 0.0)
            daily_target = float(trow.get("daily_target", 0.0) or 0.0)
            actual_sales = float(summary_row.get("total_net_sales", 0.0) or 0.0)

            month_days = monthrange(target_year, target_month)[1]
            month_start = datetime(target_year, target_month, 1).date()
            month_end = datetime(target_year, target_month, month_days).date()
            # Only count the overlap between the selected dashboard range and the target's
            # calendar month, otherwise cross-month filters would overstate the target.
            effective_start = max(start_dt, month_start)
            effective_end = min(end_dt, month_end)
            selected_days = max((effective_end - effective_start).days + 1, 0) if effective_end >= effective_start else 0
            selected_range_target = daily_target * selected_days

            achievement_range = (actual_sales / selected_range_target * 100.0) if selected_range_target > 0 else 0.0
            achievement_monthly = (actual_sales / monthly_target * 100.0) if monthly_target > 0 else 0.0
            remaining_vs_month = monthly_target - actual_sales

            tc1, tc2, tc3, tc4 = st.columns(4)
            with tc1:
                st.metric("Monthly Target", format_currency(monthly_target))
            with tc2:
                st.metric("Per Day Target", format_currency(daily_target))
            with tc3:
                st.metric(
                    "Selected Range Target",
                    format_currency(selected_range_target),
                    delta=f"{selected_days} day(s)",
                )
            with tc4:
                st.metric(
                    "Range Achievement",
                    format_percentage(achievement_range),
                    delta=format_currency(actual_sales),
                )

            tt1, tt2 = st.columns(2)
            with tt1:
                st.metric("Monthly Achievement", format_percentage(achievement_monthly))
            with tt2:
                st.metric("Remaining vs Monthly Target", format_currency(remaining_vs_month))

            st.caption(
                f"Target source: KDS_DB.dbo.call_center_targets | "
                f"Month: {target_year}-{target_month:02d} | "
                f"Sale Point: {trow.get('sale_point', 'Call Center')}"
            )

        st.markdown("---")
        st.subheader("Latest Sales Day Snapshot")
        if latest_df.empty:
            st.info("No latest day snapshot found.")
        else:
            show_latest = latest_df.copy()
            for col in ["gross_before_discount", "total_discount", "total_sales_wo_tax_delivery", "total_net_sales", "subtotal", "tax_amount", "delivery_charges"]:
                if col in show_latest.columns:
                    show_latest[col] = show_latest[col].apply(lambda x: format_currency(float(x or 0)))
            st.dataframe(
                show_latest,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=150, tablet=140, phone=130, kind="compact"),
            )

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Order Type Breakdown")
            show_ot = order_type_df.copy()
            if "total_net_sales" in show_ot.columns:
                show_ot["total_net_sales"] = show_ot["total_net_sales"].apply(lambda x: format_currency(float(x or 0)))
            if "total_discount" in show_ot.columns:
                show_ot["total_discount"] = show_ot["total_discount"].apply(lambda x: format_currency(float(x or 0)))
            st.dataframe(
                show_ot,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=260, tablet=230, phone=210, kind="compact"),
            )
        with c2:
            st.subheader("Payment Status Breakdown")
            show_pay = payment_df.copy()
            if "total_net_sales" in show_pay.columns:
                show_pay["total_net_sales"] = show_pay["total_net_sales"].apply(lambda x: format_currency(float(x or 0)))
            if "total_discount" in show_pay.columns:
                show_pay["total_discount"] = show_pay["total_discount"].apply(lambda x: format_currency(float(x or 0)))
            st.dataframe(
                show_pay,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=260, tablet=230, phone=210, kind="compact"),
            )

        st.markdown("---")
        st.subheader("Order Status Funnel")
        if funnel_df.empty:
            st.info("No order status funnel data found.")
        else:
            funnel_row = funnel_df.iloc[0]
            booked_orders = int(funnel_row.get("booked_orders", 0) or 0)
            dispatched_orders = int(funnel_row.get("dispatched_orders", 0) or 0)
            completed_orders = int(funnel_row.get("completed_orders", 0) or 0)
            rejected_orders = int(funnel_row.get("rejected_orders", 0) or 0)

            drop_booked_to_dispatch = ((booked_orders - dispatched_orders) / booked_orders * 100.0) if booked_orders else 0.0
            drop_dispatch_to_completed = ((dispatched_orders - completed_orders) / dispatched_orders * 100.0) if dispatched_orders else 0.0
            rejected_rate = (rejected_orders / booked_orders * 100.0) if booked_orders else 0.0

            f1, f2, f3, f4 = st.columns(4)
            with f1:
                st.metric("Booked", f"{booked_orders:,}")
            with f2:
                st.metric("Dispatched", f"{dispatched_orders:,}", delta=f"-{format_percentage(drop_booked_to_dispatch)} drop")
            with f3:
                st.metric("Completed", f"{completed_orders:,}", delta=f"-{format_percentage(drop_dispatch_to_completed)} drop")
            with f4:
                st.metric("Rejected", f"{rejected_orders:,}", delta=f"{format_percentage(rejected_rate)} of booked")

            funnel_chart_df = pd.DataFrame(
                {
                    "stage": ["Booked", "Dispatched", "Completed"],
                    "orders": [booked_orders, dispatched_orders, completed_orders],
                    "sales": [
                        float(funnel_row.get("booked_sales", 0.0) or 0.0),
                        float(funnel_row.get("dispatched_sales", 0.0) or 0.0),
                        float(funnel_row.get("completed_sales", 0.0) or 0.0),
                    ],
                }
            )
            # Reuse the same compact frame for both the chart and detail table so the stage
            # ordering stays consistent between visual and numeric views.
            funnel_chart_df = funnel_chart_df.set_index("stage")

            fc1, fc2 = st.columns(2)
            with fc1:
                st.caption("Booked -> Dispatch -> Completed")
                st.bar_chart(funnel_chart_df["orders"], use_container_width=True)
            with fc2:
                show_funnel_sales = funnel_chart_df.reset_index().copy()
                show_funnel_sales["sales"] = show_funnel_sales["sales"].apply(format_currency)
                st.dataframe(
                    show_funnel_sales,
                    use_container_width=True,
                    hide_index=True,
                    height=clamp_dataframe_height(self.responsive, desktop=210, tablet=190, phone=180, kind="compact"),
                )

        st.markdown("---")
        st.subheader("Branch/Counter Drilldown")
        if drilldown_df.empty:
            st.info("No branch/counter drilldown data found.")
        else:
            # The source query is at branch+counter grain. These rollups surface the best
            # performers without losing the detailed matrix further down the page.
            branch_summary = (
                drilldown_df.groupby("branch_id", as_index=False)
                .agg(
                    total_orders=("total_orders", "sum"),
                    total_net_sales=("total_net_sales", "sum"),
                    total_discount=("total_discount", "sum"),
                )
                .sort_values("total_net_sales", ascending=False)
            )
            branch_summary["avg_order_value"] = branch_summary["total_net_sales"] / branch_summary["total_orders"].replace(0, pd.NA)

            counter_summary = (
                drilldown_df.groupby("counter_id", as_index=False)
                .agg(
                    total_orders=("total_orders", "sum"),
                    total_net_sales=("total_net_sales", "sum"),
                    total_discount=("total_discount", "sum"),
                )
                .sort_values("total_net_sales", ascending=False)
            )
            counter_summary["avg_order_value"] = counter_summary["total_net_sales"] / counter_summary["total_orders"].replace(0, pd.NA)

            top_branch_row = branch_summary.iloc[0] if not branch_summary.empty else None
            top_counter_row = counter_summary.iloc[0] if not counter_summary.empty else None

            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.metric("Active Branches", f"{branch_summary['branch_id'].nunique():,}")
            with d2:
                st.metric("Active Counters", f"{counter_summary['counter_id'].nunique():,}")
            with d3:
                if top_branch_row is not None:
                    st.metric(
                        "Top Branch",
                        f"{int(top_branch_row['branch_id'])}",
                        delta=format_currency(float(top_branch_row["total_net_sales"] or 0.0)),
                    )
            with d4:
                if top_counter_row is not None:
                    st.metric(
                        "Top Counter",
                        f"{int(top_counter_row['counter_id'])}",
                        delta=format_currency(float(top_counter_row["total_net_sales"] or 0.0)),
                    )

            b1, b2 = st.columns(2)
            with b1:
                st.caption("Branch Comparison")
                show_branch = branch_summary.copy()
                show_branch["total_net_sales"] = show_branch["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
                show_branch["total_discount"] = show_branch["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
                show_branch["avg_order_value"] = show_branch["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
                st.dataframe(
                    show_branch,
                    use_container_width=True,
                    hide_index=True,
                    height=clamp_dataframe_height(self.responsive, desktop=250, tablet=220, phone=200, kind="compact"),
                )
            with b2:
                st.caption("Counter Comparison")
                show_counter = counter_summary.copy()
                show_counter["total_net_sales"] = show_counter["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
                show_counter["total_discount"] = show_counter["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
                show_counter["avg_order_value"] = show_counter["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
                st.dataframe(
                    show_counter,
                    use_container_width=True,
                    hide_index=True,
                    height=clamp_dataframe_height(self.responsive, desktop=250, tablet=220, phone=200, kind="compact"),
                )

            st.caption("Detailed Branch x Counter Matrix")
            show_drill = drilldown_df.copy()
            show_drill["total_net_sales"] = show_drill["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
            show_drill["total_discount"] = show_drill["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
            show_drill["avg_order_value"] = show_drill["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
            st.dataframe(
                show_drill,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=330, tablet=290, phone=250),
            )

        st.markdown("---")
        st.subheader("Area-wise Sales")
        if area_df.empty:
            st.info("No area-wise sales data found.")
        else:
            top_area = area_df.iloc[0]
            bottom_area = area_df.iloc[-1]

            a1, a2 = st.columns(2)
            with a1:
                st.metric(
                    "Top Area",
                    str(top_area.get("delv_area", "(blank)")),
                    delta=format_currency(float(top_area.get("total_net_sales", 0.0) or 0.0)),
                )
            with a2:
                st.metric(
                    "Bottom Area",
                    str(bottom_area.get("delv_area", "(blank)")),
                    delta=format_currency(float(bottom_area.get("total_net_sales", 0.0) or 0.0)),
                )

            top_areas = area_df.head(5).copy()
            bottom_areas = area_df.tail(5).sort_values("total_net_sales", ascending=True).copy()

            ar1, ar2 = st.columns(2)
            with ar1:
                st.caption("Top 5 Areas by Sales")
                show_top = top_areas.copy()
                show_top["total_net_sales"] = show_top["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
                show_top["total_discount"] = show_top["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
                show_top["avg_order_value"] = show_top["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
                st.dataframe(
                    show_top,
                    use_container_width=True,
                    hide_index=True,
                    height=clamp_dataframe_height(self.responsive, desktop=230, tablet=210, phone=190, kind="compact"),
                )
            with ar2:
                st.caption("Bottom 5 Areas by Sales")
                show_bottom = bottom_areas.copy()
                show_bottom["total_net_sales"] = show_bottom["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
                show_bottom["total_discount"] = show_bottom["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
                show_bottom["avg_order_value"] = show_bottom["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
                st.dataframe(
                    show_bottom,
                    use_container_width=True,
                    hide_index=True,
                    height=clamp_dataframe_height(self.responsive, desktop=230, tablet=210, phone=190, kind="compact"),
                )

            st.caption("Area Sales Chart")
            area_chart_df = area_df.head(15).copy()
            st.bar_chart(area_chart_df.set_index("delv_area")["total_net_sales"], use_container_width=True)

            show_area = area_df.copy()
            show_area["total_net_sales"] = show_area["total_net_sales"].apply(lambda x: format_currency(float(x or 0.0)))
            show_area["total_discount"] = show_area["total_discount"].apply(lambda x: format_currency(float(x or 0.0)))
            show_area["avg_order_value"] = show_area["avg_order_value"].apply(lambda x: format_currency(float(x or 0.0)))
            st.dataframe(
                show_area,
                use_container_width=True,
                hide_index=True,
                height=clamp_dataframe_height(self.responsive, desktop=330, tablet=290, phone=250),
            )

        st.markdown("---")
        st.subheader("Daily Sales Trend")
        if metric_profile.startswith("XLS-aligned"):
            st.caption(f"Business day buckets ({cutoff_hour:02d}:{cutoff_minute:02d} to next-day {cutoff_hour-1:02d}:{cutoff_minute+50:02d}) with DELIVERY + non-deleted scope.")
        else:
            st.caption("Strict/realized daily view using existing exclusion logic.")
        if daily_df.empty:
            st.info("No daily sales found.")
            return

        chart_df = daily_df.sort_values("sales_day")
        st.line_chart(chart_df.set_index("sales_day")["total_net_sales"], use_container_width=True)

        show_daily = daily_df.copy()
        show_daily["total_net_sales"] = show_daily["total_net_sales"].apply(lambda x: format_currency(float(x or 0)))
        if "total_sales_wo_tax_delivery" in show_daily.columns:
            show_daily["total_sales_wo_tax_delivery"] = show_daily["total_sales_wo_tax_delivery"].apply(
                lambda x: format_currency(float(x or 0))
            )
        if "total_tax" in show_daily.columns:
            show_daily["total_tax"] = show_daily["total_tax"].apply(lambda x: format_currency(float(x or 0)))
        if "total_delivery_charges" in show_daily.columns:
            show_daily["total_delivery_charges"] = show_daily["total_delivery_charges"].apply(
                lambda x: format_currency(float(x or 0))
            )
        if "total_discount" in show_daily.columns:
            show_daily["total_discount"] = show_daily["total_discount"].apply(lambda x: format_currency(float(x or 0)))
        st.dataframe(
            show_daily,
            use_container_width=True,
            hide_index=True,
            height=clamp_dataframe_height(self.responsive, desktop=380, tablet=320, phone=280),
        )
