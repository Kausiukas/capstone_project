"""
Inspector Continuous Monitor Module (Task 4.2.1)

This module provides real-time system monitoring capabilities for the Inspector system.
It monitors system resources, Inspector processes, and generates monitoring events.
"""

import asyncio
import json
import logging
import os
import psutil
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorType(Enum):
    """Types of monitoring metrics"""
    SYSTEM = "system"
    PROCESS = "process"
    NETWORK = "network"
    DISK = "disk"
    MEMORY = "memory"
    CPU = "cpu"
    INSPECTOR = "inspector"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_processes: int
    load_average: Optional[float] = None


@dataclass
class ProcessMetrics:
    """Process-specific metrics"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    status: str
    create_time: float
    num_threads: int
    io_counters: Optional[Dict[str, int]] = None


@dataclass
class InspectorMetrics:
    """Inspector-specific metrics"""
    timestamp: datetime
    active_connections: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float
    active_jobs: int
    queue_size: int
    uptime_seconds: float


@dataclass
class MonitoringEvent:
    """Monitoring event data"""
    event_id: str
    timestamp: datetime
    event_type: str
    source: str
    message: str
    alert_level: AlertLevel
    metrics: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


@dataclass
class MonitorConfig:
    """Monitoring configuration"""
    enabled: bool = True
    interval_seconds: float = 5.0
    max_history_size: int = 1000
    alert_thresholds: Dict[str, float] = None
    monitored_processes: List[str] = None
    data_retention_days: int = 7
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "response_time_ms": 5000.0,
                "error_rate_percent": 5.0
            }
        if self.monitored_processes is None:
            self.monitored_processes = ["python", "node", "npx"]


class InspectorContinuousMonitor:
    """Continuous monitoring system for Inspector"""
    
    def __init__(self, config: MonitorConfig = None, data_dir: str = "data/monitoring"):
        self.config = config or MonitorConfig()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Monitoring state
        self.is_running = False
        self.monitor_thread = None
        self.metrics_history = defaultdict(lambda: deque(maxlen=self.config.max_history_size))
        self.events_history = deque(maxlen=self.config.max_history_size)
        
        # Event callbacks
        self.event_callbacks: List[Callable[[MonitoringEvent], None]] = []
        
        # Performance tracking
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        self.start_time = time.time()
        
        # Load existing data
        self._load_monitoring_data()
        
        logger.info("Inspector Continuous Monitor initialized")
    
    def start_monitoring(self) -> bool:
        """Start the monitoring system"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return False
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Continuous monitoring started")
        return True
    
    def stop_monitoring(self) -> bool:
        """Stop the monitoring system"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return False
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Continuous monitoring stopped")
        return True
    
    def add_event_callback(self, callback: Callable[[MonitoringEvent], None]) -> None:
        """Add an event callback function"""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[MonitoringEvent], None]) -> None:
        """Remove an event callback function"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = {}
            try:
                net_io = psutil.net_io_counters()
                network_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            except Exception as e:
                logger.warning(f"Failed to get network I/O: {e}")
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_io,
                active_processes=len(psutil.pids())
            )
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return None
    
    def get_process_metrics(self, process_names: List[str] = None) -> List[ProcessMetrics]:
        """Get metrics for specific processes"""
        if process_names is None:
            process_names = self.config.monitored_processes
        
        process_metrics = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time', 'num_threads']):
                try:
                    if proc.info['name'] and any(name.lower() in proc.info['name'].lower() for name in process_names):
                        # Get additional memory info
                        memory_info = proc.memory_info()
                        
                        # Get I/O counters if available
                        io_counters = None
                        try:
                            io_counters = proc.io_counters()._asdict()
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass
                        
                        process_metrics.append(ProcessMetrics(
                            pid=proc.info['pid'],
                            name=proc.info['name'],
                            cpu_percent=proc.info['cpu_percent'],
                            memory_percent=proc.info['memory_percent'],
                            memory_rss=memory_info.rss,
                            status=proc.info['status'],
                            create_time=proc.info['create_time'],
                            num_threads=proc.info['num_threads'],
                            io_counters=io_counters
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Failed to get process metrics: {e}")
        
        return process_metrics
    
    def get_inspector_metrics(self) -> InspectorMetrics:
        """Get Inspector-specific metrics"""
        try:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            # Calculate request metrics
            requests_per_minute = 0
            average_response_time = 0
            error_rate = 0
            
            if self.total_requests > 0:
                # Calculate requests per minute
                time_window = max(1, min(60, uptime))  # Ensure time_window is at least 1 second
                recent_requests = sum(1 for req_time in self.request_times 
                                   if current_time - req_time <= time_window)
                requests_per_minute = (recent_requests / time_window) * 60
                
                # Calculate average response time
                if self.request_times:
                    average_response_time = sum(self.request_times) / len(self.request_times)
                
                # Calculate error rate
                error_rate = (self.error_count / self.total_requests) * 100
            
            return InspectorMetrics(
                timestamp=datetime.now(),
                active_connections=len(self.event_callbacks),  # Simplified
                requests_per_minute=requests_per_minute,
                average_response_time=average_response_time,
                error_rate=error_rate,
                active_jobs=len([m for m in self.metrics_history[MonitorType.INSPECTOR.value] 
                               if isinstance(m, InspectorMetrics)]),
                queue_size=len(self.events_history),
                uptime_seconds=uptime
            )
        except Exception as e:
            logger.error(f"Failed to get Inspector metrics: {e}")
            return None
    
    def record_request(self, response_time: float, is_error: bool = False) -> None:
        """Record a request for metrics calculation"""
        self.total_requests += 1
        if is_error:
            self.error_count += 1
        self.request_times.append(response_time)
    
    def check_alert_thresholds(self, metrics: Dict[str, Any]) -> List[MonitoringEvent]:
        """Check metrics against alert thresholds"""
        events = []
        
        for metric_name, threshold in self.config.alert_thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if value > threshold:
                    alert_level = AlertLevel.WARNING if value < threshold * 1.5 else AlertLevel.CRITICAL
                    
                    event = MonitoringEvent(
                        event_id=f"threshold_{metric_name}_{int(time.time())}",
                        timestamp=datetime.now(),
                        event_type="threshold_exceeded",
                        source="monitor",
                        message=f"{metric_name} exceeded threshold: {value:.2f} > {threshold:.2f}",
                        alert_level=alert_level,
                        metrics={metric_name: value, "threshold": threshold},
                        tags=["threshold", metric_name]
                    )
                    events.append(event)
        
        return events
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        logger.info("Monitoring loop started")
        
        while self.is_running:
            try:
                # Collect system metrics
                system_metrics = self.get_system_metrics()
                if system_metrics:
                    self.metrics_history[MonitorType.SYSTEM.value].append(system_metrics)
                    
                    # Check thresholds
                    metrics_dict = {
                        "cpu_percent": system_metrics.cpu_percent,
                        "memory_percent": system_metrics.memory_percent,
                        "disk_percent": system_metrics.disk_usage_percent
                    }
                    
                    threshold_events = self.check_alert_thresholds(metrics_dict)
                    for event in threshold_events:
                        self._emit_event(event)
                
                # Collect process metrics
                process_metrics = self.get_process_metrics()
                if process_metrics:
                    self.metrics_history[MonitorType.PROCESS.value].append(process_metrics)
                
                # Collect Inspector metrics
                inspector_metrics = self.get_inspector_metrics()
                if inspector_metrics:
                    self.metrics_history[MonitorType.INSPECTOR.value].append(inspector_metrics)
                    
                    # Check Inspector-specific thresholds
                    inspector_dict = {
                        "response_time_ms": inspector_metrics.average_response_time * 1000,
                        "error_rate_percent": inspector_metrics.error_rate
                    }
                    
                    inspector_events = self.check_alert_thresholds(inspector_dict)
                    for event in inspector_events:
                        self._emit_event(event)
                
                # Save data periodically
                if len(self.events_history) % 10 == 0:
                    self._save_monitoring_data()
                
                # Wait for next interval
                time.sleep(self.config.interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.interval_seconds)
    
    def _emit_event(self, event: MonitoringEvent) -> None:
        """Emit a monitoring event to all callbacks"""
        self.events_history.append(event)
        
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def get_metrics_history(self, metric_type: MonitorType, limit: int = None) -> List[Any]:
        """Get historical metrics for a specific type"""
        history = list(self.metrics_history[metric_type.value])
        if limit:
            history = history[-limit:]
        return history
    
    def get_recent_events(self, limit: int = 100) -> List[MonitoringEvent]:
        """Get recent monitoring events"""
        return list(self.events_history)[-limit:]
    
    def get_events_by_level(self, alert_level: AlertLevel) -> List[MonitoringEvent]:
        """Get events filtered by alert level"""
        return [event for event in self.events_history if event.alert_level == alert_level]
    
    def clear_old_data(self, days: int = None) -> None:
        """Clear old monitoring data"""
        if days is None:
            days = self.config.data_retention_days
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Clear old metrics
        for metric_type in self.metrics_history:
            self.metrics_history[metric_type] = deque(
                [m for m in self.metrics_history[metric_type] 
                 if hasattr(m, 'timestamp') and m.timestamp > cutoff_time],
                maxlen=self.config.max_history_size
            )
        
        # Clear old events
        self.events_history = deque(
            [e for e in self.events_history if e.timestamp > cutoff_time],
            maxlen=self.config.max_history_size
        )
        
        logger.info(f"Cleared monitoring data older than {days} days")
    
    def _save_monitoring_data(self) -> None:
        """Save monitoring data to disk"""
        try:
            # Save metrics history
            metrics_file = self.data_dir / "metrics_history.json"
            metrics_data = {}
            
            for metric_type, history in self.metrics_history.items():
                metrics_data[metric_type] = []
                for item in history:
                    if hasattr(item, '__dict__'):
                        item_dict = asdict(item)
                        if 'timestamp' in item_dict:
                            item_dict['timestamp'] = item_dict['timestamp'].isoformat()
                        metrics_data[metric_type].append(item_dict)
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Save events history
            events_file = self.data_dir / "events_history.json"
            events_data = []
            
            for event in self.events_history:
                event_dict = asdict(event)
                event_dict['timestamp'] = event_dict['timestamp'].isoformat()
                event_dict['alert_level'] = event_dict['alert_level'].value
                events_data.append(event_dict)
            
            with open(events_file, 'w') as f:
                json.dump(events_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save monitoring data: {e}")
    
    def _load_monitoring_data(self) -> None:
        """Load monitoring data from disk"""
        try:
            # Load metrics history
            metrics_file = self.data_dir / "metrics_history.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                
                for metric_type, history_data in metrics_data.items():
                    for item_data in history_data:
                        if metric_type == MonitorType.SYSTEM.value:
                            item_data['timestamp'] = datetime.fromisoformat(item_data['timestamp'])
                            self.metrics_history[metric_type].append(SystemMetrics(**item_data))
                        elif metric_type == MonitorType.INSPECTOR.value:
                            item_data['timestamp'] = datetime.fromisoformat(item_data['timestamp'])
                            self.metrics_history[metric_type].append(InspectorMetrics(**item_data))
            
            # Load events history
            events_file = self.data_dir / "events_history.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    events_data = json.load(f)
                
                for event_data in events_data:
                    event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'])
                    event_data['alert_level'] = AlertLevel(event_data['alert_level'])
                    self.events_history.append(MonitoringEvent(**event_data))
                    
        except Exception as e:
            logger.error(f"Failed to load monitoring data: {e}")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get a summary of current monitoring status"""
        try:
            system_metrics = self.get_system_metrics()
            inspector_metrics = self.get_inspector_metrics()
            
            recent_events = self.get_recent_events(10)
            critical_events = self.get_events_by_level(AlertLevel.CRITICAL)
            
            return {
                "monitoring_active": self.is_running,
                "uptime_seconds": time.time() - self.start_time,
                "system_metrics": asdict(system_metrics) if system_metrics else None,
                "inspector_metrics": asdict(inspector_metrics) if inspector_metrics else None,
                "recent_events_count": len(recent_events),
                "critical_events_count": len(critical_events),
                "total_events": len(self.events_history),
                "metrics_history_sizes": {
                    metric_type: len(history) 
                    for metric_type, history in self.metrics_history.items()
                }
            }
        except Exception as e:
            logger.error(f"Failed to get monitoring summary: {e}")
            return {"error": str(e)}


# Example usage and testing
if __name__ == "__main__":
    # Create monitoring configuration
    config = MonitorConfig(
        interval_seconds=2.0,
        max_history_size=100,
        alert_thresholds={
            "cpu_percent": 50.0,  # Lower threshold for testing
            "memory_percent": 70.0,
            "disk_percent": 80.0
        }
    )
    
    # Create monitor
    monitor = InspectorContinuousMonitor(config)
    
    # Add event callback
    def event_handler(event: MonitoringEvent):
        print(f"[{event.alert_level.value.upper()}] {event.message}")
    
    monitor.add_event_callback(event_handler)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        print("Monitoring started. Press Ctrl+C to stop...")
        while True:
            time.sleep(5)
            summary = monitor.get_monitoring_summary()
            print(f"Active: {summary['monitoring_active']}, "
                  f"CPU: {summary['system_metrics']['cpu_percent']:.1f}%, "
                  f"Memory: {summary['system_metrics']['memory_percent']:.1f}%")
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        monitor.stop_monitoring()
        print("Monitoring stopped.") 