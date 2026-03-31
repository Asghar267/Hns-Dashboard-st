"""
Shared QR tab renderer used by both dashboards.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
import streamlit as st

from modules.blink_reporting import prepare_blink_orders
from modules.utils import export_excel, format_currency, perf_trace
from modules.qr_business_toggles import QR_TOGGLES
from services.qr_commission_service import QRCommissionService
from dashboard_tabs.qr_commission_tab import QRCommissionTab


def render_qr_tab(
    start_date_str: str,
    end_date_str: str,
    selected_branches: List[int],
    data_mode: str,
    key_prefix: str = "qr",
    allowed_tables: object | None = None,
) -> None:
    """Wrapper to render the QR Commission tab using the modular class implementation."""
    st.header("QR Commission")
    commission_rate = st.number_input(
        "Commission Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(QR_TOGGLES.default_commission_rate),
        step=0.1,
        key=f"{key_prefix}_commission_rate",
        help="Commission percentage for QR sales",
    )
    tab = QRCommissionTab(
        start_date=start_date_str,
        end_date=end_date_str,
        selected_branches=selected_branches,
        data_mode=data_mode,
        allowed_tables=allowed_tables,
    )
    tab.render_qr_commission(commission_rate=commission_rate)

def _render_price_only_match_table(
    qr_service: QRCommissionService,
    df_non_no_ref: pd.DataFrame,
    start_date_str: str,
    end_exclusive: str,
    branch_ids: List[int],
    data_mode: str,
    key_prefix: str,
    title: str,
) -> None:
    """Price-only matching for non-Blinkco rows with no external_ref_id."""
    if df_non_no_ref is None or df_non_no_ref.empty:
        st.info("No non-Blinkco rows without external_ref_id for price-only matching.")
        return

    raw = qr_service.get_blink_raw_orders(start_date_str, end_exclusive)
    if raw is None or raw.empty:
        st.info("No Blink raw orders found in this period for price-only matching.")
        return

    raw_prep = raw.copy()
    raw_prep = raw_prep[["BlinkOrderId", "OrderJson", "CreatedAt"]].copy()
    raw_prep = prepare_blink_orders(raw_prep)
    raw_prices_series = pd.to_numeric(raw_prep.get("Indoge_total_price", 0), errors="coerce").dropna()
    raw_prices_series = raw_prices_series[raw_prices_series > 0].astype(float)
    if raw_prices_series.empty:
        st.info("Blink raw orders contain no valid prices for price-only matching.")
        return

    raw_valid = raw_prep.loc[raw_prices_series.index].copy()
    raw_valid["Indoge_total_price"] = raw_prices_series
    raw_valid["indoge_total_qty"] = pd.to_numeric(raw_valid.get("indoge_total_qty", 0), errors="coerce").fillna(0).astype(int)
    raw_valid["indoge_item_count"] = pd.to_numeric(raw_valid.get("indoge_item_count", 0), errors="coerce").fillna(0).astype(int)
    raw_valid = raw_valid.sort_values("Indoge_total_price").reset_index(drop=True)
    raw_prices_sorted = raw_valid["Indoge_total_price"].values
    raw_qty_sorted = raw_valid["indoge_total_qty"].values
    raw_item_sorted = raw_valid["indoge_item_count"].values

    non_ref = df_non_no_ref.copy()
    non_ref["total_sale"] = pd.to_numeric(non_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
    non_ref = non_ref[non_ref["total_sale"] > 0].copy()
    if non_ref.empty:
        st.info("Non-Blinkco rows have no valid prices for price-only matching.")
        return

    def _series(df: pd.DataFrame, col: str, default):
        if col in df.columns:
            return df[col]
        return pd.Series([default] * len(df), index=df.index)

    # Attach POS qty/item lines for non-blinkco rows
    pos_stats = qr_service.get_pos_line_item_stats(start_date_str, end_exclusive, branch_ids, data_mode, blinkco_only=False)
    if pos_stats is not None and not pos_stats.empty:
        pos_stats = pos_stats.rename(columns={"pos_total_qty": "pos_total_qty", "pos_item_lines": "pos_item_lines"})
        non_ref = non_ref.merge(pos_stats, on="sale_id", how="left")
    non_ref["pos_total_qty"] = pd.to_numeric(_series(non_ref, "pos_total_qty", 0), errors="coerce").fillna(0).astype(int)
    non_ref["pos_item_lines"] = pd.to_numeric(_series(non_ref, "pos_item_lines", 0), errors="coerce").fillna(0).astype(int)

    def _nearest_index(x: float) -> int:
        idx = np.searchsorted(raw_prices_sorted, x, side="left")
        if idx == 0:
            return 0
        if idx >= len(raw_prices_sorted):
            return len(raw_prices_sorted) - 1
        prev_v = raw_prices_sorted[idx - 1]
        next_v = raw_prices_sorted[idx]
        return (idx - 1) if abs(x - prev_v) <= abs(x - next_v) else idx

    nearest_idx = non_ref["total_sale"].apply(_nearest_index)
    non_ref["closest_indoge_price"] = nearest_idx.map(lambda i: float(raw_prices_sorted[i]))
    non_ref["indoge_total_qty"] = nearest_idx.map(lambda i: int(raw_qty_sorted[i]))
    non_ref["indoge_item_count"] = nearest_idx.map(lambda i: int(raw_item_sorted[i]))
    non_ref["difference"] = non_ref["total_sale"] - non_ref["closest_indoge_price"]
    non_ref["diff_pct"] = (
        (non_ref["difference"].abs() / non_ref["total_sale"].replace(0, np.nan)) * 100.0
    ).round(2)
    non_ref["price_match_exact"] = non_ref["difference"].abs() < 0.01

    # Qty matching using indoge_total_qty (from JSON) vs POS total qty
    non_ref["indoge_total_qty"] = pd.to_numeric(_series(non_ref, "indoge_total_qty", 0), errors="coerce").fillna(0).astype(int)
    non_ref["indoge_item_count"] = pd.to_numeric(_series(non_ref, "indoge_item_count", 0), errors="coerce").fillna(0).astype(int)
    non_ref["qty_match"] = (non_ref["pos_total_qty"] > 0) & (non_ref["indoge_total_qty"] > 0) & (
        non_ref["pos_total_qty"] == non_ref["indoge_total_qty"]
    )
    non_ref["item_match"] = (non_ref["pos_item_lines"] > 0) & (non_ref["indoge_item_count"] > 0) & (
        non_ref["pos_item_lines"] == non_ref["indoge_item_count"]
    )

    abs_diff = non_ref["difference"].abs()
    non_ref["match_abs_1"] = abs_diff <= 1
    non_ref["match_abs_5"] = abs_diff <= 5
    non_ref["match_abs_10"] = abs_diff <= 10

    non_ref["match_pct_1"] = non_ref["diff_pct"] <= 1
    non_ref["match_pct_2"] = non_ref["diff_pct"] <= 2
    non_ref["match_pct_5"] = non_ref["diff_pct"] <= 5
    non_ref["match_pct_20"] = non_ref["diff_pct"] <= 20

    exact_count = int(non_ref["price_match_exact"].sum())
    match_pct = (exact_count / len(non_ref) * 100.0) if len(non_ref) else 0.0

    st.markdown(f"#### {title}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows (No external_ref_id)", f"{len(non_ref):,}")
    m2.metric("Exact Price Matches", f"{exact_count:,}")
    m3.metric("Exact Match %", f"{match_pct:.2f}%")
    m4.metric("Mean Diff %", f"{non_ref['diff_pct'].mean():.2f}%")

    st.markdown("#### Filter (Price-Only Match)")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        max_diff_pct = st.number_input(
            "Max Diff % (0-100) — Recommended 20%",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=0.5,
            key=f"{key_prefix}_max_diff_pct",
        )
    with f2:
        use_abs_filter = st.checkbox("Use Abs Diff (PKR)", value=False, key=f"{key_prefix}_use_abs_diff")
    with f3:
        max_abs_diff = st.number_input(
            "Max Abs Diff (PKR)",
            min_value=0.0,
            value=10.0,
            step=1.0,
            key=f"{key_prefix}_max_abs_diff",
            disabled=not use_abs_filter,
        )
    with f4:
        match_mode = st.selectbox(
            "Match Filter",
            options=[
                "All rows",
                "Qty OR Item",
                "Qty AND Item",
                "Price + Qty + Item",
            ],
            index=0,
            key=f"{key_prefix}_match_mode",
        )

    filtered = non_ref.copy()
    filtered = filtered[filtered["diff_pct"].fillna(0.0) <= float(max_diff_pct)]
    if use_abs_filter:
        filtered = filtered[filtered["difference"].abs() <= float(max_abs_diff)]
    if match_mode == "Qty OR Item":
        filtered = filtered[filtered["qty_match"] | filtered["item_match"]]
    elif match_mode == "Qty AND Item":
        filtered = filtered[filtered["qty_match"] & filtered["item_match"]]
    elif match_mode == "Price + Qty + Item":
        filtered = filtered[filtered["price_match_exact"] & filtered["qty_match"] & filtered["item_match"]]

    st.caption(f"Filtered rows: {len(filtered):,} (from {len(non_ref):,})")

    tol_stats = pd.DataFrame(
        [
            {
                "Metric": "Abs <= 1 PKR",
                "Matches": int(non_ref["match_abs_1"].sum()),
                "Match %": round(non_ref["match_abs_1"].mean() * 100.0, 2),
            },
            {
                "Metric": "Abs <= 5 PKR",
                "Matches": int(non_ref["match_abs_5"].sum()),
                "Match %": round(non_ref["match_abs_5"].mean() * 100.0, 2),
            },
            {
                "Metric": "Abs <= 10 PKR",
                "Matches": int(non_ref["match_abs_10"].sum()),
                "Match %": round(non_ref["match_abs_10"].mean() * 100.0, 2),
            },
            {
                "Metric": "Diff <= 1%",
                "Matches": int(non_ref["match_pct_1"].sum()),
                "Match %": round(non_ref["match_pct_1"].mean() * 100.0, 2),
            },
            {
                "Metric": "Diff <= 2%",
                "Matches": int(non_ref["match_pct_2"].sum()),
                "Match %": round(non_ref["match_pct_2"].mean() * 100.0, 2),
            },
            {
                "Metric": "Diff <= 5%",
                "Matches": int(non_ref["match_pct_5"].sum()),
                "Match %": round(non_ref["match_pct_5"].mean() * 100.0, 2),
            },
            {
                "Metric": "Diff <= 20% (Acceptable)",
                "Matches": int(non_ref["match_pct_20"].sum()),
                "Match %": round(non_ref["match_pct_20"].mean() * 100.0, 2),
            },
        ]
    )
    st.dataframe(tol_stats, width="stretch", hide_index=True)

    qty_match_count = int(non_ref["qty_match"].sum())
    qty_match_pct = (qty_match_count / len(non_ref) * 100.0) if len(non_ref) else 0.0
    item_match_count = int(non_ref["item_match"].sum())
    item_match_pct = (item_match_count / len(non_ref) * 100.0) if len(non_ref) else 0.0
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Qty Matches (POS vs Indoge)", f"{qty_match_count:,}")
    q2.metric("Qty Match %", f"{qty_match_pct:.2f}%")
    q3.metric("Item Matches (Lines vs JSON)", f"{item_match_count:,}")
    q4.metric("Item Match %", f"{item_match_pct:.2f}%")

    show = filtered.copy().sort_values("total_sale", ascending=False).reset_index(drop=True)
    show.index = range(1, len(show) + 1)
    show.index.name = "#"
    show["total_sale"] = show["total_sale"].apply(format_currency)
    show["closest_indoge_price"] = show["closest_indoge_price"].apply(format_currency)
    show["difference"] = show["difference"].apply(format_currency)
    show["diff_pct"] = show["diff_pct"].apply(lambda x: f"{min(max(x, 0.0), 100.0):.2f}%")

    st.markdown("#### Employee Summary (Price-Only Match)")
    emp_sum = (
        filtered.groupby(
            ["employee_id", "employee_code", "employee_name", "shop_name"], as_index=False
        )
        .agg(
            non_blink_sales=("total_sale", "sum"),
            indoge_price_sum=("closest_indoge_price", "sum"),
            tx_count=("sale_id", "count"),
            pos_qty_sum=("pos_total_qty", "sum"),
            indoge_qty_sum=("indoge_total_qty", "sum"),
            pos_item_lines_sum=("pos_item_lines", "sum"),
            indoge_item_count_sum=("indoge_item_count", "sum"),
        )
    )
    emp_sum["difference"] = emp_sum["non_blink_sales"] - emp_sum["indoge_price_sum"]
    emp_sum["diff_pct"] = (
        (emp_sum["difference"].abs() / emp_sum["non_blink_sales"].replace(0, np.nan)) * 100.0
    ).round(2)
    emp_sum["candela_commission"] = emp_sum["non_blink_sales"] * (QR_TOGGLES.default_commission_rate / 100.0)
    emp_sum["indoge_commission"] = emp_sum["indoge_price_sum"] * (QR_TOGGLES.default_commission_rate / 100.0)
    emp_sum = emp_sum.sort_values("non_blink_sales", ascending=False).reset_index(drop=True)
    emp_sum.index = range(1, len(emp_sum) + 1)
    emp_sum.index.name = "#"

    emp_show = emp_sum.copy()
    emp_show = emp_show.rename(
        columns={
            "non_blink_sales": "Candelahns_sale",
            "indoge_price_sum": "Indoge_sale",
            "candela_commission": "Candelahns_commission",
            "indoge_commission": "Indoge_commission",
        }
    )
    emp_show["Candelahns_sale"] = emp_show["Candelahns_sale"].apply(format_currency)
    emp_show["Indoge_sale"] = emp_show["Indoge_sale"].apply(format_currency)
    emp_show["Candelahns_commission"] = emp_show["Candelahns_commission"].apply(format_currency)
    emp_show["Indoge_commission"] = emp_show["Indoge_commission"].apply(format_currency)
    emp_show["difference"] = emp_show["difference"].apply(format_currency)
    emp_show["diff_pct"] = emp_show["diff_pct"].apply(lambda x: f"{min(max(x, 0.0), 100.0):.2f}%")
    st.dataframe(
        emp_show[
            [
                "employee_id",
                "employee_code",
                "employee_name",
                "shop_name",
                "tx_count",
                "Candelahns_sale",
                "Indoge_sale",
                "pos_qty_sum",
                "indoge_qty_sum",
                "pos_item_lines_sum",
                "indoge_item_count_sum",
                "Candelahns_commission",
                "Indoge_commission",
                "diff_pct",
                "difference",
            ]
        ],
        width="stretch",
        hide_index=False,
        height=360,
    )
    st.download_button(
        label="Download Employee Summary (Price-Only) Excel",
        data=export_excel(emp_sum.reset_index(drop=True), "Employee Summary Price-Only"),
        file_name=f"price_only_employee_summary_{start_date_str}_to_{end_exclusive}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_price_only_emp_summary",
    )

    st.markdown("#### Transaction-Level (Price-Only Match)")
    st.dataframe(
        show[
            [
                "sale_id",
                "shop_name",
                "employee_id",
                "employee_code",
                "employee_name",
                "total_sale",
                "closest_indoge_price",
                "difference",
                "diff_pct",
                "pos_total_qty",
                "indoge_total_qty",
                "qty_match",
                "pos_item_lines",
                "indoge_item_count",
                "item_match",
                "price_match_exact",
            ]
        ],
        width="stretch",
        hide_index=False,
        height=360,
    )
    st.download_button(
        label="Download Price-Only Match Excel",
        data=export_excel(filtered.reset_index(drop=True), "Price Only Match (Filtered)"),
        file_name=f"price_only_match_{start_date_str}_to_{end_exclusive}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_dl_price_only_match",
    )

def render_khadda_diagnostics_tab(
    start_date_str: str,
    end_date_str: str,
    selected_branches: List[int],
    data_mode: str,
    key_prefix: str = "khadda",
) -> None:
    """Standalone Khadda diagnostics tab (POS non-Blinkco + Blinkco match checks)."""
    st.header("Khadda Diagnostics")
    # Fixed cutoff: include 1–11 Mar in <=20% no-ref logic, then post-cutoff from 12 Mar onward.
    original_start_date_str = start_date_str
    original_end_date_str = end_date_str
    original_end_exclusive = (pd.to_datetime(original_end_date_str) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    start_date_str = "2026-03-01"
    cutoff_dt = pd.Timestamp("2026-03-12 00:00:00")
    cutoff_dt_str = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = "2026-03-11"
    st.caption(
        f"Fixed range for this tab: 2026-03-01 to {end_date_str} (<=20% no external_ref_id), "
        f"then post-cutoff external_ref_id from {cutoff_dt_str} up to {original_end_date_str}."
    )
    if 2 not in (selected_branches or []):
        st.info("Select Khadda Main Branch (shop_id=2) in sidebar to view this tab.")
        return

    qr_service = QRCommissionService()
    commission_rate = st.number_input(
        "Commission Rate (%)",
        0.0,
        100.0,
        float(QR_TOGGLES.default_commission_rate),
        0.1,
        key=f"{key_prefix}_commission_rate",
        help="Commission percentage for QR sales",
    )
    end_exclusive = cutoff_dt_str

    c1, c2, c3 = st.columns(3)
    with c1:
        employee_search = st.text_input("Search Employee", key=f"{key_prefix}_employee_search")
    with c2:
        include_unassigned = st.checkbox(
            "Include Online/Unassigned",
            value=bool(QR_TOGGLES.include_unassigned_default),
            key=f"{key_prefix}_include_unassigned",
        )
    with c3:
        show_zero_rows = st.checkbox("Include zero rows", value=True, key=f"{key_prefix}_include_zero")

    # Blinkco side (Candela vs Indoge) + POS non-blinkco totals come from split report.
    with perf_trace("Khadda fetch (qr/total/blink raw)", "db"):
        df_qr = qr_service.get_qr_commission_data(start_date_str, end_exclusive, [2], data_mode)
        df_total_sales = qr_service.get_total_sales_data(start_date_str, end_exclusive, [2], data_mode)
        df_blink_raw = qr_service.get_blink_raw_orders_for_qr_sales(start_date_str, end_exclusive, [2], data_mode)
    with perf_trace("Khadda process (merge)", "processing"):
        df_merged = qr_service.process_qr_data(df_qr, df_blink_raw, commission_rate)

    # Keep defaults so later sections don't crash if a block errors
    df_non_blink = pd.DataFrame()
    df_non_with_ref = pd.DataFrame()
    df_non_no_ref = pd.DataFrame()
    within_20 = pd.DataFrame()
    qr_post = pd.DataFrame()

    if not df_merged.empty:
        blinkco_summary = (
            df_merged.groupby(["employee_id", "employee_name", "shop_id", "shop_name"], as_index=False)
            .agg(total_sales_blinkco=("total_sale", "sum"), total_transactions_blinkco=("sale_id", "count"))
        )
    else:
        blinkco_summary = pd.DataFrame(
            columns=["employee_id", "employee_name", "shop_id", "shop_name", "total_sales_blinkco", "total_transactions_blinkco"]
        )

    split_report = qr_service.get_split_report(df_total_sales, blinkco_summary, commission_rate)
    split_report = qr_service.filter_split_report(
        split_report,
        employee_search=employee_search,
        branches=[],
        include_zero_rows=show_zero_rows,
        include_unassigned=include_unassigned,
    )

    st.markdown("---")
    st.subheader("Khadda Branch: Sales Without Blinkco Order (POS)")
    st.caption("Commission uses the same rate above. Match check: Blinkco Candela vs Indoge Match % >= 50%.")

    if split_report.empty:
        st.info("No sales data available for this period.")
    else:
        kh = split_report.copy()
        kh = kh[pd.to_numeric(kh.get("shop_id", 0), errors="coerce").fillna(0).astype(int) == 2].copy()
        if not include_unassigned:
            kh = kh[kh["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
        if employee_search.strip():
            kh = kh[kh["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)]

        if not df_merged.empty:
            tx_kh = df_merged.copy()
            tx_kh["shop_id"] = pd.to_numeric(tx_kh.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
            tx_kh = tx_kh[tx_kh["shop_id"] == 2].copy()
            if not include_unassigned:
                tx_kh = tx_kh[tx_kh["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
            tx_kh["employee_id"] = pd.to_numeric(tx_kh.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
            tx_kh["Indoge_total_price"] = pd.to_numeric(tx_kh.get("Indoge_total_price", 0), errors="coerce").fillna(0.0)
            indoge_by_emp = tx_kh.groupby(["employee_id", "shop_id"], as_index=False).agg(
                indoge_blink_sales=("Indoge_total_price", "sum")
            )
            kh["employee_id"] = pd.to_numeric(kh.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
            kh["shop_id"] = pd.to_numeric(kh.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
            kh = kh.merge(indoge_by_emp, on=["employee_id", "shop_id"], how="left")
            kh["indoge_blink_sales"] = pd.to_numeric(kh.get("indoge_blink_sales", 0), errors="coerce").fillna(0.0)
        else:
            kh["indoge_blink_sales"] = 0.0

        cand_blink = pd.to_numeric(kh.get("total_sales_blinkco", 0), errors="coerce")
        indoge_blink = pd.to_numeric(kh.get("indoge_blink_sales", 0), errors="coerce")
        both = pd.concat([cand_blink, indoge_blink], axis=1)
        denom_match = both.max(axis=1).replace(0, pd.NA)
        numer_match = both.min(axis=1)
        kh["blink_match_pct"] = ((numer_match / denom_match) * 100.0).astype("Float64").round(2)
        kh["blink_match_ok_50pct"] = kh["blink_match_pct"] >= 50.0

        kh_show = kh.sort_values("total_sales_without_blinkco", ascending=False).reset_index(drop=True)
        kh_show.index = range(1, len(kh_show) + 1)
        kh_show.index.name = "#"
        kh_disp = kh_show.copy()
        kh_disp["blink_match_pct"] = kh_disp["blink_match_pct"].map(lambda x: "" if pd.isna(x) else f"{float(x):.2f}%")
        for col in [
            "total_sales_all",
            "total_sales_blinkco",
            "indoge_blink_sales",
            "total_sales_without_blinkco",
            "commission_total_sales",
            "commission_blinkco_sales",
            "commission_without_blinkco_sales",
        ]:
            if col in kh_disp.columns:
                kh_disp[col] = kh_disp[col].apply(format_currency)

        st.dataframe(
            kh_disp[
                [
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "shop_name",
                    "total_transactions_all",
                    "total_transactions_blinkco",
                    "total_transactions_without_blinkco",
                    "total_sales_all",
                    "total_sales_blinkco",
                    "indoge_blink_sales",
                    "total_sales_without_blinkco",
                    "blink_match_pct",
                    "blink_match_ok_50pct",
                    "commission_total_sales",
                    "commission_blinkco_sales",
                    "commission_without_blinkco_sales",
                ]
            ],
            width="stretch",
            hide_index=False,
            height=420,
        )
        st.download_button(
            label="Download Khadda POS (Non-Blinkco) Excel",
            data=export_excel(kh_show, "Khadda POS Non-Blinkco"),
            file_name=f"qr_khadda_non_blinkco_{start_date_str}_to_{end_date_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_dl_khadda_non_blinkco",
        )

        st.markdown("---")
        st.subheader("Detailed Transactions (Without Blinkco Order) - Khadda")
        st.caption("Rows without external_ref_id cannot be matched to Blink raw; match fields stay blank.")

        # Reuse the same best-effort logic as QR tab, but in standalone form.
        try:
            df_non_blink = qr_service.get_non_blinkco_sales_transactions(start_date_str, end_exclusive, [2], data_mode)
            if df_non_blink is None or df_non_blink.empty:
                st.info("No non-Blinkco transactions found for Khadda in this period.")
                df_non_blink = pd.DataFrame()
                df_non_with_ref = pd.DataFrame()
                df_non_no_ref = pd.DataFrame()
                within_20 = pd.DataFrame()
            else:
                df_non_blink["total_sale"] = pd.to_numeric(df_non_blink.get("total_sale", 0), errors="coerce").fillna(0.0)

                ext = (
                    df_non_blink.get("external_ref_id", pd.Series([], dtype="object"))
                    .astype(str)
                    .str.strip()
                    .replace("None", "")
                )
                has_ref = ext.ne("")
                df_non_with_ref = df_non_blink.loc[has_ref].copy()
                df_non_no_ref = df_non_blink.loc[~has_ref].copy()

                # Non-Blinkco overview metrics
                tx_total = int(len(df_non_blink))
                tx_with_ref = int(len(df_non_with_ref))
                tx_no_ref = int(len(df_non_no_ref))
                sales_total = float(df_non_blink["total_sale"].sum())
                sales_with_ref = float(df_non_with_ref["total_sale"].sum()) if not df_non_with_ref.empty else 0.0
                sales_no_ref = float(df_non_no_ref["total_sale"].sum()) if not df_non_no_ref.empty else 0.0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Non-Blinkco Sales", format_currency(sales_total))
                m2.metric("Non-Blinkco Tx", f"{tx_total:,}")
                m3.metric("With external_ref_id", f"{tx_with_ref:,}")
                m4.metric("Without external_ref_id", f"{tx_no_ref:,}")
                m5.metric("Sales w/o external_ref_id", format_currency(sales_no_ref))

            # Build <=20% price-diff subset for fixed-range no-ref rows
            within_20 = pd.DataFrame()
            try:
                non_ref_summary = df_non_no_ref.copy()
                non_ref_summary["total_sale"] = pd.to_numeric(
                    non_ref_summary.get("total_sale", 0), errors="coerce"
                ).fillna(0.0)
                if not non_ref_summary.empty:
                    raw = qr_service.get_blink_raw_orders(start_date_str, end_exclusive)
                    if raw is not None and not raw.empty:
                        raw_prep = raw[["BlinkOrderId", "OrderJson", "CreatedAt"]].copy()
                        raw_prep = prepare_blink_orders(raw_prep)
                        raw_prices = pd.to_numeric(
                            raw_prep.get("Indoge_total_price", 0), errors="coerce"
                        ).dropna()
                        raw_prices = raw_prices[raw_prices > 0].astype(float)
                        if not raw_prices.empty:
                            raw_prices_sorted = np.sort(raw_prices.values)

                            def _nearest_price(x: float) -> float:
                                idx = np.searchsorted(raw_prices_sorted, x, side="left")
                                if idx == 0:
                                    return float(raw_prices_sorted[0])
                                if idx >= len(raw_prices_sorted):
                                    return float(raw_prices_sorted[-1])
                                prev_v = raw_prices_sorted[idx - 1]
                                next_v = raw_prices_sorted[idx]
                                return float(prev_v if abs(x - prev_v) <= abs(x - next_v) else next_v)

                            non_ref_summary["closest_indoge_price"] = non_ref_summary["total_sale"].apply(_nearest_price)
                            non_ref_summary["diff_pct"] = (
                                (non_ref_summary["total_sale"] - non_ref_summary["closest_indoge_price"]).abs()
                                / non_ref_summary["total_sale"].replace(0, pd.NA) * 100.0
                            )
                            within_20 = non_ref_summary[non_ref_summary["diff_pct"] <= 20.0].copy()
            except Exception:
                within_20 = pd.DataFrame()

            daily_no_ref_rendered = False
            daily_post_rendered = False
            try:
                # Post-cutoff uses QR sales with external_ref_id up to sidebar end date (for daily summaries)
                post_start = cutoff_dt_str
                if pd.to_datetime(original_end_date_str) >= pd.to_datetime(post_start):
                    qr_post_emp = qr_service.get_qr_commission_data(post_start, original_end_exclusive, [2], data_mode)
                else:
                    qr_post_emp = pd.DataFrame()
                if qr_post_emp is not None and not qr_post_emp.empty:
                    qr_post_emp["external_ref_id"] = qr_post_emp["external_ref_id"].astype(str).str.strip().replace("None", "")
                    qr_post_emp = qr_post_emp[qr_post_emp["external_ref_id"] != ""].copy()
                    qr_post = qr_post_emp.copy()
                else:
                    qr_post = pd.DataFrame()

                # Daily employee summaries
                st.markdown("#### Daily Employee Summary (<=20% Price Diff, No external_ref_id) - 1 Mar to 11 Mar")
                try:
                    daily_no_ref = within_20.copy() if isinstance(within_20, pd.DataFrame) else pd.DataFrame()
                    if not include_unassigned:
                        daily_no_ref = daily_no_ref[
                            daily_no_ref["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"
                        ].copy()
                    if employee_search.strip():
                        daily_no_ref = daily_no_ref[
                            daily_no_ref["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)
                        ].copy()
                    if "sale_date" in daily_no_ref.columns:
                        daily_no_ref["sale_day"] = pd.to_datetime(daily_no_ref["sale_date"], errors="coerce").dt.date
                    else:
                        daily_no_ref["sale_day"] = pd.NaT
                    daily_no_ref = daily_no_ref.dropna(subset=["sale_day"])
                    daily_no_ref["total_sale"] = pd.to_numeric(daily_no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                    if daily_no_ref.empty:
                        st.info("No daily employee rows for <=20% no-ref summary.")
                    else:
                        daily_emp = (
                            daily_no_ref.groupby(
                                ["sale_day", "employee_id", "employee_code", "employee_name", "shop_name"],
                                as_index=False
                            )
                            .agg(
                                tx_count=("sale_id", "count"),
                                total_sale=("total_sale", "sum"),
                            )
                        )
                        daily_emp = daily_emp.sort_values(["sale_day", "total_sale"], ascending=[False, False]).reset_index(drop=True)
                        daily_emp.index = range(1, len(daily_emp) + 1)
                        daily_emp.index.name = "#"
                        daily_show = daily_emp.copy()
                        daily_show["total_sale"] = daily_show["total_sale"].apply(format_currency)
                        st.dataframe(
                            daily_show[
                                [
                                    "sale_day",
                                    "employee_id",
                                    "employee_code",
                                    "employee_name",
                                    "shop_name",
                                    "tx_count",
                                    "total_sale",
                                ]
                            ],
                            width="stretch",
                            hide_index=False,
                            height=360,
                        )
                        daily_no_ref_rendered = True
                except Exception as e:
                    st.warning(f"Daily employee summary (no-ref) skipped due to error: {e}")

                st.markdown(f"#### Daily Employee Summary (Post-cutoff, with external_ref_id) -> {original_end_date_str}")
                try:
                    if not isinstance(qr_post, pd.DataFrame):
                        qr_post = pd.DataFrame()
                    daily_post = qr_post.copy()
                    if not include_unassigned:
                        daily_post = daily_post[
                            daily_post["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"
                        ].copy()
                    if employee_search.strip():
                        daily_post = daily_post[
                            daily_post["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)
                        ].copy()
                    if "sale_date" in daily_post.columns:
                        daily_post["sale_day"] = pd.to_datetime(daily_post["sale_date"], errors="coerce").dt.date
                    else:
                        daily_post["sale_day"] = pd.NaT
                    daily_post = daily_post.dropna(subset=["sale_day"])
                    daily_post["total_sale"] = pd.to_numeric(daily_post.get("total_sale", 0), errors="coerce").fillna(0.0)
                    if daily_post.empty:
                        st.info("No daily employee rows for post-cutoff summary.")
                    else:
                        daily_post_emp = (
                            daily_post.groupby(
                                ["sale_day", "employee_id", "employee_code", "employee_name", "shop_name"],
                                as_index=False
                            )
                            .agg(
                                tx_count=("sale_id", "count"),
                                total_sale=("total_sale", "sum"),
                            )
                        )
                        daily_post_emp = daily_post_emp.sort_values(["sale_day", "total_sale"], ascending=[False, False]).reset_index(drop=True)
                        daily_post_emp.index = range(1, len(daily_post_emp) + 1)
                        daily_post_emp.index.name = "#"
                        post_show = daily_post_emp.copy()
                        post_show["total_sale"] = post_show["total_sale"].apply(format_currency)
                        st.dataframe(
                            post_show[
                                [
                                    "sale_day",
                                    "employee_id",
                                    "employee_code",
                                    "employee_name",
                                    "shop_name",
                                    "tx_count",
                                    "total_sale",
                                ]
                            ],
                            width="stretch",
                            hide_index=False,
                            height=360,
                        )
                        daily_post_rendered = True
                except Exception as e:
                    st.warning(f"Daily employee summary (post-cutoff) skipped due to error: {e}")
            except Exception as e:
                st.warning(f"Employee Summary (no-ref) skipped due to error: {e}")

            if not daily_no_ref_rendered:
                st.markdown("#### Daily Employee Summary (<=20% Price Diff, No external_ref_id) - 1 Mar to 11 Mar")
                st.info("No daily employee rows for <=20% no-ref summary.")
            if not daily_post_rendered:
                st.markdown(f"#### Daily Employee Summary (Post-cutoff, with external_ref_id) -> {original_end_date_str}")
                st.info("No daily employee rows for post-cutoff summary.")

            # Combined employee-wise totals (QR Commission format) based on selected date range
            st.markdown("---")
            st.subheader("Employee-wise Totals (with Shop)")
            try:
                fixed_start = pd.Timestamp("2026-03-01")
                fixed_end = pd.Timestamp("2026-03-11")
                sel_start = pd.to_datetime(original_start_date_str)
                sel_end = pd.to_datetime(original_end_date_str)

                def _fetch_qr_range(range_start: pd.Timestamp, range_end: pd.Timestamp) -> pd.DataFrame:
                    if range_start > range_end:
                        return pd.DataFrame()
                    end_excl = (range_end + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                    df = qr_service.get_qr_commission_data(
                        range_start.strftime("%Y-%m-%d"),
                        end_excl,
                        [2],
                        data_mode,
                    )
                    if df is None or df is False or isinstance(df, (int, float)):
                        return pd.DataFrame()
                    return df.copy()

                # Build external_ref_id data for selected range excluding fixed 1–11 Mar window
                pre_end = min(sel_end, fixed_start - pd.Timedelta(days=1))
                post_start = max(sel_start, fixed_end + pd.Timedelta(days=1))

                qr_pre = _fetch_qr_range(sel_start, pre_end)
                qr_post = _fetch_qr_range(post_start, sel_end)
                qr_ext = pd.concat([qr_pre, qr_post], ignore_index=True)

                def _coerce_series(df: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
                    if col in df.columns:
                        return pd.to_numeric(df[col], errors="coerce").fillna(default)
                    return pd.Series([default] * len(df), index=df.index, dtype="float64")

                if not qr_ext.empty:
                    qr_ext["external_ref_id"] = qr_ext["external_ref_id"].astype(str).str.strip().replace("None", "")
                    qr_ext = qr_ext[qr_ext["external_ref_id"] != ""].copy()
                    if not include_unassigned:
                        qr_ext = qr_ext[
                            qr_ext["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"
                        ].copy()
                    if employee_search.strip():
                        qr_ext = qr_ext[
                            qr_ext["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)
                        ].copy()
                    qr_ext["total_sale"] = _coerce_series(qr_ext, "total_sale", 0.0)
                    # Enforce commission on total sale (same % for both external_ref_id and <=20% no-ref)
                    qr_ext["Candelahns_commission"] = _coerce_series(qr_ext, "total_sale", 0.0) * (commission_rate / 100.0)
                    qr_ext["Indoge_total_price"] = _coerce_series(qr_ext, "Indoge_total_price", 0.0)
                    qr_ext["Indoge_commission"] = _coerce_series(qr_ext, "Indoge_commission", 0.0)
                    qr_ext_sum = (
                        qr_ext.groupby(
                            ["employee_id", "employee_code", "employee_name", "shop_id", "shop_name"], as_index=False
                        )
                        .agg(
                            transaction_count=("sale_id", "count"),
                            total_sale=("total_sale", "sum"),
                            Candelahns_commission=("Candelahns_commission", "sum"),
                            Indoge_total_price=("Indoge_total_price", "sum"),
                            Indoge_commission=("Indoge_commission", "sum"),
                        )
                    )
                else:
                    qr_ext_sum = pd.DataFrame(
                        columns=[
                            "employee_id",
                            "employee_code",
                            "employee_name",
                            "shop_id",
                            "shop_name",
                            "transaction_count",
                            "total_sale",
                            "Candelahns_commission",
                            "Indoge_total_price",
                            "Indoge_commission",
                        ]
                    )

                # Build <=20% no-ref data only if selected range overlaps 1–11 Mar
                overlap_start = max(sel_start, fixed_start)
                overlap_end = min(sel_end, fixed_end)
                if overlap_start <= overlap_end and isinstance(within_20, pd.DataFrame) and not within_20.empty:
                    fixed_df = within_20.copy()
                    if "sale_date" in fixed_df.columns:
                        fixed_df["sale_day"] = pd.to_datetime(fixed_df["sale_date"], errors="coerce").dt.date
                        fixed_df = fixed_df.dropna(subset=["sale_day"])
                        fixed_df = fixed_df[
                            (fixed_df["sale_day"] >= overlap_start.date())
                            & (fixed_df["sale_day"] <= overlap_end.date())
                        ].copy()
                    if not include_unassigned and not fixed_df.empty:
                        fixed_df = fixed_df[
                            fixed_df["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"
                        ].copy()
                    if employee_search.strip() and not fixed_df.empty:
                        fixed_df = fixed_df[
                            fixed_df["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)
                        ].copy()
                    if not fixed_df.empty:
                        fixed_df["total_sale"] = pd.to_numeric(fixed_df.get("total_sale", 0), errors="coerce").fillna(0.0)
                        fixed_df["Candelahns_commission"] = fixed_df["total_sale"] * (commission_rate / 100.0)
                        fixed_sum = (
                            fixed_df.groupby(
                                ["employee_id", "employee_code", "employee_name", "shop_id", "shop_name"],
                                as_index=False
                            )
                            .agg(
                                transaction_count=("sale_id", "count"),
                                total_sale=("total_sale", "sum"),
                                Candelahns_commission=("Candelahns_commission", "sum"),
                            )
                        )
                        fixed_sum["Indoge_total_price"] = 0.0
                        fixed_sum["Indoge_commission"] = 0.0
                    else:
                        fixed_sum = pd.DataFrame(
                            columns=[
                                "employee_id",
                                "employee_code",
                                "employee_name",
                                "shop_id",
                                "shop_name",
                                "transaction_count",
                                "total_sale",
                                "Candelahns_commission",
                                "Indoge_total_price",
                                "Indoge_commission",
                            ]
                        )
                else:
                    fixed_sum = pd.DataFrame(
                        columns=[
                            "employee_id",
                            "employee_code",
                            "employee_name",
                            "shop_id",
                            "shop_name",
                            "transaction_count",
                            "total_sale",
                            "Candelahns_commission",
                            "Indoge_total_price",
                            "Indoge_commission",
                        ]
                    )

                combined_sum = pd.concat([qr_ext_sum, fixed_sum], ignore_index=True)
                if combined_sum.empty:
                    st.info("No employee totals available for selected range.")
                else:
                    combined_sum["employee_id"] = pd.to_numeric(combined_sum.get("employee_id"), errors="coerce").fillna(0).astype(int)
                    combined_sum["employee_code"] = combined_sum.get("employee_code", "").fillna("").astype(str)
                    combined_sum = combined_sum.groupby(
                        ["employee_id", "employee_code", "employee_name", "shop_id", "shop_name"], as_index=False
                    ).agg(
                        transaction_count=("transaction_count", "sum"),
                        total_sale=("total_sale", "sum"),
                        Candelahns_commission=("Candelahns_commission", "sum"),
                        Indoge_total_price=("Indoge_total_price", "sum"),
                        Indoge_commission=("Indoge_commission", "sum"),
                    )
                    # Ensure commission is 2% (or selected rate) of combined total
                    combined_sum["Candelahns_commission"] = combined_sum["total_sale"] * (commission_rate / 100.0)

                    show = combined_sum.sort_values("total_sale", ascending=False).reset_index(drop=True)
                    show.index = range(1, len(show) + 1)
                    show.index.name = "#"

                    show["total_sale"] = show["total_sale"].apply(lambda x: f"{x:,.0f}")
                    show["Candelahns_commission"] = show["Candelahns_commission"].apply(lambda x: f"{x:,.0f}")
                    show["Indoge_total_price"] = show["Indoge_total_price"].apply(lambda x: f"{x:,.0f}")
                    show["Indoge_commission"] = show["Indoge_commission"].apply(lambda x: f"{x:,.0f}")

                    st.dataframe(
                        show[
                            [
                                "employee_id",
                                "employee_code",
                                "employee_name",
                                "shop_name",
                                "transaction_count",
                                "total_sale",
                                "Candelahns_commission",
                                "Indoge_total_price",
                                "Indoge_commission",
                            ]
                        ],
                        width="stretch",
                        hide_index=False,
                        height=360,
                        column_config={
                            "employee_id": st.column_config.Column("Emp ID", width="small"),
                            "employee_code": st.column_config.Column("Field Code", width="small"),
                            "employee_name": st.column_config.Column("Employee", width="medium"),
                            "shop_name": st.column_config.Column("Shop", width="medium"),
                            "transaction_count": st.column_config.Column("Tx Count", width="small"),
                            "total_sale": st.column_config.Column("Total Sales", width="medium"),
                            "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                            "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                            "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
                        },
                    )
            except Exception as e:
                st.warning(f"Employee-wise totals skipped due to error: {e}")
            try:
                st.markdown("#### Employee Match: Non-Blinkco POS vs Indoge (By Employee/Shop)")
                if not df_non_blink.empty:
                    emp_non = df_non_blink.copy()
                    if not include_unassigned:
                        emp_non = emp_non[emp_non["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
                    if employee_search.strip():
                        emp_non = emp_non[emp_non["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)].copy()

                    if not emp_non.empty:
                        non_emp = emp_non.copy()
                        non_emp["employee_id"] = pd.to_numeric(non_emp.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
                        non_emp["shop_id"] = pd.to_numeric(non_emp.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
                        non_emp["total_sale"] = pd.to_numeric(non_emp.get("total_sale", 0), errors="coerce").fillna(0.0)
                        non_emp_sum = (
                            non_emp.groupby(["employee_id", "employee_code", "employee_name", "shop_id", "shop_name"], as_index=False)
                            .agg(non_blink_sales=("total_sale", "sum"), non_blink_tx=("sale_id", "count"))
                        )

                        if not df_merged.empty:
                            ind = df_merged.copy()
                            ind["employee_id"] = pd.to_numeric(ind.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
                            ind["shop_id"] = pd.to_numeric(ind.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
                            ind["Indoge_total_price"] = pd.to_numeric(ind.get("Indoge_total_price", 0), errors="coerce").fillna(0.0)
                            ind_sum = ind.groupby(["employee_id", "shop_id"], as_index=False).agg(
                                indoge_blink_sales=("Indoge_total_price", "sum"),
                                blink_tx=("sale_id", "count"),
                            )
                        else:
                            ind_sum = pd.DataFrame(columns=["employee_id", "shop_id", "indoge_blink_sales", "blink_tx"])

                        cmp_df = non_emp_sum.merge(ind_sum, on=["employee_id", "shop_id"], how="left")
                        cmp_df["indoge_blink_sales"] = pd.to_numeric(cmp_df.get("indoge_blink_sales", 0), errors="coerce").fillna(0.0)
                        cmp_df["blink_tx"] = pd.to_numeric(cmp_df.get("blink_tx", 0), errors="coerce").fillna(0).astype(int)

                        denom = pd.concat([cmp_df["non_blink_sales"], cmp_df["indoge_blink_sales"]], axis=1).max(axis=1).replace(0, pd.NA)
                        numer = pd.concat([cmp_df["non_blink_sales"], cmp_df["indoge_blink_sales"]], axis=1).min(axis=1)
                        cmp_df["match_pct"] = ((numer / denom) * 100.0).astype("Float64").round(2)
                        cmp_df["difference"] = cmp_df["non_blink_sales"] - cmp_df["indoge_blink_sales"]

                        cmp_df = cmp_df.sort_values("non_blink_sales", ascending=False).reset_index(drop=True)
                        cmp_df.index = range(1, len(cmp_df) + 1)
                        cmp_df.index.name = "#"

                        cmp_show = cmp_df.copy()
                        cmp_show["non_blink_sales"] = cmp_show["non_blink_sales"].apply(format_currency)
                        cmp_show["indoge_blink_sales"] = cmp_show["indoge_blink_sales"].apply(format_currency)
                        cmp_show["difference"] = cmp_show["difference"].apply(format_currency)
                        cmp_show["match_pct"] = cmp_show["match_pct"].map(lambda x: "" if pd.isna(x) else f"{float(x):.2f}%")

                        st.dataframe(
                            cmp_show[[
                                "employee_id",
                                "employee_code",
                                "employee_name",
                                "shop_name",
                                "non_blink_tx",
                                "blink_tx",
                                "non_blink_sales",
                                "indoge_blink_sales",
                                "match_pct",
                                "difference",
                            ]],
                            width="stretch",
                            hide_index=False,
                            height=360,
                        )
                        st.download_button(
                            label="Download Employee Match (Non-Blinkco vs Indoge) Excel",
                            data=export_excel(cmp_df.reset_index(drop=True), "Employee Match Non-Blinkco vs Indoge"),
                            file_name=f"employee_match_non_blink_vs_indoge_{start_date_str}_to_{end_date_str}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"{key_prefix}_dl_emp_match_non_blink",
                        )

                    else:
                        st.info("No employee rows available for comparison.")

            except Exception as e:
                st.warning("Employee match tables skipped due to error: " + str(e))
            try:
                if not df_non_no_ref.empty:
                    st.warning(
                        f"{tx_no_ref:,} non-Blinkco sales have no external_ref_id. "
                        "Indoge matching is not possible for them because tblInitialRawBlinkOrder has no employee_id/shop_id to match by."
                    )
                    _render_price_only_match_table(
                        qr_service=qr_service,
                        df_non_no_ref=df_non_no_ref,
                        start_date_str=start_date_str,
                        end_exclusive=end_exclusive,
                        branch_ids=[2],
                        data_mode=data_mode,
                        key_prefix=f"{key_prefix}_khadda_price_only",
                        title="Price-Only Match (Non-Blinkco vs Blink Raw)",
                    )

                    st.markdown("---")
                    st.subheader("Summary: 1 Mar-11 Mar (<=20% Price Diff) vs Post-cutoff External Ref IDs")
                    try:
                        s1, s2, s3 = st.columns(3)
                        s1.metric("1-11 Mar rows <=20% (non-Blinkco)", f"{len(within_20):,}")
                        s2.metric("1-11 Mar sales <=20%", format_currency(float(within_20["total_sale"].sum()) if not within_20.empty else 0.0))
                        post_start = cutoff_dt_str
                        if pd.to_datetime(original_end_date_str) >= pd.to_datetime(post_start):
                            qr_post = qr_service.get_qr_commission_data(post_start, original_end_exclusive, [2], data_mode)
                            if qr_post is not None and not qr_post.empty:
                                qr_post["external_ref_id"] = qr_post["external_ref_id"].astype(str).str.strip().replace("None", "")
                                qr_post = qr_post[qr_post["external_ref_id"] != ""].copy()
                                qr_post["total_sale"] = pd.to_numeric(qr_post.get("total_sale", 0), errors="coerce").fillna(0.0)
                            else:
                                qr_post = pd.DataFrame()
                        else:
                            qr_post = pd.DataFrame()
                        s3.metric(
                            f"Post-cutoff QR sales (with external_ref_id) -> {original_end_date_str}",
                            format_currency(float(qr_post["total_sale"].sum()) if not qr_post.empty else 0.0),
                        )
                    except Exception as e:
                        st.warning(f"Summary computation skipped due to error: {e}")
            except Exception as e:
                st.warning("Price-only/summary skipped due to error: " + str(e))

            # Final detailed transactions table (Khadda)
            if not df_non_with_ref.empty:
                df_non_raw = qr_service.get_blink_raw_orders_for_non_blink_sales(start_date_str, end_exclusive, [2], data_mode)
                non_with_ref = qr_service.process_qr_data(df_non_with_ref, df_non_raw, commission_rate)
            else:
                non_with_ref = pd.DataFrame()
    
            non_no_ref = df_non_no_ref.copy()
            if not non_no_ref.empty:
                non_no_ref["total_sale"] = pd.to_numeric(non_no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_no_ref["Candelahns_commission"] = non_no_ref["total_sale"] * (commission_rate / 100.0)
                non_no_ref["Indoge_total_price"] = pd.NA
                non_no_ref["difference"] = pd.NA
                non_no_ref["Match %"] = pd.NA
                non_no_ref["Matched"] = False
                non_no_ref["BlinkOrderId"] = pd.NA
    
            if not non_with_ref.empty:
                non_with_ref["total_sale"] = pd.to_numeric(non_with_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_with_ref["Indoge_total_price"] = pd.to_numeric(non_with_ref.get("Indoge_total_price", 0), errors="coerce").fillna(0.0)
                non_with_ref["difference"] = pd.to_numeric(non_with_ref.get("difference", 0), errors="coerce").fillna(0.0)
                if "has_blink_order" not in non_with_ref.columns:
                    non_with_ref["has_blink_order"] = False
                else:
                    non_with_ref["has_blink_order"] = non_with_ref["has_blink_order"].fillna(False).astype(bool)
                if "json_parse_ok" not in non_with_ref.columns:
                    non_with_ref["json_parse_ok"] = False
                else:
                    non_with_ref["json_parse_ok"] = non_with_ref["json_parse_ok"].fillna(False).astype(bool)
                if "blink_mismatch_flag" not in non_with_ref.columns:
                    non_with_ref["blink_mismatch_flag"] = False
                else:
                    non_with_ref["blink_mismatch_flag"] = non_with_ref["blink_mismatch_flag"].fillna(False).astype(bool)
    
                cand2 = pd.to_numeric(non_with_ref.get("total_sale", 0), errors="coerce")
                ind2 = pd.to_numeric(non_with_ref.get("Indoge_total_price", 0), errors="coerce")
                both2 = pd.concat([cand2, ind2], axis=1)
                denom2 = both2.max(axis=1).replace(0, pd.NA)
                numer2 = both2.min(axis=1)
                non_with_ref["Match %"] = ((numer2 / denom2) * 100.0).astype("Float64").round(2)
                non_with_ref["Matched"] = non_with_ref["has_blink_order"] & non_with_ref["json_parse_ok"] & (~non_with_ref["blink_mismatch_flag"])
    
                indoge_ok = non_with_ref["has_blink_order"] & non_with_ref["json_parse_ok"]
                for col in ["Indoge_total_price", "difference", "Match %", "BlinkOrderId"]:
                    if col in non_with_ref.columns:
                        non_with_ref[col] = non_with_ref[col].where(indoge_ok, pd.NA)
    
            st.markdown("#### Non-Blinkco Detailed Transactions (Khadda)")
            base_cols = [
                "shop_name",
                "employee_id",
                "employee_code",
                "employee_name",
                "external_ref_type",
                "Matched",
                "Match %",
                "total_sale",
                "Candelahns_commission",
                "Indoge_total_price",
                "difference",
                "BlinkOrderId",
                "external_ref_id",
                "sale_id",
            ]
            for df_ in [non_with_ref, non_no_ref]:
                if df_ is None or df_.empty:
                    continue
                for c in base_cols:
                    if c not in df_.columns:
                        df_[c] = pd.NA
    
            non_all = pd.concat(
                ([non_with_ref[base_cols]] if not non_with_ref.empty else [])
                + ([non_no_ref[base_cols]] if not non_no_ref.empty else []),
                ignore_index=True,
            )
    
            if non_all.empty:
                st.info("No detailed non-Blinkco transactions available.")
            else:
                if employee_search.strip():
                    non_all = non_all[non_all["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)].copy()
                if not include_unassigned:
                    non_all = non_all[non_all["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
    
                non_all["total_sale"] = pd.to_numeric(non_all.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_all["Candelahns_commission"] = pd.to_numeric(non_all.get("Candelahns_commission", 0), errors="coerce").fillna(0.0)
                non_all = non_all.sort_values("total_sale", ascending=False).reset_index(drop=True)
                non_all.index = range(1, len(non_all) + 1)
                non_all.index.name = "#"
    
                non_display = non_all.copy()
                non_display["Candelahns_sale"] = pd.to_numeric(non_display.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_display = non_display.drop(columns=["total_sale"], errors="ignore")
    
                show_cols = [
                    "shop_name",
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "external_ref_type",
                    "Matched",
                    "Match %",
                    "Candelahns_sale",
                    "Candelahns_commission",
                    "Indoge_total_price",
                    "difference",
                    "BlinkOrderId",
                    "external_ref_id",
                    "sale_id",
                ]
                show_cols = [c for c in show_cols if c in non_display.columns]
    
                def _style_tx(df: pd.DataFrame) -> pd.DataFrame:
                    styles = pd.DataFrame("", index=df.index, columns=df.columns)
                    if "difference" in df.columns:
                        diff = pd.to_numeric(df["difference"], errors="coerce").fillna(0.0)
                        styles.loc[diff > 0, "difference"] = "background-color: #d4edda; color: #155724;"
                        styles.loc[diff < 0, "difference"] = "background-color: #f8d7da; color: #721c24;"
                    if "Matched" in df.columns:
                        ok = df["Matched"].astype(bool)
                        styles.loc[ok, "Matched"] = "background-color: #d4edda; color: #155724; font-weight: 600;"
                        styles.loc[~ok, "Matched"] = "background-color: #f8d7da; color: #721c24; font-weight: 600;"
                    return styles
    
                st.dataframe(
                    non_display[show_cols].style.apply(_style_tx, axis=None).format(
                        {
                            "Candelahns_sale": "PKR {:,.0f}",
                            "Candelahns_commission": "PKR {:,.0f}",
                            "Indoge_total_price": "PKR {:,.0f}",
                            "difference": "PKR {:,.0f}",
                            "Match %": "{:.2f}",
                        },
                        na_rep="",
                    ),
                    width="stretch",
                    hide_index=False,
                    height=420,
                )
                st.download_button(
                    label="Download Non-Blinkco Detailed Transactions (Khadda) Excel",
                    data=export_excel(non_all.reset_index(drop=True), "Khadda Non-Blinkco Tx"),
                    file_name=f"khadda_non_blinkco_transactions_{start_date_str}_to_{end_date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"{key_prefix}_dl_khadda_non_blink_tx",
                )
    
        except Exception as e:
            st.warning(f"Khadda non-Blinkco diagnostics skipped due to error: {e}")
            if not df_non_with_ref.empty:
                df_non_raw = qr_service.get_blink_raw_orders_for_non_blink_sales(start_date_str, end_exclusive, [2], data_mode)
                non_with_ref = qr_service.process_qr_data(df_non_with_ref, df_non_raw, commission_rate)
            else:
                non_with_ref = pd.DataFrame()

            non_no_ref = df_non_no_ref.copy()
            if not non_no_ref.empty:
                non_no_ref["total_sale"] = pd.to_numeric(non_no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_no_ref["Candelahns_commission"] = non_no_ref["total_sale"] * (commission_rate / 100.0)
                non_no_ref["Indoge_total_price"] = pd.NA
                non_no_ref["difference"] = pd.NA
                non_no_ref["Match %"] = pd.NA
                non_no_ref["Matched"] = False
                non_no_ref["BlinkOrderId"] = pd.NA

            if not non_with_ref.empty:
                non_with_ref["total_sale"] = pd.to_numeric(non_with_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                non_with_ref["Indoge_total_price"] = pd.to_numeric(non_with_ref.get("Indoge_total_price", 0), errors="coerce").fillna(0.0)
                non_with_ref["difference"] = pd.to_numeric(non_with_ref.get("difference", 0), errors="coerce").fillna(0.0)
                if "has_blink_order" not in non_with_ref.columns:
                    non_with_ref["has_blink_order"] = False
                else:
                    non_with_ref["has_blink_order"] = non_with_ref["has_blink_order"].fillna(False).astype(bool)
                if "json_parse_ok" not in non_with_ref.columns:
                    non_with_ref["json_parse_ok"] = False
                else:
                    non_with_ref["json_parse_ok"] = non_with_ref["json_parse_ok"].fillna(False).astype(bool)
                if "blink_mismatch_flag" not in non_with_ref.columns:
                    non_with_ref["blink_mismatch_flag"] = False
                else:
                    non_with_ref["blink_mismatch_flag"] = non_with_ref["blink_mismatch_flag"].fillna(False).astype(bool)

                cand2 = pd.to_numeric(non_with_ref.get("total_sale", 0), errors="coerce")
                ind2 = pd.to_numeric(non_with_ref.get("Indoge_total_price", 0), errors="coerce")
                both2 = pd.concat([cand2, ind2], axis=1)
                denom2 = both2.max(axis=1).replace(0, pd.NA)
                numer2 = both2.min(axis=1)
                non_with_ref["Match %"] = ((numer2 / denom2) * 100.0).astype("Float64").round(2)
                non_with_ref["Matched"] = non_with_ref["has_blink_order"] & non_with_ref["json_parse_ok"] & (~non_with_ref["blink_mismatch_flag"])

                indoge_ok = non_with_ref["has_blink_order"] & non_with_ref["json_parse_ok"]
                for col in ["Indoge_total_price", "difference", "Match %", "BlinkOrderId"]:
                    if col in non_with_ref.columns:
                        non_with_ref[col] = non_with_ref[col].where(indoge_ok, pd.NA)

        except Exception as e:
            st.warning(f"Khadda non-Blinkco diagnostics skipped due to error: {e}")
            base_cols = [
                "shop_name",
                "employee_id",
                "employee_code",
                "employee_name",
                "external_ref_type",
                "Matched",
                "Match %",
                "total_sale",
                "Candelahns_commission",
                "Indoge_total_price",
                "difference",
                "BlinkOrderId",
                "external_ref_id",
                "sale_id",
            ]
            for df_ in [non_with_ref, non_no_ref]:
                if df_ is None or df_.empty:
                    continue
                for c in base_cols:
                    if c not in df_.columns:
                        df_[c] = pd.NA
    
            non_all = pd.concat(
                ([non_with_ref[base_cols]] if not non_with_ref.empty else [])
                + ([non_no_ref[base_cols]] if not non_no_ref.empty else []),
                ignore_index=True,
            )
    
            if employee_search.strip():
                non_all = non_all[non_all["employee_name"].astype(str).str.contains(employee_search.strip(), case=False, na=False)].copy()
            if not include_unassigned:
                non_all = non_all[non_all["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
    
            non_all["total_sale"] = pd.to_numeric(non_all.get("total_sale", 0), errors="coerce").fillna(0.0)
            non_all["Candelahns_commission"] = pd.to_numeric(non_all.get("Candelahns_commission", 0), errors="coerce").fillna(0.0)
            non_all = non_all.sort_values("total_sale", ascending=False).reset_index(drop=True)
            non_all.index = range(1, len(non_all) + 1)
            non_all.index.name = "#"
    
            non_display = non_all.copy()
            non_display["Candelahns_sale"] = pd.to_numeric(non_display.get("total_sale", 0), errors="coerce").fillna(0.0)
            non_display = non_display.drop(columns=["total_sale"], errors="ignore")
    
            show_cols = [
                "shop_name",
                "employee_id",
                "employee_code",
                "employee_name",
                "external_ref_type",
                "Matched",
                "Match %",
                "Candelahns_sale",
                "Candelahns_commission",
                "Indoge_total_price",
                "difference",
                "BlinkOrderId",
                "external_ref_id",
                "sale_id",
            ]
            show_cols = [c for c in show_cols if c in non_display.columns]
    
            def _style_tx(df: pd.DataFrame) -> pd.DataFrame:
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                if "difference" in df.columns:
                    diff = pd.to_numeric(df["difference"], errors="coerce").fillna(0.0)
                    styles.loc[diff > 0, "difference"] = "background-color: #d4edda; color: #155724;"
                    styles.loc[diff < 0, "difference"] = "background-color: #f8d7da; color: #721c24;"
                if "Matched" in df.columns:
                    ok = df["Matched"].astype(bool)
                    styles.loc[ok, "Matched"] = "background-color: #d4edda; color: #155724; font-weight: 600;"
                    styles.loc[~ok, "Matched"] = "background-color: #f8d7da; color: #721c24; font-weight: 600;"
                return styles
    
            st.dataframe(
                non_display[show_cols].style.apply(_style_tx, axis=None).format(
                    {
                        "Candelahns_sale": "PKR {:,.0f}",
                        "Candelahns_commission": "PKR {:,.0f}",
                        "Indoge_total_price": "PKR {:,.0f}",
                        "difference": "PKR {:,.0f}",
                        "Match %": "{:.2f}",
                    },
                    na_rep="",
                ),
                width="stretch",
                hide_index=False,
                height=420,
            )
            st.download_button(
                label="Download Non-Blinkco Detailed Transactions (Khadda) Excel",
                data=export_excel(non_all.reset_index(drop=True), "Khadda Non-Blinkco Tx"),
                file_name=f"khadda_non_blinkco_transactions_{start_date_str}_to_{end_date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}_dl_khadda_non_blink_tx",
            )
    
    
