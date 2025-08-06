#!/usr/bin/env python3
"""
Inspector Standards Reporter

This module implements comprehensive standards reporting for the Inspector system.
Part of Task 3.1.3 in the Inspector Task List.

Features:
- Generate compliance reports
- Create standards dashboard
- Trend analysis and visualization
- Improvement recommendations
- Report export and distribution
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import statistics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

# Import existing modules
from inspector_standards_validator import StandardsValidator, StandardsReport, ValidationResult
from inspector_compliance_checker import ComplianceChecker, ComplianceReport, ComplianceResult
from inspector_config_manager import InspectorConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types of reports"""
    COMPLIANCE_SUMMARY = "compliance_summary"
    STANDARDS_VALIDATION = "standards_validation"
    TREND_ANALYSIS = "trend_analysis"
    IMPROVEMENT_PLAN = "improvement_plan"
    EXECUTIVE_SUMMARY = "executive_summary"

class ReportFormat(Enum):
    """Report formats"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"

@dataclass
class TrendData:
    """Trend analysis data"""
    metric: str
    values: List[float]
    dates: List[datetime]
    trend_direction: str
    trend_strength: float
    change_percentage: float
    confidence_level: float

@dataclass
class ImprovementRecommendation:
    """Improvement recommendation"""
    category: str
    priority: str
    title: str
    description: str
    impact_score: float
    effort_score: float
    roi_score: float
    timeline: str
    dependencies: List[str]
    action_items: List[str]

@dataclass
class StandardsDashboard:
    """Standards dashboard data"""
    dashboard_id: str
    overall_score: float
    overall_grade: str
    category_scores: Dict[str, float]
    recent_trends: List[TrendData]
    top_issues: List[str]
    improvement_opportunities: List[ImprovementRecommendation]
    last_updated: datetime
    next_review_date: datetime

class StandardsReporter:
    """
    Main standards reporter for the Inspector system.
    
    Generates comprehensive reports, creates dashboards, performs trend analysis,
    and provides improvement recommendations.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.standards_validator: Optional[StandardsValidator] = None
        self.compliance_checker: Optional[ComplianceChecker] = None
        self.reports_dir = Path("reports/standards_reports")
        self.dashboards_dir = Path("reports/dashboards")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.dashboards_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self) -> None:
        """Initialize the standards reporter"""
        try:
            logger.info("Initializing Standards Reporter...")
            
            # Initialize validators and checkers
            self.standards_validator = StandardsValidator(self.config_manager)
            await self.standards_validator.initialize()
            
            self.compliance_checker = ComplianceChecker(self.config_manager)
            await self.compliance_checker.initialize()
            
            logger.info("Standards Reporter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Standards Reporter: {e}")
            raise
    
    async def generate_comprehensive_report(self, report_type: ReportType = ReportType.EXECUTIVE_SUMMARY,
                                          format: ReportFormat = ReportFormat.HTML) -> str:
        """Generate a comprehensive standards report"""
        try:
            logger.info(f"Generating {report_type.value} report in {format.value} format...")
            
            # Collect data
            standards_report = await self.standards_validator.validate_standards()
            compliance_report = await self.compliance_checker.check_compliance()
            
            # Generate report based on type
            if report_type == ReportType.COMPLIANCE_SUMMARY:
                report_content = await self._generate_compliance_summary(standards_report, compliance_report)
            elif report_type == ReportType.STANDARDS_VALIDATION:
                report_content = await self._generate_standards_validation_report(standards_report)
            elif report_type == ReportType.TREND_ANALYSIS:
                report_content = await self._generate_trend_analysis_report()
            elif report_type == ReportType.IMPROVEMENT_PLAN:
                report_content = await self._generate_improvement_plan_report(standards_report, compliance_report)
            elif report_type == ReportType.EXECUTIVE_SUMMARY:
                report_content = await self._generate_executive_summary(standards_report, compliance_report)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Format report
            if format == ReportFormat.HTML:
                formatted_report = await self._format_as_html(report_content, report_type)
            elif format == ReportFormat.JSON:
                formatted_report = await self._format_as_json(report_content)
            elif format == ReportFormat.MARKDOWN:
                formatted_report = await self._format_as_markdown(report_content, report_type)
            elif format == ReportFormat.CSV:
                formatted_report = await self._format_as_csv(report_content)
            else:
                formatted_report = report_content
            
            # Save report
            filename = f"{report_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format.value}"
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            
            logger.info(f"Report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    async def create_standards_dashboard(self) -> StandardsDashboard:
        """Create a comprehensive standards dashboard"""
        try:
            logger.info("Creating standards dashboard...")
            
            # Get latest reports
            standards_report = await self.standards_validator.validate_standards()
            compliance_report = await self.compliance_checker.check_compliance()
            
            # Calculate overall metrics
            overall_score = (standards_report.overall_score + compliance_report.overall_score) / 2
            overall_grade = self._calculate_overall_grade(overall_score)
            
            # Get category scores
            category_scores = {}
            for category, score in compliance_report.category_scores.items():
                category_scores[category.value] = score
            
            # Analyze trends
            recent_trends = await self._analyze_trends()
            
            # Identify top issues
            top_issues = await self._identify_top_issues(standards_report, compliance_report)
            
            # Generate improvement opportunities
            improvement_opportunities = await self._generate_improvement_opportunities(
                standards_report, compliance_report
            )
            
            # Create dashboard
            dashboard = StandardsDashboard(
                dashboard_id=f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overall_score=overall_score,
                overall_grade=overall_grade,
                category_scores=category_scores,
                recent_trends=recent_trends,
                top_issues=top_issues,
                improvement_opportunities=improvement_opportunities,
                last_updated=datetime.now(timezone.utc),
                next_review_date=datetime.now(timezone.utc) + timedelta(days=7)
            )
            
            # Save dashboard
            await self._save_dashboard(dashboard)
            
            logger.info("Standards dashboard created successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    async def analyze_trends(self, days: int = 30) -> List[TrendData]:
        """Analyze trends over a specified period"""
        try:
            logger.info(f"Analyzing trends over {days} days...")
            
            # Get historical data
            standards_history = await self.standards_validator.get_validation_history(limit=50)
            compliance_history = await self.compliance_checker.get_compliance_history(limit=50)
            
            trends = []
            
            # Analyze overall score trends
            overall_scores = []
            dates = []
            
            for report in standards_history:
                if isinstance(report, dict) and 'overall_score' in report:
                    overall_scores.append(report['overall_score'])
                    dates.append(datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00')))
            
            if len(overall_scores) > 1:
                trend_data = self._calculate_trend(overall_scores, dates, "Overall Score")
                trends.append(trend_data)
            
            # Analyze compliance grade trends
            compliance_scores = []
            compliance_dates = []
            
            for report in compliance_history:
                if isinstance(report, dict) and 'overall_score' in report:
                    compliance_scores.append(report['overall_score'])
                    compliance_dates.append(datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00')))
            
            if len(compliance_scores) > 1:
                trend_data = self._calculate_trend(compliance_scores, compliance_dates, "Compliance Score")
                trends.append(trend_data)
            
            logger.info(f"Trend analysis completed. Found {len(trends)} trends.")
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return []
    
    async def generate_improvement_recommendations(self, 
                                                 standards_report: StandardsReport,
                                                 compliance_report: ComplianceReport) -> List[ImprovementRecommendation]:
        """Generate improvement recommendations based on reports"""
        try:
            logger.info("Generating improvement recommendations...")
            
            recommendations = []
            
            # Analyze failed requirements
            failed_requirements = [r for r in standards_report.validation_results if r.status.value == "fail"]
            for requirement in failed_requirements:
                if requirement.requirement.validation_level.value == "critical":
                    recommendations.append(ImprovementRecommendation(
                        category=requirement.requirement.standard_type.value,
                        priority="Critical",
                        title=f"Fix {requirement.requirement.title}",
                        description=requirement.requirement.description,
                        impact_score=3.0,
                        effort_score=2.0,
                        roi_score=1.5,
                        timeline="Immediate",
                        dependencies=[],
                        action_items=[
                            f"Address {requirement.requirement.title}",
                            "Implement required fixes",
                            "Retest after implementation"
                        ]
                    ))
            
            # Analyze failed compliance checks
            failed_checks = [r for r in compliance_report.compliance_results if r.status.value == "fail"]
            for check in failed_checks:
                if check.check.weight >= 1.5:
                    recommendations.append(ImprovementRecommendation(
                        category=check.check.category.value,
                        priority="High" if check.check.weight >= 2.0 else "Medium",
                        title=f"Improve {check.check.title}",
                        description=check.check.description,
                        impact_score=2.5,
                        effort_score=1.5,
                        roi_score=1.7,
                        timeline="1-2 weeks",
                        dependencies=[],
                        action_items=[
                            f"Address {check.check.title}",
                            "Review and implement improvements",
                            "Validate improvements"
                        ]
                    ))
            
            # Add performance-specific recommendations
            if any(r.requirement.standard_type.value == "performance_standards" 
                   and r.status.value == "fail" for r in standards_report.validation_results):
                recommendations.append(ImprovementRecommendation(
                    category="performance_standards",
                    priority="Critical",
                    title="Address MCP Server Performance Issues",
                    description="Fix performance and stability issues identified in Task 2.4",
                    impact_score=3.0,
                    effort_score=3.0,
                    roi_score=1.0,
                    timeline="2-4 weeks",
                    dependencies=[],
                    action_items=[
                        "Optimize MCP server response times",
                        "Fix concurrent execution issues",
                        "Improve server stability under load",
                        "Implement proper error recovery"
                    ]
                ))
            
            logger.info(f"Generated {len(recommendations)} improvement recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def _generate_compliance_summary(self, standards_report: StandardsReport, 
                                         compliance_report: ComplianceReport) -> Dict[str, Any]:
        """Generate compliance summary report"""
        return {
            "report_type": "compliance_summary",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_metrics": {
                "standards_score": standards_report.overall_score,
                "compliance_score": compliance_report.overall_score,
                "combined_score": (standards_report.overall_score + compliance_report.overall_score) / 2
            },
            "standards_summary": {
                "total_requirements": standards_report.total_requirements,
                "passed_requirements": standards_report.passed_requirements,
                "failed_requirements": standards_report.failed_requirements,
                "compliance_level": standards_report.compliance_level
            },
            "compliance_summary": {
                "total_checks": compliance_report.total_checks,
                "passed_checks": compliance_report.passed_checks,
                "failed_checks": compliance_report.failed_checks,
                "overall_grade": compliance_report.overall_grade.value
            },
            "category_breakdown": compliance_report.category_scores,
            "top_issues": await self._identify_top_issues(standards_report, compliance_report),
            "recommendations": standards_report.recommendations + compliance_report.recommendations
        }
    
    async def _generate_standards_validation_report(self, standards_report: StandardsReport) -> Dict[str, Any]:
        """Generate detailed standards validation report"""
        return {
            "report_type": "standards_validation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "standards_report": asdict(standards_report),
            "detailed_analysis": {
                "critical_requirements": len([r for r in standards_report.validation_results 
                                           if r.requirement.validation_level.value == "critical"]),
                "high_priority_requirements": len([r for r in standards_report.validation_results 
                                                 if r.requirement.validation_level.value == "high"]),
                "medium_priority_requirements": len([r for r in standards_report.validation_results 
                                                   if r.requirement.validation_level.value == "medium"])
            }
        }
    
    async def _generate_trend_analysis_report(self) -> Dict[str, Any]:
        """Generate trend analysis report"""
        trends = await self.analyze_trends()
        
        return {
            "report_type": "trend_analysis",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trends": [asdict(trend) for trend in trends],
            "analysis_period": "30 days",
            "trend_summary": {
                "improving_metrics": len([t for t in trends if t.trend_direction == "improving"]),
                "declining_metrics": len([t for t in trends if t.trend_direction == "declining"]),
                "stable_metrics": len([t for t in trends if t.trend_direction == "stable"])
            }
        }
    
    async def _generate_improvement_plan_report(self, standards_report: StandardsReport,
                                              compliance_report: ComplianceReport) -> Dict[str, Any]:
        """Generate improvement plan report"""
        recommendations = await self.generate_improvement_recommendations(standards_report, compliance_report)
        
        return {
            "report_type": "improvement_plan",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_state": {
                "standards_score": standards_report.overall_score,
                "compliance_score": compliance_report.overall_score
            },
            "target_state": {
                "standards_score": 90.0,
                "compliance_score": 90.0
            },
            "recommendations": [asdict(rec) for rec in recommendations],
            "implementation_plan": {
                "immediate_actions": [r for r in recommendations if r.priority == "Critical"],
                "short_term_actions": [r for r in recommendations if r.priority == "High"],
                "medium_term_actions": [r for r in recommendations if r.priority == "Medium"]
            }
        }
    
    async def _generate_executive_summary(self, standards_report: StandardsReport,
                                        compliance_report: ComplianceReport) -> Dict[str, Any]:
        """Generate executive summary report"""
        combined_score = (standards_report.overall_score + compliance_report.overall_score) / 2
        overall_grade = self._calculate_overall_grade(combined_score)
        
        return {
            "report_type": "executive_summary",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "executive_summary": {
                "overall_score": combined_score,
                "overall_grade": overall_grade,
                "status": "Needs Improvement" if combined_score < 80 else "Good" if combined_score < 90 else "Excellent",
                "key_achievements": [
                    f"Standards compliance: {standards_report.overall_score:.1f}%",
                    f"Protocol compliance: {compliance_report.overall_score:.1f}%"
                ],
                "critical_issues": len([r for r in standards_report.validation_results 
                                      if r.status.value == "fail" and r.requirement.validation_level.value == "critical"]),
                "recommendations_count": len(standards_report.recommendations) + len(compliance_report.recommendations)
            },
            "quick_facts": {
                "total_requirements": standards_report.total_requirements,
                "total_checks": compliance_report.total_checks,
                "passed_items": standards_report.passed_requirements + compliance_report.passed_checks,
                "failed_items": standards_report.failed_requirements + compliance_report.failed_checks
            }
        }
    
    async def _format_as_html(self, content: Dict[str, Any], report_type: ReportType) -> str:
        """Format report as HTML"""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspector Standards Report - {report_type.value.replace('_', ' ').title()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
        .critical {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .success {{ color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Inspector Standards Report</h1>
        <h2>{report_type.value.replace('_', ' ').title()}</h2>
        <p>Generated: {content.get('timestamp', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h3>Report Content</h3>
        <pre>{json.dumps(content, indent=2)}</pre>
    </div>
</body>
</html>
        """
        return html_template
    
    async def _format_as_json(self, content: Dict[str, Any]) -> str:
        """Format report as JSON"""
        return json.dumps(content, indent=2, default=str)
    
    async def _format_as_markdown(self, content: Dict[str, Any], report_type: ReportType) -> str:
        """Format report as Markdown"""
        markdown = f"""# Inspector Standards Report

## {report_type.value.replace('_', ' ').title()}

**Generated:** {content.get('timestamp', 'Unknown')}

## Summary

"""
        
        if 'executive_summary' in content:
            summary = content['executive_summary']
            markdown += f"""
- **Overall Score:** {summary.get('overall_score', 'N/A')}%
- **Overall Grade:** {summary.get('overall_grade', 'N/A')}
- **Status:** {summary.get('status', 'N/A')}
- **Critical Issues:** {summary.get('critical_issues', 'N/A')}

### Key Achievements
"""
            for achievement in summary.get('key_achievements', []):
                markdown += f"- {achievement}\n"
        
        markdown += f"""
## Detailed Report

```json
{json.dumps(content, indent=2)}
```
"""
        return markdown
    
    async def _format_as_csv(self, content: Dict[str, Any]) -> str:
        """Format report as CSV"""
        # Simplified CSV format for key metrics
        csv_lines = ["Metric,Value"]
        
        if 'executive_summary' in content:
            summary = content['executive_summary']
            csv_lines.extend([
                f"Overall Score,{summary.get('overall_score', 'N/A')}",
                f"Overall Grade,{summary.get('overall_grade', 'N/A')}",
                f"Status,{summary.get('status', 'N/A')}",
                f"Critical Issues,{summary.get('critical_issues', 'N/A')}"
            ])
        
        return "\n".join(csv_lines)
    
    async def _analyze_trends(self) -> List[TrendData]:
        """Analyze trends from historical data"""
        return await self.analyze_trends()
    
    async def _identify_top_issues(self, standards_report: StandardsReport,
                                 compliance_report: ComplianceReport) -> List[str]:
        """Identify top issues from reports"""
        issues = []
        
        # Add failed critical requirements
        critical_failures = [r for r in standards_report.validation_results 
                           if r.status.value == "fail" and r.requirement.validation_level.value == "critical"]
        for failure in critical_failures:
            issues.append(f"Critical: {failure.requirement.title}")
        
        # Add failed high-priority checks
        high_priority_failures = [r for r in compliance_report.compliance_results 
                                if r.status.value == "fail" and r.check.weight >= 1.5]
        for failure in high_priority_failures:
            issues.append(f"High Priority: {failure.check.title}")
        
        return issues[:10]  # Return top 10 issues
    
    async def _generate_improvement_opportunities(self, standards_report: StandardsReport,
                                                compliance_report: ComplianceReport) -> List[ImprovementRecommendation]:
        """Generate improvement opportunities"""
        return await self.generate_improvement_recommendations(standards_report, compliance_report)
    
    def _calculate_overall_grade(self, score: float) -> str:
        """Calculate overall grade from score"""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        else:
            return "F"
    
    def _calculate_trend(self, values: List[float], dates: List[datetime], metric: str) -> TrendData:
        """Calculate trend for a metric"""
        if len(values) < 2:
            return TrendData(
                metric=metric,
                values=values,
                dates=dates,
                trend_direction="insufficient_data",
                trend_strength=0.0,
                change_percentage=0.0,
                confidence_level=0.0
            )
        
        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Determine trend direction
        if slope > 0.1:
            trend_direction = "improving"
        elif slope < -0.1:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        # Calculate change percentage
        change_percentage = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
        
        # Calculate confidence (R-squared)
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        confidence_level = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return TrendData(
            metric=metric,
            values=values,
            dates=dates,
            trend_direction=trend_direction,
            trend_strength=abs(slope),
            change_percentage=change_percentage,
            confidence_level=confidence_level
        )
    
    async def _save_dashboard(self, dashboard: StandardsDashboard) -> None:
        """Save dashboard to file"""
        try:
            filename = f"{dashboard.dashboard_id}.json"
            filepath = self.dashboards_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(dashboard), f, indent=2, default=str)
            
            logger.info(f"Dashboard saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save dashboard: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            logger.info("Cleaning up Standards Reporter...")
            
            if self.standards_validator:
                await self.standards_validator.cleanup()
            
            if self.compliance_checker:
                await self.compliance_checker.cleanup()
            
            logger.info("Standards Reporter cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

async def main():
    """Main function for testing"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize standards reporter
        reporter = StandardsReporter(config_manager)
        await reporter.initialize()
        
        # Generate executive summary report
        report_path = await reporter.generate_comprehensive_report(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            format=ReportFormat.HTML
        )
        
        # Create dashboard
        dashboard = await reporter.create_standards_dashboard()
        
        print(f"\nReport generated: {report_path}")
        print(f"Dashboard created: {dashboard.dashboard_id}")
        print(f"Overall Score: {dashboard.overall_score:.1f}%")
        print(f"Overall Grade: {dashboard.overall_grade}")
        
        # Cleanup
        await reporter.cleanup()
        await config_manager.cleanup()
        
    except Exception as e:
        logger.error(f"Standards reporting failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 