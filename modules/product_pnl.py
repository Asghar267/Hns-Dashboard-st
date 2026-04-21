"""
Product PNL data helpers.
Provides branch-product profitability tables split by Non-Foodpanda and Foodpanda channels.
"""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from modules.database import build_filter_clause, placeholders, pool
from modules.material_cost_commission import resolve_material_cost_dataframe

PRODUCT_PNL_CATEGORY_LABELS = [
    "Sales - Rolls",
    "Sales - Fast Food",
    "Sales - Handi",
    "Sales - Bar B Q",
    "Sales - Chinese",
    "Sales - Beverages",
    "Sales-Tandoor",
    "Sales - Karahi",
    "Sales - Juices Shakes & Desserts",
    "Deals",
    "Sales Side Orders",
    "Sales-Nashta",
]

_CATEGORY_CANONICAL_MAP = {
    "SALES-ROLLS": "Sales - Rolls",
    "SALES-FAST FOOD": "Sales - Fast Food",
    "SALES-HANDI": "Sales - Handi",
    "SALES-BAR B Q": "Sales - Bar B Q",
    "SALES-CHINESE": "Sales - Chinese",
    "SALES-BEVERAGES": "Sales - Beverages",
    "SALES-TANDOOR": "Sales-Tandoor",
    "SALES-KARAHI": "Sales - Karahi",
    "SALES-JUICES SHAKES & DESSERTS": "Sales - Juices Shakes & Desserts",
    "DEALS": "Deals",
    "SALES SIDE ORDERS": "Sales Side Orders",
    "SALES-NASHTA": "Sales-Nashta",
}


def _is_foodpanda_predicate() -> str:
    return "LOWER(LTRIM(RTRIM(COALESCE(s.Cust_name, '')))) IN ('food panda', 'foodpanda')"


def _product_match_expression() -> str:
    return (
        "COALESCE("
        "CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END, "
        "CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END, "
        "li.Product_Item_ID"
        ")"
    )


def _normalize_category_key(text: str) -> str:
    value = str(text or "").strip().upper()
    value = " ".join(value.split())
    value = value.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
    return value


def _canonicalize_category(text: str) -> str:
    key = _normalize_category_key(text)
    if key in _CATEGORY_CANONICAL_MAP:
        return _CATEGORY_CANONICAL_MAP[key]
    return str(text or "(Unmapped)")


def _load_material_cost_map(product_map: pd.DataFrame) -> pd.DataFrame:
    resolved = resolve_material_cost_dataframe(product_map=product_map, commission_data=None)
    if resolved is None or resolved.empty:
        return pd.DataFrame(
            columns=["product_code", "material_cost", "material_cost_source", "material_cost_resolved"]
        )
    return resolved[
        ["product_code", "material_cost", "material_cost_source", "material_cost_resolved"]
    ].drop_duplicates(subset=["product_code"], keep="last")


def _fetch_channel_aggregates(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str = "Filtered",
) -> pd.DataFrame:
    if not branch_ids:
        return pd.DataFrame()

    filter_clause, filter_params = build_filter_clause(data_mode)
    is_fp = _is_foodpanda_predicate()
    product_match = _product_match_expression()
    branch_params = [int(b) for b in branch_ids]

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sales_base AS (
        SELECT
            s.shop_id,
            sh.shop_name,
            {product_match} AS product_code,
            COALESCE(NULLIF(LTRIM(RTRIM(p.item_name)), ''), CONCAT('Product ', CAST({product_match} AS VARCHAR(20)))) AS product_name,
            CASE
                WHEN li.Product_Item_ID IN (2642, 3782)
                    OR COALESCE(p.item_name, '') LIKE '%Deal%'
                    OR COALESCE(p.item_name, '') LIKE '%Meal%'
                THEN 'Deals'
                ELSE COALESCE(NULLIF(LTRIM(RTRIM(t.field_name)), ''), '(Unmapped)')
            END AS category,
            CASE WHEN {is_fp} THEN 1 ELSE 0 END AS is_foodpanda,
            CAST(li.qty AS FLOAT) AS qty,
            CAST(li.Unit_price AS FLOAT) AS unit_price,
            s.sale_date,
            s.sale_id
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblSalesLineItems li WITH (NOLOCK)
            ON s.sale_id = li.sale_id AND s.shop_id = li.shop_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_params))})
            {filter_clause}
    ),
    latest_price AS (
        SELECT
            shop_id,
            product_code,
            is_foodpanda,
            unit_price,
            ROW_NUMBER() OVER (
                PARTITION BY shop_id, product_code, is_foodpanda
                ORDER BY sale_date DESC, sale_id DESC
            ) AS rn
        FROM sales_base
    )
    SELECT
        b.shop_id,
        b.shop_name,
        b.product_code,
        b.product_name,
        b.category,
        b.is_foodpanda,
        SUM(b.qty) AS total_units,
        SUM(b.qty * b.unit_price) AS total_sales,
        CASE WHEN SUM(b.qty) = 0 THEN 0 ELSE SUM(b.qty * b.unit_price) / SUM(b.qty) END AS avg_unit_price,
        MAX(CASE WHEN lp.rn = 1 THEN lp.unit_price END) AS latest_unit_price
    FROM sales_base b
    LEFT JOIN latest_price lp
        ON b.shop_id = lp.shop_id
        AND b.product_code = lp.product_code
        AND b.is_foodpanda = lp.is_foodpanda
    GROUP BY
        b.shop_id,
        b.shop_name,
        b.product_code,
        b.product_name,
        b.category,
        b.is_foodpanda
    ORDER BY b.shop_name, b.category, b.product_name
    """

    params = [start_date, end_date] + branch_params + filter_params
    conn = pool.get_connection("candelahns")
    return pd.read_sql(query, conn, params=params)


def _compute_pnl(df: pd.DataFrame, is_foodpanda: bool) -> pd.DataFrame:
    if df is None or df.empty:
        cols = [
            "branch",
            "category",
            "product",
            "avg_unit_price",
            "latest_unit_price",
            "material_cost",
            "sales_price_minus_material_cost",
            "total_sales",
            "margin",
            "margin_percentage",
            "cost_missing",
            "material_cost_source",
            "material_cost_resolved",
        ]
        if is_foodpanda:
            cols.append("foodpanda_commission")
        return pd.DataFrame(columns=cols)

    out = df.copy()
    out["branch"] = out["shop_name"].astype(str)
    out["product"] = out["product_name"].astype(str)
    out["category"] = out["category"].astype(str).apply(_canonicalize_category)
    out["total_units"] = pd.to_numeric(out["total_units"], errors="coerce").fillna(0.0)
    out["total_sales"] = pd.to_numeric(out["total_sales"], errors="coerce").fillna(0.0)
    out["avg_unit_price"] = pd.to_numeric(out["avg_unit_price"], errors="coerce").fillna(0.0)
    out["latest_unit_price"] = pd.to_numeric(out["latest_unit_price"], errors="coerce").fillna(0.0)

    product_map = out[["product_code", "product_name"]].drop_duplicates(subset=["product_code"], keep="last")
    material_map = _load_material_cost_map(product_map)
    out = out.merge(material_map, on="product_code", how="left")
    out["cost_missing"] = out["material_cost"].isna()
    out["material_cost"] = pd.to_numeric(out["material_cost"], errors="coerce").fillna(0.0)

    out["sales_price_minus_material_cost"] = out["avg_unit_price"] - out["material_cost"]
    out["material_cost_total"] = out["material_cost"] * out["total_units"]

    if is_foodpanda:
        out["foodpanda_commission"] = out["total_sales"] * 0.18
        out["margin"] = out["total_sales"] - out["material_cost_total"] - out["foodpanda_commission"]
    else:
        out["margin"] = out["total_sales"] - out["material_cost_total"]

    out["margin_percentage"] = (
        (out["margin"] / out["total_sales"].replace(0, pd.NA)) * 100.0
    ).fillna(0.0)

    selected_cols = [
        "branch",
        "category",
        "product",
        "avg_unit_price",
        "latest_unit_price",
        "material_cost",
        "sales_price_minus_material_cost",
        "total_sales",
        "margin",
        "margin_percentage",
        "cost_missing",
        "material_cost_source",
        "material_cost_resolved",
    ]
    if is_foodpanda:
        selected_cols.append("foodpanda_commission")

    out = out[selected_cols].sort_values(["branch", "category", "product"]).reset_index(drop=True)
    return out


def get_product_pnl_tables(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str = "Filtered",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return two product PNL tables:
    1) Non-Foodpanda table
    2) Foodpanda table (with 18% commission)
    """
    base = _fetch_channel_aggregates(start_date, end_date, branch_ids, data_mode=data_mode)
    if base is None or base.empty:
        return _compute_pnl(pd.DataFrame(), is_foodpanda=False), _compute_pnl(pd.DataFrame(), is_foodpanda=True)

    non_fp = base[base["is_foodpanda"] == 0].copy()
    fp = base[base["is_foodpanda"] == 1].copy()
    return _compute_pnl(non_fp, is_foodpanda=False), _compute_pnl(fp, is_foodpanda=True)
