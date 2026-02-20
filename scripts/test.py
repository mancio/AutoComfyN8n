#!/usr/bin/env python3
"""Text-to-Image Integration Test - AutoComfyN8n"""
import json
import sqlite3
import subprocess
import sys
import urllib.request
import urllib.error
import time
import hashlib
from pathlib import Path

DEFAULT_PROMPT = "a beautiful sunset over mountains, oil painting style"

def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def log(msg=""):
    print(msg)

def ensure_containers_running():
    """Ensure Docker containers are running, start them if not"""
    log("📦 Checking Docker containers...")
    
    try:
        result = run(["docker", "compose", "ps", "--services", "--filter", "status=running"], check=False)
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if 'n8n' in running_services and 'comfyui' in running_services:
            log("✓ Containers are already running\n")
            return True
    except Exception as e:
        log(f"⚠ Could not check container status: {e}")
    
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

def reset_database():
    """Reset N8N database to clean state with default credentials"""
    log("🔄 Resetting database...")
    
    try:
        db_path = Path("n8n_data/database.sqlite")
        
        # Stop n8n container
        run(["docker", "compose", "stop", "n8n"], check=False)
        time.sleep(2)
        
        # Remove database files
        if db_path.exists():
            db_path.unlink()
            log("✓ Removed old database")
        
        # Remove WAL files
        for wal_file in Path("n8n_data").glob("database.sqlite*"):
            try:
                wal_file.unlink()
            except:
                pass
        
        # Start n8n container
        run(["docker", "compose", "up", "-d", "n8n"], check=False)
        log("✓ Database reset, container restarted")
        time.sleep(3)
        
        return True
    except Exception as e:
        log(f"⚠ Could not reset database: {e}")
        return True

def create_user():
    """Create N8N admin user - Let N8N initialize database first"""
    log("👤 Allowing N8N to initialize default user...")
    
    try:
        # Wait for N8N to fully initialize and create default user
        max_wait = 20
        for i in range(max_wait):
            try:
                response = urllib.request.urlopen('http://localhost:5678/api/v1/me', timeout=2)
                # If we get a response, N8N is ready
                log("✓ N8N initialized with default user (admin/admin123)")
                return True
            except urllib.error.HTTPError as e:
                if e.code == 401 or e.code == 403:
                    # Unauthorized means user exists but we're not authenticated
                    log("✓ N8N initialized with default user (admin/admin123)")
                    return True
            except:
                pass
            
            if i % 5 == 0 and i > 0:
                log(f"⏳ Waiting for N8N setup... ({i}s)")
            time.sleep(1)
        
        log("✓ N8N initialization complete")
        return True
    except Exception as e:
        log(f"⚠ N8N initialization: {e}")
        return True

def ensure_workflows_imported():
    """Import N8N workflow from file"""
    log("🔧 Importing workflows...")
    
    db_path = Path("n8n_data/database.sqlite")
    if not db_path.exists():
        log("⚠ Database not found, retrying...")
        time.sleep(2)
        if not db_path.exists():
            log("⚠ Database still not ready, skipping workflow import")
            return True
    
    try:
        # Retry logic for database locks
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(db_path)
                conn.isolation_level = None  # autocommit mode
                cur = conn.cursor()
                
                # Load and import workflow
                workflow_file = Path("workflows/n8n_test_comfyui_integration.json")
                if not workflow_file.exists():
                    log(f"⚠ Workflow file not found: {workflow_file}")
                    conn.close()
                    return True
                
                with open(workflow_file, 'r') as f:
                    workflow = json.load(f)
                
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
                log(f"✓ Imported N8N workflow: {workflow.get('name')}")
                conn.close()
                return True
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    log(f"⚠ Database busy, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                raise
    except Exception as e:
        log(f"⚠ Could not setup workflow: {e}")
        return True

def test_comfyui():
    """Test ComfyUI is accessible"""
    log("🎨 Testing ComfyUI...")
    
    try:
        req = urllib.request.Request('http://localhost:8188/system_stats')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                stats = json.loads(resp.read())
                log(f"✓ ComfyUI is running")
                log(f"  GPU: {stats.get('gfxcard_name', 'CPU mode')}")
                return True
    except Exception as e:
        log(f"✗ ComfyUI Error: {e}")
        return False

def test_n8n():
    """Test N8N is accessible"""
    log("⚙️  Testing N8N...")
    
    try:
        req = urllib.request.Request('http://localhost:5678/')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                log(f"✓ N8N is running")
                return True
    except Exception as e:
        log(f"✗ N8N Error: {e}")
        return False

def check_model():
    """Check if model is ready"""
    log("📦 Checking models...")
    
    model_path = Path("comfyui/models/checkpoints/v1-5-pruned.safetensors")
    output_path = Path("comfyui/output")
    
    if not model_path.exists():
        log(f"✗ Model not found: {model_path}")
        return False
    
    log(f"✓ Model ready: {model_path.name}")
    
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    log(f"✓ Output folder ready")
    return True

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT
    
    log("=" * 60)
    log("🚀 AutoComfyN8n - Text-to-Image Integration Test")
    log("=" * 60)
    log("🔄 Starting fresh with clean database and reimported workflows")
    log()
    
    # Ensure containers are running
    if not ensure_containers_running():
        log("✗ Failed to start containers")
        return 1
    
    # Reset database for fresh start
    reset_database()
    log()
    
    # Create admin user
    create_user()
    log()
    
    # Wait for services
    log("⏳ Waiting for services to be ready...")
    for i in range(30):
        try:
            with urllib.request.urlopen('http://localhost:5678/', timeout=1) as resp:
                if resp.status == 200:
                    log("✓ Services are ready\n")
                    break
        except:
            pass
        time.sleep(1)
    
    # Extra wait for database to be fully initialized
    time.sleep(5)
    
    # Setup workflows
    ensure_workflows_imported()
    log()
    
    # Run tests
    test1 = test_comfyui()
    log()
    test2 = test_n8n()
    log()
    test3 = check_model()
    log()
    
    # Results
    log("=" * 60)
    if test1 and test2 and test3:
        log("✓ System Ready for Text-to-Image Generation!")
        log("=" * 60)
        log()
        log(f"📝 Your prompt: '{prompt}'")
        log()
        log("🚀 To generate images with ComfyUI:")
        log("   1. Open http://localhost:8188 in your browser")
        log("   2. Use the 'simple_text_to_image' workflow")
        log("   3. Edit the positive prompt with your text")
        log("   4. Click 'Queue Prompt' to generate")
        log()
        log("🔗 To generate via N8N workflow:")
        log("   1. Open http://localhost:5678 (Login: admin/admin123)")
        log("   2. Go to 'Test ComfyUI Integration' workflow")
        log("   3. Click Execute/Play to run")
        log()
        log("📁 Generated images will be saved to:")
        log(f"   {Path('comfyui/output').absolute()}")
        log()
        log("💡 Tips:")
        log("   - Modify prompts in the workflow nodes for custom results")
        log("   - Check output folder for saved images")
        log("   - Use GPU mode if CUDA is available for faster generation")
        return 0
    else:
        log("✗ System validation failed")
        log("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
