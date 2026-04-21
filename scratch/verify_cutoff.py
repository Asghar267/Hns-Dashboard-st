import pyodbc

def main():
    conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.86.55.34,50908;DATABASE=HNSYGCC;UID=sa;PWD=123;Encrypt=yes;TrustServerCertificate=yes;"
    start_ts = "2026-04-01 04:10:00"
    end_ts = "2026-04-20 04:10:00"
    
    query = """
    SELECT COUNT(*) 
    FROM dbo.orderMaster 
    WHERE [datetime] >= ? AND [datetime] < ? 
      AND isDelete = 0 
      AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
    """
    
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(query, [start_ts, end_ts])
            count = cursor.fetchone()[0]
            print(f"Total Orders with 04:10 cutoff: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
