import sys
import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. _fetch_summary replacement
summary_new = """    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_summary(_self, start_date: str, end_date: str) -> pd.DataFrame:
        query = \"\"\"
        WITH range_data AS (
            SELECT
                [datetime],
                UPPER(ISNULL(LTRIM(RTRIM(orderStatus)), '')) AS order_status_norm,
                UPPER(ISNULL(LTRIM(RTRIM(paymentStatus)), '')) AS payment_status_norm,
                ISNULL(isReject, 0) AS is_reject,
                COALESCE(subTotal, 0) AS subtotal,
                COALESCE(taxAmount, 0) AS tax_amount,
                COALESCE(deliveryCharges, 0) AS delivery_charges,
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
        marked AS (
            SELECT
                [datetime],
                subtotal,
                tax_amount,
                delivery_charges,
                gross_before_discount,
                total_discount,
                net_amount,
                CASE
                    WHEN is_reject = 1 OR order_status_norm LIKE '%REJECT%' OR order_status_norm LIKE '%CANCEL%' THEN 1
                    WHEN order_status_norm = 'BOOKED' AND payment_status_norm IN ('NP', 'PREORDER') THEN 1
                    ELSE 0
                END AS is_excluded
            FROM range_data
        )
        SELECT
            SUM(CASE WHEN is_excluded = 0 THEN 1 ELSE 0 END) AS total_orders,
            SUM(CASE WHEN is_excluded = 0 THEN (gross_before_discount - total_discount) ELSE 0 END) AS total_net_sales,
            SUM(CASE WHEN is_excluded = 0 THEN net_amount ELSE 0 END) AS total_net_sales_with_delivery,
            SUM(CASE WHEN is_excluded = 0 THEN (subtotal - total_discount) ELSE 0 END) AS total_sales_wo_tax_delivery,
            SUM(CASE WHEN is_excluded = 0 THEN tax_amount ELSE 0 END) AS total_tax,
            SUM(CASE WHEN is_excluded = 0 THEN delivery_charges ELSE 0 END) AS total_delivery_charges,
            SUM(CASE WHEN is_excluded = 0 THEN total_discount ELSE 0 END) AS total_discount,
            AVG(CASE WHEN is_excluded = 0 THEN (gross_before_discount - total_discount) ELSE NULL END) AS avg_order_value,
            MIN(CASE WHEN is_excluded = 0 THEN [datetime] ELSE NULL END) AS first_order_ts,
            MAX(CASE WHEN is_excluded = 0 THEN [datetime] ELSE NULL END) AS last_order_ts
        FROM marked;
        \"\"\"
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_date, end_date])"""

# Replace _fetch_summary
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_summary\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_date, end_date\]\)', summary_new, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fetch Summary replacement complete.")
