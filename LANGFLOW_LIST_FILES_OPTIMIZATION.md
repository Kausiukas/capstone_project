# 🔧 LangFlow List Files Optimization Guide

## 🎯 **Problem Analysis**

### **Current Issue**:
The `list_files` tool is trying to load all 130,179 files from the repository into memory at once, causing memory overflow when used in LangFlow.

### **Root Cause**:
```python
# Current implementation - loads everything into memory
async def handle_list_files(self, args: Dict[str, Any]) -> str:
    directory = args.get("directory", ".")
    try:
        files = []  # ❌ Loads ALL files into memory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            files.append({
                "name": item,
                "is_file": os.path.isfile(item_path),
                "is_dir": os.path.isdir(item_path)
            })
        return f"Directory contents:\n{json.dumps(files, indent=2)}"  # ❌ Returns everything
    except Exception as e:
        return f"Error listing directory: {str(e)}"
```

---

## 📊 **Repository Analysis**

### **Current Repository Size**:
- **Total Files**: 130,179 files
- **Memory Impact**: ~50-100MB+ when loaded entirely
- **LangFlow Limit**: Exceeds available memory for chat output

### **Memory Usage Estimation**:
- **Per File Entry**: ~200-500 bytes (name, path, metadata)
- **Total Memory**: 130,179 × 400 bytes = ~52MB
- **JSON Serialization**: Additional 50-100% overhead
- **Total Estimated**: 75-150MB per request

---

## 🚀 **Optimization Strategy**

### **1. Batching Implementation**
- **Batch Size**: 50-100 files per batch
- **Pagination**: Support for offset/limit parameters
- **Memory Limit**: Max 5MB per response

### **2. Smart Filtering**
- **File Type Filtering**: Only show specific extensions
- **Directory Depth**: Limit recursion depth
- **Size Filtering**: Skip large files

### **3. Memory Management**
- **Streaming**: Process files in chunks
- **Caching**: Cache directory listings
- **Cleanup**: Immediate memory cleanup

---

## 🔧 **Implementation Plan**

### **Step 1: Enhanced List Files Tool**

#### **1.1 Updated Tool Definition**
```python
{
    "name": "list_files",
    "description": "List files in a directory with batching and filtering",
    "inputSchema": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path to list files from",
                "default": "."
            },
            "batch_size": {
                "type": "integer",
                "description": "Number of files to return per batch (10-100)",
                "default": 50,
                "minimum": 10,
                "maximum": 100
            },
            "offset": {
                "type": "integer",
                "description": "Starting position for pagination",
                "default": 0,
                "minimum": 0
            },
            "file_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by file extensions (e.g., ['.py', '.txt'])",
                "default": []
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum directory depth to traverse",
                "default": 1,
                "minimum": 1,
                "maximum": 5
            },
            "include_hidden": {
                "type": "boolean",
                "description": "Include hidden files and directories",
                "default": false
            },
            "sort_by": {
                "type": "string",
                "enum": ["name", "size", "modified", "type"],
                "description": "Sort files by criteria",
                "default": "name"
            },
            "sort_order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "Sort order",
                "default": "asc"
            }
        },
        "required": ["directory"]
    }
}
```

#### **1.2 Optimized Implementation**
```python
import os
import json
import time
from typing import Dict, Any, List, Generator
from pathlib import Path
import psutil

class OptimizedFileLister:
    """Optimized file listing with batching and memory management"""
    
    def __init__(self, max_memory_mb: int = 50):
        self.max_memory_mb = max_memory_mb
        self.memory_manager = None  # Will integrate with existing MemoryManager
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def should_stop_processing(self) -> bool:
        """Check if we should stop processing due to memory constraints"""
        return self.get_memory_usage() > self.max_memory_mb
    
    def file_generator(self, directory: str, max_depth: int = 1, 
                      include_hidden: bool = False, file_types: List[str] = None) -> Generator[Dict, None, None]:
        """Generate file entries one at a time to minimize memory usage"""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return
            
            for root, dirs, files in os.walk(directory):
                # Calculate current depth
                depth = root.replace(directory, '').count(os.sep)
                if depth > max_depth:
                    continue
                
                # Filter hidden files/directories
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    files = [f for f in files if not f.startswith('.')]
                
                # Process files
                for file in files:
                    file_path = Path(root) / file
                    
                    # Filter by file type
                    if file_types and file_path.suffix.lower() not in file_types:
                        continue
                    
                    try:
                        stat = file_path.stat()
                        yield {
                            "name": file,
                            "path": str(file_path.relative_to(directory_path)),
                            "is_file": True,
                            "is_dir": False,
                            "size_bytes": stat.st_size,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified": stat.st_mtime,
                            "extension": file_path.suffix.lower()
                        }
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                
                # Process directories
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        stat = dir_path.stat()
                        yield {
                            "name": dir_name,
                            "path": str(dir_path.relative_to(directory_path)),
                            "is_file": False,
                            "is_dir": True,
                            "size_bytes": 0,
                            "size_mb": 0,
                            "modified": stat.st_mtime,
                            "extension": ""
                        }
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            yield {"error": str(e)}
    
    def get_batched_files(self, directory: str, batch_size: int = 50, offset: int = 0,
                         max_depth: int = 1, include_hidden: bool = False,
                         file_types: List[str] = None, sort_by: str = "name",
                         sort_order: str = "asc") -> Dict[str, Any]:
        """Get files in batches with memory management"""
        
        start_time = time.time()
        initial_memory = self.get_memory_usage()
        
        try:
            # Generate all files first (with memory monitoring)
            all_files = []
            file_count = 0
            
            for file_entry in self.file_generator(directory, max_depth, include_hidden, file_types):
                if "error" in file_entry:
                    return {"error": file_entry["error"]}
                
                all_files.append(file_entry)
                file_count += 1
                
                # Memory check every 1000 files
                if file_count % 1000 == 0:
                    current_memory = self.get_memory_usage()
                    if current_memory - initial_memory > self.max_memory_mb:
                        return {
                            "error": f"Memory limit exceeded ({self.max_memory_mb}MB). Processed {file_count} files.",
                            "partial_results": True,
                            "files_processed": file_count
                        }
            
            # Sort files
            reverse = sort_order.lower() == "desc"
            if sort_by == "name":
                all_files.sort(key=lambda x: x["name"].lower(), reverse=reverse)
            elif sort_by == "size":
                all_files.sort(key=lambda x: x["size_bytes"], reverse=reverse)
            elif sort_by == "modified":
                all_files.sort(key=lambda x: x["modified"], reverse=reverse)
            elif sort_by == "type":
                all_files.sort(key=lambda x: x["extension"], reverse=reverse)
            
            # Apply pagination
            total_files = len(all_files)
            start_idx = min(offset, total_files)
            end_idx = min(start_idx + batch_size, total_files)
            
            batch_files = all_files[start_idx:end_idx]
            
            # Calculate summary statistics
            total_size_mb = sum(f["size_mb"] for f in all_files if f["is_file"])
            file_types_count = {}
            for f in all_files:
                ext = f["extension"]
                file_types_count[ext] = file_types_count.get(ext, 0) + 1
            
            processing_time = time.time() - start_time
            final_memory = self.get_memory_usage()
            
            return {
                "success": True,
                "batch": {
                    "files": batch_files,
                    "offset": start_idx,
                    "limit": batch_size,
                    "total_files": total_files,
                    "has_more": end_idx < total_files,
                    "next_offset": end_idx if end_idx < total_files else None
                },
                "summary": {
                    "total_files": total_files,
                    "total_directories": len([f for f in all_files if f["is_dir"]]),
                    "total_size_mb": round(total_size_mb, 2),
                    "file_types": file_types_count,
                    "processing_time_seconds": round(processing_time, 2),
                    "memory_usage_mb": round(final_memory - initial_memory, 2)
                },
                "directory": directory,
                "filters": {
                    "max_depth": max_depth,
                    "include_hidden": include_hidden,
                    "file_types": file_types or [],
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error listing directory: {str(e)}",
                "processing_time_seconds": time.time() - start_time
            }

# Updated MCP tool handler
async def handle_list_files_optimized(self, args: Dict[str, Any]) -> str:
    """Optimized file listing with batching and memory management"""
    
    # Initialize optimized lister
    lister = OptimizedFileLister(max_memory_mb=50)
    
    # Extract parameters
    directory = args.get("directory", ".")
    batch_size = min(max(args.get("batch_size", 50), 10), 100)
    offset = max(args.get("offset", 0), 0)
    max_depth = min(max(args.get("max_depth", 1), 1), 5)
    include_hidden = args.get("include_hidden", False)
    file_types = args.get("file_types", [])
    sort_by = args.get("sort_by", "name")
    sort_order = args.get("sort_order", "asc")
    
    # Get batched results
    result = lister.get_batched_files(
        directory=directory,
        batch_size=batch_size,
        offset=offset,
        max_depth=max_depth,
        include_hidden=include_hidden,
        file_types=file_types,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Format response
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Create user-friendly response
    response_parts = []
    
    # Summary
    summary = result["summary"]
    response_parts.append(f"📁 Directory: {result['directory']}")
    response_parts.append(f"📊 Summary: {summary['total_files']} files, {summary['total_directories']} directories")
    response_parts.append(f"💾 Total Size: {summary['total_size_mb']} MB")
    response_parts.append(f"⏱️ Processing Time: {summary['processing_time_seconds']}s")
    response_parts.append(f"🧠 Memory Used: {summary['memory_usage_mb']} MB")
    
    # Batch info
    batch = result["batch"]
    response_parts.append(f"📄 Showing files {batch['offset'] + 1}-{batch['offset'] + len(batch['files'])} of {batch['total_files']}")
    
    if batch["has_more"]:
        response_parts.append(f"🔄 More files available. Use offset={batch['next_offset']} for next batch.")
    
    # File list (limited to first 20 for readability)
    files_to_show = batch["files"][:20]
    response_parts.append("\n📋 Files in this batch:")
    
    for file in files_to_show:
        if file["is_dir"]:
            response_parts.append(f"📁 {file['path']}/")
        else:
            size_str = f"{file['size_mb']} MB" if file['size_mb'] > 0 else "< 1 MB"
            response_parts.append(f"📄 {file['path']} ({size_str})")
    
    if len(batch["files"]) > 20:
        response_parts.append(f"... and {len(batch['files']) - 20} more files")
    
    # File type breakdown
    if result["summary"]["file_types"]:
        response_parts.append("\n📈 File Types:")
        for ext, count in sorted(result["summary"]["file_types"].items(), key=lambda x: x[1], reverse=True)[:10]:
            response_parts.append(f"  {ext or 'no extension'}: {count} files")
    
    return "\n".join(response_parts)
```

### **Step 2: Integration with Existing Memory Manager**

#### **2.1 Memory Manager Integration**
```python
# Add to mcp_langflow_connector_simple.py
from src.modules.module_2_support.memory_manager import MemoryManager

class SimpleLangFlowMCPConnector:
    def __init__(self):
        # ... existing code ...
        self.memory_manager = None
        self._initialize_memory_manager()
    
    def _initialize_memory_manager(self):
        """Initialize memory manager for file operations"""
        try:
            self.memory_manager = MemoryManager(
                cache_dir="cache/file_listings",
                max_memory_mb=100
            )
        except Exception as e:
            logger.warning(f"Memory manager initialization failed: {e}")
    
    async def _cache_directory_listing(self, directory: str, result: Dict) -> None:
        """Cache directory listing results"""
        if self.memory_manager:
            cache_key = f"dir_listing_{hash(directory)}"
            await self.memory_manager.set_cache(
                key=cache_key,
                value=result,
                ttl_seconds=300,  # 5 minutes cache
                use_disk=True
            )
    
    async def _get_cached_directory_listing(self, directory: str) -> Optional[Dict]:
        """Get cached directory listing"""
        if self.memory_manager:
            cache_key = f"dir_listing_{hash(directory)}"
            cache_result = await self.memory_manager.get_cache(cache_key, use_disk=True)
            if cache_result.get("success"):
                return cache_result.get("data")
        return None
```

### **Step 3: Enhanced Tool Configuration**

#### **3.1 Updated Tool Schema**
```python
# Replace the existing list_files tool in mcp_langflow_connector_simple.py
{
    "name": "list_files",
    "description": "List files in a directory with batching, filtering, and memory optimization",
    "inputSchema": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path to list files from",
                "default": "."
            },
            "batch_size": {
                "type": "integer",
                "description": "Number of files to return per batch (10-100)",
                "default": 50,
                "minimum": 10,
                "maximum": 100
            },
            "offset": {
                "type": "integer",
                "description": "Starting position for pagination",
                "default": 0,
                "minimum": 0
            },
            "file_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by file extensions (e.g., ['.py', '.txt'])",
                "default": []
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum directory depth to traverse",
                "default": 1,
                "minimum": 1,
                "maximum": 5
            },
            "include_hidden": {
                "type": "boolean",
                "description": "Include hidden files and directories",
                "default": false
            },
            "sort_by": {
                "type": "string",
                "enum": ["name", "size", "modified", "type"],
                "description": "Sort files by criteria",
                "default": "name"
            },
            "sort_order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "Sort order",
                "default": "asc"
            },
            "use_cache": {
                "type": "boolean",
                "description": "Use cached results if available",
                "default": true
            }
        },
        "required": ["directory"]
    }
}
```

---

## 🧪 **Testing Strategy**

### **Test 1: Memory Usage Testing**
```python
# Test memory usage with large directories
async def test_memory_usage():
    lister = OptimizedFileLister(max_memory_mb=50)
    
    # Test with large repository
    result = lister.get_batched_files(
        directory="D:\\GUI\\System-Reference-Clean",
        batch_size=50,
        max_depth=2
    )
    
    assert result["summary"]["memory_usage_mb"] < 50
    assert "error" not in result
```

### **Test 2: Batching Functionality**
```python
# Test pagination and batching
async def test_batching():
    lister = OptimizedFileLister()
    
    # First batch
    result1 = lister.get_batched_files(
        directory=".",
        batch_size=10,
        offset=0
    )
    
    # Second batch
    result2 = lister.get_batched_files(
        directory=".",
        batch_size=10,
        offset=10
    )
    
    assert len(result1["batch"]["files"]) == 10
    assert result1["batch"]["has_more"] == True
    assert result1["batch"]["next_offset"] == 10
```

### **Test 3: Performance Testing**
```python
# Test processing time
async def test_performance():
    lister = OptimizedFileLister()
    
    start_time = time.time()
    result = lister.get_batched_files(
        directory="D:\\GUI\\System-Reference-Clean",
        batch_size=100,
        max_depth=1
    )
    processing_time = time.time() - start_time
    
    assert processing_time < 5.0  # Should complete within 5 seconds
    assert result["summary"]["processing_time_seconds"] < 5.0
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Core Optimization**
- [ ] Implement `OptimizedFileLister` class
- [ ] Add memory monitoring and limits
- [ ] Implement file generator for streaming
- [ ] Add batching and pagination logic

### **Phase 2: Integration**
- [ ] Update MCP server with new tool schema
- [ ] Integrate with existing MemoryManager
- [ ] Add caching for directory listings
- [ ] Update error handling

### **Phase 3: Testing & Validation**
- [ ] Test with large repositories (130K+ files)
- [ ] Validate memory usage limits
- [ ] Test batching functionality
- [ ] Performance benchmarking

### **Phase 4: Documentation & Deployment**
- [ ] Update LangFlow testing workflows
- [ ] Create usage examples
- [ ] Document new parameters
- [ ] Deploy optimized version

---

## 🚀 **Quick Implementation**

### **1. Replace Current Implementation**
```bash
# Backup current implementation
cp mcp_langflow_connector_simple.py mcp_langflow_connector_simple_backup.py

# Update with optimized version
# (Apply the code changes above)
```

### **2. Test with Large Directory**
```bash
# Test the optimized version
python -c "
import asyncio
from mcp_langflow_connector_simple import OptimizedFileLister

async def test():
    lister = OptimizedFileLister()
    result = lister.get_batched_files('D:\\GUI\\System-Reference-Clean', batch_size=50)
    print(f'Memory used: {result[\"summary\"][\"memory_usage_mb\"]} MB')
    print(f'Files processed: {result[\"summary\"][\"total_files\"]}')

asyncio.run(test())
"
```

### **3. Update LangFlow Testing**
Update `LANGFLOW_TESTING_WORKFLOWS.md` to include the new batching parameters for Workflow 3.

---

## 🎯 **Success Metrics**

### **Primary Success Criteria**:
- [ ] **Memory Usage**: < 50MB per request
- [ ] **Response Time**: < 5 seconds for large directories
- [ ] **Batching**: Successful pagination with 50-100 files per batch
- [ ] **Error Handling**: Graceful handling of memory limits

### **Secondary Success Criteria**:
- [ ] **Caching**: Directory listings cached for 5 minutes
- [ ] **Filtering**: File type and depth filtering working
- [ ] **Sorting**: Multiple sort options available
- [ ] **Performance**: 10x improvement in memory efficiency

---

*LangFlow List Files Optimization Guide Created: August 1, 2025*  
*Status: READY FOR IMPLEMENTATION*  
*Next: Begin with Phase 1 Core Optimization* 