"""
Inspector Metrics Dashboard - Task 1.3.3
========================================

This module provides a web-based dashboard for visualizing Inspector metrics data,
performance trends, and analysis results. It offers real-time monitoring and
interactive charts for system performance analysis.

Key Features:
- Real-time metrics visualization with interactive charts
- Performance trend analysis and historical data display
- Bottleneck and anomaly visualization
- System health monitoring dashboard
- Configurable dashboard layouts and widgets
- Export capabilities for reports and charts
- Integration with Metrics Collector and Performance Analyzer

Author: Inspector Development Team
Date: January 2025
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from inspector_metrics_collector import MetricsCollector, MetricType
from inspector_performance_analyzer import PerformanceAnalyzer, PerformanceStatus, AlertLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardWidget(Enum):
    """Types of dashboard widgets available."""
    METRICS_OVERVIEW = "metrics_overview"
    PERFORMANCE_TRENDS = "performance_trends"
    SYSTEM_HEALTH = "system_health"
    BOTTLENECK_ANALYSIS = "bottleneck_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    ALERTS_PANEL = "alerts_panel"
    RECOMMENDATIONS = "recommendations"
    REAL_TIME_METRICS = "real_time_metrics"


@dataclass
class DashboardConfig:
    """Configuration for the dashboard."""
    port: int = 8080
    host: str = "localhost"
    refresh_interval: int = 30  # seconds
    max_data_points: int = 100
    enable_auto_refresh: bool = True
    widgets: List[DashboardWidget] = None
    theme: str = "light"  # "light" or "dark"


class MetricsDashboard:
    """
    Web-based dashboard for Inspector metrics visualization.
    
    Provides real-time monitoring, interactive charts, and performance analysis
    visualization through a web interface.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, 
                 performance_analyzer: PerformanceAnalyzer,
                 config: Optional[DashboardConfig] = None):
        """
        Initialize the metrics dashboard.
        
        Args:
            metrics_collector: Instance of MetricsCollector
            performance_analyzer: Instance of PerformanceAnalyzer
            config: Dashboard configuration
        """
        self.metrics_collector = metrics_collector
        self.performance_analyzer = performance_analyzer
        self.config = config or DashboardConfig()
        
        # Set default widgets if not specified
        if self.config.widgets is None:
            self.config.widgets = [
                DashboardWidget.METRICS_OVERVIEW,
                DashboardWidget.PERFORMANCE_TRENDS,
                DashboardWidget.SYSTEM_HEALTH,
                DashboardWidget.BOTTLENECK_ANALYSIS,
                DashboardWidget.ALERTS_PANEL
            ]
        
        # Dashboard state
        self.server: Optional[HTTPServer] = None
        self.is_running = False
        self.dashboard_thread: Optional[threading.Thread] = None
        
        # Data cache
        self.cached_data: Dict[str, Any] = {}
        self.last_update = datetime.now()
        
        logger.info("Metrics Dashboard initialized successfully")
    
    def start_dashboard(self):
        """Start the web dashboard server."""
        if self.is_running:
            logger.warning("Dashboard is already running")
            return
        
        try:
            # Create server
            self.server = HTTPServer((self.config.host, self.config.port), DashboardHandler)
            self.server.dashboard = self
            
            # Start server in a separate thread
            self.is_running = True
            self.dashboard_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.dashboard_thread.start()
            
            # Open browser
            url = f"http://{self.config.host}:{self.config.port}"
            logger.info(f"Dashboard started at: {url}")
            
            # Try to open browser (may fail in headless environments)
            try:
                webbrowser.open(url)
            except Exception as e:
                logger.info(f"Could not open browser automatically: {e}")
                logger.info(f"Please open your browser and navigate to: {url}")
            
        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")
            self.is_running = False
    
    def stop_dashboard(self):
        """Stop the web dashboard server."""
        if not self.is_running:
            logger.warning("Dashboard is not running")
            return
        
        try:
            self.is_running = False
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.dashboard_thread:
                self.dashboard_thread.join(timeout=5.0)
            
            logger.info("Dashboard stopped")
            
        except Exception as e:
            logger.error(f"Error stopping dashboard: {e}")
    
    def _run_server(self):
        """Run the HTTP server."""
        try:
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.is_running = False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data for all widgets."""
        try:
            current_time = datetime.now()
            
            # Update cache if needed
            if (current_time - self.last_update).total_seconds() > self.config.refresh_interval:
                self._update_cache()
                self.last_update = current_time
            
            return self.cached_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'error': str(e)}
    
    def _update_cache(self):
        """Update the dashboard data cache."""
        try:
            # Get metrics summary
            metrics_summary = self.metrics_collector.get_metrics_summary()
            
            # Get performance analysis
            analysis_results = self.performance_analyzer.analyze_performance()
            
            # Get alerts
            alerts = self.performance_analyzer.get_alerts()
            
            # Build dashboard data
            self.cached_data = {
                'timestamp': datetime.now().isoformat(),
                'metrics_overview': self._build_metrics_overview(metrics_summary),
                'performance_trends': self._build_performance_trends(analysis_results),
                'system_health': self._build_system_health(metrics_summary),
                'bottleneck_analysis': self._build_bottleneck_analysis(analysis_results),
                'anomaly_detection': self._build_anomaly_detection(analysis_results),
                'alerts_panel': self._build_alerts_panel(alerts),
                'recommendations': self._build_recommendations(analysis_results),
                'real_time_metrics': self._build_real_time_metrics(metrics_summary)
            }
            
        except Exception as e:
            logger.error(f"Error updating cache: {e}")
            self.cached_data = {'error': str(e)}
    
    def _build_metrics_overview(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build metrics overview widget data."""
        overview = {
            'total_metrics': 0,
            'active_metrics': 0,
            'critical_metrics': 0,
            'warning_metrics': 0,
            'metric_status': {}
        }
        
        try:
            for metric_type, data in metrics_summary.get('metrics', {}).items():
                overview['total_metrics'] += 1
                
                # Determine metric status
                if metric_type == 'response_time':
                    avg_value = data.get('average', 0)
                    if avg_value > 10.0:
                        status = 'critical'
                        overview['critical_metrics'] += 1
                    elif avg_value > 5.0:
                        status = 'warning'
                        overview['warning_metrics'] += 1
                    else:
                        status = 'good'
                        overview['active_metrics'] += 1
                
                elif metric_type == 'success_rate':
                    avg_value = data.get('average', 1.0)
                    if avg_value < 0.7:
                        status = 'critical'
                        overview['critical_metrics'] += 1
                    elif avg_value < 0.9:
                        status = 'warning'
                        overview['warning_metrics'] += 1
                    else:
                        status = 'good'
                        overview['active_metrics'] += 1
                
                else:
                    status = 'good'
                    overview['active_metrics'] += 1
                
                overview['metric_status'][metric_type] = {
                    'status': status,
                    'value': data.get('average', 0),
                    'latest': data.get('latest', 0)
                }
        
        except Exception as e:
            logger.error(f"Error building metrics overview: {e}")
        
        return overview
    
    def _build_performance_trends(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build performance trends widget data."""
        trends_data = {
            'trends': [],
            'trend_summary': {
                'improving': 0,
                'stable': 0,
                'degrading': 0
            }
        }
        
        try:
            for trend in analysis_results.get('trends', []):
                trend_info = {
                    'metric': trend.metric_type.value,
                    'direction': trend.trend_direction,
                    'strength': trend.trend_strength,
                    'slope': trend.slope,
                    'confidence': trend.confidence
                }
                trends_data['trends'].append(trend_info)
                
                # Update summary
                trends_data['trend_summary'][trend.trend_direction] += 1
        
        except Exception as e:
            logger.error(f"Error building performance trends: {e}")
        
        return trends_data
    
    def _build_system_health(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build system health widget data."""
        health_data = {
            'overall_status': 'unknown',
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_io': {},
            'process_count': 0
        }
        
        try:
            if 'system_health' in metrics_summary.get('metrics', {}):
                system_data = metrics_summary['metrics']['system_health']
                
                # Extract system metrics from metadata
                if system_data.get('metadata', {}):
                    metadata = system_data['metadata']
                    health_data['cpu_usage'] = system_data.get('average', 0)
                    health_data['memory_usage'] = metadata.get('memory_percent', 0)
                    health_data['disk_usage'] = metadata.get('disk_usage_percent', 0)
                    health_data['process_count'] = metadata.get('process_count', 0)
                
                # Determine overall status
                if health_data['cpu_usage'] > 90 or health_data['memory_usage'] > 95:
                    health_data['overall_status'] = 'critical'
                elif health_data['cpu_usage'] > 80 or health_data['memory_usage'] > 85:
                    health_data['overall_status'] = 'warning'
                else:
                    health_data['overall_status'] = 'good'
        
        except Exception as e:
            logger.error(f"Error building system health: {e}")
        
        return health_data
    
    def _build_bottleneck_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build bottleneck analysis widget data."""
        bottleneck_data = {
            'total_bottlenecks': 0,
            'critical_bottlenecks': 0,
            'bottlenecks': [],
            'severity_distribution': {
                'critical': 0,
                'degraded': 0
            }
        }
        
        try:
            for bottleneck in analysis_results.get('bottlenecks', []):
                bottleneck_info = {
                    'type': bottleneck.bottleneck_type,
                    'severity': bottleneck.severity.value,
                    'impact_score': bottleneck.impact_score,
                    'root_cause': bottleneck.root_cause,
                    'recommendations': bottleneck.recommendations[:3]  # Top 3 recommendations
                }
                bottleneck_data['bottlenecks'].append(bottleneck_info)
                bottleneck_data['total_bottlenecks'] += 1
                
                if bottleneck.severity == PerformanceStatus.CRITICAL:
                    bottleneck_data['critical_bottlenecks'] += 1
                    bottleneck_data['severity_distribution']['critical'] += 1
                else:
                    bottleneck_data['severity_distribution']['degraded'] += 1
        
        except Exception as e:
            logger.error(f"Error building bottleneck analysis: {e}")
        
        return bottleneck_data
    
    def _build_anomaly_detection(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build anomaly detection widget data."""
        anomaly_data = {
            'total_anomalies': 0,
            'critical_anomalies': 0,
            'anomalies': [],
            'anomaly_types': {
                'spike': 0,
                'drop': 0,
                'deviation': 0
            }
        }
        
        try:
            for anomaly in analysis_results.get('anomalies', []):
                anomaly_info = {
                    'metric': anomaly.metric_type.value,
                    'type': anomaly.anomaly_type,
                    'severity': anomaly.severity.value,
                    'deviation': anomaly.deviation,
                    'timestamp': anomaly.timestamp.isoformat(),
                    'expected': anomaly.expected_value,
                    'actual': anomaly.actual_value
                }
                anomaly_data['anomalies'].append(anomaly_info)
                anomaly_data['total_anomalies'] += 1
                
                if anomaly.severity == AlertLevel.CRITICAL:
                    anomaly_data['critical_anomalies'] += 1
                
                anomaly_data['anomaly_types'][anomaly.anomaly_type] += 1
        
        except Exception as e:
            logger.error(f"Error building anomaly detection: {e}")
        
        return anomaly_data
    
    def _build_alerts_panel(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build alerts panel widget data."""
        alerts_data = {
            'total_alerts': len(alerts),
            'critical_alerts': 0,
            'warning_alerts': 0,
            'info_alerts': 0,
            'recent_alerts': []
        }
        
        try:
            # Count alerts by level
            for alert in alerts:
                if alert['level'] == 'critical':
                    alerts_data['critical_alerts'] += 1
                elif alert['level'] == 'warning':
                    alerts_data['warning_alerts'] += 1
                else:
                    alerts_data['info_alerts'] += 1
            
            # Get recent alerts (last 10)
            recent_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:10]
            alerts_data['recent_alerts'] = recent_alerts
        
        except Exception as e:
            logger.error(f"Error building alerts panel: {e}")
        
        return alerts_data
    
    def _build_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build recommendations widget data."""
        recommendations_data = {
            'total_recommendations': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0,
            'recommendations': []
        }
        
        try:
            for rec in analysis_results.get('recommendations', []):
                rec_info = {
                    'type': rec.recommendation_type,
                    'priority': rec.priority,
                    'impact_score': rec.impact_score,
                    'effort_score': rec.effort_score,
                    'description': rec.description,
                    'implementation_steps': rec.implementation_steps[:3]  # Top 3 steps
                }
                recommendations_data['recommendations'].append(rec_info)
                recommendations_data['total_recommendations'] += 1
                
                if rec.priority >= 4:
                    recommendations_data['high_priority'] += 1
                elif rec.priority >= 2:
                    recommendations_data['medium_priority'] += 1
                else:
                    recommendations_data['low_priority'] += 1
        
        except Exception as e:
            logger.error(f"Error building recommendations: {e}")
        
        return recommendations_data
    
    def _build_real_time_metrics(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build real-time metrics widget data."""
        real_time_data = {
            'current_metrics': {},
            'update_frequency': self.config.refresh_interval,
            'last_update': datetime.now().isoformat()
        }
        
        try:
            for metric_type, data in metrics_summary.get('metrics', {}).items():
                real_time_data['current_metrics'][metric_type] = {
                    'current_value': data.get('latest', 0),
                    'average_value': data.get('average', 0),
                    'min_value': data.get('min', 0),
                    'max_value': data.get('max', 0),
                    'data_points': data.get('count', 0)
                }
        
        except Exception as e:
            logger.error(f"Error building real-time metrics: {e}")
        
        return real_time_data
    
    def export_dashboard_report(self, format: str = 'json') -> str:
        """Export current dashboard data as a report."""
        try:
            dashboard_data = self.get_dashboard_data()
            
            if format.lower() == 'json':
                return json.dumps(dashboard_data, indent=2, default=str)
            elif format.lower() == 'html':
                return self._generate_html_report(dashboard_data)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting dashboard report: {e}")
            return f"Error: {e}"
    
    def _generate_html_report(self, dashboard_data: Dict[str, Any]) -> str:
        """Generate HTML report from dashboard data."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Inspector Metrics Dashboard Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px; }
        .critical { background: #ffebee; border-left: 4px solid #f44336; }
        .warning { background: #fff3e0; border-left: 4px solid #ff9800; }
        .good { background: #e8f5e8; border-left: 4px solid #4caf50; }
        .alert { margin: 10px 0; padding: 10px; border-radius: 3px; }
        .alert.critical { background: #ffebee; border: 1px solid #f44336; }
        .alert.warning { background: #fff3e0; border: 1px solid #ff9800; }
        .alert.info { background: #e3f2fd; border: 1px solid #2196f3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Inspector Metrics Dashboard Report</h1>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Metrics Overview</h2>
        <p>Total Metrics: {total_metrics}</p>
        <p>Active Metrics: {active_metrics}</p>
        <p>Critical Metrics: {critical_metrics}</p>
        <p>Warning Metrics: {warning_metrics}</p>
    </div>
    
    <div class="section">
        <h2>System Health</h2>
        <p>Overall Status: <span class="{health_status}">{health_status}</span></p>
        <p>CPU Usage: {cpu_usage}%</p>
        <p>Memory Usage: {memory_usage}%</p>
        <p>Process Count: {process_count}</p>
    </div>
    
    <div class="section">
        <h2>Recent Alerts</h2>
        {alerts_html}
    </div>
    
    <div class="section">
        <h2>Top Recommendations</h2>
        {recommendations_html}
    </div>
</body>
</html>
        """
        
        # Extract data for HTML template
        metrics_overview = dashboard_data.get('metrics_overview', {})
        system_health = dashboard_data.get('system_health', {})
        alerts_panel = dashboard_data.get('alerts_panel', {})
        recommendations = dashboard_data.get('recommendations', {})
        
        # Generate alerts HTML
        alerts_html = ""
        for alert in alerts_panel.get('recent_alerts', [])[:5]:
            alerts_html += f"""
            <div class="alert {alert['level']}">
                <strong>{alert['title']}</strong><br>
                {alert['message']}<br>
                <small>{alert['timestamp']}</small>
            </div>
            """
        
        # Generate recommendations HTML
        recommendations_html = ""
        for rec in recommendations.get('recommendations', [])[:5]:
            recommendations_html += f"""
            <div class="metric">
                <strong>{rec['type']}</strong> (Priority: {rec['priority']})<br>
                {rec['description']}
            </div>
            """
        
        # Fill template
        html_content = html_template.format(
            timestamp=dashboard_data.get('timestamp', 'Unknown'),
            total_metrics=metrics_overview.get('total_metrics', 0),
            active_metrics=metrics_overview.get('active_metrics', 0),
            critical_metrics=metrics_overview.get('critical_metrics', 0),
            warning_metrics=metrics_overview.get('warning_metrics', 0),
            health_status=system_health.get('overall_status', 'unknown'),
            cpu_usage=system_health.get('cpu_usage', 0),
            memory_usage=system_health.get('memory_usage', 0),
            process_count=system_health.get('process_count', 0),
            alerts_html=alerts_html,
            recommendations_html=recommendations_html
        )
        
        return html_content


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == '/':
                self._serve_dashboard()
            elif path == '/api/data':
                self._serve_api_data()
            elif path == '/api/export':
                self._serve_export()
            else:
                self._serve_404()
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._serve_error(str(e))
    
    def _serve_dashboard(self):
        """Serve the main dashboard HTML."""
        html_content = self._get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _serve_api_data(self):
        """Serve dashboard data as JSON."""
        dashboard_data = self.server.dashboard.get_dashboard_data()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(dashboard_data, default=str).encode('utf-8'))
    
    def _serve_export(self):
        """Serve exported dashboard report."""
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        format_type = query_params.get('format', ['json'])[0]
        
        report_data = self.server.dashboard.export_dashboard_report(format_type)
        
        if format_type == 'html':
            content_type = 'text/html'
        else:
            content_type = 'application/json'
        
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-Disposition', f'attachment; filename="dashboard_report.{format_type}"')
        self.end_headers()
        self.wfile.write(report_data.encode('utf-8'))
    
    def _serve_404(self):
        """Serve 404 error page."""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 - Page Not Found</h1>')
    
    def _serve_error(self, error_message: str):
        """Serve error page."""
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f'<h1>500 - Server Error</h1><p>{error_message}</p>'.encode('utf-8'))
    
    def _get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Inspector Metrics Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .header { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .dashboard-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 20px; 
        }
        .widget { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .widget h3 { 
            margin-top: 0; 
            color: #333; 
        }
        .metric-card { 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            background: #f8f9fa; 
            border-radius: 6px; 
            border-left: 4px solid #007bff; 
        }
        .metric-card.critical { border-left-color: #dc3545; background: #f8d7da; }
        .metric-card.warning { border-left-color: #ffc107; background: #fff3cd; }
        .metric-card.good { border-left-color: #28a745; background: #d4edda; }
        .alert { 
            margin: 10px 0; 
            padding: 10px; 
            border-radius: 4px; 
        }
        .alert.critical { background: #f8d7da; border: 1px solid #dc3545; }
        .alert.warning { background: #fff3cd; border: 1px solid #ffc107; }
        .alert.info { background: #d1ecf1; border: 1px solid #17a2b8; }
        .refresh-btn { 
            background: #007bff; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        .refresh-btn:hover { background: #0056b3; }
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px; 
        }
        .status-good { background: #28a745; }
        .status-warning { background: #ffc107; }
        .status-critical { background: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Inspector Metrics Dashboard</h1>
        <p>Real-time monitoring and performance analysis</p>
        <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
        <span id="last-update"></span>
    </div>
    
    <div class="dashboard-grid" id="dashboard-content">
        <div class="widget">
            <h3>Loading...</h3>
            <p>Please wait while dashboard data loads...</p>
        </div>
    </div>
    
    <script>
        let dashboardData = {};
        
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/data');
                dashboardData = await response.json();
                updateDashboard();
                updateLastUpdate();
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                document.getElementById('dashboard-content').innerHTML = 
                    '<div class="widget"><h3>Error</h3><p>Failed to load dashboard data</p></div>';
            }
        }
        
        function updateDashboard() {
            const content = document.getElementById('dashboard-content');
            content.innerHTML = '';
            
            // Metrics Overview
            if (dashboardData.metrics_overview) {
                content.innerHTML += createMetricsOverviewWidget(dashboardData.metrics_overview);
            }
            
            // System Health
            if (dashboardData.system_health) {
                content.innerHTML += createSystemHealthWidget(dashboardData.system_health);
            }
            
            // Alerts Panel
            if (dashboardData.alerts_panel) {
                content.innerHTML += createAlertsWidget(dashboardData.alerts_panel);
            }
            
            // Bottleneck Analysis
            if (dashboardData.bottleneck_analysis) {
                content.innerHTML += createBottleneckWidget(dashboardData.bottleneck_analysis);
            }
            
            // Recommendations
            if (dashboardData.recommendations) {
                content.innerHTML += createRecommendationsWidget(dashboardData.recommendations);
            }
        }
        
        function createMetricsOverviewWidget(data) {
            return `
                <div class="widget">
                    <h3>Metrics Overview</h3>
                    <div class="metric-card">
                        <strong>Total Metrics:</strong> ${data.total_metrics}
                    </div>
                    <div class="metric-card good">
                        <strong>Active:</strong> ${data.active_metrics}
                    </div>
                    <div class="metric-card warning">
                        <strong>Warnings:</strong> ${data.warning_metrics}
                    </div>
                    <div class="metric-card critical">
                        <strong>Critical:</strong> ${data.critical_metrics}
                    </div>
                </div>
            `;
        }
        
        function createSystemHealthWidget(data) {
            const statusClass = data.overall_status === 'good' ? 'good' : 
                              data.overall_status === 'warning' ? 'warning' : 'critical';
            return `
                <div class="widget">
                    <h3>System Health</h3>
                    <div class="metric-card ${statusClass}">
                        <span class="status-indicator status-${data.overall_status}"></span>
                        <strong>Status:</strong> ${data.overall_status}
                    </div>
                    <div class="metric-card">
                        <strong>CPU Usage:</strong> ${data.cpu_usage.toFixed(1)}%
                    </div>
                    <div class="metric-card">
                        <strong>Memory Usage:</strong> ${data.memory_usage.toFixed(1)}%
                    </div>
                    <div class="metric-card">
                        <strong>Processes:</strong> ${data.process_count}
                    </div>
                </div>
            `;
        }
        
        function createAlertsWidget(data) {
            let alertsHtml = '';
            data.recent_alerts.forEach(alert => {
                alertsHtml += `
                    <div class="alert ${alert.level}">
                        <strong>${alert.title}</strong><br>
                        ${alert.message}<br>
                        <small>${new Date(alert.timestamp).toLocaleString()}</small>
                    </div>
                `;
            });
            
            return `
                <div class="widget">
                    <h3>Recent Alerts (${data.total_alerts})</h3>
                    ${alertsHtml || '<p>No recent alerts</p>'}
                </div>
            `;
        }
        
        function createBottleneckWidget(data) {
            return `
                <div class="widget">
                    <h3>Bottleneck Analysis</h3>
                    <div class="metric-card">
                        <strong>Total:</strong> ${data.total_bottlenecks}
                    </div>
                    <div class="metric-card critical">
                        <strong>Critical:</strong> ${data.critical_bottlenecks}
                    </div>
                    ${data.bottlenecks.map(b => `
                        <div class="metric-card ${b.severity}">
                            <strong>${b.type}</strong><br>
                            Impact: ${(b.impact_score * 100).toFixed(1)}%
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function createRecommendationsWidget(data) {
            return `
                <div class="widget">
                    <h3>Top Recommendations</h3>
                    <div class="metric-card">
                        <strong>Total:</strong> ${data.total_recommendations}
                    </div>
                    <div class="metric-card">
                        <strong>High Priority:</strong> ${data.high_priority}
                    </div>
                    ${data.recommendations.slice(0, 3).map(rec => `
                        <div class="metric-card">
                            <strong>${rec.type}</strong> (Priority: ${rec.priority})<br>
                            ${rec.description}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function updateLastUpdate() {
            const timestamp = dashboardData.timestamp || 'Unknown';
            document.getElementById('last-update').textContent = 
                `Last updated: ${new Date(timestamp).toLocaleString()}`;
        }
        
        function refreshData() {
            loadDashboardData();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadDashboardData, 30000);
        
        // Load initial data
        loadDashboardData();
    </script>
</body>
</html>
        """


def main():
    """Main function for testing the metrics dashboard."""
    print("Inspector Metrics Dashboard - Task 1.3.3")
    print("=" * 50)
    
    # Initialize components
    collector = MetricsCollector()
    analyzer = PerformanceAnalyzer(collector)
    dashboard = MetricsDashboard(collector, analyzer)
    
    try:
        # Start collection and analysis
        print("Starting metrics collection...")
        collector.start_collection()
        
        # Simulate some operations
        print("Simulating operations...")
        for i in range(5):
            operation_id = f"test_op_{i}"
            collector.record_operation_start(operation_id, f"test_tool_{i}")
            
            # Simulate operation duration
            time.sleep(0.3)
            
            success = i % 3 != 0  # Some operations fail
            collector.record_operation_end(operation_id, success)
        
        # Start dashboard
        print("Starting dashboard...")
        dashboard.start_dashboard()
        
        # Keep running
        print("Dashboard is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
    finally:
        dashboard.stop_dashboard()
        collector.stop_collection()
        print("Dashboard stopped")


if __name__ == "__main__":
    main() 