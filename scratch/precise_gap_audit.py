import pandas as pd
from modules.database import pool, build_filter_clause

def precise_audit():
    # Use March 2026 as reference
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15] # Common active branches
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # 1. Get raw invoices from Overview logic
    query_ov = f"""
    SELECT s.sale_id, s.shop_id, s.Nt_amount, s.Cust_name, s.Additional_Comments
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
    """
    df_ov = pd.read_sql(query_ov, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # 2. Get line item totals from Chef logic
    query_chef = f"""
    WITH filtered_sales AS (
        SELECT s.sale_id, s.shop_id, s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id IN ({placeholders})
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
        fs.sale_id,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS chef_total
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    WHERE li.Unit_price > 0
    GROUP BY fs.sale_id
    """
    df_chef = pd.read_sql(query_chef, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # 3. Merge and Compare
    comparison = df_ov.merge(df_chef, on='sale_id', how='left').fillna(0)
    comparison['diff'] = comparison['Nt_amount'] - comparison['chef_total']
    
    # Significant differences (> 1 PKR)
    diffs = comparison[abs(comparison['diff']) > 1]
    
    print(f"Total Overview Count: {len(df_ov)}")
    print(f"Total Chef Count: {len(df_chef)}")
    print(f"Invoices with significant difference: {len(diffs)}")
    print(f"Total Gap Found: {diffs['diff'].sum():,.2f} PKR")
    
    if not diffs.empty:
        print("\nTop 10 Differing Invoices:")
        print(diffs.sort_values('diff', ascending=False).head(10))
        
        # Breakdown by Customer
        print("\nGap Breakdown by Customer Name:")
        print(diffs.groupby('Cust_name')['diff'].sum().sort_values(ascending=False).head(10))
        
        # Check an example of a missing invoice
        example_id = diffs.iloc[0]['sale_id']
        print(f"\nAudit for Sale_ID: {example_id}")
        query_audit = f"""
        SELECT li.Product_Item_ID, li.qty, li.Unit_price, p.item_name
        FROM tblSalesLineItems li WITH (NOLOCK)
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        WHERE li.sale_id = {example_id}
        """
        df_audit = pd.read_sql(query_audit, conn)
        print(df_audit)

if __name__ == "__main__":
    precise_audit()
