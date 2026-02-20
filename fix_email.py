import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Update email to valid format
cur.execute("""
    UPDATE user 
    SET email = 'admin@example.com', firstName = 'Admin', lastName = 'User'
    WHERE roleSlug = 'global:owner'
""")
conn.commit()

# Verify
cur.execute("SELECT id, email, firstName, lastName FROM user WHERE roleSlug = 'global:owner'")
row = cur.fetchone()
if row:
    print(f"✓ Updated user:")
    print(f"  Email: {row[1]}")
    print(f"  Name: {row[2]} {row[3]}")

conn.close()
