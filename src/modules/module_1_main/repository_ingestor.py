"""
Repository Ingestor - Handles repository cloning, analysis, and management
"""

import asyncio
import subprocess
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class RepositoryInfo:
    """Repository information structure"""
    name: str
    url: str
    local_path: str
    branch: str
    commit_hash: str
    file_count: int
    size_bytes: int
    languages: List[str]

class RepositoryIngestor:
    """
    Handles repository ingestion including cloning, analysis, and management
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd() / "repositories"
        self.base_path.mkdir(exist_ok=True)
        self.repositories = {}
        self.analysis_cache = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the repository ingestor
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info(f"Initializing repository ingestor for base path: {self.base_path}")
            
            # Ensure base directory exists
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Clear caches
            self.repositories.clear()
            self.analysis_cache.clear()
            
            # Scan for existing repositories
            if self.base_path.exists():
                for repo_dir in self.base_path.iterdir():
                    if repo_dir.is_dir() and (repo_dir / ".git").exists():
                        try:
                            repo_info = await self._get_repository_info(
                                repo_dir, 
                                f"local/{repo_dir.name}", 
                                "main"
                            )
                            self.repositories[repo_dir.name] = repo_info
                            logger.info(f"Found existing repository: {repo_dir.name}")
                        except Exception as e:
                            logger.warning(f"Could not load repository {repo_dir.name}: {e}")
            
            self.initialized = True
            logger.info("Repository ingestor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize repository ingestor: {e}")
            return False
        
    async def clone_repository(self, repo_url: str, branch: str = "main", 
                             depth: int = None) -> Dict[str, Any]:
        """
        Clone a repository from URL
        
        Args:
            repo_url: Git repository URL
            branch: Branch to clone (default: main)
            depth: Clone depth for shallow clone
            
        Returns:
            Dictionary containing clone operation result
        """
        try:
            # Extract repository name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            local_path = self.base_path / repo_name
            
            # Check if repository already exists
            if local_path.exists():
                return {
                    "success": False,
                    "error": f"Repository already exists: {repo_name}",
                    "local_path": str(local_path)
                }
            
            # Prepare git clone command
            cmd = ["git", "clone"]
            if depth:
                cmd.extend(["--depth", str(depth)])
            cmd.extend(["-b", branch, repo_url, str(local_path)])
            
            # Execute clone command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git clone failed: {stderr.decode()}",
                    "repo_url": repo_url,
                    "branch": branch
                }
            
            # Get repository information
            repo_info = await self._get_repository_info(local_path, repo_url, branch)
            
            # Store repository info
            self.repositories[repo_name] = repo_info
            
            return {
                "success": True,
                "repo_name": repo_name,
                "local_path": str(local_path),
                "branch": branch,
                "info": repo_info.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error cloning repository {repo_url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }
    
    async def _get_repository_info(self, local_path: Path, repo_url: str, 
                                  branch: str) -> RepositoryInfo:
        """
        Get detailed information about a repository
        
        Args:
            local_path: Local path to the repository
            repo_url: Original repository URL
            branch: Current branch
            
        Returns:
            RepositoryInfo object
        """
        try:
            # Get current commit hash
            process = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD",
                cwd=str(local_path),
                stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            commit_hash = stdout.decode().strip()
            
            # Count files
            file_count = 0
            size_bytes = 0
            languages = set()
            
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    size_bytes += file_path.stat().st_size
                    
                    # Detect language from file extension
                    ext = file_path.suffix.lower()
                    if ext in ['.py']:
                        languages.add('Python')
                    elif ext in ['.js', '.ts']:
                        languages.add('JavaScript/TypeScript')
                    elif ext in ['.java']:
                        languages.add('Java')
                    elif ext in ['.cpp', '.c', '.h', '.hpp']:
                        languages.add('C/C++')
                    elif ext in ['.go']:
                        languages.add('Go')
                    elif ext in ['.rs']:
                        languages.add('Rust')
                    elif ext in ['.php']:
                        languages.add('PHP')
                    elif ext in ['.rb']:
                        languages.add('Ruby')
                    elif ext in ['.cs']:
                        languages.add('C#')
                    elif ext in ['.swift']:
                        languages.add('Swift')
                    elif ext in ['.kt']:
                        languages.add('Kotlin')
            
            return RepositoryInfo(
                name=local_path.name,
                url=repo_url,
                local_path=str(local_path),
                branch=branch,
                commit_hash=commit_hash,
                file_count=file_count,
                size_bytes=size_bytes,
                languages=list(languages)
            )
            
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            # Return basic info if detailed analysis fails
            return RepositoryInfo(
                name=local_path.name,
                url=repo_url,
                local_path=str(local_path),
                branch=branch,
                commit_hash="unknown",
                file_count=0,
                size_bytes=0,
                languages=[]
            )
    
    async def analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """
        Perform detailed analysis of a repository
        
        Args:
            repo_name: Name of the repository to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if repo_name not in self.repositories:
                return {
                    "success": False,
                    "error": f"Repository not found: {repo_name}"
                }
            
            repo_info = self.repositories[repo_name]
            local_path = Path(repo_info.local_path)
            
            # Check if analysis is cached
            cache_key = f"{repo_name}_{repo_info.commit_hash}"
            if cache_key in self.analysis_cache:
                return {
                    "success": True,
                    "cached": True,
                    "analysis": self.analysis_cache[cache_key]
                }
            
            # Perform analysis
            analysis = {
                "file_types": {},
                "largest_files": [],
                "recent_changes": [],
                "dependencies": {},
                "structure": {},
                "metrics": {}
            }
            
            # Analyze file types and sizes
            file_sizes = []
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    size = file_path.stat().st_size
                    
                    # Count file types
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    # Track file sizes
                    file_sizes.append((str(file_path.relative_to(local_path)), size))
            
            # Get largest files
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            analysis["largest_files"] = file_sizes[:10]
            
            # Analyze directory structure
            analysis["structure"] = await self._analyze_directory_structure(local_path)
            
            # Detect dependencies
            analysis["dependencies"] = await self._detect_dependencies(local_path)
            
            # Calculate metrics
            analysis["metrics"] = {
                "total_files": len(file_sizes),
                "total_size_mb": sum(size for _, size in file_sizes) / (1024 * 1024),
                "average_file_size_kb": sum(size for _, size in file_sizes) / len(file_sizes) / 1024 if file_sizes else 0,
                "file_type_diversity": len(analysis["file_types"]),
                "depth": max(len(Path(f).parts) for f, _ in file_sizes) if file_sizes else 0
            }
            
            # Cache analysis
            self.analysis_cache[cache_key] = analysis
            
            return {
                "success": True,
                "cached": False,
                "repo_name": repo_name,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo_name": repo_name
            }
    
    async def _analyze_directory_structure(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze the directory structure of a repository
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary containing directory structure analysis
        """
        structure = {
            "directories": [],
            "depth_stats": {},
            "common_patterns": []
        }
        
        try:
            # Get all directories
            for item in repo_path.rglob('*'):
                if item.is_dir():
                    rel_path = str(item.relative_to(repo_path))
                    depth = len(item.relative_to(repo_path).parts)
                    
                    structure["directories"].append({
                        "path": rel_path,
                        "depth": depth,
                        "name": item.name
                    })
                    
                    # Count depth distribution
                    structure["depth_stats"][depth] = structure["depth_stats"].get(depth, 0) + 1
            
            # Find common directory patterns
            dir_names = [d["name"] for d in structure["directories"]]
            from collections import Counter
            common_dirs = Counter(dir_names).most_common(10)
            structure["common_patterns"] = [{"name": name, "count": count} for name, count in common_dirs]
            
        except Exception as e:
            logger.error(f"Error analyzing directory structure: {str(e)}")
        
        return structure
    
    async def _detect_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """
        Detect dependencies in the repository
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary containing detected dependencies
        """
        dependencies = {
            "python": [],
            "javascript": [],
            "java": [],
            "other": []
        }
        
        try:
            # Python dependencies
            requirements_files = list(repo_path.glob("**/requirements*.txt"))
            for req_file in requirements_files:
                async with aiofiles.open(req_file, 'r') as f:
                    content = await f.read()
                    deps = [line.strip() for line in content.split('\n') 
                           if line.strip() and not line.startswith('#')]
                    dependencies["python"].extend(deps)
            
            # JavaScript dependencies
            package_files = list(repo_path.glob("**/package.json"))
            for pkg_file in package_files:
                async with aiofiles.open(pkg_file, 'r') as f:
                    content = await f.read()
                    try:
                        pkg_data = json.loads(content)
                        if "dependencies" in pkg_data:
                            dependencies["javascript"].extend(list(pkg_data["dependencies"].keys()))
                        if "devDependencies" in pkg_data:
                            dependencies["javascript"].extend(list(pkg_data["devDependencies"].keys()))
                    except json.JSONDecodeError:
                        pass
            
            # Java dependencies (Maven)
            pom_files = list(repo_path.glob("**/pom.xml"))
            for pom_file in pom_files:
                # Basic Maven dependency detection
                async with aiofiles.open(pom_file, 'r') as f:
                    content = await f.read()
                    if "<dependency>" in content:
                        dependencies["java"].append("Maven dependencies detected")
            
        except Exception as e:
            logger.error(f"Error detecting dependencies: {str(e)}")
        
        return dependencies
    
    async def list_repositories(self) -> Dict[str, Any]:
        """
        List all ingested repositories
        
        Returns:
            Dictionary containing list of repositories
        """
        try:
            repos = []
            for repo_name, repo_info in self.repositories.items():
                repos.append({
                    "name": repo_name,
                    "url": repo_info.url,
                    "local_path": repo_info.local_path,
                    "branch": repo_info.branch,
                    "commit_hash": repo_info.commit_hash,
                    "file_count": repo_info.file_count,
                    "size_mb": repo_info.size_bytes / (1024 * 1024),
                    "languages": repo_info.languages
                })
            
            return {
                "success": True,
                "repositories": repos,
                "total_count": len(repos)
            }
            
        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def remove_repository(self, repo_name: str) -> Dict[str, Any]:
        """
        Remove a repository from the system
        
        Args:
            repo_name: Name of the repository to remove
            
        Returns:
            Dictionary containing removal operation result
        """
        try:
            if repo_name not in self.repositories:
                return {
                    "success": False,
                    "error": f"Repository not found: {repo_name}"
                }
            
            repo_info = self.repositories[repo_name]
            local_path = Path(repo_info.local_path)
            
            # Remove from cache
            cache_keys = [key for key in self.analysis_cache.keys() if key.startswith(repo_name)]
            for key in cache_keys:
                del self.analysis_cache[key]
            
            # Remove from repositories dict
            del self.repositories[repo_name]
            
            # Remove local files
            if local_path.exists():
                import shutil
                shutil.rmtree(local_path)
            
            return {
                "success": True,
                "repo_name": repo_name,
                "message": "Repository removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing repository {repo_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo_name": repo_name
            } 