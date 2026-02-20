import sqlite3
import json
from pathlib import Path
import uuid

p = Path('n8n_data/database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Get the workflow
cur.execute('SELECT id, name, nodes, connections FROM workflow_entity WHERE id = ?', ['comfyui-test'])
row = cur.fetchone()

if row:
    workflow_id, name, nodes_json, connections_json = row
    
    # Create a version ID
    version_id = str(uuid.uuid4())
    
    # Insert workflow_history
    cur.execute('''
        INSERT INTO workflow_history 
        (versionId, workflowId, authors, createdAt, updatedAt, nodes, connections, name, autosaved, description)
        VALUES (?, ?, ?, datetime('now'), datetime('now'), ?, ?, ?, ?, ?)
    ''', [
        version_id,
        workflow_id,
        json.dumps([]),  # authors
        nodes_json,
        connections_json,
        name,
        0,  # autosaved
        None  # description
    ])
    
    # Update workflow_entity with activeVersionId
    cur.execute('UPDATE workflow_entity SET activeVersionId = ?, versionId = ? WHERE id = ?', 
               [version_id, version_id, workflow_id])
    
    conn.commit()
    print(f'✓ Created workflow_history version: {version_id}')
    print(f'✓ Updated workflow_entity activeVersionId')
else:
    print('✗ Workflow not found')

conn.close()
