import os
import re

def fix_all_mappings():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The problematic mapping block found in multiple functions
    # Note: Some have slightly different SELECT 2642 union part, 
    # so we will use a regex to capture variants.
    
    pattern = r'LEFT JOIN \(SELECT Product_Item_ID,.*?FROM TempProductBarcode WITH \(NOLOCK\).*?\) t ON li\.Product_Item_ID = t\.Product_Item_ID AND li\.Product_code = t\.Product_code'
    
    replacement = """-- Official Category Mapping Chain:
        LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id"""

    updated_content = re.sub(pattern, replacement, content)
    
    # Also check if there's a variation where only the subquery is present without the ON clause 
    # (used in some places where they want just the table t)
    # But usually it's combined.
    
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Success: Globally updated multiple mapping blocks in database.py")
    else:
        print("No matches found for the global mapping pattern.")

if __name__ == "__main__":
    fix_all_mappings()
