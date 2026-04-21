import os

file_path = 'services/targets_service.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Add Daily Target calculation
    if "df_res['Remaining'] = df_res['Target'] - df_res['Current Sale']" in line:
        indent = line[:line.find("df_res['Remaining']")]
        new_lines.append(f"{indent}num_days = monthrange(target_year, target_month)[1]\n")
        new_lines.append(f"{indent}df_res['Daily Target'] = df_res['Target'] / num_days\n")
        new_lines.append(line)
        continue
    
    # Update return columns
    if "return df_res[['Product', 'Target', 'Type', 'Current Sale', 'Remaining', 'Achievement %', 'Bonus']]" in line:
        line = line.replace("'Target', ", "'Target', 'Daily Target', ")
        new_lines.append(line)
        continue

    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("Daily Target added to targets_service.py")
