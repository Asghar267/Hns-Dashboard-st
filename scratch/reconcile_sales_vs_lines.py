import pyodbc
import pandas as pd

def audit_integrity():
    conn_str = "Driver={SQL Server};Server=FAHAD-PC\\SQLEXPRESS01;Database=candelahns;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = '(2, 4, 14)' # Assume these are selected
    
    # 1. Get Total Overview Revenue (Nt_amount)
    query_overview = f"""
    SELECT SUM(Nt_amount) as overview_total
    FROM tblSales WITH (NOLOCK)
    WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND shop_id IN {branch_ids}
      AND is_cancel = 0
    """
    overview_total = pd.read_sql(query_overview, conn).iloc[0]['overview_total']
    
    # 2. Get Total Line Item Revenue (Calculated)
    # Using my latest refactored logic
    query_chef = f"""
    WITH filtered_sales AS (
        SELECT sale_id, Nt_amount
        FROM tblSales WITH (NOLOCK)
        WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
          AND shop_id IN {branch_ids}
          AND is_cancel = 0
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
    chef_total = pd.read_sql(query_chef, conn).iloc[0]['chef_total']
    
    # 3. Find missing Sales IDs
    query_missing = f"""
    SELECT s.sale_id, s.Nt_amount
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.shop_id IN {branch_ids}
      AND s.is_cancel = 0
      AND li.sale_id IS NULL
    """
    df_missing = pd.read_sql(query_missing, conn)
    missing_revenue = df_missing['Nt_amount'].sum()
    
    print(f"\n--- INTEGRITY AUDIT (March, B2, 4, 14) ---")
    print(f"Overview Total (Nt_amount): {overview_total:,.2f}")
    print(f"Chef Total (Weighted):    {chef_total:,.2f}")
    print(f"Discrepancy:             {overview_total - chef_total:,.2f}")
    print(f"\nRevenue from Sales with ZERO Line Items: {missing_revenue:,.2f}")
    print(f"Count of Sales with ZERO Line Items: {len(df_missing)}")

if __name__ == "__main__":
    audit_integrity()
