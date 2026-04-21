import pandas as pd
from modules.database import pool, build_filter_clause

def check_orphans():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # Check for sales that have NO line items at all
    query = f"""
    SELECT s.sale_id, s.Nt_amount, s.Cust_name
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
      AND li.sale_id IS NULL
    """
    df_orphans = pd.read_sql(query, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    print(f"Total Invoices with NO Line Items: {len(df_orphans)}")
    if not df_orphans.empty:
        print(f"Total Bill Amount of Orphans: {df_orphans['Nt_amount'].sum():,.2f}")
        print("\nSample Orphans:")
        print(df_orphans.head(10))

if __name__ == "__main__":
    check_orphans()
