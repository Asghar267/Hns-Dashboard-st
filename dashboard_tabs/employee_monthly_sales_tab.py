"""
Employee Monthly Sales Tab
Monthly employee sales without blocked-name/comment filters.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.database import get_cached_employee_monthly_sales, get_cached_employee_monthly_sales_multi
from modules.utils import export_excel, format_currency, format_number


class EmployeeMonthlySalesTab:
    def __init__(self, selected_branches: list[int]) -> None:
        self.selected_branches = selected_branches

    def render(self) -> None:
        st.header("Employee Monthly Sales")
        st.caption("Monthly employee sales. This tab ignores blocked-name/comment filtering and uses its own month selection.")

        current_now = datetime.now()
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Year", min_value=2020, max_value=2100, value=current_now.year, step=1, key="emp_monthly_year")
        with col2:
            months = st.multiselect(
                "Months",
                options=list(range(1, 13)),
                default=[current_now.month],
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                key="emp_monthly_months",
            )

        months_selected = tuple(int(m) for m in months)
        if not months_selected:
            st.info("Select at least one month to view sales.")
            return
        if len(months_selected) == 1:
            df = get_cached_employee_monthly_sales(int(year), int(months_selected[0]), self.selected_branches)
            if not df.empty:
                df = df.assign(sale_year=int(year), sale_month=int(months_selected[0]))
        else:
            df = get_cached_employee_monthly_sales_multi(int(year), tuple(months_selected), self.selected_branches)
        if df is None or df.empty:
            st.info("No employee monthly sales found for the selected month(s).")
            return

        total_sale = float(df["total_sale"].sum()) if "total_sale" in df.columns else 0.0
        total_tx = int(df["total_transactions"].sum()) if "total_transactions" in df.columns else 0
        active_employees = int(df["employee_id"].nunique()) if "employee_id" in df.columns else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Sales", format_number(total_sale))
        m2.metric("Transactions", f"{total_tx:,}")
        m3.metric("Active Employees", f"{active_employees:,}")

        # Roll up per-employee per-month totals (source df can have multiple rows per employee due to shop breakdown).
        emp_month = (
            df.groupby(["sale_year", "sale_month", "employee_id", "employee_code", "employee_name"], as_index=False)
            .agg(
                total_transactions=("total_transactions", "sum"),
                total_sale=("total_sale", "sum"),
                qr_sale=("qr_sale", "sum"),
                normal_sale=("normal_sale", "sum"),
                shops=("shop_name", "nunique"),
            )
            .sort_values(["sale_year", "sale_month", "total_sale"], ascending=[True, True, False])
        )
        emp_month["month_label"] = emp_month.apply(
            lambda r: f"{int(r['sale_year'])}-{datetime(2000, int(r['sale_month']), 1).strftime('%b')}", axis=1
        )
        emp_month["employee_label"] = emp_month.apply(
            lambda r: (f"{str(r['employee_code']).strip()} - {str(r['employee_name']).strip()}").strip(" -")
            if str(r["employee_code"]).strip()
            else f"{int(r['employee_id'])} - {str(r['employee_name']).strip()}",
            axis=1,
        )

        st.markdown("---")
        left, right = st.columns(2)

        with left:
            st.subheader("Month-wise Totals")
            month_summary = (
                df.groupby(["sale_year", "sale_month"], as_index=False)
                .agg(
                    total_transactions=("total_transactions", "sum"),
                    total_sale=("total_sale", "sum"),
                )
                .sort_values(["sale_year", "sale_month"], ascending=[True, True])
            )
            month_show = month_summary.copy()
            month_show["month_name"] = month_show["sale_month"].apply(lambda m: datetime(2000, int(m), 1).strftime("%B"))
            month_show = month_show[["sale_year", "month_name", "total_transactions", "total_sale"]].rename(
                columns={"sale_year": "year", "month_name": "month"}
            )
            month_show["total_sale"] = month_show["total_sale"].apply(format_currency)
            st.dataframe(month_show, width="stretch", hide_index=True, height=240)

            st.subheader("Branch-wise Totals")
            branch_summary = (
                df.groupby(["shop_name"], as_index=False)
                .agg(
                    active_employees=("employee_id", "nunique"),
                    total_transactions=("total_transactions", "sum"),
                    total_sale=("total_sale", "sum"),
                )
                .sort_values("total_sale", ascending=False)
            )
            branch_show = branch_summary.copy()
            branch_show["total_sale"] = branch_show["total_sale"].apply(format_currency)
            st.dataframe(branch_show, width="stretch", hide_index=True, height=280)

        with right:
            st.subheader("Top 10 Employees")
            top_employees = (
                df.groupby(["employee_id", "employee_code", "employee_name"], as_index=False)
                .agg(
                    shops=("shop_name", "nunique"),
                    total_transactions=("total_transactions", "sum"),
                    total_sale=("total_sale", "sum"),
                )
                .sort_values(["total_sale", "employee_name"], ascending=[False, True])
                .head(10)
                .copy()
            )
            top_show = top_employees.copy()
            top_show["total_sale"] = pd.to_numeric(top_show["total_sale"], errors="coerce").fillna(0.0).apply(format_currency)
            st.dataframe(top_show, width="stretch", hide_index=True, height=280)

        st.markdown("---")
        st.subheader("Employee-wise Monthly Trend")
        c1, c2 = st.columns(2)
        with c1:
            chart_type = st.radio("Chart Type", options=["Line", "Bar"], horizontal=True, key="emp_monthly_chart_type")
        with c2:
            top_n = st.slider("Employees to Plot", min_value=3, max_value=30, value=10, step=1, key="emp_monthly_top_n")

        top_employee_labels = (
            emp_month.groupby(["employee_label"], as_index=False)
            .agg(total_sale=("total_sale", "sum"))
            .sort_values("total_sale", ascending=False)
            .head(int(top_n))["employee_label"]
            .tolist()
        )
        trend_src = emp_month[emp_month["employee_label"].isin(top_employee_labels)].copy()
        trend = (
            trend_src.pivot_table(index=["sale_year", "sale_month", "month_label"], columns="employee_label", values="total_sale", aggfunc="sum")
            .sort_index(level=[0, 1])
            .fillna(0.0)
        )
        trend.index = trend.index.get_level_values("month_label")
        if chart_type == "Bar":
            st.bar_chart(trend, height=360)
        else:
            st.line_chart(trend, height=360)

        st.markdown("---")
        tleft, tright = st.columns(2)
        with tleft:
            st.subheader("Top 10 Employees per Month")
            top_per_month = (
                emp_month.sort_values(["sale_year", "sale_month", "total_sale"], ascending=[True, True, False])
                .groupby(["sale_year", "sale_month"], group_keys=False)
                .head(10)
                .copy()
            )
            top_per_month["rank"] = (
                top_per_month.groupby(["sale_year", "sale_month"])["total_sale"].rank(method="first", ascending=False).astype("int64")
            )
            top_show2 = top_per_month[["sale_year", "month_label", "rank", "employee_label", "shops", "total_transactions", "total_sale"]].copy()
            top_show2 = top_show2.rename(columns={"sale_year": "year", "month_label": "month", "employee_label": "employee"})
            top_show2["total_sale"] = top_show2["total_sale"].apply(format_currency)
            st.dataframe(top_show2, width="stretch", hide_index=True, height=360)

        with tright:
            st.subheader("Bottom 10 Employees per Month")
            bottom_per_month = (
                emp_month.sort_values(["sale_year", "sale_month", "total_sale"], ascending=[True, True, True])
                .groupby(["sale_year", "sale_month"], group_keys=False)
                .head(10)
                .copy()
            )
            bottom_per_month["rank"] = (
                bottom_per_month.groupby(["sale_year", "sale_month"])["total_sale"].rank(method="first", ascending=True).astype("int64")
            )
            bottom_show2 = bottom_per_month[["sale_year", "month_label", "rank", "employee_label", "shops", "total_transactions", "total_sale"]].copy()
            bottom_show2 = bottom_show2.rename(columns={"sale_year": "year", "month_label": "month", "employee_label": "employee"})
            bottom_show2["total_sale"] = bottom_show2["total_sale"].apply(format_currency)
            st.dataframe(bottom_show2, width="stretch", hide_index=True, height=360)

        st.markdown("---")
        show = df.copy().sort_values(["sale_year", "sale_month", "total_sale", "employee_name"], ascending=[True, True, False, True]).reset_index(drop=True)
        show.index = range(1, len(show) + 1)
        show.index.name = "#"

        if "sale_month" in show.columns:
            show["month"] = show["sale_month"].apply(lambda m: datetime(2000, int(m), 1).strftime("%b"))

        for col in ["total_sale", "qr_sale", "normal_sale"]:
            if col in show.columns:
                show[col] = show[col].apply(format_number)

        st.dataframe(
            show[
                [
                    "sale_year",
                    "month",
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "shop_name",
                    "total_transactions",
                    "total_sale",
                    "qr_sale",
                    "normal_sale",
                ]
            ],
            width="stretch",
            hide_index=False,
            height=520,
        )

        df_export = df.copy()
        if "sale_month" in df_export.columns:
            df_export["month"] = df_export["sale_month"].apply(lambda m: datetime(2000, int(m), 1).strftime("%B"))
            df_export = df_export.drop(columns=["sale_month"])
        if "sale_year" in df_export.columns:
            df_export = df_export.rename(columns={"sale_year": "year"})

        st.download_button(
            "Download Employee Monthly Sales Excel",
            export_excel(df_export, sheet_name="Employee Monthly Sales"),
            f"employee_monthly_sales_{int(year)}_{'_'.join([f'{m:02d}' for m in sorted(set(months_selected))])}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
