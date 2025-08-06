"""
Workspace Manager - Core file operations and workspace management
"""

import os
import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """File information structure"""
    path: str
    size: int
    modified_time: float
    file_type: str
    content_hash: str

class WorkspaceManager:
    """
    Manages workspace operations including file read/write, 
    directory scanning, and workspace health monitoring
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini',
            '.html', '.css', '.scss', '.sql', '.sh', '.bat', '.ps1'
        }
        self.file_cache = {}
        self.workspace_stats = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the workspace manager
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info(f"Initializing workspace manager for path: {self.workspace_path}")
            
            # Ensure workspace directory exists
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Clear cache and stats
            self.file_cache.clear()
            self.workspace_stats.clear()
            
            # Perform initial workspace scan
            scan_result = await self.scan_workspace()
            if scan_result['success']:
                self.workspace_stats['initial_scan'] = {
                    'total_files': len(scan_result['files']),
                    'scan_time': asyncio.get_event_loop().time()
                }
            
            self.initialized = True
            logger.info("Workspace manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace manager: {e}")
            return False
        
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file and return its content with metadata
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dictionary containing file content and metadata
        """
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "content": None,
                    "metadata": None
                }
            
            # Read file content
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Get file metadata
            stat = full_path.stat()
            file_info = FileInfo(
                path=str(full_path),
                size=stat.st_size,
                modified_time=stat.st_mtime,
                file_type=full_path.suffix,
                content_hash=str(hash(content))
            )
            
            return {
                "success": True,
                "content": content,
                "metadata": {
                    "path": file_info.path,
                    "size": file_info.size,
                    "modified_time": file_info.modified_time,
                    "file_type": file_info.file_type,
                    "content_hash": file_info.content_hash
                }
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "metadata": None
            }
    
    async def read_file_simple(self, file_path: str) -> str:
        """
        Read a file and return its content as a string
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
        """
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise

    async def list_files(self, directory: str = ".") -> List[str]:
        """
        List files in a directory
        
        Args:
            directory: Directory to list files from (relative to workspace)
            
        Returns:
            List of file paths
        """
        try:
            target_path = self.workspace_path / directory
            
            if not target_path.exists():
                return []
            
            if not target_path.is_dir():
                return []
            
            files = []
            for item in target_path.iterdir():
                if item.is_file():
                    files.append(str(item))
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            return []

    async def write_file(self, file_path: str, content: str, 
                        overwrite: bool = True) -> Dict[str, Any]:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary containing operation result
        """
        try:
            full_path = self.workspace_path / file_path
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and overwrite flag
            if full_path.exists() and not overwrite:
                return {
                    "success": False,
                    "error": f"File already exists: {file_path}",
                    "path": str(full_path)
                }
            
            # Write file content
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            # Update cache
            self.file_cache[str(full_path)] = {
                "content": content,
                "hash": str(hash(content)),
                "modified": full_path.stat().st_mtime
            }
            
            return {
                "success": True,
                "path": str(full_path),
                "size": len(content),
                "message": "File written successfully"
            }
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "path": str(full_path) if 'full_path' in locals() else None
            }
    
    async def scan_workspace(self, include_hidden: bool = False) -> Dict[str, Any]:
        """
        Scan the workspace and return file structure
        
        Args:
            include_hidden: Whether to include hidden files
            
        Returns:
            Dictionary containing workspace structure
        """
        try:
            files = []
            directories = []
            
            for item in self.workspace_path.rglob('*'):
                if item.is_file():
                    # Skip hidden files if not requested
                    if not include_hidden and any(part.startswith('.') for part in item.parts):
                        continue
                    
                    # Skip unsupported file types
                    if item.suffix not in self.supported_extensions:
                        continue
                    
                    stat = item.stat()
                    files.append({
                        "path": str(item.relative_to(self.workspace_path)),
                        "size": stat.st_size,
                        "modified_time": stat.st_mtime,
                        "file_type": item.suffix
                    })
                
                elif item.is_dir():
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    directories.append(str(item.relative_to(self.workspace_path)))
            
            self.workspace_stats = {
                "total_files": len(files),
                "total_directories": len(directories),
                "workspace_size": sum(f["size"] for f in files),
                "last_scan": asyncio.get_event_loop().time()
            }
            
            return {
                "success": True,
                "workspace_path": str(self.workspace_path),
                "files": files,
                "directories": directories,
                "stats": self.workspace_stats
            }
            
        except Exception as e:
            logger.error(f"Error scanning workspace: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workspace_path": str(self.workspace_path)
            }
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            stat = full_path.stat()
            
            # Read first few lines for preview
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                preview_lines = content.split('\n')[:10]
                preview = '\n'.join(preview_lines)
            
            return {
                "success": True,
                "path": str(full_path),
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "file_type": full_path.suffix,
                "content_hash": str(hash(content)),
                "line_count": len(content.split('\n')),
                "preview": preview,
                "is_binary": False  # We only handle text files
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file from the workspace
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Dictionary containing operation result
        """
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Remove from cache if present
            if str(full_path) in self.file_cache:
                del self.file_cache[str(full_path)]
            
            # Delete the file
            full_path.unlink()
            
            return {
                "success": True,
                "path": str(full_path),
                "message": "File deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workspace_health(self) -> Dict[str, Any]:
        """
        Get workspace health metrics
        
        Returns:
            Dictionary containing workspace health information
        """
        try:
            # Scan workspace if stats are not available
            if not self.workspace_stats:
                await self.scan_workspace()
            
            # Calculate health metrics
            total_size_mb = self.workspace_stats["workspace_size"] / (1024 * 1024)
            
            health_score = 100
            issues = []
            
            # Check for large files
            if total_size_mb > 100:  # More than 100MB
                health_score -= 20
                issues.append("Workspace size is large")
            
            # Check for many files
            if self.workspace_stats["total_files"] > 1000:
                health_score -= 15
                issues.append("Many files in workspace")
            
            # Check cache efficiency
            cache_hit_rate = len(self.file_cache) / max(self.workspace_stats["total_files"], 1)
            if cache_hit_rate < 0.1:
                health_score -= 10
                issues.append("Low cache efficiency")
            
            return {
                "success": True,
                "health_score": max(health_score, 0),
                "total_files": self.workspace_stats["total_files"],
                "total_directories": self.workspace_stats["total_directories"],
                "workspace_size_mb": round(total_size_mb, 2),
                "cache_size": len(self.file_cache),
                "cache_hit_rate": round(cache_hit_rate, 3),
                "issues": issues,
                "last_scan": self.workspace_stats.get("last_scan", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace health: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """
        Cleanup resources and reset state
        """
        try:
            # Clear cache
            self.file_cache.clear()
            self.workspace_stats.clear()
            self.initialized = False
            logger.info("Workspace manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during workspace manager cleanup: {e}") 