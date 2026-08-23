# Resource Monitor During Network Issues
# Checks if system resources cause network drops

$logPath = "D:\code_ai\code\project-designs\connection-monitoring-for-network\logs"
New-Item -ItemType Directory -Force -Path $logPath | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$logFile = Join-Path $logPath "resource-monitor-$timestamp.csv"

Write-Host "Monitoring system resources..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

# Log header
"Time,CPU_%,RAM_GB,Disk_Active_%,Network_Bytes/sec" | Out-File $logFile

while ($true) {
    # Get CPU
    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
    
    # Get RAM
    $os = Get-CimInstance Win32_OperatingSystem
    $ramUsed = ($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB
    
    # Get Disk
    $disk = (Get-Counter '\PhysicalDisk(_Total)\% Disk Time').CounterSamples[0].CookedValue
    
    # Get Network
    $network = (Get-Counter '\Network Interface(*)\Bytes Total/sec').CounterSamples | 
               Measure-Object -Property CookedValue -Sum | 
               Select-Object -ExpandProperty Sum
    
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$time,$($cpu.ToString('0.00')),$($ramUsed.ToString('0.00')),$($disk.ToString('0.00')),$([math]::Round($network))"
    $logEntry | Out-File $logFile -Append
    
    # Color code based on thresholds
    $cpuColor = if ($cpu -gt 80) { "Red" } elseif ($cpu -gt 50) { "Yellow" } else { "Green" }
    $ramColor = if ($ramUsed -gt 12) { "Red" } elseif ($ramUsed -gt 8) { "Yellow" } else { "Green" }
    $diskColor = if ($disk -gt 90) { "Red" } elseif ($disk -gt 50) { "Yellow" } else { "Green" }
    
    Write-Host "[$time]" -NoNewline
    Write-Host " CPU: $($cpu.ToString('0.0'))%" -ForegroundColor $cpuColor -NoNewline
    Write-Host " | RAM: $($ramUsed.ToString('0.1'))GB" -ForegroundColor $ramColor -NoNewline
    Write-Host " | Disk: $($disk.ToString('0.0'))%" -ForegroundColor $diskColor -NoNewline
    Write-Host " | Network: $([math]::Round($network/1KB))KB/s"
    
    Start-Sleep -Seconds 2
}
