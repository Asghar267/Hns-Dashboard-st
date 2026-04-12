"""
Responsive layout helpers for the Streamlit dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import streamlit as st


_PHONE_HINTS = (
    "iphone",
    "android mobile",
    "mobile",
    "windows phone",
    "opera mini",
    "blackberry",
    "mobi",
)
_TABLET_HINTS = (
    "ipad",
    "tablet",
    "kindle",
    "silk",
    "playbook",
    "sm-t",
    "nexus 7",
    "nexus 10",
)


@dataclass(frozen=True)
class ResponsiveContext:
    tier: str
    user_agent: str
    source: str

    @property
    def is_phone(self) -> bool:
        return self.tier == "phone"

    @property
    def is_tablet(self) -> bool:
        return self.tier == "tablet"

    @property
    def is_desktop(self) -> bool:
        return self.tier == "desktop"

    @property
    def initial_sidebar_state(self) -> str:
        return "collapsed" if self.is_phone else "expanded"


def _get_headers() -> dict[str, Any]:
    try:
        headers = getattr(st.context, "headers", None)
    except Exception:
        headers = None

    if headers is None:
        return {}
    if hasattr(headers, "to_dict"):
        try:
            return dict(headers.to_dict())
        except Exception:
            pass
    try:
        return dict(headers)
    except Exception:
        return {}


def _detect_tier_from_user_agent(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if not ua:
        return "desktop"
    if any(token in ua for token in _TABLET_HINTS):
        return "tablet"
    if "android" in ua and "mobile" not in ua:
        return "tablet"
    if any(token in ua for token in _PHONE_HINTS):
        return "phone"
    return "desktop"


def get_responsive_context() -> ResponsiveContext:
    override = str(st.session_state.get("responsive_view_mode", "Auto")).strip().lower()
    if override in {"desktop", "tablet", "phone"}:
        return ResponsiveContext(tier=override, user_agent="", source="override")

    headers = _get_headers()
    user_agent = str(
        headers.get("User-Agent")
        or headers.get("user-agent")
        or headers.get("X-User-Agent")
        or ""
    )
    detected = _detect_tier_from_user_agent(user_agent)
    return ResponsiveContext(tier=detected, user_agent=user_agent, source="user_agent")


def infer_initial_sidebar_state() -> str:
    return get_responsive_context().initial_sidebar_state


def render_layout_mode_control(ui: Any, key: str = "responsive_view_mode") -> str:
    options = ["Auto", "Desktop", "Tablet", "Phone"]
    current = str(st.session_state.get(key, "Auto"))
    if current not in options:
        current = "Auto"
    return ui.selectbox(
        "Layout Mode",
        options=options,
        index=options.index(current),
        key=key,
        help="Auto uses the browser device hint. Override it to preview desktop/tablet/phone layouts.",
    )


def responsive_column_count(
    ctx: ResponsiveContext,
    desktop: int,
    tablet: int | None = None,
    phone: int = 1,
) -> int:
    tablet = desktop if tablet is None else tablet
    if ctx.is_phone:
        return max(1, phone)
    if ctx.is_tablet:
        return max(1, tablet)
    return max(1, desktop)


def responsive_columns(
    ctx: ResponsiveContext,
    desktop: int,
    tablet: int | None = None,
    phone: int = 1,
    gap: str = "small",
):
    return st.columns(responsive_column_count(ctx, desktop, tablet=tablet, phone=phone), gap=gap)


def clamp_dataframe_height(
    ctx: ResponsiveContext,
    desktop: int | None = None,
    tablet: int | None = None,
    phone: int | None = None,
    *,
    kind: str = "default",
) -> int | None:
    presets = {
        "compact": (220, 220, 200),
        "default": (420, 340, 280),
        "tall": (520, 420, 320),
        "full": (620, 480, 360),
    }
    base_desktop, base_tablet, base_phone = presets.get(kind, presets["default"])
    desktop = base_desktop if desktop is None else desktop
    tablet = base_tablet if tablet is None else tablet
    phone = base_phone if phone is None else phone
    if ctx.is_phone:
        return phone
    if ctx.is_tablet:
        return tablet
    return desktop


def pick_columns_for_tier(
    ctx: ResponsiveContext,
    available: Sequence[str],
    *,
    desktop: Iterable[str] | None = None,
    tablet: Iterable[str] | None = None,
    phone: Iterable[str] | None = None,
) -> list[str]:
    allowed = list(available)

    def _clean(cols: Iterable[str] | None) -> list[str]:
        if cols is None:
            return allowed
        return [c for c in cols if c in allowed]

    if ctx.is_phone:
        selected = _clean(phone or tablet or desktop)
    elif ctx.is_tablet:
        selected = _clean(tablet or desktop)
    else:
        selected = _clean(desktop)
    return selected or allowed


def apply_plotly_responsive_layout(
    fig: Any,
    ctx: ResponsiveContext,
    *,
    desktop_height: int = 500,
    tablet_height: int = 420,
    phone_height: int = 340,
) -> Any:
    height = desktop_height
    if ctx.is_tablet:
        height = tablet_height
    if ctx.is_phone:
        height = phone_height

    legend = dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
    margins = dict(l=30, r=30, t=50, b=30)
    if ctx.is_phone:
        legend = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        margins = dict(l=20, r=20, t=45, b=20)
    elif ctx.is_tablet:
        margins = dict(l=24, r=24, t=48, b=24)

    try:
        fig.update_layout(height=height, legend=legend, margin=margins)
    except Exception:
        return fig
    return fig
