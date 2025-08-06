"""
Inspector Metrics Collector - Task 1.3.1
========================================

This module provides comprehensive metrics collection capabilities for the Inspector system.
It collects performance data, operational metrics, and system health information from
MCP server operations and Inspector CLI interactions.

Key Features:
- Real-time metrics collection from MCP server operations
- Performance timing and resource usage monitoring
- Error rate and success rate tracking
- Historical data storage and trend analysis
- Integration with Inspector CLI utilities
- Configurable collection intervals and data retention

Author: Inspector Development Team
Date: January 2025
"""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from enum import Enum
import psutil
import asyncio
from pathlib import Path

from inspector_cli_utils import InspectorCLIUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected."""
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    THROUGHPUT = "throughput"
    CONCURRENT_REQUESTS = "concurrent_requests"
    SYSTEM_HEALTH = "system_health"
    TOOL_PERFORMANCE = "tool_performance"


class MetricStatus(Enum):
    """Status of metric collection operations."""
    COLLECTED = "collected"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INVALID = "invalid"


@dataclass
class MetricData:
    """Data structure for individual metric measurements."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]
    status: MetricStatus
    source: str
    tool_name: Optional[str] = None
    operation_id: Optional[str] = None


@dataclass
class SystemSnapshot:
    """Snapshot of system resource usage."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int


class MetricsCollector:
    """
    Main metrics collector for the Inspector system.
    
    Collects comprehensive metrics from MCP server operations, Inspector CLI interactions,
    and system resource usage. Provides real-time monitoring and historical data analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the metrics collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        self.config = config or self._get_default_config()
        self.inspector_cli = InspectorCLIUtils()
        
        # Metrics storage
        self.metrics_history: Dict[MetricType, deque] = defaultdict(
            lambda: deque(maxlen=self.config['max_history_size'])
        )
        self.system_snapshots: deque = deque(maxlen=self.config['max_history_size'])
        
        # Collection state
        self.is_collecting = False
        self.collection_thread: Optional[threading.Thread] = None
        self.stop_collection = threading.Event()
        
        # Performance tracking
        self.operation_timers: Dict[str, float] = {}
        self.concurrent_operations = 0
        self.max_concurrent_operations = 0
        
        # Error tracking
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        
        # Initialize storage directory
        self._init_storage()
        
        logger.info("Metrics Collector initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the metrics collector."""
        return {
            'collection_interval': 5.0,  # seconds
            'max_history_size': 1000,
            'storage_directory': 'inspector_metrics',
            'enable_system_monitoring': True,
            'enable_performance_tracking': True,
            'enable_error_tracking': True,
            'metrics_retention_days': 30,
            'auto_cleanup': True,
            'compression_enabled': True
        }
    
    def _init_storage(self):
        """Initialize storage directory and files."""
        storage_path = Path(self.config['storage_directory'])
        storage_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (storage_path / 'metrics').mkdir(exist_ok=True)
        (storage_path / 'snapshots').mkdir(exist_ok=True)
        (storage_path / 'reports').mkdir(exist_ok=True)
        
        logger.info(f"Storage initialized at: {storage_path.absolute()}")
    
    def start_collection(self):
        """Start continuous metrics collection."""
        if self.is_collecting:
            logger.warning("Metrics collection is already running")
            return
        
        self.is_collecting = True
        self.stop_collection.clear()
        
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()
        
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop continuous metrics collection."""
        if not self.is_collecting:
            logger.warning("Metrics collection is not running")
            return
        
        self.is_collecting = False
        self.stop_collection.set()
        
        if self.collection_thread:
            self.collection_thread.join(timeout=5.0)
        
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop for continuous metrics gathering."""
        while self.is_collecting and not self.stop_collection.is_set():
            try:
                # Collect system metrics
                if self.config['enable_system_monitoring']:
                    self._collect_system_metrics()
                
                # Collect performance metrics
                if self.config['enable_performance_tracking']:
                    self._collect_performance_metrics()
                
                # Collect error metrics
                if self.config['enable_error_tracking']:
                    self._collect_error_metrics()
                
                # Store metrics
                self._store_metrics()
                
                # Wait for next collection interval
                time.sleep(self.config['collection_interval'])
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(1.0)  # Brief pause on error
    
    def _collect_system_metrics(self):
        """Collect system resource usage metrics."""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_data = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # Create snapshot
            snapshot = SystemSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available,
                disk_usage_percent=disk.percent,
                network_io=network_data,
                process_count=process_count
            )
            
            self.system_snapshots.append(snapshot)
            
            # Create metric data
            metric_data = MetricData(
                metric_type=MetricType.SYSTEM_HEALTH,
                value=cpu_percent,
                timestamp=datetime.now(),
                metadata={
                    'memory_percent': memory.percent,
                    'disk_usage_percent': disk.percent,
                    'process_count': process_count
                },
                status=MetricStatus.COLLECTED,
                source='system_monitor'
            )
            
            self.metrics_history[MetricType.SYSTEM_HEALTH].append(metric_data)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_performance_metrics(self):
        """Collect performance-related metrics."""
        try:
            # Calculate current throughput
            current_time = datetime.now()
            recent_metrics = []
            
            for metric_type in [MetricType.RESPONSE_TIME, MetricType.THROUGHPUT]:
                if self.metrics_history[metric_type]:
                    recent_metrics.extend(list(self.metrics_history[metric_type])[-10:])
            
            if recent_metrics:
                # Calculate average response time
                response_times = [
                    m.value for m in recent_metrics 
                    if m.metric_type == MetricType.RESPONSE_TIME
                ]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    
                    metric_data = MetricData(
                        metric_type=MetricType.RESPONSE_TIME,
                        value=avg_response_time,
                        timestamp=current_time,
                        metadata={'sample_count': len(response_times)},
                        status=MetricStatus.COLLECTED,
                        source='performance_monitor'
                    )
                    
                    self.metrics_history[MetricType.RESPONSE_TIME].append(metric_data)
                
                # Calculate throughput
                throughput = len(recent_metrics) / 60.0  # operations per minute
                
                metric_data = MetricData(
                    metric_type=MetricType.THROUGHPUT,
                    value=throughput,
                    timestamp=current_time,
                    metadata={'operation_count': len(recent_metrics)},
                    status=MetricStatus.COLLECTED,
                    source='performance_monitor'
                )
                
                self.metrics_history[MetricType.THROUGHPUT].append(metric_data)
            
            # Track concurrent operations
            metric_data = MetricData(
                metric_type=MetricType.CONCURRENT_REQUESTS,
                value=self.concurrent_operations,
                timestamp=current_time,
                metadata={'max_concurrent': self.max_concurrent_operations},
                status=MetricStatus.COLLECTED,
                source='performance_monitor'
            )
            
            self.metrics_history[MetricType.CONCURRENT_REQUESTS].append(metric_data)
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    def _collect_error_metrics(self):
        """Collect error and success rate metrics."""
        try:
            current_time = datetime.now()
            
            # Calculate error rates by source
            for source in set(self.error_counts.keys()) | set(self.success_counts.keys()):
                total_operations = self.error_counts[source] + self.success_counts[source]
                
                if total_operations > 0:
                    error_rate = self.error_counts[source] / total_operations
                    success_rate = self.success_counts[source] / total_operations
                    
                    # Error rate metric
                    error_metric = MetricData(
                        metric_type=MetricType.ERROR_RATE,
                        value=error_rate,
                        timestamp=current_time,
                        metadata={'source': source, 'total_operations': total_operations},
                        status=MetricStatus.COLLECTED,
                        source='error_monitor'
                    )
                    
                    self.metrics_history[MetricType.ERROR_RATE].append(error_metric)
                    
                    # Success rate metric
                    success_metric = MetricData(
                        metric_type=MetricType.SUCCESS_RATE,
                        value=success_rate,
                        timestamp=current_time,
                        metadata={'source': source, 'total_operations': total_operations},
                        status=MetricStatus.COLLECTED,
                        source='error_monitor'
                    )
                    
                    self.metrics_history[MetricType.SUCCESS_RATE].append(success_metric)
            
        except Exception as e:
            logger.error(f"Error collecting error metrics: {e}")
    
    def _store_metrics(self):
        """Store collected metrics to persistent storage."""
        try:
            storage_path = Path(self.config['storage_directory'])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Store metrics data
            metrics_file = storage_path / 'metrics' / f'metrics_{timestamp}.json'
            metrics_data = {
                'timestamp': timestamp,
                'metrics': {
                    metric_type.value: [
                        {
                            'value': metric.value,
                            'timestamp': metric.timestamp.isoformat(),
                            'metadata': metric.metadata,
                            'status': metric.status.value,
                            'source': metric.source,
                            'tool_name': metric.tool_name,
                            'operation_id': metric.operation_id
                        }
                        for metric in metrics_list
                    ]
                    for metric_type, metrics_list in self.metrics_history.items()
                }
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Store system snapshots
            snapshots_file = storage_path / 'snapshots' / f'snapshots_{timestamp}.json'
            snapshots_data = {
                'timestamp': timestamp,
                'snapshots': [
                    {
                        'timestamp': snapshot.timestamp.isoformat(),
                        'cpu_percent': snapshot.cpu_percent,
                        'memory_percent': snapshot.memory_percent,
                        'memory_available': snapshot.memory_available,
                        'disk_usage_percent': snapshot.disk_usage_percent,
                        'network_io': snapshot.network_io,
                        'process_count': snapshot.process_count
                    }
                    for snapshot in self.system_snapshots
                ]
            }
            
            with open(snapshots_file, 'w') as f:
                json.dump(snapshots_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    def record_operation_start(self, operation_id: str, tool_name: Optional[str] = None):
        """Record the start of an operation for timing purposes."""
        self.operation_timers[operation_id] = time.time()
        self.concurrent_operations += 1
        self.max_concurrent_operations = max(
            self.max_concurrent_operations, 
            self.concurrent_operations
        )
        
        logger.debug(f"Operation started: {operation_id} (tool: {tool_name})")
    
    def record_operation_end(self, operation_id: str, success: bool = True, 
                           error_message: Optional[str] = None):
        """Record the end of an operation and calculate timing metrics."""
        if operation_id not in self.operation_timers:
            logger.warning(f"Operation {operation_id} not found in timers")
            return
        
        start_time = self.operation_timers.pop(operation_id)
        duration = time.time() - start_time
        self.concurrent_operations = max(0, self.concurrent_operations - 1)
        
        # Record response time metric
        metric_data = MetricData(
            metric_type=MetricType.RESPONSE_TIME,
            value=duration,
            timestamp=datetime.now(),
            metadata={'operation_id': operation_id, 'success': success},
            status=MetricStatus.COLLECTED if success else MetricStatus.FAILED,
            source='operation_timer',
            operation_id=operation_id
        )
        
        self.metrics_history[MetricType.RESPONSE_TIME].append(metric_data)
        
        # Record success/error counts
        source = 'mcp_operations'
        if success:
            self.success_counts[source] += 1
        else:
            self.error_counts[source] += 1
            logger.error(f"Operation {operation_id} failed: {error_message}")
        
        logger.debug(f"Operation completed: {operation_id} (duration: {duration:.3f}s, success: {success})")
    
    def record_tool_performance(self, tool_name: str, duration: float, 
                              success: bool, metadata: Optional[Dict[str, Any]] = None):
        """Record performance metrics for a specific tool."""
        metric_data = MetricData(
            metric_type=MetricType.TOOL_PERFORMANCE,
            value=duration,
            timestamp=datetime.now(),
            metadata=metadata or {},
            status=MetricStatus.COLLECTED if success else MetricStatus.FAILED,
            source='tool_monitor',
            tool_name=tool_name
        )
        
        self.metrics_history[MetricType.TOOL_PERFORMANCE].append(metric_data)
        
        # Update success/error counts
        source = f'tool_{tool_name}'
        if success:
            self.success_counts[source] += 1
        else:
            self.error_counts[source] += 1
    
    def get_metrics_summary(self, metric_type: Optional[MetricType] = None, 
                          time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        try:
            current_time = datetime.now()
            time_range = time_range or timedelta(hours=1)
            
            summary = {
                'timestamp': current_time.isoformat(),
                'time_range': str(time_range),
                'metrics': {}
            }
            
            # Filter metrics by time range
            cutoff_time = current_time - time_range
            
            for mt, metrics_list in self.metrics_history.items():
                if metric_type and mt != metric_type:
                    continue
                
                recent_metrics = [
                    m for m in metrics_list 
                    if m.timestamp >= cutoff_time
                ]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    summary['metrics'][mt.value] = {
                        'count': len(recent_metrics),
                        'min': min(values),
                        'max': max(values),
                        'average': sum(values) / len(values),
                        'latest': recent_metrics[-1].value,
                        'status_distribution': self._get_status_distribution(recent_metrics)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return {'error': str(e)}
    
    def _get_status_distribution(self, metrics: List[MetricData]) -> Dict[str, int]:
        """Get distribution of metric statuses."""
        distribution = defaultdict(int)
        for metric in metrics:
            distribution[metric.status.value] += 1
        return dict(distribution)
    
    def cleanup_old_data(self):
        """Clean up old metrics data based on retention policy."""
        try:
            retention_days = self.config['metrics_retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            storage_path = Path(self.config['storage_directory'])
            
            # Clean up metrics files
            metrics_dir = storage_path / 'metrics'
            for file_path in metrics_dir.glob('metrics_*.json'):
                try:
                    file_date_str = file_path.stem.split('_')[1]  # Get date part
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        logger.info(f"Deleted old metrics file: {file_path}")
                        
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse date from filename: {file_path}")
            
            # Clean up snapshot files
            snapshots_dir = storage_path / 'snapshots'
            for file_path in snapshots_dir.glob('snapshots_*.json'):
                try:
                    file_date_str = file_path.stem.split('_')[1]  # Get date part
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        logger.info(f"Deleted old snapshot file: {file_path}")
                        
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse date from filename: {file_path}")
            
            logger.info("Old data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
    
    def export_metrics(self, format: str = 'json', 
                      time_range: Optional[timedelta] = None) -> str:
        """Export metrics data in the specified format."""
        try:
            summary = self.get_metrics_summary(time_range=time_range)
            
            if format.lower() == 'json':
                return json.dumps(summary, indent=2)
            elif format.lower() == 'csv':
                return self._convert_to_csv(summary)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return f"Error: {e}"
    
    def _convert_to_csv(self, summary: Dict[str, Any]) -> str:
        """Convert metrics summary to CSV format."""
        csv_lines = ['Metric Type,Count,Min,Max,Average,Latest']
        
        for metric_type, data in summary.get('metrics', {}).items():
            csv_lines.append(
                f"{metric_type},{data['count']},{data['min']:.3f},"
                f"{data['max']:.3f},{data['average']:.3f},{data['latest']:.3f}"
            )
        
        return '\n'.join(csv_lines)


def main():
    """Main function for testing the metrics collector."""
    print("Inspector Metrics Collector - Task 1.3.1")
    print("=" * 50)
    
    # Initialize collector
    collector = MetricsCollector()
    
    try:
        # Start collection
        print("Starting metrics collection...")
        collector.start_collection()
        
        # Simulate some operations
        print("Simulating operations...")
        for i in range(5):
            operation_id = f"test_op_{i}"
            collector.record_operation_start(operation_id, f"test_tool_{i}")
            
            # Simulate operation duration
            time.sleep(0.5)
            
            success = i % 3 != 0  # Some operations fail
            collector.record_operation_end(operation_id, success)
        
        # Wait for collection
        time.sleep(10)
        
        # Get summary
        print("\nMetrics Summary:")
        summary = collector.get_metrics_summary()
        print(json.dumps(summary, indent=2))
        
        # Export metrics
        print("\nExported Metrics (CSV):")
        csv_data = collector.export_metrics(format='csv')
        print(csv_data)
        
    except KeyboardInterrupt:
        print("\nStopping collection...")
    finally:
        collector.stop_collection()
        print("Metrics collection stopped")


if __name__ == "__main__":
    main() 