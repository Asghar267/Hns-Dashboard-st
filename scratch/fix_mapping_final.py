import os

def fix_remaining_mappings():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacement logic for multi-line LEFT JOIN subqueries on TempProductBarcode
    # This replacement is safer than regex for multi-line SQL
    
    mapping_replacement = """-- Official Category Mapping Chain:
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id"""

    mapping_replacement_alt = """-- Official Category Mapping Chain:
                LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
                LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
                LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id"""

    updated_content = content

    # 1. Fix get_cached_hourly_sales (approx line 711)
    old_hourly = """        LEFT JOIN (
            SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name
            FROM TempProductBarcode WITH (NOLOCK)
            UNION ALL SELECT 2642, '0570', 'Deals'
        ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code"""
    
    if old_hourly in updated_content:
        updated_content = updated_content.replace(old_hourly, mapping_replacement)
        print("Updated get_cached_hourly_sales")

    # 2. Fix order_type distribution variant (line 726)
    old_variant = """    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name
        FROM TempProductBarcode WITH (NOLOCK)
        UNION ALL SELECT 2642, '0570', 'Deals'
    ) t ON sl.Product_Item_ID = t.Product_Item_ID AND sl.Product_code = t.Product_code"""
    # Note: this one uses "sl" instead of "li"
    mapping_replacement_sl = mapping_replacement.replace("li.", "sl.")
    if old_variant in updated_content:
        updated_content = updated_content.replace(old_variant, mapping_replacement_sl)
        print("Updated order_type distribution variant")

    # 3. Fix get_cached_order_type_others_breakdown (line 1253)
    old_others = """            LEFT JOIN (
                SELECT
                    Product_Item_ID,
                    CAST(Product_code AS VARCHAR(50)) as Product_code,
                    CAST(field_name AS VARCHAR(100)) as field_name
                FROM TempProductBarcode WITH (NOLOCK)
                UNION ALL SELECT 2642, '0570', 'Deals'
            ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code"""

    if old_others in updated_content:
        updated_content = updated_content.replace(old_others, mapping_replacement_alt)
        print("Updated get_cached_order_type_others_breakdown")

    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("File successfully saved with remaining fixes.")
    else:
        print("No matches found for remaining blocks.")

if __name__ == "__main__":
    fix_remaining_mappings()
