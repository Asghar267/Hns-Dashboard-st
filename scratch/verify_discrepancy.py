import pyodbc
import pandas as pd
import sys
import os

# Add the current directory to path so we can import modules
sys.path.append(os.getcwd())

from modules.config import BLOCKED_NAMES, BLOCKED_COMMENTS

def verify():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,2001;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=60;"
    )
    
    # Employees mentioned by user
    emp_ids = [362, 304, 341, 368]
    start_date = '2026-04-01'
    end_date = '2026-04-17'
    
    try:
        conn = pyodbc.connect(conn_str)
        print("Connected to database.")
        
        # 1. RAW QUERY (Like the user's)
        raw_query = f"""
        SELECT
            e.shop_employee_id,
            e.field_name,
            COUNT(s.sale_id) as tx_count,
            SUM(s.Nt_amount) as raw_total
        FROM tblSales s
        INNER JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date < '{end_date}'
          AND s.shop_id IN (1, 2, 3, 4, 5, 6, 7)
          AND s.external_ref_type = 'Blinkco order'
          AND e.shop_employee_id IN ({','.join(map(str, emp_ids))})
        GROUP BY e.shop_employee_id, e.field_name
        """
        df_raw = pd.read_sql(raw_query, conn)
        
        # 2. FILTERED QUERY (Like Dashboard)
        # Note: Dashboard uses branch_ids [2, 3, 4, 6, 14, 15, 16] usually, but let's keep user's branches for fair comparison of "Blocked" filters
        filtered_query = f"""
        SELECT
            e.shop_employee_id,
            e.field_name,
            COUNT(s.sale_id) as tx_count,
            SUM(s.Nt_amount) as filtered_total
        FROM tblSales s
        INNER JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date < '{end_date}'
          AND s.shop_id IN (1, 2, 3, 4, 5, 6, 7)
          AND s.external_ref_type = 'Blinkco order'
          AND e.shop_employee_id IN ({','.join(map(str, emp_ids))})
          AND s.Cust_name NOT IN ({','.join(["'"+n+"'" for n in BLOCKED_NAMES])})
          AND (s.Additional_Comments NOT IN ({','.join(["'"+c+"'" for c in BLOCKED_COMMENTS])}) OR s.Additional_Comments IS NULL)
        GROUP BY e.shop_employee_id, e.field_name
        """
        df_filtered = pd.read_sql(filtered_query, conn)
        
        # 3. IMPACT ANALYSIS (What exactly was blocked)
        impact_query = f"""
        SELECT
            e.field_name,
            s.Cust_name,
            s.Additional_Comments,
            s.Nt_amount,
            s.sale_date
        FROM tblSales s
        INNER JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        WHERE s.sale_date >= '{start_date}' AND s.sale_date < '{end_date}'
          AND e.shop_employee_id IN ({','.join(map(str, emp_ids))})
          AND s.external_ref_type = 'Blinkco order'
          AND (
              s.Cust_name IN ({','.join(["'"+n+"'" for n in BLOCKED_NAMES])})
              OR s.Additional_Comments IN ({','.join(["'"+c+"'" for c in BLOCKED_COMMENTS])})
          )
        """
        df_impact = pd.read_sql(impact_query, conn)
        
        print("\n--- RAW TOTALS (User Query Like) ---")
        print(df_raw)
        
        print("\n--- FILTERED TOTALS (Dashboard Logic) ---")
        print(df_filtered)
        
        print("\n--- DISCREPANCY PER EMPLOYEE ---")
        merged = df_raw.merge(df_filtered, on='shop_employee_id', how='left')
        merged['diff'] = merged['raw_total'] - merged['filtered_total'].fillna(0)
        print(merged[['field_name_x', 'raw_total', 'filtered_total', 'diff']])
        
        print("\n--- BLOCKED TRANSACTIONS SAMPLES ---")
        if not df_impact.empty:
            print(df_impact.head(20))
        else:
            print("No blocked transactions found for these employees in this range.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
