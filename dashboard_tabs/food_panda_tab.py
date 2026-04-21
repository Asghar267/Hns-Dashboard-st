"""





Food Panda Tab          





Lists Food Panda transactions and summaries.





"""











from __future__ import annotations









import re




from pathlib import Path




from typing import List









import pandas as pd




import streamlit as st









from modules.connection_cloud import DatabaseConfig




from modules.database import pool, placeholders, build_filter_clause




from modules.utils import format_currency, export_to_excel




from modules.responsive import (




    clamp_dataframe_height,




    get_responsive_context,




    pick_columns_for_tier,




    responsive_columns,




)




from modules.foodpanda_reconciliation import (




    load_foodpanda_order_summary,




    load_tower_order_details,




    fetch_foodpanda_sales_by_codes,




    fetch_foodpanda_sales_in_range,




    reconcile_foodpanda_orders,




)










HIDE_EXTERNAL_REF_COLS = {"external_ref_type", "external_ref_id"}

















def _drop_hidden_cols(df: pd.DataFrame) -> pd.DataFrame:





    if df is None or df.empty:





        return df





    return df.drop(columns=[c for c in HIDE_EXTERNAL_REF_COLS if c in df.columns], errors="ignore")

















def _attach_tower_cancellation_reasons(df: pd.DataFrame, tower_df: pd.DataFrame | None) -> pd.DataFrame:




    if df is None or df.empty or tower_df is None or tower_df.empty:





        return df





    if "excel_order_code_norm" not in df.columns:





        return df











    tower_cols = ["tower_order_code_norm", "Cancellation reason"]




    for optional_col in ["Cancelled at", "Order status", "Has Complaint?", "Complaint Reason", "Cancellation owner"]:




        if optional_col in tower_df.columns:




            tower_cols.append(optional_col)










    merged = df.merge(





        tower_df[tower_cols],





        left_on="excel_order_code_norm",





        right_on="tower_order_code_norm",





        how="left",





    )





    reason = merged.get("Cancellation reason", "").fillna("").astype(str).str.strip()





    merged["tower_cancellation_status"] = "Non Cancelled"





    merged.loc[reason.ne(""), "tower_cancellation_status"] = "Cancelled"





    return merged.drop(columns=["tower_order_code_norm"], errors="ignore")

















def _cancelled_only(df: pd.DataFrame) -> pd.DataFrame:




    if df is None or df.empty or "Cancellation reason" not in df.columns:




        return pd.DataFrame()




    reason = df["Cancellation reason"].fillna("").astype(str).str.strip()




    return df[reason.ne("")].copy()














def _select_cancel_view_cols(df: pd.DataFrame) -> pd.DataFrame:




    if df is None or df.empty:




        return df




    preferred = [




        "Order Code",




        "Outlet Name",




        "Vendor Code",




        "excel_order_date",




        "Order Date",




        "excel_order_amount",




        "Order Amount",




                            "excel_calculated_order_amount",

                            "calc_amount_diff",

                            "calc_amount_match",

                            "sale_id",
        "shop_name",




        "match_status",




        "tower_cancellation_status",




        "Cancellation reason",




        "Cancellation owner",




        "Cancelled at",




        "Order status",




        "Has Complaint?",




        "Complaint Reason",




    ]




    cols = [c for c in preferred if c in df.columns]




    return df[cols].copy() if cols else df














def _norm_reason(series: pd.Series) -> pd.Series:




    return series.fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})














def _to_dt(series: pd.Series) -> pd.Series:




    if series is None:




        return pd.to_datetime(pd.Series(dtype=object), errors="coerce")




    return pd.to_datetime(series, errors="coerce")














def _to_bool(series: pd.Series) -> pd.Series:




    if series is None:




        return pd.Series(dtype=bool)




    s = series.fillna("").astype(str).str.strip().str.lower()




    return s.isin(["y", "yes", "true", "1"])














_LOOSE_CODE_RE = re.compile(r"[^a-z0-9]+")




_CODE_TOKEN_RE = re.compile(r"[A-Za-z0-9]{6,}")














def _loose_norm_code(v: object) -> str:




    if v is None:




        return ""




    s = str(v).strip().lower()




    if s in {"none", "nan"}:




        return ""




    return _LOOSE_CODE_RE.sub("", s)














def _db_code_source(row: pd.Series) -> str:




    adj = str(row.get("adjustment_comments", "") or "").strip()




    add = str(row.get("Additional_Comments", "") or "").strip()




    ext = str(row.get("external_ref_id", "") or "").strip()




    if adj and adj.lower() not in {"none", "nan"}:




        return "adjustment_comments"




    if add and add.lower() not in {"none", "nan"}:




        return "Additional_Comments"




    if ext and ext.lower() not in {"none", "nan"}:




        return "external_ref_id"




    return "unknown"














def _find_excel_token_in_raw(raw: object, excel_codes: set[str], excel_loose_codes: set[str]) -> str:




    text = "" if raw is None else str(raw)




    if not text.strip():




        return ""




    for token in _CODE_TOKEN_RE.findall(text):




        token_norm = token.strip().lower()




        if token_norm in excel_codes:




            return token




        token_loose = _loose_norm_code(token_norm)




        if token_loose and token_loose in excel_loose_codes:




            return token




    return ""














def _fp_ctx():




    return get_responsive_context()














def _fp_columns(desktop: int, tablet: int | None = None, phone: int = 1, gap: str = "small"):




    return responsive_columns(_fp_ctx(), desktop=desktop, tablet=tablet, phone=phone, gap=gap)














def _fp_df(




    data,




    *,




    height: int | None = None,




    kind: str = "default",




    hide_index: bool = True,




    phone_columns: list[str] | None = None,




    tablet_columns: list[str] | None = None,




    desktop_columns: list[str] | None = None,




    column_config=None,




) -> None:




    df_to_show = data




    if isinstance(data, pd.DataFrame):




        cols = pick_columns_for_tier(




            _fp_ctx(),




            list(data.columns),




            desktop=desktop_columns,




            tablet=tablet_columns,




            phone=phone_columns,




        )




        df_to_show = data[cols].copy()




    kwargs = {




        "width": "stretch",




        "hide_index": hide_index,




        "height": clamp_dataframe_height(




            _fp_ctx(),




            desktop=height,




            tablet=max(220, int((height or 420) * 0.82)),




            phone=max(200, int((height or 420) * 0.68)),




            kind=kind,




        ),




    }




    if column_config is not None:




        kwargs["column_config"] = column_config




    st.dataframe(df_to_show, **kwargs)














def _fp_choose_nav(label: str, options: list[str], key: str) -> str:




    ctx = _fp_ctx()




    if ctx.is_phone:




        return st.selectbox(label, options=options, key=key)




    return st.radio(label, options, horizontal=True, label_visibility="collapsed", key=key)














def _render_foodpanda_reconciliation_tab(




    start_date: str,




    end_date: str,




    selected_branches: List[int],




    data_mode: str,




) -> None:




    st.subheader("Reconciliation")




    st.caption("Order Summary (Appendix A) reconciliation vs POS Food Panda sales. Uses DB for matching.")









    uploaded = st.file_uploader(




        "Upload Foodpanda Order Summary file",




        type=["xlsx", "xls"],




        key="foodpanda_recon_order_summary_upload",




    )




    if uploaded is None:




        st.info("Upload `005 - Order Summary.xlsx` to run reconciliation.")




        return









    try:




        xls = pd.ExcelFile(uploaded)




        sheet = st.selectbox(




            "Sheet",




            options=xls.sheet_names,




            index=xls.sheet_names.index("Appendix A") if "Appendix A" in xls.sheet_names else 0,




            key="foodpanda_recon_sheet",




        )




        df_excel = load_foodpanda_order_summary(uploaded, sheet_name=sheet)




    except Exception as e:




        st.error(f"Failed to read Excel: {e}")




        return









    if df_excel is None or df_excel.empty:




        st.warning("Order Summary sheet is empty or invalid.")




        return









    st.markdown("---")




    st.subheader("Calculated Order Amount (Appendix A)")




    st.caption(




        "Computed as: Discount Paid By Restaurant + foodpanda Commission + Waiting Time Fee + SST on foodpanda commission + "




        "Online Payment + Payable Amount + Wastage Refund Amount + Sales Tax Collection + Income Tax Withholding."




    )









    # Show only the requested component columns + the sum as "Food Panda receipt".




    requested = [




        "Discount Paid By Restaurant",




        "foodpanda Commission",




        "Waiting Time Fee",




        "SST on foodpanda commission",




        "Online Payment",




        "Payable Amount",




        "Wastage Refund Amount",




        "Sales Tax Collection",




        "Income Tax Withholding",




    ]




    calc_view = pd.DataFrame()




    calc_view["Order Code"] = df_excel.get("Order Code", df_excel.get("excel_order_code", "")).astype(str).str.strip()




    calc_view["Food GST"] = pd.to_numeric(df_excel.get("Food GST", 0.0), errors="coerce").fillna(0.0)




    for col in requested:




        excel_calc_col = f"excel_calc_{col}"




        if excel_calc_col in df_excel.columns:




            calc_view[col] = pd.to_numeric(df_excel[excel_calc_col], errors="coerce").fillna(0.0)




        elif col in df_excel.columns:




            calc_view[col] = pd.to_numeric(df_excel[col], errors="coerce").fillna(0.0)




        else:




            calc_view[col] = 0.0









    calc_view["Food Panda receipt"] = calc_view[requested].sum(axis=1)




    calc_view["Net Sales"] = calc_view["Food Panda receipt"] - calc_view["Food GST"]




    net_sales = pd.to_numeric(calc_view["Net Sales"], errors="coerce").fillna(0.0)




    food_gst = pd.to_numeric(calc_view["Food GST"], errors="coerce").fillna(0.0)




    calc_view["GST %"] = (food_gst / net_sales.replace({0.0: pd.NA})).astype("Float64") * 100.0




    calc_view["GST %"] = calc_view["GST %"].fillna(0.0).round(2)









    gst_col_config = None




    try:




        gst_col_config = {




            "GST %": st.column_config.NumberColumn("GST %", format="%.2f%%")




        }




    except Exception:




        gst_col_config = None









    _fp_df(




        calc_view,




        height=320,




        kind="compact",




        phone_columns=["Order Code", "Food Panda receipt", "Net Sales", "GST %"],




        tablet_columns=["Order Code", "Food GST", "Food Panda receipt", "Net Sales", "GST %"],




        column_config=gst_col_config,




    )









    tol = 1.0




    st.caption(f"Tolerance: +/- {tol:.0f} PKR")









    codes = df_excel["excel_order_code_norm"].dropna().astype(str).tolist()




    try:




        df_db = fetch_foodpanda_sales_by_codes(




            codes=codes,




            start_date=start_date,




            end_date=end_date,




            branch_ids=selected_branches,




            data_mode=data_mode,




            chunk_size=800,




        )




    except Exception as e:




        st.error(f"DB fetch failed: {e}")




        return









    if df_db is None or df_db.empty:




        st.warning("No DB rows fetched. Reconciliation cannot proceed.")




        return









    result = reconcile_foodpanda_orders(df_excel=df_excel, df_db=df_db, tolerance_pkr=tol)









    full = _drop_hidden_cols(result.full.copy())




    mismatches = _drop_hidden_cols(result.mismatches.copy())




    unmatched = _drop_hidden_cols(result.unmatched.copy())




    duplicates = _drop_hidden_cols(result.duplicates.copy())




    excel_duplicates = _drop_hidden_cols(result.excel_duplicates.copy())









    metrics = {r["metric"]: r["value"] for r in result.summary.to_dict("records")}




    metric_cols = _fp_columns(5, tablet=2, phone=1)




    metric_cols[0].metric("Total Rows", f"{int(metrics.get('total_rows', 0)):,}")




    metric_cols[1 % len(metric_cols)].metric("Matched OK", f"{int(metrics.get('matched_ok', 0)):,}")




    metric_cols[2 % len(metric_cols)].metric("Duplicates Resolved", f"{int(metrics.get('duplicate_resolved', 0)):,}")




    metric_cols[3 % len(metric_cols)].metric("Price Mismatch", f"{int(metrics.get('matched_price_mismatch', 0)):,}")




    metric_cols[4 % len(metric_cols)].metric("Unmatched", f"{int(metrics.get('unmatched', 0)):,}")









    st.markdown("---")




    st.subheader("Matched Only")




    matched_only = full[full["match_status"].isin(["matched_ok", "duplicate_resolved"])].copy()




    _fp_df(matched_only, height=320, kind="compact", phone_columns=["Order Code", "shop_name", "match_status", "excel_order_amount", "NT_amount"])









    st.subheader("Mismatches")




    _fp_df(mismatches, height=260, kind="compact", phone_columns=["Order Code", "shop_name", "match_status", "excel_order_amount", "NT_amount"])









    st.subheader("Unmatched")




    _fp_df(unmatched, height=260, kind="compact", phone_columns=["Order Code", "Outlet Name", "match_status", "excel_order_amount"])









    st.subheader("Excel Duplicates (Audit)")




    _fp_df(excel_duplicates, height=260, kind="compact", phone_columns=["Order Code", "Outlet Name", "excel_order_amount"])









    st.subheader("Duplicates (Audit)")




    _fp_df(duplicates, height=260, kind="compact", phone_columns=["Order Code", "shop_name", "NT_amount", "match_status"])









    st.subheader("Full Reconciliation")




    _fp_df(full, height=420, kind="default", phone_columns=["Order Code", "shop_name", "match_status", "excel_order_amount", "NT_amount", "difference"])









    st.markdown("---")




    st.subheader("Database Summary (date range)")




    st.caption("All POS sales in DB for `Cust_name = Food Panda` within the selected date range/branches (not limited to Excel codes).")




    try:




        df_db_range = fetch_foodpanda_sales_in_range(




            start_date=start_date,




            end_date=end_date,




            branch_ids=selected_branches,




            data_mode=data_mode,




        )




    except Exception as e:




        st.warning(f"Failed to load DB date-range summary: {e}")




        df_db_range = pd.DataFrame()









    if df_db_range is None or df_db_range.empty:



        st.info("No Food Panda rows found in DB for the selected date range/branches (or DB fetch failed).")



    else:



        excel_codes = set(



            df_excel.get("excel_order_code_norm", pd.Series(dtype=object))



            .dropna()



            .astype(str)



            .tolist()



        )



        excel_loose_codes = set(_loose_norm_code(c) for c in excel_codes if c)



        excel_dates = pd.to_datetime(df_excel.get("excel_order_date", pd.Series(dtype=object)), errors="coerce")



        excel_day_min = excel_dates.min().date() if excel_dates.notna().any() else None



        excel_day_max = excel_dates.max().date() if excel_dates.notna().any() else None







        db_codes = (



            df_db_range.get("db_order_code_norm", pd.Series(dtype=object)).fillna("").astype(str)



        )



        db_code_blank = int(db_codes.eq("").sum())



        db_in_excel = int(db_codes.isin(excel_codes).sum())



        db_not_in_excel = int((db_codes.ne("") & ~db_codes.isin(excel_codes)).sum())







        db_metric_cols = _fp_columns(5, tablet=2, phone=1)



        db_metric_cols[0].metric("DB Transactions", f"{len(df_db_range):,}")



        db_metric_cols[1 % len(db_metric_cols)].metric(



            "DB Sales",



            f"{float(pd.to_numeric(df_db_range.get('NT_amount'), errors='coerce').fillna(0.0).sum()):,.0f}",



        )



        db_metric_cols[2 % len(db_metric_cols)].metric("DB Codes in Excel", f"{db_in_excel:,}")



        db_metric_cols[3 % len(db_metric_cols)].metric("DB Codes not in Excel", f"{db_not_in_excel:,}")



        db_metric_cols[4 % len(db_metric_cols)].metric("DB Blank Codes", f"{db_code_blank:,}")







        excel_lookup = pd.DataFrame(

            {

                "excel_order_code_norm": df_excel.get("excel_order_code_norm", pd.Series(dtype=object)).fillna("").astype(str),

                "excel_order_amount": pd.to_numeric(df_excel.get("excel_order_amount", pd.Series(dtype=object)), errors="coerce"),

                "excel_calculated_order_amount": pd.to_numeric(
                    df_excel.get("excel_calculated_order_amount", pd.Series(dtype=object)), errors="coerce"
                ),

                "excel_day": excel_dates.dt.date,
            }

        )

        excel_lookup = excel_lookup[excel_lookup["excel_order_code_norm"].ne("")].copy()

        excel_lookup["excel_loose_code"] = excel_lookup["excel_order_code_norm"].map(_loose_norm_code)

        excel_loose_codes = set(excel_lookup["excel_loose_code"].dropna().astype(str).tolist())



        db_only_mask = db_codes.ne("") & ~db_codes.isin(excel_codes)

        db_only_enriched = pd.DataFrame()

        if int(db_only_mask.sum()):

            db_only = df_db_range.loc[db_only_mask].copy()

            db_only["NT_amount"] = pd.to_numeric(db_only.get("NT_amount"), errors="coerce").fillna(0.0)



            db_only["db_code_source"] = db_only.apply(_db_code_source, axis=1)

            db_only["db_code_loose"] = db_only.get("db_order_code_norm", "").map(_loose_norm_code)

            db_only["formatting_mismatch"] = db_only["db_code_loose"].isin(excel_loose_codes)



            db_only["excel_token_in_raw"] = db_only.get("db_order_code_raw", "").map(

                lambda v: _find_excel_token_in_raw(v, excel_codes=excel_codes, excel_loose_codes=excel_loose_codes)

            )

            db_only["embedded_in_comment"] = db_only["excel_token_in_raw"].fillna("").astype(str).str.strip().ne("")



            sale_dt = pd.to_datetime(db_only.get("sale_date", pd.NaT), errors="coerce")

            db_only["sale_day"] = sale_dt.dt.date

            if excel_day_min is not None and excel_day_max is not None:

                db_only["outside_excel_day_span"] = (db_only["sale_day"] < excel_day_min) | (db_only["sale_day"] > excel_day_max)

            else:

                db_only["outside_excel_day_span"] = False



            dup_counts = db_only.get("db_order_code_norm", pd.Series(dtype=object)).fillna("").astype(str).value_counts()

            db_only["duplicate_db_code"] = db_only.get("db_order_code_norm", "").fillna("").astype(str).map(

                lambda c: int(dup_counts.get(c, 0)) > 1

            )



            # Likely match by price/date (same day + amount ?1 PKR).

            db_only["possible_excel_code_amt"] = ""

            db_only["amount_diff_amt"] = pd.NA

            amount_tol = 1.0

            if not excel_lookup.empty and "sale_id" in db_only.columns and "sale_day" in db_only.columns:

                cand = (

                    db_only[["sale_id", "sale_day", "NT_amount"]]

                    .merge(

                        excel_lookup[["excel_order_code_norm", "excel_order_amount", "excel_day"]],

                        left_on="sale_day",

                        right_on="excel_day",

                        how="left",

                    )

                )

                cand["amount_diff"] = (cand["excel_order_amount"] - cand["NT_amount"]).abs()

                cand = cand[cand["amount_diff"].notna() & (cand["amount_diff"] <= amount_tol)].copy()

                if not cand.empty:

                    cand = cand.sort_values(["sale_id", "amount_diff"], ascending=[True, True])

                    best_amt = cand.groupby("sale_id", as_index=False).head(1)

                    best_amt = best_amt[["sale_id", "excel_order_code_norm", "amount_diff"]].copy()

                    best_amt = best_amt.rename(

                        columns={"excel_order_code_norm": "possible_excel_code_amt", "amount_diff": "amount_diff_amt"}

                    )

                    db_only = db_only.merge(best_amt, on="sale_id", how="left", suffixes=("", "_y"))

                    db_only["possible_excel_code_amt"] = db_only.get("possible_excel_code_amt", "").fillna("").astype(str)

                    db_only["amount_diff_amt"] = pd.to_numeric(db_only.get("amount_diff_amt"), errors="coerce")



            db_only["amount_date_match"] = db_only["possible_excel_code_amt"].fillna("").astype(str).str.strip().ne("")



            # Suggestions: embedded token -> formatting mismatch -> amount/date match.

            def _suggest_from_token(row: pd.Series):

                token = str(row.get("excel_token_in_raw", "") or "").strip()

                if not token:

                    return "", pd.NA

                token_norm = token.strip().lower()

                if token_norm in excel_codes:

                    sub = excel_lookup[excel_lookup["excel_order_code_norm"].eq(token_norm)]

                    if not sub.empty and pd.notna(sub["excel_order_amount"].iloc[0]):

                        diff = abs(float(sub["excel_order_amount"].iloc[0]) - float(row.get("NT_amount", 0.0)))

                        return token_norm, diff

                    return token_norm, pd.NA

                token_loose = _loose_norm_code(token_norm)

                if token_loose and token_loose in excel_loose_codes:

                    sub = excel_lookup[excel_lookup["excel_loose_code"].eq(token_loose)].copy()

                    if not sub.empty:

                        sub["_diff"] = (sub["excel_order_amount"] - float(row.get("NT_amount", 0.0))).abs()

                        sub = sub.sort_values("_diff", ascending=True)

                        code = str(sub["excel_order_code_norm"].iloc[0])

                        diff = float(sub["_diff"].iloc[0]) if pd.notna(sub["_diff"].iloc[0]) else pd.NA

                        return code, diff

                return "", pd.NA



            def _suggest_from_loose(row: pd.Series):

                loose = str(row.get("db_code_loose", "") or "").strip()

                if not loose:

                    return "", pd.NA

                sub = excel_lookup[excel_lookup["excel_loose_code"].eq(loose)].copy()

                if sub.empty:

                    return "", pd.NA

                sub["_diff"] = (sub["excel_order_amount"] - float(row.get("NT_amount", 0.0))).abs()

                sub = sub.sort_values("_diff", ascending=True)

                code = str(sub["excel_order_code_norm"].iloc[0])

                diff = float(sub["_diff"].iloc[0]) if pd.notna(sub["_diff"].iloc[0]) else pd.NA

                return code, diff



            token_suggestions = db_only.apply(_suggest_from_token, axis=1, result_type="expand")

            db_only["possible_excel_code_token"] = token_suggestions[0].fillna("").astype(str)

            db_only["amount_diff_token"] = pd.to_numeric(token_suggestions[1], errors="coerce")



            fmt_suggestions = db_only.apply(_suggest_from_loose, axis=1, result_type="expand")

            db_only["possible_excel_code_fmt"] = fmt_suggestions[0].fillna("").astype(str)

            db_only["amount_diff_fmt"] = pd.to_numeric(fmt_suggestions[1], errors="coerce")



            db_only["possible_excel_code"] = ""

            db_only["amount_diff"] = pd.NA



            token_mask = db_only["embedded_in_comment"] & db_only["possible_excel_code_token"].astype(str).str.strip().ne("")

            db_only.loc[token_mask, "possible_excel_code"] = db_only.loc[token_mask, "possible_excel_code_token"]

            db_only.loc[token_mask, "amount_diff"] = db_only.loc[token_mask, "amount_diff_token"]



            fmt_mask = (

                db_only["possible_excel_code"].astype(str).str.strip().eq("")

                & db_only["formatting_mismatch"]

                & db_only["possible_excel_code_fmt"].astype(str).str.strip().ne("")

            )

            db_only.loc[fmt_mask, "possible_excel_code"] = db_only.loc[fmt_mask, "possible_excel_code_fmt"]

            db_only.loc[fmt_mask, "amount_diff"] = db_only.loc[fmt_mask, "amount_diff_fmt"]



            amt_mask = db_only["possible_excel_code"].astype(str).str.strip().eq("") & db_only["amount_date_match"]

            db_only.loc[amt_mask, "possible_excel_code"] = db_only.loc[amt_mask, "possible_excel_code_amt"]

            db_only.loc[amt_mask, "amount_diff"] = db_only.loc[amt_mask, "amount_diff_amt"]



            # Compare DB net vs Excel "Calculated Order Amount" for the suggested Excel code.
            db_only["excel_calculated_order_amount"] = pd.NA
            db_only["calc_amount_diff"] = pd.NA
            db_only["calc_amount_match"] = False
            try:
                excel_by_code = (
                    excel_lookup.dropna(subset=["excel_order_code_norm"])
                    .drop_duplicates(subset=["excel_order_code_norm"], keep="first")
                    .set_index("excel_order_code_norm")
                )
                calc_map = excel_by_code["excel_calculated_order_amount"].to_dict()
                has_code = db_only["possible_excel_code"].fillna("").astype(str).str.strip().ne("")
                if has_code.any():
                    db_only.loc[has_code, "excel_calculated_order_amount"] = (
                        db_only.loc[has_code, "possible_excel_code"].astype(str).map(calc_map)
                    )
                    db_only["excel_calculated_order_amount"] = pd.to_numeric(
                        db_only["excel_calculated_order_amount"], errors="coerce"
                    )
                    db_only["calc_amount_diff"] = (db_only["excel_calculated_order_amount"] - db_only["NT_amount"]).abs()
                    calc_tol = 1.0
                    db_only["calc_amount_match"] = db_only["calc_amount_diff"].notna() & (db_only["calc_amount_diff"] <= calc_tol)
            except Exception:
                pass

            missing_reason = pd.Series("Missing in Excel / no match found", index=db_only.index, dtype="object")
            # Priority order: time difference -> embedded -> formatting -> amount/date -> duplicates -> default.

            missing_reason.loc[db_only["duplicate_db_code"]] = "Duplicate DB code"

            missing_reason.loc[db_only["amount_date_match"]] = "Likely match by price/date (code mismatch)"

            missing_reason.loc[db_only["formatting_mismatch"]] = "Formatting mismatch"

            missing_reason.loc[db_only["embedded_in_comment"]] = "Code embedded in comments"

            missing_reason.loc[db_only["outside_excel_day_span"]] = "Time difference"

            db_only["missing_reason"] = missing_reason



            db_only_enriched = db_only



        show_db_sample = st.checkbox("Show DB-only sample", value=False, key="foodpanda_db_only_sample")

        if show_db_sample:

            if db_only_enriched is None or db_only_enriched.empty:

                st.info("No DB codes found that are not present in the Excel Order Summary for this date range.")

            else:

                sample = db_only_enriched.copy()

                sample = sample.sort_values(["sale_date", "sale_id"], ascending=[False, False]).head(50)

                view_cols = [

                    c

                    for c in [

                        "sale_date",

                        "sale_day",

                        "shop_name",

                        "NT_amount",

                        "db_order_code_raw",

                        "db_order_code_norm",

                        "missing_reason",

                        "possible_excel_code",

                        "amount_diff",

                        "sale_id",

                    ]

                    if c in sample.columns

                ]

                out = sample[view_cols].copy() if view_cols else sample.copy()

                if "sale_date" in out.columns:

                    out["sale_date"] = pd.to_datetime(out["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

                if "NT_amount" in out.columns:

                    out["NT_amount"] = pd.to_numeric(out["NT_amount"], errors="coerce").fillna(0.0)

                if "amount_diff" in out.columns:

                    out["amount_diff"] = pd.to_numeric(out["amount_diff"], errors="coerce")

                if "excel_calculated_order_amount" in out.columns:
                    out["excel_calculated_order_amount"] = pd.to_numeric(out["excel_calculated_order_amount"], errors="coerce")

                if "calc_amount_diff" in out.columns:
                    out["calc_amount_diff"] = pd.to_numeric(out["calc_amount_diff"], errors="coerce")

                _fp_df(out, height=280, kind="compact")


        if db_only_enriched is not None and not db_only_enriched.empty:

            with st.expander("DB Codes not in Excel - Breakdown", expanded=False):

                st.caption(

                    "Heuristic breakdown of DB-only rows. This does not change reconciliation; it helps explain why a DB row "

                    "may not appear in the Excel Order Summary (time difference, code formatting, code embedded in comments, etc.)."

                )

                if excel_day_min is not None and excel_day_max is not None:

                    st.caption(f"Excel order-date span: {excel_day_min} -> {excel_day_max}")



                breakdown = (

                    db_only_enriched.groupby("missing_reason", as_index=False)

                    .size()

                    .rename(columns={"size": "count", "missing_reason": "category"})

                    .sort_values("count", ascending=False)

                )

                total = float(breakdown["count"].sum()) if not breakdown.empty else 0.0

                if total:

                    breakdown["share"] = (breakdown["count"] / total).round(4)

                _fp_df(breakdown, height=240, kind="compact", phone_columns=["category", "count", "share"])



                st.markdown("**By source field**")

                by_source = (

                    db_only_enriched.groupby(["missing_reason", "db_code_source"], as_index=False)

                    .size()

                    .rename(columns={"size": "count"})

                    .sort_values(["missing_reason", "count"], ascending=[True, False])

                )

                _fp_df(by_source, height=240, kind="compact", phone_columns=["missing_reason", "db_code_source", "count"])



                categories = breakdown["category"].tolist() if not breakdown.empty else []

                if categories:

                    selected_cat = st.selectbox(

                        "Show details for category",

                        options=categories,

                        index=0,

                        key="foodpanda_db_only_category",

                    )

                    details = db_only_enriched[db_only_enriched["missing_reason"] == selected_cat].copy()

                    details = details.sort_values(["sale_date", "sale_id"], ascending=[False, False])

                    detail_cols = [

                        "sale_date",

                        "sale_day",

                        "shop_name",

                        "NT_amount",

                        "db_order_code_raw",

                        "db_order_code_norm",

                        "missing_reason",

                        "possible_excel_code",

                        "amount_diff",

                            "excel_calculated_order_amount",

                            "calc_amount_diff",

                            "calc_amount_match",

                            "db_code_source",
                        "excel_token_in_raw",

                        "external_ref_type",

                        "external_ref_id",

                        "sale_id",

                    ]

                    cols = [c for c in detail_cols if c in details.columns]

                    out_details = details[cols].copy() if cols else details.copy()

                    if "sale_date" in out_details.columns:

                        out_details["sale_date"] = pd.to_datetime(out_details["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

                    if "NT_amount" in out_details.columns:

                        out_details["NT_amount"] = pd.to_numeric(out_details["NT_amount"], errors="coerce").fillna(0.0)

                    if "amount_diff" in out_details.columns:

                        out_details["amount_diff"] = pd.to_numeric(out_details["amount_diff"], errors="coerce")

                    if "excel_calculated_order_amount" in out_details.columns:
                        out_details["excel_calculated_order_amount"] = pd.to_numeric(
                            out_details["excel_calculated_order_amount"], errors="coerce"
                        )

                    if "calc_amount_diff" in out_details.columns:
                        out_details["calc_amount_diff"] = pd.to_numeric(out_details["calc_amount_diff"], errors="coerce")

                    _fp_df(out_details.head(500), height=420, kind="tall")


        with st.expander("Database Food Panda Transactions (date range)", expanded=False):



            st.caption("Full DB listing for the selected date range/branches. Use filters below to narrow down.")



            max_rows = st.number_input(



                "Max rows to display",



                min_value=100,



                max_value=50000,



                value=2000,



                step=100,



                key="foodpanda_db_rows_limit",



            )



            show_all_cols = st.checkbox("Show all columns", value=False, key="foodpanda_db_show_all_cols")



            search = st.text_input(



                "Search",



                value="",



                placeholder="order code / shop / sale_id",



                key="foodpanda_db_search",



            )







            db_view = df_db_range.copy()



            if search.strip():



                needle = search.strip()



                mask = (



                    db_view.get("db_order_code_raw", "").astype(str).str.contains(needle, case=False, na=False)



                    | db_view.get("db_order_code_norm", "").astype(str).str.contains(needle, case=False, na=False)



                    | db_view.get("shop_name", "").astype(str).str.contains(needle, case=False, na=False)



                    | db_view.get("sale_id", "").astype(str).str.contains(needle, case=False, na=False)



                )



                db_view = db_view[mask].copy()







            db_view = db_view.sort_values(["sale_date", "sale_id"], ascending=[False, False])



            if not show_all_cols:



                preferred = [



                    "sale_date",



                    "shop_name",



                    "NT_amount",



                    "db_order_code_raw",



                    "db_order_code_norm",



                    "external_ref_type",



                    "external_ref_id",



                    "sale_id",



                ]



                cols = [c for c in preferred if c in db_view.columns]



                db_show = db_view[cols].copy() if cols else db_view.copy()



            else:



                db_show = db_view.copy()







            if "sale_date" in db_show.columns:



                db_show["sale_date"] = pd.to_datetime(db_show["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")



            if "NT_amount" in db_show.columns:



                db_show["NT_amount"] = pd.to_numeric(db_show["NT_amount"], errors="coerce").fillna(0.0)







            _fp_df(db_show.head(int(max_rows)), height=420, kind="default")







            try:



                st.download_button(



                    label="Download DB Food Panda Excel",



                    data=export_to_excel(_drop_hidden_cols(db_view.copy()), "db_foodpanda"),



                    file_name=f"db_foodpanda_{start_date}_to_{end_date}.xlsx",



                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",



                    key="foodpanda_db_download_excel",



                )



            except Exception as e:



                st.warning(f"DB export failed: {e}")











    from modules.utils import export_tables_to_excel

    tables = {




        "order_amount_calculation": calc_view,




        "recon_full": full,




        "matched_only": matched_only,




        "mismatches": mismatches,




        "unmatched": unmatched,




        "excel_duplicates": excel_duplicates,




        "duplicates": duplicates,




        "summary": result.summary,




    }




    st.download_button(




        label="Download Reconciliation Excel",




        data=export_tables_to_excel(tables),




        file_name=f"foodpanda_recon_{start_date}_to_{end_date}.xlsx",




        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",




        key="foodpanda_recon_download",




    )
















def render_foodpanda_difference_report_tab(
    start_date: str,
    end_date: str,
    selected_branches: List[int],
    data_mode: str,
) -> None:
    st.subheader("Final Difference Report")
    st.caption(
        "Builds a 'Foodpanda Difference Report' combining DB Credit Sale (NT_amount), Appendix A receipt (Food Panda receipt), "
        "and cancellation reasons (optional)."
    )

    # Streamlit caching requires hashable inputs; normalize branch ids defensively.
    try:
        if selected_branches is None:
            branch_ids: tuple[int, ...] = ()
        elif hasattr(selected_branches, "tolist"):
            branch_ids = tuple(int(x) for x in list(selected_branches.tolist()) if str(x).strip() != "")
        elif isinstance(selected_branches, (list, tuple, set)):
            branch_ids = tuple(int(x) for x in list(selected_branches) if str(x).strip() != "")
        else:
            branch_ids = (int(selected_branches),) if str(selected_branches).strip() != "" else ()
    except Exception:
        branch_ids = tuple(selected_branches) if isinstance(selected_branches, (list, tuple)) else ()

    uploaded = st.file_uploader(
        "Upload Foodpanda Order Summary file (Appendix A)",
        type=["xlsx", "xls"],
        key="foodpanda_diff_order_summary_upload",
    )
    if uploaded is None:
        st.info("Upload `005 - Order Summary.xlsx` (and optionally the Order Details workbook) to generate the Final Difference Report.")
        return

    try:
        xls = pd.ExcelFile(uploaded)
        sheet = st.selectbox(
            "Order Summary sheet",
            options=xls.sheet_names,
            index=xls.sheet_names.index("Appendix A") if "Appendix A" in xls.sheet_names else 0,
            key="foodpanda_diff_sheet",
        )
        df_excel = load_foodpanda_order_summary(uploaded, sheet_name=sheet)
    except Exception as e:
        st.error(f"Failed to read Excel: {e}")
        return

    if df_excel is None or df_excel.empty:
        st.warning("Order Summary sheet is empty or invalid.")
        return

    tower_uploaded = st.file_uploader(
        "Upload Order Details workbook (required — cancellations & complaint reasons)",
        type=["xlsx", "xls"],
        key="foodpanda_diff_tower_upload",
        help="Required. Cancellation reasons and Complaint Reason from this file are linked into the Final Difference Report.",
    )
    if tower_uploaded is None:
        st.warning(
            "⚠️ The **Order Details workbook** is required to generate the Final Difference Report. "
            "Please upload it above (e.g. `Tower 23-29 Mar-26.xlsx` → sheet: *Order Details*)."
        )
        return
    tower_df = None
    try:
        tower_df = load_tower_order_details(tower_uploaded)
    except Exception as e:
        st.error(f"Order Details workbook read failed: {e}")
        return
    if tower_df is None or tower_df.empty:
        st.error("Order Details workbook loaded but contains no usable rows. Please check the file.")
        return

    # Fetch DB: date-range full + code-specific for reconciliation.
    try:
        df_db_range = fetch_foodpanda_sales_in_range(
            start_date=start_date,
            end_date=end_date,
            branch_ids=branch_ids,
            data_mode=data_mode,
        )
    except Exception as e:
        st.error(f"DB date-range fetch failed: {e}")
        return

    excel_codes = (
        df_excel.get("excel_order_code_norm", pd.Series(dtype=object))
        .dropna()
        .astype(str)
        .tolist()
    )
    try:
        df_db_codes = fetch_foodpanda_sales_by_codes(
            codes=excel_codes,
            start_date=start_date,
            end_date=end_date,
            branch_ids=list(branch_ids),
            data_mode=data_mode,
            chunk_size=800,
        )
    except Exception as e:
        st.error(f"DB code fetch failed: {e}")
        return

    tol = 1.0
    result = reconcile_foodpanda_orders(df_excel=df_excel, df_db=df_db_codes, tolerance_pkr=tol, keep_all_matches=True)
    recon = result.full.copy() if result and isinstance(result.full, pd.DataFrame) else pd.DataFrame()
    if recon.empty:
        st.warning("Reconciliation produced no rows.")
        return

    if tower_df is not None and not tower_df.empty:
        recon = _attach_tower_cancellation_reasons(recon, tower_df)

    def _norm_txt(v: object) -> str:
        return "" if v is None else str(v).strip()

    def _format_acc(v: object) -> str:
        if pd.isna(v) or v == "": return ""
        try:
            val = float(v)
            if abs(val) < 0.01: return "-"
            if val < 0: return f"({abs(val):.2f})"
            return f"{val:.2f}"
        except:
            return str(v)

    out_excel = pd.DataFrame()
    shop_name_s = recon.get("shop_name", pd.Series(dtype=object))
    outlet_name_s = recon.get("Outlet Name", pd.Series(dtype=object))
    vendor_code_s = recon.get("Vendor Code", pd.Series(dtype=object))
    
    out_excel["Branch"] = (
        shop_name_s.fillna("").astype(str).str.strip()
        .replace({"": pd.NA})
        .fillna(outlet_name_s.fillna("").astype(str).str.strip())
        .replace({"": pd.NA})
        .fillna(vendor_code_s.fillna("").astype(str).str.strip())
        .fillna("Unknown")
    )
    out_excel["Voucher No."] = ""
    out_excel["Receipt #"] = pd.to_numeric(recon.get("sale_id_sort", pd.Series(dtype=object)), errors="coerce")
    # Date: prefer DB sale_date for matched rows; fallback to Excel date for unmatched rows
    _db_date = pd.to_datetime(recon.get("db_sale_date", pd.Series(pd.NaT, index=recon.index)), errors="coerce")
    _excel_date = pd.to_datetime(
        recon.get("excel_order_date", recon.get("Order Date", pd.Series(pd.NaT, index=recon.index))),
        errors="coerce",
    )
    out_excel["Date"] = _db_date.fillna(_excel_date)
    # Time: extract from DB sale_date (has timestamp); Excel dates usually have no time
    out_excel["Time"] = _db_date.dt.strftime("%H:%M:%S").fillna("")
    out_excel["Order #"] = recon.get("excel_order_code", recon.get("Order Code", pd.Series("", index=recon.index))).map(_norm_txt)
    out_excel["Credit Sale"] = pd.to_numeric(recon.get("db_NT_amount"), errors="coerce")
    out_excel["Food Panda"] = pd.to_numeric(recon.get("excel_calculated_order_amount"), errors="coerce")
    out_excel["Ledger Adjustment"] = pd.NA

    credit_f = out_excel["Credit Sale"].fillna(0.0)
    receipt_f = out_excel["Food Panda"].fillna(0.0)
    # Total Difference (1st): Food Panda receipt - Credit Sale (DB)
    out_excel["_total_diff_1"] = receipt_f - credit_f

    cancel_reason = recon.get("Cancellation reason", pd.Series("", index=recon.index)).fillna("").astype(str).str.strip()
    order_status = recon.get("Order status", pd.Series("", index=recon.index)).fillna("").astype(str).str.strip()
    complaint_reason = recon.get("Complaint Reason", pd.Series("", index=recon.index)).fillna("").astype(str).str.strip()

    out_excel["Category"] = order_status
    out_excel.loc[out_excel["Category"].eq("") & cancel_reason.ne(""), "Category"] = "Cancelled"
    out_excel["Complaint Reason"] = complaint_reason

    match_status = recon.get("match_status", pd.Series("", index=recon.index)).fillna("").astype(str)
    desc = pd.Series("", index=out_excel.index, dtype="object")
    no_diff = out_excel["_total_diff_1"].abs().le(tol).fillna(False)
    desc.loc[no_diff] = "No Difference"
    desc.loc[match_status.eq("matched_price_mismatch") & (~no_diff)] = "Amount mismatch"
    desc.loc[match_status.eq("unmatched")] = "Not in DB"

    # Cancellation reason takes precedence in Description - 1
    has_cancel = cancel_reason.ne("")
    if has_cancel.any():
        desc.loc[has_cancel] = cancel_reason.loc[has_cancel]

    out_excel["Description - 1"] = desc.replace({pd.NA: ""}).fillna("")

    out_excel["Discount Paid By Restaurant"] = pd.to_numeric(
        recon.get("Discount Paid By Restaurant", pd.Series(0.0, index=recon.index)), errors="coerce"
    ).fillna(0.0)
    # Total Difference (2nd): Total Difference (1st) - Discount Paid By Restaurant
    out_excel["_total_diff_2"] = out_excel["_total_diff_1"].fillna(0.0) - out_excel["Discount Paid By Restaurant"]

    out_db_only = pd.DataFrame()
    if df_db_range is not None and not df_db_range.empty:
        excel_codes_set = set(df_excel.get("excel_order_code_norm", pd.Series(dtype=object)).dropna().astype(str).tolist())
        db_codes = df_db_range.get("db_order_code_norm", pd.Series(dtype=object)).fillna("").astype(str)
        db_only_mask = db_codes.ne("") & ~db_codes.isin(excel_codes_set)
        if int(db_only_mask.sum()):
            db_only = df_db_range.loc[db_only_mask].copy()
            db_only["NT_amount"] = pd.to_numeric(db_only.get("NT_amount"), errors="coerce").fillna(0.0)
            db_only["db_code_source"] = db_only.apply(_db_code_source, axis=1)
            db_only["db_code_loose"] = db_only.get("db_order_code_norm", "").map(_loose_norm_code)

            excel_dates = pd.to_datetime(df_excel.get("excel_order_date", pd.Series(dtype=object)), errors="coerce")
            excel_day_min = excel_dates.min().date() if excel_dates.notna().any() else None
            excel_day_max = excel_dates.max().date() if excel_dates.notna().any() else None

            excel_lookup = pd.DataFrame(
                {
                    "excel_order_code_norm": df_excel.get("excel_order_code_norm", pd.Series(dtype=object)).fillna("").astype(str),
                    "excel_order_amount": pd.to_numeric(df_excel.get("excel_order_amount", pd.Series(dtype=object)), errors="coerce"),
                    "excel_calculated_order_amount": pd.to_numeric(
                        df_excel.get("excel_calculated_order_amount", pd.Series(dtype=object)), errors="coerce"
                    ),
                    "excel_day": excel_dates.dt.date,
                }
            )
            excel_lookup = excel_lookup[excel_lookup["excel_order_code_norm"].ne("")].copy()
            excel_lookup["excel_loose_code"] = excel_lookup["excel_order_code_norm"].map(_loose_norm_code)
            excel_loose_codes = set(excel_lookup["excel_loose_code"].dropna().astype(str).tolist())

            db_only["formatting_mismatch"] = db_only["db_code_loose"].isin(excel_loose_codes)
            db_only["excel_token_in_raw"] = db_only.get("db_order_code_raw", pd.Series("", index=db_only.index)).map(
                lambda v: _find_excel_token_in_raw(v, excel_codes=excel_codes_set, excel_loose_codes=excel_loose_codes)
            )
            db_only["embedded_in_comment"] = db_only["excel_token_in_raw"].fillna("").astype(str).str.strip().ne("")

            sale_dt = pd.to_datetime(db_only.get("sale_date", pd.NaT), errors="coerce")
            db_only["sale_day"] = sale_dt.dt.date
            if excel_day_min is not None and excel_day_max is not None:
                db_only["outside_excel_day_span"] = (db_only["sale_day"] < excel_day_min) | (db_only["sale_day"] > excel_day_max)
            else:
                db_only["outside_excel_day_span"] = False

            db_only["possible_excel_code"] = ""
            db_only["amount_diff"] = pd.NA
            amount_tol = 1.0
            try:
                cand = (
                    db_only[["sale_id", "sale_day", "NT_amount"]]
                    .merge(
                        excel_lookup[["excel_order_code_norm", "excel_order_amount", "excel_day"]],
                        left_on="sale_day",
                        right_on="excel_day",
                        how="left",
                    )
                )
                cand["amount_diff"] = (cand["excel_order_amount"] - cand["NT_amount"]).abs()
                cand = cand[cand["amount_diff"].notna() & (cand["amount_diff"] <= amount_tol)].copy()
                if not cand.empty:
                    cand = cand.sort_values(["sale_id", "amount_diff"], ascending=[True, True])
                    best_amt = cand.groupby("sale_id", as_index=False).head(1)
                    best_amt = best_amt[["sale_id", "excel_order_code_norm", "amount_diff"]].rename(
                        columns={"excel_order_code_norm": "possible_excel_code", "amount_diff": "amount_diff"}
                    )
                    db_only = db_only.merge(best_amt, on="sale_id", how="left", suffixes=("", "_y"))
                    db_only["possible_excel_code"] = db_only.get("possible_excel_code", "").fillna("").astype(str)
                    db_only["amount_diff"] = pd.to_numeric(db_only.get("amount_diff"), errors="coerce")
            except Exception:
                pass

            amount_date_match = db_only["possible_excel_code"].fillna("").astype(str).str.strip().ne("")
            missing_reason = pd.Series("Missing in Excel / no match found", index=db_only.index, dtype="object")
            missing_reason.loc[amount_date_match] = "Likely match by price/date (code mismatch)"
            missing_reason.loc[db_only["formatting_mismatch"]] = "Formatting mismatch"
            missing_reason.loc[db_only["embedded_in_comment"]] = "Code embedded in comments"
            missing_reason.loc[db_only["outside_excel_day_span"]] = "Time difference"
            db_only["missing_reason"] = missing_reason

            desc2 = db_only["missing_reason"].fillna("").astype(str)
            has_suggest = db_only["possible_excel_code"].fillna("").astype(str).str.strip().ne("")
            if has_suggest.any():
                amt_txt = pd.to_numeric(db_only["amount_diff"], errors="coerce").round(2).astype("Float64").astype(str).replace({"<NA>": ""})
                desc2 = desc2.mask(
                    has_suggest,
                    desc2 + f" (possible=" + db_only["possible_excel_code"].fillna("").astype(str) + ", amt_diff=" + amt_txt + ")",
                )

            if tower_df is not None and not tower_df.empty:
                tmp = db_only.copy()
                tmp["excel_order_code_norm"] = tmp.get("db_order_code_norm", pd.Series("", index=tmp.index)).fillna("").astype(str)
                tmp = _attach_tower_cancellation_reasons(tmp, tower_df)
                
                cancel2 = tmp.get("Cancellation reason", pd.Series(dtype=object)).fillna("").astype(str).str.strip()
                status2 = tmp.get("Order status", pd.Series(dtype=object)).fillna("").astype(str).str.strip()
                
                has_cancel2 = cancel2.ne("")
                if has_cancel2.any():
                    desc2 = desc2.mask(has_cancel2, cancel2) # Use reason as description
                db_only["__cancel_reason"] = cancel2
                db_only["__order_status"] = status2
                complaint2 = tmp.get("Complaint Reason", pd.Series("", index=tmp.index)).fillna("").astype(str).str.strip()
                db_only["__complaint_reason"] = complaint2
            else:
                db_only["__cancel_reason"] = ""
                db_only["__order_status"] = ""
                db_only["__complaint_reason"] = ""

            out_db_only["Branch"] = db_only.get("shop_name", pd.Series("", index=db_only.index)).fillna("").astype(str)
            out_db_only["Voucher No."] = ""
            out_db_only["Receipt #"] = pd.to_numeric(db_only.get("sale_id"), errors="coerce")
            _db_only_dt = pd.to_datetime(db_only.get("sale_date"), errors="coerce")
            out_db_only["Date"] = _db_only_dt
            out_db_only["Time"] = _db_only_dt.dt.strftime("%H:%M:%S").fillna("")
            out_db_only["Order #"] = db_only.get("db_order_code_raw", pd.Series("", index=db_only.index)).fillna("").astype(str).str.strip()
            out_db_only.loc[out_db_only["Order #"].eq(""), "Order #"] = db_only.get("db_order_code_norm", pd.Series("", index=db_only.index)).fillna("").astype(str)
            out_db_only["Credit Sale"] = pd.to_numeric(db_only.get("NT_amount"), errors="coerce")
            out_db_only["Food Panda"] = 0.0
            out_db_only["Ledger Adjustment"] = pd.NA
            # Total Difference (1st): Food Panda (0) - Credit Sale (DB)
            out_db_only["_total_diff_1"] = out_db_only["Food Panda"] - out_db_only["Credit Sale"].fillna(0.0)
            out_db_only["Description - 1"] = desc2.fillna("")
            
            # Use order status for category, fallback to Cancelled
            out_db_only["Category"] = db_only["__order_status"]
            out_db_only.loc[out_db_only["Category"].eq("") & db_only["__cancel_reason"].fillna("").astype(str).str.strip().ne(""), "Category"] = "Cancelled"
            out_db_only["Complaint Reason"] = db_only["__complaint_reason"].fillna("").astype(str)
            
            out_db_only["Discount Paid By Restaurant"] = 0.0
            # Total Difference (2nd): Total Difference (1st) - Discount Paid By Restaurant
            out_db_only["_total_diff_2"] = out_db_only["_total_diff_1"].fillna(0.0) - out_db_only["Discount Paid By Restaurant"]

    out_all = pd.concat([out_excel, out_db_only], ignore_index=True)
    out_all["Total Difference"] = pd.to_numeric(out_all["_total_diff_1"], errors="coerce")
    out_all["Difference Without Discount"] = pd.to_numeric(out_all["_total_diff_2"], errors="coerce")

    # Safety guard: ensure Complaint Reason column exists in the combined frame
    if "Complaint Reason" not in out_all.columns:
        out_all["Complaint Reason"] = ""

    # ── Duplicate tagging ───────────────────────────────────────────────────
    _order_col = out_all["Order #"].fillna("").astype(str).str.strip().str.lower()
    _order_counts = _order_col.map(_order_col.value_counts()).fillna(1).astype(int)
    # Ignore blank/empty order codes when tagging
    _has_code = _order_col.ne("")
    out_all["Duplicate"] = ""
    out_all.loc[_has_code & (_order_counts > 1), "Duplicate"] = "Yes"
    out_all["Dup Count"] = 0
    out_all.loc[_has_code, "Dup Count"] = _order_counts.loc[_has_code]

    # Determine source of duplication (Excel side, DB side, or Both)
    # Excel duplicates: order codes that appear >1 time in the original Appendix A
    _excel_code_counts = (
        df_excel.get("excel_order_code_norm", pd.Series(dtype=object))
        .fillna("").astype(str).str.strip().str.lower()
        .value_counts()
    )
    _excel_dup_codes = set(_excel_code_counts[_excel_code_counts > 1].index)
    # DB duplicates: sale codes that appear >1 time in the DB range fetch
    _db_dup_codes = set()
    if df_db_range is not None and not df_db_range.empty:
        _db_code_counts = (
            df_db_range.get("db_order_code_norm", pd.Series(dtype=object))
            .fillna("").astype(str).str.strip().str.lower()
            .value_counts()
        )
        _db_dup_codes = set(_db_code_counts[_db_code_counts > 1].index)

    def _dup_source(code: str) -> str:
        if not code:
            return ""
        in_excel = code in _excel_dup_codes
        in_db = code in _db_dup_codes
        if in_excel and in_db:
            return "Both (Excel + DB)"
        if in_excel:
            return "Excel"
        if in_db:
            return "DB"
        return "Cross-match"  # duplicated only because Excel×DB merge produced multiple rows

    out_all["Dup Source"] = ""
    _dup_mask = out_all["Duplicate"].eq("Yes")
    if _dup_mask.any():
        out_all.loc[_dup_mask, "Dup Source"] = _order_col.loc[_dup_mask].map(_dup_source)

    final_cols_unique = [
        "Branch",
        "Voucher No.",
        "Receipt #",
        "Date",
        "Time",
        "Order #",
        "Credit Sale",
        "Food Panda",
        "Ledger Adjustment",
        "Total Difference",
        "Description - 1",
        "Category",
        "Complaint Reason",
        "Discount Paid By Restaurant",
        "Difference Without Discount",
        "Duplicate",
        "Dup Count",
        "Dup Source",
    ]
    final_unique = out_all[final_cols_unique].copy()
    
    # Format Date for display/export
    if "Date" in final_unique.columns:
        final_unique["Date"] = pd.to_datetime(final_unique["Date"], errors="coerce").dt.strftime("%d/%m/%Y")
    # Ensure Time column exists (empty for rows without DB time)
    if "Time" not in final_unique.columns:
        final_unique["Time"] = ""

    # Format numeric columns for accounting style
    for col in ["Credit Sale", "Food Panda", "Total Difference", "Discount Paid By Restaurant", "Difference Without Discount"]:
        if col in final_unique.columns:
            final_unique[col] = final_unique[col].apply(_format_acc)

    # Prepare for display with unique column names but identical labels
    display_df = final_unique.copy()
    # No rename needed — column is already "Difference Without Discount"
    
    st.markdown("### Final Difference Report Table")
    st.info(f"Report generated with {len(display_df)} total records.")
    
    # Use st.dataframe with custom formatting via the applied _format_acc
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # Download button is placed after all summary tables below

    # ── Summary Tables ──────────────────────────────────────────────────────
    st.markdown("---")

    # Build a clean numeric copy for summaries (out_all already has raw floats)
    _summary_src = out_all.copy()
    _summary_src["Credit Sale"] = pd.to_numeric(_summary_src.get("Credit Sale"), errors="coerce").fillna(0.0)
    _summary_src["Food Panda"] = pd.to_numeric(_summary_src.get("Food Panda"), errors="coerce").fillna(0.0)
    _summary_src["Total Difference"] = pd.to_numeric(_summary_src.get("Total Difference"), errors="coerce").fillna(0.0)
    _summary_src["Difference Without Discount"] = pd.to_numeric(_summary_src.get("Difference Without Discount"), errors="coerce").fillna(0.0)
    _summary_src["Discount Paid By Restaurant"] = pd.to_numeric(_summary_src.get("Discount Paid By Restaurant"), errors="coerce").fillna(0.0)
    _summary_src["_date_str"] = pd.to_datetime(_summary_src.get("Date"), errors="coerce").dt.strftime("%d/%m/%Y").fillna("No Date")

    # ── 1) Date-wise Summary ────────────────────────────────────────────────
    st.markdown("### Date-wise Summary")
    date_grp = (
        _summary_src
        .groupby("_date_str", as_index=False)
        .agg(
            Orders=("_date_str", "size"),
            Credit_Sale=("Credit Sale", "sum"),
            Food_Panda=("Food Panda", "sum"),
            Total_Difference=("Total Difference", "sum"),
            Discount_Paid=("Discount Paid By Restaurant", "sum"),
            Diff_Without_Discount=("Difference Without Discount", "sum"),
        )
        .rename(columns={
            "_date_str": "Date",
            "Credit_Sale": "Credit Sale",
            "Food_Panda": "Food Panda",
            "Total_Difference": "Total Difference",
            "Discount_Paid": "Discount Paid By Restaurant",
            "Diff_Without_Discount": "Difference Without Discount",
        })
    )
    # Sort by date properly
    date_grp["_sort"] = pd.to_datetime(date_grp["Date"], format="%d/%m/%Y", errors="coerce")
    date_grp = date_grp.sort_values("_sort").drop(columns=["_sort"])

    # Add totals row
    totals_date = pd.DataFrame([{
        "Date": "TOTAL",
        "Orders": date_grp["Orders"].sum(),
        "Credit Sale": date_grp["Credit Sale"].sum(),
        "Food Panda": date_grp["Food Panda"].sum(),
        "Total Difference": date_grp["Total Difference"].sum(),
        "Discount Paid By Restaurant": date_grp["Discount Paid By Restaurant"].sum(),
        "Difference Without Discount": date_grp["Difference Without Discount"].sum(),
    }])
    date_grp = pd.concat([date_grp, totals_date], ignore_index=True)

    # Format numeric columns
    for _c in ["Credit Sale", "Food Panda", "Total Difference", "Discount Paid By Restaurant", "Difference Without Discount"]:
        if _c in date_grp.columns:
            date_grp[_c] = date_grp[_c].apply(_format_acc)

    st.dataframe(date_grp, use_container_width=True, hide_index=True)

    # ── 2) Description-1-wise Summary ───────────────────────────────────────
    st.markdown("### Description-1-wise Summary")
    desc_col = _summary_src.get("Description - 1", pd.Series("", index=_summary_src.index)).fillna("").astype(str).str.strip()
    desc_col = desc_col.replace({"": "(No Description)"})
    _summary_src["_desc_grp"] = desc_col

    desc_grp = (
        _summary_src
        .groupby("_desc_grp", as_index=False)
        .agg(
            Orders=("_desc_grp", "size"),
            Credit_Sale=("Credit Sale", "sum"),
            Food_Panda=("Food Panda", "sum"),
            Total_Difference=("Total Difference", "sum"),
            Discount_Paid=("Discount Paid By Restaurant", "sum"),
            Diff_Without_Discount=("Difference Without Discount", "sum"),
        )
        .rename(columns={
            "_desc_grp": "Description - 1",
            "Credit_Sale": "Credit Sale",
            "Food_Panda": "Food Panda",
            "Total_Difference": "Total Difference",
            "Discount_Paid": "Discount Paid By Restaurant",
            "Diff_Without_Discount": "Difference Without Discount",
        })
    )
    desc_grp = desc_grp.sort_values("Orders", ascending=False)

    # Add totals row
    totals_desc = pd.DataFrame([{
        "Description - 1": "TOTAL",
        "Orders": desc_grp["Orders"].sum(),
        "Credit Sale": desc_grp["Credit Sale"].sum(),
        "Food Panda": desc_grp["Food Panda"].sum(),
        "Total Difference": desc_grp["Total Difference"].sum(),
        "Discount Paid By Restaurant": desc_grp["Discount Paid By Restaurant"].sum(),
        "Difference Without Discount": desc_grp["Difference Without Discount"].sum(),
    }])
    desc_grp = pd.concat([desc_grp, totals_desc], ignore_index=True)

    # Format numeric columns
    for _c in ["Credit Sale", "Food Panda", "Total Difference", "Discount Paid By Restaurant", "Difference Without Discount"]:
        if _c in desc_grp.columns:
            desc_grp[_c] = desc_grp[_c].apply(_format_acc)

    st.dataframe(desc_grp, use_container_width=True, hide_index=True)

    # ── Combined Excel Download (all tables in one file) ────────────────────
    st.markdown("---")
    try:
        from modules.utils import export_tables_to_excel

        all_tables = {
            "Differences": display_df,
            "Date-wise Summary": date_grp,
            "Description-1 Summary": desc_grp,
        }
        st.download_button(
            label="📥 Download All Tables (Excel)",
            data=export_tables_to_excel(all_tables),
            file_name=f"foodpanda_final_difference_report_{start_date}_to_{end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="foodpanda_diff_download_all",
        )
    except Exception as e:
        st.warning(f"Excel export failed: {e}")

def _render_foodpanda_cancellation_tab() -> None:




    st.subheader("Cancellation")




    st.caption("Cancelled vs non-cancelled analytics from Excel files only (Order Summary + Order Details workbook). No DB is used here.")









    sum_uploaded = st.file_uploader(




        "Upload Order Summary (optional)",




        type=["xlsx", "xls"],




        key="foodpanda_cancel_order_summary_upload",




    )




    df_sum = pd.DataFrame()




    if sum_uploaded is not None:




        try:




            xls = pd.ExcelFile(sum_uploaded)




            sheet = st.selectbox(




                "Order Summary sheet",




                options=xls.sheet_names,




                index=xls.sheet_names.index("Appendix A") if "Appendix A" in xls.sheet_names else 0,




                key="foodpanda_cancel_sum_sheet",




            )




            df_sum = load_foodpanda_order_summary(sum_uploaded, sheet_name=sheet)




        except Exception as e:




            st.warning(f"Order Summary read failed: {e}")









    tower_uploaded = st.file_uploader(




        "Upload Order Details workbook",




        type=["xlsx", "xls"],




        key="foodpanda_cancel_tower_upload",




    )




    tower_df = None




    tower_source_label = None




    if tower_uploaded is not None:




        try:




            tower_df = load_tower_order_details(tower_uploaded)




            tower_source_label = tower_uploaded.name




        except Exception as e:




            st.error(f"Workbook read failed: {e}")









    with st.expander("Workbook load status", expanded=False):




        if tower_df is not None and not tower_df.empty:




            st.write(f"Loaded: `{tower_source_label}`")




            st.write(f"Rows: {len(tower_df):,}")




        else:




            st.write("Not loaded.")




            st.write("Tip: Upload the Order Details workbook to run cancellation analytics.")









    if tower_df is None or tower_df.empty:




        st.info("Upload the Order Details workbook to see cancelled vs non-cancelled analytics.")




        return









    tower_reason = _norm_reason(tower_df.get("Cancellation reason", pd.Series(dtype=object)))




    tower_cancelled_mask = tower_reason.ne("")




    tower_cancelled = tower_df[tower_cancelled_mask].copy()




    tower_non_cancelled = tower_df[~tower_cancelled_mask].copy()









    st.markdown("**All Orders (Order Details workbook)**")




    tower_cols = _fp_columns(3, tablet=2, phone=1)




    tower_cols[0].metric("Orders", f"{len(tower_df):,}")




    tower_cols[1 % len(tower_cols)].metric("Cancelled", f"{len(tower_cancelled):,}")




    tower_cols[2 % len(tower_cols)].metric("Non Cancelled", f"{len(tower_non_cancelled):,}")









    tower_reason_counts = (




        tower_cancelled.assign(_reason=tower_reason[tower_cancelled_mask].values)




        .groupby("_reason", as_index=False)




        .size()




        .rename(columns={"_reason": "Cancellation reason", "size": "count"})




        .sort_values("count", ascending=False)




    )




    _fp_df(tower_reason_counts, height=260, kind="compact")









    tower_complaints = _norm_reason(tower_df.get("Complaint Reason", pd.Series(dtype=object)))




    tower_complaints_df = pd.DataFrame({"Complaint Reason": tower_complaints})




    tower_complaints_df = tower_complaints_df[tower_complaints_df["Complaint Reason"].ne("")].copy()




    if tower_complaints_df.empty:




        tower_complaint_counts = pd.DataFrame(columns=["Complaint Reason", "count"])




        st.info("No complaint reasons found in the Order Details sheet.")




    else:




        tower_complaint_counts = (




            tower_complaints_df.groupby("Complaint Reason", as_index=False)




            .size()




            .rename(columns={"size": "count"})




            .sort_values("count", ascending=False)




        )




        _fp_df(tower_complaint_counts, height=240, kind="compact")









    tower_in_summary = pd.DataFrame()




    if df_sum is not None and not df_sum.empty and "excel_order_code_norm" in df_sum.columns:




        sum_codes = set(df_sum["excel_order_code_norm"].dropna().astype(str).tolist())




        tower_in_summary = tower_df[tower_df["tower_order_code_norm"].astype(str).isin(sum_codes)].copy()









        st.markdown("**Subset (present in Order Summary)**")




        reason2 = _norm_reason(tower_in_summary.get("Cancellation reason", pd.Series(dtype=object)))




        s_mask = reason2.ne("")




        subset_cols = _fp_columns(3, tablet=2, phone=1)




        subset_cols[0].metric("Subset Orders", f"{len(tower_in_summary):,}")




        subset_cols[1 % len(subset_cols)].metric("Subset Cancelled", f"{int(s_mask.sum()):,}")




        subset_cols[2 % len(subset_cols)].metric("Subset Non Cancelled", f"{int((~s_mask).sum()):,}")









    with st.expander("Diagnostics", expanded=False):




        base = tower_df.copy()




        base["tower_cancelled"] = tower_cancelled_mask




        base["has_complaint"] = _to_bool(base.get("Has Complaint?", pd.Series(dtype=object)))









        group_cols = [c for c in ["Restaurant name", "Store ID"] if c in base.columns]




        if group_cols:




            by_store = (




                base.groupby(group_cols, as_index=False)




                .agg(




                    orders=("tower_order_code", "count"),




                    cancelled=("tower_cancelled", "sum"),




                    complaints=("has_complaint", "sum"),




                )




            )




            by_store["cancel_rate"] = (by_store["cancelled"] / by_store["orders"]).round(4)




            by_store["complaint_rate"] = (by_store["complaints"] / by_store["orders"]).round(4)




            by_store = by_store.sort_values(["cancel_rate", "orders"], ascending=[False, False])









            min_orders = st.slider(




                "Min orders (for rate tables)",




                min_value=1,




                max_value=int(max(1, by_store["orders"].max())),




                value=min(20, int(max(1, by_store["orders"].max()))),




                step=1,




                key="tower_diag_min_orders_cancel",




            )




            st.markdown("**Highest cancellation rate (filtered)**")




            _fp_df(by_store[by_store["orders"].ge(min_orders)].head(30), height=260, kind="compact")




        else:




            by_store = pd.DataFrame()




            st.info("Restaurant/store columns not found in the Order Details sheet; skipping store-level diagnostics.")









        if "Order received at" in base.columns:




            received = _to_dt(base["Order received at"])




            base["_recv_date"] = received.dt.date




            base["_recv_hour"] = received.dt.hour









            by_day = (




                base.dropna(subset=["_recv_date"])




                .groupby("_recv_date", as_index=False)




                .agg(orders=("tower_order_code", "count"), cancelled=("tower_cancelled", "sum"))




                .sort_values("_recv_date")




            )




            if not by_day.empty:




                by_day["cancel_rate"] = (by_day["cancelled"] / by_day["orders"]).round(4)




                st.markdown("**Day-wise cancellation trend**")




                _fp_df(by_day, height=260, kind="compact")




        else:




            by_day = pd.DataFrame()









        channel_cols = [c for c in ["Delivery Type", "Payment type", "Payment method", "Cancellation owner"] if c in base.columns]




        for c in channel_cols:




            tmp = base.copy()




            tmp[c] = _norm_reason(tmp[c])




            tmp = tmp[tmp[c].ne("")].copy()




            if tmp.empty:




                continue




            agg = (




                tmp.groupby(c, as_index=False)




                .agg(orders=("tower_order_code", "count"), cancelled=("tower_cancelled", "sum"))




                .sort_values(["cancelled", "orders"], ascending=[False, False])




            )




            agg["cancel_rate"] = (agg["cancelled"] / agg["orders"]).round(4)




            st.markdown(f"**By {c}**")




            _fp_df(agg.head(40), height=240, kind="compact")









    with st.expander("Cancelled order details", expanded=False):




        if tower_cancelled.empty:




            st.info("No cancelled orders in the Order Details sheet.")




        else:




            reasons_all = sorted([r for r in tower_reason[tower_cancelled_mask].unique().tolist() if r])




            selected_tower_reason = st.selectbox(




                "Cancellation reason",




                options=["<all>"] + reasons_all,




                index=0,




                key="tower_cancel_reason_filter_cancel",




            )




            tower_cancelled_details = tower_cancelled.copy()




            if selected_tower_reason != "<all>":




                tower_cancelled_details = tower_cancelled_details[




                    _norm_reason(tower_cancelled_details["Cancellation reason"]).eq(selected_tower_reason)




                ].copy()




            _fp_df(_select_cancel_view_cols(tower_cancelled_details), height=380, kind="default")









    joined = pd.DataFrame()




    if df_sum is not None and not df_sum.empty:




        joined = _attach_tower_cancellation_reasons(df_sum.copy(), tower_df)




        st.markdown("**Order Summary joined with Order Details (Excel-only)**")




        _fp_df(_select_cancel_view_cols(joined), height=320, kind="compact")









    from modules.utils import export_tables_to_excel




    cancel_tables = {




        "tower_reason_counts": tower_reason_counts,




        "tower_complaint_counts": tower_complaint_counts,




        "tower_store_diagnostics": by_store,




        "tower_by_day": by_day,




        "tower_in_order_summary": tower_in_summary,




        "order_summary_joined_tower": joined,




    }




    st.download_button(




        label="Download Cancellation Report Excel",




        data=export_tables_to_excel(cancel_tables),




        file_name=f"foodpanda_cancellation.xlsx",




        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",




        key="foodpanda_cancel_download",




    )















@st.cache_data(ttl=DatabaseConfig.CACHE_TTL)
def _cached_food_panda_sales(
    start_date: str,
    end_date: str,
    branch_ids_key: tuple[int, ...],
    data_mode: str,
) -> pd.DataFrame:
    branch_ids = list(branch_ids_key)
    conn = pool.get_connection("candelahns")
    filter_clause, filter_params = build_filter_clause(data_mode)











    query = f"""





    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;





    SELECT





        s.sale_id,





        s.sale_date,





        s.shop_id,





        sh.shop_name,





        COALESCE(e.shop_employee_id, 0) AS employee_id,





        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,





        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,





        s.Cust_name AS order_type,





        s.Nt_amount AS net_amount,





        s.adjustment_comments,





        s.Additional_Comments,





        s.external_ref_type,





        s.external_ref_id





    FROM tblSales s WITH (NOLOCK)




    LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id




    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id




    WHERE s.sale_date >= ?

      AND s.sale_date < DATEADD(DAY, 1, ?)

      AND s.shop_id IN ({placeholders(len(branch_ids))})

      AND s.Cust_name = 'Food Panda'

      {filter_clause}

    ORDER BY s.sale_date DESC, s.sale_id DESC




    """




    params: List = [start_date, end_date] + list(branch_ids) + list(filter_params)





    df = pd.read_sql(query, conn, params=params)





    if not df.empty:





        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")





        df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0.0)





        # "Order ID" for users = POS sale_id (stable identifier in tblSales).





        df["order_id"] = pd.to_numeric(df["sale_id"], errors="coerce").fillna(0).astype(int)





        # Foodpanda order code lives in adjustment_comments in this POS DB.





        # Fall back to Additional_Comments then external_ref_id.





        adj = df.get("adjustment_comments", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})





        add = df.get("Additional_Comments", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})





        ext = df.get("external_ref_id", "").fillna("").astype(str).str.strip().replace({"None": "", "nan": ""})





        df["order_code"] = adj.mask(adj.eq(""), add).mask(adj.eq("") & add.eq(""), ext)





        df["employee_id"] = pd.to_numeric(df["employee_id"], errors="coerce").fillna(0).astype(int)





        df["employee_code"] = df.get("employee_code", "").fillna("").astype(str)





        df["employee_name"] = df.get("employee_name", "").fillna("").astype(str)





        df["shop_name"] = df.get("shop_name", "").fillna("").astype(str)





    return df

















class FoodPandaTab:





    def __init__(





        self,





        start_date: str,





        end_date: str,





        selected_branches: List[int],





        data_mode: str,





    ) -> None:





        self.start_date = start_date





        self.end_date = end_date





        # Normalize for Streamlit caching (avoid passing pandas Series/Index into cached DB calls).
        try:
            if selected_branches is None:
                self.selected_branches = []
            elif hasattr(selected_branches, "tolist"):
                self.selected_branches = [int(x) for x in list(selected_branches.tolist())]
            else:
                self.selected_branches = [int(x) for x in list(selected_branches)]
        except Exception:
            self.selected_branches = selected_branches if isinstance(selected_branches, list) else []





        self.data_mode = data_mode











    def render(self) -> None:
        st.header("Food Panda")
        st.caption("Food Panda transactions based on `tblSales.Cust_name = 'Food Panda'`.")

        # 1. Navigation / Sub-tabs moved to top for visibility
        subtab = _fp_choose_nav(
            "Foodpanda Subtab",
            ["Reconciliation", "Cancellation", "Analytics"],
            key="foodpanda_subtab",
        )

        if subtab == "Reconciliation":
            _render_foodpanda_reconciliation_tab(
                start_date=self.start_date,
                end_date=self.end_date,
                selected_branches=self.selected_branches,
                data_mode=self.data_mode,
            )
            return
        elif subtab == "Cancellation":
            _render_foodpanda_cancellation_tab()
            return

        # Analytics (Original view)
        df = _cached_food_panda_sales(self.start_date, self.end_date, tuple(self.selected_branches), self.data_mode)










        total_sales = float(df["net_amount"].sum()) if not df.empty else 0.0





        total_tx = int(len(df)) if not df.empty else 0





        aov = (total_sales / total_tx) if total_tx else 0.0











        metric_cols = _fp_columns(3, tablet=2, phone=1)




        metric_cols[0].metric("Total Sales", format_currency(total_sales))




        metric_cols[1 % len(metric_cols)].metric("Transactions", f"{total_tx:,}")




        metric_cols[2 % len(metric_cols)].metric("Avg Order Value", format_currency(aov))










        st.markdown("---")





        if df.empty:





            st.info("No Food Panda transactions found for the selected filters.")





            return











        # Summaries





        summary_cols = _fp_columns(2, tablet=2, phone=1)




        with summary_cols[0]:




            st.subheader("By Branch")




            by_branch = (




                df.groupby(["shop_id", "shop_name"], as_index=False)




                .agg(transactions=("sale_id", "count"), sales=("net_amount", "sum"))




                .sort_values("sales", ascending=False)




            )




            by_branch["sales"] = by_branch["sales"].apply(format_currency)




            _fp_df(by_branch, height=280, kind="compact", phone_columns=["shop_name", "transactions", "sales"])









        with summary_cols[1 % len(summary_cols)]:




            st.subheader("Top Employees")




            by_emp = (




                df.groupby(["employee_id", "employee_code", "employee_name"], as_index=False)




                .agg(transactions=("sale_id", "count"), sales=("net_amount", "sum"))




                .sort_values("sales", ascending=False)




            )




            by_emp["sales"] = by_emp["sales"].apply(format_currency)




            _fp_df(by_emp.head(50), height=280, kind="compact", phone_columns=["employee_name", "transactions", "sales"])










        st.markdown("---")





        st.subheader("All Food Panda Transactions")











        search = st.text_input("Search (employee / branch / comments / ref)", value="", key="food_panda_search")





        show_all_cols = st.checkbox("Show all columns", value=False, key="food_panda_show_all_cols")











        out = _drop_hidden_cols(df.copy())





        if search.strip():





            needle = search.strip()





            mask = (





                out["employee_name"].astype(str).str.contains(needle, case=False, na=False)





                | out["shop_name"].astype(str).str.contains(needle, case=False, na=False)





                | out.get("Additional_Comments", "").astype(str).str.contains(needle, case=False, na=False)





                | out.get("order_code", "").astype(str).str.contains(needle, case=False, na=False)





            )





            out = out[mask].copy()











        default_cols = [





            "order_id",





            "order_code",





            "sale_date",





            "shop_name",





            "employee_name",





            "net_amount",





            "adjustment_comments",





            "Additional_Comments",





            "sale_id",





        ]





        if show_all_cols:





            cols = [c for c in out.columns if c not in HIDE_EXTERNAL_REF_COLS]





        else:





            cols = [c for c in default_cols if c in out.columns]











        out_show = out[cols].copy()





        if "sale_date" in out_show.columns:





            out_show["sale_date"] = pd.to_datetime(out_show["sale_date"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")





        if "net_amount" in out_show.columns:





            out_show["net_amount"] = pd.to_numeric(out_show["net_amount"], errors="coerce").fillna(0.0)











        _fp_df(




            out_show,




            height=520,




            kind="tall",




            phone_columns=["order_id", "order_code", "sale_date", "shop_name", "net_amount"],




            tablet_columns=["order_id", "order_code", "sale_date", "shop_name", "employee_name", "net_amount"],




        )










        df_export = _drop_hidden_cols(df.copy())
        st.download_button(
            label="Download Food Panda Excel",
            data=export_to_excel(df_export, "Food Panda"),
            file_name=f"food_panda_{self.start_date}_to_{self.end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return

        uploaded = st.file_uploader(
            "Upload Foodpanda Order Summary file",
            type=["xlsx", "xls"],
            key="foodpanda_order_summary_upload",
        )





        if uploaded is None:





            st.info("Upload `005 - Order Summary.xlsx` to run reconciliation.")





            return











        try:





            xls = pd.ExcelFile(uploaded)





            sheet = st.selectbox(





                "Sheet",





                options=xls.sheet_names,





                index=xls.sheet_names.index("Appendix A") if "Appendix A" in xls.sheet_names else 0,





                key="foodpanda_recon_sheet",





            )





            df_excel = load_foodpanda_order_summary(uploaded, sheet_name=sheet)





        except Exception as e:





            st.error(f"Failed to read Excel: {e}")





            return











        tol = 1.0




        st.caption(f"Tolerance: +/- {tol:.0f} PKR")









        tower_uploaded = st.file_uploader(




            "Upload Order Details workbook (optional)",




            type=["xlsx", "xls"],




            key="foodpanda_tower_upload",




            help="Matches `Order Details -> Order ID` with Appendix A `Order Code`.",




        )










        tower_df = None





        tower_source_label = None





        if tower_uploaded is not None:




            try:




                tower_df = load_tower_order_details(tower_uploaded)




                tower_source_label = tower_uploaded.name




            except Exception as e:




                st.warning(f"Workbook read failed: {e}")









        with st.expander("Workbook cancellation status", expanded=False):




            if tower_df is not None and not tower_df.empty:




                st.write(f"Loaded: `{tower_source_label}`")




                st.write(f"Rows: {len(tower_df):,}")




            else:




                st.write("Not loaded.")




                st.write("Tip: Upload the Order Details workbook to enable cancelled-order tables.")









        if tower_source_label:




            st.caption(f"Cancellation reasons source: `{tower_source_label}`")










        codes = df_excel["excel_order_code_norm"].dropna().astype(str).tolist()





        try:





            df_db = fetch_foodpanda_sales_by_codes(





                codes=codes,





                start_date=self.start_date,





                end_date=self.end_date,





                branch_ids=self.selected_branches,





                data_mode=self.data_mode,





                chunk_size=800,





            )





        except Exception as e:





            st.error(f"DB fetch failed: {e}")





            return











        result = reconcile_foodpanda_orders(df_excel=df_excel, df_db=df_db, tolerance_pkr=tol)











        full_with_cancellation = _attach_tower_cancellation_reasons(result.full.copy(), tower_df)





        mismatches_with_cancellation = _attach_tower_cancellation_reasons(result.mismatches.copy(), tower_df)











        # Keep core reconciliation views unchanged.





        full = _drop_hidden_cols(result.full.copy())





        mismatches = _drop_hidden_cols(result.mismatches.copy())





        unmatched = _drop_hidden_cols(result.unmatched.copy())





        duplicates = _drop_hidden_cols(result.duplicates.copy())





        excel_duplicates = _drop_hidden_cols(result.excel_duplicates.copy())











        # Summary metrics





        metrics = {r["metric"]: r["value"] for r in result.summary.to_dict("records")}





        c1, c2, c3, c4, c5 = st.columns(5)





        c1.metric("Total Rows", f"{int(metrics.get('total_rows', 0)):,}")





        c2.metric("Matched OK", f"{int(metrics.get('matched_ok', 0)):,}")





        c3.metric("Duplicates Resolved", f"{int(metrics.get('duplicate_resolved', 0)):,}")





        c4.metric("Price Mismatch", f"{int(metrics.get('matched_price_mismatch', 0)):,}")





        c5.metric("Unmatched", f"{int(metrics.get('unmatched', 0)):,}")











        st.markdown("---")





        st.subheader("Matched Only")





        matched_only = full[full["match_status"].isin(["matched_ok", "duplicate_resolved"])].copy()





        st.dataframe(matched_only, width="stretch", hide_index=True, height=320)











        st.subheader("Mismatches")





        st.dataframe(mismatches, width="stretch", hide_index=True, height=260)











        st.subheader("Unmatched")





        st.dataframe(unmatched, width="stretch", hide_index=True, height=260)











        st.subheader("Excel Duplicates (Audit)")





        st.dataframe(excel_duplicates, width="stretch", hide_index=True, height=260)











        st.subheader("Duplicates (Audit)")




        st.dataframe(duplicates, width="stretch", hide_index=True, height=260)









        st.markdown("---")




        st.subheader("Cancellation (Order Details)")




        st.caption("Cancellation and complaint analysis from the Order Details sheet. This section is separate from reconciliation.")









        # Separate cancellation report tables (do not mix with reconciliation export).




        cancelled_matched = pd.DataFrame()




        cancelled_duplicate_resolved = pd.DataFrame()




        cancelled_price_mismatch = pd.DataFrame()









        if tower_df is None or tower_df.empty:




            st.info("Upload the Order Details workbook to see cancellation/complaint analysis here.")




        else:




            st.markdown("**All Orders (Order Details workbook)**")




            tower_reason = _norm_reason(tower_df.get("Cancellation reason", pd.Series(dtype=object)))




            tower_cancelled_mask = tower_reason.ne("")




            tower_cancelled = tower_df[tower_cancelled_mask].copy()




            tower_non_cancelled = tower_df[~tower_cancelled_mask].copy()









            t1, t2, t3 = st.columns(3)




            t1.metric("Orders", f"{len(tower_df):,}")




            t2.metric("Cancelled", f"{len(tower_cancelled):,}")




            t3.metric("Non Cancelled", f"{len(tower_non_cancelled):,}")









            tower_reason_counts = (




                tower_cancelled.assign(_reason=tower_reason[tower_cancelled_mask].values)




                .groupby("_reason", as_index=False)




                .size()




                .rename(columns={"_reason": "Cancellation reason", "size": "count"})




                .sort_values("count", ascending=False)




            )




            if tower_reason_counts.empty:




                st.info("No cancellation reasons found in the Order Details sheet.")




            else:




                st.dataframe(tower_reason_counts, width="stretch", hide_index=True, height=260)









            tower_complaints = _norm_reason(tower_df.get("Complaint Reason", pd.Series(dtype=object)))




            tower_complaints_df = pd.DataFrame({"Complaint Reason": tower_complaints})




            tower_complaints_df = tower_complaints_df[tower_complaints_df["Complaint Reason"].ne("")].copy()




            if tower_complaints_df.empty:




                st.info("No complaint reasons found in the Order Details sheet.")




                tower_complaint_counts = pd.DataFrame(columns=["Complaint Reason", "count"])




            else:




                tower_complaint_counts = (




                    tower_complaints_df.groupby("Complaint Reason", as_index=False)




                    .size()




                    .rename(columns={"size": "count"})




                    .sort_values("count", ascending=False)




                )




                st.dataframe(tower_complaint_counts, width="stretch", hide_index=True, height=240)









            with st.expander("Diagnostics", expanded=False):




                # Cancellation/complaint rates by restaurant/store where possible.




                base = tower_df.copy()




                base["tower_cancelled"] = tower_cancelled_mask




                base["has_complaint"] = _to_bool(base.get("Has Complaint?", pd.Series(dtype=object)))









                group_cols = []




                if "Restaurant name" in base.columns:




                    group_cols.append("Restaurant name")




                if "Store ID" in base.columns:




                    group_cols.append("Store ID")









                if group_cols:




                    by_store = (




                        base.groupby(group_cols, as_index=False)




                        .agg(




                            orders=("tower_order_code", "count"),




                            cancelled=("tower_cancelled", "sum"),




                            complaints=("has_complaint", "sum"),




                        )




                    )




                    by_store["cancel_rate"] = (by_store["cancelled"] / by_store["orders"]).round(4)




                    by_store["complaint_rate"] = (by_store["complaints"] / by_store["orders"]).round(4)




                    by_store = by_store.sort_values(["cancel_rate", "orders"], ascending=[False, False])









                    min_orders = st.slider(




                        "Min orders (for rate tables)",




                        min_value=1,




                        max_value=int(max(1, by_store["orders"].max())),




                        value=min(20, int(max(1, by_store["orders"].max()))),




                        step=1,




                        key="tower_diag_min_orders",




                    )




                    st.markdown("**Highest cancellation rate (filtered)**")




                    st.dataframe(by_store[by_store["orders"].ge(min_orders)].head(30), width="stretch", hide_index=True, height=260)









                    st.markdown("**Highest cancelled count**")




                    st.dataframe(by_store.sort_values(["cancelled", "orders"], ascending=[False, False]).head(30), width="stretch", hide_index=True, height=260)




                else:




                    by_store = pd.DataFrame()




                    st.info("Restaurant/store columns not found in the Order Details sheet; skipping store-level diagnostics.")









                # Time diagnostics (if timestamps exist).




                if "Order received at" in base.columns:




                    received = _to_dt(base["Order received at"])




                    base["_recv_date"] = received.dt.date




                    base["_recv_hour"] = received.dt.hour









                    by_day = (




                        base.dropna(subset=["_recv_date"])




                        .groupby("_recv_date", as_index=False)




                        .agg(orders=("tower_order_code", "count"), cancelled=("tower_cancelled", "sum"))




                        .sort_values("_recv_date")




                    )




                    if not by_day.empty:




                        by_day["cancel_rate"] = (by_day["cancelled"] / by_day["orders"]).round(4)




                        st.markdown("**Day-wise cancellation trend**")




                        st.dataframe(by_day, width="stretch", hide_index=True, height=260)




                    else:




                        st.info("Could not compute day-wise trend (no parsable 'Order received at').")









                    by_hour = (




                        base.dropna(subset=["_recv_hour"])




                        .groupby("_recv_hour", as_index=False)




                        .agg(orders=("tower_order_code", "count"), cancelled=("tower_cancelled", "sum"))




                        .sort_values("_recv_hour")




                    )




                    if not by_hour.empty:




                        by_hour["cancel_rate"] = (by_hour["cancelled"] / by_hour["orders"]).round(4)




                        st.markdown("**Hour-wise cancellation trend**")




                        st.dataframe(by_hour, width="stretch", hide_index=True, height=240)




                else:




                    by_day = pd.DataFrame()




                    by_hour = pd.DataFrame()




                    st.info("Timestamp column `Order received at` not found; skipping time diagnostics.")









                # Channel diagnostics (payment/delivery).




                channel_cols = [c for c in ["Delivery Type", "Payment type", "Payment method", "Cancellation owner"] if c in base.columns]




                if channel_cols:




                    for c in channel_cols:




                        tmp = base.copy()




                        tmp[c] = _norm_reason(tmp[c])




                        tmp = tmp[tmp[c].ne("")].copy()




                        if tmp.empty:




                            continue




                        agg = (




                            tmp.groupby(c, as_index=False)




                            .agg(orders=("tower_order_code", "count"), cancelled=("tower_cancelled", "sum"))




                            .sort_values(["cancelled", "orders"], ascending=[False, False])




                        )




                        agg["cancel_rate"] = (agg["cancelled"] / agg["orders"]).round(4)




                        st.markdown(f"**By {c}**")




                        st.dataframe(agg.head(40), width="stretch", hide_index=True, height=240)









            with st.expander("Cancelled order details", expanded=False):




                if tower_cancelled.empty:




                    st.info("No cancelled orders in the Order Details sheet.")




                else:




                    reasons_all = sorted([r for r in tower_reason[tower_cancelled_mask].unique().tolist() if r])




                    selected_tower_reason = st.selectbox(




                        "Cancellation reason",




                        options=["<all>"] + reasons_all,




                        index=0,




                        key="tower_cancel_reason_filter",




                    )




                    tower_cancelled_details = tower_cancelled.copy()




                    if selected_tower_reason != "<all>":




                        tower_cancelled_details = tower_cancelled_details[




                            _norm_reason(tower_cancelled_details["Cancellation reason"]).eq(selected_tower_reason)




                        ].copy()




                    st.dataframe(




                        _drop_hidden_cols(_select_cancel_view_cols(tower_cancelled_details)),




                        width="stretch",




                        hide_index=True,




                        height=380,




                    )









            st.markdown("---")




            # Consider only reconciled rows for cancellation/non-cancellation reporting.




            recon_scope = full_with_cancellation[




                full_with_cancellation["match_status"].isin(["matched_ok", "duplicate_resolved", "matched_price_mismatch"])




            ].copy()









            cancellation_reason = _norm_reason(recon_scope.get("Cancellation reason", pd.Series(dtype=object)))




            recon_scope["tower_cancellation_status"] = "Non Cancelled"




            recon_scope.loc[cancellation_reason.ne(""), "tower_cancellation_status"] = "Cancelled"









            cancelled_only = _cancelled_only(recon_scope)




            non_cancelled_only = recon_scope[recon_scope["tower_cancellation_status"] == "Non Cancelled"].copy()









            # Requested: cancelled subsets from reconciliation buckets.




            cancelled_matched = _drop_hidden_cols(




                _select_cancel_view_cols(




                    cancelled_only[cancelled_only["match_status"].isin(["matched_ok"])].copy()




                )




            )




            cancelled_duplicate_resolved = _drop_hidden_cols(




                _select_cancel_view_cols(




                    cancelled_only[cancelled_only["match_status"].isin(["duplicate_resolved"])].copy()




                )




            )




            cancelled_price_mismatch = _drop_hidden_cols(




                _select_cancel_view_cols(




                    cancelled_only[cancelled_only["match_status"].isin(["matched_price_mismatch"])].copy()




                )




            )









            m1, m2, m3, m4 = st.columns(4)




            m1.metric("Reconciled Rows", f"{len(recon_scope):,}")




            m2.metric("Cancelled", f"{len(cancelled_only):,}")




            m3.metric("Non Cancelled", f"{len(non_cancelled_only):,}")




            m4.metric("Workbook Rows", f"{len(tower_df):,}")









            st.markdown("**Cancellation reason categories**")




            reason_counts = (




                cancelled_only.assign(_reason=_norm_reason(cancelled_only.get("Cancellation reason", "")))




                .groupby("_reason", as_index=False)




                .size()




                .rename(columns={"_reason": "Cancellation reason", "size": "count"})




                .sort_values("count", ascending=False)




            )




            if reason_counts.empty:




                st.info("No cancellation reasons found for reconciled rows.")




            else:




                total_cancelled = float(reason_counts["count"].sum()) if "count" in reason_counts.columns else 0.0




                if total_cancelled:




                    reason_counts["share"] = (reason_counts["count"] / total_cancelled).round(4)




                st.dataframe(reason_counts, width="stretch", hide_index=True, height=260)









            st.markdown("**Complaint reason categories (on cancelled orders)**")




            complaint_series = _norm_reason(cancelled_only.get("Complaint Reason", pd.Series(dtype=object)))




            complaint_df = pd.DataFrame({"Complaint Reason": complaint_series})




            complaint_df = complaint_df[complaint_df["Complaint Reason"].ne("")].copy()




            if complaint_df.empty:




                st.info("No complaint reasons found on cancelled reconciled rows.")




                complaint_counts = pd.DataFrame(columns=["Complaint Reason", "count"])




            else:




                complaint_counts = (




                    complaint_df.groupby("Complaint Reason", as_index=False)




                    .size()




                    .rename(columns={"size": "count"})




                    .sort_values("count", ascending=False)




                )




                st.dataframe(complaint_counts, width="stretch", hide_index=True, height=240)









            st.markdown("**Complaint reason categories (all reconciled rows)**")




            complaint_series_all = _norm_reason(recon_scope.get("Complaint Reason", pd.Series(dtype=object)))




            complaint_df_all = pd.DataFrame({"Complaint Reason": complaint_series_all})




            complaint_df_all = complaint_df_all[complaint_df_all["Complaint Reason"].ne("")].copy()




            if complaint_df_all.empty:




                st.info("No complaint reasons found on reconciled rows.")




                complaint_counts_all = pd.DataFrame(columns=["Complaint Reason", "count"])




            else:




                complaint_counts_all = (




                    complaint_df_all.groupby("Complaint Reason", as_index=False)




                    .size()




                    .rename(columns={"size": "count"})




                    .sort_values("count", ascending=False)




                )




                st.dataframe(complaint_counts_all, width="stretch", hide_index=True, height=240)









            st.markdown("**Cancelled orders details**")




            if cancelled_only.empty:




                st.info("No cancelled reconciled orders to show.")




                cancelled_details = pd.DataFrame()




            else:




                reasons = sorted([r for r in _norm_reason(cancelled_only["Cancellation reason"]).unique().tolist() if r])




                selected_reason = st.selectbox(




                    "Filter by cancellation reason",




                    options=["<all>"] + reasons,




                    index=0,




                    key="foodpanda_cancel_reason_filter",




                )




                cancelled_details = cancelled_only.copy()




                if selected_reason != "<all>":




                    cancelled_details = cancelled_details[_norm_reason(cancelled_details["Cancellation reason"]).eq(selected_reason)].copy()




                cancelled_details = _drop_hidden_cols(_select_cancel_view_cols(cancelled_details))




                st.dataframe(cancelled_details, width="stretch", hide_index=True, height=340)









            st.markdown("**Complaint details (all reconciled rows)**")




            complaint_scope = recon_scope.copy()




            complaint_reason_norm = _norm_reason(complaint_scope.get("Complaint Reason", pd.Series(dtype=object)))




            complaint_scope = complaint_scope[complaint_reason_norm.ne("")].copy()




            if complaint_scope.empty:




                st.info("No complaint details found for reconciled rows.")




                complaint_details = pd.DataFrame()




            else:




                complaint_reasons = sorted([r for r in complaint_reason_norm.unique().tolist() if r])




                selected_complaint = st.selectbox(




                    "Filter by complaint reason",




                    options=["<all>"] + complaint_reasons,




                    index=0,




                    key="foodpanda_complaint_reason_filter",




                )




                complaint_details = complaint_scope.copy()




                if selected_complaint != "<all>":




                    complaint_details = complaint_details[_norm_reason(complaint_details["Complaint Reason"]).eq(selected_complaint)].copy()




                complaint_details = _drop_hidden_cols(_select_cancel_view_cols(complaint_details))




                st.dataframe(complaint_details, width="stretch", hide_index=True, height=340)









            from modules.utils import export_tables_to_excel




            cancel_tables = {




                "tower_reason_counts": tower_reason_counts,




                "tower_complaint_counts": tower_complaint_counts,




                "tower_store_diagnostics": by_store if isinstance(by_store, pd.DataFrame) else pd.DataFrame(),




                "tower_by_day": by_day if isinstance(by_day, pd.DataFrame) else pd.DataFrame(),




                "tower_by_hour": by_hour if isinstance(by_hour, pd.DataFrame) else pd.DataFrame(),




                "reconciled_scope": _drop_hidden_cols(_select_cancel_view_cols(recon_scope.copy())),




                "cancelled_only": _drop_hidden_cols(_select_cancel_view_cols(cancelled_only.copy())),




                "non_cancelled_only": _drop_hidden_cols(_select_cancel_view_cols(non_cancelled_only.copy())),




                "cancelled_matched": cancelled_matched,




                "cancelled_duplicate_resolved": cancelled_duplicate_resolved,




                "cancelled_price_mismatch": cancelled_price_mismatch,




                "cancellation_reason_counts": reason_counts,




                "complaint_reason_counts": complaint_counts,




                "complaint_reason_counts_all": complaint_counts_all,




                "cancelled_details_filtered": cancelled_details,




                "complaint_details_filtered": complaint_details,




            }




            st.download_button(




                label="Download Cancellation Report Excel",




                data=export_tables_to_excel(cancel_tables),




                file_name=f"foodpanda_cancellation_{self.start_date}_to_{self.end_date}.xlsx",




                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",




                key="foodpanda_cancel_download",




            )










        st.subheader("Full Reconciliation")





        st.dataframe(full, width="stretch", hide_index=True, height=420)











        from modules.utils import export_tables_to_excel




        tables = {




            "recon_full": full,




            "matched_only": matched_only,




            "mismatches": mismatches,




            "unmatched": unmatched,




            "excel_duplicates": excel_duplicates,




            "duplicates": duplicates,




            "summary": result.summary,




        }




        st.download_button(





            label="Download Reconciliation Excel",





            data=export_tables_to_excel(tables),





            file_name=f"foodpanda_recon_{self.start_date}_to_{self.end_date}.xlsx",





            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",





            key="foodpanda_recon_download",





        )
