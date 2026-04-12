"""
Chef Targets Tab
Targets vs achievements by category (sale/qty) using KDS chef_sale categories.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.config import QTY_CATEGORIES, SALE_CATEGORIES
from modules.database import get_cached_line_items, get_cached_targets, pool
from modules.utils import export_excel


def _clean_name(name: object) -> str:
    s = str(name or "").upper()
    s = s.replace("SALES -", "").replace("SALES", "").strip()
    s = s.replace("SIDE ORDERS", "SIDE ORDER")
    s = s.replace("-", " ")
    words = s.split()
    out = []
    for w in words:
        if w == "ROLLS":
            w = "ROLL"
        elif w == "ORDERS":
            w = "ORDER"
        elif w == "SIDES":
            w = "SIDE"
        out.append(w)
    return " ".join(out).strip()


class ChefTargetsTab:
    def __init__(self, target_year: int, target_month: int, start_date: str, end_date: str, selected_branches: list[int], data_mode: str):
        self.target_year = int(target_year)
        self.target_month = int(target_month)
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

    def render(self) -> None:
        st.header("Chef Targets & Achievement")

        # Branch list from DB, to keep names accurate.
        df_branch = pd.DataFrame()
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
        selected_branch = st.selectbox("Select Branch", branch_names, key="chef_targets_branch")
        shop_id = int(df_branch[df_branch["shop_name"] == selected_branch]["shop_id"].iloc[0])

        month_label = datetime(self.target_year, self.target_month, 1).strftime("%B %Y")
        st.info(f"Showing targets for {selected_branch} - {month_label}")

        # Targets data for month
        _, chef_targets, _, _ = get_cached_targets(self.target_year, self.target_month)
        if chef_targets is None or chef_targets.empty:
            st.warning("No chef targets data available.")
            return

        df_chef_filtered = chef_targets[chef_targets["shop_id"] == shop_id].copy()
        if df_chef_filtered.empty:
            st.warning(f"No targets found for {selected_branch}.")
            return

        # Category master from KDS DB
        try:
            conn_kds = pool.get_connection("kdsdb")
            categories = pd.read_sql("SELECT category_id, category_name FROM dbo.chef_sale", conn_kds)
            if "category_id" in categories.columns:
                categories["category_id"] = pd.to_numeric(categories["category_id"], errors="coerce").fillna(0).astype(int)
                # Avoid exploding merge if chef_sale has duplicate category_id rows.
                categories = categories.drop_duplicates(subset=["category_id"], keep="first")
        except Exception as e:
            st.error(f"Could not load chef_sale categories from KDS DB: {e}")
            return

        # If duplicate target rows exist for same (shop_id, category_id) in the same period,
        # the merge and table display will show duplicates. Prefer a stable collapse and warn.
        dup = (
            df_chef_filtered.groupby(["shop_id", "category_id"], dropna=False)
            .size()
            .reset_index(name="count")
        )
        dup = dup[dup["count"] > 1]
        if not dup.empty:
            st.warning(
                f"Duplicate Chef Target rows found for this branch/month: {len(dup):,}. "
                "This usually means duplicate rows in `branch_chef_targets` for the same (shop_id, category_id). "
                "Collapsing duplicates by keeping the highest target."
            )
            df_chef_filtered = (
                df_chef_filtered.copy()
                .sort_values(["target_amount"], ascending=False)
                .drop_duplicates(subset=["shop_id", "category_id"], keep="first")
            )

        df_targets = df_chef_filtered.merge(categories, on="category_id", how="left")
        allowed_categories = SALE_CATEGORIES + QTY_CATEGORIES
        df_targets = df_targets[df_targets["category_name"].isin(allowed_categories)].copy()
        if df_targets.empty:
            st.info("No allowed categories found in targets for this branch.")
            return

        def _normalize_target_type(v: object) -> str:
            s = str(v or "").strip().lower()
            if not s:
                return ""
            if s.startswith("q") or "qty" in s or "quantity" in s:
                return "quantity"
            if s.startswith("s") or "sale" in s or "amount" in s or "value" in s:
                return "amount"
            return "amount"

        def get_target_type(cat: str) -> str:
            if cat in SALE_CATEGORIES:
                return "amount"
            if cat in QTY_CATEGORIES:
                return "quantity"
            return "amount"

        # Prefer DB-provided target_type when present (e.g. 'quantity'), otherwise fallback to config lists.
        has_db_type = "target_type" in df_targets.columns and df_targets["target_type"].notna().any()
        if has_db_type:
            norm = df_targets["target_type"].map(_normalize_target_type)
            df_targets["target_type"] = norm.where(norm.astype(str).str.len() > 0, df_targets["category_name"].astype(str).apply(get_target_type))
        else:
            df_targets["target_type"] = df_targets["category_name"].astype(str).apply(get_target_type)

        # Sales data for this branch (uses cached line items)
        df_line_item = get_cached_line_items(self.start_date, self.end_date, self.selected_branches, self.data_mode)
        if df_line_item is None or df_line_item.empty:
            st.info("No line-item sales available for selected period.")
            return

        df_sales_branch = df_line_item[df_line_item["shop_id"] == shop_id].copy()
        if df_sales_branch.empty:
            st.info("No chef sales for this branch in selected period.")
            return

        products_to_hide = {"Sales - Employee Food", "Deals", "Modifiers"}
        if "product" in df_sales_branch.columns:
            df_sales_branch = df_sales_branch[~df_sales_branch["product"].astype(str).isin(products_to_hide)]

        df_sales_branch["product_clean"] = df_sales_branch["product"].apply(_clean_name)
        df_targets["category_clean"] = df_targets["category_name"].apply(_clean_name)

        df_join = df_targets.merge(
            df_sales_branch,
            left_on="category_clean",
            right_on="product_clean",
            how="left",
        ).fillna({"total_line_value_incl_tax": 0, "total_qty": 0})

        df_join["Product"] = df_join["product"].fillna(df_join["category_name"])
        df_join["Target"] = pd.to_numeric(df_join.get("target_amount"), errors="coerce").fillna(0.0)

        # Choose current based on type
        df_join["Current"] = df_join.apply(
            lambda r: float(r.get("total_line_value_incl_tax", 0.0)) if r.get("target_type") == "amount" else float(r.get("total_qty", 0.0)),
            axis=1,
        )

        df_join["Remaining"] = df_join["Target"] - df_join["Current"]
        df_join["Achievement %"] = df_join.apply(
            lambda r: (r["Current"] / r["Target"] * 100.0) if r["Target"] > 0 else 0.0, axis=1
        )
        # Basic bonus policy from legacy: if >=100%, bonus = 10% of target (sale) or fixed 0 for qty.
        df_join["Bonus"] = df_join.apply(
            lambda r: (0.1 * r["Target"]) if (r.get("target_type") == "amount" and r["Achievement %"] >= 100.0) else 0.0,
            axis=1,
        )

        display = df_join[["Product", "target_type", "Target", "Current", "Remaining", "Achievement %", "Bonus"]].copy()
        display["Target"] = display["Target"].apply(lambda x: f"{x:,.0f}")
        display["Current"] = display["Current"].apply(lambda x: f"{x:,.0f}")
        display["Remaining"] = display["Remaining"].apply(lambda x: f"{x:,.0f}")
        display["Achievement %"] = display["Achievement %"].apply(lambda x: f"{x:.1f}%")
        display["Bonus"] = display["Bonus"].apply(lambda x: f"{x:,.0f}")
        display = display.rename(columns={"target_type": "Type"})

        st.dataframe(display, width="stretch", hide_index=True, height=420)

        # Chart
        st.markdown("---")
        st.subheader("Target vs Achievement Comparison")
        has_sale = (df_join["target_type"] == "amount").any()
        has_qty = (df_join["target_type"] == "quantity").any()
        if has_sale:
            sale_df = df_join[df_join["target_type"] == "amount"][["Product", "Target", "Current"]].copy()
            sale_df = sale_df.rename(columns={"Current": "Current Sale"})
            melt = sale_df.melt(id_vars="Product", value_vars=["Target", "Current Sale"], var_name="Type", value_name="Value")
            fig = px.bar(
                melt,
                x="Value",
                y="Product",
                color="Type",
                orientation="h",
                barmode="group",
                height=520,
                title=f"Targets vs Sales (PKR) - {month_label}",
            )
            st.plotly_chart(fig, width="stretch")
        if has_qty:
            qty_df = df_join[df_join["target_type"] == "quantity"][["Product", "Target", "Current"]].copy()
            qty_df = qty_df.rename(columns={"Current": "Current Qty"})
            melt = qty_df.melt(id_vars="Product", value_vars=["Target", "Current Qty"], var_name="Type", value_name="Value")
            fig = px.bar(
                melt,
                x="Value",
                y="Product",
                color="Type",
                orientation="h",
                barmode="group",
                height=520,
                title=f"Targets vs Quantity - {month_label}",
            )
            st.plotly_chart(fig, width="stretch")

        # Export
        raw_export = df_join[["Product", "target_type", "Target", "Current", "Remaining", "Achievement %", "Bonus"]].copy()
        st.download_button(
            "Download Chef Targets Excel",
            export_excel(raw_export, sheet_name="Chef Targets"),
            f"chef_targets_{selected_branch}_{self.target_year}_{self.target_month}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


