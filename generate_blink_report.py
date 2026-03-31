#!/usr/bin/env python3
"""
Generate Blink Sales Report for M. Mushtaq
Creates reports with and without 'Blinkco order' filter and calculates percentages
"""

import pandas as pd
import sqlite3
from datetime import datetime

# Mock data generation for testing (since we don't have actual database)
def create_mock_data():
    """Create mock sales data for testing"""
    data = []
    
    # Mock employees and shops
    employees = [
        "M. Mushtaq", "A. Khan", "S. Ahmed", "R. Ali", "T. Hussain",
        "Online/Unassigned", "System Generated"
    ]
    
    shops = [
        (2, "Khadda Main Branch"),
        (3, "Festival"), 
        (4, "Rahat Commercial"),
        (6, "Tower"),
        (8, "North Nazimabad"),
        (10, "Malir"),
        (14, "Festival 2")
    ]
    
    # Generate mock sales data
    import random
    from datetime import timedelta
    
    start_date = datetime(2026, 1, 25)
    end_date = datetime(2026, 2, 25)  # Updated to match new query range
    
    current_date = start_date
    sale_id = 1
    
    while current_date <= end_date:
        for shop_id, shop_name in shops:
            for emp_name in employees:
                # Generate 1-5 transactions per day per employee per shop
                num_transactions = random.randint(0, 5)
                
                for _ in range(num_transactions):
                    # Randomly decide if this is a Blinkco order
                    is_blinkco = random.choice([True, False])
                    external_ref_type = "Blinkco order" if is_blinkco else "POS Sale"
                    
                    # Generate sale amounts
                    candela_sale = round(random.uniform(500, 5000), 2)
                    indoge_sale = round(random.uniform(100, 2000), 2) if is_blinkco else 0
                    
                    data.append({
                        'sale_id': sale_id,
                        'employee_name': emp_name,
                        'shop_name': shop_name,
                        'sale_date': current_date.strftime('%Y-%m-%d'),
                        'external_ref_type': external_ref_type,
                        'shop_id': shop_id,
                        'candela_sale': candela_sale,
                        'indoge_sale': indoge_sale
                    })
                    sale_id += 1
        
        current_date += timedelta(days=1)
    
    return data

def setup_database():
    """Setup SQLite database with mock data"""
    conn = sqlite3.connect(':memory:')  # In-memory database for testing
    
    # Create tables
    conn.execute('''
        CREATE TABLE tblSales (
            sale_id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            shop_id INTEGER,
            sale_date TEXT,
            external_ref_type TEXT,
            Nt_amount REAL,
            external_ref_id TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE tblDefShopEmployees (
            shop_employee_id INTEGER PRIMARY KEY,
            field_name TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE tblDefShops (
            shop_id INTEGER PRIMARY KEY,
            shop_name TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE tblInitialRawBlinkOrder (
            BlinkOrderId TEXT PRIMARY KEY,
            OrderJson TEXT
        )
    ''')
    
    # Insert mock data
    mock_data = create_mock_data()
    
    # Insert employees
    employees = set()
    for row in mock_data:
        employees.add(row['employee_name'])
    
    for i, emp in enumerate(employees, 1):
        conn.execute("INSERT INTO tblDefShopEmployees VALUES (?, ?)", (i, emp))
    
    # Insert shops
    shops = set()
    for row in mock_data:
        shops.add((row['shop_id'], row['shop_name']))
    
    for shop_id, shop_name in shops:
        conn.execute("INSERT INTO tblDefShops VALUES (?, ?)", (shop_id, shop_name))
    
    # Insert sales
    for row in mock_data:
        conn.execute('''
            INSERT INTO tblSales (sale_id, employee_id, shop_id, sale_date, external_ref_type, Nt_amount, external_ref_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['sale_id'], 1, row['shop_id'], row['sale_date'], row['external_ref_type'], 
              row['candela_sale'], f"blink_{row['sale_id']}" if row['external_ref_type'] == 'Blinkco order' else None))
    
    # Insert blink orders
    for row in mock_data:
        if row['external_ref_type'] == 'Blinkco order':
            order_json = f'{{"total_price":"{row["indoge_sale"]}", "other_field":"value"}}'
            conn.execute("INSERT INTO tblInitialRawBlinkOrder VALUES (?, ?)", 
                        (f"blink_{row['sale_id']}", order_json))
    
    conn.commit()
    return conn

def execute_query(conn, include_blinkco_filter=False):
    """Execute the main query with or without Blinkco order filter"""
    
    # Base query without Blinkco filter
    base_query = """
    WITH RawBlinkSales AS (
        SELECT 
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            sh.shop_name,
            s.sale_id,
            s.Nt_amount AS candela_sale,
            -- Manual string extraction for "total_price" from JSON (SQLite compatible)
            CASE 
                WHEN INSTR(rb.OrderJson, '"total_price":"') > 0 THEN
                    CAST(SUBSTR(
                        rb.OrderJson, 
                        INSTR(rb.OrderJson, '"total_price":"') + 15, 
                        INSTR(SUBSTR(rb.OrderJson, INSTR(rb.OrderJson, '"total_price":"') + 15), '"') - 1
                    ) AS REAL)
                ELSE 0 
            END AS indoge_sale
        FROM tblSales s
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
        LEFT JOIN tblInitialRawBlinkOrder rb ON s.external_ref_id = rb.BlinkOrderId
        WHERE 
            -- Date Range
            s.sale_date BETWEEN '2026-01-25' AND '2026-02-25'
            -- Allowed Branches
            AND s.shop_id IN (2, 3, 4, 6, 8, 10, 14)
    """
    
    # Add Blinkco filter if requested
    if include_blinkco_filter:
        base_query += "        AND s.external_ref_type = 'Blinkco order'\n"
    
    base_query += """
    )
    SELECT 
        employee_name,
        shop_name,
        COUNT(sale_id) AS total_transactions,
        
        -- RAW TOTALS
        SUM(candela_sale) AS Total_POS_Sales,
        SUM(indoge_sale) AS Total_Blink_Sales,

        -- COMMISSION ON EVERYTHING
        SUM(candela_sale) * (2.0 / 100) AS POS_Commission,
        SUM(indoge_sale) * (2.0 / 100) AS Blink_Commission

    FROM RawBlinkSales
    GROUP BY 
        employee_name,
        shop_name
    ORDER BY 
        Total_POS_Sales DESC;
    """
    
    return pd.read_sql_query(base_query, conn)

def calculate_percentages(df_without_filter, df_with_filter):
    """Calculate percentages comparing with and without Blinkco filter"""
    
    # Create a key for merging
    df_without_filter['key'] = df_without_filter['employee_name'] + '_' + df_without_filter['shop_name']
    df_with_filter['key'] = df_with_filter['employee_name'] + '_' + df_with_filter['shop_name']
    
    # Merge dataframes
    merged = pd.merge(
        df_without_filter[['key', 'Total_POS_Sales', 'Total_Blink_Sales']],
        df_with_filter[['key', 'Total_POS_Sales', 'Total_Blink_Sales']],
        on='key',
        suffixes=('_without', '_with'),
        how='outer'
    ).fillna(0)
    
    # Calculate percentages
    merged['POS_Sales_Percentage'] = (merged['Total_POS_Sales_with'] / merged['Total_POS_Sales_without'] * 100).round(2)
    merged['Blink_Sales_Percentage'] = (merged['Total_Blink_Sales_with'] / merged['Total_Blink_Sales_without'] * 100).round(2)
    
    return merged

def generate_report():
    """Generate the complete report"""
    
    print("Setting up database with mock data...")
    conn = setup_database()
    
    print("Executing query without 'Blinkco order' filter...")
    df_without = execute_query(conn, include_blinkco_filter=False)
    
    print("Executing query with 'Blinkco order' filter...")
    df_with = execute_query(conn, include_blinkco_filter=True)
    
    print("Calculating percentages...")
    percentages = calculate_percentages(df_without, df_with)
    
    # Generate report for ALL employees
    report = f"""
# Blink Sales Report for All Employees
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Date Range:** 2026-01-25 to 2026-02-25
**Commission Rate:** 2.0%

## Summary

### Without 'Blinkco order' Filter
Total transactions across all branches: {df_without['total_transactions'].sum()}

### With 'Blinkco order' Filter  
Total transactions across all branches: {df_with['total_transactions'].sum()}

## All Employees Performance Analysis

"""
    
    # Group by employee and calculate totals
    employee_summary = percentages.copy()
    employee_summary['employee_name'] = employee_summary['key'].str.split('_').str[0]
    employee_summary['shop_name'] = employee_summary['key'].str.split('_').str[1:].str.join(' ')
    
    # Calculate employee-level totals
    employee_totals = employee_summary.groupby('employee_name').agg({
        'Total_POS_Sales_without': 'sum',
        'Total_Blink_Sales_without': 'sum',
        'Total_POS_Sales_with': 'sum',
        'Total_Blink_Sales_with': 'sum'
    }).reset_index()
    
    # Calculate overall percentages for each employee
    employee_totals['Overall_POS_Percentage'] = (employee_totals['Total_POS_Sales_with'] / employee_totals['Total_POS_Sales_without'] * 100).round(2)
    employee_totals['Overall_Blink_Percentage'] = (employee_totals['Total_Blink_Sales_with'] / employee_totals['Total_Blink_Sales_without'] * 100).round(2)
    
    # Sort by total POS sales
    employee_totals = employee_totals.sort_values('Total_POS_Sales_without', ascending=False)
    
    for _, row in employee_totals.iterrows():
        employee_name = row['employee_name']
        pos_pct = row['Overall_POS_Percentage']
        blink_pct = row['Overall_Blink_Percentage']
        
        report += f"""
### {employee_name}

- **Overall POS Sales Percentage:** {pos_pct}% (of total POS sales)
- **Overall Blink Sales Percentage:** {blink_pct}% (of total Blink sales)
"""
    
    # Add detailed tables
    report += """
## Detailed Data Tables

### Without 'Blinkco order' Filter
"""
    report += df_without.to_markdown(index=False)
    
    report += """
### With 'Blinkco order' Filter
"""
    report += df_with.to_markdown(index=False)
    
    report += """
### Percentage Analysis
"""
    report += percentages.to_markdown(index=False)
    
    return report, df_without, df_with, percentages

def save_report(report: str, df_without: pd.DataFrame, df_with: pd.DataFrame, percentages: pd.DataFrame):
    """Save report to files"""
    
    # Save markdown report
    with open('blink_sales_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save data to Excel
    with pd.ExcelWriter('blink_sales_report.xlsx', engine='openpyxl') as writer:
        df_without.to_excel(writer, sheet_name='Without_Blinkco_Filter', index=False)
        df_with.to_excel(writer, sheet_name='With_Blinkco_Filter', index=False)
        percentages.to_excel(writer, sheet_name='Percentages', index=False)
    
    print("Report saved to:")
    print("- blink_sales_report.md")
    print("- blink_sales_report.xlsx")

if __name__ == "__main__":
    print("Generating Blink Sales Report...")
    report, df_without, df_with, percentages = generate_report()
    
    print("\n" + "="*50)
    print("REPORT SUMMARY")
    print("="*50)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    save_report(report, df_without, df_with, percentages)
    
    print("\nReport generation completed successfully!")
