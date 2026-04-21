import os
import sys
import pandas as pd
import pyodbc
from typing import List

# Add current dir to path
sys.path.append(os.getcwd())

from modules.connection_cloud import enhanced_pool
from modules.config import SELECTED_BRANCH_IDS

def run_audit():
    print("Starting Audit...")
    conn = None
    try:
        # Use the same logic as the dashboard to get connection
        print("Getting connection...")
        conn = enhanced_pool.get_connection("candelahns")
        print("Connected.")
        
        emp_ids = [362, 304, 341, 368]
        start_date = '2026-04-01'
        end_date = '2026-04-17'
        
        query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        
        SELECT 
            e.field_name AS Employee,
            s.sale_id,
            s.external_ref_id,
            s.Nt_amount AS POS_Price,
            rb.BlinkOrderId,
            rb.OrderJson
        FROM tblSales s WITH (NOLOCK)
        INNER JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblInitialRawBlinkOrder rb ON LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) = LTRIM(RTRIM(CONVERT(varchar(64), rb.BlinkOrderId)))
        WHERE s.sale_date >= ? AND s.sale_date < ?
          AND e.shop_employee_id IN ({','.join(['?']*len(emp_ids))})
          AND s.external_ref_type = 'Blinkco order'
          AND s.shop_id IN ({','.join(['?']*len(SELECTED_BRANCH_IDS))})
        """
        params = [start_date, end_date] + emp_ids + SELECTED_BRANCH_IDS
        
        print("Executing query...")
        df = pd.read_sql(query, conn, params=params)
        print(f"Fetched {len(df)} rows.")
        
        if df.empty:
            print("No data found.")
            return

        # 1. Missing Match Count
        missing_match = df[df['BlinkOrderId'].isna()]
        print(f"\nTotal Missing Matches: {len(missing_match)}")
        print(f"Total Lost Amount due to Missing Match: {missing_match['POS_Price'].sum()}")
        
        # 2. JSON Parse Audit
        from modules.blink_reporting import safe_json_order_fields
        
        def safe_get_price(json_str):
            price, _, _, _, ok = safe_json_order_fields(json_str)
            return price if ok else 0.0

        df['Indoge_Price'] = df['OrderJson'].apply(safe_get_price)
        
        mismatched = df[df['BlinkOrderId'].notna() & (abs(df['POS_Price'] - df['Indoge_Price']) > 1)]
        print(f"\nTotal Price Mismatches (Matched but different price): {len(mismatched)}")
        print(f"Total POS Amount for Mismatched: {mismatched['POS_Price'].sum()}")
        print(f"Total Indoge Amount for Mismatched: {mismatched['Indoge_Price'].sum()}")
        
        # 3. Employee-wise Summary
        summary = df.groupby('Employee').agg({
            'POS_Price': 'sum',
            'Indoge_Price': 'sum'
        })
        summary['Diff'] = summary['POS_Price'] - summary['Indoge_Price']
        print("\n--- Employee Summary ---")
        print(summary)
        
        # 4. Show sample missing matches
        if not missing_match.empty:
            print("\n--- Sample Missing Matches (Order not in tblInitialRawBlinkOrder) ---")
            print(missing_match[['Employee', 'sale_id', 'external_ref_id', 'POS_Price']].head(10))

    except Exception as e:
        print(f"Error during audit: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    run_audit()
