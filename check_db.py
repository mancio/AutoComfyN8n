import sqlite3
from pathlib import Path

p = Path('n8n_data/database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Check all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()
print('All tables:')
for t in tables:
    print(f'  {t[0]}')

# Check if workflow_history exists
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='workflow_history'")
if cur.fetchone()[0] > 0:
    cur.execute('SELECT * FROM workflow_history LIMIT 1')
    cols = [desc[0] for desc in cur.description]
    print(f'\nworkflow_history columns: {cols}')

conn.close()
