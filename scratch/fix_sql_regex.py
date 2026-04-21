import re
import os

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_select = False
has_group_by = False
current_query_start = 0

# Pass 1: Remove all "SUM(total_discount,)" trailing commas
for i in range(len(lines)):
    lines[i] = lines[i].replace("SUM(total_discount,)", "SUM(total_discount)")

# Pass 2: Fix the non-aggregated net_amount in GROUP BY queries
# We'll look for blocks of SELECT ... GROUP BY
full_text = "".join(lines)

def fix_group_by_select(match):
    select_part = match.group(1)
    # If the select part contains the broken pattern
    broken = "CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount"
    if broken in select_part:
        # Check if there are other aggregates in the SELECT suggesting it's the final select
        if "SUM(" in select_part:
            fixed_select = select_part.replace(broken, "SUM(net_amount) AS total_net_with_delivery")
            return f"SELECT{fixed_select}FROM{match.group(2)}GROUP BY"
    return match.group(0)

# Regex to find SELECT ... FROM ... GROUP BY blocks
# We use re.DOTALL to match across lines
pattern = re.compile(r"SELECT(.*?)FROM(.*?)GROUP BY", re.DOTALL | re.IGNORECASE)
fixed_text = pattern.sub(fix_group_by_select, full_text)

# Pass 3: Fix specific broken AVG call in _fetch_area_sales
# josh logic: AVG(gross_before_discount - total_discount,)
fixed_text = fixed_text.replace("AVG(gross_before_discount - total_discount,)", "AVG(gross_before_discount - total_discount)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_text)

print("Regex surgery complete.")
