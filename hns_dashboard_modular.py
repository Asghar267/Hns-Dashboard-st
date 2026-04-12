"""
HNS Sales Dashboard (Modular)

Feature-complete modular dashboard entry point.
"""

from __future__ import annotations

import time
import threading
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

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
from dashboard_tabs.database_health_tab import DatabaseHealthDiagnosticsTab
from dashboard_tabs.food_panda_tab import FoodPandaTab
from dashboard_tabs.material_cost_commission_tab import MaterialCostCommissionTab
from dashboard_tabs.order_takers_tab import OrderTakersTab
from dashboard_tabs.overview_tab import OverviewTab
from dashboard_tabs.ot_targets_tab import OTTargetsTab
from dashboard_tabs.pivot_tables_tab import PivotTablesTab
from dashboard_tabs.ramzan_deals_tab import RamzanDealsTab
from dashboard_tabs.web_items_export_tab import WebItemsExportTab
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
from modules.database import (
    get_cached_all_branches_lookup,
    get_cached_branch_lookup,
    refresh_all_caches,
    warm_up_caches,
)
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
from modules.responsive import (
    clamp_dataframe_height,
    get_responsive_context,
    infer_initial_sidebar_state,
    render_layout_mode_control,
    responsive_columns,
)


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
        :root {{
            --hns-phone-breakpoint: 768px;
            --hns-tablet-breakpoint: 1024px;
        }}
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
        .mobile-controls-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }}
        .mobile-controls-card p {{
            margin: 0;
            color: {text_color};
        }}
        /* Reduce top whitespace above main heading */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1.25rem !important;
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
        /* Fullscreen dataframes (scoped):
           Streamlit "Settings" and other built-in dialogs also use role="dialog".
           Scope these rules to dialogs that actually contain a DataFrame/Table so we
           don't blank the Settings modal. Uses :has(...) (supported in modern Chromium). */
        div[role="dialog"]:has([data-testid="stDataFrame"]),
        div[role="dialog"]:has([data-testid="stTable"]),
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]),
        div[data-testid="stDialog"]:has([data-testid="stTable"]),
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]),
        div[data-testid="stModal"]:has([data-testid="stTable"]),
        div[aria-modal="true"]:has([data-testid="stDataFrame"]),
        div[aria-modal="true"]:has([data-testid="stTable"]) {{
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
        div[role="dialog"]:has([data-testid="stDataFrame"]) > div,
        div[role="dialog"]:has([data-testid="stTable"]) > div,
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) > div,
        div[data-testid="stDialog"]:has([data-testid="stTable"]) > div,
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) > div,
        div[data-testid="stModal"]:has([data-testid="stTable"]) > div,
        div[data-testid="stModalContent"]:has([data-testid="stDataFrame"]),
        div[data-testid="stModalContent"]:has([data-testid="stTable"]) {{
            height: 100vh !important;
            max-height: 100vh !important;
        }}

        /* Force a flex layout so the table area can expand instead of leaving blank space */
        div[role="dialog"]:has([data-testid="stDataFrame"]) > div,
        div[role="dialog"]:has([data-testid="stTable"]) > div,
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) > div,
        div[data-testid="stDialog"]:has([data-testid="stTable"]) > div,
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) > div,
        div[data-testid="stModal"]:has([data-testid="stTable"]) > div,
        div[data-testid="stModalContent"]:has([data-testid="stDataFrame"]),
        div[data-testid="stModalContent"]:has([data-testid="stTable"]) {{
            display: flex !important;
            flex-direction: column !important;
            min-height: 0 !important;
        }}

        /* The dataframe wrapper + resizable container + grid editor should take remaining height.
           Use calc(...) to beat inline px heights coming from st.dataframe(height=...). */
        div[role="dialog"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrame"],
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrame"],
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrame"],
        div[aria-modal="true"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrame"] {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 4rem) !important;
            max-height: calc(100vh - 4rem) !important;
        }}
        div[role="dialog"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrameResizable"],
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrameResizable"],
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrameResizable"],
        div[aria-modal="true"]:has([data-testid="stDataFrame"]) [data-testid="stDataFrameResizable"],
        div[role="dialog"]:has([data-testid="stDataFrame"]) .glideDataEditor,
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) .glideDataEditor,
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) .glideDataEditor,
        div[aria-modal="true"]:has([data-testid="stDataFrame"]) .glideDataEditor,
        div[role="dialog"]:has([data-testid="stDataFrame"]) [role="grid"],
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) [role="grid"],
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) [role="grid"],
        div[aria-modal="true"]:has([data-testid="stDataFrame"]) [role="grid"],
        div[role="dialog"]:has([data-testid="stDataFrame"]) canvas,
        div[data-testid="stDialog"]:has([data-testid="stDataFrame"]) canvas,
        div[data-testid="stModal"]:has([data-testid="stDataFrame"]) canvas,
        div[aria-modal="true"]:has([data-testid="stDataFrame"]) canvas {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 5rem) !important;
            max-height: calc(100vh - 5rem) !important;
            width: 98vw !important;
            max-width: 98vw !important;
            margin: 0 auto !important;
        }}

        /* st.table fallback */
        div[role="dialog"]:has([data-testid="stTable"]) [data-testid="stTable"],
        div[data-testid="stDialog"]:has([data-testid="stTable"]) [data-testid="stTable"],
        div[data-testid="stModal"]:has([data-testid="stTable"]) [data-testid="stTable"],
        div[aria-modal="true"]:has([data-testid="stTable"]) [data-testid="stTable"] {{
            flex: 1 1 auto !important;
            min-height: 0 !important;
            height: calc(100vh - 5rem) !important;
            max-height: calc(100vh - 5rem) !important;
            width: 98vw !important;
            max-width: 98vw !important;
            margin: 0 auto !important;
        }}
        @media (max-width: 1024px) {{
            .metric-card {{
                padding: 16px;
            }}
            .metric-value {{
                font-size: 1.65rem;
            }}
        }}
        @media (max-width: 768px) {{
            .block-container {{
                padding-top: 0.75rem !important;
                padding-left: 0.9rem !important;
                padding-right: 0.9rem !important;
            }}
            .metric-card {{
                padding: 14px;
                margin: 8px 0;
            }}
            .metric-value {{
                font-size: 1.35rem;
            }}
            .metric-label {{
                font-size: 0.8rem;
            }}
            div[data-testid="stHorizontalBlock"] {{
                gap: 0.5rem !important;
            }}
            div[role="dialog"]:has([data-testid="stDataFrame"]),
            div[data-testid="stDialog"]:has([data-testid="stDataFrame"]),
            div[data-testid="stModal"]:has([data-testid="stDataFrame"]),
            div[aria-modal="true"]:has([data-testid="stDataFrame"]) {{
                inset: 0.5rem !important;
                width: calc(100vw - 1rem) !important;
                height: calc(100vh - 1rem) !important;
            }}
        }}
        </style>

    """, unsafe_allow_html=True)


SNAPSHOT_SETTINGS_PATH = Path("config") / "snapshot_settings.json"
SNAPSHOT_SETTINGS_DEFAULTS: Dict[str, bool] = {
    "branch_cards": True,
    "all_products_by_branch": True,
    "qr_employee_no_sales": True,
    "qr_employee_with_sales": True,
    "ramzan_deals": True,
    "material_cost_commission": True,
    "khadda_diagnostics": True,
}


def load_snapshot_settings() -> Dict[str, bool]:
    try:
        if SNAPSHOT_SETTINGS_PATH.exists():
            data = json.loads(SNAPSHOT_SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                out = SNAPSHOT_SETTINGS_DEFAULTS.copy()
                out.update({k: bool(v) for k, v in data.items() if k in out})
                return out
    except Exception:
        pass
    return SNAPSHOT_SETTINGS_DEFAULTS.copy()


def save_snapshot_settings(settings: Dict[str, Any]) -> None:
    data = SNAPSHOT_SETTINGS_DEFAULTS.copy()
    if isinstance(settings, dict):
        for k in data.keys():
            if k in settings:
                data[k] = bool(settings[k])
    SNAPSHOT_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = SNAPSHOT_SETTINGS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(SNAPSHOT_SETTINGS_PATH)


def render_user_management_tab(branch_name_map: dict) -> None:
    responsive = get_responsive_context()
    st.header("Admin & Snapshots")
    st.caption("Manage users, access controls, and snapshot generation/viewing.")

    ui_users, ui_snaps = st.tabs(["Users", "Snapshots"])

    with ui_users:
        users = list_users()
        usernames = [u.get("username") for u in users if u.get("username")]

        with st.expander("Current Users", expanded=False):
            if users:
                df_users = pd.DataFrame(users)
                for col in ["allowed_branches", "allowed_tabs", "allowed_tables"]:
                    if col in df_users.columns:
                        df_users[col] = df_users[col].apply(lambda v: str(v))
                st.dataframe(df_users, width="stretch", hide_index=True, height=clamp_dataframe_height(responsive, desktop=260, tablet=240, phone=220, kind="compact"))
            else:
                st.info("No users found yet.")

        tab_options = [
            "Overview", "Order Takers", "Chef Sales", "Chef Targets", "Food Panda", "OT Targets",
            "QR Commission", "Khadda Diagnostics", "Database Health Diagnostics", "Material Cost Commission",
            "Trends & Analytics", "Ramzan Deals", "Category Filters & Coverage", "Pivot Tables",
            "Admin & Snapshots",
        ]
        qr_table_options = [
            "Split Report", "Detailed Transactions", "Employee Totals",
            "Employee Totals (No Sales/Candelahns)",
            "Employee Pivot", "Branch Totals", "Product-wise Commission", "Data Quality",
        ]

        if "user_mgmt_selected" not in st.session_state:
            st.session_state.user_mgmt_selected = "<new>"

        admin_cols = responsive_columns(responsive, desktop=2, tablet=2, phone=1, gap="large")
        sel_col = admin_cols[0]
        form_col = admin_cols[1 % len(admin_cols)]
        with sel_col:
            st.subheader("Select User")
            with st.form("user_select_form"):
                selected = st.selectbox(
                    "User",
                    ["<new>"] + usernames,
                    index=(["<new>"] + usernames).index(st.session_state.user_mgmt_selected)
                    if st.session_state.user_mgmt_selected in (["<new>"] + usernames) else 0,
                    key="user_mgmt_select",
                    help="Load an existing user or create a new one.",
                )
                load_user = st.form_submit_button("Load", width="stretch")
                if load_user:
                    st.session_state.user_mgmt_selected = selected

        selected = st.session_state.user_mgmt_selected
        existing = next((u for u in users if u.get("username") == selected), None) if selected != "<new>" else None

        with form_col:
            st.subheader("User Details")
            with st.form("user_management_form"):
                username = st.text_input(
                    "Username",
                    value=existing.get("username") if existing else "",
                    disabled=bool(existing),
                    autocomplete="username",
                )
                password = st.text_input("Password (leave blank to keep)", type="password", value="", autocomplete="new-password")
                role = st.selectbox("Role", ["user", "admin"], index=0 if not existing or existing.get("role") != "admin" else 1)

                st.markdown("**Access**")
                all_branches = st.checkbox("Allow all branches", value=existing.get("allowed_branches") == "all" if existing else False)
                branch_ids = list(branch_name_map.keys()) if branch_name_map else SELECTED_BRANCH_IDS
                allowed_branches = st.multiselect(
                    "Branches",
                    options=branch_ids,
                    default=branch_ids if all_branches else (existing.get("allowed_branches") or [] if existing else []),
                    format_func=lambda x: branch_name_map.get(int(x), f"Branch {x}"),
                    disabled=all_branches,
                )

                all_tabs = st.checkbox("Allow all tabs", value=existing.get("allowed_tabs") == "all" if existing else False)
                existing_tabs = existing.get("allowed_tabs") if existing else []
                if isinstance(existing_tabs, list):
                    normalized_tabs = list(existing_tabs)
                    if "User Management" in normalized_tabs and "Admin & Snapshots" not in normalized_tabs:
                        normalized_tabs = [t for t in normalized_tabs if t != "User Management"] + ["Admin & Snapshots"]
                    existing_tabs = normalized_tabs
                allowed_tabs = st.multiselect(
                    "Tabs",
                    options=tab_options,
                    default=tab_options if all_tabs else (existing_tabs or []),
                    disabled=all_tabs,
                )

                show_qr_tables = all_tabs or ("QR Commission" in allowed_tabs)
                all_qr_tables = st.checkbox(
                    "Allow all QR tables",
                    value=(existing.get("allowed_tables", {}).get("QR Commission") == "all") if existing else False,
                    disabled=not show_qr_tables,
                )
                allowed_qr_tables = st.multiselect(
                    "QR Tables",
                    options=qr_table_options,
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
                        cleaned_tabs = [t for t in allowed_tabs if t != "User Management"]
                        record["allowed_tabs"] = "all" if all_tabs else cleaned_tabs
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

    with ui_snaps:
        st.subheader("Snapshots")
        st.caption("Saved settings are used by the sidebar **Generate Snapshots** button.")

        snap_cols = responsive_columns(responsive, desktop=2, tablet=2, phone=1, gap="large")
        left = snap_cols[0]
        right = snap_cols[1 % len(snap_cols)]

        with left:
            st.markdown("**Generation Settings**")
            st.caption("Enable/disable sections once; the choice is remembered.")

            current = load_snapshot_settings()
            settings_meta = [
                ("branch_cards", "Branch performance cards"),
                ("all_products_by_branch", "All products by branch"),
                ("qr_employee_no_sales", "QR employees (No Sales/Candelahns)"),
                ("qr_employee_with_sales", "QR employees (with Sales)"),
                ("ramzan_deals", "Ramzan deals"),
                ("material_cost_commission", "Material cost commission"),
                ("khadda_diagnostics", "Khadda diagnostics"),
            ]

            btn1, btn2 = responsive_columns(responsive, desktop=2, tablet=2, phone=1)
            with btn1:
                if st.button("Enable All", width="stretch", key="snap_enable_all"):
                    current = {k: True for k in SNAPSHOT_SETTINGS_DEFAULTS.keys()}
                    save_snapshot_settings(current)
                    st.success("Enabled all sections.")
                    st.rerun()
            with btn2:
                if st.button("Disable All", width="stretch", key="snap_disable_all"):
                    current = {k: False for k in SNAPSHOT_SETTINGS_DEFAULTS.keys()}
                    save_snapshot_settings(current)
                    st.success("Disabled all sections.")
                    st.rerun()

            with st.form("snapshot_settings_form", clear_on_submit=False):
                new_settings: Dict[str, bool] = {}
                for key, label in settings_meta:
                    new_settings[key] = st.checkbox(label, value=bool(current.get(key, True)))
                save = st.form_submit_button("Save Settings", width="stretch")
                if save:
                    save_snapshot_settings(new_settings)
                    st.success("Snapshot settings saved.")

            if SNAPSHOT_SETTINGS_PATH.exists():
                ts = datetime.fromtimestamp(SNAPSHOT_SETTINGS_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"Last saved: {ts}")

        with right:
            st.markdown("**Snapshot Viewer**")
            base_dir = Path("HNS_Deshboard") / "snapshots"
            if not base_dir.exists():
                st.info("No snapshots folder found yet. Generate snapshots from the sidebar first.")
                return

            folders = [p for p in base_dir.iterdir() if p.is_dir()]
            folders = sorted(folders, key=lambda p: p.stat().st_mtime, reverse=True)
            if not folders:
                st.info("No snapshots generated yet.")
                return

            selected_folder = st.selectbox("Run", folders, format_func=lambda p: p.name)
            st.caption(f"Path: {selected_folder}")
            params_path = selected_folder / "run_params.json"
            params = {}
            if params_path.exists():
                try:
                    params = json.loads(params_path.read_text(encoding="utf-8"))
                except Exception:
                    params = {}

            if params:
                metric_cols = responsive_columns(responsive, desktop=4, tablet=2, phone=1)
                with metric_cols[0]:
                    st.metric("Start", str(params.get("start_date", "")) or "-")
                with metric_cols[1 % len(metric_cols)]:
                    st.metric("End", str(params.get("end_date", "")) or "-")
                with metric_cols[2 % len(metric_cols)]:
                    st.metric("Mode", str(params.get("data_mode", "")) or "-")
                with metric_cols[3 % len(metric_cols)]:
                    st.metric("Branches", str(len(params.get("branches", []) or [])))
                ga = str(params.get("generated_at", "") or "").strip()
                if ga:
                    st.caption(f"Generated at: {ga}")

            section_dirs = [p for p in selected_folder.iterdir() if p.is_dir()]
            section_dirs = sorted(section_dirs, key=lambda p: p.name)
            section_labels = ["(root)"] + [p.name for p in section_dirs]
            selected_section = st.selectbox("Section", section_labels)
            browse_dir = selected_folder if selected_section == "(root)" else (selected_folder / selected_section)

            try:
                all_files = [p for p in browse_dir.rglob("*") if p.is_file()]
                images_count = sum(1 for p in all_files if p.suffix.lower() == ".png")
                csv_count = sum(1 for p in all_files if p.suffix.lower() == ".csv")
                json_count = sum(1 for p in all_files if p.suffix.lower() == ".json")
                file_metric_cols = responsive_columns(responsive, desktop=3, tablet=2, phone=1)
                with file_metric_cols[0]:
                    st.metric("PNGs", str(images_count))
                with file_metric_cols[1 % len(file_metric_cols)]:
                    st.metric("CSVs", str(csv_count))
                with file_metric_cols[2 % len(file_metric_cols)]:
                    st.metric("JSON", str(json_count))
            except Exception:
                pass

            name_filter = st.text_input("Filter files", value="", placeholder="Type to filter by filename…")
            files = [p for p in browse_dir.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".csv", ".json"}]
            files = sorted(files, key=lambda p: p.name)
            if name_filter.strip():
                nf = name_filter.strip().lower()
                files = [p for p in files if nf in p.name.lower()]

            if not files:
                st.info("No files found for this section/filter.")
                return

            chosen = st.selectbox("File", files, format_func=lambda p: p.name)
            st.caption(f"Selected: {chosen.name}")
            if chosen.suffix.lower() == ".png":
                st.image(str(chosen), use_container_width=True)
                st.download_button("Download PNG", data=chosen.read_bytes(), file_name=chosen.name, mime="image/png")
            elif chosen.suffix.lower() == ".csv":
                try:
                    df = pd.read_csv(chosen)
                    st.dataframe(df, width="stretch", hide_index=True, height=clamp_dataframe_height(responsive, desktop=520, tablet=400, phone=300, kind="tall"))
                except Exception as e:
                    st.error(f"Could not read CSV: {e}")
                st.download_button("Download CSV", data=chosen.read_bytes(), file_name=chosen.name, mime="text/csv")
            elif chosen.suffix.lower() == ".json":
                try:
                    st.json(json.loads(chosen.read_text(encoding="utf-8")))
                except Exception as e:
                    st.error(f"Could not read JSON: {e}")
                st.download_button("Download JSON", data=chosen.read_bytes(), file_name=chosen.name, mime="application/json")


def main() -> None:
    pd.set_option("future.no_silent_downcasting", True)

    st.set_page_config(
        page_title="HNS Sales Dashboard (Modular)",
        page_icon="HNS",
        layout="wide",
        initial_sidebar_state=infer_initial_sidebar_state(),
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
    responsive = get_responsive_context()
    st.session_state["responsive_tier"] = responsive.tier

    auth_slot = st.empty()
    if not st.session_state.get("authenticated", False):
        with auth_slot.container():
            authed = authenticate_user()
        if not authed:
            st.stop()
        auth_slot.empty()

    if check_session_timeout():
        logout_user()
        st.warning("Session timed out. Please log in again.")
        st.stop()
    update_activity()

    user_record = st.session_state.get("user", {}) or {}
    role = str(user_record.get("role", "user")).lower()

    navbar_config = app_config.AppConfig.NAVBAR_ITEMS

    st.sidebar.title("Dashboard Controls")
    render_layout_mode_control(st.sidebar)

    if st.sidebar.button("Logout", key="dashboard_logout_btn", width="stretch"):
        logout_user()
        st.rerun()

    if st.sidebar.checkbox("Dark Mode", value=st.session_state.get("dark_mode", False), key="dashboard_dark_mode_toggle"):
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
        key="dashboard_date_preset",
    )

    # Presets come from `get_date_presets`; do not override them here.
    # The selected start/end are also used by snapshot generation, so this must remain consistent.
    start_date, end_date = get_date_presets(date_preset)

    if date_preset == "Custom":
        start_date = st.sidebar.date_input("Start Date", start_date, key="dashboard_start_date")
        end_date = st.sidebar.date_input("End Date", end_date, key="dashboard_end_date")
    else:
        st.sidebar.caption(f"Using preset range: {start_date} → {end_date}")

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
        key="dashboard_data_mode",
    )

    branch_name_map = {int(k): str(v) for k, v in BRANCH_NAMES.items()}
    df_all_branches = get_cached_all_branches_lookup()
    if df_all_branches is not None and not df_all_branches.empty:
        try:
            db_branch_name_map = {
                int(row.shop_id): str(row.shop_name)
                for row in df_all_branches.itertuples(index=False)
                if pd.notna(row.shop_id)
            }
            if db_branch_name_map:
                branch_name_map = db_branch_name_map
        except Exception:
            pass
    if not branch_name_map:
        branch_name_map = {int(b): f"Branch {b}" for b in SELECTED_BRANCH_IDS}

    allowed_branches = user_record.get("allowed_branches", SELECTED_BRANCH_IDS)
    if allowed_branches == "all":
        allowed_branches = sorted(branch_name_map.keys())
    else:
        try:
            allowed_branches = [int(b) for b in allowed_branches]
        except Exception:
            allowed_branches = list(SELECTED_BRANCH_IDS)
        if branch_name_map:
            allowed_branches = [b for b in allowed_branches if b in branch_name_map]
        if not allowed_branches:
            allowed_branches = sorted(branch_name_map.keys()) if branch_name_map else list(SELECTED_BRANCH_IDS)

    selected_branches: List[int] = st.sidebar.multiselect(
        "Select Branches",
        options=allowed_branches,
        default=allowed_branches,
        key="dashboard_selected_branches",
        format_func=lambda x: branch_name_map.get(int(x), f"Branch {x}"),
    )

    if not selected_branches:
        st.sidebar.warning("Please select at least one branch")
        st.stop()

    st.sidebar.markdown("---")
    if add_vertical_space is not None:
        add_vertical_space(1)
    st.sidebar.header("Target Period")
    target_year = st.sidebar.number_input("Year", 2000, 2100, 2026, 1, key="dashboard_target_year")
    target_month = st.sidebar.selectbox(
        "Month", range(1, 13),
        index=datetime.now().month - 1,
        key="dashboard_target_month",
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
        auto_refresh = st.checkbox("Auto", value=st.session_state.auto_refresh, key="dashboard_auto_refresh")
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh

    warm_cache = st.sidebar.checkbox(
        "Warm Cache in Background",
        value=st.session_state.get("warm_cache_enabled", False),
        key="dashboard_warm_cache",
        help="Preloads common queries after filters are set. If UI becomes unstable/blank, turn this off.",
    )
    st.session_state.warm_cache_enabled = warm_cache
    if warm_cache:
        warm_sig = f"{start_date_str}:{end_date_str}:{sorted(selected_branches)}:{data_mode}:{target_year}:{target_month}"
        if st.session_state.get("warm_cache_signature") != warm_sig:
            st.session_state.warm_cache_signature = warm_sig
            def _warm():
                warm_up_caches(start_date_str, end_date_str, selected_branches, data_mode, target_year, target_month, include_heavy=False)
            t = threading.Thread(target=_warm, daemon=True)
            t.start()

    if st.sidebar.button("Generate Snapshots", width="stretch", key="main_sidebar_snapshots"):
        with st.spinner("Generating snapshots..."):
            try:
                from daily_branch_snapshots import generate_snapshots
                snap_settings = load_snapshot_settings()
                out_dir = generate_snapshots(
                    start_date=start_date_str, end_date=end_date_str,
                    target_year=target_year, target_month=target_month,
                    branches=selected_branches, data_mode=data_mode,
                    output_dir="HNS_Deshboard/snapshots",
                    enabled_sections=snap_settings,
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

    allowed_branch_ids_normalized = [int(b) for b in allowed_branches]
    db_lookup = get_cached_branch_lookup(allowed_branch_ids_normalized)
    branch_name_map = {int(k): str(v) for k, v in BRANCH_NAMES.items()}
    if db_lookup is not None and not db_lookup.empty:
        try:
            db_map = {
                int(row.shop_id): str(row.shop_name)
                for row in db_lookup.itertuples(index=False)
                if pd.notna(row.shop_id)
            }
            branch_name_map.update(db_map)
        except Exception:
            pass

    if not branch_name_map:
        branch_name_map = {int(b): f"Branch {b}" for b in selected_branches}

    selected_set = set(int(b) for b in selected_branches)
    allowed_set = set(allowed_branch_ids_normalized)
    is_all_allowed_selected = selected_set == allowed_set

    branch_labels = [branch_name_map.get(int(b), f"Branch {b}") for b in selected_branches]
    title_text = "HNS Sales Dashboard" if is_all_allowed_selected else f"HNS Sales Dashboard: {', '.join(branch_labels)}"

    if responsive.is_phone:
        mobile_layout_default = st.session_state.get("mobile_responsive_view_mode", st.session_state.get("responsive_view_mode", "Auto"))
        if mobile_layout_default not in {"Auto", "Desktop", "Tablet", "Phone"}:
            mobile_layout_default = "Auto"
        if "mobile_date_preset" not in st.session_state:
            st.session_state["mobile_date_preset"] = st.session_state.get("dashboard_date_preset", date_preset)
        if "mobile_selected_branches" not in st.session_state:
            st.session_state["mobile_selected_branches"] = list(selected_branches)
        if "mobile_data_mode" not in st.session_state:
            st.session_state["mobile_data_mode"] = data_mode
        if "mobile_target_year" not in st.session_state:
            st.session_state["mobile_target_year"] = int(target_year)
        if "mobile_target_month" not in st.session_state:
            st.session_state["mobile_target_month"] = int(target_month)
        if "mobile_dark_mode" not in st.session_state:
            st.session_state["mobile_dark_mode"] = bool(st.session_state.get("dark_mode", False))
        if "mobile_auto_refresh" not in st.session_state:
            st.session_state["mobile_auto_refresh"] = bool(st.session_state.get("auto_refresh", False))
        if "mobile_warm_cache" not in st.session_state:
            st.session_state["mobile_warm_cache"] = bool(st.session_state.get("warm_cache_enabled", False))
        if "mobile_responsive_view_mode" not in st.session_state:
            st.session_state["mobile_responsive_view_mode"] = mobile_layout_default

        with st.expander("Filters & Controls", expanded=False):
            st.caption(f"Detected layout: {responsive.tier.title()} ({responsive.source.replace('_', ' ')})")
            mobile_layout_mode = st.selectbox(
                "Layout Mode",
                ["Auto", "Desktop", "Tablet", "Phone"],
                index=["Auto", "Desktop", "Tablet", "Phone"].index(mobile_layout_default),
                key="mobile_responsive_view_mode",
            )
            mobile_dark_mode = st.checkbox("Dark Mode", value=st.session_state["mobile_dark_mode"], key="mobile_dark_mode")

            mobile_date_preset = st.selectbox(
                "Quick Select",
                ["Custom", "Today", "Yesterday", "This Week", "Last Week", "This Month", "Last Month", "This Quarter", "This Year"],
                index=["Custom", "Today", "Yesterday", "This Week", "Last Week", "This Month", "Last Month", "This Quarter", "This Year"].index(st.session_state["mobile_date_preset"]),
                key="mobile_date_preset",
            )
            mobile_start_date, mobile_end_date = get_date_presets(mobile_date_preset)
            if mobile_date_preset == "Custom":
                mobile_start_date = st.date_input("Start Date", value=start_date, key="mobile_start_date")
                mobile_end_date = st.date_input("End Date", value=end_date, key="mobile_end_date")
            else:
                st.caption(f"Using preset range: {mobile_start_date} -> {mobile_end_date}")

            mobile_data_mode = st.radio(
                "Data Mode",
                ["Filtered", "Unfiltered"],
                index=0 if st.session_state.get("mobile_data_mode", data_mode) == "Filtered" else 1,
                key="mobile_data_mode",
                help="Filtered mode excludes blocked customers and comments",
            )
            mobile_selected_branches = st.multiselect(
                "Select Branches",
                options=allowed_branches,
                default=[b for b in st.session_state["mobile_selected_branches"] if b in allowed_branches] or allowed_branches,
                key="mobile_selected_branches",
                format_func=lambda x: branch_name_map.get(int(x), f"Branch {x}"),
            )
            mobile_target_year = st.number_input("Year", 2000, 2100, int(st.session_state["mobile_target_year"]), 1, key="mobile_target_year")
            mobile_target_month = st.selectbox(
                "Month",
                range(1, 13),
                index=int(st.session_state["mobile_target_month"]) - 1,
                key="mobile_target_month",
                format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            )
            mobile_auto_refresh = st.checkbox("Auto Refresh", value=st.session_state["mobile_auto_refresh"], key="mobile_auto_refresh")
            mobile_warm_cache = st.checkbox("Warm Cache in Background", value=st.session_state["mobile_warm_cache"], key="mobile_warm_cache")

            apply_col, refresh_col = st.columns(2)
            with apply_col:
                if st.button("Apply Mobile Filters", key="mobile_apply_filters", width="stretch"):
                    if mobile_date_preset == "Custom":
                        st.session_state["dashboard_start_date"] = mobile_start_date
                        st.session_state["dashboard_end_date"] = mobile_end_date
                    st.session_state["responsive_view_mode"] = mobile_layout_mode
                    st.session_state["dashboard_dark_mode_toggle"] = mobile_dark_mode
                    st.session_state["dashboard_date_preset"] = mobile_date_preset
                    st.session_state["dashboard_data_mode"] = mobile_data_mode
                    st.session_state["dashboard_selected_branches"] = mobile_selected_branches or list(allowed_branches)
                    st.session_state["dashboard_target_year"] = int(mobile_target_year)
                    st.session_state["dashboard_target_month"] = int(mobile_target_month)
                    st.session_state["dashboard_auto_refresh"] = mobile_auto_refresh
                    st.session_state["dashboard_warm_cache"] = mobile_warm_cache
                    st.session_state["dark_mode"] = mobile_dark_mode
                    st.session_state["auto_refresh"] = mobile_auto_refresh
                    st.session_state["warm_cache_enabled"] = mobile_warm_cache
                    st.rerun()
            with refresh_col:
                if st.button("Refresh Now", key="mobile_refresh_btn", width="stretch"):
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

    responsive = get_responsive_context()
    st.session_state["responsive_tier"] = responsive.tier

    st.title(title_text)
    st.caption(f"Period: {start_date_str} to {end_date_str} | Mode: {data_mode}")

    user_record = st.session_state.get("user", {}) or {}
    role = str(user_record.get("role", "user")).lower()
    allowed_tabs = user_record.get("allowed_tabs", "all")
    allowed_tables = user_record.get("allowed_tables", "all")
    if role == "admin":
        allowed_tabs = "all"

    df_line_item = None

    def _nav_key_from_label(label: str) -> str:
        # Keep this aligned with components/new_navbar.py normalization.
        if label == "Category Filters & Coverage":
            return "category_filters_&_coverage"
        if label == "Admin & Snapshots":
            return "admin_snapshots"
        return label.lower().replace(" ", "_").replace("&", "")

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

    def _render_database_health_diagnostics():
        DatabaseHealthDiagnosticsTab(start_date_str, end_date_str, selected_branches, data_mode).render()

    def _render_web_items_export():
        WebItemsExportTab().render()

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
        current_user = st.session_state.get("user", {}) or {}
        current_role = str(current_user.get("role", "user")).lower()
        if current_role != "admin":
            st.error("Admin & Snapshots is admin-only.")
            return
        render_user_management_tab(branch_name_map)


    tab_map = {
        'overview': _render_overview,
        'order_takers': _render_order_takers,
        'chef_sales': _render_chef_sales,
        'chef_targets': _render_chef_targets,
        'food_panda': _render_food_panda,
        'ot_targets': _render_ot_targets,
        'qr_commission': _render_qr_commission,
        'khadda_diagnostics': _render_khadda_diagnostics,
        'database_health_diagnostics': _render_database_health_diagnostics,
        'web_items_export': _render_web_items_export,
        'material_cost_commission': _render_material_cost,
        'trends_analytics': _render_trends_analytics,
        'ramzan_deals': _render_ramzan_deals,
        'category_filters_&_coverage': _render_category_coverage,
        'pivot_tables': _render_pivot_tables,
    }
    # Support legacy/double-underscore key from navbar normalization
    tab_map.setdefault('trends__analytics', _render_trends_analytics)
    # Also support mapping by label (defensive) in case something stores labels in session.
    tab_map.setdefault("Admin & Snapshots", _render_user_management)
    tab_map.setdefault("admin_snapshots", _render_user_management)
    tab_map.setdefault("User Management", _render_user_management)  # legacy label
    tab_map.setdefault("user_management", _render_user_management)  # legacy key

    # Render a single active tab only (Streamlit reruns on any widget change; this avoids
    # recomputing the entire dashboard across all tabs on every interaction).
    active_key = NewNavbarComponent(navbar_config).render(user_record=user_record)

    normalized_active_key = active_key
    try:
        if isinstance(active_key, str):
            normalized_active_key = _nav_key_from_label(active_key)
    except Exception:
        normalized_active_key = active_key

    render_fn = (
        tab_map.get(active_key)
        or (tab_map.get(active_key.replace("&", "")) if isinstance(active_key, str) else None)
        or tab_map.get(normalized_active_key)
        or _render_overview
    )
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
