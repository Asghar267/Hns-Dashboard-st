import pyodbc
import pandas as pd

def verify_reconciliation():
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
    
    # 9 Branches from user
    branch_ids = [2, 3, 4, 6, 8, 10, 14, 15, 16]
    blocked_names = [
        'Employee food','Wali Jaan','Wali jan','Wali Jaan Personal','Employee Food',
        'Wali jaan personal','Gv (Wali Jaan)','Personal Wali Jaan','Wali Jaan Persnal',
        'Wali Jan Personal','Wali Jaan Personal order'
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        # April 1-16
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH filtered_sales AS (
            SELECT s.sale_id, s.shop_id, s.Nt_amount
            FROM tblSales s WITH (NOLOCK)
            WHERE s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
                AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
                AND s.Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        ),
        line_totals AS (
            SELECT li.sale_id, SUM(li.qty * li.Unit_price) AS line_total
            FROM tblSalesLineItems li WITH (NOLOCK)
            JOIN filtered_sales fs ON fs.sale_id = li.sale_id
            WHERE li.Unit_price > 0
            GROUP BY li.sale_id
        )
        SELECT 
            sh.shop_name,
            SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS TotalSales
        FROM filtered_sales fs
        JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
        JOIN line_totals lt ON lt.sale_id = fs.sale_id
        JOIN tblDefShops sh ON fs.shop_id = sh.shop_id
        WHERE li.Unit_price > 0
        GROUP BY sh.shop_name
        ORDER BY TotalSales DESC
        """
        params = branch_ids + blocked_names
        df = pd.read_sql(query, conn, params=params)
        
        print("\nBranch-wise Total Sales (Chef Sales Method):")
        print(df)
        print(f"\nGRAND TOTAL: {df['TotalSales'].sum():,.2f}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_reconciliation()
