import pyodbc
import pandas as pd

def check_targets_standalone():
    # Direct connection params from database.py context
    # Usually: Driver={SQL Server};Server=DESKTOP-Q7C4R3R;Database=candelahns;Trusted_Connection=yes;
    # But I'll use the pool logic if I can, or just try to connect.
    # Actually, I'll use pyodbc directly with the strings I saw earlier.
    
    conn_str = "Driver={SQL Server};Server=FAHAD-PC\\SQLEXPRESS01;Database=candelahns;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = '(2, 4, 14)'
    
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
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.shop_id IN {branch_ids}
      AND s.is_cancel = 0
      AND li.Unit_price > 0
    GROUP BY t.field_name
    ORDER BY raw_revenue_no_weight DESC
    """
    df = pd.read_sql(query, conn)
    print("\n--- RAW REVENUE BREAKDOWN (March, B2,4,14) ---")
    print(df)

if __name__ == "__main__":
    check_targets_standalone()
