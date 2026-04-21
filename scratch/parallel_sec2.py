
import pathlib
import re

file_path = pathlib.Path(r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\daily_branch_snapshots.py')
content = file_path.read_text(encoding='utf-8')

# Add import
if 'import concurrent.futures' not in content:
    content = content.replace('import matplotlib', 'import concurrent.futures\nimport matplotlib')

# Function to wrap the loops in ThreadPoolExecutor
# Let's target the Section 2 loop as first target
section2_pattern = r'# 2\) All products by branch \(separate branch files\).*?for b in branches:.*?rows_per_page=30,.*?subtitle=subtitle_label,.*?\)'
# Actually, it's safer to just replace individual loops with a helper function and a list comprehension

# NEW STRATEGY: 
# 1. Define a helper function inside generate_snapshots or globally for branch rendering
# 2. Use a ThreadPoolExecutor.map or submit

# Let's just do a direct replacement for Section 2
old_loop2 = """        for b in branches:
            bdf = products[products["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not bdf.empty:
                bdf = bdf.drop(columns=["shop_id"])
            table_image(
                bdf,
                title=f"All Products by Branch - {bname}",
                out_path=p_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )"""

new_loop2 = """        def render_branch_products(b):
            bdf = products[products["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not bdf.empty:
                bdf = bdf.drop(columns=["shop_id"])
            table_image(
                bdf,
                title=f"All Products by Branch - {bname}",
                out_path=p_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_branch_products, branches)"""

if old_loop2 in content:
    content = content.replace(old_loop2, new_loop2)
else:
    # Try with CRLF
    old_loop2_crlf = old_loop2.replace('\n', '\r\n')
    if old_loop2_crlf in content:
        content = content.replace(old_loop2_crlf, new_loop2.replace('\n', '\r\n'))

file_path.write_text(content, encoding='utf-8')
print("Successfully parallelized section 2.")
