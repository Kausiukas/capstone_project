"""
Inspector Alerting System Module (Task 4.2.2)

This module provides alert generation and management capabilities for the Inspector system.
It handles alert rules, notifications, and alert lifecycle management.
"""

import asyncio
import json
import logging
import smtplib
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union
import threading
from collections import defaultdict, deque
import queue
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertStatus(Enum):
    """Alert status values"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Notification delivery types"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    CONSOLE = "console"
    SMS = "sms"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    condition: str  # JSONPath-like expression
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    max_alerts_per_hour: int = 10
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["console"]


@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    timestamp: datetime
    severity: AlertSeverity
    status: AlertStatus
    message: str
    source: str
    metrics: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class NotificationConfig:
    """Notification configuration"""
    channel_id: str
    notification_type: NotificationType
    enabled: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class EmailConfig:
    """Email notification configuration"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    to_emails: List[str]
    use_tls: bool = True


@dataclass
class WebhookConfig:
    """Webhook notification configuration"""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = None
    timeout: int = 30
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


@dataclass
class SlackConfig:
    """Slack notification configuration"""
    webhook_url: str
    channel: str = "#alerts"
    username: str = "Inspector Alert Bot"
    icon_emoji: str = ":warning:"


class InspectorAlertingSystem:
    """Alerting system for Inspector"""
    
    def __init__(self, data_dir: str = "data/alerts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Alert management
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        
        # Alert tracking
        self.alert_counts = defaultdict(int)  # rule_id -> count
        self.last_alert_times = defaultdict(float)  # rule_id -> timestamp
        self.alert_history = deque(maxlen=1000)
        
        # Notification queue
        self.notification_queue = queue.Queue()
        self.notification_thread = None
        self.is_running = False
        
        # Load existing data
        self._load_alert_data()
        
        logger.info("Inspector Alerting System initialized")
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add a new alert rule"""
        try:
            self.alert_rules[rule.rule_id] = rule
            self._save_alert_rules()
            logger.info(f"Added alert rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add alert rule: {e}")
            return False
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self._save_alert_rules()
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False
    
    def add_notification_config(self, config: NotificationConfig) -> bool:
        """Add a notification configuration"""
        try:
            self.notification_configs[config.channel_id] = config
            self._save_notification_configs()
            logger.info(f"Added notification config: {config.channel_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add notification config: {e}")
            return False
    
    def remove_notification_config(self, channel_id: str) -> bool:
        """Remove a notification configuration"""
        if channel_id in self.notification_configs:
            del self.notification_configs[channel_id]
            self._save_notification_configs()
            logger.info(f"Removed notification config: {channel_id}")
            return True
        return False
    
    def process_monitoring_event(self, event: Any) -> List[Alert]:
        """Process a monitoring event and generate alerts"""
        alerts = []
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if self._is_in_cooldown(rule):
                continue
            
            # Check rate limiting
            if self._is_rate_limited(rule):
                continue
            
            # Evaluate rule condition
            if self._evaluate_condition(rule, event):
                alert = self._create_alert(rule, event)
                if alert:
                    alerts.append(alert)
                    self._track_alert(rule)
        
        return alerts
    
    def create_alert(self, rule_id: str, message: str, source: str, 
                    metrics: Dict[str, Any] = None, tags: List[str] = None) -> Optional[Alert]:
        """Manually create an alert"""
        if rule_id not in self.alert_rules:
            logger.error(f"Alert rule not found: {rule_id}")
            return None
        
        rule = self.alert_rules[rule_id]
        
        # Check cooldown and rate limiting
        if self._is_in_cooldown(rule) or self._is_rate_limited(rule):
            return None
        
        alert = Alert(
            alert_id=f"alert_{int(time.time())}_{rule_id}",
            rule_id=rule_id,
            timestamp=datetime.now(),
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=message,
            source=source,
            metrics=metrics,
            tags=tags or [],
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        self.alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        self._track_alert(rule)
        self._save_alerts()
        
        # Queue notification (non-blocking)
        try:
            self.notification_queue.put_nowait(alert)
        except queue.Full:
            logger.warning("Notification queue is full, dropping alert")
        
        logger.info(f"Created alert: {alert.alert_id} - {message}")
        return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            self._save_alerts()
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            self._save_alerts()
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() 
                if alert.status == AlertStatus.ACTIVE]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts filtered by severity"""
        return [alert for alert in self.alerts.values() 
                if alert.severity == severity]
    
    def get_alerts_by_source(self, source: str) -> List[Alert]:
        """Get alerts filtered by source"""
        return [alert for alert in self.alerts.values() 
                if alert.source == source]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        active_alerts = self.get_active_alerts()
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "acknowledged_alerts": len([a for a in self.alerts.values() 
                                     if a.status == AlertStatus.ACKNOWLEDGED]),
            "resolved_alerts": len([a for a in self.alerts.values() 
                                  if a.status == AlertStatus.RESOLVED]),
            "alerts_by_severity": {
                severity.value: len(self.get_alerts_by_severity(severity))
                for severity in AlertSeverity
            },
            "alert_rules_count": len(self.alert_rules),
            "notification_channels_count": len(self.notification_configs)
        }
    
    def start_notification_processor(self) -> bool:
        """Start the notification processing thread"""
        if self.is_running:
            logger.warning("Notification processor is already running")
            return False
        
        self.is_running = True
        self.notification_thread = threading.Thread(
            target=self._notification_processor_loop, daemon=True)
        self.notification_thread.start()
        
        logger.info("Notification processor started")
        return True
    
    def stop_notification_processor(self) -> bool:
        """Stop the notification processing thread"""
        if not self.is_running:
            logger.warning("Notification processor is not running")
            return False
        
        self.is_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=5.0)
        
        logger.info("Notification processor stopped")
        return True
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Check if rule is in cooldown period"""
        last_time = self.last_alert_times.get(rule.rule_id, 0)
        cooldown_seconds = rule.cooldown_minutes * 60
        return time.time() - last_time < cooldown_seconds
    
    def _is_rate_limited(self, rule: AlertRule) -> bool:
        """Check if rule is rate limited"""
        count = self.alert_counts.get(rule.rule_id, 0)
        return count >= rule.max_alerts_per_hour
    
    def _evaluate_condition(self, rule: AlertRule, event: Any) -> bool:
        """Evaluate alert rule condition against event"""
        try:
            # Simple condition evaluation (can be extended with JSONPath)
            if hasattr(event, 'alert_level'):
                # For MonitoringEvent objects
                if rule.condition == "alert_level == 'critical'":
                    return event.alert_level.value == 'critical'
                elif rule.condition == "alert_level == 'error'":
                    return event.alert_level.value == 'error'
                elif rule.condition == "alert_level == 'warning'":
                    return event.alert_level.value == 'warning'
            
            # For metrics-based conditions
            if hasattr(event, 'metrics') and event.metrics:
                for metric_name, threshold in event.metrics.items():
                    if f"{metric_name} > {threshold}" in rule.condition:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _create_alert(self, rule: AlertRule, event: Any) -> Optional[Alert]:
        """Create an alert from a rule and event"""
        try:
            alert = Alert(
                alert_id=f"alert_{int(time.time())}_{rule.rule_id}",
                rule_id=rule.rule_id,
                timestamp=datetime.now(),
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                message=getattr(event, 'message', f"Alert triggered by rule: {rule.name}"),
                source=getattr(event, 'source', 'unknown'),
                metrics=getattr(event, 'metrics', {}),
                tags=getattr(event, 'tags', []),
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            self.alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self._save_alerts()
            
            # Queue notification (non-blocking)
            try:
                self.notification_queue.put_nowait(alert)
            except queue.Full:
                logger.warning("Notification queue is full, dropping alert")
            
            return alert
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return None
    
    def _track_alert(self, rule: AlertRule) -> None:
        """Track alert for rate limiting"""
        self.alert_counts[rule.rule_id] += 1
        self.last_alert_times[rule.rule_id] = time.time()
    
    def _notification_processor_loop(self) -> None:
        """Main notification processing loop"""
        logger.info("Notification processor loop started")
        
        while self.is_running:
            try:
                # Process notifications in batches
                notifications = []
                try:
                    while len(notifications) < 10:
                        alert = self.notification_queue.get_nowait()
                        notifications.append(alert)
                except queue.Empty:
                    pass
                
                for alert in notifications:
                    self._send_notifications(alert)
                
                time.sleep(1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in notification processor: {e}")
                time.sleep(5)
    
    def _send_notifications(self, alert: Alert) -> None:
        """Send notifications for an alert"""
        rule = self.alert_rules.get(alert.rule_id)
        if not rule:
            return
        
        for channel_id in rule.notification_channels:
            config = self.notification_configs.get(channel_id)
            if not config or not config.enabled:
                continue
            
            try:
                if config.notification_type == NotificationType.EMAIL:
                    self._send_email_notification(config, alert)
                elif config.notification_type == NotificationType.WEBHOOK:
                    self._send_webhook_notification(config, alert)
                elif config.notification_type == NotificationType.SLACK:
                    self._send_slack_notification(config, alert)
                elif config.notification_type == NotificationType.CONSOLE:
                    self._send_console_notification(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel_id}: {e}")
    
    def _send_email_notification(self, config: NotificationConfig, alert: Alert) -> None:
        """Send email notification"""
        try:
            email_config = EmailConfig(**config.config)
            
            msg = MIMEMultipart()
            msg['From'] = email_config.from_email
            msg['To'] = ', '.join(email_config.to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] Inspector Alert: {alert.message}"
            
            body = f"""
Alert Details:
- ID: {alert.alert_id}
- Severity: {alert.severity.value}
- Source: {alert.source}
- Message: {alert.message}
- Timestamp: {alert.timestamp}
- Metrics: {alert.metrics}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
            if email_config.use_tls:
                server.starttls()
            server.login(email_config.username, email_config.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_webhook_notification(self, config: NotificationConfig, alert: Alert) -> None:
        """Send webhook notification"""
        try:
            webhook_config = WebhookConfig(**config.config)
            
            payload = {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "metrics": alert.metrics
            }
            
            response = requests.request(
                method=webhook_config.method,
                url=webhook_config.url,
                headers=webhook_config.headers,
                json=payload,
                timeout=webhook_config.timeout
            )
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    def _send_slack_notification(self, config: NotificationConfig, alert: Alert) -> None:
        """Send Slack notification"""
        try:
            slack_config = SlackConfig(**config.config)
            
            payload = {
                "channel": slack_config.channel,
                "username": slack_config.username,
                "icon_emoji": slack_config.icon_emoji,
                "text": f"*[{alert.severity.value.upper()}] Inspector Alert*\n{alert.message}",
                "attachments": [{
                    "fields": [
                        {"title": "Alert ID", "value": alert.alert_id, "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": True}
                    ]
                }]
            }
            
            response = requests.post(slack_config.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def _send_console_notification(self, alert: Alert) -> None:
        """Send console notification"""
        print(f"[{alert.severity.value.upper()}] {alert.message}")
        print(f"  Alert ID: {alert.alert_id}")
        print(f"  Source: {alert.source}")
        print(f"  Timestamp: {alert.timestamp}")
        if alert.metrics:
            print(f"  Metrics: {alert.metrics}")
        print()
    
    def _save_alerts(self) -> None:
        """Save alerts to disk"""
        try:
            alerts_file = self.data_dir / "alerts.json"
            alerts_data = []
            
            for alert in self.alerts.values():
                alert_dict = asdict(alert)
                alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
                alert_dict['severity'] = alert_dict['severity'].value
                alert_dict['status'] = alert_dict['status'].value
                if alert_dict['acknowledged_at']:
                    alert_dict['acknowledged_at'] = alert_dict['acknowledged_at'].isoformat()
                if alert_dict['resolved_at']:
                    alert_dict['resolved_at'] = alert_dict['resolved_at'].isoformat()
                if alert_dict['expires_at']:
                    alert_dict['expires_at'] = alert_dict['expires_at'].isoformat()
                alerts_data.append(alert_dict)
            
            with open(alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def _save_alert_rules(self) -> None:
        """Save alert rules to disk"""
        try:
            rules_file = self.data_dir / "alert_rules.json"
            rules_data = []
            
            for rule in self.alert_rules.values():
                rule_dict = asdict(rule)
                rule_dict['severity'] = rule_dict['severity'].value
                rules_data.append(rule_dict)
            
            with open(rules_file, 'w') as f:
                json.dump(rules_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alert rules: {e}")
    
    def _save_notification_configs(self) -> None:
        """Save notification configurations to disk"""
        try:
            configs_file = self.data_dir / "notification_configs.json"
            configs_data = []
            
            for config in self.notification_configs.values():
                config_dict = asdict(config)
                config_dict['notification_type'] = config_dict['notification_type'].value
                configs_data.append(config_dict)
            
            with open(configs_file, 'w') as f:
                json.dump(configs_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save notification configs: {e}")
    
    def _load_alert_data(self) -> None:
        """Load alert data from disk"""
        try:
            # Load alerts
            alerts_file = self.data_dir / "alerts.json"
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                
                for alert_data in alerts_data:
                    alert_data['timestamp'] = datetime.fromisoformat(alert_data['timestamp'])
                    alert_data['severity'] = AlertSeverity(alert_data['severity'])
                    alert_data['status'] = AlertStatus(alert_data['status'])
                    if alert_data['acknowledged_at']:
                        alert_data['acknowledged_at'] = datetime.fromisoformat(alert_data['acknowledged_at'])
                    if alert_data['resolved_at']:
                        alert_data['resolved_at'] = datetime.fromisoformat(alert_data['resolved_at'])
                    if alert_data['expires_at']:
                        alert_data['expires_at'] = datetime.fromisoformat(alert_data['expires_at'])
                    self.alerts[alert_data['alert_id']] = Alert(**alert_data)
            
            # Load alert rules
            rules_file = self.data_dir / "alert_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                
                for rule_data in rules_data:
                    rule_data['severity'] = AlertSeverity(rule_data['severity'])
                    self.alert_rules[rule_data['rule_id']] = AlertRule(**rule_data)
            
            # Load notification configs
            configs_file = self.data_dir / "notification_configs.json"
            if configs_file.exists():
                with open(configs_file, 'r') as f:
                    configs_data = json.load(f)
                
                for config_data in configs_data:
                    config_data['notification_type'] = NotificationType(config_data['notification_type'])
                    self.notification_configs[config_data['channel_id']] = NotificationConfig(**config_data)
                    
        except Exception as e:
            logger.error(f"Failed to load alert data: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Create alerting system
    alerting_system = InspectorAlertingSystem()
    
    # Add notification config
    console_config = NotificationConfig(
        channel_id="console",
        notification_type=NotificationType.CONSOLE
    )
    alerting_system.add_notification_config(console_config)
    
    # Add alert rules
    cpu_rule = AlertRule(
        rule_id="high_cpu",
        name="High CPU Usage",
        description="Alert when CPU usage exceeds threshold",
        condition="cpu_percent > 80",
        severity=AlertSeverity.HIGH,
        notification_channels=["console"]
    )
    alerting_system.add_alert_rule(cpu_rule)
    
    memory_rule = AlertRule(
        rule_id="high_memory",
        name="High Memory Usage",
        description="Alert when memory usage exceeds threshold",
        condition="memory_percent > 85",
        severity=AlertSeverity.CRITICAL,
        notification_channels=["console"]
    )
    alerting_system.add_alert_rule(memory_rule)
    
    # Start notification processor
    alerting_system.start_notification_processor()
    
    # Test creating alerts
    alerting_system.create_alert(
        rule_id="high_cpu",
        message="CPU usage is at 90%",
        source="system_monitor",
        metrics={"cpu_percent": 90.0}
    )
    
    alerting_system.create_alert(
        rule_id="high_memory",
        message="Memory usage is at 95%",
        source="system_monitor",
        metrics={"memory_percent": 95.0}
    )
    
    # Get summary
    summary = alerting_system.get_alert_summary()
    print("Alert Summary:", summary)
    
    # Stop notification processor
    alerting_system.stop_notification_processor() 