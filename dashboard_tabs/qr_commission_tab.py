"""
QR Commission Tab Module
Handles QR/Blinkco commission analysis
"""

import pandas as pd
from typing import Dict, List, Optional
import streamlit as st
import numpy as np

# Import from existing modules
from modules.connection_cloud import DatabaseConfig
from modules.database import (
    get_qr_daily_summary,
    get_qr_employee_daily_summary,
    pool,
    placeholders
)
from modules.blink_reporting import (
    prepare_blink_orders,
    apply_split_filters,
    add_transaction_quality_flags,
)
from modules.utils import (
    format_currency,
    perf_trace,
)
from modules.config import BLOCKED_NAMES, BLOCKED_COMMENTS


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_qr_commission_data(start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    qr_query = f"""
    SELECT
        s.sale_id,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.Nt_amount AS total_sale,
        s.external_ref_id,
        s.sale_date
    FROM tblSales s
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.external_ref_type = 'Blinkco order'
    """
    qr_params: List = [start_str, end_exclusive_str] + branch_ids
    if mode == "Filtered":
        if BLOCKED_NAMES:
            qr_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            qr_params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            qr_query += (
                f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                f" OR s.Additional_Comments IS NULL)"
            )
            qr_params.extend(BLOCKED_COMMENTS)
    return pd.read_sql(qr_query, conn, params=qr_params)


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_sales_summary_combined(start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    query = f"""
    SELECT
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COUNT(DISTINCT s.sale_id) AS total_transactions_all,
        SUM(s.Nt_amount) AS total_sales_all,
        SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN 1 ELSE 0 END) AS total_transactions_blinkco,
        SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN s.Nt_amount ELSE 0 END) AS total_sales_blinkco
    FROM tblSales s
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
    """
    params: List = [start_str, end_exclusive_str] + branch_ids
    if mode == "Filtered":
        if BLOCKED_NAMES:
            query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            query += (
                f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                f" OR s.Additional_Comments IS NULL)"
            )
            params.extend(BLOCKED_COMMENTS)
    query += """
    GROUP BY
        s.shop_id, sh.shop_name,
        COALESCE(e.shop_employee_id, 0),
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
        COALESCE(e.field_name, 'Online/Unassigned')
    ORDER BY total_sales_all DESC
    """
    return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_blink_raw_orders(start_str: str, end_exclusive_str: str) -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    blink_raw_query = """
SELECT
    BlinkOrderId,
    OrderJson,
    CreatedAt
FROM tblInitialRawBlinkOrder
    WHERE CreatedAt >= ? AND CreatedAt < ?
    """
    return pd.read_sql(blink_raw_query, conn, params=[start_str, end_exclusive_str])


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_qr_product_sales_data(start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    product_query = f"""
    SELECT
        s.shop_id,
        sh.shop_name,
        p.Product_code,
        p.item_name AS product_name,
        SUM(li.qty) AS total_qty,
        SUM(li.qty * li.Unit_price) AS product_sales
    FROM tblSales s
    INNER JOIN tblSalesLineItems li ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p ON pi.Product_ID = p.Product_ID
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.external_ref_type = 'Blinkco order'
    """
    params: List = [start_str, end_exclusive_str] + branch_ids
    if mode == "Filtered":
        if BLOCKED_NAMES:
            product_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            product_query += (
                f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                f" OR s.Additional_Comments IS NULL)"
            )
            params.extend(BLOCKED_COMMENTS)
    product_query += """
    GROUP BY s.shop_id, sh.shop_name, p.Product_code, p.item_name
    ORDER BY product_sales DESC
    """
    return pd.read_sql(product_query, conn, params=params)


class QRCommissionTab:
    """QR Commission tab functionality"""
    
    def __init__(
        self,
        start_date: str,
        end_date: str,
        selected_branches: List[int],
        data_mode: str,
        allowed_tables: Optional[object] = None,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.allowed_tables = allowed_tables

    def render_qr_commission(self, commission_rate: float = 2.0):
        """Render the QR Commission dashboard"""
        end_exclusive_qr = (pd.to_datetime(self.end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        cache_bucket = st.session_state.setdefault("qr_tab_cache", {})
        cache_sig = (self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode)

        def _session_cached(name: str, loader):
            key = f"{name}:{cache_sig}"
            if key in cache_bucket:
                return cache_bucket[key]
            value = loader()
            cache_bucket[key] = value
            return value

        def _allow(section: str) -> bool:
            if self.allowed_tables in (None, "all"):
                return True
            if isinstance(self.allowed_tables, dict):
                allowed = self.allowed_tables.get("QR Commission", "all")
                if allowed == "all":
                    return True
                return section in allowed
            if isinstance(self.allowed_tables, list):
                return section in self.allowed_tables
            return True

        # Fetch data
        with perf_trace("QR fetch (queries)", "db"):
            df_qr = self._fetch_qr_commission_data(self.start_date, end_exclusive_qr, self.selected_branches, self.data_mode)
            # Reduce redundant queries: use combined summary for all+blinkco in one call.
            df_total_sales = self._fetch_sales_summary_combined(
                self.start_date,
                end_exclusive_qr,
                self.selected_branches,
                self.data_mode,
            )
            df_blink_raw = self._fetch_blink_raw_orders(self.start_date, end_exclusive_qr)
            df_qr_products = self._fetch_qr_product_sales_data(self.start_date, end_exclusive_qr, self.selected_branches, self.data_mode)

        raw_blink_rows = len(df_blink_raw)
        with perf_trace("QR process (blink prep)", "processing"):
            df_blink = _session_cached("blink_prepared", lambda: prepare_blink_orders(df_blink_raw))
        deduped_blink_rows = len(df_blink)

        with perf_trace("QR process (merge+flags)", "processing"):
            if not df_qr.empty:
                df_qr["employee_id"] = pd.to_numeric(df_qr.get("employee_id"), errors="coerce").fillna(0).astype(int)
                df_qr["employee_code"] = df_qr.get("employee_code", "").fillna("").astype(str)
                df_qr['total_sale'] = pd.to_numeric(df_qr['total_sale'], errors='coerce').fillna(0.0)
                df_merged = df_qr.merge(
                    df_blink,
                    left_on='external_ref_id',
                    right_on='BlinkOrderId',
                    how='left'
                )
                df_merged['Indoge_total_price'] = pd.to_numeric(df_merged['Indoge_total_price'], errors='coerce').fillna(0.0)
                df_merged['BlinkOrderId'] = df_merged['BlinkOrderId'].fillna('-')
                df_merged['json_parse_ok'] = df_merged['json_parse_ok'].fillna(False)
                df_merged['difference'] = df_merged['Indoge_total_price'] - df_merged['total_sale']
                df_merged['Candelahns_commission'] = df_merged['total_sale'] * (commission_rate / 100)
                df_merged['Indoge_commission'] = df_merged['Indoge_total_price'] * (commission_rate / 100)
                df_merged = add_transaction_quality_flags(df_merged)

                # Legacy top metrics (as before)
                total_sale = df_merged['total_sale'].sum()
                total_cand_comm = df_merged['Candelahns_commission'].sum()
                total_indoge_comm = df_merged['Indoge_commission'].sum()
                total_tx = len(df_merged)

                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total QR Sales", format_currency(total_sale))
                    col2.metric("Candelahns Commission", format_currency(total_cand_comm))
                    col3.metric("Indoge Commission", format_currency(total_indoge_comm))
                    col4.metric("Transactions", f"{total_tx:,}")
            else:
                df_merged = pd.DataFrame()

        if not df_total_sales.empty:
            df_total_sales["employee_id"] = pd.to_numeric(df_total_sales.get("employee_id"), errors="coerce").fillna(0).astype(int)
            df_total_sales["employee_code"] = df_total_sales.get("employee_code", "").fillna("").astype(str)

        st.markdown("### Split Report Controls")
        c1, c2, c3 = st.columns(3)
        with c1:
            employee_search = st.text_input("Search Employee", key="qr_split_employee_search")
        with c2:
            branch_options = sorted(df_total_sales['shop_name'].dropna().astype(str).unique().tolist()) if not df_total_sales.empty else []
            selected_branch_names = st.multiselect(
                "Branches in report",
                options=branch_options,
                default=branch_options,
                key="qr_split_branch_filter"
            )
        with c3:
            include_zero_rows = st.checkbox("Include zero rows", value=True, key="qr_split_include_zero")
            include_unassigned = st.checkbox("Include Online/Unassigned", value=True, key="qr_split_include_unassigned")

            sort_choice = st.selectbox(
                "Ranking",
                [
                    "Total Sales (desc)",
                    "Blinkco Sales (desc)",
                    "Blinkco Share % (desc)",
                    "Diff (Total-Blinkco) (desc)",
                    "Commission Total (desc)",
                ],
                index=0,
                key="qr_split_sort_choice"
            )

        if not df_merged.empty:
            blinkco_summary = (
                df_merged.groupby(['employee_id', 'employee_name', 'shop_id', 'shop_name'], as_index=False)
                .agg(
                    total_sales_blinkco=('total_sale', 'sum'),
                    total_transactions_blinkco=('sale_id', 'count')
                )
            )
        else:
            blinkco_summary = pd.DataFrame(
                columns=[
                    'employee_id', 'employee_name', 'shop_id', 'shop_name',
                    'total_sales_blinkco', 'total_transactions_blinkco'
                ]
            )

        split_report = self._build_split_report(df_total_sales, blinkco_summary, commission_rate)
        split_report_filtered = apply_split_filters(
            split_report,
            employee_search=employee_search,
            branches=selected_branch_names,
            include_zero_rows=include_zero_rows,
            include_unassigned=include_unassigned,
        )

        if not split_report.empty:
            # Reconciliation + sanity checks
            recon_all = abs(split_report['total_sales_all'].sum() - pd.to_numeric(df_total_sales['total_sales_all'], errors='coerce').fillna(0).sum())
            recon_blink = abs(split_report['total_sales_blinkco'].sum() - blinkco_summary['total_sales_blinkco'].sum()) if not blinkco_summary.empty else 0.0
            invalid_share_rows = int(((split_report['blinkco_share_pct'] < 0) | (split_report['blinkco_share_pct'] > 100)).sum())
            bad_comm_rows = int((
                (split_report['commission_total_sales'] - split_report['total_sales_all'] * (commission_rate / 100)).abs() > 0.01
            ).sum())

            if recon_all > 1 or recon_blink > 1 or invalid_share_rows > 0 or bad_comm_rows > 0:
                st.warning(
                    f"Quality warning | recon_all_diff={recon_all:,.2f}, recon_blink_diff={recon_blink:,.2f}, "
                    f"invalid_share_rows={invalid_share_rows}, bad_comm_rows={bad_comm_rows}"
                )

            # KPI cards (filtered)
            k_all = split_report_filtered['total_sales_all'].sum() if not split_report_filtered.empty else 0.0
            k_blink = split_report_filtered['total_sales_blinkco'].sum() if not split_report_filtered.empty else 0.0
            k_wo = split_report_filtered['total_sales_without_blinkco'].sum() if not split_report_filtered.empty else 0.0
            k_comm = split_report_filtered['commission_total_sales'].sum() if not split_report_filtered.empty else 0.0
            k_share = (k_blink / k_all * 100) if k_all else 0.0

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Sales", format_currency(k_all))
            m2.metric("Blinkco Sales", format_currency(k_blink))
            m3.metric("Sales w/o Blinkco", format_currency(k_wo))
            m4.metric("Commission on Total", format_currency(k_comm))
            m5.metric("Blinkco Share", f"{k_share:.2f}%")

            st.markdown("---")
            if _allow("Split Report"):
                st.subheader("Employee + Branch Sales Split Report")

            sort_map = {
                "Total Sales (desc)": "total_sales_all",
                "Blinkco Sales (desc)": "total_sales_blinkco",
                "Blinkco Share % (desc)": "blinkco_share_pct",
                "Diff (Total-Blinkco) (desc)": "diff_total_minus_blinkco",
                "Commission Total (desc)": "commission_total_sales",
            }
            sort_col = sort_map.get(sort_choice, "total_sales_all")
            split_sorted = split_report_filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)
            split_sorted.index = range(1, len(split_sorted) + 1)
            split_sorted.index.name = "#"

            show = split_sorted.copy()
            show["employee_id"] = pd.to_numeric(show.get("employee_id"), errors="coerce").fillna(0).astype(int)
            show["employee_code"] = show.get("employee_code", "").fillna("").astype(str)
            show['blinkco_share_pct'] = show['blinkco_share_pct'].apply(lambda x: f"{x:.2f}%")
            show['without_blinkco_share_pct'] = show['without_blinkco_share_pct'].apply(lambda x: f"{x:.2f}%")
            for col in [
                'total_sales_all', 'total_sales_blinkco', 'total_sales_without_blinkco',
                'diff_total_minus_blinkco', 'commission_total_sales', 'commission_blinkco_sales',
                'commission_without_blinkco_sales'
            ]:
                show[col] = show[col].apply(format_currency)

            if _allow("Split Report"):
                self._render_table(
                    show[[
                        'employee_id', 'employee_code', 'employee_name', 'shop_name', 'total_transactions_all', 'total_transactions_blinkco',
                        'total_transactions_without_blinkco', 'total_sales_all', 'total_sales_blinkco',
                        'total_sales_without_blinkco', 'blinkco_share_pct', 'without_blinkco_share_pct',
                        'diff_total_minus_blinkco', 'commission_total_sales', 'commission_blinkco_sales',
                        'commission_without_blinkco_sales', 'has_blink_order', 'blink_mismatch_flag'
                    ]],
                    width="stretch",
                    hide_index=False,
                    height=520,
                )

            split_summary = pd.DataFrame([{
                'employees_rows': len(split_report_filtered),
                'total_sales_all': k_all,
                'total_sales_blinkco': k_blink,
                'total_sales_without_blinkco': k_wo,
                'blinkco_share_pct': round(k_share, 2),
                'commission_total_sales': k_comm,
                'commission_blinkco_sales': split_report_filtered['commission_blinkco_sales'].sum() if not split_report_filtered.empty else 0.0,
                'commission_without_blinkco_sales': split_report_filtered['commission_without_blinkco_sales'].sum() if not split_report_filtered.empty else 0.0,
            }])

            if _allow("Split Report"):
                st.download_button(
                    label="Download Split Report Full Excel",
                    data=self._export_to_excel(split_report.sort_values('total_sales_all', ascending=False), "Split Report Full"),
                    file_name="qr_employee_branch_sales_split_full.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.download_button(
                    label="Download Split Report Filtered Excel",
                    data=self._export_to_excel(
                        split_report_filtered.sort_values(sort_col, ascending=False),
                        "Split Report Filtered",
                    ),
                    file_name="qr_employee_branch_sales_split_filtered.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.download_button(
                    label="Download Split Summary Excel",
                    data=self._export_to_excel(split_summary, "Split Summary"),
                    file_name="qr_employee_branch_sales_split_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        else:
            st.info("No total sales data available for split report.")

        if not df_merged.empty:
            st.markdown("---")
            if _allow("Detailed Transactions"):
                st.subheader("Detailed Transactions")

            tx_show = df_merged.copy()
            if selected_branch_names:
                tx_show = tx_show[tx_show['shop_name'].isin(selected_branch_names)]
            if employee_search.strip():
                tx_show = tx_show[tx_show['employee_name'].astype(str).str.contains(employee_search.strip(), case=False, na=False)]
            if not include_unassigned:
                tx_show = tx_show[tx_show['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned']

            tx_show = tx_show.sort_values('total_sale', ascending=False).reset_index(drop=True)
            tx_show.index = range(1, len(tx_show) + 1)
            tx_show.index.name = "#"

            df_display = tx_show.copy()
            df_display['BlinkOrderId'] = df_display['BlinkOrderId'].astype(str)
            df_display['Matched'] = df_display['difference'].apply(lambda x: '✅' if abs(x) <= 1 else '❌')
            diff_num = pd.to_numeric(df_display['difference'], errors='coerce')
            denom_num = pd.to_numeric(df_display['Indoge_total_price'], errors='coerce').replace(0, np.nan)
            match_pct = (1 - (diff_num.abs() / denom_num)) * 100
            match_pct = pd.to_numeric(match_pct, errors='coerce')
            df_display['Match %'] = match_pct.fillna(0).clip(lower=0, upper=100).round(1)

            def diff_color(val):
                try:
                    if pd.isna(val):
                        return ''
                    if val > 0:
                        return 'color: green'
                    if val < 0:
                        return 'color: red'
                except Exception:
                    return ''
                return ''

            styler = (
                df_display[[
                    'sale_date',
                    'shop_name',
                    'employee_name',
                    'total_sale',
                    'Candelahns_commission',
                    'Indoge_total_price',
                    'Indoge_commission',
                    'difference',
                    'Matched',
                    'Match %',
                    'BlinkOrderId',
                    'external_ref_id'
                ]]
                .style
                .format({
                    'sale_date': lambda x: pd.to_datetime(x).strftime('%Y-%m-%d') if pd.notna(x) else '',
                    'total_sale': "{:,.0f}",
                    'Candelahns_commission': "{:,.0f}",
                    'Indoge_total_price': lambda x: "{:,.0f}".format(x) if x > 0 else "-",
                    'Indoge_commission': lambda x: "{:,.0f}".format(x) if x > 0 else "-",
                    'difference': lambda x: "{:,.0f}".format(x) if x != 0 else "-",
                })
                .map(diff_color, subset=['difference'])
            )

            if _allow("Detailed Transactions"):
                self._render_table(
                    styler,
                    width="stretch",
                    hide_index=False,
                    height=420,
                )

            # Daily Summary
            st.markdown("---")
            st.subheader("Daily Summary")
            
            # Fetch from SQL instead of Python aggregation
            daily_summary = get_qr_daily_summary(
                self.start_date,
                end_exclusive_qr,
                self.selected_branches
            )
            
            if not daily_summary.empty:
                daily_display = daily_summary.copy()
                daily_display['sale_date'] = daily_display['sale_date'].dt.strftime('%Y-%m-%d')
                daily_display['total_sale'] = daily_display['total_sale'].apply(lambda x: f"{x:,.0f}")
                daily_display['Candelahns_commission'] = daily_display['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
                daily_display['Indoge_total_price'] = daily_display['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
                daily_display['Indoge_commission'] = daily_display['Indoge_commission'].apply(lambda x: f"{x:,.0f}")
                
                daily_summary_display = daily_display.copy()
                daily_summary_display.index = range(1, len(daily_summary_display) + 1)
                daily_summary_display.index.name = "#"
                
                self._render_table(
                    daily_summary_display[[
                        'sale_date',
                        'transaction_count',
                        'total_sale',
                        'Candelahns_commission',
                        'Indoge_total_price',
                        'Indoge_commission'
                    ]],
                    width="stretch",
                    hide_index=False,
                    height=300,
                    column_config={
                        "sale_date": st.column_config.Column("Date", width="medium"),
                        "transaction_count": st.column_config.Column("Transactions", width="small"),
                        "total_sale": st.column_config.Column("Total Sales", width="medium"),
                        "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                        "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                        "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
                    }
                )
            else:
                st.info("No daily summary data available.")
            
            # Employee Daily Breakdown
            st.markdown("---")
            st.subheader("Employee Daily Breakdown")
            
            # Fetch from SQL instead of Python aggregation
            emp_daily_summary = get_qr_employee_daily_summary(
                self.start_date,
                end_exclusive_qr,
                self.selected_branches
            )
            
            if not emp_daily_summary.empty:
                emp_daily_display = emp_daily_summary.copy()
                emp_daily_display['sale_date'] = emp_daily_display['sale_date'].dt.strftime('%Y-%m-%d')
                emp_daily_display['total_sale'] = emp_daily_display['total_sale'].apply(lambda x: f"{x:,.0f}")
                emp_daily_display['Candelahns_commission'] = emp_daily_display['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
                emp_daily_display['Indoge_total_price'] = emp_daily_display['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
                emp_daily_display['Indoge_commission'] = emp_daily_display['Indoge_commission'].apply(lambda x: f"{x:,.0f}")
                
                emp_daily_summary_display = emp_daily_display.copy()
                emp_daily_summary_display.index = range(1, len(emp_daily_summary_display) + 1)
                emp_daily_summary_display.index.name = "#"
                
                self._render_table(
                    emp_daily_summary_display[[
                        'sale_date',
                        'shop_name',
                        'employee_name',
                        'transaction_count',
                        'total_sale',
                        'Candelahns_commission',
                        'Indoge_total_price',
                        'Indoge_commission'
                    ]],
                    width="stretch",
                    hide_index=False,
                    height=400,
                    column_config={
                        "sale_date": st.column_config.Column("Date", width="medium"),
                        "shop_name": st.column_config.Column("Branch", width="medium"),
                        "employee_name": st.column_config.Column("Employee", width="medium"),
                        "transaction_count": st.column_config.Column("Tx Count", width="small"),
                        "total_sale": st.column_config.Column("Total Sales", width="medium"),
                        "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                        "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                        "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
                    }
                )
            else:
                st.info("No employee daily breakdown data available.")

            # Legacy tables restored (same style/structure as before)
            st.markdown("---")
            if _allow("Employee Totals"):
                st.subheader("Employee-wise Totals (with Shop)")

            employee_summary = df_merged.groupby(['employee_id', 'employee_code', 'employee_name', 'shop_id', 'shop_name'], as_index=False).agg({
                'total_sale': 'sum',
                'Candelahns_commission': 'sum',
                'Indoge_total_price': 'sum',
                'Indoge_commission': 'sum',
                'external_ref_id': 'count'
            }).rename(columns={'external_ref_id': 'transaction_count'})
            employee_summary["employee_id"] = pd.to_numeric(employee_summary.get("employee_id"), errors="coerce").fillna(0).astype(int)
            employee_summary["employee_code"] = employee_summary.get("employee_code", "").fillna("").astype(str)
            # Keep both legacy employee tables aligned by excluding unassigned rows.
            employee_summary = employee_summary[
                employee_summary['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
            ].copy()

            # Attach employment dates + active/inactive status (display/diagnostics only).
            try:
                conn = pool.get_connection("candelahns")
                placeholders_str = ",".join(["?" for _ in self.selected_branches])
                emp_meta_query = f"""
                SELECT
                    shop_employee_id,
                    shop_id,
                    start_date,
                    end_date
                FROM tblDefShopEmployees
                WHERE shop_id IN ({placeholders_str})
                """
                emp_meta = pd.read_sql(emp_meta_query, conn, params=self.selected_branches)
                emp_meta["shop_employee_id"] = pd.to_numeric(emp_meta["shop_employee_id"], errors="coerce").fillna(0).astype(int)
                emp_meta["shop_id"] = pd.to_numeric(emp_meta["shop_id"], errors="coerce").fillna(0).astype(int)
                employee_summary["employee_id"] = pd.to_numeric(employee_summary["employee_id"], errors="coerce").fillna(0).astype(int)
                employee_summary["shop_id"] = pd.to_numeric(employee_summary["shop_id"], errors="coerce").fillna(0).astype(int)
                employee_summary = employee_summary.merge(
                    emp_meta,
                    left_on=["employee_id", "shop_id"],
                    right_on=["shop_employee_id", "shop_id"],
                    how="left",
                )
                employee_summary = employee_summary.drop(columns=["shop_employee_id"], errors="ignore")
            except Exception:
                employee_summary["start_date"] = pd.NaT
                employee_summary["end_date"] = pd.NaT

            range_start = pd.to_datetime(self.start_date)
            range_end = pd.to_datetime(self.end_date)
            employee_summary["employment_start_date"] = pd.to_datetime(employee_summary.get("start_date"), errors="coerce")
            employee_summary["employment_end_date"] = pd.to_datetime(employee_summary.get("end_date"), errors="coerce")
            start_ok = employee_summary["employment_start_date"].isna() | (employee_summary["employment_start_date"] <= range_end)
            end_ok = employee_summary["employment_end_date"].isna() | (employee_summary["employment_end_date"] >= range_start)
            employee_summary["active_in_range"] = (start_ok & end_ok).fillna(True)
            employee_summary["employment_status"] = employee_summary["active_in_range"].map(
                lambda x: "Active" if bool(x) else "Inactive"
            )

            emp_show = employee_summary.sort_values('total_sale', ascending=False).reset_index(drop=True)
            emp_show.index = range(1, len(emp_show) + 1)
            emp_show.index.name = "#"

            emp_show['total_sale'] = emp_show['total_sale'].apply(lambda x: f"{x:,.0f}")
            emp_show['Candelahns_commission'] = emp_show['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
            emp_show['Indoge_total_price'] = emp_show['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
            emp_show['Indoge_commission'] = emp_show['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

            if _allow("Employee Totals"):
                self._render_table(
                    emp_show[[
                        'employee_id',
                        'employee_code',
                        'employee_name',
                        'shop_name',
                        'employment_status',
                        'transaction_count',
                        'total_sale',
                        'Candelahns_commission',
                        'Indoge_total_price',
                        'Indoge_commission'
                    ]],
                    width="stretch",
                    hide_index=False,
                    column_config={
                        "employee_id": st.column_config.Column("Emp ID", width="small"),
                        "employee_code": st.column_config.Column("Field Code", width="small"),
                        "employee_name": st.column_config.Column("Employee", width="medium"),
                        "shop_name": st.column_config.Column("Shop", width="medium"),
                        "employment_status": st.column_config.Column("Status", width="small"),
                        "transaction_count": st.column_config.Column("Tx Count", width="small"),
                        "total_sale": st.column_config.Column("Total Sales", width="medium"),
                        "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                        "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                        "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
                    }
                )

            st.markdown("---")
            if _allow("Employee Totals (No Sales/Candelahns)"):
                st.subheader("Employee-wise Totals (with Shop) - No Total Sales / Candelahns")
            show_zero_qr = st.checkbox("Show all employees (including zero QR sales)", value=True, key="show_zero_qr_toggle_legacy")
            employment_filter = st.selectbox(
                "Employment Filter",
                ["Active only", "Inactive only", "Both"],
                index=0,
                key="qr_employment_filter",
                help="Uses tblDefShopEmployees.start_date/end_date to decide active/inactive in selected date range."
            )

            try:
                conn = pool.get_connection("candelahns")
                placeholders_str = ",".join(["?" for _ in self.selected_branches])
                all_employees_query = f"""
                SELECT DISTINCT
                    e.shop_employee_id,
                    LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
                    e.field_name AS employee_name,
                    e.shop_id,
                    sh.shop_name,
                    e.start_date,
                    e.end_date
                FROM tblDefShopEmployees e
                INNER JOIN tblDefShops sh ON e.shop_id = sh.shop_id
                WHERE e.shop_id IN ({placeholders_str})
                ORDER BY e.shop_id, e.field_name
                """
                all_employees_df = pd.read_sql(all_employees_query, conn, params=self.selected_branches)
                all_employees_df = all_employees_df.drop_duplicates(subset=['shop_employee_id', 'shop_id']).copy()

                emp_no_sales = all_employees_df.merge(
                    employee_summary,
                    left_on=['shop_employee_id', 'shop_id'],
                    right_on=['employee_id', 'shop_id'],
                    how='left'
                ).fillna({
                    'total_sale': 0,
                    'Candelahns_commission': 0,
                    'Indoge_total_price': 0,
                    'Indoge_commission': 0,
                    'transaction_count': 0
                })
                emp_no_sales['employee_name'] = emp_no_sales['employee_name_x'].fillna(emp_no_sales.get('employee_name_y'))
                emp_no_sales['shop_name'] = emp_no_sales['shop_name_x'].fillna(emp_no_sales.get('shop_name_y'))
                emp_no_sales['employee_code'] = emp_no_sales['employee_code_x'].fillna(emp_no_sales.get('employee_code_y'))
                emp_no_sales['start_date'] = emp_no_sales.get('start_date_x').fillna(emp_no_sales.get('start_date_y'))
                emp_no_sales['end_date'] = emp_no_sales.get('end_date_x').fillna(emp_no_sales.get('end_date_y'))
                emp_no_sales['employee_id'] = pd.to_numeric(
                    emp_no_sales['shop_employee_id'], errors='coerce'
                ).fillna(0).astype(int)
                emp_no_sales["employee_id"] = pd.to_numeric(emp_no_sales.get("employee_id"), errors="coerce").fillna(0).astype(int)
                emp_no_sales["employee_code"] = emp_no_sales.get("employee_code", "").fillna("").astype(str)

                # Employment status (active/inactive in selected date range)
                range_start = pd.to_datetime(self.start_date, errors='coerce').date()
                range_end = pd.to_datetime(self.end_date, errors='coerce').date()
                emp_no_sales['employment_start_date'] = pd.to_datetime(emp_no_sales.get('start_date'), errors='coerce').dt.date
                emp_no_sales['employment_end_date'] = pd.to_datetime(emp_no_sales.get('end_date'), errors='coerce').dt.date
                start_ok = emp_no_sales['employment_start_date'].isna() | (emp_no_sales['employment_start_date'] <= range_end)
                end_ok = emp_no_sales['employment_end_date'].isna() | (emp_no_sales['employment_end_date'] >= range_start)
                emp_no_sales['active_in_range'] = (start_ok & end_ok).fillna(True)
                emp_no_sales['employment_status'] = emp_no_sales['active_in_range'].map(lambda x: "Active" if bool(x) else "Inactive")

                # Keep this table aligned with Branch-wise Totals (which excludes Online/Unassigned)
                emp_no_sales = emp_no_sales[
                    emp_no_sales['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
                ].copy()

                # Keep an unfiltered roster copy for the overall multi-sheet Excel export.
                emp_no_sales_all_download = emp_no_sales.copy()

                if employment_filter == "Active only":
                    emp_no_sales = emp_no_sales[emp_no_sales['active_in_range']].copy()
                elif employment_filter == "Inactive only":
                    emp_no_sales = emp_no_sales[~emp_no_sales['active_in_range']].copy()

                if not show_zero_qr:
                    emp_no_sales = emp_no_sales[emp_no_sales['Indoge_total_price'] > 0]

                emp_no_sales = emp_no_sales.sort_values(['shop_id', 'Indoge_total_price'], ascending=[True, False]).reset_index(drop=True)
                emp_no_sales.index = range(1, len(emp_no_sales) + 1)
                emp_no_sales.index.name = "#"

            except Exception as e:
                st.warning(f"Could not fetch all employees: {e}")
                emp_no_sales = employee_summary.copy()
                emp_no_sales = emp_no_sales[
                    emp_no_sales['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
                ].copy()
                emp_no_sales_all_download = emp_no_sales.copy()

            # Keep raw numeric copy for Excel export before display formatting.
            for col, default in [
                ("employment_status", ""),
                ("employment_start_date", pd.NaT),
                ("employment_end_date", pd.NaT),
                ("active_in_range", True),
            ]:
                if col not in emp_no_sales.columns:
                    emp_no_sales[col] = default
            emp_no_sales_download = emp_no_sales.copy()

            emp_no_sales['Indoge_total_price'] = emp_no_sales['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
            emp_no_sales['Indoge_commission'] = emp_no_sales['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

            if _allow("Employee Totals (No Sales/Candelahns)"):
                self._render_table(
                        emp_no_sales[[
                            'employee_id',
                            'employee_code',
                            'employee_name',
                            'shop_name',
                            'employment_status',
                            'employment_start_date',
                            'employment_end_date',
                            'transaction_count',
                            'Indoge_total_price',
                            'Indoge_commission'
                        ]],
                    width="stretch",
                    hide_index=False,
                        column_config={
                            "employee_id": st.column_config.Column("Emp ID", width="small"),
                            "employee_code": st.column_config.Column("Field Code", width="small"),
                            "employee_name": st.column_config.Column("Employee", width="medium"),
                            "shop_name": st.column_config.Column("Shop", width="medium"),
                            "employment_status": st.column_config.Column("Status", width="small"),
                            "employment_start_date": st.column_config.Column("Start", width="small"),
                            "employment_end_date": st.column_config.Column("End", width="small"),
                            "transaction_count": st.column_config.Column("Tx Count", width="small"),
                            "Indoge_total_price": st.column_config.Column("QR Total Sales", width="medium"),
                            "Indoge_commission": st.column_config.Column("QR Commission", width="medium"),
                        }
                    )

            if _allow("Employee Totals (No Sales/Candelahns)"):
                st.download_button(
                    label="Download Employee + Shop Summary (No Sales/Candelahns) Excel",
                    data=self._export_to_excel(emp_no_sales_download, "Employee Shop Summary"),
                    file_name="qr_employee_shop_summary_no_sales.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.markdown("---")

            st.markdown("---")
            if _allow("Employee Pivot"):
                st.subheader("Employee-wise Pivot (No Total Sales / Candelahns)")
            pivot_metric = st.selectbox(
                "Pivot Metric",
                options=["QR Total Sales", "QR Commission", "Tx Count"],
                index=0,
                key="qr_emp_pivot_metric"
            )

            metric_col_map = {
                "QR Total Sales": "Indoge_total_price",
                "QR Commission": "Indoge_commission",
                "Tx Count": "transaction_count",
            }
            metric_col = metric_col_map[pivot_metric]

            pivot_source = emp_no_sales.copy()
            if metric_col in ["Indoge_total_price", "Indoge_commission"]:
                pivot_source[metric_col] = pd.to_numeric(pivot_source[metric_col], errors="coerce").fillna(0.0)
            else:
                pivot_source[metric_col] = pd.to_numeric(pivot_source[metric_col], errors="coerce").fillna(0).astype(int)

            pivot_df = pivot_source.pivot_table(
                index=["employee_id", "employee_code", "employee_name"],
                columns="shop_name",
                values=metric_col,
                aggfunc="sum",
                fill_value=0
            ).reset_index()

            # Keep IDs as strings to avoid mixed dtype issues in Streamlit/Arrow.
            pivot_df["employee_id"] = pivot_df["employee_id"].astype(str)
            pivot_df["employee_code"] = pivot_df["employee_code"].astype(str)

            branch_cols = [c for c in pivot_df.columns if c not in ["employee_id", "employee_code", "employee_name"]]
            pivot_df["Grand Total"] = pivot_df[branch_cols].sum(axis=1) if branch_cols else 0
            pivot_df = pivot_df.sort_values("Grand Total", ascending=False).reset_index(drop=True)

            total_row = {"employee_id": "", "employee_code": "", "employee_name": "Branch Total"}
            for col in branch_cols + ["Grand Total"]:
                total_row[col] = pivot_df[col].sum() if col in pivot_df.columns else 0
            pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])], ignore_index=True)

            pivot_df.index = range(1, len(pivot_df) + 1)
            pivot_df.index.name = "#"

            pivot_show = pivot_df.copy()
            if metric_col in ["Indoge_total_price", "Indoge_commission"]:
                for col in branch_cols + ["Grand Total"]:
                    pivot_show[col] = pivot_show[col].apply(lambda x: f"{x:,.0f}")

            if _allow("Employee Pivot"):
                self._render_table(
                    pivot_show,
                    width="stretch",
                    hide_index=False,
                    height=420,
                    column_config={
                        "employee_id": st.column_config.Column("Emp ID", width="small"),
                        "employee_code": st.column_config.Column("Field Code", width="small"),
                        "employee_name": st.column_config.Column("Employee", width="medium"),
                        "Grand Total": st.column_config.Column("Grand Total", width="medium"),
                    }
                )

                st.download_button(
                    label="Download Employee Pivot Excel",
                    data=self._export_to_excel(pivot_df, "Employee Pivot"),
                    file_name="qr_employee_pivot_no_sales_candelahns.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.markdown("---")
            if _allow("Branch Totals"):
                st.subheader("Branch-wise Totals")

            branch_source = df_merged[
                df_merged['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
            ].copy()

            branch_summary = branch_source.groupby('shop_name', as_index=False).agg({
                'total_sale': 'sum',
                'Candelahns_commission': 'sum',
                'Indoge_total_price': 'sum',
                'Indoge_commission': 'sum',
                'external_ref_id': 'count'
            }).rename(columns={'external_ref_id': 'transaction_count'})

            branch_show = branch_summary.sort_values('total_sale', ascending=False).reset_index(drop=True)
            branch_show.index = range(1, len(branch_show) + 1)
            branch_show.index.name = "#"
            branch_show['total_sale'] = branch_show['total_sale'].apply(lambda x: f"{x:,.0f}")
            branch_show['Candelahns_commission'] = branch_show['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
            branch_show['Indoge_total_price'] = branch_show['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
            branch_show['Indoge_commission'] = branch_show['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

            if _allow("Branch Totals"):
                self._render_table(
                    branch_show[[
                        'shop_name',
                        'transaction_count',
                        'total_sale',
                        'Candelahns_commission',
                        'Indoge_total_price',
                        'Indoge_commission'
                    ]],
                    width="stretch",
                    hide_index=False,
                    column_config={
                        "shop_name": st.column_config.Column("Branch", width="medium"),
                        "transaction_count": st.column_config.Column("Tx Count", width="small"),
                        "total_sale": st.column_config.Column("Total Sales", width="medium"),
                        "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                        "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                        "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
                    }
                )

            if _allow("Employee Totals"):
                st.download_button(
                    label="Download Employee + Shop Summary Excel",
                    data=self._export_to_excel(
                        employee_summary.sort_values('total_sale', ascending=False),
                        "Employee Totals",
                    ),
                    file_name="qr_employee_shop_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            if _allow("Branch Totals"):
                st.download_button(
                    label="Download Branch Summary Excel",
                    data=self._export_to_excel(
                        branch_summary.sort_values('total_sale', ascending=False),
                        "Branch Totals",
                    ),
                    file_name="qr_branch_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # Product-wise commission (restored/added in QR tab)
            st.markdown("---")
            if _allow("Product-wise Commission"):
                st.subheader("Product-wise Commission (Blinkco)")

            if not df_qr_products.empty:
                prod_overall = (
                    df_qr_products.groupby(['Product_code', 'product_name'], as_index=False)
                    .agg(
                        total_qty=('total_qty', 'sum'),
                        product_sales=('product_sales', 'sum')
                    )
                    .sort_values('product_sales', ascending=False)
                    .reset_index(drop=True)
                )
                prod_overall['product_commission'] = prod_overall['product_sales'] * (commission_rate / 100.0)

                prod_show = prod_overall.copy()
                prod_show.index = range(1, len(prod_show) + 1)
                prod_show.index.name = "#"
                prod_show['total_qty'] = prod_show['total_qty'].map(lambda x: f"{x:,.2f}")
                prod_show['product_sales'] = prod_show['product_sales'].apply(format_currency)
                prod_show['product_commission'] = prod_show['product_commission'].apply(format_currency)

                if _allow("Product-wise Commission"):
                    self._render_table(
                        prod_show[['Product_code', 'product_name', 'total_qty', 'product_sales', 'product_commission']],
                        width="stretch",
                        hide_index=False,
                        height=380,
                        column_config={
                            "Product_code": st.column_config.Column("Product Code", width="small"),
                            "product_name": st.column_config.Column("Product", width="large"),
                            "total_qty": st.column_config.Column("Qty", width="small"),
                            "product_sales": st.column_config.Column("Total Sales", width="medium"),
                            "product_commission": st.column_config.Column("Commission", width="medium"),
                        }
                    )

                    st.download_button(
                        label="Download Product-wise Commission Excel",
                        data=self._export_to_excel(prod_overall, "Product Commission"),
                        file_name="qr_product_wise_commission.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No Blinkco product-wise data available for this period.")

            st.markdown("---")
            if _allow("Data Quality"):
                st.subheader("Transaction Quality Flags Summary")
            if not df_merged.empty:
                q_stats = []
                for flag_col, label in [
                    ('is_mismatch', 'Total Mismatches (Candel vs Blink)'),
                    ('is_unassigned', 'Unassigned Employees'),
                    ('is_blink_only', 'Blinkco-only (missing in Candelahns)'),
                    ('is_candel_only', 'Candelahns-only (missing in Blinkco)'),
                ]:
                    count = int(df_merged[flag_col].sum())
                    q_stats.append({'Metric': label, 'Count': count})

                quality_df = pd.DataFrame(q_stats)
                if _allow("Data Quality"):
                    self._render_table(quality_df, width="stretch", height=220)
            else:
                quality_df = pd.DataFrame()

            overall_tables = {
                "Split Report (Filtered)": split_report_filtered.sort_values(sort_col, ascending=False)
                if 'split_report_filtered' in locals() and not split_report_filtered.empty
                else pd.DataFrame(),
                "Split Report (Full)": split_report.sort_values("total_sales_all", ascending=False)
                if 'split_report' in locals() and not split_report.empty
                else pd.DataFrame(),
                "Transactions (QR)": df_merged.copy(),
                "Employee Totals": employee_summary.sort_values("total_sale", ascending=False).copy()
                if 'employee_summary' in locals() and not employee_summary.empty
                else pd.DataFrame(),
                "Employee Totals (All)": emp_no_sales_all_download.copy()
                if 'emp_no_sales_all_download' in locals() and emp_no_sales_all_download is not None
                else pd.DataFrame(),
                "Employee Pivot": pivot_df.copy() if 'pivot_df' in locals() and pivot_df is not None else pd.DataFrame(),
                "Branch Totals": branch_summary.sort_values("total_sale", ascending=False).copy()
                if 'branch_summary' in locals() and not branch_summary.empty
                else pd.DataFrame(),
                "Quality Summary": quality_df.copy(),
            }

            st.download_button(
                label="Download QR Tab Excel (All Sheets)",
                data=self._export_tables_to_excel(overall_tables),
                file_name=f"qr_tab_{self.start_date}_to_{self.end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.download_button(
                label="Download Detailed Transactions Excel",
                data=self._export_to_excel(df_merged, "Transactions"),
                file_name="qr_detailed_with_commissions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.download_button(
                label="Download Data Quality Checks Excel",
                data=self._export_to_excel(quality_df, "Data Quality"),
                file_name="qr_data_quality_checks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No QR/Blinkco transaction data available.")

    def _fetch_qr_commission_data(self, start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch Blinkco transactions at sale level."""
        return _cached_qr_commission_data(start_str, end_exclusive_str, branch_ids, mode)

    def _fetch_total_sales_data(self, start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch total sales (all order types) by employee and branch."""
        conn = pool.get_connection("candelahns")
        total_query = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions_all,
            SUM(s.Nt_amount) AS total_sales_all
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
        """

        total_params: List = [start_str, end_exclusive_str] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                total_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                total_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                total_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                total_params.extend(BLOCKED_COMMENTS)

        total_query += """
        GROUP BY
            s.shop_id, sh.shop_name,
            COALESCE(e.shop_employee_id, 0),
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY total_sales_all DESC
        """
        return pd.read_sql(total_query, conn, params=total_params)

    def _fetch_sales_summary_combined(self, start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch combined sales summary (all + blinkco) by employee and branch in one query."""
        return _cached_sales_summary_combined(start_str, end_exclusive_str, branch_ids, mode)

    def _fetch_blink_raw_orders(self, start_str: str, end_exclusive_str: str) -> pd.DataFrame:
        return _cached_blink_raw_orders(start_str, end_exclusive_str)

    def _fetch_qr_product_sales_data(self, start_str: str, end_exclusive_str: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch Blinkco line-item product sales for product-wise commission."""
        return _cached_qr_product_sales_data(start_str, end_exclusive_str, branch_ids, mode)

    def _fetch_non_blinkco_employee_summary(
        self,
        start_str: str,
        end_exclusive_str: str,
        branch_ids: List[int],
        mode: str,
    ) -> pd.DataFrame:
        """Fetch Non-Blinkco POS employee summary (external_ref_type != 'Blinkco order' OR null)."""
        conn = pool.get_connection("candelahns")
        non_q = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS transaction_count,
            SUM(s.Nt_amount) AS total_sale
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND (s.external_ref_type IS NULL OR s.external_ref_type <> 'Blinkco order')
        """
        params: List = [start_str, end_exclusive_str] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                non_q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                non_q += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)
        non_q += """
        GROUP BY
            s.shop_id, sh.shop_name,
            COALESCE(e.shop_employee_id, 0),
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY total_sale DESC
        """
        return pd.read_sql(non_q, conn, params=params)

    def _build_split_report(self, df_total_sales: pd.DataFrame, df_blinkco_summary: pd.DataFrame, commission_rate: float) -> pd.DataFrame:
        """Build employee+branch split report (all/blinkco/non-blinkco + shares + commissions)."""
        base = df_total_sales.copy() if df_total_sales is not None else pd.DataFrame()
        blink = df_blinkco_summary.copy() if df_blinkco_summary is not None else pd.DataFrame()

        required_total = {"employee_name", "shop_name", "total_transactions_all", "total_sales_all"}
        required_blink = {"employee_name", "shop_name", "total_sales_blinkco", "total_transactions_blinkco"}
        if base.empty or not required_total.issubset(set(base.columns)):
            return pd.DataFrame()
        if blink.empty:
            blink = pd.DataFrame(columns=list(required_blink))
        # Prefer stable identity keys when available; names can legitimately repeat.
        if {"employee_id", "shop_id"}.issubset(set(base.columns)) and {"employee_id", "shop_id"}.issubset(set(blink.columns)):
            key_cols = ["employee_id", "shop_id"]
        else:
            key_cols = ["employee_name", "shop_name"]

        # If combined summary already includes blinkco columns, don't re-merge and create suffixes.
        if {"total_sales_blinkco", "total_transactions_blinkco"}.issubset(set(base.columns)):
            merged = base.copy()
        else:
            merged = base.merge(
                blink[key_cols + ["total_sales_blinkco", "total_transactions_blinkco"]],
                on=key_cols,
                how="left",
            )

        # SQL aggregates can come back as Decimal/object; normalize early so pandas ops like .clip work.
        if "total_sales_all" in merged.columns:
            merged["total_sales_all"] = pd.to_numeric(merged["total_sales_all"], errors="coerce").fillna(0.0)
        if "total_transactions_all" in merged.columns:
            merged["total_transactions_all"] = (
                pd.to_numeric(merged["total_transactions_all"], errors="coerce").fillna(0).astype(int)
            )

        # Handle suffix fallback if any legacy merge created _x/_y columns.
        if "total_sales_blinkco" not in merged.columns:
            if "total_sales_blinkco_y" in merged.columns:
                merged["total_sales_blinkco"] = merged["total_sales_blinkco_y"]
            elif "total_sales_blinkco_x" in merged.columns:
                merged["total_sales_blinkco"] = merged["total_sales_blinkco_x"]
        if "total_transactions_blinkco" not in merged.columns:
            if "total_transactions_blinkco_y" in merged.columns:
                merged["total_transactions_blinkco"] = merged["total_transactions_blinkco_y"]
            elif "total_transactions_blinkco_x" in merged.columns:
                merged["total_transactions_blinkco"] = merged["total_transactions_blinkco_x"]

        merged["total_sales_blinkco"] = pd.to_numeric(merged["total_sales_blinkco"], errors="coerce").fillna(0.0)
        merged["total_transactions_blinkco"] = pd.to_numeric(merged["total_transactions_blinkco"], errors="coerce").fillna(0).astype(int)
        merged["total_sales_without_blinkco"] = (merged["total_sales_all"] - merged["total_sales_blinkco"]).clip(lower=0)
        merged["total_transactions_without_blinkco"] = (
            pd.to_numeric(merged["total_transactions_all"], errors="coerce").fillna(0).astype(int)
            - merged["total_transactions_blinkco"]
        ).clip(lower=0)

        # Use NaN (not pd.NA) to keep float dtype; pd.NA can force object dtype and
        # later .round() will fail with "Expected numeric dtype, got object instead."
        total_den = merged["total_sales_all"].replace(0, np.nan)
        merged["blinkco_share_pct"] = (merged["total_sales_blinkco"] / total_den * 100).fillna(0).round(2)
        merged["without_blinkco_share_pct"] = (merged["total_sales_without_blinkco"] / total_den * 100).fillna(0).round(2)
        merged["diff_total_minus_blinkco"] = merged["total_sales_all"] - merged["total_sales_blinkco"]

        merged["commission_total_sales"] = merged["total_sales_all"] * (commission_rate / 100.0)
        merged["commission_blinkco_sales"] = merged["total_sales_blinkco"] * (commission_rate / 100.0)
        merged["commission_without_blinkco_sales"] = merged["total_sales_without_blinkco"] * (commission_rate / 100.0)
        merged["has_blink_order"] = merged["total_transactions_blinkco"] > 0
        merged["blink_mismatch_flag"] = (merged["diff_total_minus_blinkco"].abs() > 1.0) & merged["has_blink_order"]
        return merged

    def _export_to_excel(self, df: pd.DataFrame, sheet_name: str) -> bytes:
        """Export DataFrame to Excel with formatting"""
        from modules.utils import export_to_excel
        return export_to_excel(df, sheet_name)

    def _export_tables_to_excel(self, tables: dict) -> bytes:
        """Export multiple DataFrames into a single Excel workbook"""
        from modules.utils import export_tables_to_excel
        return export_tables_to_excel(tables)

    def _render_table(self, data, width: str = "stretch", height: Optional[int] = None, hide_index: bool = True, column_config: Optional[Dict] = None):
        """Consistent dataframe rendering for readability across the dashboard."""
        kwargs = {
            "width": width,
            "hide_index": hide_index
        }
        if height is not None:
            kwargs["height"] = height
        if column_config is not None:
            kwargs["column_config"] = column_config
        st.dataframe(data, **kwargs)
