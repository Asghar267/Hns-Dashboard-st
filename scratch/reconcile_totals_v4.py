import pandas as pd
from modules.database import pool, build_filter_clause

def reconcile_all():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # 1. Overview Totals
    query_ov = f"""
    SELECT sh.shop_name, SUM(s.Nt_amount) as ov_total, COUNT(s.sale_id) as ov_count
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
    GROUP BY sh.shop_name
    """
    df_ov = pd.read_sql(query_ov, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # 2. Chef Totals (Replicating logic WITH NO CATEGORY FILTERS)
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
        sh.shop_name,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS chef_total
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    JOIN tblDefShops sh WITH (NOLOCK) ON fs.shop_id = sh.shop_id
    WHERE li.Unit_price > 0
    GROUP BY sh.shop_name
    """
    df_chef = pd.read_sql(query_chef, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # 3. Compare
    comparison = df_ov.merge(df_chef, on='shop_name', how='left').fillna(0)
    comparison['gap'] = comparison['ov_total'] - comparison['chef_total']
    
    print("\n--- BRANCH-WISE RECONCILIATION ---")
    print(comparison)
    print(f"\nTotal Gap Sum: {comparison['gap'].sum():,.2f}")
    
    # 4. Find where the gap is: Invoices missing from line_totals but present in filtered_sales
    query_leak = f"""
    WITH filtered_sales AS (
        SELECT s.sale_id, s.Nt_amount, s.Cust_name
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id IN ({placeholders})
          {filter_clause}
    )
    SELECT fs.sale_id, fs.Nt_amount, fs.Cust_name
    FROM filtered_sales fs
    WHERE NOT EXISTS (
        SELECT 1 FROM tblSalesLineItems li 
        WHERE li.sale_id = fs.sale_id AND li.Unit_price > 0
    )
    AND fs.Nt_amount > 1
    """
    df_leak = pd.read_sql(query_leak, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    print("\n--- INVOICES WITH NT_AMOUNT > 1 BUT NO PRICED LINE ITEMS ---")
    print(f"Count: {len(df_leak)}")
    print(f"Total Value: {df_leak['Nt_amount'].sum():,.2f}")
    if not df_leak.empty:
        print("\nBreakdown by Customer:")
        print(df_leak.groupby('Cust_name')['Nt_amount'].sum().sort_values(ascending=False).head(10))

if __name__ == "__main__":
    reconcile_all()
