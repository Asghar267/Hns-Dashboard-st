"""
OPTIMIZED Database Analysis for HOTNSPICYHEAD
Uses bulk queries for faster schema extraction
"""
import pyodbc
import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

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
    """Connect to database"""
    return pyodbc.connect(CONN_STR)


def fetch_all_tables(conn):
    """Get all user tables"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    tables = [(row.TABLE_SCHEMA, row.TABLE_NAME) for row in cursor.fetchall()]
    cursor.close()
    return tables


def fetch_all_columns(conn):
    """Bulk fetch all columns for all tables"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMNPROPERTY(object_id(QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)), COLUMN_NAME, 'IsIdentity') as IsIdentity
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """)
    
    columns = defaultdict(list)
    for row in cursor.fetchall():
        col = {
            'name': row.COLUMN_NAME,
            'data_type': row.DATA_TYPE,
            'max_length': row.CHARACTER_MAXIMUM_LENGTH,
            'precision': row.NUMERIC_PRECISION,
            'scale': row.NUMERIC_SCALE,
            'nullable': row.IS_NULLABLE == 'YES',
            'default': row.COLUMN_DEFAULT,
            'is_identity': bool(row.IsIdentity),
            'is_primary_key': False  # will fill later
        }
        key = f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}"
        columns[key].append(col)
    cursor.close()
    return columns


def fetch_all_primary_keys(conn):
    """Bulk fetch all primary keys"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            k.TABLE_SCHEMA,
            k.TABLE_NAME,
            k.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k ON 
            k.CONSTRAINT_SCHEMA = t.CONSTRAINT_SCHEMA AND
            k.CONSTRAINT_NAME = t.CONSTRAINT_NAME AND
            k.TABLE_NAME = t.TABLE_NAME
        WHERE t.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY k.TABLE_SCHEMA, k.TABLE_NAME, k.ORDINAL_POSITION
    """)
    
    pks = defaultdict(list)
    for row in cursor.fetchall():
        key = f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}"
        pks[key].append(row.COLUMN_NAME)
    cursor.close()
    return pks


def fetch_all_foreign_keys(conn):
    """Bulk fetch all foreign key relationships"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s1.name AS schema_name,
            t1.name AS table_name,
            c1.name AS parent_column,
            s2.name AS ref_schema,
            t2.name AS referenced_table,
            c2.name AS referenced_column,
            fk.name AS constraint_name
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.tables t1 ON fk.parent_object_id = t1.object_id
        JOIN sys.schemas s1 ON t1.schema_id = s1.schema_id
        JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
        JOIN sys.tables t2 ON fk.referenced_object_id = t2.object_id
        JOIN sys.schemas s2 ON t2.schema_id = s2.schema_id
        JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
        ORDER BY s1.name, t1.name
    """)
    
    fks = defaultdict(list)
    for row in cursor.fetchall():
        key = f"{row.schema_name}.{row.table_name}"
        fk = {
            'constraint_name': row.constraint_name,
            'parent_column': row.parent_column,
            'referenced_schema': row.ref_schema,
            'referenced_table': row.referenced_table,
            'referenced_column': row.referenced_column
        }
        fks[key].append(fk)
    cursor.close()
    return fks


def fetch_fast_row_counts(conn, tables):
    """Get row counts for all tables at once using sys.dm_db_partition_stats (FAST)"""
    cursor = conn.cursor()
    # This query returns row counts for ALL tables in the database in one shot
    query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            SUM(p.row_count) AS row_count
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.dm_db_partition_stats p ON t.object_id = p.object_id
        WHERE p.index_id IN (0, 1)  -- heap or clustered index
        GROUP BY s.name, t.name
    """
    
    cursor.execute(query)
    counts = {}
    for row in cursor.fetchall():
        key = f"{row.schema_name}.{row.table_name}"
        counts[key] = row.row_count
    cursor.close()
    
    # Fill missing tables with 0 (shouldn't be missing but just in case)
    result = {}
    for schema, table in tables:
        key = f"{schema}.{table}"
        result[key] = counts.get(key, 0)
    return result


def fetch_sample_data(conn, tables, limit=3):
    """Fetch sample data for top N largest tables only"""
    sample_data = {}
    cursor = conn.cursor()
    
    # Sort by row count, take top 10
    sorted_tables = sorted(tables, key=lambda t: t[2] if len(t) > 2 else 0, reverse=True)[:10]
    
    for schema, table, row_count in sorted_tables:
        if row_count == 0:
            continue
        try:
            query = f"SELECT TOP {limit} * FROM [{schema}].[{table}]"
            df = pd.read_sql(query, conn)
            sample_data[f"{schema}.{table}"] = df
        except Exception as e:
            print(f"  [WARN] Could not fetch sample for {schema}.{table}: {e}")
    
    cursor.close()
    return sample_data


def generate_documentation(tables_data):
    """Generate Markdown documentation"""
    print("\n" + "="*100)
    print("GENERATING DOCUMENTATION")
    print("="*100)
    
    doc = []
    doc.append("# Database Documentation: HOTNSPICYHEAD")
    doc.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.append(f"**Server:** 103.86.55.34,50908")
    doc.append(f"**Database:** HOTNSPICYHEAD")
    doc.append("")
    
    total_tables = len(tables_data)
    total_rows = sum(t['row_count'] for t in tables_data.values())
    total_fks = sum(len(t['foreign_keys']) for t in tables_data.values())
    
    doc.append("## Summary")
    doc.append(f"- **Total Tables:** {total_tables}")
    doc.append(f"- **Total Rows:** {total_rows:,}")
    doc.append(f"- **Foreign Key Relationships:** {total_fks}")
    doc.append("")
    
    # Table of Contents
    doc.append("## Table of Contents")
    sorted_keys = sorted(tables_data.keys())
    for i, key in enumerate(sorted_keys, 1):
        t = tables_data[key]
        doc.append(f"{i}. [{key}](#{key.lower().replace('.', '-')})")
    doc.append("")
    
    # Detailed table docs
    doc.append("## Table Details")
    doc.append("")
    
    for key in sorted_keys:
        t = tables_data[key]
        doc.append(f"### {key}")
        doc.append("")
        doc.append(f"**Rows:** {t['row_count']:,}  |  ")
        doc.append(f"**Columns:** {len(t['columns'])}  |  ")
        doc.append(f"**Foreign Keys:** {len(t['foreign_keys'])}")
        doc.append("")
        
        # Columns table
        doc.append("#### Columns")
        doc.append("")
        doc.append("| Column Name | Data Type | Nullable | Identity | PK |")
        doc.append("|-------------|-----------|----------|----------|----|")
        for col in t['columns']:
            dtype = col['data_type']
            if col['max_length']:
                dtype += f"({col['max_length']})"
            elif col.get('precision'):
                dtype += f"({col['precision']},{col['scale']})"
            nullable = "Yes" if col['nullable'] else "No"
            identity = "Yes" if col['is_identity'] else "No"
            pk_marker = "(PK)" if col['is_primary_key'] else ""
            doc.append(f"| {col['name']} | {dtype} | {nullable} | {identity} | {pk_marker} |")
        doc.append("")
        
        # Primary Keys
        if t['primary_keys']:
            doc.append("#### Primary Key")
            doc.append(f"`{', '.join(t['primary_keys'])}`")
            doc.append("")
        
        # Foreign Keys
        if t['foreign_keys']:
            doc.append("#### Foreign Keys")
            doc.append("")
            doc.append("| Constraint | Local Column | Referenced Table | Referenced Column |")
            doc.append("|------------|--------------|------------------|-------------------|")
            for fk in t['foreign_keys']:
                ref_table = f"{fk['referenced_schema']}.{fk['referenced_table']}"
                doc.append(f"| {fk['constraint_name']} | {fk['parent_column']} | {ref_table} | {fk['referenced_column']} |")
            doc.append("")
        
        # Sample Data
        if key in t.get('sample_data', {}):
            doc.append("#### Sample Data (First 3 rows)")
            doc.append("")
            df = t['sample_data'][key]
            if not df.empty:
                # Truncate long values
                df_display = df.copy()
                for col in df_display.columns:
                    if df_display[col].dtype == 'object':
                        df_display[col] = df_display[col].astype(str).str.slice(0, 50)
                doc.append(df_display.to_markdown(index=False))
                doc.append("")
        
        doc.append("---")
        doc.append("")
    
    # Relationships section
    all_fks = []
    for key, t in tables_data.items():
        for fk in t['foreign_keys']:
            all_fks.append({
                'from': key,
                'from_col': fk['parent_column'],
                'to': f"{fk['referenced_schema']}.{fk['referenced_table']}",
                'to_col': fk['referenced_column'],
                'constraint': fk['constraint_name']
            })
    
    if all_fks:
        doc.append("## Foreign Key Relationships")
        doc.append("")
        doc.append("| From Table | From Column | To Table | To Column | Constraint |")
        doc.append("|------------|-------------|----------|-----------|------------|")
        for fk in all_fks:
            doc.append(f"| {fk['from']} | {fk['from_col']} | {fk['to']} | {fk['to_col']} | {fk['constraint']} |")
        doc.append("")
    
    return "\n".join(doc)


def main():
    print("\n" + "="*100)
    print("OPTIMIZED HOTNSPICYHEAD DATABASE ANALYSIS")
    print("="*100)
    
    conn = None
    try:
        print("\n[1/6] Connecting to database...")
        conn = connect()
        print("  [OK] Connected")
        
        print("\n[2/6] Fetching table list...")
        tables = fetch_all_tables(conn)
        print(f"  [OK] Found {len(tables)} tables")
        
        print("\n[3/6] Bulk fetching columns...")
        columns_data = fetch_all_columns(conn)
        print(f"  [OK] Columns for {len(columns_data)} tables")
        
        print("\n[4/6] Bulk fetching primary keys...")
        pk_data = fetch_all_primary_keys(conn)
        print(f"  [OK] PKs for {len(pk_data)} tables")
        
        print("\n[5/6] Bulk fetching foreign keys...")
        fk_data = fetch_all_foreign_keys(conn)
        print(f"  [OK] FKs for {len(fk_data)} tables")
        
        print("\n[6/6] Fetching fast row counts...")
        row_counts = fetch_fast_row_counts(conn, tables)
        print(f"  [OK] Row counts retrieved")
        
        # Build table data structure
        tables_data = {}
        for schema, table in tables:
            key = f"{schema}.{table}"
            t = {
                'schema': schema,
                'name': table,
                'columns': columns_data.get(key, []),
                'primary_keys': pk_data.get(key, []),
                'foreign_keys': fk_data.get(key, []),
                'row_count': row_counts.get(key, 0),
                'sample_data': {}
            }
            
            # Mark PK columns
            pk_cols = set(t['primary_keys'])
            for col in t['columns']:
                if col['name'] in pk_cols:
                    col['is_primary_key'] = True
            
            tables_data[key] = t
        
        # Fetch sample data for top 10 largest tables only (optional, comment out if too slow)
        print("\n[7/6] Fetching sample data for largest tables...")
        enriched_tables = [(t['schema'], t['name'], t['row_count']) for t in tables_data.values()]
        sample_data = fetch_sample_data(conn, enriched_tables, limit=3)
        for key, df in sample_data.items():
            if key in tables_data:
                tables_data[key]['sample_data'] = {key: df}
        
        # Generate docs
        markdown = generate_documentation(tables_data)
        
        with open("DATABASE_DOCUMENTATION.md", "w", encoding="utf-8") as f:
            f.write(markdown)
        print("\n  [OK] Markdown documentation saved to DATABASE_DOCUMENTATION.md")
        
        # Export JSON
        schema_export = {
            'database': 'HOTNSPICYHEAD',
            'generated_at': datetime.now().isoformat(),
            'statistics': {
                'total_tables': len(tables_data),
                'total_rows': sum(t['row_count'] for t in tables_data.values()),
                'total_relationships': sum(len(t['foreign_keys']) for t in tables_data.values())
            },
            'tables': tables_data
        }
        
        with open("database_schema.json", "w", encoding="utf-8") as f:
            json.dump(schema_export, f, indent=2, default=str)
        print("  [OK] JSON schema exported to database_schema.json")
        
        print("\n" + "="*100)
        print("ANALYSIS COMPLETE")
        print("="*100)
        print(f"\nTables: {len(tables_data)}")
        print(f"Total Rows: {sum(t['row_count'] for t in tables_data.values()):,}")
        print(f"Foreign Keys: {sum(len(t['foreign_keys']) for t in tables_data.values())}")
        print("\nGenerated files:")
        print("  1. DATABASE_DOCUMENTATION.md")
        print("  2. database_schema.json")
        print("")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
