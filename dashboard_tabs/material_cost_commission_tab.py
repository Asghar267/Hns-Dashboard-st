"""
Material Cost Commission Tab
Renders commission analysis using built-in 73-product matrix (no DB commission table).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.material_cost_commission import (
    get_branch_material_cost_summary,
    get_branch_product_material_cost_summary,
    get_employee_material_cost_summary,
    get_material_cost_commission_analysis,
    get_material_cost_commission_data,
    get_product_material_cost_summary,
    load_persisted_material_cost_commission_setup,
    save_persisted_material_cost_commission_setup,
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

        state_key = "mcc_product_commission_setup"
        default_setup = material_cost_data.copy()
        default_setup["active"] = True
        persisted_setup = load_persisted_material_cost_commission_setup()
        if state_key not in st.session_state:
            st.session_state[state_key] = persisted_setup

        st.markdown("### Product Commission Controls (This Tab Only)")
        st.caption(
            "Commission and active/deactive changes here apply only to Material Cost Commission tab. "
            "Use Save Setup to keep changes after restart."
        )
        c1, c2, c3 = st.columns([1, 1, 1])
        if c1.button("Reset Setup to Default", key="mcc_reset_setup"):
            st.session_state[state_key] = default_setup
            st.rerun()
        if c2.button("Save Setup", key="mcc_save_setup"):
            if save_persisted_material_cost_commission_setup(st.session_state[state_key]):
                st.success("Setup saved for future sessions.")
            else:
                st.error("Unable to save setup. Please check logs.")
        c3.metric("Default Products", f"{len(default_setup):,}")

        current_setup = st.session_state[state_key].copy()
        if "active" not in current_setup.columns:
            current_setup["active"] = True
        current_setup["active"] = current_setup["active"].fillna(False).astype(bool)

        st.markdown("#### Bulk Active/Deactive")
        product_choices = []
        code_by_label: dict[str, int] = {}
        for row in current_setup.sort_values(["product_name", "product_code"]).itertuples(index=False):
            label = f"{int(row.product_code)} - {row.product_name}"
            product_choices.append(label)
            code_by_label[label] = int(row.product_code)

        selected_labels = st.multiselect(
            "Select products for bulk action",
            options=product_choices,
            key="mcc_bulk_selected_products",
            placeholder="Search product and select multiple...",
        )
        selected_codes = {code_by_label[label] for label in selected_labels}

        b1, b2, b3, b4 = st.columns(4)
        if b1.button("Activate Selected", key="mcc_activate_selected", use_container_width=True):
            if not selected_codes:
                st.warning("Please select at least one product.")
            else:
                updated = st.session_state[state_key].copy()
                updated["active"] = updated["active"].fillna(False).astype(bool)
                updated.loc[updated["product_code"].isin(selected_codes), "active"] = True
                st.session_state[state_key] = updated
                st.success(f"Activated {len(selected_codes)} selected product(s).")
                st.rerun()
        if b2.button("Deactivate Selected", key="mcc_deactivate_selected", use_container_width=True):
            if not selected_codes:
                st.warning("Please select at least one product.")
            else:
                updated = st.session_state[state_key].copy()
                updated["active"] = updated["active"].fillna(False).astype(bool)
                updated.loc[updated["product_code"].isin(selected_codes), "active"] = False
                st.session_state[state_key] = updated
                st.success(f"Deactivated {len(selected_codes)} selected product(s).")
                st.rerun()
        if b3.button("Activate All", key="mcc_activate_all", use_container_width=True):
            updated = st.session_state[state_key].copy()
            updated["active"] = True
            st.session_state[state_key] = updated
            st.success("All products activated.")
            st.rerun()
        if b4.button("Deactivate All", key="mcc_deactivate_all", use_container_width=True):
            updated = st.session_state[state_key].copy()
            updated["active"] = False
            st.session_state[state_key] = updated
            st.warning("All products deactivated.")
            st.rerun()

        with st.expander("Add Missing Product", expanded=False):
            p1, p2 = st.columns(2)
            new_code = p1.number_input("Product Code", min_value=1, step=1, value=270, key="mcc_new_product_code")
            new_name = p2.text_input("Product Name", value="", key="mcc_new_product_name")
            p3, p4, p5 = st.columns(3)
            new_material_cost = p3.number_input(
                "Material Cost",
                min_value=0.0,
                step=1.0,
                value=0.0,
                help="If unknown, keep 0 and update later.",
                key="mcc_new_product_material_cost",
            )
            new_commission = p4.number_input("Commission", min_value=0.0, step=1.0, value=50.0, key="mcc_new_product_commission")
            new_active = p5.checkbox("Active", value=True, key="mcc_new_product_active")
            if st.button("Add / Update Product", key="mcc_add_missing_product"):
                name_clean = str(new_name).strip()
                if not name_clean:
                    st.error("Product name is required.")
                else:
                    updated = st.session_state[state_key].copy()
                    updated["product_code"] = pd.to_numeric(updated["product_code"], errors="coerce").fillna(0).astype(int)
                    code_int = int(new_code)
                    if (updated["product_code"] == code_int).any():
                        updated.loc[updated["product_code"] == code_int, ["product_name", "material_cost", "commission", "active"]] = [
                            name_clean,
                            float(new_material_cost),
                            float(new_commission),
                            bool(new_active),
                        ]
                        st.success(f"Product {code_int} updated.")
                    else:
                        updated = pd.concat(
                            [
                                updated,
                                pd.DataFrame(
                                    [
                                        {
                                            "product_code": code_int,
                                            "product_name": name_clean,
                                            "material_cost": float(new_material_cost),
                                            "commission": float(new_commission),
                                            "active": bool(new_active),
                                        }
                                    ]
                                ),
                            ],
                            ignore_index=True,
                        )
                        st.success(f"Product {code_int} added.")
                    st.session_state[state_key] = updated.sort_values(["product_name", "product_code"]).reset_index(drop=True)
                    st.rerun()

        edited_setup = st.data_editor(
            st.session_state[state_key],
            width="stretch",
            hide_index=True,
            height=340,
            key="mcc_setup_editor",
            column_order=["active", "product_code", "product_name", "material_cost", "commission"],
            disabled=["product_code", "product_name", "material_cost"],
            column_config={
                "active": st.column_config.CheckboxColumn("Active", help="Uncheck to exclude product from this tab."),
                "product_code": st.column_config.NumberColumn("Product Code", format="%d"),
                "product_name": st.column_config.TextColumn("Product Name"),
                "material_cost": st.column_config.NumberColumn("Material Cost", format="%.2f"),
                "commission": st.column_config.NumberColumn("Commission", format="%.2f"),
            },
        )
        edited_setup["commission"] = pd.to_numeric(edited_setup["commission"], errors="coerce").fillna(0.0)
        edited_setup["active"] = edited_setup["active"].fillna(False).astype(bool)
        st.session_state[state_key] = edited_setup
        active_setup = edited_setup[edited_setup["active"]].copy()
        if active_setup.empty:
            st.warning("All products are inactive. Please activate at least one product to view analysis.")
            return

        with st.expander("Product Commission Setup Overview", expanded=False):
            total_material_cost = float(active_setup["material_cost"].sum())
            total_commission = float(active_setup["commission"].sum())
            avg_commission_rate = (total_commission / total_material_cost * 100.0) if total_material_cost > 0 else 0.0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Active Products", f"{len(active_setup):,}")
            col2.metric("Avg Material Cost", format_currency(total_material_cost / len(active_setup)))
            col3.metric("Avg Commission", format_currency(total_commission / len(active_setup)))
            col4.metric("Avg Rate", f"{avg_commission_rate:.1f}%")

            display_material = edited_setup.copy()
            display_material["material_cost"] = display_material["material_cost"].apply(format_currency)
            display_material["commission"] = display_material["commission"].apply(format_currency)
            st.dataframe(
                display_material[["active", "product_code", "product_name", "material_cost", "commission"]],
                width="stretch",
                hide_index=True,
                height=320,
            )

        st.markdown("---")
        st.subheader("Real-Time Commission Analysis")
        st.markdown(f"**Period:** {self.start_date} to {self.end_date}")
        st.caption(
            f"Data mode: {self.data_mode}. Using {len(active_setup)} active products from this tab's local commission setup."
        )

        show_price_diag = st.checkbox(
            "Show pricing diagnostics (avg/min/max unit price, variants)",
            value=False,
            key="mcc_show_pricing_diag",
            help="Helps explain per-unit sales differences when the same product_code is sold at multiple prices/variants.",
        )

        st.markdown("### Branch Summary")
        branch_comm_df = get_branch_material_cost_summary(
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
            commission_data=active_setup,
        )
        if branch_comm_df is None or branch_comm_df.empty:
            st.info("No commission data for selected branches in this period.")
        else:
            df_show = branch_comm_df.copy()
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            if "foodpanda_total_sales" in df_show.columns:
                df_show["foodpanda_total_sales"] = df_show["foodpanda_total_sales"].apply(format_currency)
            if "non_foodpanda_total_sales" in df_show.columns:
                df_show["non_foodpanda_total_sales"] = df_show["non_foodpanda_total_sales"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["avg_commission_rate"] = df_show["avg_commission_rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                df_show[
                    [
                        "shop_name",
                        "total_units_sold",
                        "total_sales",
                        "foodpanda_total_units",
                        "foodpanda_total_sales",
                        "non_foodpanda_total_units",
                        "non_foodpanda_total_sales",
                        "total_material_cost",
                        "total_commission",
                        "avg_commission_rate",
                    ]
                ],
                width="stretch",
                hide_index=True,
                height=320,
            )

            with st.expander("Charts & Insights", expanded=False):
                try:
                    raw = branch_comm_df.copy()
                    for col in [
                        "total_sales",
                        "foodpanda_total_sales",
                        "non_foodpanda_total_sales",
                        "total_units_sold",
                        "foodpanda_total_units",
                        "non_foodpanda_total_units",
                    ]:
                        if col in raw.columns:
                            raw[col] = pd.to_numeric(raw[col], errors="coerce").fillna(0.0)

                    fp_sales = float(raw.get("foodpanda_total_sales", pd.Series([0.0])).sum())
                    non_fp_sales = float(raw.get("non_foodpanda_total_sales", pd.Series([0.0])).sum())
                    denom = fp_sales + non_fp_sales
                    fp_share = (fp_sales / denom * 100.0) if denom > 0 else 0.0

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Foodpanda Sales", format_currency(fp_sales))
                    m2.metric("Non-Foodpanda Sales", format_currency(non_fp_sales))
                    m3.metric("Foodpanda Share", f"{fp_share:.1f}%")

                    if {"foodpanda_total_sales", "non_foodpanda_total_sales"}.issubset(raw.columns):
                        long_sales = raw.melt(
                            id_vars=["shop_name"],
                            value_vars=["foodpanda_total_sales", "non_foodpanda_total_sales"],
                            var_name="channel",
                            value_name="sales",
                        )
                        long_sales["channel"] = long_sales["channel"].map(
                            {
                                "foodpanda_total_sales": "Foodpanda",
                                "non_foodpanda_total_sales": "Non-Foodpanda",
                            }
                        )
                        fig = px.bar(
                            long_sales,
                            x="shop_name",
                            y="sales",
                            color="channel",
                            barmode="stack",
                            title="Branch Sales Split (Foodpanda vs Non-Foodpanda)",
                        )
                        fig.update_layout(xaxis_title="", yaxis_title="Sales", legend_title="")
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.info(f"Charts unavailable for this selection. Details: {e}")

        st.markdown("### Employee Summary")
        emp_comm_df = get_employee_material_cost_summary(
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
            commission_data=active_setup,
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
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
            commission_data=active_setup,
        )
        if branch_product_comm_df is None or branch_product_comm_df.empty:
            st.info("No product-wise branch commission data for this period.")
        else:
            df_show = branch_product_comm_df.copy()
            if "total_units_sold" in df_show.columns and "total_sales" in df_show.columns:
                denom = pd.to_numeric(df_show["total_units_sold"], errors="coerce").replace(0, pd.NA)
                num = pd.to_numeric(df_show["total_sales"], errors="coerce")
                df_show["avg_unit_price"] = (num / denom).fillna(0.0)
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["material_cost"] = df_show["material_cost"].apply(format_currency)
            df_show["commission"] = df_show["commission"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["commission_rate"] = df_show["commission_rate"].apply(lambda x: f"{x:.1f}%")

            cols = [
                "shop_name",
                "product_code",
                "product_name",
                "total_units_sold",
                "total_sales",
                "foodpanda_total_units",
                "foodpanda_total_sales",
                "foodpanda_unit_price",
                "non_foodpanda_total_units",
                "non_foodpanda_total_sales",
                "non_foodpanda_unit_price",
                "material_cost",
                "total_material_cost",
                "commission",
                "total_commission",
                "commission_rate",
            ]
            if show_price_diag:
                for c in [
                    "avg_unit_price",
                    "min_unit_price",
                    "max_unit_price",
                    "foodpanda_unit_price",
                    "non_foodpanda_unit_price",
                ]:
                    if c in df_show.columns:
                        df_show[c] = df_show[c].apply(format_currency)
                cols.extend(
                    [
                        "avg_unit_price",
                        "min_unit_price",
                        "max_unit_price",
                        "distinct_unit_prices",
                        "distinct_product_ids",
                        "foodpanda_distinct_unit_prices",
                        "non_foodpanda_distinct_unit_prices",
                    ]
                )
            st.dataframe(
                df_show[cols],
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
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
            commission_data=active_setup,
        )
        if product_comm_df is None or product_comm_df.empty:
            st.info("No product-wise overall commission data for this period.")
        else:
            df_show = product_comm_df.copy()
            if "total_units_sold" in df_show.columns and "total_sales" in df_show.columns:
                denom = pd.to_numeric(df_show["total_units_sold"], errors="coerce").replace(0, pd.NA)
                num = pd.to_numeric(df_show["total_sales"], errors="coerce")
                df_show["avg_unit_price"] = (num / denom).fillna(0.0)
            df_show["total_sales"] = df_show["total_sales"].apply(format_currency)
            df_show["material_cost"] = df_show["material_cost"].apply(format_currency)
            df_show["commission"] = df_show["commission"].apply(format_currency)
            df_show["total_material_cost"] = df_show["total_material_cost"].apply(format_currency)
            df_show["total_commission"] = df_show["total_commission"].apply(format_currency)
            df_show["commission_rate"] = df_show["commission_rate"].apply(lambda x: f"{x:.1f}%")

            cols = [
                "product_code",
                "product_name",
                "total_units_sold",
                "total_sales",
                "foodpanda_total_units",
                "foodpanda_total_sales",
                "foodpanda_unit_price",
                "non_foodpanda_total_units",
                "non_foodpanda_total_sales",
                "non_foodpanda_unit_price",
                "material_cost",
                "total_material_cost",
                "commission",
                "total_commission",
                "commission_rate",
            ]
            if show_price_diag:
                for c in [
                    "avg_unit_price",
                    "min_unit_price",
                    "max_unit_price",
                    "foodpanda_unit_price",
                    "non_foodpanda_unit_price",
                ]:
                    if c in df_show.columns:
                        df_show[c] = df_show[c].apply(format_currency)
                cols.extend(
                    [
                        "avg_unit_price",
                        "min_unit_price",
                        "max_unit_price",
                        "distinct_unit_prices",
                        "distinct_product_ids",
                        "foodpanda_distinct_unit_prices",
                        "non_foodpanda_distinct_unit_prices",
                    ]
                )
            st.dataframe(
                df_show[cols],
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
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
            commission_data=active_setup,
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
