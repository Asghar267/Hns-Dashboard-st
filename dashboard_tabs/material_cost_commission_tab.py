"""
Material Cost Commission Tab
Renders commission analysis using built-in 73-product matrix (no DB commission table).
"""

from __future__ import annotations

import streamlit as st

from modules.material_cost_commission import (
    get_branch_material_cost_summary,
    get_branch_product_material_cost_summary,
    get_employee_material_cost_summary,
    get_material_cost_commission_analysis,
    get_material_cost_commission_data,
    get_product_material_cost_summary,
)
from modules.utils import export_excel, format_currency


class MaterialCostCommissionTab:
    def __init__(self, start_date: str, end_date: str, selected_branches: list[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

    def render(self) -> None:
        st.header("Material Cost Commission")
        material_cost_data = get_material_cost_commission_data()

        if material_cost_data is None or material_cost_data.empty:
            st.info("Commission setup is empty (built-in matrix expected).")
            return

        with st.expander("Product Commission Setup Overview", expanded=False):
            total_material_cost = float(material_cost_data["material_cost"].sum())
            total_commission = float(material_cost_data["commission"].sum())
            avg_commission_rate = (total_commission / total_material_cost * 100.0) if total_material_cost > 0 else 0.0

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Material Cost", format_currency(total_material_cost / len(material_cost_data)))
            col2.metric("Avg Commission", format_currency(total_commission / len(material_cost_data)))
            col3.metric("Avg Rate", f"{avg_commission_rate:.1f}%")

            display_material = material_cost_data.copy()
            display_material["material_cost"] = display_material["material_cost"].apply(format_currency)
            display_material["commission"] = display_material["commission"].apply(format_currency)
            st.dataframe(
                display_material[["product_code", "product_name", "material_cost", "commission"]],
                width="stretch",
                hide_index=True,
                height=320,
            )

        st.markdown("---")
        st.subheader("Real-Time Commission Analysis")
        st.markdown(f"**Period:** {self.start_date} to {self.end_date}")
        st.caption(f"Data mode: {self.data_mode}. Commission setup uses built-in 73 products (no DB table required).")

        st.markdown("### Branch Summary")
        branch_comm_df = get_branch_material_cost_summary(
            self.start_date, self.end_date, self.selected_branches, data_mode=self.data_mode
        )
        if branch_comm_df is None or branch_comm_df.empty:
            st.info("No commission data for selected branches in this period.")
        else:
            df_show = branch_comm_df.copy()
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["avg_commission_rate"] = df_show["avg_commission_rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show[
                    ["shop_name", "total_units_sold", "total_sales", "total_material_cost", "total_commission", "avg_commission_rate"]
                ],
                width="stretch",
                hide_index=True,
                height=320,
            )

        st.markdown("### Employee Summary")
        emp_comm_df = get_employee_material_cost_summary(
            self.start_date, self.end_date, self.selected_branches, data_mode=self.data_mode
        )
        if emp_comm_df is None or emp_comm_df.empty:
            st.info("No employee commission data for this period.")
        else:
            df_show = emp_comm_df.copy()
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["avg_commission_rate"] = df_show["avg_commission_rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show[["employee_name", "shop_name", "total_units_sold", "total_sales", "total_material_cost", "total_commission"]],
                width="stretch",
                hide_index=True,
                height=420,
            )

        st.markdown("### Product-wise by Branch")
        branch_product_comm_df = get_branch_product_material_cost_summary(
            self.start_date, self.end_date, self.selected_branches, data_mode=self.data_mode
        )
        if branch_product_comm_df is None or branch_product_comm_df.empty:
            st.info("No product-wise branch commission data for this period.")
        else:
            df_show = branch_product_comm_df.copy()
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["material_cost"] = df_show["material_cost"].apply(format_currency)
            df_show["commission"] = df_show["commission"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["commission_rate"] = df_show["commission_rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show[
                    [
                        "shop_name",
                        "product_code",
                        "product_name",
                        "total_units_sold",
                        "total_sales",
                        "material_cost",
                        "total_material_cost",
                        "commission",
                        "total_commission",
                        "commission_rate",
                    ]
                ],
                width="stretch",
                hide_index=True,
                height=420,
            )
            st.download_button(
                "Download Product-wise Branch Commission Excel",
                export_excel(branch_product_comm_df, sheet_name="Product Branch Commission"),
                f"product_branch_commission_{self.start_date}_to_{self.end_date}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.markdown("### Product-wise Overall")
        product_comm_df = get_product_material_cost_summary(
            self.start_date, self.end_date, self.selected_branches, data_mode=self.data_mode
        )
        if product_comm_df is None or product_comm_df.empty:
            st.info("No product-wise overall commission data for this period.")
        else:
            df_show = product_comm_df.copy()
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["material_cost"] = df_show["material_cost"].apply(format_currency)
            df_show["commission"] = df_show["commission"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["commission_rate"] = df_show["commission_rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show[
                    [
                        "product_code",
                        "product_name",
                        "total_units_sold",
                        "total_sales",
                        "material_cost",
                        "total_material_cost",
                        "commission",
                        "total_commission",
                        "commission_rate",
                    ]
                ],
                width="stretch",
                hide_index=True,
                height=350,
            )
            st.download_button(
                "Download Product-wise Overall Commission Excel",
                export_excel(product_comm_df, sheet_name="Product Overall Commission"),
                f"product_overall_commission_{self.start_date}_to_{self.end_date}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.markdown("### Detailed Analysis (Product wise employees and branches)")
        search_query = st.text_input("Search Product or Employee", key="mcc_detail_search")
        detail_comm_df = get_material_cost_commission_analysis(
            self.start_date, self.end_date, self.selected_branches, data_mode=self.data_mode
        )
        if detail_comm_df is None or detail_comm_df.empty:
            st.info("No detailed commission records found.")
            return

        if search_query:
            mask = (
                detail_comm_df["product_name"].str.contains(search_query, case=False, na=False)
                | detail_comm_df["employee_name"].str.contains(search_query, case=False, na=False)
                | detail_comm_df["shop_name"].str.contains(search_query, case=False, na=False)
            )
            detail_comm_df = detail_comm_df[mask].copy()

        df_show = detail_comm_df.copy()
        df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
        df_show["material_cost"] = df_show["material_cost"].apply(format_currency)
        df_show["commission"] = df_show["commission"].apply(format_currency)
        df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
        df_show["total_commission"] = df_show["total_commission"].apply(format_currency)

        st.dataframe(
            df_show[
                [
                    "shop_name",
                    "employee_name",
                    "product_name",
                    "units_sold",
                    "total_sales",
                    "material_cost",
                    "total_material_cost",
                    "commission",
                    "total_commission",
                ]
            ],
            width="stretch",
            hide_index=True,
            height=600,
        )
        st.download_button(
            "Download Detailed Commission Report Excel",
            export_excel(detail_comm_df, sheet_name="Detailed Commission"),
            f"detailed_commission_{self.start_date}_to_{self.end_date}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
