import streamlit as st
from typing import Dict

from modules.responsive import get_responsive_context

class NewNavbarComponent:
    def __init__(self, config: Dict):
        self.config = config
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = 'overview'

    def render(self, user_record: Dict = None) -> str:
        responsive = get_responsive_context()
        tabs_config = self.config.get('tabs', {})
        if user_record and str(user_record.get('role', 'user')).lower() == 'admin':
            user_allowed_tabs = 'all'
        else:
            user_allowed_tabs = user_record.get('allowed_tabs', 'all') if user_record else 'all'
        hidden_labels = {"Indoge-First Diagnostics", "Multi-Signal Match"}

        alias_allowed = {
            "Admin & Snapshots": {"User Management"},
        }

        display_tabs = []
        for label, info in tabs_config.items():
            if label in hidden_labels:
                continue
            if info.get('admin_only', False) and (not user_record or user_record.get('role', 'user').lower() != 'admin'):
                continue
            allowed_by_label = user_allowed_tabs == 'all' or label in user_allowed_tabs
            if not allowed_by_label and isinstance(user_allowed_tabs, list):
                aliases = alias_allowed.get(label, set())
                if aliases and any(a in user_allowed_tabs for a in aliases):
                    allowed_by_label = True

            if allowed_by_label:
                if label == "Category Filters & Coverage":
                    key = "category_filters_&_coverage"
                elif label == "Admin & Snapshots":
                    key = "admin_snapshots"
                else:
                    key = label.lower().replace(' ', '_').replace('&', '')
                if any(t['key'] == key for t in display_tabs):
                    continue
                display_tabs.append({
                    'label': label,
                    'key': key
                })

        if display_tabs:
            valid_keys = [t["key"] for t in display_tabs]
            if st.session_state.get('active_tab') not in valid_keys:
                st.session_state.active_tab = valid_keys[0]

        labels = [t["label"] for t in display_tabs]
        keys = [t["key"] for t in display_tabs]

        default_index = 0
        if st.session_state.active_tab in keys:
            default_index = keys.index(st.session_state.active_tab)

        if responsive.is_phone:
            selected = st.selectbox(
                "Navigation",
                labels,
                index=default_index,
                key="hns_nav_select",
            )
        else:
            selected = st.radio(
                "Navigation",
                labels,
                index=default_index,
                horizontal=not responsive.is_tablet,
                label_visibility="collapsed",
                key="hns_nav_radio",
            )

        for t in display_tabs:
            if t["label"] == selected:
                st.session_state.active_tab = t["key"]
                break

        return st.session_state.active_tab
