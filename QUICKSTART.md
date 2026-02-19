# Quick Test Guide

This guide will help you test the N8N ↔ ComfyUI integration in 5 minutes.

## Prerequisites Check

```powershell
# Make sure containers are running
docker compose ps

# You should see both containers "Up"
```

## How N8N and ComfyUI Work Together

Before diving into testing, let's understand how these services interact:

### Architecture Overview

```
User → N8N Webhook → ComfyUI API → Image Generation → Output Folder
```

### Step-by-Step Flow

#### 1. **User Triggers N8N (Entry Point)**
```powershell
# You send a POST request to N8N's webhook
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy"
  -Body '{"prompt": "a beautiful sunset"}'
```

#### 2. **N8N Receives the Request**
The N8N workflow has a **Webhook node** that:
- Listens at: `http://localhost:5678/webhook/test-comfy`
- Receives the JSON with your prompt
- Extracts the text prompt from the request body

#### 3. **N8N Calls ComfyUI API**
N8N uses an **HTTP Request node** to communicate with ComfyUI:
```
POST http://comfyui:8188/prompt
```

The request includes:
- Your text prompt
- Model to use (v1-5-pruned.safetensors)
- Generation parameters (steps, seed, etc.)
- Workflow definition (nodes and connections)

**Important:** N8N uses `http://comfyui:8188` (Docker container name) NOT `http://localhost:8188`. Both containers share an internal Docker network called `social-automation-network`.

#### 4. **ComfyUI Processes the Request**
- Receives the workflow definition as JSON
- Loads the Stable Diffusion model into memory
- Encodes your text prompt
- Generates the image using AI
- Saves image to `comfyui/output/ComfyUI_xxxxx.png`

#### 5. **N8N Returns Response**
N8N sends back confirmation:
```json
{
  "success": true,
  "prompt_id": "abc123",
  "message": "Image generation started"
}
```

### Visual Representation

```
┌─────────────────┐
│   Your Browser  │
└────────┬────────┘
         │ POST /webhook/test-comfy
         │ {"prompt": "sunset"}
         ▼
┌─────────────────┐
│      N8N        │ localhost:5678
│  ┌───────────┐  │
│  │  Webhook  │  │ Receives request
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │HTTP Request│  │ Calls ComfyUI API
│  └─────┬─────┘  │
└────────┼────────┘
         │ http://comfyui:8188/prompt
         │ (Docker internal network)
         ▼
┌─────────────────┐
│    ComfyUI      │ localhost:8188
│  ┌───────────┐  │
│  │ API Server│  │ Receives prompt
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ Generate  │  │ Creates image
│  │   Image   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │Save Output│  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  comfyui/output │
│   image.png     │
└─────────────────┘
```

### Why This Setup is Powerful

1. **N8N orchestrates** - You can add:
   - Scheduled triggers (generate images daily)
   - Multiple prompts in sequence
   - Conditional logic
   - Database storage
   - Social media posting

2. **ComfyUI generates** - Focused on AI image creation
   - Advanced workflows
   - Multiple models
   - Complex node graphs

3. **Decoupled services** - Each does one thing well
   - N8N = Automation logic
   - ComfyUI = Image generation
   - Easy to scale or replace either service

---

## Step 1: Download Model (One-time setup)

```powershell
# Create checkpoints directory if it doesn't exist
New-Item -ItemType Directory -Force -Path ".\comfyui\models\checkpoints"

# Download Stable Diffusion 1.5 (~2GB)
Invoke-WebRequest -Uri "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors" -OutFile ".\comfyui\models\checkpoints\v1-5-pruned.safetensors"
```

⏱️ This will take 5-15 minutes depending on your internet speed.

## Step 2: Import N8N Workflow

1. Open http://localhost:5678
2. Create account (if first time)
3. Click **"+ Add workflow"** → **"Import from file"**
4. Select: `n8n_data\workflows\test_comfyui_integration.json`
5. Click the **"Inactive"** toggle to **Activate** the workflow
6. You should see "Active" in green

## Step 3: Test It!

Run this command to trigger image generation:

```powershell
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"prompt": "a beautiful sunset over mountains, oil painting style"}'
```

### Expected Response:

```json
{
  "success": true,
  "prompt_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "message": "Image generation started. Check ComfyUI output folder for results.",
  "comfyui_url": "http://localhost:8188",
  "input_prompt": "a beautiful sunset over mountains, oil painting style"
}
```

## Step 4: Check Results

```powershell
# View generated images
explorer.exe .\comfyui\output\

# Or list them
Get-ChildItem .\comfyui\output\*.png | Select-Object Name, LastWriteTime
```

## More Test Prompts

Try different prompts:

```powershell
# Fantasy landscape
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"prompt": "fantasy castle on a floating island, magical atmosphere"}'

# Cyberpunk city
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"prompt": "cyberpunk city at night, neon lights, rain"}'

# Nature scene
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"prompt": "serene forest with waterfalls, morning mist"}'
```

## Troubleshooting

### Webhook doesn't respond
- Check N8N workflow is **Active** (green toggle)
- Make sure containers are running: `docker compose ps`

### "Model not found" error
- Verify model file exists: `ls .\comfyui\models\checkpoints\`
- Check the filename is exactly: `v1-5-pruned.safetensors`

### Slow generation
- First generation is always slower (loading model into memory)
- CPU mode is slow - consider GPU if you have NVIDIA card
- Reduce image size in workflow (default is 512x512)

## What's Next?

1. **Customize the N8N workflow**: Add loops, conditionals, multiple prompts
2. **Explore ComfyUI**: Load `comfyui/workflows/simple_text_to_image.json` to see the visual workflow
3. **Add more models**: Download LoRAs, VAEs, or other checkpoints
4. **Build automation**: Create scheduled workflows, social media posting, etc.

## Viewing in ComfyUI Interface

1. Open http://localhost:8188
2. Click **"Load"** button
3. Select `comfyui/workflows/simple_text_to_image.json`
4. You'll see the visual node-based workflow
5. Change the prompt in the "CLIPTextEncode" node
6. Click **"Queue Prompt"** to generate

---

**Happy automating! 🎨🤖**
