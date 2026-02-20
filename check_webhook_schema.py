import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get webhook_entity schema
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='webhook_entity'")
schema = cur.fetchone()
if schema:
    print('webhook_entity schema:')
    print(schema[0])

# Get first few rows
cur.execute('SELECT * FROM webhook_entity LIMIT 3')
rows = cur.fetchall()
print(f'\nFound {len(rows)} webhooks')
for row in rows:
    print(row)

conn.close()
