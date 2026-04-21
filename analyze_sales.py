"""
Sales Analysis for HOTNSPICYHEAD Database
Analyzes sales tables to understand:
- What sales tables exist
- Sales methods/order types
- Latest sales dates
- Sales volume and totals
"""
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=103.86.55.34,50908;"
    "DATABASE=HOTNSPICYHEAD;"
    "UID=sa;"
    "PWD=123;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

def connect():
    return pyodbc.connect(CONN_STR)

def analyze_sales_structure(conn):
    """Analyze the sales/order table structure"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES TABLES IN DATABASE")
    print("="*80)
    
    # Find all sales/order related tables
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT
        FROM INFORMATION_SCHEMA.TABLES t
        CROSS APPLY (
            SELECT SUM(p.row_count) as ROW_COUNT
            FROM sys.dm_db_partition_stats p
            WHERE p.object_id = OBJECT_ID(QUOTENAME(t.TABLE_SCHEMA) + '.' + QUOTENAME(t.TABLE_NAME))
              AND p.index_id IN (0, 1)
        ) counts
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND (TABLE_NAME LIKE '%sale%' OR TABLE_NAME LIKE '%order%' OR TABLE_NAME LIKE '%customer%pos%' 
               OR TABLE_NAME LIKE '%invoice%' OR TABLE_NAME LIKE '%kot%' OR TABLE_NAME LIKE '%dine%')
        ORDER BY ROW_COUNT DESC
    """)
    
    sales_tables = cursor.fetchall()
    print(f"\n{'Schema':<10} {'Table':<35} {'Rows':>12}")
    print("-"*60)
    for row in sales_tables:
        print(f"{row.TABLE_SCHEMA:<10} {row.TABLE_NAME:<35} {row.ROW_COUNT:>12,}")
    
    cursor.close()
    return [t.TABLE_NAME for t in sales_tables]

def get_latest_sales_dates(conn):
    """Find latest dates in sales tables"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("LATEST SALES DATES")
    print("="*80)
    
    tables_to_check = [
        ('Order_Detail', 'date'),
        ('Dine_In_Order', 'order_date'),
        ('OrderKot', 'date'),
        ('OrderMaster', 'Date'),
        ('SaleInvoiceMaster', 'Date'),
        ('CustomerPOS', None),  # No date column likely
    ]
    
    results = []
    for table, date_col in tables_to_check:
        try:
            if date_col:
                query = f"SELECT MAX([{date_col}]) FROM [{table}]"
                cursor.execute(query)
                max_date = cursor.fetchone()[0]
                if max_date:
                    results.append((table, max_date))
                    print(f"{table:<30} Latest {date_col:<15} {max_date}")
            else:
                # Check if any date-like column exists
                cursor.execute(f"""
                    SELECT TOP 1 name FROM sys.columns 
                    WHERE object_id = OBJECT_ID('{table}') 
                      AND name LIKE '%date%' OR name LIKE '%time%'
                    ORDER BY column_id
                """)
                date_col_row = cursor.fetchone()
                if date_col_row:
                    date_col = date_col_row.name
                    query = f"SELECT MAX([{date_col}]) FROM [{table}]"
                    cursor.execute(query)
                    max_date = cursor.fetchone()[0]
                    if max_date:
                        results.append((table, max_date))
                        print(f"{table:<30} Latest {date_col:<15} {max_date}")
        except Exception as e:
            print(f"{table:<30} ERROR: {str(e)[:40]}")
    
    cursor.close()
    return results

def get_sales_methods(conn):
    """Identify sales methods/order types/channels"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES METHODS / ORDER TYPES")
    print("="*80)
    
    # Check various order type/category columns
    checks = [
        ('Dine_In_Order', 'order_type', 'Dine_In_Order.order_type'),
        ('Order_Detail', 'category_name', 'Order_Detail.category_name'),
        ('OrderMaster', 'order_type', 'OrderMaster.order_type'),
        ('CustomerPOS', None, 'Check distinct order_key patterns'),
    ]
    
    for table, col, desc in checks:
        try:
            if col:
                cursor.execute(f"SELECT DISTINCT TOP 20 [{col}] FROM [{table}] WHERE [{col}] IS NOT NULL")
            else:
                cursor.execute(f"SELECT DISTINCT TOP 20 order_key FROM [{table}] WHERE order_key IS NOT NULL")
            rows = cursor.fetchall()
            if rows:
                print(f"\n{desc}:")
                for row in rows:
                    print(f"  - {row[0]}")
        except Exception as e:
            print(f"\n{desc}: ERROR - {e}")
    
    cursor.close()

def get_sales_summary(conn):
    """Get total sales statistics"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES VOLUME SUMMARY")
    print("="*80)
    
    tables = ['Order_Detail', 'Dine_In_Order', 'OrderKot', 'CustomerPOS']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cursor.fetchone()[0]
            print(f"{table:<30} Total Records: {count:,}")
        except:
            print(f"{table:<30} Table not accessible")
    
    cursor.close()

def get_order_amounts(conn):
    """Check if there are amount/price columns to calculate sales value"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES AMOUNT / REVENUE FIELDS")
    print("="*80)
    
    # Check for amount/price columns in key tables
    tables = ['Order_Detail', 'Dine_In_Order', 'OrderKot', 'SaleInvoiceMaster']
    for table in tables:
        try:
            cursor.execute(f"""
                SELECT name, data_type, max_length
                FROM sys.columns
                WHERE object_id = OBJECT_ID('{table}')
                  AND (name LIKE '%amount%' OR name LIKE '%price%' OR name LIKE '%total%' OR name LIKE '%grand%')
                ORDER BY column_id
            """)
            cols = cursor.fetchall()
            if cols:
                print(f"\n{table}:")
                for col in cols:
                    print(f"  {col.name} ({col.data_type})")
        except Exception as e:
            print(f"{table}: ERROR - {e}")
    
    cursor.close()

def main():
    print("\n" + "="*80)
    print("HOTNSPICYHEAD SALES DATA ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    conn = None
    try:
        conn = connect()
        print("\n[OK] Connected to HOTNSPICYHEAD database")
        
        # Run analyses
        sales_tables = analyze_sales_structure(conn)
        latest_dates = get_latest_sales_dates(conn)
        get_sales_methods(conn)
        get_sales_summary(conn)
        get_order_amounts(conn)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nKey Sales Tables Found: {len(sales_tables)}")
        print("See details above for structure, dates, and methods.")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
