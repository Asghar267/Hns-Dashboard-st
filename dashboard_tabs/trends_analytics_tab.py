"""
Trends & Analytics Tab (Modular)
Expanded implementation aligned with archive/hns_dashboard_imported.py.
"""

from __future__ import annotations

from calendar import month_name as _mn
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    import altair as alt
except Exception:
    alt = None

try:
    from streamlit_extras.metric_cards import style_metric_cards
except Exception:
    style_metric_cards = None

from modules.database import (
    get_cached_branch_summary,
    get_cached_daily_sales,
    get_cached_monthly_sales,
    get_cached_product_monthly_sales,
    get_cached_product_monthly_sales_by_product,
    get_cached_daily_sales_by_products,
)
from modules.utils import format_currency, perf_trace
from modules.visualization import (
    create_monthly_sales_trend,
    create_forecast_with_ci,
    create_product_time_series,
)
from modules.responsive import (
    apply_plotly_responsive_layout,
    clamp_dataframe_height,
    get_responsive_context,
    responsive_columns,
)


def month_name(year: int, month: int) -> str:
    try:
        return _mn[month] + f" {year}"
    except Exception:
        return f"{year}-{month:02d}"


def render_table(
    df: pd.DataFrame,
    width: str = "stretch",
    height: Optional[int] = None,
    hide_index: bool = True,
):
    if df is None or df.empty:
        st.info("No data to display.")
        return
    ctx = get_responsive_context()
    st.dataframe(
        df,
        width=width,
        height=clamp_dataframe_height(
            ctx,
            desktop=height,
            tablet=max(220, int((height or 420) * 0.82)),
            phone=max(200, int((height or 420) * 0.68)),
            kind="default" if height is None else "compact",
        ),
        hide_index=hide_index,
    )


class TrendsAnalyticsTab:
    def __init__(
        self,
        start_date: str,
        end_date: str,
        selected_branches: list[int],
        data_mode: str,
        target_year: Optional[int] = None,
        target_month: Optional[int] = None,
        branch_name_map: Optional[dict[int, str]] = None,
        df_line_item: Optional[pd.DataFrame] = None,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.target_year = target_year
        self.target_month = target_month
        self.branch_name_map = branch_name_map or {
            2: "Khadda Main Branch",
            3: "FESTIVAL",
            4: "Rahat Commercial",
            6: "TOWER",
            8: "North Nazimabad",
            10: "MALIR",
            14: "FESTIVAL 2",
        }
        self.df_line_item = df_line_item if df_line_item is not None else pd.DataFrame()
        self.responsive = get_responsive_context()

    def render(self) -> None:
        st.header("Trends & Analytics")

        with perf_trace("Trends fetch (summary+trends)", "db"):
            df_branch = get_cached_branch_summary(self.start_date, self.end_date, self.selected_branches, self.data_mode)
            df_monthly = get_cached_monthly_sales(self.start_date, self.end_date, self.selected_branches, self.data_mode)
            df_daily = get_cached_daily_sales(self.start_date, self.end_date, self.selected_branches, self.data_mode)

        st.subheader("Performance Summary")
        if df_branch is not None and not df_branch.empty:
            fig = px.bar(
                df_branch,
                x="shop_name",
                y="total_Nt_amount",
                title="Branch Sales Comparison",
                labels={"shop_name": "Branch", "total_Nt_amount": "Sales (PKR)"},
                color="total_Nt_amount",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(apply_plotly_responsive_layout(fig, self.responsive, desktop_height=400, tablet_height=340, phone_height=300), width="stretch")

            try:
                forecast_method = st.selectbox(
                    "Forecast method",
                    options=["simple", "prophet"],
                    index=0,
                    help="Prophet requires the 'prophet' package to be installed.",
                )
                forecast_horizon = st.slider("Forecast horizon (days)", 1, 30, 7)

                trend_cols = responsive_columns(self.responsive, desktop=2, tablet=1, phone=1)
                with trend_cols[0]:
                    trend_fig = create_monthly_sales_trend(df_monthly, periods=24, rolling=3)
                    st.plotly_chart(apply_plotly_responsive_layout(trend_fig, self.responsive, desktop_height=420, tablet_height=360, phone_height=320), width="stretch")
                with trend_cols[1 % len(trend_cols)]:
                    forecast_fig = create_forecast_with_ci(
                        df_daily, periods_ahead=forecast_horizon, method=forecast_method
                    )
                    st.plotly_chart(apply_plotly_responsive_layout(forecast_fig, self.responsive, desktop_height=420, tablet_height=360, phone_height=320), width="stretch")
            except Exception as e:
                st.warning(f"Could not load trend/forecast data: {e}")
        else:
            st.info("No branch summary data for this period.")

        st.markdown("---")
        st.subheader("Product Comparison - Current vs Previous Month")

        if self.target_year and self.target_month:
            curr_year = int(self.target_year)
            curr_month = int(self.target_month)
        else:
            end_dt = pd.to_datetime(self.end_date, errors="coerce")
            if pd.isna(end_dt):
                end_dt = pd.Timestamp.today()
            curr_year = int(end_dt.year)
            curr_month = int(end_dt.month)

        if curr_month == 1:
            prev_year, prev_month = curr_year - 1, 12
        else:
            prev_year, prev_month = curr_year, curr_month - 1

        df_curr_all = get_cached_product_monthly_sales(curr_year, curr_month, self.selected_branches, self.data_mode)
        df_prev_all = get_cached_product_monthly_sales(prev_year, prev_month, self.selected_branches, self.data_mode)

        st.markdown("---")
        st.subheader("Line Item Name - Current Month")
        top_n_products = st.number_input("Top N items to show", min_value=1, max_value=500, value=15)

        if df_curr_all is None or df_curr_all.empty:
            df_curr_all = pd.DataFrame(columns=["Product", "Total_Sales", "Total_Qty"])
        else:
            df_curr_all = df_curr_all.rename(
                columns={"Product": "Category", "Total_Sales": "Current_Sales", "Total_Qty": "Current_Qty"}
            )

        if not df_curr_all.empty:
            allowed_line_items = [
                "SALES - BAR B Q",
                "SALES - CHINESE",
                "SALES - FAST FOOD",
                "SALES - HANDI",
                "SALES - JUICES SHAKES & DESSERTS",
                "SALES - KARAHI",
                "SALES - TANDOOR",
                "SALES - ROLL",
                "SALES - NASHTA",
                "Deal",
                "Deals",
                "Breakfast",
                "Sales - Beverages",
                "SALES - BEVERAGES",
                "Sales Side Orders",
                "SALES SIDE ORDERS",
                "SALES - SIDE ORDER",
            ]
            df_curr_all["__cat_norm"] = (
                df_curr_all["Category"].astype(str).str.upper().str.replace(r"\s+", " ", regex=True).str.strip()
            )
            allowed_norm = {str(x).upper().strip() for x in allowed_line_items}
            df_curr_all = df_curr_all[df_curr_all["__cat_norm"].isin(allowed_norm)].drop(columns=["__cat_norm"])
            df_top_categories = df_curr_all[["Category", "Current_Sales", "Current_Qty"]].copy()
            df_top_categories = df_top_categories.sort_values("Current_Sales", ascending=False).head(top_n_products)

            display_cat = df_top_categories.copy()
            display_cat["Total Sales"] = display_cat["Current_Sales"].apply(lambda x: format_currency(x))
            display_cat["Total Qty"] = display_cat["Current_Qty"].apply(lambda x: f"{int(x):,}")
            display_cat = display_cat[["Category", "Total Sales", "Total Qty"]]

            render_table(display_cat, width="stretch", height=300)

            fig_cat = px.bar(
                df_top_categories,
                x="Current_Sales",
                y="Category",
                orientation="h",
                title=f"Top {len(df_top_categories)} Line Item Names - {month_name(curr_year, curr_month)}",
                labels={"Current_Sales": "Sales (PKR)", "Category": "Line Item Name"},
                color="Current_Sales",
                color_continuous_scale="Viridis",
            )
            fig_cat.update_traces(texttemplate=" %{x:,.0f}", textposition="inside")
            fig_cat.update_layout(showlegend=False)
            st.plotly_chart(apply_plotly_responsive_layout(fig_cat, self.responsive, desktop_height=350, tablet_height=320, phone_height=280), width="stretch")
        else:
            st.info("No current month category data available for Top Line Item Names")

        st.markdown("---")
        st.subheader("Top Products (by Product Name) - Current Month")

        df_products_curr = get_cached_product_monthly_sales_by_product(
            curr_year, curr_month, self.selected_branches, self.data_mode, category=None
        )

        if df_products_curr is None or df_products_curr.empty:
            st.info("No current month product-level data available")
        else:
            df_products_curr = df_products_curr.rename(
                columns={"Product": "Product", "Total_Sales": "Current_Sales", "Total_Qty": "Current_Qty"}
            )

            df_top_products = df_products_curr[["Product", "Current_Sales", "Current_Qty"]].copy()
            df_top_products = df_top_products.sort_values("Current_Sales", ascending=False).head(top_n_products)

            display_top = df_top_products.copy()
            display_top["Total Sales"] = display_top["Current_Sales"].apply(lambda x: format_currency(x))
            display_top["Total Qty"] = display_top["Current_Qty"].apply(lambda x: f"{int(x):,}")
            display_top = display_top[["Product", "Total Sales", "Total Qty"]]

            render_table(display_top, width="stretch", height=350)

            fig_top = px.bar(
                df_top_products,
                x="Current_Sales",
                y="Product",
                orientation="h",
                title=f"Top {len(df_top_products)} Products - {month_name(curr_year, curr_month)}",
                labels={"Current_Sales": "Sales (PKR)", "Product": "Product"},
                color="Current_Sales",
                color_continuous_scale="Greens",
            )
            fig_top.update_traces(texttemplate=" %{x:,.0f}", textposition="inside")
            fig_top.update_layout(showlegend=False)
            st.plotly_chart(
                apply_plotly_responsive_layout(fig_top, self.responsive, desktop_height=400, tablet_height=340, phone_height=300),
                width="stretch",
            )

            try:
                allowed_line_items = [
                    "SALES - BAR B Q",
                    "SALES - CHINESE",
                    "SALES - FAST FOOD",
                    "SALES - HANDI",
                    "SALES - JUICES SHAKES & DESSERTS",
                    "SALES - KARAHI",
                    "SALES - TANDOOR",
                    "SALES - ROLL",
                    "SALES - NASHTA",
                    "Deal",
                    "Breakfast",
                    "Sales - Beverages",
                    "SALES - BEVERAGES",
                    "Sales Side Orders",
                    "SALES SIDE ORDERS",
                    "SALES - SIDE ORDER",
                ]
                allowed_products = set()
                try:
                    for cat in allowed_line_items:
                        df_cat = get_cached_product_monthly_sales_by_product(
                            curr_year, curr_month, self.selected_branches, self.data_mode, category=cat
                        )
                        if df_cat is not None and not df_cat.empty and "Product" in df_cat.columns:
                            allowed_products.update(df_cat["Product"].dropna().astype(str).tolist())
                except Exception:
                    allowed_products = set()

                df_products_for_trends = df_products_curr.copy()
                if allowed_products:
                    df_products_for_trends = df_products_for_trends[
                        df_products_for_trends["Product"].isin(allowed_products)
                    ]

                df_products_for_trends = df_products_for_trends[
                    ~df_products_for_trends["Product"].str.contains("cut in", case=False, na=False)
                ]
                df_products_for_trends = df_products_for_trends[df_products_for_trends["Current_Sales"] > 0]

                df_top_10 = df_products_for_trends.sort_values("Current_Sales", ascending=False).head(10)
                top_product_list = df_top_10["Product"].tolist()

                df_bottom_10 = df_products_for_trends[["Product", "Current_Sales", "Current_Qty"]].copy()
                df_bottom_10 = df_bottom_10.sort_values("Current_Sales", ascending=True).head(10)
                bottom_product_list = df_bottom_10["Product"].tolist()

                st.markdown("**Top 10 Products - Daily Sales Trend**")
                top_selected = st.multiselect(
                    "Top 10 chart products",
                    options=sorted(df_products_for_trends["Product"].dropna().astype(str).unique().tolist()),
                    default=top_product_list,
                    key="top10_products_filter",
                )
                if st.button("Reset Top 10 Highest", key="reset_top10"):
                    st.session_state["top10_products_filter"] = top_product_list
                    top_selected = top_product_list

                if top_selected:
                    st.markdown("**Selected (Top Chart):**")
                    st.write(", ".join(top_selected))

                if top_selected:
                    df_top_trend = get_cached_daily_sales_by_products(
                        self.start_date, self.end_date, self.selected_branches, self.data_mode, top_selected
                    )
                    if df_top_trend is not None and not df_top_trend.empty:
                        prod_col = "Product" if "Product" in df_top_trend.columns else "product_name"
                        date_col = "day" if "day" in df_top_trend.columns else (
                            "date" if "date" in df_top_trend.columns else None
                        )
                        if date_col:
                            df_top_trend[date_col] = pd.to_datetime(df_top_trend[date_col])
                            fig_top_trend = px.line(
                                df_top_trend,
                                x=date_col,
                                y="total_Nt_amount",
                                color=prod_col,
                                markers=True,
                                title="Top 10 Products - Daily Sales",
                                labels={"total_Nt_amount": "Sales (PKR)", prod_col: "Product"},
                            )
                            fig_top_trend.update_layout(hovermode="x unified")
                            fig_top_trend.update_yaxes(tickformat=",.0f")
                            st.plotly_chart(
                                apply_plotly_responsive_layout(fig_top_trend, self.responsive, desktop_height=420, tablet_height=360, phone_height=320),
                                width="stretch",
                            )
                        else:
                            st.info("Info: Daily trend data missing date column for top products.")
                else:
                    st.info("Info: No top products available for trend chart.")

                st.markdown("---")
                st.markdown("**Bottom 10 Products - Daily Sales Trend**")
                bottom_selected = st.multiselect(
                    "Bottom 10 chart products",
                    options=sorted(df_products_for_trends["Product"].dropna().astype(str).unique().tolist()),
                    default=bottom_product_list,
                    key="bottom10_products_filter",
                )
                if st.button("Reset Bottom 10 Lowest", key="reset_bottom10"):
                    st.session_state["bottom10_products_filter"] = bottom_product_list
                    bottom_selected = bottom_product_list

                if bottom_selected:
                    st.markdown("**Selected (Bottom Chart):**")
                    st.write(", ".join(bottom_selected))

                if bottom_selected:
                    df_bottom_trend = get_cached_daily_sales_by_products(
                        self.start_date, self.end_date, self.selected_branches, self.data_mode, bottom_selected
                    )
                    if df_bottom_trend is not None and not df_bottom_trend.empty:
                        prod_col = "Product" if "Product" in df_bottom_trend.columns else "product_name"
                        date_col = "day" if "day" in df_bottom_trend.columns else (
                            "date" if "date" in df_bottom_trend.columns else None
                        )
                        if date_col:
                            df_bottom_trend[date_col] = pd.to_datetime(df_bottom_trend[date_col])
                            fig_bottom_trend = px.line(
                                df_bottom_trend,
                                x=date_col,
                                y="total_Nt_amount",
                                color=prod_col,
                                markers=True,
                                title="Bottom 10 Products - Daily Sales",
                                labels={"total_Nt_amount": "Sales (PKR)", prod_col: "Product"},
                            )
                            fig_bottom_trend.update_layout(hovermode="x unified")
                            fig_bottom_trend.update_yaxes(tickformat=",.0f")
                            st.plotly_chart(
                                apply_plotly_responsive_layout(fig_bottom_trend, self.responsive, desktop_height=420, tablet_height=360, phone_height=320),
                                width="stretch",
                            )
                        else:
                            st.info("Info: Daily trend data missing date column for bottom products.")
                else:
                    st.info("Info: No bottom products available for trend chart.")

            except Exception as e:
                st.warning(f"Could not load product trend charts: {e}")

            st.markdown("---")
            st.subheader("Product Explorer")
            if "df_products_for_trends" in locals():
                all_products = df_products_for_trends["Product"].dropna().astype(str).unique().tolist()
            else:
                all_products = df_products_curr["Product"].dropna().astype(str).unique().tolist()

            if all_products:
                selected_prod = st.selectbox("Product to view", options=sorted(all_products), index=0)
                try:
                    df_sel = get_cached_daily_sales_by_products(
                        self.start_date, self.end_date, self.selected_branches, self.data_mode, [selected_prod]
                    )
                    prod_fig = create_product_time_series(df_sel, selected_prod, agg="daily", show_qty=True, rolling=7)
                    st.plotly_chart(
                        apply_plotly_responsive_layout(prod_fig, self.responsive, desktop_height=420, tablet_height=360, phone_height=320),
                        width="stretch",
                    )
                except Exception as e:
                    st.warning(f"Could not load detailed series for {selected_prod}: {e}")
            else:
                st.info("Info: No products available to view.")

            st.markdown("---")
            st.subheader("Low-performing Products & Line Items")
            low_n = st.number_input("Show bottom N products/line-items", min_value=1, max_value=100, value=5)

            try:
                df_bottom_products = df_products_curr[["Product", "Current_Sales", "Current_Qty"]].copy()
                df_bottom_products = df_bottom_products.sort_values("Current_Sales", ascending=True).head(low_n)
                if not df_bottom_products.empty:
                    low_cols = responsive_columns(self.responsive, desktop=2, tablet=1, phone=1)
                    with low_cols[0]:
                        st.write("Bottom products by sales")
                        render_table(
                            df_bottom_products.assign(
                                Current_Sales=lambda d: d["Current_Sales"].apply(format_currency)
                            ),
                            width="stretch",
                            height=200,
                        )
                    with low_cols[1 % len(low_cols)]:
                        fig_low = px.bar(
                            df_bottom_products,
                            x="Current_Sales",
                            y="Product",
                            orientation="h",
                            labels={"Current_Sales": "Sales (PKR)", "Product": "Product"},
                            color="Current_Sales",
                            color_continuous_scale="Reds",
                        )
                        fig_low.update_layout(showlegend=False)
                        st.plotly_chart(
                            apply_plotly_responsive_layout(fig_low, self.responsive, desktop_height=300, tablet_height=280, phone_height=260),
                            width="stretch",
                        )
            except Exception:
                pass

            try:
                df_bottom_cats = df_curr_all.rename(
                    columns={"Category": "Category", "Current_Sales": "Current_Sales"}
                )[["Category", "Current_Sales", "Current_Qty"]].copy()
                df_bottom_cats = df_bottom_cats.sort_values("Current_Sales", ascending=True).head(low_n)
                if not df_bottom_cats.empty:
                    st.write("Bottom line-item names by sales")
                    render_table(
                        df_bottom_cats.assign(Current_Sales=lambda d: d["Current_Sales"].apply(format_currency)),
                        width="stretch",
                        height=200,
                    )
            except Exception:
                pass

        st.markdown("---")
        st.subheader("Comparison Table")

        categories = []
        try:
            if not self.df_line_item.empty:
                categories = sorted(self.df_line_item["product"].dropna().unique().tolist())
        except Exception:
            categories = []

        selected_category = st.selectbox("Select Category (Line Item)", options=["All"] + categories, index=0)

        branch_filter_options = [
            "All",
            self.branch_name_map.get(2, "Khadda Main Branch"),
            self.branch_name_map.get(3, "FESTIVAL"),
            self.branch_name_map.get(4, "Rahat Commercial"),
            self.branch_name_map.get(6, "TOWER"),
            self.branch_name_map.get(8, "North Nazimabad"),
            self.branch_name_map.get(10, "MALIR"),
            self.branch_name_map.get(14, "FESTIVAL 2"),
        ]
        if self.responsive.is_phone:
            branch_option_comp = st.selectbox("Branch Filter", options=branch_filter_options, index=0)
        else:
            branch_option_comp = st.radio(
                "Branch Filter",
                options=branch_filter_options,
                index=0,
                horizontal=True,
            )
        if branch_option_comp == "All":
            branch_ids_query = self.selected_branches
        else:
            branch_ids_query = [k for k, v in self.branch_name_map.items() if v == branch_option_comp]

        if selected_category and selected_category != "All":
            df_curr = get_cached_product_monthly_sales_by_product(
                curr_year, curr_month, branch_ids_query, self.data_mode, category=selected_category
            )
            df_prev = get_cached_product_monthly_sales_by_product(
                prev_year, prev_month, branch_ids_query, self.data_mode, category=selected_category
            )
        else:
            df_curr = get_cached_product_monthly_sales_by_product(
                curr_year, curr_month, branch_ids_query, self.data_mode, category=None
            )
            df_prev = get_cached_product_monthly_sales_by_product(
                prev_year, prev_month, branch_ids_query, self.data_mode, category=None
            )

        if df_curr is None or df_curr.empty:
            df_curr = pd.DataFrame(columns=["Product", "Current_Sales", "Current_Qty"])
        else:
            df_curr = df_curr.rename(
                columns={"Product": "Product", "Total_Sales": "Current_Sales", "Total_Qty": "Current_Qty"}
            )

        if df_prev is None or df_prev.empty:
            df_prev = pd.DataFrame(columns=["Product", "Previous_Sales", "Previous_Qty"])
        else:
            df_prev = df_prev.rename(
                columns={"Product": "Product", "Total_Sales": "Previous_Sales", "Total_Qty": "Previous_Qty"}
            )

        df_comp = pd.merge(
            df_curr[["Product", "Current_Sales", "Current_Qty"]],
            df_prev[["Product", "Previous_Sales", "Previous_Qty"]],
            on="Product",
            how="outer",
        ).fillna(0)

        df_comp["Balance"] = df_comp["Current_Qty"] - df_comp["Previous_Qty"]
        df_comp["Achieved"] = df_comp["Current_Qty"] >= df_comp["Previous_Qty"]

        df_comp_display = df_comp.sort_values("Current_Sales", ascending=False)

        curr_label_sales = f"{month_name(curr_year, curr_month)} Sales"
        curr_label_qty = f"{month_name(curr_year, curr_month)} Qty"
        prev_label_sales = f"{month_name(prev_year, prev_month)} Sales"
        prev_label_qty = f"{month_name(prev_year, prev_month)} Qty"

        df_display = df_comp_display.copy()
        df_display[curr_label_sales] = df_display["Current_Sales"].apply(lambda x: format_currency(x))
        df_display[curr_label_qty] = df_display["Current_Qty"].apply(lambda x: f"{int(x):,}")
        df_display[prev_label_sales] = df_display["Previous_Sales"].apply(lambda x: format_currency(x))
        df_display[prev_label_qty] = df_display["Previous_Qty"].apply(lambda x: f"{int(x):,}")
        df_display["Balance"] = df_display["Balance"].apply(lambda x: f"{int(x):+,}")
        df_display["Achievement"] = df_display["Achieved"].apply(lambda v: "Yes" if v else "No")

        cols = [
            "Product",
            curr_label_sales,
            curr_label_qty,
            prev_label_sales,
            prev_label_qty,
            "Balance",
            "Achievement",
        ]
        df_display = df_display[cols]

        st.markdown(
            f"**Comparison:** {month_name(curr_year, curr_month)} (Current) vs {month_name(prev_year, prev_month)} (Previous)"
        )
        if df_display.empty:
            st.info("No product sales data available for these months")
        else:
            render_table(df_display, width="stretch", height=600)

