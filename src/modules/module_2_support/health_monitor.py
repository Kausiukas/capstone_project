"""
Health Monitor - Monitors system health and performance
"""

import asyncio
import psutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics structure"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    process_count: int
    uptime: timedelta
    timestamp: datetime

class HealthMonitor:
    """
    Monitors system health and performance metrics
    """
    
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 1000
        self.monitoring = False
        self.monitor_task = None
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0
        }
        self.alerts = []
        self.initialized = False

    async def initialize(self) -> bool:
        """
        Initialize the health monitor

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing health monitor...")

            # Clear existing data
            self.metrics_history.clear()
            self.alerts.clear()

            # Verify psutil is available
            try:
                psutil.cpu_percent()
                psutil.virtual_memory()
                psutil.disk_usage('/')
            except Exception as e:
                logger.warning(f"Some system metrics may not be available: {e}")

            self.initialized = True
            logger.info("Health monitor initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize health monitor: {e}")
            return False
        
    async def start_monitoring(self, interval: int = 30) -> Dict[str, Any]:
        """
        Start system health monitoring
        
        Args:
            interval: Monitoring interval in seconds
            
        Returns:
            Dictionary containing start result
        """
        try:
            if self.monitoring:
                return {
                    "success": False,
                    "error": "Health monitoring already running"
                }
            
            self.monitoring = True
            self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
            
            return {
                "success": True,
                "message": f"Health monitoring started with {interval}s interval"
            }
            
        except Exception as e:
            logger.error(f"Error starting health monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop system health monitoring
        
        Returns:
            Dictionary containing stop result
        """
        try:
            if not self.monitoring:
                return {
                    "success": False,
                    "error": "Health monitoring not running"
                }
            
            self.monitoring = False
            
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
            
            return {
                "success": True,
                "message": "Health monitoring stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping health monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics
        
        Returns:
            Dictionary containing current metrics
        """
        try:
            metrics = await self._collect_metrics()
            
            return {
                "success": True,
                "metrics": {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "network_io": metrics.network_io,
                    "process_count": metrics.process_count,
                    "uptime": str(metrics.uptime),
                    "timestamp": metrics.timestamp.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_metrics_history(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics history for specified hours
        
        Args:
            hours: Number of hours to retrieve
            
        Returns:
            Dictionary containing metrics history
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics by time
            recent_metrics = [
                metrics for metrics in self.metrics_history
                if metrics.timestamp >= cutoff_time
            ]
            
            # Convert to serializable format
            history = []
            for metrics in recent_metrics:
                history.append({
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "network_io": metrics.network_io,
                    "process_count": metrics.process_count,
                    "uptime": str(metrics.uptime),
                    "timestamp": metrics.timestamp.isoformat()
                })
            
            return {
                "success": True,
                "history": history,
                "total_records": len(history),
                "time_range_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics history: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health assessment
        
        Returns:
            Dictionary containing health assessment
        """
        try:
            current_metrics = await self._collect_metrics()
            
            # Calculate health score
            health_score = 100.0
            
            # CPU health
            if current_metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
                health_score -= 20
            elif current_metrics.cpu_percent > 60:
                health_score -= 10
            
            # Memory health
            if current_metrics.memory_percent > self.alert_thresholds["memory_percent"]:
                health_score -= 25
            elif current_metrics.memory_percent > 70:
                health_score -= 15
            
            # Disk health
            if current_metrics.disk_usage_percent > self.alert_thresholds["disk_usage_percent"]:
                health_score -= 30
            elif current_metrics.disk_usage_percent > 80:
                health_score -= 20
            
            # Process count health
            if current_metrics.process_count > 200:
                health_score -= 10
            
            health_score = max(0, health_score)
            
            # Determine health status
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            elif health_score >= 40:
                status = "critical"
            else:
                status = "emergency"
            
            # Check for alerts
            alerts = []
            if current_metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
                alerts.append(f"High CPU usage: {current_metrics.cpu_percent:.1f}%")
            
            if current_metrics.memory_percent > self.alert_thresholds["memory_percent"]:
                alerts.append(f"High memory usage: {current_metrics.memory_percent:.1f}%")
            
            if current_metrics.disk_usage_percent > self.alert_thresholds["disk_usage_percent"]:
                alerts.append(f"High disk usage: {current_metrics.disk_usage_percent:.1f}%")
            
            return {
                "success": True,
                "health": {
                    "status": status,
                    "score": round(health_score, 1),
                    "alerts": alerts,
                    "metrics": {
                        "cpu_percent": current_metrics.cpu_percent,
                        "memory_percent": current_metrics.memory_percent,
                        "disk_usage_percent": current_metrics.disk_usage_percent,
                        "process_count": current_metrics.process_count,
                        "uptime": str(current_metrics.uptime)
                    },
                    "timestamp": current_metrics.timestamp.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_alert_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """
        Set alert thresholds for monitoring
        
        Args:
            thresholds: Dictionary of threshold values
            
        Returns:
            Dictionary containing set result
        """
        try:
            for key, value in thresholds.items():
                if key in self.alert_thresholds:
                    self.alert_thresholds[key] = value
            
            return {
                "success": True,
                "message": "Alert thresholds updated",
                "thresholds": self.alert_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error setting alert thresholds: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_alerts(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get recent alerts
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary containing alerts
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_alerts = [
                alert for alert in self.alerts
                if alert["timestamp"] >= cutoff_time
            ]
            
            return {
                "success": True,
                "alerts": recent_alerts,
                "total_alerts": len(recent_alerts),
                "time_range_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                
                # Store in history
                self.metrics_history.append(metrics)
                
                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # System uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count,
                uptime=uptime,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            # Return default metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0},
                process_count=0,
                uptime=timedelta(0),
                timestamp=datetime.now()
            )
    
    async def _check_alerts(self, metrics: SystemMetrics):
        """Check for alert conditions"""
        try:
            current_time = datetime.now()
            
            # Check CPU threshold
            if metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
                self._add_alert("high_cpu", f"CPU usage is {metrics.cpu_percent:.1f}%", current_time)
            
            # Check memory threshold
            if metrics.memory_percent > self.alert_thresholds["memory_percent"]:
                self._add_alert("high_memory", f"Memory usage is {metrics.memory_percent:.1f}%", current_time)
            
            # Check disk threshold
            if metrics.disk_usage_percent > self.alert_thresholds["disk_usage_percent"]:
                self._add_alert("high_disk", f"Disk usage is {metrics.disk_usage_percent:.1f}%", current_time)
            
            # Check process count
            if metrics.process_count > 200:
                self._add_alert("high_process_count", f"Process count is {metrics.process_count}", current_time)
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
    
    def _add_alert(self, alert_type: str, message: str, timestamp: datetime):
        """Add an alert to the alerts list"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": timestamp,
            "severity": "warning"
        }
        
        self.alerts.append(alert)
        
        # Limit alerts list size
        if len(self.alerts) > 1000:
            self.alerts.pop(0)
    
    async def cleanup(self):
        """
        Cleanup resources and reset state
        """
        try:
            # Stop monitoring if running
            if self.monitoring:
                await self.stop_monitoring()
            
            # Clear data
            self.metrics_history.clear()
            self.alerts.clear()
            self.initialized = False
            logger.info("Health monitor cleanup completed")
        except Exception as e:
            logger.error(f"Error during health monitor cleanup: {e}") 