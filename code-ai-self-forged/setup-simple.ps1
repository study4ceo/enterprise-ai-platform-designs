# Simple Setup Script - No syntax errors
# Run as Administrator

Write-Host "Code-AI-Self-Forged Setup" -ForegroundColor Cyan
Write-Host ""

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Run as Administrator" -ForegroundColor Red
    pause
    exit 1
}

# Step 1: Set Ollama to D drive
Write-Host "[1/5] Setting Ollama to D: drive..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', 'D:\ollama\models', 'Machine')
$env:OLLAMA_MODELS = 'D:\ollama\models'
New-Item -ItemType Directory -Path 'D:\ollama\models' -Force | Out-Null
Write-Host "Done" -ForegroundColor Green

# Step 2: Install Ollama
Write-Host "[2/5] Installing Ollama..." -ForegroundColor Yellow
winget install --id Ollama.Ollama --silent
Write-Host "Done" -ForegroundColor Green

# Step 3: Wait and pull model
Write-Host "[3/5] Waiting for Ollama service..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "[4/5] Downloading model (5GB)..." -ForegroundColor Yellow
ollama pull llama3.1:8b

# Step 4: Install Python deps
Write-Host "[5/5] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location 'D:\code_ai\code\project-designs\code-ai-self-forged'
pip install -r requirements.txt

# Create .env
$envText = "LLM_PROVIDER=ollama`nOLLAMA_MODEL=llama3.1:8b`nOLLAMA_BASE_URL=http://localhost:11434`nMAX_TOKENS=8000`nTEMPERATURE=0.7`nEXECUTION_TIMEOUT=30`nLOG_LEVEL=INFO"
Set-Content -Path '.env' -Value $envText

Write-Host ""
Write-Host "COMPLETE! Everything on D: drive" -ForegroundColor Green
pause
