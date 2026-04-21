import pandas as pd
from modules.database import pool, build_filter_clause

def check_targets():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 14]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    conn = pool.get_connection("candelahns")
    
    # Check revenue for the "Missing" categories
    query = f"""
    SELECT 
        COALESCE(t.field_name, '(Unmapped)') as category,
        SUM(li.qty * li.Unit_price) as raw_revenue_no_weight
    FROM tblSalesLineItems li WITH (NOLOCK)
    JOIN tblSales s WITH (NOLOCK) ON li.sale_id = s.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders})
      {filter_clause}
      AND li.Unit_price > 0
    GROUP BY t.field_name
    ORDER BY raw_revenue_no_weight DESC
    """
    df = pd.read_sql(query, conn, params=[start_date, end_date] + branch_ids + filter_params)
    print("\n--- RAW REVENUE BREAKDOWN (March, B2,4,14) ---")
    print(df)

if __name__ == "__main__":
    check_targets()
