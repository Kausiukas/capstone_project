"""
Inspector Quality Dashboard Module
Task 3.2.3: Inspector Quality Dashboard

This module provides a web-based dashboard for visualizing quality metrics,
defect tracking, and quality management data.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

from inspector_config_manager import InspectorConfigManager
from inspector_quality_assurance import InspectorQualityAssurance, QualityMetric, QualityLevel
from inspector_defect_tracker import InspectorDefectTracker, DefectStatus, DefectSeverity, DefectCategory


class QualityDashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the quality dashboard."""
    
    def __init__(self, *args, quality_assurance: InspectorQualityAssurance, 
                 defect_tracker: InspectorDefectTracker, **kwargs):
        self.quality_assurance = quality_assurance
        self.defect_tracker = defect_tracker
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            if path == "/" or path == "/index.html":
                self._serve_dashboard()
            elif path == "/api/quality-report":
                self._serve_quality_report()
            elif path == "/api/defect-statistics":
                self._serve_defect_statistics()
            elif path == "/api/defects":
                self._serve_defects()
            elif path == "/api/quality-trends":
                self._serve_quality_trends()
            elif path.startswith("/static/"):
                self._serve_static_file(path[8:])  # Remove /static/ prefix
            else:
                self._serve_404()
        
        except Exception as e:
            self._serve_error(str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            if path == "/api/defects":
                self._handle_defect_update()
            elif path == "/api/quality-metrics":
                self._handle_quality_metric_add()
            else:
                self._serve_404()
        
        except Exception as e:
            self._serve_error(str(e))
    
    def _serve_dashboard(self):
        """Serve the main dashboard HTML."""
        html_content = self._generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _serve_quality_report(self):
        """Serve quality report data."""
        report = self.quality_assurance.generate_quality_report()
        
        # Convert report to serializable format
        report_data = {
            "overall_score": report.overall_score,
            "overall_level": report.overall_level.value,
            "metric_scores": {
                metric.value: {
                    "score": score.score,
                    "level": score.level.value,
                    "weight": score.weight,
                    "details": score.details
                }
                for metric, score in report.metric_scores.items()
            },
            "recommendations": report.recommendations,
            "timestamp": report.timestamp.isoformat(),
            "summary": report.summary
        }
        
        self._serve_json(report_data)
    
    def _serve_defect_statistics(self):
        """Serve defect statistics."""
        stats = self.defect_tracker.get_defect_statistics()
        
        stats_data = {
            "total_defects": stats.total_defects,
            "open_defects": stats.open_defects,
            "resolved_defects": stats.resolved_defects,
            "closed_defects": stats.closed_defects,
            "critical_defects": stats.critical_defects,
            "high_priority_defects": stats.high_priority_defects,
            "resolution_rate": stats.resolution_rate,
            "average_resolution_time": stats.average_resolution_time,
            "defects_by_category": {cat.value: count for cat, count in stats.defects_by_category.items()},
            "defects_by_severity": {sev.value: count for sev, count in stats.defects_by_severity.items()},
            "defects_by_status": {status.value: count for status, count in stats.defects_by_status.items()}
        }
        
        self._serve_json(stats_data)
    
    def _serve_defects(self):
        """Serve defects data."""
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Get filters
        status_filter = query_params.get('status', [None])[0]
        severity_filter = query_params.get('severity', [None])[0]
        category_filter = query_params.get('category', [None])[0]
        
        # Apply filters
        filters = {}
        if status_filter:
            filters['status'] = DefectStatus(status_filter)
        if severity_filter:
            filters['severity'] = DefectSeverity(severity_filter)
        if category_filter:
            filters['category'] = DefectCategory(category_filter)
        
        defects = self.defect_tracker.search_defects(**filters)
        
        # Convert to serializable format
        defects_data = []
        for defect in defects:
            defect_dict = {
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "severity": defect.severity.value,
                "priority": defect.priority.value,
                "category": defect.category.value,
                "status": defect.status.value,
                "created_at": defect.created_at.isoformat(),
                "updated_at": defect.updated_at.isoformat(),
                "reported_by": defect.reported_by,
                "assigned_to": defect.assigned_to,
                "component": defect.component,
                "version": defect.version,
                "resolution": defect.resolution,
                "resolved_at": defect.resolved_at.isoformat() if defect.resolved_at else None,
                "resolved_by": defect.resolved_by,
                "comments_count": len(defect.comments)
            }
            defects_data.append(defect_dict)
        
        self._serve_json(defects_data)
    
    def _serve_quality_trends(self):
        """Serve quality trends data."""
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        metric_name = query_params.get('metric', ['functionality'])[0]
        days = int(query_params.get('days', ['7'])[0])
        
        try:
            metric = QualityMetric(metric_name)
            trends = self.quality_assurance.get_quality_trends(metric, days)
            
            trends_data = [
                {
                    "date": date.isoformat(),
                    "value": value
                }
                for date, value in trends
            ]
            
            self._serve_json(trends_data)
        
        except ValueError:
            self._serve_error(f"Invalid metric: {metric_name}")
    
    def _handle_defect_update(self):
        """Handle defect updates."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        defect_id = data.get('id')
        updates = data.get('updates', {})
        
        if not defect_id:
            self._serve_error("Defect ID is required")
            return
        
        success = self.defect_tracker.update_defect(defect_id, **updates)
        
        if success:
            self._serve_json({"success": True, "message": "Defect updated successfully"})
        else:
            self._serve_error("Failed to update defect")
    
    def _handle_quality_metric_add(self):
        """Handle adding quality metrics."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            metric = QualityMetric(data['metric'])
            value = float(data['value'])
            description = data['description']
            source = data['source']
            
            self.quality_assurance.add_quality_metric(
                metric=metric,
                value=value,
                description=description,
                source=source,
                weight=data.get('weight'),
                confidence=data.get('confidence', 1.0)
            )
            
            self._serve_json({"success": True, "message": "Quality metric added successfully"})
        
        except (KeyError, ValueError) as e:
            self._serve_error(f"Invalid data: {str(e)}")
    
    def _serve_static_file(self, filename: str):
        """Serve static files (CSS, JS)."""
        static_dir = Path(__file__).parent / "static"
        filepath = static_dir / filename
        
        if not filepath.exists():
            self._serve_404()
            return
        
        # Determine content type
        content_type = "text/plain"
        if filename.endswith('.css'):
            content_type = "text/css"
        elif filename.endswith('.js'):
            content_type = "application/javascript"
        elif filename.endswith('.png'):
            content_type = "image/png"
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = "image/jpeg"
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)
    
    def _serve_json(self, data: Any):
        """Serve JSON response."""
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json_content.encode('utf-8'))
    
    def _serve_404(self):
        """Serve 404 error."""
        self.send_response(404)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"404 - Not Found")
    
    def _serve_error(self, message: str):
        """Serve error response."""
        error_data = {"error": message}
        self.send_response(400)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def _generate_dashboard_html(self) -> str:
        """Generate the main dashboard HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspector Quality Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
        }}
        
        .card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .metric-label {{
            font-weight: 500;
        }}
        
        .metric-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .quality-score {{
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        
        .excellent {{ color: #28a745; }}
        .good {{ color: #17a2b8; }}
        .acceptable {{ color: #ffc107; }}
        .poor {{ color: #fd7e14; }}
        .critical {{ color: #dc3545; }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .defects-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .defects-table th,
        .defects-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .defects-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        
        .severity-critical {{ color: #dc3545; font-weight: bold; }}
        .severity-high {{ color: #fd7e14; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; font-weight: bold; }}
        .severity-low {{ color: #28a745; }}
        .severity-minor {{ color: #6c757d; }}
        
        .status-open {{ color: #dc3545; }}
        .status-in_progress {{ color: #ffc107; }}
        .status-resolved {{ color: #28a745; }}
        .status-closed {{ color: #6c757d; }}
        
        .chart-container {{
            height: 300px;
            margin: 20px 0;
        }}
        
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 0;
        }}
        
        .refresh-btn:hover {{
            background: #5a6fd8;
        }}
        
        .loading {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Inspector Quality Dashboard</h1>
        <p>Comprehensive quality monitoring and defect tracking for the Inspector system</p>
    </div>
    
    <div class="container">
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Dashboard</button>
        
        <div class="dashboard-grid">
            <!-- Quality Overview Card -->
            <div class="card">
                <h3>📊 Quality Overview</h3>
                <div id="quality-overview" class="loading">Loading...</div>
            </div>
            
            <!-- Defect Statistics Card -->
            <div class="card">
                <h3>🐛 Defect Statistics</h3>
                <div id="defect-stats" class="loading">Loading...</div>
            </div>
            
            <!-- Quality Metrics Card -->
            <div class="card">
                <h3>📈 Quality Metrics</h3>
                <div id="quality-metrics" class="loading">Loading...</div>
            </div>
            
            <!-- Defect Categories Card -->
            <div class="card">
                <h3>📋 Defect Categories</h3>
                <div id="defect-categories" class="loading">Loading...</div>
            </div>
        </div>
        
        <!-- Recent Defects Table -->
        <div class="card">
            <h3>📝 Recent Defects</h3>
            <div id="recent-defects" class="loading">Loading...</div>
        </div>
        
        <!-- Quality Trends Chart -->
        <div class="card">
            <h3>📈 Quality Trends</h3>
            <div class="chart-container" id="quality-trends">
                <div class="loading">Loading trends...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard functionality
        let refreshInterval;
        
        function refreshDashboard() {{
            loadQualityOverview();
            loadDefectStatistics();
            loadQualityMetrics();
            loadDefectCategories();
            loadRecentDefects();
            loadQualityTrends();
        }}
        
        async function loadQualityOverview() {{
            try {{
                const response = await fetch('/api/quality-report');
                const data = await response.json();
                
                const overviewDiv = document.getElementById('quality-overview');
                const qualityClass = data.overall_level.toLowerCase();
                
                overviewDiv.innerHTML = `
                    <div class="quality-score ${{qualityClass}}">${{(data.overall_score * 100).toFixed(1)}}%</div>
                    <div class="metric">
                        <span class="metric-label">Overall Level:</span>
                        <span class="metric-value">${{data.overall_level.toUpperCase()}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Recommendations:</span>
                        <span class="metric-value">${{data.recommendations.length}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Updated:</span>
                        <span class="metric-value">${{new Date(data.timestamp).toLocaleString()}}</span>
                    </div>
                `;
            }} catch (error) {{
                console.error('Error loading quality overview:', error);
                document.getElementById('quality-overview').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        async function loadDefectStatistics() {{
            try {{
                const response = await fetch('/api/defect-statistics');
                const data = await response.json();
                
                const statsDiv = document.getElementById('defect-stats');
                const resolutionRate = data.resolution_rate ? (data.resolution_rate * 100).toFixed(1) : 'N/A';
                
                statsDiv.innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total Defects:</span>
                        <span class="metric-value">${{data.total_defects}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Open Defects:</span>
                        <span class="metric-value">${{data.open_defects}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Critical Defects:</span>
                        <span class="metric-value">${{data.critical_defects}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">High Priority:</span>
                        <span class="metric-value">${{data.high_priority_defects}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Resolution Rate:</span>
                        <span class="metric-value">${{resolutionRate}}%</span>
                    </div>
                `;
            }} catch (error) {{
                console.error('Error loading defect statistics:', error);
                document.getElementById('defect-stats').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        async function loadQualityMetrics() {{
            try {{
                const response = await fetch('/api/quality-report');
                const data = await response.json();
                
                const metricsDiv = document.getElementById('quality-metrics');
                let metricsHtml = '';
                
                for (const [metric, score] of Object.entries(data.metric_scores)) {{
                    const percentage = (score.score * 100).toFixed(1);
                    const qualityClass = score.level.toLowerCase();
                    
                    metricsHtml += `
                        <div class="metric">
                            <span class="metric-label">${{metric.charAt(0).toUpperCase() + metric.slice(1)}}:</span>
                            <span class="metric-value ${{qualityClass}}">${{percentage}}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill ${{qualityClass}}" style="width: ${{percentage}}%; background-color: ${{getQualityColor(score.level)}};"></div>
                        </div>
                    `;
                }}
                
                metricsDiv.innerHTML = metricsHtml;
            }} catch (error) {{
                console.error('Error loading quality metrics:', error);
                document.getElementById('quality-metrics').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        async function loadDefectCategories() {{
            try {{
                const response = await fetch('/api/defect-statistics');
                const data = await response.json();
                
                const categoriesDiv = document.getElementById('defect-categories');
                let categoriesHtml = '';
                
                for (const [category, count] of Object.entries(data.defects_by_category)) {{
                    categoriesHtml += `
                        <div class="metric">
                            <span class="metric-label">${{category.charAt(0).toUpperCase() + category.slice(1)}}:</span>
                            <span class="metric-value">${{count}}</span>
                        </div>
                    `;
                }}
                
                categoriesDiv.innerHTML = categoriesHtml;
            }} catch (error) {{
                console.error('Error loading defect categories:', error);
                document.getElementById('defect-categories').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        async function loadRecentDefects() {{
            try {{
                const response = await fetch('/api/defects?limit=10');
                const data = await response.json();
                
                const defectsDiv = document.getElementById('recent-defects');
                
                if (data.length === 0) {{
                    defectsDiv.innerHTML = '<p>No defects found.</p>';
                    return;
                }}
                
                let tableHtml = `
                    <table class="defects-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Severity</th>
                                <th>Status</th>
                                <th>Category</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.slice(0, 10).forEach(defect => {{
                    tableHtml += `
                        <tr>
                            <td>${{defect.id.substring(0, 8)}}...</td>
                            <td>${{defect.title}}</td>
                            <td class="severity-${{defect.severity}}">${{defect.severity.toUpperCase()}}</td>
                            <td class="status-${{defect.status}}">${{defect.status.replace('_', ' ').toUpperCase()}}</td>
                            <td>${{defect.category.charAt(0).toUpperCase() + defect.category.slice(1)}}</td>
                            <td>${{new Date(defect.created_at).toLocaleDateString()}}</td>
                        </tr>
                    `;
                }});
                
                tableHtml += '</tbody></table>';
                defectsDiv.innerHTML = tableHtml;
            }} catch (error) {{
                console.error('Error loading recent defects:', error);
                document.getElementById('recent-defects').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        async function loadQualityTrends() {{
            try {{
                const response = await fetch('/api/quality-trends?metric=functionality&days=7');
                const data = await response.json();
                
                const trendsDiv = document.getElementById('quality-trends');
                
                if (data.length === 0) {{
                    trendsDiv.innerHTML = '<p>No trend data available.</p>';
                    return;
                }}
                
                // Simple trend visualization
                let trendsHtml = '<div style="height: 200px; display: flex; align-items: end; gap: 2px;">';
                
                data.forEach(point => {{
                    const height = (point.value * 100) + '%';
                    const color = getQualityColor(getQualityLevel(point.value));
                    trendsHtml += `<div style="flex: 1; background: ${{color}}; height: ${{height}}; min-height: 10px;"></div>`;
                }});
                
                trendsHtml += '</div>';
                trendsDiv.innerHTML = trendsHtml;
            }} catch (error) {{
                console.error('Error loading quality trends:', error);
                document.getElementById('quality-trends').innerHTML = '<div class="loading">Error loading data</div>';
            }}
        }}
        
        function getQualityColor(level) {{
            const colors = {{
                'excellent': '#28a745',
                'good': '#17a2b8',
                'acceptable': '#ffc107',
                'poor': '#fd7e14',
                'critical': '#dc3545'
            }};
            return colors[level.toLowerCase()] || '#6c757d';
        }}
        
        function getQualityLevel(score) {{
            if (score >= 0.9) return 'excellent';
            if (score >= 0.8) return 'good';
            if (score >= 0.7) return 'acceptable';
            if (score >= 0.6) return 'poor';
            return 'critical';
        }}
        
        // Auto-refresh every 30 seconds
        function startAutoRefresh() {{
            refreshInterval = setInterval(refreshDashboard, 30000);
        }}
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            refreshDashboard();
            startAutoRefresh();
        }});
    </script>
</body>
</html>
        """
    
    def log_message(self, format, *args):
        """Override to reduce logging verbosity."""
        pass


class InspectorQualityDashboard:
    """
    Web-based quality dashboard for the Inspector system.
    
    Provides real-time visualization of quality metrics and defect tracking.
    """
    
    def __init__(self, config_manager: InspectorConfigManager,
                 quality_assurance: InspectorQualityAssurance,
                 defect_tracker: InspectorDefectTracker):
        """Initialize the quality dashboard."""
        self.config_manager = config_manager
        self.quality_assurance = quality_assurance
        self.defect_tracker = defect_tracker
        self.logger = logging.getLogger(__name__)
        
        self.server = None
        self.server_thread = None
        self.port = 8080
        
        # Ensure static directory exists
        self.static_dir = Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
    
    def start_dashboard(self, port: int = 8080, auto_open: bool = True) -> str:
        """Start the quality dashboard server."""
        self.port = port
        
        # Create custom handler with dependencies
        def handler_factory(*args, **kwargs):
            return QualityDashboardHandler(
                *args,
                quality_assurance=self.quality_assurance,
                defect_tracker=self.defect_tracker,
                **kwargs
            )
        
        # Start server in a separate thread
        def run_server():
            self.server = HTTPServer(('localhost', port), handler_factory)
            self.logger.info(f"Quality dashboard started on http://localhost:{port}")
            self.server.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        dashboard_url = f"http://localhost:{port}"
        
        if auto_open:
            try:
                webbrowser.open(dashboard_url)
                self.logger.info(f"Opened dashboard in browser: {dashboard_url}")
            except Exception as e:
                self.logger.warning(f"Could not open browser automatically: {e}")
                print(f"Dashboard available at: {dashboard_url}")
        else:
            print(f"Dashboard available at: {dashboard_url}")
        
        return dashboard_url
    
    def stop_dashboard(self) -> None:
        """Stop the quality dashboard server."""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.logger.info("Quality dashboard stopped")
    
    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get dashboard status information."""
        return {
            "running": self.server is not None,
            "port": self.port,
            "url": f"http://localhost:{self.port}" if self.server else None,
            "thread_alive": self.server_thread.is_alive() if self.server_thread else False
        }


def main():
    """Main function for testing the quality dashboard."""
    # Initialize components
    config_manager = InspectorConfigManager()
    quality_assurance = InspectorQualityAssurance(config_manager)
    defect_tracker = InspectorDefectTracker(config_manager)
    
    # Add sample data
    quality_assurance.add_quality_metric(
        QualityMetric.FUNCTIONALITY, 0.85,
        "Tool execution success rate", "test_tool_execution.py"
    )
    quality_assurance.add_quality_metric(
        QualityMetric.PERFORMANCE, 0.45,
        "Response time performance", "test_response_times.py"
    )
    
    defect_tracker.create_defect(
        title="Sample Performance Issue",
        description="Test defect for dashboard",
        severity=DefectSeverity.HIGH,
        priority=DefectPriority.HIGH,
        category=DefectCategory.PERFORMANCE,
        reported_by="dashboard_test"
    )
    
    # Initialize and start dashboard
    dashboard = InspectorQualityDashboard(config_manager, quality_assurance, defect_tracker)
    
    try:
        dashboard_url = dashboard.start_dashboard(port=8080, auto_open=True)
        print(f"Quality dashboard started at: {dashboard_url}")
        print("Press Ctrl+C to stop the dashboard...")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        dashboard.stop_dashboard()
        print("Dashboard stopped.")


if __name__ == "__main__":
    main() 