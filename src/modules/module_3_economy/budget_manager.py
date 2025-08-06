"""
Budget Manager for Module 3: ECONOMY

This module handles budget allocation, tracking, and management for the system.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union
from enum import Enum

import aiofiles
from aiofiles.os import wrap


class BudgetPeriod(Enum):
    """Budget period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetStatus(Enum):
    """Budget status types"""
    UNDER_BUDGET = "under_budget"
    NEAR_LIMIT = "near_limit"
    OVER_BUDGET = "over_budget"
    CRITICAL = "critical"


@dataclass
class Budget:
    """Budget configuration"""
    id: str
    name: str
    amount: Decimal
    period: BudgetPeriod
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str = ""
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class BudgetUsage:
    """Budget usage tracking"""
    budget_id: str
    period_start: datetime
    period_end: datetime
    allocated_amount: Decimal
    used_amount: Decimal
    remaining_amount: Decimal
    usage_percentage: float
    status: BudgetStatus
    last_updated: datetime


@dataclass
class BudgetAlert:
    """Budget alert configuration"""
    budget_id: str
    threshold_percentage: float
    alert_type: str  # "warning", "critical", "exceeded"
    message: str
    is_active: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class BudgetManager:
    """
    Manages budget allocation, tracking, and alerts for the system.
    """
    
    def __init__(self, data_dir: str = "data/budgets"):
        self.data_dir = data_dir
        self.budgets: Dict[str, Budget] = {}
        self.usage: Dict[str, BudgetUsage] = {}
        self.alerts: Dict[str, List[BudgetAlert]] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Default alert thresholds
        self.default_thresholds = {
            "warning": 0.7,  # 70%
            "critical": 0.9,  # 90%
            "exceeded": 1.0   # 100%
        }
    
    async def initialize(self) -> None:
        """Initialize the budget manager"""
        self.logger.info("Initializing budget manager...")
        
        try:
            await self._ensure_data_dir()
            await self._load_budgets()
            await self._load_usage()
            await self._load_alerts()
            
            self.logger.info("Budget manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize budget manager: {e}")
            raise
    
    async def create_budget(
        self,
        name: str,
        amount: Union[float, Decimal],
        period: Union[BudgetPeriod, str], # Allow string or enum
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        description: str = ""
    ) -> str:
        """Create a new budget"""
        async with self._lock:
            try:
                budget_id = f"budget_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
                
                if start_date is None:
                    start_date = datetime.utcnow()
                
                # Ensure period is an Enum member
                if isinstance(period, str):
                    try:
                        period_enum = BudgetPeriod[period.upper()]
                    except KeyError:
                        raise ValueError(f"Invalid budget period: {period}. Must be one of {list(BudgetPeriod.__members__.keys())}")
                elif isinstance(period, BudgetPeriod):
                    period_enum = period
                else:
                    raise TypeError(f"Period must be a string or BudgetPeriod enum, got {type(period)}")
                
                budget = Budget(
                    id=budget_id,
                    name=name,
                    amount=Decimal(str(amount)),
                    period=period_enum, # Use the enum member
                    start_date=start_date,
                    end_date=end_date,
                    description=description
                )
                
                self.budgets[budget_id] = budget
                await self._save_budgets()
                
                # Create default alerts
                await self._create_default_alerts(budget_id)
                
                self.logger.info(f"Created budget: {budget_id} - {name}")
                return budget_id
                
            except Exception as e:
                self.logger.error(f"Failed to create budget: {e}")
                raise
    
    async def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get budget by ID"""
        return self.budgets.get(budget_id)
    
    async def list_budgets(self, active_only: bool = True) -> List[Budget]:
        """List all budgets"""
        budgets = list(self.budgets.values())
        if active_only:
            budgets = [b for b in budgets if b.is_active]
        return budgets
    
    async def update_budget(
        self,
        budget_id: str,
        amount: Optional[Union[float, Decimal]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """Update budget configuration"""
        async with self._lock:
            try:
                if budget_id not in self.budgets:
                    return False
                
                budget = self.budgets[budget_id]
                
                if amount is not None:
                    budget.amount = Decimal(str(amount))
                if name is not None:
                    budget.name = name
                if description is not None:
                    budget.description = description
                if is_active is not None:
                    budget.is_active = is_active
                
                budget.updated_at = datetime.utcnow()
                await self._save_budgets()
                
                self.logger.info(f"Updated budget: {budget_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update budget: {e}")
                return False
    
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget"""
        async with self._lock:
            try:
                if budget_id not in self.budgets:
                    return False
                
                del self.budgets[budget_id]
                if budget_id in self.usage:
                    del self.usage[budget_id]
                if budget_id in self.alerts:
                    del self.alerts[budget_id]
                
                await self._save_budgets()
                await self._save_usage()
                await self._save_alerts()
                
                self.logger.info(f"Deleted budget: {budget_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete budget: {e}")
                return False
    
    async def record_expense(
        self,
        budget_id: str,
        amount: Union[float, Decimal],
        description: str = "",
        category: str = "general"
    ) -> bool:
        """Record an expense against a budget"""
        async with self._lock:
            try:
                if budget_id not in self.budgets:
                    return False
                
                budget = self.budgets[budget_id]
                if not budget.is_active:
                    return False
                
                # Get or create usage record for current period
                current_usage = await self._get_current_usage(budget_id)
                current_usage.used_amount += Decimal(str(amount))
                current_usage.remaining_amount = current_usage.allocated_amount - current_usage.used_amount
                current_usage.usage_percentage = float(current_usage.used_amount / current_usage.allocated_amount)
                current_usage.last_updated = datetime.utcnow()
                
                # Update status based on usage
                current_usage.status = self._calculate_status(current_usage.usage_percentage)
                
                self.usage[budget_id] = current_usage
                await self._save_usage()
                
                # Check for alerts
                await self._check_alerts(budget_id, current_usage)
                
                self.logger.info(f"Recorded expense: {amount} for budget {budget_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to record expense: {e}")
                return False
    
    async def get_budget_usage(self, budget_id: str) -> Optional[BudgetUsage]:
        """Get current budget usage"""
        return self.usage.get(budget_id)
    
    async def get_all_usage(self) -> List[BudgetUsage]:
        """Get usage for all budgets"""
        return list(self.usage.values())
    
    async def set_alert_threshold(
        self,
        budget_id: str,
        alert_type: str,
        threshold_percentage: float
    ) -> bool:
        """Set alert threshold for a budget"""
        async with self._lock:
            try:
                if budget_id not in self.budgets:
                    return False
                
                if budget_id not in self.alerts:
                    self.alerts[budget_id] = []
                
                # Remove existing alert of this type
                self.alerts[budget_id] = [
                    alert for alert in self.alerts[budget_id]
                    if alert.alert_type != alert_type
                ]
                
                # Add new alert
                alert = BudgetAlert(
                    budget_id=budget_id,
                    threshold_percentage=threshold_percentage,
                    alert_type=alert_type,
                    message=f"{alert_type.title()} alert at {threshold_percentage}% usage"
                )
                
                self.alerts[budget_id].append(alert)
                await self._save_alerts()
                
                self.logger.info(f"Set {alert_type} alert for budget {budget_id} at {threshold_percentage}%")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to set alert threshold: {e}")
                return False
    
    async def get_budget_alerts(self, budget_id: str) -> List[BudgetAlert]:
        """Get alerts for a budget"""
        return self.alerts.get(budget_id, [])
    
    async def get_active_alerts(self) -> List[BudgetAlert]:
        """Get all active alerts"""
        active_alerts = []
        for budget_alerts in self.alerts.values():
            active_alerts.extend([alert for alert in budget_alerts if alert.is_active])
        return active_alerts
    
    async def get_budget_summary(self) -> Dict:
        """Get summary of all budgets"""
        total_budgets = len(self.budgets)
        active_budgets = len([b for b in self.budgets.values() if b.is_active])
        total_allocated = sum(b.amount for b in self.budgets.values() if b.is_active)
        total_used = sum(u.used_amount for u in self.usage.values())
        total_remaining = total_allocated - total_used
        
        return {
            "total_budgets": total_budgets,
            "active_budgets": active_budgets,
            "total_allocated": float(total_allocated),
            "total_used": float(total_used),
            "total_remaining": float(total_remaining),
            "overall_usage_percentage": float(total_used / total_allocated) if total_allocated > 0 else 0
        }
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        import os
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'budgets.json': [],
            'usage.json': [],
            'alerts.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_budgets(self) -> None:
        """Load budgets from file"""
        import os
        filepath = os.path.join(self.data_dir, 'budgets.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    budgets_data = json.loads(data)
                    
                    for budget_data in budgets_data:
                        budget = Budget(
                            id=budget_data['id'],
                            name=budget_data['name'],
                            amount=Decimal(str(budget_data['amount'])),
                            period=BudgetPeriod(budget_data['period']),
                            start_date=datetime.fromisoformat(budget_data['start_date']),
                            end_date=datetime.fromisoformat(budget_data['end_date']) if budget_data.get('end_date') else None,
                            description=budget_data.get('description', ''),
                            is_active=budget_data.get('is_active', True),
                            created_at=datetime.fromisoformat(budget_data['created_at']),
                            updated_at=datetime.fromisoformat(budget_data['updated_at'])
                        )
                        self.budgets[budget.id] = budget
            else:
                # Create default file
                await self._save_budgets()
        except Exception as e:
            self.logger.error(f"Failed to load budgets: {e}")
            # Create default file on error
            await self._save_budgets()

    async def _save_budgets(self) -> None:
        """Save budgets to file"""
        try:
            budget_file = f"{self.data_dir}/budgets.json"
            budgets_data = []
            for budget in self.budgets.values():
                budget_dict = asdict(budget)
                budget_dict['amount'] = str(budget_dict['amount'])
                budget_dict['period'] = budget_dict['period'].value
                budget_dict['start_date'] = budget_dict['start_date'].isoformat()
                if budget_dict['end_date']:
                    budget_dict['end_date'] = budget_dict['end_date'].isoformat()
                budget_dict['created_at'] = budget_dict['created_at'].isoformat()
                budget_dict['updated_at'] = budget_dict['updated_at'].isoformat()
                budgets_data.append(budget_dict)
            
            async with aiofiles.open(budget_file, 'w') as f:
                await f.write(json.dumps(budgets_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save budgets: {e}")
    
    async def _load_usage(self) -> None:
        """Load usage data from file"""
        import os
        filepath = os.path.join(self.data_dir, 'usage.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    usage_data = json.loads(data)
                    
                    for usage_item in usage_data:
                        usage = BudgetUsage(
                            budget_id=usage_item['budget_id'],
                            period_start=datetime.fromisoformat(usage_item['period_start']),
                            period_end=datetime.fromisoformat(usage_item['period_end']),
                            allocated_amount=Decimal(str(usage_item['allocated_amount'])),
                            used_amount=Decimal(str(usage_item['used_amount'])),
                            remaining_amount=Decimal(str(usage_item['remaining_amount'])),
                            usage_percentage=usage_item['usage_percentage'],
                            status=BudgetStatus(usage_item['status']),
                            last_updated=datetime.fromisoformat(usage_item['last_updated'])
                        )
                        self.usage[usage.budget_id] = usage
            else:
                # Create default file
                await self._save_usage()
        except Exception as e:
            self.logger.error(f"Failed to load usage data: {e}")
            # Create default file on error
            await self._save_usage()
    
    async def _save_usage(self) -> None:
        """Save usage data to file"""
        try:
            usage_file = f"{self.data_dir}/usage.json"
            usage_data = []
            for usage in self.usage.values():
                usage_dict = asdict(usage)
                usage_dict['allocated_amount'] = str(usage_dict['allocated_amount'])
                usage_dict['used_amount'] = str(usage_dict['used_amount'])
                usage_dict['remaining_amount'] = str(usage_dict['remaining_amount'])
                usage_dict['period_start'] = usage_dict['period_start'].isoformat()
                usage_dict['period_end'] = usage_dict['period_end'].isoformat()
                usage_dict['last_updated'] = usage_dict['last_updated'].isoformat()
                usage_dict['status'] = usage_dict['status'].value
                usage_data.append(usage_dict)
            
            async with aiofiles.open(usage_file, 'w') as f:
                await f.write(json.dumps(usage_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save usage: {e}")
    
    async def _load_alerts(self) -> None:
        """Load alerts from file"""
        import os
        filepath = os.path.join(self.data_dir, 'alerts.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    alerts_data = json.loads(data)
                    
                    for budget_id, budget_alerts in alerts_data.items():
                        self.alerts[budget_id] = []
                        for alert_data in budget_alerts:
                            alert = BudgetAlert(
                                budget_id=alert_data['budget_id'],
                                threshold_percentage=alert_data['threshold_percentage'],
                                alert_type=alert_data['alert_type'],
                                message=alert_data['message'],
                                is_active=alert_data.get('is_active', True),
                                created_at=datetime.fromisoformat(alert_data['created_at'])
                            )
                            self.alerts[budget_id].append(alert)
            else:
                # Create default file
                await self._save_alerts()
        except Exception as e:
            self.logger.error(f"Failed to load alerts: {e}")
            # Create default file on error
            await self._save_alerts()
    
    async def _save_alerts(self) -> None:
        """Save alerts to file"""
        try:
            alerts_file = f"{self.data_dir}/alerts.json"
            alerts_data = {}
            for budget_id, budget_alerts in self.alerts.items():
                alerts_data[budget_id] = []
                for alert in budget_alerts:
                    alert_dict = asdict(alert)
                    alert_dict['created_at'] = alert_dict['created_at'].isoformat()
                    alerts_data[budget_id].append(alert_dict)
            
            async with aiofiles.open(alerts_file, 'w') as f:
                await f.write(json.dumps(alerts_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")
    
    async def _create_default_alerts(self, budget_id: str) -> None:
        """Create default alerts for a new budget"""
        for alert_type, threshold in self.default_thresholds.items():
            await self.set_alert_threshold(budget_id, alert_type, threshold)
    
    async def _get_current_usage(self, budget_id: str) -> BudgetUsage:
        """Get or create current usage record for a budget"""
        if budget_id in self.usage:
            return self.usage[budget_id]
        
        budget = self.budgets[budget_id]
        period_start, period_end = self._calculate_period_dates(budget)
        
        usage = BudgetUsage(
            budget_id=budget_id,
            period_start=period_start,
            period_end=period_end,
            allocated_amount=budget.amount,
            used_amount=Decimal('0'),
            remaining_amount=budget.amount,
            usage_percentage=0.0,
            status=BudgetStatus.UNDER_BUDGET,
            last_updated=datetime.utcnow()
        )
        
        return usage
    
    def _calculate_period_dates(self, budget: Budget) -> tuple[datetime, datetime]:
        """Calculate period start and end dates"""
        now = datetime.utcnow()
        
        if budget.period == BudgetPeriod.DAILY:
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif budget.period == BudgetPeriod.WEEKLY:
            days_since_monday = now.weekday()
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            period_end = period_start + timedelta(weeks=1)
        elif budget.period == BudgetPeriod.MONTHLY:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.QUARTERLY:
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            period_start = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            if quarter_start_month == 10:
                period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                period_end = now.replace(month=quarter_start_month + 3, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # YEARLY
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return period_start, period_end
    
    def _calculate_status(self, usage_percentage: float) -> BudgetStatus:
        """Calculate budget status based on usage percentage"""
        if usage_percentage >= 1.0:
            return BudgetStatus.CRITICAL
        elif usage_percentage >= 0.9:
            return BudgetStatus.OVER_BUDGET
        elif usage_percentage >= 0.7:
            return BudgetStatus.NEAR_LIMIT
        else:
            return BudgetStatus.UNDER_BUDGET
    
    async def _check_alerts(self, budget_id: str, usage: BudgetUsage) -> None:
        """Check and trigger alerts for budget usage"""
        if budget_id not in self.alerts:
            return
        
        for alert in self.alerts[budget_id]:
            if not alert.is_active:
                continue
            
            if usage.usage_percentage >= alert.threshold_percentage:
                self.logger.warning(f"Budget alert triggered: {alert.message} for budget {budget_id}")
                # Here you could integrate with the alert system to send notifications 