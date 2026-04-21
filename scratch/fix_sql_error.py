import sys

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Match the specific line in the base CTE
    if "total_discount" in line and "AS DECIMAL(18, 2)" not in line and ")" in line and i < 150:
        if "total_discount" in line and "," not in line:
            lines[i] = line.replace("total_discount", "total_discount,")
            lines.insert(i + 1, "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount\n")
            print(f"Applied fix at line {i+1}")
            break
else:
    print("Could not find targets to fix")
    sys.exit(1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
