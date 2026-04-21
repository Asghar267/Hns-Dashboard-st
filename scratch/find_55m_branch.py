import pandas as pd
from modules.database import pool, build_filter_clause

def find_missing_branch():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    # Check ALL branches to see who adds up to the user's 55.9M
    all_branch_ids = [2, 4, 8, 10, 11, 12, 13, 14, 15, 16]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(all_branch_ids))
    conn = pool.get_connection("candelahns")
    
    query = f"""
    SELECT sh.shop_id, sh.shop_name, SUM(s.Nt_amount) as total
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
    GROUP BY sh.shop_id, sh.shop_name
    ORDER BY total DESC
    """
    df = pd.read_sql(query, conn, params=[start_date, end_date] + all_branch_ids + filter_params)
    print("\n--- ALL BRANCHES OVERVIEW ---")
    print(df)

if __name__ == "__main__":
    find_missing_branch()
