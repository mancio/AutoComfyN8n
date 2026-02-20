import sqlite3
import json
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Check webhook_entity table
print("Webhooks registered:\n")
cur.execute('SELECT id, nodeId, workflowId FROM webhook_entity LIMIT 10')
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f'  Webhook ID: {row[0]}, Node: {row[1]}, Workflow: {row[2]}')
else:
    print('  (no webhooks registered)')

# Get the webhook node details from our workflow
print("\nWorkflow nodes:")
cur.execute('SELECT nodes FROM workflow_entity WHERE id = ?', ['comfyui-integration-workflow'])
nodes_row = cur.fetchone()
if nodes_row:
    nodes = json.loads(nodes_row[0])
    for node in nodes:
        if node.get('type') == 'n8n-nodes-base.webhook':
            print(f'\nWebhook node details:')
            print(json.dumps(node, indent=2))

conn.close()
