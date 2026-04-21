import pyodbc
import pandas as pd

def analyze_discrepancy():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    
    # Blocked lists from config.py
    BLOCKED_NAMES = [
        "Wali Jaan Personal Orders", "Raza Khan M.D", "Customer Discount 100%",
        "Daraksha Mobile 100%", "DHA Police Discount 100%", "HNS Product Marketing 100%",
        "Home Food Order (Madam)", "Home Food Orders", "Home Food Orders (Raza Khan)",
        "Home Food Orders (Shehryar Khan)", "Home Food Orders (Umair Sb)",
        "Rangers mobile 100%", "Return N Cancellation (Aftert Preperation)",
        "Return N Cancellation (without preperation)"
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        print("\n--- Discrepancy Analysis for Rolls (March 2026) ---")
        
        # 1. Total Raw Gross Sales (No filters)
        q_gross = """
        SELECT SUM(li.qty * li.Unit_price) as Gross
        FROM tblSalesLineItems li
        JOIN tblSales s ON li.sale_id = s.sale_id
        LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems l ON p.line_item_id = l.line_item_id
        WHERE l.field_name LIKE '%Roll%'
        AND s.sale_date >= '2026-03-01' AND s.sale_date < '2026-04-01'
        """
        raw_gross = pd.read_sql(q_gross, conn).iloc[0,0]
        print(f"1. Raw Gross Sales: {raw_gross:,.2f}")

        # 2. Total Gross Sales excluding Blocked Customers
        placeholders = ','.join(["?"] * len(BLOCKED_NAMES))
        q_filtered_gross = f"""
        SELECT SUM(li.qty * li.Unit_price) as FilteredGross
        FROM tblSalesLineItems li
        JOIN tblSales s ON li.sale_id = s.sale_id
        LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems l ON p.line_item_id = l.line_item_id
        WHERE l.field_name LIKE '%Roll%'
        AND s.sale_date >= '2026-03-01' AND s.sale_date < '2026-04-01'
        AND s.Cust_name NOT IN ({placeholders})
        """
        filtered_gross = pd.read_sql(q_filtered_gross, conn, params=BLOCKED_NAMES).iloc[0,0]
        print(f"2. Filtered Gross (No Wali Jaan, etc.): {filtered_gross:,.2f}")

        # 3. Dashboard Proportional Net Sales (with all filters)
        q_dashboard = f"""
        WITH filtered_sales AS (
            SELECT s.sale_id, s.Nt_amount
            FROM tblSales s
            WHERE s.sale_date >= '2026-03-01' AND s.sale_date < '2026-04-01'
            AND s.Cust_name NOT IN ({placeholders})
        ),
        line_totals AS (
            SELECT li.sale_id, SUM(li.qty * li.Unit_price) AS line_total
            FROM tblSalesLineItems li
            JOIN filtered_sales fs ON fs.sale_id = li.sale_id
            WHERE li.Unit_price > 0
            GROUP BY li.sale_id
        )
        SELECT SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS DashboardNet
        FROM filtered_sales fs
        JOIN tblSalesLineItems li ON fs.sale_id = li.sale_id
        JOIN line_totals lt ON lt.sale_id = fs.sale_id
        LEFT JOIN tblProductItem pi ON li.Product_Item_ID = pi.Product_Item_ID
        LEFT JOIN tblDefProducts p ON pi.Product_ID = p.product_id
        LEFT JOIN tblDefLineItems l ON p.line_item_id = l.line_item_id
        WHERE l.field_name LIKE '%%Roll%%'
        AND li.Unit_price > 0
        """
        dashboard_net = pd.read_sql(q_dashboard, conn, params=BLOCKED_NAMES).iloc[0,0]
        print(f"3. Dashboard Net Sales (Proportional): {dashboard_net:,.2f}")

        print("\n--- Conclusion ---")
        if raw_gross > dashboard_net:
            diff = raw_gross - dashboard_net
            print(f"Difference is {diff:,.2f} ({diff/raw_gross:.1%} decrease)")
            print("This is primarily due to Discounts/Nt_amount allocation and Blocked Filters.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_discrepancy()
