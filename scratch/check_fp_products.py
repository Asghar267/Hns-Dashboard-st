import os
import pyodbc
import pandas as pd

def check_fp_products():
    driver = "SQL Server"
    server = "103.86.55.183,10306"
    database = "CandelaFP"
    uid = "ReadOnlyUser"
    pwd = "902729@Rafy"
    
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    
    query = """
    SELECT DISTINCT p.item_name
    FROM dbo.tblDefProducts p
    WHERE p.item_name LIKE '%Chicken%'
    ORDER BY p.item_name
    """
    
    try:
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql(query, conn)
        print("Products in CandelaFP:")
        for idx, row in df.iterrows():
            print(f"{idx}: {row['item_name']}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_fp_products()
