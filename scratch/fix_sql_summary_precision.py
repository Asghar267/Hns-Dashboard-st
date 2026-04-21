import sys

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def fix(line_num, new_content):
    idx = line_num - 1
    if idx < len(lines):
        # Determine indentation from the line itself or use default
        current_line = lines[idx]
        indent = current_line[:len(current_line) - len(current_line.lstrip())] if current_line.strip() else "                "
        lines[idx] = indent + new_content + "\n"
        return True
    return False

# 1. Fix _fetch_summary
# Currently line 65 is delivery_charges,
# We need to insert gross_before_discount after it.
# Instead of complicating with inserts, let's just rewrite the block from 66 to 76
fix(66, "(")
fix(67, "    COALESCE(totalWithTax, 0)")
fix(68, "    + COALESCE(deliveryCharges, 0)")
fix(69, "    + COALESCE(extraCharges, 0)")
fix(70, "    + COALESCE(cardCharges, 0)")
fix(71, ") AS gross_before_discount,")
fix(72, "(")
fix(73, "    COALESCE(")
fix(74, "        CASE")
fix(75, "            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount")
# Oh wait, my line indices are shifting. Let's just replace the whole range carefully.

# Rewriting _fetch_summary CTE range (Lines 66-76)
new_summary_cte = [
    "                (\n",
    "                    COALESCE(totalWithTax, 0)\n",
    "                    + COALESCE(deliveryCharges, 0)\n",
    "                    + COALESCE(extraCharges, 0)\n",
    "                    + COALESCE(cardCharges, 0)\n",
    "                ) AS gross_before_discount,\n",
    "                (\n",
    "                    COALESCE(\n",
    "                        CASE\n",
    "                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount\n",
    "                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount\n",
    "                            ELSE 0\n",
    "                        END,\n",
    "                        0\n",
    "                    ) + COALESCE(voucherAmount, 0)\n",
    "                ) AS total_discount,\n",
    "                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount\n"
]
# lines[65:76] in 0-indexed is lines 66 to 76 in 1-indexed.
lines[65:76] = new_summary_cte

# Also check _fetch_summary final SELECT list commas (now shifted)
# We'll search for the lines to be safe instead of hardcoding shifting indices.
for i in range(len(lines)):
    if "SUM(CASE WHEN is_excluded = 0 THEN total_discount ELSE 0 END) AS total_discount" in lines[i]:
        if "total_discount," not in lines[i]:
             lines[i] = lines[i].replace("total_discount", "total_discount,")
    if "AVG(CASE WHEN is_excluded = 0 THEN (gross_before_discount - total_discount) ELSE NULL END) AS avg_order_value" in lines[i]:
        if "avg_order_value," not in lines[i]:
             lines[i] = lines[i].replace("avg_order_value", "avg_order_value,")

# 2. Fix _fetch_summary_xls_aligned
# Need to find the lines for total_discount and net_amount
for i in range(len(lines)):
    if "AS total_discount" in lines[i] and i+1 < len(lines) and "CAST(ISNULL(netAmount" in lines[i+1]:
        if "total_discount," not in lines[i]:
            lines[i] = lines[i].replace("total_discount", "total_discount,")
    
    # Also fix the SELECT list commas in aligned summary
    if "SUM(total_discount) AS total_discount" in lines[i] and "AVG(" in lines[i+1]:
        if "total_discount," not in lines[i]:
            lines[i] = lines[i].replace("total_discount", "total_discount,")
    if "AVG(total_with_tax - total_discount) AS avg_order_value" in lines[i] and "MIN(" in lines[i+1]:
        if "avg_order_value," not in lines[i]:
            lines[i] = lines[i].replace("avg_order_value", "avg_order_value,")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Precision fix for Summary methods complete.")
