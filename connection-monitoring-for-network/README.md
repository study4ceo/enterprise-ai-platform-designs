# Network Connection Monitoring Toolkit

## Quick Start

### Step 1: Run Basic Network Test

Open PowerShell and run:

```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network
.\monitor-network.ps1
```

This will monitor your connection for 60 minutes by default.

### Step 2: Analyze Connection Quality

```powershell
.\analyze-connection.ps1
```

This sends 100 pings and provides detailed statistics.

### Step 3: Monitor System Resources

```powershell
.\monitor-resources.ps1
```

This shows if CPU/RAM/Disk issues correlate with connection drops.

---

## Files in This Directory

```
connection-monitoring-for-network/
├── README.md                      ← You are here
├── NETWORK_MONITORING_GUIDE.md    ← Complete troubleshooting guide
├── monitor-network.ps1            ← Continuous network monitoring
├── analyze-connection.ps1         ← Connection quality analyzer
├── monitor-resources.ps1          ← System resource monitor
├── logs/                          ← Monitoring logs (created automatically)
└── captures/                      ← Wireshark captures (create manually)
```

---

## Recommended Workflow

### For Connection Drops:

1. **Start monitoring:**
   ```powershell
   .\monitor-network.ps1 -DurationMinutes 30
   ```

2. **Wait for a drop to occur**

3. **Check the log file** in `.\logs\` folder

4. **Look for patterns:**
   - Drops at same time every day?
   - All targets fail simultaneously?
   - High response times before drops?

### For Performance Issues:

1. **Run connection analysis:**
   ```powershell
   .\analyze-connection.ps1
   ```

2. **Check results:**
   - Packet loss > 2%? → Network issue
   - Average latency > 100ms? → Congestion
   - Intermittent? → WiFi interference

### For Root Cause:

1. **Run resource monitor:**
   ```powershell
   .\monitor-resources.ps1
   ```

2. **Watch for:**
   - CPU spike during drops?
   - Disk at 100%?
   - Network usage drops to zero?

---

## Need More Help?

Read the full guide: `NETWORK_MONITORING_GUIDE.md`

It covers:
- Wireshark installation and usage
- Alternative monitoring tools (GlassWire, TCPView)
- Common issues and solutions
- How to interpret results
- Advanced troubleshooting

---

## Tool Recommendations

**Easiest:** GlassWire (https://www.glasswire.com/)
- Visual graphs
- Real-time alerts
- No learning curve

**Most Powerful:** Wireshark (https://www.wireshark.org/)
- Packet-level analysis
- See everything
- Steep learning curve

**Lightest:** TCPView (https://learn.microsoft.com/en-us/sysinternals/downloads/tcpview)
- See active connections
- Minimal resource usage
- Portable (no install)

---

**Created:** August 2026
