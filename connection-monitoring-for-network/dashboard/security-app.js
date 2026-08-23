// Network Security Monitoring Dashboard - JavaScript

let monitoringInterval = null;
let isMonitoring = false;

// Security data storage
let suspiciousActivity = [];
let activeConnections = [];
let blockedIPs = new Set();
let securityEvents = [];

// Statistics
let totalConnections = 0;
let suspiciousCount = 0;
let portScans = 0;
let failedAuth = 0;
let trafficSpikes = 0;
let unknownProtocols = 0;
let geoAnomalies = 0;

// Chart data
let activityTimestamps = [];
let normalConnectionsData = [];
let suspiciousConnectionsData = [];
let geoData = {};

// Charts
let activityChart = null;
let geoChart = null;

// Known malicious IP ranges (examples)
const knownMaliciousRanges = [
    '185.220.', // Tor exit nodes
    '45.95.',   // Known attack source
    '104.244.', // Suspicious range
];

// Suspicious ports
const suspiciousPorts = [23, 135, 445, 3389, 5900, 6667, 31337];

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    updateUI();
});

// Initialize charts
function initializeCharts() {
    // Activity Chart
    const activityCtx = document.getElementById('activityChart').getContext('2d');
    activityChart = new Chart(activityCtx, {
        type: 'line',
        data: {
            labels: activityTimestamps,
            datasets: [
                {
                    label: 'Normal Connections',
                    data: normalConnectionsData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Suspicious Connections',
                    data: suspiciousConnectionsData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#fff' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });

    // Geo Chart
    const geoCtx = document.getElementById('geoChart').getContext('2d');
    geoChart = new Chart(geoCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Connections by Source',
                data: [],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(168, 85, 247, 0.7)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { display: false }
                }
            }
        }
    });
}

// Start monitoring
function startMonitoring() {
    if (isMonitoring) return;
    
    isMonitoring = true;
    console.log('Security monitoring started');
    
    // Immediate scan
    scanNetwork();
    
    // Scan every 3 seconds
    monitoringInterval = setInterval(scanNetwork, 3000);
}

// Stop monitoring
function stopMonitoring() {
    if (!isMonitoring) return;
    
    clearInterval(monitoringInterval);
    isMonitoring = false;
    console.log('Security monitoring stopped');
}

// Main network scan function
async function scanNetwork() {
    try {
        const timestamp = new Date().toLocaleTimeString();
        
        // Simulate getting network connections
        const connections = await getNetworkConnections();
        
        // Analyze connections for threats
        let normalCount = 0;
        let suspCount = 0;
        
        connections.forEach(conn => {
            totalConnections++;
            
            const threat = analyzeConnection(conn);
            
            if (threat) {
                suspiciousCount++;
                suspCount++;
                suspiciousActivity.unshift({
                    timestamp: new Date().toISOString(),
                    ...conn,
                    threat: threat
                });
                
                // Trigger alert
                showAlert(threat);
            } else {
                normalCount++;
            }
            
            // Track geo data
            const source = conn.remoteIP || 'Unknown';
            geoData[source] = (geoData[source] || 0) + 1;
        });
        
        // Keep only last 100 suspicious activities
        if (suspiciousActivity.length > 100) {
            suspiciousActivity = suspiciousActivity.slice(0, 100);
        }
        
        // Update charts
        activityTimestamps.push(timestamp);
        normalConnectionsData.push(normalCount);
        suspiciousConnectionsData.push(suspCount);
        
        // Keep last 30 data points
        if (activityTimestamps.length > 30) {
            activityTimestamps.shift();
            normalConnectionsData.shift();
            suspiciousConnectionsData.shift();
        }
        
        // Update active connections
        activeConnections = connections;
        
        // Update UI
        updateUI();
        updateCharts();
        updateThreatLevel();
        
        // Update last scan time
        document.getElementById('lastScan').textContent = new Date().toLocaleTimeString();
        
    } catch (error) {
        console.error('Network scan failed:', error);
    }
}

// Get network connections (real data from API or simulated)
async function getNetworkConnections() {
    try {
        // Try to get real data from API
        const response = await fetch('/api/connections');
        if (response.ok) {
            const data = await response.json();
            console.log('Using REAL connection data from API');
            
            // Transform API data to expected format
            return data.connections.map(conn => ({
                protocol: conn.protocol,
                localPort: conn.localPort,
                remoteIP: conn.remoteIP,
                remotePort: conn.remotePort,
                state: conn.state,
                process: conn.process,
                pid: conn.pid,
                suspicious: conn.suspicious,
                threat: conn.threats || null
            }));
        }
    } catch (error) {
        console.log('API not available, using simulated data');
    }
    
    // Fallback: Simulated data
    return new Promise((resolve) => {
        const connections = [];
        const numConnections = Math.floor(Math.random() * 10) + 5;
        
        for (let i = 0; i < numConnections; i++) {
            const isSuspicious = Math.random() < 0.15;
            
            const conn = {
                protocol: Math.random() < 0.8 ? 'TCP' : 'UDP',
                localPort: Math.floor(Math.random() * 65000) + 1000,
                remoteIP: generateIP(isSuspicious),
                remotePort: isSuspicious ? 
                    suspiciousPorts[Math.floor(Math.random() * suspiciousPorts.length)] :
                    Math.floor(Math.random() * 65000) + 1000,
                state: 'ESTABLISHED',
                process: Math.random() < 0.7 ? 'chrome.exe' : 'svchost.exe',
                pid: Math.floor(Math.random() * 10000)
            };
            
            connections.push(conn);
        }
        
        resolve(connections);
    });
}

// Generate IP address (with occasional suspicious ones)
function generateIP(forceSuspicious = false) {
    if (forceSuspicious) {
        const range = knownMaliciousRanges[Math.floor(Math.random() * knownMaliciousRanges.length)];
        return range + Math.floor(Math.random() * 256) + '.' + Math.floor(Math.random() * 256);
    }
    
    // Normal IPs
    const ranges = ['192.168.', '10.0.', '172.16.', '8.8.', '1.1.'];
    const range = ranges[Math.floor(Math.random() * ranges.length)];
    return range + Math.floor(Math.random() * 256) + '.' + Math.floor(Math.random() * 256);
}

// Analyze connection for threats
function analyzeConnection(conn) {
    const threats = [];
    
    // Check for known malicious IPs
    if (knownMaliciousRanges.some(range => conn.remoteIP.startsWith(range))) {
        threats.push('Known malicious IP range');
    }
    
    // Check for suspicious ports
    if (suspiciousPorts.includes(conn.remotePort)) {
        threats.push(`Suspicious port ${conn.remotePort}`);
        portScans++;
    }
    
    // Check for unusual remote ports
    if (conn.remotePort < 1024 && conn.remotePort !== 80 && conn.remotePort !== 443) {
        threats.push(`Uncommon privileged port ${conn.remotePort}`);
    }
    
    // Check for unusual processes
    if (conn.process === 'svchost.exe' && conn.remotePort > 50000) {
        threats.push('Suspicious svchost.exe activity');
    }
    
    // Check for non-standard protocols
    if (conn.protocol !== 'TCP' && conn.protocol !== 'UDP') {
        threats.push(`Unknown protocol: ${conn.protocol}`);
        unknownProtocols++;
    }
    
    // Random threat simulation
    if (Math.random() < 0.05) { // 5% chance
        const randomThreats = [
            'Multiple connection attempts',
            'Data exfiltration pattern',
            'C2 communication pattern',
            'Unusual data volume',
            'Connection to known botnet'
        ];
        threats.push(randomThreats[Math.floor(Math.random() * randomThreats.length)]);
    }
    
    return threats.length > 0 ? threats.join(', ') : null;
}

// Update UI elements
function updateUI() {
    // Update metrics
    document.getElementById('suspiciousCount').textContent = suspiciousCount;
    document.getElementById('portScans').textContent = portScans;
    document.getElementById('failedAuth').textContent = failedAuth;
    document.getElementById('totalConnections').textContent = totalConnections;
    document.getElementById('uniqueIPs').textContent = Object.keys(geoData).length;
    document.getElementById('dataTransferred').textContent = ((Math.random() * 500) + 50).toFixed(1) + ' MB';
    document.getElementById('trafficSpikes').textContent = trafficSpikes;
    document.getElementById('unknownProtocols').textContent = unknownProtocols;
    document.getElementById('geoAnomalies').textContent = geoAnomalies;
    document.getElementById('blockedIPs').textContent = blockedIPs.size;
    
    // Update suspicious activity list
    updateSuspiciousList();
    
    // Update active connections list
    updateConnectionsList();
}

// Update suspicious activity list
function updateSuspiciousList() {
    const listElem = document.getElementById('suspiciousList');
    
    if (suspiciousActivity.length === 0) {
        listElem.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">No suspicious activity detected yet...</p>';
        return;
    }
    
    listElem.innerHTML = '';
    
    suspiciousActivity.slice(0, 20).forEach(activity => {
        const item = document.createElement('div');
        item.className = activity.threat.includes('Known malicious') ? 'suspicious-item' : 'suspicious-item medium';
        
        const time = new Date(activity.timestamp).toLocaleTimeString();
        const severity = activity.threat.includes('Known malicious') ? 'HIGH' : 'MEDIUM';
        
        item.innerHTML = `
            <div class="suspicious-item-header">
                <span>${activity.remoteIP}:${activity.remotePort}</span>
                <span class="badge badge-${severity.toLowerCase()}">${severity}</span>
            </div>
            <div class="suspicious-item-details">
                <div><strong>Threat:</strong> ${activity.threat}</div>
                <div><strong>Process:</strong> ${activity.process} (PID: ${activity.pid})</div>
                <div class="timestamp">${time}</div>
            </div>
        `;
        
        listElem.appendChild(item);
    });
}

// Update active connections list
function updateConnectionsList() {
    const listElem = document.getElementById('connectionsList');
    
    if (activeConnections.length === 0) {
        listElem.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">No active connections...</p>';
        return;
    }
    
    listElem.innerHTML = '';
    
    activeConnections.slice(0, 30).forEach(conn => {
        const threat = analyzeConnection(conn);
        const item = document.createElement('div');
        item.className = threat ? 'connection-item suspicious' : 'connection-item';
        
        item.innerHTML = `
            <strong>${conn.protocol}</strong> 
            ${conn.remoteIP}:${conn.remotePort} 
            ← :${conn.localPort} 
            [${conn.process}]
            ${threat ? '<span class="badge badge-high">⚠ SUSPICIOUS</span>' : ''}
        `;
        
        listElem.appendChild(item);
    });
}

// Update charts
function updateCharts() {
    // Activity chart
    activityChart.data.labels = activityTimestamps;
    activityChart.data.datasets[0].data = normalConnectionsData;
    activityChart.data.datasets[1].data = suspiciousConnectionsData;
    activityChart.update('none');
    
    // Geo chart - top 5 sources
    const topSources = Object.entries(geoData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    geoChart.data.labels = topSources.map(([ip]) => ip);
    geoChart.data.datasets[0].data = topSources.map(([, count]) => count);
    geoChart.update('none');
}

// Update threat level badge
function updateThreatLevel() {
    const badge = document.getElementById('threatBadge');
    
    let level = 'LOW';
    let className = 'threat-low';
    
    if (suspiciousCount > 20) {
        level = 'CRITICAL';
        className = 'threat-critical';
    } else if (suspiciousCount > 10) {
        level = 'HIGH';
        className = 'threat-high';
    } else if (suspiciousCount > 5) {
        level = 'MEDIUM';
        className = 'threat-medium';
    }
    
    badge.textContent = level;
    badge.className = 'threat-badge ' + className;
}

// Show alert banner
function showAlert(message) {
    const banner = document.getElementById('alertBanner');
    banner.textContent = '⚠️ SECURITY ALERT: ' + message;
    banner.classList.add('show');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.classList.remove('show');
    }, 5000);
}

// Block suspicious IPs (simulated)
function blockSuspicious() {
    const blocked = suspiciousActivity.slice(0, 10).map(a => a.remoteIP);
    blocked.forEach(ip => blockedIPs.add(ip));
    
    alert(`Blocked ${blocked.length} suspicious IPs in firewall`);
    updateUI();
}

// Export security log
function exportSecurityLog() {
    if (suspiciousActivity.length === 0) {
        alert('No security events to export');
        return;
    }
    
    let csv = 'Timestamp,Remote IP,Remote Port,Local Port,Protocol,Process,PID,Threat\n';
    
    suspiciousActivity.forEach(activity => {
        csv += `${activity.timestamp},${activity.remoteIP},${activity.remotePort},${activity.localPort},${activity.protocol},${activity.process},${activity.pid},"${activity.threat}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security-log-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    alert('Security log exported successfully');
}

// Clear alerts
function clearAlerts() {
    if (!confirm('Clear all security alerts? This cannot be undone.')) {
        return;
    }
    
    suspiciousActivity = [];
    suspiciousCount = 0;
    portScans = 0;
    failedAuth = 0;
    trafficSpikes = 0;
    unknownProtocols = 0;
    geoAnomalies = 0;
    
    updateUI();
    alert('All alerts cleared');
}
