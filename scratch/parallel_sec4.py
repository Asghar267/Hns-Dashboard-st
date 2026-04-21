
import pathlib
import re

file_path = pathlib.Path(r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\daily_branch_snapshots.py')
content = file_path.read_text(encoding='utf-8')

# Section 4: Ramzan Deals
old_loop4 = """        for b in branches:
            rdf = ram_branch[ram_branch["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not rdf.empty:
                rdf = rdf.drop(columns=["shop_id", "Product_Item_ID", "Product_code"])
            table_image(
                rdf,
                title=f"Ramzan Deals - Branch-wise Sales - {bname}",
                out_path=r_dir / f"branch_{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )"""

new_loop4 = """        def render_ramzan_branch(b):
            rdf = ram_branch[ram_branch["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not rdf.empty:
                rdf = rdf.drop(columns=["shop_id", "Product_Item_ID", "Product_code"])
            table_image(
                rdf,
                title=f"Ramzan Deals - Branch-wise Sales - {bname}",
                out_path=r_dir / f"branch_{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=30,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_ramzan_branch, branches)"""

if old_loop4 in content:
    content = content.replace(old_loop4, new_loop4)
else:
    old_loop4_crlf = old_loop4.replace('\n', '\r\n')
    if old_loop4_crlf in content:
        content = content.replace(old_loop4_crlf, new_loop4.replace('\n', '\r\n'))

file_path.write_text(content, encoding='utf-8')
print("Successfully parallelized section 4.")
