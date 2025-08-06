"""
Inspector Quality Assurance Module
Task 3.2.1: Inspector Quality Assurance

This module provides comprehensive quality assurance capabilities for the Inspector system,
including quality metrics calculation, quality scoring, and quality management.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics
from collections import defaultdict

from inspector_config_manager import InspectorConfigManager


class QualityMetric(Enum):
    """Quality metrics for the Inspector system."""
    FUNCTIONALITY = "functionality"
    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    STABILITY = "stability"


class QualityLevel(Enum):
    """Quality levels for scoring."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class QualityMetricData:
    """Data structure for quality metric measurements."""
    metric: QualityMetric
    value: float
    weight: float
    timestamp: datetime
    description: str
    source: str
    confidence: float = 1.0


@dataclass
class QualityScore:
    """Quality score for a specific metric or category."""
    metric: QualityMetric
    score: float  # 0.0 to 1.0
    level: QualityLevel
    weight: float
    details: Dict[str, Any]
    timestamp: datetime


@dataclass
class QualityReport:
    """Comprehensive quality report."""
    overall_score: float
    overall_level: QualityLevel
    metric_scores: Dict[QualityMetric, QualityScore]
    recommendations: List[str]
    timestamp: datetime
    period: str
    summary: str


class InspectorQualityAssurance:
    """
    Comprehensive quality assurance system for the Inspector.
    
    Provides quality metrics calculation, scoring, and management capabilities.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        """Initialize the quality assurance system."""
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.thresholds = {
            QualityLevel.EXCELLENT: 0.9,
            QualityLevel.GOOD: 0.8,
            QualityLevel.ACCEPTABLE: 0.7,
            QualityLevel.POOR: 0.6,
            QualityLevel.CRITICAL: 0.0
        }
        
        # Metric weights (sum = 1.0)
        self.metric_weights = {
            QualityMetric.FUNCTIONALITY: 0.25,
            QualityMetric.RELIABILITY: 0.20,
            QualityMetric.PERFORMANCE: 0.20,
            QualityMetric.USABILITY: 0.10,
            QualityMetric.MAINTAINABILITY: 0.10,
            QualityMetric.SECURITY: 0.10,
            QualityMetric.COMPLIANCE: 0.03,
            QualityMetric.STABILITY: 0.02
        }
        
        # Data storage
        self.quality_data: List[QualityMetricData] = []
        self.reports: List[QualityReport] = []
        
        # Ensure data directory exists
        self.data_dir = Path("results/inspector/quality")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def add_quality_metric(self, metric: QualityMetric, value: float, 
                          description: str, source: str, weight: Optional[float] = None,
                          confidence: float = 1.0) -> None:
        """Add a quality metric measurement."""
        if weight is None:
            weight = self.metric_weights.get(metric, 0.1)
        
        metric_data = QualityMetricData(
            metric=metric,
            value=value,
            weight=weight,
            timestamp=datetime.now(),
            description=description,
            source=source,
            confidence=confidence
        )
        
        self.quality_data.append(metric_data)
        self.logger.info(f"Added quality metric: {metric.value} = {value:.3f}")
    
    def calculate_quality_score(self, metric: QualityMetric, 
                              time_window: Optional[timedelta] = None) -> QualityScore:
        """Calculate quality score for a specific metric."""
        # Filter data by metric and time window
        filtered_data = [
            data for data in self.quality_data 
            if data.metric == metric
        ]
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            filtered_data = [
                data for data in filtered_data 
                if data.timestamp >= cutoff_time
            ]
        
        if not filtered_data:
            # No data available, return neutral score
            return QualityScore(
                metric=metric,
                score=0.5,
                level=QualityLevel.ACCEPTABLE,
                weight=self.metric_weights.get(metric, 0.1),
                details={"reason": "No data available"},
                timestamp=datetime.now()
            )
        
        # Calculate weighted average
        total_weight = sum(data.weight * data.confidence for data in filtered_data)
        weighted_sum = sum(data.value * data.weight * data.confidence for data in filtered_data)
        
        if total_weight == 0:
            score = 0.5
        else:
            score = weighted_sum / total_weight
        
        # Determine quality level
        level = self._determine_quality_level(score)
        
        # Prepare details
        details = {
            "data_points": len(filtered_data),
            "min_value": min(data.value for data in filtered_data),
            "max_value": max(data.value for data in filtered_data),
            "avg_value": statistics.mean(data.value for data in filtered_data),
            "std_dev": statistics.stdev(data.value for data in filtered_data) if len(filtered_data) > 1 else 0,
            "confidence": statistics.mean(data.confidence for data in filtered_data),
            "time_span": (max(data.timestamp for data in filtered_data) - 
                         min(data.timestamp for data in filtered_data)).total_seconds()
        }
        
        return QualityScore(
            metric=metric,
            score=score,
            level=level,
            weight=self.metric_weights.get(metric, 0.1),
            details=details,
            timestamp=datetime.now()
        )
    
    def generate_quality_report(self, time_window: Optional[timedelta] = None,
                              period: str = "current") -> QualityReport:
        """Generate a comprehensive quality report."""
        # Calculate scores for all metrics
        metric_scores = {}
        for metric in QualityMetric:
            score = self.calculate_quality_score(metric, time_window)
            metric_scores[metric] = score
        
        # Calculate overall score
        overall_score = sum(
            score.score * score.weight 
            for score in metric_scores.values()
        )
        
        # Determine overall level
        overall_level = self._determine_quality_level(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_scores, overall_score)
        
        # Create summary
        summary = self._create_summary(metric_scores, overall_score, overall_level)
        
        report = QualityReport(
            overall_score=overall_score,
            overall_level=overall_level,
            metric_scores=metric_scores,
            recommendations=recommendations,
            timestamp=datetime.now(),
            period=period,
            summary=summary
        )
        
        self.reports.append(report)
        return report
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on score."""
        if score >= self.thresholds[QualityLevel.EXCELLENT]:
            return QualityLevel.EXCELLENT
        elif score >= self.thresholds[QualityLevel.GOOD]:
            return QualityLevel.GOOD
        elif score >= self.thresholds[QualityLevel.ACCEPTABLE]:
            return QualityLevel.ACCEPTABLE
        elif score >= self.thresholds[QualityLevel.POOR]:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _generate_recommendations(self, metric_scores: Dict[QualityMetric, QualityScore], 
                                overall_score: float) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Overall recommendations
        if overall_score < 0.7:
            recommendations.append("Overall quality needs significant improvement")
        elif overall_score < 0.8:
            recommendations.append("Overall quality needs moderate improvement")
        
        # Metric-specific recommendations
        for metric, score in metric_scores.items():
            if score.level in [QualityLevel.POOR, QualityLevel.CRITICAL]:
                recommendations.append(f"Improve {metric.value}: Current score {score.score:.3f}")
            elif score.score < 0.8:
                recommendations.append(f"Consider improving {metric.value}: Current score {score.score:.3f}")
        
        # Performance-specific recommendations
        if QualityMetric.PERFORMANCE in metric_scores:
            perf_score = metric_scores[QualityMetric.PERFORMANCE]
            if perf_score.score < 0.6:
                recommendations.append("Critical: Performance issues detected - immediate attention required")
            elif perf_score.score < 0.8:
                recommendations.append("Performance optimization recommended")
        
        # Security-specific recommendations
        if QualityMetric.SECURITY in metric_scores:
            sec_score = metric_scores[QualityMetric.SECURITY]
            if sec_score.score < 0.8:
                recommendations.append("Security review recommended")
        
        return recommendations
    
    def _create_summary(self, metric_scores: Dict[QualityMetric, QualityScore], 
                       overall_score: float, overall_level: QualityLevel) -> str:
        """Create a summary of the quality report."""
        excellent_count = sum(1 for score in metric_scores.values() 
                            if score.level == QualityLevel.EXCELLENT)
        good_count = sum(1 for score in metric_scores.values() 
                        if score.level == QualityLevel.GOOD)
        poor_count = sum(1 for score in metric_scores.values() 
                        if score.level in [QualityLevel.POOR, QualityLevel.CRITICAL])
        
        summary = f"Overall Quality: {overall_level.value.title()} ({overall_score:.1%})\n"
        summary += f"Metrics: {excellent_count} excellent, {good_count} good, {poor_count} poor/critical"
        
        return summary
    
    def save_quality_data(self, filename: Optional[str] = None) -> str:
        """Save quality data to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_data_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        # Convert data to serializable format
        data = {
            "quality_data": [
                {
                    "metric": item.metric.value,
                    "value": item.value,
                    "weight": item.weight,
                    "timestamp": item.timestamp.isoformat(),
                    "description": item.description,
                    "source": item.source,
                    "confidence": item.confidence
                }
                for item in self.quality_data
            ],
            "reports": [
                {
                    "overall_score": report.overall_score,
                    "overall_level": report.overall_level.value,
                    "metric_scores": {
                        metric.value: {
                            "score": score.score,
                            "level": score.level.value,
                            "weight": score.weight,
                            "details": score.details,
                            "timestamp": score.timestamp.isoformat()
                        }
                        for metric, score in report.metric_scores.items()
                    },
                    "recommendations": report.recommendations,
                    "timestamp": report.timestamp.isoformat(),
                    "period": report.period,
                    "summary": report.summary
                }
                for report in self.reports
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Quality data saved to {filepath}")
        return str(filepath)
    
    def load_quality_data(self, filename: str) -> None:
        """Load quality data from file."""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Quality data file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load quality data
        self.quality_data = []
        for item in data.get("quality_data", []):
            metric_data = QualityMetricData(
                metric=QualityMetric(item["metric"]),
                value=item["value"],
                weight=item["weight"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                description=item["description"],
                source=item["source"],
                confidence=item["confidence"]
            )
            self.quality_data.append(metric_data)
        
        # Load reports
        self.reports = []
        for report_data in data.get("reports", []):
            metric_scores = {}
            for metric_name, score_data in report_data["metric_scores"].items():
                score = QualityScore(
                    metric=QualityMetric(metric_name),
                    score=score_data["score"],
                    level=QualityLevel(score_data["level"]),
                    weight=score_data["weight"],
                    details=score_data["details"],
                    timestamp=datetime.fromisoformat(score_data["timestamp"])
                )
                metric_scores[QualityMetric(metric_name)] = score
            
            report = QualityReport(
                overall_score=report_data["overall_score"],
                overall_level=QualityLevel(report_data["overall_level"]),
                metric_scores=metric_scores,
                recommendations=report_data["recommendations"],
                timestamp=datetime.fromisoformat(report_data["timestamp"]),
                period=report_data["period"],
                summary=report_data["summary"]
            )
            self.reports.append(report)
        
        self.logger.info(f"Quality data loaded from {filepath}")
    
    def get_quality_trends(self, metric: QualityMetric, 
                          days: int = 7) -> List[Tuple[datetime, float]]:
        """Get quality trends for a specific metric over time."""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Group data by day
        daily_data = defaultdict(list)
        for data in self.quality_data:
            if data.metric == metric and data.timestamp >= cutoff_time:
                day = data.timestamp.date()
                daily_data[day].append(data.value)
        
        # Calculate daily averages
        trends = []
        for day in sorted(daily_data.keys()):
            avg_value = statistics.mean(daily_data[day])
            trends.append((datetime.combine(day, datetime.min.time()), avg_value))
        
        return trends
    
    def export_quality_report(self, report: QualityReport, 
                            format: str = "json") -> str:
        """Export quality report in specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            filename = f"quality_report_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # Convert report to serializable format
            report_data = {
                "overall_score": report.overall_score,
                "overall_level": report.overall_level.value,
                "metric_scores": {
                    metric.value: {
                        "score": score.score,
                        "level": score.level.value,
                        "weight": score.weight,
                        "details": score.details,
                        "timestamp": score.timestamp.isoformat()
                    }
                    for metric, score in report.metric_scores.items()
                },
                "recommendations": report.recommendations,
                "timestamp": report.timestamp.isoformat(),
                "period": report.period,
                "summary": report.summary
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            filename = f"quality_report_{timestamp}.csv"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write("Metric,Score,Level,Weight,Details\n")
                for metric, score in report.metric_scores.items():
                    details_str = json.dumps(score.details).replace('"', '""')
                    f.write(f"{metric.value},{score.score:.3f},{score.level.value},{score.weight},{details_str}\n")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Quality report exported to {filepath}")
        return str(filepath)


def main():
    """Main function for testing the quality assurance module."""
    # Initialize configuration manager
    config_manager = InspectorConfigManager()
    
    # Initialize quality assurance
    qa = InspectorQualityAssurance(config_manager)
    
    # Add sample quality metrics
    qa.add_quality_metric(
        QualityMetric.FUNCTIONALITY, 0.85,
        "Tool execution success rate", "test_tool_execution.py"
    )
    qa.add_quality_metric(
        QualityMetric.PERFORMANCE, 0.45,
        "Response time performance", "test_response_times.py"
    )
    qa.add_quality_metric(
        QualityMetric.RELIABILITY, 0.78,
        "System stability under load", "test_concurrent_execution.py"
    )
    qa.add_quality_metric(
        QualityMetric.SECURITY, 0.92,
        "Security compliance check", "security_audit.py"
    )
    
    # Generate quality report
    report = qa.generate_quality_report()
    
    # Print report
    print("=== Quality Assurance Report ===")
    print(f"Overall Score: {report.overall_score:.1%}")
    print(f"Overall Level: {report.overall_level.value.title()}")
    print(f"Summary: {report.summary}")
    print("\nRecommendations:")
    for rec in report.recommendations:
        print(f"- {rec}")
    
    # Save data
    qa.save_quality_data()
    
    print(f"\nQuality data saved to results/inspector/quality/")


if __name__ == "__main__":
    main() 