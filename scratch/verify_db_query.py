import pyodbc
import pandas as pd
from datetime import datetime

def test_db():
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
        print("Connecting to DB...")
        conn = pyodbc.connect(conn_str)
        print("Connected successfully.")
        
        # 1. Check categories in TempProductBarcode
        print("\n--- Categories found in TempProductBarcode ---")
        cat_query = "SELECT DISTINCT TOP 10 field_name FROM TempProductBarcode WHERE field_name IS NOT NULL AND field_name <> ''"
        df_cats = pd.read_sql(cat_query, conn)
        print(df_cats if not df_cats.empty else "No categories found in TempProductBarcode.")

        # 2. Check if there are sales in April 2026 (current month in user's context)
        print("\n--- Checking for sales in April 2026 ---")
        sales_check = """
        SELECT COUNT(*) as SaleCount 
        FROM tblSales 
        WHERE MONTH(sale_date) = 4 AND YEAR(sale_date) = 2026
        """
        df_check = pd.read_sql(sales_check, conn)
        print(f"Sales found for April 2026: {df_check['SaleCount'][0]}")

        if df_check['SaleCount'][0] == 0:
            print("No sales for April 2026. Checking last matching date...")
            last_date = "SELECT MAX(sale_date) as LastDate FROM tblSales"
            df_last = pd.read_sql(last_date, conn)
            print(f"Latest sale date in DB: {df_last['LastDate'][0]}")

        # 3. Try a simplified group by category query
        print("\n--- Running Total Sale by Category Query ---")
        query = """
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT TOP 10
            COALESCE(t.field_name, '(Unmapped)') AS CategoryName,
            SUM(li.qty) AS TotalQty,
            SUM(li.qty * li.Unit_price) AS TotalSale
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN (
            SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
            FROM TempProductBarcode WITH (NOLOCK) 
        ) t ON (li.Product_Item_ID = t.Product_Item_ID OR CAST(li.Product_code AS VARCHAR(50)) = CAST(t.Product_code AS VARCHAR(50)))
        WHERE s.sale_date >= '2026-04-01'
        GROUP BY COALESCE(t.field_name, '(Unmapped)')
        ORDER BY TotalSale DESC
        """
        df_res = pd.read_sql(query, conn)
        print(df_res if not df_res.empty else "Query returned no data for April.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_db()
