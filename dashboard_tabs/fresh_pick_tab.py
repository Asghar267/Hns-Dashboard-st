"""
Fresh Pick Tab
Shows CandelaFP Fresh Pick sales with monthly target comparison.
"""

from __future__ import annotations

import re
import pandas as pd
import streamlit as st

from modules.database import get_cached_fresh_pick_sales, get_cached_targets
from modules.config import FRESH_PICK_PRODUCTS, FRESH_PICK_SALES_ITEM_NAMES, FRESH_PICK_VENDOR_ALIASES
from modules.utils import export_excel, format_currency, format_number, format_percentage


def _norm_text(value: object) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    # Normalize punctuation/spacing so cross-DB naming differences still match.
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Cross-DB alias map: KDS target names <-> CandelaFP item names
_PRODUCT_ALIASES = {
    "chicken breast boneless chicken mince": "chicken mince",
    "chicken breast boneless": "chicken breast boneless",
    "chicken mince": "chicken mince",
    "chicken skin on": "chicken skin on",
    "whole chicken skin on": "whole chicken skin on",
    "chicken leg bone in": "chicken leg bone in",
}


def _product_key(name: object) -> str:
    base = _norm_text(name)
    if not base:
        return ""
    return _PRODUCT_ALIASES.get(base, base)


def _vendor_key(name: object) -> str:
    base = _norm_text(name)
    if not base:
        return ""
    return (FRESH_PICK_VENDOR_ALIASES or {}).get(base, base)


class FreshPickTab:
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
        st.header("Fresh Pick")
        st.caption(
            f"Source: CandelaFP | Period: {self.start_date} to {self.end_date} | "
            f"Target Month: {self.target_year}-{self.target_month:02d}"
        )

        df_sales = get_cached_fresh_pick_sales(self.start_date, self.end_date, self.data_mode)
        _, _, _, df_fresh_targets = get_cached_targets(self.target_year, self.target_month)

        if df_sales is None or df_sales.empty:
            st.info("No Fresh Pick sales found for selected dates/products.")
            return

        sales = df_sales.copy()
        sales = sales.rename(columns={"Customer": "vendor", "Product": "product_name"})
        for col in ("TotalQuantitySold", "TotalRevenue", "TotalSaleAmount", "NumberOfSales"):
            if col in sales.columns:
                sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0.0)
        sales["vendor_key"] = sales["vendor"].apply(_vendor_key)
        sales["product_key"] = sales["product_name"].apply(_product_key)
        sales = (
            sales.groupby(["vendor_key", "product_key"], as_index=False)
            .agg(
                vendor=("vendor", "first"),
                product_name=("product_name", "first"),
                TotalQuantitySold=("TotalQuantitySold", "sum"),
                TotalRevenue=("TotalRevenue", "sum"),
                TotalSaleAmount=("TotalSaleAmount", "sum"),
                NumberOfSales=("NumberOfSales", "sum"),
            )
        )

        if df_fresh_targets is None or df_fresh_targets.empty:
            targets = pd.DataFrame(columns=["vendor", "product_name", "monthly_target_qty", "daily_target_qty"])
            st.warning(f"No Fresh Pick targets found in KDS DB for {self.target_year}-{self.target_month:02d}.")
        else:
            targets = df_fresh_targets.copy()
            targets["monthly_target_qty"] = pd.to_numeric(targets.get("monthly_target_qty"), errors="coerce").fillna(0.0)
            targets["daily_target_qty"] = pd.to_numeric(targets.get("daily_target_qty"), errors="coerce").fillna(0.0)
        targets["vendor_key"] = targets.get("vendor", "").apply(_vendor_key)
        targets["product_key"] = targets.get("product_name", "").apply(_product_key)

        # Keep only Fresh Pick products (robust across DB naming differences).
        allowed_product_keys = {
            _product_key(p) for p in (FRESH_PICK_PRODUCTS or []) + (FRESH_PICK_SALES_ITEM_NAMES or [])
        }
        allowed_product_keys.discard("")
        if allowed_product_keys and "product_key" in targets.columns:
            targets = targets[targets["product_key"].isin(allowed_product_keys)].copy()

        targets = (
            targets.groupby(["vendor_key", "product_key"], as_index=False)
            .agg(
                vendor=("vendor", "first"),
                product_name=("product_name", "first"),
                monthly_target_qty=("monthly_target_qty", "sum"),
                daily_target_qty=("daily_target_qty", "sum"),
            )
        )
        # Prefer target-side naming for each normalized product key.
        target_name_by_product_key = (
            targets.groupby("product_key", as_index=False)
            .agg(target_product_name=("product_name", "first"))
        )
        target_name_map = dict(
            zip(target_name_by_product_key["product_key"], target_name_by_product_key["target_product_name"])
        )

        merged = pd.merge(
            targets,
            sales,
            on=["vendor_key", "product_key"],
            how="outer",
        )
        
        # Safely fill string columns
        merged["vendor_x"] = merged["vendor_x"].fillna("")
        merged["vendor_y"] = merged["vendor_y"].fillna("")
        merged["product_name_x"] = merged["product_name_x"].fillna("")
        merged["product_name_y"] = merged["product_name_y"].fillna("")
        
        merged["vendor"] = merged["vendor_x"].where(merged["vendor_x"].astype(str).str.strip() != "", merged["vendor_y"]).astype(str)
        merged["product_name"] = merged["product_name_x"].where(
            merged["product_name_x"].astype(str).str.strip() != "", merged["product_name_y"]
        ).astype(str)
        
        # Fill numeric columns
        num_cols = ["monthly_target_qty", "daily_target_qty", "TotalQuantitySold", "TotalRevenue", "TotalSaleAmount", "NumberOfSales"]
        for col in num_cols:
            if col in merged.columns:
                merged[col] = merged[col].fillna(0.0)
        merged = merged.drop(
            columns=[c for c in ["vendor_x", "vendor_y", "product_name_x", "product_name_y"] if c in merged.columns]
        )
        merged["product_name"] = merged["product_key"].map(target_name_map).fillna(merged["product_name"])

        with st.expander("Vendor/Product mapping debug", expanded=False):
            try:
                target_vendors = set(targets["vendor_key"].astype(str).unique())
                sale_vendors = set(sales["vendor_key"].astype(str).unique())
                only_in_targets = sorted(v for v in target_vendors - sale_vendors if v)
                only_in_sales = sorted(v for v in sale_vendors - target_vendors if v)
                st.caption("If vendors are missing due to naming differences, add entries to `FRESH_PICK_VENDOR_ALIASES`.")
                st.write({"vendors_only_in_targets": only_in_targets, "vendors_only_in_sales": only_in_sales})

                target_products = set(targets["product_key"].astype(str).unique())
                sale_products = set(sales["product_key"].astype(str).unique())
                only_products_in_targets = sorted(p for p in target_products - sale_products if p)
                only_products_in_sales = sorted(p for p in sale_products - target_products if p)
                st.write(
                    {
                        "products_only_in_targets": only_products_in_targets,
                        "products_only_in_sales": only_products_in_sales,
                    }
                )
            except Exception as e:
                st.warning(f"Could not compute mapping debug: {e}")

        # Product-level consolidation (requirement: targeted vs non-targeted by product).
        product_view = (
            merged.groupby("product_key", as_index=False)
            .agg(
                product_name=("product_name", "first"),
                monthly_target_qty=("monthly_target_qty", "sum"),
                daily_target_qty=("daily_target_qty", "sum"),
                TotalQuantitySold=("TotalQuantitySold", "sum"),
                TotalRevenue=("TotalRevenue", "sum"),
                TotalSaleAmount=("TotalSaleAmount", "sum"),
                NumberOfSales=("NumberOfSales", "sum"),
            )
        )

        product_view["Achievement_%"] = product_view.apply(
            lambda r: (r["TotalQuantitySold"] / r["monthly_target_qty"] * 100.0)
            if r["monthly_target_qty"] > 0 else 0.0,
            axis=1,
        )
        product_view["Remaining_Qty"] = product_view["monthly_target_qty"] - product_view["TotalQuantitySold"]
        product_view["Target_Type"] = product_view["monthly_target_qty"].apply(
            lambda x: "Targeted" if float(x) > 0 else "Non-Targeted"
        )

        total_qty = float(merged["TotalQuantitySold"].sum())
        targeted_qty = float(merged.loc[merged["monthly_target_qty"] > 0, "TotalQuantitySold"].sum())
        non_targeted_qty = float(merged.loc[merged["monthly_target_qty"] <= 0, "TotalQuantitySold"].sum())
        total_target_qty = float(merged["monthly_target_qty"].sum())
        
        total_sale_amount = float(merged["TotalSaleAmount"].sum())
        targeted_sale_amount = float(merged.loc[merged["monthly_target_qty"] > 0, "TotalSaleAmount"].sum())
        non_targeted_sale_amount = float(merged.loc[merged["monthly_target_qty"] <= 0, "TotalSaleAmount"].sum())

        overall_achievement = (targeted_qty / total_target_qty * 100.0) if total_target_qty > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Qty Sold (All)", format_number(total_qty))
        c2.metric("Targeted Qty Sold", format_number(targeted_qty))
        c3.metric("Total Qty Target", format_number(total_target_qty))
        c4.metric("Qty Achievement (Targeted)", format_percentage(overall_achievement))
        
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Total Amount (All)", format_currency(total_sale_amount))
        d2.metric("Targeted Amount", format_currency(targeted_sale_amount))
        d3.metric("Non-Targeted Amount", format_currency(non_targeted_sale_amount))
        d4.metric("Non-Targeted Qty Sold", format_number(non_targeted_qty))
        
        st.caption("Name mapping active: KDS target names are normalized and matched with CandelaFP item names.")

        st.markdown("---")
        st.subheader("Target vs Actual (Product-Level)")

        view = product_view.copy()
        view = view.rename(
            columns={
                "product_name": "Product",
                "monthly_target_qty": "Monthly Target Qty",
                "daily_target_qty": "Per Day Target Qty",
                "TotalQuantitySold": "Actual Qty Sold",
                "TotalRevenue": "Total Revenue",
                "TotalSaleAmount": "Total Sale Amount",
                "NumberOfSales": "No. of Sales",
                "Achievement_%": "Achievement %",
                "Remaining_Qty": "Remaining Qty",
                "Target_Type": "Target Type",
            }
        )
        view["__sort"] = view["Target Type"].map({"Targeted": 0, "Non-Targeted": 1}).fillna(2)
        view = view.sort_values(["__sort", "Product"]).drop(columns=["__sort"])

        display = view.copy()
        display["Monthly Target Qty"] = display["Monthly Target Qty"].apply(format_number)
        display["Per Day Target Qty"] = display["Per Day Target Qty"].apply(format_number)
        display["Actual Qty Sold"] = display["Actual Qty Sold"].apply(format_number)
        display["Remaining Qty"] = display["Remaining Qty"].apply(format_number)
        display["Total Revenue"] = display["Total Revenue"].apply(format_currency)
        display["Total Sale Amount"] = display["Total Sale Amount"].apply(format_currency)
        display["No. of Sales"] = display["No. of Sales"].apply(format_number)
        display["Achievement %"] = display["Achievement %"].apply(format_percentage)

        st.dataframe(display, width="stretch", hide_index=True, height=460)

        st.markdown("---")
        st.subheader("Vendor / Customer Wise Breakdown")

        # Vendor-wise view
        vendor_view = merged.copy()
        vendor_view["Achievement %"] = vendor_view.apply(
            lambda r: (r["TotalQuantitySold"] / r["monthly_target_qty"] * 100.0)
            if r["monthly_target_qty"] > 0
            else 0.0,
            axis=1,
        )
        vendor_view["Remaining Qty"] = vendor_view["monthly_target_qty"] - vendor_view["TotalQuantitySold"]
        
        # Sort by vendor then product
        vendor_view = vendor_view.sort_values(["vendor", "product_name"])
        
        # Select and rename columns for display
        vendor_display = vendor_view[
            [
                "vendor",
                "product_name",
                "monthly_target_qty",
                "daily_target_qty",
                "TotalQuantitySold",
                "TotalRevenue",
                "TotalSaleAmount",
                "Achievement %",
                "Remaining Qty",
            ]
        ].copy()
        
        vendor_display = vendor_display.rename(
            columns={
                "vendor": "Vendor / Customer",
                "product_name": "Product",
                "monthly_target_qty": "Monthly Target",
                "daily_target_qty": "Daily Target",
                "TotalQuantitySold": "Actual Qty",
                "TotalRevenue": "Revenue",
                "TotalSaleAmount": "Sale Amount",
            }
        )

        # Formatting
        vendor_display["Monthly Target"] = vendor_display["Monthly Target"].apply(format_number)
        vendor_display["Daily Target"] = vendor_display["Daily Target"].apply(format_number)
        vendor_display["Actual Qty"] = vendor_display["Actual Qty"].apply(format_number)
        vendor_display["Remaining Qty"] = vendor_display["Remaining Qty"].apply(format_number)
        vendor_display["Revenue"] = vendor_display["Revenue"].apply(format_currency)
        vendor_display["Sale Amount"] = vendor_display["Sale Amount"].apply(format_currency)
        vendor_display["Achievement %"] = vendor_display["Achievement %"].apply(format_percentage)

        st.dataframe(vendor_display, width="stretch", hide_index=True, height=600)

        st.download_button(
            "Download Fresh Pick Report",
            export_excel(view.sort_values("Total Sale Amount", ascending=False), sheet_name="Fresh Pick"),
            f"fresh_pick_report_{self.target_year}_{self.target_month}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
