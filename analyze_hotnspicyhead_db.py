"""
Comprehensive Database Analysis Tool for HOTNSPICYHEAD Database
Analyzes schema, relationships, data samples, and generates documentation
"""
import pyodbc
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json
from datetime import datetime

# Connection string for HOTNSPICYHEAD database
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


@dataclass
class ColumnInfo:
    """Represents column metadata"""
    name: str
    data_type: str
    max_length: Optional[int]
    precision: Optional[int]
    scale: Optional[int]
    nullable: bool
    default: Optional[str]
    is_identity: bool
    is_primary_key: bool = False


@dataclass
class TableInfo:
    """Represents table metadata"""
    name: str
    schema: str
    columns: List[ColumnInfo] = field(default_factory=list)
    row_count: int = 0
    indexes: List[Dict] = field(default_factory=list)
    foreign_keys: List[Dict] = field(default_factory=list)
    primary_key_columns: List[str] = field(default_factory=list)
    sample_data: Optional[pd.DataFrame] = None


class DatabaseAnalyzer:
    """Comprehensive database analyzer"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn: Optional[pyodbc.Connection] = None
        self.tables: Dict[str, TableInfo] = {}
        self.relationships: List[Dict] = []
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.conn.timeout = 60
            print(f"[OK] Connected to database successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
    
    def get_all_tables(self):
        """Fetch all user tables"""
        cursor = self.conn.cursor()
        query = """
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        cursor.execute(query)
        tables = cursor.fetchall()
        cursor.close()
        return tables
    
    def get_table_columns(self, schema: str, table: str) -> List[ColumnInfo]:
        """Get column information for a table"""
        cursor = self.conn.cursor()
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMNPROPERTY(object_id(QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)), COLUMN_NAME, 'IsIdentity') as IsIdentity
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        cursor.execute(query, (schema, table))
        columns = []
        for row in cursor.fetchall():
            col = ColumnInfo(
                name=row.COLUMN_NAME,
                data_type=row.DATA_TYPE,
                max_length=row.CHARACTER_MAXIMUM_LENGTH,
                precision=row.NUMERIC_PRECISION,
                scale=row.NUMERIC_SCALE,
                nullable=row.IS_NULLABLE == 'YES',
                default=row.COLUMN_DEFAULT,
                is_identity=bool(row.IsIdentity)
            )
            columns.append(col)
        cursor.close()
        return columns
    
    def get_primary_keys(self, schema: str, table: str) -> List[str]:
        """Get primary key columns for a table"""
        cursor = self.conn.cursor()
        query = """
        SELECT k.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k ON 
            k.TABLE_SCHEMA = t.TABLE_SCHEMA AND 
            k.TABLE_NAME = t.TABLE_NAME AND 
            k.CONSTRAINT_NAME = t.CONSTRAINT_NAME
        WHERE t.TABLE_SCHEMA = ? AND t.TABLE_NAME = ? AND t.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY k.ORDINAL_POSITION
        """
        cursor.execute(query, (schema, table))
        pk_columns = [row.COLUMN_NAME for row in cursor.fetchall()]
        cursor.close()
        return pk_columns
    
    def get_foreign_keys(self, schema: str, table: str) -> List[Dict]:
        """Get foreign key relationships for a table"""
        cursor = self.conn.cursor()
        query = """
        SELECT 
            fk.name AS FK_Name,
            tp.name AS ParentTable,
            cp.name AS ParentColumn,
            tr.name AS ReferencedTable,
            cr.name AS ReferencedColumn
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
        INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
        INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
        INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
        WHERE SCHEMA_NAME(fk.schema_id) = ? AND OBJECT_NAME(fk.parent_object_id) = ?
        """
        cursor.execute(query, (schema, table))
        fks = []
        for row in cursor.fetchall():
            fk = {
                'constraint_name': row.FK_Name,
                'parent_table': row.ParentTable,
                'parent_column': row.ParentColumn,
                'referenced_table': row.ReferencedTable,
                'referenced_column': row.ReferencedColumn
            }
            fks.append(fk)
        cursor.close()
        return fks
    
    def get_indexes(self, schema: str, table: str) -> List[Dict]:
        """Get indexes for a table"""
        cursor = self.conn.cursor()
        query = """
        SELECT 
            i.name AS IndexName,
            i.type_desc AS IndexType,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS Columns
        FROM sys.indexes i
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE SCHEMA_NAME(i.schema_id) = ? AND OBJECT_NAME(i.object_id) = ?
        GROUP BY i.name, i.type_desc
        ORDER BY i.type_desc, i.name
        """
        try:
            cursor.execute(query, (schema, table))
            indexes = []
            for row in cursor.fetchall():
                idx = {
                    'name': row.IndexName,
                    'type': row.IndexType,
                    'columns': row.Columns
                }
                indexes.append(idx)
            cursor.close()
            return indexes
        except Exception as e:
            print(f"  Warning: Could not fetch indexes for {schema}.{table}: {e}")
            return []
    
    def get_row_count(self, schema: str, table: str) -> int:
        """Get approximate row count for a table"""
        cursor = self.conn.cursor()
        query = f"SELECT COUNT(*) FROM [{schema}].[{table}]"
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f"  Warning: Could not count rows for {schema}.{table}: {e}")
            return 0
    
    def get_sample_data(self, schema: str, table: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """Fetch sample data from table"""
        try:
            query = f"SELECT TOP {limit} * FROM [{schema}].[{table}]"
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(f"  Warning: Could not fetch sample data for {schema}.{table}: {e}")
            return None
    
    def analyze_database(self):
        """Main analysis method"""
        print("\n" + "="*100)
        print("DATABASE ANALYSIS: HOTNSPICYHEAD")
        print("="*100)
        
        # Get all tables
        tables = self.get_all_tables()
        print(f"\nFound {len(tables)} tables\n")
        
        for schema_name, table_name in tables:
            print(f"Analyzing: [{schema_name}].[{table_name}]")
            
            table_info = TableInfo(name=table_name, schema=schema_name)
            
            # Get columns
            columns = self.get_table_columns(schema_name, table_name)
            table_info.columns = columns
            
            # Get primary keys
            pk_columns = self.get_primary_keys(schema_name, table_name)
            table_info.primary_key_columns = pk_columns
            for col in table_info.columns:
                if col.name in pk_columns:
                    col.is_primary_key = True
            
            # Get foreign keys
            fks = self.get_foreign_keys(schema_name, table_name)
            table_info.foreign_keys = fks
            
            # Get indexes
            indexes = self.get_indexes(schema_name, table_name)
            table_info.indexes = indexes
            
            # Get row count (with timeout protection)
            row_count = self.get_row_count(schema_name, table_name)
            table_info.row_count = row_count
            print(f"  Row count: {row_count:,}")
            
            # Get sample data
            sample_data = self.get_sample_data(schema_name, table_name, 3)
            if sample_data is not None:
                table_info.sample_data = sample_data
            
            self.tables[f"{schema_name}.{table_name}"] = table_info
            print(f"  [OK] Analysis complete\n")
        
        # Build relationship graph
        self._build_relationship_graph()
    
    def _build_relationship_graph(self):
        """Build relationship graph from foreign keys"""
        self.relationships = []
        for table_key, table_info in self.tables.items():
            for fk in table_info.foreign_keys:
                rel = {
                    'from_table': table_key,
                    'from_column': fk['parent_column'],
                    'to_table': f"{fk['referenced_schema'] if 'referenced_schema' in fk else table_info.schema}.{fk['referenced_table']}",
                    'to_column': fk['referenced_column'],
                    'constraint': fk['constraint_name']
                }
                self.relationships.append(rel)
    
    def generate_documentation(self) -> str:
        """Generate comprehensive documentation as markdown"""
        doc = []
        doc.append("# Database Documentation: HOTNSPICYHEAD")
        doc.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"**Server:** 103.86.55.34,50908")
        doc.append(f"**Database:** HOTNSPICYHEAD")
        doc.append("")
        
        # Summary statistics
        total_tables = len(self.tables)
        total_rows = sum(t.row_count for t in self.tables.values())
        total_relationships = len(self.relationships)
        
        doc.append("## Summary")
        doc.append(f"- **Total Tables:** {total_tables}")
        doc.append(f"- **Total Rows:** {total_rows:,}")
        doc.append(f"- **Foreign Key Relationships:** {total_relationships}")
        doc.append("")
        
        # Table of Contents
        doc.append("## Table of Contents")
        for i, (table_key, table_info) in enumerate(self.tables.items(), 1):
            doc.append(f"{i}. [{table_info.schema}.{table_info.name}](#{table_info.schema.lower()}-{table_info.name.lower()})")
        doc.append("")
        
        # Detailed table documentation
        doc.append("## Table Details")
        doc.append("")
        
        for table_key, table_info in sorted(self.tables.items()):
            doc.append(f"### {table_info.schema}.{table_info.name}")
            doc.append("")
            
            # Table info header
            doc.append(f"**Rows:** {table_info.row_count:,}  |  ")
            doc.append(f"**Columns:** {len(table_info.columns)}  |  ")
            doc.append(f"**Indexes:** {len(table_info.indexes)}  |  ")
            doc.append(f"**Foreign Keys:** {len(table_info.foreign_keys)}")
            doc.append("")
            
            # Column details table
            doc.append("#### Columns")
            doc.append("")
            doc.append("| Column Name | Data Type | Nullable | Default | Identity | Key |")
            doc.append("|------------|-----------|----------|---------|----------|-----|")
            
            for col in table_info.columns:
                dtype = col.data_type
                if col.max_length:
                    dtype += f"({col.max_length})"
                elif col.precision:
                    dtype += f"({col.precision},{col.scale})"
                
                nullable = "Yes" if col.nullable else "No"
                identity = "Yes" if col.is_identity else "No"
                pk_marker = "(PK)" if col.is_primary_key else ""
                
                default_str = col.default[:20] + "..." if col.default and len(str(col.default)) > 20 else str(col.default) if col.default else ""
                default_str = default_str.replace("\n", " ").replace("|", "/")
                
                doc.append(f"| {col.name} | {dtype} | {nullable} | {default_str} | {identity} | {pk_marker} |")
            
            doc.append("")
            
            # Primary Key section
            if table_info.primary_key_columns:
                doc.append("#### Primary Key")
                doc.append(f"`{', '.join(table_info.primary_key_columns)}`")
                doc.append("")
            
            # Foreign Keys section
            if table_info.foreign_keys:
                doc.append("#### Foreign Keys")
                doc.append("")
                doc.append("| Constraint | Local Column | Referenced Table | Referenced Column |")
                doc.append("|------------|--------------|------------------|-------------------|")
                for fk in table_info.foreign_keys:
                    ref_table = f"{table_info.schema}.{fk['referenced_table']}"
                    doc.append(f"| {fk['constraint_name']} | {fk['parent_column']} | {ref_table} | {fk['referenced_column']} |")
                doc.append("")
            
            # Indexes section
            if table_info.indexes:
                doc.append("#### Indexes")
                doc.append("")
                doc.append("| Index Name | Type | Columns |")
                doc.append("|------------|------|---------|")
                for idx in table_info.indexes:
                    doc.append(f"| {idx['name']} | {idx['type']} | {idx['columns']} |")
                doc.append("")
            
            # Sample Data section
            if table_info.sample_data is not None and not table_info.sample_data.empty:
                doc.append("#### Sample Data (First 3 rows)")
                doc.append("")
                sample_df = table_info.sample_data
                # Clean data for markdown
                sample_df_clean = sample_df.copy()
                for col in sample_df_clean.columns:
                    if sample_df_clean[col].dtype == 'object':
                        sample_df_clean[col] = sample_df_clean[col].astype(str).str.replace(r'\n', ' ', regex=True).str[:50]
                
                markdown_table = sample_df_clean.to_markdown(index=False)
                doc.append(markdown_table)
                doc.append("")
            
            doc.append("---")
            doc.append("")
        
        # Relationships visualization
        if self.relationships:
            doc.append("## Foreign Key Relationships")
            doc.append("")
            doc.append("| From Table | From Column | To Table | To Column | Constraint |")
            doc.append("|------------|-------------|----------|-----------|------------|")
            for rel in self.relationships:
                doc.append(f"| {rel['from_table']} | {rel['from_column']} | {rel['to_table']} | {rel['to_column']} | {rel['constraint']} |")
            doc.append("")
        
        # Schema summary by table
        doc.append("## Schema Summary")
        doc.append("")
        for table_key, table_info in sorted(self.tables.items()):
            doc.append(f"### {table_info.schema}.{table_info.name}")
            doc.append("")
            doc.append(f"- **Row Count:** {table_info.row_count:,}")
            doc.append(f"- **Columns:** {len(table_info.columns)}")
            col_names = [f"`{c.name}`" for c in table_info.columns]
            doc.append(f"- **All Columns:** {', '.join(col_names)}")
            doc.append("")
        
        return "\n".join(doc)
    
    def export_schema_json(self, filename: str = "database_schema.json"):
        """Export schema as JSON"""
        schema_data = {
            'database': 'HOTNSPICYHEAD',
            'generated_at': datetime.now().isoformat(),
            'statistics': {
                'total_tables': len(self.tables),
                'total_rows': sum(t.row_count for t in self.tables.values()),
                'total_relationships': len(self.relationships)
            },
            'tables': {}
        }
        
        for table_key, table_info in self.tables.items():
            schema_data['tables'][table_key] = {
                'schema': table_info.schema,
                'name': table_info.name,
                'row_count': table_info.row_count,
                'columns': [
                    {
                        'name': col.name,
                        'data_type': col.data_type,
                        'max_length': col.max_length,
                        'nullable': col.nullable,
                        'is_identity': col.is_identity,
                        'is_primary_key': col.is_primary_key,
                        'default': str(col.default) if col.default else None
                    }
                    for col in table_info.columns
                ],
                'primary_keys': table_info.primary_key_columns,
                'foreign_keys': table_info.foreign_keys,
                'indexes': table_info.indexes
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, default=str)
        print(f"\n[OK] Schema exported to {filename}")


def main():
    """Main execution"""
    print("\n" + "="*100)
    print("HOTNSPICYHEAD DATABASE ANALYSIS")
    print("="*100)
    
    analyzer = DatabaseAnalyzer(CONN_STR)
    
    if not analyzer.connect():
        print("\nPlease check:")
        print("1. SQL Server is running on 103.86.55.34:50908")
        print("2. Database HOTNSPICYHEAD exists")
        print("3. Credentials (sa/123) are correct")
        print("4. Firewall allows connection to port 50908")
        return
    
    try:
        analyzer.analyze_database()
        
        # Generate documentation
        print("\n" + "="*100)
        print("GENERATING DOCUMENTATION")
        print("="*100)
        
        markdown_doc = analyzer.generate_documentation()
        
        # Save to file
        with open("DATABASE_DOCUMENTATION.md", "w", encoding="utf-8") as f:
            f.write(markdown_doc)
        print("✓ Markdown documentation saved to DATABASE_DOCUMENTATION.md")
        
        # Export JSON schema
        analyzer.export_schema_json("database_schema.json")
        
        # Print summary
        print("\n" + "="*100)
        print("ANALYSIS COMPLETE")
        print("="*100)
        print(f"\nTables analyzed: {len(analyzer.tables)}")
        print(f"Total rows: {sum(t.row_count for t in analyzer.tables.values()):,}")
        print(f"Relationships: {len(analyzer.relationships)}")
        print("\nFiles generated:")
        print("  1. DATABASE_DOCUMENTATION.md - Comprehensive markdown documentation")
        print("  2. database_schema.json - Machine-readable schema JSON")
        print("\n")
        
        # Print first few lines of doc
        print("Preview of documentation:")
        print("-" * 80)
        preview_lines = markdown_doc.split('\n')[:50]
        print('\n'.join(preview_lines))
        print("...\n")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
