import pandas as pd
from modules.database import pool, build_filter_clause

def audit_unmapped():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    placeholders = ",".join(["?"] * len(branch_ids))
    
    conn = pool.get_connection("candelahns")
    
    query = f"""
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
        COALESCE(t.field_name, '(Unmapped)') as category_name,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS revenue
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE li.Unit_price > 0
    GROUP BY t.field_name
    ORDER BY revenue DESC
    """
    
    df = pd.read_sql(query, conn, params=[start_date, end_date] + branch_ids + filter_params)
    print("\n--- REVENUE BY CATEGORY (INCLUDING UNMAPPED) ---")
    print(df)

if __name__ == "__main__":
    audit_unmapped()
