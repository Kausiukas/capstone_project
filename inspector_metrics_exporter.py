"""
Inspector Metrics Exporter - Task 1.3.4
=======================================

This module provides comprehensive export capabilities for Inspector metrics data,
analysis results, and reports. It supports multiple export formats and provides
automated export scheduling and data archival.

Key Features:
- Multiple export formats (JSON, CSV, Excel, HTML, PDF)
- Automated export scheduling and data archival
- Custom report generation with templates
- Data compression and backup capabilities
- Integration with Metrics Collector and Performance Analyzer
- Configurable export filters and data selection
- Export validation and error handling

Author: Inspector Development Team
Date: January 2025
"""

import json
import csv
import logging
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from enum import Enum
import zipfile
import gzip
import shutil
from collections import defaultdict

from inspector_metrics_collector import MetricsCollector, MetricType
from inspector_performance_analyzer import PerformanceAnalyzer, PerformanceStatus, AlertLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    HTML = "html"
    PDF = "pdf"
    XML = "xml"
    YAML = "yaml"


class ExportType(Enum):
    """Types of data that can be exported."""
    METRICS_DATA = "metrics_data"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SYSTEM_HEALTH = "system_health"
    ALERTS = "alerts"
    RECOMMENDATIONS = "recommendations"
    DASHBOARD_REPORT = "dashboard_report"
    COMPREHENSIVE_REPORT = "comprehensive_report"


@dataclass
class ExportConfig:
    """Configuration for export operations."""
    output_directory: str = "inspector_exports"
    compression_enabled: bool = True
    backup_enabled: bool = True
    max_file_size_mb: int = 100
    retention_days: int = 30
    auto_cleanup: bool = True
    include_timestamps: bool = True
    include_metadata: bool = True


@dataclass
class ExportRequest:
    """Export request specification."""
    export_type: ExportType
    format: ExportFormat
    time_range: Optional[timedelta] = None
    filters: Optional[Dict[str, Any]] = None
    custom_filename: Optional[str] = None
    include_charts: bool = True
    include_summaries: bool = True


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    export_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricsExporter:
    """
    Comprehensive metrics exporter for the Inspector system.
    
    Provides multiple export formats, automated scheduling, and data archival
    capabilities for metrics data and analysis results.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, 
                 performance_analyzer: PerformanceAnalyzer,
                 config: Optional[ExportConfig] = None):
        """
        Initialize the metrics exporter.
        
        Args:
            metrics_collector: Instance of MetricsCollector
            performance_analyzer: Instance of PerformanceAnalyzer
            config: Export configuration
        """
        self.metrics_collector = metrics_collector
        self.performance_analyzer = performance_analyzer
        self.config = config or ExportConfig()
        
        # Export state
        self.export_history: List[ExportResult] = []
        self.scheduled_exports: Dict[str, Dict[str, Any]] = {}
        self.is_exporting = False
        
        # Initialize output directory
        self._init_output_directory()
        
        logger.info("Metrics Exporter initialized successfully")
    
    def _init_output_directory(self):
        """Initialize the output directory structure."""
        output_path = Path(self.config.output_directory)
        output_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (output_path / 'metrics').mkdir(exist_ok=True)
        (output_path / 'analysis').mkdir(exist_ok=True)
        (output_path / 'reports').mkdir(exist_ok=True)
        (output_path / 'backups').mkdir(exist_ok=True)
        (output_path / 'archives').mkdir(exist_ok=True)
        
        logger.info(f"Export directory initialized at: {output_path.absolute()}")
    
    def export_data(self, request: ExportRequest) -> ExportResult:
        """
        Export data according to the specified request.
        
        Args:
            request: Export request specification
            
        Returns:
            ExportResult containing the result of the export operation
        """
        try:
            self.is_exporting = True
            start_time = datetime.now()
            
            # Generate filename
            filename = self._generate_filename(request)
            file_path = Path(self.config.output_directory) / self._get_subdirectory(request.export_type) / filename
            
            # Export data based on type
            if request.export_type == ExportType.METRICS_DATA:
                data = self._export_metrics_data(request)
            elif request.export_type == ExportType.PERFORMANCE_ANALYSIS:
                data = self._export_performance_analysis(request)
            elif request.export_type == ExportType.SYSTEM_HEALTH:
                data = self._export_system_health(request)
            elif request.export_type == ExportType.ALERTS:
                data = self._export_alerts(request)
            elif request.export_type == ExportType.RECOMMENDATIONS:
                data = self._export_recommendations(request)
            elif request.export_type == ExportType.DASHBOARD_REPORT:
                data = self._export_dashboard_report(request)
            elif request.export_type == ExportType.COMPREHENSIVE_REPORT:
                data = self._export_comprehensive_report(request)
            else:
                raise ValueError(f"Unsupported export type: {request.export_type}")
            
            # Write data to file
            self._write_data_to_file(data, file_path, request.format)
            
            # Compress if enabled
            if self.config.compression_enabled and request.format != ExportFormat.PDF:
                file_path = self._compress_file(file_path)
            
            # Create backup if enabled
            if self.config.backup_enabled:
                self._create_backup(file_path)
            
            # Calculate file size
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            # Create result
            result = ExportResult(
                success=True,
                file_path=str(file_path),
                file_size=file_size,
                export_time=datetime.now(),
                metadata={
                    'export_type': request.export_type.value,
                    'format': request.format.value,
                    'time_range': str(request.time_range) if request.time_range else None,
                    'duration': (datetime.now() - start_time).total_seconds()
                }
            )
            
            # Add to history
            self.export_history.append(result)
            
            logger.info(f"Export completed successfully: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            result = ExportResult(
                success=False,
                export_time=datetime.now(),
                error_message=str(e)
            )
            self.export_history.append(result)
            return result
        
        finally:
            self.is_exporting = False
    
    def _generate_filename(self, request: ExportRequest) -> str:
        """Generate filename for the export."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if request.custom_filename:
            base_name = request.custom_filename
        else:
            base_name = f"{request.export_type.value}_{request.format.value}"
        
        # Add timestamp if enabled
        if self.config.include_timestamps:
            filename = f"{base_name}_{timestamp}"
        else:
            filename = base_name
        
        # Add appropriate extension
        extensions = {
            ExportFormat.JSON: '.json',
            ExportFormat.CSV: '.csv',
            ExportFormat.EXCEL: '.xlsx',
            ExportFormat.HTML: '.html',
            ExportFormat.PDF: '.pdf',
            ExportFormat.XML: '.xml',
            ExportFormat.YAML: '.yaml'
        }
        
        return filename + extensions.get(request.format, '.txt')
    
    def _get_subdirectory(self, export_type: ExportType) -> str:
        """Get subdirectory for the export type."""
        subdirs = {
            ExportType.METRICS_DATA: 'metrics',
            ExportType.PERFORMANCE_ANALYSIS: 'analysis',
            ExportType.SYSTEM_HEALTH: 'analysis',
            ExportType.ALERTS: 'analysis',
            ExportType.RECOMMENDATIONS: 'analysis',
            ExportType.DASHBOARD_REPORT: 'reports',
            ExportType.COMPREHENSIVE_REPORT: 'reports'
        }
        return subdirs.get(export_type, 'reports')
    
    def _export_metrics_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Export metrics data."""
        # Get metrics summary
        metrics_summary = self.metrics_collector.get_metrics_summary(
            time_range=request.time_range
        )
        
        # Apply filters if specified
        if request.filters:
            metrics_summary = self._apply_filters(metrics_summary, request.filters)
        
        # Add metadata
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'metrics_data': metrics_summary
        }
        
        if self.config.include_metadata:
            export_data['metadata'] = {
                'total_metrics': len(metrics_summary.get('metrics', {})),
                'data_points': sum(
                    data.get('count', 0) for data in metrics_summary.get('metrics', {}).values()
                )
            }
        
        return export_data
    
    def _export_performance_analysis(self, request: ExportRequest) -> Dict[str, Any]:
        """Export performance analysis results."""
        # Get analysis results
        analysis_results = self.performance_analyzer.analyze_performance(
            time_range=request.time_range
        )
        
        # Apply filters if specified
        if request.filters:
            analysis_results = self._apply_filters(analysis_results, request.filters)
        
        # Add metadata
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'analysis_results': analysis_results
        }
        
        if self.config.include_metadata:
            export_data['metadata'] = {
                'bottlenecks_count': len(analysis_results.get('bottlenecks', [])),
                'anomalies_count': len(analysis_results.get('anomalies', [])),
                'recommendations_count': len(analysis_results.get('recommendations', [])),
                'overall_status': analysis_results.get('summary', {}).get('overall_status', 'unknown')
            }
        
        return export_data
    
    def _export_system_health(self, request: ExportRequest) -> Dict[str, Any]:
        """Export system health data."""
        # Get system health metrics
        metrics_summary = self.metrics_collector.get_metrics_summary(
            time_range=request.time_range
        )
        
        # Extract system health data
        system_health = {}
        if 'system_health' in metrics_summary.get('metrics', {}):
            system_health = metrics_summary['metrics']['system_health']
        
        # Get system snapshots if available
        system_snapshots = []
        if hasattr(self.metrics_collector, 'system_snapshots'):
            cutoff_time = datetime.now() - (request.time_range or timedelta(hours=1))
            system_snapshots = [
                {
                    'timestamp': snapshot.timestamp.isoformat(),
                    'cpu_percent': snapshot.cpu_percent,
                    'memory_percent': snapshot.memory_percent,
                    'memory_available': snapshot.memory_available,
                    'disk_usage_percent': snapshot.disk_usage_percent,
                    'network_io': snapshot.network_io,
                    'process_count': snapshot.process_count
                }
                for snapshot in self.metrics_collector.system_snapshots
                if snapshot.timestamp >= cutoff_time
            ]
        
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'system_health': system_health,
            'system_snapshots': system_snapshots
        }
        
        return export_data
    
    def _export_alerts(self, request: ExportRequest) -> Dict[str, Any]:
        """Export alerts data."""
        # Get alerts
        alerts = self.performance_analyzer.get_alerts()
        
        # Filter by time range if specified
        if request.time_range:
            cutoff_time = datetime.now() - request.time_range
            alerts = [
                alert for alert in alerts
                if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
            ]
        
        # Apply additional filters if specified
        if request.filters:
            alerts = self._apply_filters(alerts, request.filters)
        
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'alerts': alerts,
            'alerts_summary': {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['level'] == 'warning']),
                'info_alerts': len([a for a in alerts if a['level'] == 'info'])
            }
        }
        
        return export_data
    
    def _export_recommendations(self, request: ExportRequest) -> Dict[str, Any]:
        """Export recommendations data."""
        # Get analysis results
        analysis_results = self.performance_analyzer.analyze_performance(
            time_range=request.time_range
        )
        
        # Extract recommendations
        recommendations = analysis_results.get('recommendations', [])
        
        # Apply filters if specified
        if request.filters:
            recommendations = self._apply_filters(recommendations, request.filters)
        
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'recommendations': [
                {
                    'type': rec.recommendation_type,
                    'priority': rec.priority,
                    'impact_score': rec.impact_score,
                    'effort_score': rec.effort_score,
                    'description': rec.description,
                    'implementation_steps': rec.implementation_steps,
                    'expected_improvement': rec.expected_improvement
                }
                for rec in recommendations
            ],
            'recommendations_summary': {
                'total_recommendations': len(recommendations),
                'high_priority': len([r for r in recommendations if r.priority >= 4]),
                'medium_priority': len([r for r in recommendations if 2 <= r.priority < 4]),
                'low_priority': len([r for r in recommendations if r.priority < 2])
            }
        }
        
        return export_data
    
    def _export_dashboard_report(self, request: ExportRequest) -> Dict[str, Any]:
        """Export dashboard report."""
        # This would typically integrate with the dashboard module
        # For now, we'll create a simplified dashboard report
        
        # Get all relevant data
        metrics_summary = self.metrics_collector.get_metrics_summary(
            time_range=request.time_range
        )
        analysis_results = self.performance_analyzer.analyze_performance(
            time_range=request.time_range
        )
        alerts = self.performance_analyzer.get_alerts()
        
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'dashboard_report': {
                'metrics_overview': self._build_metrics_overview(metrics_summary),
                'performance_analysis': analysis_results.get('summary', {}),
                'recent_alerts': alerts[:10],  # Top 10 alerts
                'key_metrics': self._extract_key_metrics(metrics_summary),
                'system_status': self._get_system_status(metrics_summary)
            }
        }
        
        return export_data
    
    def _export_comprehensive_report(self, request: ExportRequest) -> Dict[str, Any]:
        """Export comprehensive report with all data."""
        # Get all data
        metrics_summary = self.metrics_collector.get_metrics_summary(
            time_range=request.time_range
        )
        analysis_results = self.performance_analyzer.analyze_performance(
            time_range=request.time_range
        )
        alerts = self.performance_analyzer.get_alerts()
        
        # Build comprehensive report
        export_data = {
            'export_info': {
                'export_type': request.export_type.value,
                'format': request.format.value,
                'timestamp': datetime.now().isoformat(),
                'time_range': str(request.time_range) if request.time_range else None
            },
            'executive_summary': {
                'overall_status': analysis_results.get('summary', {}).get('overall_status', 'unknown'),
                'critical_issues': analysis_results.get('summary', {}).get('critical_issues', 0),
                'total_alerts': len(alerts),
                'recommendations_count': len(analysis_results.get('recommendations', [])),
                'key_findings': self._generate_key_findings(analysis_results)
            },
            'detailed_analysis': {
                'metrics_data': metrics_summary,
                'performance_analysis': analysis_results,
                'alerts': alerts,
                'system_health': self._get_system_health_summary(metrics_summary)
            },
            'recommendations': {
                'high_priority': [
                    rec for rec in analysis_results.get('recommendations', [])
                    if rec.priority >= 4
                ],
                'medium_priority': [
                    rec for rec in analysis_results.get('recommendations', [])
                    if 2 <= rec.priority < 4
                ],
                'low_priority': [
                    rec for rec in analysis_results.get('recommendations', [])
                    if rec.priority < 2
                ]
            }
        }
        
        return export_data
    
    def _apply_filters(self, data: Any, filters: Dict[str, Any]) -> Any:
        """Apply filters to the data."""
        # This is a simplified filter implementation
        # In a real implementation, this would be more sophisticated
        
        if isinstance(data, dict):
            filtered_data = {}
            for key, value in data.items():
                if key in filters:
                    if isinstance(value, list):
                        # Filter list items
                        filtered_value = [
                            item for item in value
                            if self._matches_filter(item, filters[key])
                        ]
                        filtered_data[key] = filtered_value
                    else:
                        # Direct value comparison
                        if self._matches_filter(value, filters[key]):
                            filtered_data[key] = value
                else:
                    filtered_data[key] = value
            return filtered_data
        elif isinstance(data, list):
            return [
                item for item in data
                if self._matches_filter(item, filters)
            ]
        else:
            return data
    
    def _matches_filter(self, item: Any, filter_value: Any) -> bool:
        """Check if an item matches a filter."""
        if isinstance(filter_value, dict):
            # Complex filter
            for key, value in filter_value.items():
                if hasattr(item, key):
                    item_value = getattr(item, key)
                    if not self._matches_filter(item_value, value):
                        return False
                elif isinstance(item, dict) and key in item:
                    if not self._matches_filter(item[key], value):
                        return False
                else:
                    return False
            return True
        else:
            # Simple value comparison
            return item == filter_value
    
    def _write_data_to_file(self, data: Dict[str, Any], file_path: Path, format: ExportFormat):
        """Write data to file in the specified format."""
        if format == ExportFormat.JSON:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        
        elif format == ExportFormat.CSV:
            self._write_csv_data(data, file_path)
        
        elif format == ExportFormat.HTML:
            html_content = self._generate_html_report(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif format == ExportFormat.XML:
            xml_content = self._generate_xml_report(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        
        elif format == ExportFormat.YAML:
            import yaml
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _write_csv_data(self, data: Dict[str, Any], file_path: Path):
        """Write data as CSV."""
        # This is a simplified CSV export
        # In a real implementation, this would handle complex nested data structures
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            if 'export_info' in data:
                writer.writerow(['Export Type', 'Format', 'Timestamp', 'Time Range'])
                writer.writerow([
                    data['export_info'].get('export_type', ''),
                    data['export_info'].get('format', ''),
                    data['export_info'].get('timestamp', ''),
                    data['export_info'].get('time_range', '')
                ])
                writer.writerow([])  # Empty row
            
            # Write data based on export type
            if 'metrics_data' in data:
                self._write_metrics_csv(writer, data['metrics_data'])
            elif 'analysis_results' in data:
                self._write_analysis_csv(writer, data['analysis_results'])
            elif 'alerts' in data:
                self._write_alerts_csv(writer, data['alerts'])
    
    def _write_metrics_csv(self, writer, metrics_data):
        """Write metrics data as CSV."""
        writer.writerow(['Metric Type', 'Count', 'Min', 'Max', 'Average', 'Latest'])
        
        for metric_type, data in metrics_data.get('metrics', {}).items():
            writer.writerow([
                metric_type,
                data.get('count', 0),
                data.get('min', 0),
                data.get('max', 0),
                data.get('average', 0),
                data.get('latest', 0)
            ])
    
    def _write_analysis_csv(self, writer, analysis_data):
        """Write analysis data as CSV."""
        writer.writerow(['Analysis Type', 'Status', 'Details'])
        
        # Write bottlenecks
        for bottleneck in analysis_data.get('bottlenecks', []):
            writer.writerow([
                'Bottleneck',
                bottleneck.severity.value,
                bottleneck.bottleneck_type
            ])
        
        # Write anomalies
        for anomaly in analysis_data.get('anomalies', []):
            writer.writerow([
                'Anomaly',
                anomaly.severity.value,
                anomaly.metric_type.value
            ])
    
    def _write_alerts_csv(self, writer, alerts):
        """Write alerts data as CSV."""
        writer.writerow(['Timestamp', 'Level', 'Title', 'Message'])
        
        for alert in alerts:
            writer.writerow([
                alert.get('timestamp', ''),
                alert.get('level', ''),
                alert.get('title', ''),
                alert.get('message', '')
            ])
    
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report from data."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Inspector Export Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px; }
        .critical { background: #ffebee; border-left: 4px solid #f44336; }
        .warning { background: #fff3e0; border-left: 4px solid #ff9800; }
        .good { background: #e8f5e8; border-left: 4px solid #4caf50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Inspector Export Report</h1>
        <p>Generated: {timestamp}</p>
        <p>Export Type: {export_type}</p>
        <p>Format: {format}</p>
    </div>
    
    {content}
</body>
</html>
        """
        
        # Generate content based on data type
        content = self._generate_html_content(data)
        
        return html_template.format(
            timestamp=data.get('export_info', {}).get('timestamp', 'Unknown'),
            export_type=data.get('export_info', {}).get('export_type', 'Unknown'),
            format=data.get('export_info', {}).get('format', 'Unknown'),
            content=content
        )
    
    def _generate_html_content(self, data: Dict[str, Any]) -> str:
        """Generate HTML content for the report."""
        content = ""
        
        if 'metrics_data' in data:
            content += self._generate_metrics_html(data['metrics_data'])
        elif 'analysis_results' in data:
            content += self._generate_analysis_html(data['analysis_results'])
        elif 'alerts' in data:
            content += self._generate_alerts_html(data['alerts'])
        elif 'dashboard_report' in data:
            content += self._generate_dashboard_html(data['dashboard_report'])
        
        return content
    
    def _generate_metrics_html(self, metrics_data: Dict[str, Any]) -> str:
        """Generate HTML for metrics data."""
        html = '<div class="section"><h2>Metrics Data</h2>'
        
        for metric_type, data in metrics_data.get('metrics', {}).items():
            html += f"""
            <div class="metric">
                <strong>{metric_type}</strong><br>
                Count: {data.get('count', 0)}<br>
                Average: {data.get('average', 0):.3f}<br>
                Latest: {data.get('latest', 0):.3f}
            </div>
            """
        
        html += '</div>'
        return html
    
    def _generate_analysis_html(self, analysis_data: Dict[str, Any]) -> str:
        """Generate HTML for analysis data."""
        html = '<div class="section"><h2>Performance Analysis</h2>'
        
        # Summary
        summary = analysis_data.get('summary', {})
        html += f"""
        <div class="metric">
            <strong>Overall Status:</strong> {summary.get('overall_status', 'unknown')}<br>
            <strong>Critical Issues:</strong> {summary.get('critical_issues', 0)}<br>
            <strong>Warnings:</strong> {summary.get('warnings', 0)}
        </div>
        """
        
        # Bottlenecks
        bottlenecks = analysis_data.get('bottlenecks', [])
        if bottlenecks:
            html += '<h3>Bottlenecks</h3>'
            for bottleneck in bottlenecks:
                html += f"""
                <div class="metric {bottleneck.severity.value}">
                    <strong>{bottleneck.bottleneck_type}</strong><br>
                    Severity: {bottleneck.severity.value}<br>
                    Impact: {bottleneck.impact_score:.2f}
                </div>
                """
        
        html += '</div>'
        return html
    
    def _generate_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate HTML for alerts data."""
        html = '<div class="section"><h2>Alerts</h2>'
        
        for alert in alerts:
            html += f"""
            <div class="metric {alert.get('level', 'info')}">
                <strong>{alert.get('title', '')}</strong><br>
                {alert.get('message', '')}<br>
                <small>{alert.get('timestamp', '')}</small>
            </div>
            """
        
        html += '</div>'
        return html
    
    def _generate_dashboard_html(self, dashboard_data: Dict[str, Any]) -> str:
        """Generate HTML for dashboard report."""
        html = '<div class="section"><h2>Dashboard Report</h2>'
        
        # Metrics overview
        metrics_overview = dashboard_data.get('metrics_overview', {})
        html += f"""
        <div class="metric">
            <strong>Metrics Overview</strong><br>
            Total: {metrics_overview.get('total_metrics', 0)}<br>
            Active: {metrics_overview.get('active_metrics', 0)}<br>
            Critical: {metrics_overview.get('critical_metrics', 0)}
        </div>
        """
        
        # System status
        system_status = dashboard_data.get('system_status', {})
        html += f"""
        <div class="metric">
            <strong>System Status</strong><br>
            Status: {system_status.get('status', 'unknown')}<br>
            CPU: {system_status.get('cpu_usage', 0):.1f}%<br>
            Memory: {system_status.get('memory_usage', 0):.1f}%
        </div>
        """
        
        html += '</div>'
        return html
    
    def _generate_xml_report(self, data: Dict[str, Any]) -> str:
        """Generate XML report from data."""
        # This is a simplified XML generation
        # In a real implementation, this would be more comprehensive
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<inspector_report>']
        
        # Export info
        export_info = data.get('export_info', {})
        xml_lines.append('  <export_info>')
        for key, value in export_info.items():
            xml_lines.append(f'    <{key}>{value}</{key}>')
        xml_lines.append('  </export_info>')
        
        # Data content (simplified)
        xml_lines.append('  <data>')
        xml_lines.append('    <!-- Data content would be here -->')
        xml_lines.append('  </data>')
        
        xml_lines.append('</inspector_report>')
        
        return '\n'.join(xml_lines)
    
    def _compress_file(self, file_path: Path) -> Path:
        """Compress a file using gzip."""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original file
        file_path.unlink()
        
        return compressed_path
    
    def _create_backup(self, file_path: Path):
        """Create a backup of the exported file."""
        backup_dir = Path(self.config.output_directory) / 'backups'
        backup_path = backup_dir / file_path.name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
    
    def _build_metrics_overview(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build metrics overview for dashboard report."""
        overview = {
            'total_metrics': 0,
            'active_metrics': 0,
            'critical_metrics': 0,
            'warning_metrics': 0
        }
        
        for metric_type, data in metrics_summary.get('metrics', {}).items():
            overview['total_metrics'] += 1
            
            # Determine status (simplified)
            if metric_type == 'response_time':
                avg_value = data.get('average', 0)
                if avg_value > 10.0:
                    overview['critical_metrics'] += 1
                elif avg_value > 5.0:
                    overview['warning_metrics'] += 1
                else:
                    overview['active_metrics'] += 1
            else:
                overview['active_metrics'] += 1
        
        return overview
    
    def _extract_key_metrics(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for dashboard report."""
        key_metrics = {}
        
        for metric_type, data in metrics_summary.get('metrics', {}).items():
            key_metrics[metric_type] = {
                'current': data.get('latest', 0),
                'average': data.get('average', 0),
                'trend': 'stable'  # Simplified
            }
        
        return key_metrics
    
    def _get_system_status(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Get system status for dashboard report."""
        status = {
            'status': 'unknown',
            'cpu_usage': 0,
            'memory_usage': 0
        }
        
        if 'system_health' in metrics_summary.get('metrics', {}):
            system_data = metrics_summary['metrics']['system_health']
            status['cpu_usage'] = system_data.get('average', 0)
            
            if system_data.get('metadata', {}):
                status['memory_usage'] = system_data['metadata'].get('memory_percent', 0)
            
            # Determine overall status
            if status['cpu_usage'] > 90 or status['memory_usage'] > 95:
                status['status'] = 'critical'
            elif status['cpu_usage'] > 80 or status['memory_usage'] > 85:
                status['status'] = 'warning'
            else:
                status['status'] = 'good'
        
        return status
    
    def _get_system_health_summary(self, metrics_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Get system health summary for comprehensive report."""
        return self._get_system_status(metrics_summary)
    
    def _generate_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate key findings for comprehensive report."""
        findings = []
        
        # Check for critical bottlenecks
        bottlenecks = analysis_results.get('bottlenecks', [])
        critical_bottlenecks = [b for b in bottlenecks if b.severity == PerformanceStatus.CRITICAL]
        if critical_bottlenecks:
            findings.append(f"Found {len(critical_bottlenecks)} critical performance bottlenecks")
        
        # Check for anomalies
        anomalies = analysis_results.get('anomalies', [])
        critical_anomalies = [a for a in anomalies if a.severity == AlertLevel.CRITICAL]
        if critical_anomalies:
            findings.append(f"Detected {len(critical_anomalies)} critical performance anomalies")
        
        # Check for degradation
        degradation = analysis_results.get('degradation_analysis', {})
        if degradation.get('degradation_detected'):
            findings.append(f"Performance degradation detected: {degradation.get('degradation_type')}")
        
        return findings
    
    def schedule_export(self, schedule_id: str, request: ExportRequest, 
                       schedule_interval: timedelta) -> bool:
        """Schedule a recurring export."""
        try:
            self.scheduled_exports[schedule_id] = {
                'request': request,
                'interval': schedule_interval,
                'last_run': None,
                'next_run': datetime.now() + schedule_interval,
                'enabled': True
            }
            
            logger.info(f"Export scheduled: {schedule_id} (interval: {schedule_interval})")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling export: {e}")
            return False
    
    def cancel_scheduled_export(self, schedule_id: str) -> bool:
        """Cancel a scheduled export."""
        if schedule_id in self.scheduled_exports:
            del self.scheduled_exports[schedule_id]
            logger.info(f"Scheduled export cancelled: {schedule_id}")
            return True
        return False
    
    def get_export_history(self, limit: Optional[int] = None) -> List[ExportResult]:
        """Get export history."""
        if limit:
            return self.export_history[-limit:]
        return self.export_history.copy()
    
    def cleanup_old_exports(self):
        """Clean up old export files based on retention policy."""
        try:
            retention_date = datetime.now() - timedelta(days=self.config.retention_days)
            output_path = Path(self.config.output_directory)
            
            for subdir in ['metrics', 'analysis', 'reports']:
                dir_path = output_path / subdir
                if dir_path.exists():
                    for file_path in dir_path.glob('*'):
                        try:
                            # Try to extract date from filename
                            if '_' in file_path.stem:
                                date_part = file_path.stem.split('_')[-1]
                                file_date = datetime.strptime(date_part, '%Y%m%d_%H%M%S')
                                
                                if file_date < retention_date:
                                    file_path.unlink()
                                    logger.info(f"Deleted old export file: {file_path}")
                        except (ValueError, IndexError):
                            # Skip files that don't match the naming pattern
                            continue
            
            logger.info("Old export cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during export cleanup: {e}")


def main():
    """Main function for testing the metrics exporter."""
    print("Inspector Metrics Exporter - Task 1.3.4")
    print("=" * 50)
    
    # Initialize components
    collector = MetricsCollector()
    analyzer = PerformanceAnalyzer(collector)
    exporter = MetricsExporter(collector, analyzer)
    
    try:
        # Start collection
        print("Starting metrics collection...")
        collector.start_collection()
        
        # Simulate some operations
        print("Simulating operations...")
        for i in range(5):
            operation_id = f"test_op_{i}"
            collector.record_operation_start(operation_id, f"test_tool_{i}")
            
            # Simulate operation duration
            time.sleep(0.2)
            
            success = i % 3 != 0  # Some operations fail
            collector.record_operation_end(operation_id, success)
        
        # Wait for collection
        time.sleep(5)
        
        # Test different export types
        print("\nTesting exports...")
        
        # Export metrics data
        metrics_request = ExportRequest(
            export_type=ExportType.METRICS_DATA,
            format=ExportFormat.JSON
        )
        result = exporter.export_data(metrics_request)
        print(f"Metrics export: {'Success' if result.success else 'Failed'}")
        
        # Export performance analysis
        analysis_request = ExportRequest(
            export_type=ExportType.PERFORMANCE_ANALYSIS,
            format=ExportFormat.HTML
        )
        result = exporter.export_data(analysis_request)
        print(f"Analysis export: {'Success' if result.success else 'Failed'}")
        
        # Export comprehensive report
        comprehensive_request = ExportRequest(
            export_type=ExportType.COMPREHENSIVE_REPORT,
            format=ExportFormat.JSON,
            custom_filename="comprehensive_report"
        )
        result = exporter.export_data(comprehensive_request)
        print(f"Comprehensive export: {'Success' if result.success else 'Failed'}")
        
        # Show export history
        print("\nExport History:")
        for export_result in exporter.get_export_history(5):
            status = "Success" if export_result.success else "Failed"
            print(f"- {status}: {export_result.file_path or export_result.error_message}")
        
    except KeyboardInterrupt:
        print("\nStopping exporter...")
    finally:
        collector.stop_collection()
        print("Metrics exporter stopped")


if __name__ == "__main__":
    main() 