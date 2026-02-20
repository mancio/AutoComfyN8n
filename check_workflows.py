import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Check workflow_entity table
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='workflow_entity'")
schema = cur.fetchone()
if schema:
    print('Workflow table schema:')
    print(schema[0])
else:
    print('No workflow_entity table found')

# List workflows
print('\nExisting workflows:')
cur.execute('SELECT id, name FROM workflow_entity LIMIT 10')
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f'  ID: {row[0]}, Name: {row[1]}')
else:
    print('  (no workflows)')

conn.close()
