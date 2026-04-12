"""
Category Coverage Tab
Shows included/excluded category sales coverage, and filter impact breakdown.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.config import BLOCKED_NAMES, BLOCKED_COMMENTS
from modules.database import (
    get_cached_blocked_impact,
    get_cached_branch_summary,
    get_cached_category_filter_coverage,
    get_cached_unmapped_products,
    get_saved_category_filters,
    refresh_all_caches,
    save_category_filters,
    _normalize_category_name,
)
from modules.utils import format_currency
from modules.responsive import clamp_dataframe_height, get_responsive_context, responsive_columns


class CategoryCoverageTab:
    def __init__(
        self,
        start_date: str,
        end_date: str,
        selected_branches: list[int],
        data_mode: str,
        key_prefix: str = "category_coverage",
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.key_prefix = key_prefix
        self.responsive = get_responsive_context()

    def render(self) -> None:
        st.header("📊 Category Filters & Coverage")
        st.caption("Configure categories and review sales impact with detailed coverage analysis.")

        # Load common data before tabs so they are available
        with st.spinner("Loading categories..."):
            df_cov_all = get_cached_category_filter_coverage(self.start_date, self.end_date, self.selected_branches, self.data_mode)
        
        if df_cov_all is None or df_cov_all.empty:
            st.error("No category data available for the selected period.")
            return

        main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
            "⚙️ Configuration", 
            "📈 Impact Analysis", 
            "🚫 Blocked Transactions", 
            "📦 Unmapped Items"
        ])

        with main_tab1:

            # Get all categories from actual sales data (52-53 including unmapped)
            all_sales_categories = sorted(df_cov_all["category_name"].dropna().unique().tolist())

            # Separate unmapped
            unmapped_exists = "(Unmapped)" in all_sales_categories
            category_options = [c for c in all_sales_categories if c != "(Unmapped)"]

            saved_filters = get_saved_category_filters()
            current_include = [x for x in saved_filters.get("included_category_names", []) if x in category_options]

            # If no filters saved yet, default to all categories selected
            default_selection = current_include if current_include else category_options

            # Single filter section - included categories only
            with st.expander("🔍 Choose Categories", expanded=False):
                st.caption("Select categories to include. All unselected categories are excluded automatically.")
                actual_selected_count = len(current_include) if current_include else len(category_options)
                st.caption(f"**Available: {len(category_options)} | Selected: {actual_selected_count}**")

                if unmapped_exists:
                    st.info(f"📦 + Unmapped products (not included in filter)")

                btn_cols = responsive_columns(self.responsive, desktop=3, tablet=2, phone=1)
                btn_col1 = btn_cols[0]
                btn_col2 = btn_cols[1 % len(btn_cols)]
                btn_col3 = btn_cols[2 % len(btn_cols)]
                with btn_col1:
                    if st.button("✓ Select All", key=f"{self.key_prefix}_sel_all_cov", width="stretch"):
                        st.session_state[f"{self.key_prefix}_selected_cov"] = category_options.copy()
                        st.rerun()
                with btn_col2:
                    if st.button("✗ Clear All (Exclude All)", key=f"{self.key_prefix}_clear_all_cov", width="stretch"):
                        st.session_state[f"{self.key_prefix}_selected_cov"] = []
                        st.rerun()
                with btn_col3:
                    st.write("")

                selected_names = st.multiselect(
                    "Choose categories to **INCLUDE** (unselected will be excluded)",
                    options=category_options,
                    default=default_selection,
                    key=f"{self.key_prefix}_selected_cov",
                    placeholder="Select categories..."
                )

            # Handle session state
            if f"{self.key_prefix}_selected_cov" in st.session_state:
                selected_names = st.session_state[f"{self.key_prefix}_selected_cov"]

            # Save/Reset buttons (always visible)
            st.divider()
            btn_col1, btn_col2 = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
            with btn_col1:
                save_clicked = st.button("💾 Save Configuration", width="stretch", type="primary", key=f"{self.key_prefix}_save_cfg")
            with btn_col2:
                reset_clicked = st.button("🔄 Reset All", width="stretch", key=f"{self.key_prefix}_reset_cfg")

            if save_clicked:
                # Selected = Included, Unselected = Excluded
                excluded_names = [x for x in category_options if x not in selected_names]

                payload = {
                    "included_category_ids": [],
                    "excluded_category_ids": [],
                    "included_category_names": selected_names,
                    "excluded_category_names": excluded_names,
                }
                try:
                    save_category_filters(payload)
                    refresh_all_caches()
                    st.success(f"✅ Saved! {len(selected_names)} included, {len(excluded_names)} excluded")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save: {e}")

            if reset_clicked:
                payload = {
                    "included_category_ids": [],
                    "excluded_category_ids": [],
                    "included_category_names": [],
                    "excluded_category_names": [],
                }
                try:
                    save_category_filters(payload)
                    refresh_all_caches()
                    st.success("✅ All filters cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not reset: {e}")
            else:
                st.info("No categories available to configure.")

            # Current configuration summary
            current_cfg = get_saved_category_filters()
            inc_count = len(current_cfg.get("included_category_names", []))
            exc_count = len(current_cfg.get("excluded_category_names", []))

            # Show status if any filters are applied
            if inc_count > 0 or exc_count > 0:
                st.divider()
                status_col1, status_col2 = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                with status_col1:
                    if inc_count > 0:
                        st.info(f"✅ **{inc_count}** categories included")
                    else:
                        st.write("✅ No include filters set")
                with status_col2:
                    if exc_count > 0:
                        st.info(f"❌ **{exc_count}** categories excluded")
                    else:
                        st.write("❌ No exclude filters set")

            st.markdown("---")
            st.subheader("📈 Category Coverage Analysis")
            st.caption(
                "Shows which categories are included/excluded in calculations and their sales impact."
            )

            # Use the already-loaded df_cov_all instead of reloading
            df_cov = df_cov_all.copy()
            df_cov["total_qty"] = pd.to_numeric(df_cov["total_qty"], errors="coerce").fillna(0.0)
            df_cov["total_sales"] = pd.to_numeric(df_cov["total_sales"], errors="coerce").fillna(0.0)

            # Separate unmapped products
            unmapped_rows = df_cov[df_cov["category_name"] == "(Unmapped)"].copy()
            df_cov_actual = df_cov[df_cov["category_name"] != "(Unmapped)"].copy()

            # Deduplicate by category name (keep first = highest sales)
            df_cov_actual = df_cov_actual.drop_duplicates(subset=["category_name"], keep="first")

            # Show unmapped info
            if not unmapped_rows.empty:
                unmapped_sales = unmapped_rows["total_sales"].sum()
                unmapped_qty = unmapped_rows["total_qty"].sum()
                if unmapped_sales > 0:
                    st.info(f"📦 **Unmapped Products:** {unmapped_qty:,.0f} qty (PKR {unmapped_sales:,.0f})")

            # Use actual sales categories
            df_cov = df_cov_actual

            # Add "counted" status based on applied filters
            current_filters = get_saved_category_filters()
            included_list = current_filters.get("included_category_names", [])

            # Normalize both sides for proper matching
            included_normalized = set(_normalize_category_name(cat) for cat in included_list) if included_list else set()
            df_cov["counted"] = df_cov["category_name"].apply(
                lambda x: _normalize_category_name(x) in included_normalized if included_normalized else False
            )

            # Split into included and excluded
            counted_df = df_cov[df_cov["counted"] == True].copy()
            excluded_df = df_cov[df_cov["counted"] == False].copy()

            # Key metrics - based on ACTUAL sales data
            metric_cols = responsive_columns(self.responsive, desktop=4, tablet=2, phone=1)
            with metric_cols[0]:
                st.metric("📊 Total Categories", f"{len(df_cov)}", border=True)
            with metric_cols[1 % len(metric_cols)]:
                st.metric("✅ Counted", f"{len(counted_df)}", border=True)
            with metric_cols[2 % len(metric_cols)]:
                st.metric("❌ Excluded", f"{len(excluded_df)}", border=True)
            with metric_cols[3 % len(metric_cols)]:
                st.metric("💰 Impact", f"PKR {excluded_df['total_sales'].sum():,.0f}", border=True)

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["✅ Included Categories", "❌ Excluded Categories", "📊 Details"])

            with tab1:
                if len(counted_df) > 0:
                    display_counted = counted_df.sort_values("total_sales", ascending=False)[[
                        "category_name", "total_qty", "total_sales"
                    ]].copy()
                    display_counted.columns = ["Category", "Qty", "Sales (PKR)"]
                    display_counted["Sales (PKR)"] = display_counted["Sales (PKR)"].apply(lambda x: f"{x:,.0f}")
                    st.dataframe(display_counted, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=400, tablet=320, phone=260, kind="default"))
                else:
                    st.info("No included categories")

            with tab2:
                if len(excluded_df) > 0:
                    display_excluded = excluded_df.sort_values("total_sales", ascending=False)[[
                        "category_name", "total_qty", "total_sales"
                    ]].copy()
                    display_excluded.columns = ["Category", "Qty", "Sales (PKR)"]
                    display_excluded["Sales (PKR)"] = display_excluded["Sales (PKR)"].apply(lambda x: f"{x:,.0f}")
                    st.dataframe(display_excluded, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=400, tablet=320, phone=260, kind="default"))
                else:
                    st.info("No excluded categories")

            with tab3:
                st.write("**Coverage Summary:**")
                detail_cols = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                with detail_cols[0]:
                    st.write(f"- Included Sales: PKR {counted_df['total_sales'].sum():,.0f}")
                    st.write(f"- Excluded Sales: PKR {excluded_df['total_sales'].sum():,.0f}")
                with detail_cols[1 % len(detail_cols)]:
                    total_sales = df_cov['total_sales'].sum()
                    exc_impact_pct = (excluded_df['total_sales'].sum() / total_sales * 100) if total_sales > 0 else 0
                    st.write(f"- Total Sales: PKR {total_sales:,.0f}")
                    st.write(f"- Excluded %: {exc_impact_pct:.1f}%")

        with main_tab2:
            st.subheader("🔍 Filter Impact Analysis")
            st.caption(
                "Compares the effect of category filters and blocked items on sales totals."
            )

            with st.spinner("Calculating filter impact..."):
                df_unfiltered_raw = get_cached_branch_summary(
                    self.start_date, self.end_date, self.selected_branches, "Unfiltered", apply_category_filters=False
                )
                df_blocked_only = get_cached_branch_summary(
                    self.start_date, self.end_date, self.selected_branches, "Filtered", apply_category_filters=False
                )
                df_category_only = get_cached_branch_summary(
                    self.start_date, self.end_date, self.selected_branches, "Unfiltered", apply_category_filters=True
                )
                df_both = get_cached_branch_summary(
                    self.start_date, self.end_date, self.selected_branches, "Filtered", apply_category_filters=True
                )

            def _safe_sum(df: pd.DataFrame) -> float:
                if df is None or df.empty or "total_Nt_amount" not in df.columns:
                    return 0.0
                return float(pd.to_numeric(df["total_Nt_amount"], errors="coerce").fillna(0.0).sum())

            total_unfiltered_raw = _safe_sum(df_unfiltered_raw)
            total_blocked_only = _safe_sum(df_blocked_only)
            total_category_only = _safe_sum(df_category_only)
            total_both = _safe_sum(df_both)

            blocked_impact = total_unfiltered_raw - total_blocked_only
            blocked_pct = (blocked_impact / total_unfiltered_raw * 100.0) if total_unfiltered_raw > 0 else 0.0
            category_impact = total_unfiltered_raw - total_category_only
            category_pct = (category_impact / total_unfiltered_raw * 100.0) if total_unfiltered_raw > 0 else 0.0
            combined_impact = total_unfiltered_raw - total_both
            combined_pct = (combined_impact / total_unfiltered_raw * 100.0) if total_unfiltered_raw > 0 else 0.0

            # Improved metrics display
            top_cols = responsive_columns(self.responsive, desktop=2, tablet=1, phone=1)

            with top_cols[0]:
                st.markdown("**Base Sales (No Filters)**")
                left_metrics = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                with left_metrics[0]:
                    st.metric("💰 Raw Total", format_currency(total_unfiltered_raw), border=True)
                with left_metrics[1 % len(left_metrics)]:
                    st.metric("🚫 After Blocking", format_currency(total_blocked_only), border=True)

            with top_cols[1 % len(top_cols)]:
                st.markdown("**With Category Filters**")
                right_metrics = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                with right_metrics[0]:
                    st.metric("📊 Category Only", format_currency(total_category_only), border=True)
                with right_metrics[1 % len(right_metrics)]:
                    st.metric("✅ Both Applied", format_currency(total_both), border=True)

            # Impact summary
            st.markdown("**Impact Summary:**")
            impact_cols = responsive_columns(self.responsive, desktop=3, tablet=2, phone=1)

            with impact_cols[0]:
                st.write(f"**Blocked Impact:**")
                st.write(f"- Amount: PKR {blocked_impact:,.0f}")
                st.write(f"- Percentage: {blocked_pct:.1f}%")

            with impact_cols[1 % len(impact_cols)]:
                st.write(f"**Category Impact:**")
                st.write(f"- Amount: PKR {category_impact:,.0f}")
                st.write(f"- Percentage: {category_pct:.1f}%")

            with impact_cols[2 % len(impact_cols)]:
                st.write(f"**Combined Impact:**")
                st.write(f"- Amount: PKR {combined_impact:,.0f}")
                st.write(f"- Percentage: {combined_pct:.1f}%")


            if (
                df_unfiltered_raw is not None
                and not df_unfiltered_raw.empty
                and df_blocked_only is not None
                and not df_blocked_only.empty
                and df_category_only is not None
                and not df_category_only.empty
                and df_both is not None
                and not df_both.empty
            ):
                base = df_unfiltered_raw[["shop_id", "shop_name", "total_Nt_amount"]].rename(
                    columns={"total_Nt_amount": "unfiltered_raw"}
                )
                out = (
                    base.merge(
                        df_blocked_only[["shop_id", "total_Nt_amount"]].rename(columns={"total_Nt_amount": "blocked_only"}),
                        on="shop_id",
                        how="left",
                    )
                    .merge(
                        df_category_only[["shop_id", "total_Nt_amount"]].rename(columns={"total_Nt_amount": "category_only"}),
                        on="shop_id",
                        how="left",
                    )
                    .merge(
                        df_both[["shop_id", "total_Nt_amount"]].rename(columns={"total_Nt_amount": "blocked_plus_category"}),
                        on="shop_id",
                        how="left",
                    )
                )
                for col in ["unfiltered_raw", "blocked_only", "category_only", "blocked_plus_category"]:
                    out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
                out["Blocked Impact (PKR)"] = out["unfiltered_raw"] - out["blocked_only"]
                out["Category Impact (PKR)"] = out["unfiltered_raw"] - out["category_only"]
                out["Total Impact (PKR)"] = out["unfiltered_raw"] - out["blocked_plus_category"]
                out["Total Impact (%)"] = (
                    out["Total Impact (PKR)"] / out["unfiltered_raw"].replace(0, pd.NA) * 100.0
                ).fillna(0.0).round(2)

                show = out.rename(
                    columns={
                        "shop_name": "Branch",
                        "unfiltered_raw": "Unfiltered (Raw)",
                        "blocked_only": "Blocked Only",
                        "category_only": "Category Only",
                        "blocked_plus_category": "Blocked + Category",
                    }
                ).sort_values("shop_id")

                st.subheader("🏪 Branch-wise Impact Breakdown")
                st.dataframe(show, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=340, tablet=300, phone=240, kind="default"))
            else:
                st.info("No branch impact data available for this period/branches.")


        with main_tab3:
            st.subheader("🚫 Blocked Transactions Analysis")
            st.caption("Transactions excluded by Blocked Names or Blocked Comments.")

            df_impact = get_cached_blocked_impact(self.start_date, self.end_date, self.selected_branches)
            if df_impact is None or df_impact.empty:
                st.info("No blocked transactions found for this period (or blocked lists are empty).")
            else:
                df_impact = df_impact.copy()
                df_impact["Nt_amount"] = pd.to_numeric(df_impact["Nt_amount"], errors="coerce").fillna(0.0)
                total_impact = float(df_impact["Nt_amount"].sum())
                count_impact = int(len(df_impact))

                # Add a column to show blocking reason
                def get_block_reason(row):
                    """Identify which list caused the block"""
                    if row['Cust_name'] in BLOCKED_NAMES:
                        return f"Name: '{row['Cust_name']}'"
                    elif row['Additional_Comments'] in BLOCKED_COMMENTS:
                        return f"Comment: '{row['Additional_Comments']}'"
                    return "Unknown"

                df_impact["Block_Reason"] = df_impact.apply(get_block_reason, axis=1)

                # Show summary metrics
                block_cols = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                with block_cols[0]:
                    st.metric("💰 Total Blocked Sales", format_currency(total_impact), border=True)
                with block_cols[1 % len(block_cols)]:
                    st.metric("🚫 Blocked Transactions", f"{count_impact:,}", border=True)

                # Branch summary
                st.markdown("**By Branch:**")
                df_branch_sum = (
                    df_impact.groupby(["shop_id", "shop_name"], as_index=False)["Nt_amount"]
                    .agg(blocked_sales_sum="sum", blocked_tx_count="count")
                    .sort_values("blocked_sales_sum", ascending=False)
                )
                df_branch_sum["blocked_sales_sum"] = df_branch_sum["blocked_sales_sum"].apply(lambda x: f"PKR {x:,.0f}")
                df_branch_sum.columns = ["Branch ID", "Branch Name", "Blocked Sales", "Transaction Count"]
                st.dataframe(df_branch_sum, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=260, tablet=240, phone=220, kind="compact"))

                # Blocking rules breakdown
                st.markdown("**By Blocking Rule:**")
                rule_summary = df_impact["Block_Reason"].value_counts().reset_index()
                rule_summary.columns = ["Blocked Item", "Transaction Count"]

                # Add sales amount per rule
                sales_by_rule = df_impact.groupby("Block_Reason")["Nt_amount"].sum().reset_index()
                sales_by_rule.columns = ["Blocked Item", "Total Sales (PKR)"]
                sales_by_rule["Total Sales (PKR)"] = sales_by_rule["Total Sales (PKR)"].apply(lambda x: f"PKR {x:,.0f}")

                rule_detailed = rule_summary.merge(sales_by_rule, on="Blocked Item")
                st.dataframe(rule_detailed, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=260, tablet=240, phone=220, kind="compact"))

                # Detailed transaction view
                with st.expander("📋 View All Blocked Transactions", expanded=False):
                    st.markdown("**Complete Blocked Transaction List:**")

                    # Prepare display columns
                    df_display = df_impact.copy()
                    df_display["sale_date"] = pd.to_datetime(df_display["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d")
                    df_display["Nt_amount"] = df_display["Nt_amount"].apply(lambda x: f"PKR {x:,.0f}")

                    display_cols = {
                        "shop_name": "Branch",
                        "sale_date": "Date",
                        "Cust_name": "Customer Name",
                        "Additional_Comments": "Comments",
                        "Block_Reason": "Why Blocked",
                        "Nt_amount": "Sales Amount"
                    }

                    df_show = df_display[list(display_cols.keys())].rename(columns=display_cols)
                    df_show = df_show.sort_values("Date", ascending=False)

                    st.dataframe(df_show, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=500, tablet=380, phone=300, kind="tall"))

        with main_tab4:
            st.subheader("📦 Unmapped Products")
            st.caption("Products making sales but not linked to any category in TempProductBarcode.")
            df_unmapped = get_cached_unmapped_products(self.start_date, self.end_date, self.selected_branches)
            if df_unmapped is None or df_unmapped.empty:
                st.success("✅ No unmapped products detected for this period.")
            else:
                df_unmapped = df_unmapped.copy()
                df_unmapped["total_sales"] = pd.to_numeric(df_unmapped.get("total_sales"), errors="coerce").fillna(0.0)
                df_unmapped["total_qty"] = pd.to_numeric(df_unmapped.get("total_qty"), errors="coerce").fillna(0.0)

                # Summary metrics
                total_unmapped_sales = df_unmapped["total_sales"].sum()
                total_unmapped_qty = df_unmapped["total_qty"].sum()
                unmapped_count = len(df_unmapped)

                unmapped_cols = responsive_columns(self.responsive, desktop=3, tablet=2, phone=1)
                with unmapped_cols[0]:
                    st.metric("💰 Sales", f"PKR {total_unmapped_sales:,.0f}", border=True)
                with unmapped_cols[1 % len(unmapped_cols)]:
                    st.metric("📦 Qty", f"{total_unmapped_qty:,.0f}", border=True)
                with unmapped_cols[2 % len(unmapped_cols)]:
                    st.metric("🔗 Products", f"{unmapped_count}", border=True)

                # Display table
                st.markdown("**Unmapped Product Details:**")
                df_display_unmapped = df_unmapped.copy()
                if "total_sales" in df_display_unmapped.columns:
                    df_display_unmapped["total_sales"] = df_display_unmapped["total_sales"].apply(lambda x: f"PKR {x:,.0f}")
                st.dataframe(df_display_unmapped, width="stretch", hide_index=True, height=clamp_dataframe_height(self.responsive, desktop=350, tablet=300, phone=240, kind="default"))
