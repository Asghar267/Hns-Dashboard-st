import os

def unhide_deals():
    file_path = r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\modules\config.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Look for 'Deals' in the list
    new_lines = []
    for line in lines:
        if "'Deals'" in line and "HIDDEN_PRODUCTS" not in line:
            print(f"Removing line: {line.strip()}")
            continue
        new_lines.append(line)

    if len(new_lines) != len(lines):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Successfully updated config.py to unhide Deals.")
    else:
        print("Could not find 'Deals' in a way that could be safely removed.")

if __name__ == "__main__":
    unhide_deals()
