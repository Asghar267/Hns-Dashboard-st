import pyodbc
import pandas as pd

def diagnose_gap():
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
    
    branch_ids = [2, 3, 4, 6, 8, 10, 14, 15, 16]
    blocked_names = [
        'Employee food','Wali Jaan','Wali jan','Wali Jaan Personal','Employee Food',
        'Wali jaan personal','Gv (Wali Jaan)','Personal Wali Jaan','Wali Jaan Persnal',
        'Wali Jan Personal','Wali Jaan Personal order'
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        # SQL logic mimicking the current database.py mapping
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
            COALESCE(
                CASE 
                    WHEN li.Product_Item_ID IN (2642, 3782) OR p.item_name LIKE '%Deal%' OR p.item_name LIKE '%Meal%' THEN 'Deals'
                    ELSE t.field_name 
                END, 
                '(Unmapped)'
            ) AS Category,
            SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS TotalSales
        FROM filtered_sales fs
        JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
        JOIN line_totals lt ON lt.sale_id = fs.sale_id
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
        WHERE li.Unit_price > 0
        GROUP BY 
            COALESCE(
                CASE 
                    WHEN li.Product_Item_ID IN (2642, 3782) OR p.item_name LIKE '%Deal%' OR p.item_name LIKE '%Meal%' THEN 'Deals'
                    ELSE t.field_name 
                END, 
                '(Unmapped)'
            )
        ORDER BY TotalSales DESC
        """
        params = branch_ids + blocked_names
        df = pd.read_sql(query, conn, params=params)
        
        print("\n--- Category Breakdown for Target Branches ---")
        print(df)
        
        total_all = df['TotalSales'].sum()
        visible_cats = df[~df['Category'].isin(['Unused', '(Unmapped)'])]
        total_visible = visible_cats['TotalSales'].sum()
        total_hidden = df[df['Category'].isin(['Unused', '(Unmapped)'])]['TotalSales'].sum()

        print(f"\nGRAND TOTAL (Everything): {total_all:,.2f}")
        print(f"VISIBLE TOTAL (Without Unused/Unmapped): {total_visible:,.2f}")
        print(f"HIDDEN TOTAL (Unused/Unmapped): {total_hidden:,.2f}")
        
        # Also check for exact shop totals to match the 55.9M
        q_shops = f"""
        SELECT sh.shop_name, SUM(s.Nt_amount) as OverviewTotal
        FROM tblSales s
        JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
        AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
        AND s.Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        GROUP BY sh.shop_name
        """
        df_shops = pd.read_sql(q_shops, conn, params=branch_ids + blocked_names)
        print("\n--- Individual Branch Overview Totals ---")
        print(df_shops)
        print(f"OVERVIEW SUM: {df_shops['OverviewTotal'].sum():,.2f}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_gap()
