import sqlite3
from pathlib import Path

p = Path(r"C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite")
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT id, email, roleSlug FROM user")
print(list(cur.fetchall()))
cur.execute("SELECT id, name, type, creatorId FROM project")
print(list(cur.fetchall()))
