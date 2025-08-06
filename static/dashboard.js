// Dashboard JavaScript
let charts = {};
let autoRefreshInterval;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    setupAutoRefresh();
});

// Load dashboard data
async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        if (data.error) {
            console.error('Dashboard error:', data.error);
            return;
        }
        
        updateDashboard(data);
        updateLastUpdate(data.timestamp);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Update dashboard with new data
function updateDashboard(data) {
    updateSystemStatus(data.system_status);
    updateMetrics(data.metrics);
    updateAlerts(data.alerts);
    updateCharts(data.metrics, data.charts);
}

// Update system status
function updateSystemStatus(status) {
    const monitoringStatus = document.getElementById('monitoring-status');
    const uptime = document.getElementById('uptime');
    const cpuUsage = document.getElementById('cpu-usage');
    const memoryUsage = document.getElementById('memory-usage');
    
    // Monitoring status
    if (status.monitoring_active) {
        monitoringStatus.className = 'status-indicator active';
        monitoringStatus.textContent = 'Active';
    } else {
        monitoringStatus.className = 'status-indicator inactive';
        monitoringStatus.textContent = 'Inactive';
    }
    
    // Uptime
    if (status.uptime_seconds) {
        const hours = Math.floor(status.uptime_seconds / 3600);
        const minutes = Math.floor((status.uptime_seconds % 3600) / 60);
        uptime.textContent = `${hours}h ${minutes}m`;
    } else {
        uptime.textContent = 'N/A';
    }
    
    // CPU Usage
    if (status.system_metrics && status.system_metrics.cpu_percent !== undefined) {
        cpuUsage.textContent = `${status.system_metrics.cpu_percent.toFixed(1)}%`;
    } else {
        cpuUsage.textContent = 'N/A';
    }
    
    // Memory Usage
    if (status.system_metrics && status.system_metrics.memory_percent !== undefined) {
        memoryUsage.textContent = `${status.system_metrics.memory_percent.toFixed(1)}%`;
    } else {
        memoryUsage.textContent = 'N/A';
    }
}

// Update metrics
function updateMetrics(metrics) {
    const requestsPerMinute = document.getElementById('requests-per-minute');
    const avgResponseTime = document.getElementById('avg-response-time');
    const errorRate = document.getElementById('error-rate');
    const activeConnections = document.getElementById('active-connections');
    
    if (metrics.inspector) {
        const inspector = metrics.inspector;
        
        // Get latest values
        const latestRequests = inspector.requests_per_minute && inspector.requests_per_minute.length > 0 
            ? inspector.requests_per_minute[inspector.requests_per_minute.length - 1].value : 0;
        const latestResponseTime = inspector.response_time && inspector.response_time.length > 0 
            ? inspector.response_time[inspector.response_time.length - 1].value : 0;
        const latestErrorRate = inspector.error_rate && inspector.error_rate.length > 0 
            ? inspector.error_rate[inspector.error_rate.length - 1].value : 0;
        
        requestsPerMinute.textContent = latestRequests.toFixed(1);
        avgResponseTime.textContent = `${(latestResponseTime * 1000).toFixed(0)}ms`;
        errorRate.textContent = `${latestErrorRate.toFixed(2)}%`;
        activeConnections.textContent = 'N/A'; // Would need to be added to metrics
    } else {
        requestsPerMinute.textContent = 'N/A';
        avgResponseTime.textContent = 'N/A';
        errorRate.textContent = 'N/A';
        activeConnections.textContent = 'N/A';
    }
}

// Update alerts
function updateAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    
    if (!alerts.active_alerts || alerts.active_alerts.length === 0) {
        container.innerHTML = '<div class="no-alerts">No active alerts</div>';
        return;
    }
    
    container.innerHTML = alerts.active_alerts.map(alert => `
        <div class="alert-item ${alert.severity}">
            <div class="alert-header">
                <span class="alert-severity">${alert.severity.toUpperCase()}</span>
                <span class="alert-timestamp">${formatTimestamp(alert.timestamp)}</span>
            </div>
            <div class="alert-message">${alert.message}</div>
            <div class="alert-meta">
                Source: ${alert.source} | ID: ${alert.alert_id}
            </div>
        </div>
    `).join('');
}

// Update charts
function updateCharts(metrics, chartsConfig) {
    if (!chartsConfig.enabled) return;
    
    chartsConfig.charts.forEach(chartConfig => {
        const canvas = document.getElementById(chartConfig.id);
        if (!canvas) return;
        
        const data = getChartData(metrics, chartConfig.data_source);
        updateChart(canvas, chartConfig, data);
    });
}

// Get chart data from metrics
function getChartData(metrics, dataSource) {
    const parts = dataSource.split('.');
    let data = metrics;
    
    for (const part of parts) {
        if (data && data[part]) {
            data = data[part];
        } else {
            return [];
        }
    }
    
    return data || [];
}

// Update individual chart
function updateChart(canvas, config, data) {
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (charts[config.id]) {
        charts[config.id].destroy();
    }
    
    // Prepare chart data
    const labels = data.map(d => formatTime(d.timestamp));
    const values = data.map(d => d.value);
    
    // Create new chart
    charts[config.id] = new Chart(ctx, {
        type: config.type,
        data: {
            labels: labels,
            datasets: [{
                label: config.title,
                data: values,
                borderColor: config.color,
                backgroundColor: config.color + '20',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: config.y_axis_label
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

// Setup auto refresh
function setupAutoRefresh() {
    const autoRefreshCheckbox = document.getElementById('auto-refresh');
    
    autoRefreshCheckbox.addEventListener('change', function() {
        if (this.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Start auto refresh by default
    startAutoRefresh();
}

// Start auto refresh
function startAutoRefresh() {
    stopAutoRefresh(); // Clear existing interval
    
    const refreshInterval = 5000; // 5 seconds
    autoRefreshInterval = setInterval(loadDashboard, refreshInterval);
}

// Stop auto refresh
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Manual refresh
function refreshDashboard() {
    loadDashboard();
}

// Update last update timestamp
function updateLastUpdate(timestamp) {
    const lastUpdate = document.getElementById('last-update');
    const date = new Date(timestamp);
    lastUpdate.textContent = `Last updated: ${date.toLocaleTimeString()}`;
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Format time for charts
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}