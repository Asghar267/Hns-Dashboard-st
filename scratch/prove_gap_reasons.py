import pyodbc
import pandas as pd

def prove_reconciliation():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.86.55.183,10305;"
        "DATABASE=Candelahns;"
        "UID=ReadOnlyUser;"
        "PWD=902729@Rafy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branch_ids = '(2, 4, 14)'
    
    # 1. Fetch exact aggregate columns from tblSales
    query = f"""
    SELECT 
        SUM(Nt_amount) as total_overview,
        SUM(total_tax) as taxes,
        SUM(service_charges) as service_charges,
        SUM(total_discount) as discounts,
        SUM(Round_Amount) as rounding
    FROM tblSales WITH (NOLOCK)
    WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND shop_id IN {branch_ids}
      AND is_cancel = 0
    """
    df = pd.read_sql(query, conn)
    
    # 2. Fetch sum of line items
    query_lines = f"""
    SELECT SUM(qty * Unit_price) as line_item_sum
    FROM tblSalesLineItems li WITH (NOLOCK)
    JOIN tblSales s WITH (NOLOCK) ON s.sale_id = li.sale_id
    WHERE s.sale_date BETWEEN '{start_date}' AND '{end_date}'
      AND s.shop_id IN {branch_ids}
      AND s.is_cancel = 0
    """
    df_lines = pd.read_sql(query_lines, conn)
    
    # 3. Present Proof
    ov = df.iloc[0]['total_overview']
    tax = df.iloc[0]['taxes']
    sc = df.iloc[0]['service_charges']
    disc = df.iloc[0]['discounts']
    round_amt = df.iloc[0]['rounding']
    line_sum = df_lines.iloc[0]['line_item_sum']
    
    # In Candela: Nt_amount = (Line Sum) + (Tax) + (SC) - (Disc) + (Rounding)
    calculated_nt = line_sum + tax + sc - disc + round_amt
    
    print(f"\n--- PROOF OF RECONCILIATION GAP (March) ---")
    print(f"1. Total Overview Revenue (Nt_amount): {ov:,.2f}")
    print(f"2. Sum of Products (Line Items):       {line_sum:,.2f}")
    print(f"3. GAP TO RECONCILE:                    {ov - line_sum:,.2f}")
    print(f"\n--- REASONS FOR THE GAP (Extracted from Database) ---")
    print(f"A. Total Taxes:          {tax:,.2f}")
    print(f"B. Service Charges:      {sc:,.2f}")
    print(f"C. Discounts:           -{disc:,.2f}")
    print(f"D. Rounding:             {round_amt:,.2f}")
    print(f"-------------------------------------------")
    print(f"TOTAL OF REASONS (A+B+C+D): {tax + sc - disc + round_amt:,.2f}")
    
    print(f"\nUnexplained Gap: { (ov - line_sum) - (tax + sc - disc + round_amt) :,.2f}")

if __name__ == "__main__":
    prove_reconciliation()
