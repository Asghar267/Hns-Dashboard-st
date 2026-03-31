import pyodbc

def list_tables(conn_str, label):
    conn = pyodbc.connect(conn_str, timeout=5)
    cur = conn.cursor()
    cur.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    rows = cur.fetchall()
    print(f"\n{label} ({len(rows)} tables)")
    for s, t in rows:
        print(f"{s}.{t}")

# Candelahns
list_tables(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=103.86.55.183,2001;"
    "DATABASE=Candelahns;"
    "UID=ReadOnlyUser;"
    "PWD=902729@Rafy;"
    "Encrypt=no;TrustServerCertificate=yes;MARS_Connection=Yes;",
    "Candelahns"
)

# KDS_DB (local)
list_tables(
    "DRIVER={SQL Server};"
    "SERVER=localhost;"
    "DATABASE=KDS_DB;"
    "Trusted_Connection=yes;"
    "MARS_Connection=Yes;",
    "KDS_DB"
)
