# Unified Production Server - Performance + Security Monitoring
# Provides REAL DATA ONLY - No mocks

param(
    [int]$Port = 8080
)

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host "   Network Monitoring - Production Server         " -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan

Write-Host "Starting server on port $Port..." -ForegroundColor Green
Write-Host "Dashboard URL: http://localhost:$Port`n" -ForegroundColor Yellow

# Known malicious IP ranges
$maliciousRanges = @('185.220.', '45.95.', '104.244.', '162.243.', '192.42.116.')
$suspiciousPorts = @(23, 135, 445, 3389, 5900, 6667, 31337, 1433, 3306)

# Create HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")

try {
    $listener.Start()
    
    Write-Host "[OK] Server started successfully!" -ForegroundColor Green
    Write-Host "[OK] Opening browser..." -ForegroundColor Green
    Write-Host "`nPress Ctrl+C to stop server`n" -ForegroundColor Yellow
    Write-Host "====================================================`n" -ForegroundColor Cyan
    
    # Open browser
    Start-Sleep -Milliseconds 500
    Start-Process "http://localhost:$Port"
    
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $path = $request.Url.LocalPath
        $timestamp = Get-Date -Format "HH:mm:ss"
        
        # Logging
        Write-Host "[$timestamp] $($request.HttpMethod) $path" -ForegroundColor Cyan
        
        # Route handling
        switch ($path) {
            "/" {
                # Serve unified dashboard
                $htmlPath = Join-Path $PSScriptRoot "unified-dashboard.html"
                if (Test-Path $htmlPath) {
                    $content = Get-Content $htmlPath -Raw -Encoding UTF8
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                    $response.ContentType = "text/html; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/unified-app.js" {
                # Serve JavaScript
                $jsPath = Join-Path $PSScriptRoot "unified-app.js"
                if (Test-Path $jsPath) {
                    $content = Get-Content $jsPath -Raw -Encoding UTF8
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                    $response.ContentType = "application/javascript; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/api/ping" {
                # REAL PING TEST
                try {
                    $pingTarget = "8.8.8.8"
                    $pingResult = Test-Connection -ComputerName $pingTarget -Count 1 -ErrorAction SilentlyContinue
                    
                    $data = @{
                        timestamp = (Get-Date).ToString("o")
                        success = $null -ne $pingResult
                        latency = if ($pingResult) { $pingResult.ResponseTime } else { $null }
                        target = $pingTarget
                    }
                    
                    $json = $data | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.ContentType = "application/json; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                    
                    $status = if ($data.success) { "[OK]" } else { "[FAIL]" }
                    Write-Host "  $status Ping: $($data.latency)ms" -ForegroundColor $(if ($data.success) { "Green" } else { "Red" })
                    
                } catch {
                    Write-Host "  [ERROR] Ping failed: $_" -ForegroundColor Red
                    $error = @{ error = $_.Exception.Message; success = $false }
                    $json = $error | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.StatusCode = 500
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/api/resources" {
                # REAL SYSTEM RESOURCES
                try {
                    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
                    $os = Get-CimInstance Win32_OperatingSystem
                    $totalMem = $os.TotalVisibleMemorySize / 1MB
                    $freeMem = $os.FreePhysicalMemory / 1MB
                    $memUsed = (($totalMem - $freeMem) / $totalMem) * 100
                    
                    $networkCounters = Get-Counter '\Network Interface(*)\Bytes Total/sec' -ErrorAction SilentlyContinue
                    $networkIO = if ($networkCounters) {
                        ($networkCounters.CounterSamples | Measure-Object -Property CookedValue -Sum).Sum / 1KB
                    } else { 0 }
                    
                    $data = @{
                        cpu = [math]::Round($cpu, 2)
                        memory = [math]::Round($memUsed, 2)
                        networkIO = [math]::Round($networkIO, 2)
                        timestamp = (Get-Date).ToString("o")
                    }
                    
                    $json = $data | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.ContentType = "application/json; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                    
                    Write-Host "  [OK] Resources: CPU=$($data.cpu)% MEM=$($data.memory)%" -ForegroundColor Green
                    
                } catch {
                    Write-Host "  [ERROR] Resources failed: $_" -ForegroundColor Red
                    $error = @{ error = $_.Exception.Message }
                    $json = $error | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.StatusCode = 500
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/api/connections" {
                # REAL NETWORK CONNECTIONS
                try {
                    $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | 
                        Select-Object -First 100 |
                        ForEach-Object {
                            $processName = "Unknown"
                            $processPath = ""
                            
                            try {
                                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                                if ($proc) {
                                    $processName = $proc.ProcessName
                                    $processPath = $proc.Path
                                }
                            } catch {}
                            
                            # Analyze for threats
                            $isSuspicious = $false
                            $threats = @()
                            
                            # Check malicious IP ranges
                            foreach ($range in $maliciousRanges) {
                                if ($_.RemoteAddress -like "$range*") {
                                    $isSuspicious = $true
                                    $threats += "Known malicious IP range"
                                }
                            }
                            
                            # Check suspicious ports
                            if ($suspiciousPorts -contains $_.RemotePort) {
                                $isSuspicious = $true
                                $threats += "Suspicious port $($_.RemotePort)"
                            }
                            
                            # Check unusual svchost
                            if ($processName -eq "svchost" -and $_.RemotePort -gt 50000) {
                                $isSuspicious = $true
                                $threats += "Unusual svchost.exe activity"
                            }
                            
                            # Check non-standard high ports
                            if ($_.RemotePort -gt 60000) {
                                $isSuspicious = $true
                                $threats += "Non-standard high port"
                            }
                            
                            [PSCustomObject]@{
                                protocol = "TCP"
                                localPort = $_.LocalPort
                                remoteIP = $_.RemoteAddress
                                remotePort = $_.RemotePort
                                state = $_.State
                                process = $processName
                                processPath = $processPath
                                pid = $_.OwningProcess
                                suspicious = $isSuspicious
                                threats = ($threats -join ", ")
                            }
                        }
                    
                    $suspiciousCount = ($connections | Where-Object { $_.suspicious }).Count
                    
                    $data = @{
                        timestamp = (Get-Date).ToString("o")
                        connections = $connections
                        totalCount = $connections.Count
                        suspiciousCount = $suspiciousCount
                    }
                    
                    $json = $data | ConvertTo-Json -Depth 10
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.ContentType = "application/json; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                    
                    $color = if ($suspiciousCount -eq 0) { "Green" } elseif ($suspiciousCount -lt 5) { "Yellow" } else { "Red" }
                    Write-Host "  [OK] Connections: $($connections.Count) total, $suspiciousCount suspicious" -ForegroundColor $color
                    
                } catch {
                    Write-Host "  [ERROR] Connections failed: $_" -ForegroundColor Red
                    $error = @{ error = $_.Exception.Message; connections = @() }
                    $json = $error | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.StatusCode = 500
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/api/firewall" {
                # REAL FIREWALL STATUS
                try {
                    $firewallStatus = Get-NetFirewallProfile -Profile Domain,Public,Private | 
                        Select-Object Name, Enabled
                    
                    $blockedRules = Get-NetFirewallRule | 
                        Where-Object { $_.Action -eq 'Block' -and $_.Enabled -eq $true } |
                        Measure-Object |
                        Select-Object -ExpandProperty Count
                    
                    $data = @{
                        enabled = ($firewallStatus | Where-Object { $_.Enabled -eq $true }).Count -gt 0
                        profiles = $firewallStatus
                        blockedRules = $blockedRules
                        timestamp = (Get-Date).ToString("o")
                    }
                    
                    $json = $data | ConvertTo-Json -Depth 5
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.ContentType = "application/json; charset=utf-8"
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                    
                    Write-Host "  [OK] Firewall: $($data.enabled) - Blocked Rules: $blockedRules" -ForegroundColor Green
                    
                } catch {
                    Write-Host "  [ERROR] Firewall check failed: $_" -ForegroundColor Red
                    $error = @{ error = $_.Exception.Message; enabled = $false }
                    $json = $error | ConvertTo-Json
                    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                    $response.StatusCode = 500
                    $response.ContentLength64 = $buffer.Length
                    $response.OutputStream.Write($buffer, 0, $buffer.Length)
                }
            }
            
            "/api/block-ip" {
                # BLOCK IP ADDRESS IN FIREWALL
                if ($request.HttpMethod -eq "POST") {
                    try {
                        $reader = New-Object System.IO.StreamReader($request.InputStream)
                        $body = $reader.ReadToEnd() | ConvertFrom-Json
                        $ip = $body.ip
                        
                        if ($ip) {
                            $ruleName = "Block_Threat_$($ip -replace '\.', '_')_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                            
                            New-NetFirewallRule -DisplayName $ruleName `
                                -Direction Outbound `
                                -Action Block `
                                -RemoteAddress $ip `
                                -Description "Blocked by Network Monitor - Suspicious activity detected" `
                                -ErrorAction Stop | Out-Null
                            
                            $data = @{
                                success = $true
                                message = "IP $ip blocked successfully"
                                ip = $ip
                                ruleName = $ruleName
                            }
                            
                            Write-Host "  [BLOCKED] IP: $ip" -ForegroundColor Red -BackgroundColor Yellow
                            
                        } else {
                            $data = @{
                                success = $false
                                message = "No IP provided"
                            }
                        }
                        
                        $json = $data | ConvertTo-Json
                        $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                        $response.ContentType = "application/json; charset=utf-8"
                        $response.ContentLength64 = $buffer.Length
                        $response.OutputStream.Write($buffer, 0, $buffer.Length)
                        
                    } catch {
                        Write-Host "  [ERROR] Block IP failed: $_" -ForegroundColor Red
                        $error = @{ 
                            success = $false
                            message = $_.Exception.Message 
                        }
                        $json = $error | ConvertTo-Json
                        $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                        $response.StatusCode = 500
                        $response.ContentLength64 = $buffer.Length
                        $response.OutputStream.Write($buffer, 0, $buffer.Length)
                    }
                }
            }
            
            default {
                # 404 Not Found
                $response.StatusCode = 404
                $content = "404 - Not Found: $path"
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
                Write-Host "  [404] $path" -ForegroundColor Yellow
            }
        }
        
        $response.Close()
    }
}
catch {
    Write-Host "`n[ERROR] Server error: $_" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Port $Port might be in use - try: .\unified-server.ps1 -Port 8081" -ForegroundColor Gray
    Write-Host "  2. Run PowerShell as Administrator" -ForegroundColor Gray
    Write-Host "  3. Check firewall settings" -ForegroundColor Gray
}
finally {
    $listener.Stop()
    Write-Host "`n====================================================" -ForegroundColor Cyan
    Write-Host "Server stopped." -ForegroundColor Yellow
    Write-Host "====================================================`n" -ForegroundColor Cyan
}
