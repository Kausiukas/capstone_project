"""
Performance Tracker - Tracks and optimizes system performance
"""

import asyncio
import time
import psutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric structure"""
    operation_name: str
    duration: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    success: bool
    error: str = None

class PerformanceTracker:
    """
    Tracks and optimizes system performance
    """
    
    def __init__(self):
        self.metrics = []
        self.max_metrics = 10000
        self.operation_timers = {}
        self.performance_thresholds = {
            "slow_operation_threshold": 5.0,  # seconds
            "high_memory_threshold": 100.0,   # MB
            "high_cpu_threshold": 50.0        # percent
        }
        self.optimization_suggestions = []
    
    async def initialize(self) -> None:
        """Initialize the performance tracker"""
        try:
            logger.info("Initializing performance tracker...")
            # Clear existing data
            self.metrics = []
            self.operation_timers = {}
            self.optimization_suggestions = []
            
            logger.info("Performance tracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize performance tracker: {e}")
            raise
        
    async def start_operation_timer(self, operation_name: str) -> Dict[str, Any]:
        """
        Start timing an operation
        
        Args:
            operation_name: Name of the operation to time
            
        Returns:
            Dictionary containing timer start result
        """
        try:
            if operation_name in self.operation_timers:
                return {
                    "success": False,
                    "error": f"Timer for operation '{operation_name}' already running"
                }
            
            self.operation_timers[operation_name] = {
                "start_time": time.time(),
                "start_memory": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                "start_cpu": psutil.cpu_percent()
            }
            
            return {
                "success": True,
                "operation_name": operation_name,
                "message": f"Timer started for operation '{operation_name}'"
            }
            
        except Exception as e:
            logger.error(f"Error starting operation timer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_operation_timer(self, operation_name: str, success: bool = True, error: str = None) -> Dict[str, Any]:
        """
        End timing an operation and record metrics
        
        Args:
            operation_name: Name of the operation
            success: Whether the operation was successful
            error: Error message if operation failed
            
        Returns:
            Dictionary containing timer end result
        """
        try:
            if operation_name not in self.operation_timers:
                return {
                    "success": False,
                    "error": f"No timer found for operation '{operation_name}'"
                }
            
            timer_data = self.operation_timers[operation_name]
            end_time = time.time()
            
            # Calculate metrics
            duration = end_time - timer_data["start_time"]
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - timer_data["start_memory"]
            cpu_usage = psutil.cpu_percent() - timer_data["start_cpu"]
            
            # Create metric
            metric = PerformanceMetric(
                operation_name=operation_name,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=datetime.now(),
                success=success,
                error=error
            )
            
            # Store metric
            self.metrics.append(metric)
            
            # Limit metrics list size
            if len(self.metrics) > self.max_metrics:
                self.metrics.pop(0)
            
            # Remove timer
            del self.operation_timers[operation_name]
            
            # Check for performance issues
            await self._check_performance_issues(metric)
            
            return {
                "success": True,
                "operation_name": operation_name,
                "metrics": {
                    "duration": round(duration, 3),
                    "memory_usage_mb": round(memory_usage, 2),
                    "cpu_usage_percent": round(cpu_usage, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error ending operation timer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for specified hours
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing performance summary
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics by time
            recent_metrics = [
                metric for metric in self.metrics
                if metric.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    "success": True,
                    "summary": {
                        "total_operations": 0,
                        "average_duration": 0,
                        "success_rate": 100,
                        "slow_operations": 0,
                        "high_memory_operations": 0
                    }
                }
            
            # Calculate summary statistics
            total_operations = len(recent_metrics)
            successful_operations = sum(1 for m in recent_metrics if m.success)
            success_rate = (successful_operations / total_operations) * 100
            
            durations = [m.duration for m in recent_metrics]
            average_duration = sum(durations) / len(durations)
            
            slow_operations = sum(1 for m in recent_metrics 
                                if m.duration > self.performance_thresholds["slow_operation_threshold"])
            
            high_memory_operations = sum(1 for m in recent_metrics 
                                       if m.memory_usage > self.performance_thresholds["high_memory_threshold"])
            
            # Top slowest operations
            slowest_operations = sorted(recent_metrics, key=lambda x: x.duration, reverse=True)[:5]
            
            return {
                "success": True,
                "summary": {
                    "total_operations": total_operations,
                    "successful_operations": successful_operations,
                    "success_rate": round(success_rate, 2),
                    "average_duration": round(average_duration, 3),
                    "slow_operations": slow_operations,
                    "high_memory_operations": high_memory_operations,
                    "slowest_operations": [
                        {
                            "operation_name": op.operation_name,
                            "duration": round(op.duration, 3),
                            "memory_usage_mb": round(op.memory_usage, 2),
                            "timestamp": op.timestamp.isoformat()
                        }
                        for op in slowest_operations
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_operation_metrics(self, operation_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics for a specific operation
        
        Args:
            operation_name: Name of the operation
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing operation metrics
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics by operation and time
            operation_metrics = [
                metric for metric in self.metrics
                if metric.operation_name == operation_name and metric.timestamp >= cutoff_time
            ]
            
            if not operation_metrics:
                return {
                    "success": False,
                    "error": f"No metrics found for operation '{operation_name}'"
                }
            
            # Calculate statistics
            total_calls = len(operation_metrics)
            successful_calls = sum(1 for m in operation_metrics if m.success)
            success_rate = (successful_calls / total_calls) * 100
            
            durations = [m.duration for m in operation_metrics]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            memory_usages = [m.memory_usage for m in operation_metrics]
            avg_memory = sum(memory_usages) / len(memory_usages)
            
            cpu_usages = [m.cpu_usage for m in operation_metrics]
            avg_cpu = sum(cpu_usages) / len(cpu_usages)
            
            return {
                "success": True,
                "operation_name": operation_name,
                "metrics": {
                    "total_calls": total_calls,
                    "successful_calls": successful_calls,
                    "success_rate": round(success_rate, 2),
                    "duration_stats": {
                        "average": round(avg_duration, 3),
                        "minimum": round(min_duration, 3),
                        "maximum": round(max_duration, 3)
                    },
                    "memory_stats": {
                        "average_mb": round(avg_memory, 2)
                    },
                    "cpu_stats": {
                        "average_percent": round(avg_cpu, 2)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting operation metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Get performance optimization suggestions
        
        Returns:
            Dictionary containing optimization suggestions
        """
        try:
            # Analyze recent metrics for patterns
            recent_metrics = self.metrics[-100:] if self.metrics else []
            
            suggestions = []
            
            if recent_metrics:
                # Check for slow operations
                slow_operations = [m for m in recent_metrics 
                                 if m.duration > self.performance_thresholds["slow_operation_threshold"]]
                
                if slow_operations:
                    slow_op_names = set(m.operation_name for m in slow_operations)
                    suggestions.append({
                        "type": "slow_operations",
                        "severity": "high",
                        "message": f"Found {len(slow_operations)} slow operations: {', '.join(slow_op_names)}",
                        "recommendation": "Consider optimizing these operations or implementing caching"
                    })
                
                # Check for high memory usage
                high_memory_ops = [m for m in recent_metrics 
                                 if m.memory_usage > self.performance_thresholds["high_memory_threshold"]]
                
                if high_memory_ops:
                    high_mem_op_names = set(m.operation_name for m in high_memory_ops)
                    suggestions.append({
                        "type": "high_memory_usage",
                        "severity": "medium",
                        "message": f"Found {len(high_memory_ops)} operations with high memory usage: {', '.join(high_mem_op_names)}",
                        "recommendation": "Consider implementing memory pooling or reducing data retention"
                    })
                
                # Check for failed operations
                failed_operations = [m for m in recent_metrics if not m.success]
                
                if failed_operations:
                    failed_op_names = set(m.operation_name for m in failed_operations)
                    suggestions.append({
                        "type": "failed_operations",
                        "severity": "high",
                        "message": f"Found {len(failed_operations)} failed operations: {', '.join(failed_op_names)}",
                        "recommendation": "Review error handling and implement retry mechanisms"
                    })
            
            return {
                "success": True,
                "suggestions": suggestions,
                "total_suggestions": len(suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_performance_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """
        Set performance thresholds
        
        Args:
            thresholds: Dictionary of threshold values
            
        Returns:
            Dictionary containing set result
        """
        try:
            for key, value in thresholds.items():
                if key in self.performance_thresholds:
                    self.performance_thresholds[key] = value
            
            return {
                "success": True,
                "message": "Performance thresholds updated",
                "thresholds": self.performance_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error setting performance thresholds: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def clear_metrics(self, hours: int = None) -> Dict[str, Any]:
        """
        Clear old metrics
        
        Args:
            hours: Clear metrics older than this many hours (None = clear all)
            
        Returns:
            Dictionary containing clear result
        """
        try:
            if hours is None:
                # Clear all metrics
                cleared_count = len(self.metrics)
                self.metrics.clear()
            else:
                # Clear metrics older than specified hours
                cutoff_time = datetime.now() - timedelta(hours=hours)
                original_count = len(self.metrics)
                self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
                cleared_count = original_count - len(self.metrics)
            
            return {
                "success": True,
                "message": f"Cleared {cleared_count} metrics",
                "remaining_metrics": len(self.metrics)
            }
            
        except Exception as e:
            logger.error(f"Error clearing metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_performance_issues(self, metric: PerformanceMetric):
        """Check for performance issues in a metric"""
        try:
            issues = []
            
            # Check for slow operations
            if metric.duration > self.performance_thresholds["slow_operation_threshold"]:
                issues.append(f"Slow operation: {metric.duration:.3f}s")
            
            # Check for high memory usage
            if metric.memory_usage > self.performance_thresholds["high_memory_threshold"]:
                issues.append(f"High memory usage: {metric.memory_usage:.2f}MB")
            
            # Check for high CPU usage
            if metric.cpu_usage > self.performance_thresholds["high_cpu_threshold"]:
                issues.append(f"High CPU usage: {metric.cpu_usage:.2f}%")
            
            # Check for failed operations
            if not metric.success:
                issues.append(f"Operation failed: {metric.error}")
            
            # Store issues for later analysis
            if issues:
                self.optimization_suggestions.append({
                    "operation_name": metric.operation_name,
                    "issues": issues,
                    "timestamp": metric.timestamp
                })
                
                # Limit suggestions list size
                if len(self.optimization_suggestions) > 1000:
                    self.optimization_suggestions.pop(0)
                    
        except Exception as e:
            logger.error(f"Error checking performance issues: {str(e)}") 