"""
Module 1: MAIN - Workspace Operations Module

This module handles all workspace operations including:
- File read/write operations
- Repository ingestion and management
- Code explanation and analysis
- Code refactoring
- External service integration
- Local machine operations
"""

from .workspace_manager import WorkspaceManager
from .repository_ingestor import RepositoryIngestor
from .code_analyzer import CodeAnalyzer
from .code_refactorer import CodeRefactorer
from .external_services import ExternalServiceManager
from .workspace_operations import WorkspaceOperations, WorkspaceOperationResult

__version__ = "1.0.0"
__author__ = "LangFlow Connect Team"

__all__ = [
    "WorkspaceManager",
    "RepositoryIngestor", 
    "CodeAnalyzer",
    "CodeRefactorer",
    "ExternalServiceManager",
    "WorkspaceOperations",
    "WorkspaceOperationResult"
] 