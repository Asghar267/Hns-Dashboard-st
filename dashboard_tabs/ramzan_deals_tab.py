"""
Ramzan Deals Tab
Branch-wise and product-wise sales coverage for configured Ramzan deal products.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from modules.config import RAMZAN_DEALS_PRODUCT_IDS
from modules.database import get_cached_ramzan_deals_sales, get_cached_ramzan_product_master


class RamzanDealsTab:
    def __init__(self, start_date: date, end_date: date, selected_branches: list[int], branch_name_map: dict[int, str]):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.branch_name_map = branch_name_map

    def render(self) -> None:
        st.header("Ramzan Deals")

        rcol1, rcol2 = st.columns(2)
        with rcol1:
            ramzan_start_date = st.date_input("Ramzan Start Date", value=self.start_date, key="ramzan_start_date")
        with rcol2:
            ramzan_end_date = st.date_input("Ramzan End Date", value=self.end_date, key="ramzan_end_date")

        if ramzan_start_date > ramzan_end_date:
            st.error("Start date cannot be after end date.")
            return

        ramzan_start_str = ramzan_start_date.strftime("%Y-%m-%d")
        ramzan_end_str = ramzan_end_date.strftime("%Y-%m-%d")

        st.markdown("#### Branch Selection")
        ramzan_branches = st.multiselect(
            "Select Branches for Ramzan Deals",
            options=self.selected_branches,
            default=self.selected_branches,
            format_func=lambda x: self.branch_name_map.get(int(x), f"Branch {x}"),
            key="ramzan_branch_selector",
        )
        if not ramzan_branches:
            st.warning("Please select at least one branch for Ramzan Deals.")
            return

        ramzan_master = get_cached_ramzan_product_master()
        if ramzan_master is None or ramzan_master.empty:
            st.info("No Ramzan deal products found.")
            return

        ramzan_master = ramzan_master[
            ramzan_master["Product_code"].astype(str).isin([str(x) for x in RAMZAN_DEALS_PRODUCT_IDS])
        ].copy()
        if ramzan_master.empty:
            st.info("Ramzan master table returned no configured products.")
            return

        ramzan_master["display"] = ramzan_master["Product_code"].astype(str) + " - " + ramzan_master["item_name"].astype(str)
        selected_ramzan_products = st.multiselect(
            "Select Ramzan Deal Products",
            options=ramzan_master["display"].tolist(),
            default=ramzan_master["display"].tolist(),
            key="ramzan_product_selector",
        )
        if not selected_ramzan_products:
            st.warning("Please select at least one Ramzan product.")
            return

        selected_product_df = ramzan_master[ramzan_master["display"].isin(selected_ramzan_products)].copy()
        selected_product_ids = selected_product_df["Product_Item_ID"].tolist()

        ramzan_sales_df = get_cached_ramzan_deals_sales(ramzan_start_str, ramzan_end_str, ramzan_branches, selected_product_ids)

        merge_keys = ["shop_id", "shop_name", "Product_Item_ID", "Product_code", "item_name"]
        if ramzan_sales_df is None or ramzan_sales_df.empty:
            ramzan_sales_df = pd.DataFrame(columns=merge_keys + ["total_qty", "total_sales"])

        branches_df = pd.DataFrame(
            {
                "shop_id": ramzan_branches,
                "shop_name": [self.branch_name_map.get(int(b), f"Branch {b}") for b in ramzan_branches],
            }
        )
        branches_df["key"] = 1
        selected_product_df["key"] = 1
        full_grid = branches_df.merge(
            selected_product_df[["Product_Item_ID", "Product_code", "item_name", "key"]],
            on="key",
            how="inner",
        ).drop(columns=["key"])

        branch_wise_full = full_grid.merge(
            ramzan_sales_df[merge_keys + ["total_qty", "total_sales"]],
            on=merge_keys,
            how="left",
        )
        branch_wise_full["total_qty"] = pd.to_numeric(branch_wise_full["total_qty"], errors="coerce").fillna(0.0)
        branch_wise_full["total_sales"] = pd.to_numeric(branch_wise_full["total_sales"], errors="coerce").fillna(0.0)

        product_overall = branch_wise_full.groupby(["Product_Item_ID", "Product_code", "item_name"], as_index=False).agg(
            total_qty=("total_qty", "sum"),
            total_sales=("total_sales", "sum"),
        )

        total_sales_ramzan = float(product_overall["total_sales"].sum()) if not product_overall.empty else 0.0
        total_qty_ramzan = float(product_overall["total_qty"].sum()) if not product_overall.empty else 0.0

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Total Sales (PKR)", f"{total_sales_ramzan:,.0f}")
        with m2:
            st.metric("Total Quantity", f"{total_qty_ramzan:,.0f}")

        st.markdown("#### Branch-wise Sales")
        st.dataframe(branch_wise_full.sort_values(["shop_name", "Product_code"]), width="stretch", hide_index=True, height=420)

        st.markdown("#### Product-wise Overall Sales")
        st.dataframe(product_overall.sort_values(["Product_code"]), width="stretch", hide_index=True, height=280)

        # Downloads removed (Excel-only policy; no Ramzan export here)

