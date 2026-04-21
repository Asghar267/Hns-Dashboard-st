import os

def fix_database_mapping_safe():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # SECTION 1: Fix get_all_available_categories mapping
    # Searching for the specific Candelahns mapping part
    old_cat_part = """    # Get categories from Candelahns TempProductBarcode (mapping table)
    try:
        conn = pool.get_connection("candelahns")
        df_candel = pd.read_sql(
            \"\"\"SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT DISTINCT field_name as category_name 
            FROM TempProductBarcode WITH (NOLOCK)
            WHERE field_name IS NOT NULL AND field_name <> ''
            ORDER BY field_name\"\"\",
            conn
        )"""
    
    new_cat_part = """    # Get categories from Candelahns (official tblDefLineItems)
    try:
        conn = pool.get_connection("candelahns")
        df_candel = pd.read_sql(
            \"\"\"SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            SELECT DISTINCT field_name as category_name 
            FROM tblDefLineItems WITH (NOLOCK)
            WHERE field_name IS NOT NULL AND field_name <> ''
            UNION
            SELECT DISTINCT field_name as category_name 
            FROM TempProductBarcode WITH (NOLOCK)
            WHERE field_name IS NOT NULL AND field_name <> ''
            ORDER BY category_name\"\"\",
            conn
        )"""

    # SECTION 2: Fix get_cached_line_items mapping
    # We will look for the specific block of the LEFT JOIN
    # Note: I am using the exact whitespace found previously
    old_sql_block = """    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM TempProductBarcode WITH (NOLOCK) 
        UNION ALL 
        SELECT 0 AS Product_Item_ID, CAST(product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM tblDefLineItems WITH (NOLOCK)
    ) t ON (li.Product_Item_ID = t.Product_Item_ID 
        OR CAST(li.Product_code AS VARCHAR(50)) = CAST(t.Product_code AS VARCHAR(50))
        OR CAST(li.Product_code AS VARCHAR(50)) LIKE CAST(t.Product_code AS VARCHAR(50)) + '%'
        OR CAST(t.Product_code AS VARCHAR(50)) LIKE CAST(li.Product_code AS VARCHAR(50)) + '%')"""

    new_sql_block = """    -- Official Category Mapping Chain:
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id"""

    updated_content = content
    
    # Check for category list update
    if old_cat_part in content:
        updated_content = updated_content.replace(old_cat_part, new_cat_part)
        print("Success: Updated get_all_available_categories")
    else:
        # Fallback for slight whitespace variations
        print("Warning: Could not find exact match for get_all_available_categories. Checking normalized version...")
        if "FROM TempProductBarcode" in content and "get_all_available_categories" in content:
             print("Manual intervention needed or check whitespace.")

    # Check for line items update
    if old_sql_block in updated_content:
        updated_content = updated_content.replace(old_sql_block, new_sql_block)
        print("Success: Updated get_cached_line_items mapping")
    else:
        print("Warning: Could not find exact match for get_cached_line_items block.")

    # Write back the full content if changes were made
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("File successfully saved.")
    else:
        print("No changes applied.")

if __name__ == "__main__":
    fix_database_mapping_safe()
