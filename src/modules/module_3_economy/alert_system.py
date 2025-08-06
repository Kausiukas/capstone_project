"""
Alert System for Module 3: ECONOMY

This module handles cost alerts and notifications for the system.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum

import aiofiles


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status types"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertChannel(Enum):
    """Alert notification channels"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TELEGRAM = "telegram"
    CONSOLE = "console"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    name: str
    description: str
    condition: str  # JSON string representing the condition
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int = 30
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    data: Dict[str, Any]
    triggered_at: datetime = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None

    def __post_init__(self):
        if self.triggered_at is None:
            self.triggered_at = datetime.now(timezone.utc)


@dataclass
class NotificationConfig:
    """Notification configuration"""
    channel: AlertChannel
    config: Dict[str, Any]
    is_active: bool = True
    rate_limit_per_hour: int = 10


class AlertSystem:
    """
    Manages cost alerts and notifications for the system.
    """
    
    def __init__(self, data_dir: str = "data/alerts"):
        self.data_dir = data_dir
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.notifications: Dict[AlertChannel, NotificationConfig] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Default alert rules
        self.default_rules = [
            {
                "name": "High Cost Threshold",
                "description": "Alert when daily cost exceeds threshold",
                "condition": '{"metric": "daily_cost", "operator": ">", "value": 100}',
                "severity": AlertSeverity.WARNING,
                "channels": [AlertChannel.LOG, AlertChannel.CONSOLE]
            },
            {
                "name": "Cost Spike Detection",
                "description": "Alert when cost increases by more than 50%",
                "condition": '{"metric": "cost_change_percentage", "operator": ">", "value": 50}',
                "severity": AlertSeverity.ERROR,
                "channels": [AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL]
            },
            {
                "name": "Budget Exceeded",
                "description": "Alert when budget limit is exceeded",
                "condition": '{"metric": "budget_usage_percentage", "operator": ">=", "value": 100}',
                "severity": AlertSeverity.CRITICAL,
                "channels": [AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL, AlertChannel.WEBHOOK]
            }
        ]
        
        # Notification handlers
        self.notification_handlers: Dict[AlertChannel, Callable] = {
            AlertChannel.LOG: self._send_log_notification,
            AlertChannel.CONSOLE: self._send_console_notification,
            AlertChannel.EMAIL: self._send_email_notification,
            AlertChannel.WEBHOOK: self._send_webhook_notification,
            AlertChannel.SLACK: self._send_slack_notification,
            AlertChannel.TELEGRAM: self._send_telegram_notification
        }
    
    async def initialize(self) -> None:
        """Initialize the alert system"""
        self.logger.info("Initializing alert system...")
        
        try:
            await self._ensure_data_dir()
            await self._load_rules()
            await self._load_alerts()
            await self._load_notifications()
            
            # Create default rules if none exist
            if not self.rules:
                await self._create_default_rules()
            
            self.logger.info("Alert system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize alert system: {e}")
            raise
    
    async def create_alert_rule(
        self,
        name: str,
        description: str,
        condition: Dict[str, Any],
        severity: AlertSeverity,
        channels: List[AlertChannel],
        cooldown_minutes: int = 30
    ) -> str:
        """Create a new alert rule"""
        async with self._lock:
            try:
                rule_id = f"rule_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
                
                rule = AlertRule(
                    id=rule_id,
                    name=name,
                    description=description,
                    condition=json.dumps(condition),
                    severity=severity,
                    channels=channels,
                    cooldown_minutes=cooldown_minutes
                )
                
                self.rules[rule_id] = rule
                await self._save_rules()
                
                self.logger.info(f"Created alert rule: {rule_id} - {name}")
                return rule_id
                
            except Exception as e:
                self.logger.error(f"Failed to create alert rule: {e}")
                raise
    
    async def get_alert_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        return self.rules.get(rule_id)
    
    async def list_alert_rules(self, active_only: bool = True) -> List[AlertRule]:
        """List alert rules"""
        rules = list(self.rules.values())
        if active_only:
            rules = [r for r in rules if r.is_active]
        return rules
    
    async def update_alert_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        condition: Optional[Dict[str, Any]] = None,
        severity: Optional[AlertSeverity] = None,
        channels: Optional[List[AlertChannel]] = None,
        cooldown_minutes: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """Update alert rule"""
        async with self._lock:
            try:
                if rule_id not in self.rules:
                    return False
                
                rule = self.rules[rule_id]
                
                if name is not None:
                    rule.name = name
                if description is not None:
                    rule.description = description
                if condition is not None:
                    rule.condition = json.dumps(condition)
                if severity is not None:
                    rule.severity = severity
                if channels is not None:
                    rule.channels = channels
                if cooldown_minutes is not None:
                    rule.cooldown_minutes = cooldown_minutes
                if is_active is not None:
                    rule.is_active = is_active
                
                rule.updated_at = datetime.now(timezone.utc)
                await self._save_rules()
                
                self.logger.info(f"Updated alert rule: {rule_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update alert rule: {e}")
                return False
    
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete alert rule"""
        async with self._lock:
            try:
                if rule_id not in self.rules:
                    return False
                
                del self.rules[rule_id]
                await self._save_rules()
                
                self.logger.info(f"Deleted alert rule: {rule_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete alert rule: {e}")
                return False
    
    async def check_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """Check metrics against alert rules and trigger alerts"""
        async with self._lock:
            try:
                triggered_alerts = []
                
                for rule in self.rules.values():
                    if not rule.is_active:
                        continue
                    
                    # Check if rule should be triggered
                    if await self._should_trigger_alert(rule, metrics):
                        alert_id = await self._create_alert(rule, metrics)
                        if alert_id:
                            triggered_alerts.append(alert_id)
                
                return triggered_alerts
                
            except Exception as e:
                self.logger.error(f"Failed to check alerts: {e}")
                raise
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        return self.alerts.get(alert_id)
    
    async def list_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """List alerts with optional filtering"""
        alerts = list(self.alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if status:
            alerts = [a for a in alerts if a.status == status]
        if start_date:
            alerts = [a for a in alerts if a.triggered_at >= start_date]
        if end_date:
            alerts = [a for a in alerts if a.triggered_at <= end_date]
        
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        async with self._lock:
            try:
                if alert_id not in self.alerts:
                    return False
                
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now(timezone.utc)
                alert.acknowledged_by = acknowledged_by
                
                await self._save_alerts()
                
                self.logger.info(f"Acknowledged alert: {alert_id} by {acknowledged_by}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to acknowledge alert: {e}")
                return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert"""
        async with self._lock:
            try:
                if alert_id not in self.alerts:
                    return False
                
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now(timezone.utc)
                alert.resolved_by = resolved_by
                
                await self._save_alerts()
                
                self.logger.info(f"Resolved alert: {alert_id} by {resolved_by}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to resolve alert: {e}")
                return False
    
    async def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss an alert"""
        async with self._lock:
            try:
                if alert_id not in self.alerts:
                    return False
                
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.DISMISSED
                
                await self._save_alerts()
                
                self.logger.info(f"Dismissed alert: {alert_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to dismiss alert: {e}")
                return False
    
    async def configure_notification(
        self,
        channel: AlertChannel,
        config: Dict[str, Any],
        is_active: bool = True,
        rate_limit_per_hour: int = 10
    ) -> bool:
        """Configure notification channel"""
        async with self._lock:
            try:
                notification_config = NotificationConfig(
                    channel=channel,
                    config=config,
                    is_active=is_active,
                    rate_limit_per_hour=rate_limit_per_hour
                )
                
                self.notifications[channel] = notification_config
                await self._save_notifications()
                
                self.logger.info(f"Configured notification channel: {channel.value}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to configure notification: {e}")
                return False
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])
        acknowledged_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACKNOWLEDGED])
        resolved_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED])
        
        # Count by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                a for a in self.alerts.values() if a.severity == severity
            ])
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": resolved_alerts,
            "severity_breakdown": severity_counts,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.is_active])
        }
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'rules.json': [],
            'alerts.json': [],
            'notifications.json': {}
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_rules(self) -> None:
        """Load alert rules from file"""
        filepath = os.path.join(self.data_dir, 'rules.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    rules_data = json.loads(data)
                    
                    for rule_data in rules_data:
                        rule = AlertRule(
                            id=rule_data['id'],
                            name=rule_data['name'],
                            description=rule_data['description'],
                            condition=rule_data['condition'],
                            severity=AlertSeverity(rule_data['severity']),
                            channels=[AlertChannel(ch) for ch in rule_data['channels']],
                            cooldown_minutes=rule_data.get('cooldown_minutes', 30),
                            is_active=rule_data.get('is_active', True),
                            created_at=datetime.fromisoformat(rule_data['created_at']),
                            updated_at=datetime.fromisoformat(rule_data['updated_at'])
                        )
                        self.rules[rule.id] = rule
            else:
                # Create default file
                await self._save_rules()
        except Exception as e:
            self.logger.error(f"Failed to load alert rules: {e}")
            # Create default file on error
            await self._save_rules()

    async def _save_rules(self) -> None:
        """Save alert rules to file"""
        try:
            rules_file = f"{self.data_dir}/rules.json"
            rules_data = []
            for rule in self.rules.values():
                rule_dict = asdict(rule)
                rule_dict['severity'] = rule_dict['severity'].value
                rule_dict['channels'] = [c.value for c in rule_dict['channels']]
                rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
                rules_data.append(rule_dict)
            
            async with aiofiles.open(rules_file, 'w') as f:
                await f.write(json.dumps(rules_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save rules: {e}")
    
    async def _load_alerts(self) -> None:
        """Load alerts from file"""
        filepath = os.path.join(self.data_dir, 'alerts.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    alerts_data = json.loads(data)
                    
                    for alert_data in alerts_data:
                        alert = Alert(
                            id=alert_data['id'],
                            rule_id=alert_data['rule_id'],
                            title=alert_data['title'],
                            message=alert_data['message'],
                            severity=AlertSeverity(alert_data['severity']),
                            status=AlertStatus(alert_data['status']),
                            data=alert_data['data'],
                            triggered_at=datetime.fromisoformat(alert_data['triggered_at']),
                            acknowledged_at=datetime.fromisoformat(alert_data['acknowledged_at']) if alert_data.get('acknowledged_at') else None,
                            resolved_at=datetime.fromisoformat(alert_data['resolved_at']) if alert_data.get('resolved_at') else None,
                            acknowledged_by=alert_data.get('acknowledged_by'),
                            resolved_by=alert_data.get('resolved_by')
                        )
                        self.alerts[alert.id] = alert
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
            alerts_data = []
            for alert in self.alerts.values():
                alert_dict = asdict(alert)
                alert_dict['severity'] = alert_dict['severity'].value
                alert_dict['status'] = alert_dict['status'].value
                alert_dict['triggered_at'] = alert_dict['triggered_at'].isoformat()
                if alert_dict['acknowledged_at']:
                    alert_dict['acknowledged_at'] = alert_dict['acknowledged_at'].isoformat()
                if alert_dict['resolved_at']:
                    alert_dict['resolved_at'] = alert_dict['resolved_at'].isoformat()
                alerts_data.append(alert_dict)
            
            async with aiofiles.open(alerts_file, 'w') as f:
                await f.write(json.dumps(alerts_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")
    
    async def _load_notifications(self) -> None:
        """Load notification configurations from file"""
        filepath = os.path.join(self.data_dir, 'notifications.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    notifications_data = json.loads(data)
                    
                    for channel_str, config_data in notifications_data.items():
                        channel = AlertChannel(channel_str)
                        config = NotificationConfig(
                            channel=channel,
                            config=config_data['config'],
                            is_active=config_data.get('is_active', True),
                            rate_limit_per_hour=config_data.get('rate_limit_per_hour', 10)
                        )
                        self.notifications[channel] = config
            else:
                # Create default file
                await self._save_notifications()
        except Exception as e:
            self.logger.error(f"Failed to load notification configurations: {e}")
            # Create default file on error
            await self._save_notifications()

    async def _save_notifications(self) -> None:
        """Save notification configurations to file"""
        try:
            notifications_file = f"{self.data_dir}/notifications.json"
            notifications_data = {}
            for channel, config in self.notifications.items():
                notifications_data[channel.value] = {
                    'config': config.config,
                    'is_active': config.is_active,
                    'rate_limit_per_hour': config.rate_limit_per_hour
                }
            
            async with aiofiles.open(notifications_file, 'w') as f:
                await f.write(json.dumps(notifications_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save notifications: {e}")
    
    async def _create_default_rules(self) -> None:
        """Create default alert rules"""
        for rule_config in self.default_rules:
            await self.create_alert_rule(
                name=rule_config["name"],
                description=rule_config["description"],
                condition=json.loads(rule_config["condition"]),
                severity=rule_config["severity"],
                channels=rule_config["channels"]
            )
    
    async def _should_trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Check if an alert rule should be triggered"""
        try:
            # Check cooldown period
            recent_alerts = [
                a for a in self.alerts.values()
                if a.rule_id == rule.id and a.triggered_at > datetime.now(timezone.utc) - timedelta(minutes=rule.cooldown_minutes)
            ]
            
            if recent_alerts:
                return False
            
            # Evaluate condition
            condition = json.loads(rule.condition)
            metric_value = metrics.get(condition["metric"], 0)
            operator = condition["operator"]
            threshold = condition["value"]
            
            if operator == ">":
                return metric_value > threshold
            elif operator == ">=":
                return metric_value >= threshold
            elif operator == "<":
                return metric_value < threshold
            elif operator == "<=":
                return metric_value <= threshold
            elif operator == "==":
                return metric_value == threshold
            elif operator == "!=":
                return metric_value != threshold
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to evaluate alert condition: {e}")
            return False
    
    async def _create_alert(self, rule: AlertRule, metrics: Dict[str, Any]) -> Optional[str]:
        """Create a new alert"""
        try:
            alert_id = f"alert_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{rule.id}"
            
            # Generate alert message
            condition = json.loads(rule.condition)
            metric_value = metrics.get(condition["metric"], 0)
            threshold = condition["value"]
            
            title = f"{rule.name} - {rule.severity.value.upper()}"
            message = f"{rule.description}. Current value: {metric_value}, Threshold: {threshold}"
            
            alert = Alert(
                id=alert_id,
                rule_id=rule.id,
                title=title,
                message=message,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                data=metrics
            )
            
            self.alerts[alert_id] = alert
            await self._save_alerts()
            
            # Send notifications
            await self._send_notifications(alert, rule.channels)
            
            self.logger.info(f"Created alert: {alert_id}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            return None
    
    async def _send_notifications(self, alert: Alert, channels: List[AlertChannel]) -> None:
        """Send notifications for an alert"""
        for channel in channels:
            try:
                if channel in self.notification_handlers:
                    await self.notification_handlers[channel](alert)
            except Exception as e:
                self.logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _send_log_notification(self, alert: Alert) -> None:
        """Send log notification"""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        self.logger.log(log_level, f"ALERT: {alert.title} - {alert.message}")
    
    async def _send_console_notification(self, alert: Alert) -> None:
        """Send console notification"""
        print(f"\n🚨 ALERT [{alert.severity.value.upper()}]: {alert.title}")
        print(f"   {alert.message}")
        print(f"   Triggered: {alert.triggered_at}")
        print()
    
    async def _send_email_notification(self, alert: Alert) -> None:
        """Send email notification"""
        # This would integrate with an email service
        self.logger.info(f"Email notification would be sent for alert: {alert.id}")
    
    async def _send_webhook_notification(self, alert: Alert) -> None:
        """Send webhook notification"""
        # This would send HTTP POST to configured webhook
        self.logger.info(f"Webhook notification would be sent for alert: {alert.id}")
    
    async def _send_slack_notification(self, alert: Alert) -> None:
        """Send Slack notification"""
        # This would integrate with Slack API
        self.logger.info(f"Slack notification would be sent for alert: {alert.id}")
    
    async def _send_telegram_notification(self, alert: Alert) -> None:
        """Send Telegram notification"""
        # This would integrate with Telegram Bot API
        self.logger.info(f"Telegram notification would be sent for alert: {alert.id}") 