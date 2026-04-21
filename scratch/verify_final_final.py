import pyodbc
import pandas as pd
from datetime import datetime
import sys
import re

# Connection string helper from the dashboard
def get_conn_str():
    return "DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.86.55.34,50908;DATABASE=HNSYGCC;UID=sa;PWD=123;Encrypt=yes;TrustServerCertificate=yes;"

def test_queries():
    conn_str = get_conn_str()
    start_date = "2026-04-01"
    end_date = "2026-04-19"
    
    file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 1. Static check for broken commas
    error_patterns = [
        "SUM(total_discount,)",
        "total_discount\s+SUM", # Missing comma
    ]
    
    found_errors = False
    
    # Re-check for the specific missing comma pattern
    if re.search(r"AS total_discount\s+SUM\(", code, re.IGNORECASE):
        print("CRITICAL ERROR: Found missing comma between total_discount and next SUM!")
        found_errors = True

    if not found_errors:
        print("Static check passed: No obvious missing commas found between total_discount and SUM.")

    # 2. Test execution of queries
    try:
        with pyodbc.connect(conn_str) as conn:
            # Test _fetch_latest_snapshot
            print("Testing _fetch_latest_snapshot...")
            match = re.search(r'_fetch_latest_snapshot\(_self\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn)
                print("_fetch_latest_snapshot: SUCCESS")
            
            # Test _fetch_summary
            print("Testing _fetch_summary...")
            match = re.search(r'_fetch_summary\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn, params=[start_date, end_date])
                print("_fetch_summary: SUCCESS")

            # Test _fetch_daily_sales
            print("Testing _fetch_daily_sales...")
            match = re.search(r'_fetch_daily_sales\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn, params=[start_date, end_date])
                print("_fetch_daily_sales: SUCCESS")

            # Test _fetch_area_sales
            print("Testing _fetch_area_sales...")
            match = re.search(r'_fetch_area_sales\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn, params=[start_date, end_date])
                print("_fetch_area_sales: SUCCESS")

    except Exception as e:
        print(f"SQL EXECUTION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_queries()
