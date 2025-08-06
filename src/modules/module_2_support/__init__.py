"""
Module 2: SUPPORT - System Support and Coordination Module

This module handles system support operations including:
- PostgreSQL vector agent with enhanced capabilities
- System coordination and health monitoring
- Performance tracking and optimization
- Memory management and caching
- Inter-module communication
"""

from .postgresql_vector_agent import PostgreSQLVectorAgent
from .system_coordinator import SystemCoordinator
from .health_monitor import HealthMonitor
from .performance_tracker import PerformanceTracker
from .memory_manager import MemoryManager

__version__ = "1.0.0"
__author__ = "LangFlow Connect Team"

__all__ = [
    "PostgreSQLVectorAgent",
    "SystemCoordinator",
    "HealthMonitor", 
    "PerformanceTracker",
    "MemoryManager"
] 