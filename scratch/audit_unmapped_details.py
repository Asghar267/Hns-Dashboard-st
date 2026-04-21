import pyodbc
import pandas as pd

def audit_unmapped_details():
    conn_str = "Driver={SQL Server};Server=FAHAD-PC\\SQLEXPRESS01;Database=candelahns;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = '(2, 4, 14)'
    
    query = f"""
    SELECT 
        p.item_name,
        t.field_name as category,
        SUM(li.qty * li.Unit_price) as raw_revenue
    FROM tblSalesLineItems li WITH (NOLOCK)
    JOIN tblSales s WITH (NOLOCK) ON li.sale_id = s.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.shop_id IN {branch_ids}
      AND (t.field_name IS NULL OR t.field_name = 'Unused')
      AND li.Unit_price > 0
    GROUP BY p.item_name, t.field_name
    ORDER BY raw_revenue DESC
    """
    df = pd.read_sql(query, conn)
    print("\n--- DETAILED ITEMS IN UNMAPPED/UNUSED ---")
    print(df)

if __name__ == "__main__":
    audit_unmapped_details()
