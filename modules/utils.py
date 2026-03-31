"""
Utility Functions Module
Helper functions for formatting, calculations, exports, etc.
"""

import pandas as pd
import io
import time
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from typing import Tuple, Union
import streamlit as st
import re

# ========================
# FORMATTING FUNCTIONS
# ========================

# Online/Unassigned rows should not be counted in employee-level analytics by default.
EXCLUDED_EMPLOYEE_NAMES = {"online/unassigned"}


def exclude_employee_names(
    df: pd.DataFrame,
    column: str = "employee_name",
    excluded_names: set[str] | None = None,
) -> pd.DataFrame:
    """
    Remove non-attributed employee rows (e.g., Online/Unassigned) from analytics tables.

    Note: This is a display/analytics helper; SQL-level inclusion is controlled elsewhere.
    """
    if df is None or df.empty or column not in df.columns:
        return df
    excluded = excluded_names or EXCLUDED_EMPLOYEE_NAMES
    normalized = df[column].astype(str).str.strip().str.lower()
    return df[~normalized.isin(excluded)].copy()

def format_currency(value: Union[int, float]) -> str:
    """Format number as PKR currency"""
    try:
        if pd.isna(value) or value is None:
            return "PKR 0"
        return f"PKR {float(value):,.0f}"
    except:
        return "PKR 0"

def format_percentage(value: Union[int, float]) -> str:
    """Format number as percentage"""
    try:
        if pd.isna(value) or value is None:
            return "0.0%"
        return f"{float(value):.1f}%"
    except:
        return "0.0%"

def format_number(value: Union[int, float]) -> str:
    """Format number with thousand separators"""
    try:
        if pd.isna(value) or value is None:
            return "0"
        return f"{float(value):,.0f}"
    except:
        return "0"

# ========================
# CALCULATION FUNCTIONS
# ========================

def calculate_achievement(current: float, target: float) -> float:
    """Calculate achievement percentage"""
    try:
        if target == 0 or pd.isna(target):
            return 0.0
        return (float(current) / float(target)) * 100
    except:
        return 0.0

def calculate_growth(current: float, previous: float) -> float:
    """Calculate growth percentage"""
    try:
        if previous == 0 or pd.isna(previous):
            return 0.0
        return ((float(current) - float(previous)) / float(previous)) * 100
    except:
        return 0.0

def calculate_variance(actual: float, budgeted: float) -> float:
    """Calculate variance"""
    try:
        return float(actual) - float(budgeted)
    except:
        return 0.0

# ========================
# DATE PRESET FUNCTIONS
# ========================

def get_date_presets(preset: str) -> Tuple[date, date]:
    """Get date range based on preset"""
    
    today = datetime.now().date()
    
    if preset == "Today":
        return today, today
    
    elif preset == "Yesterday":
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    
    elif preset == "This Week":
        start = today - timedelta(days=today.weekday())
        return start, today
    
    elif preset == "Last Week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start, end
    
    elif preset == "This Month":
        start = today.replace(day=1)
        return start, today
    
    elif preset == "Last Month":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        return first_day_last_month, last_day_last_month
    
    elif preset == "This Quarter":
        quarter = (today.month - 1) // 3
        start = date(today.year, quarter * 3 + 1, 1)
        return start, today
    
    elif preset == "This Year":
        start = date(today.year, 1, 1)
        return start, today
    
    else:  # Custom
        start = today.replace(day=1)
        return start, today

# ========================
# EXPORT FUNCTIONS
# ========================

def _sanitize_sheet_name(name: str) -> str:
    safe = re.sub(r"[\[\]\:\*\?\/\\]", " ", str(name)).strip()
    safe = re.sub(r"\s+", " ", safe) or "Sheet"
    return safe[:31]


def _format_worksheet(worksheet) -> None:
    worksheet.freeze_panes = "A2"
    try:
        worksheet.auto_filter.ref = worksheet.dimensions
    except Exception:
        pass
    for cell in worksheet[1]:
        cell.font = cell.font.copy(bold=True)
        cell.fill = cell.fill.copy(fgColor="366092")
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)


def export_to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Export a single dataframe to one-sheet excel with standardized formatting."""
    return export_excel(df, sheet_name=sheet_name)


def export_tables_to_excel(tables: dict[str, pd.DataFrame]) -> bytes:
    """
    Export multiple DataFrames into a single Excel workbook (multi-sheet) with:
    - frozen header row
    - AutoFilter enabled
    - simple header styling
    - auto column widths
    """

    output = io.BytesIO()
    used: dict[str, int] = {}

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for raw_name, df in (tables or {}).items():
            if df is None:
                continue
            sheet = _sanitize_sheet_name(raw_name)
            if sheet in used:
                used[sheet] += 1
                suffix = f" ({used[sheet]})"
                sheet = (sheet[: max(0, 31 - len(suffix))] + suffix).strip()
            else:
                used[sheet] = 1

            df.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.sheets[sheet]
            _format_worksheet(ws)

    output.seek(0)
    return output.getvalue()


def export_excel(data, sheet_name: str = "Sheet1") -> bytes:
    """
    Unified excel export helper:
    - pd.DataFrame -> single-sheet workbook
    - dict[str, pd.DataFrame] -> multi-sheet workbook
    """
    if isinstance(data, dict):
        return export_tables_to_excel(data)

    output = io.BytesIO()
    sheet = _sanitize_sheet_name(sheet_name)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name=sheet, index=False)
        ws = writer.sheets[sheet]
        _format_worksheet(ws)
    output.seek(0)
    return output.getvalue()

# ========================
# LOGGING FUNCTIONS
# ========================

def log_query_time(query_name: str, execution_time: float):
    """Log query execution time"""
    
    # Initialize log if not exists
    if 'query_log' not in st.session_state:
        st.session_state.query_log = []
    
    # Add log entry
    log_entry = {
        'timestamp': datetime.now(),
        'query': query_name,
        'time': execution_time
    }
    
    st.session_state.query_log.append(log_entry)
    
    # Keep only last 100 entries
    if len(st.session_state.query_log) > 100:
        st.session_state.query_log = st.session_state.query_log[-100:]

def get_query_statistics() -> pd.DataFrame:
    """Get query performance statistics"""
    
    if 'query_log' not in st.session_state or not st.session_state.query_log:
        return pd.DataFrame()
    
    df = pd.DataFrame(st.session_state.query_log)
    
    # Calculate statistics
    stats = df.groupby('query').agg({
        'time': ['count', 'mean', 'min', 'max', 'std']
    }).round(4)
    
    return stats

# ========================
# PERFORMANCE TRACE
# ========================

def perf_trace_reset() -> None:
    """Reset in-session performance trace list."""
    st.session_state["perf_trace_events"] = []

def perf_trace_enabled() -> bool:
    """Return True if performance tracing is enabled."""
    return bool(st.session_state.get("perf_trace_enabled", False))

@contextmanager
def perf_trace(label: str, group: str = "general"):
    """Context manager to record timing for a labeled step."""
    if not perf_trace_enabled():
        yield
        return
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000.0
        entry = {
            "timestamp": datetime.now(),
            "group": group,
            "label": label,
            "ms": round(duration_ms, 2),
        }
        st.session_state.setdefault("perf_trace_events", []).append(entry)

def get_perf_trace_df() -> pd.DataFrame:
    """Return performance trace events as a DataFrame."""
    events = st.session_state.get("perf_trace_events", [])
    if not events:
        return pd.DataFrame()
    df = pd.DataFrame(events)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df

def persist_perf_trace(path: str) -> None:
    """Append performance trace events to a CSV file."""
    df = get_perf_trace_df()
    if df.empty:
        return
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_header = not os.path.exists(path)
    df.to_csv(path, mode="a", header=write_header, index=False, encoding="utf-8")

# ========================
# DATA VALIDATION
# ========================

def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate date range"""
    
    if start_date > end_date:
        st.error("Start date cannot be after end date.")
        return False
    
    # Check if range is too large (> 1 year)
    if (end_date - start_date).days > 365:
        st.warning("Date range exceeds 1 year. This may slow down performance.")
    
    return True

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """Validate DataFrame has required columns"""
    
    if df.empty:
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return False
    
    return True

# ========================
# DATA PROCESSING
# ========================

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame - remove nulls, duplicates, etc."""
    
    if df.empty:
        return df
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Fill numeric nulls with 0
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Fill string nulls with empty string
    string_columns = df.select_dtypes(include=['object']).columns
    df[string_columns] = df[string_columns].fillna('')
    
    return df

def aggregate_data(df: pd.DataFrame, group_by: list, agg_dict: dict) -> pd.DataFrame:
    """Aggregate DataFrame by specified columns"""
    
    if df.empty:
        return df
    
    try:
        df_agg = df.groupby(group_by).agg(agg_dict).reset_index()
        return df_agg
    except Exception as e:
        st.error(f"Error aggregating data: {e}")
        return pd.DataFrame()

# ========================
# HELPER FUNCTIONS
# ========================

def generate_summary_stats(df: pd.DataFrame, value_column: str) -> dict:
    """Generate summary statistics for a column"""
    
    if df.empty or value_column not in df.columns:
        return {}
    
    return {
        'count': len(df),
        'sum': df[value_column].sum(),
        'mean': df[value_column].mean(),
        'median': df[value_column].median(),
        'std': df[value_column].std(),
        'min': df[value_column].min(),
        'max': df[value_column].max()
    }

def create_comparison_dataframe(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    join_on: str,
    value_col: str,
    labels: Tuple[str, str]
) -> pd.DataFrame:
    """Create comparison DataFrame from two DataFrames"""
    
    if df1.empty or df2.empty:
        return pd.DataFrame()
    
    # Merge DataFrames
    df_merged = pd.merge(
        df1[[join_on, value_col]],
        df2[[join_on, value_col]],
        on=join_on,
        suffixes=(f'_{labels[0]}', f'_{labels[1]}')
    )
    
    # Calculate variance and growth
    col1 = f'{value_col}_{labels[0]}'
    col2 = f'{value_col}_{labels[1]}'
    
    df_merged['Variance'] = df_merged[col1] - df_merged[col2]
    df_merged['Growth_%'] = calculate_growth(df_merged[col1], df_merged[col2])
    
    return df_merged

def get_top_performers(
    df: pd.DataFrame,
    name_col: str,
    value_col: str,
    top_n: int = 10
) -> pd.DataFrame:
    """Get top N performers from DataFrame"""
    
    if df.empty:
        return df
    
    return df.nlargest(top_n, value_col)[[name_col, value_col]]

def get_bottom_performers(
    df: pd.DataFrame,
    name_col: str,
    value_col: str,
    bottom_n: int = 10
) -> pd.DataFrame:
    """Get bottom N performers from DataFrame"""
    
    if df.empty:
        return df
    
    return df.nsmallest(bottom_n, value_col)[[name_col, value_col]]
