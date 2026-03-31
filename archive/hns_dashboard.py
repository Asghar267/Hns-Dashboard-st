"""
Optimized Sales Dashboard - Complete Version
Features: Caching, Performance Improvements, Advanced Visualizations, Dark Mode
No Authentication Required
"""

import streamlit as st
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
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
    get_cached_blocked_impact,
    get_cached_category_filter_coverage,
    get_cached_ramzan_deals_sales,
    get_cached_ramzan_product_master,
    get_cached_unmapped_products,
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
from modules.qr_tab_renderer import (
    render_khadda_diagnostics_tab,
    render_qr_tab,
    render_indoge_first_tab,
    render_multi_signal_match_tab,
)
from modules.qr_business_toggles import QR_TOGGLES
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
        "hide_index": hide_index,
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
    page_icon="HNS",
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
        /* Enable full width/height for tables in fullscreen mode */
        div[role="dialog"] {{
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            top: 0 !important;
            left: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        div[role="dialog"] > div:nth-child(2) {{
            height: 100vh !important;
            width: 100vw !important;
            max-height: 100vh !important;
        }}
        /* Target the table containers specifically with vh units to override inline heights */
        div[role="dialog"] [data-testid="stDataFrame"],
        div[role="dialog"] [data-testid="stDataFrame"] > div,
        div[role="dialog"] [data-testid="stDataFrame"] .stDataFrame,
        div[role="dialog"] [data-testid="stDataFrame"] .stDataFrame > div,
        div[role="dialog"] [data-testid="stDataFrameResizable"],
        div[role="dialog"] .glideDataEditor,
        div[role="dialog"] [role="grid"],
        div[role="dialog"] canvas {{
            width: 98vw !important;
            max-width: 98vw !important;
            height: 90vh !important;
            max-height: 90vh !important;
            margin: 0 auto !important;
        }}
        /* Also target any custom table classes */
        div[role="dialog"] [data-testid="stTable"],
        div[role="dialog"] [data-testid="stTable"] > div {{
            height: 90vh !important;
            width: 98vw !important;
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
st.sidebar.title("Dashboard Controls")

# Logout button
if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()

# Dark Mode Toggle
if st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
    load_custom_css()
else:
    st.session_state.dark_mode = False
    load_custom_css()

st.sidebar.markdown("---")

# ========================
# DATE FILTERS
# ========================
st.sidebar.header("Date Range")

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
    st.sidebar.error("Start Date cannot be after End Date")
    st.stop()

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

st.sidebar.markdown("---")

# ========================
# FILTER OPTIONS
# ========================
st.sidebar.header("Filters")

# Filter Mode
data_mode = st.sidebar.radio(
    "Data Mode",
    ["Filtered", "Unfiltered"],
    index=0 if QR_TOGGLES.blocked_mode_default.lower() == "filtered" else 1,
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
    st.sidebar.warning("Please select at least one branch")
    st.stop()

st.sidebar.markdown("---")

# ========================
# TARGET PERIOD
# ========================
st.sidebar.header("Target Period")
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
st.sidebar.header("Data Controls")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Refresh", width="stretch"):
        with st.spinner("Refreshing data..."):
            refresh_all_caches()
            st.session_state.last_refresh = datetime.now()
            st.success("Data refreshed.")
            time.sleep(1)
            st.rerun()

with col2:
    auto_refresh = st.checkbox("Auto", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh

# Snapshot Generation
if st.sidebar.button("Generate Snapshots", width="stretch"):
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
            st.sidebar.success(f"Saved to {out_dir.name}")
        except Exception as e:
            st.sidebar.error(f"Error setting up snapshots: {e}")

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
st.sidebar.header("Performance")

# Connection health check
if st.sidebar.button("Health Check", width="stretch"):
    with st.spinner("Checking connection health..."):
        health_status = health_check()
        if health_status['status'] == 'healthy':
            st.sidebar.success("All connections healthy")
        else:
            st.sidebar.error(f"Health check failed: {health_status.get('error', 'Unknown error')}")

# Performance metrics
if st.sidebar.button("Metrics", width="stretch"):
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
with st.sidebar.expander("Connection Settings"):
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

st.title(title_text)
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15 = st.tabs([
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
    "Pivot Tables",
    "Khadda Diagnostics",
])

# ========================
# TAB 1: OVERVIEW
# ========================
with tab1:
    st.header("Sales Overview")
    
    if df_branch.empty:
        st.info("No data available for selected filters")
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
        col_a, col_b, col_c = st.columns(2)

        # Top 5 Chef Sales (by product revenue)
        with col_a:
            st.markdown("**Chef Sales - Top 5 Products**")
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
            st.markdown("**Line Item Sub-Products - Top 5**")
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
            st.markdown("**OT Sales - Top 5**")
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
                with st.expander(f"{row['shop_name']} (ID: {row['shop_id']})"):
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

            render_table(display_daily, width="stretch", height=450)
        except Exception as e:
            st.warning(f"Could not load daily branch sales (last 30 days): {e}")
        st.markdown("---")
        
        # Order Type Analysis
        st.subheader("Order Type Distribution")
        
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
                            f"{ot}",
                            format_currency(sales),
                            f"{orders:,} orders"
                        )
            
            # Detailed table
            with st.expander("Detailed Order Type Breakdown"):
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
    st.header("Order Taker Performance")
    
    if df_ot.empty:
        st.info("No OT data available")
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
        st.subheader("Top 10 Performers")
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
        st.subheader("All Order Takers")
        
        search = st.text_input("Search by name", "")
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
    st.header("Chef Sales Analysis")
    
    if df_line_item.empty:
        st.info("No chef sales data available")
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
        st.subheader("Top 15 Products by Revenue")
        
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
        st.subheader("Product Category Distribution")
        
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
        st.subheader("All Products")
        
        # Format for display
        display_products = df_product_summary.copy()
        display_products['total_qty'] = display_products['total_qty'].apply(lambda x: f"{x:,.0f}")
        display_products['total_line_value_incl_tax'] = display_products['total_line_value_incl_tax'].apply(lambda x: format_currency(x))
        
        render_table(display_products, width="stretch")

        # Branch-wise table
        st.subheader("All Products by Branch")
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
                ]].style.map(color_remaining, subset=['Remaining']) \
                      .map(color_ach, subset=['Achievement %'])

                render_table(styled, width="stretch", height=450)
            else:
                st.info("No products available for daily targets.")
        except Exception as e:
            st.warning(f"Could not load product daily targets: {e}")

# ========================
# TAB 4: CHEF TARGETS
# ========================
with tab4:
    st.header("Chef Targets & Achievement")
    
    # Branch selection
    if not df_branch.empty:
        branch_names = df_branch['shop_name'].tolist()
        selected_branch = st.selectbox("Select Branch", branch_names)
        shop_id = df_branch[df_branch['shop_name'] == selected_branch]['shop_id'].iloc[0]
        
        st.info(f"Showing targets for **{selected_branch}** - {datetime(target_year, target_month, 1).strftime('%B %Y')}")
        
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
                    st.subheader("Target vs Achievement Comparison")
                    
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
                    st.error(f"Error loading chef targets data: {e}")
                    st.info("Make sure the chef_sale table exists in KDS database")
            else:
                st.warning(f"No targets found for {selected_branch}")
        else:
            st.warning("No chef targets data available")
    else:
        st.error("No branch data available")

# ========================
# TAB 5: OT TARGETS
# ========================
with tab5:
    st.header("Order Taker Targets")
    
    # Branch selection
    if not df_branch.empty:
        branch_names = df_branch['shop_name'].tolist()
        selected_branch_ot = st.selectbox("Select Branch", branch_names, key="ot_branch")
        shop_id_ot = df_branch[df_branch['shop_name'] == selected_branch_ot]['shop_id'].iloc[0]
        
        st.info(f"Showing OT performance for **{selected_branch_ot}**")
        
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
                        df = pd.read_sql(query, conn, params=params)
                        if 'employee_id' in df.columns:
                            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
                        return df

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
                st.subheader("Top 10 OT Performance")
                
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
                st.warning("No OT targets data available")
                
                # Show sales data without targets
                display_ot_notarget = df_ot_branch[['employee_name', 'total_sale']].copy()
                display_ot_notarget['total_sale'] = display_ot_notarget['total_sale'].apply(lambda x: format_currency(x))
                render_table(display_ot_notarget, width="stretch")
        else:
            st.info("No OT data for this branch")
    else:
        st.error("No branch data available")

# ========================
# TAB 7: QR COMMISSION
# ========================
with tab6:
    render_qr_tab(
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        selected_branches=selected_branches,
        data_mode=data_mode,
        key_prefix="legacy_qr",
    )
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
    st.subheader("Performance Summary")

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
    st.subheader("Product Comparison - Current vs Previous Month")

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
    # Line Item Name (Category) - Current Month
    # -------------------------------
    st.markdown("---")
    st.subheader("Line Item Name - Current Month")
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
            title=f"Top {len(df_top_categories)} Line Item Names - {month_name(curr_year, curr_month)}",
            labels={'Current_Sales': 'Sales ()', 'Category': 'Line Item Name'},
            color='Current_Sales',
            color_continuous_scale='Viridis'
        )
        fig_cat.update_traces(texttemplate=' %{x:,.0f}', textposition='inside')
        fig_cat.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_cat, width="stretch")

    else:
        st.info("No current month category data available for Top Line Item Names")

    # -------------------------------
    # Top products (by product name) - Current Month
    # -------------------------------
    st.markdown("---")
    st.subheader("Top Products (by Product Name) - Current Month")

    # Fetch top products by product name using the new DB function
    df_products_curr = get_cached_product_monthly_sales_by_product(curr_year, curr_month, selected_branches, data_mode, category=None)

    if df_products_curr is None or df_products_curr.empty:
        st.info("No current month product-level data available")
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
            title=f"Top {len(df_top_products)} Products - {month_name(curr_year, curr_month)}",
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
        st.subheader("Low-performing Products & Line Items")
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
    st.subheader("Comparison Table")

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
        st.info("No product sales data available for these months")
    else:
        render_table(df_display, width="stretch", height=600)
        # Download numeric comparison (unformatted)





# ========================
# TAB 9: RAMZAN DEALS
# ========================
with tab9:
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
# TAB 10: CATEGORY FILTERS
# ========================
with tab10:
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
# TAB 11: CATEGORY COVERAGE
# ========================
with tab11:
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

    st.markdown("---")
    st.subheader("Branch-wise Filter Impact (Blocked vs Category)")
    st.caption(
        "Compares four layers: Raw (no blocked, no category), Blocked-only, Category-only, Both. "
        "This answers: blocked names/comments ka impact hai ya category include/exclude ka."
    )

    with st.spinner("Calculating filter impact..."):
        df_unfiltered_raw = get_cached_branch_summary(
            start_date_str, end_date_str, selected_branches, "Unfiltered", apply_category_filters=False
        )
        df_blocked_only = get_cached_branch_summary(
            start_date_str, end_date_str, selected_branches, "Filtered", apply_category_filters=False
        )
        df_category_only = get_cached_branch_summary(
            start_date_str, end_date_str, selected_branches, "Unfiltered", apply_category_filters=True
        )
        df_both = get_cached_branch_summary(
            start_date_str, end_date_str, selected_branches, "Filtered", apply_category_filters=True
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

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Unfiltered (Raw)", format_currency(total_unfiltered_raw))
    with m2:
        st.metric(
            "Blocked Only",
            format_currency(total_blocked_only),
            delta=f"-{format_currency(blocked_impact)} ({blocked_pct:.1f}%)",
            delta_color="inverse",
        )
    with m3:
        st.metric(
            "Category Only",
            format_currency(total_category_only),
            delta=f"-{format_currency(category_impact)} ({category_pct:.1f}%)",
            delta_color="inverse",
        )
    with m4:
        st.metric(
            "Blocked + Category",
            format_currency(total_both),
            delta=f"-{format_currency(combined_impact)} ({combined_pct:.1f}%)",
            delta_color="inverse",
        )

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

        render_table(
            show[
                [
                    "Branch",
                    "Unfiltered (Raw)",
                    "Blocked Only",
                    "Category Only",
                    "Blocked + Category",
                    "Blocked Impact (PKR)",
                    "Category Impact (PKR)",
                    "Total Impact (PKR)",
                    "Total Impact (%)",
                ]
            ],
            width="stretch",
            height=340,
        )
    else:
        st.info("No branch impact data available for this period/branches.")

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

        m1, m2, m3 = st.columns(2)
        with m1:
            st.metric("Included Categories", f"{len(counted_df):,}")
        with m2:
            st.metric("Excluded Categories", f"{len(excluded_df):,}")
        with m3:
            st.metric("Excluded Sales Impact", f"{excluded_df['total_sales'].sum():,.0f}")

        with st.expander("Edit Active Categories (Save deactivations by name)", expanded=False):
            df_editor = df_cov.copy()
            df_editor["Active"] = df_editor["counted"].astype(bool)
            edited_df = st.data_editor(
                df_editor[["category_name", "Active", "total_qty", "total_sales", "status"]],
                column_config={
                    "category_name": "Category",
                    "Active": st.column_config.CheckboxColumn("Active", default=True),
                    "total_sales": st.column_config.NumberColumn("Total Sales", format="Rs %.0f"),
                    "total_qty": st.column_config.NumberColumn("Total Qty", format="%.0f"),
                    "status": "Current Filter Status",
                },
                disabled=["category_name", "total_qty", "total_sales", "status"],
                hide_index=True,
                width="stretch",
                key="cat_coverage_editor",
            )
            if st.button("Save Active/Inactive Categories", key="save_cat_coverage_editor"):
                deactivated = edited_df.loc[~edited_df["Active"], "category_name"].astype(str).tolist()
                current_settings = get_saved_category_filters()
                current_settings["excluded_category_names"] = [str(x).strip() for x in deactivated if str(x).strip()]
                save_category_filters(current_settings)
                refresh_all_caches()
                st.success(f"Saved. {len(deactivated):,} categories deactivated.")
                st.rerun()

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

        st.markdown("---")
        st.subheader("Blocked Transactions (Detail)")
        st.caption("Transactions excluded by Blocked Names or Blocked Comments (for Filtered mode).")

        df_impact = get_cached_blocked_impact(start_date_str, end_date_str, selected_branches)
        if df_impact is None or df_impact.empty:
            st.info("No blocked transactions found for this period (or blocked lists are empty).")
        else:
            df_impact = df_impact.copy()
            df_impact["Nt_amount"] = pd.to_numeric(df_impact["Nt_amount"], errors="coerce").fillna(0.0)

            total_impact = float(df_impact["Nt_amount"].sum())
            count_impact = int(len(df_impact))
            b1, b2 = st.columns(2)
            with b1:
                st.metric("Total Excluded Sales", format_currency(total_impact))
            with b2:
                st.metric("Excluded Transactions", f"{count_impact:,}")

            df_branch_sum = (
                df_impact.groupby(["shop_id", "shop_name"], as_index=False)["Nt_amount"]
                .agg(blocked_sales_sum="sum", blocked_tx_count="count")
                .sort_values("blocked_sales_sum", ascending=False)
            )
            render_table(
                df_branch_sum.rename(
                    columns={
                        "shop_name": "Branch",
                        "blocked_sales_sum": "Excluded Sales (PKR)",
                        "blocked_tx_count": "Tx Count",
                    }
                )[["Branch", "Excluded Sales (PKR)", "Tx Count"]],
                width="stretch",
                height=260,
            )

            with st.expander("View Detailed Blocked Transactions", expanded=False):
                grand = pd.DataFrame(
                    [
                        {
                            "shop_id": -1,
                            "shop_name": "Grand Total",
                            "blocked_sales_sum": float(df_branch_sum["blocked_sales_sum"].sum()),
                            "blocked_tx_count": int(df_branch_sum["blocked_tx_count"].sum()),
                        }
                    ]
                )
                branch_totals = pd.concat([df_branch_sum, grand], ignore_index=True)
                render_table(
                    branch_totals.rename(
                        columns={
                            "shop_name": "Branch",
                            "blocked_sales_sum": "Excluded Sales (PKR)",
                            "blocked_tx_count": "Tx Count",
                        }
                    )[["Branch", "Excluded Sales (PKR)", "Tx Count"]],
                    width="stretch",
                    height=220,
                )
                df_show = df_impact.copy()
                df_show["sale_date"] = pd.to_datetime(df_show["sale_date"], errors="coerce")
                df_show = df_show.sort_values(["shop_name", "sale_date"], ascending=[True, False])
                render_table(df_show, width="stretch", height=420, hide_index=True)

        st.markdown("---")
        st.subheader("Unmapped Products")
        st.caption("Products making sales but not linked to any category in TempProductBarcode.")
        df_unmapped = get_cached_unmapped_products(start_date_str, end_date_str, selected_branches)
        if df_unmapped is None or df_unmapped.empty:
            st.success("No unmapped products detected for this period.")
        else:
            df_unmapped = df_unmapped.copy()
            df_unmapped["total_sales"] = pd.to_numeric(df_unmapped.get("total_sales"), errors="coerce").fillna(0.0)
            df_unmapped["total_qty"] = pd.to_numeric(df_unmapped.get("total_qty"), errors="coerce").fillna(0.0)
            u1, u2, u3 = st.columns(2)
            with u1:
                st.metric("Unmapped Items", f"{len(df_unmapped):,}")
            with u2:
                st.metric("Unmapped Sales", format_currency(float(df_unmapped["total_sales"].sum())))
            with u3:
                st.metric("Unmapped Qty", f"{float(df_unmapped['total_qty'].sum()):,.0f}")

            render_table(df_unmapped, width="stretch", height=420, hide_index=True)

# ========================
# TAB 12: PIVOT TABLES
# ========================
with tab12:
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
# TAB 13: KHADDA DIAGNOSTICS
# ========================
with tab13:
    render_khadda_diagnostics_tab(
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        selected_branches=selected_branches,
        data_mode=data_mode,
        key_prefix="khadda",
    )

# ========================
# TAB 14: INDOGE-FIRST DIAGNOSTICS
# ========================
with tab14:
    render_indoge_first_tab(
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        selected_branches=selected_branches,
        data_mode=data_mode,
        key_prefix="indoge_first",
    )

# ========================
# TAB 15: MULTI-SIGNAL MATCH
# ========================
with tab15:
    render_multi_signal_match_tab(
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        selected_branches=selected_branches,
        data_mode=data_mode,
        key_prefix="multi_signal",
    )

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








