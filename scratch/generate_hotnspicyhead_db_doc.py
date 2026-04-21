import json
import os
from datetime import datetime
from decimal import Decimal

import pyodbc

SERVER = "103.86.55.34,50908"
DATABASE = "HOTNSPICYHEAD"
USER = os.environ.get("HOTNS_DB_USER", "sa")
PASSWORD = os.environ.get("HOTNS_DB_PASSWORD")

OUTPUT_DIR = os.path.join("docs", "hotnspicyhead")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USER};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

if not PASSWORD:
    raise RuntimeError(
        "Set HOTNS_DB_PASSWORD in environment before running this script."
    )


def qident(name: str) -> str:
    return "[" + name.replace("]", "]]" ) + "]"


def json_safe(value):
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    return value


conn = pyodbc.connect(CONN_STR)
conn.timeout = 120
cur = conn.cursor()

cur.execute(
    """
    SELECT t.TABLE_SCHEMA, t.TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES t
    WHERE t.TABLE_TYPE = 'BASE TABLE'
    ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME;
    """
)
tables = [{"schema": r[0], "table": r[1]} for r in cur.fetchall()]

cur.execute(
    """
    SELECT
      s.name AS schema_name,
      t.name AS table_name,
      SUM(p.rows) AS row_count
    FROM sys.tables t
    JOIN sys.schemas s ON s.schema_id = t.schema_id
    JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0,1)
    GROUP BY s.name, t.name
    ORDER BY s.name, t.name;
    """
)
row_counts = {(r[0], r[1]): int(r[2] or 0) for r in cur.fetchall()}

cur.execute(
    """
    SELECT
      c.TABLE_SCHEMA,
      c.TABLE_NAME,
      c.ORDINAL_POSITION,
      c.COLUMN_NAME,
      c.DATA_TYPE,
      c.CHARACTER_MAXIMUM_LENGTH,
      c.NUMERIC_PRECISION,
      c.NUMERIC_SCALE,
      c.IS_NULLABLE,
      c.COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS c
    ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION;
    """
)
columns = []
for r in cur.fetchall():
    columns.append(
        {
            "schema": r[0],
            "table": r[1],
            "ordinal": int(r[2]),
            "column": r[3],
            "data_type": r[4],
            "max_length": r[5],
            "precision": r[6],
            "scale": r[7],
            "is_nullable": r[8],
            "default": r[9],
        }
    )

cur.execute(
    """
    SELECT
      tc.TABLE_SCHEMA,
      tc.TABLE_NAME,
      tc.CONSTRAINT_NAME,
      kcu.COLUMN_NAME,
      kcu.ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
      ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
     AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
     AND tc.TABLE_NAME = kcu.TABLE_NAME
    WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    ORDER BY tc.TABLE_SCHEMA, tc.TABLE_NAME, tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION;
    """
)
primary_keys = []
for r in cur.fetchall():
    primary_keys.append(
        {
            "schema": r[0],
            "table": r[1],
            "constraint": r[2],
            "column": r[3],
            "ordinal": int(r[4]),
        }
    )

cur.execute(
    """
    SELECT
      fk.name AS fk_name,
      sch_parent.name AS parent_schema,
      tab_parent.name AS parent_table,
      col_parent.name AS parent_column,
      sch_ref.name AS referenced_schema,
      tab_ref.name AS referenced_table,
      col_ref.name AS referenced_column,
      fkc.constraint_column_id AS column_ordinal
    FROM sys.foreign_keys fk
    JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
    JOIN sys.tables tab_parent ON fk.parent_object_id = tab_parent.object_id
    JOIN sys.schemas sch_parent ON tab_parent.schema_id = sch_parent.schema_id
    JOIN sys.columns col_parent
      ON col_parent.object_id = tab_parent.object_id
     AND col_parent.column_id = fkc.parent_column_id
    JOIN sys.tables tab_ref ON fk.referenced_object_id = tab_ref.object_id
    JOIN sys.schemas sch_ref ON tab_ref.schema_id = sch_ref.schema_id
    JOIN sys.columns col_ref
      ON col_ref.object_id = tab_ref.object_id
     AND col_ref.column_id = fkc.referenced_column_id
    ORDER BY sch_parent.name, tab_parent.name, fk.name, fkc.constraint_column_id;
    """
)
foreign_keys = []
for r in cur.fetchall():
    foreign_keys.append(
        {
            "fk_name": r[0],
            "parent_schema": r[1],
            "parent_table": r[2],
            "parent_column": r[3],
            "referenced_schema": r[4],
            "referenced_table": r[5],
            "referenced_column": r[6],
            "ordinal": int(r[7]),
        }
    )

sample_data = {}
for t in tables:
    schema = t["schema"]
    table = t["table"]

    table_cols = [c["column"] for c in columns if c["schema"] == schema and c["table"] == table]
    if not table_cols:
        continue

    pk_cols = [
        p["column"]
        for p in sorted(
            [x for x in primary_keys if x["schema"] == schema and x["table"] == table],
            key=lambda x: x["ordinal"],
        )
    ]

    order_clause = ", ".join(qident(c) for c in pk_cols) if pk_cols else None
    select_sql = f"SELECT TOP 3 * FROM {qident(schema)}.{qident(table)}"
    if order_clause:
        select_sql += f" ORDER BY {order_clause}"

    try:
        c2 = conn.cursor()
        c2.execute(select_sql)
        col_names = [desc[0] for desc in c2.description]
        rows = c2.fetchall()
        sample_rows = []
        for row in rows:
            sample_rows.append({col_names[i]: json_safe(row[i]) for i in range(len(col_names))})
        sample_data[f"{schema}.{table}"] = sample_rows
        c2.close()
    except Exception as e:
        sample_data[f"{schema}.{table}"] = [{"error": str(e)}]

# write csv files
import csv

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

overview_rows = []
for t in tables:
    key = (t["schema"], t["table"])
    overview_rows.append(
        {
            "schema": t["schema"],
            "table": t["table"],
            "row_count": row_counts.get(key, 0),
            "column_count": len([c for c in columns if c["schema"] == t["schema"] and c["table"] == t["table"]]),
            "pk_columns": ", ".join(
                [
                    p["column"]
                    for p in sorted(
                        [x for x in primary_keys if x["schema"] == t["schema"] and x["table"] == t["table"]],
                        key=lambda x: x["ordinal"],
                    )
                ]
            ),
        }
    )

write_csv(
    os.path.join(OUTPUT_DIR, "tables_overview.csv"),
    overview_rows,
    ["schema", "table", "row_count", "column_count", "pk_columns"],
)
write_csv(
    os.path.join(OUTPUT_DIR, "columns_catalog.csv"),
    columns,
    [
        "schema",
        "table",
        "ordinal",
        "column",
        "data_type",
        "max_length",
        "precision",
        "scale",
        "is_nullable",
        "default",
    ],
)
write_csv(
    os.path.join(OUTPUT_DIR, "primary_keys.csv"),
    primary_keys,
    ["schema", "table", "constraint", "column", "ordinal"],
)
write_csv(
    os.path.join(OUTPUT_DIR, "foreign_keys.csv"),
    foreign_keys,
    [
        "fk_name",
        "parent_schema",
        "parent_table",
        "parent_column",
        "referenced_schema",
        "referenced_table",
        "referenced_column",
        "ordinal",
    ],
)

with open(os.path.join(OUTPUT_DIR, "sample_data_top3.json"), "w", encoding="utf-8") as f:
    json.dump(sample_data, f, ensure_ascii=True, indent=2)

# build markdown document
captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

total_tables = len(tables)
total_columns = len(columns)
total_rows = sum(row_counts.values())

top_tables = sorted(overview_rows, key=lambda x: x["row_count"], reverse=True)[:25]

md_lines = []
md_lines.append("# HOTNSPICYHEAD Database Documentation")
md_lines.append("")
md_lines.append(f"Generated at: {captured_at}")
md_lines.append("")
md_lines.append("## Connection Profile")
md_lines.append("")
md_lines.append("- Server: `103.86.55.34,50908`")
md_lines.append("- Database: `HOTNSPICYHEAD`")
md_lines.append("- Auth: SQL Login (`sa`) ")
md_lines.append("- Encryption: `Encrypt=True`, `TrustServerCertificate=True`")
md_lines.append("")
md_lines.append("## High-Level Summary")
md_lines.append("")
md_lines.append(f"- Total tables: **{total_tables}**")
md_lines.append(f"- Total columns: **{total_columns}**")
md_lines.append(f"- Approximate total rows across tables: **{total_rows}**")
md_lines.append(f"- Primary key entries: **{len(primary_keys)}**")
md_lines.append(f"- Foreign key mappings: **{len(foreign_keys)}**")
md_lines.append("")
md_lines.append("## Largest Tables (Top 25 by row count)")
md_lines.append("")
md_lines.append("| Schema | Table | Rows | Columns | PK |")
md_lines.append("|---|---|---:|---:|---|")
for r in top_tables:
    md_lines.append(
        f"| {r['schema']} | {r['table']} | {r['row_count']} | {r['column_count']} | {r['pk_columns'] or '-'} |"
    )
md_lines.append("")

md_lines.append("## Relation Map (Foreign Keys)")
md_lines.append("")
if foreign_keys:
    md_lines.append("| FK Name | From (Child) | To (Parent) |")
    md_lines.append("|---|---|---|")
    for fk in foreign_keys:
        child = f"{fk['parent_schema']}.{fk['parent_table']}.{fk['parent_column']}"
        parent = f"{fk['referenced_schema']}.{fk['referenced_table']}.{fk['referenced_column']}"
        md_lines.append(f"| {fk['fk_name']} | {child} | {parent} |")
else:
    md_lines.append("No explicit foreign keys found in metadata.")
md_lines.append("")

md_lines.append("## Per-Table Catalog")
md_lines.append("")
for t in tables:
    schema = t["schema"]
    table = t["table"]
    key = (schema, table)
    table_cols = [c for c in columns if c["schema"] == schema and c["table"] == table]
    table_pks = [p for p in primary_keys if p["schema"] == schema and p["table"] == table]
    table_fks = [f for f in foreign_keys if f["parent_schema"] == schema and f["parent_table"] == table]

    md_lines.append(f"### {schema}.{table}")
    md_lines.append("")
    md_lines.append(f"- Row count: **{row_counts.get(key, 0)}**")
    md_lines.append(f"- Columns: **{len(table_cols)}**")
    md_lines.append(
        "- Primary key: "
        + (", ".join([x["column"] for x in sorted(table_pks, key=lambda x: x["ordinal"])]) if table_pks else "None")
    )
    md_lines.append(f"- Outgoing foreign keys: **{len(table_fks)}**")
    md_lines.append("")

    md_lines.append("| # | Column | Type | Nullable | Default |")
    md_lines.append("|---:|---|---|---|---|")
    for c in table_cols:
        type_str = c["data_type"]
        if c["max_length"] is not None and c["max_length"] > 0:
            type_str += f"({c['max_length']})"
        elif c["precision"] is not None:
            scale = c["scale"] if c["scale"] is not None else 0
            type_str += f"({c['precision']},{scale})"
        default_val = str(c["default"]).replace("|", "\\|") if c["default"] is not None else ""
        md_lines.append(
            f"| {c['ordinal']} | {c['column']} | {type_str} | {c['is_nullable']} | {default_val} |"
        )
    md_lines.append("")

    if table_fks:
        md_lines.append("Foreign key links:")
        for fk in table_fks:
            md_lines.append(
                f"- `{fk['parent_column']}` -> `{fk['referenced_schema']}.{fk['referenced_table']}.{fk['referenced_column']}` ({fk['fk_name']})"
            )
        md_lines.append("")

    samples = sample_data.get(f"{schema}.{table}", [])
    md_lines.append("Sample data (`TOP 3`):")
    if samples and "error" not in samples[0]:
        md_lines.append("")
        md_lines.append("```json")
        md_lines.append(json.dumps(samples, ensure_ascii=True, indent=2))
        md_lines.append("```")
    else:
        md_lines.append("")
        md_lines.append("```text")
        md_lines.append(samples[0].get("error", "No rows") if samples else "No rows")
        md_lines.append("```")
    md_lines.append("")

md_path = os.path.join(OUTPUT_DIR, "HOTNSPICYHEAD_DATABASE_DOCUMENTATION.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

conn.close()

print(f"Generated: {md_path}")
print(f"Tables: {total_tables}, Columns: {total_columns}, FK rows: {len(foreign_keys)}")
