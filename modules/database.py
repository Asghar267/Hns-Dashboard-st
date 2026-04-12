"""
Database Module
Implements caching, connection pooling, and optimized queries
"""

import streamlit as st
import pandas as pd
import pyodbc
import warnings
import json
import os
from typing import List, Tuple, Dict, Optional
import time
from datetime import datetime, date, timedelta

# Suppress pandas warning for supported pyodbc DBAPI usage in this app.
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable.*",
    category=UserWarning
)

# Import enhanced database config
try:
    from modules.connection_cloud import DatabaseConfig
except ImportError:
    class DatabaseConfig:
        CACHE_TTL = 300

from modules.config import (
    BLOCKED_NAMES,
    BLOCKED_COMMENTS,
    CATEGORY_FILTERS_FILE,
    DEFAULT_EXCLUDED_CATEGORY_IDS,
    DEFAULT_BRANCH_TARGETS,
    EXCLUDED_BRANCH_NAMES,
)
from modules.utils import log_query_time

# ========================
# CONNECTION POOL
# ========================
# Use the enhanced connection pool from connection_cloud
from modules.connection_cloud import enhanced_pool

# Global connection pool (enhanced)
pool = enhanced_pool

# Cache TTL tuning for heavy queries
HEAVY_CACHE_TTL = int(
    os.environ.get("DB_HEAVY_CACHE_TTL", str(DatabaseConfig.CACHE_TTL * 3))
)
MEDIUM_CACHE_TTL = int(
    os.environ.get("DB_MEDIUM_CACHE_TTL", str(DatabaseConfig.CACHE_TTL * 2))
)

# ========================
# HELPER FUNCTIONS
# ========================
def placeholders(n: int) -> str:
    """Generate SQL placeholders"""
    return ", ".join(["?"] * n) if n > 0 else ""


def _normalize_branch_name(name: object) -> str:
    try:
        text = str(name or "").strip().lower()
    except Exception:
        return ""
    if not text:
        return ""
    # Collapse repeated whitespace so "Dry   Store" matches "dry store"
    return " ".join(text.split())


def _filter_excluded_branches(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "shop_name" not in df.columns:
        return df
    excluded = { _normalize_branch_name(n) for n in (EXCLUDED_BRANCH_NAMES or set()) }
    excluded.discard("")
    if not excluded:
        return df
    norm = df["shop_name"].map(_normalize_branch_name)
    return df[~norm.isin(excluded)].copy()

def build_filter_clause(data_mode: str) -> Tuple[str, List]:
    """Build WHERE clause for filtering blocked items."""
    clause = ""
    params = []
    
    if data_mode == "Filtered":
        if BLOCKED_NAMES:
            clause += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            clause += f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))}) OR s.Additional_Comments IS NULL)"
            params.extend(BLOCKED_COMMENTS)
    
    return clause, params


def _warn_once(session_key: str, message: str) -> None:
    """Show a Streamlit warning only once per session."""
    try:
        if st.session_state.get(session_key):
            return
        st.session_state[session_key] = True
    except Exception:
        # session_state may not be available in some contexts
        pass
    st.warning(message)


def _log_cached_query_time(query_name: str, start_time: float) -> None:
    """Log cached query timings (best-effort)."""
    try:
        duration = time.time() - start_time
        log_query_time(query_name, duration)
    except Exception:
        pass


def _resolve_qualified_table(
    conn: pyodbc.Connection, table_name: str, preferred_schema: str = "dbo"
) -> Optional[str]:
    """Resolve `[schema].[table]` for a table/view name, tolerating non-`dbo` schemas."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT TOP (2) s.name
            FROM sys.objects o
            JOIN sys.schemas s ON s.schema_id = o.schema_id
            WHERE o.name = ?
              AND o.type IN ('U', 'V')
            ORDER BY CASE WHEN s.name = ? THEN 0 ELSE 1 END, s.name
            """,
            (table_name, preferred_schema),
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        schema = rows[0][0]
        return f"[{schema}].[{table_name}]"
    except Exception:
        # If catalog access fails (permissions, etc.), probe the default schema directly.
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP (0) 1 FROM [{preferred_schema}].[{table_name}]")
            return f"[{preferred_schema}].[{table_name}]"
        except Exception:
            return None


def _find_employee_role_column(conn: pyodbc.Connection) -> Optional[str]:
    """Best-effort detect a role/designation column on tblDefShopEmployees."""
    candidates = [
        "designation",
        "role",
        "job_title",
        "employee_type",
        "position",
        "emp_type",
        "type",
        "department",
    ]
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.name
            FROM sys.columns c
            JOIN sys.objects o ON o.object_id = c.object_id
            WHERE o.name = ?
              AND o.type IN ('U', 'V')
            """,
            ("tblDefShopEmployees",),
        )
        cols = {row[0].lower() for row in cursor.fetchall()}
        for cand in candidates:
            if cand.lower() in cols:
                return cand
        return None
    except Exception:
        return None


def _get_db_context(conn: pyodbc.Connection) -> str:
    """Best-effort string describing the connected DB/server."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DB_NAME() AS db_name, CAST(SERVERPROPERTY('ServerName') AS NVARCHAR(256)) AS server_name"
        )
        row = cursor.fetchone()
        cursor.close()
        if row and len(row) >= 2:
            return f"{row[0]} @ {row[1]}"
    except Exception:
        pass
    return "unknown_db"

def _exception_text(e: Exception) -> str:
    try:
        return str(e)
    except Exception:
        return repr(e)


def _has_sqlstate(e: Exception, sqlstate: str) -> bool:
    """Best-effort check for an ODBC SQLSTATE like 42S22 / 42S02."""
    try:
        args = getattr(e, "args", None)
        if args:
            for a in args:
                if isinstance(a, str) and a.strip().upper() == sqlstate.upper():
                    return True
                if isinstance(a, (tuple, list)) and a and isinstance(a[0], str) and a[0].strip().upper() == sqlstate.upper():
                    return True
    except Exception:
        pass
    return sqlstate.upper() in _exception_text(e).upper()


def _table_supports_period_filters(conn: pyodbc.Connection, table_ref: str) -> bool:
    """Return True if table has target_year and target_month columns."""
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP (0) target_year, target_month FROM {table_ref}")
        return True
    except Exception:
        return False
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            pass


def _table_supports_target_date(conn: pyodbc.Connection, table_ref: str) -> bool:
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP (0) target_date FROM {table_ref}")
        return True
    except Exception:
        return False
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            pass


def _resolve_table_across_databases(
    conn: pyodbc.Connection,
    table_name: str,
    preferred_schema: str = "dbo",
    candidate_databases: Optional[List[str]] = None,
) -> Optional[str]:
    """Resolve a targets table, optionally across multiple DBs on same server.

    Returns a bracketed identifier like `[dbo].[branch_targets]` (current DB) or
    `[KDS_DB].[dbo].[branch_targets]` (other DB).
    """
    # 1) Try current DB with schema discovery.
    qualified = _resolve_qualified_table(conn, table_name, preferred_schema=preferred_schema)
    if qualified:
        return qualified

    # 2) Try common alternate DBs on the same server (3-part names).
    if not candidate_databases:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        for db in candidate_databases:
            db = str(db).strip()
            if not db:
                continue
            probe = f"[{db}].[{preferred_schema}].[{table_name}]"
            try:
                cursor.execute(f"SELECT TOP (0) 1 FROM {probe}")
                return probe
            except Exception:
                continue
    finally:
        try:
            if cursor is not None:
                cursor.close()
        except Exception:
            pass

    return None



@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_blocked_impact(
    start_date: str,
    end_date: str,
    branch_ids: List[int]
) -> pd.DataFrame:
    """Fetch details of transactions excluded by blocked lists (Impact Analysis)"""
    if not BLOCKED_NAMES and not BLOCKED_COMMENTS:
        return pd.DataFrame()

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        s.shop_id,
        sh.shop_name,
        s.Cust_name,
        COALESCE(s.Additional_Comments, 'N/A') as Additional_Comments,
        s.Nt_amount,
        s.sale_date
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND (
          s.Cust_name IN ({placeholders(len(BLOCKED_NAMES))})
          OR s.Additional_Comments IN ({placeholders(len(BLOCKED_COMMENTS))})
      )
    """
    
    params = [start_date, end_date] + branch_ids + BLOCKED_NAMES + BLOCKED_COMMENTS
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df['Nt_amount'] = pd.to_numeric(df['Nt_amount'], errors='coerce').fillna(0).astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching blocked impact: {e}")
        return pd.DataFrame()




@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_saved_category_filters() -> Dict:
    """Load saved include/exclude category filters from disk.
    Deduplicates category names by normalized version."""
    defaults = {
        "included_category_ids": [],
        "excluded_category_ids": DEFAULT_EXCLUDED_CATEGORY_IDS.copy(),
        "included_category_names": [],
        "excluded_category_names": []
    }
    try:
        if os.path.exists(CATEGORY_FILTERS_FILE):
            with open(CATEGORY_FILTERS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                for key in defaults:
                    if key in saved and isinstance(saved[key], list):
                        defaults[key] = saved[key]
        
        # Deduplicate category names by normalized version
        included_names = defaults.get("included_category_names", [])
        excluded_names = defaults.get("excluded_category_names", [])
        
        # Deduplicate included names - keep first occurrence of each normalized name
        seen_normalized = set()
        dedup_included = []
        for name in included_names:
            normalized = _normalize_category_name(name)
            if normalized and normalized not in seen_normalized:
                seen_normalized.add(normalized)
                dedup_included.append(name)
        
        # Deduplicate excluded names
        seen_normalized = set()
        dedup_excluded = []
        for name in excluded_names:
            normalized = _normalize_category_name(name)
            if normalized and normalized not in seen_normalized:
                seen_normalized.add(normalized)
                dedup_excluded.append(name)
        
        defaults["included_category_names"] = dedup_included
        defaults["excluded_category_names"] = dedup_excluded
        
    except Exception:
        pass
    return defaults


def save_category_filters(settings: Dict) -> None:
    """Persist include/exclude category filters to disk.
    Deduplicates category names by normalized version."""
    # Deduplicate included names
    included_names = [str(x) for x in settings.get("included_category_names", [])]
    seen_normalized = set()
    dedup_included = []
    for name in included_names:
        normalized = _normalize_category_name(name)
        if normalized and normalized not in seen_normalized:
            seen_normalized.add(normalized)
            dedup_included.append(name)
    
    # Deduplicate excluded names
    excluded_names = [str(x) for x in settings.get("excluded_category_names", [])]
    seen_normalized = set()
    dedup_excluded = []
    for name in excluded_names:
        normalized = _normalize_category_name(name)
        if normalized and normalized not in seen_normalized:
            seen_normalized.add(normalized)
            dedup_excluded.append(name)
    
    payload = {
        "included_category_ids": [int(x) for x in settings.get("included_category_ids", [])],
        "excluded_category_ids": [int(x) for x in settings.get("excluded_category_ids", [])],
        "included_category_names": dedup_included,
        "excluded_category_names": dedup_excluded,
        "updated_at": datetime.now().isoformat(timespec="seconds")
    }
    os.makedirs(os.path.dirname(CATEGORY_FILTERS_FILE), exist_ok=True)
    with open(CATEGORY_FILTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    try:
        get_saved_category_filters.clear()
    except Exception:
        pass


def _normalize_category_name(name: str) -> str:
    """Normalize category name for consistent matching and deduplication.
    Converts to uppercase and standardizes spacing/punctuation."""
    if not isinstance(name, str):
        return ""
    # Convert to uppercase, strip whitespace, normalize dashes/spaces/hyphens
    normalized = name.upper().strip()
    # Replace multiple spaces with single space
    normalized = " ".join(normalized.split())
    # Standardize dashes and hyphens
    normalized = normalized.replace(" -", "-").replace("- ", "-")
    return normalized


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_all_available_categories() -> pd.DataFrame:
    """Fetch ALL available categories from both KDS DB and Candelahns sources.
    
    Returns a DataFrame with columns: category_id, category_name, source, normalized_name
    Combines categories from:
    - dbo.chef_sale (KDS DB) - has category_id
    - TempProductBarcode (Candelahns) - field_name mapping
    
    Deduplicates by normalized name, keeping the cleanest/most standard version.
    """
    all_categories = []
    
    # Get categories from KDS DB (dbo.chef_sale)
    try:
        conn_kds = pool.get_connection("kdsdb")
        df_kds = pd.read_sql(
            "SELECT category_id, category_name FROM dbo.chef_sale ORDER BY category_name",
            conn_kds
        )
        if not df_kds.empty:
            df_kds["source"] = "KDS"
            all_categories.append(df_kds)
    except Exception:
        pass
    
    # Get categories from Candelahns TempProductBarcode (mapping table)
    try:
        conn = pool.get_connection("candelahns")
        df_candel = pd.read_sql(
            """SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT DISTINCT field_name as category_name 
            FROM TempProductBarcode WITH (NOLOCK)
            WHERE field_name IS NOT NULL AND field_name <> ''
            ORDER BY field_name""",
            conn
        )
        if not df_candel.empty:
            df_candel["category_id"] = None
            df_candel["source"] = "Candelahns"
            all_categories.append(df_candel)
    except Exception:
        pass
    
    # Combine all categories and deduplicate by normalized name
    if all_categories:
        df_combined = pd.concat(all_categories, ignore_index=True)
        # Add normalized name column
        df_combined["normalized_name"] = df_combined["category_name"].apply(_normalize_category_name)
        # Remove duplicates, keeping KDS source first (has more metadata)
        df_combined["source_priority"] = df_combined["source"].apply(lambda x: 0 if x == "KDS" else 1)
        df_combined = df_combined.sort_values(["normalized_name", "source_priority"])
        df_combined = df_combined.drop_duplicates(subset=["normalized_name"], keep="first")
        # Sort by category name
        return df_combined.sort_values("category_name").reset_index(drop=True)
    
    return pd.DataFrame(columns=["category_id", "category_name", "source", "normalized_name"])


def build_category_name_filter_clause(category_alias: str = "t") -> Tuple[str, List]:
    """Build category include/exclude clause for line-item queries."""
    settings = get_saved_category_filters()
    include_names = [str(x).strip() for x in settings.get("included_category_names", []) if str(x).strip()]
    exclude_names = [str(x).strip() for x in settings.get("excluded_category_names", []) if str(x).strip()]

    # Deduplicate
    include_names = list(dict.fromkeys(include_names))
    exclude_names = list(dict.fromkeys(exclude_names))

    # If both present, prioritize exclusion (remove from include if excluded)
    if include_names and exclude_names:
        include_names = [x for x in include_names if x not in set(exclude_names)]

    clause = ""
    params: List = []
    
    # Use field_name from TempProductBarcode
    if include_names:
        clause += f" AND {category_alias}.field_name IN ({placeholders(len(include_names))})"
        params.extend(include_names)
    
    # Exclude names. Check for NULL to handle unmapped items if not explicitly excluded
    if exclude_names:
        clause += f" AND ({category_alias}.field_name NOT IN ({placeholders(len(exclude_names))}) OR {category_alias}.field_name IS NULL)"
        params.extend(exclude_names)

    return clause, params


def is_category_counted(category_name: str, included_names: List[str], excluded_names: List[str]) -> bool:
    """Evaluate whether a category is counted based on include/exclude name rules.
    Uses normalized category name matching (case-insensitive, whitespace-normalized)."""
    # Normalize the category name for comparison
    cname_normalized = _normalize_category_name(category_name)
    
    # Normalize included and excluded lists
    include_set = set(_normalize_category_name(str(x)) for x in included_names if str(x).strip())
    exclude_set = set(_normalize_category_name(str(x)) for x in excluded_names if str(x).strip())
    
    # Check excluded first (exclusion takes priority)
    if exclude_set and cname_normalized in exclude_set:
        return False
    
    # If include list is not empty, only count if in include list
    if include_set and cname_normalized not in include_set:
        return False
    
    # If no include list, default to true (unless explicitly excluded)
    return True

# ========================
# CACHED QUERY FUNCTIONS
# ========================

# Add these functions to the database module to get category-level data

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_category_monthly_history(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch category-level monthly sales history"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            FORMAT(s.sale_date, 'yyyy-MM') AS month,
            COALESCE(t.field_name, '(Unmapped)') AS category_name,
            li.qty * li.Unit_price AS line_val,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS order_total,
            s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
    )
    SELECT
        month,
        category_name,
        SUM(line_val / NULLIF(order_total, 0) * Nt_amount) AS total_sales
    FROM sale_lines
    GROUP BY month, category_name
    ORDER BY month, total_sales DESC
    """
    
    params = [start_date, end_date] + branch_ids + category_params + filter_params
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_sales' in df.columns:
            df['total_sales'] = df['total_sales'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching category history: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_top_products(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    category: Optional[str] = None,
    top_n: int = 10,
    sort_ascending: bool = False
) -> pd.DataFrame:
    """Fetch top or bottom products by sales"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    
    specific_cat_clause = ""
    specific_cat_params = []
    if category:
        specific_cat_clause = " AND t.field_name = ?"
        specific_cat_params = [category]

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH lines AS (
        SELECT
            COALESCE(p.item_name, t.field_name) AS product_name,
            li.qty * li.Unit_price AS line_val,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS order_total,
            s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
            {specific_cat_clause}
    )
    SELECT TOP {int(top_n)}
        product_name,
        SUM(line_val / NULLIF(order_total, 0) * Nt_amount) AS total_sales
    FROM lines
    GROUP BY product_name
    ORDER BY total_sales {"ASC" if sort_ascending else "DESC"}
    """
    
    params = [start_date, end_date] + branch_ids + category_params + filter_params + specific_cat_params
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'Total_Sales' in df.columns:
            df['Total_Sales'] = df['Total_Sales'].astype(float)
        if 'Total_Qty' in df.columns:
            df['Total_Qty'] = df['Total_Qty'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching top products: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=HEAVY_CACHE_TTL, show_spinner=False)
def get_cached_top_products_overview(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    top_n: int = 5,
) -> pd.DataFrame:
    """Fetch top products by sales (overview lightweight)."""
    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.sale_id,
            s.Nt_amount,
            li.qty,
            li.Unit_price,
            li.Product_Item_ID,
            li.Product_code,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (
            SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name
            FROM TempProductBarcode WITH (NOLOCK)
            UNION ALL SELECT 2642, '0570', 'Deals'
        ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
            AND li.Unit_price > 0
    )
    SELECT TOP {int(top_n)}
        COALESCE(t.field_name, '(Unmapped)') AS product,
        SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_sales
    FROM sale_lines sl
    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name
        FROM TempProductBarcode WITH (NOLOCK)
        UNION ALL SELECT 2642, '0570', 'Deals'
    ) t ON sl.Product_Item_ID = t.Product_Item_ID AND sl.Product_code = t.Product_code
    GROUP BY COALESCE(t.field_name, '(Unmapped)')
    ORDER BY total_sales DESC
    """
    params = [start_date, end_date] + branch_ids + category_params + filter_params
    try:
        t0 = time.time()
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if "total_sales" in df.columns:
            df["total_sales"] = df["total_sales"].astype(float)
        _log_cached_query_time("get_cached_top_products_overview", t0)
        return df
    except Exception as e:
        st.error(f"Error fetching overview top products: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_branch_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    apply_category_filters: bool = False,
) -> pd.DataFrame:
    """Fetch branch summary with caching - simplified for performance"""
    if apply_category_filters:
        df = get_cached_branch_summary_variants(start_date, end_date, branch_ids)
        if df is None or df.empty:
            return pd.DataFrame()
        total_col = "total_category_only" if data_mode == "Unfiltered" else "total_both"
        cols = ["shop_id", "shop_name", "total_sales", total_col]
        df = df[cols].copy()
        df = df.rename(columns={total_col: "total_Nt_amount"})
        return df
    filter_clause, filter_params = build_filter_clause(data_mode)

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH shop_sales AS (
        SELECT
            s.shop_id,
            COUNT(DISTINCT s.sale_id) AS total_sales,
            SUM(s.Nt_amount) AS total_Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
        GROUP BY s.shop_id
    )
    SELECT
        sh.shop_id,
        sh.shop_name,
        COALESCE(ss.total_sales, 0) AS total_sales,
        COALESCE(ss.total_Nt_amount, 0) AS total_Nt_amount
    FROM tblDefShops sh WITH (NOLOCK)
    LEFT JOIN shop_sales ss ON sh.shop_id = ss.shop_id
    WHERE sh.shop_id IN ({placeholders(len(branch_ids))})
    ORDER BY sh.shop_id
    """

    params = [start_date, end_date] + branch_ids + filter_params + branch_ids
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'employee_id' in df.columns:
            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
        return df
    except Exception as e:
        st.error(f"Error fetching branch summary: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_branch_summary_variants(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> pd.DataFrame:
    """Fetch branch summary for raw/blocked/category/both in one query."""
    settings = get_saved_category_filters()
    include_names = [str(x).strip() for x in settings.get("included_category_names", []) if str(x).strip()]
    exclude_names = [str(x).strip() for x in settings.get("excluded_category_names", []) if str(x).strip()]

    include_names = list(dict.fromkeys(include_names))
    exclude_names = list(dict.fromkeys(exclude_names))
    if include_names and exclude_names:
        include_names = [x for x in include_names if x not in set(exclude_names)]

    category_params: List = []
    if include_names:
        category_expr = f"t.field_name IN ({placeholders(len(include_names))})"
        category_params.extend(include_names)
    else:
        category_expr = "1=1"

    if exclude_names:
        category_expr = f"({category_expr}) AND (t.field_name NOT IN ({placeholders(len(exclude_names))}) OR t.field_name IS NULL)"
        category_params.extend(exclude_names)

    blocked_params: List = []
    blocked_expr_parts = []
    if BLOCKED_NAMES:
        blocked_expr_parts.append(f"s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})")
        blocked_params.extend(BLOCKED_NAMES)
    if BLOCKED_COMMENTS:
        blocked_expr_parts.append(f"(s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))}) OR s.Additional_Comments IS NULL)")
        blocked_params.extend(BLOCKED_COMMENTS)
    blocked_expr = " AND ".join(blocked_expr_parts) if blocked_expr_parts else "1=1"

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.sale_id,
            s.shop_id,
            s.Nt_amount,
            li.qty,
            li.Unit_price,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS line_total,
            CASE WHEN {blocked_expr} THEN 1 ELSE 0 END AS blocked_ok,
            CASE WHEN {category_expr} THEN 1 ELSE 0 END AS category_ok
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
    ),
    shop_sales AS (
        SELECT
            shop_id,
            COUNT(DISTINCT sale_id) AS total_sales,
            SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_raw,
            SUM(CASE WHEN blocked_ok = 1 THEN (qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount ELSE 0 END) AS total_blocked_only,
            SUM(CASE WHEN category_ok = 1 THEN (qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount ELSE 0 END) AS total_category_only,
            SUM(CASE WHEN blocked_ok = 1 AND category_ok = 1 THEN (qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount ELSE 0 END) AS total_both
        FROM sale_lines
        GROUP BY shop_id
    )
    SELECT
        sh.shop_id,
        sh.shop_name,
        COALESCE(ss.total_sales, 0) AS total_sales,
        COALESCE(ss.total_raw, 0) AS total_raw,
        COALESCE(ss.total_blocked_only, 0) AS total_blocked_only,
        COALESCE(ss.total_category_only, 0) AS total_category_only,
        COALESCE(ss.total_both, 0) AS total_both
    FROM tblDefShops sh WITH (NOLOCK)
    LEFT JOIN shop_sales ss ON sh.shop_id = ss.shop_id
    WHERE sh.shop_id IN ({placeholders(len(branch_ids))})
    ORDER BY sh.shop_id
    """

    params = blocked_params + category_params + [start_date, end_date] + branch_ids + branch_ids
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error fetching branch summary variants: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_ot_data(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch OT/Employee data with caching - simplified for performance"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH emp_sales AS (
        SELECT 
            s.shop_id,
            s.employee_id,
            SUM(s.Nt_amount) AS total_sale
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
        GROUP BY s.shop_id, s.employee_id
    )
    SELECT 
        es.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COALESCE(es.total_sale, 0) AS total_sale
    FROM emp_sales es
    LEFT JOIN tblDefShopEmployees e ON es.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON es.shop_id = sh.shop_id
    ORDER BY es.shop_id, employee_name
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'employee_id' in df.columns:
            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
        if "employee_code" in df.columns:
            df["employee_code"] = df["employee_code"].fillna("").astype(str)
        df['total_sale'] = df['total_sale'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching OT data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_cashier_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch cashier/counter cashier sales using role/type columns when available."""
    filter_clause, filter_params = build_filter_clause(data_mode)
    try:
        conn = pool.get_connection("candelahns")
        role_col = _find_employee_role_column(conn)
        emp_table = _resolve_qualified_table(conn, "tblDefShopEmployees") or "tblDefShopEmployees"
        shop_table = _resolve_qualified_table(conn, "tblDefShops") or "tblDefShops"
        sales_table = _resolve_qualified_table(conn, "tblSales") or "tblSales"

        if role_col:
            role_filter = f"LOWER(COALESCE(e.[{role_col}], '')) LIKE '%cashier%'"
        else:
            role_filter = "LOWER(COALESCE(e.field_name, '')) LIKE '%cashier%'"

        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH emp_sales AS (
            SELECT 
                s.shop_id,
                s.employee_id,
                SUM(s.Nt_amount) AS total_sale
            FROM {sales_table} s WITH (NOLOCK)
            WHERE s.sale_date BETWEEN ? AND ?
                AND s.shop_id IN ({placeholders(len(branch_ids))})
                {filter_clause}
            GROUP BY s.shop_id, s.employee_id
        )
        SELECT 
            es.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COALESCE(es.total_sale, 0) AS total_sale
        FROM emp_sales es
        LEFT JOIN {emp_table} e ON es.employee_id = e.shop_employee_id
        LEFT JOIN {shop_table} sh ON es.shop_id = sh.shop_id
        WHERE {role_filter}
        ORDER BY es.shop_id, employee_name
        """

        params = [start_date, end_date] + branch_ids + filter_params
        df = pd.read_sql(query, conn, params=params)
        if 'employee_id' in df.columns:
            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
        if "employee_code" in df.columns:
            df["employee_code"] = df["employee_code"].fillna("").astype(str)
        df['total_sale'] = df['total_sale'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching cashier sales: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=HEAVY_CACHE_TTL)
def get_cached_line_items(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch line items with caching (filtered line totals to avoid full table scans)."""
    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH filtered_sales AS (
        SELECT s.sale_id, s.shop_id, s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
    ),
    line_totals AS (
        SELECT li.sale_id, SUM(li.qty * li.Unit_price) AS line_total
        FROM tblSalesLineItems li WITH (NOLOCK)
        JOIN filtered_sales fs ON fs.sale_id = li.sale_id
        WHERE li.Unit_price > 0
        GROUP BY li.sale_id
    )
    SELECT 
        fs.shop_id,
        sh.shop_name,
        COALESCE(t.field_name, '(Unmapped)') AS product,
        SUM(li.qty) AS total_qty,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS total_line_value_incl_tax
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t
        ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON fs.shop_id = sh.shop_id
    WHERE li.Unit_price > 0
        {category_clause}
    GROUP BY fs.shop_id, sh.shop_name, COALESCE(t.field_name, '(Unmapped)')
    ORDER BY fs.shop_id, COALESCE(t.field_name, '(Unmapped)')
    """

    params = [start_date, end_date] + branch_ids + filter_params + category_params

    try:
        t0 = time.time()
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        df['total_line_value_incl_tax'] = df['total_line_value_incl_tax'].astype(float)
        _log_cached_query_time("get_cached_line_items", t0)
        return df
    except Exception as e:
        st.error(f"Error fetching line items: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_order_types(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch order type analysis with caching and category filtering"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    settings = get_saved_category_filters()
    include_names = [str(x).strip() for x in settings.get("included_category_names", []) if str(x).strip()]
    exclude_names = [str(x).strip() for x in settings.get("excluded_category_names", []) if str(x).strip()]
    has_category_filters = bool(include_names or exclude_names)
    category_clause, category_params = build_category_name_filter_clause("t")

    if not has_category_filters:
        # Fast path when no category filters are active (uses sales only).
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            CASE
                WHEN s.Cust_name = 'Food Panda' THEN 'Food Panda'
                WHEN s.Cust_name = 'Takeaway' THEN 'Takeaway'
                WHEN s.Cust_name = 'Web Online Paid Order' THEN 'Web Online Paid Order'
                WHEN s.Cust_name = 'Cash Web Online Order' THEN 'Cash Web Online Order'
                WHEN s.Cust_name = 'Dine IN' THEN 'Dine IN'
                WHEN s.Cust_name = 'Credit Card South' THEN 'Credit Card South'
                WHEN s.Cust_name = 'HNS Credit Card' THEN 'HNS Credit Card'
                WHEN s.Cust_name = 'Delivery' THEN 'Delivery'
                ELSE 'Others'
            END AS order_type,
            COUNT(DISTINCT s.sale_id) AS total_orders,
            SUM(s.Nt_amount) AS total_sales
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
        GROUP BY
            CASE
                WHEN s.Cust_name = 'Food Panda' THEN 'Food Panda'
                WHEN s.Cust_name = 'Takeaway' THEN 'Takeaway'
                WHEN s.Cust_name = 'Web Online Paid Order' THEN 'Web Online Paid Order'
                WHEN s.Cust_name = 'Cash Web Online Order' THEN 'Cash Web Online Order'
                WHEN s.Cust_name = 'Dine IN' THEN 'Dine IN'
                WHEN s.Cust_name = 'Credit Card South' THEN 'Credit Card South'
                WHEN s.Cust_name = 'HNS Credit Card' THEN 'HNS Credit Card'
                WHEN s.Cust_name = 'Delivery' THEN 'Delivery'
                ELSE 'Others'
            END
        ORDER BY total_sales DESC
        """
        params = [start_date, end_date] + branch_ids + filter_params
    else:
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH sale_lines AS (
            SELECT
                s.sale_id,
                CASE
                    WHEN s.Cust_name = 'Food Panda' THEN 'Food Panda'
                    WHEN s.Cust_name = 'Takeaway' THEN 'Takeaway'
                    WHEN s.Cust_name = 'Web Online Paid Order' THEN 'Web Online Paid Order'
                    WHEN s.Cust_name = 'Cash Web Online Order' THEN 'Cash Web Online Order'
                    WHEN s.Cust_name = 'Dine IN' THEN 'Dine IN'
                    WHEN s.Cust_name = 'Credit Card South' THEN 'Credit Card South'
                    WHEN s.Cust_name = 'HNS Credit Card' THEN 'HNS Credit Card'
                    WHEN s.Cust_name = 'Delivery' THEN 'Delivery'
                    ELSE 'Others'
                END AS order_type,
                li.qty,
                li.Unit_price,
                s.Nt_amount,
                SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id) AS line_total
            FROM tblSales s WITH (NOLOCK)
            JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
            LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
            WHERE s.sale_date BETWEEN ? AND ?
                AND s.shop_id IN ({placeholders(len(branch_ids))})
                {category_clause}
                {filter_clause}
        ),
        order_type_sales AS (
            SELECT
                order_type,
                COUNT(DISTINCT sale_id) AS total_orders,
                SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_sales
            FROM sale_lines
            GROUP BY order_type
        )
        SELECT * FROM order_type_sales ORDER BY total_sales DESC
        """
        params = [start_date, end_date] + branch_ids + category_params + filter_params
    
    try:
        t0 = time.time()
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        df['total_sales'] = df['total_sales'].astype(float)
        _log_cached_query_time("get_cached_order_types", t0)
        return df
    except Exception as e:
        st.error(f"Error fetching order types: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_order_type_others_breakdown(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """
    Diagnose what is included in the 'Others' bucket for order_type analysis.

    Returns the raw tblSales.Cust_name values (trimmed) that are NOT mapped to the known order types,
    with orders and sales computed in the same way as get_cached_order_types (including optional
    category filters).
    """
    filter_clause, filter_params = build_filter_clause(data_mode)
    settings = get_saved_category_filters()
    include_names = [str(x).strip() for x in settings.get("included_category_names", []) if str(x).strip()]
    exclude_names = [str(x).strip() for x in settings.get("excluded_category_names", []) if str(x).strip()]
    has_category_filters = bool(include_names or exclude_names)
    category_clause, category_params = build_category_name_filter_clause("t")

    # Must match the CASE mapping in get_cached_order_types.
    known_order_types = [
        "Food Panda",
        "Takeaway",
        "Web Online Paid Order",
        "Cash Web Online Order",
        "Dine IN",
        "Credit Card South",
        "HNS Credit Card",
        "Delivery",
    ]
    known_list_sql = ", ".join(["'" + x.replace("'", "''") + "'" for x in known_order_types])

    if not has_category_filters:
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            CASE
                WHEN s.Cust_name IS NULL THEN '(NULL)'
                WHEN s.Cust_name = '' THEN '(Blank)'
                ELSE CONCAT('>', s.Cust_name, '<')
            END AS raw_order_type,
            COUNT(DISTINCT s.sale_id) AS total_orders,
            SUM(s.Nt_amount) AS total_sales
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
            AND (s.Cust_name IS NULL OR s.Cust_name NOT IN ({known_list_sql}))
        GROUP BY
            CASE
                WHEN s.Cust_name IS NULL THEN '(NULL)'
                WHEN s.Cust_name = '' THEN '(Blank)'
                ELSE CONCAT('>', s.Cust_name, '<')
            END
        ORDER BY total_sales DESC
        """
        params = [start_date, end_date] + branch_ids + filter_params
    else:
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH sale_lines AS (
            SELECT
                s.sale_id,
                s.Cust_name AS cust_name_raw,
                CASE
                    WHEN s.Cust_name IS NULL THEN '(NULL)'
                    WHEN s.Cust_name = '' THEN '(Blank)'
                    ELSE CONCAT('>', s.Cust_name, '<')
                END AS raw_order_type,
                li.qty,
                li.Unit_price,
                s.Nt_amount,
                SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id) AS line_total
            FROM tblSales s WITH (NOLOCK)
            JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
            LEFT JOIN (
                SELECT
                    Product_Item_ID,
                    CAST(Product_code AS VARCHAR(50)) as Product_code,
                    CAST(field_name AS VARCHAR(100)) as field_name
                FROM TempProductBarcode WITH (NOLOCK)
                UNION ALL
                SELECT 2642, '0570', 'Deals'
            ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
            WHERE s.sale_date BETWEEN ? AND ?
                AND s.shop_id IN ({placeholders(len(branch_ids))})
                {category_clause}
                {filter_clause}
        ),
        others_sales AS (
            SELECT
                raw_order_type,
                COUNT(DISTINCT sale_id) AS total_orders,
                SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_sales
            FROM sale_lines
            WHERE (cust_name_raw IS NULL OR cust_name_raw NOT IN ({known_list_sql}))
            GROUP BY raw_order_type
        )
        SELECT * FROM others_sales ORDER BY total_sales DESC
        """
        params = [start_date, end_date] + branch_ids + category_params + filter_params

    try:
        t0 = time.time()
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if not df.empty and "total_sales" in df.columns:
            df["total_sales"] = df["total_sales"].astype(float)
        _log_cached_query_time("get_cached_order_type_others_breakdown", t0)
        return df
    except Exception as e:
        st.error(f"Error fetching Others breakdown: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_order_type_others_order_takers(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """
    Diagnose which order takers are contributing to the 'Others' bucket.

    Returns employee_name with orders and sales using the same 'Others' definition as
    get_cached_order_types.
    """
    filter_clause, filter_params = build_filter_clause(data_mode)
    settings = get_saved_category_filters()
    include_names = [str(x).strip() for x in settings.get("included_category_names", []) if str(x).strip()]
    exclude_names = [str(x).strip() for x in settings.get("excluded_category_names", []) if str(x).strip()]
    has_category_filters = bool(include_names or exclude_names)
    category_clause, category_params = build_category_name_filter_clause("t")

    known_order_types = [
        "Food Panda",
        "Takeaway",
        "Web Online Paid Order",
        "Cash Web Online Order",
        "Dine IN",
        "Credit Card South",
        "HNS Credit Card",
        "Delivery",
    ]
    known_list_sql = ", ".join(["'" + x.replace("'", "''") + "'" for x in known_order_types])

    if not has_category_filters:
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20)))) AS shop_name,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS total_orders,
            SUM(s.Nt_amount) AS total_sales
        FROM tblSales s WITH (NOLOCK)
        LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
            AND (s.Cust_name IS NULL OR s.Cust_name NOT IN ({known_list_sql}))
        GROUP BY
            COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20)))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY total_sales DESC, shop_name, employee_name
        """
        params = [start_date, end_date] + branch_ids + filter_params
    else:
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH sale_lines AS (
            SELECT
                s.sale_id,
                s.Cust_name AS cust_name_raw,
                COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20)))) AS shop_name,
                COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
                li.qty,
                li.Unit_price,
                s.Nt_amount,
                SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id) AS line_total
            FROM tblSales s WITH (NOLOCK)
            JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
            LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t
                ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
            LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
            LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
            WHERE s.sale_date BETWEEN ? AND ?
                AND s.shop_id IN ({placeholders(len(branch_ids))})
                {category_clause}
                {filter_clause}
        ),
        others_sales AS (
            SELECT
                shop_name,
                employee_name,
                COUNT(DISTINCT sale_id) AS total_orders,
                SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_sales
            FROM sale_lines
            WHERE (cust_name_raw IS NULL OR cust_name_raw NOT IN ({known_list_sql}))
            GROUP BY shop_name, employee_name
        )
        SELECT * FROM others_sales ORDER BY total_sales DESC, shop_name, employee_name
        """
        params = [start_date, end_date] + branch_ids + category_params + filter_params

    try:
        t0 = time.time()
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if not df.empty and "total_sales" in df.columns:
            df["total_sales"] = df["total_sales"].astype(float)
        _log_cached_query_time("get_cached_order_type_others_order_takers", t0)
        return df
    except Exception as e:
        st.error(f"Error fetching Others order takers breakdown: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_fresh_pick_sales(
    start_date: str,
    end_date: str,
    data_mode: str
) -> pd.DataFrame:
    """Fresh Pick removed in this deployment — return empty DataFrame."""
    # Keep function available for callers but return empty DataFrame
    try:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=HEAVY_CACHE_TTL)
def get_cached_product_monthly_sales(
    year: int,
    month: int,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch product-level sales and quantity for a given month and branches."""
    # Build month date range
    try:
        start = date(year, month, 1)
        # next month start
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end = next_month - timedelta(days=1)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
    except Exception:
        # Fallback to first/last day using datetime
        start_str = f"{year}-{month:02d}-01"
        end_str = start_str

    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        COALESCE(t.field_name, '(Unmapped)') AS Product,
        SUM(li.qty) AS Total_Qty,
        SUM((li.qty * li.Unit_price) / NULLIF(st.line_total, 0) * s.Nt_amount) AS Total_Sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    JOIN (
        SELECT sale_id, SUM(qty * Unit_price) AS line_total
        FROM tblSalesLineItems WITH (NOLOCK)
        GROUP BY sale_id
    ) st ON st.sale_id = s.sale_id
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
    {category_clause}
    {filter_clause}
    GROUP BY COALESCE(t.field_name, '(Unmapped)')
    ORDER BY Total_Sales DESC
    """

    params = [start_str, end_str] + branch_ids + category_params + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        # Ensure numeric types
        if 'Total_Sales' in df.columns:
            df['Total_Sales'] = df['Total_Sales'].astype(float)
        if 'Total_Qty' in df.columns:
            df['Total_Qty'] = df['Total_Qty'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching product monthly sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=HEAVY_CACHE_TTL)
def get_cached_product_monthly_sales_by_product(
    year: int,
    month: int,
    branch_ids: List[int],
    data_mode: str,
    category: Optional[str] = None
) -> pd.DataFrame:
    """Fetch product-level sales (by product name) for a given month and branches.

    If `category` is provided, the query filters to products that map to that
    TempProductBarcode.field_name value (line-item / category).
    Returns columns: Product, Total_Qty, Total_Sales
    """
    # Build month date range
    try:
        start = date(year, month, 1)
        # next month start
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end = next_month - timedelta(days=1)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
    except Exception:
        start_str = f"{year}-{month:02d}-01"
        end_str = start_str

    filter_clause, filter_params = build_filter_clause(data_mode)
    saved_category_clause, saved_category_params = build_category_name_filter_clause("t")

    # Optional category filter
    category_clause = ""
    category_params: List = []
    if category:
        category_clause = " AND t.field_name = ?"
        category_params = [category]

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        COALESCE(p.item_name, t.field_name, '(Unmapped)') AS Product,
        SUM(li.qty) AS Total_Qty,
        SUM((li.qty * li.Unit_price) / NULLIF(st.line_total, 0) * s.Nt_amount) AS Total_Sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    JOIN (
        SELECT s.sale_id, s.shop_id, SUM(li.qty * li.Unit_price) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        GROUP BY s.sale_id, s.shop_id
    ) st ON st.sale_id = s.sale_id AND st.shop_id = s.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
    {saved_category_clause}
    {category_clause}
    {filter_clause}
    GROUP BY COALESCE(p.item_name, t.field_name, '(Unmapped)')
    ORDER BY Total_Sales DESC
    """

    params = [start_str, end_str] + branch_ids + saved_category_params + category_params + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'Total_Sales' in df.columns:
            df['Total_Sales'] = df['Total_Sales'].astype(float)
        if 'Total_Qty' in df.columns:
            df['Total_Qty'] = df['Total_Qty'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching product-level monthly sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_monthly_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch total sales aggregated by month between start_date and end_date."""

    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.sale_id,
            s.sale_date,
            s.Nt_amount,
            li.qty,
            li.Unit_price,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
    )
    SELECT
        DATEFROMPARTS(YEAR(sale_date), MONTH(sale_date), 1) AS period_date,
        YEAR(sale_date) AS year,
        MONTH(sale_date) AS month,
        SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_Nt_amount
    FROM sale_lines
    GROUP BY YEAR(sale_date), MONTH(sale_date)
    ORDER BY period_date
    """

    params = [start_date, end_date] + branch_ids + category_params + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_Nt_amount' in df.columns:
            df['total_Nt_amount'] = df['total_Nt_amount'].astype(float)
        df['period_date'] = pd.to_datetime(df['period_date'])
        return df
    except Exception as e:
        st.error(f"Error fetching monthly sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_daily_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch total sales aggregated by day between start_date and end_date."""

    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    try:
        end_date_plus1 = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    except Exception:
        end_date_plus1 = end_date

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.sale_id,
            CAST(s.sale_date AS DATE) AS day,
            s.Nt_amount,
            li.qty,
            li.Unit_price,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date >= ? AND s.sale_date < ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
    )
    SELECT
        day,
        SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_Nt_amount
    FROM sale_lines
    GROUP BY day
    ORDER BY day
    """

    params = [start_date, end_date_plus1] + branch_ids + category_params + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_Nt_amount' in df.columns:
            df['total_Nt_amount'] = df['total_Nt_amount'].astype(float)
        df['day'] = pd.to_datetime(df['day'])
        return df
    except Exception as e:
        st.error(f"Error fetching daily sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=MEDIUM_CACHE_TTL)
def get_cached_daily_sales_by_branch(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch daily sales aggregated by day and branch between start_date and end_date."""

    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    try:
        end_date_plus1 = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    except Exception:
        end_date_plus1 = end_date

    # Use pre-aggregated table when possible (unfiltered + no category filters).
    if data_mode == "Unfiltered" and not category_clause:
        agg_query = f"""
        IF OBJECT_ID('dbo.DailyBranchSalesAgg', 'U') IS NOT NULL
        BEGIN
            SELECT
                a.sale_day AS day,
                a.shop_id,
                sh.shop_name,
                a.total_sales AS total_Nt_amount
            FROM dbo.DailyBranchSalesAgg a WITH (NOLOCK)
            LEFT JOIN tblDefShops sh WITH (NOLOCK) ON a.shop_id = sh.shop_id
            WHERE a.sale_day >= ? AND a.sale_day < ?
              AND a.shop_id IN ({placeholders(len(branch_ids))})
            ORDER BY a.sale_day, a.shop_id
        END
        ELSE
        BEGIN
            SELECT CAST(NULL AS DATE) AS day, CAST(NULL AS INT) AS shop_id,
                   CAST(NULL AS VARCHAR(100)) AS shop_name, CAST(NULL AS FLOAT) AS total_Nt_amount
            WHERE 1 = 0
        END
        """
        params = [start_date, end_date_plus1] + branch_ids
        try:
            conn = pool.get_connection("candelahns")
            df = pd.read_sql(agg_query, conn, params=params)
            if not df.empty:
                if 'total_Nt_amount' in df.columns:
                    df['total_Nt_amount'] = df['total_Nt_amount'].astype(float)
                df['day'] = pd.to_datetime(df['day'])
                return df
        except Exception:
            # Fall back to raw query below if agg table missing or failed.
            pass

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.sale_id,
            CAST(s.sale_date AS DATE) AS day,
            s.shop_id,
            s.Nt_amount,
            li.qty,
            li.Unit_price,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date >= ? AND s.sale_date < ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {category_clause}
            {filter_clause}
    )
    SELECT
        sl.day,
        sl.shop_id,
        sh.shop_name,
        SUM((sl.qty * sl.Unit_price) / NULLIF(sl.line_total, 0) * sl.Nt_amount) AS total_Nt_amount
    FROM sale_lines sl
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON sl.shop_id = sh.shop_id
    GROUP BY sl.day, sl.shop_id, sh.shop_name
    ORDER BY sl.day, sl.shop_id
    """

    params = [start_date, end_date_plus1] + branch_ids + category_params + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_Nt_amount' in df.columns:
            df['total_Nt_amount'] = df['total_Nt_amount'].astype(float)
        df['day'] = pd.to_datetime(df['day'])
        return df
    except Exception as e:
        st.error(f"Error fetching daily sales by branch: {e}")
        return pd.DataFrame()


def warm_up_caches(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    target_year: int,
    target_month: int,
    include_heavy: bool = False,
) -> None:
    """Best-effort cache warm-up for commonly used queries."""
    try:
        get_cached_branch_summary(start_date, end_date, branch_ids, data_mode)
        get_cached_ot_data(start_date, end_date, branch_ids, data_mode)
        get_cached_order_types(start_date, end_date, branch_ids, data_mode)
        get_cached_daily_sales_by_branch(start_date, end_date, branch_ids, data_mode)
        get_cached_daily_sales(start_date, end_date, branch_ids, data_mode)
        get_cached_monthly_sales(start_date, end_date, branch_ids, data_mode)
        get_cached_targets(target_year, target_month)
        if include_heavy:
            get_cached_line_items(start_date, end_date, branch_ids, data_mode)
    except Exception:
        # Warm-up is best-effort; ignore errors here.
        pass


@st.cache_data(ttl=HEAVY_CACHE_TTL)
def get_cached_daily_sales_by_products(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str,
    products: List[str]
) -> pd.DataFrame:
    """Fetch daily sales for a list of products (product names) between dates.

    products: list of product names as returned by COALESCE(p.item_name, t.field_name)
    Returns columns: day, Product, total_Nt_amount
    """

    if not products:
        return pd.DataFrame()

    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")

    # Build IN clause placeholders
    prod_placeholders = ','.join(['?'] * len(products))

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        CAST(s.sale_date AS DATE) AS day,
        COALESCE(p.item_name, t.field_name) AS Product,
        SUM((li.qty * li.Unit_price) / NULLIF(st.line_total, 0) * s.Nt_amount) AS total_Nt_amount
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    JOIN (
        SELECT s.sale_id, s.shop_id, SUM(li.qty * li.Unit_price) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        GROUP BY s.sale_id, s.shop_id
    ) st ON st.sale_id = s.sale_id AND st.shop_id = s.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
        {category_clause}
        AND COALESCE(p.item_name, t.field_name) IN ({prod_placeholders})
    {filter_clause}
    GROUP BY CAST(s.sale_date AS DATE), COALESCE(p.item_name, t.field_name)
    ORDER BY Product, day
    """

    params = [start_date, end_date] + branch_ids + category_params + products + filter_params

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_Nt_amount' in df.columns:
            df['total_Nt_amount'] = df['total_Nt_amount'].astype(float)
        df['day'] = pd.to_datetime(df['day'])
        return df
    except Exception as e:
        st.error(f"Error fetching daily product sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_category_filter_coverage(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Return category-wise sales coverage and whether category is counted/excluded by saved rules."""
    if not branch_ids:
        return pd.DataFrame(columns=["category_name", "total_qty", "total_sales", "counted", "status"])

    # Remove data_mode filter to show ALL categories that have sales
    # filter_clause, filter_params = build_filter_clause(data_mode)
    filter_clause = ""
    filter_params = []

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            COALESCE(t.field_name, '(Unmapped)') AS category_name,
            li.qty AS qty,
            li.Unit_price AS unit_price,
            s.Nt_amount AS nt_amount,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id, s.shop_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
    )
    SELECT
        category_name,
        SUM(qty) AS total_qty,
        SUM((qty * unit_price) / NULLIF(line_total, 0) * nt_amount) AS total_sales
    FROM sale_lines
    GROUP BY category_name
    ORDER BY total_sales DESC
    """

    params = [start_date, end_date] + branch_ids

    try:
        conn = pool.get_connection("candelahns")
        df_sales = pd.read_sql(query, conn, params=params)
        
        # Fetch master list from KDSDB
        try:
            conn_kds = pool.get_connection("kdsdb")
            df_master_kds = pd.read_sql("SELECT category_id, category_name FROM dbo.chef_sale", conn_kds)
        except Exception:
            df_master_kds = pd.DataFrame(columns=["category_id", "category_name"])

        # Fetch additional categories from mapping table (Candelahns)
        try:
            # Fetch ALL distinct categories from TempProductBarcode
            query_mapping = """
            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT DISTINCT field_name as category_name 
            FROM TempProductBarcode WITH (NOLOCK)
            WHERE field_name IS NOT NULL AND field_name <> ''
            """
            df_master_candel = pd.read_sql(query_mapping, conn)
        except Exception:
            df_master_candel = pd.DataFrame(columns=["category_name"])


        # Combine master lists
        if not df_master_kds.empty and not df_master_candel.empty:
            df_master = pd.concat([
                df_master_kds[["category_name"]], 
                df_master_candel[["category_name"]]
            ]).drop_duplicates().reset_index(drop=True)
        elif not df_master_kds.empty:
            df_master = df_master_kds[["category_name"]].drop_duplicates()
        else:
            df_master = df_master_candel.drop_duplicates()

        if df_sales is None or df_sales.empty:
            if df_master.empty:
                return pd.DataFrame(columns=["category_name", "total_qty", "total_sales", "counted", "status", "category_id"])
            else:
                df = df_master.copy()
                df["total_qty"] = 0.0
                df["total_sales"] = 0.0
        else:
            # Start with actual sales data (authoritative names from the DB)
            df = df_sales.copy()

            # Add any master-only categories (those that exist in master but had zero sales)
            if not df_master.empty:
                existing_names = set(df["category_name"].str.strip().str.upper())
                master_only = df_master[
                    ~df_master["category_name"].str.strip().str.upper().isin(existing_names)
                ].copy()
                if not master_only.empty:
                    master_only["total_qty"] = 0.0
                    master_only["total_sales"] = 0.0
                    df = pd.concat([df, master_only[["category_name", "total_qty", "total_sales"]]], ignore_index=True)

            df["total_qty"] = pd.to_numeric(df["total_qty"], errors="coerce").fillna(0.0)
            df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce").fillna(0.0)

            
        # Ensure category_name is string and not missing
        df["category_name"] = df["category_name"].fillna("(Unmapped)")

        saved = get_saved_category_filters()
        include_names = [str(x) for x in saved.get("included_category_names", [])]
        exclude_names = [str(x) for x in saved.get("excluded_category_names", [])]

        counted_flags = []
        statuses = []
        # Use normalized sets for proper matching
        include_set = set(_normalize_category_name(str(x)) for x in include_names if str(x).strip())
        exclude_set = set(_normalize_category_name(str(x)) for x in exclude_names if str(x).strip())
        include_active = len(include_set) > 0

        for cname in df["category_name"].astype(str):
            counted = is_category_counted(cname, include_names, exclude_names)
            counted_flags.append(counted)
            # Normalize cname for comparison
            cname_normalized = _normalize_category_name(cname)
            if include_active and cname_normalized not in include_set:
                statuses.append("Excluded (not in include list)")
            elif cname_normalized in exclude_set:
                statuses.append("Excluded (explicit)")
            else:
                statuses.append("Included")

        df["counted"] = counted_flags
        df["status"] = statuses
        return df
    except Exception as e:
        st.error(f"Error fetching category coverage: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_qr_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch QR sales data with caching and category filtering"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    category_clause, category_params = build_category_name_filter_clause("t")
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH sale_lines AS (
        SELECT
            s.shop_id,
            s.employee_id,
            s.external_ref_id,
            s.external_ref_type,
            li.qty,
            li.Unit_price,
            s.Nt_amount,
            SUM(li.qty * li.Unit_price) OVER (PARTITION BY s.sale_id) AS line_total
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            AND s.external_ref_type = 'Blinkco order'
            {category_clause}
            {filter_clause}
    ),
    qr_sales_agg AS (
        SELECT
            shop_id,
            employee_id,
            external_ref_id,
            external_ref_type,
            SUM((qty * Unit_price) / NULLIF(line_total, 0) * Nt_amount) AS total_sale
        FROM sale_lines
        GROUP BY shop_id, employee_id, external_ref_id, external_ref_type
    )
    SELECT
        qs.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        qs.total_sale,
        qs.external_ref_id,
        qs.external_ref_type
    FROM qr_sales_agg qs
    LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON qs.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON qs.shop_id = sh.shop_id
    ORDER BY total_sale DESC
    """
    
    params = [start_date, end_date] + branch_ids + category_params + filter_params
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        df['total_sale'] = df['total_sale'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching QR sales: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_employee_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int]
) -> pd.DataFrame:
    """Fetch employee-wise sales breakdown with caching"""
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COUNT(DISTINCT s.sale_id) AS total_transactions,
        SUM(s.NT_amount) AS total_sales,
        SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN s.NT_amount ELSE 0 END) AS qr_sales,
        SUM(CASE WHEN s.external_ref_type != 'Blinkco order' OR s.external_ref_type IS NULL THEN s.NT_amount ELSE 0 END) AS normal_sales,
        COUNT(CASE WHEN s.external_ref_type = 'Blinkco order' THEN 1 END) AS qr_transactions,
        COUNT(CASE WHEN s.external_ref_type != 'Blinkco order' OR s.external_ref_type IS NULL THEN 1 END) AS normal_transactions,
        CASE
            WHEN SUM(s.NT_amount) > 0
            THEN (SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN s.NT_amount ELSE 0 END) * 100.0 / SUM(s.NT_amount))
            ELSE 0
        END AS qr_percentage
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
    GROUP BY 
        COALESCE(e.shop_employee_id, 0),
        COALESCE(e.field_name, 'Online/Unassigned')
    ORDER BY total_sales DESC
    """
    
    params = [start_date, end_date] + branch_ids
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'employee_id' in df.columns:
            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
        return df
    except Exception as e:
        st.error(f"Error fetching employee sales: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_targets(
    year: int,
    month: int
) -> Tuple[Dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch all targets with caching"""
    
    try:
        conn = pool.get_connection("kdsdb")

        # Some local setups keep targets in `KDS_DB` instead of `Candelahns_Targets`.
        alt_dbs = [
            x.strip()
            for x in os.environ.get("KDSDB_ALT_DATABASES", "KDS_DB,Candelahns_Targets").split(",")
            if x.strip()
        ]

        branch_table = _resolve_table_across_databases(
            conn, "branch_targets", preferred_schema="dbo", candidate_databases=alt_dbs
        )
        chef_table = _resolve_table_across_databases(
            conn, "branch_chef_targets", preferred_schema="dbo", candidate_databases=alt_dbs
        )
        ot_table = _resolve_table_across_databases(
            conn, "ot_targets", preferred_schema="dbo", candidate_databases=alt_dbs
        )

        # Branch targets
        if branch_table is None:
            _warn_once(
                "warn_missing_branch_targets",
                "Targets table `branch_targets` not found in the targets database; using built-in default targets.",
            )
            branch_targets = DEFAULT_BRANCH_TARGETS.copy()
            try:
                st.session_state["using_default_targets"] = True
            except Exception:
                pass
        else:
            try:
                if _table_supports_period_filters(conn, branch_table):
                    df_branch_targets = pd.read_sql(
                        f"SELECT shop_id, monthly_target FROM {branch_table} WHERE target_year = ? AND target_month = ?",
                        conn,
                        params=(year, month),
                    )
                elif _table_supports_target_date(conn, branch_table):
                    df_branch_targets = pd.read_sql(
                        f"SELECT shop_id, monthly_target FROM {branch_table} WHERE target_date = ?",
                        conn,
                        params=(date(year, month, 1),),
                    )
                    _warn_once(
                        "warn_branch_targets_no_period_cols",
                        "branch_targets is missing target_year/target_month; filtering by target_date instead.",
                    )
                else:
                    df_branch_targets = pd.read_sql(
                        f"SELECT shop_id, monthly_target FROM {branch_table}",
                        conn,
                    )
                    _warn_once(
                        "warn_branch_targets_no_period_cols",
                        "branch_targets is missing period columns; using unfiltered targets table.",
                    )
                branch_targets = dict(zip(df_branch_targets["shop_id"], df_branch_targets["monthly_target"]))
            except Exception as e:
                _warn_once(
                    "warn_branch_targets_query_failed",
                    f"Failed to read branch_targets ({e}); using built-in default targets.",
                )
                branch_targets = DEFAULT_BRANCH_TARGETS.copy()
                try:
                    st.session_state["using_default_targets"] = True
                except Exception:
                    pass

            # Chef targets
            if chef_table is None:
                _warn_once(
                    "warn_missing_chef_targets",
                    "Chef targets table `branch_chef_targets` not found; Chef Targets tab will show empty targets.",
                )
                df_chef_targets = pd.DataFrame()
            else:
                try:
                    if _table_supports_period_filters(conn, chef_table):
                        df_chef_targets = pd.read_sql(
                            f"SELECT shop_id, category_id, monthly_target as target_amount, target_type FROM {chef_table} WHERE target_year = ? AND target_month = ?",
                            conn,
                            params=(year, month),
                        )
                    elif _table_supports_target_date(conn, chef_table):
                        df_chef_targets = pd.read_sql(
                            f"SELECT shop_id, category_id, monthly_target as target_amount, target_type FROM {chef_table} WHERE target_date = ?",
                            conn,
                            params=(date(year, month, 1),),
                        )
                        _warn_once(
                            "warn_chef_targets_no_period_cols",
                            "branch_chef_targets is missing target_year/target_month; filtering by target_date instead.",
                        )
                    else:
                        df_chef_targets = pd.read_sql(
                            f"SELECT shop_id, category_id, monthly_target as target_amount, target_type FROM {chef_table}",
                            conn,
                        )
                        _warn_once(
                            "warn_chef_targets_no_period_cols",
                            "branch_chef_targets is missing period columns; using unfiltered targets table.",
                        )
                except Exception as e:
                    _warn_once(
                        "warn_chef_targets_query_failed",
                        f"Failed to read branch_chef_targets ({e}); Chef Targets will be empty targets.",
                    )
                    df_chef_targets = pd.DataFrame()

            # Local overrides (e.g., April 2026 targets) merged on top of DB targets.
        # OT targets
        if ot_table is None:
            _warn_once(
                "warn_missing_ot_targets",
                "OT targets table `ot_targets` not found; OT Targets tab will show empty targets.",
            )
            df_ot_targets = pd.DataFrame()
        else:
            try:
                # Prefer period filtering. If the table schema doesn't support it, fall back.
                try:
                    df_ot_targets = pd.read_sql(
                        f"SELECT shop_id, employee_id, monthly_target as target_amount FROM {ot_table} WHERE target_year = ? AND target_month = ?",
                        conn,
                        params=(year, month),
                    )
                except Exception as e_period:
                    if _has_sqlstate(e_period, "42S22"):
                        if _table_supports_target_date(conn, ot_table):
                            df_ot_targets = pd.read_sql(
                                f"SELECT shop_id, employee_id, monthly_target as target_amount FROM {ot_table} WHERE target_date = ?",
                                conn,
                                params=(date(year, month, 1),),
                            )
                            _warn_once(
                                "warn_ot_targets_no_period_cols",
                                "ot_targets is missing target_year/target_month; filtering by target_date instead.",
                            )
                        else:
                            df_ot_targets = pd.read_sql(
                                f"SELECT shop_id, employee_id, monthly_target as target_amount FROM {ot_table}",
                                conn,
                            )
                            _warn_once(
                                "warn_ot_targets_no_period_cols",
                                "ot_targets is missing period columns; using unfiltered targets table.",
                            )
                    else:
                        raise
            except Exception as e:
                # 42S22 = missing column, treat as schema mismatch and continue without failing the whole targets fetch.
                if _has_sqlstate(e, "42S22"):
                    _warn_once(
                        "warn_ot_targets_schema_mismatch",
                        "ot_targets schema is missing period columns; using unfiltered ot_targets table.",
                    )
                    try:
                        df_ot_targets = pd.read_sql(
                            f"SELECT shop_id, employee_id, monthly_target as target_amount FROM {ot_table}",
                            conn,
                        )
                    except Exception as e2:
                        _warn_once(
                            "warn_ot_targets_query_failed",
                            f"Failed to read ot_targets ({e2}); OT Targets will be empty.",
                        )
                        df_ot_targets = pd.DataFrame()
                else:
                    _warn_once(
                        "warn_ot_targets_query_failed",
                        f"Failed to read ot_targets ({e}); OT Targets will be empty.",
                    )
                    df_ot_targets = pd.DataFrame()
        
        # Fresh Pick targets removed in this deployment
        df_fresh_targets = pd.DataFrame()
        
        # Clear flag indicating default targets are in use
        try:
            if branch_table is not None:
                st.session_state["using_default_targets"] = False
        except Exception:
            # session_state may not be available in some contexts; ignore safely
            pass

        return branch_targets, df_chef_targets, df_ot_targets, df_fresh_targets
        
    except Exception as e:
        # Warn and mark that built-in defaults are being used
        st.warning(f"Error fetching targets: {e} - using built-in default targets.")
        try:
            st.session_state['using_default_targets'] = True
        except Exception:
            # session_state might not be available in some contexts
            pass

        return DEFAULT_BRANCH_TARGETS.copy(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ========================
# RAMZAN DEALS QUERIES
# ========================

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_ramzan_product_master() -> pd.DataFrame:
    """Fetch product master for Ramzan Deal products (Product_code 701,703-709)."""
    from modules.config import RAMZAN_DEALS_PRODUCT_IDS
    codes_str = ",".join([f"'{code}'" for code in RAMZAN_DEALS_PRODUCT_IDS])
    query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            pi.Product_Item_ID,
            p.Product_code,
            p.item_name
        FROM tblDefProducts p WITH (NOLOCK)
        INNER JOIN tblProductItem pi WITH (NOLOCK)
            ON p.Product_ID = pi.Product_ID
        WHERE p.Product_code IN ({codes_str})
    """
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn)
        if 'employee_id' in df.columns:
            df['employee_id'] = pd.to_numeric(df['employee_id'], errors='coerce').fillna(0).astype('int64')
        return df
    except Exception as e:
        st.error(f"Error fetching Ramzan product master: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_ramzan_deals_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    product_item_ids: Optional[List[int]] = None
) -> pd.DataFrame:
    """Fetch branch-wise sales for Ramzan Deal products.

    Parameters
    ----------
    start_date, end_date : date range strings (YYYY-MM-DD)
    branch_ids : list of shop_ids to include
    product_item_ids : optional filter to a subset of Ramzan product IDs;
                       defaults to all RAMZAN_DEALS_PRODUCT_IDS
    """
    from modules.config import RAMZAN_DEALS_PRODUCT_IDS
    if not branch_ids:
        return pd.DataFrame()

    codes_str = ",".join([f"'{code}'" for code in RAMZAN_DEALS_PRODUCT_IDS])
    product_filter_clause = ""
    if product_item_ids:
        ids_str = ",".join(map(str, product_item_ids))
        product_filter_clause = f" AND pi.Product_Item_ID IN ({ids_str})"

    query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT  
            sh.shop_id,
            sh.shop_name,
            pi.Product_Item_ID,
            p.Product_code,
            p.item_name,
            ISNULL(SUM(sales_data.qty),0) AS total_qty,
            ISNULL(SUM(sales_data.qty * sales_data.Unit_price),0) AS total_sales
        FROM tblDefShops sh WITH (NOLOCK)
        CROSS JOIN tblProductItem pi WITH (NOLOCK)
        INNER JOIN tblDefProducts p WITH (NOLOCK)
            ON pi.Product_ID = p.Product_ID
        LEFT JOIN (
            SELECT 
                s.shop_id,
                li.Product_Item_ID,
                li.qty,
                li.Unit_price
            FROM tblSales s WITH (NOLOCK)
            INNER JOIN tblSalesLineItems li WITH (NOLOCK)
                ON s.sale_id = li.sale_id
            WHERE CAST(s.sale_date AS date) BETWEEN ? AND ?
        ) sales_data
            ON sales_data.shop_id = sh.shop_id
            AND sales_data.Product_Item_ID = pi.Product_Item_ID
        WHERE
            sh.shop_id IN ({placeholders(len(branch_ids))})
            AND p.Product_code IN ({codes_str})
            {product_filter_clause}
        GROUP BY
            sh.shop_id,
            sh.shop_name,
            pi.Product_Item_ID,
            p.Product_code,
            p.item_name
        ORDER BY
            sh.shop_id,
            p.Product_code
    """

    params = [start_date, end_date] + branch_ids

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if 'total_qty' in df.columns:
            df['total_qty'] = df['total_qty'].astype(float)
        if 'total_sales' in df.columns:
            df['total_sales'] = df['total_sales'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching Ramzan deals sales: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_unmapped_products(
    start_date: str,
    end_date: str,
    branch_ids: List[int]
) -> pd.DataFrame:
    """Fetch products that are not mapped to any category in TempProductBarcode."""
    if not branch_ids:
        return pd.DataFrame()

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT
            li.Product_code,
            COALESCE(p.item_name, '(Unknown)') AS Product_name,
            SUM(li.qty) AS total_qty,
            SUM((li.qty * li.Unit_price) / NULLIF(st.line_total, 0) * s.Nt_amount) AS total_sales
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.Product_ID
        LEFT JOIN (SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642, '0570', 'Deals') t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
        JOIN (
            SELECT sale_id, SUM(qty * Unit_price) AS line_total
            FROM tblSalesLineItems WITH (NOLOCK)
            GROUP BY sale_id
        ) st ON st.sale_id = s.sale_id
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            AND (t.field_name IS NULL OR t.field_name = '' OR t.field_name = '(Unmapped)')
        GROUP BY li.Product_code, COALESCE(p.item_name, '(Unknown)')
        ORDER BY total_sales DESC
        """
    
    params = [start_date, end_date] + branch_ids
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error fetching unmapped products: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_qr_daily_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> pd.DataFrame:
    """Fetch QR daily sales summary with caching"""
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH daily_sales AS (
        SELECT
            CAST(s.sale_date AS DATE) AS sale_date,
            COUNT(DISTINCT s.sale_id) AS transaction_count,
            SUM(s.Nt_amount) AS total_sale,
            SUM(s.Nt_amount) * 2.0 / 100 AS Candelahns_commission,
            0 AS Indoge_total_price,
            0 AS Indoge_commission
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date >= ? AND s.sale_date < ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            AND s.external_ref_type = 'Blinkco order'
        GROUP BY CAST(s.sale_date AS DATE)
    )
    SELECT
        sale_date,
        transaction_count,
        total_sale,
        Candelahns_commission,
        Indoge_total_price,
        Indoge_commission
    FROM daily_sales
    ORDER BY sale_date DESC
    """
    
    params = [start_date, end_date] + branch_ids
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['total_sale'] = df['total_sale'].astype(float)
        df['Candelahns_commission'] = df['Candelahns_commission'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching QR daily summary: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_qr_employee_daily_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> pd.DataFrame:
    """Fetch QR employee daily breakdown with caching"""
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH emp_daily_sales AS (
        SELECT
            CAST(s.sale_date AS DATE) AS sale_date,
            sh.shop_name,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS transaction_count,
            SUM(s.Nt_amount) AS total_sale,
            SUM(s.Nt_amount) * 2.0 / 100 AS Candelahns_commission,
            0 AS Indoge_total_price,
            0 AS Indoge_commission
        FROM tblSales s WITH (NOLOCK)
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ? AND s.sale_date < ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            AND s.external_ref_type = 'Blinkco order'
        GROUP BY CAST(s.sale_date AS DATE), sh.shop_name, e.field_name
    )
    SELECT
        sale_date,
        shop_name,
        employee_name,
        transaction_count,
        total_sale,
        Candelahns_commission,
        Indoge_total_price,
        Indoge_commission
    FROM emp_daily_sales
    ORDER BY sale_date DESC, total_sale DESC
    """
    
    params = [start_date, end_date] + branch_ids
    
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['total_sale'] = df['total_sale'].astype(float)
        df['Candelahns_commission'] = df['Candelahns_commission'].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching QR employee daily breakdown: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_branch_days_since_last_sale(
    branch_ids: List[int],
) -> pd.DataFrame:
    """Return last sale date + days since last sale for selected branches."""
    if not branch_ids:
        return pd.DataFrame(columns=["shop_id", "shop_name", "last_sale_date", "days_since_last_sale"])

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        s.shop_id,
        COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20)))) AS shop_name,
        MAX(CAST(s.sale_date AS DATE)) AS last_sale_date,
        DATEDIFF(day, MAX(CAST(s.sale_date AS DATE)), CAST(GETDATE() AS DATE)) AS days_since_last_sale
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON sh.shop_id = s.shop_id
    WHERE s.shop_id IN ({placeholders(len(branch_ids))})
    GROUP BY s.shop_id, COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20))))
    ORDER BY s.shop_id;
    """
    params = branch_ids

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["last_sale_date"] = pd.to_datetime(df["last_sale_date"], errors="coerce")
            df["days_since_last_sale"] = pd.to_numeric(df["days_since_last_sale"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error fetching branch recency diagnostics: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_database_orphan_summary() -> pd.DataFrame:
    """Return orphan counts for core sales relations."""
    query = """
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        (SELECT SUM(CASE WHEN s.sale_id IS NULL THEN 1 ELSE 0 END)
         FROM tblSalesLineItems li WITH (NOLOCK)
         LEFT JOIN tblSales s WITH (NOLOCK) ON s.sale_id = li.sale_id) AS lineitem_without_sale,
        (SELECT SUM(CASE WHEN li.sale_id IS NULL THEN 1 ELSE 0 END)
         FROM tblSales s WITH (NOLOCK)
         LEFT JOIN (SELECT DISTINCT sale_id FROM tblSalesLineItems WITH (NOLOCK)) li
             ON li.sale_id = s.sale_id) AS sales_without_lineitems;
    """
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching orphan diagnostics: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_database_range_quality(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> pd.DataFrame:
    """Return core data-quality stats for selected date range and branches."""
    if not branch_ids:
        return pd.DataFrame()

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COUNT(*) AS rows_total,
        COUNT(DISTINCT s.sale_id) AS distinct_sales,
        SUM(CASE WHEN s.Cust_name IS NULL THEN 1 ELSE 0 END) AS cust_name_null,
        SUM(CASE WHEN s.Cust_name = '' THEN 1 ELSE 0 END) AS cust_name_blank,
        SUM(CASE WHEN s.Cust_name IS NOT NULL AND LTRIM(RTRIM(s.Cust_name)) = '' THEN 1 ELSE 0 END) AS cust_name_whitespace,
        SUM(CASE WHEN s.NT_amount IS NULL THEN 1 ELSE 0 END) AS nt_amount_null,
        SUM(CASE WHEN s.NT_amount < 0 THEN 1 ELSE 0 END) AS nt_amount_negative,
        SUM(CASE WHEN s.sale_date IS NULL THEN 1 ELSE 0 END) AS sale_date_null
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))});
    """
    params = [start_date, end_date] + branch_ids

    try:
        conn = pool.get_connection("candelahns")
        return pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.error(f"Error fetching range quality diagnostics: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_filter_impact_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
) -> pd.DataFrame:
    """Return unfiltered vs filtered impact summary for selected range and branches."""
    if not branch_ids:
        return pd.DataFrame()

    filtered_clause, filtered_params = build_filter_clause("Filtered")

    q_unfiltered = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COUNT(DISTINCT s.sale_id) AS orders_unfiltered,
        SUM(s.NT_amount) AS sales_unfiltered
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))});
    """
    q_filtered = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COUNT(DISTINCT s.sale_id) AS orders_filtered,
        SUM(s.NT_amount) AS sales_filtered
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filtered_clause};
    """
    q_blocked_name = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COUNT(DISTINCT s.sale_id) AS blocked_name_orders,
        SUM(s.NT_amount) AS blocked_name_sales
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.Cust_name IN ({placeholders(len(BLOCKED_NAMES))});
    """
    q_blocked_comment = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COUNT(DISTINCT s.sale_id) AS blocked_comment_orders,
        SUM(s.NT_amount) AS blocked_comment_sales
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.Additional_Comments IN ({placeholders(len(BLOCKED_COMMENTS))});
    """

    base_params = [start_date, end_date] + branch_ids
    filtered_query_params = base_params + filtered_params
    blocked_name_params = base_params + BLOCKED_NAMES
    blocked_comment_params = base_params + BLOCKED_COMMENTS

    try:
        conn = pool.get_connection("candelahns")
        df_unf = pd.read_sql(q_unfiltered, conn, params=base_params)
        df_flt = pd.read_sql(q_filtered, conn, params=filtered_query_params)
        df_bname = pd.read_sql(q_blocked_name, conn, params=blocked_name_params)
        df_bcomment = pd.read_sql(q_blocked_comment, conn, params=blocked_comment_params)

        if df_unf.empty or df_flt.empty or df_bname.empty or df_bcomment.empty:
            return pd.DataFrame()

        out = pd.concat([df_unf, df_flt, df_bname, df_bcomment], axis=1)
        for col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
        out["orders_excluded_est"] = out["orders_unfiltered"] - out["orders_filtered"]
        out["sales_excluded_est"] = out["sales_unfiltered"] - out["sales_filtered"]
        return out
    except Exception as e:
        st.error(f"Error fetching filter impact diagnostics: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_stale_branches_all() -> pd.DataFrame:
    """Return days since last sale for all branches present in tblSales."""
    query = """
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        s.shop_id,
        COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20)))) AS shop_name,
        MAX(CAST(s.sale_date AS DATE)) AS last_sale_date,
        DATEDIFF(day, MAX(CAST(s.sale_date AS DATE)), CAST(GETDATE() AS DATE)) AS days_since_last_sale
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON sh.shop_id = s.shop_id
    GROUP BY s.shop_id, COALESCE(sh.shop_name, CONCAT('Branch ', CAST(s.shop_id AS VARCHAR(20))))
    ORDER BY days_since_last_sale DESC, s.shop_id;
    """

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn)
        if not df.empty:
            df["last_sale_date"] = pd.to_datetime(df["last_sale_date"], errors="coerce")
            df["days_since_last_sale"] = pd.to_numeric(df["days_since_last_sale"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error fetching stale branch diagnostics: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_branch_lookup(branch_ids: List[int]) -> pd.DataFrame:
    """Return shop_id/shop_name lookup from tblDefShops for provided branch ids."""
    if not branch_ids:
        return pd.DataFrame(columns=["shop_id", "shop_name"])

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        sh.shop_id,
        sh.shop_name
    FROM tblDefShops sh WITH (NOLOCK)
    WHERE sh.shop_id IN ({placeholders(len(branch_ids))})
    ORDER BY sh.shop_id;
    """
    params = branch_ids

    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn, params=params)
        if not df.empty:
            df["shop_id"] = pd.to_numeric(df["shop_id"], errors="coerce").astype("Int64")
        return _filter_excluded_branches(df)
    except Exception as e:
        _warn_once("branch_lookup_error", f"Branch lookup unavailable (DB connection). Details: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def get_cached_all_branches_lookup() -> pd.DataFrame:
    """Return shop_id/shop_name lookup for all branches in tblDefShops."""
    query = """
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        sh.shop_id,
        sh.shop_name
    FROM tblDefShops sh WITH (NOLOCK)
    ORDER BY sh.shop_id;
    """
    try:
        conn = pool.get_connection("candelahns")
        df = pd.read_sql(query, conn)
        if not df.empty:
            df["shop_id"] = pd.to_numeric(df["shop_id"], errors="coerce").astype("Int64")
        return _filter_excluded_branches(df)
    except Exception as e:
        _warn_once("all_branch_lookup_error", f"All-branch lookup unavailable (DB connection). Details: {e}")
        return pd.DataFrame()


# ========================
# CACHE MANAGEMENT
# ========================
def refresh_all_caches():
    """Clear all cached data"""
    st.cache_data.clear()
    st.success("All caches cleared!")
