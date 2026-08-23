# Network Security Monitoring Guide
## What to Watch for Attacks & Intrusions

---

## 🚨 Critical Security Indicators

### **Top Priority: What to Monitor During an Attack**

```
┌────────────────────────────────────────────────────────────┐
│           Attack Detection Hierarchy                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  🔴 CRITICAL (Immediate Action Required):                  │
│     • Unknown outbound connections                         │
│     • Connections to known malicious IPs                   │
│     • Unusual ports (23, 135, 445, 3389, 5900)            │
│     • Multiple failed login attempts                       │
│     • Sudden spike in network traffic                      │
│                                                            │
│  🟠 HIGH (Investigate Within Minutes):                     │
│     • New processes making network connections             │
│     • Connections from suspicious geo-locations            │
│     • Port scanning activity                               │
│     • Data exfiltration patterns                           │
│     • C2 (Command & Control) communication patterns        │
│                                                            │
│  🟡 MEDIUM (Monitor Closely):                              │
│     • Unusual DNS queries                                  │
│     • Encrypted traffic to unknown destinations            │
│     • Abnormal protocol usage                              │
│     • Connection time anomalies (3 AM traffic)             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 Security Dashboard - Key Metrics

### **What the Security Dashboard Shows:**

#### 1. **Active Threats Panel** (Most Important)
```
🚨 Active Threats:
├─ Suspicious Connections: Shows REAL-TIME malicious connections
├─ Port Scans Detected: Someone probing your network
└─ Failed Auth Attempts: Brute force attack attempts
```

#### 2. **Network Activity** (Context)
```
🌐 Network Activity:
├─ Total Connections: Normal = 10-50, Suspicious = 100+
├─ Unique IPs: Watch for sudden spikes
└─ Data Transferred: Unusual spikes = data theft
```

#### 3. **Anomalies** (Early Warning)
```
⚠️ Anomalies:
├─ Traffic Spikes: DDoS or data exfiltration
├─ Unknown Protocols: Non-standard communication
└─ Geo Anomalies: Connections from unexpected countries
```

#### 4. **Security Status**
```
🔒 Security Status:
├─ Firewall: Should always be ACTIVE
├─ Blocked IPs: Growing = active attack
└─ Last Scan: How fresh is the data
```

---

## 🔍 What Each Metric Means in Attack Context

### **Suspicious Connections** 🔴
```
What it shows: Number of connections to known bad IPs or unusual ports

Red Flags:
• > 0: You have a problem
• > 5: Active attack or malware
• > 20: Serious compromise

What to do:
1. Click "Block Suspicious IPs" immediately
2. Note the IP addresses
3. Check which process is making connections
4. Disconnect from internet if critical
```

### **Port Scans Detected** 🟠
```
What it shows: Someone is probing your open ports

Red Flags:
• 1-5: Reconnaissance phase (attacker is mapping)
• > 10: Active attack preparation
• Continuous: Automated botnet scan

What to do:
1. Note the source IP
2. Enable stealth mode in firewall
3. Close unnecessary ports
4. Watch for follow-up attacks
```

### **Failed Auth Attempts** 🔴
```
What it shows: Brute force login attempts

Red Flags:
• > 3 in quick succession: Active attack
• Same user, different IPs: Distributed attack
• Different users, same IP: Credential stuffing

What to do:
1. Lock affected accounts
2. Check for successful logins before attacks
3. Enable account lockout policies
4. Require password reset for affected accounts
```

### **Traffic Spikes** 🟠
```
What it shows: Sudden increase in network usage

Red Flags:
• Outbound spike: Data exfiltration or botnet
• Inbound spike: DDoS attack
• Both: Active compromise

What to do:
1. Check which process is using bandwidth
2. Block the process if malicious
3. Capture traffic with Wireshark
4. Disconnect if exfiltration suspected
```

### **Geo Anomalies** 🟡
```
What it shows: Connections from unexpected locations

Red Flags:
• Connections from China/Russia (if you're not there)
• Multiple countries simultaneously
• Countries known for cyber attacks

What to do:
1. Verify if you use services from those countries
2. Block entire country ranges if not needed
3. Check for compromised accounts
```

---

## 🎯 Attack Patterns to Recognize

### **Pattern 1: Initial Compromise**
```
Timeline:
1. Port scan detected (reconnaissance)
2. Failed auth attempts (trying to get in)
3. Successful connection to suspicious port
4. New process making outbound connections

Action: Disconnect immediately, investigate process
```

### **Pattern 2: Data Exfiltration**
```
Timeline:
1. Unusual outbound connection established
2. Large data transfer to unknown IP
3. Connection persists for extended time
4. Multiple files being accessed rapidly

Action: Kill process, block IP, check what was accessed
```

### **Pattern 3: Botnet/Malware**
```
Timeline:
1. Connection to known C2 server
2. Regular periodic connections (beaconing)
3. Downloads from suspicious sources
4. Lateral movement attempts (scanning local network)

Action: Full system scan, isolate machine, wipe if necessary
```

### **Pattern 4: Ransomware**
```
Timeline:
1. Suspicious email attachment opened
2. Outbound connection to C2 server
3. Encryption process starts (high CPU + disk)
4. Network shares being accessed
5. Ransom note appears

Action: DISCONNECT IMMEDIATELY, do not pay, restore from backup
```

---

## 🔍 Deep Dive: Suspicious Indicators

### **IP Address Analysis**

```powershell
# Check IP reputation (PowerShell)
$ip = "185.220.100.240"

# Method 1: nslookup
nslookup $ip

# Method 2: Online lookup
Start-Process "https://www.abuseipdb.com/check/$ip"

# Method 3: Whois
whois $ip
```

**Known Malicious IP Ranges:**
```
Tor Exit Nodes:
• 185.220.x.x
• 199.249.x.x

Common Attack Sources:
• 45.x.x.x (cheap VPS providers)
• 104.244.x.x (known botnet)
• 162.243.x.x (compromised servers)

Legitimate but watch:
• 8.8.8.8 (Google DNS - OK)
• 1.1.1.1 (Cloudflare DNS - OK)
• 13.x.x.x (Amazon AWS - Depends)
```

### **Port Analysis**

```
Suspicious Ports (Never Normal):
┌──────┬────────────────────┬────────────────────────┐
│ Port │ Service            │ Why Suspicious         │
├──────┼────────────────────┼────────────────────────┤
│ 23   │ Telnet             │ Unencrypted, old       │
│ 135  │ Windows RPC        │ Exploitation vector    │
│ 445  │ SMB                │ WannaCry, ransomware   │
│ 3389 │ RDP                │ Brute force target     │
│ 5900 │ VNC                │ Remote access          │
│ 6667 │ IRC                │ Botnet C2              │
│ 31337│ Back Orifice       │ Classic backdoor       │
└──────┴────────────────────┴────────────────────────┘

Legitimate Ports (Usually Safe):
┌──────┬────────────────────┬────────────────────────┐
│ 80   │ HTTP               │ Web traffic            │
│ 443  │ HTTPS              │ Secure web traffic     │
│ 53   │ DNS                │ Domain resolution      │
│ 123  │ NTP                │ Time synchronization   │
│ 25   │ SMTP               │ Email (outbound)       │
└──────┴────────────────────┴────────────────────────┘
```

### **Process Analysis**

```
Legitimate Processes (Normal Network Activity):
• chrome.exe, firefox.exe, msedge.exe (browsers)
• OneDrive.exe (cloud sync)
• Teams.exe, Slack.exe (communication)
• Steam.exe (gaming)
• Windows Update services

Suspicious Processes:
• svchost.exe connecting to unusual ports
• cmd.exe or powershell.exe with network activity
• Unknown .exe from Temp or AppData folders
• Processes with random names (aksdj.exe)
• Multiple instances of same process
```

---

## 🛡️ Response Procedures

### **Level 1: Suspicious Activity Detected**

```
✅ Immediate Actions:
1. Click "Block Suspicious IPs" in dashboard
2. Export security log (evidence)
3. Take screenshot of suspicious activity
4. Continue monitoring

⏰ Within 5 Minutes:
1. Identify which process is responsible
2. Check if process is legitimate
3. Google the process name + "malware"
4. Scan with antivirus

📋 Within 30 Minutes:
1. Review recent software installations
2. Check startup programs
3. Review browser extensions
4. Change important passwords (if compromised)
```

### **Level 2: Active Attack Confirmed**

```
🚨 IMMEDIATE (30 seconds):
1. Disconnect from internet/WiFi
2. Do NOT shut down (preserves memory evidence)
3. Take photos of screen with phone

⚠️ Within 2 Minutes:
1. Open Task Manager
2. Note all running processes
3. Kill suspicious process (not svchost.exe!)
4. Save any open work

📞 Within 10 Minutes:
1. Call IT department (if work computer)
2. Change passwords from different device
3. Enable 2FA on all accounts
4. Notify relevant parties
```

### **Level 3: System Compromised**

```
🔴 CRITICAL (Immediate):
1. DISCONNECT ALL NETWORK CABLES
2. Turn off WiFi
3. DO NOT turn off computer yet
4. Photo evidence with phone
5. Call professional help

🛑 Do NOT:
• Try to "fix" it yourself (makes forensics harder)
• Delete files (destroys evidence)
• Pay ransom (no guarantee)
• Reconnect to network

✅ DO:
• Preserve evidence
• Contact cyber security professional
• File police report (serious attacks)
• Notify affected parties (data breach)
• Restore from clean backup (after wiping)
```

---

## 📱 Using the Security Dashboard

### **How to Launch:**

```powershell
cd D:\code_ai\code\project-designs\connection-monitoring-for-network\dashboard

# Open security dashboard
start security-dashboard.html

# Or with real data (if you set up backend)
.\security-server.ps1
```

### **What to Watch:**

```
🟢 Normal Operation:
• Suspicious Connections: 0
• Port Scans: 0
• Threat Level: LOW
• Connections to known IPs (Google, Microsoft, etc.)

🟡 Minor Concern:
• Suspicious Connections: 1-2 (investigate)
• Port Scans: 1-3 (recon attempt)
• Threat Level: MEDIUM
• Unknown but not malicious IPs

🟠 Serious Concern:
• Suspicious Connections: 3-10
• Port Scans: 5+
• Threat Level: HIGH
• Multiple known malicious IPs

🔴 CRITICAL:
• Suspicious Connections: 10+
• Active data exfiltration
• Threat Level: CRITICAL
• Immediate action required
```

---

## 🔧 Advanced: Real Network Monitoring

### **Get Real Connection Data:**

```powershell
# Show all active connections
netstat -ano

# Show connections with process names
Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | 
    ForEach-Object {
        $_ | Add-Member -NotePropertyName ProcessName -NotePropertyValue (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name -PassThru
    } | Format-Table

# Monitor continuously
while($true) {
    Clear-Host
    Get-NetTCPConnection | Where-Object {$_.State -eq 'Established'} | 
        Select-Object RemoteAddress, RemotePort, State | 
        Format-Table
    Start-Sleep -Seconds 2
}
```

### **Block Malicious IP in Firewall:**

```powershell
# Block specific IP
New-NetFirewallRule -DisplayName "Block Malicious IP" -Direction Outbound -Action Block -RemoteAddress 185.220.100.240

# Block entire range
New-NetFirewallRule -DisplayName "Block Malicious Range" -Direction Outbound -Action Block -RemoteAddress 185.220.0.0/16

# List blocked IPs
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Block*"}

# Remove rule
Remove-NetFirewallRule -DisplayName "Block Malicious IP"
```

---

## 📊 Data Collection for Analysis

### **What to Capture During Attack:**

```
1. Network Traffic (Wireshark):
   • Capture during suspicious activity
   • Save as: attack-YYYY-MM-DD-HHmm.pcapng
   • Include 5 minutes before/after

2. Active Connections:
   • Screenshot of netstat output
   • Export dashboard security log
   • Note all suspicious IPs

3. Process Information:
   • Task Manager screenshot
   • Note suspicious processes and PIDs
   • File locations of suspicious .exe

4. System Logs:
   • Event Viewer → Security logs
   • Export last 1000 events
   • Look for failed logins

5. Firewall Logs:
   • C:\Windows\System32\LogFiles\Firewall\pfirewall.log
   • Shows blocked connections
```

---

## 🎓 Learn to Read the Data

### **Dashboard Charts:**

**Connection Activity Over Time:**
```
Normal Pattern:
  ▁▁▂▂▂▃▃▃▂▂▂▁▁  (Gradual curves)

Attack Pattern:
  ▁▁▁▁████████▁▁  (Sudden spike)
  
  ▁▁▁▁▁▁▃▃▃▃▃▃▃▃  (Sustained high traffic)
```

**Top Source Countries/IPs:**
```
Normal: Mostly local/known services
Attack: Multiple unknown IPs, foreign countries
```

### **Suspicious Activity Log:**

```
Read it like this:

[Time] [IP:Port] [Severity] [Threat]

Example:
10:23:45 185.220.100.240:31337 HIGH Known malicious IP, Backdoor port

Translation:
• Time: When it happened
• IP: Who is doing it
• Port 31337: Back Orifice backdoor (very bad!)
• Severity HIGH: Immediate action needed
```

---

## 🚨 Common False Positives

**Not Every Alert is an Attack:**

```
False Positive Examples:

1. "Suspicious Port 3389 (RDP)"
   • If YOU use Remote Desktop: Normal
   • If you DON'T use it: Suspicious

2. "Connection to Unknown IP"
   • Could be CDN (Content Delivery Network)
   • Could be legit service you use
   • Google the IP before panicking

3. "Traffic Spike"
   • Windows Update downloading: Normal
   • Cloud backup: Normal
   • Netflix streaming: Normal
   • At 3 AM: Suspicious

4. "Multiple Connections"
   • Browser opening many tabs: Normal
   • One process, many connections: Suspicious
```

**How to Verify:**
1. Check if YOU initiated the activity
2. Google the IP address
3. Check process name
4. Look at timing (expected vs. unexpected)

---

## 📚 Resources & Tools

### **Online IP Checkers:**
- https://www.abuseipdb.com/ (IP reputation)
- https://www.virustotal.com/ (IP/domain check)
- https://www.shodan.io/ (What's exposed)

### **Process Checkers:**
- https://www.processlibrary.com/ (Is this process legit?)
- Task Manager → Details tab (Check signatures)

### **Security Tools:**
- Windows Defender (built-in)
- Malwarebytes (malware scanner)
- Wireshark (traffic analysis)
- GlassWire (visual firewall)

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│         SECURITY DASHBOARD QUICK REFERENCE              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔴 IMMEDIATE THREAT:                                   │
│     • Suspicious Connections > 5                        │
│     • Known malicious IP detected                       │
│     • Data exfiltration pattern                         │
│     → Disconnect, block, investigate                    │
│                                                         │
│  🟠 INVESTIGATE NOW:                                    │
│     • Suspicious Connections 1-5                        │
│     • Port scans detected                               │
│     • Unusual traffic spike                             │
│     → Monitor closely, gather evidence                  │
│                                                         │
│  🟡 MONITOR:                                            │
│     • Geo anomalies                                     │
│     • Unknown protocols                                 │
│     • Unusual connection times                          │
│     → Continue monitoring, review later                 │
│                                                         │
│  🟢 NORMAL:                                             │
│     • All metrics at 0                                  │
│     • Known IPs only                                    │
│     • Threat Level: LOW                                 │
│     → All good, routine monitoring                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**Document Created:** August 2026
**Last Updated:** August 2026
**Version:** 1.0
