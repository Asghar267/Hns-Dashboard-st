import pyodbc
import pandas as pd

def audit_integrity():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=60;"
    )
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    
    # 1. Audit ALL Branches Overview Totals
    query_branches = f"""
    SELECT sh.shop_id, sh.shop_name, SUM(s.Nt_amount) as total
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.is_cancel = 0
    GROUP BY sh.shop_id, sh.shop_name
    ORDER BY total DESC
    """
    df_branches = pd.read_sql(query_branches, conn)
    print("\n--- ALL BRANCH TOTALS (March) ---")
    print(df_branches)
    
    # Let's try to find which combination matches 55,998,555
    # B2 + B4 + B14 = 54,489,355 (my previous finding)
    # What if we add Branch 15 (Festival ID 3)? 
    # Wait! ID 14 is Festival 2. ID 3 is Festival 1.
    
    # 2. Check orphaned invoices (No Line Items)
    query_orphans = f"""
    SELECT shop_id, SUM(Nt_amount) as orphan_revenue, COUNT(*) as orphan_count
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.is_cancel = 0
      AND NOT EXISTS (SELECT 1 FROM tblSalesLineItems li WHERE li.sale_id = s.sale_id)
    GROUP BY shop_id
    """
    df_orphans = pd.read_sql(query_orphans, conn)
    print("\n--- ORPHANED REVENUE (No Line Items) ---")
    print(df_orphans)

if __name__ == "__main__":
    audit_integrity()
