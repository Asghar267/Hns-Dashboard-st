import pyodbc
import pandas as pd

def audit_totals():
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
    
    # Blocked Names from modules/config.py (approximated based on previous knowledge)
    blocked_names = [
        'Employee food','Wali Jaan','Wali jan','Wali Jaan Personal','Employee Food','Wali jaan personal','Gv (Wali Jaan)',
        'Personal Wali Jaan','Wali Jaan Persnal','Wali Jan Personal','Wali Jaan Personal order'
    ]
    
    try:
        conn = pyodbc.connect(conn_str)
        
        # Period: April 1 to April 16, 2026
        
        # 1. Total Nt_amount from tblSales (Overview Logic)
        q_overview = f"""
        SELECT SUM(Nt_amount) 
        FROM tblSales WITH (NOLOCK)
        WHERE sale_date >= '2026-04-01' AND sale_date < '2026-04-17'
        AND Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        """
        overview_total = pd.read_sql(q_overview, conn, params=blocked_names).iloc[0,0]
        
        # 2. Total Line Value from Dashboard Query (Net Sales Logic)
        q_chef_net = f"""
        WITH filtered_sales AS (
            SELECT s.sale_id, s.Nt_amount
            FROM tblSales s WITH (NOLOCK)
            WHERE s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
            AND s.Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        ),
        line_totals AS (
            SELECT li.sale_id, SUM(li.qty * li.Unit_price) AS line_total
            FROM tblSalesLineItems li WITH (NOLOCK)
            JOIN filtered_sales fs ON fs.sale_id = li.sale_id
            WHERE li.Unit_price > 0
            GROUP BY li.sale_id
        )
        SELECT SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS total_chef_net
        FROM filtered_sales fs
        JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
        JOIN line_totals lt ON lt.sale_id = fs.sale_id
        WHERE li.Unit_price > 0
        """
        chef_net_total = pd.read_sql(q_chef_net, conn, params=blocked_names).iloc[0,0]

        # 3. Total Gross Sales (Qty * Price) - This is what users often expect
        q_chef_gross = f"""
        SELECT SUM(li.qty * li.Unit_price) AS total_chef_gross
        FROM tblSales s WITH (NOLOCK)
        JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
        WHERE s.sale_date >= '2026-04-01' AND s.sale_date < '2026-04-17'
        AND s.Cust_name NOT IN ({','.join(['?' for _ in blocked_names])})
        AND li.Unit_price > 0
        """
        chef_gross_total = pd.read_sql(q_chef_gross, conn, params=blocked_names).iloc[0,0]
        
        print(f"\nAudit for April 1-16, 2026:")
        print(f"1. Sales Overview (Nt_amount): {overview_total:,.2f}")
        print(f"2. Chef Sales (Dashboard Net): {chef_net_total:,.2f}")
        print(f"3. Chef Sales (Raw Gross):     {chef_gross_total:,.2f}")
        
        # 4. Check "Unused" category mapping
        q_unused = """
        SELECT TOP 5 p.item_name, l.field_name
        FROM tblDefProducts p
        JOIN tblDefLineItems l ON p.line_item_id = l.line_item_id
        WHERE l.field_name = 'Unused'
        """
        unused_items = pd.read_sql(q_unused, conn)
        print("\nItems mapped to 'Unused':")
        print(unused_items)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_totals()
