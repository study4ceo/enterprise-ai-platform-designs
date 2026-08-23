# Network Connection Monitoring & Troubleshooting Guide

## Purpose
Diagnose and identify the root cause of connection drops and network interruptions.

---

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [Built-in Windows Tools](#built-in-windows-tools)
3. [Wireshark Analysis](#wireshark-analysis)
4. [Alternative Tools](#alternative-tools)
5. [Automated Monitoring Scripts](#automated-monitoring-scripts)
6. [Analysis & Interpretation](#analysis-interpretation)
7. [Common Issues & Solutions](#common-issues-solutions)

---

## Quick Start

### Immediate Diagnosis (Run This Now)

```powershell
# Open PowerShell as Administrator and run:

# Test 1: Continuous ping to Google DNS (Ctrl+C to stop)
ping -t 8.8.8.8

# Test 2: Ping with timestamp logging
Test-Connection -ComputerName 8.8.8.8 -Continuous | 
    Select-Object @{n='Time';e={Get-Date -f 'yyyy-MM-dd HH:mm:ss'}}, 
                  @{n='Status';e={if($_.StatusCode -eq 0){'Success'}else{'Failed'}}}, 
                  ResponseTime | 
    Tee-Object -FilePath "D:\code_ai\code\project-designs\connection-monitoring-for-network\logs\network-test.txt"

# Test 3: Check network adapter status
Get-NetAdapter | Select Name, Status, LinkSpeed, MediaConnectionState
```

**What to look for:**
- ✗ `Request timed out` = Network drop
- ✗ High ResponseTime (>100ms normally, >200ms concerning)
- ✗ Status: Disconnected

---

## Built-in Windows Tools

### 1. Continuous Ping Monitor

```powershell
# Create log directory first
New-Item -ItemType Directory -Force -Path "D:\code_ai\code\project-designs\connection-monitoring-for-network\logs"

# Monitor multiple hosts
$hosts = @('8.8.8.8', '1.1.1.1', 'www.google.com')

foreach ($host in $hosts) {
    Write-Host "Testing $host..." -ForegroundColor Cyan
    Test-Connection -ComputerName $host -Count 4 | 
        Select-Object @{n='Target';e={$host}}, 
                      @{n='Time';e={Get-Date -f 'HH:mm:ss'}}, 
                      Address, ResponseTime
}
```

### 2. Network Statistics

```cmd
:: Run in CMD (not PowerShell)

:: Real-time network stats (updates every 5 seconds)
netstat -e 5

:: Show active connections
netstat -ano

:: Show routing table
route print

:: Show DNS cache
ipconfig /displaydns
```

### 3. Performance Monitor (PerfMon)

```powershell
# Open Resource Monitor
perfmon /res

# Or create custom monitoring
perfmon
```

**Steps:**
1. Press `Win + R`
2. Type: `perfmon /res`
3. Go to **Network** tab
4. Watch during connection drops

**What to monitor:**
- Network utilization %
- TCP connections active
- Packet errors

### 4. Event Viewer (Check System Logs)

```powershell
# Open Event Viewer
eventvwr

# Or query via PowerShell
Get-EventLog -LogName System -Newest 100 | 
    Where-Object {$_.Source -like "*network*" -or $_.Source -like "*tcpip*"} |
    Select-Object TimeGenerated, Source, Message |
    Format-Table -AutoSize
```

---

## Wireshark Analysis

### Installation

**Download:** https://www.wireshark.org/download.html

**Installation Steps:**
1. Download Windows Installer (64-bit)
2. Run installer (accept defaults)
3. Install Npcap when prompted (required for packet capture)
4. Restart if prompted

### Basic Capture

**Step-by-Step:**

1. **Launch Wireshark**
2. **Select Interface:**
   - WiFi: Look for "Wi-Fi" or "Wireless"
   - Ethernet: Look for "Ethernet" or "Local Area Connection"
   - Select the one showing activity (blue graph)

3. **Start Capture:**
   - Click the blue shark fin icon (Start Capturing)
   - Or press `Ctrl + E`

4. **Capture During Drop:**
   - Let it run for 5-10 minutes
   - Try to trigger the connection drop
   - Perform actions that usually cause drops

5. **Stop Capture:**
   - Click red square icon
   - Or press `Ctrl + E`

6. **Save Capture:**
   - File → Save As
   - Location: `D:\code_ai\code\project-designs\connection-monitoring-for-network\captures\`
   - Filename: `capture-YYYY-MM-DD-HHmm.pcapng`

### Useful Wireshark Filters

```
Display Filters (enter in top filter bar):

# Show only your traffic to/from internet
ip.addr == YOUR_IP_ADDRESS

# Show connection failures
tcp.analysis.flags

# Show retransmissions (indicates network problems)
tcp.analysis.retransmission

# Show DNS queries
dns

# Show TLS/SSL handshakes
tls.handshake.type == 1

# Show HTTP traffic
http

# Show only errors
tcp.analysis.flags && !tcp.analysis.window_update

# Show traffic to specific domain
dns.qry.name contains "anthropic.com"

# Show high latency (SYN to SYN-ACK > 100ms)
tcp.time_delta > 0.1 && tcp.flags.syn == 1
```

### What to Look For

**Connection Issues:**
```
Symptom                          | Wireshark Filter           | Meaning
---------------------------------|----------------------------|---------------------------
Slow responses                   | tcp.time_delta > 0.5       | High latency
Connection drops                 | tcp.flags.reset == 1       | Connections being reset
Packet loss                      | tcp.analysis.retransmission| Packets need resending
DNS failures                     | dns.flags.rcode != 0       | Can't resolve domains
TLS errors                       | tls.alert_message          | Certificate/encryption issues
```

---

## Alternative Tools

### 1. GlassWire (Recommended for Beginners)

**Website:** https://www.glasswire.com/

**Features:**
- ✓ Visual network activity graph
- ✓ Real-time alerts for new connections
- ✓ Shows which apps use network
- ✓ Firewall built-in
- ✓ Beautiful, easy-to-understand UI

**Installation:**
1. Download from website
2. Install (free version available)
3. Launch GlassWire
4. Go to "Graph" tab to see network activity

**Use Case:**
- Monitor what's happening when connection drops
- See if specific app causes issues
- Block suspicious connections

### 2. TCPView (Microsoft Sysinternals)

**Download:** https://learn.microsoft.com/en-us/sysinternals/downloads/tcpview

**Features:**
- ✓ Shows all TCP/UDP connections in real-time
- ✓ Color-coded (green=new, red=closed)
- ✓ Lightweight, no install needed
- ✓ Can close connections directly

**Usage:**
1. Download `TCPView.zip`
2. Extract to: `D:\code_ai\code\project-designs\connection-monitoring-for-network\tools\`
3. Run `Tcpview.exe`
4. Sort by "State" column
5. Watch for connections closing (red) during drops

### 3. NetLimiter

**Website:** https://www.netlimiter.com/

**Features:**
- Shows bandwidth usage per application
- Can limit or block apps
- Traffic statistics

**Use Case:**
- Find which app is hogging bandwidth
- Block background updates during work

### 4. PingPlotter

**Website:** https://www.pingplotter.com/

**Features:**
- Visual ping + traceroute over time
- Identifies where packet loss occurs (ISP, router, etc.)
- Timeline view

**Use Case:**
- Diagnose if problem is local network or ISP

---

## Automated Monitoring Scripts

### Script 1: Continuous Network Monitor

Save as: `monitor-network.ps1`

```powershell
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
```

**Run it:**
```powershell
# Navigate to directory
cd D:\code_ai\code\project-designs\connection-monitoring-for-network

# Run for 60 minutes (default)
.\monitor-network.ps1

# Or specify duration
.\monitor-network.ps1 -DurationMinutes 120
```

### Script 2: Connection Quality Analyzer

Save as: `analyze-connection.ps1`

```powershell
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
```

**Run it:**
```powershell
.\analyze-connection.ps1
```

### Script 3: System Resource Monitor During Drops

Save as: `monitor-resources.ps1`

```powershell
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
```

---

## Analysis & Interpretation

### Understanding Ping Results

```
Response Time Interpretation:
┌─────────────────┬──────────────┬─────────────────────────────┐
│ Response Time   │ Quality      │ Meaning                     │
├─────────────────┼──────────────┼─────────────────────────────┤
│ < 20ms          │ Excellent    │ Local network / same city   │
│ 20-50ms         │ Good         │ Regional connection         │
│ 50-100ms        │ Acceptable   │ Cross-country               │
│ 100-200ms       │ Slow         │ International / congestion  │
│ > 200ms         │ Very Slow    │ Satellite / severe issues   │
│ Request timeout │ Failed       │ Connection lost             │
└─────────────────┴──────────────┴─────────────────────────────┘

Packet Loss Interpretation:
┌──────────────┬──────────────┬─────────────────────────────┐
│ Packet Loss  │ Quality      │ Action Needed               │
├──────────────┼──────────────┼─────────────────────────────┤
│ 0%           │ Perfect      │ None                        │
│ 0-2%         │ Acceptable   │ Monitor                     │
│ 2-5%         │ Concerning   │ Check WiFi signal           │
│ 5-10%        │ Poor         │ Investigate network         │
│ > 10%        │ Critical     │ Call ISP / replace hardware │
└──────────────┴──────────────┴─────────────────────────────┘
```

### Common Patterns

**Pattern 1: Intermittent Drops Every X Minutes**
```
Likely Causes:
• ISP modem/router rebooting
• DHCP lease renewal
• Scheduled task (Windows Update, antivirus scan)
• WiFi interference (microwave, neighbor's network)

Solution:
• Check router logs
• Check Windows Task Scheduler
• Change WiFi channel
```

**Pattern 2: High Latency, No Drops**
```
Likely Causes:
• Network congestion (too many users)
• Background downloads (Windows Update, cloud sync)
• QoS settings prioritizing other traffic
• ISP throttling

Solution:
• Check bandwidth usage (Task Manager → Performance → Network)
• Pause cloud syncs (OneDrive, Dropbox)
• Test at different times of day
```

**Pattern 3: Sudden Complete Loss**
```
Likely Causes:
• WiFi signal lost (too far from router)
• Ethernet cable disconnected
• Driver crash
• Firewall blocking

Solution:
• Check physical connections
• Check Device Manager for errors
• Temporarily disable firewall/antivirus
```

---

## Common Issues & Solutions

### Issue 1: WiFi Keeps Disconnecting

**Diagnosis:**
```powershell
# Check WiFi signal strength
netsh wlan show interfaces

# Look for "Signal" line (should be >70%)
```

**Solutions:**
1. Move closer to router
2. Change WiFi channel (router settings)
3. Update WiFi driver:
   ```powershell
   # Open Device Manager
   devmgmt.msc
   
   # Right-click WiFi adapter → Update driver
   ```
4. Disable power saving:
   ```powershell
   # Device Manager → WiFi adapter → Properties
   # Power Management → Uncheck "Allow computer to turn off this device"
   ```

### Issue 2: High Latency / Lag Spikes

**Diagnosis:**
```powershell
# Check what's using network
Get-NetTCPConnection | Group-Object State | Select Name, Count

# Check for Windows Update
Get-WindowsUpdate -Online
```

**Solutions:**
1. Pause Windows Update:
   ```
   Settings → Windows Update → Pause updates for 7 days
   ```
2. Close bandwidth-heavy apps (Chrome, OneDrive, Steam)
3. Restart router (unplug 30 seconds, plug back in)

### Issue 3: DNS Issues (Can't Reach Websites)

**Diagnosis:**
```powershell
# Test DNS resolution
nslookup google.com

# Flush DNS cache
ipconfig /flushdns
```

**Solutions:**
1. Change DNS servers to Google:
   ```powershell
   # Open Network Connections
   ncpa.cpl
   
   # Right-click adapter → Properties → IPv4 → Use following DNS
   # Preferred: 8.8.8.8
   # Alternate: 8.8.4.4
   ```

2. Or use Cloudflare DNS: `1.1.1.1` and `1.0.0.1`

### Issue 4: Firewall/Antivirus Blocking

**Diagnosis:**
```powershell
# Check Windows Firewall logs
C:\Windows\System32\LogFiles\Firewall\pfirewall.log

# Test with firewall temporarily disabled
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Re-enable after test
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

**Solutions:**
1. Add exception for your app in Windows Defender Firewall
2. Temporarily disable third-party antivirus (Avast, Norton, etc.)
3. Check if VPN is causing issues (disconnect VPN, test)

---

## Next Steps

1. **Run Immediate Tests:**
   ```powershell
   cd D:\code_ai\code\project-designs\connection-monitoring-for-network
   .\monitor-network.ps1 -DurationMinutes 30
   ```

2. **Capture Wireshark Data:**
   - Install Wireshark
   - Capture for 10-15 minutes during typical usage
   - Save to `.\captures\` folder
   - Share path with me for analysis

3. **Monitor Resources:**
   ```powershell
   .\monitor-resources.ps1
   ```
   Watch if CPU/Disk spikes correlate with connection drops

4. **Review Logs:**
   - Check `.\logs\` folder after monitoring
   - Look for patterns (drops at same time every day?)

---

## Contact & Support

If you need help analyzing results:
1. Share log files from `.\logs\` directory
2. Share Wireshark captures from `.\captures\` directory
3. Describe when drops occur (time of day, during specific activities, etc.)

I can analyze the data and identify the root cause!

---

**Document Created:** August 2026
**Last Updated:** August 2026
