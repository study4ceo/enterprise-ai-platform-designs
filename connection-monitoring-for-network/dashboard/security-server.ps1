# Security Monitoring Server
# Provides REAL network connection data for security dashboard

param(
    [int]$Port = 8081
)

Write-Host "Starting Security Monitoring Server..." -ForegroundColor Green
Write-Host "Port: $Port" -ForegroundColor Cyan
Write-Host "Opening browser..." -ForegroundColor Yellow

# Create HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")

# Known malicious IP ranges for detection
$maliciousRanges = @('185.220.', '45.95.', '104.244.', '162.243.')
$suspiciousPorts = @(23, 135, 445, 3389, 5900, 6667, 31337)

# IP reputation cache
$ipReputationCache = @{}

try {
    $listener.Start()
    Write-Host "`nServer started successfully!" -ForegroundColor Green
    Write-Host "Dashboard: http://localhost:$Port/security" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
    
    # Open browser
    Start-Process "http://localhost:$Port/security"
    
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $path = $request.Url.LocalPath
        
        # Routes
        if ($path -eq "/" -or $path -eq "/security") {
            # Serve security dashboard
            $htmlPath = Join-Path $PSScriptRoot "security-dashboard.html"
            if (Test-Path $htmlPath) {
                $content = Get-Content $htmlPath -Raw -Encoding UTF8
                # Inject real data indicator
                $content = $content -replace '<body>', '<body data-real-data="true">'
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                $response.ContentType = "text/html; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/security-app.js") {
            # Serve JavaScript
            $jsPath = Join-Path $PSScriptRoot "security-app.js"
            if (Test-Path $jsPath) {
                $content = Get-Content $jsPath -Raw -Encoding UTF8
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                $response.ContentType = "application/javascript; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/api/connections") {
            # Get REAL network connections
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API: /api/connections" -ForegroundColor Cyan
            
            try {
                # Get all TCP connections with process info
                $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | 
                    Select-Object -First 50 |
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
                        
                        # Check unusual svchost activity
                        if ($processName -eq "svchost" -and $_.RemotePort -gt 50000) {
                            $isSuspicious = $true
                            $threats += "Unusual svchost.exe activity"
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
                
                $data = @{
                    timestamp = (Get-Date).ToString("o")
                    connections = $connections
                    totalCount = $connections.Count
                    suspiciousCount = ($connections | Where-Object { $_.suspicious }).Count
                }
                
                $json = $data | ConvertTo-Json -Depth 10
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                $response.ContentType = "application/json; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
                
                Write-Host "  → Sent $($connections.Count) connections ($($data.suspiciousCount) suspicious)" -ForegroundColor Green
                
            } catch {
                Write-Host "  → Error: $_" -ForegroundColor Red
                $error = @{ error = $_.Exception.Message }
                $json = $error | ConvertTo-Json
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                $response.StatusCode = 500
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/api/firewall") {
            # Get firewall status
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API: /api/firewall" -ForegroundColor Cyan
            
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
                
                Write-Host "  → Firewall status sent" -ForegroundColor Green
                
            } catch {
                Write-Host "  → Error: $_" -ForegroundColor Red
                $error = @{ error = $_.Exception.Message }
                $json = $error | ConvertTo-Json
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                $response.StatusCode = 500
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/api/processes") {
            # Get processes with network activity
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API: /api/processes" -ForegroundColor Cyan
            
            try {
                $processes = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
                    Group-Object OwningProcess |
                    ForEach-Object {
                        $pid = $_.Name
                        $connectionCount = $_.Count
                        
                        try {
                            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                            if ($proc) {
                                [PSCustomObject]@{
                                    name = $proc.ProcessName
                                    pid = $pid
                                    path = $proc.Path
                                    connections = $connectionCount
                                    cpu = [math]::Round($proc.CPU, 2)
                                    memory = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                                }
                            }
                        } catch {}
                    } |
                    Where-Object { $_ -ne $null } |
                    Sort-Object connections -Descending |
                    Select-Object -First 20
                
                $data = @{
                    timestamp = (Get-Date).ToString("o")
                    processes = $processes
                }
                
                $json = $data | ConvertTo-Json -Depth 5
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                $response.ContentType = "application/json; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
                
                Write-Host "  → Sent $($processes.Count) processes" -ForegroundColor Green
                
            } catch {
                Write-Host "  → Error: $_" -ForegroundColor Red
                $error = @{ error = $_.Exception.Message }
                $json = $error | ConvertTo-Json
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
                $response.StatusCode = 500
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/api/block-ip") {
            # Block an IP address
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] API: /api/block-ip" -ForegroundColor Cyan
            
            if ($request.HttpMethod -eq "POST") {
                try {
                    $reader = New-Object System.IO.StreamReader($request.InputStream)
                    $body = $reader.ReadToEnd() | ConvertFrom-Json
                    $ip = $body.ip
                    
                    if ($ip) {
                        $ruleName = "Block_Malicious_$($ip -replace '\.', '_')"
                        
                        # Check if rule already exists
                        $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
                        
                        if (-not $existing) {
                            New-NetFirewallRule -DisplayName $ruleName `
                                -Direction Outbound `
                                -Action Block `
                                -RemoteAddress $ip `
                                -ErrorAction Stop | Out-Null
                            
                            $data = @{
                                success = $true
                                message = "IP $ip blocked successfully"
                                ip = $ip
                            }
                            
                            Write-Host "  → Blocked IP: $ip" -ForegroundColor Green
                        } else {
                            $data = @{
                                success = $true
                                message = "IP $ip already blocked"
                                ip = $ip
                            }
                            
                            Write-Host "  → IP already blocked: $ip" -ForegroundColor Yellow
                        }
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
                    Write-Host "  → Error blocking IP: $_" -ForegroundColor Red
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
        else {
            # 404
            $response.StatusCode = 404
            $content = "404 - Not Found"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        
        $response.Close()
    }
}
catch {
    Write-Host "`nError: $_" -ForegroundColor Red
}
finally {
    $listener.Stop()
    Write-Host "`nServer stopped." -ForegroundColor Yellow
}
