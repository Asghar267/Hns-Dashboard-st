"""
Food Panda Tab
Lists Food Panda transactions and summaries.
"""

from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from modules.connection_cloud import DatabaseConfig
from modules.database import pool, placeholders, build_filter_clause
from modules.utils import format_currency, export_to_excel
from modules.foodpanda_reconciliation import (
    load_foodpanda_order_summary,
    fetch_foodpanda_sales_by_codes,
    reconcile_foodpanda_orders,
)

HIDE_EXTERNAL_REF_COLS = {"external_ref_type", "external_ref_id"}


def _drop_hidden_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.drop(columns=[c for c in HIDE_EXTERNAL_REF_COLS if c in df.columns], errors="ignore")


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_food_panda_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
) -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    filter_clause, filter_params = build_filter_clause(data_mode)

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        s.sale_id,
        s.sale_date,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.Cust_name AS order_type,
        s.Nt_amount AS net_amount,
        s.adjustment_comments,
        s.Additional_Comments,
        s.external_ref_type,
        s.external_ref_id
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.Cust_name = 'Food Panda'
      {filter_clause}
    ORDER BY s.sale_date DESC, s.sale_id DESC
    """
    params: List = [start_date, end_date] + list(branch_ids) + list(filter_params)
    df = pd.read_sql(query, conn, params=params)
    if not df.empty:
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0.0)
        # "Order ID" for users = POS sale_id (stable identifier in tblSales).
        df["order_id"] = pd.to_numeric(df["sale_id"], errors="coerce").fillna(0).astype(int)
        # Foodpanda order code lives in adjustment_comments in this POS DB.
        # Fall back to Additional_Comments then external_ref_id.
        adj = df.get("adjustment_comments", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})
        add = df.get("Additional_Comments", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})
        ext = df.get("external_ref_id", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})
        df["order_code"] = adj.mask(adj.eq(""), add).mask(adj.eq("") & add.eq(""), ext)
        df["employee_id"] = pd.to_numeric(df["employee_id"], errors="coerce").fillna(0).astype(int)
        df["employee_code"] = df.get("employee_code", "").fillna("").astype(str)
        df["employee_name"] = df.get("employee_name", "").fillna("").astype(str)
        df["shop_name"] = df.get("shop_name", "").fillna("").astype(str)
    return df


class FoodPandaTab:
    def __init__(
        self,
        start_date: str,
        end_date: str,
        selected_branches: List[int],
        data_mode: str,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

    def render(self) -> None:
        st.header("Food Panda")
        st.caption("Food Panda transactions based on `tblSales.Cust_name = 'Food Panda'`.")

        df = _cached_food_panda_sales(self.start_date, self.end_date, self.selected_branches, self.data_mode)

        total_sales = float(df["net_amount"].sum()) if not df.empty else 0.0
        total_tx = int(len(df)) if not df.empty else 0
        aov = (total_sales / total_tx) if total_tx else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Sales", format_currency(total_sales))
        m2.metric("Transactions", f"{total_tx:,}")
        m3.metric("Avg Order Value", format_currency(aov))

        st.markdown("---")
        if df.empty:
            st.info("No Food Panda transactions found for the selected filters.")
            return

        # Summaries
        left, right = st.columns(2)
        with left:
            st.subheader("By Branch")
            by_branch = (
                df.groupby(["shop_id", "shop_name"], as_index=False)
                .agg(transactions=("sale_id", "count"), sales=("net_amount", "sum"))
                .sort_values("sales", ascending=False)
            )
            by_branch["sales"] = by_branch["sales"].apply(format_currency)
            st.dataframe(by_branch, width="stretch", hide_index=True, height=280)

        with right:
            st.subheader("Top Employees")
            by_emp = (
                df.groupby(["employee_id", "employee_code", "employee_name"], as_index=False)
                .agg(transactions=("sale_id", "count"), sales=("net_amount", "sum"))
                .sort_values("sales", ascending=False)
            )
            by_emp["sales"] = by_emp["sales"].apply(format_currency)
            st.dataframe(by_emp.head(50), width="stretch", hide_index=True, height=280)

        st.markdown("---")
        st.subheader("All Food Panda Transactions")

        search = st.text_input("Search (employee / branch / comments / ref)", value="", key="food_panda_search")
        show_all_cols = st.checkbox("Show all columns", value=False, key="food_panda_show_all_cols")

        out = _drop_hidden_cols(df.copy())
        if search.strip():
            needle = search.strip()
            mask = (
                out["employee_name"].astype(str).str.contains(needle, case=False, na=False)
                | out["shop_name"].astype(str).str.contains(needle, case=False, na=False)
                | out.get("Additional_Comments", "").astype(str).str.contains(needle, case=False, na=False)
                | out.get("order_code", "").astype(str).str.contains(needle, case=False, na=False)
            )
            out = out[mask].copy()

        default_cols = [
            "order_id",
            "order_code",
            "sale_date",
            "shop_name",
            "employee_name",
            "net_amount",
            "adjustment_comments",
            "Additional_Comments",
            "sale_id",
        ]
        if show_all_cols:
            cols = [c for c in out.columns if c not in HIDE_EXTERNAL_REF_COLS]
        else:
            cols = [c for c in default_cols if c in out.columns]

        out_show = out[cols].copy()
        if "sale_date" in out_show.columns:
            out_show["sale_date"] = pd.to_datetime(out_show["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
        if "net_amount" in out_show.columns:
            out_show["net_amount"] = pd.to_numeric(out_show["net_amount"], errors="coerce").fillna(0.0)

        st.dataframe(out_show, width="stretch", hide_index=True, height=520)

        df_export = _drop_hidden_cols(df.copy())
        st.download_button(
            label="Download Food Panda Excel",
            data=export_to_excel(df_export, "Food Panda"),
            file_name=f"food_panda_{self.start_date}_to_{self.end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.markdown("---")
        st.subheader("Reconcile Order Summary.xlsx (Appendix A)")
        st.caption("Matches Foodpanda `Order Code` to POS Food Panda sales and verifies `Order Amount` vs `NT_amount` (±1 PKR).")

        uploaded = st.file_uploader(
            "Upload Foodpanda Order Summary file",
            type=["xlsx", "xls"],
            key="foodpanda_order_summary_upload",
        )
        if uploaded is None:
            st.info("Upload `005 - Order Summary.xlsx` to run reconciliation.")
            return

        try:
            xls = pd.ExcelFile(uploaded)
            sheet = st.selectbox(
                "Sheet",
                options=xls.sheet_names,
                index=xls.sheet_names.index("Appendix A") if "Appendix A" in xls.sheet_names else 0,
                key="foodpanda_recon_sheet",
            )
            df_excel = load_foodpanda_order_summary(uploaded, sheet_name=sheet)
        except Exception as e:
            st.error(f"Failed to read Excel: {e}")
            return

        tol = 1.0
        st.caption(f"Tolerance: ±{tol:.0f} PKR")

        codes = df_excel["excel_order_code_norm"].dropna().astype(str).tolist()
        try:
            df_db = fetch_foodpanda_sales_by_codes(
                codes=codes,
                start_date=self.start_date,
                end_date=self.end_date,
                branch_ids=self.selected_branches,
                data_mode=self.data_mode,
                chunk_size=800,
            )
        except Exception as e:
            st.error(f"DB fetch failed: {e}")
            return

        result = reconcile_foodpanda_orders(df_excel=df_excel, df_db=df_db, tolerance_pkr=tol)

        # Hide noisy integration columns from reconciliation views/exports.
        full = _drop_hidden_cols(result.full.copy())
        mismatches = _drop_hidden_cols(result.mismatches.copy())
        unmatched = _drop_hidden_cols(result.unmatched.copy())
        duplicates = _drop_hidden_cols(result.duplicates.copy())
        excel_duplicates = _drop_hidden_cols(result.excel_duplicates.copy())

        # Summary metrics
        metrics = {r["metric"]: r["value"] for r in result.summary.to_dict("records")}
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Rows", f"{int(metrics.get('total_rows', 0)):,}")
        c2.metric("Matched OK", f"{int(metrics.get('matched_ok', 0)):,}")
        c3.metric("Duplicates Resolved", f"{int(metrics.get('duplicate_resolved', 0)):,}")
        c4.metric("Price Mismatch", f"{int(metrics.get('matched_price_mismatch', 0)):,}")
        c5.metric("Unmatched", f"{int(metrics.get('unmatched', 0)):,}")

        st.markdown("---")
        st.subheader("Matched Only")
        matched_only = full[full["match_status"].isin(["matched_ok", "duplicate_resolved"])].copy()
        st.dataframe(matched_only, width="stretch", hide_index=True, height=320)

        st.subheader("Mismatches")
        st.dataframe(mismatches, width="stretch", hide_index=True, height=260)

        st.subheader("Unmatched")
        st.dataframe(unmatched, width="stretch", hide_index=True, height=260)

        st.subheader("Excel Duplicates (Audit)")
        st.dataframe(excel_duplicates, width="stretch", hide_index=True, height=260)

        st.subheader("Duplicates (Audit)")
        st.dataframe(duplicates, width="stretch", hide_index=True, height=260)

        st.subheader("Full Reconciliation")
        st.dataframe(full, width="stretch", hide_index=True, height=420)

        from modules.utils import export_tables_to_excel
        tables = {
            "recon_full": full,
            "matched_only": matched_only,
            "mismatches": mismatches,
            "unmatched": unmatched,
            "excel_duplicates": excel_duplicates,
            "duplicates": duplicates,
            "summary": result.summary,
        }
        st.download_button(
            label="Download Reconciliation Excel",
            data=export_tables_to_excel(tables),
            file_name=f"foodpanda_recon_{self.start_date}_to_{self.end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="foodpanda_recon_download",
        )
