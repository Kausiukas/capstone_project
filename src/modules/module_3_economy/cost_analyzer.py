"""
Cost Analyzer for Module 3: ECONOMY

This module handles cost analysis, reporting, and insights for the system.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from enum import Enum

import aiofiles


class AnalysisPeriod(Enum):
    """Analysis period types"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class CostCategory(Enum):
    """Cost category types"""
    API_CALLS = "api_calls"
    MODEL_USAGE = "model_usage"
    STORAGE = "storage"
    COMPUTATION = "computation"
    NETWORK = "network"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


@dataclass
class CostTrend:
    """Cost trend analysis"""
    period: str
    start_date: datetime
    end_date: datetime
    total_cost: Decimal
    cost_change: Decimal
    percentage_change: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    confidence_level: float


@dataclass
class CostBreakdown:
    """Cost breakdown by category"""
    category: CostCategory
    total_cost: Decimal
    percentage: float
    usage_count: int
    avg_cost_per_unit: Decimal
    trend: CostTrend


@dataclass
class CostAnomaly:
    """Cost anomaly detection"""
    id: str
    timestamp: datetime
    category: CostCategory
    expected_cost: Decimal
    actual_cost: Decimal
    deviation_percentage: float
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggested_action: str


@dataclass
class CostReport:
    """Comprehensive cost report"""
    id: str
    period: AnalysisPeriod
    start_date: datetime
    end_date: datetime
    total_cost: Decimal
    cost_breakdown: List[CostBreakdown]
    trends: List[CostTrend]
    anomalies: List[CostAnomaly]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime = None

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now(timezone.utc)


class CostAnalyzer:
    """
    Analyzes cost patterns, trends, and anomalies for the system.
    """
    
    def __init__(self, data_dir: str = "data/analysis"):
        self.data_dir = data_dir
        self.reports: Dict[str, CostReport] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            "low": 0.2,      # 20% deviation
            "medium": 0.5,   # 50% deviation
            "high": 1.0,     # 100% deviation
            "critical": 2.0  # 200% deviation
        }
    
    async def initialize(self) -> None:
        """Initialize the cost analyzer"""
        self.logger.info("Initializing cost analyzer...")
        
        try:
            await self._ensure_data_dir()
            await self._load_reports()
            
            self.logger.info("Cost analyzer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize cost analyzer: {e}")
            raise
    
    async def analyze_costs(
        self,
        cost_data: List[Dict],
        period: AnalysisPeriod = AnalysisPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Analyze costs and generate a comprehensive report"""
        async with self._lock:
            try:
                if not start_date:
                    start_date = datetime.utcnow() - timedelta(days=30)
                if not end_date:
                    end_date = datetime.utcnow()
                
                report_id = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                # Generate cost breakdown
                cost_breakdown = await self._generate_cost_breakdown(cost_data, start_date, end_date)
                
                # Analyze trends
                trends = await self._analyze_cost_trends(cost_data, period, start_date, end_date)
                
                # Detect anomalies
                anomalies = await self._detect_anomalies(cost_data, start_date, end_date)
                
                # Generate insights
                insights = await self._generate_insights(cost_breakdown, trends, anomalies)
                
                # Generate recommendations
                recommendations = await self._generate_recommendations(cost_breakdown, trends, anomalies)
                
                # Calculate total cost
                total_cost = sum(bd.total_cost for bd in cost_breakdown)
                
                report = CostReport(
                    id=report_id,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    total_cost=total_cost,
                    cost_breakdown=cost_breakdown,
                    trends=trends,
                    anomalies=anomalies,
                    insights=insights,
                    recommendations=recommendations
                )
                
                self.reports[report_id] = report
                await self._save_reports()
                
                self.logger.info(f"Generated cost analysis report: {report_id}")
                return report_id
                
            except Exception as e:
                self.logger.error(f"Failed to analyze costs: {e}")
                raise
    
    async def get_report(self, report_id: str) -> Optional[CostReport]:
        """Get report by ID"""
        return self.reports.get(report_id)
    
    async def list_reports(
        self,
        period: Optional[AnalysisPeriod] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostReport]:
        """List reports with optional filtering"""
        reports = list(self.reports.values())
        
        if period:
            reports = [r for r in reports if r.period == period]
        if start_date:
            reports = [r for r in reports if r.start_date >= start_date]
        if end_date:
            reports = [r for r in reports if r.end_date <= end_date]
        
        return sorted(reports, key=lambda x: x.generated_at, reverse=True)
    
    async def detect_anomalies(
        self,
        cost_data: List[Dict],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostAnomaly]:
        """Detect cost anomalies in the data"""
        async with self._lock:
            try:
                if not start_date:
                    start_date = datetime.utcnow() - timedelta(days=7)
                if not end_date:
                    end_date = datetime.utcnow()
                
                anomalies = []
                
                # Group data by category and time period
                for category in CostCategory:
                    category_data = [
                        d for d in cost_data
                        if d.get('category') == category.value
                        and start_date <= datetime.fromisoformat(d.get('timestamp', '')) <= end_date
                    ]
                    
                    if not category_data:
                        continue
                    
                    # Calculate expected costs based on historical patterns
                    expected_costs = await self._calculate_expected_costs(category_data)
                    
                    # Compare actual vs expected
                    for data_point in category_data:
                        actual_cost = Decimal(str(data_point.get('cost', 0)))
                        timestamp = datetime.fromisoformat(data_point.get('timestamp', ''))
                        
                        # Find expected cost for this time period
                        expected_cost = await self._get_expected_cost_for_timestamp(
                            expected_costs, timestamp
                        )
                        
                        if expected_cost > 0:
                            deviation = abs(actual_cost - expected_cost) / expected_cost
                            
                            if deviation > self.anomaly_thresholds["low"]:
                                severity = self._determine_anomaly_severity(deviation)
                                
                                anomaly = CostAnomaly(
                                    id=f"anomaly_{timestamp.strftime('%Y%m%d_%H%M%S')}_{category.value}",
                                    timestamp=timestamp,
                                    category=category,
                                    expected_cost=expected_cost,
                                    actual_cost=actual_cost,
                                    deviation_percentage=deviation * 100,
                                    severity=severity,
                                    description=f"Cost deviation of {deviation:.1%} detected",
                                    suggested_action=self._get_anomaly_action(severity, category)
                                )
                                
                                anomalies.append(anomaly)
                
                return anomalies
                
            except Exception as e:
                self.logger.error(f"Failed to detect anomalies: {e}")
                raise
    
    async def get_cost_trends(
        self,
        cost_data: List[Dict],
        period: AnalysisPeriod = AnalysisPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostTrend]:
        """Analyze cost trends over time"""
        async with self._lock:
            try:
                if not start_date:
                    start_date = datetime.utcnow() - timedelta(days=30)
                if not end_date:
                    end_date = datetime.utcnow()
                
                return await self._analyze_cost_trends(cost_data, period, start_date, end_date)
                
            except Exception as e:
                self.logger.error(f"Failed to get cost trends: {e}")
                raise
    
    async def get_cost_breakdown(
        self,
        cost_data: List[Dict],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CostBreakdown]:
        """Get cost breakdown by category"""
        async with self._lock:
            try:
                if not start_date:
                    start_date = datetime.utcnow() - timedelta(days=30)
                if not end_date:
                    end_date = datetime.utcnow()
                
                return await self._generate_cost_breakdown(cost_data, start_date, end_date)
                
            except Exception as e:
                self.logger.error(f"Failed to get cost breakdown: {e}")
                raise
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'reports.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_reports(self) -> None:
        """Load reports from file"""
        filepath = os.path.join(self.data_dir, 'reports.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    reports_data = json.loads(data)
                    
                    for report_data in reports_data:
                        # Reconstruct CostReport from data
                        cost_breakdown = []
                        for breakdown_data in report_data['cost_breakdown']:
                            breakdown = CostBreakdown(
                                category=CostCategory(breakdown_data['category']),
                                total_cost=Decimal(str(breakdown_data['total_cost'])),
                                percentage=breakdown_data['percentage'],
                                usage_count=breakdown_data['usage_count'],
                                avg_cost_per_unit=Decimal(str(breakdown_data['avg_cost_per_unit'])),
                                trend=CostTrend(**breakdown_data['trend'])
                            )
                            cost_breakdown.append(breakdown)
                        
                        trends = [CostTrend(**trend_data) for trend_data in report_data['trends']]
                        anomalies = [CostAnomaly(**anomaly_data) for anomaly_data in report_data['anomalies']]
                        
                        report = CostReport(
                            id=report_data['id'],
                            period=AnalysisPeriod(report_data['period']),
                            start_date=datetime.fromisoformat(report_data['start_date']),
                            end_date=datetime.fromisoformat(report_data['end_date']),
                            total_cost=Decimal(str(report_data['total_cost'])),
                            cost_breakdown=cost_breakdown,
                            trends=trends,
                            anomalies=anomalies,
                            insights=report_data['insights'],
                            recommendations=report_data['recommendations'],
                            generated_at=datetime.fromisoformat(report_data['generated_at'])
                        )
                        self.reports[report.id] = report
            else:
                # Create default file
                await self._save_reports()
        except Exception as e:
            self.logger.error(f"Failed to load reports: {e}")
            # Create default file on error
            await self._save_reports()
    
    async def _save_reports(self) -> None:
        """Save reports to file"""
        try:
            reports_file = f"{self.data_dir}/reports.json"
            reports_data = []
            for report in self.reports.values():
                report_dict = asdict(report)
                report_dict['period'] = report_dict['period'].value
                report_dict['start_date'] = report_dict['start_date'].isoformat()
                report_dict['end_date'] = report_dict['end_date'].isoformat()
                report_dict['generated_at'] = report_dict['generated_at'].isoformat()
                
                # Convert nested objects
                for breakdown in report_dict['cost_breakdown']:
                    breakdown['category'] = breakdown['category'].value
                    breakdown['total_cost'] = str(breakdown['total_cost'])
                    breakdown['avg_cost_per_unit'] = str(breakdown['avg_cost_per_unit'])
                
                reports_data.append(report_dict)
            
            async with aiofiles.open(reports_file, 'w') as f:
                await f.write(json.dumps(reports_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save reports: {e}")
    
    async def _generate_cost_breakdown(
        self,
        cost_data: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[CostBreakdown]:
        """Generate cost breakdown by category"""
        breakdowns = []
        total_cost = Decimal('0')
        
        # Filter data by date range
        filtered_data = [
            d for d in cost_data
            if start_date <= datetime.fromisoformat(d.get('timestamp', '')) <= end_date
        ]
        
        # Group by category
        category_data = {}
        for data in filtered_data:
            category = data.get('category', 'other')
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(data)
        
        # Calculate totals
        for category_name, data in category_data.items():
            category_cost = sum(Decimal(str(d.get('cost', 0))) for d in data)
            total_cost += category_cost
        
        # Generate breakdowns
        for category_name, data in category_data.items():
            category_cost = sum(Decimal(str(d.get('cost', 0))) for d in data)
            percentage = float(category_cost / total_cost * 100) if total_cost > 0 else 0
            avg_cost = category_cost / len(data) if data else Decimal('0')
            
            breakdown = CostBreakdown(
                category=CostCategory(category_name),
                total_cost=category_cost,
                percentage=percentage,
                usage_count=len(data),
                avg_cost_per_unit=avg_cost,
                trend=CostTrend(  # Placeholder trend
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    total_cost=category_cost,
                    cost_change=Decimal('0'),
                    percentage_change=0.0,
                    trend_direction="stable",
                    confidence_level=0.8
                )
            )
            
            breakdowns.append(breakdown)
        
        return breakdowns
    
    async def _analyze_cost_trends(
        self,
        cost_data: List[Dict],
        period: AnalysisPeriod,
        start_date: datetime,
        end_date: datetime
    ) -> List[CostTrend]:
        """Analyze cost trends over time"""
        trends = []
        
        # Group data by time periods
        period_data = self._group_data_by_period(cost_data, period, start_date, end_date)
        
        # Calculate trends for each category
        for category in CostCategory:
            category_trends = self._calculate_category_trends(period_data, category)
            trends.extend(category_trends)
        
        return trends
    
    async def _detect_anomalies(
        self,
        cost_data: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[CostAnomaly]:
        """Detect anomalies in cost data"""
        return await self.detect_anomalies(cost_data, start_date, end_date)
    
    async def _generate_insights(
        self,
        breakdown: List[CostBreakdown],
        trends: List[CostTrend],
        anomalies: List[CostAnomaly]
    ) -> List[str]:
        """Generate insights from analysis"""
        insights = []
        
        # Top cost category
        if breakdown:
            top_category = max(breakdown, key=lambda x: x.total_cost)
            insights.append(f"Highest cost category: {top_category.category.value} ({top_category.percentage:.1f}%)")
        
        # Trend insights
        increasing_trends = [t for t in trends if t.trend_direction == "increasing"]
        if increasing_trends:
            insights.append(f"Found {len(increasing_trends)} categories with increasing costs")
        
        # Anomaly insights
        if anomalies:
            critical_anomalies = [a for a in anomalies if a.severity == "critical"]
            if critical_anomalies:
                insights.append(f"Detected {len(critical_anomalies)} critical cost anomalies")
        
        return insights
    
    async def _generate_recommendations(
        self,
        breakdown: List[CostBreakdown],
        trends: List[CostTrend],
        anomalies: List[CostAnomaly]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # High cost recommendations
        high_cost_categories = [b for b in breakdown if b.percentage > 30]
        for category in high_cost_categories:
            recommendations.append(f"Review {category.category.value} usage - represents {category.percentage:.1f}% of total costs")
        
        # Trend-based recommendations
        for trend in trends:
            if trend.trend_direction == "increasing" and trend.percentage_change > 20:
                recommendations.append(f"Investigate increasing trend in {trend.period} costs ({trend.percentage_change:.1f}% increase)")
        
        # Anomaly-based recommendations
        for anomaly in anomalies:
            if anomaly.severity in ["high", "critical"]:
                recommendations.append(f"Address {anomaly.severity} anomaly in {anomaly.category.value}: {anomaly.description}")
        
        return recommendations
    
    def _group_data_by_period(
        self,
        cost_data: List[Dict],
        period: AnalysisPeriod,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List[Dict]]:
        """Group cost data by time periods"""
        period_data = {}
        
        current_date = start_date
        while current_date <= end_date:
            period_key = self._get_period_key(current_date, period)
            period_data[period_key] = []
            current_date = self._get_next_period(current_date, period)
        
        # Assign data to periods
        for data in cost_data:
            timestamp = datetime.fromisoformat(data.get('timestamp', ''))
            if start_date <= timestamp <= end_date:
                period_key = self._get_period_key(timestamp, period)
                if period_key in period_data:
                    period_data[period_key].append(data)
        
        return period_data
    
    def _get_period_key(self, date: datetime, period: AnalysisPeriod) -> str:
        """Get period key for grouping"""
        if period == AnalysisPeriod.HOURLY:
            return date.strftime('%Y-%m-%d %H:00')
        elif period == AnalysisPeriod.DAILY:
            return date.strftime('%Y-%m-%d')
        elif period == AnalysisPeriod.WEEKLY:
            return date.strftime('%Y-W%W')
        elif period == AnalysisPeriod.MONTHLY:
            return date.strftime('%Y-%m')
        elif period == AnalysisPeriod.QUARTERLY:
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"
        else:  # YEARLY
            return date.strftime('%Y')
    
    def _get_next_period(self, date: datetime, period: AnalysisPeriod) -> datetime:
        """Get next period date"""
        if period == AnalysisPeriod.HOURLY:
            return date + timedelta(hours=1)
        elif period == AnalysisPeriod.DAILY:
            return date + timedelta(days=1)
        elif period == AnalysisPeriod.WEEKLY:
            return date + timedelta(weeks=1)
        elif period == AnalysisPeriod.MONTHLY:
            if date.month == 12:
                return date.replace(year=date.year + 1, month=1)
            else:
                return date.replace(month=date.month + 1)
        elif period == AnalysisPeriod.QUARTERLY:
            if date.month in [10, 11, 12]:
                return date.replace(year=date.year + 1, month=1)
            else:
                return date.replace(month=date.month + 3)
        else:  # YEARLY
            return date.replace(year=date.year + 1)
    
    def _calculate_category_trends(
        self,
        period_data: Dict[str, List[Dict]],
        category: CostCategory
    ) -> List[CostTrend]:
        """Calculate trends for a specific category"""
        trends = []
        periods = sorted(period_data.keys())
        
        for i, period in enumerate(periods):
            category_data = [
                d for d in period_data[period]
                if d.get('category') == category.value
            ]
            
            total_cost = sum(Decimal(str(d.get('cost', 0))) for d in category_data)
            
            if i > 0:
                prev_period = periods[i-1]
                prev_category_data = [
                    d for d in period_data[prev_period]
                    if d.get('category') == category.value
                ]
                prev_total_cost = sum(Decimal(str(d.get('cost', 0))) for d in prev_category_data)
                
                cost_change = total_cost - prev_total_cost
                percentage_change = float(cost_change / prev_total_cost * 100) if prev_total_cost > 0 else 0
                
                if percentage_change > 5:
                    trend_direction = "increasing"
                elif percentage_change < -5:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                trend = CostTrend(
                    period=period,
                    start_date=datetime.strptime(period, '%Y-%m-%d'),
                    end_date=datetime.strptime(period, '%Y-%m-%d'),
                    total_cost=total_cost,
                    cost_change=cost_change,
                    percentage_change=percentage_change,
                    trend_direction=trend_direction,
                    confidence_level=0.8
                )
                
                trends.append(trend)
        
        return trends
    
    async def _calculate_expected_costs(self, category_data: List[Dict]) -> Dict[str, Decimal]:
        """Calculate expected costs based on historical patterns"""
        # Simple moving average for now
        if len(category_data) < 3:
            return {}
        
        costs = [Decimal(str(d.get('cost', 0))) for d in category_data]
        avg_cost = sum(costs) / len(costs)
        
        return {"average": avg_cost}
    
    async def _get_expected_cost_for_timestamp(
        self,
        expected_costs: Dict[str, Decimal],
        timestamp: datetime
    ) -> Decimal:
        """Get expected cost for a specific timestamp"""
        return expected_costs.get("average", Decimal('0'))
    
    def _determine_anomaly_severity(self, deviation: float) -> str:
        """Determine anomaly severity based on deviation"""
        if deviation >= self.anomaly_thresholds["critical"]:
            return "critical"
        elif deviation >= self.anomaly_thresholds["high"]:
            return "high"
        elif deviation >= self.anomaly_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _get_anomaly_action(self, severity: str, category: CostCategory) -> str:
        """Get suggested action for an anomaly"""
        if severity == "critical":
            return f"Immediately investigate {category.value} usage and implement cost controls"
        elif severity == "high":
            return f"Review {category.value} usage patterns and consider optimization"
        elif severity == "medium":
            return f"Monitor {category.value} usage for continued anomalies"
        else:
            return f"Continue monitoring {category.value} usage" 