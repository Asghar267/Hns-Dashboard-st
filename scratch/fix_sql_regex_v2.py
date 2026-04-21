import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Standardize net_amount aggregation in main SELECTs of GROUP BY queries
# Look for: net_amount (or netAmount) in a SELECT that also has a GROUP BY
# We want to change the final SELECT's net_amount to SUM(net_amount)

# Find all blocks of SELECT ... GROUP BY
def fix_grouped_net(match):
    body = match.group(0)
    # If the block has a GROUP BY, then the net_amount in the SELECT (not in a CTE) must be SUM
    # The CTE definitions usually come before the main SELECT
    
    # Let's target the specific broken lines one by one if they are in a GROUP BY context
    # Broken line pattern: any line starting with spaces, followed by CAST(ISNULL(netAmount...)) AS net_amount
    # occurring BEFORE the 'FROM' that is followed by 'GROUP BY'
    
    select_part = body[:body.lower().find("from")]
    from_part = body[body.lower().find("from"):]
    
    broken_pattern = r"CAST\(ISNULL\(netAmount, 0\) AS DECIMAL\(18, 2\)\) AS net_amount"
    
    if re.search(broken_pattern, select_part):
        # Fix it to SUM(net_amount)
        # Note: In the SELECT list of the main query, it should refer to the CTE alias 'net_amount'
        new_select = re.sub(broken_pattern, "SUM(net_amount) AS total_net_with_delivery", select_part)
        return new_select + from_part
    return body

pattern = re.compile(r"SELECT.*?FROM.*?GROUP BY", re.DOTALL | re.IGNORECASE)
new_text = pattern.sub(fix_grouped_net, text)

# 2. Final check for any remaining SUM(total_discount,)
new_text = new_text.replace("SUM(total_discount,)", "SUM(total_discount)")
new_text = new_text.replace("total_discount ,", "total_discount")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Regex surgery v2 complete.")
