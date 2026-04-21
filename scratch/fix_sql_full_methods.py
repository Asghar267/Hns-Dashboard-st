import sys
import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace _fetch_branch_counter_drilldown
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

# 2. Replace _fetch_area_sales
area_new = """    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_area_sales(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = \"\"\"
        WITH base AS (
            SELECT
                ISNULL(NULLIF(LTRIM(RTRIM(delvArea)), ''), '(blank)') AS delv_area,
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
        ),
        filtered AS (
            SELECT * FROM base
            WHERE NOT (is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%')
              AND NOT (order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER'))
        )
        SELECT
            delv_area,
            COUNT(*) AS total_orders,
            SUM(gross_before_discount - total_discount) AS total_net_sales,
            SUM(total_discount) AS total_discount,
            SUM(net_amount) AS total_net_with_delivery,
            AVG(gross_before_discount - total_discount) AS avg_order_value
        FROM filtered
        GROUP BY delv_area
        ORDER BY total_net_sales DESC;
        \"\"\"
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])"""

# Precise replacement using regex to find the method starts and ends
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_branch_counter_drilldown\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_date, end_date\]\)', drilldown_new, content, flags=re.DOTALL)
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_area_sales\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_date, end_date\]\)', area_new, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Full method replacement complete.")
