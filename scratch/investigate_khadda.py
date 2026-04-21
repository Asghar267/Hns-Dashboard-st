import pyodbc
import pandas as pd

def _build_conn_str():
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.34,50908;"
        "DATABASE=HNSYGCC;"
        "UID=sa;"
        "PWD=123;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )

def main():
    conn_str = _build_conn_str()
    start_ts = "2026-04-01 04:00:00"
    end_ts = "2026-04-20 04:00:00"
    
    try:
        with pyodbc.connect(conn_str) as conn:
            # Check KHADDA orders (branchId 1)
            query = """
            SELECT
                auto_id,
                [datetime],
                orderNumber,
                orderType,
                orderStatus,
                isDelete,
                deleteReason,
                totalWithTax,
                netAmount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
              AND branchId = 1
            ORDER BY [datetime] ASC;
            """
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            
            print(f"KHADDA Orders Count (Branch 1): {len(df)}")
            print("\nBreakdown by isDelete and orderType:")
            summary = df.groupby(['isDelete', 'orderType']).size().reset_index(name='count')
            print(summary)
            
            # If total is 876, then one must be deleted or not DELIVERY
            if len(df) == 876:
                print("\nFound 876 orders! Let's see the one(s) that are normally filtered out.")
                filtered = df[(df['isDelete'] == 1) | (df['orderType'].str.upper() != 'DELIVERY')]
                print(filtered)
            else:
                print(f"\nStill found {len(df)} orders. Checking slightly outside range.")
                query_edge = """
                SELECT COUNT(*) FROM dbo.orderMaster 
                WHERE branchId = 1 AND [datetime] >= '2026-04-01 03:55:00' AND [datetime] < '2026-04-01 04:05:00'
                """
                cursor = conn.cursor()
                cursor.execute(query_edge)
                print(f"Orders near start boundary: {cursor.fetchone()[0]}")
                
                query_edge_end = """
                SELECT COUNT(*) FROM dbo.orderMaster 
                WHERE branchId = 1 AND [datetime] >= '2026-04-20 03:55:00' AND [datetime] < '2026-04-20 04:05:00'
                """
                cursor.execute(query_edge_end)
                print(f"Orders near end boundary: {cursor.fetchone()[0]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
