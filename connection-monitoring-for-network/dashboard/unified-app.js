// Unified Production Dashboard - REAL DATA ONLY
// No mock data, all data fetched from backend APIs

let monitoringInterval = null;
let isMonitoring = false;

// Data storage
let performanceData = {
    timestamps: [],
    latencies: [],
    packetLoss: [],
    cpuUsage: [],
    memoryUsage: [],
    totalTests: 0,
    successfulTests: 0,
    failedTests: 0
};

let securityData = {
    connections: [],
    suspiciousActivity: [],
    blockedIPs: new Set(),
    uniqueIPs: new Set(),
    portScans: 0,
    totalThreats: 0
};

// Charts
let perfChart = null;
let secChart = null;
let analysisChart = null;

// Current tab
let currentTab = 'performance';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    checkBackendConnection();
});

// Tab switching
function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// Initialize charts
function initializeCharts() {
    // Performance Chart
    const perfCtx = document.getElementById('perfChart').getContext('2d');
    perfChart = new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: performanceData.timestamps,
            datasets: [
                {
                    label: 'Latency (ms)',
                    data: performanceData.latencies,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y'
                },
                {
                    label: 'Packet Loss (%)',
                    data: performanceData.packetLoss,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            plugins: { legend: { labels: { color: '#fff' } } },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Latency (ms)', color: '#fff' },
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Packet Loss (%)', color: '#fff' },
                    ticks: { color: '#fff' },
                    grid: { display: false }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });

    // Security Chart
    const secCtx = document.getElementById('secChart').getContext('2d');
    secChart = new Chart(secCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Normal Connections',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Suspicious Connections',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#fff' } } },
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

    // Analysis Chart
    const analysisCtx = document.getElementById('analysisChart').getContext('2d');
    analysisChart = new Chart(analysisCtx, {
        type: 'bar',
        data: {
            labels: ['Latency', 'Packet Loss', 'CPU', 'Memory', 'Threats', 'Blocked'],
            datasets: [{
                label: 'Current Metrics',
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(16, 185, 129, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
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

// Check backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch('/api/ping');
        if (response.ok) {
            showAlert('✓ Backend connected - Ready for monitoring', 'success');
        }
    } catch (error) {
        showAlert('⚠ Backend not running - Start unified-server.ps1 first!', 'error');
        document.getElementById('connectionStatus').classList.remove('online');
        document.getElementById('connectionStatus').classList.add('offline');
        document.getElementById('connectionText').textContent = 'Backend Offline';
    }
}

// Start monitoring
function startMonitoring() {
    if (isMonitoring) {
        showAlert('Already monitoring', 'info');
        return;
    }

    isMonitoring = true;
    showAlert('Monitoring started', 'success');
    
    // Initial scan
    runMonitoringCycle();
    
    // Then every 3 seconds
    monitoringInterval = setInterval(runMonitoringCycle, 3000);
}

// Stop monitoring
function stopMonitoring() {
    if (!isMonitoring) {
        showAlert('Not monitoring', 'info');
        return;
    }

    clearInterval(monitoringInterval);
    isMonitoring = false;
    showAlert('Monitoring stopped', 'info');
}

// Main monitoring cycle - fetches all real data
async function runMonitoringCycle() {
    try {
        // Fetch performance data
        await fetchPerformanceData();
        
        // Fetch security data
        await fetchSecurityData();
        
        // Fetch firewall status
        await fetchFirewallStatus();
        
        // Update all UI
        updateAllUI();
        
    } catch (error) {
        console.error('Monitoring cycle failed:', error);
        showAlert('Error fetching data: ' + error.message, 'error');
    }
}

// Fetch real performance data
async function fetchPerformanceData() {
    try {
        // Ping test
        const pingResponse = await fetch('/api/ping');
        if (!pingResponse.ok) throw new Error('Ping API failed');
        
        const pingData = await pingResponse.json();
        const timestamp = new Date().toLocaleTimeString();
        
        performanceData.totalTests++;
        
        if (pingData.success) {
            performanceData.successfulTests++;
            performanceData.latencies.push(pingData.latency);
            performanceData.packetLoss.push(0);
            
            addToLog('perfLog', 
                `✓ ${pingData.latency}ms - Success`,
                'success',
                timestamp
            );
        } else {
            performanceData.failedTests++;
            performanceData.latencies.push(null);
            performanceData.packetLoss.push(100);
            
            addToLog('perfLog',
                `✗ Timeout - Failed`,
                'danger',
                timestamp
            );
        }
        
        performanceData.timestamps.push(timestamp);
        
        // Keep last 50 data points
        if (performanceData.timestamps.length > 50) {
            performanceData.timestamps.shift();
            performanceData.latencies.shift();
            performanceData.packetLoss.shift();
        }
        
        // System resources
        const resourceResponse = await fetch('/api/resources');
        if (resourceResponse.ok) {
            const resources = await resourceResponse.json();
            performanceData.cpuUsage.push(resources.cpu);
            performanceData.memoryUsage.push(resources.memory);
            
            if (performanceData.cpuUsage.length > 50) {
                performanceData.cpuUsage.shift();
                performanceData.memoryUsage.shift();
            }
        }
        
    } catch (error) {
        console.error('Performance data fetch failed:', error);
        throw error;
    }
}

// Fetch real security data
async function fetchSecurityData() {
    try {
        const response = await fetch('/api/connections');
        if (!response.ok) throw new Error('Connections API failed');
        
        const data = await response.json();
        securityData.connections = data.connections || [];
        
        // Process connections
        let suspiciousCount = 0;
        let normalCount = 0;
        
        securityData.connections.forEach(conn => {
            // Track unique IPs
            securityData.uniqueIPs.add(conn.remoteIP);
            
            if (conn.suspicious) {
                suspiciousCount++;
                
                // Add to suspicious activity log
                securityData.suspiciousActivity.unshift({
                    timestamp: new Date().toISOString(),
                    ...conn
                });
                
                // Check for port scans
                if (conn.threats && conn.threats.includes('Suspicious port')) {
                    securityData.portScans++;
                }
                
                securityData.totalThreats++;
                
                // Add to log
                addToLog('secLog',
                    `${conn.remoteIP}:${conn.remotePort} - ${conn.threats}`,
                    'danger',
                    new Date().toLocaleTimeString(),
                    `Process: ${conn.process} (PID: ${conn.pid})`
                );
                
                // Show alert for high-severity threats
                if (conn.threats.includes('malicious')) {
                    showAlert(`🚨 Malicious IP detected: ${conn.remoteIP}`, 'error');
                    updateThreatLevel('HIGH');
                }
            } else {
                normalCount++;
            }
        });
        
        // Keep only last 100 suspicious activities
        if (securityData.suspiciousActivity.length > 100) {
            securityData.suspiciousActivity = securityData.suspiciousActivity.slice(0, 100);
        }
        
        // Update security chart data
        const timestamp = new Date().toLocaleTimeString();
        if (!secChart.data.labels.includes(timestamp)) {
            secChart.data.labels.push(timestamp);
            secChart.data.datasets[0].data.push(normalCount);
            secChart.data.datasets[1].data.push(suspiciousCount);
            
            // Keep last 30 data points
            if (secChart.data.labels.length > 30) {
                secChart.data.labels.shift();
                secChart.data.datasets[0].data.shift();
                secChart.data.datasets[1].data.shift();
            }
        }
        
        // Update connections list
        updateConnectionsList();
        
    } catch (error) {
        console.error('Security data fetch failed:', error);
        throw error;
    }
}

// Fetch firewall status
async function fetchFirewallStatus() {
    try {
        const response = await fetch('/api/firewall');
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('sec-firewall').textContent = 
                data.enabled ? 'ACTIVE' : 'DISABLED';
            document.getElementById('sec-firewall').className = 
                data.enabled ? 'metric-value good' : 'metric-value danger';
            
            document.getElementById('sec-rules').textContent = data.blockedRules || 0;
        }
    } catch (error) {
        console.error('Firewall status fetch failed:', error);
    }
}

// Update all UI elements
function updateAllUI() {
    // Performance metrics
    const latestLatency = performanceData.latencies[performanceData.latencies.length - 1];
    if (latestLatency !== null && latestLatency !== undefined) {
        updateMetric('perf-latency', `${latestLatency}ms`, 
            latestLatency < 50 ? 'good' : latestLatency < 100 ? 'warning' : 'danger');
    } else {
        updateMetric('perf-latency', 'Timeout', 'danger');
    }
    
    const validLatencies = performanceData.latencies.filter(l => l !== null);
    if (validLatencies.length > 0) {
        const avgLatency = validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length;
        updateMetric('perf-avg-latency', `${Math.round(avgLatency)}ms`,
            avgLatency < 50 ? 'good' : avgLatency < 100 ? 'warning' : 'danger');
    }
    
    const packetLoss = performanceData.totalTests > 0 
        ? ((performanceData.failedTests / performanceData.totalTests) * 100).toFixed(2)
        : '0.00';
    updateMetric('perf-packet-loss', `${packetLoss}%`,
        parseFloat(packetLoss) === 0 ? 'good' : 
        parseFloat(packetLoss) < 5 ? 'warning' : 'danger');
    
    document.getElementById('perf-total').textContent = performanceData.totalTests;
    document.getElementById('perf-success').textContent = performanceData.successfulTests;
    document.getElementById('perf-failed').textContent = performanceData.failedTests;
    
    // Latest system resources
    if (performanceData.cpuUsage.length > 0) {
        const latestCPU = performanceData.cpuUsage[performanceData.cpuUsage.length - 1];
        updateMetric('perf-cpu', `${latestCPU.toFixed(1)}%`,
            latestCPU < 50 ? 'good' : latestCPU < 80 ? 'warning' : 'danger');
    }
    
    if (performanceData.memoryUsage.length > 0) {
        const latestMem = performanceData.memoryUsage[performanceData.memoryUsage.length - 1];
        updateMetric('perf-memory', `${latestMem.toFixed(1)}%`,
            latestMem < 70 ? 'good' : latestMem < 90 ? 'warning' : 'danger');
    }
    
    // Network I/O (simulated for now - would need additional API)
    document.getElementById('perf-network').textContent = '--';
    
    // Security metrics
    document.getElementById('sec-suspicious').textContent = 
        securityData.connections.filter(c => c.suspicious).length;
    document.getElementById('sec-portscans').textContent = securityData.portScans;
    document.getElementById('sec-blocked').textContent = securityData.blockedIPs.size;
    document.getElementById('sec-connections').textContent = securityData.connections.length;
    document.getElementById('sec-unique-ips').textContent = securityData.uniqueIPs.size;
    document.getElementById('sec-lastscan').textContent = new Date().toLocaleTimeString();
    
    // Analysis tab
    document.getElementById('analysis-uptime').textContent = 
        performanceData.totalTests > 0 
            ? `${((performanceData.successfulTests / performanceData.totalTests) * 100).toFixed(1)}%`
            : '--';
    document.getElementById('analysis-latency').textContent = 
        validLatencies.length > 0
            ? `${Math.round(validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length)}ms`
            : '--';
    document.getElementById('analysis-drops').textContent = performanceData.failedTests;
    document.getElementById('analysis-threats').textContent = securityData.totalThreats;
    document.getElementById('analysis-blocked').textContent = securityData.blockedIPs.size;
    
    // Update charts
    perfChart.update('none');
    secChart.update('none');
    
    // Update analysis chart
    analysisChart.data.datasets[0].data = [
        latestLatency || 0,
        parseFloat(packetLoss),
        performanceData.cpuUsage[performanceData.cpuUsage.length - 1] || 0,
        performanceData.memoryUsage[performanceData.memoryUsage.length - 1] || 0,
        securityData.connections.filter(c => c.suspicious).length,
        securityData.blockedIPs.size
    ];
    analysisChart.update('none');
    
    // Update threat level
    const suspiciousCount = securityData.connections.filter(c => c.suspicious).length;
    if (suspiciousCount > 10) {
        updateThreatLevel('CRITICAL');
    } else if (suspiciousCount > 5) {
        updateThreatLevel('HIGH');
    } else if (suspiciousCount > 2) {
        updateThreatLevel('MEDIUM');
    } else {
        updateThreatLevel('LOW');
    }
}

// Update connections list
function updateConnectionsList() {
    const listElem = document.getElementById('connectionsList');
    listElem.innerHTML = '';
    
    if (securityData.connections.length === 0) {
        listElem.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">No connections detected</p>';
        return;
    }
    
    securityData.connections.slice(0, 30).forEach(conn => {
        const div = document.createElement('div');
        div.className = 'data-item ' + (conn.suspicious ? 'danger' : 'success');
        
        div.innerHTML = `
            <strong>${conn.protocol}</strong> 
            ${conn.remoteIP}:${conn.remotePort} ← :${conn.localPort} 
            [${conn.process}]
            ${conn.suspicious ? '<span class="badge badge-high">⚠ SUSPICIOUS</span>' : ''}
            ${conn.threats ? `<div class="timestamp">${conn.threats}</div>` : ''}
        `;
        
        listElem.appendChild(div);
    });
}

// Helper: Update metric
function updateMetric(id, value, className) {
    const elem = document.getElementById(id);
    elem.textContent = value;
    elem.className = 'metric-value ' + className;
}

// Helper: Add to log
function addToLog(logId, message, type, timestamp, extra = '') {
    const logElem = document.getElementById(logId);
    
    const div = document.createElement('div');
    div.className = 'data-item ' + type;
    div.innerHTML = `
        ${message}
        ${extra ? `<div class="timestamp">${extra}</div>` : ''}
        <div class="timestamp">${timestamp}</div>
    `;
    
    logElem.insertBefore(div, logElem.firstChild);
    
    // Keep only last 50 entries
    while (logElem.children.length > 50) {
        logElem.removeChild(logElem.lastChild);
    }
}

// Update threat level
function updateThreatLevel(level) {
    const badge = document.getElementById('threatLevel');
    badge.textContent = level;
    badge.className = `threat-badge threat-${level.toLowerCase()}`;
    
    const riskElem = document.getElementById('analysis-risk');
    if (riskElem) {
        riskElem.textContent = level;
        riskElem.className = 'metric-value ' + 
            (level === 'LOW' ? 'good' : level === 'MEDIUM' ? 'warning' : 'danger');
    }
}

// Show alert
function showAlert(message, type) {
    const banner = document.getElementById('alertBanner');
    banner.textContent = message;
    banner.classList.add('show');
    
    setTimeout(() => {
        banner.classList.remove('show');
    }, 5000);
}

// Block threats
async function blockThreats() {
    const suspicious = securityData.connections.filter(c => c.suspicious);
    
    if (suspicious.length === 0) {
        showAlert('No threats to block', 'info');
        return;
    }
    
    if (!confirm(`Block ${suspicious.length} suspicious IP(s)?`)) {
        return;
    }
    
    for (const conn of suspicious) {
        try {
            const response = await fetch('/api/block-ip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip: conn.remoteIP })
            });
            
            if (response.ok) {
                securityData.blockedIPs.add(conn.remoteIP);
            }
        } catch (error) {
            console.error('Failed to block IP:', error);
        }
    }
    
    showAlert(`Blocked ${suspicious.length} IP(s) in firewall`, 'success');
    updateAllUI();
}

// Export data
function exportData() {
    const data = {
        performance: performanceData,
        security: {
            ...securityData,
            blockedIPs: Array.from(securityData.blockedIPs),
            uniqueIPs: Array.from(securityData.uniqueIPs)
        },
        exportedAt: new Date().toISOString()
    };
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `network-monitoring-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showAlert('Data exported successfully', 'success');
}

// Clear data
function clearData() {
    if (!confirm('Clear all monitoring data? This cannot be undone.')) {
        return;
    }
    
    performanceData = {
        timestamps: [],
        latencies: [],
        packetLoss: [],
        cpuUsage: [],
        memoryUsage: [],
        totalTests: 0,
        successfulTests: 0,
        failedTests: 0
    };
    
    securityData = {
        connections: [],
        suspiciousActivity: [],
        blockedIPs: new Set(),
        uniqueIPs: new Set(),
        portScans: 0,
        totalThreats: 0
    };
    
    document.getElementById('perfLog').innerHTML = '';
    document.getElementById('secLog').innerHTML = '';
    document.getElementById('connectionsList').innerHTML = '';
    
    updateAllUI();
    showAlert('All data cleared', 'info');
}
