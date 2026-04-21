import json
import os
import sys
import pandas as pd

# Add current dir to path
sys.path.append(os.getcwd())

from modules.connection_cloud import enhanced_pool

def fetch_full_json():
    conn = enhanced_pool.get_connection("candelahns")
    query = "SELECT TOP 1 OrderJson, Nt_amount FROM tblSales s JOIN tblInitialRawBlinkOrder rb ON LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) = LTRIM(RTRIM(CONVERT(varchar(64), rb.BlinkOrderId))) WHERE s.sale_id = 2149783"
    df = pd.read_sql(query, conn)
    if not df.empty:
        print(f"POS Price: {df.iloc[0]['Nt_amount']}")
        print("FULL JSON:")
        print(df.iloc[0]['OrderJson'])

if __name__ == "__main__":
    fetch_full_json()
