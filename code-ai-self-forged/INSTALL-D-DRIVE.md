# Install Ollama on D: Drive

## Step 1: Set Ollama Home Directory

Before installing Ollama, set the environment variable to use D: drive:

### PowerShell (Run as Administrator):
```powershell
# Set Ollama models directory to D: drive
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', 'D:\ollama\models', 'Machine')

# Verify
$env:OLLAMA_MODELS
```

### Or via System Environment Variables GUI:
1. Press `Win + X` → System → Advanced system settings
2. Environment Variables → System Variables → New
3. Variable name: `OLLAMA_MODELS`
4. Variable value: `D:\ollama\models`
5. Click OK

## Step 2: Create Directory

```powershell
New-Item -ItemType Directory -Path "D:\ollama\models" -Force
```

## Step 3: Install Ollama

**Option A: Using winget**
```powershell
winget install Ollama.Ollama
```

**Option B: Manual Download**
1. Download from: https://ollama.ai/download/windows
2. Run installer
3. Ollama will use D:\ollama\models for storage

## Step 4: Verify Installation

```powershell
# Restart PowerShell to reload environment variables
# Then check:
ollama --version

# Check models directory
Write-Host "Models will be stored in: $env:OLLAMA_MODELS"
```

## Step 5: Pull Model to D: Drive

```powershell
# This will download ~5GB to D:\ollama\models
ollama pull llama3.1:8b
```

## Step 6: Verify Model Location

```powershell
# Check D: drive usage
Get-ChildItem -Path "D:\ollama\models" -Recurse | Measure-Object -Property Length -Sum
```

## Complete Setup Script

Run this PowerShell script as Administrator:

```powershell
# Set Ollama to use D: drive
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', 'D:\ollama\models', 'Machine')

# Create directory
New-Item -ItemType Directory -Path "D:\ollama\models" -Force

# Install Ollama
winget install Ollama.Ollama

# Restart PowerShell, then:
# Pull model
ollama pull llama3.1:8b

Write-Host "✓ Ollama installed on D: drive"
Write-Host "Models location: D:\ollama\models"
```

## Disk Space

Models will use approximately:
- `llama3.1:8b` → 5GB
- `codellama:34b` → 20GB
- `qwen2.5-coder:32b` → 19GB

All stored on D: drive!
