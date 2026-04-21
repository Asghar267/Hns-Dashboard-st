import os
import sys
import pandas as pd

# Add current dir to path
sys.path.append(os.getcwd())

from modules.connection_cloud import enhanced_pool

def check_item_count():
    conn = enhanced_pool.get_connection("candelahns")
    
    # Check POS item count for Sale 2149783
    query = """
    SELECT 
        SUM(qty) as pos_item_qty,
        COUNT(Product_Item_ID) as pos_distinct_items
    FROM tblSalesLineItems
    WHERE sale_id = 2149783
    """
    df = pd.read_sql(query, conn)
    print("POS Sales Line Items Summary:")
    print(df)

if __name__ == "__main__":
    check_item_count()
