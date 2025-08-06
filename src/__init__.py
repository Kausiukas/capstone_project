"""
LangFlow Connect - Secure MCP Integration Project

This package contains the modular system architecture for secure
MCP connections to Langflow applications.
"""

__version__ = "1.0.0"
__author__ = "LangFlow Connect Team"
__description__ = "Secure MCP Integration with Langflow"

# Import main modules
from .modules.module_4_langflow.langflow_connector import LangflowConnector
from .modules.module_1_main.workspace_operations import WorkspaceOperations
from .modules.module_2_support.system_coordinator import SystemCoordinator
from .modules.module_3_economy.cost_tracker import CostTracker

__all__ = [
    "LangflowConnector",
    "WorkspaceOperations", 
    "SystemCoordinator",
    "CostTracker"
]