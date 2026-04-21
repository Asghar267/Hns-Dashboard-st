import pyodbc
import pandas as pd

def research_discrepancy():
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
    
    # Branches provided by user
    branch_names = [
        'Khadda Main Branch', 'Festival 1', 'Rahat Commercial', 'TOWER', 
        'North Nazimabad', 'MALIR', 'FESTIVAL 2', 'Tipu Sultan', 'Mandi'
    ]
    
    blocked_names = [
        'Employee food','Wali Jaan','Wali jan','Wali Jaan Personal','Employee Food',
        'Wali jaan personal','Gv (Wali Jaan)','Personal Wali Jaan','Wali Jaan Persnal',
        'Wali Jan Personal','Wali Jaan Personal order'
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        # 1. Get Branch IDs
        q_branches = f"SELECT shop_id, shop_name FROM tblDefShops WHERE shop_name IN ({','.join(['?' for _ in branch_names])})"
        df_branches = pd.read_sql(q_branches, conn, params=branch_names)
        branch_ids = df_branches['shop_id'].tolist()
        print("\nBranch IDs for specified branches:")
        print(df_branches)
        
        # 2. Verify Overview Total for these branches (Filtered mode)
        q_overview = f"""
        SELECT SUM(Nt_amount) as OverviewTotal
        FROM tblSales WITH (NOLOCK)
        WHERE sale_date >= '2026-04-01' AND sale_date < '2026-04-17'
        AND shop_id IN ({','.join(['?' for _ in branch_ids])})
        AND Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        """
        params = branch_ids + blocked_names
        overview_res = pd.read_sql(q_overview, conn, params=params)
        print(f"\nCalculated Overview Total for these branches: {overview_res.iloc[0,0]:,.2f}")
        
        # 3. Investigate "Deals" (Product_Item_ID 2642)
        q_deals = """
        SELECT p.product_id, p.item_name, p.line_item_id, l.field_name as Category
        FROM tblDefProducts p
        LEFT JOIN tblDefLineItems l ON p.line_item_id = l.line_item_id
        WHERE p.product_id = 2642 OR p.item_name LIKE '%Deal%'
        """
        deals_info = pd.read_sql(q_deals, conn)
        print("\nDeals Product Info:")
        print(deals_info)
        
        # Check if they exist in line items for April
        q_deals_sales = f"""
        SELECT COUNT(*) as DealCount, SUM(li.qty * li.Unit_price) as DealGross
        FROM tblSalesLineItems li
        JOIN tblSales s ON li.sale_id = s.sale_id
        WHERE s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
        AND s.shop_id IN ({','.join(['?' for _ in branch_ids])})
        AND li.Product_Item_ID = 2642
        """
        deals_sales = pd.read_sql(q_deals_sales, conn, params=branch_ids)
        print("\nDeal Sales in April for these branches:")
        print(deals_sales)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    research_discrepancy()
