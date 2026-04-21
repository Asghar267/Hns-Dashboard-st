import os

file_path = 'services/targets_service.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Add NASHTA -> BREAKFAST mapping
    if "elif word == 'DEALS': word = 'DEAL'" in line:
        # Preserve indentation
        indent = line[:line.find('elif')]
        new_lines.append(line)
        new_lines.append(f"{indent}elif word == 'NASHTA': word = 'BREAKFAST'\n")
        continue

    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("Replacement successful.")
