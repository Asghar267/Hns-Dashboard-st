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

# Fix _fetch_branch_counter_drilldown
fix(488, "                    ) + COALESCE(voucherAmount, 0)")
fix(489, "                ) AS total_discount,")
fix(490, "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount,")

fix(506, "            SUM(total_discount) AS total_discount,")
fix(507, "            AVG(gross_before_discount - total_discount) AS avg_order_value,")
fix(508, "            SUM(net_amount) AS total_net_with_delivery,")

# Fix _fetch_area_sales
fix(538, "                        END,")
fix(539, "                        0")
fix(540, "                    ) + COALESCE(voucherAmount, 0)")
fix(541, "                ) AS total_discount,")
fix(542, "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

fix(557, "            AVG(gross_before_discount - total_discount) AS avg_order_value,")
fix(558, "            SUM(net_amount) AS total_net_with_delivery")
# Line 559 was a duplicate broken CAST, we need to clear it or it will cause error
fix(559, "        FROM filtered") # Overwriting the 'FROM filtered' which was at 560
# Wait, look at the view_file again:
# 559:                 CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
# 560:         FROM filtered
# 561:         GROUP BY delv_area
# 562:         ORDER BY total_net_sales DESC;

# I'll just remove the redundant line from 559
lines.pop(558) # 559 in 1-indexed is 558 in 0-indexed.

# Fix _fetch_excluded_orders
fix(589, "                    ) + COALESCE(voucherAmount, 0)")
fix(590, "                ) AS total_discount,")
fix(591, "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Line-by-line surgery v3 complete.")
