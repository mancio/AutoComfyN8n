import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get owner user
cur.execute("SELECT id FROM user WHERE roleSlug = 'global:owner' LIMIT 1")
user_id = cur.fetchone()[0]

# Update email 
cur.execute("UPDATE user SET email = ? WHERE id = ?", ('admin@localhost', user_id))
conn.commit()
print(f'✓ Updated user {user_id} with email admin@localhost')

# Verify
cur.execute('SELECT id, email, roleSlug FROM user')
for row in cur.fetchall():
    print(f'  User: {row[0][:8]}... Email: {row[1]} Role: {row[2]}')

conn.close()
