# Creative Automation Hub - Quick Start Script

Write-Host "🚀 Creative Automation Hub Startup" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

$checks = @{
    "Go" = "go version"
    "Python" = "python --version"
    "Node.js" = "node --version"
    "Redis" = "redis-cli --version"
    "PostgreSQL" = "psql --version"
}

foreach ($tool in $checks.Keys) {
    try {
        $null = Invoke-Expression $checks[$tool] 2>&1
        Write-Host "✓ $tool installed" -ForegroundColor Green
    } catch {
        Write-Host "✗ $tool not found" -ForegroundColor Red
    }
}

# Start services
Write-Host "`n[1/3] Starting Go Backend..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend-go; go run cmd/server/main.go" -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Python Workers..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd ai-workers; python worker.py" -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 2

Write-Host "[3/3] Starting Next.js Frontend..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WorkingDirectory $PSScriptRoot

Write-Host "`n✅ All services starting!" -ForegroundColor Green
Write-Host "`nAccess the app: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API health: http://localhost:8080/health" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C in each terminal to stop services" -ForegroundColor Gray
