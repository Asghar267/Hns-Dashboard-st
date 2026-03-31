"""
Quick DB diagnostics for Candela vs Indoge matching.

Goal: explain why Match % is 0 by checking:
- tblSales external_ref_id/external_ref_type coverage
- joinability to tblInitialRawBlinkOrder
- whether OrderJson contains total_price keys (and how often)
"""

from __future__ import annotations

import argparse
from typing import List

import pandas as pd

from modules.database import placeholders, pool


def _parse_branches(raw: str) -> List[int]:
    out: List[int] = []
    for x in (raw or "").split(","):
        x = x.strip()
        if not x:
            continue
        out.append(int(x))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end-exclusive", required=True, help="YYYY-MM-DD")
    ap.add_argument("--branches", default="2", help="comma-separated shop_id (default: 2=Khadda)")
    args = ap.parse_args()

    branches = _parse_branches(args.branches)
    if not branches:
        print("No branches provided.")
        return 2

    conn = pool.get_connection("candelahns")
    start_date = args.start_date
    end_excl = args.end_exclusive

    print("=== QR Match Debug ===")
    print(f"Range: {start_date} -> {end_excl} (exclusive)")
    print(f"Branches: {branches}")

    # Column inventory (quick sanity)
    cols_q = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME IN ('tblSales', 'tblInitialRawBlinkOrder')
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    df_cols = pd.read_sql(cols_q, conn)
    print("\n-- Columns (tblSales + tblInitialRawBlinkOrder) --")
    print(df_cols.to_string(index=False))

    # Sales coverage: external_ref_id/type
    sales_cov_q = f"""
    SELECT
      COUNT(*) AS total_sales,
      SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN 1 ELSE 0 END) AS blinkco_sales,
      SUM(CASE WHEN s.external_ref_type <> 'Blinkco order' OR s.external_ref_type IS NULL THEN 1 ELSE 0 END) AS non_blinkco_sales,
      SUM(CASE WHEN s.external_ref_id IS NULL THEN 1 ELSE 0 END) AS external_ref_id_null,
      SUM(CASE WHEN s.external_ref_id IS NOT NULL THEN 1 ELSE 0 END) AS external_ref_id_not_null
    FROM tblSales s
    WHERE s.sale_date >= ? AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branches))})
    """
    df_cov = pd.read_sql(sales_cov_q, conn, params=[start_date, end_excl] + branches)
    print("\n-- Sales Coverage --")
    print(df_cov.to_string(index=False))

    # External ref type breakdown
    type_q = f"""
    SELECT TOP 50
      COALESCE(s.external_ref_type, '(NULL)') AS external_ref_type,
      COUNT(*) AS cnt
    FROM tblSales s
    WHERE s.sale_date >= ? AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branches))})
    GROUP BY COALESCE(s.external_ref_type, '(NULL)')
    ORDER BY COUNT(*) DESC
    """
    df_types = pd.read_sql(type_q, conn, params=[start_date, end_excl] + branches)
    print("\n-- external_ref_type breakdown (Top 50) --")
    print(df_types.to_string(index=False))

    # Joinability: distinct external_ref_id that exists in raw blink table
    join_q = f"""
    WITH refs AS (
      SELECT DISTINCT LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS ref_id
      FROM tblSales s
      WHERE s.sale_date >= ? AND s.sale_date < ?
        AND s.shop_id IN ({placeholders(len(branches))})
        AND s.external_ref_id IS NOT NULL
    )
    SELECT
      (SELECT COUNT(*) FROM refs) AS distinct_refs,
      (SELECT COUNT(*) FROM refs r INNER JOIN tblInitialRawBlinkOrder b
         ON LTRIM(RTRIM(CONVERT(varchar(64), b.BlinkOrderId))) = r.ref_id
      ) AS distinct_refs_with_raw
    """
    df_join = pd.read_sql(join_q, conn, params=[start_date, end_excl] + branches)
    print("\n-- Joinability to tblInitialRawBlinkOrder --")
    print(df_join.to_string(index=False))

    # Does JSON contain total_price string pattern?
    json_cov_q = """
    SELECT
      COUNT(*) AS raw_rows,
      SUM(CASE WHEN CHARINDEX('\"total_price\"', OrderJson) > 0 THEN 1 ELSE 0 END) AS has_total_price_key,
      SUM(CASE WHEN CHARINDEX('\"totalPrice\"', OrderJson) > 0 THEN 1 ELSE 0 END) AS has_totalPrice_key
    FROM tblInitialRawBlinkOrder
    WHERE CreatedAt >= ? AND CreatedAt < ?
    """
    df_json_cov = pd.read_sql(json_cov_q, conn, params=[start_date, end_excl])
    print("\n-- Raw JSON Key Coverage (in date window) --")
    print(df_json_cov.to_string(index=False))

    # Sample 3 JSONs that include the key
    sample_q = """
    SELECT TOP 3 BlinkOrderId, CreatedAt,
           SUBSTRING(OrderJson, 1, 400) AS OrderJson_prefix
    FROM tblInitialRawBlinkOrder
    WHERE CreatedAt >= ? AND CreatedAt < ?
      AND (CHARINDEX('\"total_price\"', OrderJson) > 0 OR CHARINDEX('\"totalPrice\"', OrderJson) > 0)
    ORDER BY CreatedAt DESC
    """
    df_sample = pd.read_sql(sample_q, conn, params=[start_date, end_excl])
    print("\n-- Sample OrderJson (prefix) --")
    print(df_sample.to_string(index=False))

    print("\nIf `distinct_refs_with_raw` is 0, then Match % will be 0 for 'without Blinkco filter' rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

