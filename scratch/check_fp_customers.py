import os
import pyodbc
import pandas as pd

def check_fp_customers():
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
    SELECT DISTINCT LTRIM(RTRIM(ISNULL(s.Cust_name, ''))) AS Customer
    FROM dbo.tblSales s
    WHERE s.sale_date >= '2026-04-01'
    ORDER BY Customer
    """
    
    try:
        conn = pyodbc.connect(conn_str)
        df = pd.read_sql(query, conn)
        print("Customers in CandelaFP (April 2026):")
        for idx, row in df.iterrows():
            print(f"{idx}: {row['Customer']}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_fp_customers()
