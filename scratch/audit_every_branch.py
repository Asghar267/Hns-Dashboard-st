import pyodbc
import pandas as pd

def audit_all_branches():
    conn_str = "Driver={SQL Server};Server=FAHAD-PC\\SQLEXPRESS01;Database=candelahns;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    
    query = f"""
    SELECT sh.shop_id, sh.shop_name, SUM(s.Nt_amount) as total
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.is_cancel = 0
    GROUP BY sh.shop_id, sh.shop_name
    ORDER BY total DESC
    """
    df = pd.read_sql(query, conn)
    print("\n--- EVERY BRANCH TOTAL (March) ---")
    print(df)

if __name__ == "__main__":
    audit_all_branches()
