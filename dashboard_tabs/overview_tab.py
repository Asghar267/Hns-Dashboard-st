"""
Overview Tab Module
Handles the main dashboard overview functionality
"""

import pandas as pd
from typing import List, Optional
import streamlit as st
from datetime import datetime

# Import from existing modules
from modules.database import (
    get_cached_branch_summary,
    get_cached_branch_days_since_last_sale,
    get_cached_ot_data,
    get_cached_order_types,
    get_cached_order_type_others_breakdown,
    get_cached_order_type_others_order_takers,
    get_cached_daily_sales_by_branch,
    get_cached_product_monthly_sales_by_product,
    get_cached_targets,
    get_cached_top_products_overview,
)
from modules.utils import (
    format_currency,
    format_percentage,
    exclude_employee_names,
    perf_trace,
)
from modules.visualization import (
    create_achievement_gauge,
    create_waterfall_chart,
    create_heatmap,
    create_sankey_diagram
)
from modules.responsive import (
    apply_plotly_responsive_layout,
    clamp_dataframe_height,
    get_responsive_context,
    responsive_columns,
)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_branch_summary(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_branch_summary(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_branch_health(branches: tuple[int, ...]):
    return get_cached_branch_days_since_last_sale(list(branches))


@st.cache_data(ttl=300, show_spinner=False)
def _cached_ot_data(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_ot_data(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_order_types(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_order_types(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_order_types_others(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_order_type_others_breakdown(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_order_types_others_ot(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_order_type_others_order_takers(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_daily_sales(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_daily_sales_by_branch(start_date, end_date, list(branches), mode)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_top_products(start_date: str, end_date: str, branches: tuple[int, ...], mode: str):
    return get_cached_top_products_overview(start_date, end_date, list(branches), mode, top_n=5)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_product_monthly_sales(year: int, month: int, branches: tuple[int, ...], mode: str, category: str | None = None):
    return get_cached_product_monthly_sales_by_product(year, month, list(branches), mode, category=category)


class OverviewTab:
    """Overview tab functionality"""
    
    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

        self._cache_epoch = st.session_state.get("mod_cache_epoch", 0)
        self._session_cache = st.session_state.setdefault("mod_cache", {})

        # Data will be fetched lazily to keep initial load fast.
        self.df_branch = None
        self.df_ot = None
        self.df_order_types = None
        self.responsive = get_responsive_context()

        # Targets for overview cards/charts (month derived from end_date)
        try:
            end_dt = pd.to_datetime(end_date, errors="coerce")
            if pd.isna(end_dt):
                end_dt = pd.Timestamp.today()
            self.target_year = int(end_dt.year)
            self.target_month = int(end_dt.month)
        except Exception:
            now = datetime.now()
            self.target_year = int(now.year)
            self.target_month = int(now.month)

        try:
            self.branch_targets, _, _, _ = get_cached_targets(self.target_year, self.target_month)
        except Exception:
            self.branch_targets = {}

    def _session_cached(self, key: str, loader):
        """Session-level cache wrapper to avoid refetches on reruns."""
        cache_key = f"{key}:{self._cache_epoch}"
        if cache_key in self._session_cache:
            return self._session_cache[cache_key]
        value = loader()
        self._session_cache[cache_key] = value
        return value
        
    def render_overview(self):
        """Render the main overview dashboard"""
        if self.df_branch is None:
            with perf_trace("Overview fetch (branch summary)", "db"):
                self.df_branch = self._session_cached(
                    "branch_summary",
                    lambda: _cached_branch_summary(
                        self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                    ),
                )

        st.header("Sales Overview")
        if self.df_branch.empty:
            st.info("No data available for selected filters")
            return
            
        # Add targets to branch data (display-only copy for overview)
        df_branch_display = self.df_branch.copy()
        df_branch_display['total_Nt_amount'] = df_branch_display['total_Nt_amount'].astype(float)

        # Add Monthly_Target if missing (needed by heatmap/waterfall/cards)
        if "Monthly_Target" not in df_branch_display.columns:
            df_branch_display["Monthly_Target"] = (
                df_branch_display["shop_id"].map(self.branch_targets).fillna(0).astype(float)
            )
        
        # Merge FESTIVAL (ID 3) + FESTIVAL 2 (ID 14) for overview cards
        festival_mask = df_branch_display['shop_id'] == 3
        festival2_mask = df_branch_display['shop_id'] == 14
        if festival_mask.any() and festival2_mask.any():
            festival2_sales = df_branch_display.loc[festival2_mask, 'total_Nt_amount'].sum()
            festival2_target = df_branch_display.loc[festival2_mask, 'Monthly_Target'].sum() if "Monthly_Target" in df_branch_display.columns else 0
            df_branch_display.loc[festival_mask, 'total_Nt_amount'] += festival2_sales
            if "Monthly_Target" in df_branch_display.columns:
                df_branch_display.loc[festival_mask, 'Monthly_Target'] += float(festival2_target)
            df_branch_display.loc[festival_mask, 'shop_name'] = "FESTIVAL"
            # Hide FESTIVAL 2 card in overview
            df_branch_display = df_branch_display.loc[~festival2_mask].copy()

        # Derived target columns
        if "Monthly_Target" in df_branch_display.columns:
            df_branch_display["Remaining_Target"] = df_branch_display["Monthly_Target"] - df_branch_display["total_Nt_amount"]
            df_branch_display["Achievement_%"] = df_branch_display.apply(
                lambda r: (r["total_Nt_amount"] / r["Monthly_Target"] * 100.0) if r["Monthly_Target"] > 0 else 0.0,
                axis=1,
            )

        # Summary Metrics
        total_sales = df_branch_display['total_Nt_amount'].sum()
        total_target = df_branch_display['Monthly_Target'].sum() if 'Monthly_Target' in df_branch_display.columns else 0
        total_remaining = total_target - total_sales
        overall_achievement = (total_sales / total_target * 100) if total_target > 0 else 0
        
        # Display metrics with custom styling
        self._render_summary_metrics(total_sales, total_target, total_remaining, overall_achievement)
        self._render_branch_health_widget()
        
        st.markdown("---")
        st.subheader("Top 5 Highlights")
        self._render_top_highlights()
        
        st.markdown("---")
        
        # Overall Performance (gauge) + Branch-wise Performance (heatmap) in one row
        st.subheader("Overall & Branch-wise Performance")
        charts = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
        with charts[0]:
            gauge_fig = create_achievement_gauge(overall_achievement, "Overall Achievement")
            st.plotly_chart(
                apply_plotly_responsive_layout(gauge_fig, self.responsive, desktop_height=360, tablet_height=340, phone_height=300),
                width="stretch",
            )
        with charts[min(1, len(charts) - 1)]:
            heatmap_fig = create_heatmap(df_branch_display)
            st.plotly_chart(
                apply_plotly_responsive_layout(heatmap_fig, self.responsive, desktop_height=420, tablet_height=360, phone_height=320),
                width="stretch",
            )
        
        # Individual branch cards
        self._render_branch_cards(df_branch_display)
        
        st.markdown("---")
        
        # Waterfall Chart for Target Breakdown
        st.subheader("Target Achievement Breakdown")
        waterfall_fig = create_waterfall_chart(df_branch_display)
        st.plotly_chart(
            apply_plotly_responsive_layout(waterfall_fig, self.responsive, desktop_height=420, tablet_height=360, phone_height=320),
            width="stretch",
        )
        
        st.markdown("---")
        self._render_daily_sales_by_branch()
        
        st.markdown("---")
        self._render_order_type_analysis()
        
        # Export Options
        st.markdown("---")
        self._render_export_options(df_branch_display)

    def _render_summary_metrics(self, total_sales: float, total_target: float, total_remaining: float, overall_achievement: float):
        """Render summary metrics cards"""
        metric_cols = responsive_columns(self.responsive, desktop=4, tablet=2, phone=1)

        with metric_cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Sales</div>
                    <div class="metric-value">{format_currency(total_sales)}</div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[1 % len(metric_cols)]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Target</div>
                    <div class="metric-value">{format_currency(total_target)}</div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[2 % len(metric_cols)]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Remaining</div>
                    <div class="metric-value">{format_currency(total_remaining)}</div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[3 % len(metric_cols)]:
            achievement_class = (
                'success-metric' if overall_achievement >= 100 
                else 'warning-metric' if overall_achievement >= 70 
                else 'danger-metric'
            )
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Achievement</div>
                    <div class="metric-value {achievement_class}">
                        {format_percentage(overall_achievement)}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def _render_branch_health_widget(self):
        """Render branch health diagnostics focused on recency."""
        st.subheader("Branch Health")
        df_health = self._session_cached(
            "overview_branch_health",
            lambda: _cached_branch_health(tuple(sorted(self.selected_branches))),
        )
        if df_health is None or df_health.empty:
            st.info("Branch health data is unavailable for current branch selection.")
            return

        max_days = int(df_health["days_since_last_sale"].max()) if "days_since_last_sale" in df_health.columns else 0
        stale_count = int((df_health["days_since_last_sale"] > 1).sum()) if "days_since_last_sale" in df_health.columns else 0
        cols = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
        with cols[0]:
            st.metric("Max Days Since Last Sale", f"{max_days}")
        with cols[1 % len(cols)]:
            st.metric("Branches Stale (>1 day)", f"{stale_count}")

        display = df_health.copy()
        display["last_sale_date"] = pd.to_datetime(display["last_sale_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        display["status"] = display["days_since_last_sale"].apply(
            lambda days: "Fresh" if int(pd.to_numeric(days, errors="coerce") or 0) <= 1 else ("Warning" if int(pd.to_numeric(days, errors="coerce") or 0) <= 7 else "Stale")
        )
        styler = display[["shop_id", "shop_name", "last_sale_date", "days_since_last_sale", "status"]].style.apply(
            lambda row: [
                (
                    "background-color: #d1fae5; color: #065f46; font-weight: 600;"
                    if int(pd.to_numeric(row["days_since_last_sale"], errors="coerce") or 0) <= 1
                    else (
                        "background-color: #fef3c7; color: #92400e; font-weight: 600;"
                        if int(pd.to_numeric(row["days_since_last_sale"], errors="coerce") or 0) <= 7
                        else "background-color: #fee2e2; color: #991b1b; font-weight: 600;"
                    )
                ) if col == "status" else ""
                for col in row.index
            ],
            axis=1,
        )
        self._render_table(styler, width="stretch", height=230)

    def _render_top_highlights(self):
        """Render top 5 highlights"""
        try:
            range_days = (pd.to_datetime(self.end_date) - pd.to_datetime(self.start_date)).days + 1
        except Exception:
            range_days = 0
        default_load = range_days <= 14 if range_days else True
        load_top_products = st.checkbox(
            "Load Top Products (heavy)",
            value=default_load,
            key="overview_load_top_products",
            help="Turn off to speed up initial load; turn on when you need top product details.",
        )

        top_cols = responsive_columns(self.responsive, desktop=3, tablet=2, phone=1)

        # Top 5 Chef Sales (by product revenue)
        with top_cols[0]:
            st.markdown("**Chef Sales - Top 5 Products**")
            if not load_top_products:
                st.caption("Skipped (toggle on to load).")
            else:
                with perf_trace("Overview fetch (top products)", "db"):
                    df_top_products = self._session_cached(
                        "overview_top_products",
                        lambda: _cached_top_products(
                            self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                        ),
                    )
                if df_top_products is not None and not df_top_products.empty:
                    df_top_products = df_top_products.rename(columns={"total_sales": "Sales"})
                    df_top_products["Sales"] = df_top_products["Sales"].apply(format_currency)
                    self._render_table(df_top_products[["product", "Sales"]], width="stretch", height=230)
                else:
                    st.info("No chef sales data")

        # Top 5 Line Item Sub-Products (product names)
        with top_cols[1 % len(top_cols)]:
            st.markdown("**Line Item Sub-Products - Top 5**")
            try:
                if not load_top_products:
                    st.caption("Skipped (toggle on to load).")
                else:
                    with perf_trace("Overview fetch (top items)", "db"):
                        df_top_items = self._session_cached(
                            "overview_top_items",
                            lambda: _cached_product_monthly_sales(
                                self.target_year, self.target_month, tuple(sorted(self.selected_branches)), self.data_mode, category=None
                            ),
                        )
                    if df_top_items is not None and not df_top_items.empty:
                        df_top_items = df_top_items.rename(columns={'Total_Sales': 'Sales'})
                        df_top_items = df_top_items.sort_values('Sales', ascending=False).head(5)
                        df_top_items['Sales'] = df_top_items['Sales'].apply(format_currency)
                        self._render_table(df_top_items[['Product', 'Sales']], width="stretch", height=230)
                    else:
                        st.info("No product data for current month")
            except Exception:
                st.info("No product data for current month")

        # Top 5 OT Sales
        with top_cols[2 % len(top_cols)]:
            st.markdown("**OT Sales - Top 5**")
            if self.df_ot is None:
                with perf_trace("Overview fetch (OT sales)", "db"):
                    self.df_ot = self._session_cached(
                        "overview_ot",
                        lambda: _cached_ot_data(
                            self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                        ),
                    )
                self.df_ot = exclude_employee_names(self.df_ot, "employee_name")
            if self.df_ot is not None and not self.df_ot.empty:
                df_top_ot = self.df_ot.sort_values('total_sale', ascending=False).head(5)
                df_top_ot['Sales'] = df_top_ot['total_sale'].apply(format_currency)
                self._render_table(df_top_ot[['employee_name', 'Sales']], width="stretch", height=230)
            else:
                st.info("No OT sales data")

    def _render_branch_cards(self, df_branch_display: pd.DataFrame):
        """Render individual branch performance cards"""
        cols = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
        for idx, (_, row) in enumerate(df_branch_display.iterrows()):
            with cols[idx % len(cols)]:
                with st.expander(f"📌 {row['shop_name']} (ID: {int(row['shop_id'])})", expanded=True):
                    # Metrics in a cleaner layout
                    branch_metric_cols = responsive_columns(self.responsive, desktop=2, tablet=2, phone=1)
                    branch_metric_cols[0].metric("Current Sales", format_currency(row['total_Nt_amount']))
                    if 'Monthly_Target' in row:
                        branch_metric_cols[1 % len(branch_metric_cols)].metric("Monthly Target", format_currency(row['Monthly_Target']))
                        branch_metric_cols[0].metric("Remaining", format_currency(row['Remaining_Target']))
                        branch_metric_cols[1 % len(branch_metric_cols)].metric("Achievement", format_percentage(row['Achievement_%']))

    def _render_daily_sales_by_branch(self):
        """Render daily sales by branch for last 30 days"""
        st.subheader("Daily Sales by Branch (Last 30 Days)")

        from datetime import date, timedelta
        last_30_end = date.today()
        last_30_start = last_30_end - timedelta(days=29)
        last_30_start_str = last_30_start.strftime("%Y-%m-%d")
        last_30_end_str = last_30_end.strftime("%Y-%m-%d")

        load_key = "overview_load_daily_branch"
        if load_key not in st.session_state:
            st.session_state[load_key] = False

        if st.button("Load Daily Sales by Branch (Last 30 Days)", key="overview_daily_branch_btn"):
            st.session_state[load_key] = True

        if not st.session_state[load_key]:
            st.caption("Click the button to load this section.")
            return

        try:
            with perf_trace("Overview fetch (daily by branch)", "db"):
                df_daily_branch = self._session_cached(
                    "overview_daily_branch",
                    lambda: _cached_daily_sales(
                        last_30_start_str, last_30_end_str, tuple(sorted(self.selected_branches)), self.data_mode
                    ),
                )
            if df_daily_branch.empty:
                st.info("No daily branch sales data for the last 30 days.")
            else:
                # Pivot to Date x Branch for easier viewing
                pivot_daily = (
                    df_daily_branch
                    .pivot_table(index='day', columns='shop_name', values='total_Nt_amount', aggfunc='sum')
                    .sort_index()
                    .fillna(0)
                )
                display_daily = pivot_daily.reset_index().rename(columns={'day': 'Date'})
                display_daily['Date'] = display_daily['Date'].dt.strftime("%Y-%m-%d")

                # Format sales columns
                for col in display_daily.columns:
                    if col != 'Date':
                        display_daily[col] = display_daily[col].apply(lambda x: format_currency(x))

                self._render_table(display_daily, width="stretch", height=450)
        except Exception as e:
            st.warning(f"Could not load daily branch sales (last 30 days): {e}")

    def _render_order_type_analysis(self):
        """Render order type analysis"""
        st.subheader("Order Type Distribution")
        if self.df_order_types is None:
            with perf_trace("Overview fetch (order types)", "db"):
                self.df_order_types = self._session_cached(
                    "overview_order_types",
                    lambda: _cached_order_types(
                        self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                    ),
                )

        if self.df_order_types is not None and not self.df_order_types.empty:
            # Sankey Diagram
            sankey_fig = create_sankey_diagram(self.df_order_types)
            st.plotly_chart(
                apply_plotly_responsive_layout(sankey_fig, self.responsive, desktop_height=520, tablet_height=420, phone_height=340),
                width="stretch",
            )
            
            # Order type metrics
            metric_cols = responsive_columns(self.responsive, desktop=3, tablet=2, phone=1)
            
            order_types_display = ['Food Panda', 'Delivery', 'Dine IN']
            for idx, ot in enumerate(order_types_display):
                ot_data = self.df_order_types[self.df_order_types['order_type'] == ot]
                if not ot_data.empty:
                    with metric_cols[idx % len(metric_cols)]:
                        sales = ot_data['total_sales'].iloc[0]
                        orders = ot_data['total_orders'].iloc[0]
                        st.metric(
                            f"{ot}",
                            format_currency(sales),
                            f"{orders:,} orders"
                        )
            
            # Detailed table
            with st.expander("Detailed Order Type Breakdown"):
                df_ot_display = self.df_order_types.copy()
                df_ot_display['total_sales_pct'] = (
                    df_ot_display['total_sales'] / df_ot_display['total_sales'].sum() * 100
                )
                
                # Format for display
                display_df = df_ot_display.copy()
                display_df['total_sales'] = display_df['total_sales'].apply(lambda x: format_currency(x))
                display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
                display_df['total_sales_pct'] = display_df['total_sales_pct'].apply(lambda x: f"{x:.1f}%")
                
                self._render_table(display_df[['order_type', 'total_orders', 'total_sales', 'total_sales_pct']], 
                    width="stretch")

                others_row = df_ot_display[df_ot_display["order_type"] == "Others"]
                if not others_row.empty:
                    with st.expander("Inspect 'Others' (what is inside)"):
                        df_others = self._session_cached(
                            "overview_order_types_others",
                            lambda: _cached_order_types_others(
                                self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                            ),
                        )

                        if df_others is None or df_others.empty:
                            st.info("No rows found inside 'Others' for the current filters/date range.")
                        else:
                            total_sales_all = float(df_ot_display["total_sales"].sum() or 0.0)
                            total_sales_others = float(others_row["total_sales"].iloc[0] or 0.0)

                            df_show = df_others.copy()
                            if total_sales_others > 0:
                                df_show["sales_pct_of_others"] = df_show["total_sales"] / total_sales_others * 100
                            else:
                                df_show["sales_pct_of_others"] = 0.0
                            if total_sales_all > 0:
                                df_show["sales_pct_of_total"] = df_show["total_sales"] / total_sales_all * 100
                            else:
                                df_show["sales_pct_of_total"] = 0.0

                            df_show["total_sales"] = df_show["total_sales"].apply(lambda x: format_currency(float(x)))
                            df_show["total_orders"] = df_show["total_orders"].apply(lambda x: f"{int(x):,}")
                            df_show["sales_pct_of_others"] = df_show["sales_pct_of_others"].apply(lambda x: f"{x:.1f}%")
                            df_show["sales_pct_of_total"] = df_show["sales_pct_of_total"].apply(lambda x: f"{x:.1f}%")

                            self._render_table(
                                df_show[["raw_order_type", "total_orders", "total_sales", "sales_pct_of_others", "sales_pct_of_total"]],
                                width="stretch",
                            )

                        st.markdown("#### Others by Order Taker")
                        df_others_ot = self._session_cached(
                            "overview_order_types_others_ot",
                            lambda: _cached_order_types_others_ot(
                                self.start_date, self.end_date, tuple(sorted(self.selected_branches)), self.data_mode
                            ),
                        )
                        if df_others_ot is None or df_others_ot.empty:
                            st.info("No order-taker rows found inside 'Others' for the current filters/date range.")
                        else:
                            df_ot_show = df_others_ot.copy()
                            total_sales_all = float(df_ot_display["total_sales"].sum() or 0.0)
                            total_sales_others = float(others_row["total_sales"].iloc[0] or 0.0)

                            if total_sales_others > 0:
                                df_ot_show["sales_pct_of_others"] = df_ot_show["total_sales"] / total_sales_others * 100
                            else:
                                df_ot_show["sales_pct_of_others"] = 0.0
                            if total_sales_all > 0:
                                df_ot_show["sales_pct_of_total"] = df_ot_show["total_sales"] / total_sales_all * 100
                            else:
                                df_ot_show["sales_pct_of_total"] = 0.0

                            df_ot_show["total_sales"] = df_ot_show["total_sales"].apply(lambda x: format_currency(float(x)))
                            df_ot_show["total_orders"] = df_ot_show["total_orders"].apply(lambda x: f"{int(x):,}")
                            df_ot_show["sales_pct_of_others"] = df_ot_show["sales_pct_of_others"].apply(lambda x: f"{x:.1f}%")
                            df_ot_show["sales_pct_of_total"] = df_ot_show["sales_pct_of_total"].apply(lambda x: f"{x:.1f}%")

                            self._render_table(
                                df_ot_show[["shop_name", "employee_name", "total_orders", "total_sales", "sales_pct_of_others", "sales_pct_of_total"]],
                                width="stretch",
                            )

    def _render_export_options(self, df_branch_display: pd.DataFrame):
        """Render export options"""
        st.subheader("Export Options")
        
        col1 = st.columns(1)[0]
        
        with col1:
            from modules.utils import export_to_excel
            excel_data = export_to_excel(df_branch_display, "Branch Summary")
            st.download_button(
                "Download Excel",
                excel_data,
                "branch_summary.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

    def _render_table(self, data, width: str = "stretch", height: Optional[int] = None, hide_index: bool = True):
        """Consistent dataframe rendering for readability across the dashboard."""
        kwargs = {
            "width": width,
            "hide_index": hide_index
        }
        kwargs["height"] = clamp_dataframe_height(
            self.responsive,
            desktop=height,
            tablet=max(220, int((height or 420) * 0.82)),
            phone=max(200, int((height or 420) * 0.68)),
            kind="default" if height is None else "compact",
        )
        st.dataframe(data, **kwargs)
