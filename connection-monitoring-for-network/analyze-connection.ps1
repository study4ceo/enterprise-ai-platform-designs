# Connection Quality Analyzer
# Provides detailed statistics

function Test-ConnectionQuality {
    param(
        [string]$Target = "8.8.8.8",
        [int]$Count = 100
    )
    
    Write-Host "Testing connection quality to $Target..." -ForegroundColor Cyan
    Write-Host "Sending $Count packets...`n" -ForegroundColor Yellow
    
    $results = @()
    $failed = 0
    
    for ($i = 1; $i -le $Count; $i++) {
        Write-Progress -Activity "Pinging $Target" -Status "$i of $Count" -PercentComplete (($i / $Count) * 100)
        
        $result = Test-Connection -ComputerName $Target -Count 1 -ErrorAction SilentlyContinue
        
        if ($result) {
            $results += $result.ResponseTime
        } else {
            $failed++
        }
    }
    
    Write-Progress -Activity "Pinging $Target" -Completed
    
    if ($results.Count -gt 0) {
        $avg = ($results | Measure-Object -Average).Average
        $min = ($results | Measure-Object -Minimum).Minimum
        $max = ($results | Measure-Object -Maximum).Maximum
        $packetLoss = ($failed / $Count) * 100
        
        Write-Host "`n=== Connection Quality Report ===" -ForegroundColor Green
        Write-Host "Target: $Target"
        Write-Host "Packets Sent: $Count"
        Write-Host "Packets Lost: $failed ($($packetLoss.ToString('0.00'))%)"
        Write-Host "`nResponse Times:"
        Write-Host "  Minimum: $($min)ms"
        Write-Host "  Average: $($avg.ToString('0.00'))ms"
        Write-Host "  Maximum: $($max)ms"
        
        # Quality assessment
        Write-Host "`nQuality Assessment:" -ForegroundColor Cyan
        if ($packetLoss -eq 0 -and $avg -lt 50) {
            Write-Host "  ✓ Excellent - No issues detected" -ForegroundColor Green
        } elseif ($packetLoss -lt 5 -and $avg -lt 100) {
            Write-Host "  ✓ Good - Minor latency but acceptable" -ForegroundColor Yellow
        } elseif ($packetLoss -lt 10) {
            Write-Host "  ⚠ Fair - Some packet loss detected" -ForegroundColor Yellow
        } else {
            Write-Host "  ✗ Poor - Significant issues detected" -ForegroundColor Red
        }
    } else {
        Write-Host "`n✗ Connection Failed - 100% packet loss" -ForegroundColor Red
    }
}

# Run the test
Test-ConnectionQuality -Target "8.8.8.8" -Count 100
