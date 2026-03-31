"""
Optimized Sales Dashboard - Complete Version
Features: Caching, Performance Improvements, Advanced Visualizations, Dark Mode
No Authentication Required
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pyodbc
from datetime import date, datetime, timedelta
import time
from calendar import monthrange
from typing import Dict, List, Tuple, Optional
import os
import json

# Import custom modules
from modules.database import (
    get_cached_branch_summary,
    get_cached_ot_data,
    get_cached_line_items,
    get_cached_order_types,
    get_cached_qr_sales,
    get_cached_product_monthly_sales,
    get_cached_product_monthly_sales_by_product,
    get_cached_monthly_sales,
    get_cached_daily_sales,
    get_cached_daily_sales_by_branch,
    get_cached_daily_sales_by_products,
    get_cached_employee_sales,
    get_cached_targets,
    refresh_all_caches,
    pool,
    placeholders,
    build_filter_clause,
    get_saved_category_filters,
    save_category_filters,
    get_cached_category_filter_coverage,
    get_cached_ramzan_deals_sales,
    get_cached_ramzan_product_master
)
from modules.material_cost_commission import (
    create_material_cost_commission_table,
    get_material_cost_commission_data,
    get_material_cost_commission_analysis,
    get_employee_material_cost_summary,
    get_branch_material_cost_summary,
    get_product_material_cost_summary,
    get_branch_product_material_cost_summary
)
from modules.connection_cloud import (
    get_performance_metrics,
    health_check,
    DatabaseConfig
)
from modules.blink_reporting import (
    prepare_blink_orders,
    build_split_report,
    apply_split_filters,
    add_transaction_quality_flags,
    build_quality_summary
)
from modules.visualization import (
    create_achievement_gauge,
    create_waterfall_chart,
    create_trend_chart,
    create_heatmap,
    create_sankey_diagram,
    create_forecast_chart,
    create_monthly_sales_trend,
    create_top_categories_small_multiples,
    create_product_time_series,
    create_forecast_with_ci
)
from modules.utils import (
    format_currency,
    format_percentage,
    calculate_achievement,
    get_date_presets,
    export_to_excel,
    export_tables_to_excel,
        log_query_time
)
from modules.config import (
    BLOCKED_NAMES,
    BLOCKED_COMMENTS,
    ORDER_TYPES,
    SELECTED_BRANCH_IDS,
    RAMZAN_DEALS_PRODUCT_IDS,
    SALE_CATEGORIES,
    QTY_CATEGORIES,
    DEFAULT_EXCLUDED_CATEGORY_IDS
)
from modules.auth import (
    authenticate_user,
    logout_user,
    check_session_timeout,
    update_activity
)

# -------------------------------
# Product comparison helper
# -------------------------------
def month_name(year: int, month: int) -> str:
    from calendar import month_name as _mn
    return f"{_mn[month]} {year}"

def render_table(
    data,
    width: str = "stretch",
    height: Optional[int] = None,
    hide_index: bool = True,
    column_config: Optional[Dict] = None,
    key: Optional[str] = None
):
    """Consistent dataframe rendering for readability across the dashboard."""
    kwargs = {
        "width": width,
        "hide_index": hide_index
    }
    if height is not None:
        kwargs["height"] = height
    if column_config is not None:
        kwargs["column_config"] = column_config
    if key is not None:
        kwargs["key"] = key
    st.dataframe(data, **kwargs)

EXCLUDED_EMPLOYEE_NAMES = {"online/unassigned"}

def exclude_employee_names(df: pd.DataFrame, column: str = "employee_name") -> pd.DataFrame:
    """Exclude non-attributed employee rows from analytics and tables."""
    if df is None or df.empty or column not in df.columns:
        return df
    normalized = df[column].astype(str).str.strip().str.lower()
    return df[~normalized.isin(EXCLUDED_EMPLOYEE_NAMES)].copy()

# ========================
# PAGE CONFIGURATION
# ========================
st.set_page_config(
    page_title="HNS Sales Dashboard",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# CUSTOM CSS & DARK MODE
# ========================
def load_custom_css():
    """Load custom CSS for better UI"""
    dark_mode = st.session_state.get('dark_mode', False)
    
    if dark_mode:
        bg_color = "#0e1117"
        text_color = "#fafafa"
        card_bg = "#1e2130"
        border_color = "#2e3441"
    else:
        bg_color = "#ffffff"
        text_color = "#262730"
        card_bg = "#f0f2f6"
        border_color = "#e0e0e0"
    
    st.markdown(f"""
        <style>
        .metric-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid {border_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4;
        }}
        .metric-label {{
            font-size: 0.9rem;
            color: {text_color};
            margin-bottom: 5px;
        }}
        .stButton>button {{
            border-radius: 5px;
            font-weight: 500;
        }}
        .success-metric {{
            color: #28a745;
        }}
        .warning-metric {{
            color: #ffc107;
        }}
        .danger-metric {{
            color: #dc3545;
        }}
        .data-fresh {{
            font-size: 0.8rem;
            color: #6c757d;
            font-style: italic;
        }}
        div[data-testid="stDataFrame"] * {{
            font-size: 0.9rem;
        }}
        div[data-testid="stDataFrame"] [role="columnheader"] {{
            font-weight: 600;
        }}
        div[data-testid="stExpander"] {{
            background-color: {card_bg};
            border-radius: 5px;
        }}
        /* Enable full height for tables in fullscreen mode */
        div[data-testid="stDataFrame"][data-is-fullscreen="true"] {{
            height: 100vh !important;
        }}
        div[data-testid="stDataFrame"][data-is-fullscreen="true"] > div {{
            height: 100% !important;
        }}
        </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ========================
# SESSION STATE INITIALIZATION
# ========================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ========================
# AUTHENTICATION GATE
# ========================
if st.session_state.authenticated:
    if check_session_timeout():
        logout_user()
        st.warning("Session timed out. Please log in again.")
        st.stop()
    update_activity()
else:
    authenticate_user()
    st.stop()

# ========================
# SIDEBAR CONFIGURATION
# ========================
st.sidebar.title("??? Dashboard Controls")

# Logout button
if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()

# Dark Mode Toggle
if st.sidebar.checkbox("?? Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
    load_custom_css()
else:
    st.session_state.dark_mode = False
    load_custom_css()

st.sidebar.markdown("---")

# ========================
# DATE FILTERS
# ========================
st.sidebar.header("?? Date Range")

# Date presets
date_preset = st.sidebar.selectbox(
    "Quick Select",
    ["Custom", "Today", "Yesterday", "This Week", "Last Week", 
     "This Month", "Last Month", "This Quarter", "This Year"]
)

start_date, end_date = get_date_presets(date_preset)

# Default to current month range when not Custom
if date_preset == "Custom":
    pass
else:
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today

if date_preset == "Custom":
    start_date = st.sidebar.date_input("Start Date", start_date)
    end_date = st.sidebar.date_input("End Date", end_date)

if start_date > end_date:
    st.sidebar.error("?? Start Date cannot be after End Date")
    st.stop()

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

st.sidebar.markdown("---")

# ========================
# FILTER OPTIONS
# ========================
st.sidebar.header("?? Filters")

# Filter Mode
data_mode = st.sidebar.radio(
    "Data Mode",
    ["Filtered", "Unfiltered"],
    help="Filtered mode excludes blocked customers and comments"
)

# Branch Selection
branch_name_map = {
    2: "Khadda Main Branch",
    3: "FESTIVAL",
    4: "Rahat Commercial",
    6: "TOWER",
    8: "North Nazimabad",
    10: "MALIR",
    14: "FESTIVAL 2"
}

user_record = st.session_state.get('user', {}) or {}
allowed_branches = user_record.get('allowed_branches', SELECTED_BRANCH_IDS)
if allowed_branches == "all":
    allowed_branches = SELECTED_BRANCH_IDS

selected_branches = st.sidebar.multiselect(
    "Select Branches",
    options=allowed_branches,
    default=allowed_branches,
    format_func=lambda x: branch_name_map.get(x, f"Branch {x}")
)

if not selected_branches:
    st.sidebar.warning("?? Please select at least one branch")
    st.stop()

st.sidebar.markdown("---")

# ========================
# TARGET PERIOD
# ========================
st.sidebar.header("?? Target Period")
target_year = st.sidebar.number_input("Year", 2000, 2100, 2026, 1)
target_month = st.sidebar.selectbox(
    "Month", 
    range(1, 13), 
    index=datetime.now().month - 1,
    format_func=lambda x: datetime(2000, x, 1).strftime("%B")
)

st.sidebar.markdown("---")

# ========================
# REFRESH CONTROLS
# ========================
st.sidebar.header("?? Data Controls")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("?? Refresh", width="stretch"):
        with st.spinner("Refreshing data..."):
            refresh_all_caches()
            st.session_state.last_refresh = datetime.now()
            st.success("? Data refreshed!")
            time.sleep(1)
            st.rerun()

with col2:
    auto_refresh = st.checkbox("Auto", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh

# Snapshot Generation
if st.sidebar.button("?? Generate Snapshots", width="stretch"):
    with st.spinner("Generating snapshots..."):
        try:
            from daily_branch_snapshots import generate_snapshots
            out_dir = generate_snapshots(
                start_date=start_date_str,
                end_date=end_date_str,
                target_year=target_year,
                target_month=target_month,
                branches=selected_branches,
                data_mode=data_mode,
                output_dir="HNS_Deshboard/snapshots"
            )
            st.sidebar.success(f"? Saved to {out_dir.name}")
        except Exception as e:
            st.sidebar.error(f"? Error setting up snapshots: {e}")

# Data freshness indicator
time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
st.sidebar.markdown(
    f'<p class="data-fresh">Last refresh: {time_since_refresh}s ago</p>',
    unsafe_allow_html=True
)

# Auto-refresh logic
if st.session_state.auto_refresh:
    if time_since_refresh > 300:  # 5 minutes
        refresh_all_caches()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

# Active category filters badge
saved_filter_badge = get_saved_category_filters()
badge_inc = saved_filter_badge.get("included_category_ids", [])
badge_exc = saved_filter_badge.get("excluded_category_ids", [])
inc_text = ",".join(map(str, badge_inc)) if badge_inc else "none"
exc_text = ",".join(map(str, badge_exc)) if badge_exc else "none"
st.sidebar.caption(f"Category Filters | Included: {inc_text} | Excluded: {exc_text}")

# ========================
# PERFORMANCE MONITORING
# ========================
st.sidebar.header("?? Performance")

# Connection health check
if st.sidebar.button("?? Health Check", width="stretch"):
    with st.spinner("Checking connection health..."):
        health_status = health_check()
        if health_status['status'] == 'healthy':
            st.sidebar.success("? All connections healthy")
        else:
            st.sidebar.error(f"? Health check failed: {health_status.get('error', 'Unknown error')}")

# Performance metrics
if st.sidebar.button("?? Metrics", width="stretch"):
    with st.spinner("Fetching performance metrics..."):
        metrics = get_performance_metrics()
        
        # Display connection pool stats
        pool_stats = metrics.get('pool_stats', {})
        st.sidebar.subheader("Connection Pool")
        st.sidebar.metric("Pool Size", pool_stats.get('pool_size', 0))
        st.sidebar.metric("Active Connections", pool_stats.get('active_connections', 0))
        st.sidebar.metric("Total Queries", pool_stats.get('total_queries', 0))
        st.sidebar.metric("Avg Query Time", f"{pool_stats.get('avg_query_time', 0):.2f}s")
        
        # Display query stats
        candelahns_stats = metrics.get('candelahns_stats', {})
        if candelahns_stats:
            st.sidebar.subheader("Candelahns DB")
            st.sidebar.metric("Success Rate", f"{candelahns_stats.get('success_rate', 0):.1f}%")
            st.sidebar.metric("Slow Queries", candelahns_stats.get('slow_queries', 0))
            st.sidebar.metric("Max Query Time", f"{candelahns_stats.get('max_query_time', 0):.2f}s")

# Connection configuration
with st.sidebar.expander("?? Connection Settings"):
    st.write("**Timeouts:**")
    st.write(f"- Connection: {DatabaseConfig.CONNECTION_TIMEOUT}s")
    st.write(f"- Query: {DatabaseConfig.QUERY_TIMEOUT}s")
    st.write(f"- Pool: {DatabaseConfig.POOL_TIMEOUT}s")
    
    st.write("**Retries:**")
    st.write(f"- Max Retries: {DatabaseConfig.MAX_RETRIES}")
    st.write(f"- Retry Delay: {DatabaseConfig.RETRY_DELAY}s")
    
    st.write("**Pool:**")
    st.write(f"- Pool Size: {DatabaseConfig.POOL_SIZE}")
    st.write(f"- Slow Query Threshold: {DatabaseConfig.SLOW_QUERY_THRESHOLD}s")

# ========================
# MAIN DASHBOARD
# ========================
# Dynamic title based on allowed branches
allowed_set = set(allowed_branches) if isinstance(allowed_branches, list) else set(SELECTED_BRANCH_IDS)
if allowed_set == set(SELECTED_BRANCH_IDS):
    title_text = "HNS Sales Dashboard"
elif allowed_set == {8, 10}:
    title_text = "HNS Sales Dashboard: Malir & North Nazimabad"
elif allowed_set == {2, 4, 6}:
    title_text = "HNS Sales Dashboard: Khadda Rahat TOWER"
elif allowed_set == {3, 14}:
    title_text = "HNS Sales Dashboard: Festival & Festival 2"
else:
    title_text = "HNS Sales Dashboard"

st.title(f"?? {title_text}")
st.markdown(f"**Period:** {start_date_str} to {end_date_str}")

# ========================
# FETCH DATA WITH TIMING
# ========================
with st.spinner("Loading dashboard data..."):
    query_start = time.time()
    
    # Fetch all data
    df_branch = get_cached_branch_summary(
        start_date_str, end_date_str, selected_branches, data_mode
    )
    df_ot = get_cached_ot_data(
        start_date_str, end_date_str, selected_branches, data_mode
    )
    df_line_item = get_cached_line_items(
        start_date_str, end_date_str, selected_branches, data_mode
    )
    df_order_types = get_cached_order_types(
        start_date_str, end_date_str, selected_branches, data_mode
    )
    df_qr_sales = get_cached_qr_sales(
        start_date_str, end_date_str, selected_branches, data_mode
    )
    df_employee_sales = get_cached_employee_sales(
        start_date_str, end_date_str, selected_branches
    )

    # Exclude non-attributed rows like Online/Unassigned from OT-level reporting.
    df_ot = exclude_employee_names(df_ot, "employee_name")
    df_employee_sales = exclude_employee_names(df_employee_sales, "employee_name")
    
    # Fetch targets
    branch_targets, chef_targets, ot_targets, fresh_targets = get_cached_targets(
        target_year, target_month
    )
    
    query_time = time.time() - query_start
    log_query_time("Dashboard Load", query_time)

# Performance indicator
st.sidebar.markdown(
    f'<p class="data-fresh">Query time: {query_time:.2f}s</p>',
    unsafe_allow_html=True
)

# ========================
# TABS
# ========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "Overview",
    "Order Takers",
    "Chef Sales",
    "Chef Targets",
    "OT Targets",
    "QR Commission",
    "Material Cost Commission",
    "Trends & Analytics",
    "Ramzan Deals",
    "Category Filters",
    "Category Coverage",
    "Pivot Tables"
])

# ========================
# TAB 1: OVERVIEW
# ========================
with tab1:
    st.header("?? Sales Overview")
    
    if df_branch.empty:
        st.info("?? No data available for selected filters")
    else:
        # Add targets to branch data (display-only copy for overview)
        df_branch_display = df_branch.copy()
        df_branch_display['Monthly_Target'] = df_branch_display['shop_id'].map(branch_targets).fillna(0).astype(float)
        df_branch_display['total_Nt_amount'] = df_branch_display['total_Nt_amount'].astype(float)

        # Merge FESTIVAL (ID 3) + FESTIVAL 2 (ID 14) for overview cards
        festival_mask = df_branch_display['shop_id'] == 3
        festival2_mask = df_branch_display['shop_id'] == 14
        if festival_mask.any() and festival2_mask.any():
            festival2_sales = df_branch_display.loc[festival2_mask, 'total_Nt_amount'].sum()
            df_branch_display.loc[festival_mask, 'total_Nt_amount'] += festival2_sales
            df_branch_display.loc[festival_mask, 'shop_name'] = "FESTIVAL"
            # Hide FESTIVAL 2 card in overview
            df_branch_display = df_branch_display.loc[~festival2_mask].copy()

        df_branch_display['Remaining_Target'] = df_branch_display['Monthly_Target'] - df_branch_display['total_Nt_amount']
        df_branch_display['Achievement_%'] = df_branch_display.apply(
            lambda row: (row['total_Nt_amount'] / row['Monthly_Target'] * 100) if row['Monthly_Target'] > 0 else 0,
            axis=1
        )
        
        # Summary Metrics
        total_sales = df_branch_display['total_Nt_amount'].sum()
        total_target = df_branch_display['Monthly_Target'].sum()
        total_remaining = total_target - total_sales
        overall_achievement = (total_sales / total_target * 100) if total_target > 0 else 0
        
        # Display metrics with custom styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Sales</div>
                    <div class="metric-value">{format_currency(total_sales)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Target</div>
                    <div class="metric-value">{format_currency(total_target)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        
        with col4:
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
        
        st.markdown("---")
        st.subheader("Top 5 Highlights")
        col_a, col_b, col_c = st.columns(3)

        # Top 5 Chef Sales (by product revenue)
        with col_a:
            st.markdown("**Chef Sales — Top 5 Products**")
            if not df_line_item.empty:
                df_top_products = df_line_item.groupby('product', as_index=False).agg({
                    'total_line_value_incl_tax': 'sum'
                }).sort_values('total_line_value_incl_tax', ascending=False).head(5)
                df_top_products['Sales'] = df_top_products['total_line_value_incl_tax'].apply(format_currency)
                render_table(df_top_products[['product', 'Sales']], width="stretch", height=230)
            else:
                st.info("No chef sales data")

        # Top 5 Line Item Sub-Products (product names)
        with col_b:
            st.markdown("**Line Item Sub-Products — Top 5**")
            try:
                df_top_items = get_cached_product_monthly_sales_by_product(
                    target_year, target_month, selected_branches, data_mode, category=None
                )
                if df_top_items is not None and not df_top_items.empty:
                    df_top_items = df_top_items.rename(columns={'Total_Sales': 'Sales'})
                    df_top_items = df_top_items.sort_values('Sales', ascending=False).head(5)
                    df_top_items['Sales'] = df_top_items['Sales'].apply(format_currency)
                    render_table(df_top_items[['Product', 'Sales']], width="stretch", height=230)
                else:
                    st.info("No product data for current month")
            except Exception:
                st.info("No product data for current month")

        # Top 5 OT Sales
        with col_c:
            st.markdown("**OT Sales — Top 5**")
            if not df_ot.empty:
                df_top_ot = df_ot.sort_values('total_sale', ascending=False).head(5)
                df_top_ot['Sales'] = df_top_ot['total_sale'].apply(format_currency)
                render_table(df_top_ot[['employee_name', 'Sales']], width="stretch", height=230)
            else:
                st.info("No OT sales data")

        st.markdown("---")
        
        # Gauge Chart for Overall Achievement
        st.subheader("Overall Performance")
        gauge_fig = create_achievement_gauge(overall_achievement, "Overall Achievement")
        st.plotly_chart(gauge_fig, width="stretch")
        
        st.markdown("---")
        
        # Branch-wise Performance
        st.subheader("Branch-wise Performance")
        
        # Heatmap for branch performance
        heatmap_fig = create_heatmap(df_branch_display)
        st.plotly_chart(heatmap_fig, width="stretch")
        
        # Individual branch cards
        cols = st.columns(2)
        for idx, (_, row) in enumerate(df_branch_display.iterrows()):
            with cols[idx % 2]:
                with st.expander(f"?? {row['shop_name']} (ID: {row['shop_id']})"):
                    # Metrics in a cleaner layout
                    col1, col2 = st.columns(2)
                    col1.metric("Current Sales", format_currency(row['total_Nt_amount']))
                    col2.metric("Monthly Target", format_currency(row['Monthly_Target']))
                    col1.metric("Remaining", format_currency(row['Remaining_Target']))
                    col2.metric("Achievement", format_percentage(row['Achievement_%']))
        
        st.markdown("---")
        
        # Waterfall Chart for Target Breakdown
        st.subheader("Target Achievement Breakdown")
        waterfall_fig = create_waterfall_chart(df_branch_display)
        st.plotly_chart(waterfall_fig, width="stretch")
        
        st.markdown("---")
        st.subheader("Daily Sales by Branch (Last 30 Days)")

        last_30_end = date.today()
        last_30_start = last_30_end - timedelta(days=29)
        last_30_start_str = last_30_start.strftime("%Y-%m-%d")
        last_30_end_str = last_30_end.strftime("%Y-%m-%d")

        try:
            df_daily_branch = get_cached_daily_sales_by_branch(
                last_30_start_str, last_30_end_str, selected_branches, data_mode
            )
            if df_daily_branch.empty:
                st.info("?? No daily branch sales data for the last 30 days.")
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

            render_table(display_daily, width="stretch", height=450)
        except Exception as e:
            st.warning(f"Could not load daily branch sales (last 30 days): {e}")
        st.markdown("---")
        
        # Order Type Analysis
        st.subheader("?? Order Type Distribution")
        
        if not df_order_types.empty:
            # Sankey Diagram
            sankey_fig = create_sankey_diagram(df_order_types)
            st.plotly_chart(sankey_fig, width="stretch")
            
            # Order type metrics
            col1, col2, col3 = st.columns(3)
            
            order_types_display = ['Food Panda', 'Delivery', 'Dine IN']
            for idx, ot in enumerate(order_types_display):
                ot_data = df_order_types[df_order_types['order_type'] == ot]
                if not ot_data.empty:
                    with [col1, col2, col3][idx]:
                        sales = ot_data['total_sales'].iloc[0]
                        orders = ot_data['total_orders'].iloc[0]
                        st.metric(
                            f"??? {ot}",
                            format_currency(sales),
                            f"{orders:,} orders"
                        )
            
            # Detailed table
            with st.expander("?? Detailed Order Type Breakdown"):
                df_ot_display = df_order_types.copy()
                df_ot_display['total_sales_pct'] = (
                    df_ot_display['total_sales'] / df_ot_display['total_sales'].sum() * 100
                )
                
                # Format for display
                display_df = df_ot_display.copy()
                display_df['total_sales'] = display_df['total_sales'].apply(lambda x: format_currency(x))
                display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
                display_df['total_sales_pct'] = display_df['total_sales_pct'].apply(lambda x: f"{x:.1f}%")
                
        render_table(display_df[['order_type', 'total_orders', 'total_sales', 'total_sales_pct']], 
            width="stretch")
        
        # Export Options
        st.markdown("---")
        st.subheader("Export Options")
        
        col1 = st.columns(1)[0]
        
        with col1:
            excel_data = export_to_excel(df_branch_display, "Branch Summary")
            st.download_button(
                "Download Excel",
                excel_data,
                "branch_summary.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

# ========================
# TAB 2: ORDER TAKERS
# ========================
with tab2:
    st.header("?? Order Taker Performance")
    
    if df_ot.empty:
        st.info("?? No OT data available")
    else:
        # Summary metrics
        total_ot_sales = df_ot['total_sale'].sum()
        unique_ots = df_ot['employee_id'].nunique()
        avg_sale_per_ot = total_ot_sales / unique_ots if unique_ots > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total OT Sales", format_currency(total_ot_sales))
        col2.metric("Active OTs", f"{unique_ots:,}")
        col3.metric("Avg per OT", format_currency(avg_sale_per_ot))
        
        st.markdown("---")
        
        # Top performers
        st.subheader("?? Top 10 Performers")
        df_ot_sorted = df_ot.sort_values('total_sale', ascending=False).head(10)
        
        fig = px.bar(
            df_ot_sorted,
            x='total_sale',
            y='employee_name',
            orientation='h',
            title="Top 10 Order Takers by Sales",
            labels={'total_sale': 'Sales ()', 'employee_name': 'Order Taker'},
            color='total_sale',
            color_continuous_scale='Blues',
            text='total_sale'
        )
        
        # Add value labels inside bars
        fig.update_traces(
            texttemplate=' %{text:,.0f}',
            textposition='inside',
            textfont_size=11,
            textfont_color='white',
            insidetextanchor='middle'
        )
        
        fig.update_layout(
            showlegend=False, 
            height=500,
            xaxis_title="Sales ()",
            yaxis_title="Order Taker"
        )
        
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # Detailed table with search
        st.subheader("?? All Order Takers")
        
        search = st.text_input("?? Search by name", "")
        if search:
            df_ot_filtered = df_ot[
                df_ot['employee_name'].str.contains(search, case=False, na=False)
            ]
        else:
            df_ot_filtered = df_ot
        
        # Format for display
        display_ot = df_ot_filtered.copy()
        display_ot['total_sale'] = display_ot['total_sale'].apply(lambda x: format_currency(x))
        
        render_table(display_ot, width="stretch")
        
        # Export

# ========================
# TAB 3: CHEF SALES
# ========================
with tab3:
    st.header("????? Chef Sales Analysis")
    
    if df_line_item.empty:
        st.info("?? No chef sales data available")
    else:
        # Product analysis
        df_product_summary = df_line_item.groupby('product').agg({
            'total_qty': 'sum',
            'total_line_value_incl_tax': 'sum'
        }).reset_index()
        df_product_summary = df_product_summary.sort_values(
            'total_line_value_incl_tax', ascending=False
        )
        
        # Top products
        st.subheader("??? Top 15 Products by Revenue")
        
        top_products = df_product_summary.head(15)
        fig = px.bar(
            top_products,
            x='total_line_value_incl_tax',
            y='product',
            orientation='h',
            title="Top 15 Products",
            labels={
                'total_line_value_incl_tax': 'Revenue ()',
                'product': 'Product'
            },
            color='total_line_value_incl_tax',
            color_continuous_scale='Greens',
            text='total_line_value_incl_tax'
        )
        
        # Add value labels inside bars
        fig.update_traces(
            texttemplate=' %{text:,.0f}',
            textposition='inside',
            textfont_size=11,
            textfont_color='white',
            insidetextanchor='middle'
        )
        
        fig.update_layout(
            showlegend=False, 
            height=600,
            xaxis_title="Revenue ()",
            yaxis_title="Product"
        )
        
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # Category breakdown
        st.subheader("?? Product Category Distribution")
        
        # Pie chart for top 10 products
        fig_pie = px.pie(
            top_products.head(10),
            values='total_line_value_incl_tax',
            names='product',
            title="Revenue Distribution - Top 10 Products"
        )
        st.plotly_chart(fig_pie, width="stretch")
        
        st.markdown("---")
        
        # Detailed table
        st.subheader("?? All Products")
        
        # Format for display
        display_products = df_product_summary.copy()
        display_products['total_qty'] = display_products['total_qty'].apply(lambda x: f"{x:,.0f}")
        display_products['total_line_value_incl_tax'] = display_products['total_line_value_incl_tax'].apply(lambda x: format_currency(x))
        
        render_table(display_products, width="stretch")

        # Branch-wise table
        st.subheader("?? All Products by Branch")
        display_branch_products = df_line_item.copy()
        display_branch_products = display_branch_products.rename(
            columns={
                'shop_name': 'Branch',
                'product': 'Product',
                'total_qty': 'Total Qty',
                'total_line_value_incl_tax': 'Total Sales'
            }
        )
        display_branch_products['Total Qty'] = display_branch_products['Total Qty'].apply(lambda x: f"{x:,.0f}")
        display_branch_products['Total Sales'] = display_branch_products['Total Sales'].apply(lambda x: format_currency(x))
        display_branch_products = display_branch_products.sort_values(['Branch', 'Total Sales'], ascending=[True, False])
        render_table(
            display_branch_products[['Branch', 'Product', 'Total Qty', 'Total Sales']],
            width="stretch",
            height=800
        )

        # Reconciliation check: Chef tab totals vs Overview branch totals
        try:
            df_chef_branch = (
                df_line_item.groupby(['shop_id', 'shop_name'], as_index=False)
                .agg({'total_line_value_incl_tax': 'sum'})
                .rename(columns={'total_line_value_incl_tax': 'chef_sales_total'})
            )

            df_overview_branch = df_branch[['shop_id', 'shop_name', 'total_Nt_amount']].copy()
            df_overview_branch['total_Nt_amount'] = pd.to_numeric(
                df_overview_branch['total_Nt_amount'], errors='coerce'
            ).fillna(0.0)
            df_overview_branch = df_overview_branch.rename(columns={'total_Nt_amount': 'overview_sales_total'})

            df_reconcile = df_overview_branch.merge(
                df_chef_branch,
                on=['shop_id', 'shop_name'],
                how='left'
            )
            df_reconcile['chef_sales_total'] = pd.to_numeric(df_reconcile['chef_sales_total'], errors='coerce').fillna(0.0)
            df_reconcile['difference'] = df_reconcile['overview_sales_total'] - df_reconcile['chef_sales_total']
            df_reconcile = df_reconcile.sort_values('shop_id')

            st.markdown("#### Branch Reconciliation (Overview vs Chef)")
            render_table(
                df_reconcile[['shop_id', 'shop_name', 'overview_sales_total', 'chef_sales_total', 'difference']],
                width="stretch",
                height=260
            )
        except Exception as e:
            st.info(f"Reconciliation table unavailable: {e}")
        
        # Export

        # -------------------------------
        # Daily Product Targets (15% vs Previous Day)
        # -------------------------------
        st.markdown("---")
        st.subheader("Product Daily Targets (25% vs Previous Day)")

        try:
            # Use current real data (today/yesterday/MTD) and product-level names
            conn = pool.get_connection("candelahns")
            filter_clause, filter_params = build_filter_clause(data_mode)

            def fetch_product_sales(start_d: date, end_d: date) -> pd.DataFrame:
                end_next = end_d + timedelta(days=1)
                query = f"""
                SELECT
                    p.item_name AS product,
                    SUM(li.qty) AS total_qty
                FROM tblSales s WITH (NOLOCK)
                JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
                LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
                LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
                WHERE s.sale_date >= ? AND s.sale_date < ?
                  AND s.shop_id IN ({placeholders(len(selected_branches))})
                  AND p.item_name IS NOT NULL AND LTRIM(RTRIM(p.item_name)) <> ''
                {filter_clause}
                GROUP BY p.item_name
                """
                params = [
                    start_d.strftime("%Y-%m-%d"),
                    end_next.strftime("%Y-%m-%d"),
                ] + selected_branches + filter_params
                try:
                    return pd.read_sql(query, conn, params=params)
                except Exception as e:
                    err_text = str(e)
                    # Retry once for transient SQL Server lock-timeout (error 1222)
                    if ("1222" in err_text) or ("Lock request time out period exceeded" in err_text):
                        time.sleep(1)
                        return pd.read_sql(query, conn, params=params)
                    raise

            today_date = date.today()
            yesterday_date = today_date - timedelta(days=1)
            month_start = date(today_date.year, today_date.month, 1)
            days_in_month = monthrange(today_date.year, today_date.month)[1]
            remaining_days = max(days_in_month - today_date.day, 0)

            df_today = fetch_product_sales(today_date, today_date).rename(columns={'total_qty': 'today_qty'})
            df_yest = fetch_product_sales(yesterday_date, yesterday_date).rename(columns={'total_qty': 'yesterday_qty'})
            df_mtd = fetch_product_sales(month_start, today_date).rename(columns={'total_qty': 'mtd_qty'})

            # Build table from products seen in MTD (fallback to yesterday/today)
            if not df_mtd.empty:
                product_list = df_mtd['product'].dropna().astype(str).unique().tolist()
            elif not df_yest.empty:
                product_list = df_yest['product'].dropna().astype(str).unique().tolist()
            else:
                product_list = df_today['product'].dropna().astype(str).unique().tolist()

            if product_list:
                df_prod = pd.DataFrame({'Product': product_list})
                df_prod = df_prod.merge(df_yest, left_on='Product', right_on='product', how='left').drop(columns=['product'])
                df_prod = df_prod.merge(df_today, left_on='Product', right_on='product', how='left').drop(columns=['product'])
                df_prod = df_prod.merge(df_mtd, left_on='Product', right_on='product', how='left').drop(columns=['product'])

                df_prod['yesterday_qty'] = df_prod['yesterday_qty'].fillna(0)
                df_prod['today_qty'] = df_prod['today_qty'].fillna(0)
                df_prod['mtd_qty'] = df_prod['mtd_qty'].fillna(0)

                # Targets: 25% above previous day (qty-based)
                df_prod['Target'] = df_prod['yesterday_qty'] * 1.25
                df_prod['Previous Achieved'] = df_prod['yesterday_qty']
                df_prod['Today Target'] = df_prod['Target']
                df_prod['Next Day Target'] = df_prod['yesterday_qty'] * 1.25
                df_prod['Current Sale'] = df_prod['today_qty']
                df_prod['Remaining'] = df_prod['Target'] - df_prod['today_qty']
                df_prod['Achievement %'] = df_prod.apply(
                    lambda row: (row['Current Sale'] / row['Target'] * 100) if row['Target'] > 0 else 0,
                    axis=1
                )

                # Format + styling
                display_prod = df_prod.copy()
                for col in [
                    'Previous Achieved', 'Today Target',
                    'Next Day Target', 'Current Sale', 'Remaining'
                ]:
                    display_prod[col] = display_prod[col].apply(lambda x: f"{x:,.0f}")
                display_prod['Achievement %'] = display_prod['Achievement %'].apply(lambda x: f"{x:.1f}%")

                def color_remaining(val):
                    try:
                        num = float(str(val).replace(',', '').replace('', '').strip())
                        return 'color: green' if num <= 0 else 'color: red'
                    except Exception:
                        return ''

                def color_ach(val):
                    try:
                        num = float(str(val).replace('%', '').strip())
                        return 'color: green' if num >= 100 else 'color: red'
                    except Exception:
                        return ''

                styled = display_prod[[
                    'Product', 'Previous Achieved', 'Today Target',
                    'Next Day Target', 'Current Sale', 'Remaining', 'Achievement %'
                ]].style.applymap(color_remaining, subset=['Remaining']) \
                      .applymap(color_ach, subset=['Achievement %'])

                render_table(styled, width="stretch", height=450)
            else:
                st.info("?? No products available for daily targets.")
        except Exception as e:
            st.warning(f"Could not load product daily targets: {e}")

# ========================
# TAB 4: CHEF TARGETS
# ========================
with tab4:
    st.header("?? Chef Targets & Achievement")
    
    # Branch selection
    if not df_branch.empty:
        branch_names = df_branch['shop_name'].tolist()
        selected_branch = st.selectbox("Select Branch", branch_names)
        shop_id = df_branch[df_branch['shop_name'] == selected_branch]['shop_id'].iloc[0]
        
        st.info(f"?? Showing targets for **{selected_branch}** - {datetime(target_year, target_month, 1).strftime('%B %Y')}")
        
        # Get targets for this branch
        if not chef_targets.empty:
            df_chef_filtered = chef_targets[chef_targets['shop_id'] == shop_id]
            
            if not df_chef_filtered.empty:
                # Get categories from KDS DB
                try:
                    from modules.database import pool
                    import pandas as pd
                    conn_kds = pool.get_connection("kdsdb")
                    categories = pd.read_sql("SELECT * FROM dbo.chef_sale", conn_kds)
                    
                    # Merge targets with categories
                    df_targets_with_categories = df_chef_filtered.merge(categories, on='category_id', how='left')
                    
                    # Filter to only show specified categories
                    allowed_categories = SALE_CATEGORIES + QTY_CATEGORIES
                    df_targets_with_categories = df_targets_with_categories[
                        df_targets_with_categories['category_name'].isin(allowed_categories)
                    ]
                    
                    # Set correct target_type based on category
                    def get_target_type(cat):
                        if cat in SALE_CATEGORIES:
                            return 'Sale'
                        elif cat in QTY_CATEGORIES:
                            return 'Quantity'
                        else:
                            return 'Sale'
                    
                    df_targets_with_categories['target_type'] = df_targets_with_categories['category_name'].apply(get_target_type)
                    
                    # Get sales data for this branch
                    df_sales_this_branch = df_line_item[df_line_item['shop_id'] == shop_id].copy()
                    
                    # Filter out unwanted products
                    products_to_hide = ['Sales - Employee Food', 'Deals', 'Modifiers']
                    # products_to_hide = ['Sales - Employee Food', 'Deals', 'Modifiers']
                    df_sales_this_branch = df_sales_this_branch[~df_sales_this_branch['product'].isin(products_to_hide)]
                    
                    # Clean names for merging
                    def clean_name(name):
                        name = str(name).upper()
                        name = name.replace("SALES -", "").replace("SALES", "").strip()
                        name = name.replace("SIDE ORDERS", "SIDE ORDER")
                        name = name.replace("-", " ")
                        words = name.split()
                        cleaned_words = []
                        for word in words:
                            if word in ['ROLLS']:
                                word = 'ROLL'
                            elif word in ['ORDERS']:
                                word = 'ORDER'
                            elif word in ['SIDES']:
                                word = 'SIDE'
                            cleaned_words.append(word)
                        return ' '.join(cleaned_words)
                    
                    df_sales_this_branch['product_clean'] = df_sales_this_branch['product'].apply(clean_name)
                    df_targets_with_categories['category_clean'] = df_targets_with_categories['category_name'].apply(clean_name)
                    
                    # Left join targets with sales data
                    df_products_with_targets = df_targets_with_categories.merge(
                        df_sales_this_branch, 
                        left_on='category_clean', 
                        right_on='product_clean', 
                        how='left'
                    ).fillna({'total_line_value_incl_tax': 0, 'total_qty': 0})
                    
                    # Set product name
                    df_products_with_targets['product'] = df_products_with_targets['product'].fillna(
                        df_products_with_targets['category_name']
                    )
                    
                    # Create display table
                    product_table = df_products_with_targets[['product', 'target_amount', 'target_type']].copy()
                    
                    # For Sale targets, use sales amount; for quantity targets, use quantity
                    product_table['Current'] = df_products_with_targets.apply(
                        lambda row: row['total_line_value_incl_tax'] if row['target_type'] == 'Sale' else row['total_qty'], 
                        axis=1
                    )
                    
                    product_table.columns = ['Product', 'Target', 'Type', 'Current Sale']
                    
                    # Ensure numeric types
                    product_table['Target'] = pd.to_numeric(product_table['Target'], errors='coerce').fillna(0)
                    product_table['Current Sale'] = pd.to_numeric(product_table['Current Sale'], errors='coerce').fillna(0)
                    
                    # Calculate remaining and achievement
                    product_table['Remaining'] = product_table['Target'] - product_table['Current Sale']
                    product_table['Achievement %'] = product_table.apply(
                        lambda row: (row['Current Sale'] / row['Target'] * 100) if row['Target'] > 0 else 0,
                        axis=1
                    )
                    
                    # Calculate bonus
                    product_table['Bonus'] = product_table.apply(
                        lambda row: row['Current Sale'] * 0.5 if row['Achievement %'] >= 100 else 0, 
                        axis=1
                    )
                    
                    # Save numeric values for chart
                    df_chart = product_table[['Product', 'Target', 'Current Sale']].copy()
                    
                    # Format for display
                    display_table = product_table.copy()
                    display_table['Target'] = display_table.apply(
                        lambda row: f"{int(row['Target']):,} qty" if row['Type'] == 'Quantity' else f" {int(row['Target']):,}",
                        axis=1
                    )
                    display_table['Current Sale'] = display_table['Current Sale'].apply(lambda x: f"{int(x):,}")
                    display_table['Remaining'] = display_table['Remaining'].apply(lambda x: f"{int(x):,}")
                    display_table['Achievement %'] = display_table['Achievement %'].apply(lambda x: f"{x:.1f}%")
                    display_table['Bonus'] = display_table['Bonus'].apply(lambda x: f" {int(x):,}")
                    
                    # Display table
                    render_table(
                        display_table[['Product', 'Target', 'Current Sale', 'Remaining', 'Achievement %', 'Bonus']],
                        width="stretch",
                        height=400
                    )
                    
                    st.markdown("---")
                    
                    # Chart: Target vs Current Sale
                    st.subheader("?? Target vs Achievement Comparison")
                    
                    df_chart_melt = df_chart.melt(
                        id_vars='Product', 
                        value_vars=['Target', 'Current Sale'], 
                        var_name='Type', 
                        value_name='Value'
                    )
                    
                    fig = px.bar(
                        df_chart_melt,
                        x='Value',
                        y='Product',
                        color='Type',
                        orientation='h',
                        title=f"Targets vs Sales - {datetime(target_year, target_month, 1).strftime('%B %Y')}",
                        labels={'Value': 'Amount', 'Product': 'Product Category'},
                        barmode='group',
                        color_discrete_map={'Target': '#1f77b4', 'Current Sale': '#ff7f0e'},
                        text='Value',
                       
                    )
                    
                    # Format the text labels to show inside bars
                    fig.update_traces(
                        texttemplate='%{text:,.0f}',
                        textposition='inside',
                        textfont_size=24,
                        textfont_color='white',
                        insidetextanchor='middle'
                    )
                    
                    fig.update_layout(
                        height=600,
                        xaxis_title="Amount ()",
                        yaxis_title="Product Category",
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, width="stretch")
                    
                    # Export
                    
                except Exception as e:
                    st.error(f"? Error loading chef targets data: {e}")
                    st.info("Make sure the chef_sale table exists in KDS database")
            else:
                st.warning(f"?? No targets found for {selected_branch}")
        else:
            st.warning("?? No chef targets data available")
    else:
        st.error("? No branch data available")

# ========================
# TAB 5: OT TARGETS
# ========================
with tab5:
    st.header("?? Order Taker Targets")
    
    # Branch selection
    if not df_branch.empty:
        branch_names = df_branch['shop_name'].tolist()
        selected_branch_ot = st.selectbox("Select Branch", branch_names, key="ot_branch")
        shop_id_ot = df_branch[df_branch['shop_name'] == selected_branch_ot]['shop_id'].iloc[0]
        
        st.info(f"?? Showing OT performance for **{selected_branch_ot}**")
        
        # Options to filter
        hide_zero_sales = st.checkbox("Hide employees with 0 current sales", value=False)
        hide_zero_target = st.checkbox("Hide employees with 0 target", value=False)
        
        # Get OT sales data for this branch
        df_ot_branch = df_ot[df_ot['shop_id'] == shop_id_ot].copy()
        
        if not df_ot_branch.empty:
            # Get targets for this branch
            if not ot_targets.empty:
                df_ot_targets_branch = ot_targets[ot_targets['shop_id'] == shop_id_ot]
                
                # Merge sales with targets
                df_ot_perf = df_ot_branch.merge(
                    df_ot_targets_branch, 
                    on=['shop_id', 'employee_id'], 
                    how='left'
                ).fillna({'target_amount': 0})
                
                # For employees without names, use 'ID: employee_id'
                if 'employee_name' in df_ot_perf.columns:
                    df_ot_perf['employee_name'] = df_ot_perf['employee_name'].fillna(
                        df_ot_perf['employee_id'].astype(str).apply(lambda x: f'ID: {x}')
                    )
                else:
                    df_ot_perf['employee_name'] = df_ot_perf['employee_id'].astype(str).apply(lambda x: f'ID: {x}')
                
                # Apply filters
                if hide_zero_sales:
                    df_ot_perf = df_ot_perf[df_ot_perf['total_sale'] > 0]
                
                if hide_zero_target:
                    df_ot_perf = df_ot_perf[df_ot_perf['target_amount'] > 0]
                
                # Daily sales + target calculations
                employee_ids = df_ot_perf['employee_id'].dropna().astype(int).unique().tolist()
                days_in_month = monthrange(target_year, target_month)[1]
                # Ignore date filter: use actual current date for yesterday/MTD
                month_start = date(target_year, target_month, 1)
                month_end = date(target_year, target_month, days_in_month)
                ref_date = date.today()
                yesterday_date = ref_date - timedelta(days=1)

                # Remaining days based on target month
                remaining_days = max((month_end - ref_date).days, 0)

                if employee_ids:
                    conn = pool.get_connection("candelahns")
                    filter_clause, filter_params = build_filter_clause(data_mode)

                    def fetch_ot_sales(start_d: date, end_d: date) -> pd.DataFrame:
                        # Use half-open range to handle datetime sale_date
                        end_next = end_d + timedelta(days=1)
                        query = f"""
                        SELECT s.employee_id, SUM(s.Nt_amount) AS total_sale
                        FROM tblSales s
                        WHERE s.sale_date >= ? AND s.sale_date < ?
                          AND s.shop_id = ?
                          AND s.employee_id IN ({placeholders(len(employee_ids))})
                        {filter_clause}
                        GROUP BY s.employee_id
                        """
                        params = [start_d.strftime("%Y-%m-%d"), end_next.strftime("%Y-%m-%d"), shop_id_ot] + employee_ids + filter_params
                        return pd.read_sql(query, conn, params=params)

                    df_yest = fetch_ot_sales(yesterday_date, yesterday_date).rename(columns={'total_sale': 'yesterday_sale'})
                    df_mtd = fetch_ot_sales(month_start, ref_date).rename(columns={'total_sale': 'mtd_sale'})

                    df_ot_perf = df_ot_perf.merge(df_yest, on='employee_id', how='left')
                    df_ot_perf = df_ot_perf.merge(df_mtd, on='employee_id', how='left')
                else:
                    df_ot_perf['yesterday_sale'] = 0
                    df_ot_perf['mtd_sale'] = 0

                df_ot_perf['yesterday_sale'] = df_ot_perf['yesterday_sale'].fillna(0)
                df_ot_perf['mtd_sale'] = df_ot_perf['mtd_sale'].fillna(0)

                # Create display table
                ot_table = df_ot_perf[['employee_name', 'target_amount', 'total_sale', 'yesterday_sale', 'mtd_sale']].copy()
                ot_table.columns = ['OT Name', 'Target', 'Current Sale', 'Yesterday Achieved', 'MTD Sale']

                # Daily target math
                ot_table['Days in Month'] = days_in_month
                ot_table['Per-Day Target'] = ot_table['Target'] / days_in_month if days_in_month > 0 else 0
                ot_table['Today Target'] = ot_table['Per-Day Target']
                ot_table['Remaining Target'] = ot_table['Target'] - ot_table['MTD Sale']
                ot_table['Remaining Days'] = remaining_days
                ot_table['Next Day Target'] = ot_table.apply(
                    lambda row: (row['Remaining Target'] / remaining_days) if remaining_days > 0 else 0,
                    axis=1
                )
                
                # Calculate remaining and achievement
                ot_table['Remaining'] = ot_table['Target'] - ot_table['Current Sale']
                ot_table['Achievement %'] = ot_table.apply(
                    lambda row: (row['Current Sale'] / row['Target'] * 100) if row['Target'] > 0 else 0,
                    axis=1
                )
                
                # Summary metrics
                total_ot_sales = ot_table['Current Sale'].sum()
                total_ot_target = ot_table['Target'].sum()
                num_ots = len(ot_table)
                avg_achievement = ot_table['Achievement %'].mean() if len(ot_table) > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total OT Sales", format_currency(total_ot_sales))
                col2.metric("Total Target", format_currency(total_ot_target))
                col3.metric("Number of OTs", num_ots)
                col4.metric("Avg Achievement", format_percentage(avg_achievement))
                
                st.markdown("---")
                
                # Save numeric values for chart
                ot_chart_data = ot_table.copy()
                
                # Format for display
                display_ot = ot_table.copy()
                display_ot['Target'] = display_ot['Target'].apply(lambda x: format_currency(x))
                display_ot['Current Sale'] = display_ot['Current Sale'].apply(lambda x: format_currency(x))
                display_ot['MTD Sale'] = display_ot['MTD Sale'].apply(lambda x: format_currency(x))
                display_ot['Per-Day Target'] = display_ot['Per-Day Target'].apply(lambda x: format_currency(x))
                display_ot['Yesterday Achieved'] = display_ot['Yesterday Achieved'].apply(lambda x: format_currency(x))
                display_ot['Today Target'] = display_ot['Today Target'].apply(lambda x: format_currency(x))
                display_ot['Remaining Target'] = display_ot['Remaining Target'].apply(lambda x: format_currency(x))
                display_ot['Next Day Target'] = display_ot['Next Day Target'].apply(lambda x: format_currency(x))
                display_ot['Remaining'] = display_ot['Remaining'].apply(lambda x: format_currency(x))
                display_ot['Achievement %'] = display_ot['Achievement %'].apply(lambda x: f"{x:.1f}%")
                
                # Display table
                render_table(
                    display_ot[['OT Name', 'Target', 'Per-Day Target', 'Yesterday Achieved', 'Today Target', 'MTD Sale', 'Remaining Target', 'Remaining Days', 'Next Day Target', 'Current Sale', 'Remaining', 'Achievement %']], 
                    width="stretch",
                    height=400
                )
                
                # Chart
                st.markdown("---")
                st.subheader("?? Top 10 OT Performance")
                
                top_10_ot = ot_chart_data.nlargest(10, 'Current Sale')
                
                fig = px.bar(
                    top_10_ot,
                    x='Current Sale',
                    y='OT Name',
                    orientation='h',
                    title="Top 10 Order Takers by Sales",
                    labels={'Current Sale': 'Sales ()', 'OT Name': 'Order Taker'},
                    color='Achievement %',
                    color_continuous_scale='RdYlGn',
                    text='Current Sale'
                )
                
                # Add text labels inside bars
                fig.update_traces(
                    texttemplate=' %{text:,.0f}',
                    textposition='inside',
                    textfont_size=11,
                    textfont_color='white',
                    insidetextanchor='middle'
                )
                
                fig.update_layout(
                    height=500,
                    xaxis_title="Sales ()",
                    yaxis_title="Order Taker"
                )
                
                st.plotly_chart(fig, width="stretch")
                
                # Export
                
            else:
                st.warning("?? No OT targets data available")
                
                # Show sales data without targets
                display_ot_notarget = df_ot_branch[['employee_name', 'total_sale']].copy()
                display_ot_notarget['total_sale'] = display_ot_notarget['total_sale'].apply(lambda x: format_currency(x))
                render_table(display_ot_notarget, width="stretch")
        else:
            st.info("?? No OT data for this branch")
    else:
        st.error("? No branch data available")

# ========================
# TAB 7: QR COMMISSION
# ========================
with tab6:
    st.header("QR / Blinkco Commission Analysis")

    commission_rate = st.number_input(
        "Commission Rate (%)",
        0.0, 100.0, 2.0, 0.1,
        help="Commission percentage for QR sales"
    )

    end_exclusive_qr = (pd.to_datetime(end_date_str) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    @st.cache_data(ttl=300)
    def fetch_qr_commission_data(
        start_str: str,
        end_exclusive_str: str,
        branch_ids: List[int],
        mode: str,
    ) -> pd.DataFrame:
        """Fetch Blinkco transactions at sale level."""
        conn = pool.get_connection("candelahns")

        qr_query = f"""
        SELECT
            s.sale_id,
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            s.Nt_amount AS total_sale,
            s.external_ref_id
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.external_ref_type = 'Blinkco order'
        """

        qr_params: List = [start_str, end_exclusive_str] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                qr_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                qr_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                qr_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                qr_params.extend(BLOCKED_COMMENTS)

        return pd.read_sql(qr_query, conn, params=qr_params)

    @st.cache_data(ttl=300)
    def fetch_total_sales_data(
        start_str: str,
        end_exclusive_str: str,
        branch_ids: List[int],
        mode: str,
    ) -> pd.DataFrame:
        """Fetch total sales (all order types) by employee and branch."""
        conn = pool.get_connection("candelahns")
        total_query = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions_all,
            SUM(s.Nt_amount) AS total_sales_all
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
        """

        total_params: List = [start_str, end_exclusive_str] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                total_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                total_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                total_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                total_params.extend(BLOCKED_COMMENTS)

        total_query += """
        GROUP BY
            s.shop_id, sh.shop_name,
            COALESCE(e.shop_employee_id, 0),
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY total_sales_all DESC
        """
        return pd.read_sql(total_query, conn, params=total_params)

    @st.cache_data(ttl=300)
    def fetch_blink_raw_orders(start_str: str, end_exclusive_str: str) -> pd.DataFrame:
        conn = pool.get_connection("candelahns")
        blink_raw_query = """
    SELECT
        BlinkOrderId,
        OrderJson,
        CreatedAt
    FROM tblInitialRawBlinkOrder
        WHERE CreatedAt >= ? AND CreatedAt < ?
        """
        return pd.read_sql(blink_raw_query, conn, params=[start_str, end_exclusive_str])

    @st.cache_data(ttl=300)
    def fetch_qr_product_sales_data(
        start_str: str,
        end_exclusive_str: str,
        branch_ids: List[int],
        mode: str,
    ) -> pd.DataFrame:
        """Fetch Blinkco line-item product sales for product-wise commission."""
        conn = pool.get_connection("candelahns")
        product_query = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            p.Product_code,
            p.item_name AS product_name,
            SUM(li.qty) AS total_qty,
            SUM(li.qty * li.Unit_price) AS product_sales
        FROM tblSales s
        INNER JOIN tblSalesLineItems li ON s.sale_id = li.sale_id
        LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p ON pi.Product_ID = p.Product_ID
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.external_ref_type = 'Blinkco order'
        """

        product_params: List = [start_str, end_exclusive_str] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                product_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                product_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                product_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                product_params.extend(BLOCKED_COMMENTS)

        product_query += """
        GROUP BY s.shop_id, sh.shop_name, p.Product_code, p.item_name
        ORDER BY product_sales DESC
        """
        return pd.read_sql(product_query, conn, params=product_params)

    @st.cache_data(ttl=300)
    def fetch_employee_data_quality() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
        """Employee name/code duplication diagnostics from tblDefShopEmployees."""
        conn = pool.get_connection("candelahns")

        stats_q = """
        SELECT
          COUNT(*) AS total_employees,
          COUNT(DISTINCT LTRIM(RTRIM(COALESCE(field_Code,'')))) AS distinct_codes
        FROM tblDefShopEmployees
        """
        stats = pd.read_sql(stats_q, conn).to_dict("records")[0]

        dup_code_q = """
        SELECT TOP 50
          LTRIM(RTRIM(field_Code)) AS field_code,
          COUNT(DISTINCT shop_employee_id) AS distinct_employee_ids,
          MIN(shop_employee_id) AS min_employee_id,
          MAX(shop_employee_id) AS max_employee_id
        FROM tblDefShopEmployees
        WHERE field_Code IS NOT NULL AND LTRIM(RTRIM(field_Code)) <> ''
        GROUP BY LTRIM(RTRIM(field_Code))
        HAVING COUNT(DISTINCT shop_employee_id) > 1
        ORDER BY COUNT(DISTINCT shop_employee_id) DESC, COUNT(*) DESC
        """
        df_dup_codes = pd.read_sql(dup_code_q, conn)

        dup_names_q = """
        WITH dup_names AS (
          SELECT field_name
          FROM tblDefShopEmployees
          GROUP BY field_name
          HAVING COUNT(DISTINCT shop_employee_id) > 1
        )
        SELECT
          e.field_name AS employee_name,
          e.shop_employee_id AS employee_id,
          LTRIM(RTRIM(COALESCE(e.field_Code,''))) AS field_code,
          e.shop_id,
          sh.shop_name,
          e.start_date,
          e.end_date
        FROM tblDefShopEmployees e
        LEFT JOIN tblDefShops sh ON e.shop_id = sh.shop_id
        INNER JOIN dup_names d ON e.field_name = d.field_name
        ORDER BY e.field_name, e.shop_employee_id
        """
        df_dup_names = pd.read_sql(dup_names_q, conn)

        out_stats = {
            "total_employees": int(stats.get("total_employees") or 0),
            "distinct_codes": int(stats.get("distinct_codes") or 0),
            "duplicate_codes_rows": int(len(df_dup_codes)),
            "duplicate_names_rows": int(len(df_dup_names)),
        }
        return df_dup_codes, df_dup_names, out_stats

    if selected_branches:
        try:
            df_qr = fetch_qr_commission_data(start_date_str, end_exclusive_qr, selected_branches, data_mode)
            df_total_sales = fetch_total_sales_data(start_date_str, end_exclusive_qr, selected_branches, data_mode)
            df_blink_raw = fetch_blink_raw_orders(start_date_str, end_exclusive_qr)
            df_qr_products = fetch_qr_product_sales_data(start_date_str, end_exclusive_qr, selected_branches, data_mode)
        except Exception as e:
            st.error(f"Database error: {e}")
            df_qr = pd.DataFrame()
            df_total_sales = pd.DataFrame()
            df_blink_raw = pd.DataFrame()
            df_qr_products = pd.DataFrame()
    else:
        df_qr = pd.DataFrame()
        df_total_sales = pd.DataFrame()
        df_blink_raw = pd.DataFrame()
        df_qr_products = pd.DataFrame()

    raw_blink_rows = len(df_blink_raw)
    df_blink = prepare_blink_orders(df_blink_raw)
    deduped_blink_rows = len(df_blink)

    if not df_qr.empty:
        df_qr['total_sale'] = pd.to_numeric(df_qr['total_sale'], errors='coerce').fillna(0.0)
        df_merged = df_qr.merge(
            df_blink,
            left_on='external_ref_id',
            right_on='BlinkOrderId',
            how='left'
        )
        df_merged['Indoge_total_price'] = pd.to_numeric(df_merged['Indoge_total_price'], errors='coerce').fillna(0.0)
        df_merged['BlinkOrderId'] = df_merged['BlinkOrderId'].fillna('-')
        df_merged['json_parse_ok'] = df_merged['json_parse_ok'].fillna(False)
        df_merged['difference'] = df_merged['Indoge_total_price'] - df_merged['total_sale']
        df_merged['Candelahns_commission'] = df_merged['total_sale'] * (commission_rate / 100)
        df_merged['Indoge_commission'] = df_merged['Indoge_total_price'] * (commission_rate / 100)
        df_merged = add_transaction_quality_flags(df_merged)

        # Legacy top metrics (as before)
        total_sale = df_merged['total_sale'].sum()
        total_cand_comm = df_merged['Candelahns_commission'].sum()
        total_indoge_comm = df_merged['Indoge_commission'].sum()
        total_tx = len(df_merged)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total QR Sales", format_currency(total_sale))
        col2.metric("Candelahns Commission", format_currency(total_cand_comm))
        col3.metric("Indoge Commission", format_currency(total_indoge_comm))
        col4.metric("Transactions", f"{total_tx:,}")
    else:
        df_merged = pd.DataFrame()

    st.markdown("### Split Report Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        employee_search = st.text_input("Search Employee", key="qr_split_employee_search")
    with c2:
        branch_options = sorted(df_total_sales['shop_name'].dropna().astype(str).unique().tolist()) if not df_total_sales.empty else []
        selected_branch_names = st.multiselect(
            "Branches in report",
            options=branch_options,
            default=branch_options,
            key="qr_split_branch_filter"
        )
    with c3:
        include_zero_rows = st.checkbox("Include zero rows", value=True, key="qr_split_include_zero")
        include_unassigned = st.checkbox("Include Online/Unassigned", value=True, key="qr_split_include_unassigned")

        sort_choice = st.selectbox(
            "Ranking",
            [
                "Total Sales (desc)",
                "Blinkco Sales (desc)",
                "Blinkco Share % (desc)",
                "Diff (Total-Blinkco) (desc)",
                "Commission Total (desc)",
            ],
            index=0,
            key="qr_split_sort_choice"
        )

        df_dup_codes, df_dup_names, employee_dq_stats = fetch_employee_data_quality()
        with st.expander("Data Quality (Employees)", expanded=False):
            st.caption("Note: `field_Code` is not unique; do not use it for grouping totals.")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Employees", f"{employee_dq_stats.get('total_employees', 0):,}")
            c2.metric("Distinct Codes", f"{employee_dq_stats.get('distinct_codes', 0):,}")
            c3.metric("Duplicate Codes", f"{employee_dq_stats.get('duplicate_codes_rows', 0):,}")
            c4.metric("Duplicate Names", f"{employee_dq_stats.get('duplicate_names_rows', 0):,}")

            st.subheader("Duplicate Field Codes (Top 50)")
            render_table(df_dup_codes, width="stretch", hide_index=True, height=260)

            st.subheader("Duplicate Names: IDs + Field Code")
            render_table(df_dup_names, width="stretch", hide_index=True, height=320)

    if not df_merged.empty:
        blinkco_summary = (
            df_merged.groupby(['employee_id', 'employee_name', 'shop_id', 'shop_name'], as_index=False)
            .agg(
                total_sales_blinkco=('total_sale', 'sum'),
                total_transactions_blinkco=('sale_id', 'count')
            )
        )
    else:
        blinkco_summary = pd.DataFrame(
            columns=[
                'employee_id', 'employee_name', 'shop_id', 'shop_name',
                'total_sales_blinkco', 'total_transactions_blinkco'
            ]
        )

    split_report = build_split_report(df_total_sales, blinkco_summary, commission_rate)
    split_report_filtered = apply_split_filters(
        split_report,
        employee_search=employee_search,
        branches=selected_branch_names,
        include_zero_rows=include_zero_rows,
        include_unassigned=include_unassigned,
    )

    if not split_report.empty:
        # Reconciliation + sanity checks
        recon_all = abs(split_report['total_sales_all'].sum() - pd.to_numeric(df_total_sales['total_sales_all'], errors='coerce').fillna(0).sum())
        recon_blink = abs(split_report['total_sales_blinkco'].sum() - blinkco_summary['total_sales_blinkco'].sum()) if not blinkco_summary.empty else 0.0
        invalid_share_rows = int(((split_report['blinkco_share_pct'] < 0) | (split_report['blinkco_share_pct'] > 100)).sum())
        bad_comm_rows = int((
            (split_report['commission_total_sales'] - split_report['total_sales_all'] * (commission_rate / 100)).abs() > 0.01
        ).sum())

        if recon_all > 1 or recon_blink > 1 or invalid_share_rows > 0 or bad_comm_rows > 0:
            st.warning(
                f"Quality warning | recon_all_diff={recon_all:,.2f}, recon_blink_diff={recon_blink:,.2f}, "
                f"invalid_share_rows={invalid_share_rows}, bad_comm_rows={bad_comm_rows}"
            )

        # KPI cards (filtered)
        k_all = split_report_filtered['total_sales_all'].sum() if not split_report_filtered.empty else 0.0
        k_blink = split_report_filtered['total_sales_blinkco'].sum() if not split_report_filtered.empty else 0.0
        k_wo = split_report_filtered['total_sales_without_blinkco'].sum() if not split_report_filtered.empty else 0.0
        k_comm = split_report_filtered['commission_total_sales'].sum() if not split_report_filtered.empty else 0.0
        k_share = (k_blink / k_all * 100) if k_all else 0.0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Sales", format_currency(k_all))
        m2.metric("Blinkco Sales", format_currency(k_blink))
        m3.metric("Sales w/o Blinkco", format_currency(k_wo))
        m4.metric("Commission on Total", format_currency(k_comm))
        m5.metric("Blinkco Share", f"{k_share:.2f}%")

        st.markdown("---")
        st.subheader("Employee + Branch Sales Split Report")

        sort_map = {
            "Total Sales (desc)": "total_sales_all",
            "Blinkco Sales (desc)": "total_sales_blinkco",
            "Blinkco Share % (desc)": "blinkco_share_pct",
            "Diff (Total-Blinkco) (desc)": "diff_total_minus_blinkco",
            "Commission Total (desc)": "commission_total_sales",
        }
        sort_col = sort_map.get(sort_choice, "total_sales_all")
        split_sorted = split_report_filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)
        split_sorted.index = range(1, len(split_sorted) + 1)
        split_sorted.index.name = "#"

        show = split_sorted.copy()
        show['blinkco_share_pct'] = show['blinkco_share_pct'].apply(lambda x: f"{x:.2f}%")
        show['without_blinkco_share_pct'] = show['without_blinkco_share_pct'].apply(lambda x: f"{x:.2f}%")
        for col in [
            'total_sales_all', 'total_sales_blinkco', 'total_sales_without_blinkco',
            'diff_total_minus_blinkco', 'commission_total_sales', 'commission_blinkco_sales',
            'commission_without_blinkco_sales'
        ]:
            show[col] = show[col].apply(format_currency)

        render_table(
            show[[
                'employee_id', 'employee_code', 'employee_name', 'shop_name', 'total_transactions_all', 'total_transactions_blinkco',
                'total_transactions_without_blinkco', 'total_sales_all', 'total_sales_blinkco',
                'total_sales_without_blinkco', 'blinkco_share_pct', 'without_blinkco_share_pct',
                'diff_total_minus_blinkco', 'commission_total_sales', 'commission_blinkco_sales',
                'commission_without_blinkco_sales', 'has_blink_order', 'blink_mismatch_flag'
            ]],
            width="stretch",
            hide_index=False,
            height=520,
        )

        split_summary = pd.DataFrame([{
            'employees_rows': len(split_report_filtered),
            'total_sales_all': k_all,
            'total_sales_blinkco': k_blink,
            'total_sales_without_blinkco': k_wo,
            'blinkco_share_pct': round(k_share, 2),
            'commission_total_sales': k_comm,
            'commission_blinkco_sales': split_report_filtered['commission_blinkco_sales'].sum() if not split_report_filtered.empty else 0.0,
            'commission_without_blinkco_sales': split_report_filtered['commission_without_blinkco_sales'].sum() if not split_report_filtered.empty else 0.0,
        }])

        st.download_button(
            label="Download Split Report Full Excel",
            data=export_to_excel(
                split_report.sort_values('total_sales_all', ascending=False),
                "Split Report Full",
            ),
            file_name="qr_employee_branch_sales_split_full.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="Download Split Report Filtered Excel",
            data=export_to_excel(
                split_report_filtered.sort_values(sort_col, ascending=False),
                "Split Report Filtered",
            ),
            file_name="qr_employee_branch_sales_split_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="Download Split Summary Excel",
            data=export_to_excel(split_summary, "Split Summary"),
            file_name="qr_employee_branch_sales_split_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("No total sales data available for split report.")

    if not df_merged.empty:
        st.markdown("---")
        st.subheader("Detailed Transactions")

        tx_show = df_merged.copy()
        if selected_branch_names:
            tx_show = tx_show[tx_show['shop_name'].isin(selected_branch_names)]
        if employee_search.strip():
            tx_show = tx_show[tx_show['employee_name'].astype(str).str.contains(employee_search.strip(), case=False, na=False)]
        if not include_unassigned:
            tx_show = tx_show[tx_show['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned']

        tx_show = tx_show.sort_values('total_sale', ascending=False).reset_index(drop=True)
        tx_show.index = range(1, len(tx_show) + 1)
        tx_show.index.name = "#"

        df_display = tx_show.copy()
        df_display['BlinkOrderId'] = df_display['BlinkOrderId'].astype(str)
        df_display['Matched'] = df_display['difference'].apply(lambda x: '?' if abs(x) <= 1 else '?')
        denom = df_display['Indoge_total_price'].replace(0, pd.NA)
        match_pct = (1 - (df_display['difference'].abs() / denom)) * 100
        df_display['Match %'] = match_pct.fillna(0).clip(lower=0, upper=100).round(1)

        def diff_color(val):
            try:
                if pd.isna(val):
                    return ''
                if val > 0:
                    return 'color: green'
                if val < 0:
                    return 'color: red'
            except Exception:
                return ''
            return ''

        styler = (
            df_display[[
                'shop_name',
                'employee_name',
                'total_sale',
                'Candelahns_commission',
                'Indoge_total_price',
                'Indoge_commission',
                'difference',
                'Matched',
                'Match %',
                'BlinkOrderId',
                'external_ref_id'
            ]]
            .style
            .format({
                'total_sale': "{:,.0f}",
                'Candelahns_commission': "{:,.0f}",
                'Indoge_total_price': lambda x: "{:,.0f}".format(x) if x > 0 else "-",
                'Indoge_commission': lambda x: "{:,.0f}".format(x) if x > 0 else "-",
                'difference': lambda x: "{:,.0f}".format(x) if x != 0 else "-",
            })
            .applymap(diff_color, subset=['difference'])
        )

        render_table(
            styler,
            width="stretch",
            hide_index=False,
            height=420,
        )

        # Legacy tables restored (same style/structure as before)
        st.markdown("---")
        st.subheader("Employee-wise Totals (with Shop)")

        employee_summary = df_merged.groupby(['employee_id', 'employee_code', 'employee_name', 'shop_id', 'shop_name'], as_index=False).agg({
            'total_sale': 'sum',
            'Candelahns_commission': 'sum',
            'Indoge_total_price': 'sum',
            'Indoge_commission': 'sum',
            'external_ref_id': 'count'
        }).rename(columns={'external_ref_id': 'transaction_count'})
        # Keep both legacy employee tables aligned by excluding unassigned rows.
        employee_summary = employee_summary[
            employee_summary['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
        ].copy()

        # Attach employment dates + active/inactive status (display/diagnostics only).
        try:
            conn = pool.get_connection("candelahns")
            placeholders_str = ",".join(["?" for _ in selected_branches])
            emp_meta_query = f"""
            SELECT
                shop_employee_id,
                shop_id,
                start_date,
                end_date
            FROM tblDefShopEmployees
            WHERE shop_id IN ({placeholders_str})
            """
            emp_meta = pd.read_sql(emp_meta_query, conn, params=selected_branches)
            emp_meta["shop_employee_id"] = pd.to_numeric(emp_meta["shop_employee_id"], errors="coerce").fillna(0).astype(int)
            emp_meta["shop_id"] = pd.to_numeric(emp_meta["shop_id"], errors="coerce").fillna(0).astype(int)
            employee_summary["employee_id"] = pd.to_numeric(employee_summary["employee_id"], errors="coerce").fillna(0).astype(int)
            employee_summary["shop_id"] = pd.to_numeric(employee_summary["shop_id"], errors="coerce").fillna(0).astype(int)
            employee_summary = employee_summary.merge(
                emp_meta,
                left_on=["employee_id", "shop_id"],
                right_on=["shop_employee_id", "shop_id"],
                how="left",
            )
            employee_summary = employee_summary.drop(columns=["shop_employee_id"], errors="ignore")
        except Exception:
            employee_summary["start_date"] = pd.NaT
            employee_summary["end_date"] = pd.NaT

        range_start = pd.to_datetime(start_date_str)
        range_end = pd.to_datetime(end_date_str)
        employee_summary["employment_start_date"] = pd.to_datetime(employee_summary.get("start_date"), errors="coerce")
        employee_summary["employment_end_date"] = pd.to_datetime(employee_summary.get("end_date"), errors="coerce")
        start_ok = employee_summary["employment_start_date"].isna() | (employee_summary["employment_start_date"] <= range_end)
        end_ok = employee_summary["employment_end_date"].isna() | (employee_summary["employment_end_date"] >= range_start)
        employee_summary["active_in_range"] = (start_ok & end_ok).fillna(True)
        employee_summary["employment_status"] = employee_summary["active_in_range"].map(
            lambda x: "Active" if bool(x) else "Inactive"
        )

        emp_show = employee_summary.sort_values('total_sale', ascending=False).reset_index(drop=True)
        emp_show.index = range(1, len(emp_show) + 1)
        emp_show.index.name = "#"

        emp_show['total_sale'] = emp_show['total_sale'].apply(lambda x: f"{x:,.0f}")
        emp_show['Candelahns_commission'] = emp_show['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
        emp_show['Indoge_total_price'] = emp_show['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
        emp_show['Indoge_commission'] = emp_show['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

        render_table(
            emp_show[[
                'employee_id',
                'employee_code',
                'employee_name',
                'shop_name',
                'employment_status',
                'transaction_count',
                'total_sale',
                'Candelahns_commission',
                'Indoge_total_price',
                'Indoge_commission'
            ]],
            width="stretch",
            hide_index=False,
            column_config={
                "employee_id": st.column_config.Column("Emp ID", width="small"),
                "employee_code": st.column_config.Column("Field Code", width="small"),
                "employee_name": st.column_config.Column("Employee", width="medium"),
                "shop_name": st.column_config.Column("Shop", width="medium"),
                "employment_status": st.column_config.Column("Status", width="small"),
                "transaction_count": st.column_config.Column("Tx Count", width="small"),
                "total_sale": st.column_config.Column("Total Sales", width="medium"),
                "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
            }
        )

        st.markdown("---")
        st.subheader("Employee-wise Totals (with Shop) - No Total Sales / Candelahns")
        show_zero_qr = st.checkbox("Show all employees (including zero QR sales)", value=True, key="show_zero_qr_toggle_legacy")
        employment_filter = st.selectbox(
            "Employment Filter",
            ["Active only", "Inactive only", "Both"],
            index=0,
            key="qr_employment_filter",
            help="Uses tblDefShopEmployees.start_date/end_date to decide active/inactive in selected date range."
        )

        try:
            conn = pool.get_connection("candelahns")
            placeholders_str = ",".join(["?" for _ in selected_branches])
            all_employees_query = f"""
            SELECT DISTINCT
                e.shop_employee_id,
                LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
                e.field_name AS employee_name,
                e.shop_id,
                sh.shop_name,
                e.start_date,
                e.end_date
            FROM tblDefShopEmployees e
            INNER JOIN tblDefShops sh ON e.shop_id = sh.shop_id
            WHERE e.shop_id IN ({placeholders_str})
            ORDER BY e.shop_id, e.field_name
            """
            all_employees_df = pd.read_sql(all_employees_query, conn, params=selected_branches)
            all_employees_df = all_employees_df.drop_duplicates(subset=['shop_employee_id', 'shop_id']).copy()

            emp_no_sales = all_employees_df.merge(
                employee_summary,
                left_on=['shop_employee_id', 'shop_id'],
                right_on=['employee_id', 'shop_id'],
                how='left'
            ).fillna({
                'total_sale': 0,
                'Candelahns_commission': 0,
                'Indoge_total_price': 0,
                'Indoge_commission': 0,
                'transaction_count': 0
            })
            emp_no_sales['employee_name'] = emp_no_sales['employee_name_x'].fillna(emp_no_sales.get('employee_name_y'))
            emp_no_sales['shop_name'] = emp_no_sales['shop_name_x'].fillna(emp_no_sales.get('shop_name_y'))
            emp_no_sales['employee_code'] = emp_no_sales['employee_code_x'].fillna(emp_no_sales.get('employee_code_y'))
            emp_no_sales['start_date'] = emp_no_sales.get('start_date_x').fillna(emp_no_sales.get('start_date_y'))
            emp_no_sales['end_date'] = emp_no_sales.get('end_date_x').fillna(emp_no_sales.get('end_date_y'))
            emp_no_sales['employee_id'] = pd.to_numeric(
                emp_no_sales['shop_employee_id'], errors='coerce'
            ).fillna(0).astype(int)

            # Employment status (active/inactive in selected date range)
            range_start = pd.to_datetime(start_date_str, errors='coerce').date()
            range_end = pd.to_datetime(end_date_str, errors='coerce').date()
            emp_no_sales['employment_start_date'] = pd.to_datetime(emp_no_sales.get('start_date'), errors='coerce').dt.date
            emp_no_sales['employment_end_date'] = pd.to_datetime(emp_no_sales.get('end_date'), errors='coerce').dt.date
            start_ok = emp_no_sales['employment_start_date'].isna() | (emp_no_sales['employment_start_date'] <= range_end)
            end_ok = emp_no_sales['employment_end_date'].isna() | (emp_no_sales['employment_end_date'] >= range_start)
            emp_no_sales['active_in_range'] = (start_ok & end_ok).fillna(True)
            emp_no_sales['employment_status'] = emp_no_sales['active_in_range'].map(lambda x: "Active" if bool(x) else "Inactive")

            # Keep this table aligned with Branch-wise Totals (which excludes Online/Unassigned)
            emp_no_sales = emp_no_sales[
                emp_no_sales['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
            ].copy()

            # Keep an unfiltered roster copy for the overall multi-sheet Excel export.
            emp_no_sales_all_download = emp_no_sales.copy()

            if employment_filter == "Active only":
                emp_no_sales = emp_no_sales[emp_no_sales['active_in_range']].copy()
            elif employment_filter == "Inactive only":
                emp_no_sales = emp_no_sales[~emp_no_sales['active_in_range']].copy()

            if not show_zero_qr:
                emp_no_sales = emp_no_sales[emp_no_sales['Indoge_total_price'] > 0]

            emp_no_sales = emp_no_sales.sort_values(['shop_id', 'Indoge_total_price'], ascending=[True, False]).reset_index(drop=True)
            emp_no_sales.index = range(1, len(emp_no_sales) + 1)
            emp_no_sales.index.name = "#"

        except Exception as e:
            st.warning(f"Could not fetch all employees: {e}")
            emp_no_sales = employee_summary.copy()
            emp_no_sales = emp_no_sales[
                emp_no_sales['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
            ].copy()
            emp_no_sales_all_download = emp_no_sales.copy()

        # Keep raw numeric copy for Excel export before display formatting.
        for col, default in [
            ("employment_status", ""),
            ("employment_start_date", pd.NaT),
            ("employment_end_date", pd.NaT),
            ("active_in_range", True),
        ]:
            if col not in emp_no_sales.columns:
                emp_no_sales[col] = default
        emp_no_sales_download = emp_no_sales.copy()

        emp_no_sales['Indoge_total_price'] = emp_no_sales['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
        emp_no_sales['Indoge_commission'] = emp_no_sales['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

        render_table(
                emp_no_sales[[
                    'employee_id',
                    'employee_code',
                    'employee_name',
                    'shop_name',
                    'employment_status',
                    'employment_start_date',
                    'employment_end_date',
                    'transaction_count',
                    'Indoge_total_price',
                    'Indoge_commission'
                ]],
            width="stretch",
            hide_index=False,
                column_config={
                    "employee_id": st.column_config.Column("Emp ID", width="small"),
                    "employee_code": st.column_config.Column("Field Code", width="small"),
                    "employee_name": st.column_config.Column("Employee", width="medium"),
                    "shop_name": st.column_config.Column("Shop", width="medium"),
                    "employment_status": st.column_config.Column("Status", width="small"),
                    "employment_start_date": st.column_config.Column("Start", width="small"),
                    "employment_end_date": st.column_config.Column("End", width="small"),
                    "transaction_count": st.column_config.Column("Tx Count", width="small"),
                    "Indoge_total_price": st.column_config.Column("QR Total Sales", width="medium"),
                    "Indoge_commission": st.column_config.Column("QR Commission", width="medium"),
                }
            )

        st.download_button(
            label="Download Employee + Shop Summary (No Sales/Candelahns) Excel",
            data=export_to_excel(emp_no_sales_download, "Employee Shop Summary"),
            file_name="qr_employee_shop_summary_no_sales.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.subheader("Employee-wise Pivot (No Total Sales / Candelahns)")
        pivot_metric = st.selectbox(
            "Pivot Metric",
            options=["QR Total Sales", "QR Commission", "Tx Count"],
            index=0,
            key="qr_emp_pivot_metric"
        )

        metric_col_map = {
            "QR Total Sales": "Indoge_total_price",
            "QR Commission": "Indoge_commission",
            "Tx Count": "transaction_count",
        }
        metric_col = metric_col_map[pivot_metric]

        pivot_source = emp_no_sales.copy()
        if metric_col in ["Indoge_total_price", "Indoge_commission"]:
            pivot_source[metric_col] = pd.to_numeric(pivot_source[metric_col], errors="coerce").fillna(0.0)
        else:
            pivot_source[metric_col] = pd.to_numeric(pivot_source[metric_col], errors="coerce").fillna(0).astype(int)

        pivot_df = pivot_source.pivot_table(
            index=["employee_id", "employee_code", "employee_name"],
            columns="shop_name",
            values=metric_col,
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        branch_cols = [c for c in pivot_df.columns if c not in ["employee_id", "employee_code", "employee_name"]]
        pivot_df["Grand Total"] = pivot_df[branch_cols].sum(axis=1) if branch_cols else 0
        pivot_df = pivot_df.sort_values("Grand Total", ascending=False).reset_index(drop=True)

        total_row = {"employee_id": "", "employee_code": "", "employee_name": "Branch Total"}
        for col in branch_cols + ["Grand Total"]:
            total_row[col] = pivot_df[col].sum() if col in pivot_df.columns else 0
        pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])], ignore_index=True)

        pivot_df.index = range(1, len(pivot_df) + 1)
        pivot_df.index.name = "#"

        pivot_show = pivot_df.copy()
        if metric_col in ["Indoge_total_price", "Indoge_commission"]:
            for col in branch_cols + ["Grand Total"]:
                pivot_show[col] = pivot_show[col].apply(lambda x: f"{x:,.0f}")

        render_table(
            pivot_show,
            width="stretch",
            hide_index=False,
            height=420,
            column_config={
                "employee_id": st.column_config.Column("Emp ID", width="small"),
                "employee_code": st.column_config.Column("Field Code", width="small"),
                "employee_name": st.column_config.Column("Employee", width="medium"),
                "Grand Total": st.column_config.Column("Grand Total", width="medium"),
            }
        )

        st.download_button(
            label="Download Employee Pivot Excel",
            data=export_to_excel(pivot_df, "Employee Pivot"),
            file_name="qr_employee_pivot_no_sales_candelahns.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.subheader("Branch-wise Totals")

        branch_source = df_merged[
            df_merged['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
        ].copy()

        branch_summary = branch_source.groupby('shop_name', as_index=False).agg({
            'total_sale': 'sum',
            'Candelahns_commission': 'sum',
            'Indoge_total_price': 'sum',
            'Indoge_commission': 'sum',
            'external_ref_id': 'count'
        }).rename(columns={'external_ref_id': 'transaction_count'})

        branch_show = branch_summary.sort_values('total_sale', ascending=False).reset_index(drop=True)
        branch_show.index = range(1, len(branch_show) + 1)
        branch_show.index.name = "#"
        branch_show['total_sale'] = branch_show['total_sale'].apply(lambda x: f"{x:,.0f}")
        branch_show['Candelahns_commission'] = branch_show['Candelahns_commission'].apply(lambda x: f"{x:,.0f}")
        branch_show['Indoge_total_price'] = branch_show['Indoge_total_price'].apply(lambda x: f"{x:,.0f}")
        branch_show['Indoge_commission'] = branch_show['Indoge_commission'].apply(lambda x: f"{x:,.0f}")

        render_table(
            branch_show[[
                'shop_name',
                'transaction_count',
                'total_sale',
                'Candelahns_commission',
                'Indoge_total_price',
                'Indoge_commission'
            ]],
            width="stretch",
            hide_index=False,
            column_config={
                "shop_name": st.column_config.Column("Branch", width="medium"),
                "transaction_count": st.column_config.Column("Tx Count", width="small"),
                "total_sale": st.column_config.Column("Total Sales", width="medium"),
                "Candelahns_commission": st.column_config.Column("Candelahns Comm.", width="medium"),
                "Indoge_total_price": st.column_config.Column("Indoge Total", width="medium"),
                "Indoge_commission": st.column_config.Column("Indoge Comm.", width="medium"),
            }
        )

        st.download_button(
            label="Download Employee + Shop Summary Excel",
            data=export_to_excel(
                employee_summary.sort_values('total_sale', ascending=False),
                "Employee Totals",
            ),
            file_name="qr_employee_shop_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="Download Branch Summary Excel",
            data=export_to_excel(
                branch_summary.sort_values('total_sale', ascending=False),
                "Branch Totals",
            ),
            file_name="qr_branch_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Product-wise commission (restored/added in QR tab)
        st.markdown("---")
        st.subheader("Product-wise Commission (Blinkco)")

        if not df_qr_products.empty:
            prod_overall = (
                df_qr_products.groupby(['Product_code', 'product_name'], as_index=False)
                .agg(
                    total_qty=('total_qty', 'sum'),
                    product_sales=('product_sales', 'sum')
                )
                .sort_values('product_sales', ascending=False)
                .reset_index(drop=True)
            )
            prod_overall['product_commission'] = prod_overall['product_sales'] * (commission_rate / 100.0)

            prod_show = prod_overall.copy()
            prod_show.index = range(1, len(prod_show) + 1)
            prod_show.index.name = "#"
            prod_show['total_qty'] = prod_show['total_qty'].map(lambda x: f"{x:,.2f}")
            prod_show['product_sales'] = prod_show['product_sales'].apply(format_currency)
            prod_show['product_commission'] = prod_show['product_commission'].apply(format_currency)

            render_table(
                prod_show[['Product_code', 'product_name', 'total_qty', 'product_sales', 'product_commission']],
                width="stretch",
                hide_index=False,
                height=380,
                column_config={
                    "Product_code": st.column_config.Column("Product Code", width="small"),
                    "product_name": st.column_config.Column("Product", width="large"),
                    "total_qty": st.column_config.Column("Qty", width="small"),
                    "product_sales": st.column_config.Column("Total Sales", width="medium"),
                    "product_commission": st.column_config.Column("Commission", width="medium"),
                }
            )

            st.download_button(
                label="Download Product-wise Commission Excel",
                data=export_to_excel(prod_overall, "Product Commission"),
                file_name="qr_product_wise_commission.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No Blinkco product-wise data available for this period.")

        st.markdown("---")
        st.subheader("Transaction Quality Flags Summary")
        if not df_merged.empty:
            q_stats = []
            for flag_col, label in [
                ('is_mismatch', 'Total Mismatches (Candel vs Blink)'),
                ('is_unassigned', 'Unassigned Employees'),
                ('is_blink_only', 'Blinkco-only (missing in Candelahns)'),
                ('is_candel_only', 'Candelahns-only (missing in Blinkco)'),
            ]:
                count = int(df_merged[flag_col].sum())
                q_stats.append({'Metric': label, 'Count': count})

            quality_df = pd.DataFrame(q_stats)
            render_table(quality_df, width="stretch", height=220)
        else:
            quality_df = pd.DataFrame()

        overall_tables: Dict[str, pd.DataFrame] = {
            "Split Report (Filtered)": split_report_filtered.sort_values(sort_col, ascending=False)
            if 'split_report_filtered' in locals() and not split_report_filtered.empty
            else pd.DataFrame(),
            "Split Report (Full)": split_report.sort_values("total_sales_all", ascending=False)
            if 'split_report' in locals() and not split_report.empty
            else pd.DataFrame(),
            "Transactions (QR)": df_merged.copy(),
            "Employee Totals": employee_summary.sort_values("total_sale", ascending=False).copy()
            if 'employee_summary' in locals() and not employee_summary.empty
            else pd.DataFrame(),
            "Employee Totals (All)": emp_no_sales_all_download.copy()
            if 'emp_no_sales_all_download' in locals() and emp_no_sales_all_download is not None
            else pd.DataFrame(),
            "Employee Pivot": pivot_df.copy() if 'pivot_df' in locals() and pivot_df is not None else pd.DataFrame(),
            "Branch Totals": branch_summary.sort_values("total_sale", ascending=False).copy()
            if 'branch_summary' in locals() and not branch_summary.empty
            else pd.DataFrame(),
            "Quality Summary": quality_df.copy(),
            "DQ Duplicate Codes": df_dup_codes.copy() if df_dup_codes is not None else pd.DataFrame(),
            "DQ Duplicate Names": df_dup_names.copy() if df_dup_names is not None else pd.DataFrame(),
        }

        st.download_button(
            label="Download QR Tab Excel (All Sheets)",
            data=export_tables_to_excel(overall_tables),
            file_name=f"qr_tab_{start_date_str}_to_{end_date_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="Download Detailed Transactions Excel",
            data=export_to_excel(df_merged, "Transactions"),
            file_name="qr_detailed_with_commissions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="Download Data Quality Checks Excel",
            data=export_to_excel(quality_df, "Data Quality"),
            file_name="qr_data_quality_checks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No QR/Blinkco transaction data available.")
# ========================
# TAB 7: MATERIAL COST COMMISSION
# ========================
with tab7:
    material_cost_data = get_material_cost_commission_data()

    if not material_cost_data.empty:
        with st.expander("Product Commission Setup Overview", expanded=False):
            total_material_cost = material_cost_data["material_cost"].sum()
            total_commission = material_cost_data["commission"].sum()
            avg_commission_rate = (total_commission / total_material_cost * 100) if total_material_cost > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Material Cost", format_currency(total_material_cost / len(material_cost_data)))
            col2.metric("Avg Commission", format_currency(total_commission / len(material_cost_data)))
            col3.metric("Avg Rate", f"{avg_commission_rate:.1f}%")

            st.subheader("All Registered Products")
            display_material = material_cost_data.copy()
            display_material["material_cost"] = display_material["material_cost"].apply(format_currency)
            display_material["commission"] = display_material["commission"].apply(format_currency)
            render_table(
                display_material[["product_code", "product_name", "material_cost", "commission"]],
                width="stretch",
                height=300,
            )

        st.markdown("---")
        st.subheader("Real-Time Commission Analysis")
        st.markdown(f"**Period:** {start_date_str} to {end_date_str}")
        st.caption(f"Data mode: {data_mode}. Commission setup uses built-in 73 products (no DB table required).")

        st.markdown("### Branch Summary")
        branch_comm_df = get_branch_material_cost_summary(
            start_date_str, end_date_str, selected_branches, data_mode=data_mode
        )
        if not branch_comm_df.empty:
            df_branch_show = branch_comm_df.copy()
            df_branch_show["total_sales"] = df_branch_show["total_sales"].apply(format_currency)
            df_branch_show["total_material_cost"] = df_branch_show["total_material_cost"].apply(format_currency)
            df_branch_show["total_commission"] = df_branch_show["total_commission"].apply(format_currency)
            df_branch_show["avg_commission_rate"] = df_branch_show["avg_commission_rate"].apply(lambda x: f"{x:.1f}%")
            render_table(
                df_branch_show[["shop_name", "total_units_sold", "total_sales", "total_material_cost", "total_commission", "avg_commission_rate"]],
                width="stretch",
            )
        else:
            st.info("No commission data for selected branches in this period.")

        st.markdown("### Employee Summary")
        emp_comm_df = get_employee_material_cost_summary(
            start_date_str, end_date_str, selected_branches, data_mode=data_mode
        )
        if not emp_comm_df.empty:
            df_emp_show = emp_comm_df.copy()
            df_emp_show["total_sales"] = df_emp_show["total_sales"].apply(format_currency)
            df_emp_show["total_material_cost"] = df_emp_show["total_material_cost"].apply(format_currency)
            df_emp_show["total_commission"] = df_emp_show["total_commission"].apply(format_currency)
            df_emp_show["avg_commission_rate"] = df_emp_show["avg_commission_rate"].apply(lambda x: f"{x:.1f}%")
            render_table(
                df_emp_show[["employee_name", "shop_name", "total_units_sold", "total_sales", "total_material_cost", "total_commission"]],
                width="stretch",
                height=400,
            )
        else:
            st.info("No employee commission data for this period.")

        st.markdown("### Product-wise by Branch")
        branch_product_comm_df = get_branch_product_material_cost_summary(
            start_date_str, end_date_str, selected_branches, data_mode=data_mode
        )
        if not branch_product_comm_df.empty:
            df_branch_prod_show = branch_product_comm_df.copy()
            df_branch_prod_show["total_sales"] = df_branch_prod_show["total_sales"].apply(format_currency)
            df_branch_prod_show["material_cost"] = df_branch_prod_show["material_cost"].apply(format_currency)
            df_branch_prod_show["commission"] = df_branch_prod_show["commission"].apply(format_currency)
            df_branch_prod_show["total_material_cost"] = df_branch_prod_show["total_material_cost"].apply(format_currency)
            df_branch_prod_show["total_commission"] = df_branch_prod_show["total_commission"].apply(format_currency)
            df_branch_prod_show["commission_rate"] = df_branch_prod_show["commission_rate"].apply(lambda x: f"{x:.1f}%")
            render_table(
                df_branch_prod_show[
                    [
                        "shop_name",
                        "product_code",
                        "product_name",
                        "total_units_sold",
                        "total_sales",
                        "material_cost",
                        "commission",
                        "total_material_cost",
                        "total_commission",
                        "commission_rate",
                    ]
                ],
                width="stretch",
                height=450,
            )
        else:
            st.info("No product-wise branch commission data for this period.")

        st.markdown("### Product-wise Overall")
        product_comm_df = get_product_material_cost_summary(
            start_date_str, end_date_str, selected_branches, data_mode=data_mode
        )
        if not product_comm_df.empty:
            df_prod_show = product_comm_df.copy()
            df_prod_show["total_sales"] = df_prod_show["total_sales"].apply(format_currency)
            df_prod_show["material_cost"] = df_prod_show["material_cost"].apply(format_currency)
            df_prod_show["commission"] = df_prod_show["commission"].apply(format_currency)
            df_prod_show["total_material_cost"] = df_prod_show["total_material_cost"].apply(format_currency)
            df_prod_show["total_commission"] = df_prod_show["total_commission"].apply(format_currency)
            df_prod_show["commission_rate"] = df_prod_show["commission_rate"].apply(lambda x: f"{x:.1f}%")
            render_table(
                df_prod_show[
                    [
                        "product_code",
                        "product_name",
                        "total_units_sold",
                        "total_sales",
                        "material_cost",
                        "commission",
                        "total_material_cost",
                        "total_commission",
                        "commission_rate",
                    ]
                ],
                width="stretch",
                height=350,
            )
        else:
            st.info("No product-wise overall commission data for this period.")

        st.markdown("### Detailed Analysis (Product wise employees and branches)")
        search_query = st.text_input("Search Product or Employee", key="comm_detail_search")
        detail_comm_df = get_material_cost_commission_analysis(
            start_date_str, end_date_str, selected_branches, data_mode=data_mode
        )
        if not detail_comm_df.empty:
            if search_query:
                mask = (
                    detail_comm_df["product_name"].str.contains(search_query, case=False, na=False)
                    | detail_comm_df["employee_name"].str.contains(search_query, case=False, na=False)
                    | detail_comm_df["shop_name"].str.contains(search_query, case=False, na=False)
                )
                detail_comm_df = detail_comm_df[mask]

            df_detail_show = detail_comm_df.copy()
            df_detail_show["total_sales"] = df_detail_show["total_sales"].apply(format_currency)
            df_detail_show["material_cost"] = df_detail_show["material_cost"].apply(format_currency)
            df_detail_show["commission"] = df_detail_show["commission"].apply(format_currency)
            df_detail_show["total_material_cost"] = df_detail_show["total_material_cost"].apply(format_currency)
            df_detail_show["total_commission"] = df_detail_show["total_commission"].apply(format_currency)
            render_table(
                df_detail_show[
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
                height=600,
            )
        else:
            st.info("No detailed commission records found.")
    else:
        st.info("Material cost commission setup is empty. This tab uses a built-in 73-product matrix and does not require a database commission table.")
# ========================
# TAB 8: TRENDS & ANALYTICS
# ========================
with tab8:
    # Trends & Analytics header and interactive trend controls removed per request
    # Show Performance Summary and Product Comparison only
    st.subheader("?? Performance Summary")

    if not df_branch.empty:
        # Create summary chart
        fig = px.bar(
            df_branch,
            x='shop_name',
            y='total_Nt_amount',
            title="Branch Sales Comparison",
            labels={'shop_name': 'Branch', 'total_Nt_amount': 'Sales ()'},
            color='total_Nt_amount',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, width="stretch")
        # Monthly trend + Forecast (use selected date range)
        try:
            df_monthly = get_cached_monthly_sales(start_date_str, end_date_str, selected_branches, data_mode)
            df_daily = get_cached_daily_sales(start_date_str, end_date_str, selected_branches, data_mode)

            # Forecast controls: let user choose method and horizon
            forecast_method = st.selectbox(
                "Forecast method",
                options=["simple", "prophet"],
                index=0,
                help="Choose forecasting method. Prophet requires the 'prophet' package to be installed."
            )
            forecast_horizon = st.slider("Forecast horizon (days)", 1, 30, 7)

            col_a, col_b = st.columns([2, 1])
            with col_a:
                trend_fig = create_monthly_sales_trend(df_monthly, periods=24, rolling=3)
                st.plotly_chart(trend_fig, width="stretch")

            with col_b:
                # Forecast using daily data with selected method
                forecast_fig = create_forecast_with_ci(
                    df_daily, periods_ahead=forecast_horizon, method=forecast_method
                )
                st.plotly_chart(forecast_fig, width="stretch")
        except Exception as e:
            st.warning(f"Could not load trend/forecast data: {e}")

    # -------------------------------
    # Product comparison: Current month vs Previous month
    # -------------------------------
    st.markdown("---")
    st.subheader("?? Product Comparison — Current vs Previous Month")

    # Current month is target_year/target_month from sidebar; previous month computed automatically
    curr_year = int(target_year)
    curr_month = int(target_month)
    if curr_month == 1:
        prev_year = curr_year - 1
        prev_month = 12
    else:
        prev_year = curr_year
        prev_month = curr_month - 1

    # Fetch product monthly sales for Top Products using the overall selected branches (sidebar multiselect)
    # Top Products should not be affected by the comparison-only branch radio
    df_curr_all = get_cached_product_monthly_sales(curr_year, curr_month, selected_branches, data_mode)
    df_prev_all = get_cached_product_monthly_sales(prev_year, prev_month, selected_branches, data_mode)

    # (df_curr and df_prev will be fetched & normalized later for the comparison table)

    # -------------------------------
    # Line Item Name (Category) — Current Month
    # -------------------------------
    st.markdown("---")
    st.subheader("Line Item Name — Current Month")
    top_n_products = st.number_input("Top N items to show", min_value=1, max_value=500, value=15)

    # Build top categories from current month totals (using overall selection)
    if df_curr_all is None or df_curr_all.empty:
        df_curr_all = pd.DataFrame(columns=['Product', 'Total_Sales', 'Total_Qty'])
    else:
        # df_curr_all comes from get_cached_product_monthly_sales which uses TempProductBarcode.field_name
        df_curr_all = df_curr_all.rename(columns={
            'Product': 'Category',
            'Total_Sales': 'Current_Sales',
            'Total_Qty': 'Current_Qty'
        })

    if not df_curr_all.empty:
        # Keep only allowed line-item categories
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
            "SALES - SIDE ORDER"
        ]
        df_curr_all['__cat_norm'] = df_curr_all['Category'].astype(str).str.upper().str.replace(r"\s+", " ", regex=True).str.strip()
        allowed_norm = {str(x).upper().strip() for x in allowed_line_items}
        df_curr_all = df_curr_all[df_curr_all['__cat_norm'].isin(allowed_norm)].drop(columns=['__cat_norm'])
        df_top_categories = df_curr_all[['Category', 'Current_Sales', 'Current_Qty']].copy()
        df_top_categories = df_top_categories.sort_values('Current_Sales', ascending=False).head(top_n_products)

        # Format display for categories
        display_cat = df_top_categories.copy()
        display_cat['Total Sales'] = display_cat['Current_Sales'].apply(lambda x: format_currency(x))
        display_cat['Total Qty'] = display_cat['Current_Qty'].apply(lambda x: f"{int(x):,}")
        display_cat = display_cat[['Category', 'Total Sales', 'Total Qty']]

        render_table(display_cat, width="stretch", height=300)

        # Bar chart for top categories
        fig_cat = px.bar(
            df_top_categories,
            x='Current_Sales',
            y='Category',
            orientation='h',
            title=f"Top {len(df_top_categories)} Line Item Names — {month_name(curr_year, curr_month)}",
            labels={'Current_Sales': 'Sales ()', 'Category': 'Line Item Name'},
            color='Current_Sales',
            color_continuous_scale='Viridis'
        )
        fig_cat.update_traces(texttemplate=' %{x:,.0f}', textposition='inside')
        fig_cat.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_cat, width="stretch")

    else:
        st.info("?? No current month category data available for Top Line Item Names")

    # -------------------------------
    # Top products (by product name) — Current Month
    # -------------------------------
    st.markdown("---")
    st.subheader("?? Top Products (by Product Name) — Current Month")

    # Fetch top products by product name using the new DB function
    df_products_curr = get_cached_product_monthly_sales_by_product(curr_year, curr_month, selected_branches, data_mode, category=None)

    if df_products_curr is None or df_products_curr.empty:
        st.info("?? No current month product-level data available")
    else:
        df_products_curr = df_products_curr.rename(columns={
            'Product': 'Product',
            'Total_Sales': 'Current_Sales',
            'Total_Qty': 'Current_Qty'
        })

        df_top_products = df_products_curr[['Product', 'Current_Sales', 'Current_Qty']].copy()
        df_top_products = df_top_products.sort_values('Current_Sales', ascending=False).head(top_n_products)

        # Format display for products
        display_top = df_top_products.copy()
        display_top['Total Sales'] = display_top['Current_Sales'].apply(lambda x: format_currency(x))
        display_top['Total Qty'] = display_top['Current_Qty'].apply(lambda x: f"{int(x):,}")
        display_top = display_top[['Product', 'Total Sales', 'Total Qty']]

        render_table(display_top, width="stretch", height=350)

        # Bar chart for top products
        fig_top = px.bar(
            df_top_products,
            x='Current_Sales',
            y='Product',
            orientation='h',
            title=f"Top {len(df_top_products)} Products — {month_name(curr_year, curr_month)}",
            labels={'Current_Sales': 'Sales ()', 'Product': 'Product'},
            color='Current_Sales',
            color_continuous_scale='Greens'
        )
        fig_top.update_traces(texttemplate=' %{x:,.0f}', textposition='inside')
        fig_top.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_top, width="stretch")

        # Detailed charts for Top 10 and Bottom 10 products (daily trends)
        try:
            # Exclude products that belong to specific line item names or contain excluded keywords
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
                "SALES - SIDE ORDER"
            ]
            allowed_products = set()
            try:
                for cat in allowed_line_items:
                    df_cat = get_cached_product_monthly_sales_by_product(
                        curr_year, curr_month, selected_branches, data_mode, category=cat
                    )
                    if df_cat is not None and not df_cat.empty and 'Product' in df_cat.columns:
                        allowed_products.update(df_cat['Product'].dropna().astype(str).tolist())
            except Exception:
                allowed_products = set()

            df_products_for_trends = df_products_curr.copy()
            if allowed_products:
                df_products_for_trends = df_products_for_trends[df_products_for_trends['Product'].isin(allowed_products)]

            # Exclude "Cut in" products by keyword
            df_products_for_trends = df_products_for_trends[
                ~df_products_for_trends['Product'].str.contains("cut in", case=False, na=False)
            ]

            # Exclude products with zero sales (price/amount effectively 0 in current period)
            df_products_for_trends = df_products_for_trends[df_products_for_trends['Current_Sales'] > 0]

            df_top_10 = df_products_for_trends.sort_values('Current_Sales', ascending=False).head(10)
            top_product_list = df_top_10['Product'].tolist()

            df_bottom_10 = df_products_for_trends[['Product', 'Current_Sales', 'Current_Qty']].copy()
            df_bottom_10 = df_bottom_10.sort_values('Current_Sales', ascending=True).head(10)
            bottom_product_list = df_bottom_10['Product'].tolist()

            st.markdown("**Top 10 Products - Daily Sales Trend**")
            top_selected = st.multiselect(
                "Top 10 chart products",
                options=sorted(df_products_for_trends['Product'].dropna().astype(str).unique().tolist()),
                default=top_product_list,
                key="top10_products_filter"
            )
            if st.button("Reset Top 10 Highest", key="reset_top10"):
                st.session_state["top10_products_filter"] = top_product_list
                top_selected = top_product_list

            if top_selected:
                st.markdown("**Selected (Top Chart):**")
                st.write(", ".join(top_selected))

            if top_selected:
                df_top_trend = get_cached_daily_sales_by_products(
                    start_date_str, end_date_str, selected_branches, data_mode, top_selected
                )
                if df_top_trend is not None and not df_top_trend.empty:
                    prod_col = 'Product' if 'Product' in df_top_trend.columns else 'product_name'
                    date_col = 'day' if 'day' in df_top_trend.columns else ('date' if 'date' in df_top_trend.columns else None)
                    if date_col:
                        df_top_trend[date_col] = pd.to_datetime(df_top_trend[date_col])
                        fig_top_trend = px.line(
                            df_top_trend,
                            x=date_col,
                            y='total_Nt_amount',
                            color=prod_col,
                            markers=True,
                            title="Top 10 Products - Daily Sales",
                            labels={'total_Nt_amount': 'Sales ()', prod_col: 'Product'}
                        )
                        fig_top_trend.update_layout(height=420, hovermode='x unified')
                        fig_top_trend.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_top_trend, width="stretch")
                    else:
                        st.info("Info: Daily trend data missing date column for top products.")
            else:
                st.info("Info: No top products available for trend chart.")

            st.markdown("---")
            st.markdown("**Bottom 10 Products - Daily Sales Trend**")
            bottom_selected = st.multiselect(
                "Bottom 10 chart products",
                options=sorted(df_products_for_trends['Product'].dropna().astype(str).unique().tolist()),
                default=bottom_product_list,
                key="bottom10_products_filter"
            )
            if st.button("Reset Bottom 10 Lowest", key="reset_bottom10"):
                st.session_state["bottom10_products_filter"] = bottom_product_list
                bottom_selected = bottom_product_list

            if bottom_selected:
                st.markdown("**Selected (Bottom Chart):**")
                st.write(", ".join(bottom_selected))

            if bottom_selected:
                df_bottom_trend = get_cached_daily_sales_by_products(
                    start_date_str, end_date_str, selected_branches, data_mode, bottom_selected
                )
                if df_bottom_trend is not None and not df_bottom_trend.empty:
                    prod_col = 'Product' if 'Product' in df_bottom_trend.columns else 'product_name'
                    date_col = 'day' if 'day' in df_bottom_trend.columns else ('date' if 'date' in df_bottom_trend.columns else None)
                    if date_col:
                        df_bottom_trend[date_col] = pd.to_datetime(df_bottom_trend[date_col])
                        fig_bottom_trend = px.line(
                            df_bottom_trend,
                            x=date_col,
                            y='total_Nt_amount',
                            color=prod_col,
                            markers=True,
                            title="Bottom 10 Products - Daily Sales",
                            labels={'total_Nt_amount': 'Sales ()', prod_col: 'Product'}
                        )
                        fig_bottom_trend.update_layout(height=420, hovermode='x unified')
                        fig_bottom_trend.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_bottom_trend, width="stretch")
                    else:
                        st.info("Info: Daily trend data missing date column for bottom products.")
            else:
                st.info("Info: No bottom products available for trend chart.")

        except Exception as e:
            st.warning(f"Could not load product trend charts: {e}")

        # -------------------------------
        # Clickable Product Explorer
        # -------------------------------
        st.markdown("---")
        st.subheader("Product Explorer")
        if 'df_products_for_trends' in locals():
            all_products = df_products_for_trends['Product'].dropna().astype(str).unique().tolist()
        else:
            all_products = df_products_curr['Product'].dropna().astype(str).unique().tolist()

        if all_products:
            selected_prod = st.selectbox("Product to view", options=sorted(all_products), index=0)
            try:
                df_sel = get_cached_daily_sales_by_products(start_date_str, end_date_str, selected_branches, data_mode, [selected_prod])
                prod_fig = create_product_time_series(df_sel, selected_prod, agg='daily', show_qty=True, rolling=7)
                st.plotly_chart(prod_fig, width="stretch")
            except Exception as e:
                st.warning(f"Could not load detailed series for {selected_prod}: {e}")
        else:
            st.info("Info: No products available to view.")

        # -------------------------------
        # Low-performing Products & Line Items
        # -------------------------------
        st.markdown("---")
        st.subheader("?? Low-performing Products & Line Items")
        low_n = st.number_input("Show bottom N products/line-items", min_value=1, max_value=100, value=5)

        # Bottom products by sales
        try:
            df_bottom_products = df_products_curr[['Product', 'Current_Sales', 'Current_Qty']].copy()
            df_bottom_products = df_bottom_products.sort_values('Current_Sales', ascending=True).head(low_n)
            if not df_bottom_products.empty:
                col_lp1, col_lp2 = st.columns([1, 2])
                with col_lp1:
                    st.write("Bottom products by sales")
                    render_table(
                        df_bottom_products.assign(Current_Sales=lambda d: d['Current_Sales'].apply(format_currency)),
                        width="stretch",
                        height=200
                    )
                with col_lp2:
                    fig_low = px.bar(
                        df_bottom_products,
                        x='Current_Sales',
                        y='Product',
                        orientation='h',
                        labels={'Current_Sales': 'Sales ()', 'Product': 'Product'},
                        color='Current_Sales',
                        color_continuous_scale='Reds'
                    )
                    fig_low.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig_low, width="stretch")
        except Exception:
            pass

        # Bottom line-items (categories)
        try:
            df_bottom_cats = df_curr_all.rename(columns={'Category': 'Category', 'Current_Sales': 'Current_Sales'})[['Category', 'Current_Sales', 'Current_Qty']].copy()
            df_bottom_cats = df_bottom_cats.sort_values('Current_Sales', ascending=True).head(low_n)
            if not df_bottom_cats.empty:
                st.write("Bottom line-item names by sales")
                render_table(
                    df_bottom_cats.assign(Current_Sales=lambda d: d['Current_Sales'].apply(format_currency)),
                    width="stretch",
                    height=200
                )
        except Exception:
            pass

        except Exception as e:
            st.warning(f"Could not load product trend charts: {e}")

    # -------------------------------
    # Comparison table (unified) - sorted by current month sales desc
    # Add Branch Filter here (All / North Nazimabad / Malir) as requested
    # -------------------------------
    st.markdown("---")
    st.subheader("?? Comparison Table")

    # Category selector (to compare products inside a category)
    categories = []
    try:
        if not df_line_item.empty:
            categories = sorted(df_line_item['product'].dropna().unique().tolist())
    except Exception:
        categories = []

    selected_category = st.selectbox(
        "Select Category (Line Item)",
        options=["All"] + categories,
        index=0
    )

    # Branch filter for the comparison table only
    branch_option_comp = st.radio(
        "Branch Filter",
        options=[
            "All",
            branch_name_map.get(2, "Khadda Main Branch"),
            branch_name_map.get(3, "FESTIVAL"),
            branch_name_map.get(4, "Rahat Commercial"),
            branch_name_map.get(6, "TOWER"),
            branch_name_map.get(8, "North Nazimabad"),
            branch_name_map.get(10, "MALIR"),
            branch_name_map.get(14, "FESTIVAL 2")
        ],
        index=0,
        horizontal=True
    )
    if branch_option_comp == "All":
        branch_ids_query = selected_branches
    else:
        branch_ids_query = [k for k, v in branch_name_map.items() if v == branch_option_comp]

    # Fetch current & previous month for the comparison based on branch selection
    # If a specific category is selected, fetch product-level sales inside that category.
    if selected_category and selected_category != "All":
        df_curr = get_cached_product_monthly_sales_by_product(curr_year, curr_month, branch_ids_query, data_mode, category=selected_category)
        df_prev = get_cached_product_monthly_sales_by_product(prev_year, prev_month, branch_ids_query, data_mode, category=selected_category)
    else:
        # No category selected -> fetch product-level sales for all categories
        df_curr = get_cached_product_monthly_sales_by_product(curr_year, curr_month, branch_ids_query, data_mode, category=None)
        df_prev = get_cached_product_monthly_sales_by_product(prev_year, prev_month, branch_ids_query, data_mode, category=None)

    # Normalize if empty
    # Normalize/rename columns to expected names
    if df_curr is None or df_curr.empty:
        df_curr = pd.DataFrame(columns=['Product', 'Current_Sales', 'Current_Qty'])
    else:
        df_curr = df_curr.rename(columns={
            'Product': 'Product',
            'Total_Sales': 'Current_Sales',
            'Total_Qty': 'Current_Qty'
        })

    if df_prev is None or df_prev.empty:
        df_prev = pd.DataFrame(columns=['Product', 'Previous_Sales', 'Previous_Qty'])
    else:
        df_prev = df_prev.rename(columns={
            'Product': 'Product',
            'Total_Sales': 'Previous_Sales',
            'Total_Qty': 'Previous_Qty'
        })

    df_comp = pd.merge(
        df_curr[['Product', 'Current_Sales', 'Current_Qty']],
        df_prev[['Product', 'Previous_Sales', 'Previous_Qty']],
        on='Product',
        how='outer'
    ).fillna(0)

    # Calculations
    df_comp['Balance'] = df_comp['Current_Qty'] - df_comp['Previous_Qty']
    df_comp['Achieved'] = df_comp['Current_Qty'] >= df_comp['Previous_Qty']

    # Sort by current month sales (descending)
    df_comp_display = df_comp.sort_values('Current_Sales', ascending=False)

    # Month-labelled column names
    curr_label_sales = f"{month_name(curr_year, curr_month)} Sales"
    curr_label_qty = f"{month_name(curr_year, curr_month)} Qty"
    prev_label_sales = f"{month_name(prev_year, prev_month)} Sales"
    prev_label_qty = f"{month_name(prev_year, prev_month)} Qty"

    # Prepare display
    df_display = df_comp_display.copy()
    df_display[curr_label_sales] = df_display['Current_Sales'].apply(lambda x: format_currency(x))
    df_display[curr_label_qty] = df_display['Current_Qty'].apply(lambda x: f"{int(x):,}")
    df_display[prev_label_sales] = df_display['Previous_Sales'].apply(lambda x: format_currency(x))
    df_display[prev_label_qty] = df_display['Previous_Qty'].apply(lambda x: f"{int(x):,}")
    df_display['Balance'] = df_display['Balance'].apply(lambda x: f"{int(x):+,}")
    df_display['Achievement'] = df_display['Achieved'].apply(lambda v: '?' if v else '?')

    cols = ['Product', curr_label_sales, curr_label_qty, prev_label_sales, prev_label_qty, 'Balance', 'Achievement']
    df_display = df_display[cols]

    st.markdown(f"**Comparison:** {month_name(curr_year,curr_month)} (Current) vs {month_name(prev_year,prev_month)} (Previous)")
    if df_display.empty:
        st.info("?? No product sales data available for these months")
    else:
        render_table(df_display, width="stretch", height=600)
        # Download numeric comparison (unformatted)





# ========================
# TAB 8: RAMZAN DEALS
# ========================
with tab8:
    st.header("Ramzan Deals")

    rcol1, rcol2 = st.columns(2)
    with rcol1:
        ramzan_start_date = st.date_input(
            "Ramzan Start Date",
            value=start_date,
            key="ramzan_start_date"
        )
    with rcol2:
        ramzan_end_date = st.date_input(
            "Ramzan End Date",
            value=end_date,
            key="ramzan_end_date"
        )

    if ramzan_start_date > ramzan_end_date:
        st.error("Start date cannot be after end date.")
    else:
        st.markdown("#### Branch Selection")
        ramzan_branches = st.multiselect(
            "Select Branches for Ramzan Deals",
            options=selected_branches,
            default=selected_branches,
            format_func=lambda x: branch_name_map.get(x, f"Branch {x}"),
            key="ramzan_branch_selector"
        )

        if not ramzan_branches:
            st.warning("Please select at least one branch for Ramzan Deals.")
        else:
            ramzan_master = get_cached_ramzan_product_master()
            if ramzan_master is None or ramzan_master.empty:
                st.info("No Ramzan deal products found.")
            else:
                ramzan_master = ramzan_master[
                    ramzan_master["Product_code"].astype(str).isin([str(x) for x in RAMZAN_DEALS_PRODUCT_IDS])
                ].copy()
                ramzan_master["display"] = (
                    ramzan_master["Product_code"].astype(str) + " - " + ramzan_master["item_name"].astype(str)
                )

                selected_ramzan_products = st.multiselect(
                    "Select Ramzan Deal Products",
                    options=ramzan_master["display"].tolist(),
                    default=ramzan_master["display"].tolist(),
                    key="ramzan_product_selector"
                )

                if not selected_ramzan_products:
                    st.warning("Please select at least one Ramzan product.")
                else:
                    selected_product_df = ramzan_master[
                        ramzan_master["display"].isin(selected_ramzan_products)
                    ].copy()
                    selected_product_ids = selected_product_df["Product_Item_ID"].tolist()

                    ramzan_sales_df = get_cached_ramzan_deals_sales(
                        ramzan_start_date.strftime("%Y-%m-%d"),
                        ramzan_end_date.strftime("%Y-%m-%d"),
                        ramzan_branches,
                        selected_product_ids
                    )

                    merge_keys = ["shop_id", "shop_name", "Product_Item_ID", "Product_code", "item_name"]
                    if ramzan_sales_df is None or ramzan_sales_df.empty:
                        ramzan_sales_df = pd.DataFrame(columns=merge_keys + ["total_qty", "total_sales"])

                    branches_df = pd.DataFrame({
                        "shop_id": ramzan_branches,
                        "shop_name": [branch_name_map.get(b, f"Branch {b}") for b in ramzan_branches]
                    })

                    branches_df["key"] = 1
                    selected_product_df["key"] = 1
                    full_grid = branches_df.merge(
                        selected_product_df[["Product_Item_ID", "Product_code", "item_name", "key"]],
                        on="key",
                        how="inner"
                    ).drop(columns=["key"])

                    branch_wise_full = full_grid.merge(
                        ramzan_sales_df[merge_keys + ["total_qty", "total_sales"]],
                        on=merge_keys,
                        how="left"
                    )
                    branch_wise_full["total_qty"] = pd.to_numeric(branch_wise_full["total_qty"], errors="coerce").fillna(0)
                    branch_wise_full["total_sales"] = pd.to_numeric(branch_wise_full["total_sales"], errors="coerce").fillna(0)

                    product_overall = branch_wise_full.groupby(
                        ["Product_Item_ID", "Product_code", "item_name"],
                        as_index=False
                    ).agg({
                        "total_qty": "sum",
                        "total_sales": "sum"
                    })

                    total_sales_ramzan = product_overall["total_sales"].sum()
                    total_qty_ramzan = product_overall["total_qty"].sum()

                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Total Sales (PKR)", f"{total_sales_ramzan:,.0f}")
                    with m2:
                        st.metric("Total Quantity", f"{total_qty_ramzan:,.0f}")

                    st.markdown("#### Branch-wise Sales")
                    render_table(
                        branch_wise_full.sort_values(["shop_name", "Product_code"]),
                        width="stretch",
                        height=420
                    )

                    st.markdown("#### Product-wise Overall Sales")
                    render_table(
                        product_overall.sort_values(["Product_code"]),
                        width="stretch",
                        height=280
                    )

                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                    with dcol2:

# ========================
# TAB 9: CATEGORY FILTERS
# ========================
with tab9:
    st.header("Category Filters")
    st.caption("Select included/excluded line-item categories. Settings are saved and reused automatically.")

    try:
        conn_kds = pool.get_connection("kdsdb")
        df_category_master = pd.read_sql(
            "SELECT category_id, category_name FROM dbo.chef_sale ORDER BY category_name",
            conn_kds
        )
    except Exception as e:
        st.error(f"Could not load category master from KDS DB: {e}")
        df_category_master = pd.DataFrame(columns=["category_id", "category_name"])

    if df_category_master.empty:
        st.info("No categories available to configure.")
    else:
        df_category_master = df_category_master.dropna(subset=["category_id", "category_name"]).copy()
        df_category_master["category_id"] = df_category_master["category_id"].astype(int)
        df_category_master["category_name"] = df_category_master["category_name"].astype(str)
        category_options = df_category_master["category_id"].tolist()
        id_to_name = dict(zip(df_category_master["category_id"], df_category_master["category_name"]))

        saved_filters = get_saved_category_filters()
        default_include = [x for x in saved_filters.get("included_category_ids", []) if x in category_options]
        default_exclude = [x for x in saved_filters.get("excluded_category_ids", []) if x in category_options]

        with st.form("category_filter_form"):
            included_ids = st.multiselect(
                "Included Category IDs",
                options=category_options,
                default=default_include,
                format_func=lambda x: f"{x} - {id_to_name.get(x, '')}"
            )
            excluded_ids = st.multiselect(
                "Excluded Category IDs",
                options=category_options,
                default=default_exclude,
                format_func=lambda x: f"{x} - {id_to_name.get(x, '')}"
            )

            c1, c2 = st.columns(2)
            save_clicked = c1.form_submit_button("Save Filters", width="stretch")
            reset_clicked = c2.form_submit_button("Reset Default", width="stretch")

        if save_clicked:
            overlap = set(included_ids).intersection(set(excluded_ids))
            if overlap:
                included_ids = [x for x in included_ids if x not in overlap]
                st.warning("Overlap found in include/exclude. Overlapping IDs were removed from Included.")

            payload = {
                "included_category_ids": included_ids,
                "excluded_category_ids": excluded_ids,
                "included_category_names": [id_to_name[x] for x in included_ids if x in id_to_name],
                "excluded_category_names": [id_to_name[x] for x in excluded_ids if x in id_to_name],
            }
            try:
                save_category_filters(payload)
                refresh_all_caches()
                st.success("Category filters saved.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save category filters: {e}")

        if reset_clicked:
            default_excluded_ids = [x for x in DEFAULT_EXCLUDED_CATEGORY_IDS if x in category_options]
            payload = {
                "included_category_ids": [],
                "excluded_category_ids": default_excluded_ids,
                "included_category_names": [],
                "excluded_category_names": [id_to_name[x] for x in default_excluded_ids if x in id_to_name],
            }
            try:
                save_category_filters(payload)
                refresh_all_caches()
                st.success("Category filters reset to default.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not reset category filters: {e}")

        st.markdown("#### Current Saved Configuration")
        current = get_saved_category_filters()
        current_include = [str(x) for x in current.get("included_category_ids", [])]
        current_exclude = [str(x) for x in current.get("excluded_category_ids", [])]
        st.write(f"Included IDs: {', '.join(current_include) if current_include else '(none)'}")
        st.write(f"Excluded IDs: {', '.join(current_exclude) if current_exclude else '(none)'}")

# ========================
# TAB 10: CATEGORY COVERAGE
# ========================
with tab10:
    st.header("Category Coverage in Sales Counts")
    st.caption("Shows which line-item categories are currently included or excluded in branch/total/monthly/daily sales calculations.")

    saved_cfg = get_saved_category_filters()
    inc_ids = [str(x) for x in saved_cfg.get("included_category_ids", [])]
    exc_ids = [str(x) for x in saved_cfg.get("excluded_category_ids", [])]
    inc_names = [str(x) for x in saved_cfg.get("included_category_names", [])]
    exc_names = [str(x) for x in saved_cfg.get("excluded_category_names", [])]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Included Rules**")
        st.write(f"IDs: {', '.join(inc_ids) if inc_ids else '(none)'}")
        st.write(f"Names: {', '.join(inc_names) if inc_names else '(none)'}")
    with c2:
        st.markdown("**Excluded Rules**")
        st.write(f"IDs: {', '.join(exc_ids) if exc_ids else '(none)'}")
        st.write(f"Names: {', '.join(exc_names) if exc_names else '(none)'}")

    df_cov = get_cached_category_filter_coverage(
        start_date_str,
        end_date_str,
        selected_branches,
        data_mode
    )

    if df_cov is None or df_cov.empty:
        st.info("No category coverage data available for selected filters.")
    else:
        # Load category IDs for display (from KDS master)
        try:
            conn_kds = pool.get_connection("kdsdb")
            df_cat_master = pd.read_sql(
                "SELECT category_id, category_name FROM dbo.chef_sale",
                conn_kds
            )
            if not df_cat_master.empty:
                df_cat_master["category_name_norm"] = (
                    df_cat_master["category_name"].astype(str).str.strip().str.upper()
                )
                df_cov["category_name_norm"] = df_cov["category_name"].astype(str).str.strip().str.upper()
                df_cov = df_cov.merge(
                    df_cat_master[["category_id", "category_name_norm"]],
                    on="category_name_norm",
                    how="left"
                )
                df_cov.drop(columns=["category_name_norm"], inplace=True)
        except Exception:
            df_cov["category_id"] = None

        df_cov["total_qty"] = pd.to_numeric(df_cov["total_qty"], errors="coerce").fillna(0.0)
        df_cov["total_sales"] = pd.to_numeric(df_cov["total_sales"], errors="coerce").fillna(0.0)
        if "category_id" not in df_cov.columns:
            df_cov["category_id"] = None
        df_cov["category_id"] = pd.to_numeric(df_cov["category_id"], errors="coerce")

        counted_df = df_cov[df_cov["counted"] == True].copy()
        excluded_df = df_cov[df_cov["counted"] == False].copy()

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Included Categories", f"{len(counted_df):,}")
        with m2:
            st.metric("Excluded Categories", f"{len(excluded_df):,}")
        with m3:
            st.metric("Excluded Sales Impact", f"{excluded_df['total_sales'].sum():,.0f}")

        st.markdown("#### Included Categories (Counted)")
        render_table(
            counted_df.sort_values("total_sales", ascending=False)[
                ["category_id", "category_name", "status", "total_qty", "total_sales"]
            ],
            width="stretch",
            height=320
        )

        st.markdown("#### Excluded Categories (Not Counted)")
        render_table(
            excluded_df.sort_values("total_sales", ascending=False)[
                ["category_id", "category_name", "status", "total_qty", "total_sales"]
            ],
            width="stretch",
            height=320
        )

# ========================
# TAB 11: PIVOT TABLES
# ========================
with tab11:
    st.header("Pivot Tables")
    st.caption("Interactive pivots for branch/category/date analysis using current filters.")

    pivot_type = st.selectbox(
        "Pivot Type",
        options=[
            "Branch x Category",
            "Branch x Day",
            "Month x Branch"
        ],
        index=0
    )
    metric_choice = st.selectbox(
        "Metric",
        options=["Sales", "Quantity"],
        index=0
    )

    if pivot_type == "Branch x Category":
        if df_line_item is None or df_line_item.empty:
            st.info("No line-item data available for this pivot.")
        else:
            metric_col = "total_line_value_incl_tax" if metric_choice == "Sales" else "total_qty"
            value_name = "Total Sales" if metric_choice == "Sales" else "Total Qty"
            piv = pd.pivot_table(
                df_line_item,
                index="shop_name",
                columns="product",
                values=metric_col,
                aggfunc="sum",
                fill_value=0
            )
            piv = piv.sort_index()
            piv["Grand Total"] = piv.sum(axis=1)
            piv.loc["Grand Total"] = piv.sum(axis=0)

            st.markdown(f"#### {value_name}: Branch x Category")
            render_table(piv.reset_index().rename(columns={"shop_name": "Branch"}), width="stretch", height=520)

    elif pivot_type == "Branch x Day":
        df_daily_branch_pivot = get_cached_daily_sales_by_branch(
            start_date_str,
            end_date_str,
            selected_branches,
            data_mode
        )
        piv = None
        if df_daily_branch_pivot is None or df_daily_branch_pivot.empty:
            st.info("No daily branch data available for this pivot.")
        else:
            if metric_choice == "Sales":
                working = df_daily_branch_pivot.copy()
                working["day_str"] = pd.to_datetime(working["day"]).dt.strftime("%Y-%m-%d")
                piv = pd.pivot_table(
                    working,
                    index="shop_name",
                    columns="day_str",
                    values="total_Nt_amount",
                    aggfunc="sum",
                    fill_value=0
                )
                value_name = "Total Sales"
            else:
                working = df_line_item.copy()
                if working.empty:
                    st.info("Quantity pivot needs line-item data, but it is empty.")
                    working = None
                if working is not None:
                    # Approx day-level qty by reusing existing date range fetch in product targets style is heavy;
                    # keep quantity pivot branch/category only for now.
                    st.info("Quantity is best viewed in Branch x Category pivot.")
            if metric_choice == "Sales" and piv is not None:
                piv = piv.sort_index()
                piv["Grand Total"] = piv.sum(axis=1)
                piv.loc["Grand Total"] = piv.sum(axis=0)
                st.markdown(f"#### {value_name}: Branch x Day")
                render_table(piv.reset_index().rename(columns={"shop_name": "Branch"}), width="stretch", height=520)

    elif pivot_type == "Month x Branch":
        df_daily_branch_pivot = get_cached_daily_sales_by_branch(
            start_date_str,
            end_date_str,
            selected_branches,
            data_mode
        )
        piv = None
        if df_daily_branch_pivot is None or df_daily_branch_pivot.empty:
            st.info("No data available for month x branch pivot.")
        else:
            if metric_choice == "Sales":
                working = df_daily_branch_pivot.copy()
                working["month"] = pd.to_datetime(working["day"]).dt.to_period("M").astype(str)
                piv = pd.pivot_table(
                    working,
                    index="shop_name",
                    columns="month",
                    values="total_Nt_amount",
                    aggfunc="sum",
                    fill_value=0
                )
                value_name = "Total Sales"
            else:
                st.info("Quantity is best viewed in Branch x Category pivot.")
                piv = None
            if metric_choice == "Sales" and piv is not None:
                piv = piv.sort_index()
                piv["Grand Total"] = piv.sum(axis=1)
                piv.loc["Grand Total"] = piv.sum(axis=0)
                st.markdown(f"#### {value_name}: Month x Branch")
                render_table(piv.reset_index().rename(columns={"shop_name": "Branch"}), width="stretch", height=520)

# ========================
# FOOTER
# ========================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; font-size: 0.8rem;'>
        HNS Sales Dashboard v2.0 - Optimized for Performance | 
        Last Updated: {} | Query Time: {:.2f}s
    </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        query_time
    ),
    unsafe_allow_html=True
)












