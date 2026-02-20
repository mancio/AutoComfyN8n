import sqlite3
import json
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get workflow details
cur.execute('SELECT id, name, active, nodes, connections FROM workflow_entity WHERE id = ?', ['comfyui-integration-workflow'])
row = cur.fetchone()

if row:
    print(f'Workflow ID: {row[0]}')
    print(f'Name: {row[1]}')
    print(f'Active: {row[2]}')
    
    if row[3]:
        nodes = json.loads(row[3])
        print(f'\nNodes ({len(nodes)}):')
        for node in nodes:
            print(f"  - {node.get('name')} (type: {node.get('type')})")
    
    if row[4]:
        connections = json.loads(row[4])
        print(f'\nConnections: {connections}')
else:
    print('Workflow not found')

conn.close()
