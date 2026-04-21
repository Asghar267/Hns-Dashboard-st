import pandas as pd
from modules.database import pool

def audit_mapping():
    conn = pool.get_connection("candelahns")
    
    # Check for categories that match the user's missing list
    query = """
    SELECT DISTINCT t.field_name, COUNT(p.product_id) as product_count
    FROM tblDefLineItems t WITH (NOLOCK)
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON t.line_item_id = p.line_item_id
    WHERE t.field_name LIKE '%Nashta%' 
       OR t.field_name LIKE '%SALES%'
       OR t.field_name LIKE '%Special%'
       OR t.field_name LIKE '%Continental%'
       OR t.field_name LIKE '%Iftar%'
    GROUP BY t.field_name
    """
    df = pd.read_sql(query, conn)
    print("\n--- LINE ITEMS MAPPING ---")
    print(df)
    
    # Check for products that might have these in their names but are UNMAPPED
    query_unmapped = """
    SELECT TOP 20 item_name, product_id, line_item_id
    FROM tblDefProducts WITH (NOLOCK)
    WHERE (item_name LIKE '%Nashta%' 
       OR item_name LIKE '%SALES%'
       OR item_name LIKE '%Special%')
      AND (line_item_id IS NULL OR line_item_id = 0)
    """
    df_um = pd.read_sql(query_unmapped, conn)
    print("\n--- UNMAPPED PRODUCTS WITH TARGET NAMES ---")
    print(df_um)

if __name__ == "__main__":
    audit_mapping()
