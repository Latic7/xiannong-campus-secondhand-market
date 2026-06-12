"""Check MySQL database schema vs code models and SQL schema file.
Redirect output to file to avoid GBK encoding issues."""
import sys, os
from pathlib import Path

# Load .env
os.chdir(str(Path(__file__).resolve().parent))
from dotenv import load_dotenv
load_dotenv(Path(".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}", file=sys.stderr)

# Parse MySQL connection params
# mysql+pymysql://user:pass@host:port/db?charset=utf8mb4
import re
m = re.match(r'mysql\+pymysql://(.+?):(.+?)@(.+?):(\d+)/(.+?)(\?|$)', DATABASE_URL)
user, password, host, port, dbname = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5)

import pymysql
conn = pymysql.connect(host=host, user=user, password=password, database=dbname, port=port)
cursor = conn.cursor()

# Get all tables
cursor.execute("SHOW TABLES")
tables = [r[0] for r in cursor.fetchall()]
print(f"\nTables in DB ({len(tables)}): {tables}")

# Check each table's columns
for table in sorted(tables):
    cursor.execute(f"DESCRIBE `{table}`")
    cols = cursor.fetchall()
    print(f"\n--- {table} ({len(cols)} columns) ---")
    for c in cols:
        print(f"  {c[0]:25s} {c[1]:30s} null={c[2]} default={c[4]}")

conn.close()
