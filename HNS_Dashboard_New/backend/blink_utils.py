import json
import re
from typing import Dict, Tuple, Any, List, Optional
import pandas as pd
import numpy as np

def _walk_find_key(obj: Any, keys: Tuple[str, ...], depth: int = 0, max_depth: int = 6):
    if depth > max_depth:
        return None
    if isinstance(obj, dict):
        for key in keys:
            if key in obj:
                return obj.get(key)
        for v in obj.values():
            found = _walk_find_key(v, keys, depth + 1, max_depth)
            if found is not None:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _walk_find_key(v, keys, depth + 1, max_depth)
            if found is not None:
                return found
    return None

def _walk_find_items(obj: Any, depth: int = 0, max_depth: int = 6):
    if depth > max_depth:
        return None
    if isinstance(obj, dict):
        for key in ("items", "order_items", "orderItems", "products", "product_list"):
            if key in obj and isinstance(obj.get(key), list):
                return obj.get(key)
        for v in obj.values():
            found = _walk_find_items(v, depth + 1, max_depth)
            if found is not None:
                return found
    if isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return obj
        for v in obj:
            found = _walk_find_items(v, depth + 1, max_depth)
            if found is not None:
                return found
    return None

def safe_json_order_fields(order_json: str) -> Tuple[float, int, int, Optional[str], bool]:
    """Extract total_price, total_qty, item_count, order_time from blink order json safely."""
    if pd.isna(order_json) or not str(order_json).strip():
        return 0.0, 0, 0, None, False
    try:
        payload = json.loads(order_json)
        raw_total = _walk_find_key(payload, ("total_price", "totalPrice", "total", "grand_total"))
        raw_time = _walk_find_key(payload, ("order_time", "orderTime", "created_at", "createdAt", "order_date", "due_at", "dueAt"))
        items = _walk_find_items(payload)

        total_price = 0.0
        if raw_total is not None:
            total_price = float(str(raw_total).strip())

        total_qty = 0
        item_count = 0
        if isinstance(items, list):
            item_count = len(items)
            for it in items:
                if isinstance(it, dict):
                    qty = it.get("qty", it.get("quantity", it.get("count", 0)))
                    try:
                        total_qty += int(float(str(qty)))
                    except Exception:
                        continue

        order_time = None
        if raw_time is not None:
            order_time = str(raw_time).strip()

        return total_price, total_qty, item_count, order_time, True
    except Exception:
        s = str(order_json)
        m = re.search(r"\"total_price\"\\s*:\\s*\"?(-?\\d+(?:\\.\\d+)?)\"?", s)
        if not m:
            m = re.search(r"\"totalPrice\"\\s*:\\s*\"?(-?\\d+(?:\\.\\d+)?)\"?", s)
        if not m:
            return 0.0, 0, 0, None, False
        try:
            return float(m.group(1)), 0, 0, None, True
        except Exception:
            return 0.0, 0, 0, None, False

def prepare_blink_orders(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Parse + dedupe raw blink orders by BlinkOrderId.
    Keeps latest CreatedAt row per BlinkOrderId.
    """
    cols = [
        "BlinkOrderId",
        "Indoge_total_price",
        "json_parse_ok",
        "CreatedAt",
        "indoge_total_qty",
        "indoge_item_count",
        "indoge_order_time",
    ]
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=cols)

    df = df_raw.copy()
    if "CreatedAt" in df.columns:
        df["CreatedAt"] = pd.to_datetime(df["CreatedAt"], errors="coerce")
        df = df.sort_values(["BlinkOrderId", "CreatedAt"], ascending=[True, False])
    else:
        df["CreatedAt"] = pd.NaT

    parsed = df.get("OrderJson", pd.Series([""] * len(df))).apply(safe_json_order_fields)
    df["Indoge_total_price"] = parsed.apply(lambda x: x[0]).astype(float)
    df["indoge_total_qty"] = parsed.apply(lambda x: int(x[1]) if x[1] is not None else 0)
    df["indoge_item_count"] = parsed.apply(lambda x: int(x[2]) if x[2] is not None else 0)
    df["indoge_order_time"] = parsed.apply(lambda x: x[3])
    df["json_parse_ok"] = parsed.apply(lambda x: bool(x[4]))

    df = df.drop_duplicates(subset=["BlinkOrderId"], keep="first")
    return df[cols]

def build_split_report(
    df_total_sales: pd.DataFrame,
    df_blinkco_summary: pd.DataFrame,
    commission_rate: float,
) -> pd.DataFrame:
    """Build employee+branch split report (all/blinkco/non-blinkco + shares + commissions)."""
    base = df_total_sales.copy() if df_total_sales is not None else pd.DataFrame()
    blink = df_blinkco_summary.copy() if df_blinkco_summary is not None else pd.DataFrame()

    required_total = {"employee_name", "shop_name", "total_transactions_all", "total_sales_all"}
    required_blink = {"employee_name", "shop_name", "total_sales_blinkco", "total_transactions_blinkco"}
    if base.empty or not required_total.issubset(set(base.columns)):
        return pd.DataFrame()
    if blink.empty:
        blink = pd.DataFrame(columns=list(required_blink))
    
    if {"employee_id", "shop_id"}.issubset(set(base.columns)) and {"employee_id", "shop_id"}.issubset(set(blink.columns)):
        key_cols = ["employee_id", "shop_id"]
    else:
        key_cols = ["employee_name", "shop_name"]

    merged = base.merge(
        blink[key_cols + ["total_sales_blinkco", "total_transactions_blinkco"]],
        on=key_cols,
        how="left",
    )

    merged["total_sales_blinkco"] = pd.to_numeric(merged["total_sales_blinkco"], errors="coerce").fillna(0.0)
    merged["total_transactions_blinkco"] = pd.to_numeric(merged["total_transactions_blinkco"], errors="coerce").fillna(0).astype(int)
    merged["total_sales_without_blinkco"] = (merged["total_sales_all"] - merged["total_sales_blinkco"]).clip(lower=0)
    merged["total_transactions_without_blinkco"] = (
        pd.to_numeric(merged["total_transactions_all"], errors="coerce").fillna(0).astype(int)
        - merged["total_transactions_blinkco"]
    ).clip(lower=0)

    total_den = merged["total_sales_all"].replace(0, pd.NA)
    merged["blinkco_share_pct"] = (merged["total_sales_blinkco"] / total_den * 100).fillna(0).round(2)
    merged["without_blinkco_share_pct"] = (merged["total_sales_without_blinkco"] / total_den * 100).fillna(0).round(2)
    
    merged["commission_total_sales"] = merged["total_sales_all"] * (commission_rate / 100.0)
    merged["commission_blinkco_sales"] = merged["total_sales_blinkco"] * (commission_rate / 100.0)
    merged["commission_without_blinkco_sales"] = merged["total_sales_without_blinkco"] * (commission_rate / 100.0)
    return merged
