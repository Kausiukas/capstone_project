"""
Module 3: ECONOMY - Cost Tracking and Optimization Module

This module handles cost tracking and optimization including:
- Token usage tracking and monitoring
- Cost analysis and optimization strategies
- Budget management and alerts
- System self-sufficiency optimization
- Cost prediction and forecasting
"""

from .cost_tracker import CostTracker
from .budget_manager import BudgetManager
from .optimization_engine import OptimizationEngine
from .cost_analyzer import CostAnalyzer
from .alert_system import AlertSystem

__version__ = "1.0.0"
__author__ = "LangFlow Connect Team"

__all__ = [
    "CostTracker",
    "BudgetManager",
    "OptimizationEngine",
    "CostAnalyzer",
    "AlertSystem"
] 