"""
Memory Manager - Manages memory and caching operations
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry structure"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int
    last_accessed: datetime
    size_bytes: int

class MemoryManager:
    """
    Manages memory and caching operations
    """
    
    def __init__(self, cache_dir: str = None, max_memory_mb: int = 1000):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_memory_mb = max_memory_mb
        self.memory_cache = {}
        self.disk_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size_mb": 0
        }
        self.cleanup_task = None
    
    async def initialize(self) -> None:
        """Initialize the memory manager"""
        try:
            logger.info("Initializing memory manager...")
            # Clear existing data
            self.memory_cache = {}
            self.disk_cache = {}
            self.cache_stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "total_size_mb": 0
            }
            
            # Ensure cache directory exists
            self.cache_dir.mkdir(exist_ok=True)
            
            logger.info("Memory manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            raise
        
    async def start(self) -> Dict[str, Any]:
        """
        Start the memory manager
        
        Returns:
            Dictionary containing start result
        """
        try:
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            return {
                "success": True,
                "message": "Memory manager started successfully",
                "cache_dir": str(self.cache_dir),
                "max_memory_mb": self.max_memory_mb
            }
            
        except Exception as e:
            logger.error(f"Error starting memory manager: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop(self) -> Dict[str, Any]:
        """
        Stop the memory manager
        
        Returns:
            Dictionary containing stop result
        """
        try:
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            return {
                "success": True,
                "message": "Memory manager stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping memory manager: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_cache(self, key: str, value: Any, ttl_seconds: int = None,
                       use_disk: bool = False) -> Dict[str, Any]:
        """
        Set a value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (None = no expiration)
            use_disk: Whether to use disk cache
            
        Returns:
            Dictionary containing set result
        """
        try:
            # Generate cache key hash
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            # Calculate value size
            value_size = len(json.dumps(value).encode())
            
            # Create cache entry
            created_at = datetime.now()
            expires_at = None
            if ttl_seconds:
                expires_at = created_at + timedelta(seconds=ttl_seconds)
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=created_at,
                expires_at=expires_at,
                access_count=0,
                last_accessed=created_at,
                size_bytes=value_size
            )
            
            if use_disk:
                # Store in disk cache
                await self._store_disk_cache(key_hash, entry)
            else:
                # Store in memory cache
                await self._store_memory_cache(key_hash, entry)
            
            return {
                "success": True,
                "key": key,
                "key_hash": key_hash,
                "size_bytes": value_size,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_cache(self, key: str, use_disk: bool = False) -> Dict[str, Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
            use_disk: Whether to check disk cache
            
        Returns:
            Dictionary containing get result
        """
        try:
            # Generate cache key hash
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            # Check memory cache first
            if key_hash in self.memory_cache:
                entry = self.memory_cache[key_hash]
                if await self._is_entry_valid(entry):
                    await self._update_entry_access(entry)
                    self.cache_stats["hits"] += 1
                    return {
                        "success": True,
                        "value": entry.value,
                        "source": "memory",
                        "access_count": entry.access_count,
                        "created_at": entry.created_at.isoformat()
                    }
            
            # Check disk cache if requested
            if use_disk and key_hash in self.disk_cache:
                entry = await self._load_disk_cache(key_hash)
                if entry and await self._is_entry_valid(entry):
                    await self._update_entry_access(entry)
                    self.cache_stats["hits"] += 1
                    return {
                        "success": True,
                        "value": entry.value,
                        "source": "disk",
                        "access_count": entry.access_count,
                        "created_at": entry.created_at.isoformat()
                    }
            
            self.cache_stats["misses"] += 1
            return {
                "success": False,
                "error": "Cache key not found or expired"
            }
            
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_cache(self, key: str) -> Dict[str, Any]:
        """
        Delete a value from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            Dictionary containing delete result
        """
        try:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            deleted = False
            
            # Remove from memory cache
            if key_hash in self.memory_cache:
                entry = self.memory_cache[key_hash]
                self.cache_stats["total_size_mb"] -= entry.size_bytes / (1024 * 1024)
                del self.memory_cache[key_hash]
                deleted = True
            
            # Remove from disk cache
            disk_cache_file = self.cache_dir / f"{key_hash}.cache"
            if disk_cache_file.exists():
                disk_cache_file.unlink()
                if key_hash in self.disk_cache:
                    del self.disk_cache[key_hash]
                deleted = True
            
            return {
                "success": True,
                "deleted": deleted,
                "message": "Cache entry deleted" if deleted else "Cache entry not found"
            }
            
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def clear_cache(self, cache_type: str = "all") -> Dict[str, Any]:
        """
        Clear cache
        
        Args:
            cache_type: Type of cache to clear ("memory", "disk", "all")
            
        Returns:
            Dictionary containing clear result
        """
        try:
            cleared_count = 0
            
            if cache_type in ["memory", "all"]:
                cleared_count += len(self.memory_cache)
                self.memory_cache.clear()
                self.cache_stats["total_size_mb"] = 0
            
            if cache_type in ["disk", "all"]:
                # Clear disk cache files
                cache_files = list(self.cache_dir.glob("*.cache"))
                for cache_file in cache_files:
                    cache_file.unlink()
                    cleared_count += 1
                self.disk_cache.clear()
            
            return {
                "success": True,
                "cleared_count": cleared_count,
                "cache_type": cache_type
            }
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            # Calculate hit rate
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate memory usage
            memory_entries = len(self.memory_cache)
            disk_entries = len(self.disk_cache)
            
            return {
                "success": True,
                "stats": {
                    "hits": self.cache_stats["hits"],
                    "misses": self.cache_stats["misses"],
                    "hit_rate_percent": round(hit_rate, 2),
                    "evictions": self.cache_stats["evictions"],
                    "total_size_mb": round(self.cache_stats["total_size_mb"], 2),
                    "memory_entries": memory_entries,
                    "disk_entries": disk_entries,
                    "max_memory_mb": self.max_memory_mb
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _store_memory_cache(self, key_hash: str, entry: CacheEntry):
        """Store entry in memory cache"""
        # Check if we need to evict entries
        current_size_mb = self.cache_stats["total_size_mb"]
        entry_size_mb = entry.size_bytes / (1024 * 1024)
        
        if current_size_mb + entry_size_mb > self.max_memory_mb:
            await self._evict_memory_cache(entry_size_mb)
        
        self.memory_cache[key_hash] = entry
        self.cache_stats["total_size_mb"] += entry_size_mb
    
    async def _store_disk_cache(self, key_hash: str, entry: CacheEntry):
        """Store entry in disk cache"""
        cache_file = self.cache_dir / f"{key_hash}.cache"
        
        # Serialize entry
        entry_data = {
            "key": entry.key,
            "value": entry.value,
            "created_at": entry.created_at.isoformat(),
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed.isoformat(),
            "size_bytes": entry.size_bytes
        }
        
        async with aiofiles.open(cache_file, 'w') as f:
            await f.write(json.dumps(entry_data))
        
        self.disk_cache[key_hash] = entry
    
    async def _load_disk_cache(self, key_hash: str) -> Optional[CacheEntry]:
        """Load entry from disk cache"""
        try:
            cache_file = self.cache_dir / f"{key_hash}.cache"
            
            if not cache_file.exists():
                return None
            
            async with aiofiles.open(cache_file, 'r') as f:
                content = await f.read()
                entry_data = json.loads(content)
            
            return CacheEntry(
                key=entry_data["key"],
                value=entry_data["value"],
                created_at=datetime.fromisoformat(entry_data["created_at"]),
                expires_at=datetime.fromisoformat(entry_data["expires_at"]) if entry_data["expires_at"] else None,
                access_count=entry_data["access_count"],
                last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                size_bytes=entry_data["size_bytes"]
            )
            
        except Exception as e:
            logger.error(f"Error loading disk cache: {str(e)}")
            return None
    
    async def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is valid (not expired)"""
        if entry.expires_at and datetime.now() > entry.expires_at:
            return False
        return True
    
    async def _update_entry_access(self, entry: CacheEntry):
        """Update entry access statistics"""
        entry.access_count += 1
        entry.last_accessed = datetime.now()
    
    async def _evict_memory_cache(self, required_size_mb: float):
        """Evict entries from memory cache to make space"""
        # Sort entries by access count and last accessed time
        entries = list(self.memory_cache.items())
        entries.sort(key=lambda x: (x[1].access_count, x[1].last_accessed))
        
        freed_size_mb = 0
        evicted_count = 0
        
        for key_hash, entry in entries:
            if freed_size_mb >= required_size_mb:
                break
            
            entry_size_mb = entry.size_bytes / (1024 * 1024)
            freed_size_mb += entry_size_mb
            self.cache_stats["total_size_mb"] -= entry_size_mb
            del self.memory_cache[key_hash]
            evicted_count += 1
        
        self.cache_stats["evictions"] += evicted_count
    
    async def _cleanup_loop(self):
        """Periodic cleanup loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up expired entries
                await self._cleanup_expired_entries()
                
                # Clean up old disk cache files
                await self._cleanup_old_disk_files()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        
        # Clean memory cache
        expired_keys = []
        for key_hash, entry in self.memory_cache.items():
            if not await self._is_entry_valid(entry):
                expired_keys.append(key_hash)
        
        for key_hash in expired_keys:
            entry = self.memory_cache[key_hash]
            self.cache_stats["total_size_mb"] -= entry.size_bytes / (1024 * 1024)
            del self.memory_cache[key_hash]
        
        # Clean disk cache
        expired_disk_keys = []
        for key_hash in self.disk_cache:
            entry = self.disk_cache[key_hash]
            if not await self._is_entry_valid(entry):
                expired_disk_keys.append(key_hash)
        
        for key_hash in expired_disk_keys:
            cache_file = self.cache_dir / f"{key_hash}.cache"
            if cache_file.exists():
                cache_file.unlink()
            del self.disk_cache[key_hash]
    
    async def _cleanup_old_disk_files(self):
        """Clean up old disk cache files"""
        try:
            # Remove files older than 7 days
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for cache_file in self.cache_dir.glob("*.cache"):
                if cache_file.stat().st_mtime < cutoff_time.timestamp():
                    cache_file.unlink()
                    
                    # Remove from disk cache dict if present
                    key_hash = cache_file.stem
                    if key_hash in self.disk_cache:
                        del self.disk_cache[key_hash]
                        
        except Exception as e:
            logger.error(f"Error cleaning up old disk files: {str(e)}") 