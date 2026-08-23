# Simple HTTP Server for Network Monitoring Dashboard
# Runs a local web server and provides real network monitoring data

param(
    [int]$Port = 8080
)

# Create HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")

try {
    $listener.Start()
    Write-Host "Dashboard server started!" -ForegroundColor Green
    Write-Host "Open your browser and go to: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow
    
    # Open browser automatically
    Start-Process "http://localhost:$Port"
    
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $path = $request.Url.LocalPath
        
        # Handle different endpoints
        if ($path -eq "/" -or $path -eq "/index.html") {
            # Serve index.html
            $htmlPath = Join-Path $PSScriptRoot "index.html"
            if (Test-Path $htmlPath) {
                $content = Get-Content $htmlPath -Raw -Encoding UTF8
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                $response.ContentType = "text/html; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/app.js") {
            # Serve app.js
            $jsPath = Join-Path $PSScriptRoot "app.js"
            if (Test-Path $jsPath) {
                $content = Get-Content $jsPath -Raw -Encoding UTF8
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                $response.ContentType = "application/javascript; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
        elseif ($path -eq "/api/ping") {
            # Perform real network test
            $pingResult = Test-Connection -ComputerName 8.8.8.8 -Count 1 -ErrorAction SilentlyContinue
            
            $data = @{
                timestamp = (Get-Date).ToString("o")
                success = $null -ne $pingResult
                latency = if ($pingResult) { $pingResult.ResponseTime } else { $null }
            }
            
            $json = $data | ConvertTo-Json
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
            $response.ContentType = "application/json; charset=utf-8"
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        elseif ($path -eq "/api/resources") {
            # Get real system resources
            $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
            $os = Get-CimInstance Win32_OperatingSystem
            $totalMem = $os.TotalVisibleMemorySize / 1MB
            $freeMem = $os.FreePhysicalMemory / 1MB
            $memUsed = (($totalMem - $freeMem) / $totalMem) * 100
            
            # Get network bytes
            $networkCounters = Get-Counter '\Network Interface(*)\Bytes Total/sec' -ErrorAction SilentlyContinue
            $networkIO = if ($networkCounters) {
                ($networkCounters.CounterSamples | Measure-Object -Property CookedValue -Sum).Sum / 1KB
            } else {
                0
            }
            
            $data = @{
                cpu = [math]::Round($cpu, 2)
                memory = [math]::Round($memUsed, 2)
                networkIO = [math]::Round($networkIO, 2)
            }
            
            $json = $data | ConvertTo-Json
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
            $response.ContentType = "application/json; charset=utf-8"
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        else {
            # 404 Not Found
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
    Write-Host "Error: $_" -ForegroundColor Red
}
finally {
    $listener.Stop()
    Write-Host "`nServer stopped." -ForegroundColor Yellow
}
