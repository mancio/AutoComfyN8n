#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
import base64
import time

DEFAULT_PROMPT = "a beautiful sunset over mountains, oil painting style"
MODEL_URL = os.environ.get(
    "MODEL_URL",
    "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors",
)
MODEL_NAME = os.environ.get("MODEL_NAME", "v1-5-pruned.safetensors")
N8N_USER = os.environ.get("N8N_USER", "admin")
N8N_PASS = os.environ.get("N8N_PASS", "admin123")


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def log(msg):
    print(msg)


def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    models_dir = os.path.join(project_root, "comfyui", "models", "checkpoints")
    model_path = os.path.join(models_dir, MODEL_NAME)
    output_dir = os.path.join(project_root, "comfyui", "output")
    workflow_path = os.path.join(project_root, "n8n_data", "workflows", "test_comfyui_integration.json")

    log("[1/5] Checking Docker containers...")
    try:
        run(["docker", "compose", "ps"])
    except subprocess.CalledProcessError:
        print("docker compose is not available or the stack is not running.")
        return 1

    ps_out = run(["docker", "compose", "ps"], check=False).stdout
    if "n8n-love-comfy" not in ps_out or "comfyui-love-comfy" not in ps_out:
        log("Containers not found. Starting stack...")
        run(["docker", "compose", "up", "-d"])

    log("[2/5] Ensuring model exists...")
    os.makedirs(models_dir, exist_ok=True)
    if not os.path.isfile(model_path):
        log(f"Model not found. Downloading {MODEL_NAME} (this can take a while)...")
        urllib.request.urlretrieve(MODEL_URL, model_path)
    else:
        log(f"Model already present: {MODEL_NAME}")

    auth_token = base64.b64encode(f"{N8N_USER}:{N8N_PASS}".encode("utf-8")).decode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_token}",
    }

    if os.path.isfile(workflow_path):
        log("[2.5/5] Importing N8N workflow via CLI...")
        container_path = "/home/node/.n8n/workflows/test_comfyui_integration.json"
        try:
            run([
                "docker",
                "compose",
                "exec",
                "-T",
                "n8n",
                "n8n",
                "import:workflow",
                "--input",
                container_path,
            ])
            result = run([
                "docker",
                "compose",
                "exec",
                "-T",
                "n8n",
                "n8n",
                "list:workflow",
            ], check=False)
            workflow_id = None
            for line in result.stdout.splitlines():
                if "|" in line:
                    wf_id, wf_name = line.split("|", 1)
                    if wf_name.strip() == "Test ComfyUI Integration":
                        workflow_id = wf_id.strip()
                        break

            if workflow_id:
                run([
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "n8n",
                    "n8n",
                    "publish:workflow",
                    "--id",
                    workflow_id,
                ], check=False)
                run(["docker", "compose", "restart", "n8n"], check=False)
                time.sleep(5)
        except subprocess.CalledProcessError:
            print("Failed to import workflow via CLI. Import manually if needed.")

    log("[3/5] Sending prompt to N8N webhook...")
    body = json.dumps({"prompt": prompt}).encode("utf-8")

    primary_url = "http://localhost:5678/webhook/comfyui-integration-workflow/webhook/test-comfy"
    test_url = "http://localhost:5678/webhook-test/comfyui-integration-workflow/webhook/test-comfy"

    response_text = None
    for url in (primary_url, test_url):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                response_text = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise

    if response_text is None:
        print("Webhook not found. Make sure the N8N workflow is imported and activated.")
        print(f"Tried: {primary_url} and {test_url}")
        return 1

    log("[4/5] N8N response:")
    print(response_text)

    log("[5/5] Latest generated images:")
    if os.path.isdir(output_dir):
        images = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.lower().endswith(".png")
        ]
        images.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        for img in images[:5]:
            print(img)
    else:
        print(f"Output folder not found yet: {output_dir}")

    log(f"Done. You can open the output folder here: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
