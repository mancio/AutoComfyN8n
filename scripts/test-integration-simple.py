#!/usr/bin/env python3
"""Simple integration test that calls ComfyUI directly via N8N or standalone"""
import json
import urllib.request
import urllib.error
import time
import sys

def test_comfyui_direct():
    """Test ComfyUI is accessible"""
    print("[1/2] Testing ComfyUI...")
    
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
    print("[2/2] Testing N8N availability...")
    
    try:
        req = urllib.request.Request('http://localhost:5678/')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print(f"✓ N8N is available at http://localhost:5678")
                print(f"✓ Log in with admin/admin123 to set up workflows")
                return True
    except Exception as e:
        print(f"✗ N8N Error: {e}")
        return False

def main():
    print("=== Integration Test ===\n")
    
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
    
    test1 = test_comfyui_direct()
    test2 = test_n8n_available()
    
    print(f"\n{'='*50}")
    if test1 and test2:
        print("✓ Integration test PASSED")
        print("\nNext steps:")
        print("1. Open http://localhost:5678 in your browser")
        print("2. Log in with admin/admin123")
        print("3. Create or import N8N workflows to orchestrate ComfyUI")
        return 0
    else:
        print("✗ Integration  test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
