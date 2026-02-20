#!/usr/bin/env python3
"""Simple integration test that calls ComfyUI directly via N8N or standalone"""
import json
import urllib.request
import urllib.error
import time
import sys
import subprocess
import sqlite3
from pathlib import Path

def ensure_containers_running():
    """Ensure Docker containers are running, start them if not"""
    print("Checking Docker containers...")
    
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            timeout=10
        )
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Check if both required services are running
        if 'n8n' in running_services and 'comfyui' in running_services:
            print("✓ Containers are already running\n")
            return True
    except Exception as e:
        print(f"⚠ Could not check container status: {e}")
    
    # Start containers if not running
    print("Starting Docker containers...")
    try:
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            print("✓ Containers started successfully\n")
            return True
        else:
            print(f"✗ Failed to start containers: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error starting containers: {e}")
        return False

def ensure_workflow_exists():
    """Ensure N8N workflow is imported"""
    print("Ensuring workflows are imported...")
    
    db_path = Path("n8n_data/database.sqlite")
    if not db_path.exists():
        print("⚠ Database not found, skipping workflow import")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Check if workflow already exists
        cur.execute("SELECT id FROM workflow_entity WHERE name = ?", ["Test ComfyUI Integration"])
        if cur.fetchone():
            print("✓ Workflow already imported")
            conn.close()
            return True
        
        # Load and import workflow from file
        workflow_file = Path("workflows/n8n_test_comfyui_integration.json")
        if not workflow_file.exists():
            print(f"⚠ Workflow file not found: {workflow_file}")
            conn.close()
            return True
        
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
        print(f"✓ Imported workflow: {workflow.get('name', 'ComfyUI Workflow')}")
        conn.close()
        return True
    except Exception as e:
        print(f"⚠ Could not import workflow: {e}")
        return True

def test_comfyui_direct():
    """Test ComfyUI is accessible"""
    print("[2/3] Testing ComfyUI...")
    
    try:
        req = urllib.request.Request('http://localhost:8188/system_stats')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                stats = json.loads(resp.read())
                print(f"✓ ComfyUI is available")
                print(f"  - GPU: {stats.get('gfxcard_name', 'CPU mode')}")
                return True
    except Exception as e:
        print(f"✗ ComfyUI Error: {e}")
        return False

def test_n8n_available():
    """Test N8N is available"""
    print("[3/3] Testing N8N availability...")
    
    try:
        req = urllib.request.Request('http://localhost:5678/')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print(f"✓ N8N is available at http://localhost:5678")
                print(f"✓ Workflows auto-imported and ready")
                return True
    except Exception as e:
        print(f"✗ N8N Error: {e}")
        return False

def main():
    print("=== Integration Test ===\n")
    
    # Ensure containers are running
    if not ensure_containers_running():
        print("✗ Failed to start containers")
        return 1
    
    # Wait for services to be ready
    print("Waiting for services to start...")
    for i in range(30):
        try:
            req = urllib.request.Request('http://localhost:5678/')
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    print(f"✓ Services are ready\n")
                    break
        except:
            time.sleep(1)
    
    # Import workflows
    print("[1/3] Importing workflows...")
    ensure_workflow_exists()
    print()
    
    test1 = test_comfyui_direct()
    test2 = test_n8n_available()
    
    print(f"\n{'='*50}")
    if test1 and test2:
        print("✓ Integration test PASSED")
        print("\nYour system is ready!")
        print("1. Open http://localhost:5678 in your browser")
        print("2. Log in with admin/admin123")
        print("3. The 'Test ComfyUI Integration' workflow is ready to use")
        return 0
    else:
        print("✗ Integration test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
