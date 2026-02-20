# Social Automation with N8N and ComfyUI

A Docker-based setup for social media automation workflows using N8N orchestration and ComfyUI for AI image generation. **Uses NVIDIA CUDA for GPU-accelerated image generation.**

## Services

### N8N (Workflow Automation)
- **Container**: n8n-love-comfy
- **Port**: 5678
- **Access**: http://localhost:5678
- **Data**: Stored in `./n8n_data`

### ComfyUI (Image Generation)
- **Container**: comfyui-love-comfy
- **Port**: 8188
- **Access**: http://localhost:8188
- **Models**: Stored in `./comfyui/models`
- **Output**: Generated images in `./comfyui/output`

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- NVIDIA GPU with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed (CUDA 12.1+)

### Running the Stack

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Check service status**:
```bash
docker-compose ps
```

3. **View logs**:
```bash
docker-compose logs -f n8n
docker-compose logs -f comfyui
```

### Accessing the Services

- **N8N**: Open http://localhost:5678 in your browser
- **ComfyUI**: Open http://localhost:8188 in your browser

## GPU Support (CUDA)

This project uses NVIDIA CUDA 12.1 by default for GPU-accelerated image generation.

**Requirements:**
- NVIDIA GPU with compatible drivers
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed on the host
- Docker Desktop with GPU support enabled (Windows: WSL2 backend)

GPU passthrough is already configured in `docker-compose.yml`. If you don't have a GPU, ComfyUI will fall back to CPU mode (significantly slower).

## Directory Structure

```
AutoComfyN8n/
├── docker-compose.yml
├── Dockerfile.n8n
├── Dockerfile.comfyui
├── README.md
├── .gitignore
├── .env.example
├── n8n_data/
│   └── workflows/         # Example N8N workflows
│       └── test_comfyui_integration.json
└── comfyui/
    ├── models/            # AI models (checkpoints, VAE, etc.)
    │   └── checkpoints/   # Put .safetensors files here
    ├── output/            # Generated images output
    ├── input/             # Input images for processing
    └── workflows/         # Example ComfyUI workflows
        └── simple_text_to_image.json
```

## Next Steps

1. **Download Models**: Add your AI models to `comfyui/models/`
2. **Create Workflows**: Design automation workflows in N8N
3. **Connect Services**: Use N8N to call ComfyUI API endpoints

## Testing the Integration

This project includes example workflows to test N8N and ComfyUI integration.

### Step 1: Download a Model

First, download a Stable Diffusion model (needed for image generation):

```powershell
# Download SD 1.5 model (~2GB) - Windows PowerShell
Invoke-WebRequest -Uri "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors" -OutFile ".\comfyui\models\checkpoints\v1-5-pruned.safetensors"
```

Or use curl (bash/Linux/Mac):
```bash
curl -L -o ./comfyui/models/checkpoints/v1-5-pruned.safetensors \
  "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors"
```

### Step 2: Load ComfyUI Workflow (Optional)

1. Open ComfyUI: http://localhost:8188
2. Click "Load" button
3. Select: `comfyui/workflows/simple_text_to_image.json`
4. This workflow shows a basic text-to-image setup

### Step 3: Import N8N Workflow

1. Open N8N: http://localhost:5678
2. Set up your account (first time only)
3. Click "Import from File"
4. Select: `n8n_data/workflows/test_comfyui_integration.json`
5. Click "Activate" to enable the workflow

### Step 4: Test the Integration

Once the workflow is active in N8N, trigger it with:

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"prompt": "a beautiful sunset over mountains"}'
```

**curl (bash/Linux/Mac):**
```bash
curl -X POST http://localhost:5678/webhook/test-comfy \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset over mountains"}'
```

### Step 5: Check the Results

- Generated images will be in: `comfyui/output/`
- The webhook will return a JSON response with the prompt ID
- You can view the generation progress in ComfyUI: http://localhost:8188

### What Happens?

1. 🎯 N8N receives your webhook with a text prompt
2. 🚀 N8N sends the prompt to ComfyUI API
3. 🎨 ComfyUI generates an image based on your prompt
4. 💾 Image is saved to `comfyui/output/`
5. ✅ N8N returns success response

## Stopping the Services

```bash
docker-compose down
```

To also remove volumes and data:
```bash
docker-compose down -v
```

## Troubleshooting

- **N8N not starting**: Check port 5678 is available
- **ComfyUI not starting**: Ensure `comfyui/models` exists and has necessary models
- **GPU not detected**: Verify nvidia-docker is installed and configured

## API Endpoints

- **N8N Webhook**: http://localhost:5678/webhook/
- **ComfyUI API**: http://localhost:8188/api/
