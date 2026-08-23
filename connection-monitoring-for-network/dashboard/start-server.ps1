# Start Server Script
# Starts the unified monitoring server in the current window
# Use Ctrl+C to stop

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host "   Network Monitoring Dashboard - Launcher" -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan

# Check if server is already running
$existing = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($existing) {
    Write-Host "[WARNING] Port 8080 is already in use!" -ForegroundColor Yellow
    Write-Host "  Run .\stop-server.ps1 first, or use a different port:`n" -ForegroundColor Yellow
    Write-Host "  .\unified-server.ps1 -Port 8081`n" -ForegroundColor Gray
    exit 1
}

Write-Host "[OK] Port 8080 is available" -ForegroundColor Green
Write-Host "[OK] Starting server...`n" -ForegroundColor Green

# Start the actual server script
.\unified-server.ps1

Write-Host "`n[OK] Server stopped cleanly`n" -ForegroundColor Green
