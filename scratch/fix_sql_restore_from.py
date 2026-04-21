import sys

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def fix(line_num, new_content):
    idx = line_num - 1
    if idx < len(lines):
        indent = lines[idx][:lines[idx].find(lines[idx].strip())] if lines[idx].strip() else "                "
        lines[idx] = indent + new_content + "\n"
        return True
    return False

# Restoring FROM filtered and continuing the SELECT fix for _fetch_area_sales
fix(559, "            SUM(net_amount) AS total_net_with_delivery")
# Add the missing FROM line back
lines.insert(559, "        FROM filtered\n")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Restored FROM filtered and fixed naming.")
