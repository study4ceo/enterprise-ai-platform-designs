# Network Monitoring Script
# Run in PowerShell: .\monitor-network.ps1

param(
    [int]$DurationMinutes = 60,
    [string]$LogPath = "D:\code_ai\code\project-designs\connection-monitoring-for-network\logs"
)

# Create log directory
New-Item -ItemType Directory -Force -Path $LogPath | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$logFile = Join-Path $LogPath "network-monitor-$timestamp.csv"

Write-Host "Starting network monitoring for $DurationMinutes minutes..." -ForegroundColor Green
Write-Host "Logging to: $logFile" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop early`n" -ForegroundColor Yellow

# Targets to test
$targets = @{
    'Google DNS' = '8.8.8.8'
    'Cloudflare DNS' = '1.1.1.1'
    'Google.com' = 'www.google.com'
}

# Initialize log file
"Time,Target,Status,ResponseTime_ms,PacketLoss" | Out-File $logFile

$startTime = Get-Date
$endTime = $startTime.AddMinutes($DurationMinutes)

while ((Get-Date) -lt $endTime) {
    foreach ($name in $targets.Keys) {
        $target = $targets[$name]
        $result = Test-Connection -ComputerName $target -Count 1 -ErrorAction SilentlyContinue
        
        if ($result) {
            $status = "Success"
            $responseTime = $result.ResponseTime
            $packetLoss = 0
            $color = "Green"
        } else {
            $status = "Failed"
            $responseTime = "N/A"
            $packetLoss = 100
            $color = "Red"
        }
        
        $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logEntry = "$time,$name,$status,$responseTime,$packetLoss"
        $logEntry | Out-File $logFile -Append
        
        Write-Host "[$time] $name : $status (${responseTime}ms)" -ForegroundColor $color
    }
    
    Write-Host "" # Blank line for readability
    Start-Sleep -Seconds 5
}

Write-Host "`nMonitoring complete. Log saved to: $logFile" -ForegroundColor Green
