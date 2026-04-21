import pandas as pd
from modules.database import pool, build_filter_clause

def find_specific_gap():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    # Use branches that sum to ~55M in Overview
    branch_ids = [2, 4, 14] 
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    conn = pool.get_connection("candelahns")
    
    # 1. Overview
    query_ov = f"SELECT shop_id, SUM(Nt_amount) as ov_total FROM tblSales s WITH (NOLOCK) WHERE s.sale_date BETWEEN ? AND ? AND s.shop_id IN ({placeholders}) {filter_clause} GROUP BY shop_id"
    df_ov = pd.read_sql(query_ov, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # 2. Chef (Raw weighted logic)
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
        fs.shop_id,
        COALESCE(t.field_name, '(Unmapped)') as category,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS revenue
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE li.Unit_price > 0
    GROUP BY fs.shop_id, t.field_name
    """
    df_chef = pd.read_sql(query_chef, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    print("\n--- OVERVIEW TOTALS ---")
    print(df_ov)
    print(f"Overall Total: {df_ov['ov_total'].sum():,.2f}")
    
    print("\n--- CHEF REVENUE BY CATEGORY ---")
    chef_summary = df_chef.groupby('category')['revenue'].sum().sort_values(ascending=False).reset_index()
    print(chef_summary)
    print(f"Grand Total: {chef_summary['revenue'].sum():,.2f}")
    
    # Calculate difference
    gap = df_ov['ov_total'].sum() - chef_summary['revenue'].sum()
    print(f"\nDiscrepancy: {gap:,.2f}")

if __name__ == "__main__":
    find_specific_gap()
