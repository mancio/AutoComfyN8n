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
$workflowPath = Join-Path $projectRoot "n8n_data\workflows\test_comfyui_integration.json"

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

$authBytes = [Text.Encoding]::UTF8.GetBytes("$N8nUser`:$N8nPass")
$authHeader = [Convert]::ToBase64String($authBytes)
$headers = @{"Content-Type"="application/json"; "Authorization"="Basic $authHeader"}

if (Test-Path $workflowPath) {
    Write-Host "[2.5/5] Importing N8N workflow via CLI..."
    $containerPath = "/home/node/.n8n/workflows/test_comfyui_integration.json"
    try {
        & docker compose exec -T n8n n8n import:workflow --input $containerPath | Out-Null
        $list = & docker compose exec -T n8n n8n list:workflow
        $workflowId = $null
        foreach ($line in $list) {
            if ($line -match "\|") {
                $parts = $line -split "\|", 2
                if ($parts[1].Trim() -eq "Test ComfyUI Integration") {
                    $workflowId = $parts[0].Trim()
                    break
                }
            }
        }

        if ($workflowId) {
            & docker compose exec -T n8n n8n publish:workflow --id $workflowId | Out-Null
            & docker compose restart n8n | Out-Null
            Start-Sleep -Seconds 5
        }
    } catch {
        Write-Host "Failed to import workflow via CLI. Import manually if needed."
    }
}

Write-Host "[3/5] Sending prompt to N8N webhook..."
$body = @{ prompt = $Prompt } | ConvertTo-Json -Compress
$response = Invoke-RestMethod -Uri "http://localhost:5678/webhook/test-comfy" -Method POST -Headers $headers -Body $body

Write-Host "[4/5] N8N response:"
$response | ConvertTo-Json -Depth 4

Write-Host "[5/5] Latest generated images:"
if (Test-Path $outputDir) {
    Get-ChildItem $outputDir -Filter *.png | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime
} else {
    Write-Host "Output folder not found yet: $outputDir"
}

Write-Host "Done. You can open the output folder here: $outputDir"
