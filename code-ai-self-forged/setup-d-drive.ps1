# Complete Setup Script for Code-AI-Self-Forged on D: Drive
Write-Host "Code-AI-Self-Forged - D: Drive Setup" -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run as Administrator" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Step 1: Setting Ollama to D: drive..." -ForegroundColor Yellow
$ollamaModelsPath = "D:\ollama\models"
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ollamaModelsPath, "Machine")
$env:OLLAMA_MODELS = $ollamaModelsPath
New-Item -ItemType Directory -Path $ollamaModelsPath -Force | Out-Null
Write-Host "Done" -ForegroundColor Green

Write-Host "Step 2: Installing Ollama..." -ForegroundColor Yellow
winget install --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
Write-Host "Done" -ForegroundColor Green

Write-Host "Step 3: Waiting for Ollama..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Step 4: Downloading model (5GB, may take 10-30 min)..." -ForegroundColor Yellow
ollama pull llama3.1:8b

Write-Host "Step 5: Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "D:\code_ai\code\project-designs\code-ai-self-forged"
pip install -r requirements.txt

Write-Host "Step 6: Creating .env file..." -ForegroundColor Yellow
$envContent = "LLM_PROVIDER=ollama`nOLLAMA_MODEL=llama3.1:8b`nOLLAMA_BASE_URL=http://localhost:11434`nMAX_TOKENS=8000`nTEMPERATURE=0.7`nEXECUTION_TIMEOUT=30`nLOG_LEVEL=INFO"
Set-Content -Path ".env" -Value $envContent

Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "Everything installed on D: drive" -ForegroundColor Green
pause
