"""
Connection Monitor for Module 4: LangflowConnector

This module handles Langflow connection monitoring and health checks.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum

import aiofiles


class ConnectionStatus(Enum):
    """Connection status types"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    TIMEOUT = "timeout"


class HealthStatus(Enum):
    """Health status types"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MonitorType(Enum):
    """Monitor types"""
    PING = "ping"
    HTTP = "http"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"


@dataclass
class ConnectionMetrics:
    """Connection metrics"""
    timestamp: datetime
    status: ConnectionStatus
    response_time: float  # in milliseconds
    latency: float  # in milliseconds
    throughput: float  # bytes per second
    error_count: int
    success_count: int
    uptime_percentage: float


@dataclass
class HealthCheck:
    """Health check configuration"""
    id: str
    name: str
    monitor_type: MonitorType
    target: str  # URL, endpoint, or custom identifier
    interval: int  # seconds
    timeout: int  # seconds
    retries: int
    threshold: float  # failure threshold
    is_active: bool = True
    config: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
        if self.config is None:
            self.config = {}


@dataclass
class HealthCheckResult:
    """Health check result"""
    check_id: str
    timestamp: datetime
    status: HealthStatus
    response_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class ConnectionAlert:
    """Connection alert"""
    id: str
    title: str
    message: str
    severity: str  # "info", "warning", "error", "critical"
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConnectionMonitor:
    """
    Monitors Langflow connection health and status.
    """
    
    def __init__(self, data_dir: str = "data/monitoring"):
        self.data_dir = data_dir
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results: Dict[str, List[HealthCheckResult]] = {}
        self.connection_metrics: List[ConnectionMetrics] = []
        self.alerts: Dict[str, ConnectionAlert] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        
        # Default health checks
        self.default_checks = [
            {
                "name": "Langflow API Health",
                "monitor_type": MonitorType.HTTP,
                "target": "http://localhost:3000/api/v1/health",
                "interval": 30,
                "timeout": 10,
                "retries": 3,
                "threshold": 0.8
            },
            {
                "name": "WebSocket Connection",
                "monitor_type": MonitorType.WEBSOCKET,
                "target": "ws://localhost:3000/ws",
                "interval": 60,
                "timeout": 15,
                "retries": 2,
                "threshold": 0.9
            },
            {
                "name": "Database Connection",
                "monitor_type": MonitorType.CUSTOM,
                "target": "database_connection",
                "interval": 120,
                "timeout": 20,
                "retries": 2,
                "threshold": 0.95
            }
        ]
        
        # Alert thresholds
        self.alert_thresholds = {
            "response_time": 5000,  # 5 seconds
            "error_rate": 0.1,  # 10%
            "uptime": 0.95  # 95%
        }
    
    async def initialize(self) -> None:
        """Initialize the connection monitor"""
        self.logger.info("Initializing connection monitor...")
        
        try:
            await self._ensure_data_dir()
            await self._load_health_checks()
            await self._load_check_results()
            await self._load_alerts()
            
            # Create default health checks if none exist
            if not self.health_checks:
                await self._create_default_checks()
            
            self.logger.info("Connection monitor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection monitor: {e}")
            raise
    
    async def start_monitoring(self) -> None:
        """Start connection monitoring"""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started connection monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop connection monitoring"""
        if not self._is_monitoring:
            return
        
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped connection monitoring")
    
    async def create_health_check(
        self,
        name: str,
        monitor_type: MonitorType,
        target: str,
        interval: int,
        timeout: int,
        retries: int,
        threshold: float,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new health check"""
        async with self._lock:
            try:
                check_id = f"check_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
                
                health_check = HealthCheck(
                    id=check_id,
                    name=name,
                    monitor_type=monitor_type,
                    target=target,
                    interval=interval,
                    timeout=timeout,
                    retries=retries,
                    threshold=threshold,
                    config=config or {}
                )
                
                self.health_checks[check_id] = health_check
                self.check_results[check_id] = []
                await self._save_health_checks()
                
                self.logger.info(f"Created health check: {check_id} - {name}")
                return check_id
                
            except Exception as e:
                self.logger.error(f"Failed to create health check: {e}")
                raise
    
    async def get_health_check(self, check_id: str) -> Optional[HealthCheck]:
        """Get health check by ID"""
        return self.health_checks.get(check_id)
    
    async def list_health_checks(self, active_only: bool = True) -> List[HealthCheck]:
        """List health checks"""
        checks = list(self.health_checks.values())
        if active_only:
            checks = [c for c in checks if c.is_active]
        return checks
    
    async def update_health_check(
        self,
        check_id: str,
        name: Optional[str] = None,
        monitor_type: Optional[MonitorType] = None,
        target: Optional[str] = None,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        threshold: Optional[float] = None,
        is_active: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update health check"""
        async with self._lock:
            try:
                if check_id not in self.health_checks:
                    return False
                
                check = self.health_checks[check_id]
                
                if name is not None:
                    check.name = name
                if monitor_type is not None:
                    check.monitor_type = monitor_type
                if target is not None:
                    check.target = target
                if interval is not None:
                    check.interval = interval
                if timeout is not None:
                    check.timeout = timeout
                if retries is not None:
                    check.retries = retries
                if threshold is not None:
                    check.threshold = threshold
                if is_active is not None:
                    check.is_active = is_active
                if config is not None:
                    check.config = config
                
                check.updated_at = datetime.now(timezone.utc)
                await self._save_health_checks()
                
                self.logger.info(f"Updated health check: {check_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update health check: {e}")
                return False
    
    async def delete_health_check(self, check_id: str) -> bool:
        """Delete health check"""
        async with self._lock:
            try:
                if check_id not in self.health_checks:
                    return False
                
                del self.health_checks[check_id]
                if check_id in self.check_results:
                    del self.check_results[check_id]
                
                await self._save_health_checks()
                
                self.logger.info(f"Deleted health check: {check_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete health check: {e}")
                return False
    
    async def run_health_check(self, check_id: str) -> HealthCheckResult:
        """Run a single health check"""
        try:
            if check_id not in self.health_checks:
                raise ValueError(f"Health check {check_id} not found")
            
            check = self.health_checks[check_id]
            start_time = datetime.now(timezone.utc)
            
            # Run the health check based on type
            if check.monitor_type == MonitorType.HTTP:
                result = await self._run_http_check(check)
            elif check.monitor_type == MonitorType.WEBSOCKET:
                result = await self._run_websocket_check(check)
            elif check.monitor_type == MonitorType.PING:
                result = await self._run_ping_check(check)
            elif check.monitor_type == MonitorType.CUSTOM:
                result = await self._run_custom_check(check)
            else:
                raise ValueError(f"Unsupported monitor type: {check.monitor_type}")
            
            # Calculate response time
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Create result
            health_result = HealthCheckResult(
                check_id=check_id,
                timestamp=start_time,
                status=result["status"],
                response_time=response_time,
                error_message=result.get("error"),
                details=result.get("details", {})
            )
            
            # Store result
            if check_id not in self.check_results:
                self.check_results[check_id] = []
            
            self.check_results[check_id].append(health_result)
            
            # Keep only recent results (last 100)
            if len(self.check_results[check_id]) > 100:
                self.check_results[check_id] = self.check_results[check_id][-100:]
            
            await self._save_check_results()
            
            # Check for alerts
            await self._check_alerts(check, health_result)
            
            return health_result
            
        except Exception as e:
            self.logger.error(f"Failed to run health check {check_id}: {e}")
            raise
    
    async def get_check_results(
        self,
        check_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[HealthCheckResult]:
        """Get health check results"""
        if check_id not in self.check_results:
            return []
        
        results = self.check_results[check_id]
        
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def get_connection_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ConnectionMetrics]:
        """Get connection metrics"""
        metrics = self.connection_metrics
        
        if start_date:
            metrics = [m for m in metrics if m.timestamp >= start_date]
        if end_date:
            metrics = [m for m in metrics if m.timestamp <= end_date]
        
        return sorted(metrics, key=lambda x: x.timestamp, reverse=True)
    
    async def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        if not self.connection_metrics:
            return ConnectionStatus.UNKNOWN
        
        latest_metric = max(self.connection_metrics, key=lambda x: x.timestamp)
        return latest_metric.status
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health monitoring summary"""
        total_checks = len(self.health_checks)
        active_checks = len([c for c in self.health_checks.values() if c.is_active])
        
        # Calculate overall health
        healthy_checks = 0
        total_results = 0
        
        for check_id, results in self.check_results.items():
            if not results:
                continue
            
            # Get latest result
            latest_result = max(results, key=lambda x: x.timestamp)
            if latest_result.status == HealthStatus.HEALTHY:
                healthy_checks += 1
            total_results += 1
        
        overall_health = healthy_checks / total_results if total_results > 0 else 0
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts.values()
            if alert.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
        ]
        
        return {
            "total_checks": total_checks,
            "active_checks": active_checks,
            "healthy_checks": healthy_checks,
            "overall_health": overall_health,
            "connection_status": await self.get_connection_status(),
            "recent_alerts": len(recent_alerts),
            "last_check": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_alerts(
        self,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ConnectionAlert]:
        """Get connection alerts"""
        alerts = list(self.alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        if start_date:
            alerts = [a for a in alerts if a.timestamp >= start_date]
        if end_date:
            alerts = [a for a in alerts if a.timestamp <= end_date]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        async with self._lock:
            try:
                if alert_id not in self.alerts:
                    return False
                
                alert = self.alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now(timezone.utc)
                
                await self._save_alerts()
                
                self.logger.info(f"Resolved alert: {alert_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to resolve alert: {e}")
                return False
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'health_checks.json': [],
            'check_results.json': [],
            'alerts.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))
    
    async def _load_health_checks(self) -> None:
        """Load health checks from file"""
        try:
            checks_file = f"{self.data_dir}/health_checks.json"
            async with aiofiles.open(checks_file, 'r') as f:
                data = await f.read()
                if data:
                    checks_data = json.loads(data)
                    for check_dict in checks_data:
                        check = HealthCheck(**check_dict)
                        check.monitor_type = MonitorType(check.monitor_type)
                        # Ensure timezone-aware datetime loading
                        created_at_str = check.created_at
                        updated_at_str = check.updated_at
                        if isinstance(created_at_str, str):
                            check.created_at = datetime.fromisoformat(created_at_str)
                            if check.created_at.tzinfo is None:
                                check.created_at = check.created_at.replace(tzinfo=timezone.utc)
                        if isinstance(updated_at_str, str):
                            check.updated_at = datetime.fromisoformat(updated_at_str)
                            if check.updated_at.tzinfo is None:
                                check.updated_at = check.updated_at.replace(tzinfo=timezone.utc)
                        self.health_checks[check.id] = check
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to load health checks: {e}")
    
    async def _save_health_checks(self) -> None:
        """Save health checks to file"""
        try:
            checks_file = f"{self.data_dir}/health_checks.json"
            checks_data = []
            for check in self.health_checks.values():
                check_dict = asdict(check)
                check_dict['monitor_type'] = check_dict['monitor_type'].value
                check_dict['created_at'] = check_dict['created_at'].isoformat()
                check_dict['updated_at'] = check_dict['updated_at'].isoformat()
                checks_data.append(check_dict)
            
            async with aiofiles.open(checks_file, 'w') as f:
                await f.write(json.dumps(checks_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save health checks: {e}")
    
    async def _load_check_results(self) -> None:
        """Load check results from file"""
        try:
            results_file = f"{self.data_dir}/check_results.json"
            async with aiofiles.open(results_file, 'r') as f:
                data = await f.read()
                if data:
                    results_data = json.loads(data)
                    for check_id, results_list in results_data.items():
                        self.check_results[check_id] = []
                        for result_dict in results_list:
                            # Convert string status back to enum
                            if 'status' in result_dict and isinstance(result_dict['status'], str):
                                result_dict['status'] = HealthStatus(result_dict['status'])
                            result = HealthCheckResult(**result_dict)
                            # Ensure timezone-aware datetime loading
                            timestamp_str = result.timestamp
                            if isinstance(timestamp_str, str):
                                result.timestamp = datetime.fromisoformat(timestamp_str)
                                if result.timestamp.tzinfo is None:
                                    result.timestamp = result.timestamp.replace(tzinfo=timezone.utc)
                            self.check_results[check_id].append(result)
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to load check results: {e}")
    
    async def _save_check_results(self) -> None:
        """Save check results to file"""
        try:
            results_file = f"{self.data_dir}/check_results.json"
            results_data = {}
            for check_id, results in self.check_results.items():
                results_data[check_id] = []
                for result in results:
                    result_dict = asdict(result)
                    result_dict['timestamp'] = result_dict['timestamp'].isoformat()
                    # Convert enum to string for JSON serialization
                    result_dict['status'] = result_dict['status'].value
                    results_data[check_id].append(result_dict)
            
            async with aiofiles.open(results_file, 'w') as f:
                await f.write(json.dumps(results_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save check results: {e}")
    
    async def _load_alerts(self) -> None:
        """Load alerts from file"""
        try:
            alerts_file = f"{self.data_dir}/alerts.json"
            async with aiofiles.open(alerts_file, 'r') as f:
                data = await f.read()
                if data:
                    alerts_data = json.loads(data)
                    for alert_dict in alerts_data:
                        alert = ConnectionAlert(**alert_dict)
                        alert.timestamp = datetime.fromisoformat(alert.timestamp)
                        if alert.resolved_at:
                            alert.resolved_at = datetime.fromisoformat(alert.resolved_at)
                        self.alerts[alert.id] = alert
        except FileNotFoundError:
            pass
        except Exception as e:
            self.logger.error(f"Failed to load alerts: {e}")
    
    async def _save_alerts(self) -> None:
        """Save alerts to file"""
        try:
            alerts_file = f"{self.data_dir}/alerts.json"
            alerts_data = []
            for alert in self.alerts.values():
                alert_dict = asdict(alert)
                alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
                if alert_dict['resolved_at']:
                    alert_dict['resolved_at'] = alert_dict['resolved_at'].isoformat()
                # Convert any enum values to strings for JSON serialization
                if 'status' in alert_dict and hasattr(alert_dict['status'], 'value'):
                    alert_dict['status'] = alert_dict['status'].value
                alerts_data.append(alert_dict)
            
            async with aiofiles.open(alerts_file, 'w') as f:
                await f.write(json.dumps(alerts_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")
    
    async def _create_default_checks(self) -> None:
        """Create default health checks"""
        for check_config in self.default_checks:
            await self.create_health_check(
                name=check_config["name"],
                monitor_type=check_config["monitor_type"],
                target=check_config["target"],
                interval=check_config["interval"],
                timeout=check_config["timeout"],
                retries=check_config["retries"],
                threshold=check_config["threshold"]
            )
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self._is_monitoring:
            try:
                # Run all active health checks
                for check in self.health_checks.values():
                    if not check.is_active:
                        continue
                    
                    # Check if it's time to run this check
                    if check.id in self.check_results and self.check_results[check.id]:
                        last_check = max(self.check_results[check.id], key=lambda x: x.timestamp)
                        # Ensure both datetimes are timezone-aware
                        current_time = datetime.now(timezone.utc)
                        last_check_time = last_check.timestamp
                        if last_check_time.tzinfo is None:
                            # If naive, assume UTC
                            last_check_time = last_check_time.replace(tzinfo=timezone.utc)
                        time_since_last = (current_time - last_check_time).total_seconds()
                        
                        if time_since_last < check.interval:
                            continue
                    
                    # Run the health check
                    try:
                        await self.run_health_check(check.id)
                    except Exception as e:
                        self.logger.error(f"Failed to run health check {check.id}: {e}")
                
                # Update connection metrics
                await self._update_connection_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _run_http_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run HTTP health check"""
        import aiohttp
        
        start_time = datetime.now(timezone.utc)
        try:
            timeout = aiohttp.ClientTimeout(total=check.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(check.target) as response:
                    response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    
                    return {
                        "status": HealthStatus.HEALTHY if response.status < 400 else HealthStatus.WARNING,
                        "response_time": response_time,
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "content_length": len(await response.read())
                    }
        except Exception as e:
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return {
                "status": HealthStatus.CRITICAL,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def _run_websocket_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run WebSocket health check"""
        import websockets
        
        start_time = datetime.now(timezone.utc)
        try:
            timeout = check.timeout
            async with websockets.connect(check.target, close_timeout=timeout) as websocket:
                response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                return {
                    "status": HealthStatus.HEALTHY,
                    "response_time": response_time,
                    "connected": True
                }
        except Exception as e:
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return {
                "status": HealthStatus.CRITICAL,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def _run_ping_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run ping health check"""
        import subprocess
        import platform
        
        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", check.target]
            else:
                cmd = ["ping", "-c", "1", check.target]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=check.timeout)
            
            if process.returncode == 0:
                return {
                    "status": HealthStatus.HEALTHY,
                    "details": {"response": stdout.decode()}
                }
            else:
                return {
                    "status": HealthStatus.CRITICAL,
                    "error": stderr.decode(),
                    "details": {"return_code": process.returncode}
                }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "error": str(e),
                "details": {"exception": str(e)}
            }
    
    async def _run_custom_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run custom health check"""
        # This would integrate with custom health check functions
        # For now, return a mock healthy status
        return {
            "status": HealthStatus.HEALTHY,
            "details": {"custom_check": "passed"}
        }
    
    async def _update_connection_metrics(self) -> None:
        """Update connection metrics"""
        try:
            # Calculate metrics based on recent health check results
            recent_results = []
            for results in self.check_results.values():
                recent_results.extend(results[-10:])  # Last 10 results per check
            
            if not recent_results:
                return
            
            # Calculate average response time
            avg_response_time = sum(r.response_time for r in recent_results) / len(recent_results)
            
            # Calculate success rate
            success_count = sum(1 for r in recent_results if r.status == HealthStatus.HEALTHY)
            total_count = len(recent_results)
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            # Create metrics entry
            metrics = ConnectionMetrics(
                timestamp=datetime.now(timezone.utc),
                status=ConnectionStatus.CONNECTED if success_rate > 80 else ConnectionStatus.ERROR,
                response_time=avg_response_time,
                latency=avg_response_time,
                throughput=0.0,  # Would need to track actual data transfer
                error_count=total_count - success_count,
                success_count=success_count,
                uptime_percentage=success_rate
            )
            
            self.connection_metrics.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.connection_metrics) > 1000:
                self.connection_metrics = self.connection_metrics[-1000:]
                
        except Exception as e:
            self.logger.error(f"Failed to update connection metrics: {e}")
    
    async def _check_alerts(self, check: HealthCheck, result: HealthCheckResult) -> None:
        """Check for alerts based on health check result"""
        try:
            # Check response time threshold
            if result.response_time > self.alert_thresholds["response_time"]:
                await self._create_alert(
                    title=f"High Response Time - {check.name}",
                    message=f"Response time {result.response_time:.0f}ms exceeds threshold",
                    severity="warning"
                )
            
            # Check for critical failures
            if result.status == HealthStatus.CRITICAL:
                await self._create_alert(
                    title=f"Critical Failure - {check.name}",
                    message=f"Health check failed: {result.error_message}",
                    severity="critical"
                )
            
            # Check error rate
            if check.id in self.check_results:
                recent_results = self.check_results[check.id][-10:]  # Last 10 results
                if len(recent_results) >= 5:
                    error_count = len([r for r in recent_results if r.status != HealthStatus.HEALTHY])
                    error_rate = error_count / len(recent_results)
                    
                    if error_rate > self.alert_thresholds["error_rate"]:
                        await self._create_alert(
                            title=f"High Error Rate - {check.name}",
                            message=f"Error rate {error_rate:.1%} exceeds threshold",
                            severity="error"
                        )
                        
        except Exception as e:
            self.logger.error(f"Failed to check alerts: {e}")
    
    async def _create_alert(
        self,
        title: str,
        message: str,
        severity: str
    ) -> None:
        """Create a new alert"""
        try:
            alert_id = f"alert_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            alert = ConnectionAlert(
                id=alert_id,
                title=title,
                message=message,
                severity=severity,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.alerts[alert_id] = alert
            await self._save_alerts()
            
            self.logger.warning(f"Created alert: {alert_id} - {title}")
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}") 