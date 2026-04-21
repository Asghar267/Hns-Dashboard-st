import sys

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

count = 0
i = 0
while i < len(lines):
    line = lines[i]
    # Look for the last line of the CTE select list
    if "total_discount" in line and ")" in line and i + 1 < len(lines) and "FROM" in lines[i+1]:
        if "," not in line:
            lines[i] = line.replace("total_discount", "total_discount,")
            lines.insert(i + 1, "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount\n")
            count += 1
            i += 1 # Skip the newly inserted line
    i += 1

print(f"Applied fix to {count} locations")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
