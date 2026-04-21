import pyodbc
import pandas as pd

def verify_final_query():
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
        
        print("\n--- Verifying Categories & Sales Query ---")
        query = """
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        SELECT 
            l.field_name AS CategoryName,
            SUM(li.qty) AS TotalQty,
            SUM(li.qty * li.Unit_price) AS TotalSale
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON li.Product_code = p.Product_code
        LEFT JOIN tblDefLineItems l WITH (NOLOCK) ON p.line_item_id = l.line_item_id
        WHERE 
            MONTH(s.sale_date) = MONTH(GETDATE()) 
            AND YEAR(s.sale_date) = YEAR(GETDATE())
        GROUP BY l.field_name
        ORDER BY TotalSale DESC
        """
        df_res = pd.read_sql(query, conn)
        print(df_res)
        
        if df_res.empty or df_res['CategoryName'].isnull().all():
            print("\nWait, Category names are missing. Checking Product_Item_ID join...")
            query2 = """
            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT 
                l.field_name AS CategoryName,
                SUM(li.qty) AS TotalQty,
                SUM(li.qty * li.Unit_price) AS TotalSale
            FROM tblSales s WITH (NOLOCK)
            JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
            -- Try joining via Product_Item_ID -> tblProductItem -> tblDefProducts
            LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
            LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
            LEFT JOIN tblDefLineItems l WITH (NOLOCK) ON p.line_item_id = l.line_item_id
            WHERE 
                MONTH(s.sale_date) = MONTH(GETDATE()) 
                AND YEAR(s.sale_date) = YEAR(GETDATE())
            GROUP BY l.field_name
            ORDER BY TotalSale DESC
            """
            df_res2 = pd.read_sql(query2, conn)
            print(df_res2)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_final_query()
