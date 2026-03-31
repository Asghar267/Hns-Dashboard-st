import re

def get_tabs_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tabs = re.findall(r'with tab(\d+):', content)
    tab_contents = {}
    
    for i in range(len(tabs)):
        current_tab_num = tabs[i]
        start_pattern = f'with tab{current_tab_num}:'
        start_idx = content.find(start_pattern)
        
        if i + 1 < len(tabs):
            next_tab_num = tabs[i+1]
            end_pattern = f'with tab{next_tab_num}:'
            end_idx = content.find(end_pattern)
        else:
            end_idx = len(content)
            
        tab_contents[int(current_tab_num)] = content[start_idx:end_idx].strip()
        
    return tab_contents

original_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\hns_dashboard.py"
modular_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\hns_dashboard_modular.py"

orig_tabs = get_tabs_content(original_path)
mod_tabs = get_tabs_content(modular_path)

for t_num in range(1, 13):
    orig = orig_tabs.get(t_num, "")
    mod = mod_tabs.get(t_num, "")
    
    if orig != mod:
        print(f"Tab {t_num} differs!")
        print(f"  Original length: {len(orig)}")
        print(f"  Modular length: {len(mod)}")
        
        # Simple diff start
        common_prefix_len = 0
        min_len = min(len(orig), len(mod))
        for j in range(min_len):
            if orig[j] == mod[j]:
                common_prefix_len += 1
            else:
                break
        
        print(f"  Common prefix length: {common_prefix_len}")
        print(f"  Difference starts at context: {orig[common_prefix_len:common_prefix_len+100]!r}")
        print(f"  VS modular context: {mod[common_prefix_len:common_prefix_len+100]!r}")
        print("-" * 20)
    else:
        print(f"Tab {t_num} is identical.")
