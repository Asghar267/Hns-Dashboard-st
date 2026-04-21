"""
Material Cost Commission Module
Handles product-wise commission calculation based on material costs
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from modules.database import build_filter_clause, pool

logger = logging.getLogger(__name__)
_MCC_SETUP_PATH = Path(__file__).resolve().parents[1] / "config" / "material_cost_commission_tab_setup.json"
_MATERIAL_COST_SALES_FALLBACK_DAYS = int(os.environ.get("MATERIAL_COST_SALES_FALLBACK_DAYS", "180"))

def _is_foodpanda_predicate() -> str:
    # In this DB, Foodpanda orders are tagged via `tblSales.Cust_name` as "Food Panda".
    # Keep it centralized so both branch/product summaries stay consistent.
    return "LOWER(LTRIM(RTRIM(COALESCE(s.Cust_name, '')))) IN ('food panda', 'foodpanda')"


def create_material_cost_commission_table():
    """
    This function is a placeholder since we now use hardcoded data.
    The MaterialCostCommission table is no longer required.
    """
    logger.info("Using hardcoded material cost commission data - no table creation needed")
    return True


# Material cost commission data (hardcoded - can be updated with your data)
MATERIAL_COST_COMMISSION_DATA = [
    {"product_code": 137, "product_name": "Banana Shake", "material_cost": 175.0, "commission": 50},
    {"product_code": 289, "product_name": "BBQ Sauce Dip", "material_cost": 19.3, "commission": 60},
    {"product_code": 11, "product_name": "Beef Behari Cheese Roll", "material_cost": 253.4, "commission": 10},
    {"product_code": 235, "product_name": "Buffalo Wings", "material_cost": 596.9, "commission": 50},
    {"product_code": 960, "product_name": "Chadder Broast ( Breast )", "material_cost": 475.1, "commission": 50},
    {"product_code": 959, "product_name": "Chadder Broast ( Leg )", "material_cost": 470.1, "commission": 70},
    {"product_code": 555, "product_name": "Channa Tarkari", "material_cost": 53.9, "commission": 20},
    {"product_code": 260, "product_name": "Chatni Bowl", "material_cost": 178.2, "commission": 20},
    {"product_code": 91, "product_name": "Cheese Slice", "material_cost": 25.0, "commission": 15},
    {"product_code": 87, "product_name": "Cheese Sauce Dip", "material_cost": 39.1, "commission": 50},
    {"product_code": 136, "product_name": "Chekoo Shake", "material_cost": 120.5, "commission": 70},
    {"product_code": 17, "product_name": "Chicken Behari Cheese Roll", "material_cost": 159.7, "commission": 50},
    {"product_code": 36, "product_name": "Chicken Behari Kabab", "material_cost": 300.8, "commission": 50},
    {"product_code": 20, "product_name": "Chicken Crispy Cheese Roll", "material_cost": 199.8, "commission": 50},
    {"product_code": 40, "product_name": "Chicken Masala Boti", "material_cost": 317.1, "commission": 100},
    {"product_code": 60, "product_name": "Chicken Pineapple Salad", "material_cost": 512.5, "commission": 50},
    {"product_code": 14, "product_name": "Chicken Reshmi Kabab Cheese Roll", "material_cost": 135.9, "commission": 50},
    {"product_code": 13, "product_name": "Chicken Reshmi Kabab Garlic Roll", "material_cost": 147.6, "commission": 50},
    {"product_code": 68, "product_name": "Chicken Supreme Burger", "material_cost": 421.2, "commission": 70},
    {"product_code": 201, "product_name": "Chicken Tikka Wash ( Breast)", "material_cost": 214.8, "commission": 50},
    {"product_code": 203, "product_name": "Chicken Tikka Wash Leg", "material_cost": 214.9, "commission": 50},
    {"product_code": 135, "product_name": "Date Shake", "material_cost": 155.9, "commission": 50},
    {"product_code": 162, "product_name": "Disposable Glass with Ice", "material_cost": 21.7, "commission": 10},
    {"product_code": 227, "product_name": "Fish Crackers Basket", "material_cost": 58.7, "commission": 10},
    {"product_code": 61, "product_name": "Fruit Salad", "material_cost": 449.1, "commission": 50},
    {"product_code": 271, "product_name": "Fusion Platter (3)", "material_cost": 849.9, "commission": 80},
    {"product_code": 953, "product_name": "Garlic Mayo Broast ( Leg ) Topping", "material_cost": 439.2, "commission": 50},
    {"product_code": 957, "product_name": "Garlic Mayo Broast ( Breast ) Topping", "material_cost": 509.2, "commission": 50},
    {"product_code": 955, "product_name": "Garlic Mayo Fries Topping", "material_cost": 255.4, "commission": 30},
    {"product_code": 79, "product_name": "Golden Nuggets (10 Pcs)", "material_cost": 299.6, "commission": 100},
    {"product_code": 127, "product_name": "Grape Fruit", "material_cost": 233.8, "commission": 10},
    {"product_code": 803, "product_name": "Green Masala Chicken", "material_cost": 309.1, "commission": 30},
    {"product_code": 66, "product_name": "Grilled Breast Burger", "material_cost": 336.2, "commission": 50},
    {"product_code": 90, "product_name": "Hot Dog Bun", "material_cost": 32.0, "commission": 5},
    {"product_code": 166, "product_name": "Kheer", "material_cost": 170.3, "commission": 10},
    {"product_code": 255, "product_name": "Kunafa", "material_cost": 343.6, "commission": 50},
    {"product_code": 230, "product_name": "Mix Vegetable Handi", "material_cost": 338.2, "commission": 50},
    {"product_code": 231, "product_name": "Mix Vegetable Pulao", "material_cost": 197.0, "commission": 50},
    {"product_code": 106, "product_name": "Mutton Biryani", "material_cost": 979.0, "commission": 150},
    {"product_code": 129, "product_name": "Orange Juice", "material_cost": 173.0, "commission": 15},
    {"product_code": 140, "product_name": "Oreo Shake", "material_cost": 340.6, "commission": 20},
    {"product_code": 103, "product_name": "Palak Paneer Handi", "material_cost": 539.4, "commission": 100},
    {"product_code": 232, "product_name": "Paneer Makhni Handi", "material_cost": 810.3, "commission": 50},
    {"product_code": 233, "product_name": "Paneer Vegetable Karahi", "material_cost": 440.9, "commission": 50},
    {"product_code": 234, "product_name": "Peri Bite", "material_cost": 394.5, "commission": 50},
    {"product_code": 198, "product_name": "Peshawari Chicken Karahi", "material_cost": 430.1, "commission": 100},
    {"product_code": 199, "product_name": "Peshawari Mutton Karahi", "material_cost": 1276.9, "commission": 100},
    {"product_code": 131, "product_name": "Pineapple Shake", "material_cost": 192.2, "commission": 10},
    {"product_code": 109, "product_name": "Plain Rice", "material_cost": 102.0, "commission": 50},
    {"product_code": 101, "product_name": "Red Handi", "material_cost": 396.0, "commission": 150},
    {"product_code": 26, "product_name": "Seekh Kabab Cheese Roll", "material_cost": 158.8, "commission": 30},
    {"product_code": 25, "product_name": "Seekh Kabab Garlic Mayo Roll", "material_cost": 170.5, "commission": 30},
    {"product_code": 94, "product_name": "Special Chicken Karahi", "material_cost": 480.0, "commission": 100},
    {"product_code": 147, "product_name": "The Mighty Meat Platter", "material_cost": 3437.8, "commission": 200},
    {"product_code": 951, "product_name": "The Velvet Stack Burger", "material_cost": 512.2, "commission": 50},
    {"product_code": 192, "product_name": "Thunder Fries Topping", "material_cost": 173.2, "commission": 60},
    {"product_code": 115, "product_name": "Vanilla Single Scoop", "material_cost": 53.7, "commission": 30},
    {"product_code": 855, "product_name": "Volcano Drums", "material_cost": 431.2, "commission": 30},
    {"product_code": 566, "product_name": "Palak Paneer Nashta", "material_cost": 183.93, "commission": 50},
    {"product_code": 701, "product_name": "Iftar Deal 1 ( Serve 2)", "material_cost": 1689, "commission": 100},
    {"product_code": 703, "product_name": "Iftar Deal 2 (Serve3)", "material_cost": 2717, "commission": 100},
    {"product_code": 704, "product_name": "Iftar Deal 3 ( Serve 4)", "material_cost": 3218, "commission": 100},
    {"product_code": 705, "product_name": "Iftar Deal 4 ( Serve 5)", "material_cost": 2774, "commission": 100},
    {"product_code": 706, "product_name": "SEHRI DEAL 1 (SERVE 2)", "material_cost": 1156, "commission": 100},
    {"product_code": 707, "product_name": "SEHRI DEAL 2 SERVE 3", "material_cost": 2056, "commission": 100},
    {"product_code": 708, "product_name": "SEHRI DEAL 3 SERVE 4", "material_cost": 1679, "commission": 100},
    {"product_code": 709, "product_name": "SEHRI DEAL 4 SERVE 5", "material_cost": 2706, "commission": 100},
]


def _esc_sql_text(value: str) -> str:
    return str(value).replace("'", "''")


def _normalize_commission_data(commission_data: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Normalize tab-level commission data and filter inactive rows."""
    if commission_data is None:
        return pd.DataFrame()

    required = {"product_code", "product_name", "material_cost", "commission"}
    if not required.issubset(set(commission_data.columns)):
        return pd.DataFrame()

    df = commission_data.copy()
    if "active" in df.columns:
        df = df[df["active"].fillna(False).astype(bool)]

    for col in ["product_code", "material_cost", "commission"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["product_code", "material_cost", "commission"])

    df["product_code"] = df["product_code"].astype(int)
    df["product_name"] = df["product_name"].astype(str).str.strip()
    return df[["product_code", "product_name", "material_cost", "commission"]]


def _commission_values_sql(commission_data: Optional[pd.DataFrame] = None) -> str:
    """
    Build SQL to fetch commission data from the database.
    Falls back to hardcoded data if table does not exist.
    """
    override_df = _normalize_commission_data(commission_data)
    if not override_df.empty:
        rows = ",\n                ".join(
            f"({int(row.product_code)}, '{_esc_sql_text(row.product_name)}', {float(row.material_cost)}, {float(row.commission)})"
            for row in override_df.itertuples(index=False)
        )
        return f"""
            SELECT product_code, product_name, material_cost, commission
            FROM (
                VALUES
                {rows}
            ) AS mcc(product_code, product_name, material_cost, commission)
        """

    try:
        conn = pool.get_connection("candelahns")
        # Check if table exists
        check_q = "SELECT OBJECT_ID('dbo.MaterialCostCommission', 'U') as table_id"
        table_exists = pd.read_sql(check_q, conn).iloc[0]['table_id'] is not None
        
        if table_exists:
            return "SELECT product_code, product_name, material_cost, commission FROM dbo.MaterialCostCommission"
    except Exception as e:
        logger.warning(f"Error checking MaterialCostCommission table: {e}")

    # Fallback to hardcoded values
    rows = ",\n                ".join(
        f"({int(item['product_code'])}, '{_esc_sql_text(item['product_name'])}', {float(item['material_cost'])}, {float(item['commission'])})"
        for item in MATERIAL_COST_COMMISSION_DATA
    )
    return f"""
            SELECT product_code, product_name, material_cost, commission
            FROM (
                VALUES
                {rows}
            ) AS mcc(product_code, product_name, material_cost, commission)
    """


def _base_commission_df(commission_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    override_df = _normalize_commission_data(commission_data)
    if not override_df.empty:
        return override_df.copy()

    try:
        conn = pool.get_connection("candelahns")
        check_q = "SELECT OBJECT_ID('dbo.MaterialCostCommission', 'U') as table_id"
        table_exists = pd.read_sql(check_q, conn).iloc[0]["table_id"] is not None
        if table_exists:
            table_df = pd.read_sql(
                "SELECT product_code, product_name, material_cost, commission FROM dbo.MaterialCostCommission",
                conn,
            )
            if table_df is not None and not table_df.empty:
                for col in ["product_code", "material_cost", "commission"]:
                    table_df[col] = pd.to_numeric(table_df[col], errors="coerce")
                table_df = table_df.dropna(subset=["product_code", "material_cost", "commission"])
                table_df["product_code"] = table_df["product_code"].astype(int)
                table_df["product_name"] = table_df["product_name"].astype(str).str.strip()
                return table_df[["product_code", "product_name", "material_cost", "commission"]]
    except Exception:
        pass

    return pd.DataFrame(MATERIAL_COST_COMMISSION_DATA)[["product_code", "product_name", "material_cost", "commission"]]


def _fetch_fallback_costs_for_codes(product_codes: List[int]) -> pd.DataFrame:
    if not product_codes:
        return pd.DataFrame(columns=["product_code", "fallback_cost", "material_cost_source"])
    values_clause = ",".join(["(?)"] * len(product_codes))
    try:
        conn = pool.get_connection("candelahns")
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH pic AS (
            SELECT
                CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END AS product_code,
                AVG(TRY_CAST(pi.Avg_Cost_Price AS FLOAT)) AS cost_value
            FROM tblProductItem pi WITH (NOLOCK)
            INNER JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.Product_ID
            GROUP BY CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END
        ),
        dpc AS (
            SELECT
                CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END AS product_code,
                AVG(TRY_CAST(p.Average_cost AS FLOAT)) AS cost_value
            FROM tblDefProducts p WITH (NOLOCK)
            GROUP BY CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END
        ),
        slc AS (
            SELECT
                COALESCE(
                    CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END,
                    CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END
                ) AS product_code,
                AVG(TRY_CAST(li.avg_Cost AS FLOAT)) AS cost_value
            FROM tblSales s WITH (NOLOCK)
            INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
            LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
            LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.Product_ID
            WHERE CAST(s.sale_date AS date) >= DATEADD(day, -{int(_MATERIAL_COST_SALES_FALLBACK_DAYS)}, CAST(GETDATE() AS date))
            GROUP BY COALESCE(
                CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END,
                CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END
            )
        )
        SELECT
            c.product_code,
            CASE
                WHEN pic.cost_value IS NOT NULL AND pic.cost_value > 0 THEN pic.cost_value
                WHEN dpc.cost_value IS NOT NULL AND dpc.cost_value > 0 THEN dpc.cost_value
                WHEN slc.cost_value IS NOT NULL AND slc.cost_value > 0 THEN slc.cost_value
                ELSE 0
            END AS fallback_cost,
            CASE
                WHEN pic.cost_value IS NOT NULL AND pic.cost_value > 0 THEN 'product_item_avg_cost_price'
                WHEN dpc.cost_value IS NOT NULL AND dpc.cost_value > 0 THEN 'defproducts_average_cost'
                WHEN slc.cost_value IS NOT NULL AND slc.cost_value > 0 THEN 'salesline_avg_cost'
                ELSE 'missing'
            END AS material_cost_source
        FROM (
            SELECT DISTINCT CAST(v.code AS INT) AS product_code
            FROM (VALUES {values_clause}) v(code)
        ) c
        LEFT JOIN pic ON c.product_code = pic.product_code
        LEFT JOIN dpc ON c.product_code = dpc.product_code
        LEFT JOIN slc ON c.product_code = slc.product_code
        """
        df = pd.read_sql(query, conn, params=product_codes)
        if df is None or df.empty:
            return pd.DataFrame(columns=["product_code", "fallback_cost", "material_cost_source"])
        df["product_code"] = pd.to_numeric(df["product_code"], errors="coerce").fillna(-1).astype(int)
        df["fallback_cost"] = pd.to_numeric(df["fallback_cost"], errors="coerce").fillna(0.0)
        df["material_cost_source"] = df["material_cost_source"].astype(str)
        return df[["product_code", "fallback_cost", "material_cost_source"]]
    except Exception as e:
        logger.warning(f"Error fetching fallback material costs: {e}")
        return pd.DataFrame(columns=["product_code", "fallback_cost", "material_cost_source"])


def resolve_material_cost_dataframe(
    product_map: pd.DataFrame,
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Resolve material costs with manual source priority and DB fallbacks."""
    if product_map is None or product_map.empty:
        return pd.DataFrame(
            columns=[
                "product_code",
                "product_name",
                "material_cost",
                "commission",
                "material_cost_source",
                "material_cost_resolved",
            ]
        )

    base = _base_commission_df(commission_data).copy()
    for col in ["product_code", "material_cost", "commission"]:
        base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base.dropna(subset=["product_code"])
    base["product_code"] = base["product_code"].astype(int)
    base["product_name"] = base["product_name"].astype(str).str.strip()
    base["material_cost"] = pd.to_numeric(base["material_cost"], errors="coerce")
    base["commission"] = pd.to_numeric(base["commission"], errors="coerce").fillna(0.0)
    base = base.drop_duplicates(subset=["product_code"], keep="last")

    pm = product_map.copy()
    pm["product_code"] = pd.to_numeric(pm["product_code"], errors="coerce")
    pm = pm.dropna(subset=["product_code"])
    pm["product_code"] = pm["product_code"].astype(int)
    pm["product_name"] = pm["product_name"].astype(str).str.strip()
    pm = pm.drop_duplicates(subset=["product_code"], keep="last")

    merged = pm.merge(
        base[["product_code", "material_cost", "commission"]],
        on="product_code",
        how="left",
    )
    merged["material_cost_source"] = "manual"
    missing_mask = merged["material_cost"].isna() | (pd.to_numeric(merged["material_cost"], errors="coerce") <= 0)
    missing_codes = merged.loc[missing_mask, "product_code"].dropna().astype(int).unique().tolist()
    if missing_codes:
        fb = _fetch_fallback_costs_for_codes(missing_codes)
        merged = merged.merge(fb, on="product_code", how="left")
        if "material_cost_source_x" in merged.columns:
            merged["material_cost_source"] = merged["material_cost_source_x"].fillna("manual")
        else:
            merged["material_cost_source"] = merged.get("material_cost_source", "manual")
        use_fb = merged["material_cost"].isna() | (pd.to_numeric(merged["material_cost"], errors="coerce") <= 0)
        merged.loc[use_fb, "material_cost"] = pd.to_numeric(merged.loc[use_fb, "fallback_cost"], errors="coerce").fillna(0.0)
        merged.loc[use_fb, "material_cost_source"] = merged.loc[use_fb, "material_cost_source_y"].fillna("missing")
        merged = merged.drop(columns=["fallback_cost", "material_cost_source_y", "material_cost_source_x"], errors="ignore")
    merged["material_cost"] = pd.to_numeric(merged["material_cost"], errors="coerce").fillna(0.0)
    merged["commission"] = pd.to_numeric(merged["commission"], errors="coerce").fillna(0.0)
    merged["material_cost_source"] = merged["material_cost_source"].fillna("manual")
    if "material_cost_source_x" in merged.columns:
        merged = merged.drop(columns=["material_cost_source_x"], errors="ignore")
    merged["material_cost_resolved"] = merged["material_cost"]

    return merged[
        [
            "product_code",
            "product_name",
            "material_cost",
            "commission",
            "material_cost_source",
            "material_cost_resolved",
        ]
    ].drop_duplicates(subset=["product_code"], keep="last")


def _fetch_sales_product_map(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
) -> pd.DataFrame:
    if not branch_ids:
        return pd.DataFrame(columns=["product_code", "product_name"])
    try:
        conn = pool.get_connection("candelahns")
        filter_clause, filter_params = build_filter_clause(data_mode)
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            COALESCE(
                CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END,
                CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END
            ) AS product_code,
            COALESCE(NULLIF(LTRIM(RTRIM(p.item_name)), ''), '(Unknown)') AS product_name
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.Product_ID
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({",".join(["?"] * len(branch_ids))})
            {filter_clause}
        GROUP BY
            COALESCE(
                CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END,
                CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END
            ),
            COALESCE(NULLIF(LTRIM(RTRIM(p.item_name)), ''), '(Unknown)')
        """
        params = [start_date, end_date] + branch_ids + filter_params
        df = pd.read_sql(query, conn, params=params)
        if df is None or df.empty:
            return pd.DataFrame(columns=["product_code", "product_name"])
        df["product_code"] = pd.to_numeric(df["product_code"], errors="coerce")
        df = df.dropna(subset=["product_code"])
        df["product_code"] = df["product_code"].astype(int)
        df["product_name"] = df["product_name"].astype(str).str.strip()
        return df[["product_code", "product_name"]].drop_duplicates(subset=["product_code"], keep="last")
    except Exception as e:
        logger.warning(f"Error fetching sales product map for cost recovery: {e}")
        return pd.DataFrame(columns=["product_code", "product_name"])


def _commission_values_sql_with_sales_recovery(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    commission_data: Optional[pd.DataFrame] = None,
) -> str:
    product_map = _fetch_sales_product_map(start_date, end_date, branch_ids, data_mode)
    if product_map is None or product_map.empty:
        return _commission_values_sql(commission_data)
    resolved = resolve_material_cost_dataframe(product_map=product_map, commission_data=commission_data)
    if resolved is None or resolved.empty:
        return _commission_values_sql(commission_data)
    rows = ",\n                ".join(
        f"({int(row.product_code)}, '{_esc_sql_text(row.product_name)}', {float(row.material_cost)}, {float(row.commission)})"
        for row in resolved.itertuples(index=False)
    )
    return f"""
            SELECT product_code, product_name, material_cost, commission
            FROM (
                VALUES
                {rows}
            ) AS mcc(product_code, product_name, material_cost, commission)
    """


def _product_match_expression() -> str:
    return (
        "COALESCE("
        "CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END, "
        "CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END"
        ")"
    )


def _build_employee_filter(employee_ids: Optional[List[int]]) -> Tuple[str, List[int]]:
    if employee_ids:
        return f"AND s.employee_id IN ({','.join(['?' for _ in employee_ids])})", employee_ids
    return "", []


def get_material_cost_commission_data(commission_data: Optional[pd.DataFrame] = None):
    """Get all material cost commission data - uses hardcoded data"""
    try:
        override_df = _normalize_commission_data(commission_data)
        if not override_df.empty:
            return override_df.copy()
        return pd.DataFrame(MATERIAL_COST_COMMISSION_DATA)
    except Exception as e:
        logger.error(f"Error fetching material cost commission data: {e}")
        return pd.DataFrame()


def load_persisted_material_cost_commission_setup() -> pd.DataFrame:
    """Load persisted tab-only commission setup from JSON; fallback to defaults."""
    base_df = pd.DataFrame(MATERIAL_COST_COMMISSION_DATA).copy()
    base_df["active"] = True

    if not _MCC_SETUP_PATH.exists():
        return base_df

    try:
        rows = json.loads(_MCC_SETUP_PATH.read_text(encoding="utf-8"))
        persisted_df = pd.DataFrame(rows)
        required = {"product_code", "product_name", "material_cost", "commission"}
        if not required.issubset(set(persisted_df.columns)):
            return base_df

        if "active" not in persisted_df.columns:
            persisted_df["active"] = True

        for col in ["product_code", "material_cost", "commission"]:
            persisted_df[col] = pd.to_numeric(persisted_df[col], errors="coerce")
        persisted_df["active"] = persisted_df["active"].fillna(False).astype(bool)
        persisted_df = persisted_df.dropna(subset=["product_code", "material_cost", "commission"])
        persisted_df["product_code"] = persisted_df["product_code"].astype(int)
        persisted_df["product_name"] = persisted_df["product_name"].astype(str).str.strip()
        persisted_df = persisted_df[
            ["product_code", "product_name", "material_cost", "commission", "active"]
        ].drop_duplicates(subset=["product_code"], keep="last")

        merged = base_df.set_index("product_code")
        incoming = persisted_df.set_index("product_code")
        common_idx = merged.index.intersection(incoming.index)
        merged.loc[common_idx, ["commission", "active"]] = incoming.loc[common_idx, ["commission", "active"]]
        merged.loc[common_idx, "product_name"] = incoming.loc[common_idx, "product_name"]

        extra = incoming[~incoming.index.isin(merged.index)].copy()
        if not extra.empty:
            merged = pd.concat([merged, extra], axis=0)

        return merged.reset_index()[["product_code", "product_name", "material_cost", "commission", "active"]]
    except Exception as e:
        logger.warning(f"Failed to load persisted material cost setup: {e}")
        return base_df


def save_persisted_material_cost_commission_setup(setup_df: pd.DataFrame) -> bool:
    """Persist tab-only commission setup to JSON."""
    try:
        required = {"product_code", "product_name", "material_cost", "commission", "active"}
        if not required.issubset(set(setup_df.columns)):
            return False

        out_df = setup_df.copy()
        for col in ["product_code", "material_cost", "commission"]:
            out_df[col] = pd.to_numeric(out_df[col], errors="coerce")
        out_df["active"] = out_df["active"].fillna(False).astype(bool)
        out_df = out_df.dropna(subset=["product_code", "material_cost", "commission"])
        out_df["product_code"] = out_df["product_code"].astype(int)
        out_df["product_name"] = out_df["product_name"].astype(str).str.strip()
        out_df = out_df[
            ["product_code", "product_name", "material_cost", "commission", "active"]
        ].drop_duplicates(subset=["product_code"], keep="last")

        _MCC_SETUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        _MCC_SETUP_PATH.write_text(
            json.dumps(out_df.to_dict(orient="records"), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save persisted material cost setup: {e}")
        return False


def get_product_material_cost_commission(product_code: int) -> Optional[Dict]:
    """Get material cost and commission for a specific product"""
    try:
        for item in MATERIAL_COST_COMMISSION_DATA:
            if item["product_code"] == product_code:
                return item
        return None
    except Exception as e:
        logger.error(f"Error fetching material cost for product {product_code}: {e}")
        return None


def get_material_cost_commission_analysis(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    employee_ids: Optional[List[int]] = None,
    data_mode: str = "Filtered",
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Get material cost commission analysis by product, employee, and branch."""
    if not branch_ids:
        return pd.DataFrame()
    try:
        conn = pool.get_connection("candelahns")
        mcc_sql = _commission_values_sql_with_sales_recovery(
            start_date, end_date, branch_ids, data_mode, commission_data
        )
        product_match = _product_match_expression()
        employee_filter, employee_params = _build_employee_filter(employee_ids)
        filter_clause, filter_params = build_filter_clause(data_mode)

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            {product_match} AS product_code,
            mcc.product_name,
            mcc.material_cost,
            mcc.commission,
            sh.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            SUM(li.qty) AS units_sold,
            SUM(li.qty * li.Unit_price) AS total_sales,
            SUM(li.qty * mcc.material_cost) AS total_material_cost,
            SUM(li.qty * mcc.commission) AS total_commission
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
            {employee_filter}
            {filter_clause}
        GROUP BY
            {product_match}, mcc.product_name,
            mcc.material_cost, mcc.commission,
            sh.shop_id, sh.shop_name, COALESCE(e.shop_employee_id, 0),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY sh.shop_id, product_name, total_commission DESC
        """

        params = [start_date, end_date] + branch_ids + employee_params + filter_params
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            # Ensure columns are numeric to avoid object dtype errors during arithmetic
            df["material_cost"] = pd.to_numeric(df["material_cost"], errors="coerce").fillna(0.0)
            df["commission"] = pd.to_numeric(df["commission"], errors="coerce").fillna(0.0)
            
            denom = df["material_cost"].replace(0, pd.NA)
            df["commission_rate"] = (df["commission"] / denom * 100).fillna(0.0)
            df["commission_rate"] = pd.to_numeric(df["commission_rate"], errors="coerce").round(2).fillna(0.0)
        return df
    except Exception as e:
        logger.error(f"Error in material cost commission analysis: {e}")
        return pd.DataFrame()


def get_employee_material_cost_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    employee_ids: Optional[List[int]] = None,
    data_mode: str = "Filtered",
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Get employee-wise material cost commission summary."""
    if not branch_ids:
        return pd.DataFrame()
    try:
        conn = pool.get_connection("candelahns")
        mcc_sql = _commission_values_sql_with_sales_recovery(
            start_date, end_date, branch_ids, data_mode, commission_data
        )
        product_match = _product_match_expression()
        employee_filter, employee_params = _build_employee_filter(employee_ids)
        filter_clause, filter_params = build_filter_clause(data_mode)

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            sh.shop_id, sh.shop_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions,
            SUM(li.qty) AS total_units_sold,
            SUM(li.qty * li.Unit_price) AS total_sales,
            SUM(li.qty * mcc.material_cost) AS total_material_cost,
            SUM(li.qty * mcc.commission) AS total_commission,
            AVG(mcc.commission / NULLIF(mcc.material_cost, 0) * 100.0) AS avg_commission_rate
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
            {employee_filter}
            {filter_clause}
        GROUP BY
            COALESCE(e.shop_employee_id, 0), COALESCE(e.field_name, 'Online/Unassigned'),
            sh.shop_id, sh.shop_name
        ORDER BY sh.shop_id, total_commission DESC
        """

        params = [start_date, end_date] + branch_ids + employee_params + filter_params
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["avg_commission_rate"] = df["avg_commission_rate"].round(2)
        return df
    except Exception as e:
        logger.error(f"Error in employee material cost summary: {e}")
        return pd.DataFrame()


def get_branch_material_cost_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str = "Filtered",
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Get branch-wise material cost commission summary."""
    if not branch_ids:
        return pd.DataFrame()
    try:
        conn = pool.get_connection("candelahns")
        mcc_sql = _commission_values_sql_with_sales_recovery(
            start_date, end_date, branch_ids, data_mode, commission_data
        )
        product_match = _product_match_expression()
        filter_clause, filter_params = build_filter_clause(data_mode)
        is_fp = _is_foodpanda_predicate()
        is_non_fp = f"NOT ({is_fp})"

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            sh.shop_id, sh.shop_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions,
            COUNT(DISTINCT s.employee_id) AS active_employees,
            SUM(li.qty) AS total_units_sold,
            SUM(li.qty * li.Unit_price) AS total_sales,
            SUM(CASE WHEN {is_fp} THEN li.qty ELSE 0 END) AS foodpanda_total_units,
            SUM(CASE WHEN {is_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS foodpanda_total_sales,
            SUM(CASE WHEN {is_non_fp} THEN li.qty ELSE 0 END) AS non_foodpanda_total_units,
            SUM(CASE WHEN {is_non_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS non_foodpanda_total_sales,
            SUM(li.qty * mcc.material_cost) AS total_material_cost,
            SUM(li.qty * mcc.commission) AS total_commission,
            AVG(mcc.commission / NULLIF(mcc.material_cost, 0) * 100.0) AS avg_commission_rate
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
            {filter_clause}
        GROUP BY sh.shop_id, sh.shop_name
        ORDER BY total_commission DESC
        """

        params = [start_date, end_date] + branch_ids + filter_params
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["avg_commission_rate"] = df["avg_commission_rate"].round(2)
        return df
    except Exception as e:
        logger.error(f"Error in branch material cost summary: {e}")
        return pd.DataFrame()


def get_branch_product_material_cost_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str = "Filtered",
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Get product-wise summary per branch."""
    if not branch_ids:
        return pd.DataFrame()
    try:
        conn = pool.get_connection("candelahns")
        mcc_sql = _commission_values_sql_with_sales_recovery(
            start_date, end_date, branch_ids, data_mode, commission_data
        )
        product_match = _product_match_expression()
        filter_clause, filter_params = build_filter_clause(data_mode)
        is_fp = _is_foodpanda_predicate()
        is_non_fp = f"NOT ({is_fp})"

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            sh.shop_id,
            sh.shop_name,
            {product_match} AS product_code,
            mcc.product_name,
            mcc.material_cost,
            mcc.commission,
            COUNT(DISTINCT pi.Product_ID) AS distinct_product_ids,
            COUNT(DISTINCT li.Unit_price) AS distinct_unit_prices,
            MIN(li.Unit_price) AS min_unit_price,
            MAX(li.Unit_price) AS max_unit_price,
            SUM(li.qty) AS total_units_sold,
            SUM(li.qty * li.Unit_price) AS total_sales,
            SUM(CASE WHEN {is_fp} THEN li.qty ELSE 0 END) AS foodpanda_total_units,
            SUM(CASE WHEN {is_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS foodpanda_total_sales,
            COUNT(DISTINCT CASE WHEN {is_fp} THEN li.Unit_price END) AS foodpanda_distinct_unit_prices,
            MIN(CASE WHEN {is_fp} THEN li.Unit_price END) AS foodpanda_unit_price,
            SUM(CASE WHEN {is_non_fp} THEN li.qty ELSE 0 END) AS non_foodpanda_total_units,
            SUM(CASE WHEN {is_non_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS non_foodpanda_total_sales,
            COUNT(DISTINCT CASE WHEN {is_non_fp} THEN li.Unit_price END) AS non_foodpanda_distinct_unit_prices,
            MAX(CASE WHEN {is_non_fp} THEN li.Unit_price END) AS non_foodpanda_unit_price,
            SUM(li.qty * mcc.material_cost) AS total_material_cost,
            SUM(li.qty * mcc.commission) AS total_commission,
            (mcc.commission / NULLIF(mcc.material_cost, 0) * 100.0) AS commission_rate
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
            {filter_clause}
        GROUP BY
            sh.shop_id,
            sh.shop_name,
            {product_match},
            mcc.product_name,
            mcc.material_cost,
            mcc.commission
        ORDER BY sh.shop_id, product_name
        """

        params = [start_date, end_date] + branch_ids + filter_params
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["commission_rate"] = df["commission_rate"].round(2)
        return df
    except Exception as e:
        logger.error(f"Error in branch product material cost summary: {e}")
        return pd.DataFrame()


def get_product_material_cost_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str = "Filtered",
    commission_data: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Get product-wise material cost commission summary."""
    if not branch_ids:
        return pd.DataFrame()
    try:
        conn = pool.get_connection("candelahns")
        mcc_sql = _commission_values_sql_with_sales_recovery(
            start_date, end_date, branch_ids, data_mode, commission_data
        )
        product_match = _product_match_expression()
        filter_clause, filter_params = build_filter_clause(data_mode)
        is_fp = _is_foodpanda_predicate()
        is_non_fp = f"NOT ({is_fp})"

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            {product_match} AS product_code,
            mcc.product_name,
            mcc.material_cost,
            mcc.commission,
            COUNT(DISTINCT s.sale_id) AS total_transactions,
            COUNT(DISTINCT pi.Product_ID) AS distinct_product_ids,
            COUNT(DISTINCT li.Unit_price) AS distinct_unit_prices,
            MIN(li.Unit_price) AS min_unit_price,
            MAX(li.Unit_price) AS max_unit_price,
            SUM(li.qty) AS total_units_sold,
            SUM(li.qty * li.Unit_price) AS total_sales,
            SUM(CASE WHEN {is_fp} THEN li.qty ELSE 0 END) AS foodpanda_total_units,
            SUM(CASE WHEN {is_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS foodpanda_total_sales,
            COUNT(DISTINCT CASE WHEN {is_fp} THEN li.Unit_price END) AS foodpanda_distinct_unit_prices,
            MIN(CASE WHEN {is_fp} THEN li.Unit_price END) AS foodpanda_unit_price,
            SUM(CASE WHEN {is_non_fp} THEN li.qty ELSE 0 END) AS non_foodpanda_total_units,
            SUM(CASE WHEN {is_non_fp} THEN li.qty * li.Unit_price ELSE 0 END) AS non_foodpanda_total_sales,
            COUNT(DISTINCT CASE WHEN {is_non_fp} THEN li.Unit_price END) AS non_foodpanda_distinct_unit_prices,
            MAX(CASE WHEN {is_non_fp} THEN li.Unit_price END) AS non_foodpanda_unit_price,
            SUM(li.qty * mcc.material_cost) AS total_material_cost,
            SUM(li.qty * mcc.commission) AS total_commission,
            (mcc.commission / NULLIF(mcc.material_cost, 0) * 100.0) AS commission_rate
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
            {filter_clause}
        GROUP BY
            {product_match},
            mcc.product_name,
            mcc.material_cost,
            mcc.commission
        ORDER BY total_commission DESC
        """

        params = [start_date, end_date] + branch_ids + filter_params
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["commission_rate"] = df["commission_rate"].round(2)
        return df
    except Exception as e:
        logger.error(f"Error in product material cost summary: {e}")
        return pd.DataFrame()
