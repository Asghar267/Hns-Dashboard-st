import pyodbc
import pandas as pd

def explore_db():
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
        
        # 1. Sample from tblSalesLineItems
        print("\n--- tblSalesLineItems sample (April 2026) ---")
        q_sli = """
        SELECT TOP 5 li.* 
        FROM tblSalesLineItems li
        JOIN tblSales s ON li.sale_id = s.sale_id
        WHERE s.sale_date >= '2026-04-01'
        """
        df_sli = pd.read_sql(q_sli, conn)
        print(df_sli.columns.tolist())
        print(df_sli)

        # 2. Check tblDefLineItems
        print("\n--- tblDefLineItems sample ---")
        q_def = "SELECT TOP 5 * FROM tblDefLineItems"
        df_def = pd.read_sql(q_def, conn)
        print(df_def.columns.tolist())
        print(df_def)

        # 3. Try to find a real category table
        print("\n--- Trying tblDefCategory content ---")
        q_cat = "SELECT TOP 10 * FROM tblDefCategory"
        try:
            df_cat = pd.read_sql(q_cat, conn)
            print(df_cat)
        except:
            print("tblDefCategory not found or inaccessible.")

        # 4. Try to find link between product and category
        print("\n--- Trying tblProductItem or tblDefProducts columns ---")
        try:
            q_prod = "SELECT TOP 1 * FROM tblDefProducts"
            df_prod = pd.read_sql(q_prod, conn)
            print("tblDefProducts columns:", df_prod.columns.tolist())
        except:
            pass

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_db()
