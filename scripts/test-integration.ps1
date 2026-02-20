param(
    [string]$Prompt = "a beautiful sunset over mountains, oil painting style",
    [string]$ModelUrl = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors",
    [string]$ModelName = "v1-5-pruned.safetensors",
    [string]$N8nUser = "admin",
    [string]$N8nPass = "admin123"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$modelsDir = Join-Path $projectRoot "comfyui\models\checkpoints"
$modelPath = Join-Path $modelsDir $ModelName
$outputDir = Join-Path $projectRoot "comfyui\output"

Write-Host "[1/5] Checking Docker containers..."
$ps = & docker compose ps 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "docker compose is not available or the stack is not running."
}

if ($ps -notmatch "n8n-love-comfy" -or $ps -notmatch "comfyui-love-comfy") {
    Write-Host "Containers not found. Starting stack..."
    & docker compose up -d
}

Write-Host "[2/5] Ensuring model exists..."
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
}

if (-not (Test-Path $modelPath)) {
    Write-Host "Model not found. Downloading $ModelName (this can take a while)..."
    Invoke-WebRequest -Uri $ModelUrl -OutFile $modelPath
} else {
    Write-Host "Model already present: $ModelName"
}

Write-Host "[3/5] Sending prompt to N8N webhook..."
$body = @{ prompt = $Prompt } | ConvertTo-Json -Compress
$securePass = ConvertTo-SecureString $N8nPass -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($N8nUser, $securePass)
$response = Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -Credential $credential

Write-Host "[4/5] N8N response:"
$response | ConvertTo-Json -Depth 4

Write-Host "[5/5] Latest generated images:"
if (Test-Path $outputDir) {
    Get-ChildItem $outputDir -Filter *.png | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime
} else {
    Write-Host "Output folder not found yet: $outputDir"
}

Write-Host "Done. You can open the output folder here: $outputDir"
