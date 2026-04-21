import pyodbc
import pandas as pd
from datetime import datetime
import sys
import re

def get_conn_str():
    return "DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.86.55.34,50908;DATABASE=HNSYGCC;UID=sa;PWD=123;Encrypt=yes;TrustServerCertificate=yes;"

def test_queries():
    conn_str = get_conn_str()
    start_date = "2026-04-01"
    end_date = "2026-04-19"
    
    file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    try:
        with pyodbc.connect(conn_str) as conn:
            # 1. Test _fetch_latest_snapshot
            print("Testing _fetch_latest_snapshot...")
            match = re.search(r'_fetch_latest_snapshot\(_self\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn)
                print("_fetch_latest_snapshot: SUCCESS")
            
            # 2. Test _fetch_summary
            print("Testing _fetch_summary...")
            match = re.search(r'_fetch_summary\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn, params=[start_date, end_date])
                print("_fetch_summary: SUCCESS")

            # 3. Test _fetch_summary_xls_aligned
            print("Testing _fetch_summary_xls_aligned...")
            match = re.search(r'_fetch_summary_xls_aligned\(_self, start_date: str, end_date: str, cutoff_hour: int = 4, cutoff_minute: int = 10\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                start_ts = "2026-04-01 04:10:00"
                end_ts = "2026-04-20 04:10:00"
                pd.read_sql(match.group(1), conn, params=[start_ts, end_ts])
                print("_fetch_summary_xls_aligned: SUCCESS")

            # 4. Test _fetch_daily_sales
            print("Testing _fetch_daily_sales...")
            match = re.search(r'_fetch_daily_sales\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if match:
                pd.read_sql(match.group(1), conn, params=[start_date, end_date])
                print("_fetch_daily_sales: SUCCESS")

            # 5. Test _fetch_area_sales
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
