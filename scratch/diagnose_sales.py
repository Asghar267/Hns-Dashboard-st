import pyodbc
import pandas as pd

def test_queries():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,2001;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        print("Connected successfully!")
        
        # 1. Check Shop ID for Khadda
        print("\n--- Shops matching 'Khadda' ---")
        shops_query = "SELECT shop_id, shop_name FROM tblDefShops WHERE shop_name LIKE '%Khadda%'"
        df_shops = pd.read_sql(shops_query, conn)
        print(df_shops)
        
        # 2. Check Employees
        print("\n--- Employees matching requested names ---")
        names = ['Zia ur Rehman', 'Shahzad', 'Zakir Alam', 'Sher Ullah']
        for name in names:
            emp_query = f"SELECT shop_employee_id, shop_id, field_Code, field_name FROM tblDefShopEmployees WHERE field_name LIKE '%{name}%'"
            df_emp = pd.read_sql(emp_query, conn)
            print(f"Results for '{name}':")
            print(df_emp)
            
        # 3. Check Sales for April 2026 (General)
        print("\n--- General Sales Count for April 2026 ---")
        sales_count_query = "SELECT COUNT(*) as TotalSales FROM tblSales WHERE sale_date BETWEEN '2026-04-01' AND '2026-04-30'"
        df_count = pd.read_sql(sales_count_query, conn)
        print(df_count)

        # 4. Check Sales for April 2025 (General) - Just in case
        print("\n--- General Sales Count for April 2025 ---")
        sales_count_2025_query = "SELECT COUNT(*) as TotalSales FROM tblSales WHERE sale_date BETWEEN '2025-04-01' AND '2025-04-30'"
        df_count_2025 = pd.read_sql(sales_count_2025_query, conn)
        print(df_count_2025)

        # 5. Check if '362', '304', '341', '368' exist in field_Code
        print("\n--- Check specific field_Codes ---")
        codes = ['362', '304', '341', '368']
        codes_str = ", ".join([f"'{c}'" for c in codes])
        codes_query = f"SELECT shop_employee_id, field_Code, field_name, shop_id FROM tblDefShopEmployees WHERE field_Code IN ({codes_str})"
        df_codes = pd.read_sql(codes_query, conn)
        print(df_codes)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_queries()
