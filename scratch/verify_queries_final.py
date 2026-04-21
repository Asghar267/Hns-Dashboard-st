import pyodbc
import pandas as pd
from datetime import datetime

# Connection string helper from the dashboard
def get_conn_str():
    return "DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.86.55.34,50908;DATABASE=HNSYGCC;UID=sa;PWD=123;Encrypt=yes;TrustServerCertificate=yes;"

def test_queries():
    conn_str = get_conn_str()
    start_date = "2026-04-01"
    end_date = "2026-04-19"
    
    # We'll just define the queries used in the dashboard to test them
    # But wait, it's easier to just import the class if possible 
    # but the environment might not have all dependencies for streamlit.
    # So I'll manually check the queries for basic syntax errors by running them.

    queries = []
    
    # 1. _fetch_summary (simplified)
    queries.append("""
        WITH base AS (
            SELECT
                [datetime],
                CAST(ISNULL(subTotal, 0) AS DECIMAL(18, 2)) AS subtotal,
                CAST(ISNULL(taxAmount, 0) AS DECIMAL(18, 2)) AS tax_amount,
                CAST(ISNULL(deliveryCharges, 0) AS DECIMAL(18, 2)) AS delivery_charges,
                CAST(ISNULL(totalWithTax, 0) AS DECIMAL(18, 2)) AS total_with_tax,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount,
                0 AS total_discount
            FROM dbo.orderMaster
            WHERE [datetime] >= '2026-04-01' AND [datetime] < '2026-04-20'
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT COUNT(*) as total_orders, SUM(net_amount) as total_net FROM base;
    """)

    # 2. _fetch_daily_sales (The one that was broken)
    # I'll check if it still has trailing commas or non-aggregated net_amount
    # Read the file directly to see the code
    file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    error_patterns = [
        "SUM(total_discount,)",
        "SUM(total_discount ,)",
        "SUM(net_amount,) ",
        "AVG(gross_before_discount - total_discount,)"
    ]
    
    found_errors = False
    for p in error_patterns:
        if p in code:
            print(f"CRITICAL ERROR: Found broken pattern '{p}' in code!")
            found_errors = True
            
    if not found_errors:
        print("Static check passed: No broken SUM/AVG commas found.")
    
    # Try running one of the grouped queries
    try:
        with pyodbc.connect(conn_str) as conn:
            # We'll take a sample of the actual query from the file using regex
            import re
            # Extract the query in _fetch_daily_sales
            daily_query_match = re.search(r'_fetch_daily_sales\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if daily_query_match:
                q = daily_query_match.group(1).replace("?", "'2026-04-01'") # Simple param replacement for testing
                # Actually, pyodbc params are better
                print("Testing _fetch_daily_sales query structure...")
                pd.read_sql(daily_query_match.group(1), conn, params=['2026-04-01', '2026-04-19'])
                print("_fetch_daily_sales: SUCCESS")
            
            # Extract area sales query
            area_query_match = re.search(r'_fetch_area_sales\(_self, start_date: str, end_date: str\) -> pd.DataFrame:.*?query = """(.*?)"""', code, re.DOTALL)
            if area_query_match:
                print("Testing _fetch_area_sales query structure...")
                pd.read_sql(area_query_match.group(1), conn, params=['2026-04-01', '2026-04-19'])
                print("_fetch_area_sales: SUCCESS")

    except Exception as e:
        print(f"SQL EXECUTION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    test_queries()
