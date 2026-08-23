# How to Start the Network Monitoring Dashboard

## ✅ Server is Already Running!

Your server is **currently running** on port 8080.

---

## 🌐 Open Dashboard in Browser

**Just click this URL or paste in browser:**

```
http://localhost:8080
```

Or run this command:
```powershell
Start-Process "http://localhost:8080"
```

---

## 🎯 What You'll See

The dashboard has **3 tabs**:

### 1️⃣ **Performance Tab** (Blue)
- **Ping Test** - Tests connection to 8.8.8.8
- **CPU Usage** - Real-time processor load
- **Memory Usage** - RAM consumption
- **Network I/O** - Data transfer rate

### 2️⃣ **Security Tab** (Red) ⚠️ IMPORTANT
- **Active Connections** - All TCP connections on your system
- **Threat Detection** - Highlights suspicious connections:
  - 🔴 Red background = High threat (malicious IP)
  - 🟡 Yellow background = Medium threat (suspicious port)
- **Process Info** - Which program owns each connection
- **Block Button** - Click to block malicious IPs instantly

### 3️⃣ **Analysis Tab** (Green)
- **Connection Stats** - Protocols, top processes
- **Suspicious Activity** - Summary of threats
- **Export Data** - Download as JSON

---

## 🚨 How to Monitor for Attacks

1. **Go to Security Tab** (click "Security" at top)
2. **Look for colored rows**:
   - 🔴 **Red** = Dangerous (known malicious IP)
   - 🟡 **Yellow** = Suspicious (unusual port/behavior)
3. **Click "Block IP"** on any threat to add firewall rule
4. **Watch the counter** at top: "X suspicious connections detected"

---

## 🛑 Server Control

### Start the server:
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\start-server.ps1
```

### Stop the server:
**Option 1** - In the server window, press `Ctrl+C`

**Option 2** - Run the stop script:
```powershell
.\stop-server.ps1
```

### Alternative - Start on different port:
```powershell
.\unified-server.ps1 -Port 8081
```

---

## 📊 Real-Time Updates

The dashboard automatically refreshes:
- **Ping** - Every 5 seconds
- **Resources** - Every 3 seconds  
- **Connections** - Every 10 seconds
- **Firewall** - Every 30 seconds

---

## 🔍 What the Security Tab Shows

Each connection displays:
- **Remote IP** - Where the connection is going
- **Port** - Which service/port is being used
- **Process** - Program name (e.g., chrome.exe, svchost.exe)
- **PID** - Process ID
- **Threats** - Why it's flagged as suspicious

---

## ⚡ Quick Actions

### See All Connections
Just open the Security tab - it shows up to 100 active connections

### Block a Malicious IP
1. Find red/yellow row in Security tab
2. Click "Block IP" button
3. Confirm in popup
4. IP is instantly blocked in Windows Firewall

### Export Data
1. Go to Analysis tab
2. Click "Export Data" button
3. Save JSON file for later review

---

## 🎯 CURRENT STATUS

✅ **Server Running** on port 8080  
✅ **Dashboard Ready** at http://localhost:8080  
✅ **Monitoring Active** - Real data flowing  
✅ **Threat Detection** - Watching for attacks  

---

## 💡 Pro Tips

1. **Keep Security tab open** - This is where you'll see attacks
2. **Check regularly** - Threats can appear anytime
3. **Review blocked IPs** - Analysis tab shows statistics
4. **Export data daily** - Keep records of suspicious activity

---

## 🆘 Troubleshooting

### Dashboard won't load?
```powershell
# Check if server is running
Get-Process | Where-Object { $_.ProcessName -eq "powershell" }

# Restart if needed
.\unified-server.ps1
```

### Port 8080 already in use?
```powershell
# Use different port
.\unified-server.ps1 -Port 8081

# Then open: http://localhost:8081
```

### Need admin rights?
Right-click PowerShell → "Run as Administrator"

---

## 📞 Need Help?

Check these files:
- `STATUS.md` - Current system status
- `PRODUCTION_READY.md` - Full documentation
- `SECURITY_MONITORING_GUIDE.md` - Security details

---

**Ready to monitor! Open http://localhost:8080 now!** 🚀
