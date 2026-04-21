import sys
import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Unified Method Replacements

# 1. _fetch_branch_counter_drilldown
drilldown_new = """    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_branch_counter_drilldown(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = \"\"\"
        WITH base AS (
            SELECT
                ISNULL(branchId, -1) AS branch_id,
                ISNULL(counterId, -1) AS counter_id,
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount,
                [datetime]
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        ),
        filtered AS (
            SELECT * FROM base
            WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
              AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        )
        SELECT
            branch_id,
            counter_id,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
            SUM(net_amount) AS total_net_with_delivery,
            AVG(gross_before_discount - total_discount) AS avg_order_value,
            MIN([datetime]) AS first_order_ts,
            MAX([datetime]) AS last_order_ts
        FROM filtered
        GROUP BY branch_id, counter_id
        ORDER BY total_net_sales DESC;
        \"\"\"
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])"""

# 2. _fetch_excluded_orders
excluded_new = """    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_excluded_orders(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = \"\"\"
        WITH base AS (
            SELECT
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                (
                    COALESCE(totalWithTax, 0)
                    + COALESCE(deliveryCharges, 0)
                    + COALESCE(extraCharges, 0)
                    + COALESCE(cardCharges, 0)
                ) AS gross_before_discount,
                (
                    COALESCE(
                        CASE
                            WHEN COALESCE(discountAmount, 0) > 0 THEN discountAmount
                            WHEN COALESCE(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + COALESCE(voucherAmount, 0)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE CAST([datetime] AS date) BETWEEN ? AND ?
              AND ISNULL(isDelete, 0) = 0
        )
        SELECT
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' THEN 1 ELSE 0 END) AS rejected_orders,
            SUM(CASE WHEN order_status_norm LIKE '%CANCEL%' THEN 1 ELSE 0 END) AS cancelled_orders,
            SUM(CASE WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN 1 ELSE 0 END) AS open_unpaid_orders,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN 1 ELSE 0 END) AS excluded_orders,
            SUM(CASE WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN (gross_before_discount - total_discount) ELSE 0 END) AS rejected_cancelled_sales,
            SUM(CASE WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN (gross_before_discount - total_discount) ELSE 0 END) AS open_unpaid_sales,
            SUM(
                CASE
                    WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%'
                      OR (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
                    THEN (gross_before_discount - total_discount)
                    ELSE 0
                END
            ) AS excluded_sales_total
        FROM base;
        \"\"\"
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])"""

# Replace drilldown
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_branch_counter_drilldown\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_date, end_date\]\)', drilldown_new, content, flags=re.DOTALL)

# Replace excluded
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_excluded_orders\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_date, end_date\]\)', excluded_new, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Comprehensive query replacement complete.")
