import os
import re

def clean_duplicate_joins():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find the double-join blocks
    # It looks for our comment line followed by the new joins, 
    # and then another set of the same joins immediately following or nearby.
    
    # We will look for specifically the pi and p joins appearing twice consecutively.
    
    pattern1 = re.compile(r'(-- Official Category Mapping Chain:.*?LEFT JOIN tblDefLineItems t WITH \(NOLOCK\) ON p\.line_item_id = t\.line_item_id)\s+LEFT JOIN tblProductItem pi WITH \(NOLOCK\) ON li\.Product_Item_ID = pi\.Product_Item_ID\s+LEFT JOIN tblDefProducts p WITH \(NOLOCK\) ON pi\.Product_ID = p\.product_id', re.DOTALL)

    updated_content = pattern1.sub(r'\1', content)
    
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Success: Removed duplicate join blocks in database.py")
    else:
        print("No duplicate blocks found matching the primary pattern.")

if __name__ == "__main__":
    clean_duplicate_joins()
