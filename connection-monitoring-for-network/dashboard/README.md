# Network Monitoring Dashboard

Real-time network security and performance monitoring for Windows.

---

## 🚀 Quick Start

### Start Server:
```powershell
.\start-server.ps1
```

### Stop Server:
```powershell
.\stop-server.ps1
```
Or press `Ctrl+C` in the server window

### Open Dashboard:
```
http://localhost:8080
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `start-server.ps1` | **Start** the monitoring server |
| `stop-server.ps1` | **Stop** the monitoring server |
| `unified-server.ps1` | Main server (called by start-server) |
| `unified-dashboard.html` | Dashboard UI |
| `unified-app.js` | Dashboard logic |
| `HOW_TO_START.md` | Detailed usage guide |
| `STATUS.md` | Current system status |

---

## 🎯 Features

### Performance Monitoring
- Real-time ping tests
- CPU usage tracking
- Memory usage tracking  
- Network I/O monitoring

### Security Monitoring
- Active TCP connections
- Threat detection (malicious IPs, suspicious ports)
- Process tracking
- One-click IP blocking

### Analysis & Export
- Connection statistics
- Top processes
- Suspicious activity summary
- Export data as JSON

---

## 🔥 Attack Detection

The system automatically flags:
- **Known malicious IP ranges** (TOR exit nodes, botnets)
- **Suspicious ports** (23, 135, 445, 3389, etc.)
- **Unusual svchost behavior**
- **Non-standard high ports**

Suspicious connections appear in **RED** or **YELLOW** in the Security tab.

---

## 🛡️ Block Threats

Click the **"Block IP"** button next to any suspicious connection to:
1. Create a Windows Firewall rule
2. Block all traffic to that IP
3. Log the action

---

## ⚙️ Requirements

- Windows 10/11 or Windows Server
- PowerShell 5.1 or later
- Administrator rights (for blocking IPs)

---

## 🆘 Troubleshooting

### Port 8080 in use?
```powershell
.\unified-server.ps1 -Port 8081
```

### Can't stop server?
```powershell
.\stop-server.ps1
```

### Dashboard not loading?
1. Check server is running
2. Try http://localhost:8080
3. Check firewall settings

---

## 📖 Documentation

- `HOW_TO_START.md` - Complete usage guide
- `STATUS.md` - Current system status
- `../PRODUCTION_READY.md` - Full documentation
- `../SECURITY_MONITORING_GUIDE.md` - Security details

---

## ✅ No Mock Data

All data is **100% real** from Windows APIs:
- `Test-Connection` - Actual ping tests
- `Get-Counter` - Real system metrics
- `Get-NetTCPConnection` - Live connections
- `Get-NetFirewallProfile` - Firewall status
- `New-NetFirewallRule` - Actually blocks IPs

This is a **production-ready** monitoring system, not a demo.

---

**Made for real security monitoring. August 2026.**
