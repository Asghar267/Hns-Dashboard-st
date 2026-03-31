"""
Lightweight SQL helper module for ad-hoc queries and exports.

This module wraps the project's `connection_cloud.DatabaseConnection` and
exposes convenient functions that return pandas.DataFrame for the dashboard
prototyping tasks (daily/monthly/product aggregates, branch summary, sparklines).

The functions are cached with Streamlit's `st.cache_data` where appropriate so
repeated calls are cheap during development.

Usage:
    from modules.sqldatabase import get_daily_sales
    df = get_daily_sales('2026-01-01', '2026-02-28', [8,10])

Note: This file executes queries against the same DatabaseConnection used by
`modules.connection_cloud`. It will automatically fall back to the API proxy or
local CSV (if configured) as that module implements.
"""

from typing import List, Optional
import streamlit as st
import pandas as pd
import logging

from modules.connection_cloud import get_connection_candelahns

logger = logging.getLogger(__name__)


def _placeholders(n: int) -> str:
    return ", ".join(["?"] * n) if n > 0 else ""


@st.cache_data(ttl=300)
def run_query_df(query: str, params: Optional[List] = None) -> pd.DataFrame:
    """Run a SQL query and return a pandas DataFrame.

    This uses the project's DatabaseConnection wrapper so it will work with
    local pyodbc, API proxy, or CSV fallback transparently.
    """
    try:
        conn = get_connection_candelahns()
        df = conn.fetch_dataframe(query, params=params or [])
        return df
    except Exception as e:
        logger.exception("Error running query")
        try:
            st.error(f"Error running query: {e}")
        except Exception:
            pass
        return pd.DataFrame()


@st.cache_data(ttl=300)
def sample_table_rows(table_name: str, top: int = 10) -> pd.DataFrame:
    q = f"SELECT TOP {top} * FROM {table_name}"
    return run_query_df(q)


@st.cache_data(ttl=300)
def get_branch_summary(start_date: str, end_date: str, branch_ids: List[int]) -> pd.DataFrame:
    q = f"""
    SELECT
        sh.shop_id,
        sh.shop_name,
        COUNT(DISTINCT s.sale_id) AS total_sales,
        COALESCE(SUM(s.Nt_amount),0) AS total_Nt_amount
    FROM dbo.tblDefShops sh
    LEFT JOIN dbo.tblSales s
      ON sh.shop_id = s.shop_id AND s.sale_date BETWEEN ? AND ?
    WHERE sh.shop_id IN ({_placeholders(len(branch_ids))})
    GROUP BY sh.shop_id, sh.shop_name
    ORDER BY sh.shop_id
    """
    params = [start_date, end_date] + branch_ids
    return run_query_df(q, params)


@st.cache_data(ttl=300)
def get_daily_sales(start_date: str, end_date: str, branch_ids: List[int]) -> pd.DataFrame:
    q = f"""
    SELECT
      CAST(s.sale_date AS DATE) AS day,
      SUM(s.Nt_amount) AS total_Nt_amount
    FROM dbo.tblSales s
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
    GROUP BY CAST(s.sale_date AS DATE)
    ORDER BY day
    """
    params = [start_date, end_date] + branch_ids
    return run_query_df(q, params)


@st.cache_data(ttl=600)
def get_monthly_sales(start_date: str, end_date: str, branch_ids: List[int]) -> pd.DataFrame:
    q = f"""
    SELECT
      DATEFROMPARTS(YEAR(s.sale_date), MONTH(s.sale_date), 1) AS period_date,
      YEAR(s.sale_date) AS year,
      MONTH(s.sale_date) AS month,
      SUM(s.Nt_amount) AS total_Nt_amount
    FROM dbo.tblSales s
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
    GROUP BY YEAR(s.sale_date), MONTH(s.sale_date)
    ORDER BY period_date
    """
    params = [start_date, end_date] + branch_ids
    return run_query_df(q, params)


@st.cache_data(ttl=300)
def get_product_monthly_sales(year: int, month: int, branch_ids: List[int]) -> pd.DataFrame:
    """Return aggregated product sales (by TempProductBarcode.field_name) for a month."""
    start = f"{year}-{month:02d}-01"
    # naive end-of-month; SQL version uses DATEADD trick below
    q = f"""
    DECLARE @start_date DATE = '{start}';
    DECLARE @end_date DATE = DATEADD(day, -1, DATEADD(month, 1, @start_date));

    SELECT
      t.field_name AS Product,
      SUM(li.qty) AS Total_Qty,
      SUM( (li.qty * li.Unit_price) / NULLIF(st.line_total,0) * s.Nt_amount ) AS Total_Sales
    FROM dbo.tblSales s
    JOIN dbo.tblSalesLineItems li ON s.sale_id = li.sale_id
    JOIN dbo.TempProductBarcode t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    JOIN (
      SELECT sale_id, SUM(qty * Unit_price) AS line_total
      FROM dbo.tblSalesLineItems
      GROUP BY sale_id
    ) st ON st.sale_id = s.sale_id
    WHERE s.sale_date BETWEEN @start_date AND @end_date
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
    GROUP BY t.field_name
    ORDER BY Total_Sales DESC
    """
    params = branch_ids
    return run_query_df(q, params)


@st.cache_data(ttl=300)
def get_product_monthly_sales_by_product(year: int, month: int, branch_ids: List[int], category: Optional[str] = None) -> pd.DataFrame:
    start = f"{year}-{month:02d}-01"
    q = f"""
    DECLARE @start_date DATE = '{start}';
    DECLARE @end_date DATE = DATEADD(day, -1, DATEADD(month, 1, @start_date));

    SELECT
      COALESCE(p.item_name, t.field_name) AS Product,
      SUM(li.qty) AS Total_Qty,
      SUM( (li.qty * li.Unit_price) / NULLIF(st.line_total,0) * s.Nt_amount ) AS Total_Sales
    FROM dbo.tblSales s
    JOIN dbo.tblSalesLineItems li ON s.sale_id = li.sale_id
    LEFT JOIN dbo.TempProductBarcode t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    LEFT JOIN dbo.tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN dbo.tblDefProducts p ON pi.Product_ID = p.product_id
    JOIN (
      SELECT sale_id, SUM(qty * Unit_price) AS line_total
      FROM dbo.tblSalesLineItems
      GROUP BY sale_id
    ) st ON st.sale_id = s.sale_id
    WHERE s.sale_date BETWEEN @start_date AND @end_date
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
    """
    params: List = []
    params.extend(branch_ids)
    if category:
        q += " AND t.field_name = ?"
        params.append(category)

    q += "\n    GROUP BY COALESCE(p.item_name, t.field_name)\n    ORDER BY Total_Sales DESC"
    return run_query_df(q, params)


@st.cache_data(ttl=300)
def get_daily_sales_by_products(start_date: str, end_date: str, branch_ids: List[int], products: List[str]) -> pd.DataFrame:
    if not products:
        return pd.DataFrame()
    prod_placeholders = _placeholders(len(products))
    q = f"""
    SELECT
      CAST(s.sale_date AS DATE) AS day,
      COALESCE(p.item_name, t.field_name) AS Product,
      SUM( (li.qty * li.Unit_price) / NULLIF(st.line_total,0) * s.Nt_amount ) AS total_Nt_amount
    FROM dbo.tblSales s
    JOIN dbo.tblSalesLineItems li ON s.sale_id = li.sale_id
    LEFT JOIN dbo.TempProductBarcode t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    LEFT JOIN dbo.tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN dbo.tblDefProducts p ON pi.Product_ID = p.product_id
    JOIN (
      SELECT sale_id, SUM(qty * Unit_price) AS line_total
      FROM dbo.tblSalesLineItems
      GROUP BY sale_id
    ) st ON st.sale_id = s.sale_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
      AND COALESCE(p.item_name, t.field_name) IN ({prod_placeholders})
    GROUP BY CAST(s.sale_date AS DATE), COALESCE(p.item_name, t.field_name)
    ORDER BY Product, day
    """
    params = [start_date, end_date] + branch_ids + products
    return run_query_df(q, params)


@st.cache_data(ttl=300)
def get_category_monthly_history(start_date: str, end_date: str, branch_ids: List[int]) -> pd.DataFrame:
    q = f"""
    SELECT
      DATEFROMPARTS(YEAR(s.sale_date), MONTH(s.sale_date), 1) AS period_date,
      t.field_name AS Category,
      SUM( (li.qty * li.Unit_price) / NULLIF(st.line_total,0) * s.Nt_amount ) AS total_Nt_amount
    FROM dbo.tblSales s
    JOIN dbo.tblSalesLineItems li ON s.sale_id = li.sale_id
    JOIN dbo.TempProductBarcode t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    JOIN (
      SELECT sale_id, SUM(qty * Unit_price) AS line_total
      FROM dbo.tblSalesLineItems
      GROUP BY sale_id
    ) st ON st.sale_id = s.sale_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({_placeholders(len(branch_ids))})
    GROUP BY DATEFROMPARTS(YEAR(s.sale_date), MONTH(s.sale_date), 1), t.field_name
    ORDER BY Category, period_date
    """
    params = [start_date, end_date] + branch_ids
    return run_query_df(q, params)
