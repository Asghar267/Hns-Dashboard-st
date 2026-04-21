import os
import pyodbc
import pandas as pd

def _build_conn_str():
    driver = "ODBC Driver 17 for SQL Server"
    server = "103.86.55.34,50908"
    database = "HNSYGCC"
    uid = "sa"
    pwd = "123"
    
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )

def main():
    conn_str = _build_conn_str()
    start_ts = "2026-04-01 04:00:00"
    end_ts = "2026-04-20 04:00:00"
    
    query = """
    SELECT
        ISNULL(osg.subgroupName, '(unknown)') AS branch_name,
        COUNT(*) AS total_orders,
        SUM(totalWithTax - (
            ISNULL(
                CASE
                    WHEN ISNULL(discountAmount, 0) > 0 THEN discountAmount
                    WHEN ISNULL(totalDiscount, 0) > 0 THEN totalDiscount
                    ELSE 0
                END,
                0
            ) + ISNULL(voucherAmount, 0)
        )) AS net_amount
    FROM dbo.orderMaster o
    LEFT JOIN dbo.orderSubgroup osg ON osg.orderSubGroupId = o.orderSubgroupId
    WHERE o.[datetime] >= ? AND o.[datetime] < ?
      AND ISNULL(o.isDelete, 0) = 0
      AND UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '')) = 'DELIVERY'
    GROUP BY ISNULL(osg.subgroupName, '(unknown)')
    ORDER BY total_orders DESC;
    """
    
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            print("Branch-wise Breakdown (XLS-aligned):")
            print(df)
            print(f"\nTotal Orders: {df['total_orders'].sum()}")
            
            # Also check if there are any orders with NOT 'DELIVERY' that might be intended for branches
            query_all_types = """
            SELECT
                UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '(blank)')) AS order_type,
                COUNT(*) AS total_orders
            FROM dbo.orderMaster o
            WHERE o.[datetime] >= ? AND o.[datetime] < ?
              AND ISNULL(o.isDelete, 0) = 0
            GROUP BY UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '(blank)'))
            """
            df_types = pd.read_sql(query_all_types, conn, params=[start_ts, end_ts])
            print("\nOrder Type Breakdown:")
            print(df_types)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
