import pyodbc
import pandas as pd

def get_filtered_schema():
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
    df = pd.read_sql('SELECT TOP 1 * FROM tblSales', conn)
    
    keywords = ['tax', 'service', 'charge', 'disc', 'rounding', 'adjustment', 'amount', 'total']
    
    print("\nRELEVANT COLUMNS IN tblSales:")
    for col in sorted(df.columns.tolist()):
        if any(kw in col.lower() for kw in keywords):
            print(f"- {col}")

if __name__ == "__main__":
    get_filtered_schema()
