import sys

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix SUM(total_discount,)
content = content.replace("SUM(total_discount,)", "SUM(total_discount)")

# 2. Fix the netAmount aggregate issue in GROUP BY queries
# This is a bit tricky but we can target the specific broken pattern
broken_pattern = """CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount"""
lines = content.split('\n')
new_lines = []
skip_next = False

for i, line in enumerate(lines):
    # If the line contains the broken net_amount cast
    if broken_pattern in line:
        # Check if we are inside a GROUP BY context (previous lines have SUMs)
        # Simple heuristic: if the previous non-empty line ends with a comma
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        
        if j >= 0 and lines[j].strip().endswith(','):
            # We are likely in a SELECT list.
            # In GROUP BY queries, we need SUM(net_amount)
            # In non-grouped queries (like summary), it was ALREADY fixed by my previous summary fix 
            # if it was in the base CTE.
            
            # If it's the main SELECT of a grouped query:
            if "SUM(" in content[content.rfind("SELECT", 0, content.find(line)):content.find(line)]:
                line = line.replace(broken_pattern, "SUM(net_amount) AS total_net_with_delivery")

    new_lines.append(line)

final_content = '\n'.join(new_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Applied surgery to fix SQL syntax.")
