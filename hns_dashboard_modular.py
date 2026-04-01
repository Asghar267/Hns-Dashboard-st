"""
HNS Sales Dashboard (Modular)

Feature-complete modular dashboard entry point.
"""

from __future__ import annotations

import time
import threading
from datetime import date, datetime
from typing import List

import pandas as pd
import streamlit as st

try:
    from streamlit_option_menu import option_menu
except Exception:
    option_menu = None

try:
    from streamlit_extras.add_vertical_space import add_vertical_space
except Exception:
    add_vertical_space = None
try:
    from st_notifications import notify as _notify
except Exception:
    _notify = None

from dashboard_tabs.category_coverage_tab import CategoryCoverageTab
from dashboard_tabs.chef_sales_tab import ChefSalesTab
from dashboard_tabs.chef_targets_tab import ChefTargetsTab
from dashboard_tabs.food_panda_tab import FoodPandaTab
from dashboard_tabs.material_cost_commission_tab import MaterialCostCommissionTab
from dashboard_tabs.order_takers_tab import OrderTakersTab
from dashboard_tabs.overview_tab import OverviewTab
from dashboard_tabs.ot_targets_tab import OTTargetsTab
from dashboard_tabs.pivot_tables_tab import PivotTablesTab
from dashboard_tabs.ramzan_deals_tab import RamzanDealsTab
try:
    from dashboard_tabs.trends_analytics_tab import TrendsAnalyticsTab
except Exception as _trends_import_err:
    TrendsAnalyticsTab = None
    _TRENDS_IMPORT_ERROR = _trends_import_err
from modules.auth import (
    authenticate_user,
    check_session_timeout,
    delete_user,
    hash_password,
    list_users,
    logout_user,
    update_activity,
    upsert_user,
)
from modules.config import SELECTED_BRANCH_IDS, BRANCH_NAMES
from modules.database import refresh_all_caches, warm_up_caches
from modules.qr_tab_renderer import (
    render_khadda_diagnostics_tab,
    render_qr_tab,
)
from modules.qr_business_toggles import QR_TOGGLES
from modules.utils import (
    get_date_presets,
)
from modules.database import get_saved_category_filters
from config import app_config
from components.new_navbar import NewNavbarComponent


EXCLUDED_EMPLOYEE_NAMES = {"online/unassigned"}


def _toast(message: str, severity: str = "info") -> None:
    if _notify is not None:
        try:
            _notify(message, severity=severity)
            return
        except Exception:
            pass
    st.toast(message)


def exclude_employee_names(df: pd.DataFrame, column: str = "employee_name") -> pd.DataFrame:
    if df is None or df.empty or column not in df.columns:
        return df
    normalized = df[column].astype(str).str.strip().str.lower()
    return df[~normalized.isin(EXCLUDED_EMPLOYEE_NAMES)].copy()


def load_custom_css() -> None:
    """Load custom CSS for better UI."""
    dark_mode = st.session_state.get("dark_mode", False)

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

    st.markdown(
        f"""
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
        /* Reduce top whitespace above main heading */
        .block-container {{
            padding-top: 1rem !important;
        }}
        h1, h2, h3 {{
            margin-top: 0.2rem !important;
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
        /* Fullscreen dataframes: Streamlit uses different containers across versions.
           Make the overlay full-screen and aggressively override inline heights so the
           table uses the available viewport instead of leaving blank space. */
        div[role="dialog"],
        div[data-testid="stDialog"],
        div[data-testid="stModal"],
        div[aria-modal="true"] {{
            position: fixed !important;
            inset: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* Modal/dialog content wrapper */
        div[role="dialog"] > div,
        div[data-testid="stDialog"] > div,
        div[data-testid="stModal"] > div,
        div[data-testid="stModalContent"] {{
            height: 100vh !important;
            max-height: 100vh !important;
        }}

        /* Force a flex layout so the table area can expand instead of leaving blank space */
        div[role="dialog"] > div,
        div[data-testid="stDialog"] > div,
        div[data-testid="stModal"] > div,
        div[data-testid="stModalContent"] {{
            display: flex !important;
            flex-direction: column !important;
            min-height: 0 !important;
        }}

        /* The dataframe wrapper + resizable container + grid editor should take remaining height.
           Use calc(...) to beat inline px heights coming from st.dataframe(height=...). */
        div[role="dialog"] [data-testid="stDataFrame"],
        div[data-testid="stDialog"] [data-testid="stDataFrame"],
        div[data-testid="stModal"] [data-testid="stDataFrame"],
        div[aria-modal="true"] [data-testid="stDataFrame"] {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 4rem) !important;
            max-height: calc(100vh - 4rem) !important;
        }}
        div[role="dialog"] [data-testid="stDataFrameResizable"],
        div[data-testid="stDialog"] [data-testid="stDataFrameResizable"],
        div[data-testid="stModal"] [data-testid="stDataFrameResizable"],
        div[aria-modal="true"] [data-testid="stDataFrameResizable"],
        div[role="dialog"] .glideDataEditor,
        div[data-testid="stDialog"] .glideDataEditor,
        div[data-testid="stModal"] .glideDataEditor,
        div[aria-modal="true"] .glideDataEditor,
        div[role="dialog"] [role="grid"],
        div[data-testid="stDialog"] [role="grid"],
        div[data-testid="stModal"] [role="grid"],
        div[aria-modal="true"] [role="grid"],
        div[role="dialog"] canvas,
        div[data-testid="stDialog"] canvas,
        div[data-testid="stModal"] canvas,
        div[aria-modal="true"] canvas {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 5rem) !important;
            max-height: calc(100vh - 5rem) !important;
            width: 98vw !important;
            max-width: 98vw !important;
            margin: 0 auto !important;
        }}

        /* st.table fallback */
        div[role="dialog"] [data-testid="stTable"],
        div[data-testid="stDialog"] [data-testid="stTable"],
        div[data-testid="stModal"] [data-testid="stTable"],
        div[aria-modal="true"] [data-testid="stTable"] {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 5rem) !important;
            max-height: calc(100vh - 5rem) !important;
            width: 98vw !important;
            max-width: 98vw !important;
            margin: 0 auto !important;
        }}
        </style>

    """, unsafe_allow_html=True)


def render_user_management_tab(branch_name_map: dict) -> None:
    st.header("User Management")
    st.caption("Manage users, branch access, and tab/table visibility.")

    users = list_users()
    if users:
        df_users = pd.DataFrame(users)
        for col in ["allowed_branches", "allowed_tabs", "allowed_tables"]:
            if col in df_users.columns:
                df_users[col] = df_users[col].apply(lambda v: str(v))
        st.subheader("Current Users")
        st.dataframe(df_users, width="stretch", hide_index=True, height=240)

    tab_options = [
        "Overview", "Order Takers", "Chef Sales", "Chef Targets", "Food Panda", "OT Targets",
        "QR Commission", "Khadda Diagnostics", "Material Cost Commission",
        "Trends & Analytics", "Ramzan Deals", "Category Filters & Coverage", "Pivot Tables",
    ]
    qr_table_options = [
        "Split Report", "Detailed Transactions", "Employee Totals",
        "Employee Totals (No Sales/Candelahns)",
        "Employee Pivot", "Branch Totals", "Product-wise Commission", "Data Quality",
    ]

    usernames = [u.get("username") for u in users if u.get("username")]
    if "user_mgmt_selected" not in st.session_state:
        st.session_state.user_mgmt_selected = "<new>"

    with st.form("user_select_form"):
        selected = st.selectbox(
            "Select user to edit",
            ["<new>"] + usernames,
            index=(["<new>"] + usernames).index(st.session_state.user_mgmt_selected)
            if st.session_state.user_mgmt_selected in (["<new>"] + usernames) else 0,
            key="user_mgmt_select",
        )
        load_user = st.form_submit_button("Load User", width="stretch")
        if load_user:
            st.session_state.user_mgmt_selected = selected

    selected = st.session_state.user_mgmt_selected
    existing = next((u for u in users if u.get("username") == selected), None) if selected != "<new>" else None

    with st.form("user_management_form"):
        username = st.text_input("Username", value=existing.get("username") if existing else "", disabled=bool(existing), autocomplete="username")
        password = st.text_input("Password (leave blank to keep)", type="password", value="", autocomplete="new-password")
        role = st.selectbox("Role", ["user", "admin"], index=0 if not existing or existing.get("role") != "admin" else 1)

        all_branches = st.checkbox("Allow all branches", value=existing.get("allowed_branches") == "all" if existing else False)
        branch_ids = list(branch_name_map.keys()) if branch_name_map else SELECTED_BRANCH_IDS
        allowed_branches = st.multiselect(
            "Allowed Branches", options=branch_ids,
            default=branch_ids if all_branches else (existing.get("allowed_branches") or [] if existing else []),
            format_func=lambda x: branch_name_map.get(int(x), f"Branch {x}"), disabled=all_branches,
        )

        all_tabs = st.checkbox("Allow all tabs", value=existing.get("allowed_tabs") == "all" if existing else False)
        allowed_tabs = st.multiselect(
            "Allowed Tabs", options=tab_options,
            default=tab_options if all_tabs else (existing.get("allowed_tabs") or [] if existing else []),
            disabled=all_tabs,
        )

        show_qr_tables = all_tabs or ("QR Commission" in allowed_tabs)
        all_qr_tables = st.checkbox(
            "Allow all QR tables",
            value=(existing.get("allowed_tables", {}).get("QR Commission") == "all") if existing else False,
            disabled=not show_qr_tables,
        )
        allowed_qr_tables = st.multiselect(
            "Allowed QR Tables", options=qr_table_options,
            default=qr_table_options if all_qr_tables else (existing.get("allowed_tables", {}).get("QR Commission", []) if existing else []),
            disabled=not show_qr_tables or all_qr_tables,
        )

        submitted = st.form_submit_button("Save User", width="stretch")
        if submitted:
            if not username:
                st.error("Username is required.")
            else:
                record = existing.copy() if existing else {}
                record["username"] = username
                record["role"] = role
                record["allowed_branches"] = "all" if all_branches else allowed_branches
                record["allowed_tabs"] = "all" if all_tabs else allowed_tabs
                record["allowed_tables"] = {"QR Commission": "all" if all_qr_tables else allowed_qr_tables}
                if password:
                    record["password_hash"] = hash_password(password)
                elif not existing:
                    st.error("Password is required for new users.")
                    return
                upsert_user(record)
                st.success("User saved.")

    if existing and existing.get("username"):
        if st.button("Delete User", width="stretch"):
            delete_user(existing.get("username"))
            st.success("User deleted.")


def main() -> None:
    pd.set_option("future.no_silent_downcasting", True)

    st.set_page_config(
        page_title="HNS Sales Dashboard (Modular)",
        page_icon="HNS",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if "mod_cache_epoch" not in st.session_state:
        st.session_state.mod_cache_epoch = 0
    if "mod_cache" not in st.session_state:
        st.session_state.mod_cache = {}
    if "mod_cache_signature" not in st.session_state:
        st.session_state.mod_cache_signature = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "overview"

    load_custom_css()

    if st.session_state.get("authenticated", False):
        if check_session_timeout():
            logout_user()
            st.warning("Session timed out. Please log in again.")
            return
        update_activity()
    else:
        authenticate_user()
        return

    st.sidebar.title("Dashboard Controls")

    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

    user_record = st.session_state.get("user", {}) or {}
    role = str(user_record.get("role", "user")).lower()

    navbar_config = app_config.AppConfig.NAVBAR_ITEMS

    if st.sidebar.checkbox("Dark Mode", value=st.session_state.get("dark_mode", False)):
        if not st.session_state.get("dark_mode"):
            st.session_state.dark_mode = True
            st.rerun()
    else:
        if st.session_state.get("dark_mode"):
            st.session_state.dark_mode = False
            st.rerun()

    st.sidebar.markdown("---")
    if add_vertical_space is not None:
        add_vertical_space(1)
    st.sidebar.header("Date Range")

    date_preset = st.sidebar.selectbox(
        "Quick Select",
        ["Custom", "Today", "Yesterday", "This Week", "Last Week",
         "This Month", "Last Month", "This Quarter", "This Year"],
    )

    start_date, end_date = get_date_presets(date_preset)

    if date_preset != "Custom":
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
    if add_vertical_space is not None:
        add_vertical_space(1)
    st.sidebar.header("Filters")

    data_mode = st.sidebar.radio(
        "Data Mode",
        ["Filtered", "Unfiltered"],
        index=0 if QR_TOGGLES.blocked_mode_default.lower() == "filtered" else 1,
        help="Filtered mode excludes blocked customers and comments",
    )

    branch_name_map = {
        2: "Khadda Main Branch", 3: "FESTIVAL", 4: "Rahat Commercial",
        6: "TOWER", 8: "North Nazimabad", 10: "MALIR", 14: "FESTIVAL 2",
    }

    allowed_branches = user_record.get("allowed_branches", SELECTED_BRANCH_IDS)
    if allowed_branches == "all":
        allowed_branches = SELECTED_BRANCH_IDS

    selected_branches: List[int] = st.sidebar.multiselect(
        "Select Branches",
        options=allowed_branches,
        default=allowed_branches,
        format_func=lambda x: branch_name_map.get(int(x), f"Branch {x}"),
    )

    if not selected_branches:
        st.sidebar.warning("Please select at least one branch")
        st.stop()

    st.sidebar.markdown("---")
    if add_vertical_space is not None:
        add_vertical_space(1)
    st.sidebar.header("Target Period")
    target_year = st.sidebar.number_input("Year", 2000, 2100, 2026, 1)
    target_month = st.sidebar.selectbox(
        "Month", range(1, 13),
        index=datetime.now().month - 1,
        format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
    )

    signature = (start_date_str, end_date_str, tuple(sorted(selected_branches)), data_mode, target_year, target_month)
    if st.session_state.mod_cache_signature != signature:
        st.session_state.mod_cache_signature = signature
        st.session_state.mod_cache_epoch += 1
        st.session_state.mod_cache = {}

    st.sidebar.markdown("---")
    st.sidebar.header("Data Controls")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("Refresh", width="stretch"):
            with st.spinner("Refreshing data..."):
                try:
                    refresh_all_caches()
                    st.session_state.last_refresh = datetime.now()
                    st.session_state.mod_cache_epoch += 1
                    st.session_state.mod_cache = {}
                    _toast("Data refreshed.", severity="success")
                except Exception as e:
                    _toast(f"Refresh failed: {e}", severity="error")
                time.sleep(1)
                st.rerun()

    with col2:
        auto_refresh = st.checkbox("Auto", value=st.session_state.auto_refresh)
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh

    warm_cache = st.sidebar.checkbox(
        "Warm Cache in Background",
        value=st.session_state.get("warm_cache_enabled", True),
        help="Preloads common queries after filters are set.",
    )
    st.session_state.warm_cache_enabled = warm_cache
    if warm_cache:
        warm_sig = f"{start_date_str}:{end_date_str}:{sorted(selected_branches)}:{data_mode}:{target_year}:{target_month}"
        if st.session_state.get("warm_cache_signature") != warm_sig:
            st.session_state.warm_cache_signature = warm_sig
            def _warm():
                warm_up_caches(start_date_str, end_date_str, selected_branches, data_mode, target_year, target_month, include_heavy=False)
            t = threading.Thread(target=_warm, daemon=True)
            try:
                from streamlit.runtime.scriptrunner import add_script_run_ctx
                add_script_run_ctx(t)
            except Exception:
                pass
            t.start()

    if st.sidebar.button("Generate Snapshots", width="stretch", key="main_sidebar_snapshots"):
        with st.spinner("Generating snapshots..."):
            try:
                from daily_branch_snapshots import generate_snapshots
                out_dir = generate_snapshots(
                    start_date=start_date_str, end_date=end_date_str,
                    target_year=target_year, target_month=target_month,
                    branches=selected_branches, data_mode=data_mode,
                    output_dir="HNS_Deshboard/snapshots",
                )
                st.sidebar.success(f"Saved to {out_dir.name}")
            except Exception as e:
                st.sidebar.error(f"Error setting up snapshots: {e}")

    time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
    st.sidebar.markdown(f'<p class="data-fresh">Last refresh: {time_since_refresh}s ago</p>', unsafe_allow_html=True)

    if st.session_state.auto_refresh and time_since_refresh > 300:
        try:
            refresh_all_caches()
            st.session_state.last_refresh = datetime.now()
            st.session_state.mod_cache_epoch += 1
            st.session_state.mod_cache = {}
            _toast("Auto-refresh completed.", severity="success")
        except Exception as e:
            _toast(f"Auto-refresh failed: {e}", severity="error")

    saved_filter_badge = get_saved_category_filters()
    badge_inc = saved_filter_badge.get("included_category_ids", [])
    badge_exc = saved_filter_badge.get("excluded_category_ids", [])
    inc_text = ",".join(map(str, badge_inc)) if badge_inc else "none"
    exc_text = ",".join(map(str, badge_exc)) if badge_exc else "none"
    st.sidebar.caption(f"Category Filters | Included: {inc_text} | Excluded: {exc_text}")

    branch_name_map = {int(k): str(v) for k, v in BRANCH_NAMES.items()}
    if not branch_name_map:
        branch_name_map = {int(b): f"Branch {b}" for b in selected_branches}

    branch_labels = [branch_name_map.get(int(b), f"Branch {b}") for b in selected_branches]
    title_text = "HNS Sales Dashboard" if len(branch_labels) == len(SELECTED_BRANCH_IDS) else f"HNS Sales Dashboard: {', '.join(branch_labels)}"

    st.title(title_text)
    st.caption(f"Period: {start_date_str} to {end_date_str} | Mode: {data_mode}")

    user_record = st.session_state.get("user", {}) or {}
    role = str(user_record.get("role", "user")).lower()
    allowed_tabs = user_record.get("allowed_tabs", "all")
    allowed_tables = user_record.get("allowed_tables", "all")
    if role == "admin":
        allowed_tabs = "all"

    df_line_item = None

    def _render_overview():
        OverviewTab(start_date_str, end_date_str, selected_branches, data_mode).render_overview()

    def _render_order_takers():
        OrderTakersTab(start_date_str, end_date_str, selected_branches, data_mode).render_order_takers()

    def _render_chef_sales():
        ChefSalesTab(start_date_str, end_date_str, selected_branches, data_mode).render_chef_sales()

    def _render_chef_targets():
        ChefTargetsTab(target_year, target_month, start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_food_panda():
        FoodPandaTab(start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_ot_targets():
        OTTargetsTab(target_year, target_month, start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_qr_commission():
        render_qr_tab(start_date_str=start_date_str, end_date_str=end_date_str, selected_branches=selected_branches, data_mode=data_mode, key_prefix="mod_qr", allowed_tables=allowed_tables)

    def _render_khadda_diagnostics():
        render_khadda_diagnostics_tab(start_date_str=start_date_str, end_date_str=end_date_str, selected_branches=selected_branches, data_mode=data_mode, key_prefix="mod_khadda")

    def _render_material_cost():
        MaterialCostCommissionTab(start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_trends_analytics():
        if TrendsAnalyticsTab is None:
            st.error(f"Trends & Analytics tab failed to import: {_TRENDS_IMPORT_ERROR}")
            return
        TrendsAnalyticsTab(
            start_date_str,
            end_date_str,
            selected_branches,
            data_mode,
            target_year=target_year,
            target_month=target_month,
            branch_name_map=branch_name_map,
            df_line_item=df_line_item,
        ).render()

    def _render_ramzan_deals():
        RamzanDealsTab(start_date, end_date, selected_branches, branch_name_map).render()

    def _render_category_coverage():
        CategoryCoverageTab(start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_pivot_tables():
        PivotTablesTab(start_date_str, end_date_str, selected_branches, data_mode, df_line_item).render()

    def _render_user_management():
        um_map = {2: "Khadda Main Branch", 3: "FESTIVAL", 4: "Rahat Commercial", 6: "TOWER", 8: "North Nazimabad", 10: "MALIR", 14: "FESTIVAL 2"}
        render_user_management_tab(um_map)

    tab_map = {
        'overview': _render_overview,
        'order_takers': _render_order_takers,
        'chef_sales': _render_chef_sales,
        'chef_targets': _render_chef_targets,
        'food_panda': _render_food_panda,
        'ot_targets': _render_ot_targets,
        'qr_commission': _render_qr_commission,
        'khadda_diagnostics': _render_khadda_diagnostics,
        'material_cost_commission': _render_material_cost,
        'trends_analytics': _render_trends_analytics,
        'ramzan_deals': _render_ramzan_deals,
        'category_filters_&_coverage': _render_category_coverage,
        'pivot_tables': _render_pivot_tables,
    }
    # Support legacy/double-underscore key from navbar normalization
    tab_map.setdefault('trends__analytics', _render_trends_analytics)

    if role == "admin":
        tab_map['user_management'] = _render_user_management

    # Render a single active tab only (Streamlit reruns on any widget change; this avoids
    # recomputing the entire dashboard across all tabs on every interaction).
    active_key = NewNavbarComponent(navbar_config).render(user_record=user_record)
    render_fn = tab_map.get(active_key) or tab_map.get(active_key.replace("&", "")) or _render_overview
    try:
        render_fn()
    except Exception as e:
        st.error(f"An error occurred: {e}")

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
