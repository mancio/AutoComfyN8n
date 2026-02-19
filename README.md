# Social Automation with N8N and ComfyUI

A Docker-based setup for social media automation workflows using N8N orchestration and ComfyUI for image generation.

## Services

### N8N (Workflow Automation)
- **Container**: n8n-social-automation
- **Port**: 5678
- **Access**: http://localhost:5678
- **Data**: Stored in `./n8n_data`

### ComfyUI (Image Generation)
- **Container**: comfyui-social-automation
- **Port**: 8188
- **Access**: http://localhost:8188
- **Models**: Stored in `./comfyui/models`
- **Output**: Generated images in `./comfyui/output`

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Optional: NVIDIA GPU with nvidia-docker for GPU acceleration

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

## GPU Support (Optional)

To enable NVIDIA GPU support in ComfyUI:

1. Install nvidia-docker on your system
2. In `docker-compose.yml`, uncomment the `deploy` section under comfyui service
3. Restart the services

## Directory Structure

```
social-automation/
├── docker-compose.yml
├── n8n_data/              # N8N workflow and settings
├── comfyui/
│   ├── models/            # AI models (checkpoints, VAE, etc.)
│   ├── output/            # Generated images output
│   └── input/             # Input images for processing
```

## Next Steps

1. **Download Models**: Add your AI models to `comfyui/models/`
2. **Create Workflows**: Design automation workflows in N8N
3. **Connect Services**: Use N8N to call ComfyUI API endpoints

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
