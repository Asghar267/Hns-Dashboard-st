import pyodbc
import pandas as pd

def get_specific_sales():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    
    categories = [
        "Sales - Bar B Q", "Sales - Chinese", "Sales - Fast Food", 
        "Sales - Handi", "Sales - Juices Shakes & Desserts", 
        "Sales - Karahi", "SALES - TANDOOR", "Deal", 
        "Sales - Rolls", "Sales - Beverages", "Sales Side Orders"
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        print("\n--- Sales Summary (April 1 - April 16, 2026) ---")
        
        # We use a broad LIKE search to capture slight naming variations if any
        query = """
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT 
            ISNULL(l.field_name, 'Unknown') AS Category,
            SUM(li.qty) AS TotalQty,
            SUM(li.qty * li.Unit_price) AS TotalGrossSale
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems l WITH (NOLOCK) ON p.line_item_id = l.line_item_id
        WHERE 
            s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
            AND (
                l.field_name LIKE '%Bar B Q%' OR
                l.field_name LIKE '%Chinese%' OR
                l.field_name LIKE '%Fast Food%' OR
                l.field_name LIKE '%Handi%' OR
                l.field_name LIKE '%Juices%' OR
                l.field_name LIKE '%Karahi%' OR
                l.field_name LIKE '%Tandoor%' OR
                l.field_name LIKE '%Deal%' OR
                l.field_name LIKE '%Rolls%' OR
                l.field_name LIKE '%Beverages%' OR
                l.field_name LIKE '%Side Order%'
            )
        GROUP BY l.field_name
        ORDER BY TotalGrossSale DESC
        """
        df_res = pd.read_sql(query, conn)
        print(df_res.to_markdown(index=False))
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_specific_sales()
