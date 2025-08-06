#!/usr/bin/env python3
"""
Workspace Operations - High-level interface for workspace management

This module provides a unified interface for all workspace operations including:
- File read/write operations
- Directory scanning and listing
- Code analysis and metrics
- Repository management
- Workspace health monitoring
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from .workspace_manager import WorkspaceManager
from .code_analyzer import CodeAnalyzer
from .repository_ingestor import RepositoryIngestor

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceOperationResult:
    """Result structure for workspace operations"""
    success: bool
    data: Any = None
    error: str = None
    metadata: Dict[str, Any] = None

class WorkspaceOperations:
    """
    High-level workspace operations interface
    
    This class provides a unified interface for all workspace-related operations,
    combining functionality from WorkspaceManager, CodeAnalyzer, and RepositoryIngestor.
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.workspace_manager = None
        self.code_analyzer = None
        self.repository_ingestor = None
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all workspace components"""
        try:
            logger.info("Initializing workspace operations...")
            
            # Initialize workspace manager
            self.workspace_manager = WorkspaceManager(str(self.workspace_path))
            
            # Initialize code analyzer
            self.code_analyzer = CodeAnalyzer()
            await self.code_analyzer.initialize()
            
            # Initialize repository ingestor
            self.repository_ingestor = RepositoryIngestor()
            await self.repository_ingestor.initialize()
            
            self.initialized = True
            logger.info("Workspace operations initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace operations: {e}")
            return False
    
    async def read_file(self, file_path: str) -> WorkspaceOperationResult:
        """
        Read file content with metadata
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            WorkspaceOperationResult with file content and metadata
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.read_file(file_path)
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result['content'],
                    metadata=result['metadata']
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in read_file operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def write_file(self, file_path: str, content: str, 
                        overwrite: bool = True) -> WorkspaceOperationResult:
        """
        Write content to file
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            overwrite: Whether to overwrite existing file
            
        Returns:
            WorkspaceOperationResult with operation status
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.write_file(file_path, content, overwrite)
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result.get('file_info'),
                    metadata={'bytes_written': len(content)}
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in write_file operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def list_files(self, directory: str = ".", 
                        include_hidden: bool = False) -> WorkspaceOperationResult:
        """
        List files in directory
        
        Args:
            directory: Directory to list files from
            include_hidden: Whether to include hidden files
            
        Returns:
            WorkspaceOperationResult with file list
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.scan_workspace(include_hidden)
            
            if result['success']:
                # Filter for specific directory if requested
                if directory != ".":
                    target_path = Path(directory)
                    files = [
                        f for f in result['files'] 
                        if Path(f['path']).parent == target_path
                    ]
                else:
                    files = result['files']
                
                return WorkspaceOperationResult(
                    success=True,
                    data=files,
                    metadata={
                        'total_files': len(files),
                        'directory': directory
                    }
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in list_files operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def analyze_code(self, file_path: str) -> WorkspaceOperationResult:
        """
        Analyze code structure and metrics
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            WorkspaceOperationResult with code analysis
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.code_analyzer.analyze_code(file_path)
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result['analysis'],
                    metadata=result.get('metadata', {})
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in analyze_code operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def get_workspace_health(self) -> WorkspaceOperationResult:
        """
        Get workspace health information
        
        Returns:
            WorkspaceOperationResult with workspace health data
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.get_workspace_health()
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result['health'],
                    metadata=result.get('metadata', {})
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in get_workspace_health operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def delete_file(self, file_path: str) -> WorkspaceOperationResult:
        """
        Delete a file
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            WorkspaceOperationResult with operation status
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.delete_file(file_path)
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result.get('file_info'),
                    metadata={'deleted': True}
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in delete_file operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def get_file_info(self, file_path: str) -> WorkspaceOperationResult:
        """
        Get detailed file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            WorkspaceOperationResult with file information
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            result = await self.workspace_manager.get_file_info(file_path)
            
            if result['success']:
                return WorkspaceOperationResult(
                    success=True,
                    data=result['file_info'],
                    metadata=result.get('metadata', {})
                )
            else:
                return WorkspaceOperationResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error in get_file_info operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def search_files(self, pattern: str, 
                          file_types: List[str] = None) -> WorkspaceOperationResult:
        """
        Search for files matching pattern
        
        Args:
            pattern: Search pattern (filename or content)
            file_types: List of file extensions to search in
            
        Returns:
            WorkspaceOperationResult with matching files
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Get all files first
            files_result = await self.list_files()
            if not files_result.success:
                return files_result
            
            matching_files = []
            pattern_lower = pattern.lower()
            
            for file_info in files_result.data:
                file_path = file_info['path']
                file_name = Path(file_path).name
                
                # Check file type filter
                if file_types:
                    file_ext = Path(file_path).suffix
                    if file_ext not in file_types:
                        continue
                
                # Check filename match
                if pattern_lower in file_name.lower():
                    matching_files.append(file_info)
                    continue
                
                # Check content match (for text files)
                if file_info.get('file_type') in ['.txt', '.md', '.py', '.js', '.json']:
                    try:
                        content_result = await self.read_file(file_path)
                        if content_result.success and pattern_lower in content_result.data.lower():
                            matching_files.append(file_info)
                    except:
                        pass  # Skip files that can't be read
            
            return WorkspaceOperationResult(
                success=True,
                data=matching_files,
                metadata={
                    'pattern': pattern,
                    'file_types': file_types,
                    'matches': len(matching_files)
                }
            )
                
        except Exception as e:
            logger.error(f"Error in search_files operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )
    
    async def get_workspace_stats(self) -> WorkspaceOperationResult:
        """
        Get comprehensive workspace statistics
        
        Returns:
            WorkspaceOperationResult with workspace statistics
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Get workspace health
            health_result = await self.get_workspace_health()
            
            # Get file listing
            files_result = await self.list_files()
            
            if not health_result.success or not files_result.success:
                return WorkspaceOperationResult(
                    success=False,
                    error="Failed to gather workspace statistics"
                )
            
            # Calculate additional stats
            total_files = len(files_result.data)
            total_size = sum(f.get('size', 0) for f in files_result.data)
            
            # Group by file type
            file_types = {}
            for file_info in files_result.data:
                file_type = file_info.get('file_type', 'unknown')
                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1
            
            stats = {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'file_types': file_types,
                'health': health_result.data,
                'workspace_path': str(self.workspace_path)
            }
            
            return WorkspaceOperationResult(
                success=True,
                data=stats,
                metadata={'generated_at': asyncio.get_event_loop().time()}
            )
                
        except Exception as e:
            logger.error(f"Error in get_workspace_stats operation: {e}")
            return WorkspaceOperationResult(
                success=False,
                error=str(e)
            )

# Convenience functions for direct use
async def read_file(file_path: str, workspace_path: str = None) -> WorkspaceOperationResult:
    """Convenience function to read a file"""
    ops = WorkspaceOperations(workspace_path)
    return await ops.read_file(file_path)

async def write_file(file_path: str, content: str, workspace_path: str = None) -> WorkspaceOperationResult:
    """Convenience function to write a file"""
    ops = WorkspaceOperations(workspace_path)
    return await ops.write_file(file_path, content)

async def list_files(directory: str = ".", workspace_path: str = None) -> WorkspaceOperationResult:
    """Convenience function to list files"""
    ops = WorkspaceOperations(workspace_path)
    return await ops.list_files(directory)

async def analyze_code(file_path: str, workspace_path: str = None) -> WorkspaceOperationResult:
    """Convenience function to analyze code"""
    ops = WorkspaceOperations(workspace_path)
    return await ops.analyze_code(file_path)

if __name__ == "__main__":
    """Test the workspace operations"""
    async def test_workspace_operations():
        print("Testing workspace operations...")
        
        ops = WorkspaceOperations()
        await ops.initialize()
        
        # Test file listing
        result = await ops.list_files()
        if result.success:
            print(f"Found {len(result.data)} files in workspace")
        else:
            print(f"Error listing files: {result.error}")
        
        # Test workspace stats
        stats_result = await ops.get_workspace_stats()
        if stats_result.success:
            print(f"Workspace stats: {json.dumps(stats_result.data, indent=2)}")
        else:
            print(f"Error getting stats: {stats_result.error}")
    
    asyncio.run(test_workspace_operations()) 