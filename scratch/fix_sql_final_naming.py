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

# Fix _fetch_area_sales SELECT list
fix(555, "            COUNT(*) AS total_orders,")
fix(556, "            SUM(gross_before_discount - total_discount) AS total_net_sales,")
fix(557, "            SUM(total_discount) AS total_discount,")
fix(558, "            AVG(gross_before_discount - total_discount) AS avg_order_value,")
fix(559, "            SUM(net_amount) AS total_net_with_delivery")

# Fix _fetch_branch_counter_drilldown SELECT list (was missing sum(net_amount) and had missing commas)
fix(504, "            COUNT(*) AS total_orders,")
fix(505, "            SUM(gross_before_discount - total_discount) AS total_net_sales,")
fix(506, "            SUM(total_discount) AS total_discount,")
fix(507, "            SUM(net_amount) AS total_net_with_delivery,")
fix(508, "            AVG(gross_before_discount - total_discount) AS avg_order_value,")
fix(509, "            MIN([datetime]) AS first_order_ts,")
fix(510, "            MAX([datetime]) AS last_order_ts")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Final naming surgery complete.")
