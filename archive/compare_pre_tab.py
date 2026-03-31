def get_pre_tab_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_pattern = 'tab1, tab2'
    idx = content.find(start_pattern)
    return content[:idx].strip()

original_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\hns_dashboard.py"
modular_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\hns_dashboard_modular.py"

orig_pre = get_pre_tab_content(original_path)
mod_pre = get_pre_tab_content(modular_path)

if orig_pre != mod_pre:
    print("Pre-tab content differs!")
    print(f"  Original length: {len(orig_pre)}")
    print(f"  Modular length: {len(mod_pre)}")
    
    # We'll save them to files and check with diff tools or just look at the lengths
    with open('pre_orig.py', 'w', encoding='utf-8') as f: f.write(orig_pre)
    with open('pre_mod.py', 'w', encoding='utf-8') as f: f.write(mod_pre)
else:
    print("Pre-tab content is identical.")
