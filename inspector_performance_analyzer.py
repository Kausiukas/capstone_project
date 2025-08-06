"""
Inspector Performance Analyzer - Task 1.3.2
===========================================

This module provides comprehensive performance analysis capabilities for the Inspector system.
It analyzes metrics data collected by the Metrics Collector to identify performance trends,
bottlenecks, and optimization opportunities.

Key Features:
- Performance trend analysis and pattern recognition
- Bottleneck identification and root cause analysis
- Performance degradation detection and alerting
- Optimization recommendations and capacity planning
- Statistical analysis and anomaly detection
- Integration with Metrics Collector data
- Configurable analysis thresholds and alerting

Author: Inspector Development Team
Date: January 2025
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from enum import Enum
from pathlib import Path
import numpy as np
from scipy import stats

from inspector_metrics_collector import MetricsCollector, MetricType, MetricData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of performance analysis that can be performed."""
    TREND_ANALYSIS = "trend_analysis"
    BOTTLENECK_DETECTION = "bottleneck_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    CAPACITY_PLANNING = "capacity_planning"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    OPTIMIZATION_RECOMMENDATIONS = "optimization_recommendations"


class PerformanceStatus(Enum):
    """Status of performance analysis results."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class AlertLevel(Enum):
    """Levels of performance alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceTrend:
    """Data structure for performance trend analysis."""
    metric_type: MetricType
    trend_direction: str  # "improving", "stable", "degrading"
    trend_strength: float  # correlation coefficient
    slope: float  # rate of change
    confidence: float  # statistical confidence
    data_points: int
    time_range: timedelta


@dataclass
class BottleneckAnalysis:
    """Data structure for bottleneck analysis results."""
    bottleneck_type: str
    severity: PerformanceStatus
    impact_score: float  # 0-1 scale
    affected_metrics: List[MetricType]
    root_cause: str
    recommendations: List[str]
    evidence: Dict[str, Any]


@dataclass
class AnomalyDetection:
    """Data structure for anomaly detection results."""
    metric_type: MetricType
    anomaly_type: str  # "spike", "drop", "trend_break"
    severity: AlertLevel
    timestamp: datetime
    expected_value: float
    actual_value: float
    deviation: float
    confidence: float


@dataclass
class OptimizationRecommendation:
    """Data structure for optimization recommendations."""
    recommendation_type: str
    priority: int  # 1-5, higher is more important
    impact_score: float  # 0-1 scale
    effort_score: float  # 0-1 scale
    description: str
    implementation_steps: List[str]
    expected_improvement: Dict[str, float]


class PerformanceAnalyzer:
    """
    Main performance analyzer for the Inspector system.
    
    Analyzes metrics data to identify performance trends, bottlenecks, anomalies,
    and provides optimization recommendations.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the performance analyzer.
        
        Args:
            metrics_collector: Instance of MetricsCollector to analyze
            config: Configuration dictionary for the analyzer
        """
        self.metrics_collector = metrics_collector
        self.config = config or self._get_default_config()
        
        # Analysis state
        self.analysis_history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.recommendations: List[OptimizationRecommendation] = []
        
        # Performance thresholds
        self.thresholds = self.config['performance_thresholds']
        
        logger.info("Performance Analyzer initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the performance analyzer."""
        return {
            'analysis_interval': 60.0,  # seconds
            'trend_analysis_window': timedelta(hours=1),
            'anomaly_detection_sensitivity': 2.0,  # standard deviations
            'bottleneck_detection_threshold': 0.8,  # impact score threshold
            'performance_thresholds': {
                'response_time': {
                    'excellent': 0.1,  # seconds
                    'good': 0.5,
                    'acceptable': 1.0,
                    'degraded': 5.0,
                    'critical': 10.0
                },
                'success_rate': {
                    'excellent': 0.99,
                    'good': 0.95,
                    'acceptable': 0.90,
                    'degraded': 0.80,
                    'critical': 0.70
                },
                'cpu_usage': {
                    'excellent': 20.0,  # percent
                    'good': 40.0,
                    'acceptable': 60.0,
                    'degraded': 80.0,
                    'critical': 90.0
                },
                'memory_usage': {
                    'excellent': 30.0,  # percent
                    'good': 50.0,
                    'acceptable': 70.0,
                    'degraded': 85.0,
                    'critical': 95.0
                }
            },
            'alerting': {
                'enable_alerts': True,
                'alert_cooldown': 300,  # seconds
                'max_alerts_per_hour': 10
            }
        }
    
    def analyze_performance(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Perform comprehensive performance analysis.
        
        Args:
            time_range: Time range for analysis (default: last hour)
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            time_range = time_range or self.config['trend_analysis_window']
            
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'time_range': str(time_range),
                'trends': self._analyze_trends(time_range),
                'bottlenecks': self._detect_bottlenecks(time_range),
                'anomalies': self._detect_anomalies(time_range),
                'capacity_analysis': self._analyze_capacity(time_range),
                'degradation_analysis': self._detect_degradation(time_range),
                'recommendations': self._generate_recommendations(time_range),
                'summary': {}
            }
            
            # Generate summary
            analysis_results['summary'] = self._generate_analysis_summary(analysis_results)
            
            # Store analysis history
            self.analysis_history.append(analysis_results)
            
            # Check for alerts
            if self.config['alerting']['enable_alerts']:
                self._check_alerts(analysis_results)
            
            logger.info("Performance analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error during performance analysis: {e}")
            return {'error': str(e)}
    
    def _analyze_trends(self, time_range: timedelta) -> List[PerformanceTrend]:
        """Analyze performance trends over the specified time range."""
        trends = []
        
        try:
            # Get metrics summary for the time range
            summary = self.metrics_collector.get_metrics_summary(time_range=time_range)
            
            for metric_type_str, metric_data in summary.get('metrics', {}).items():
                try:
                    metric_type = MetricType(metric_type_str)
                    
                    # Get detailed metrics for trend analysis
                    cutoff_time = datetime.now() - time_range
                    recent_metrics = [
                        m for m in self.metrics_collector.metrics_history[metric_type]
                        if m.timestamp >= cutoff_time
                    ]
                    
                    if len(recent_metrics) < 3:  # Need at least 3 data points
                        continue
                    
                    # Extract values and timestamps
                    values = [m.value for m in recent_metrics]
                    timestamps = [m.timestamp for m in recent_metrics]
                    
                    # Convert timestamps to numeric values for analysis
                    time_numeric = [(t - timestamps[0]).total_seconds() for t in timestamps]
                    
                    # Calculate trend using linear regression
                    if len(time_numeric) > 1:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, values)
                        
                        # Determine trend direction
                        if abs(slope) < 0.001:  # Very small slope
                            trend_direction = "stable"
                        elif slope > 0:
                            trend_direction = "degrading" if metric_type in [
                                MetricType.RESPONSE_TIME, MetricType.ERROR_RATE, 
                                MetricType.CPU_USAGE, MetricType.MEMORY_USAGE
                            ] else "improving"
                        else:
                            trend_direction = "improving" if metric_type in [
                                MetricType.RESPONSE_TIME, MetricType.ERROR_RATE,
                                MetricType.CPU_USAGE, MetricType.MEMORY_USAGE
                            ] else "degrading"
                        
                        trend = PerformanceTrend(
                            metric_type=metric_type,
                            trend_direction=trend_direction,
                            trend_strength=abs(r_value),
                            slope=slope,
                            confidence=1 - p_value if p_value else 0,
                            data_points=len(recent_metrics),
                            time_range=time_range
                        )
                        
                        trends.append(trend)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error analyzing trend for {metric_type_str}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
        
        return trends
    
    def _detect_bottlenecks(self, time_range: timedelta) -> List[BottleneckAnalysis]:
        """Detect performance bottlenecks in the system."""
        bottlenecks = []
        
        try:
            # Get current metrics
            summary = self.metrics_collector.get_metrics_summary(time_range=time_range)
            
            # Check for response time bottlenecks
            if 'response_time' in summary.get('metrics', {}):
                response_data = summary['metrics']['response_time']
                avg_response_time = response_data.get('average', 0)
                
                if avg_response_time > self.thresholds['response_time']['degraded']:
                    bottleneck = BottleneckAnalysis(
                        bottleneck_type="High Response Time",
                        severity=PerformanceStatus.CRITICAL if avg_response_time > self.thresholds['response_time']['critical'] else PerformanceStatus.DEGRADED,
                        impact_score=min(1.0, avg_response_time / self.thresholds['response_time']['critical']),
                        affected_metrics=[MetricType.RESPONSE_TIME, MetricType.THROUGHPUT],
                        root_cause="MCP server performance issues or network latency",
                        recommendations=[
                            "Optimize MCP server configuration",
                            "Increase server resources",
                            "Implement caching mechanisms",
                            "Review network configuration"
                        ],
                        evidence={
                            'average_response_time': avg_response_time,
                            'threshold': self.thresholds['response_time']['degraded'],
                            'max_response_time': response_data.get('max', 0)
                        }
                    )
                    bottlenecks.append(bottleneck)
            
            # Check for success rate bottlenecks
            if 'success_rate' in summary.get('metrics', {}):
                success_data = summary['metrics']['success_rate']
                avg_success_rate = success_data.get('average', 1.0)
                
                if avg_success_rate < self.thresholds['success_rate']['degraded']:
                    bottleneck = BottleneckAnalysis(
                        bottleneck_type="Low Success Rate",
                        severity=PerformanceStatus.CRITICAL if avg_success_rate < self.thresholds['success_rate']['critical'] else PerformanceStatus.DEGRADED,
                        impact_score=1.0 - avg_success_rate,
                        affected_metrics=[MetricType.SUCCESS_RATE, MetricType.ERROR_RATE],
                        root_cause="High error rates or system instability",
                        recommendations=[
                            "Investigate error patterns",
                            "Improve error handling",
                            "Fix system stability issues",
                            "Implement retry mechanisms"
                        ],
                        evidence={
                            'average_success_rate': avg_success_rate,
                            'threshold': self.thresholds['success_rate']['degraded'],
                            'min_success_rate': success_data.get('min', 1.0)
                        }
                    )
                    bottlenecks.append(bottleneck)
            
            # Check for resource bottlenecks
            if 'system_health' in summary.get('metrics', {}):
                system_data = summary['metrics']['system_health']
                avg_cpu = system_data.get('average', 0)
                
                if avg_cpu > self.thresholds['cpu_usage']['degraded']:
                    bottleneck = BottleneckAnalysis(
                        bottleneck_type="High CPU Usage",
                        severity=PerformanceStatus.CRITICAL if avg_cpu > self.thresholds['cpu_usage']['critical'] else PerformanceStatus.DEGRADED,
                        impact_score=min(1.0, avg_cpu / 100.0),
                        affected_metrics=[MetricType.SYSTEM_HEALTH, MetricType.RESPONSE_TIME],
                        root_cause="High CPU utilization limiting system performance",
                        recommendations=[
                            "Optimize CPU-intensive operations",
                            "Scale system resources",
                            "Implement load balancing",
                            "Review process priorities"
                        ],
                        evidence={
                            'average_cpu_usage': avg_cpu,
                            'threshold': self.thresholds['cpu_usage']['degraded'],
                            'max_cpu_usage': system_data.get('max', 0)
                        }
                    )
                    bottlenecks.append(bottleneck)
        
        except Exception as e:
            logger.error(f"Error in bottleneck detection: {e}")
        
        return bottlenecks
    
    def _detect_anomalies(self, time_range: timedelta) -> List[AnomalyDetection]:
        """Detect performance anomalies using statistical analysis."""
        anomalies = []
        
        try:
            sensitivity = self.config['anomaly_detection_sensitivity']
            
            for metric_type in MetricType:
                # Get recent metrics for this type
                cutoff_time = datetime.now() - time_range
                recent_metrics = [
                    m for m in self.metrics_collector.metrics_history[metric_type]
                    if m.timestamp >= cutoff_time
                ]
                
                if len(recent_metrics) < 5:  # Need sufficient data points
                    continue
                
                values = [m.value for m in recent_metrics]
                mean_value = statistics.mean(values)
                std_value = statistics.stdev(values) if len(values) > 1 else 0
                
                if std_value == 0:
                    continue
                
                # Check each value for anomalies
                for metric in recent_metrics[-10:]:  # Check last 10 values
                    z_score = abs(metric.value - mean_value) / std_value
                    
                    if z_score > sensitivity:
                        # Determine anomaly type
                        if metric.value > mean_value + 2 * std_value:
                            anomaly_type = "spike"
                        elif metric.value < mean_value - 2 * std_value:
                            anomaly_type = "drop"
                        else:
                            anomaly_type = "deviation"
                        
                        # Determine severity
                        if z_score > sensitivity * 2:
                            severity = AlertLevel.CRITICAL
                        elif z_score > sensitivity * 1.5:
                            severity = AlertLevel.WARNING
                        else:
                            severity = AlertLevel.INFO
                        
                        anomaly = AnomalyDetection(
                            metric_type=metric_type,
                            anomaly_type=anomaly_type,
                            severity=severity,
                            timestamp=metric.timestamp,
                            expected_value=mean_value,
                            actual_value=metric.value,
                            deviation=z_score,
                            confidence=min(1.0, z_score / (sensitivity * 3))
                        )
                        
                        anomalies.append(anomaly)
        
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
        
        return anomalies
    
    def _analyze_capacity(self, time_range: timedelta) -> Dict[str, Any]:
        """Analyze system capacity and resource utilization."""
        capacity_analysis = {
            'current_utilization': {},
            'capacity_limits': {},
            'scaling_recommendations': [],
            'resource_efficiency': {}
        }
        
        try:
            # Get system health metrics
            summary = self.metrics_collector.get_metrics_summary(time_range=time_range)
            
            if 'system_health' in summary.get('metrics', {}):
                system_data = summary['metrics']['system_health']
                
                # CPU utilization
                avg_cpu = system_data.get('average', 0)
                capacity_analysis['current_utilization']['cpu'] = avg_cpu
                capacity_analysis['capacity_limits']['cpu'] = 100.0
                
                if avg_cpu > 80:
                    capacity_analysis['scaling_recommendations'].append({
                        'resource': 'CPU',
                        'action': 'scale_up',
                        'reason': f'High CPU utilization: {avg_cpu:.1f}%',
                        'priority': 'high' if avg_cpu > 90 else 'medium'
                    })
                
                # Memory utilization (approximate from system health)
                # Note: This is a simplified analysis - real memory data would come from system snapshots
                capacity_analysis['current_utilization']['memory'] = 'unknown'
                capacity_analysis['capacity_limits']['memory'] = 'unknown'
                
                # Throughput analysis
                if 'throughput' in summary.get('metrics', {}):
                    throughput_data = summary['metrics']['throughput']
                    avg_throughput = throughput_data.get('average', 0)
                    
                    capacity_analysis['current_utilization']['throughput'] = avg_throughput
                    capacity_analysis['capacity_limits']['throughput'] = 'dynamic'
                    
                    # Estimate capacity based on response times
                    if 'response_time' in summary.get('metrics', {}):
                        response_data = summary['metrics']['response_time']
                        avg_response_time = response_data.get('average', 1.0)
                        
                        # Theoretical max throughput (simplified)
                        theoretical_max = 1.0 / avg_response_time if avg_response_time > 0 else 0
                        efficiency = avg_throughput / theoretical_max if theoretical_max > 0 else 0
                        
                        capacity_analysis['resource_efficiency']['throughput'] = efficiency
                        
                        if efficiency < 0.5:
                            capacity_analysis['scaling_recommendations'].append({
                                'resource': 'Throughput',
                                'action': 'optimize',
                                'reason': f'Low throughput efficiency: {efficiency:.2f}',
                                'priority': 'medium'
                            })
        
        except Exception as e:
            logger.error(f"Error in capacity analysis: {e}")
        
        return capacity_analysis
    
    def _detect_degradation(self, time_range: timedelta) -> Dict[str, Any]:
        """Detect performance degradation patterns."""
        degradation_analysis = {
            'degradation_detected': False,
            'degradation_type': None,
            'severity': None,
            'affected_metrics': [],
            'time_period': None,
            'trend_analysis': {}
        }
        
        try:
            # Analyze trends for degradation patterns
            trends = self._analyze_trends(time_range)
            
            degrading_metrics = []
            for trend in trends:
                if trend.trend_direction == "degrading" and trend.trend_strength > 0.7:
                    degrading_metrics.append({
                        'metric': trend.metric_type.value,
                        'slope': trend.slope,
                        'strength': trend.trend_strength
                    })
            
            if degrading_metrics:
                degradation_analysis['degradation_detected'] = True
                degradation_analysis['affected_metrics'] = degrading_metrics
                
                # Determine degradation type and severity
                response_time_degrading = any(
                    m['metric'] == 'response_time' for m in degrading_metrics
                )
                success_rate_degrading = any(
                    m['metric'] == 'success_rate' for m in degrading_metrics
                )
                
                if response_time_degrading and success_rate_degrading:
                    degradation_analysis['degradation_type'] = 'system_wide'
                    degradation_analysis['severity'] = 'critical'
                elif response_time_degrading:
                    degradation_analysis['degradation_type'] = 'performance'
                    degradation_analysis['severity'] = 'high'
                elif success_rate_degrading:
                    degradation_analysis['degradation_type'] = 'reliability'
                    degradation_analysis['severity'] = 'medium'
                else:
                    degradation_analysis['degradation_type'] = 'resource'
                    degradation_analysis['severity'] = 'low'
                
                degradation_analysis['time_period'] = str(time_range)
                degradation_analysis['trend_analysis'] = {
                    trend.metric_type.value: {
                        'direction': trend.trend_direction,
                        'strength': trend.trend_strength,
                        'slope': trend.slope
                    }
                    for trend in trends
                }
        
        except Exception as e:
            logger.error(f"Error in degradation detection: {e}")
        
        return degradation_analysis
    
    def _generate_recommendations(self, time_range: timedelta) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        try:
            # Get analysis results
            bottlenecks = self._detect_bottlenecks(time_range)
            degradation = self._detect_degradation(time_range)
            capacity = self._analyze_capacity(time_range)
            
            # High priority recommendations based on bottlenecks
            for bottleneck in bottlenecks:
                if bottleneck.severity in [PerformanceStatus.CRITICAL, PerformanceStatus.DEGRADED]:
                    recommendation = OptimizationRecommendation(
                        recommendation_type=f"Fix {bottleneck.bottleneck_type}",
                        priority=5 if bottleneck.severity == PerformanceStatus.CRITICAL else 4,
                        impact_score=bottleneck.impact_score,
                        effort_score=0.7,  # Estimated effort
                        description=f"Address {bottleneck.bottleneck_type.lower()} to improve system performance",
                        implementation_steps=bottleneck.recommendations,
                        expected_improvement={
                            'response_time': -0.3 if 'response_time' in [m.value for m in bottleneck.affected_metrics] else 0,
                            'success_rate': 0.1 if 'success_rate' in [m.value for m in bottleneck.affected_metrics] else 0,
                            'throughput': 0.2
                        }
                    )
                    recommendations.append(recommendation)
            
            # Medium priority recommendations based on degradation
            if degradation['degradation_detected']:
                recommendation = OptimizationRecommendation(
                    recommendation_type="Address Performance Degradation",
                    priority=3,
                    impact_score=0.6,
                    effort_score=0.5,
                    description=f"System shows {degradation['degradation_type']} degradation pattern",
                    implementation_steps=[
                        "Investigate root cause of degradation",
                        "Implement monitoring for affected metrics",
                        "Apply targeted optimizations",
                        "Monitor improvement"
                    ],
                    expected_improvement={
                        'response_time': -0.2,
                        'success_rate': 0.05,
                        'stability': 0.3
                    }
                )
                recommendations.append(recommendation)
            
            # Lower priority recommendations based on capacity
            for scaling_rec in capacity.get('scaling_recommendations', []):
                recommendation = OptimizationRecommendation(
                    recommendation_type=f"Scale {scaling_rec['resource']}",
                    priority=2 if scaling_rec['priority'] == 'high' else 1,
                    impact_score=0.4,
                    effort_score=0.8,
                    description=f"Consider scaling {scaling_rec['resource']}: {scaling_rec['reason']}",
                    implementation_steps=[
                        f"Evaluate {scaling_rec['resource']} requirements",
                        "Plan scaling strategy",
                        "Implement scaling solution",
                        "Monitor performance impact"
                    ],
                    expected_improvement={
                        'capacity': 0.3,
                        'response_time': -0.1,
                        'throughput': 0.2
                    }
                )
                recommendations.append(recommendation)
            
            # Sort recommendations by priority
            recommendations.sort(key=lambda r: r.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _generate_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        summary = {
            'overall_status': 'good',
            'critical_issues': 0,
            'warnings': 0,
            'recommendations_count': 0,
            'key_metrics': {}
        }
        
        try:
            # Count critical issues and warnings
            for bottleneck in analysis_results.get('bottlenecks', []):
                if bottleneck.severity == PerformanceStatus.CRITICAL:
                    summary['critical_issues'] += 1
                elif bottleneck.severity == PerformanceStatus.DEGRADED:
                    summary['warnings'] += 1
            
            for anomaly in analysis_results.get('anomalies', []):
                if anomaly.severity == AlertLevel.CRITICAL:
                    summary['critical_issues'] += 1
                elif anomaly.severity == AlertLevel.WARNING:
                    summary['warnings'] += 1
            
            summary['recommendations_count'] = len(analysis_results.get('recommendations', []))
            
            # Determine overall status
            if summary['critical_issues'] > 0:
                summary['overall_status'] = 'critical'
            elif summary['warnings'] > 2:
                summary['overall_status'] = 'degraded'
            elif summary['warnings'] > 0:
                summary['overall_status'] = 'warning'
            else:
                summary['overall_status'] = 'good'
            
            # Extract key metrics from trends
            for trend in analysis_results.get('trends', []):
                summary['key_metrics'][trend.metric_type.value] = {
                    'direction': trend.trend_direction,
                    'strength': trend.trend_strength
                }
        
        except Exception as e:
            logger.error(f"Error generating analysis summary: {e}")
        
        return summary
    
    def _check_alerts(self, analysis_results: Dict[str, Any]):
        """Check for conditions that should trigger alerts."""
        try:
            # Check for critical bottlenecks
            for bottleneck in analysis_results.get('bottlenecks', []):
                if bottleneck.severity == PerformanceStatus.CRITICAL:
                    self._create_alert(
                        level=AlertLevel.CRITICAL,
                        title=f"Critical Bottleneck: {bottleneck.bottleneck_type}",
                        message=f"System performance is critically impacted: {bottleneck.root_cause}",
                        data=bottleneck.evidence
                    )
            
            # Check for critical anomalies
            for anomaly in analysis_results.get('anomalies', []):
                if anomaly.severity == AlertLevel.CRITICAL:
                    self._create_alert(
                        level=AlertLevel.CRITICAL,
                        title=f"Critical Anomaly: {anomaly.metric_type.value}",
                        message=f"Critical anomaly detected: {anomaly.actual_value:.3f} vs expected {anomaly.expected_value:.3f}",
                        data={
                            'metric_type': anomaly.metric_type.value,
                            'deviation': anomaly.deviation,
                            'timestamp': anomaly.timestamp.isoformat()
                        }
                    )
            
            # Check for performance degradation
            degradation = analysis_results.get('degradation_analysis', {})
            if degradation.get('degradation_detected') and degradation.get('severity') == 'critical':
                self._create_alert(
                    level=AlertLevel.WARNING,
                    title="Performance Degradation Detected",
                    message=f"System performance is degrading: {degradation.get('degradation_type')}",
                    data=degradation
                )
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _create_alert(self, level: AlertLevel, title: str, message: str, data: Dict[str, Any]):
        """Create a new alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level.value,
            'title': title,
            'message': message,
            'data': data
        }
        
        self.alerts.append(alert)
        logger.warning(f"Alert created: {title} - {message}")
    
    def get_alerts(self, level: Optional[AlertLevel] = None, 
                  time_range: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Get alerts filtered by level and time range."""
        filtered_alerts = self.alerts
        
        if level:
            filtered_alerts = [a for a in filtered_alerts if a['level'] == level.value]
        
        if time_range:
            cutoff_time = datetime.now() - time_range
            filtered_alerts = [
                a for a in filtered_alerts 
                if datetime.fromisoformat(a['timestamp']) >= cutoff_time
            ]
        
        return filtered_alerts
    
    def export_analysis_report(self, format: str = 'json', 
                             time_range: Optional[timedelta] = None) -> str:
        """Export analysis results in the specified format."""
        try:
            analysis_results = self.analyze_performance(time_range)
            
            if format.lower() == 'json':
                return json.dumps(analysis_results, indent=2, default=str)
            elif format.lower() == 'csv':
                return self._convert_analysis_to_csv(analysis_results)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analysis report: {e}")
            return f"Error: {e}"
    
    def _convert_analysis_to_csv(self, analysis_results: Dict[str, Any]) -> str:
        """Convert analysis results to CSV format."""
        csv_lines = ['Analysis Type,Status,Details']
        
        # Add bottlenecks
        for bottleneck in analysis_results.get('bottlenecks', []):
            csv_lines.append(
                f"Bottleneck,{bottleneck.severity.value},{bottleneck.bottleneck_type}"
            )
        
        # Add anomalies
        for anomaly in analysis_results.get('anomalies', []):
            csv_lines.append(
                f"Anomaly,{anomaly.severity.value},{anomaly.metric_type.value}"
            )
        
        # Add recommendations
        for rec in analysis_results.get('recommendations', []):
            csv_lines.append(
                f"Recommendation,Priority {rec.priority},{rec.recommendation_type}"
            )
        
        return '\n'.join(csv_lines)


def main():
    """Main function for testing the performance analyzer."""
    print("Inspector Performance Analyzer - Task 1.3.2")
    print("=" * 50)
    
    # Initialize metrics collector and analyzer
    collector = MetricsCollector()
    analyzer = PerformanceAnalyzer(collector)
    
    try:
        # Start collection
        print("Starting metrics collection...")
        collector.start_collection()
        
        # Simulate some operations
        print("Simulating operations...")
        for i in range(10):
            operation_id = f"test_op_{i}"
            collector.record_operation_start(operation_id, f"test_tool_{i}")
            
            # Simulate operation duration
            import time
            time.sleep(0.2)
            
            success = i % 4 != 0  # Some operations fail
            collector.record_operation_end(operation_id, success)
        
        # Wait for collection
        time.sleep(5)
        
        # Perform analysis
        print("\nPerforming performance analysis...")
        analysis_results = analyzer.analyze_performance()
        
        # Display results
        print("\nAnalysis Results:")
        print(json.dumps(analysis_results['summary'], indent=2))
        
        # Display recommendations
        print("\nTop Recommendations:")
        for rec in analysis_results.get('recommendations', [])[:3]:
            print(f"- {rec.recommendation_type} (Priority: {rec.priority})")
            print(f"  {rec.description}")
        
        # Export report
        print("\nExported Analysis Report (CSV):")
        csv_data = analyzer.export_analysis_report(format='csv')
        print(csv_data)
        
    except KeyboardInterrupt:
        print("\nStopping analysis...")
    finally:
        collector.stop_collection()
        print("Performance analysis stopped")


if __name__ == "__main__":
    main() 