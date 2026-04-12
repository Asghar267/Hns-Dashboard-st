"""
QR Commission Service
Handles QR/Blinkco commission analysis business logic
"""

import pandas as pd
from typing import Dict, List, Tuple
from modules.database import (
    pool,
    placeholders
)
from modules.blink_reporting import (
    prepare_blink_orders,
    build_split_report,
    apply_split_filters,
    add_transaction_quality_flags,
)
from modules.config import BLOCKED_NAMES, BLOCKED_COMMENTS
from modules.qr_logic import apply_monthly_split_metrics


class QRCommissionService:
    """Service for QR Commission-related operations"""
    
    @staticmethod
    def get_qr_commission_data(start_date: str, end_date: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch Blinkco transactions at sale level (end_date is inclusive)."""
        conn = pool.get_connection("candelahns")

        qr_query = f"""
        SELECT
            s.sale_id,
            s.sale_date,
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            s.Nt_amount AS total_sale,
            LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS external_ref_id
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.external_ref_type = 'Blinkco order'
        """

        qr_params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                qr_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                qr_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                qr_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                qr_params.extend(BLOCKED_COMMENTS)

        return pd.read_sql(qr_query, conn, params=qr_params)

    @staticmethod
    def get_non_blinkco_sales_transactions(
        start_date: str, end_date: str, branch_ids: List[int], mode: str
    ) -> pd.DataFrame:
        """Fetch non-Blinkco transactions at sale level (used for match checks)."""
        if not branch_ids:
            return pd.DataFrame()
        conn = pool.get_connection("candelahns")
        q = f"""
        SELECT
            s.sale_id,
            s.sale_date,
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            s.Nt_amount AS total_sale,
            LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS external_ref_id,
            s.external_ref_type
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND (s.external_ref_type <> 'Blinkco order' OR s.external_ref_type IS NULL)
        """
        params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                q += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)
        return pd.read_sql(q, conn, params=params)
    
    @staticmethod
    def get_total_sales_data(start_date: str, end_date: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch total sales (all order types) by employee and branch."""
        conn = pool.get_connection("candelahns")
        total_query = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions_all,
            SUM(s.Nt_amount) AS total_sales_all
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
        """

        total_params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                total_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                total_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                total_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                total_params.extend(BLOCKED_COMMENTS)

        total_query += """
        GROUP BY
            s.shop_id, sh.shop_name,
            COALESCE(e.shop_employee_id, 0),
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY total_sales_all DESC
        """
        return pd.read_sql(total_query, conn, params=total_params)
    
    @staticmethod
    def get_blink_raw_orders(start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch raw Blink orders"""
        conn = pool.get_connection("candelahns")
        blink_raw_query = """
        SELECT
            BlinkOrderId,
            OrderJson,
            CreatedAt
        FROM tblInitialRawBlinkOrder
        WHERE CreatedAt >= ? AND CreatedAt < DATEADD(DAY, 1, ?)
        """
        return pd.read_sql(blink_raw_query, conn, params=[start_date, end_date])

    @staticmethod
    def get_blink_raw_orders_for_qr_sales(
        start_date: str, end_date: str, branch_ids: List[int], mode: str
    ) -> pd.DataFrame:
        """
        Fetch raw Blink orders only for QR sales in selected branches/date range.
        This avoids scanning/fetching the full tblInitialRawBlinkOrder range.
        """
        if not branch_ids:
            return pd.DataFrame(columns=["BlinkOrderId", "OrderJson", "CreatedAt"])

        conn = pool.get_connection("candelahns")
        q = f"""
        SELECT
            rb.BlinkOrderId,
            rb.OrderJson,
            rb.CreatedAt
        FROM tblInitialRawBlinkOrder rb
        INNER JOIN (
            SELECT DISTINCT s.external_ref_id
            FROM tblSales s
            WHERE s.sale_date >= ?
              AND s.sale_date < DATEADD(DAY, 1, ?)
              AND s.shop_id IN ({placeholders(len(branch_ids))})
              AND s.external_ref_type = 'Blinkco order'
        """

        params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                q += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)

        q += """
        ) x ON LTRIM(RTRIM(CONVERT(varchar(64), rb.BlinkOrderId))) = LTRIM(RTRIM(CONVERT(varchar(64), x.external_ref_id)))
        """
        return pd.read_sql(q, conn, params=params)

    @staticmethod
    def get_blink_raw_orders_for_non_blink_sales(
        start_date: str, end_date: str, branch_ids: List[int], mode: str
    ) -> pd.DataFrame:
        """
        Fetch raw Blink orders only for NON-Blinkco sales that still have an external_ref_id.
        This allows match checks where external_ref_type may be missing/misclassified.
        """
        if not branch_ids:
            return pd.DataFrame(columns=["BlinkOrderId", "OrderJson", "CreatedAt"])

        conn = pool.get_connection("candelahns")
        q = f"""
        SELECT
            rb.BlinkOrderId,
            rb.OrderJson,
            rb.CreatedAt
        FROM tblInitialRawBlinkOrder rb
        INNER JOIN (
            SELECT DISTINCT s.external_ref_id
            FROM tblSales s
            WHERE s.sale_date >= ?
              AND s.sale_date < DATEADD(DAY, 1, ?)
              AND s.shop_id IN ({placeholders(len(branch_ids))})
              AND (s.external_ref_type <> 'Blinkco order' OR s.external_ref_type IS NULL)
              AND s.external_ref_id IS NOT NULL
              AND LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) <> ''
        """
        params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                q += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)

        q += """
        ) x ON LTRIM(RTRIM(CONVERT(varchar(64), rb.BlinkOrderId))) = LTRIM(RTRIM(CONVERT(varchar(64), x.external_ref_id)))
        """
        return pd.read_sql(q, conn, params=params)

    @staticmethod
    def get_pos_line_item_stats(
        start_date: str, end_date: str, branch_ids: List[int], mode: str, blinkco_only: bool = True
    ) -> pd.DataFrame:
        """Fetch POS line-item aggregates by sale_id (qty + item line count)."""
        if not branch_ids:
            return pd.DataFrame(columns=["sale_id", "pos_total_qty", "pos_item_lines"])
        conn = pool.get_connection("candelahns")
        q = f"""
        SELECT
            s.sale_id,
            SUM(li.qty) AS pos_total_qty,
            COUNT(*) AS pos_item_lines
        FROM tblSales s
        INNER JOIN tblSalesLineItems li ON s.sale_id = li.sale_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
        """
        params: List = [start_date, end_date] + branch_ids
        if blinkco_only:
            q += " AND s.external_ref_type = 'Blinkco order'"
        if mode == "Filtered":
            if BLOCKED_NAMES:
                q += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                q += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)
        q += " GROUP BY s.sale_id"
        return pd.read_sql(q, conn, params=params)
    
    @staticmethod
    def get_qr_product_sales_data(start_date: str, end_date: str, branch_ids: List[int], mode: str) -> pd.DataFrame:
        """Fetch Blinkco line-item product sales for product-wise commission."""
        conn = pool.get_connection("candelahns")
        product_query = f"""
        SELECT
            s.shop_id,
            sh.shop_name,
            p.Product_code,
            p.item_name AS product_name,
            SUM(li.qty) AS total_qty,
            SUM(li.qty * li.Unit_price) AS product_sales
        FROM tblSales s
        INNER JOIN tblSalesLineItems li ON s.sale_id = li.sale_id
        LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p ON pi.Product_ID = p.Product_ID
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.external_ref_type = 'Blinkco order'
        """

        product_params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                product_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                product_params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                product_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                product_params.extend(BLOCKED_COMMENTS)

        product_query += """
        GROUP BY s.shop_id, sh.shop_name, p.Product_code, p.item_name
        ORDER BY product_sales DESC
        """
        return pd.read_sql(product_query, conn, params=product_params)

    @staticmethod
    def get_employee_data_quality() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
        """Employee name/code duplication diagnostics from tblDefShopEmployees."""
        conn = pool.get_connection("candelahns")

        stats_q = """
        SELECT
          COUNT(*) AS total_employees,
          COUNT(DISTINCT LTRIM(RTRIM(COALESCE(field_Code,'')))) AS distinct_codes
        FROM tblDefShopEmployees
        """
        stats = pd.read_sql(stats_q, conn).to_dict("records")[0]

        dup_code_q = """
        SELECT TOP 50
          LTRIM(RTRIM(field_Code)) AS field_code,
          COUNT(DISTINCT shop_employee_id) AS distinct_employee_ids,
          MIN(shop_employee_id) AS min_employee_id,
          MAX(shop_employee_id) AS max_employee_id
        FROM tblDefShopEmployees
        WHERE field_Code IS NOT NULL AND LTRIM(RTRIM(field_Code)) <> ''
        GROUP BY LTRIM(RTRIM(field_Code))
        HAVING COUNT(DISTINCT shop_employee_id) > 1
        ORDER BY COUNT(DISTINCT shop_employee_id) DESC, COUNT(*) DESC
        """
        df_dup_codes = pd.read_sql(dup_code_q, conn)

        dup_names_q = """
        WITH dup_names AS (
          SELECT field_name
          FROM tblDefShopEmployees
          GROUP BY field_name
          HAVING COUNT(DISTINCT shop_employee_id) > 1
        )
        SELECT
          e.field_name AS employee_name,
          e.shop_employee_id AS employee_id,
          LTRIM(RTRIM(COALESCE(e.field_Code,''))) AS field_code,
          e.shop_id,
          sh.shop_name,
          e.start_date,
          e.end_date
        FROM tblDefShopEmployees e
        LEFT JOIN tblDefShops sh ON e.shop_id = sh.shop_id
        INNER JOIN dup_names d ON e.field_name = d.field_name
        ORDER BY e.field_name, e.shop_employee_id
        """
        df_dup_names = pd.read_sql(dup_names_q, conn)

        out_stats = {
            "total_employees": int(stats.get("total_employees") or 0),
            "distinct_codes": int(stats.get("distinct_codes") or 0),
            "duplicate_codes_rows": int(len(df_dup_codes)),
            "duplicate_names_rows": int(len(df_dup_names)),
        }
        return df_dup_codes, df_dup_names, out_stats

    @staticmethod
    def get_employee_roster(branch_ids: List[int]) -> pd.DataFrame:
        """Fetch all employees for selected branches with employment dates."""
        if not branch_ids:
            return pd.DataFrame()
        conn = pool.get_connection("candelahns")
        q = f"""
        SELECT
            e.shop_employee_id,
            e.shop_id,
            sh.shop_name,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            e.start_date,
            e.end_date
        FROM tblDefShopEmployees e
        LEFT JOIN tblDefShops sh ON e.shop_id = sh.shop_id
        WHERE e.shop_id IN ({placeholders(len(branch_ids))})
        """
        df = pd.read_sql(q, conn, params=branch_ids)
        if df.empty:
            return df
        df["shop_employee_id"] = pd.to_numeric(df["shop_employee_id"], errors="coerce").fillna(0).astype(int)
        df["shop_id"] = pd.to_numeric(df["shop_id"], errors="coerce").fillna(0).astype(int)
        return df

    @staticmethod
    def get_employee_monthly_sales_split(
        start_date: str,
        end_date: str,
        branch_ids: List[int],
        mode: str,
        commission_rate: float = 2.0,
    ) -> pd.DataFrame:
        """Monthly employee+shop sales split: total, blinkco, without blinkco, shares, commissions."""
        if not branch_ids:
            return pd.DataFrame()

        conn = pool.get_connection("candelahns")
        monthly_query = f"""
        SELECT
            CONVERT(char(7), CAST(s.sale_date AS date), 120) AS sale_month,
            s.shop_id,
            sh.shop_name,
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            COUNT(DISTINCT s.sale_id) AS total_transactions_all,
            SUM(s.Nt_amount) AS total_sales_all,
            SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN s.Nt_amount ELSE 0 END) AS total_sales_blinkco,
            SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN 1 ELSE 0 END) AS total_transactions_blinkco
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        WHERE s.sale_date >= ?
          AND s.sale_date < DATEADD(DAY, 1, ?)
          AND s.shop_id IN ({placeholders(len(branch_ids))})
        """

        params: List = [start_date, end_date] + branch_ids
        if mode == "Filtered":
            if BLOCKED_NAMES:
                monthly_query += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
                params.extend(BLOCKED_NAMES)
            if BLOCKED_COMMENTS:
                monthly_query += (
                    f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))})"
                    f" OR s.Additional_Comments IS NULL)"
                )
                params.extend(BLOCKED_COMMENTS)

        monthly_query += """
        GROUP BY
            CONVERT(char(7), CAST(s.sale_date AS date), 120),
            s.shop_id, sh.shop_name,
            COALESCE(e.shop_employee_id, 0),
            LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
            COALESCE(e.field_name, 'Online/Unassigned')
        ORDER BY
            sale_month, total_sales_all DESC
        """

        df = pd.read_sql(monthly_query, conn, params=params)
        if df.empty:
            return df

        return apply_monthly_split_metrics(df, commission_rate)
    
    @staticmethod
    def process_qr_data(df_qr: pd.DataFrame, df_blink_raw: pd.DataFrame, commission_rate: float = 2.0) -> pd.DataFrame:
        """Process QR data with Blink orders"""
        if df_qr.empty:
            return pd.DataFrame()
            
        df_qr['total_sale'] = pd.to_numeric(df_qr['total_sale'], errors='coerce').fillna(0.0)
        df_blink = prepare_blink_orders(df_blink_raw)

        # Normalize merge keys to avoid dtype mismatches (int vs str) causing 0 matches.
        df_qr = df_qr.copy()
        df_blink = df_blink.copy()
        df_qr["_ext_ref_key"] = df_qr["external_ref_id"].astype(str).str.strip()
        df_blink["_blink_id_key"] = df_blink["BlinkOrderId"].astype(str).str.strip()
        
        df_merged = df_qr.merge(
            df_blink,
            left_on="_ext_ref_key",
            right_on="_blink_id_key",
            how='left'
        )
        df_merged = df_merged.drop(columns=["_ext_ref_key", "_blink_id_key"], errors="ignore")
        df_merged['Indoge_total_price'] = pd.to_numeric(df_merged['Indoge_total_price'], errors='coerce').fillna(0.0)
        df_merged['BlinkOrderId'] = df_merged['BlinkOrderId'].fillna('-')
        df_merged['json_parse_ok'] = df_merged['json_parse_ok'].fillna(False)
        df_merged['difference'] = df_merged['Indoge_total_price'] - df_merged['total_sale']
        df_merged['Candelahns_commission'] = df_merged['total_sale'] * (commission_rate / 100)
        df_merged['Indoge_commission'] = df_merged['Indoge_total_price'] * (commission_rate / 100)
        df_merged = add_transaction_quality_flags(df_merged)
        
        return df_merged
    
    @staticmethod
    def calculate_qr_metrics(df_merged: pd.DataFrame) -> Dict[str, float]:
        """Calculate QR commission metrics"""
        if df_merged.empty:
            return {
                'total_sale': 0,
                'total_cand_comm': 0,
                'total_indoge_comm': 0,
                'total_tx': 0
            }
            
        total_sale = df_merged['total_sale'].sum()
        total_cand_comm = df_merged['Candelahns_commission'].sum()
        total_indoge_comm = df_merged['Indoge_commission'].sum()
        total_tx = len(df_merged)
        
        return {
            'total_sale': total_sale,
            'total_cand_comm': total_cand_comm,
            'total_indoge_comm': total_indoge_comm,
            'total_tx': total_tx
        }
    
    @staticmethod
    def get_split_report(df_total_sales: pd.DataFrame, df_blinkco_summary: pd.DataFrame, commission_rate: float) -> pd.DataFrame:
        """Build employee+branch split report"""
        return build_split_report(df_total_sales, df_blinkco_summary, commission_rate)
    
    @staticmethod
    def filter_split_report(split_report: pd.DataFrame, employee_search: str, branches: List[str], 
                          include_zero_rows: bool, include_unassigned: bool) -> pd.DataFrame:
        """Filter split report based on criteria"""
        return apply_split_filters(
            split_report,
            employee_search=employee_search,
            branches=branches,
            include_zero_rows=include_zero_rows,
            include_unassigned=include_unassigned,
        )
    
    @staticmethod
    def get_employee_summary(df_merged: pd.DataFrame) -> pd.DataFrame:
        """Get employee summary data"""
        employee_summary = df_merged.groupby(['employee_id', 'employee_code', 'employee_name', 'shop_id', 'shop_name'], as_index=False).agg({
            'total_sale': 'sum',
            'Candelahns_commission': 'sum',
            'Indoge_total_price': 'sum',
            'Indoge_commission': 'sum',
            'external_ref_id': 'count'
        }).rename(columns={'external_ref_id': 'transaction_count'})
        
        # Exclude unassigned rows
        employee_summary = employee_summary[
            employee_summary['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
        ].copy()
        
        return employee_summary
    
    @staticmethod
    def get_branch_summary(df_merged: pd.DataFrame) -> pd.DataFrame:
        """Get branch summary data"""
        branch_source = df_merged[
            df_merged['employee_name'].astype(str).str.strip().str.lower() != 'online/unassigned'
        ].copy()

        branch_summary = branch_source.groupby('shop_name', as_index=False).agg({
            'total_sale': 'sum',
            'Candelahns_commission': 'sum',
            'Indoge_total_price': 'sum',
            'Indoge_commission': 'sum',
            'external_ref_id': 'count'
        }).rename(columns={'external_ref_id': 'transaction_count'})
        
        return branch_summary
