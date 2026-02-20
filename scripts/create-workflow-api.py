#!/usr/bin/env python3
import json
import urllib.request
import base64
import sys

prompt = sys.argv[1] if len(sys.argv) > 1 else "a beautiful sunset over mountains"
auth = base64.b64encode(b'admin:admin123').decode()
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json'
}

# Create workflow via API
workflow_data = {
    "name": "Test ComfyUI Integration",
    "nodes": [
        {
            "id": "webhook",
            "name": "Webhook", 
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "parameters": {
                "path": "test-comfy",
                "httpMethod": "POST",
                "responseMode": "onReceived"
            }
        },
        {
            "id": "http",
            "name": "Call ComfyUI",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.1,
            "position": [500, 300],
            "parameters": {
                "url": "http://comfyui:8188/prompt",
                "method": "POST",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "client_id", "value": "n8n-webhook"},
                        {"name": "prompt", "value": "={{ {\"1\": {\"inputs\": {\"text\": $json.prompt || \"a sunset\"}, \"class_type\": \"CLIPTextEncode(prompt)\"}} | JSON.stringify() }}"}
                    ]
                }
            }
        }
    ],
    "connections": {
        "Webhook": {
            "main": [[{"node": "Call ComfyUI", "type": "main", "index": 0}]]
        }
    },
    "active": True
}

# POST to create workflow
req = urllib.request.Request(
    'http://localhost:5678/api/v1/workflows',
    data=json.dumps(workflow_data).encode(),
    headers=headers,
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        workflow_id = result.get('id')
        print(f"✓ Created workflow: {workflow_id}")
        print(f"✓ Send requests to: http://localhost:5678/webhook/test-comfy")
except Exception as e:
    print(f"Error creating workflow: {e}")
    sys.exit(1)

# Test the webhook
print("\nTesting webhook...")
test_body = json.dumps({"prompt": prompt}).encode()
test_headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(
    'http://localhost:5678/webhook/test-comfy',
    data=test_body,
    headers=test_headers,
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✓ Webhook response: {resp.read().decode()}")
except Exception as e:
    print(f"✗ Webhook error: {e}")
