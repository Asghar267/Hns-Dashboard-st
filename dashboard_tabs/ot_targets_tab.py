"""
OT Targets Tab
Shows order taker sales vs target for a selected branch.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.database import build_filter_clause, get_cached_ot_data, get_cached_targets, placeholders, pool
from modules.utils import export_excel, format_currency, format_percentage


class OTTargetsTab:
    def __init__(
        self,
        target_year: int,
        target_month: int,
        start_date: str,
        end_date: str,
        selected_branches: list[int],
        data_mode: str,
    ):
        self.target_year = int(target_year)
        self.target_month = int(target_month)
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

    def render(self) -> None:
        st.header("Order Taker Targets")

        # Branch list with names
        try:
            df_branch = pd.read_sql(
                f"SELECT shop_id, shop_name FROM tblDefShops WHERE shop_id IN ({', '.join(['?']*len(self.selected_branches))})",
                pool.get_connection("candelahns"),
                params=self.selected_branches,
            )
        except Exception:
            df_branch = pd.DataFrame(columns=["shop_id", "shop_name"])

        if df_branch.empty:
            st.info("No branch data available.")
            return

        branch_names = df_branch["shop_name"].astype(str).tolist()
        selected_branch = st.selectbox("Select Branch", branch_names, key="ot_targets_branch")
        shop_id = int(df_branch[df_branch["shop_name"] == selected_branch]["shop_id"].iloc[0])

        st.info(f"Showing OT performance for {selected_branch}")

        hide_zero_sales = st.checkbox("Hide employees with 0 current sales", value=False, key="ot_targets_hide_zero_sales")
        hide_zero_target = st.checkbox("Hide employees with 0 target", value=False, key="ot_targets_hide_zero_target")

        df_ot = get_cached_ot_data(
            self.start_date,
            self.end_date,
            [shop_id],
            self.data_mode,
        )

        # Targets for the month
        _, _, ot_targets, _ = get_cached_targets(self.target_year, self.target_month)
        if ot_targets is None or ot_targets.empty:
            st.warning("No OT targets data available.")
            if df_ot is None or df_ot.empty:
                st.info("No OT sales data available for this branch.")
                return
            df_ot_branch = df_ot[df_ot["shop_id"] == shop_id].copy()
            cols = [c for c in ["employee_code", "employee_name", "total_sale"] if c in df_ot_branch.columns]
            if not cols:
                cols = ["employee_name", "total_sale"]
            display_ot_notarget = df_ot_branch[cols].copy()
            display_ot_notarget["total_sale"] = display_ot_notarget["total_sale"].apply(format_currency)
            st.dataframe(display_ot_notarget, width="stretch", hide_index=True, height=420)
            return

        df_ot_targets_branch = ot_targets[ot_targets["shop_id"] == shop_id].copy()
        df_ot_branch = df_ot[df_ot["shop_id"] == shop_id].copy()

        if df_ot_branch.empty:
            st.info("No OT sales data available for this branch.")
            return

        df_perf = df_ot_branch.merge(
            df_ot_targets_branch,
            on=["shop_id", "employee_id"],
            how="left",
        ).fillna({"target_amount": 0})

        if "employee_name" in df_perf.columns:
            df_perf["employee_name"] = df_perf["employee_name"].fillna(df_perf["employee_id"].astype(str).apply(lambda x: f"ID: {x}"))
        else:
            df_perf["employee_name"] = df_perf["employee_id"].astype(str).apply(lambda x: f"ID: {x}")

        df_perf["target_amount"] = pd.to_numeric(df_perf["target_amount"], errors="coerce").fillna(0.0)
        df_perf["total_sale"] = pd.to_numeric(df_perf["total_sale"], errors="coerce").fillna(0.0)

        if hide_zero_sales:
            df_perf = df_perf[df_perf["total_sale"] > 0].copy()
        if hide_zero_target:
            df_perf = df_perf[df_perf["target_amount"] > 0].copy()

        # Daily sales + target calculations (yesterday + MTD)
        employee_ids = df_perf["employee_id"].dropna().astype(int).unique().tolist()
        days_in_month = monthrange(self.target_year, self.target_month)[1]
        month_start = date(self.target_year, self.target_month, 1)
        month_end = date(self.target_year, self.target_month, days_in_month)
        ref_date = date.today()
        yesterday_date = ref_date - timedelta(days=1)

        remaining_days = max((month_end - ref_date).days, 0)

        if employee_ids:
            conn = pool.get_connection("candelahns")
            filter_clause, filter_params = build_filter_clause(self.data_mode)

            def fetch_ot_sales(start_d: date, end_d: date) -> pd.DataFrame:
                end_next = end_d + timedelta(days=1)
                query = f"""
                SELECT s.employee_id, SUM(s.Nt_amount) AS total_sale
                FROM tblSales s
                WHERE s.sale_date >= ? AND s.sale_date < ?
                  AND s.shop_id = ?
                  AND s.employee_id IN ({placeholders(len(employee_ids))})
                {filter_clause}
                GROUP BY s.employee_id
                """
                params = [start_d.strftime("%Y-%m-%d"), end_next.strftime("%Y-%m-%d"), shop_id] + employee_ids + filter_params
                df = pd.read_sql(query, conn, params=params)
                if "employee_id" in df.columns:
                    df["employee_id"] = pd.to_numeric(df["employee_id"], errors="coerce").fillna(0).astype("int64")
                return df

            df_yest = fetch_ot_sales(yesterday_date, yesterday_date).rename(columns={"total_sale": "yesterday_sale"})
            df_mtd = fetch_ot_sales(month_start, ref_date).rename(columns={"total_sale": "mtd_sale"})

            df_perf = df_perf.merge(df_yest, on="employee_id", how="left")
            df_perf = df_perf.merge(df_mtd, on="employee_id", how="left")
        else:
            df_perf["yesterday_sale"] = 0
            df_perf["mtd_sale"] = 0

        df_perf["yesterday_sale"] = df_perf["yesterday_sale"].fillna(0)
        df_perf["mtd_sale"] = df_perf["mtd_sale"].fillna(0)

        # Build OT table
        src_cols = [c for c in ["employee_code", "employee_name", "target_amount", "total_sale", "yesterday_sale", "mtd_sale"] if c in df_perf.columns]
        ot_table = df_perf[src_cols].copy()
        rename_map = {
            "employee_code": "Field Code",
            "employee_name": "OT Name",
            "target_amount": "Target",
            "total_sale": "Current Sale",
            "yesterday_sale": "Yesterday Achieved",
            "mtd_sale": "MTD Sale",
        }
        ot_table = ot_table.rename(columns=rename_map)

        ot_table["Days in Month"] = days_in_month
        ot_table["Per-Day Target"] = ot_table["Target"] / days_in_month if days_in_month > 0 else 0
        ot_table["Today Target"] = ot_table["Per-Day Target"]
        ot_table["Remaining Target"] = ot_table["Target"] - ot_table["MTD Sale"]
        ot_table["Remaining Days"] = remaining_days
        ot_table["Next Day Target"] = ot_table.apply(
            lambda row: (row["Remaining Target"] / remaining_days) if remaining_days > 0 else 0,
            axis=1,
        )

        ot_table["Remaining"] = ot_table["Target"] - ot_table["Current Sale"]
        ot_table["Achievement %"] = ot_table.apply(
            lambda row: (row["Current Sale"] / row["Target"] * 100) if row["Target"] > 0 else 0,
            axis=1,
        )

        total_ot_sales = ot_table["Current Sale"].sum()
        total_ot_target = ot_table["Target"].sum()
        num_ots = len(ot_table)
        avg_achievement = ot_table["Achievement %"].mean() if len(ot_table) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total OT Sales", format_currency(total_ot_sales))
        col2.metric("Total Target", format_currency(total_ot_target))
        col3.metric("Number of OTs", num_ots)
        col4.metric("Avg Achievement", format_percentage(avg_achievement))

        st.markdown("---")

        display_ot = ot_table.copy()
        display_ot["Target"] = display_ot["Target"].apply(format_currency)
        display_ot["Current Sale"] = display_ot["Current Sale"].apply(format_currency)
        display_ot["MTD Sale"] = display_ot["MTD Sale"].apply(format_currency)
        display_ot["Per-Day Target"] = display_ot["Per-Day Target"].apply(format_currency)
        display_ot["Yesterday Achieved"] = display_ot["Yesterday Achieved"].apply(format_currency)
        display_ot["Today Target"] = display_ot["Today Target"].apply(format_currency)
        display_ot["Remaining Target"] = display_ot["Remaining Target"].apply(format_currency)
        display_ot["Next Day Target"] = display_ot["Next Day Target"].apply(format_currency)
        display_ot["Remaining"] = display_ot["Remaining"].apply(format_currency)
        display_ot["Achievement %"] = display_ot["Achievement %"].apply(lambda x: f"{x:.1f}%")

        desired_cols = [
            "Field Code",
            "OT Name",
            "Target",
            "Per-Day Target",
            "Yesterday Achieved",
            "Today Target",
            "MTD Sale",
            "Remaining Target",
            "Remaining Days",
            "Next Day Target",
            "Current Sale",
            "Remaining",
            "Achievement %",
        ]
        st.dataframe(
            display_ot[[c for c in desired_cols if c in display_ot.columns]],
            width="stretch",
            hide_index=True,
            height=400,
        )

        st.markdown("---")
        st.subheader("Top 10 OT Performance")

        top_10_ot = ot_table.nlargest(10, "Current Sale")
        fig = px.bar(
            top_10_ot,
            x="Current Sale",
            y="OT Name",
            orientation="h",
            title="Top 10 Order Takers by Sales",
            labels={"Current Sale": "Sales ()", "OT Name": "Order Taker"},
            color="Achievement %",
            color_continuous_scale="RdYlGn",
            text="Current Sale",
        )
        fig.update_traces(
            texttemplate=" %{text:,.0f}",
            textposition="inside",
            textfont_size=11,
            textfont_color="white",
            insidetextanchor="middle",
        )
        fig.update_layout(height=500, xaxis_title="Sales ()", yaxis_title="Order Taker")
        st.plotly_chart(fig, width="stretch")

        st.download_button(
            "Download OT Targets Excel",
            export_excel(df_perf.sort_values("total_sale", ascending=False), sheet_name="OT Targets"),
            f"ot_targets_{selected_branch}_{self.target_year}_{self.target_month}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

