import pyodbc
import pandas as pd

def audit_integrity_final():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    # Important: branches 2, 4, 14 are common.
    # What about ID 3 (FESTIVAL)? ID 14 is FESTIVAL 2. 
    # IN modules/overview_tab.py, it MERGES ID 3 and ID 14!
    branch_ids = [2, 4, 14, 3] # Try adding 3
    
    placeholders = ",".join(["?"] * len(branch_ids))
    
    # 1. OVERVIEW TOTAL (Exact logic from database.py)
    # Note: build_filter_clause returns empty "" if Filtered is not passed or if no blocked items.
    query_overview = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT SUM(s.Nt_amount) AS total_Nt_amount
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
    """
    params = [start_date, end_date] + branch_ids
    overview_total = pd.read_sql(query_overview, conn, params=params).iloc[0]['total_Nt_amount']
    
    # 2. CHEF TOTAL (My latest v105 logic)
    # Includes fallback for zero-priced items and orphaned items
    query_chef = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH filtered_sales AS (
        SELECT s.sale_id, s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id IN ({placeholders})
    ),
    line_totals AS (
        SELECT 
            li.sale_id, 
            SUM(li.qty * li.Unit_price) AS line_total,
            SUM(li.qty) AS total_qty
        FROM tblSalesLineItems li WITH (NOLOCK)
        JOIN filtered_sales fs ON fs.sale_id = li.sale_id
        GROUP BY li.sale_id
    )
    SELECT 
        SUM(
            CASE 
                WHEN lt.line_total > 0 THEN (li.qty * li.Unit_price) / lt.line_total * fs.Nt_amount
                ELSE (li.qty / NULLIF(lt.total_qty, 0)) * fs.Nt_amount
            END
        ) AS chef_total
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    LEFT JOIN line_totals lt ON lt.sale_id = fs.sale_id
    """
    chef_total = pd.read_sql(query_chef, conn, params=params).iloc[0]['chef_total']
    
    print(f"\n--- DEEP DIAGNOSIS (March, Branches {branch_ids}) ---")
    print(f"Overview Total: {overview_total:,.2f}")
    print(f"Chef Sales Total: {chef_total:,.2f}")
    print(f"Gap: {overview_total - chef_total:,.2f}")
    
    # 3. Check for sales with NO line items at all
    query_no_lines = f"""
    SELECT COUNT(*) as cnt, SUM(Nt_amount) as revenue
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      AND NOT EXISTS (SELECT 1 FROM tblSalesLineItems li WHERE li.sale_id = s.sale_id)
    """
    df_no_lines = pd.read_sql(query_no_lines, conn, params=params)
    print(f"\nRevenue found in tblSales but missing from tblSalesLineItems: {df_no_lines.iloc[0]['revenue'] or 0:,.2f}")

if __name__ == "__main__":
    audit_integrity_final()
