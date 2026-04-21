"""
Generate daily branch-wise snapshot PNGs for WhatsApp sharing.

Snapshots generated:
1) Branch performance cards (Current Sales / Remaining / Target / Achievement)
2) All Products by Branch (separate file per branch, paginated)
3) Employee-wise Totals (No Total Sales / Candelahns) by branch
4) Ramzan Deals:
   - Branch-wise Sales (separate file per branch, paginated)
   - Product-wise Overall Sales
5) Material Cost Commission:
   - Branch Summary
   - Employee Summary
   - Product-wise by Branch
   - Product-wise Overall
   - Detailed Analysis
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
import pandas as pd
import numpy as np
import concurrent.futures
import matplotlib
import matplotlib.patches as patches
matplotlib.use('Agg') # Faster headless rendering
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from modules.config import BRANCH_NAMES, RAMZAN_DEALS_PRODUCT_IDS, SELECTED_BRANCH_IDS
from modules.database import (
    get_cached_branch_summary,
    get_cached_line_items,
    get_cached_ramzan_deals_sales,
    get_cached_ramzan_product_master,
    get_cached_targets,
    placeholders,
    pool,
)
from modules.material_cost_commission import (
    get_branch_material_cost_summary,
    get_branch_product_material_cost_summary,
    get_employee_material_cost_summary,
    get_product_material_cost_summary,
)
from services.qr_commission_service import QRCommissionService
from modules.blink_reporting import prepare_blink_orders
from modules.qr_business_toggles import QR_TOGGLES


def format_currency(value: float) -> str:
    return f"PKR {float(value):,.0f}"


def as_int_list(values: Sequence[int]) -> List[int]:
    return [int(v) for v in values]


def month_bounds(year: int, month: int) -> tuple[date, date]:
    first = date(year, month, 1)
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    return first, (nxt - pd.Timedelta(days=1)).date()


def ensure_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)
    return out


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def save_table_dump(df: pd.DataFrame, path: Path) -> None:
    """Save a CSV dump of the exact data used to render a snapshot (debug/traceability)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_csv(path, index=False, encoding="utf-8-sig")
    except Exception:
        # Best-effort; never fail snapshot generation because of debug dump.
        pass


def table_image(
    df: pd.DataFrame,
    title: str,
    out_path: Path,
    rows_per_page: int = 32,
    subtitle: Optional[str] = None,
) -> List[Path]:
    saved: List[Path] = []
    if df.empty:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = Figure(figsize=(15, 3.5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.6, title, ha="center", va="center", fontsize=20, weight="bold", color="#2C3E50")
        ax.text(0.5, 0.35, "No data available.", ha="center", va="center", fontsize=14, color="#7F8C8D", style='italic')
        if subtitle:
            ax.text(0.5, 0.15, subtitle, ha="center", va="center", fontsize=12, color="#95A5A6")
        save_figure(fig, out_path)
        return [out_path]

    pages = max(1, (len(df) + rows_per_page - 1) // rows_per_page)
    for page in range(pages):
        start = page * rows_per_page
        chunk = df.iloc[start:start + rows_per_page].copy()
        nrows = len(chunk)
        # Increase figure height multiplier to accommodate larger text padding
        fig_h = max(4.0, 1.5 + (nrows * 0.45))
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = Figure(figsize=(15, fig_h))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.axis("off")
        
        # Add a subtle background color to figure
        fig.patch.set_facecolor('#F8F9F9')
        
        page_title = title if pages == 1 else f"{title} (Page {page + 1}/{pages})"
        ax.text(0.5, 1.08, page_title, ha="center", va="bottom", fontsize=20, weight="bold", color="#1A1A1A", transform=ax.transAxes)
        if subtitle:
            ax.text(0.5, 1.02, subtitle, ha="center", va="bottom", fontsize=13, color="#5F6368", transform=ax.transAxes)
            
        tbl = ax.table(
            cellText=chunk.values,
            colLabels=list(chunk.columns),
            cellLoc="left",
            colLoc="left",
            loc="center",
            bbox=[0, 0, 1, 0.98] 
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11)

        # Style colors - Premium Palette
        header_color = '#1A73E8' # Google Blue
        even_row_color = '#F8F9FA'
        odd_row_color = '#FFFFFF'
        edge_color = '#E8EAED'

        for (r, c), cell in tbl.get_celld().items():
            cell.set_edgecolor(edge_color)
            cell.set_linewidth(0.5)
            if r == 0:
                cell.set_text_props(weight="bold", color="white", fontsize=12)
                cell.set_facecolor(header_color)
                cell.PAD = 0.12
            else:
                cell.set_facecolor(even_row_color if r % 2 == 0 else odd_row_color)
                cell.set_text_props(color="#3C4043")
                cell.PAD = 0.12

            # Premium height
            cell.set_height(0.12)

        # Add footer
        ax.text(1.0, -0.05, "Generated by HNS Analytics Dashboard", ha="right", va="top", fontsize=9, color="#9AA0A6", style='italic', transform=ax.transAxes)

        page_path = out_path
        if pages > 1:
            page_path = out_path.with_name(f"{out_path.stem}_p{page + 1}{out_path.suffix}")
        save_figure(fig, page_path)
        saved.append(page_path)
    return saved


def _safe_filename(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in str(text))
    cleaned = "_".join(cleaned.strip().split())
    return cleaned.lower() or "unknown"


def render_branch_cards(
    df_cards: pd.DataFrame,
    out_path: Path,
    period_label: str,
) -> Path:
    df_cards = df_cards.copy().sort_values("shop_id")
    n = len(df_cards)
    cols = 2
    rows = max(1, (n + cols - 1) // cols)
    # Give cards a bit more vertical breathing room
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    fig = Figure(figsize=(15, max(4.5, rows * 4.0)))
    canvas = FigureCanvas(fig)
    axes = []
    for j in range(n):
        ax = fig.add_subplot(rows, cols, j + 1)
        axes.append(ax)
    fig.patch.set_facecolor('#F8F9F9')
    
    pass

    for i, ax in enumerate(axes):
        ax.axis("off")
        if i >= n:
            continue
            
        r = df_cards.iloc[i]
        title = f"{BRANCH_NAMES.get(int(r['shop_id']), r['shop_name'])}".upper()
        
        # Add subtle shadow
        shadow = patches.FancyBboxPatch(
            (0.045, 0.045), 0.92, 0.90,
            boxstyle="round,pad=0.04",
            fc="#E8EAED",
            ec="none",
            alpha=0.4,
            transform=ax.transAxes,
            zorder=1
        )
        ax.add_patch(shadow)

        rect = patches.FancyBboxPatch(
            (0.04, 0.05), 0.92, 0.90,
            boxstyle="round,pad=0.04",
            fc="#FFFFFF",
            ec="#DADCE0",
            lw=1.0,
            transform=ax.transAxes,
            zorder=2
        )
        ax.add_patch(rect)

        # Card Title
        ax.text(
            0.09, 0.86, title,
            va="top", ha="left", fontsize=18, weight="black", color="#1A73E8",
            transform=ax.transAxes,
            zorder=3
        )
        
        # Branch ID Badge
        ax.text(
            0.91, 0.86, f"ID: {int(r['shop_id'])}",
            va="top", ha="right", fontsize=10, weight="bold", color="white",
            bbox=dict(facecolor='#5F6368', edgecolor='none', boxstyle='round,pad=0.3'),
            transform=ax.transAxes,
            zorder=3
        )

        # Card Subtitle (Date)
        ax.text(
            0.09, 0.77, period_label,
            va="top", ha="left", fontsize=11, color="#70757A",
            transform=ax.transAxes,
            zorder=3
        )
        
        labels = ["CURRENT SALES", "MONTHLY TARGET", "REMAINING", "ACHIEVEMENT"]
        vals = [
            format_currency(r['total_Nt_amount']),
            format_currency(r['Monthly_Target']),
            format_currency(r['Remaining_Target']),
            f"{float(r['Achievement_%']):.1f}%"
        ]
        
        # Split into two columns within the card
        y_pos = 0.55
        for j, (lbl, val) in enumerate(zip(labels, vals)):
            col_offset = 0.09 if j % 2 == 0 else 0.53
            if j % 2 == 0 and j > 0:
                y_pos -= 0.28
                
            ax.text(col_offset, y_pos, lbl, va="top", ha="left", fontsize=10, weight="bold", color="#70757A", transform=ax.transAxes, zorder=3)
            
            # Achievement logic color
            ach_val = float(r['Achievement_%'])
            if lbl == "ACHIEVEMENT":
                val_color = "#1E8E3E" if ach_val >= 90 else "#F9AB00" if ach_val >= 70 else "#D93025"
            elif lbl == "REMAINING" and float(r['Remaining_Target']) <= 0:
                val_color = "#1E8E3E"
            else:
                val_color = "#202124"

            weight = "bold" if lbl in ["CURRENT SALES", "ACHIEVEMENT"] else "medium"
            ax.text(col_offset, y_pos - 0.07, val, va="top", ha="left", fontsize=17, weight="bold", color=val_color, transform=ax.transAxes, zorder=3)

    fig.suptitle("BRANCH PERFORMANCE SUMMARY", fontsize=24, weight="black", color="#202124", y=1.05)
    
    # Add main footer to the figure
    fig.text(0.95, 0.02, "", ha="right", fontsize=10, color="#9AA0A6", alpha=0.7)
    
    save_figure(fig, out_path)
    return out_path


def build_branch_performance(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    target_year: int,
    target_month: int,
) -> pd.DataFrame:
    df = get_cached_branch_summary(start_date, end_date, branch_ids, data_mode)
    df = ensure_numeric(df, ["shop_id", "total_Nt_amount"])
    branch_targets, _, _, _ = get_cached_targets(target_year, target_month)
    df["Monthly_Target"] = df["shop_id"].map(branch_targets).fillna(0.0).astype(float)

    # Merge FESTIVAL + FESTIVAL 2 same as dashboard cards.
    mask3 = df["shop_id"] == 3
    mask14 = df["shop_id"] == 14
    if mask3.any() and mask14.any():
        fest2_sales = df.loc[mask14, "total_Nt_amount"].sum()
        df.loc[mask3, "total_Nt_amount"] += fest2_sales
        df.loc[mask3, "shop_name"] = "FESTIVAL"
        df = df.loc[~mask14].copy()

    df["Remaining_Target"] = df["Monthly_Target"] - df["total_Nt_amount"]
    df["Achievement_%"] = df.apply(
        lambda x: (x["total_Nt_amount"] / x["Monthly_Target"] * 100.0) if x["Monthly_Target"] > 0 else 0.0,
        axis=1,
    )
    return df.sort_values("shop_id")


def build_all_products_by_branch(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
) -> pd.DataFrame:
    df = get_cached_line_items(start_date, end_date, branch_ids, data_mode)
    if df.empty:
        return pd.DataFrame(columns=["shop_id", "Branch", "Product", "Total Qty", "Total Sales"])
    df = df.rename(
        columns={
            "shop_name": "Branch",
            "product": "Product",
            "total_qty": "Total Qty",
            "total_line_value_incl_tax": "Total Sales",
        }
    )
    df = ensure_numeric(df, ["Total Qty", "Total Sales", "shop_id"])
    df = df.sort_values(["shop_id", "Total Sales"], ascending=[True, False])
    df["Total Qty"] = df["Total Qty"].map(lambda x: f"{x:,.0f}")
    df["Total Sales"] = df["Total Sales"].map(format_currency)
    return df[["shop_id", "Branch", "Product", "Total Qty", "Total Sales"]]


def build_khadda_diagnostics_snapshot(
    start_date: str,
    end_date: str,
    data_mode: str,
    commission_rate: float = 2.0,
) -> pd.DataFrame:
    """Build Khadda Diagnostics snapshot table (same columns as dashboard)."""
    qr_service = QRCommissionService()

    # QRCommissionService expects end_date to be inclusive.
    df_qr = qr_service.get_qr_commission_data(start_date, end_date, [2], data_mode)
    df_total_sales = qr_service.get_total_sales_data(start_date, end_date, [2], data_mode)
    df_blink_raw = qr_service.get_blink_raw_orders_for_qr_sales(start_date, end_date, [2], data_mode)
    df_merged = qr_service.process_qr_data(df_qr, df_blink_raw, commission_rate)

    if not df_merged.empty:
        blinkco_summary = (
            df_merged.groupby(["employee_id", "employee_name", "shop_id", "shop_name"], as_index=False)
            .agg(total_sales_blinkco=("total_sale", "sum"), total_transactions_blinkco=("sale_id", "count"))
        )
        tx_kh = df_merged.copy()
        tx_kh["employee_id"] = pd.to_numeric(tx_kh.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
        tx_kh["shop_id"] = pd.to_numeric(tx_kh.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
        tx_kh["Indoge_total_price"] = pd.to_numeric(tx_kh.get("Indoge_total_price", 0), errors="coerce").fillna(0.0)
        indoge_by_emp = tx_kh.groupby(["employee_id", "shop_id"], as_index=False).agg(
            indoge_blink_sales=("Indoge_total_price", "sum")
        )
    else:
        blinkco_summary = pd.DataFrame(
            columns=["employee_id", "employee_name", "shop_id", "shop_name", "total_sales_blinkco", "total_transactions_blinkco"]
        )
        indoge_by_emp = pd.DataFrame(columns=["employee_id", "shop_id", "indoge_blink_sales"])

    split_report = qr_service.get_split_report(df_total_sales, blinkco_summary, commission_rate)
    if split_report.empty:
        return pd.DataFrame()

    kh = split_report.copy()
    kh["employee_id"] = pd.to_numeric(kh.get("employee_id", 0), errors="coerce").fillna(0).astype(int)
    kh["shop_id"] = pd.to_numeric(kh.get("shop_id", 0), errors="coerce").fillna(0).astype(int)
    kh = kh[kh["shop_id"] == 2].copy()
    kh = kh.merge(indoge_by_emp, on=["employee_id", "shop_id"], how="left")
    kh["indoge_blink_sales"] = pd.to_numeric(kh.get("indoge_blink_sales", 0), errors="coerce").fillna(0.0)

    cand_blink = pd.to_numeric(kh.get("total_sales_blinkco", 0), errors="coerce")
    indoge_blink = pd.to_numeric(kh.get("indoge_blink_sales", 0), errors="coerce")
    both = pd.concat([cand_blink, indoge_blink], axis=1)
    denom_match = both.max(axis=1).replace(0, pd.NA)
    numer_match = both.min(axis=1)
    kh["blink_match_pct"] = ((numer_match / denom_match) * 100.0).astype("Float64").round(2)
    kh["blink_match_ok_50pct"] = kh["blink_match_pct"] >= 50.0

    # Format for snapshot
    kh = kh.sort_values("total_sales_without_blinkco", ascending=False).reset_index(drop=True)
    kh_disp = kh.copy()
    kh_disp["blink_match_pct"] = kh_disp["blink_match_pct"].map(lambda x: "" if pd.isna(x) else f"{float(x):.2f}%")
    for col in [
        "total_sales_all",
        "total_sales_blinkco",
        "indoge_blink_sales",
        "total_sales_without_blinkco",
        "commission_total_sales",
        "commission_blinkco_sales",
        "commission_without_blinkco_sales",
    ]:
        if col in kh_disp.columns:
            kh_disp[col] = kh_disp[col].map(format_currency)

    return kh_disp[
        [
            "shop_id",
            "employee_code",
            "employee_name",
            "shop_name",
            "total_transactions_all",
            "total_transactions_blinkco",
            "total_transactions_without_blinkco",
            "total_sales_all",
            "total_sales_blinkco",
            "indoge_blink_sales",
            "total_sales_without_blinkco",
            "blink_match_pct",
            "blink_match_ok_50pct",
            "commission_total_sales",
            "commission_blinkco_sales",
            "commission_without_blinkco_sales",
        ]
    ]


def build_khadda_non_blinkco_employee_snapshot(
    start_date: str,
    end_date: str,
    data_mode: str,
    commission_rate: float = 2.0,
) -> pd.DataFrame:
    """Employee summary for Khadda non-Blinkco POS (with + without external_ref_id combined)."""
    from modules.config import BLOCKED_COMMENTS, BLOCKED_NAMES

    conn = pool.get_connection("candelahns")
    q = """
    SELECT
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COUNT(DISTINCT s.sale_id) AS transaction_count,
        SUM(s.Nt_amount) AS total_sale
    FROM tblSales s
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < DATEADD(DAY, 1, ?)
      AND s.shop_id = 2
      AND (s.external_ref_type IS NULL OR s.external_ref_type <> 'Blinkco order')
    """
    params: List = [start_date, end_date]
    if data_mode == "Filtered":
        if BLOCKED_NAMES:
            q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            q += (
                f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                f" OR s.Additional_Comments IS NULL)"
            )
            params.extend(BLOCKED_COMMENTS)
    q += """
    GROUP BY
        s.shop_id, sh.shop_name,
        COALESCE(e.shop_employee_id, 0),
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
        COALESCE(e.field_name, 'Online/Unassigned')
    ORDER BY total_sale DESC
    """
    df = pd.read_sql(q, conn, params=params)
    if df.empty:
        return df
    df["total_sale"] = pd.to_numeric(df.get("total_sale", 0), errors="coerce").fillna(0.0)
    df["transaction_count"] = pd.to_numeric(df.get("transaction_count", 0), errors="coerce").fillna(0).astype(int)
    df["commission"] = df["total_sale"] * (commission_rate / 100.0)
    return df


def build_khadda_combined_employee_snapshot(
    end_date: str,
    data_mode: str,
    include_unassigned: bool = False,
    commission_rate: float = 2.0,
) -> pd.DataFrame:
    """Combined employee summary: fixed <=20% no-ref (1–10 Mar) + post-cutoff QR to end_date."""
    qr_service = QRCommissionService()
    fixed_start = "2026-03-01"
    # Fixed cutoff: include 1–11 Mar in no-ref <=20% logic
    cutoff_dt = pd.to_datetime("2026-03-12 00:00:00")
    fixed_end_date = "2026-03-11"

    df_non = qr_service.get_non_blinkco_sales_transactions(fixed_start, fixed_end_date, [2], data_mode)
    if df_non is None or df_non.empty:
        fixed_sum = pd.DataFrame(columns=["shop_id", "shop_name", "employee_id", "employee_code", "employee_name", "tx_fixed", "sales_fixed"])
    else:
        df_non["external_ref_id"] = df_non["external_ref_id"].astype(str).str.strip().replace("None", "")
        no_ref = df_non[df_non["external_ref_id"] == ""].copy()
        if not include_unassigned:
            no_ref = no_ref[no_ref["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()

        raw = qr_service.get_blink_raw_orders(fixed_start, fixed_end_date)
        within_20 = pd.DataFrame()
        if raw is not None and not raw.empty and not no_ref.empty:
            raw_prep = raw[["BlinkOrderId", "OrderJson", "CreatedAt"]].copy()
            raw_prep = prepare_blink_orders(raw_prep)
            raw_prices = pd.to_numeric(raw_prep.get("Indoge_total_price", 0), errors="coerce").dropna()
            raw_prices = raw_prices[raw_prices > 0].astype(float)
            if not raw_prices.empty:
                raw_prices_sorted = np.sort(raw_prices.values)

                def _nearest_price(x: float) -> float:
                    idx = np.searchsorted(raw_prices_sorted, x, side="left")
                    if idx == 0:
                        return float(raw_prices_sorted[0])
                    if idx >= len(raw_prices_sorted):
                        return float(raw_prices_sorted[-1])
                    prev_v = raw_prices_sorted[idx - 1]
                    next_v = raw_prices_sorted[idx]
                    return float(prev_v if abs(x - prev_v) <= abs(x - next_v) else next_v)

                no_ref["total_sale"] = pd.to_numeric(no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                no_ref["closest_indoge_price"] = no_ref["total_sale"].apply(_nearest_price)
                no_ref["diff_pct"] = (
                    (no_ref["total_sale"] - no_ref["closest_indoge_price"]).abs()
                    / no_ref["total_sale"].replace(0, pd.NA) * 100.0
                )
                within_20 = no_ref[no_ref["diff_pct"] <= 20.0].copy()

        within_20["total_sale"] = pd.to_numeric(within_20.get("total_sale", 0), errors="coerce").fillna(0.0)
        fixed_sum = (
            within_20.groupby(
                ["shop_id", "shop_name", "employee_id", "employee_code", "employee_name"],
                as_index=False
            )
            .agg(tx_fixed=("sale_id", "count"), sales_fixed=("total_sale", "sum"))
        )

    post_start = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
    qr_post = qr_service.get_qr_commission_data(post_start, end_date, [2], data_mode)
    if qr_post is None or qr_post.empty:
        post_sum = pd.DataFrame(columns=["shop_id", "shop_name", "employee_id", "employee_code", "employee_name", "tx_post", "sales_post"])
    else:
        # Defensive filter (ensure inclusive end_date and post_start in case of DB quirks)
        qr_post["sale_date"] = pd.to_datetime(qr_post.get("sale_date"), errors="coerce")
        post_start_dt = pd.to_datetime(post_start)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        qr_post = qr_post[(qr_post["sale_date"] >= post_start_dt) & (qr_post["sale_date"] < end_dt)].copy()
        qr_post["external_ref_id"] = qr_post["external_ref_id"].astype(str).str.strip().replace("None", "")
        qr_post = qr_post[qr_post["external_ref_id"] != ""].copy()
        if not include_unassigned:
            qr_post = qr_post[qr_post["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
        qr_post["total_sale"] = pd.to_numeric(qr_post.get("total_sale", 0), errors="coerce").fillna(0.0)
        post_sum = (
            qr_post.groupby(
                ["shop_id", "shop_name", "employee_id", "employee_code", "employee_name"],
                as_index=False
            )
            .agg(tx_post=("sale_id", "count"), sales_post=("total_sale", "sum"))
        )

    combined = pd.merge(
        fixed_sum,
        post_sum,
        on=["shop_id", "shop_name", "employee_id", "employee_code", "employee_name"],
        how="outer",
    )
    if combined.empty:
        return combined
    for col in ["tx_fixed", "sales_fixed", "tx_post", "sales_post"]:
        if col not in combined.columns:
            combined[col] = 0
    combined["tx_fixed"] = pd.to_numeric(combined["tx_fixed"], errors="coerce").fillna(0).astype(int)
    combined["tx_post"] = pd.to_numeric(combined["tx_post"], errors="coerce").fillna(0).astype(int)
    combined["sales_fixed"] = pd.to_numeric(combined["sales_fixed"], errors="coerce").fillna(0.0)
    combined["sales_post"] = pd.to_numeric(combined["sales_post"], errors="coerce").fillna(0.0)
    combined["tx_combined"] = combined["tx_fixed"] + combined["tx_post"]
    combined["sales_combined"] = combined["sales_fixed"] + combined["sales_post"]
    combined["commission_combined"] = combined["sales_combined"] * (commission_rate / 100.0)
    return combined.sort_values("sales_combined", ascending=False).reset_index(drop=True)


def build_khadda_daily_employee_summaries(
    end_date: str,
    data_mode: str,
    include_unassigned: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily employee summaries for Khadda: fixed no-ref range + post-cutoff QR."""
    qr_service = QRCommissionService()
    fixed_start = "2026-03-01"
    # Fixed cutoff: include 1–11 Mar in no-ref <=20% logic
    cutoff_dt = pd.to_datetime("2026-03-12 00:00:00")
    fixed_end_date = "2026-03-11"

    df_non = qr_service.get_non_blinkco_sales_transactions(fixed_start, fixed_end_date, [2], data_mode)
    if df_non is None or df_non.empty:
        fixed_daily = pd.DataFrame()
    else:
        df_non["external_ref_id"] = df_non["external_ref_id"].astype(str).str.strip().replace("None", "")
        no_ref = df_non[df_non["external_ref_id"] == ""].copy()
        if not include_unassigned:
            no_ref = no_ref[no_ref["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
        # Apply <=20% price-diff logic using nearest Blink raw prices.
        raw = qr_service.get_blink_raw_orders(fixed_start, fixed_end_date)
        within_20 = pd.DataFrame()
        if raw is not None and not raw.empty and not no_ref.empty:
            raw_prep = raw[["BlinkOrderId", "OrderJson", "CreatedAt"]].copy()
            raw_prep = prepare_blink_orders(raw_prep)
            raw_prices = pd.to_numeric(raw_prep.get("Indoge_total_price", 0), errors="coerce").dropna()
            raw_prices = raw_prices[raw_prices > 0].astype(float)
            if not raw_prices.empty:
                raw_prices_sorted = np.sort(raw_prices.values)
                def _nearest_price(x: float) -> float:
                    idx = np.searchsorted(raw_prices_sorted, x, side="left")
                    if idx == 0:
                        return float(raw_prices_sorted[0])
                    if idx >= len(raw_prices_sorted):
                        return float(raw_prices_sorted[-1])
                    prev_v = raw_prices_sorted[idx - 1]
                    next_v = raw_prices_sorted[idx]
                    return float(prev_v if abs(x - prev_v) <= abs(x - next_v) else next_v)
                no_ref["total_sale"] = pd.to_numeric(no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
                no_ref["closest_indoge_price"] = no_ref["total_sale"].apply(_nearest_price)
                no_ref["diff_pct"] = (
                    (no_ref["total_sale"] - no_ref["closest_indoge_price"]).abs()
                    / no_ref["total_sale"].replace(0, pd.NA) * 100.0
                )
                within_20 = no_ref[no_ref["diff_pct"] <= 20.0].copy()
        # Fallback: if raw missing, keep within_20 empty to avoid misleading summary.
        no_ref = within_20
        if "sale_date" in no_ref.columns:
            no_ref["sale_day"] = pd.to_datetime(no_ref["sale_date"], errors="coerce").dt.date
        else:
            no_ref["sale_day"] = pd.NaT
        no_ref = no_ref.dropna(subset=["sale_day"])
        no_ref["total_sale"] = pd.to_numeric(no_ref.get("total_sale", 0), errors="coerce").fillna(0.0)
        fixed_daily = (
            no_ref.groupby(["sale_day", "employee_id", "employee_code", "employee_name", "shop_name"], as_index=False)
            .agg(tx_count=("sale_id", "count"), total_sale=("total_sale", "sum"))
        )

    post_start = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
    qr_post = qr_service.get_qr_commission_data(post_start, end_date, [2], data_mode)
    if qr_post is None or qr_post.empty:
        post_daily = pd.DataFrame()
    else:
        # Defensive filter (ensure inclusive end_date and post_start in case of DB quirks)
        qr_post["sale_date"] = pd.to_datetime(qr_post.get("sale_date"), errors="coerce")
        post_start_dt = pd.to_datetime(post_start)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        qr_post = qr_post[(qr_post["sale_date"] >= post_start_dt) & (qr_post["sale_date"] < end_dt)].copy()
        qr_post["external_ref_id"] = qr_post["external_ref_id"].astype(str).str.strip().replace("None", "")
        qr_post = qr_post[qr_post["external_ref_id"] != ""].copy()
        if not include_unassigned:
            qr_post = qr_post[qr_post["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()
        if "sale_date" in qr_post.columns:
            qr_post["sale_day"] = pd.to_datetime(qr_post["sale_date"], errors="coerce").dt.date
        else:
            qr_post["sale_day"] = pd.NaT
        qr_post = qr_post.dropna(subset=["sale_day"])
        qr_post["total_sale"] = pd.to_numeric(qr_post.get("total_sale", 0), errors="coerce").fillna(0.0)
        post_daily = (
            qr_post.groupby(["sale_day", "employee_id", "employee_code", "employee_name", "shop_name"], as_index=False)
            .agg(tx_count=("sale_id", "count"), total_sale=("total_sale", "sum"))
        )

    return fixed_daily, post_daily


def fetch_qr_employee_no_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    commission_rate: float = 2.0,
) -> pd.DataFrame:
    """
    Snapshot helper for QR Commission "Employee Totals (No Sales/Candelahns)".

    This intentionally mirrors the QR Commission tab behavior:
    - Sale-level rows from tblSales where external_ref_type='Blinkco order'
    - End date is inclusive (handled in SQL; do not pass end_date+1 around)
    - Indoge totals come from parsed Blink raw JSON (tblInitialRawBlinkOrder)
    """
    if not branch_ids:
        return pd.DataFrame(
            columns=[
                "employee_id",
                "employee_code",
                "employee_name",
                "shop_id",
                "shop_name",
                "transaction_count",
                "total_sale",
                "Candelahns_commission",
                "Indoge_total_price",
                "Indoge_commission",
            ]
        )

    df_qr = QRCommissionService.get_qr_commission_data(start_date, end_date, branch_ids, data_mode)
    if df_qr is None or df_qr.empty:
        return pd.DataFrame(
            columns=[
                "employee_id",
                "employee_code",
                "employee_name",
                "shop_id",
                "shop_name",
                "transaction_count",
                "total_sale",
                "Candelahns_commission",
                "Indoge_total_price",
                "Indoge_commission",
            ]
        )

    conn = pool.get_connection("candelahns")
    blink_q = """
    SELECT
        BlinkOrderId,
        OrderJson,
        CreatedAt
    FROM tblInitialRawBlinkOrder
    WHERE CreatedAt >= ? AND CreatedAt < DATEADD(DAY, 1, ?)
    """
    df_blink_raw = pd.read_sql(blink_q, conn, params=[start_date, end_date])
    df_blink = prepare_blink_orders(df_blink_raw)

    df_qr = df_qr.copy()
    df_qr["employee_id"] = pd.to_numeric(df_qr.get("employee_id"), errors="coerce").fillna(0).astype(int)
    df_qr["employee_code"] = df_qr.get("employee_code", "").fillna("").astype(str)
    df_qr["employee_name"] = df_qr.get("employee_name", "Online/Unassigned").fillna("Online/Unassigned").astype(str)
    df_qr["shop_id"] = pd.to_numeric(df_qr.get("shop_id"), errors="coerce").fillna(0).astype(int)
    df_qr["shop_name"] = df_qr.get("shop_name", "").fillna("").astype(str)
    df_qr["total_sale"] = pd.to_numeric(df_qr.get("total_sale", 0.0), errors="coerce").fillna(0.0)
    df_qr["external_ref_id"] = df_qr.get("external_ref_id", "").fillna("").astype(str).str.strip()

    merged = df_qr.merge(df_blink, left_on="external_ref_id", right_on="BlinkOrderId", how="left")
    merged["Indoge_total_price"] = pd.to_numeric(merged.get("Indoge_total_price", 0.0), errors="coerce").fillna(0.0)
    merged["Candelahns_commission"] = merged["total_sale"] * (commission_rate / 100.0)
    merged["Indoge_commission"] = merged["Indoge_total_price"] * (commission_rate / 100.0)

    merged = merged[merged["employee_name"].astype(str).str.strip().str.lower() != "online/unassigned"].copy()

    employee_summary = (
        merged.groupby(
            ["employee_id", "employee_code", "employee_name", "shop_id", "shop_name"],
            as_index=False,
        )
        .agg(
            total_sale=("total_sale", "sum"),
            Candelahns_commission=("Candelahns_commission", "sum"),
            Indoge_total_price=("Indoge_total_price", "sum"),
            Indoge_commission=("Indoge_commission", "sum"),
            transaction_count=("external_ref_id", "count"),
        )
        .sort_values(["shop_id", "Indoge_total_price"], ascending=[True, False])
        .reset_index(drop=True)
    )
    return employee_summary


def build_ramzan_tables(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    master = get_cached_ramzan_product_master()
    if master.empty:
        branch_df = pd.DataFrame(columns=["shop_id", "shop_name", "Product_code", "item_name", "total_qty", "total_sales"])
        overall_df = pd.DataFrame(columns=["Product_code", "item_name", "total_qty", "total_sales"])
        return branch_df, overall_df

    master = master[master["Product_code"].astype(str).isin([str(x) for x in RAMZAN_DEALS_PRODUCT_IDS])].copy()
    ids = master["Product_Item_ID"].tolist()
    sales_df = get_cached_ramzan_deals_sales(start_date, end_date, branch_ids, ids)

    merge_keys = ["shop_id", "shop_name", "Product_Item_ID", "Product_code", "item_name"]
    if sales_df.empty:
        sales_df = pd.DataFrame(columns=merge_keys + ["total_qty", "total_sales"])

    branches = pd.DataFrame({
        "shop_id": branch_ids,
        "shop_name": [BRANCH_NAMES.get(int(b), f"Branch {b}") for b in branch_ids],
    })
    branches["key"] = 1
    products = master[["Product_Item_ID", "Product_code", "item_name"]].copy()
    products["key"] = 1
    grid = branches.merge(products, on="key", how="inner").drop(columns=["key"])

    branch_full = grid.merge(
        sales_df[merge_keys + ["total_qty", "total_sales"]],
        on=merge_keys,
        how="left",
    )
    branch_full = ensure_numeric(branch_full, ["total_qty", "total_sales", "shop_id"])
    branch_full = branch_full.sort_values(["shop_id", "Product_code"])

    overall = branch_full.groupby(["Product_Item_ID", "Product_code", "item_name"], as_index=False).agg(
        total_qty=("total_qty", "sum"),
        total_sales=("total_sales", "sum"),
    ).sort_values(["Product_code"])

    branch_show = branch_full.copy()
    branch_show = branch_show.rename(columns={"item_name": "Product", "total_qty": "Total Qty", "total_sales": "Total Sales"})
    branch_show["Total Qty"] = branch_show["Total Qty"].map(lambda x: f"{x:,.0f}")
    branch_show["Total Sales"] = branch_show["Total Sales"].map(lambda x: f"{x:,.0f}")
    
    overall_show = overall.copy()
    overall_show = overall_show.rename(columns={"item_name": "Product", "total_qty": "Total Qty", "total_sales": "Total Sales"})
    overall_show["Total Qty"] = overall_show["Total Qty"].map(lambda x: f"{x:,.0f}")
    overall_show["Total Sales"] = overall_show["Total Sales"].map(lambda x: f"{x:,.0f}")
    return branch_show, overall_show


def parse_args() -> argparse.Namespace:
    today = date.today()
    parser = argparse.ArgumentParser(description="Generate daily branch snapshot PNGs.")
    parser.add_argument("--start-date", default=today.replace(day=1).isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=today.isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--target-year", type=int, default=today.year)
    parser.add_argument("--target-month", type=int, default=today.month)
    parser.add_argument("--branches", nargs="*", type=int, default=SELECTED_BRANCH_IDS)
    parser.add_argument("--data-mode", choices=["Filtered", "Unfiltered"], default="Filtered")
    parser.add_argument("--output-dir", default="HNS_Deshboard/snapshots")
    return parser.parse_args()


def generate_snapshots(
    start_date: str,
    end_date: str,
    target_year: int,
    target_month: int,
    branches: Sequence[int],
    data_mode: str = "Filtered",
    output_dir: str = "HNS_Deshboard/snapshots",
    enabled_sections: Optional[dict] = None,
) -> Path:
    branches = as_int_list(branches)

    enabled = {
        "branch_cards": True,
        "all_products_by_branch": True,
        "qr_employee_no_sales": True,
        "qr_employee_with_sales": True,
        "ramzan_deals": True,
        "material_cost_commission": True,
        "khadda_diagnostics": True,
    }
    if isinstance(enabled_sections, dict):
        for k, v in enabled_sections.items():
            if k in enabled:
                enabled[k] = bool(v)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = Path(output_dir) / f"snap_{start_date}_to_{end_date}_{ts}"
    out_root.mkdir(parents=True, exist_ok=True)
    period_label = f"{start_date} to {end_date}"
    subtitle_label = f"{period_label} | Mode: {data_mode}"

    # Persist run parameters to make it obvious what the snapshots correspond to.
    try:
        (out_root / "run_params.json").write_text(
            json.dumps(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "target_year": int(target_year),
                    "target_month": int(target_month),
                     "branches": [int(b) for b in branches],
                     "data_mode": str(data_mode),
                     "enabled_sections": enabled,
                     "generated_at": datetime.now().isoformat(timespec="seconds"),
                 },
                 indent=2,
             ),
            encoding="utf-8",
        )
    except Exception:
        pass

    # 1) Branch cards snapshot
    if enabled.get("branch_cards", True):
        perf = build_branch_performance(
            start_date=start_date,
            end_date=end_date,
            branch_ids=branches,
            data_mode=data_mode,
            target_year=target_year,
            target_month=target_month,
        )
        card_path = out_root / "01_branch_performance_cards.png"
        render_branch_cards(perf, card_path, subtitle_label)
        save_table_dump(perf, out_root / "01_branch_performance_cards.csv")

    # 2) All products by branch (separate branch files)
    if enabled.get("all_products_by_branch", True):
        products = build_all_products_by_branch(start_date, end_date, branches, data_mode)
        p_dir = out_root / "all_products_by_branch"
        p_dir.mkdir(parents=True, exist_ok=True)
        save_table_dump(products, p_dir / "_all_products_by_branch_raw.csv")
        def render_branch_products(b):
            bdf = products[products["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not bdf.empty:
                bdf = bdf.drop(columns=["shop_id"])
            table_image(
                bdf,
                title=f"All Products by Branch - {bname}",
                out_path=p_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_branch_products, branches)

    # 3) Employee-wise Totals (No Sales/Candelahns), branch-wise
    emp = None
    if enabled.get("qr_employee_no_sales", True) or enabled.get("qr_employee_with_sales", True):
        emp = fetch_qr_employee_no_sales(start_date, end_date, branches, data_mode)

    if enabled.get("qr_employee_no_sales", True):
        e_dir = out_root / "employee_wise_no_sales_branch_wise"
        e_dir.mkdir(parents=True, exist_ok=True)
        save_table_dump(emp, e_dir / "_employee_wise_no_sales_branch_wise_raw.csv")
        def render_emp_no_sales(b):
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                edf["Indoge_total_price"] = pd.to_numeric(edf["Indoge_total_price"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["Indoge_commission"] = pd.to_numeric(edf["Indoge_commission"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        # "employee_id": "Emp ID",
                        "employee_code": "Employee Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "Indoge_total_price": "QR Total Sales",
                        "Indoge_commission": "QR Commission",
                    }
                )
            table_image(
                edf,
                title=f"Employee-wise QR Total Sales and Commission - {bname}",
                out_path=e_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_emp_no_sales, branches)

    if enabled.get("qr_employee_with_sales", True):
        # 3b) QR Employee totals (with sales + both commissions), branch-wise
        e2_dir = out_root / "qr_employee_totals_with_sales"
        e2_dir.mkdir(parents=True, exist_ok=True)
        save_table_dump(emp, e2_dir / "_qr_employee_totals_with_sales_raw.csv")
        def render_emp_with_sales(b):
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "total_sale",
                    "Candelahns_commission",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                for col in ["total_sale", "Candelahns_commission", "Indoge_total_price", "Indoge_commission"]:
                    edf[col] = pd.to_numeric(edf[col], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        # "employee_id": "Emp ID",
                        "employee_code": "Employee Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "total_sale": "Total Sales",
                        "Candelahns_commission": "Candelahns Comm.",
                        "Indoge_total_price": "Indoge Total",
                        "Indoge_commission": "Indoge Comm.",
                    }
                )
            table_image(
                edf,
                title=f"QR Employee Totals (with Sales) - {bname}",
                out_path=e2_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_emp_with_sales, branches)

    # 4) Ramzan deals: branch-wise + overall product-wise
    if enabled.get("ramzan_deals", True):
        ram_branch, ram_overall = build_ramzan_tables(start_date, end_date, branches)
        r_dir = out_root / "ramzan_deals"
        r_dir.mkdir(parents=True, exist_ok=True)
        save_table_dump(ram_branch, r_dir / "_ramzan_branch_raw.csv")
        save_table_dump(ram_overall, r_dir / "_ramzan_overall_raw.csv")
        def render_ramzan_branch(b):
            rdf = ram_branch[ram_branch["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not rdf.empty:
                rdf = rdf.drop(columns=["shop_id", "Product_Item_ID", "Product_code"])
            table_image(
                rdf,
                title=f"Ramzan Deals - Branch-wise Sales - {bname}",
                out_path=r_dir / f"branch_{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_ramzan_branch, branches)

        if not ram_overall.empty:
            ram_overall = ram_overall.drop(columns=["Product_Item_ID", "Product_code"])
        table_image(
            ram_overall,
            title="Ramzan Deals - Product-wise Overall Sales",
            out_path=r_dir / "product_wise_overall.png",
            rows_per_page=35,
            subtitle=subtitle_label,
        )

    # 5) Material Cost Commission snapshots
    if enabled.get("material_cost_commission", True):
        m_dir = out_root / "material_cost_commission"
        m_dir.mkdir(parents=True, exist_ok=True)

        branch_comm_df = get_branch_material_cost_summary(start_date, end_date, branches, data_mode=data_mode)
        if branch_comm_df is not None and not branch_comm_df.empty:
            b_show = branch_comm_df.copy()
            b_show = ensure_numeric(
                b_show,
                ["total_units_sold", "total_sales", "total_material_cost", "total_commission", "avg_commission_rate"],
            )
            b_show = b_show.rename(
                columns={
                    "shop_name": "Shop",
                    "total_units_sold": "Units Sold",
                    "total_sales": "Total Sales",
                    "total_material_cost": "Total Material Cost",
                    "total_commission": "Total Commission",
                    "avg_commission_rate": "Avg Rate",
                }
            )
            if "Total Sales" in b_show.columns:
                b_show["Total Sales"] = b_show["Total Sales"].map(format_currency)
            if "Total Material Cost" in b_show.columns:
                b_show["Total Material Cost"] = b_show["Total Material Cost"].map(format_currency)
            if "Total Commission" in b_show.columns:
                b_show["Total Commission"] = b_show["Total Commission"].map(format_currency)
            if "Avg Rate" in b_show.columns:
                b_show["Avg Rate"] = b_show["Avg Rate"].map(lambda x: f"{float(x):.1f}%")
        else:
            b_show = pd.DataFrame()
        table_image(
            b_show,
            title="Material Cost Commission - Branch Summary",
            out_path=m_dir / "01_branch_summary.png",
            rows_per_page=32,
            subtitle=subtitle_label,
        )

        emp_comm_df = get_employee_material_cost_summary(start_date, end_date, branches, data_mode=data_mode)
        if emp_comm_df is not None and not emp_comm_df.empty:
            e_show_all = emp_comm_df.copy()
            e_show_all = ensure_numeric(
                e_show_all,
                ["total_units_sold", "total_sales", "total_material_cost", "total_commission", "avg_commission_rate"],
            )
            e_show_all = e_show_all.rename(
                columns={
                    "employee_name": "Employee",
                    "employee_code": "Employee Code",
                    "shop_name": "Shop",
                    "total_units_sold": "Units Sold",
                    "total_sales": "Total Sales",
                    "total_material_cost": "Total Material Cost",
                    "total_commission": "Total Commission",
                    "avg_commission_rate": "Avg Rate",
                }
            )
            if "Total Sales" in e_show_all.columns:
                e_show_all["Total Sales"] = e_show_all["Total Sales"].map(format_currency)
            if "Total Material Cost" in e_show_all.columns:
                e_show_all["Total Material Cost"] = e_show_all["Total Material Cost"].map(format_currency)
            if "Total Commission" in e_show_all.columns:
                e_show_all["Total Commission"] = e_show_all["Total Commission"].map(format_currency)
            if "Employee Code" in e_show_all.columns:
                e_show_all["Employee Code"] = e_show_all["Employee Code"].fillna("")
        else:
            e_show_all = pd.DataFrame()

        # Branch-wise employee summary snapshots (exclude shop_id, employee_id, total_transactions, avg rate)
        def render_mcc_emp_summary(b):
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            bdf = e_show_all.copy()
            if not bdf.empty and "Shop" in bdf.columns:
                bdf = bdf[bdf["Shop"] == bname].copy()
            if "Shop" in bdf.columns:
                bdf = bdf.drop(columns=["Shop"], errors="ignore")
            bdf = bdf.drop(columns=["shop_id", "employee_id", "total_transactions", "Avg Rate"], errors="ignore")
            table_image(
                bdf,
                title=f"Material Cost Commission - Employee Summary - {bname}",
                out_path=m_dir / f"02_employee_summary_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=32,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_mcc_emp_summary, branches)

        branch_prod_df = get_branch_product_material_cost_summary(start_date, end_date, branches, data_mode=data_mode)
        if branch_prod_df is not None and not branch_prod_df.empty:
            bp_show = branch_prod_df.copy()
            bp_show = ensure_numeric(
                bp_show,
                [
                    "total_units_sold",
                    "total_sales",
                    "material_cost",
                    "total_material_cost",
                    "commission",
                    "total_commission",
                    "commission_rate",
                ],
            )
            bp_show = bp_show.rename(
                columns={
                    "shop_name": "Shop",
                    "product_code": "Product Code",
                    "product_name": "Product",
                    "total_units_sold": "Units Sold",
                    "total_sales": "Total Sales",
                    "material_cost": "Material Cost",
                    "total_material_cost": "Total Material Cost",
                    "commission": "Commission",
                    "total_commission": "Total Commission",
                    "commission_rate": "Rate",
                }
            )
            for col in ["Total Sales", "Material Cost", "Total Material Cost", "Commission", "Total Commission"]:
                if col in bp_show.columns:
                    bp_show[col] = bp_show[col].map(format_currency)
            if "Rate" in bp_show.columns:
                bp_show["Rate"] = bp_show["Rate"].map(lambda x: f"{float(x):.1f}%")
        else:
            bp_show = pd.DataFrame()
        table_image(
            bp_show,
            title="Material Cost Commission - Product-wise by Branch",
            out_path=m_dir / "03_product_by_branch.png",
            rows_per_page=28,
            subtitle=subtitle_label,
        )

        prod_df = get_product_material_cost_summary(start_date, end_date, branches, data_mode=data_mode)
        if prod_df is not None and not prod_df.empty:
            p_show = prod_df.copy()
            p_show = ensure_numeric(
                p_show,
                [
                    "total_units_sold",
                    "total_sales",
                    "material_cost",
                    "total_material_cost",
                    "commission",
                    "total_commission",
                    "commission_rate",
                ],
            )
            p_show = p_show.rename(
                columns={
                    "product_code": "Product Code",
                    "product_name": "Product",
                    "total_units_sold": "Units Sold",
                    "total_sales": "Total Sales",
                    "material_cost": "Material Cost",
                    "total_material_cost": "Total Material Cost",
                    "commission": "Commission",
                    "total_commission": "Total Commission",
                    "commission_rate": "Rate",
                }
            )
            for col in ["Total Sales", "Material Cost", "Total Material Cost", "Commission", "Total Commission"]:
                if col in p_show.columns:
                    p_show[col] = p_show[col].map(format_currency)
            if "Rate" in p_show.columns:
                p_show["Rate"] = p_show["Rate"].map(lambda x: f"{float(x):.1f}%")
        else:
            p_show = pd.DataFrame()
        table_image(
            p_show,
            title="Material Cost Commission - Product-wise Overall",
            out_path=m_dir / "04_product_overall.png",
            rows_per_page=32,
            subtitle=subtitle_label,
        )

    # Detailed analysis snapshot removed per request

    if not enabled.get("khadda_diagnostics", True):
        return out_root

    # 6) Khadda Diagnostics snapshot (Employee Summary: non-Blinkco POS, with+without ref)
    k_dir = out_root / "khadda_diagnostics"
    k_dir.mkdir(parents=True, exist_ok=True)
    khadda_emp = build_khadda_combined_employee_snapshot(
        end_date, data_mode, commission_rate=float(QR_TOGGLES.default_commission_rate)
    )
    for b in branches:
        if int(b) != 2:
            continue
        bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
        bdf = khadda_emp[khadda_emp["shop_id"] == int(b)].copy() if not khadda_emp.empty else pd.DataFrame()
        if not bdf.empty:
            bdf = bdf.rename(
                columns={
                    "shop_name": "Shop",
                    "employee_name": "Employee",
                    "tx_combined": "Tx",
                    "sales_combined": "Sales",
                    "commission_combined": "Commission",
                }
            )
            # Keep only 5 columns
            keep_cols = ["Shop", "Employee", "Tx", "Sales", "Commission"]
            bdf = bdf[[c for c in keep_cols if c in bdf.columns]].copy()
            if "Sales" in bdf.columns:
                bdf["Sales"] = bdf["Sales"].map(lambda x: f"{x:,.0f}")
            if "Commission" in bdf.columns:
                bdf["Commission"] = bdf["Commission"].map(lambda x: f"{x:,.0f}")
        table_image(
            bdf,
            title=f"Employee-wise QR Total Sales and Commission - {bname}",
            out_path=k_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
            rows_per_page=28,
            subtitle=subtitle_label,
        )

        # Combined snapshot (1–10 Mar within_20 + post-cutoff QR to end_date)
        combined_df = build_khadda_combined_employee_snapshot(
            end_date, data_mode, commission_rate=float(QR_TOGGLES.default_commission_rate)
        )
        if not combined_df.empty and "shop_id" in combined_df.columns:
            combined_df["shop_id"] = pd.to_numeric(combined_df["shop_id"], errors="coerce").fillna(0).astype(int)
        cdf = combined_df[combined_df["shop_id"] == int(b)].copy() if not combined_df.empty else pd.DataFrame()
        if not cdf.empty:
            cdf = cdf.rename(
                columns={
                    "shop_name": "Shop",
                    "employee_name": "Employee",
                    "employee_code": "Employee Code",
                    "tx_fixed": "Tx (1-10 Mar)",
                    "sales_fixed": "Sales (1-10 Mar)",
                    "tx_post": "Tx (Post-cutoff)",
                    "sales_post": "Sales (Post-cutoff)",
                    "tx_combined": "Tx (Combined)",
                    "sales_combined": "Sales (Combined)",
                    "commission_combined": "Commission (Combined)",
                }
            )
            cdf = cdf.drop(columns=["shop_id", "employee_id"], errors="ignore")
            for col in ["Sales (1-10 Mar)", "Sales (Post-cutoff)", "Sales (Combined)", "Commission (Combined)"]:
                if col in cdf.columns:
                    cdf[col] = cdf[col].map(lambda x: f"{x:,.0f}")
        table_image(
            cdf,
            title=f"Khadda Employee Summary (1-10 Mar + Post-cutoff) - {bname}",
            out_path=k_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}_combined.png",
            rows_per_page=28,
            subtitle=subtitle_label,
        )

    # 6) Khadda Diagnostics daily employee summaries (fixed range + post-cutoff)
    fixed_daily, post_daily = build_khadda_daily_employee_summaries(end_date, data_mode)
    if not fixed_daily.empty:
        fixed_show = fixed_daily.copy().sort_values(["sale_day", "total_sale"], ascending=[False, False])
        if not fixed_show.empty:
            fixed_show = fixed_show.drop(columns=["employee_id"], errors="ignore")
            fixed_show = fixed_show.rename(columns={"employee_code": "Employee Code"})
        fixed_show["total_sale"] = fixed_show["total_sale"].map(format_currency)
    else:
        fixed_show = fixed_daily
    table_image(
        fixed_show,
        title="Khadda Daily Employee Summary (≤20% Price Diff, No external_ref_id) - 1 Mar to 10 Mar",
        out_path=k_dir / "daily_employee_no_ref_1_to_10_mar.png",
        rows_per_page=28,
        subtitle="Fixed range summary",
    )

    if not post_daily.empty:
        post_show = post_daily.copy().sort_values(["sale_day", "total_sale"], ascending=[False, False])
        if not post_show.empty:
            post_show = post_show.drop(columns=["employee_id"], errors="ignore")
            post_show = post_show.rename(columns={"employee_code": "Employee Code"})
        post_show["total_sale"] = post_show["total_sale"].map(format_currency)
    else:
        post_show = post_daily
    table_image(
        post_show,
        title=f"Khadda Daily Employee Summary (Post-cutoff) - to {end_date}",
        out_path=k_dir / "daily_employee_post_cutoff.png",
        rows_per_page=28,
        subtitle=f"Post-cutoff → {end_date}",
    )

    # 7) Khadda daily snapshots per employee (combined fixed + post-cutoff)
    if not fixed_daily.empty or not post_daily.empty:
        daily_all = pd.DataFrame()
        if not fixed_daily.empty:
            daily_all = pd.concat([daily_all, fixed_daily], ignore_index=True)
        if not post_daily.empty:
            daily_all = pd.concat([daily_all, post_daily], ignore_index=True)

        if not daily_all.empty:
            daily_all["sale_day"] = pd.to_datetime(daily_all["sale_day"], errors="coerce").dt.date
            daily_all["total_sale"] = pd.to_numeric(daily_all.get("total_sale", 0), errors="coerce").fillna(0.0)
            daily_all["tx_count"] = pd.to_numeric(daily_all.get("tx_count", 0), errors="coerce").fillna(0).astype(int)

            daily_all = (
                daily_all.groupby(
                    ["sale_day", "employee_id", "employee_code", "employee_name", "shop_name"],
                    as_index=False
                )
                .agg(tx_count=("tx_count", "sum"), total_sale=("total_sale", "sum"))
            )

            emp_dir = k_dir / "daily_employee_by_person"
            emp_dir.mkdir(parents=True, exist_ok=True)
            min_day = pd.to_datetime("2026-03-01").date()
            max_day = pd.to_datetime(end_date).date()
            all_days = pd.date_range(min_day, max_day, freq="D").date

        def render_khadda_daily(group):
            (emp_id, emp_code, emp_name), sub = group
            sub = sub.copy()
            day_df = pd.DataFrame({"sale_day": all_days})
            sub = day_df.merge(sub, on="sale_day", how="left")
            sub["employee_name"] = emp_name
            sub["employee_id"] = emp_id
            sub["employee_code"] = emp_code
            if "shop_name" in sub.columns:
                sub["shop_name"] = sub["shop_name"].fillna("Khadda Main Branch")
            sub["tx_count"] = pd.to_numeric(sub.get("tx_count", 0), errors="coerce").fillna(0).astype(int)
            sub["total_sale"] = pd.to_numeric(sub.get("total_sale", 0), errors="coerce").fillna(0.0)

            total_tx = int(sub["tx_count"].sum())
            total_sales = float(sub["total_sale"].sum())

            show = sub[["sale_day", "tx_count", "total_sale"]].copy()
            show = show.rename(columns={"sale_day": "Date", "tx_count": "Tx Count", "total_sale": "Sales"})
            show["Date"] = show["Date"].astype(str)
            show["Sales"] = show["Sales"].map(lambda x: f"{x:,.0f}")

            show = pd.concat(
                [show, pd.DataFrame([{"Date": "TOTAL", "Tx Count": total_tx, "Sales": f"{total_sales:,.0f}"}])],
                ignore_index=True,
            )

            safe_name = _safe_filename(emp_name)
            out_path = emp_dir / f"{safe_name}_{int(emp_id)}.png"
            table_image(
                show,
                title=f"Khadda Daily Sales - {emp_name}",
                out_path=out_path,
                rows_per_page=35,
                subtitle=f"{min_day} to {max_day}",
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_khadda_daily, daily_all.groupby(["employee_id", "employee_code", "employee_name"]))

    return out_root


def main() -> None:
    args = parse_args()
    out_root = generate_snapshots(
        start_date=args.start_date,
        end_date=args.end_date,
        target_year=args.target_year,
        target_month=args.target_month,
        branches=args.branches,
        data_mode=args.data_mode,
        output_dir=args.output_dir,
    )

    print(f"Snapshot folder: {out_root.resolve()}")
    print("Done.")


if __name__ == "__main__":
    main()
