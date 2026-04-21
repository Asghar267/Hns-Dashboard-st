import os

def fix_database_mapping():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix get_all_available_categories mapping
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

    # 2. Fix get_cached_line_items mapping
    # We replace the entire nested query block
    import re
    
    # Looking for the LEFT JOIN block in get_cached_line_items
    pattern = r'LEFT JOIN \(\s+SELECT Product_Item_ID.*?%\'\)'
    replacement = """-- Official Category Mapping Chain:
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id"""
    
    # Since the SQL is inside a f-string, we might need to be careful with braces, 
    # but the pattern above should match the raw string part.
    
    # Try step-by-step
    updated_content = content
    if old_cat_part in content:
        updated_content = updated_content.replace(old_cat_part, new_cat_part)
        print("Updated get_all_available_categories")
    else:
        print("Could not find get_all_available_categories block")

    # For get_cached_line_items, let's use a more direct approach by finding the markers
    start_marker = "LEFT JOIN ("
    end_marker = "LIKE CAST(li.Product_code AS VARCHAR(50)) + '%')"
    
    if start_marker in updated_content and end_marker in updated_content:
        # We find the specific instance between line_totals and tblDefShops
        lines = updated_content.splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if "LEFT JOIN (" in line and "SELECT Product_Item_ID" in lines[lines.index(line)+1]:
                skip = True
                new_lines.append("    -- Official Category Mapping Chain:")
                new_lines.append("    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID")
                new_lines.append("    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id")
                new_lines.append("    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id")
            elif skip and "LIKE CAST(li.Product_code AS VARCHAR(50))" in line and " %')" in line:
                skip = False
                continue
            
            if not skip:
                new_lines.append(line)
        
        updated_content = "\n".join(new_lines)
        print("Updated get_cached_line_items using line markers")
    else:
         print("Could not find get_cached_line_items markers")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("File saved.")

if __name__ == "__main__":
    fix_database_mapping()
