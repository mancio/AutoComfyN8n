#!/usr/bin/env python3
"""Text-to-Image Integration Test - AutoComfyN8n"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import time
from pathlib import Path

DEFAULT_PROMPT = "a beautiful sunset over mountains, oil painting style"
OWNER_EMAIL = os.getenv("N8N_OWNER_EMAIL", "admin@example.com")
OWNER_FIRST_NAME = os.getenv("N8N_OWNER_FIRST_NAME", "Admin")
OWNER_LAST_NAME = os.getenv("N8N_OWNER_LAST_NAME", "User")
OWNER_PASSWORD = os.getenv("N8N_OWNER_PASSWORD", "ChangeMeNow123!")

def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def log(msg=""):
    print(msg)

def ensure_containers_running():
    """Recreate Docker containers on every test run"""
    log("📦 Recreating Docker containers for a clean run...")

    try:
        run(["docker", "compose", "down"], check=False)
    except Exception as e:
        log(f"⚠ Could not stop/remove containers cleanly: {e}")

    log("Starting Docker containers...")
    try:
        result = run(["docker", "compose", "up", "-d", "--build"], check=False)
        if result.returncode == 0:
            log("✓ Containers built and started successfully\n")
            return True

        log(f"✗ Failed to start containers: {result.stderr}")
        return False
    except Exception as e:
        log(f"✗ Error starting containers: {e}")
        return False

def ensure_workflows_imported():
    """Import N8N workflow using n8n CLI command"""
    log("🔧 Importing workflows...")

    try:
        workflow_host_path = Path("workflows/n8n_test_comfyui_integration.json")
        workflow_container_path = "/tmp/n8n_test_comfyui_integration.json"

        if not workflow_host_path.exists():
            log(f"⚠ Workflow file not found: {workflow_host_path}")
            return True

        copy_result = run([
            "docker", "compose", "cp",
            str(workflow_host_path),
            f"n8n:{workflow_container_path}"
        ], check=False)

        if copy_result.returncode != 0:
            log(f"⚠ Could not copy workflow into n8n container: {copy_result.stderr.strip() or copy_result.stdout.strip()}")
            return False

        result = run([
            "docker", "compose", "exec", "-T", "n8n",
            "n8n", "import:workflow",
            f"--input={workflow_container_path}"
        ], check=False)

        if result.returncode == 0:
            log("✓ Imported N8N workflow via n8n CLI")
            return True

        log(f"⚠ n8n workflow import command failed: {result.stderr.strip() or result.stdout.strip()}")
        return False
    except Exception as e:
        log(f"⚠ Could not setup workflow: {e}")
        return False

def ensure_owner_setup():
    """Create N8N owner via REST API if it has not been created yet"""
    log("👤 Ensuring N8N owner user exists...")

    payload = json.dumps({
        "email": OWNER_EMAIL,
        "firstName": OWNER_FIRST_NAME,
        "lastName": OWNER_LAST_NAME,
        "password": OWNER_PASSWORD,
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:5678/rest/owner/setup",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                log(f"✓ Owner setup complete: {OWNER_EMAIL}")
                return True
    except urllib.error.HTTPError as e:
        # 400 usually indicates owner already exists in n8n
        if e.code == 400:
            log("✓ Owner already initialized")
            return True
        log(f"⚠ Owner setup returned HTTP {e.code}")
        return False
    except Exception as e:
        log(f"⚠ Owner setup error: {e}")
        return False

    return False

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
    log("🔄 Starting integration validation")
    log()
    
    # Ensure containers are running
    if not ensure_containers_running():
        log("✗ Failed to start containers")
        return 1
    
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

    # Ensure owner setup is done from Python (not docker bootstrap)
    if not ensure_owner_setup():
        log("✗ Failed to setup owner user")
        return 1
    log()
    
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
        log("   1. Open http://localhost:5678")
        log(f"   2. Login with {OWNER_EMAIL}/{OWNER_PASSWORD}")
        log("   3. Go to 'Test ComfyUI Integration' workflow")
        log("   4. Click Execute/Play to run")
        log()
        log("📁 Generated images will be saved to:")
        log(f"   {Path('comfyui/output').absolute()}")
        log()
        log("💡 Tips:")
        log("   - Modify prompts in the workflow nodes for custom results")
        log("   - Check output folder for saved images")
        log("   - CUDA GPU acceleration is enabled by default")
        return 0
    else:
        log("✗ System validation failed")
        log("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
