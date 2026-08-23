# Stop Server Script
# Stops any running unified-server.ps1 processes

Write-Host "`nStopping Network Monitoring Server..." -ForegroundColor Yellow

# Find and stop the server process
$processes = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*unified-server.ps1*"
}

if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "  Stopping process ID: $($proc.Id)" -ForegroundColor Cyan
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "`n[OK] Server stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[INFO] No server process found running." -ForegroundColor Yellow
}

# Also try to free up port 8080
$tcpConnections = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($tcpConnections) {
    Write-Host "`nCleaning up port 8080..." -ForegroundColor Cyan
    foreach ($conn in $tcpConnections) {
        try {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "  Freed port 8080" -ForegroundColor Green
        } catch {
            Write-Host "  Could not free port 8080 (may require admin)" -ForegroundColor Yellow
        }
    }
}

Write-Host "`nServer shutdown complete.`n" -ForegroundColor Green
