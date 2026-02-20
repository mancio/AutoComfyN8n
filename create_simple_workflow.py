import sqlite3
import json
from pathlib import Path

p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

# Create a simpler workflow without webhook - just manual trigger
workflow = {
    "name": "ComfyUI Simple Test",
    "nodes": [
        {
            "parameters": {
                "url": "http://comfyui:8188/system_stats",
                "authentication": "none",
                "method": "GET"
            },
            "id": "http_req",
            "name": "Check ComfyUI",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.1,
            "position": [250, 300]
        }
    ],
    "connections": {},
    "active": False,
    "settings": {},
    "versionId": "test-v1",
    "meta": {"instanceId": "default"},
    "id": "comfyui-simple-test"
}

# Insert workflow
cur.execute("""
    INSERT INTO workflow_entity 
    (id, name, active, nodes, connections, versionId, createdAt, updatedAt)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
""", [
    workflow['id'],
    workflow['name'],
    0,  # not active
    json.dumps(workflow['nodes']),
    json.dumps(workflow['connections']),
    workflow['versionId']
])
conn.commit()

print(f"✓ Created simple test workflow")
conn.close()
