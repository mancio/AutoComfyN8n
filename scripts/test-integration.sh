#!/usr/bin/env bash
set -euo pipefail

PROMPT="${1:-a beautiful sunset over mountains, oil painting style}"
MODEL_URL="${MODEL_URL:-https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors}"
MODEL_NAME="${MODEL_NAME:-v1-5-pruned.safetensors}"
N8N_USER="${N8N_USER:-admin}"
N8N_PASS="${N8N_PASS:-admin123}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODELS_DIR="${PROJECT_ROOT}/comfyui/models/checkpoints"
MODEL_PATH="${MODELS_DIR}/${MODEL_NAME}"
OUTPUT_DIR="${PROJECT_ROOT}/comfyui/output"

log() {
  printf "[%s] %s\n" "$(date +%H:%M:%S)" "$1"
}

log "Checking Docker containers..."
if ! docker compose ps >/dev/null 2>&1; then
  echo "docker compose is not available or the stack is not running." >&2
  exit 1
fi

PS_OUT="$(docker compose ps 2>/dev/null || true)"
if [[ "${PS_OUT}" != *"n8n-love-comfy"* || "${PS_OUT}" != *"comfyui-love-comfy"* ]]; then
  log "Containers not found. Starting stack..."
  docker compose up -d
fi

log "Ensuring model exists..."
mkdir -p "${MODELS_DIR}"
if [[ ! -f "${MODEL_PATH}" ]]; then
  log "Model not found. Downloading ${MODEL_NAME} (this can take a while)..."
  curl -L "${MODEL_URL}" -o "${MODEL_PATH}"
else
  log "Model already present: ${MODEL_NAME}"
fi

log "Sending prompt to N8N webhook..."
RESPONSE=$(curl -s -X POST "http://localhost:5678/webhook/test-comfy" \
  -u "${N8N_USER}:${N8N_PASS}" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"${PROMPT}\"}")

log "N8N response:"
printf "%s\n" "${RESPONSE}"

log "Latest generated images:"
if [[ -d "${OUTPUT_DIR}" ]]; then
  ls -t "${OUTPUT_DIR}"/*.png 2>/dev/null | head -n 5 || true
else
  echo "Output folder not found yet: ${OUTPUT_DIR}"
fi

log "Done. You can open the output folder here: ${OUTPUT_DIR}"
