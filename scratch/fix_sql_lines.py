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

# Re-applying fixes with proper commas
# CTEs: Need a comma after total_discount if another column follows
# Line 260 is ") AS total_discount" -> should be ") AS total_discount,"
fix(260, ") AS total_discount,")
fix(261, "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

# SELECT: Need a comma after total_discount
fix(279, "SUM(total_discount) AS total_discount,")
fix(280, "SUM(net_amount) AS total_net_with_delivery")

# Line 309 in aligned CTE
fix(309, ") AS total_discount,")
fix(310, "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

# Line 323 in aligned SELECT
fix(323, "SUM(total_discount) AS total_discount,")
fix(324, "SUM(net_amount) AS total_net_with_delivery")

# Line 356 in order_type CTE
fix(356, ") AS total_discount,")
fix(357, "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

# Line 366 in order_type SELECT
fix(366, "SUM(total_discount) AS total_discount,")
fix(367, "SUM(net_amount) AS total_net_with_delivery")

# Line 401 in payment_status CTE
fix(401, ") AS total_discount,")
fix(402, "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

# Line 411 in payment_status SELECT
fix(411, "SUM(total_discount) AS total_discount,")
fix(412, "SUM(net_amount) AS total_net_with_delivery")

# Line 540 in Area sales CTE
fix(540, ") AS total_discount,")
fix(541, "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount")

# Line 556 in Area sales SELECT
fix(556, "SUM(total_discount) AS total_discount,")
fix(557, "AVG(gross_before_discount - total_discount) AS avg_order_value,")
fix(558, "SUM(net_amount) AS total_net_with_delivery")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Line-by-line surgery v2 complete.")
