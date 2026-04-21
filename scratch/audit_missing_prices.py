import pandas as pd
from modules.database import pool

def audit_prices():
    conn = pool.get_connection("candelahns")
    
    # Check for categories that match the user's missing list
    # Let's see their typical Unit_price
    query = """
    SELECT TOP 20 t.field_name, li.Unit_price, p.item_name
    FROM tblSalesLineItems li WITH (NOLOCK)
    JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE t.field_name IN ('Nashta', 'SALES', 'Special Items', 'Continental', 'Sales-Iftar')
      AND li.Unit_price >= 0
    ORDER BY li.Unit_price DESC
    """
    df = pd.read_sql(query, conn)
    print("\n--- PRICE SAMPLES FOR TARGET CATEGORIES ---")
    print(df)
    
    # Check if they EVER have Unit_price = 0
    query_zeros = """
    SELECT t.field_name, COUNT(*) as zero_price_count
    FROM tblSalesLineItems li WITH (NOLOCK)
    JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id
    WHERE t.field_name IN ('Nashta', 'SALES', 'Special Items', 'Continental', 'Sales-Iftar')
      AND li.Unit_price = 0
    GROUP BY t.field_name
    """
    df_z = pd.read_sql(query_zeros, conn)
    print("\n--- ZERO PRICE COUNTS ---")
    print(df_z)

if __name__ == "__main__":
    audit_prices()
