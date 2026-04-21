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
        auto_id, orderNumber, subTotal, taxAmount, deliveryCharges, 
        discountAmount, totalDiscount, voucherAmount, netAmount
    FROM dbo.orderMaster
    WHERE [datetime] >= ? AND [datetime] < ?
      AND isDelete = 0
      AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
      AND (discountAmount > 0 OR totalDiscount > 0)
    """
    
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            # Handle potential NaNs
            for col in ['discountAmount', 'totalDiscount', 'voucherAmount', 'subTotal', 'taxAmount', 'deliveryCharges', 'netAmount']:
                df[col] = df[col].fillna(0)

            df['max_disc'] = df[['discountAmount', 'totalDiscount']].max(axis=1) + df['voucherAmount']
            df['calc_net'] = df['subTotal'] + df['taxAmount'] + df['deliveryCharges'] - df['max_disc']
            df['diff'] = df['netAmount'] - df['calc_net']
            
            non_zero_diff = df[df['diff'].abs() > 0.01]
            if not non_zero_diff.empty:
                print("Orders with NetAmount Mismatch:")
                print(non_zero_diff[['auto_id', 'orderNumber', 'max_disc', 'netAmount', 'calc_net', 'diff']])
                print("\nSum of Net Mismatches:", non_zero_diff['diff'].sum())
            else:
                print("All orders with discounts have perfectly consistent NetAmounts (Sub+Tax+Del-Disc).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
