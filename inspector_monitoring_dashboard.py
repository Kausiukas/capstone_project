"""
Inspector Monitoring Dashboard Module (Task 4.2.3)

This module provides a web-based monitoring dashboard for the Inspector system.
It serves real-time monitoring data, alerts, and system metrics through a web interface.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import webbrowser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardTheme(Enum):
    """Dashboard theme options"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    host: str = "localhost"
    port: int = 8080
    theme: DashboardTheme = DashboardTheme.LIGHT
    refresh_interval: int = 5  # seconds
    max_data_points: int = 100
    enable_auto_refresh: bool = True
    enable_charts: bool = True
    enable_alerts: bool = True
    enable_metrics: bool = True


class InspectorMonitoringDashboard:
    """Web-based monitoring dashboard for Inspector"""
    
    def __init__(self, config: DashboardConfig = None, 
                 monitor=None, alerting_system=None):
        self.config = config or DashboardConfig()
        self.monitor = monitor
        self.alerting_system = alerting_system
        
        # Dashboard state
        self.is_running = False
        self.server = None
        self.server_thread = None
        
        # Data cache
        self.cached_data = {}
        self.last_update = datetime.now()
        
        # Static file serving
        self.static_dir = Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        
        # Create static files
        self._create_static_files()
        
        logger.info("Inspector Monitoring Dashboard initialized")
    
    def start_dashboard(self) -> bool:
        """Start the monitoring dashboard"""
        if self.is_running:
            logger.warning("Dashboard is already running")
            return False
        
        try:
            # Create HTTP server
            server_address = (self.config.host, self.config.port)
            self.server = HTTPServer(server_address, DashboardRequestHandler)
            self.server.dashboard = self
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            
            # Open browser
            url = f"http://{self.config.host}:{self.config.port}"
            logger.info(f"Dashboard started at: {url}")
            
            # Try to open browser (non-blocking)
            try:
                webbrowser.open(url)
            except Exception as e:
                logger.warning(f"Could not open browser: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return False
    
    def stop_dashboard(self) -> bool:
        """Stop the monitoring dashboard"""
        if not self.is_running:
            logger.warning("Dashboard is not running")
            return False
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5.0)
            
            self.is_running = False
            logger.info("Dashboard stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop dashboard: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "theme": self.config.theme.value,
                    "refresh_interval": self.config.refresh_interval,
                    "enable_auto_refresh": self.config.enable_auto_refresh
                },
                "system_status": self._get_system_status(),
                "metrics": self._get_metrics_data(),
                "alerts": self._get_alerts_data(),
                "charts": self._get_charts_data()
            }
            
            self.cached_data = data
            self.last_update = datetime.now()
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        try:
            if self.monitor:
                summary = self.monitor.get_monitoring_summary()
                return {
                    "monitoring_active": summary.get("monitoring_active", False),
                    "uptime_seconds": summary.get("uptime_seconds", 0),
                    "system_metrics": summary.get("system_metrics", {}),
                    "inspector_metrics": summary.get("inspector_metrics", {})
                }
            else:
                return {
                    "monitoring_active": False,
                    "uptime_seconds": 0,
                    "system_metrics": {},
                    "inspector_metrics": {}
                }
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    def _get_metrics_data(self) -> Dict[str, Any]:
        """Get metrics data for dashboard"""
        try:
            if not self.monitor:
                return {}
            
            metrics = {}
            
            # System metrics history
            system_history = self.monitor.get_metrics_history("system", self.config.max_data_points)
            if system_history:
                metrics["system"] = {
                    "cpu": [{"timestamp": m.timestamp.isoformat(), "value": m.cpu_percent} 
                           for m in system_history if hasattr(m, 'cpu_percent')],
                    "memory": [{"timestamp": m.timestamp.isoformat(), "value": m.memory_percent} 
                              for m in system_history if hasattr(m, 'memory_percent')],
                    "disk": [{"timestamp": m.timestamp.isoformat(), "value": m.disk_usage_percent} 
                            for m in system_history if hasattr(m, 'disk_usage_percent')]
                }
            
            # Inspector metrics history
            inspector_history = self.monitor.get_metrics_history("inspector", self.config.max_data_points)
            if inspector_history:
                metrics["inspector"] = {
                    "requests_per_minute": [{"timestamp": m.timestamp.isoformat(), "value": m.requests_per_minute} 
                                          for m in inspector_history if hasattr(m, 'requests_per_minute')],
                    "response_time": [{"timestamp": m.timestamp.isoformat(), "value": m.average_response_time} 
                                    for m in inspector_history if hasattr(m, 'average_response_time')],
                    "error_rate": [{"timestamp": m.timestamp.isoformat(), "value": m.error_rate} 
                                 for m in inspector_history if hasattr(m, 'error_rate')]
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics data: {e}")
            return {"error": str(e)}
    
    def _get_alerts_data(self) -> Dict[str, Any]:
        """Get alerts data for dashboard"""
        try:
            if not self.alerting_system:
                return {}
            
            summary = self.alerting_system.get_alert_summary()
            active_alerts = self.alerting_system.get_active_alerts()
            
            return {
                "summary": summary,
                "active_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "source": alert.source,
                        "timestamp": alert.timestamp.isoformat(),
                        "metrics": alert.metrics
                    }
                    for alert in active_alerts[:10]  # Limit to 10 most recent
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get alerts data: {e}")
            return {"error": str(e)}
    
    def _get_charts_data(self) -> Dict[str, Any]:
        """Get chart configuration and data"""
        try:
            return {
                "enabled": self.config.enable_charts,
                "charts": [
                    {
                        "id": "cpu_usage",
                        "title": "CPU Usage",
                        "type": "line",
                        "data_source": "metrics.system.cpu",
                        "y_axis_label": "CPU %",
                        "color": "#ff6b6b"
                    },
                    {
                        "id": "memory_usage",
                        "title": "Memory Usage",
                        "type": "line",
                        "data_source": "metrics.system.memory",
                        "y_axis_label": "Memory %",
                        "color": "#4ecdc4"
                    },
                    {
                        "id": "disk_usage",
                        "title": "Disk Usage",
                        "type": "line",
                        "data_source": "metrics.system.disk",
                        "y_axis_label": "Disk %",
                        "color": "#45b7d1"
                    },
                    {
                        "id": "requests_per_minute",
                        "title": "Requests per Minute",
                        "type": "line",
                        "data_source": "metrics.inspector.requests_per_minute",
                        "y_axis_label": "Requests/min",
                        "color": "#96ceb4"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get charts data: {e}")
            return {"error": str(e)}
    
    def _run_server(self) -> None:
        """Run the HTTP server"""
        try:
            logger.info(f"Starting dashboard server on {self.config.host}:{self.config.port}")
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
    
    def _create_static_files(self) -> None:
        """Create static HTML, CSS, and JavaScript files"""
        self._create_index_html()
        self._create_styles_css()
        self._create_dashboard_js()
    
    def _create_index_html(self) -> None:
        """Create the main HTML file"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspector Monitoring Dashboard</title>
    <link rel="stylesheet" href="/static/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <header class="dashboard-header">
            <h1>Inspector Monitoring Dashboard</h1>
            <div class="header-controls">
                <button id="refresh-btn" onclick="refreshDashboard()">Refresh</button>
                <label>
                    <input type="checkbox" id="auto-refresh" checked> Auto Refresh
                </label>
                <span id="last-update"></span>
            </div>
        </header>
        
        <div class="dashboard-content">
            <!-- System Status -->
            <div class="dashboard-section">
                <h2>System Status</h2>
                <div class="status-grid">
                    <div class="status-card">
                        <h3>Monitoring</h3>
                        <div id="monitoring-status" class="status-indicator"></div>
                    </div>
                    <div class="status-card">
                        <h3>Uptime</h3>
                        <div id="uptime" class="status-value"></div>
                    </div>
                    <div class="status-card">
                        <h3>CPU Usage</h3>
                        <div id="cpu-usage" class="status-value"></div>
                    </div>
                    <div class="status-card">
                        <h3>Memory Usage</h3>
                        <div id="memory-usage" class="status-value"></div>
                    </div>
                </div>
            </div>
            
            <!-- Charts -->
            <div class="dashboard-section">
                <h2>System Metrics</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <canvas id="cpu-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="memory-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="disk-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="requests-chart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Alerts -->
            <div class="dashboard-section">
                <h2>Active Alerts</h2>
                <div id="alerts-container" class="alerts-container">
                    <div class="no-alerts">No active alerts</div>
                </div>
            </div>
            
            <!-- Inspector Metrics -->
            <div class="dashboard-section">
                <h2>Inspector Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Requests/min</h3>
                        <div id="requests-per-minute" class="metric-value"></div>
                    </div>
                    <div class="metric-card">
                        <h3>Avg Response Time</h3>
                        <div id="avg-response-time" class="metric-value"></div>
                    </div>
                    <div class="metric-card">
                        <h3>Error Rate</h3>
                        <div id="error-rate" class="metric-value"></div>
                    </div>
                    <div class="metric-card">
                        <h3>Active Connections</h3>
                        <div id="active-connections" class="metric-value"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="/static/dashboard.js"></script>
</body>
</html>"""
        
        with open(self.static_dir / "index.html", "w") as f:
            f.write(html_content)
    
    def _create_styles_css(self) -> None:
        """Create the CSS styles file"""
        css_content = """/* Dashboard Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f5f5f5;
    color: #333;
}

.dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.dashboard-header {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard-header h1 {
    color: #2c3e50;
    font-size: 24px;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 15px;
}

.header-controls button {
    background: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.header-controls button:hover {
    background: #2980b9;
}

.header-controls label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 14px;
}

#last-update {
    font-size: 12px;
    color: #666;
}

.dashboard-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.dashboard-section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 18px;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.status-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    border-left: 4px solid #3498db;
}

.status-card h3 {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-indicator.active {
    background: #27ae60;
}

.status-indicator.inactive {
    background: #e74c3c;
}

.status-value {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.chart-container {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    height: 300px;
}

.alerts-container {
    max-height: 400px;
    overflow-y: auto;
}

.alert-item {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 10px;
}

.alert-item.critical {
    background: #f8d7da;
    border-color: #f5c6cb;
}

.alert-item.high {
    background: #fff3cd;
    border-color: #ffeaa7;
}

.alert-item.medium {
    background: #d1ecf1;
    border-color: #bee5eb;
}

.alert-item.low {
    background: #d4edda;
    border-color: #c3e6cb;
}

.alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.alert-severity {
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
}

.alert-message {
    font-size: 14px;
    margin-bottom: 5px;
}

.alert-meta {
    font-size: 12px;
    color: #666;
}

.no-alerts {
    text-align: center;
    color: #666;
    font-style: italic;
    padding: 20px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.metric-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    text-align: center;
}

.metric-card h3 {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard {
        padding: 10px;
    }
    
    .dashboard-header {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
    
    .charts-grid {
        grid-template-columns: 1fr;
    }
    
    .status-grid,
    .metrics-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
}"""
        
        with open(self.static_dir / "styles.css", "w") as f:
            f.write(css_content)
    
    def _create_dashboard_js(self) -> None:
        """Create the JavaScript file for dashboard functionality"""
        js_content = """// Dashboard JavaScript
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
}"""
        
        with open(self.static_dir / "dashboard.js", "w") as f:
            f.write(js_content)


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == "/" or path == "/index.html":
                self._serve_file("index.html", "text/html")
            elif path == "/static/styles.css":
                self._serve_file("styles.css", "text/css")
            elif path == "/static/dashboard.js":
                self._serve_file("dashboard.js", "application/javascript")
            elif path == "/api/dashboard-data":
                self._serve_dashboard_data()
            else:
                self._send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _serve_file(self, filename: str, content_type: str):
        """Serve a static file"""
        try:
            file_path = self.server.dashboard.static_dir / filename
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_error(404, "File not found")
        except Exception as e:
            logger.error(f"Error serving file {filename}: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _serve_dashboard_data(self):
        """Serve dashboard data as JSON"""
        try:
            data = self.server.dashboard.get_dashboard_data()
            content = json.dumps(data, indent=2).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving dashboard data: {e}")
            self._send_error(500, "Internal Server Error")
    
    def _send_error(self, code: int, message: str):
        """Send an error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"{code} {message}".encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"HTTP {format % args}")


# Example usage and testing
if __name__ == "__main__":
    # Create dashboard configuration
    config = DashboardConfig(
        host="localhost",
        port=8080,
        theme=DashboardTheme.LIGHT,
        refresh_interval=5
    )
    
    # Create dashboard (without monitor/alerting system for testing)
    dashboard = InspectorMonitoringDashboard(config)
    
    # Start dashboard
    if dashboard.start_dashboard():
        print("Dashboard started successfully!")
        print("Press Ctrl+C to stop...")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping dashboard...")
            dashboard.stop_dashboard()
            print("Dashboard stopped.")
    else:
        print("Failed to start dashboard.") 