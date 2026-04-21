import pyodbc
import pandas as pd

def get_rolls_sales():
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
        
        print("\n--- Fetching Rolls Sales for March 2026 ---")
        query = """
       
       
        """
        df_res = pd.read_sql(query, conn)
        print(df_res)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rolls_sales()
