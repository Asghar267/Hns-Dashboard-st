"""
Pivot Tables Tab
Interactive pivots for branch/category/date analysis using current filters.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.database import get_cached_daily_sales_by_branch, get_cached_line_items


@st.cache_data(ttl=300, show_spinner=False)
def _cached_line_items(start_date: str, end_date: str, branches: tuple[int, ...], mode: str) -> pd.DataFrame:
    return get_cached_line_items(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_daily_sales(start_date: str, end_date: str, branches: tuple[int, ...], mode: str) -> pd.DataFrame:
    return get_cached_daily_sales_by_branch(start_date, end_date, list(branches), mode)


class PivotTablesTab:
    def __init__(self, start_date: str, end_date: str, selected_branches: list[int], data_mode: str, df_line_item: pd.DataFrame | None):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.df_line_item = df_line_item

    def render(self) -> None:
        st.header("Pivot Tables")
        st.caption("Interactive pivots for branch/category/date analysis using current filters.")

        pivot_type = st.selectbox(
            "Pivot Type",
            options=["Branch x Category", "Branch x Day", "Month x Branch"],
            index=0,
            key="pivot_type",
        )
        metric_choice = st.selectbox("Metric", options=["Sales", "Quantity"], index=0, key="pivot_metric")

        signature = (
            pivot_type,
            metric_choice,
            tuple(sorted(self.selected_branches)),
            self.start_date,
            self.end_date,
            self.data_mode,
        )
        if st.session_state.get("pivot_sig") != signature:
            st.session_state["pivot_sig"] = signature
            st.session_state["pivot_loaded"] = False

        if not st.session_state.get("pivot_loaded", False):
            if st.button("Load Pivot", key="pivot_load_btn"):
                st.session_state["pivot_loaded"] = True
            else:
                st.caption("Set your filters and click **Load Pivot** to render.")
                return

        max_cols = st.slider("Columns per page", min_value=6, max_value=20, value=12, step=2, key="pivot_cols_page")

        if pivot_type == "Branch x Category":
            if self.df_line_item is None:
                self.df_line_item = _cached_line_items(
                    self.start_date,
                    self.end_date,
                    tuple(sorted(self.selected_branches)),
                    self.data_mode,
                )
            if self.df_line_item is None or self.df_line_item.empty:
                st.info("No line-item data available for this pivot.")
                return
            metric_col = "total_line_value_incl_tax" if metric_choice == "Sales" else "total_qty"
            value_name = "Total Sales" if metric_choice == "Sales" else "Total Qty"
            piv = pd.pivot_table(
                self.df_line_item,
                index="shop_name",
                columns="product",
                values=metric_col,
                aggfunc="sum",
                fill_value=0,
            )
            piv = piv.sort_index()
            piv["Grand Total"] = piv.sum(axis=1)
            piv.loc["Grand Total"] = piv.sum(axis=0)
            st.markdown(f"#### {value_name}: Branch x Category")
            display = piv.reset_index().rename(columns={"shop_name": "Branch"})
            self._render_pivot_chunked(display, max_cols=max_cols, key="pivot_branch_category")
            return

        if pivot_type == "Branch x Day":
            df_daily = _cached_daily_sales(
                self.start_date,
                self.end_date,
                tuple(sorted(self.selected_branches)),
                self.data_mode,
            )
            if df_daily is None or df_daily.empty:
                st.info("No daily branch data available for this pivot.")
                return
            if metric_choice != "Sales":
                st.info("Quantity is best viewed in Branch x Category pivot.")
                return

            working = df_daily.copy()
            working["day_str"] = pd.to_datetime(working["day"]).dt.strftime("%Y-%m-%d")
            piv = pd.pivot_table(
                working,
                index="shop_name",
                columns="day_str",
                values="total_Nt_amount",
                aggfunc="sum",
                fill_value=0,
            )
            piv = piv.sort_index()
            piv["Grand Total"] = piv.sum(axis=1)
            piv.loc["Grand Total"] = piv.sum(axis=0)
            st.markdown("#### Total Sales: Branch x Day")
            display = piv.reset_index().rename(columns={"shop_name": "Branch"})
            self._render_pivot_chunked(display, max_cols=max_cols, key="pivot_branch_day")
            return

        # Month x Branch (based on daily, grouped to month)
        df_daily = _cached_daily_sales(
            self.start_date,
            self.end_date,
            tuple(sorted(self.selected_branches)),
            self.data_mode,
        )
        if df_daily is None or df_daily.empty:
            st.info("No data available for month x branch pivot.")
            return
        if metric_choice != "Sales":
            st.info("Quantity is best viewed in Branch x Category pivot.")
            return

        working = df_daily.copy()
        working["month"] = pd.to_datetime(working["day"]).dt.to_period("M").astype(str)
        piv = pd.pivot_table(
            working,
            index="month",
            columns="shop_name",
            values="total_Nt_amount",
            aggfunc="sum",
            fill_value=0,
        )
        piv = piv.sort_index()
        piv["Grand Total"] = piv.sum(axis=1)
        piv.loc["Grand Total"] = piv.sum(axis=0)
        st.markdown("#### Total Sales: Month x Branch")
        display = piv.reset_index()
        self._render_pivot_chunked(display, max_cols=max_cols, key="pivot_month_branch")

    def _render_pivot_chunked(self, df: pd.DataFrame, max_cols: int = 12, key: str = "pivot") -> None:
        if df is None or df.empty:
            st.info("No data available for this pivot.")
            return
        cols = list(df.columns)
        if len(cols) <= max_cols:
            st.dataframe(df, width="stretch", hide_index=True, height=520)
            return

        id_col = cols[0]
        data_cols = cols[1:]
        chunk_size = max(1, max_cols - 1)
        total_pages = (len(data_cols) + chunk_size - 1) // chunk_size
        page = st.selectbox(
            "Column Page",
            options=list(range(1, total_pages + 1)),
            index=0,
            key=f"{key}_col_page",
        )
        start = (page - 1) * chunk_size
        subset_cols = [id_col] + data_cols[start:start + chunk_size]
        st.caption(f"Showing columns {start + 1}–{min(start + chunk_size, len(data_cols))} of {len(data_cols)}")
        st.dataframe(df[subset_cols], width="stretch", hide_index=True, height=520)
