"""
Database Health Diagnostics Tab
Read-only diagnostics for data quality and operational monitoring.
"""

from __future__ import annotations

from io import BytesIO
from typing import List, Optional

import pandas as pd
import streamlit as st

from modules.database import (
    get_cached_branch_days_since_last_sale,
    get_cached_database_orphan_summary,
    get_cached_database_range_quality,
    get_cached_filter_impact_summary,
    get_cached_stale_branches_all,
)
from modules.utils import format_currency
from modules.responsive import clamp_dataframe_height, get_responsive_context, responsive_columns


class DatabaseHealthDiagnosticsTab:
    """Render database health diagnostics."""

    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.responsive = get_responsive_context()

    def render(self):
        st.header("Database Health Diagnostics")
        st.caption(
            f"Range: {self.start_date} to {self.end_date} | "
            f"Branches: {', '.join(map(str, self.selected_branches))} | "
            f"Mode: {self.data_mode}"
        )

        self._render_excel_export()
        st.markdown("---")
        self._render_key_metrics()
        st.markdown("---")
        self._render_branch_recency()
        st.markdown("---")
        self._render_orphans()
        st.markdown("---")
        self._render_blanks_and_quality()
        st.markdown("---")
        self._render_filter_impact()

    def _render_key_metrics(self):
        df_selected = get_cached_branch_days_since_last_sale(self.selected_branches)
        df_orphans = get_cached_database_orphan_summary()
        df_quality = get_cached_database_range_quality(self.start_date, self.end_date, self.selected_branches)

        stale_selected = 0
        max_days = 0
        if df_selected is not None and not df_selected.empty:
            stale_selected = int((df_selected["days_since_last_sale"] > 1).sum())
            max_days = int(pd.to_numeric(df_selected["days_since_last_sale"], errors="coerce").fillna(0).max())

        lineitem_orphans = 0
        sales_orphans = 0
        if df_orphans is not None and not df_orphans.empty:
            lineitem_orphans = int(pd.to_numeric(df_orphans.iloc[0].get("lineitem_without_sale", 0), errors="coerce") or 0)
            sales_orphans = int(pd.to_numeric(df_orphans.iloc[0].get("sales_without_lineitems", 0), errors="coerce") or 0)

        blank_rows = 0
        blank_pct = 0.0
        if df_quality is not None and not df_quality.empty:
            rows_total = float(pd.to_numeric(df_quality.iloc[0].get("rows_total", 0), errors="coerce") or 0.0)
            blank_rows = int(pd.to_numeric(df_quality.iloc[0].get("cust_name_blank", 0), errors="coerce") or 0)
            blank_pct = (blank_rows / rows_total * 100.0) if rows_total > 0 else 0.0

        cols = responsive_columns(self.responsive, desktop=4, tablet=2, phone=1)
        with cols[0]:
            st.metric("Max Days Since Sale", f"{max_days}")
        with cols[1 % len(cols)]:
            st.metric("Stale Selected Branches", f"{stale_selected}")
        with cols[2 % len(cols)]:
            st.metric("Lineitem Orphans", f"{lineitem_orphans}")
        with cols[3 % len(cols)]:
            st.metric("Blank Cust_name Rows", f"{blank_rows:,} ({blank_pct:.1f}%)")

        if sales_orphans > 0:
            st.warning(f"Sales without lineitems detected: {sales_orphans}")

    def _render_branch_recency(self):
        st.subheader("Branch Recency")
        st.caption("Days since last sale by branch.")

        df_all = get_cached_stale_branches_all()
        if df_all is None or df_all.empty:
            st.info("No branch recency data found.")
            return

        df_show = df_all.copy()
        df_show["last_sale_date"] = pd.to_datetime(df_show["last_sale_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df_show["status"] = df_show["days_since_last_sale"].apply(self._recency_status_label)
        styler = df_show[["shop_id", "shop_name", "last_sale_date", "days_since_last_sale", "status"]].style.apply(
            lambda row: [self._recency_status_style(row["days_since_last_sale"]) if col == "status" else "" for col in row.index],
            axis=1,
        )
        self._render_table(styler, height=320)

    def _render_orphans(self):
        st.subheader("Orphan Diagnostics")
        st.caption("Relationship checks between sales and line items.")

        df_orphans = get_cached_database_orphan_summary()
        if df_orphans is None or df_orphans.empty:
            st.info("Orphan diagnostics are unavailable.")
            return
        self._render_table(df_orphans, height=120)

    def _render_blanks_and_quality(self):
        st.subheader("Range Quality & Blanks")
        st.caption("Core quality checks for selected range and branches.")

        df_quality = get_cached_database_range_quality(self.start_date, self.end_date, self.selected_branches)
        if df_quality is None or df_quality.empty:
            st.info("Range quality diagnostics are unavailable.")
            return

        self._render_table(df_quality, height=140)

    def _render_filter_impact(self):
        st.subheader("Filter Impact")
        st.caption("Filtered vs unfiltered impact for the selected range.")

        df = get_cached_filter_impact_summary(self.start_date, self.end_date, self.selected_branches)
        if df is None or df.empty:
            st.info("Filter impact diagnostics are unavailable.")
            return

        row = df.iloc[0].to_dict()
        cols = responsive_columns(self.responsive, desktop=4, tablet=2, phone=1)
        with cols[0]:
            st.metric("Orders (Unfiltered)", f"{int(row.get('orders_unfiltered', 0)):,}")
        with cols[1 % len(cols)]:
            st.metric("Orders (Filtered)", f"{int(row.get('orders_filtered', 0)):,}")
        with cols[2 % len(cols)]:
            st.metric("Orders Excluded", f"{int(row.get('orders_excluded_est', 0)):,}")
        with cols[3 % len(cols)]:
            st.metric("Sales Excluded", format_currency(float(row.get("sales_excluded_est", 0.0))))

        self._render_table(df, height=140)

    def _render_excel_export(self):
        """Export key diagnostics in a single Excel workbook."""
        df_recency = get_cached_stale_branches_all()
        df_orphans = get_cached_database_orphan_summary()
        df_quality = get_cached_database_range_quality(self.start_date, self.end_date, self.selected_branches)
        df_filter = get_cached_filter_impact_summary(self.start_date, self.end_date, self.selected_branches)

        if df_recency is None or df_recency.empty:
            return

        recency_export = df_recency.copy()
        recency_export["last_sale_date"] = pd.to_datetime(recency_export["last_sale_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        recency_export["status"] = recency_export["days_since_last_sale"].apply(self._recency_status_label)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            recency_export.to_excel(writer, sheet_name="Branch Recency", index=False)
            if df_orphans is not None and not df_orphans.empty:
                df_orphans.to_excel(writer, sheet_name="Orphans", index=False)
            if df_quality is not None and not df_quality.empty:
                df_quality.to_excel(writer, sheet_name="Range Quality", index=False)
            if df_filter is not None and not df_filter.empty:
                df_filter.to_excel(writer, sheet_name="Filter Impact", index=False)

        st.download_button(
            "Download Diagnostics Excel",
            data=output.getvalue(),
            file_name=f"database_health_{self.start_date}_to_{self.end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    @staticmethod
    def _recency_status_label(days_since_last_sale: int) -> str:
        days = int(pd.to_numeric(days_since_last_sale, errors="coerce") or 0)
        if days <= 1:
            return "Fresh"
        if days <= 7:
            return "Warning"
        return "Stale"

    @staticmethod
    def _recency_status_style(days_since_last_sale: int) -> str:
        days = int(pd.to_numeric(days_since_last_sale, errors="coerce") or 0)
        if days <= 1:
            return "background-color: #d1fae5; color: #065f46; font-weight: 600;"
        if days <= 7:
            return "background-color: #fef3c7; color: #92400e; font-weight: 600;"
        return "background-color: #fee2e2; color: #991b1b; font-weight: 600;"

    def _render_table(self, data, width: str = "stretch", height: Optional[int] = None):
        kwargs = {"width": width, "hide_index": True}
        kwargs["height"] = clamp_dataframe_height(
            self.responsive,
            desktop=height,
            tablet=max(220, int((height or 420) * 0.82)),
            phone=max(200, int((height or 420) * 0.68)),
            kind="default" if height is None else "compact",
        )
        st.dataframe(data, **kwargs)
