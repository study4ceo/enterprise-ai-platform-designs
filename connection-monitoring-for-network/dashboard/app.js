// Network Monitoring Dashboard - JavaScript

let monitoringInterval = null;
let isMonitoring = false;

// Data storage
let pingHistory = [];
let latencyData = [];
let cpuData = [];
let memData = [];
let timestamps = [];

let totalTests = 0;
let successfulTests = 0;
let failedTests = 0;

// Chart instances
let latencyChart = null;
let resourceChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadSavedData();
    updateStats();
});

// Initialize Chart.js charts
function initializeCharts() {
    // Latency Chart
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    latencyChart = new Chart(latencyCtx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Latency (ms)',
                data: latencyData,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Latency (ms)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });

    // Resource Chart
    const resourceCtx = document.getElementById('resourceChart').getContext('2d');
    resourceChart = new Chart(resourceCtx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: 'CPU %',
                    data: cpuData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Memory %',
                    data: memData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Usage %'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

// Start monitoring
function startMonitoring() {
    if (isMonitoring) {
        showAlert('Monitoring is already running', 'info');
        return;
    }

    isMonitoring = true;
    showAlert('Monitoring started', 'info');
    updateStatusIndicator(true);

    // Run first test immediately
    runNetworkTest();

    // Then run every 5 seconds
    monitoringInterval = setInterval(runNetworkTest, 5000);
}

// Stop monitoring
function stopMonitoring() {
    if (!isMonitoring) {
        showAlert('Monitoring is not running', 'info');
        return;
    }

    clearInterval(monitoringInterval);
    isMonitoring = false;
    showAlert('Monitoring stopped', 'warning');
    updateStatusIndicator(false);
}

// Run network test (simulated)
async function runNetworkTest() {
    try {
        // In a real scenario, this would call a backend API
        // For now, we'll simulate with random data
        
        const latency = await simulatePing();
        const resources = await getSystemResources();
        
        const timestamp = new Date().toLocaleTimeString();
        const success = latency < 500; // Consider timeout if > 500ms
        
        // Update data
        totalTests++;
        if (success) {
            successfulTests++;
            latencyData.push(latency);
        } else {
            failedTests++;
            latencyData.push(null);
        }
        
        timestamps.push(timestamp);
        cpuData.push(resources.cpu);
        memData.push(resources.memory);
        
        // Keep only last 50 data points
        if (timestamps.length > 50) {
            timestamps.shift();
            latencyData.shift();
            cpuData.shift();
            memData.shift();
        }
        
        // Add to ping history
        pingHistory.unshift({
            timestamp: new Date().toISOString(),
            latency: latency,
            success: success,
            cpu: resources.cpu,
            memory: resources.memory,
            networkIO: resources.networkIO
        });
        
        // Keep only last 100 pings
        if (pingHistory.length > 100) {
            pingHistory.pop();
        }
        
        // Update UI
        updateStats();
        updateCharts();
        updatePingList();
        updateMetrics(latency, success, resources);
        
        // Check for alerts
        checkForAlerts(latency, success, resources);
        
        // Save data
        saveData();
        
    } catch (error) {
        console.error('Network test failed:', error);
        showAlert('Network test failed: ' + error.message, 'danger');
    }
}

// Perform real ping (or simulated if API not available)
async function simulatePing() {
    try {
        // Try to fetch from API
        const response = await fetch('/api/ping');
        if (response.ok) {
            const data = await response.json();
            return data.success ? data.latency : 600; // 600 = timeout
        }
    } catch (error) {
        // Fallback to simulation if API not available
        console.log('API not available, using simulated data');
    }
    
    // Fallback: Simulate ping
    return new Promise((resolve) => {
        setTimeout(() => {
            const baseLatency = 20 + Math.random() * 30;
            const spike = Math.random() < 0.05 ? Math.random() * 200 : 0;
            const timeout = Math.random() < 0.02 ? 600 : 0;
            const latency = Math.round(baseLatency + spike + timeout);
            resolve(latency);
        }, 100);
    });
}

// Get system resources (real or simulated)
async function getSystemResources() {
    try {
        // Try to fetch from API
        const response = await fetch('/api/resources');
        if (response.ok) {
            const data = await response.json();
            return data;
        }
    } catch (error) {
        // Fallback to simulation if API not available
        console.log('API not available, using simulated data');
    }
    
    // Fallback: Simulate resources
    return new Promise((resolve) => {
        const cpu = Math.round(20 + Math.random() * 40);
        const memory = Math.round(40 + Math.random() * 20);
        const networkIO = Math.round(Math.random() * 1000);
        resolve({ cpu, memory, networkIO });
    });
}

// Update statistics display
function updateStats() {
    document.getElementById('totalTests').textContent = totalTests;
    document.getElementById('successfulTests').textContent = successfulTests;
    document.getElementById('failedTests').textContent = failedTests;
    
    // Calculate packet loss
    const packetLoss = totalTests > 0 
        ? ((failedTests / totalTests) * 100).toFixed(2) 
        : '0.00';
    
    const packetLossElem = document.getElementById('packetLoss');
    packetLossElem.textContent = packetLoss + '%';
    
    // Color code packet loss
    if (parseFloat(packetLoss) === 0) {
        packetLossElem.className = 'metric-value good';
    } else if (parseFloat(packetLoss) < 5) {
        packetLossElem.className = 'metric-value warning';
    } else {
        packetLossElem.className = 'metric-value danger';
    }
}

// Update charts
function updateCharts() {
    latencyChart.data.labels = timestamps;
    latencyChart.data.datasets[0].data = latencyData;
    latencyChart.update('none'); // 'none' for better performance
    
    resourceChart.data.labels = timestamps;
    resourceChart.data.datasets[0].data = cpuData;
    resourceChart.data.datasets[1].data = memData;
    resourceChart.update('none');
}

// Update ping list
function updatePingList() {
    const pingListElem = document.getElementById('pingList');
    pingListElem.innerHTML = '';
    
    pingHistory.slice(0, 20).forEach(ping => {
        const item = document.createElement('div');
        item.className = ping.success ? 'ping-item ping-success' : 'ping-item ping-failure';
        
        const time = new Date(ping.timestamp).toLocaleTimeString();
        const status = ping.success ? '✓ Success' : '✗ Failed';
        const latency = ping.success ? `${ping.latency}ms` : 'Timeout';
        
        item.innerHTML = `
            <div>
                <strong>${status}</strong>
                <div class="timestamp">${time}</div>
            </div>
            <div style="text-align: right;">
                <strong>${latency}</strong>
                <div class="timestamp">CPU: ${ping.cpu}% | MEM: ${ping.memory}%</div>
            </div>
        `;
        
        pingListElem.appendChild(item);
    });
}

// Update metrics
function updateMetrics(latency, success, resources) {
    // Current latency
    const currentLatencyElem = document.getElementById('currentLatency');
    if (success) {
        currentLatencyElem.textContent = latency + 'ms';
        if (latency < 50) {
            currentLatencyElem.className = 'metric-value good';
        } else if (latency < 100) {
            currentLatencyElem.className = 'metric-value warning';
        } else {
            currentLatencyElem.className = 'metric-value danger';
        }
    } else {
        currentLatencyElem.textContent = 'Timeout';
        currentLatencyElem.className = 'metric-value danger';
    }
    
    // Average latency
    const validLatencies = latencyData.filter(l => l !== null);
    if (validLatencies.length > 0) {
        const avg = validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length;
        const avgLatencyElem = document.getElementById('avgLatency');
        avgLatencyElem.textContent = Math.round(avg) + 'ms';
        
        if (avg < 50) {
            avgLatencyElem.className = 'metric-value good';
        } else if (avg < 100) {
            avgLatencyElem.className = 'metric-value warning';
        } else {
            avgLatencyElem.className = 'metric-value danger';
        }
    }
    
    // System resources
    document.getElementById('cpuUsage').textContent = resources.cpu + '%';
    document.getElementById('memUsage').textContent = resources.memory + '%';
    document.getElementById('networkIO').textContent = resources.networkIO + ' KB/s';
}

// Check for alerts
function checkForAlerts(latency, success, resources) {
    // High latency alert
    if (success && latency > 200) {
        showAlert(`High latency detected: ${latency}ms`, 'warning');
    }
    
    // Connection failure alert
    if (!success) {
        showAlert('Connection failed - possible network issue', 'danger');
    }
    
    // High CPU alert
    if (resources.cpu > 80) {
        showAlert(`High CPU usage: ${resources.cpu}%`, 'warning');
    }
    
    // High memory alert
    if (resources.memory > 90) {
        showAlert(`High memory usage: ${resources.memory}%`, 'warning');
    }
}

// Show alert
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts');
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
        <span class="timestamp" style="float: right;">${new Date().toLocaleTimeString()}</span>
    `;
    
    alertsContainer.insertBefore(alert, alertsContainer.firstChild);
    
    // Keep only last 5 alerts
    while (alertsContainer.children.length > 5) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 10000);
}

// Update status indicator
function updateStatusIndicator(online) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (online) {
        statusDot.className = 'status-dot status-online';
        statusText.textContent = 'Monitoring';
    } else {
        statusDot.className = 'status-dot status-offline';
        statusText.textContent = 'Stopped';
    }
}

// Save data to localStorage
function saveData() {
    const data = {
        pingHistory: pingHistory,
        totalTests: totalTests,
        successfulTests: successfulTests,
        failedTests: failedTests,
        timestamps: timestamps,
        latencyData: latencyData,
        cpuData: cpuData,
        memData: memData
    };
    
    localStorage.setItem('networkMonitoringData', JSON.stringify(data));
}

// Load saved data
function loadSavedData() {
    const saved = localStorage.getItem('networkMonitoringData');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            pingHistory = data.pingHistory || [];
            totalTests = data.totalTests || 0;
            successfulTests = data.successfulTests || 0;
            failedTests = data.failedTests || 0;
            timestamps = data.timestamps || [];
            latencyData = data.latencyData || [];
            cpuData = data.cpuData || [];
            memData = data.memData || [];
            
            updateStats();
            updateCharts();
            updatePingList();
            
            showAlert('Previous data loaded', 'info');
        } catch (error) {
            console.error('Failed to load saved data:', error);
        }
    }
}

// Export data to CSV
function exportData() {
    if (pingHistory.length === 0) {
        showAlert('No data to export', 'warning');
        return;
    }
    
    let csv = 'Timestamp,Latency (ms),Success,CPU %,Memory %,Network I/O (KB/s)\n';
    
    pingHistory.forEach(ping => {
        csv += `${ping.timestamp},${ping.latency},${ping.success},${ping.cpu},${ping.memory},${ping.networkIO}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `network-monitoring-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showAlert('Data exported successfully', 'info');
}

// Clear all data
function clearData() {
    if (!confirm('Are you sure you want to clear all data? This cannot be undone.')) {
        return;
    }
    
    pingHistory = [];
    latencyData = [];
    cpuData = [];
    memData = [];
    timestamps = [];
    totalTests = 0;
    successfulTests = 0;
    failedTests = 0;
    
    localStorage.removeItem('networkMonitoringData');
    
    updateStats();
    updateCharts();
    updatePingList();
    
    document.getElementById('pingList').innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No data available</p>';
    
    showAlert('All data cleared', 'info');
}
