import json
import os
import sys
import pandas as pd

# Add current dir to path
sys.path.append(os.getcwd())

from modules.connection_cloud import enhanced_pool
from modules.blink_reporting import safe_json_order_fields

def fetch_samples():
    print("Fetching mismatched samples...")
    conn = enhanced_pool.get_connection("candelahns")
    
    # Fetch 3 mismatched transactions for Zia ur Rehman
    query = """
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT TOP 3
        s.sale_id,
        s.Nt_amount AS POS_Price,
        rb.OrderJson
    FROM tblSales s WITH (NOLOCK)
    INNER JOIN tblInitialRawBlinkOrder rb ON LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) = LTRIM(RTRIM(CONVERT(varchar(64), rb.BlinkOrderId)))
    WHERE s.sale_date >= '2026-04-01'
      AND s.employee_id = 362 -- Zia
      AND s.external_ref_type = 'Blinkco order'
      AND rb.OrderJson IS NOT NULL
      -- We'll filter mismatch in Python to keep SQL simple
    """
    df = pd.read_sql(query, conn)
    
    for idx, row in df.iterrows():
        pos_price = row['POS_Price']
        order_json = row['OrderJson']
        parsed_price, *_ = safe_json_order_fields(order_json)
        
        print(f"\n--- SAMPLE {idx+1} (Sale ID: {row['sale_id']}) ---")
        print(f"POS Price: {pos_price}")
        print(f"Parsed Indoge Price: {parsed_price}")
        print(f"Difference: {pos_price - parsed_price}")
        
        try:
            js = json.loads(order_json)
            print("JSON Content (Snippet):")
            # Print keys and some specific values
            keys_to_show = ['total_price', 'totalPrice', 'grand_total', 'subtotal', 'tax', 'delivery_charges', 'fbr_pos_charge', 'payable_amount']
            for k in keys_to_show:
                if k in js:
                    print(f"  {k}: {js[k]}")
        except:
            print("Could not parse JSON for inspection.")

if __name__ == "__main__":
    fetch_samples()
