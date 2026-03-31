import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    server = os.environ.get("KDSDB_SERVER", "localhost")
    database = os.environ.get("KDSDB_DATABASE", "Candelahns")
    driver = os.environ.get("KDSDB_DRIVER_WINDOWS", "SQL Server")
    
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    print(f"Testing connection with: {conn_str}")
    
    try:
        conn = pyodbc.connect(conn_str)
        print("Connection successful!")
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 shop_name FROM tblDefShops")
        row = cursor.fetchone()
        print(f"Sample data: {row}")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
