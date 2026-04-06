"""
Foodpanda reconciliation helpers.

Matches Foodpanda Appendix A order codes to POS sales in tblSales (Food Panda)
and verifies prices (Order Amount vs NT_amount) with a tolerance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import pandas as pd

from modules.database import build_filter_clause, placeholders, pool


REQUIRED_APPENDIX_A_COLS = [
    "Order Code",
    "Order Date",
    "Order Amount",
    "Outlet Name",
    "Vendor Code",
]


def _norm_code(v: object) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in {"none", "nan"}:
        return ""
    return s.strip().lower()


def load_foodpanda_order_summary(file_obj, sheet_name: str = "Appendix A") -> pd.DataFrame:
    """
    Load Foodpanda 'Order Summary' Excel sheet and return normalized dataframe.

    Accepts a Streamlit UploadedFile, a file-like, or a path.
    """
    df = pd.read_excel(file_obj, sheet_name=sheet_name)

    missing = [c for c in REQUIRED_APPENDIX_A_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in '{sheet_name}': {missing}")

    out = df.copy()
    out["excel_order_code"] = out["Order Code"].astype(str).str.strip()
    out["excel_order_code_norm"] = out["excel_order_code"].map(_norm_code)
    out["excel_order_date"] = pd.to_datetime(out["Order Date"], errors="coerce")
    out["excel_order_amount"] = pd.to_numeric(out["Order Amount"], errors="coerce")
    return out


def _fetch_sales_for_codes(
    code_col: str,
    codes: List[str],
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    chunk_size: int,
) -> pd.DataFrame:
    if not codes:
        return pd.DataFrame()

    conn = pool.get_connection("candelahns")
    filter_clause, filter_params = build_filter_clause(data_mode)
    out_frames: list[pd.DataFrame] = []

    for i in range(0, len(codes), chunk_size):
        chunk = codes[i : i + chunk_size]
        q = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            s.sale_id,
            s.sale_date,
            s.shop_id,
            sh.shop_name,
            s.Cust_name,
            s.NT_amount,
            s.adjustment_comments,
            s.Additional_Comments,
            s.external_ref_type,
            s.external_ref_id,
            s.pos_code
        FROM tblSales s WITH (NOLOCK)
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON sh.shop_id = s.shop_id
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.Cust_name = 'Food Panda'
          AND CONVERT(nvarchar(4000), s.[{code_col}]) IN ({placeholders(len(chunk))})
          {filter_clause}
        """
        params = [start_date, end_date] + list(branch_ids) + list(chunk) + list(filter_params)
        df = pd.read_sql(q, conn, params=params)
        out_frames.append(df)

    out = pd.concat(out_frames, ignore_index=True) if out_frames else pd.DataFrame()
    if out.empty:
        return out

    out["sale_date"] = pd.to_datetime(out["sale_date"], errors="coerce")
    out["NT_amount"] = pd.to_numeric(out["NT_amount"], errors="coerce").fillna(0.0)
    out["sale_id"] = pd.to_numeric(out["sale_id"], errors="coerce").fillna(0).astype(int)
    out["shop_id"] = pd.to_numeric(out["shop_id"], errors="coerce").fillna(0).astype(int)
    out["adjustment_comments"] = out.get("adjustment_comments", "").fillna("").astype(str)
    out["Additional_Comments"] = out.get("Additional_Comments", "").fillna("").astype(str)
    out["external_ref_id"] = out.get("external_ref_id", "").fillna("").astype(str)

    out["db_order_code_raw"] = (
        out["adjustment_comments"].astype(str).str.strip().replace({"None": "", "nan": ""})
    )
    mask_empty = out["db_order_code_raw"].eq("")
    if mask_empty.any():
        out.loc[mask_empty, "db_order_code_raw"] = (
            out.loc[mask_empty, "Additional_Comments"].astype(str).str.strip().replace({"None": "", "nan": ""})
        )
    mask_empty = out["db_order_code_raw"].eq("")
    if mask_empty.any():
        out.loc[mask_empty, "db_order_code_raw"] = (
            out.loc[mask_empty, "external_ref_id"].astype(str).str.strip().replace({"None": "", "nan": ""})
        )
    out["db_order_code_norm"] = out["db_order_code_raw"].map(_norm_code)

    return out


def fetch_foodpanda_sales_by_codes(
    codes: Iterable[str],
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    chunk_size: int = 800,
) -> pd.DataFrame:
    """
    Fetch Food Panda sales for given Foodpanda order codes.

    Implementation uses a multi-pass strategy to avoid SQL Server parameter limits:
    1) adjustment_comments IN codes
    2) Additional_Comments IN remaining
    3) external_ref_id IN remaining (string)
    """
    codes_norm = [_norm_code(c) for c in codes]
    codes_norm = [c for c in codes_norm if c]
    if not codes_norm:
        return pd.DataFrame()

    # 1) adjustment_comments
    df1 = _fetch_sales_for_codes(
        code_col="adjustment_comments",
        codes=codes_norm,
        start_date=start_date,
        end_date=end_date,
        branch_ids=branch_ids,
        data_mode=data_mode,
        chunk_size=chunk_size,
    )
    found = set(df1["db_order_code_norm"].dropna().astype(str).tolist()) if not df1.empty else set()
    remaining = [c for c in codes_norm if c not in found]

    # 2) Additional_Comments
    df2 = _fetch_sales_for_codes(
        code_col="Additional_Comments",
        codes=remaining,
        start_date=start_date,
        end_date=end_date,
        branch_ids=branch_ids,
        data_mode=data_mode,
        chunk_size=chunk_size,
    )
    found2 = set(df2["db_order_code_norm"].dropna().astype(str).tolist()) if not df2.empty else set()
    remaining2 = [c for c in remaining if c not in found2]

    # 3) external_ref_id
    df3 = _fetch_sales_for_codes(
        code_col="external_ref_id",
        codes=remaining2,
        start_date=start_date,
        end_date=end_date,
        branch_ids=branch_ids,
        data_mode=data_mode,
        chunk_size=chunk_size,
    )

    frames = [d for d in (df1, df2, df3) if isinstance(d, pd.DataFrame) and not d.empty]
    if not frames:
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    # Deduplicate identical sale_id rows if a code matched multiple passes.
    out = out.drop_duplicates(subset=["sale_id"], keep="last").reset_index(drop=True)
    return out


@dataclass(frozen=True)
class ReconcileResult:
    full: pd.DataFrame
    mismatches: pd.DataFrame
    unmatched: pd.DataFrame
    duplicates: pd.DataFrame
    excel_duplicates: pd.DataFrame
    summary: pd.DataFrame


def reconcile_foodpanda_orders(
    df_excel: pd.DataFrame,
    df_db: pd.DataFrame,
    tolerance_pkr: float = 1.0,
) -> ReconcileResult:
    """Reconcile Excel Appendix A rows to DB sales and compute price verification."""
    if df_excel is None or df_excel.empty:
        empty = pd.DataFrame()
        summary = pd.DataFrame([{"metric": "total_rows", "value": 0}])
        return ReconcileResult(empty, empty, empty, empty, empty, summary)

    excel = df_excel.copy()
    excel_key = "excel_order_code_norm"
    if excel_key not in excel.columns:
        excel[excel_key] = excel.get("Order Code", "").map(_norm_code)

    db = df_db.copy() if df_db is not None else pd.DataFrame()
    if not db.empty and "db_order_code_norm" not in db.columns:
        raw = (
            db.get("adjustment_comments", "")
            .fillna("")
            .astype(str)
            .str.strip()
            .replace({"None": "", "nan": ""})
        )
        raw = raw.mask(raw.eq(""), db.get("Additional_Comments", "").fillna("").astype(str).str.strip())
        raw = raw.mask(raw.eq(""), db.get("external_ref_id", "").fillna("").astype(str).str.strip())
        db["db_order_code_raw"] = raw
        db["db_order_code_norm"] = db["db_order_code_raw"].map(_norm_code)

    if db.empty:
        out = excel.copy()
        out["match_status"] = "unmatched"
        excel_dup_counts = excel.groupby(excel_key, dropna=False).size()
        excel_dup_keys = set(excel_dup_counts[excel_dup_counts > 1].index.astype(str).tolist())
        excel_dups = excel[excel[excel_key].astype(str).isin(excel_dup_keys)].copy()
        if not excel_dups.empty:
            excel_dups["excel_dup_count"] = excel_dups[excel_key].map(
                excel_dup_counts.astype(int).to_dict()
            )
        summary = pd.DataFrame(
            [
                {"metric": "total_rows", "value": len(out)},
                {"metric": "matched", "value": 0},
                {"metric": "unmatched", "value": len(out)},
                {"metric": "price_mismatched", "value": 0},
                {"metric": "duplicates_in_db", "value": 0},
            ]
        )
        return ReconcileResult(out, pd.DataFrame(), out, pd.DataFrame(), excel_dups, summary)

    # Merge to get candidates (may produce duplicates).
    cand = excel.merge(
        db,
        left_on=excel_key,
        right_on="db_order_code_norm",
        how="left",
        suffixes=("", "_db"),
    )

    # Mark db-duplicates (by order code).
    dup_counts = db.groupby("db_order_code_norm")["sale_id"].nunique()
    dup_keys = set(dup_counts[dup_counts > 1].index.astype(str).tolist())
    cand["db_duplicate_key"] = cand[excel_key].astype(str).isin(dup_keys)

    # Excel-side duplicates (by order code).
    excel_dup_counts = excel.groupby(excel_key, dropna=False).size()
    excel_dup_keys = set(excel_dup_counts[excel_dup_counts > 1].index.astype(str).tolist())
    excel_dups = excel[excel[excel_key].astype(str).isin(excel_dup_keys)].copy()
    if not excel_dups.empty:
        excel_dups["excel_dup_count"] = excel_dups[excel_key].map(
            excel_dup_counts.astype(int).to_dict()
        )

    # Candidate scoring to pick best match per excel order code.
    cand["db_sale_date"] = pd.to_datetime(cand.get("sale_date"), errors="coerce")
    cand["db_NT_amount"] = pd.to_numeric(cand.get("NT_amount"), errors="coerce")
    cand["excel_order_date"] = pd.to_datetime(cand.get("excel_order_date", cand.get("Order Date")), errors="coerce")
    cand["excel_order_amount"] = pd.to_numeric(cand.get("excel_order_amount", cand.get("Order Amount")), errors="coerce")

    # abs day diff (NaT-safe)
    day_diff = (cand["db_sale_date"] - cand["excel_order_date"]).dt.total_seconds().abs() / 86400.0
    cand["abs_day_diff"] = day_diff.fillna(10**9)

    # Sort: closest date, then highest amount, then latest sale_id.
    cand["sale_id_sort"] = pd.to_numeric(cand.get("sale_id"), errors="coerce").fillna(0).astype(int)
    cand = cand.sort_values(
        ["excel_order_code_norm", "abs_day_diff", "db_NT_amount", "sale_id_sort"],
        ascending=[True, True, False, False],
    )

    # Keep best row per Excel code.
    best = cand.groupby("excel_order_code_norm", as_index=False).head(1).reset_index(drop=True)

    # Build duplicates audit table (all candidates for dup keys + chosen flag).
    dup_audit = cand[cand["db_duplicate_key"]].copy()
    if not dup_audit.empty:
        chosen = set(best.loc[best["db_duplicate_key"], ["excel_order_code_norm", "sale_id_sort"]].apply(tuple, axis=1))
        dup_audit["chosen"] = dup_audit[["excel_order_code_norm", "sale_id_sort"]].apply(tuple, axis=1).isin(chosen)
    else:
        dup_audit = pd.DataFrame()

    # Price verification
    best["amount_diff"] = best["db_NT_amount"] - best["excel_order_amount"]
    best["abs_diff"] = best["amount_diff"].abs()
    best["price_match_ok"] = best["abs_diff"].le(float(tolerance_pkr)).fillna(False)

    has_match = best["sale_id_sort"].gt(0) & best["db_sale_date"].notna()
    best["match_status"] = "unmatched"
    best.loc[has_match & (~best["price_match_ok"]), "match_status"] = "matched_price_mismatch"
    best.loc[has_match & (best["price_match_ok"]), "match_status"] = "matched_ok"
    best.loc[has_match & (best["price_match_ok"]) & (best["db_duplicate_key"]), "match_status"] = "duplicate_resolved"

    mismatches = best[best["match_status"] == "matched_price_mismatch"].copy()
    unmatched = best[best["match_status"] == "unmatched"].copy()

    summary = pd.DataFrame(
        [
            {"metric": "total_rows", "value": int(len(best))},
            {"metric": "matched_ok", "value": int((best["match_status"] == "matched_ok").sum())},
            {"metric": "duplicate_resolved", "value": int((best["match_status"] == "duplicate_resolved").sum())},
            {"metric": "matched_price_mismatch", "value": int((best["match_status"] == "matched_price_mismatch").sum())},
            {"metric": "unmatched", "value": int((best["match_status"] == "unmatched").sum())},
            {"metric": "duplicates_in_db", "value": int(len(dup_keys))},
        ]
    )

    return ReconcileResult(best, mismatches, unmatched, dup_audit, excel_dups, summary)
