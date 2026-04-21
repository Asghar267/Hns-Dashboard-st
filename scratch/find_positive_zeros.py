import pandas as pd
from modules.database import pool, build_filter_clause

def find_leaks():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # Find sales that show up in Overview but are LOST in Chef logic
    query = f"""
    WITH filtered_sales AS (
        SELECT s.sale_id, s.shop_id, s.Nt_amount, s.Cust_name
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id IN ({placeholders})
          {filter_clause}
    ),
    valid_sales AS (
        SELECT DISTINCT li.sale_id
        FROM tblSalesLineItems li WITH (NOLOCK)
        JOIN filtered_sales fs ON fs.sale_id = li.sale_id
        WHERE li.Unit_price > 0
    )
    SELECT fs.shop_id, SUM(fs.Nt_amount) as leaked_amount, COUNT(fs.sale_id) as leaked_count
    FROM filtered_sales fs
    LEFT JOIN valid_sales vs ON fs.sale_id = vs.sale_id
    WHERE vs.sale_id IS NULL
      AND fs.Nt_amount > 0.01
    GROUP BY fs.shop_id
    """
    
    df = pd.read_sql(query, conn, params=[start_date, end_date] + branch_ids + filter_params)
    print("\n--- POSITIVE REVENUE LOST (INVOICES WITH NO PRICED ITEMS) ---")
    print(df)
    
    # If we found any, let's see why
    if not df.empty:
        example_shop = df.iloc[0]['shop_id']
        query_eg = f"""
        SELECT TOP 10 s.sale_id, s.Nt_amount, s.Cust_name, s.Additional_Comments
        FROM tblSales s WITH (NOLOCK)
        LEFT JOIN (SELECT DISTINCT sale_id FROM tblSalesLineItems WHERE Unit_price > 0) vs ON s.sale_id = vs.sale_id
        WHERE s.sale_date BETWEEN ? AND ?
          AND s.shop_id = {example_shop}
          AND vs.sale_id IS NULL
          AND s.Nt_amount > 1
        """
        df_eg = pd.read_sql(query_eg, conn, params=[start_date, end_date])
        print("\nExample Leaked Invoices:")
        print(df_eg)

if __name__ == "__main__":
    find_leaks()
