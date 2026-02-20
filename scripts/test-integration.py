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

def ensure_containers_running():
    """Ensure Docker containers are running, start them if not"""
    log("Checking Docker containers...")
    
    try:
        result = run(["docker", "compose", "ps", "--services", "--filter", "status=running"], check=False)
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Check if both required services are running
        if 'n8n' in running_services and 'comfyui' in running_services:
            log("✓ Containers are already running\n")
            return True
    except Exception as e:
        log(f"⚠ Could not check container status: {e}")
    
    # Start containers if not running
    log("Starting Docker containers...")
    try:
        result = run(["docker", "compose", "up", "-d"], check=False)
        if result.returncode == 0:
            log("✓ Containers started successfully\n")
            return True
        else:
            log(f"✗ Failed to start containers: {result.stderr}")
            return False
    except Exception as e:
        log(f"✗ Error starting containers: {e}")
        return False

def ensure_workflow_exists():
    """Ensure the workflow exists in N8N database"""
    db_path = Path("n8n_data/database.sqlite")
    if not db_path.exists():
        log("Database not found, containers might not be running")
        return False
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if workflow already exists
    cur.execute("SELECT id FROM workflow_entity WHERE name = ?", ["Test ComfyUI Integration"])
    existing = cur.fetchone()
    if existing:
        log("✓ Workflow already exists in database")
        conn.close()
        return True
    
    # Load workflow from file
    workflow_file = Path("workflows/n8n_test_comfyui_integration.json")
    if not workflow_file.exists():
        log(f"⚠ Workflow file not found: {workflow_file}")
        conn.close()
        return False
    
    log("[Importing N8N workflow...]")
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        # Generate unique ID
        workflow_id = f"workflow-{int(time.time())}"
        
        cur.execute("""
            INSERT INTO workflow_entity 
            (id, name, active, nodes, connections, versionId, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, [
            workflow_id,
            workflow.get('name', 'ComfyUI Workflow'),
            1,
            json.dumps(workflow.get('nodes', [])),
            json.dumps(workflow.get('connections', {})),
            'v1'
        ])
        conn.commit()
        log(f"✓ Imported workflow: {workflow.get('name', 'ComfyUI Workflow')}")
        conn.close()
        return True
    except Exception as e:
        log(f"✗ Failed to import workflow: {e}")
        conn.close()
        return False

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT
    
    # Ensure containers are running
    if not ensure_containers_running():
        log("✗ Failed to start containers")
        return 1
    
    log("[1/5] Checking Docker containers...")
    ps_out = run(["docker", "compose", "ps"], check=False).stdout
    if "n8n" not in ps_out or "comfyui" not in ps_out:
        log("✗ Containers not running")
        return 1
    log("✓ Containers are running")
    
    # Wait for services to be ready
    log("[2/5] Waiting for services...")
    for i in range(30):
        try:
            with urllib.request.urlopen('http://localhost:5678/', timeout=1) as resp:
                if resp.status == 200:
                    log("✓ Services are ready")
                    break
        except:
            pass
        time.sleep(1)
    
    log("[3/5] Ensuring workflow exists...")
    if not ensure_workflow_exists():
        log("✗ Failed to set up workflow")
        return 1
    
    # Restart N8N to load database changes
    log("[4/5] Reloading N8N...")
    run(["docker", "compose", "restart", "n8n"], check=False)
    time.sleep(3)
    
    # Verify model is ready
    log("\n[5/5] Checking image generation setup...")
    model_path = Path("comfyui/models/checkpoints/v1-5-pruned.safetensors")
    output_path = Path("comfyui/output")
    
    if not model_path.exists():
        log(f"⚠ Model not found: {model_path}")
        return 1
    log(f"✓ Model ready: {model_path.name}")
    
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    log(f"✓ Output folder ready")
    
    # List any existing images
    images = list(output_path.glob("*.png"))
    if images:
        log(f"\n✓ Found {len(images)} generated image(s):")
        for img in sorted(images, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            log(f"  ✓ {img.name}")
    else:
        log("\n📝 No images generated yet")
    
    log("\n" + "="*60)
    log("✓ System Ready!")
    log("="*60)
    print(f"\nYour prompt: '{prompt}'")
    print("\n� To execute the workflow:")
    print("   1. Open http://localhost:5678")
    print("   2. Click on 'ComfyUI Test' workflow")
    print("   3. Click the Play/Execute button to run")
    print("\n🎨 To generate images:")
    print("   1. Open http://localhost:8188 (ComfyUI UI)")
    print("   2. Use the default workflow")
    print("   3. Edit text prompt to your custom text")
    print("   4. Click 'Queue Prompt' to generate")
    print("\n📁 Images will be saved to:")
    print(f"   {output_path.absolute()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
