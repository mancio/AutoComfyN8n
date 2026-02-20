import sqlite3
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Update webhook to accept POST
cur.execute("""
    UPDATE webhook_entity 
    SET method = 'POST' 
    WHERE workflowId = 'comfyui-integration-workflow'
""")
conn.commit()

# Verify
cur.execute('SELECT webhookPath, method FROM webhook_entity WHERE workflowId = ?', ['comfyui-integration-workflow'])
row = cur.fetchone()
if row:
    print(f"✓ Updated webhook:")
    print(f"  Path: {row[0]}")
    print(f"  Method: {row[1]}")

conn.close()
