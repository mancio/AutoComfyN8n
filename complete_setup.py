import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Update the setup completion flag
cur.execute("""
    UPDATE settings 
    SET value = 'true' 
    WHERE key = 'userManagement.isInstanceOwnerSetUp'
""")
conn.commit()

# Verify
cur.execute("SELECT key, value FROM settings WHERE key = 'userManagement.isInstanceOwnerSetUp'")
row = cur.fetchone()
if row:
    print(f"✓ Updated: {row[0]} = {row[1]}")
else:
    print("✗ Setting not found")

conn.close()
