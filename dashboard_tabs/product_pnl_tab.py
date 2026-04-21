"""
Product PNL Tab
Shows branch-product profitability split by Non-Foodpanda and Foodpanda channels.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.product_pnl import PRODUCT_PNL_CATEGORY_LABELS, get_product_pnl_tables
from modules.utils import export_excel, format_currency


class ProductPNLTab:
    def __init__(self, start_date: str, end_date: str, selected_branches: list[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

    @staticmethod
    def _format_percent(value: float) -> str:
        try:
            return f"{float(value):.1f}%"
        except Exception:
            return "0.0%"

    def _display_non_foodpanda_table(self, non_fp_df: pd.DataFrame) -> None:
        st.markdown("### Non-Foodpanda Product PNL")
        if non_fp_df is None or non_fp_df.empty:
            st.info("No Non-Foodpanda product records found for selected period.")
            return

        df_show = non_fp_df.copy()
        for col in [
            "avg_unit_price",
            "latest_unit_price",
            "material_cost",
            "sales_price_minus_material_cost",
            "total_sales",
            "margin",
        ]:
            df_show[col] = df_show[col].apply(format_currency)
        df_show["margin_percentage"] = df_show["margin_percentage"].apply(self._format_percent)

        df_show = df_show.rename(
            columns={
                "branch": "Branch",
                "category": "Category",
                "product": "Product",
                "avg_unit_price": "Avg Unit Price (Excl FP)",
                "latest_unit_price": "Latest Unit Price (Excl FP)",
                "material_cost": "Material Cost",
                "sales_price_minus_material_cost": "Sales Price - Material Cost",
                "total_sales": "Total Sales",
                "margin": "Margin",
                "margin_percentage": "Margin %",
                "cost_missing": "Cost Missing",
                "material_cost_source": "Material Cost Source",
                "material_cost_resolved": "Material Cost Resolved",
            }
        )
        if "Material Cost Resolved" in df_show.columns:
            df_show["Material Cost Resolved"] = df_show["Material Cost Resolved"].apply(format_currency)
        st.dataframe(df_show, width="stretch", hide_index=True, height=460)
        st.download_button(
            "Download Non-Foodpanda PNL Excel",
            export_excel(non_fp_df, sheet_name="NonFoodpanda_PNL"),
            f"product_pnl_non_foodpanda_{self.start_date}_to_{self.end_date}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def _display_foodpanda_table(self, fp_df: pd.DataFrame) -> None:
        st.markdown("### Foodpanda Product PNL")
        if fp_df is None or fp_df.empty:
            st.info("No Foodpanda product records found for selected period.")
            return

        df_show = fp_df.copy()
        for col in [
            "avg_unit_price",
            "latest_unit_price",
            "material_cost",
            "sales_price_minus_material_cost",
            "total_sales",
            "margin",
            "foodpanda_commission",
        ]:
            df_show[col] = df_show[col].apply(format_currency)
        df_show["margin_percentage"] = df_show["margin_percentage"].apply(self._format_percent)

        df_show = df_show.rename(
            columns={
                "branch": "Branch",
                "category": "Category",
                "product": "Product",
                "avg_unit_price": "Avg Unit Price (FP)",
                "latest_unit_price": "Latest Unit Price (FP)",
                "material_cost": "Material Cost",
                "sales_price_minus_material_cost": "Sales Price - Material Cost",
                "total_sales": "Total Sales",
                "margin": "Margin",
                "margin_percentage": "Margin %",
                "foodpanda_commission": "Foodpanda Commission (18%)",
                "cost_missing": "Cost Missing",
                "material_cost_source": "Material Cost Source",
                "material_cost_resolved": "Material Cost Resolved",
            }
        )
        if "Material Cost Resolved" in df_show.columns:
            df_show["Material Cost Resolved"] = df_show["Material Cost Resolved"].apply(format_currency)
        st.dataframe(df_show, width="stretch", hide_index=True, height=460)
        st.download_button(
            "Download Foodpanda PNL Excel",
            export_excel(fp_df, sheet_name="Foodpanda_PNL"),
            f"product_pnl_foodpanda_{self.start_date}_to_{self.end_date}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def render(self) -> None:
        st.header("Product PNL")
        st.markdown(f"**Period:** {self.start_date} to {self.end_date}")
        st.caption(f"Mode: {self.data_mode}. Scope: all sold products with category + branch level PNL.")

        with st.expander("Configured Category Labels", expanded=False):
            st.dataframe(pd.DataFrame({"category": PRODUCT_PNL_CATEGORY_LABELS}), width="stretch", hide_index=True, height=260)

        non_fp_df, fp_df = get_product_pnl_tables(
            self.start_date,
            self.end_date,
            self.selected_branches,
            data_mode=self.data_mode,
        )

        available_categories = set(PRODUCT_PNL_CATEGORY_LABELS)
        if non_fp_df is not None and not non_fp_df.empty and "category" in non_fp_df.columns:
            available_categories.update(non_fp_df["category"].dropna().astype(str).tolist())
        if fp_df is not None and not fp_df.empty and "category" in fp_df.columns:
            available_categories.update(fp_df["category"].dropna().astype(str).tolist())
        available_categories = sorted(available_categories)

        default_selected = [c for c in PRODUCT_PNL_CATEGORY_LABELS if c in available_categories]
        if not default_selected:
            default_selected = available_categories

        st.markdown("### Category Filter")
        selected_categories = st.multiselect(
            "Select categories",
            options=available_categories,
            default=default_selected,
            key="product_pnl_category_filter",
            placeholder="Choose categories to filter both tables...",
        )

        if selected_categories:
            selected_set = set(selected_categories)
            if non_fp_df is not None and not non_fp_df.empty:
                non_fp_df = non_fp_df[non_fp_df["category"].astype(str).isin(selected_set)].copy()
            if fp_df is not None and not fp_df.empty:
                fp_df = fp_df[fp_df["category"].astype(str).isin(selected_set)].copy()
        else:
            non_fp_df = non_fp_df.iloc[0:0].copy() if non_fp_df is not None else pd.DataFrame()
            fp_df = fp_df.iloc[0:0].copy() if fp_df is not None else pd.DataFrame()
            st.warning("No category selected. Please select at least one category.")

        self._display_non_foodpanda_table(non_fp_df)
        with st.expander("Material Cost Source Summary", expanded=False):
            src_rows = []
            if non_fp_df is not None and not non_fp_df.empty and "material_cost_source" in non_fp_df.columns:
                src_non = non_fp_df["material_cost_source"].value_counts(dropna=False).rename_axis("source").reset_index(name="non_foodpanda_rows")
            else:
                src_non = pd.DataFrame(columns=["source", "non_foodpanda_rows"])
            if fp_df is not None and not fp_df.empty and "material_cost_source" in fp_df.columns:
                src_fp = fp_df["material_cost_source"].value_counts(dropna=False).rename_axis("source").reset_index(name="foodpanda_rows")
            else:
                src_fp = pd.DataFrame(columns=["source", "foodpanda_rows"])
            src = src_non.merge(src_fp, on="source", how="outer").fillna(0)
            if not src.empty:
                for col in ["non_foodpanda_rows", "foodpanda_rows"]:
                    src[col] = pd.to_numeric(src[col], errors="coerce").fillna(0).astype(int)
                st.dataframe(src, width="stretch", hide_index=True, height=240)
            else:
                st.info("No source trace rows available for current filter.")
        st.markdown("---")
        self._display_foodpanda_table(fp_df)
