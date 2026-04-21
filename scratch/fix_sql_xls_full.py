import sys
import re

file_path = r"c:\Users\Fahad\Desktop\New folder (2)\Asghar_work\HNS_Deshboard\dashboard_tabs\call_center_tab.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. _fetch_summary_xls_aligned replacement
xls_aligned_new = """    @st.cache_data(ttl=300, show_spinner=False)
    def _fetch_summary_xls_aligned(_self, start_ts: str, end_ts: str) -> pd.DataFrame:
        query = \"\"\"
        WITH base AS (
            SELECT
                [datetime],
                CAST(ISNULL(subTotal, 0) AS DECIMAL(18, 2)) AS subtotal,
                CAST(ISNULL(taxAmount, 0) AS DECIMAL(18, 2)) AS tax_amount,
                CAST(ISNULL(deliveryCharges, 0) AS DECIMAL(18, 2)) AS delivery_charges,
                CAST(ISNULL(totalWithTax, 0) AS DECIMAL(18, 2)) AS total_with_tax,
                CAST(
                    ISNULL(
                        CASE
                            WHEN ISNULL(discountAmount, 0) > 0 THEN discountAmount
                            WHEN ISNULL(totalDiscount, 0) > 0 THEN totalDiscount
                            ELSE 0
                        END,
                        0
                    ) + ISNULL(voucherAmount, 0) AS DECIMAL(18, 2)
                ) AS total_discount,
                CAST(ISNULL(netAmount, 0) AS DECIMAL(18, 2)) AS net_amount
            FROM dbo.orderMaster
            WHERE [datetime] >= ? AND [datetime] < ?
              AND ISNULL(isDelete, 0) = 0
              AND UPPER(ISNULL(LTRIM(RTRIM(orderType)), '')) = 'DELIVERY'
        )
        SELECT
            COUNT(*) AS total_orders,
            SUM(subtotal) AS total_gross_sales,
            SUM(net_amount) AS total_net_sales_with_delivery,
            SUM(total_with_tax - total_discount) AS total_net_sales_xls,
            SUM(total_with_tax - total_discount) AS total_net_sales, -- Keep for compatibility
            SUM(subtotal - total_discount) AS total_sales_wo_tax_delivery,
            SUM(tax_amount) AS total_tax,
            SUM(delivery_charges) AS total_delivery_charges,
            SUM(total_discount) AS total_discount,
            AVG(total_with_tax - total_discount) AS avg_order_value,
            MIN([datetime]) AS first_order_ts,
            MAX([datetime]) AS last_order_ts
        FROM base;
        \"\"\"
        with pyodbc.connect(_self._build_conn_str()) as conn:
            return pd.read_sql(query, conn, params=[start_ts, end_ts])"""

# Replace _fetch_summary_xls_aligned
content = re.sub(r'    @st\.cache_data\(ttl=300, show_spinner=False\)\s+def _fetch_summary_xls_aligned\(.*?\):.*?return pd\.read_sql\(query, conn, params=\[start_ts, end_ts\]\)', xls_aligned_new, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("XLS Aligned replacement complete.")
