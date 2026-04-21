import os

file_path = 'services/targets_service.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Remove 'Deals' from products_to_hide
    if "products_to_hide = ['Sales - Employee Food', 'Deals', 'Modifiers']" in line:
        line = line.replace("'Deals', ", "")
    
    # 2. Add DEALS -> DEAL mapping
    if "elif word == 'SIDES': word = 'SIDE'" in line:
        # Preserve indentation
        indent = line[:line.find('elif')]
        new_lines.append(line)
        new_lines.append(f"{indent}elif word == 'DEALS': word = 'DEAL'\n")
        continue

    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("Replacement successful.")
