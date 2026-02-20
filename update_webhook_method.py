import sqlite3
import json
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get the current workflow
cur.execute('SELECT nodes, connections FROM workflow_entity WHERE id = ?', ['comfyui-integration-workflow'])
row = cur.fetchone()

nodes = json.loads(row[0])

# Update webhook node to accept POST
for node in nodes:
    if node.get('type') == 'n8n-nodes-base.webhook':
        if 'parameters' not in node:
            node['parameters'] = {}
        node['parameters']['httpMethod'] = 'POST'
        print(f"Updated webhook node:")
        print(json.dumps(node['parameters'], indent=2))

# Update database
cur.execute('UPDATE workflow_entity SET nodes = ? WHERE id = ?', 
            [json.dumps(nodes), 'comfyui-integration-workflow'])
conn.commit()
print("\n✓ Workflow updated")

conn.close()
