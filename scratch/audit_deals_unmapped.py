import pyodbc
import pandas as pd

def audit_deals_and_unmapped():
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
    
    try:
        conn = pyodbc.connect(conn_str)
        
        # 1. Broad search for any Deal products
        q_deal_ids = """
        SELECT product_id, item_name, line_item_id
        FROM tblDefProducts
        WHERE item_name LIKE '%Deal%' OR item_name LIKE '%Meal%'
        """
        df_deals = pd.read_sql(q_deal_ids, conn)
        print("\nAll potential Deal/Meal Products:")
        print(df_deals.head(20))
        
        # 2. Check sales for these IDs in April
        deal_ids = df_deals['product_id'].tolist()
        if deal_ids:
            q_deal_sales = f"""
            SELECT TOP 10 li.Product_Item_ID, p.item_name, COUNT(*) as SalesCount
            FROM tblSalesLineItems li
            JOIN tblSales s ON li.sale_id = s.sale_id
            JOIN tblDefProducts p ON li.Product_Item_ID = p.product_id
            WHERE s.sale_date >= '2026-04-01'
            AND li.Product_Item_ID IN ({','.join(['?' for _ in deal_ids[:100]])})
            GROUP BY li.Product_Item_ID, p.item_name
            ORDER BY SalesCount DESC
            """
            df_actual_deals = pd.read_sql(q_deal_sales, conn, params=deal_ids[:100])
            print("\nActual Deals with Sales in April:")
            print(df_actual_deals)
        
        # 3. Check for items with NULL line_item_id (Potential Unmapped)
        q_unmapped = """
        SELECT TOP 10 p.product_id, p.item_name, p.line_item_id
        FROM tblDefProducts p
        WHERE p.line_item_id IS NULL OR p.line_item_id = 0
        """
        df_nulls = pd.read_sql(q_unmapped, conn)
        print("\nProducts with no mapping (NULL/0 line_item_id):")
        print(df_nulls)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_deals_and_unmapped()
