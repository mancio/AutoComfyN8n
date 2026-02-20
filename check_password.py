import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get user details
cur.execute("SELECT id, email, password FROM user LIMIT 5")
for row in cur.fetchall():
    print(f"ID: {row[0][:8]}...")
    print(f"Email: {row[1]}")
    print(f"Password hash: {row[2][:20] if row[2] else 'NOT SET'}...")

conn.close()
