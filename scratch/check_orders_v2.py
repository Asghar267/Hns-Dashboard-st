import os
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
    
    query = """
    SELECT
        ISNULL(b.branchName, '(Unknown: ' + CAST(o.branchId AS VARCHAR) + ')') AS branch_name,
        COUNT(*) AS total_orders,
        SUM(o.totalWithTax - (
            ISNULL(
                CASE
                    WHEN ISNULL(o.discountAmount, 0) > 0 THEN o.discountAmount
                    WHEN ISNULL(o.totalDiscount, 0) > 0 THEN o.totalDiscount
                    ELSE 0
                END,
                0
            ) + ISNULL(o.voucherAmount, 0)
        )) AS net_amount
    FROM dbo.orderMaster o
    LEFT JOIN dbo.addBranch b ON b.branchId = o.branchId
    WHERE o.[datetime] >= ? AND o.[datetime] < ?
      AND ISNULL(o.isDelete, 0) = 0
      AND UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '')) = 'DELIVERY'
    GROUP BY b.branchName, o.branchId
    ORDER BY total_orders DESC;
    """
    
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            print("Branch-wise Breakdown (HNSYGCC):")
            print(df)
            print(f"\nTotal Orders: {df['total_orders'].sum()}")
            
            # Check for orders that might be excluded by the 'DELIVERY' filter but belong to these branches
            query_all = """
            SELECT
                UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '(blank)')) AS order_type,
                COUNT(*) AS total_orders
            FROM dbo.orderMaster o
            WHERE o.[datetime] >= ? AND o.[datetime] < ?
              AND ISNULL(o.isDelete, 0) = 0
            GROUP BY UPPER(ISNULL(LTRIM(RTRIM(o.orderType)), '(blank)'))
            """
            df_all = pd.read_sql(query_all, conn, params=[start_ts, end_ts])
            print("\nOrder Type Breakdown (Non-deleted):")
            print(df_all)

            # Check if there are any orders for these dates that are NOT in HNSYGCC but in the user's list?
            # User's total is 3940. DB total is 3939.
            # One order is missing in DB or filtered out.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
