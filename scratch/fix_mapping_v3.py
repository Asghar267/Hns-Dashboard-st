import os

def fix_mapping_v3():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\database.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skipped = 0
    for line in lines:
        # Check for the specific JOIN block in get_cached_line_items (around line 1035)
        # Using a very unique part of the line to identify it
        if "FROM TempProductBarcode WITH (NOLOCK) UNION ALL SELECT 2642" in line and "t ON li.Product_Item_ID" not in line:
            # Reached line 1035
            new_lines.append("    -- Official Category Mapping Chain:\n")
            new_lines.append("    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID\n")
            new_lines.append("    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id\n")
            new_lines.append("    LEFT JOIN tblDefLineItems t WITH (NOLOCK) ON p.line_item_id = t.line_item_id\n")
            skipped = 1 # Skip the current line and the next ON line
            continue
        
        if skipped == 1:
            if "ON li.Product_Item_ID = t.Product_Item_ID" in line:
                skipped = 0
                continue
            else:
                # If something is wrong, stop skipping
                skipped = 0

        new_lines.append(line)

    if len(new_lines) > 2000: # Safety check
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Successfully updated file. Total lines: {len(new_lines)}")
    else:
        print(f"Update failed or safety check failed. New line count: {len(new_lines)}")

if __name__ == "__main__":
    fix_mapping_v3()
