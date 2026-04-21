"""
Detailed Sales Schema Analysis
Find actual amount/price columns and complete order flow
"""
import pyodbc
import pandas as pd

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

def show_table_columns(conn, table_name):
    """Show all columns for a table"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, table_name)
    
    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print(f"{'='*60}")
    print(f"{'Column':<30} {'Type':<15} {'MaxLen':<8} {'Nullable'}")
    print("-"*60)
    
    cols = []
    for row in cursor.fetchall():
        max_len = row.CHARACTER_MAXIMUM_LENGTH if row.CHARACTER_MAXIMUM_LENGTH else '-'
        print(f"{row.COLUMN_NAME:<30} {row.DATA_TYPE:<15} {str(max_len):<8} {row.IS_NULLABLE}")
        cols.append(row.COLUMN_NAME)
    
    cursor.close()
    return cols

def sample_data(conn, table_name, limit=5):
    """Show sample data"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT TOP {limit} * FROM [{table_name}]")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        
        print(f"\nSample Data ({len(rows)} rows shown):")
        print("-"*60)
        # Print header
        print(" | ".join(f"{c:<20}" for c in cols[:8]))  # First 8 columns
        print("-"*60)
        for row in rows:
            vals = []
            for val in row[:8]:
                if val is None:
                    vals.append("NULL")
                else:
                    v = str(val)
                    vals.append(v[:18] if len(v) > 18 else v.ljust(20))
            print(" | ".join(vals))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

def find_revenue_columns(conn):
    """Find all columns that likely contain sales amounts"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
        WHERE c.DATA_TYPE IN ('decimal', 'numeric', 'float', 'money', 'smallmoney')
          AND t.TABLE_NAME IN (
              'Order_Detail', 'Dine_In_Order', 'OrderKot', 'OrderMaster',
              'SaleInvoiceMaster', 'CustomerSaleInvoiceMaster', 'InvoiceMaster_Company'
          )
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
    """)
    
    print("\n" + "="*80)
    print("REVENUE/AMOUNT COLUMNS IN KEY TABLES")
    print("="*80)
    print(f"{'Table':<25} {'Column':<25} {'Type':<12} {'Precision'}")
    print("-"*80)
    
    current_table = None
    for row in cursor.fetchall():
        if row.TABLE_NAME != current_table:
            current_table = row.TABLE_NAME
            print(f"\n[{current_table}]")
        print(f"  {row.COLUMN_NAME:<25} {row.DATA_TYPE:<12} {row.NUMERIC_PRECISION},{row.NUMERIC_SCALE}")
    
    cursor.close()

def get_order_flow(conn):
    """Understand the complete order flow by checking columns"""
    print("\n" + "="*80)
    print("ORDER FLOW ANALYSIS")
    print("="*80)
    
    tables = ['Order_Detail', 'Dine_In_Order', 'OrderKot', 'CustomerPOS', 'OrderMaster']
    
    for table in tables:
        try:
            cols = show_table_columns(conn, table)
            # Look for key columns
            key_cols = [c for c in cols if any(kw in c.lower() for kw in ['order', 'date', 'time', 'amount', 'total', 'price', 'qty', 'status'])]
            print(f"\nKey columns in {table}:")
            for c in key_cols[:15]:
                print(f"  - {c}")
        except Exception as e:
            print(f"\n{table}: ERROR - {e}")

def find_common_keys(conn):
    """Find foreign key relationships between sales tables"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            fk.name AS FK_Name,
            OBJECT_NAME(fk.parent_object_id) AS ChildTable,
            COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ChildColumn,
            OBJECT_NAME(fk.referenced_object_id) AS ParentTable,
            COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ParentColumn
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        WHERE OBJECT_NAME(fk.parent_object_id) IN (
            'Order_Detail', 'Dine_In_Order', 'OrderKot', 'CustomerPOS', 
            'OrderMaster', 'Order_Payment', 'CustomerPOS_'
        )
        ORDER BY ChildTable, ChildColumn
    """)
    
    print("\n" + "="*80)
    print("SALES TABLE RELATIONSHIPS")
    print("="*80)
    print(f"{'Child Table':<20} {'Child Col':<20} {'Parent Table':<20} {'Parent Col':<20} {'Constraint'}")
    print("-"*100)
    
    rows = cursor.fetchall()
    if not rows:
        print("No direct FK relationships found between main sales tables")
        print("Relationships may be through common keys like order_key, id, etc.")
    
    for row in rows:
        print(f"{row.ChildTable:<20} {row.ChildColumn:<20} {row.ParentTable:<20} {row.ParentColumn:<20} {row.FK_Name}")
    
    cursor.close()

def check_order_keys(conn):
    """Check if order_key is the linking column"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("ORDER KEY / COMMON LINK ANALYSIS")
    print("="*80)
    
    # Check order_key distribution
    for table in ['Order_Detail', 'Dine_In_Order', 'OrderKot', 'CustomerPOS']:
        try:
            cursor.execute(f"""
                SELECT 
                    COUNT(DISTINCT order_key) as unique_keys,
                    MIN(order_key) as min_key,
                    MAX(order_key) as max_key,
                    COUNT(*) as total_rows
                FROM [{table}]
                WHERE order_key IS NOT NULL
            """)
            row = cursor.fetchone()
            if row and row.total_rows:
                print(f"\n{table}:")
                print(f"  Total rows: {row.total_rows:,}")
                print(f"  Unique order_key values: {row.unique_keys:,}")
                print(f"  Min order_key: {row.min_key}")
                print(f"  Max order_key: {row.max_key}")
                
                if row.unique_keys < row.total_rows * 0.8:
                    print(f"  NOTE: order_key not unique - many-to-many or line items")
                else:
                    print(f"  NOTE: order_key likely unique per order/transaction")
        except Exception as e:
            print(f"\n{table}: ERROR - {e}")
    
    cursor.close()

def get_latest_transactions(conn):
    """Get the most recent orders"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("MOST RECENT TRANSACTIONS")
    print("="*80)
    
    # Try different date columns
    date_cols = {
        'Order_Detail': 'date',
        'Dine_In_Order': 'order_date',
        'OrderKot': 'date',
    }
    
    for table, date_col in date_cols.items():
        try:
            cursor.execute(f"""
                SELECT TOP 5 [{date_col}], *
                FROM [{table}]
                ORDER BY [{date_col}] DESC
            """)
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            
            if rows and rows[0][0]:
                print(f"\nLatest 5 records from {table} (by {date_col}):")
                # Show relevant columns only
                relevant = [i for i, c in enumerate(cols) if any(kw in c.lower() for kw in ['id', 'order', 'date', 'time', 'amount', 'total', 'name', 'qty', 'price'])]
                for row in rows:
                    vals = []
                    for i in relevant[:8]:
                        v = row[i]
                        if v is None:
                            vals.append("NULL")
                        else:
                            s = str(v)
                            vals.append(s[:20] if len(s) > 20 else s.ljust(20))
                    print("  " + " | ".join(vals))
        except Exception as e:
            print(f"\n{table}: {e}")
    
    cursor.close()

def main():
    print("\n" + "="*80)
    print("DETAILED SALES SCHEMA ANALYSIS")
    print("="*80)
    
    conn = None
    try:
        conn = connect()
        print("\n[OK] Connected\n")
        
        # Show key sales table columns
        key_tables = ['Order_Detail', 'Dine_In_Order', 'OrderKot', 'CustomerPOS', 'OrderMaster']
        for table in key_tables:
            try:
                show_table_columns(conn, table)
            except:
                pass
        
        find_revenue_columns(conn)
        find_common_keys(conn)
        check_order_keys(conn)
        get_latest_transactions(conn)
        
        print("\n" + "="*80)
        print("DONE")
        print("="*80)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
