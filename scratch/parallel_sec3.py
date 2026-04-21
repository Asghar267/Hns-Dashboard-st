
import pathlib
import re

file_path = pathlib.Path(r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\daily_branch_snapshots.py')
content = file_path.read_text(encoding='utf-8')

# Section 3: QR Employee No Sales
old_loop3 = """        for b in branches:
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                edf["Indoge_total_price"] = pd.to_numeric(edf["Indoge_total_price"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["Indoge_commission"] = pd.to_numeric(edf["Indoge_commission"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        "employee_id": "Emp ID",
                        "employee_code": "Field Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "Indoge_total_price": "QR Total Sales",
                        "Indoge_commission": "QR Commission",
                    }
                )
            table_image(
                edf,
                title=f"Employee-wise QR Total Sales and Commission - {bname}",
                out_path=e_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )"""

new_loop3 = """        def render_emp_no_sales(b):
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                edf["Indoge_total_price"] = pd.to_numeric(edf["Indoge_total_price"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["Indoge_commission"] = pd.to_numeric(edf["Indoge_commission"], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        "employee_id": "Emp ID",
                        "employee_code": "Field Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "Indoge_total_price": "QR Total Sales",
                        "Indoge_commission": "QR Commission",
                    }
                )
            table_image(
                edf,
                title=f"Employee-wise QR Total Sales and Commission - {bname}",
                out_path=e_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_emp_no_sales, branches)"""

# Section 3b: QR Employee With Sales
old_loop3b = """        for b in branches:
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "total_sale",
                    "Candelahns_commission",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                for col in ["total_sale", "Candelahns_commission", "Indoge_total_price", "Indoge_commission"]:
                    edf[col] = pd.to_numeric(edf[col], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        "employee_id": "Emp ID",
                        "employee_code": "Field Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "total_sale": "Total Sales",
                        "Candelahns_commission": "Candelahns Comm.",
                        "Indoge_total_price": "Indoge Total",
                        "Indoge_commission": "Indoge Comm.",
                    }
                )
            table_image(
                edf,
                title=f"QR Employee Totals (with Sales) - {bname}",
                out_path=e2_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )"""

new_loop3b = """        def render_emp_with_sales(b):
            edf = emp[emp["shop_id"] == int(b)].copy()
            bname = BRANCH_NAMES.get(int(b), f"branch_{b}")
            if not edf.empty:
                edf = edf[[
                    "employee_id",
                    "employee_code",
                    "employee_name",
                    "transaction_count",
                    "total_sale",
                    "Candelahns_commission",
                    "Indoge_total_price",
                    "Indoge_commission",
                ]].copy()
                for col in ["total_sale", "Candelahns_commission", "Indoge_total_price", "Indoge_commission"]:
                    edf[col] = pd.to_numeric(edf[col], errors="coerce").fillna(0.0).map(lambda x: f"{x:,.0f}")
                edf["transaction_count"] = pd.to_numeric(edf["transaction_count"], errors="coerce").fillna(0).astype(int)
                edf = edf.rename(
                    columns={
                        "employee_id": "Emp ID",
                        "employee_code": "Field Code",
                        "employee_name": "Employee",
                        "transaction_count": "Tx Count",
                        "total_sale": "Total Sales",
                        "Candelahns_commission": "Candelahns Comm.",
                        "Indoge_total_price": "Indoge Total",
                        "Indoge_commission": "Indoge Comm.",
                    }
                )
            table_image(
                edf,
                title=f"QR Employee Totals (with Sales) - {bname}",
                out_path=e2_dir / f"{int(b):02d}_{bname.replace(' ', '_').lower()}.png",
                rows_per_page=28,
                subtitle=subtitle_label,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_emp_with_sales, branches)"""

if old_loop3 in content:
    content = content.replace(old_loop3, new_loop3)
else:
    old_loop3_crlf = old_loop3.replace('\n', '\r\n')
    if old_loop3_crlf in content:
        content = content.replace(old_loop3_crlf, new_loop3.replace('\n', '\r\n'))

if old_loop3b in content:
    content = content.replace(old_loop3b, new_loop3b)
else:
    old_loop3b_crlf = old_loop3b.replace('\n', '\r\n')
    if old_loop3b_crlf in content:
        content = content.replace(old_loop3b_crlf, new_loop3b.replace('\n', '\r\n'))

file_path.write_text(content, encoding='utf-8')
print("Successfully parallelized section 3 and 3b.")
