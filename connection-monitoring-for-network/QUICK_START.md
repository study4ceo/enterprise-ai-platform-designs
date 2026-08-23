# Quick Start Guide - Connection Monitoring

## 🎯 Choose Your Tool

### **Problem 1: Internet Keeps Dropping / Slow Connection**
**Use:** Performance Dashboard
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\server.ps1
```
Opens: http://localhost:8080
Shows: Latency, packet loss, connection quality

---

### **Problem 2: Suspicious Activity / Possible Attack**
**Use:** Security Dashboard
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\security-server.ps1
```
Opens: http://localhost:8081/security
Shows: Malicious IPs, port scans, suspicious connections

---

## 📊 Dashboard Comparison

| Feature | Performance (8080) | Security (8081) |
|---------|-------------------|-----------------|
| **Purpose** | ISP/Network issues | Attack detection |
| **Backend** | server.ps1 | security-server.ps1 |
| **Port** | 8080 | 8081 |
| **Data Source** | Ping tests, CPU/RAM | netstat, firewall |
| **Shows** | Latency, uptime | Threats, IPs, ports |

---

## 🚀 Running Both at Once

You can run BOTH simultaneously in different terminals:

**Terminal 1: Performance**
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\server.ps1
```

**Terminal 2: Security**
```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard
.\security-server.ps1
```

Now you have:
- http://localhost:8080 → Performance monitoring
- http://localhost:8081/security → Security monitoring

---

## 📖 Full Documentation

| File | What It Covers |
|------|---------------|
| `NETWORK_MONITORING_GUIDE.md` | Complete troubleshooting guide (100+ pages) |
| `SECURITY_MONITORING_GUIDE.md` | Attack detection guide (80+ pages) |
| `DASHBOARD_COMPARISON.md` | Which dashboard to use when |

---

## 🔧 Without Backend (Demo Mode)

Both dashboards can run WITHOUT a backend server (simulated data):

**Performance Dashboard:**
```powershell
start dashboard\index.html
```
Shows fake latency data (for testing UI)

**Security Dashboard:**
```powershell
start dashboard\security-dashboard.html
```
Shows fake attack data (for learning what attacks look like)

---

## ⚡ Summary

```
REAL DATA (Recommended):
• Performance: .\server.ps1          → Port 8080
• Security:    .\security-server.ps1 → Port 8081

DEMO MODE (No backend needed):
• Performance: start index.html
• Security:    start security-dashboard.html

BOTH = Complete monitoring!
```

---

**Your Question: "What was port 8080?"**

**Answer:**
- Port 8080 = Performance Dashboard backend
- Port 8081 = Security Dashboard backend (NEW!)
- They're DIFFERENT dashboards for DIFFERENT purposes
- Port 8080 does NOT work for security dashboard
- Each needs its own backend server

---

**Created:** August 2026
