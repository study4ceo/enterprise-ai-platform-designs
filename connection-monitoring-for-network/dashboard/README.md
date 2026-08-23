# Network Monitoring Dashboard

## 🚀 Quick Start

### Option 1: Run with Real Data (Recommended)

Open PowerShell and run:

```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\server.ps1
```

This will:
1. Start a local web server on http://localhost:8080
2. Automatically open your browser
3. Provide **real network monitoring data** from your system

### Option 2: Open Directly (Simulated Data)

Simply open `index.html` in your browser:
- Double-click `index.html`
- Or drag it into your browser

This will use **simulated data** (good for testing the interface).

---

## 📊 Dashboard Features

### Real-Time Monitoring
- **Connection Status**: Live latency, average latency, packet loss
- **System Resources**: CPU, Memory, Network I/O usage
- **Statistics**: Total tests, successful/failed connections

### Visual Charts
- **Latency Over Time**: Line chart showing connection quality
- **System Resources**: CPU and Memory usage trends

### Recent Activity
- **Ping Results**: Last 20 ping tests with timestamps
- **Color-coded**: Green = success, Red = failure

### Alerts
- Automatic alerts for:
  - High latency (>200ms)
  - Connection failures
  - High CPU usage (>80%)
  - High memory usage (>90%)

### Data Management
- **Export**: Download all data as CSV
- **Clear**: Reset all statistics
- **Auto-save**: Data persists between sessions (localStorage)

---

## 🎮 Controls

### Buttons

**▶ Start Monitoring**
- Begins network testing every 5 seconds
- Updates all charts and metrics in real-time

**⏸ Stop Monitoring**
- Pauses monitoring
- Data is preserved

**💾 Export Data**
- Downloads CSV file with all test results
- Includes: timestamp, latency, success, CPU, memory, network I/O

**🗑 Clear Data**
- Resets all statistics and charts
- Requires confirmation

---

## 📈 Understanding the Data

### Latency (Response Time)
```
Excellent: < 20ms     (Green)
Good:      20-50ms    (Green)
Acceptable: 50-100ms  (Yellow)
Slow:      100-200ms  (Yellow)
Very Slow: > 200ms    (Red)
Timeout:   > 500ms    (Red)
```

### Packet Loss
```
Perfect:    0%        (Green)
Acceptable: 0-2%      (Green)
Concerning: 2-5%      (Yellow)
Poor:       5-10%     (Yellow)
Critical:   > 10%     (Red)
```

### System Resources
```
CPU Usage:
  Normal:  < 50%      (Green)
  High:    50-80%     (Yellow)
  Critical: > 80%     (Red)

Memory Usage:
  Normal:  < 70%      (Green)
  High:    70-90%     (Yellow)
  Critical: > 90%     (Red)
```

---

## 🔧 Technical Details

### Architecture

```
┌─────────────────────────────────────────┐
│         Browser (Frontend)              │
│  ┌───────────────────────────────────┐  │
│  │  index.html (UI)                  │  │
│  │  app.js (Logic + Charts)          │  │
│  │  Chart.js (Visualization)         │  │
│  └───────────────┬───────────────────┘  │
│                  │ HTTP requests         │
└──────────────────┼───────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    PowerShell Server (Backend)          │
│  ┌───────────────────────────────────┐  │
│  │  server.ps1                       │  │
│  │  • Serves web files               │  │
│  │  • /api/ping → Real ping test     │  │
│  │  • /api/resources → System stats  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### API Endpoints

**GET /api/ping**
```json
{
  "timestamp": "2026-08-23T10:30:00Z",
  "success": true,
  "latency": 45
}
```

**GET /api/resources**
```json
{
  "cpu": 35.5,
  "memory": 62.3,
  "networkIO": 234.5
}
```

---

## 🐛 Troubleshooting

### Dashboard Shows "Simulated Data"

**Problem**: Running without backend server

**Solution**: 
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\server.ps1
```

### Charts Not Updating

**Problem**: Monitoring not started

**Solution**: Click "▶ Start Monitoring" button

### PowerShell Server Won't Start

**Problem 1**: Port 8080 already in use

**Solution**: Use different port
```powershell
.\server.ps1 -Port 8081
```

**Problem 2**: Execution policy restriction

**Solution**: Allow script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Browser Opens but Shows Blank Page

**Problem**: Files not loaded

**Solution**: 
1. Check that you're in the correct directory
2. Refresh browser (Ctrl + F5)
3. Check browser console (F12) for errors

---

## 📁 File Structure

```
dashboard/
├── README.md          ← You are here
├── index.html         ← Dashboard UI
├── app.js             ← Dashboard logic
└── server.ps1         ← Backend server
```

---

## 🎨 Customization

### Change Monitoring Interval

Edit `app.js`, line 108:
```javascript
// Current: 5 seconds
monitoringInterval = setInterval(runNetworkTest, 5000);

// Change to 10 seconds
monitoringInterval = setInterval(runNetworkTest, 10000);
```

### Change Ping Target

Edit `server.ps1`, line 34:
```powershell
# Current: Google DNS
$pingResult = Test-Connection -ComputerName 8.8.8.8 -Count 1

# Change to Cloudflare
$pingResult = Test-Connection -ComputerName 1.1.1.1 -Count 1
```

### Add More Targets

You can modify the code to ping multiple targets and aggregate results.

---

## 💡 Tips for Best Results

1. **Run for Extended Period**: Let monitoring run for 30-60 minutes to see patterns
2. **Reproduce Issues**: Try to trigger connection drops while monitoring
3. **Export Data**: Save data before closing for later analysis
4. **Compare Times**: Check if drops occur at specific times (hourly, daily)
5. **Check Correlations**: See if CPU/Memory spikes coincide with drops

---

## 📊 What to Look For

### Connection Drop Patterns

**Pattern 1: Regular Intervals**
- Every hour → DHCP lease renewal
- Every 15 minutes → Router issue
- Every 30 seconds → WiFi interference

**Pattern 2: Random Drops**
- High packet loss → Network congestion
- Sudden spikes → Background downloads
- Gradual degradation → Hardware issue

**Pattern 3: Time-Based**
- Same time daily → Scheduled task (Windows Update, backups)
- Peak hours → ISP congestion
- After idle period → Power saving settings

---

## 🚀 Next Steps

After collecting data:

1. **Review the charts** for patterns
2. **Export CSV** for detailed analysis
3. **Share data** with me for diagnosis
4. **Try solutions** from main guide (NETWORK_MONITORING_GUIDE.md)

---

**Created**: August 2026
**Version**: 1.0
