
import pathlib
import re

file_path = pathlib.Path(r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\daily_branch_snapshots.py')
content = file_path.read_text(encoding='utf-8')

# Section 5: Material Cost - Employee Summary branch-wise
old_loop5 = """        for b in branches:
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            bdf = e_show_all.copy()
            if not bdf.empty and "Shop" in bdf.columns:
                bdf = bdf[bdf["Shop"] == bname].copy()
            if "Shop" in bdf.columns:
                bdf = bdf.drop(columns=["Shop"], errors="ignore")
            bdf = bdf.drop(columns=["shop_id", "total_transactions", "Avg Rate"], errors="ignore")
            table_image(
                bdf,
                title=f"Material Cost Commission - Employee Summary - {bname}",
                out_path=m_dir / f"02_employee_summary_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=32,
                subtitle=subtitle_label,
            )"""

new_loop5 = """        def render_mcc_emp_summary(b):
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            bdf = e_show_all.copy()
            if not bdf.empty and "Shop" in bdf.columns:
                bdf = bdf[bdf["Shop"] == bname].copy()
            if "Shop" in bdf.columns:
                bdf = bdf.drop(columns=["Shop"], errors="ignore")
            bdf = bdf.drop(columns=["shop_id", "total_transactions", "Avg Rate"], errors="ignore")
            table_image(
                bdf,
                title=f"Material Cost Commission - Employee Summary - {bname}",
                out_path=m_dir / f"02_employee_summary_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=32,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_mcc_emp_summary, branches)"""

if old_loop5 in content:
    content = content.replace(old_loop5, new_loop5)
else:
    old_loop5_crlf = old_loop5.replace('\n', '\r\n')
    if old_loop5_crlf in content:
        content = content.replace(old_loop5_crlf, new_loop5.replace('\n', '\r\n'))

file_path.write_text(content, encoding='utf-8')
print("Successfully parallelized section 5.")
