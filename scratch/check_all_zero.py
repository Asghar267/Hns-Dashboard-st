import pandas as pd
from modules.database import pool, build_filter_clause

def check_all_zero():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    # Find sales where NO line item has Unit_price > 0
    query = f"""
    SELECT s.sale_id, s.Nt_amount, s.Cust_name, s.Additional_Comments
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
    GROUP BY s.sale_id, s.Nt_amount, s.Cust_name, s.Additional_Comments
    HAVING MAX(li.Unit_price) <= 0
    """
    df_zeros = pd.read_sql(query, conn, params=[start_date, end_date] + branch_ids + filter_params)
    
    print(f"Total Invoices with ONLY Zero-Priced Items: {len(df_zeros)}")
    if not df_zeros.empty:
        print(f"Total Bill Amount of Zeros: {df_zeros['Nt_amount'].sum():,.2f}")
        print("\nSample Zeros:")
        print(df_zeros.head(10))

if __name__ == "__main__":
    check_all_zero()
