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
    start_ts = "2026-04-01 04:10:00"
    end_ts = "2026-04-20 04:10:00"
    
    try:
        with pyodbc.connect(conn_str) as conn:
            query = """
            SELECT auto_id, orderNumber, datetime, discountAmount, totalDiscount, voucherAmount, netAmount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
              AND ISNULL(isDelete, 0) = 0
              AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
            """
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            
            df['calc_disc'] = df.apply(lambda r: max(r['discountAmount'], r['totalDiscount']) + r['voucherAmount'], axis=1)
            
            print(f'Total Orders Analyzed: {len(df)}')
            print(f'Sum DiscountAmount: {df["discountAmount"].sum():,.2f}')
            print(f'Sum TotalDiscount: {df["totalDiscount"].sum():,.2f}')
            print(f'Sum VoucherAmount: {df["voucherAmount"].sum():,.2f}')
            print(f'Sum Calc Discount (Max pattern): {df["calc_disc"].sum():,.2f}')
            
            # Look for that 10k!
            # Could it be an order where discountAmount AND totalDiscount are both counted?
            df['sum_disc_components'] = df['discountAmount'] + df['totalDiscount'] + df['voucherAmount']
            print(f'Sum of (discountAmount + totalDiscount + Voucher): {df["sum_disc_components"].sum():,.2f}')
            # 11,220 + ? = 13,753? No.

            # Wait, let's look at orders where discountAmount != totalDiscount
            print("\nOrders where discountAmount and totalDiscount differ:")
            diff = df[df['discountAmount'] != df['totalDiscount']]
            print(diff[['auto_id', 'orderNumber', 'datetime', 'discountAmount', 'totalDiscount']])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
