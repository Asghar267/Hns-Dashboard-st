"""
Sales Summary & Latest Activity Query
Calculate actual revenue and find most recent sales
"""
import pyodbc
import pandas as pd
from datetime import datetime

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

def calculate_sales_revenue(conn):
    """Calculate total sales revenue from different tables"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES REVENUE CALCULATION")
    print("="*80)
    
    # Try to calculate from Order_Detail (line items)
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as item_count,
                SUM(ISNULL(qty, 0) * ISNULL(price, 0)) as gross_amount,
                SUM(ISNULL(PriceBeforeDiscount, 0)) as before_discount,
                SUM(ISNULL(Discount, 0)) as total_discount,
                SUM(ISNULL(tax, 0)) as total_tax,
                MIN(date) as first_sale,
                MAX(date) as last_sale
            FROM Order_Detail
            WHERE price IS NOT NULL AND qty IS NOT NULL
        """)
        row = cursor.fetchone()
        if row:
            print(f"\n[Order_Detail] Line Item Revenue:")
            print(f"  Line items sold: {row.item_count:,}")
            print(f"  Gross (qty * price): {row.gross_amount:,.2f}" if row.gross_amount else "  Gross: NULL")
            print(f"  Before discount: {row.before_discount:,.2f}" if row.before_discount else "  Before discount: NULL")
            print(f"  Total discount: {row.total_discount:,.2f}" if row.total_discount else "  Total discount: NULL")
            print(f"  Total tax: {row.total_tax:,.2f}" if row.total_tax else "  Total tax: NULL")
            print(f"  Date range: {row.first_sale} to {row.last_sale}")
    except Exception as e:
        print(f"\nOrder_Detail error: {e}")
    
    # Try from Dine_In_Order (order header with amount)
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as order_count,
                SUM(ISNULL(amount, 0)) as total_amount,
                SUM(ISNULL(discount, 0)) as total_discount,
                MIN(order_date) as first_order,
                MAX(order_date) as last_order
            FROM Dine_In_Order
            WHERE is_delete = 0 OR is_delete IS NULL
        """)
        row = cursor.fetchone()
        if row:
            print(f"\n[Dine_In_Order] Order Header Revenue:")
            print(f"  Total orders: {row.order_count:,}")
            print(f"  Total amount: {row.total_amount:,.2f}" if row.total_amount else "  Total amount: NULL")
            print(f"  Total discount: {row.total_discount:,.2f}" if row.total_discount else "  Total discount: NULL")
            print(f"  Date range: {row.first_order} to {row.last_order}")
    except Exception as e:
        print(f"\nDine_In_Order error: {e}")
    
    # Try OrderKot (kitchen orders)
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as kot_count,
                COUNT(DISTINCT OrderKey) as unique_orders,
                SUM(ISNULL(Qty, 0)) as total_qty,
                MIN(OrderKey) as min_order,
                MAX(OrderKey) as max_order
            FROM OrderKot
        """)
        row = cursor.fetchone()
        if row:
            print(f"\n[OrderKot] Kitchen Orders:")
            print(f"  KOT lines: {row.kot_count:,}")
            print(f"  Unique orders: {row.unique_orders:,}")
            print(f"  Total quantity: {row.total_qty:,.0f}" if row.total_qty else "  Total qty: NULL")
            print(f"  Order key range: {row.min_order} to {row.max_order}")
    except Exception as e:
        print(f"\nOrderKot error: {e}")
    
    cursor.close()

def order_types_breakdown(conn):
    """Breakdown by order type/service channel"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES BY ORDER TYPE / CHANNEL")
    print("="*80)
    
    # From Dine_In_Order
    try:
        cursor.execute("""
            SELECT 
                ISNULL(order_type, 'Unknown') as order_type,
                COUNT(*) as order_count,
                SUM(ISNULL(amount, 0)) as total_amount
            FROM Dine_In_Order
            GROUP BY order_type
            ORDER BY total_amount DESC
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"\n[Dine_In_Order] By Order Type:")
            print(f"{'Type':<20} {'Orders':>12} {'Amount':>15}")
            print("-"*50)
            total = 0
            for row in rows:
                print(f"{row.order_type:<20} {row.order_count:>12,} {row.total_amount:>15,.2f}")
                total += row.total_amount
            print(f"{'TOTAL':<20} {'':<12} {total:>15,.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # From Order_Detail categories
    try:
        cursor.execute("""
            SELECT TOP 20
                ISNULL(category_name, 'Unknown') as category,
                COUNT(*) as item_count,
                SUM(ISNULL(qty, 0)) as total_qty,
                SUM(ISNULL(qty * price, 0)) as category_amount
            FROM Order_Detail
            WHERE price IS NOT NULL
            GROUP BY category_name
            ORDER BY category_amount DESC
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"\n[Order_Detail] By Category (Qty * Price):")
            print(f"{'Category':<25} {'Items':>10} {'Qty':>10} {'Amount':>15}")
            print("-"*65)
            total = 0
            for row in rows:
                print(f"{row.category:<25} {row.item_count:>10,} {row.total_qty:>10,.1f} {row.category_amount:>15,.2f}")
                total += row.category_amount
            print(f"{'TOTAL':<25} {'':<10} {'':<10} {total:>15,.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    cursor.close()

def latest_activity(conn):
    """Show the most recent sales activity"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("LATEST SALES ACTIVITY")
    print("="*80)
    
    try:
        cursor.execute("""
            SELECT TOP 10
                order_key,
                order_date,
                order_type,
                amount,
                discount,
                Status
            FROM Dine_In_Order
            WHERE order_date IS NOT NULL
            ORDER BY order_date DESC
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"\nMost Recent Dine_In_Order records:")
            print(f"{'OrderKey':<12} {'Date':<20} {'Type':<12} {'Amount':>12} {'Discount':>10} {'Status':<8}")
            print("-"*80)
            for row in rows:
                date_str = row.order_date.strftime('%Y-%m-%d %H:%M') if row.order_date else 'NULL'
                amt = f"{row.amount:,.2f}" if row.amount else "0.00"
                disc = f"{row.discount:,.2f}" if row.discount else "0.00"
                print(f"{str(row.order_key):<12} {date_str:<20} {str(row.order_type):<12} {amt:>12} {disc:>10} {str(row.Status):<8}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Show Order_Detail latest
    try:
        cursor.execute("""
            SELECT TOP 10
                od.order_key,
                od.date,
                od.category_name,
                od.item_name,
                od.qty,
                od.price,
                (od.qty * od.price) as line_total
            FROM Order_Detail od
            WHERE od.date IS NOT NULL
            ORDER BY od.date DESC
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"\nMost Recent Order_Detail line items:")
            print(f"{'OrderKey':<12} {'Date':<20} {'Category':<15} {'Item':<20} {'Qty':>8} {'Price':>10} {'Total':>12}")
            print("-"*95)
            for row in rows:
                date_str = row.date.strftime('%Y-%m-%d %H:%M') if row.date else 'NULL'
                total = row.qty * row.price if row.qty and row.price else 0
                print(f"{str(row.order_key):<12} {date_str:<20} {str(row.category_name):<15} {str(row.item_name):<20} {row.qty:>8.2f} {row.price:>10.2f} {total:>12.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    cursor.close()

def get_hourly_sales_pattern(conn):
    """Analyze sales by hour of day"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("SALES BY HOUR OF DAY (Order_Detail)")
    print("="*80)
    
    try:
        cursor.execute("""
            SELECT 
                DATEPART(hour, date) as hour_of_day,
                COUNT(*) as transactions,
                COUNT(DISTINCT order_key) as unique_orders,
                SUM(qty * price) as revenue
            FROM Order_Detail
            WHERE date IS NOT NULL AND price IS NOT NULL
            GROUP BY DATEPART(hour, date)
            ORDER BY hour_of_day
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"\n{'Hour':<6} {'Transactions':>12} {'Orders':>10} {'Revenue':>15}")
            print("-"*50)
            total_rev = 0
            for row in rows:
                rev = row.revenue or 0
                total_rev += rev
                print(f"{row.hour_of_day:02d}:00  {row.transactions:>12,} {row.unique_orders:>10,} {rev:>15,.2f}")
            print(f"{'TOTAL':<6} {'':<12} {'':<10} {total_rev:>15,.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    cursor.close()

def main():
    print("\n" + "="*80)
    print("SALES SUMMARY REPORT - HOTNSPICYHEAD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    conn = None
    try:
        conn = connect()
        print("\n[OK] Connected to database\n")
        
        calculate_sales_revenue(conn)
        order_types_breakdown(conn)
        latest_activity(conn)
        get_hourly_sales_pattern(conn)
        
        print("\n" + "="*80)
        print("REPORT COMPLETE")
        print("="*80)
        print("\nKEY FINDINGS:")
        print("1. Sales data stops around 2021-07-01 (old data)")
        print("2. Main sales tables: Order_Detail (236K lines), Dine_In_Order (82K orders)")
        print("3. Order channels: DELIVERY (81,964), TAKE AWAY (1)")
        print("4. Product categories: ROLLS, FASTFOOD, BAR B Q, TANDOOR, HANDI, RICE (top 6)")
        print("5. Order flow: CustomerPOS -> Dine_In_Order -> Order_Detail -> OrderKot")
        print("6. Peak hours: 20:00-21:00 (highest revenue)")
        print("7. Total calculated revenue: ~PKR 357 Million (from line items)")
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
