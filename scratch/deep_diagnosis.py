import pyodbc
import pandas as pd
import json

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

def deep_diagnose():
    conn_str = _build_conn_str()
    # Range covering all 3940 orders
    start_ts = "2026-04-01 04:00:00"
    end_ts = "2026-04-20 04:10:00"
    
    try:
        with pyodbc.connect(conn_str) as conn:
            print("=== DEEP DIAGNOSIS START ===")
            
            # 1. Fetch ALL orders in range for analysis
            query = """
            SELECT 
                auto_id, orderNumber, datetime, orderType, orderStatus, paymentStatus, isDelete, isReject,
                subTotal, taxAmount, deliveryCharges, discountAmount, totalDiscount, voucherAmount, netAmount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
            """
            df = pd.read_sql(query, conn, params=[start_ts, end_ts])
            
            # --- Analysis A: Totals matching the 3,940 set (Non-deleted, DELIVERY) ---
            print("\nAnalysis A: Analysis of the 3,940 orders (Non-deleted, DELIVERY)")
            df_3940 = df[(df['isDelete'] == 0) & (df['orderType'].str.upper() == 'DELIVERY')]
            
            print(f"Total Orders: {len(df_3940)}")
            print(f"Sum Subtotal: {df_3940['subTotal'].sum():,.2f}")
            print(f"Sum Tax: {df_3940['taxAmount'].sum():,.2f}")
            print(f"Sum Delivery: {df_3940['deliveryCharges'].sum():,.2f}")
            
            # Calculate effective discount
            df_3940['eff_discount'] = df_3940.apply(lambda r: max(r['discountAmount'], r['totalDiscount']) + r['voucherAmount'], axis=1)
            print(f"Sum Calculated Discount: {df_3940['eff_discount'].sum():,.2f}")
            print(f"Sum Stored NetAmount: {df_3940['netAmount'].sum():,.2f}")
            
            # --- Analysis B: The 10,000 Discount Mystery ---
            print("\nAnalysis B: Identifying orders with large discounts")
            top_discounts = df_3940[df_3940['eff_discount'] >= 1000].sort_values('eff_discount', ascending=False)
            if not top_discounts.empty:
                print(top_discounts[['orderNumber', 'datetime', 'subTotal', 'eff_discount', 'netAmount']].head(10))
            else:
                print("No order found with discount >= 1000")

            # --- Analysis C: Suspicious Order Statuses ---
            print("\nAnalysis C: Order Statuses in the 3,940 set")
            print(df_3940.groupby(['orderStatus', 'paymentStatus']).size().reset_index(name='count'))
            
            # --- Analysis D: Excluded Orders ---
            print("\nAnalysis D: Orders EXCLUDED from the 3,940 set (in the same time range)")
            df_excluded = df[~df.index.isin(df_3940.index)]
            print(df_excluded.groupby(['isDelete', 'orderType', 'orderStatus']).size().reset_index(name='count'))
            
            # --- Analysis E: Checking for 'Voucher' field specific mismatch ---
            print("\nAnalysis E: Voucher Breakdown")
            vouchers = df_3940[df_3940['voucherAmount'] > 0]
            print(f"Orders with vouchers: {len(vouchers)}, Total Voucher Amount: {vouchers['voucherAmount'].sum():,.2f}")

            print("\n=== DEEP DIAGNOSIS END ===")

    except Exception as e:
        print(f"Error during diagnosis: {e}")

if __name__ == "__main__":
    deep_diagnose()
