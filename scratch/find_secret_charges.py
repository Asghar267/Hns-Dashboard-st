import pyodbc
import pandas as pd

def find_secrets():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    
    # Let's find sales where NT and GT differ
    query = """
    SELECT TOP 10 sale_id, GT_amount, NT_amount, (NT_amount - GT_amount) as gap, adjustment_amount
    FROM tblSales WITH (NOLOCK)
    WHERE sale_date BETWEEN '2026-03-01' AND '2026-03-31'
      AND ABS(NT_amount - GT_amount) > 1.0
      AND shop_id IN (2, 4, 14)
    ORDER BY gap DESC
    """
    df = pd.read_sql(query, conn)
    print("\nSALES WITH GAP BETWEEN GROSS AND NET:")
    print(df)
    
    if not df.empty:
        target_sale_id = df.iloc[0]['sale_id']
        print(f"\nINSPECTING SALE ID: {target_sale_id}")
        
        # Check Line Items for this sale
        query_li = f"""
        SELECT li.Product_Item_ID, li.qty, li.Unit_price, (li.qty * li.Unit_price) as total
        FROM tblSalesLineItems li WITH (NOLOCK)
        WHERE li.sale_id = {target_sale_id}
        """
        df_li = pd.read_sql(query_li, conn)
        print("\nLINE ITEMS:")
        print(df_li)
        print(f"SUM OF LINE ITEMS: {df_li['total'].sum()}")
    
if __name__ == "__main__":
    find_secrets()
