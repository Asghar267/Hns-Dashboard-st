import pyodbc
import pandas as pd

def _build_conn_str():
    return "DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.86.55.34,50908;DATABASE=HNSYGCC;UID=sa;PWD=123;Encrypt=yes;TrustServerCertificate=yes;"

def main():
    conn_str = _build_conn_str()
    start_ts = "2026-04-01 04:10:00"
    end_ts = "2026-04-20 04:10:00"
    
    query = """
    SELECT 
        b.branchName,
        COUNT(*) as orders,
        SUM(o.discountAmount) as sum_discount,
        SUM(o.netAmount) as sum_net
    FROM dbo.orderMaster o
    LEFT JOIN dbo.addBranch b ON b.branchId = o.branchId
    WHERE o.[datetime] >= ? AND o.[datetime] < ?
      AND o.isDelete = 0
      AND UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '')) = 'DELIVERY'
    GROUP BY b.branchName
    """
    
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            print(df)
            print("\nTotal Discount across all branches:", df['sum_discount'].sum())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
