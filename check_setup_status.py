import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Check user details
print("=== Users ===")
cur.execute("SELECT id, email FROM user LIMIT 5")
for row in cur.fetchall():
    print(f"  ID: {row[0][:8]}... Email: {row[1]}")

# Check setup status
print("\n=== Setup Status ===")
cur.execute("SELECT key, value FROM settings WHERE key LIKE 'userManagement%'")
for row in cur.fetchall():
    print(f"  {row[0]} = {row[1]}")

conn.close()
