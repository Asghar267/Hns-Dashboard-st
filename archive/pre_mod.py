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

# Set pandas options to avoid FutureWarnings
pd.set_option('future.no_silent_downcasting', True)
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
