import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific missing comma in _fetch_latest_snapshot and others
# Pattern: ") AS total_discount" followed by optional whitespace and then "SUM("
content = re.sub(r'(\) AS total_discount)(\s+SUM\()', r'\1,\2', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SQL Comma Fix Surgery complete.")
