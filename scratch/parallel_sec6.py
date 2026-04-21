
import pathlib
import re

file_path = pathlib.Path(r'c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\daily_branch_snapshots.py')
content = file_path.read_text(encoding='utf-8')

# Section 6: Khadda Daily Employee loop
old_loop6 = """            for (emp_id, emp_code, emp_name), sub in daily_all.groupby(["employee_id", "employee_code", "employee_name"]):
                sub = sub.copy()
                day_df = pd.DataFrame({"sale_day": all_days})
                sub = day_df.merge(sub, on="sale_day", how="left")
                sub["employee_name"] = emp_name
                sub["employee_id"] = emp_id
                sub["employee_code"] = emp_code
                if "shop_name" in sub.columns:
                    sub["shop_name"] = sub["shop_name"].fillna("Khadda Main Branch")
                sub["tx_count"] = pd.to_numeric(sub.get("tx_count", 0), errors="coerce").fillna(0).astype(int)
                sub["total_sale"] = pd.to_numeric(sub.get("total_sale", 0), errors="coerce").fillna(0.0)

                total_tx = int(sub["tx_count"].sum())
                total_sales = float(sub["total_sale"].sum())

                show = sub[["sale_day", "tx_count", "total_sale"]].copy()
                show = show.rename(columns={"sale_day": "Date", "tx_count": "Tx Count", "total_sale": "Sales"})
                show["Date"] = show["Date"].astype(str)
                show["Sales"] = show["Sales"].map(lambda x: f"{x:,.0f}")

                show = pd.concat(
                    [show, pd.DataFrame([{"Date": "TOTAL", "Tx Count": total_tx, "Sales": f"{total_sales:,.0f}"}])],
                    ignore_index=True,
                )

                safe_name = _safe_filename(emp_name)
                out_path = emp_dir / f"{safe_name}_{int(emp_id)}.png"
                table_image(
                    show,
                    title=f"Khadda Daily Sales - {emp_name}",
                    out_path=out_path,
                    rows_per_page=35,
                    subtitle=f"{min_day} to {max_day}",
                )"""

new_loop6 = """        def render_khadda_daily(group):
            (emp_id, emp_code, emp_name), sub = group
            sub = sub.copy()
            day_df = pd.DataFrame({"sale_day": all_days})
            sub = day_df.merge(sub, on="sale_day", how="left")
            sub["employee_name"] = emp_name
            sub["employee_id"] = emp_id
            sub["employee_code"] = emp_code
            if "shop_name" in sub.columns:
                sub["shop_name"] = sub["shop_name"].fillna("Khadda Main Branch")
            sub["tx_count"] = pd.to_numeric(sub.get("tx_count", 0), errors="coerce").fillna(0).astype(int)
            sub["total_sale"] = pd.to_numeric(sub.get("total_sale", 0), errors="coerce").fillna(0.0)

            total_tx = int(sub["tx_count"].sum())
            total_sales = float(sub["total_sale"].sum())

            show = sub[["sale_day", "tx_count", "total_sale"]].copy()
            show = show.rename(columns={"sale_day": "Date", "tx_count": "Tx Count", "total_sale": "Sales"})
            show["Date"] = show["Date"].astype(str)
            show["Sales"] = show["Sales"].map(lambda x: f"{x:,.0f}")

            show = pd.concat(
                [show, pd.DataFrame([{"Date": "TOTAL", "Tx Count": total_tx, "Sales": f"{total_sales:,.0f}"}])],
                ignore_index=True,
            )

            safe_name = _safe_filename(emp_name)
            out_path = emp_dir / f"{safe_name}_{int(emp_id)}.png"
            table_image(
                show,
                title=f"Khadda Daily Sales - {emp_name}",
                out_path=out_path,
                rows_per_page=35,
                subtitle=f"{min_day} to {max_day}",
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(render_khadda_daily, daily_all.groupby(["employee_id", "employee_code", "employee_name"]))"""

if old_loop6 in content:
    content = content.replace(old_loop6, new_loop6)
else:
    old_loop6_crlf = old_loop6.replace('\n', '\r\n')
    if old_loop6_crlf in content:
        content = content.replace(old_loop6_crlf, new_loop6.replace('\n', '\r\n'))

file_path.write_text(content, encoding='utf-8')
print("Successfully parallelized section 6.")
