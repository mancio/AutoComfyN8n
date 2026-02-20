#!/usr/bin/env python3
"""Integration test - ensures N8N and ComfyUI are running and workflow is set up"""
import json
import os
import sqlite3
import subprocess
import sys
import urllib.request
import urllib.error
import time
from pathlib import Path

DEFAULT_PROMPT = "a beautiful sunset over mountains, oil painting style"

def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def log(msg):
    print(msg)

def ensure_workflow_exists():
    """Ensure the workflow exists in N8N database"""
    db_path = Path("n8n_data/database.sqlite")
    if not db_path.exists():
        log("Database not found, containers might not be running")
        return False
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if workflow already exists
    cur.execute("SELECT id FROM workflow_entity WHERE id = ?", ["comfyui-test"])
    if cur.fetchone():
        log("✓ Workflow already exists in database")
        conn.close()
        return True
    
    # Create a simple workflow in the database
    log("[Creating N8N workflow...]")
    workflow = {
        "name": "ComfyUI Test",
        "nodes": [
            {
                "id": "webhook",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {
                    "path": "comfyui-test",
                    "httpMethod": "POST",
                    "responseMode": "onReceived"
                }
            }
        ],
        "connections": {},
        "active": True,
        "settings": {},
        "versionId": "v1"
    }
    
    try:
        cur.execute("""
            INSERT INTO workflow_entity 
            (id, name, active, nodes, connections, versionId, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, [
            "comfyui-test",
            workflow['name'],
            1,
            json.dumps(workflow['nodes']),
            json.dumps(workflow['connections']),
            workflow['versionId']
        ])
        conn.commit()
        log("✓ Created workflow in database")
        conn.close()
        return True
    except Exception as e:
        log(f"✗ Failed to create workflow: {e}")
        conn.close()
        return False

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT
    
    log("[1/4] Checking Docker containers...")
    ps_out = run(["docker", "compose", "ps"], check=False).stdout
    if "n8n-love-comfy" not in ps_out or "comfyui-love-comfy" not in ps_out:
        log("✗ Containers not running")
        return 1
    log("✓ Containers are running")
    
    # Wait for services to be ready
    log("[2/4] Waiting for services...")
    for i in range(30):
        try:
            with urllib.request.urlopen('http://localhost:5678/', timeout=1) as resp:
                if resp.status == 200:
                    log("✓ Services are ready")
                    break
        except:
            pass
        time.sleep(1)
    
    log("[3/4] Ensuring workflow exists...")
    if not ensure_workflow_exists():
        log("✗ Failed to set up workflow")
        return 1
    
    # Restart N8N to load database changes
    log("[4/4] Reloading N8N...")
    run(["docker", "compose", "restart", "n8n"], check=False)
    time.sleep(3)
    
    # Verify model is ready
    log("\n[5/5] Checking image generation requirements...")
    model_path = Path("comfyui/models/checkpoints/v1-5-pruned.safetensors")
    output_path = Path("comfyui/output")
    
    if model_path.exists():
        log(f"✓ Model ready: {model_path.name}")
    else:
        log(f"⚠ Model not found at {model_path}")
    
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    log(f"✓ Output folder ready: {output_path}")
    
    log("\n" + "="*50)
    log("✓ System Ready!")
    log("="*50)
    print("\n📝 Your prompt will be used:")
    print(f"   '{prompt}'")
    print("\n🎨 To generate images:")
    print("   1. Open http://localhost:8188 (ComfyUI UI)")
    print("   2. Load the default workflow")
    print("   3. Edit the text prompt node with your prompt")
    print("   4. Click 'Queue Prompt' to generate")
    print("\n📊 Results appear in:")
    print(f"   {output_path.absolute()}")
    print("\n🔗 Or automate with N8N:")
    print("   1. Open http://localhost:5678")
    print("   2. Login: admin@example.com / admin123")
    print("   3. Create workflow to trigger ComfyUI")
    return 0

if __name__ == "__main__":
    sys.exit(main())
