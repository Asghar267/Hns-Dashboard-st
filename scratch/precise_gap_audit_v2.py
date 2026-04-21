import pandas as pd
from modules.database import pool, build_filter_clause

def precise_audit():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # Overview IDs
    query_ov = f"SELECT s.sale_id, s.Nt_amount FROM tblSales s WITH (NOLOCK) WHERE s.sale_date BETWEEN ? AND ? AND s.shop_id IN ({placeholders}) {filter_clause}"
    df_ov = pd.read_sql(query_ov, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    # Chef IDs
    query_chef = f"""
    WITH filtered_sales AS (
        SELECT s.sale_id FROM tblSales s WITH (NOLOCK) WHERE s.sale_date BETWEEN ? AND ? AND s.shop_id IN ({placeholders}) {filter_clause}
    ),
    line_totals AS (
        SELECT li.sale_id FROM tblSalesLineItems li WITH (NOLOCK) JOIN filtered_sales fs ON fs.sale_id = li.sale_id WHERE li.Unit_price > 0 GROUP BY li.sale_id
    )
    SELECT fs.sale_id FROM filtered_sales fs JOIN line_totals lt ON lt.sale_id = fs.sale_id
    """
    df_chef = pd.read_sql(query_chef, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    missing_ids = set(df_ov['sale_id']) - set(df_chef['sale_id'])
    print(f"Total Overview: {len(df_ov)}")
    print(f"Total Chef: {len(df_chef)}")
    print(f"Missing IDs count: {len(missing_ids)}")
    
    if missing_ids:
        example_id = list(missing_ids)[0]
        print(f"\n--- Investigating Missing Sale ID: {example_id} ---")
        
        # Check tblSalesLineItems
        query_li = f"SELECT * FROM tblSalesLineItems WITH (NOLOCK) WHERE sale_id = {example_id}"
        df_li = pd.read_sql(query_li, conn)
        print("\nLine Items in DB:")
        print(df_li[['sale_id', 'Product_Item_ID', 'qty', 'Unit_price']])
        
        # Check filtered_sales logic for this ID
        query_fs = f"SELECT sale_id, sale_date, shop_id, Nt_amount, Cust_name FROM tblSales WHERE sale_id = {example_id}"
        df_fs = pd.read_sql(query_fs, conn)
        print("\nSale Header in DB:")
        print(df_fs)

if __name__ == "__main__":
    precise_audit()
