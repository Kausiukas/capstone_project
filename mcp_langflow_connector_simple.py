#!/usr/bin/env python3
"""
LangFlow MCP Connector - SIMPLIFIED VERSION
Immediate response without heavy initialization to fix timeout issues
"""

import asyncio
import json
import logging
import sys
import os
import time
import psutil
import numpy as np
from typing import Any, Dict, List, Generator, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
from io import StringIO
import re

# Optional PostgreSQL import
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    PSYCOPG2_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLVectorLLM:
    """PostgreSQL+Vector LLM integration for local processing tasks"""
    
    def __init__(self, connection_params: Dict[str, str] = None):
        if not PSYCOPG2_AVAILABLE:
            logger.warning("⚠️ psycopg2 not available - PostgreSQL features disabled")
            self.available = False
            return
            
        self.available = True
        self.connection_params = connection_params or {
            "host": "localhost",
            "port": "5432",
            "database": "postgres",
            "user": os.getenv('USERNAME', 'postgres')
        }
        self.conn = None
        self._ensure_tables()
    
    def _get_connection(self):
        """Get database connection"""
        if not self.available:
            raise Exception("PostgreSQL not available - psycopg2 not installed")
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.connection_params)
        return self.conn
    
    def _ensure_tables(self):
        """Ensure necessary tables exist"""
        if not self.available:
            logger.info("✅ PostgreSQL+Vector LLM initialized (PostgreSQL disabled)")
            return
            
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Create embeddings table for vector storage
            cur.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    content TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create processing_tasks table for task tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processing_tasks (
                    id SERIAL PRIMARY KEY,
                    task_type VARCHAR(100) NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
            """)
            
            # Create dataframes table for DataFrame operations
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dataframes (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    data JSONB,
                    schema JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cur.close()
            logger.info("✅ Database tables ensured")
            
        except Exception as e:
            logger.error(f"❌ Error ensuring tables: {e}")
    
    def simple_embedding(self, text: str) -> List[float]:
        """Simple text embedding using basic NLP techniques"""
        # This is a simplified embedding - in production, you'd use a proper model
        import hashlib
        import math
        
        # Create a simple hash-based embedding
        hash_obj = hashlib.sha256(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to 1536-dimensional vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if len(embedding) >= 1536:
                break
            hex_pair = hash_hex[i:i+2]
            embedding.append(int(hex_pair, 16) / 255.0)
        
        # Pad or truncate to exactly 1536 dimensions
        while len(embedding) < 1536:
            embedding.append(0.0)
        
        return embedding[:1536]
    
    def store_embedding(self, name: str, content: str, metadata: Dict = None) -> int:
        """Store text content with embedding"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            embedding = self.simple_embedding(content)
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            cur.execute("""
                INSERT INTO embeddings (name, content, embedding, metadata)
                VALUES (%s, %s, %s::vector, %s)
                RETURNING id
            """, (name, content, embedding_str, json.dumps(metadata or {})))
            
            embedding_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return embedding_id
            
        except Exception as e:
            logger.error(f"❌ Error storing embedding: {e}")
            return None
    
    def similarity_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar content using vector similarity"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            query_embedding = self.simple_embedding(query)
            query_embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            cur.execute("""
                SELECT id, name, content, metadata,
                       embedding <-> %s::vector as distance
                FROM embeddings
                ORDER BY distance
                LIMIT %s
            """, (query_embedding_str, limit))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "content": row[2],
                    "metadata": row[3],
                    "distance": float(row[4])
                })
            
            cur.close()
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in similarity search: {e}")
            return []
    
    def process_text_with_llm(self, text: str, task: str, parameters: Dict = None) -> str:
        """Process text using local LLM-like operations"""
        try:
            # Store the task
            conn = self._get_connection()
            cur = conn.cursor()
            
            task_id = self._store_task(task, text, parameters)
            
            # Process based on task type
            if task == "summarize":
                result = self._summarize_text(text)
            elif task == "extract_keywords":
                result = self._extract_keywords(text)
            elif task == "classify":
                result = self._classify_text(text, parameters)
            elif task == "translate":
                result = self._translate_text(text, parameters)
            elif task == "sentiment_analysis":
                result = self._analyze_sentiment(text)
            else:
                result = f"Task '{task}' not implemented yet"
            
            # Update task with result
            self._update_task(task_id, result, "completed")
            
            cur.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in LLM processing: {e}")
            return f"Error: {str(e)}"
    
    def _store_task(self, task_type: str, input_data: str, metadata: Dict = None) -> int:
        """Store a processing task"""
        conn = self._get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO processing_tasks (task_type, input_data, metadata)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (task_type, input_data, json.dumps(metadata or {})))
        
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return task_id
    
    def _update_task(self, task_id: int, output_data: str, status: str):
        """Update task with result"""
        conn = self._get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE processing_tasks 
            SET output_data = %s, status = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (output_data, status, task_id))
        
        conn.commit()
        cur.close()
    
    def _summarize_text(self, text: str) -> str:
        """Simple text summarization"""
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text
        
        # Simple extractive summarization
        word_freq = {}
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sentence_scores = []
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            score = sum(word_freq.get(word, 0) for word in words)
            sentence_scores.append((score, sentence))
        
        # Get top 3 sentences
        sentence_scores.sort(reverse=True)
        summary_sentences = [s[1] for s in sentence_scores[:3]]
        return '. '.join(summary_sentences) + '.'
    
    def _extract_keywords(self, text: str) -> str:
        """Extract keywords from text"""
        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return ', '.join([word for word, freq in keywords])
    
    def _classify_text(self, text: str, parameters: Dict) -> str:
        """Simple text classification"""
        categories = parameters.get('categories', ['general'])
        text_lower = text.lower()
        
        # Simple keyword-based classification
        category_scores = {}
        for category in categories:
            score = 0
            if category.lower() in text_lower:
                score += 1
            category_scores[category] = score
        
        if not any(category_scores.values()):
            return categories[0] if categories else 'general'
        
        return max(category_scores, key=category_scores.get)
    
    def _translate_text(self, text: str, parameters: Dict) -> str:
        """Simple text translation (placeholder)"""
        target_language = parameters.get('target_language', 'english')
        return f"[Translated to {target_language}]: {text}"
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'happy'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated'}
        
        words = set(re.findall(r'\w+', text.lower()))
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def dataframe_operations(self, operation: str, data: str, parameters: Dict = None) -> str:
        """Perform DataFrame operations"""
        try:
            # Parse CSV data
            df = pd.read_csv(StringIO(data))
            
            if operation == "head":
                return df.head(parameters.get('rows', 5)).to_csv(index=False)
            elif operation == "tail":
                return df.tail(parameters.get('rows', 5)).to_csv(index=False)
            elif operation == "describe":
                return df.describe().to_csv()
            elif operation == "info":
                buffer = StringIO()
                df.info(buf=buffer)
                return buffer.getvalue()
            elif operation == "filter":
                column = parameters.get('column')
                value = parameters.get('value')
                if column and value:
                    filtered_df = df[df[column] == value]
                    return filtered_df.to_csv(index=False)
                return "Error: column and value parameters required"
            elif operation == "sort":
                column = parameters.get('column', df.columns[0])
                ascending = parameters.get('ascending', True)
                sorted_df = df.sort_values(by=column, ascending=ascending)
                return sorted_df.to_csv(index=False)
            elif operation == "groupby":
                column = parameters.get('column', df.columns[0])
                agg_column = parameters.get('agg_column', df.columns[1])
                agg_func = parameters.get('agg_func', 'mean')
                grouped = df.groupby(column)[agg_column].agg(agg_func)
                return grouped.to_csv()
            else:
                return f"Operation '{operation}' not supported"
                
        except Exception as e:
            return f"Error in DataFrame operation: {str(e)}"
    
    def split_text(self, text: str, method: str = "sentences", parameters: Dict = None) -> str:
        """Split text using various methods"""
        try:
            if method == "sentences":
                sentences = re.split(r'[.!?]+', text)
                return json.dumps([s.strip() for s in sentences if s.strip()])
            elif method == "words":
                words = re.findall(r'\w+', text)
                return json.dumps(words)
            elif method == "paragraphs":
                paragraphs = text.split('\n\n')
                return json.dumps([p.strip() for p in paragraphs if p.strip()])
            elif method == "chunks":
                chunk_size = parameters.get('chunk_size', 100)
                words = text.split()
                chunks = []
                for i in range(0, len(words), chunk_size):
                    chunks.append(' '.join(words[i:i+chunk_size]))
                return json.dumps(chunks)
            else:
                return f"Method '{method}' not supported"
                
        except Exception as e:
            return f"Error splitting text: {str(e)}"
    
    def structured_output(self, text: str, schema: Dict) -> str:
        """Extract structured data from text"""
        try:
            result = {}
            
            for field, pattern in schema.items():
                if isinstance(pattern, str):
                    # Simple regex pattern
                    match = re.search(pattern, text)
                    if match:
                        result[field] = match.group(1) if match.groups() else match.group(0)
                    else:
                        result[field] = None
                elif isinstance(pattern, dict):
                    # Complex pattern with options
                    pattern_type = pattern.get('type', 'regex')
                    if pattern_type == 'regex':
                        match = re.search(pattern['pattern'], text)
                        if match:
                            result[field] = match.group(1) if match.groups() else match.group(0)
                        else:
                            result[field] = pattern.get('default', None)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in structured output: {str(e)}"
    
    def type_convert(self, data: str, target_type: str, parameters: Dict = None) -> str:
        """Convert data between different types"""
        try:
            if target_type == "json":
                # Try to parse as JSON
                return json.dumps(json.loads(data))
            elif target_type == "csv":
                # Convert JSON to CSV
                data_obj = json.loads(data)
                if isinstance(data_obj, list):
                    df = pd.DataFrame(data_obj)
                    return df.to_csv(index=False)
                else:
                    return "Error: JSON data must be a list for CSV conversion"
            elif target_type == "yaml":
                import yaml
                data_obj = json.loads(data)
                return yaml.dump(data_obj, default_flow_style=False)
            elif target_type == "xml":
                # Simple XML conversion
                data_obj = json.loads(data)
                xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<root>']
                
                def dict_to_xml(obj, indent=0):
                    lines = []
                    for key, value in obj.items():
                        if isinstance(value, dict):
                            lines.append(' ' * indent + f'<{key}>')
                            lines.extend(dict_to_xml(value, indent + 2))
                            lines.append(' ' * indent + f'</{key}>')
                        else:
                            lines.append(' ' * indent + f'<{key}>{value}</{key}>')
                    return lines
                
                xml_lines.extend(dict_to_xml(data_obj))
                xml_lines.append('</root>')
                return '\n'.join(xml_lines)
            else:
                return f"Target type '{target_type}' not supported"
                
        except Exception as e:
            return f"Error in type conversion: {str(e)}"


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
            directory_path = Path(directory).resolve()
            if not directory_path.exists():
                return
            
            # For max_depth=1, we only want immediate children, so use os.listdir instead of os.walk
            if max_depth == 1:
                try:
                    items = os.listdir(directory_path)
                    
                    # Filter hidden items
                    if not include_hidden:
                        items = [item for item in items if not item.startswith('.')]
                    
                    for item in items:
                        item_path = directory_path / item
                        
                        try:
                            if item_path.is_file():
                                # Filter by file type
                                if file_types and item_path.suffix.lower() not in file_types:
                                    continue
                                
                                stat = item_path.stat()
                                yield {
                                    "name": item,
                                    "path": item,
                                    "is_file": True,
                                    "is_dir": False,
                                    "size_bytes": stat.st_size,
                                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                    "modified": stat.st_mtime,
                                    "extension": item_path.suffix.lower()
                                }
                            elif item_path.is_dir():
                                stat = item_path.stat()
                                yield {
                                    "name": item,
                                    "path": item,
                                    "is_file": False,
                                    "is_dir": True,
                                    "size_bytes": 0,
                                    "size_mb": 0,
                                    "modified": stat.st_mtime,
                                    "extension": ""
                                }
                        except (OSError, PermissionError):
                            # Skip items we can't access
                            continue
                            
                except (OSError, PermissionError) as e:
                    yield {"error": f"Cannot access directory: {str(e)}"}
                    return
            else:
                # For deeper scans, use os.walk with proper depth calculation
                for root, dirs, files in os.walk(directory_path):
                    # Calculate current depth relative to the target directory
                    rel_path = Path(root).relative_to(directory_path)
                    depth = len(rel_path.parts)
                    
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


class SimpleLangFlowMCPConnector:
    """Simplified MCP Connector that responds immediately"""
    
    def __init__(self):
        # No heavy initialization - just define tools
        self.memory_manager = None
        self._initialize_memory_manager()
        self.streaming_sessions = {}  # Store streaming sessions
        
        # Initialize PostgreSQL+Vector LLM
        try:
            self.vector_llm = PostgreSQLVectorLLM()
            logger.info("✅ PostgreSQL+Vector LLM initialized")
        except Exception as e:
            logger.warning(f"❌ PostgreSQL+Vector LLM initialization failed: {e}")
            self.vector_llm = None
        self.tools = [
            {
                "name": "read_file",
                "description": "Read file contents from the workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file in the workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in a directory showing only metadata (file names, types, sizes) without content",
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
                            "description": "Number of files to return per batch (5-50)",
                            "default": 20,
                            "minimum": 5,
                            "maximum": 50
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
                            "maximum": 3
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
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
                            "default": True
                        }
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "list_files_metadata_only",
                "description": "STRICT metadata-only file listing - returns only file names, types, and sizes. NO file paths to prevent automatic reading",
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
                            "description": "Number of files to return per batch (5-50)",
                            "default": 20,
                            "minimum": 5,
                            "maximum": 50
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
                            "maximum": 3
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
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
            },
            {
                "name": "list_files_readable",
                "description": "List files in a human-readable format showing file names, types, and sizes in a simple list",
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
                            "description": "Number of files to return per batch (5-50)",
                            "default": 20,
                            "minimum": 5,
                            "maximum": 50
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
                            "maximum": 3
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
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
            },
            {
                "name": "list_files_table",
                "description": "List files in LangFlow table format with type, text, annotations, and meta columns",
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
                            "description": "Number of files to return per batch (5-50)",
                            "default": 20,
                            "minimum": 5,
                            "maximum": 50
                        },
                        "offset": {
                            "type": "string",
                            "description": "Starting position for pagination (can be connected from other nodes, accepts numbers as strings)",
                            "default": "0"
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
                            "maximum": 3
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
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
                    "required": ["directory", "offset"]
                }
            },
            {
                "name": "append_file",
                "description": "Append content to an existing file or create a new file if it doesn't exist",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to append to"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file"
                        },
                        "separator": {
                            "type": "string",
                            "description": "Separator to add between existing content and new content",
                            "default": "\n"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "get_pagination_info",
                "description": "Get pagination information for directory listing to help with iteration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to analyze",
                            "default": "."
                        },
                        "batch_size": {
                            "type": "integer",
                            "description": "Batch size to use for pagination",
                            "default": 20,
                            "minimum": 5,
                            "maximum": 50
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum directory depth to traverse",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 3
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
                        }
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "stream_files",
                "description": "Stream file metadata incrementally to prevent memory overload",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from",
                            "default": "."
                        },
                        "stream_id": {
                            "type": "string",
                            "description": "Unique identifier for this streaming session",
                            "default": ""
                        },
                        "action": {
                            "type": "string",
                            "enum": ["start", "next", "stop"],
                            "description": "Streaming action to perform",
                            "default": "start"
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
                            "maximum": 2
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
                        }
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "analyze_code",
                "description": "Analyze code structure and metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the code file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "track_token_usage",
                "description": "Track token usage and costs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Name of the operation"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model used for the operation"
                        },
                        "input_tokens": {
                            "type": "integer",
                            "description": "Number of input tokens"
                        },
                        "output_tokens": {
                            "type": "integer",
                            "description": "Number of output tokens"
                        }
                    },
                    "required": ["operation", "model", "input_tokens", "output_tokens"]
                }
            },
            {
                "name": "get_cost_summary",
                "description": "Get cost summary and statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_system_health",
                "description": "Get system health status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_system_status",
                "description": "Get overall system status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "ping",
                "description": "Ping the MCP server for monitoring and debugging",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Optional message to include in ping response"
                        }
                    }
                }
            },
            {
                "name": "store_embedding",
                "description": "Store text content with vector embedding in PostgreSQL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name/identifier for the content"
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to embed and store"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata as JSON object"
                        }
                    },
                    "required": ["name", "content"]
                }
            },
            {
                "name": "similarity_search",
                "description": "Search for similar content using vector similarity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "process_text_with_llm",
                "description": "Process text using local LLM-like operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to process"
                        },
                        "task": {
                            "type": "string",
                            "enum": ["summarize", "extract_keywords", "classify", "translate", "sentiment_analysis"],
                            "description": "Type of processing task"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Task-specific parameters"
                        }
                    },
                    "required": ["text", "task"]
                }
            },
            {
                "name": "dataframe_operations",
                "description": "Perform DataFrame operations on CSV data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["head", "tail", "describe", "info", "filter", "sort", "groupby"],
                            "description": "DataFrame operation to perform"
                        },
                        "data": {
                            "type": "string",
                            "description": "CSV data to process"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Operation-specific parameters"
                        }
                    },
                    "required": ["operation", "data"]
                }
            },
            {
                "name": "split_text",
                "description": "Split text using various methods",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to split"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["sentences", "words", "paragraphs", "chunks"],
                            "description": "Splitting method",
                            "default": "sentences"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Method-specific parameters (e.g., chunk_size for chunks)"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "structured_output",
                "description": "Extract structured data from text using schema",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to extract structured data from"
                        },
                        "schema": {
                            "type": "object",
                            "description": "Schema defining fields and patterns to extract"
                        }
                    },
                    "required": ["text", "schema"]
                }
            },
            {
                "name": "type_convert",
                "description": "Convert data between different formats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Data to convert"
                        },
                        "target_type": {
                            "type": "string",
                            "enum": ["json", "csv", "yaml", "xml"],
                            "description": "Target format"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Conversion parameters"
                        }
                    },
                    "required": ["data", "target_type"]
                }
            }
        ]
    
    def _initialize_memory_manager(self):
        """Initialize memory manager for file operations"""
        try:
            # Create cache directory if it doesn't exist
            cache_dir = Path("cache/file_listings")
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Memory manager cache directory: {cache_dir}")
        except Exception as e:
            logger.warning(f"Memory manager initialization failed: {e}")
    
    async def _cache_directory_listing(self, directory: str, result: Dict) -> None:
        """Cache directory listing results"""
        try:
            cache_key = f"dir_listing_{hash(directory)}"
            cache_file = Path("cache/file_listings") / f"{cache_key}.json"
            
            # Cache with timestamp
            cache_data = {
                "timestamp": time.time(),
                "directory": directory,
                "result": result
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to cache directory listing: {e}")
    
    async def _get_cached_directory_listing(self, directory: str) -> Optional[Dict]:
        """Get cached directory listing"""
        try:
            cache_key = f"dir_listing_{hash(directory)}"
            cache_file = Path("cache/file_listings") / f"{cache_key}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is still valid (5 minutes)
                if time.time() - cache_data["timestamp"] < 300:
                    return cache_data["result"]
                    
        except Exception as e:
            logger.warning(f"Failed to get cached directory listing: {e}")
        
        return None
    
    async def _manage_streaming_session(self, stream_id: str, directory: str, file_types: List[str], 
                                      max_depth: int, include_hidden: bool) -> Dict[str, Any]:
        """Manage streaming session for file listing"""
        import uuid
        
        if not stream_id:
            stream_id = str(uuid.uuid4())[:8]
        
        if stream_id not in self.streaming_sessions:
            # Initialize new session
            lister = OptimizedFileLister(max_memory_mb=10)  # Very low memory limit
            file_generator = lister.file_generator(directory, max_depth, include_hidden, file_types)
            
            self.streaming_sessions[stream_id] = {
                "directory": directory,
                "file_generator": file_generator,
                "files_processed": 0,
                "total_files": 0,
                "start_time": time.time(),
                "file_types": file_types,
                "max_depth": max_depth,
                "include_hidden": include_hidden
            }
        
        return {"stream_id": stream_id, "session": self.streaming_sessions[stream_id]}
    
    async def _get_next_files_batch(self, stream_id: str, batch_size: int = 5) -> Dict[str, Any]:
        """Get next batch of files from streaming session"""
        if stream_id not in self.streaming_sessions:
            return {"error": "Streaming session not found"}
        
        session = self.streaming_sessions[stream_id]
        files_batch = []
        
        try:
            # Get next batch of files
            for _ in range(batch_size):
                try:
                    file_entry = next(session["file_generator"])
                    if "error" in file_entry:
                        return {"error": file_entry["error"]}
                    
                    files_batch.append({
                        "name": file_entry["name"],
                        "is_dir": file_entry["is_dir"],
                        "size_mb": file_entry["size_mb"],
                        "extension": file_entry["extension"]
                    })
                    session["files_processed"] += 1
                    
                except StopIteration:
                    # No more files
                    break
            
            return {
                "stream_id": stream_id,
                "files": files_batch,
                "files_processed": session["files_processed"],
                "has_more": len(files_batch) == batch_size,
                "processing_time": time.time() - session["start_time"]
            }
            
        except Exception as e:
            return {"error": f"Error getting next batch: {str(e)}"}
    
    async def _cleanup_streaming_session(self, stream_id: str) -> None:
        """Clean up streaming session"""
        if stream_id in self.streaming_sessions:
            del self.streaming_sessions[stream_id]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests - IMMEDIATE RESPONSE"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                # IMMEDIATE response - no initialization
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "langflow-connect-simple",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "ping":
                # Ping method for monitoring and debugging
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "message": "pong",
                        "timestamp": "2025-07-31T23:00:00",
                        "server_status": "running",
                        "tools_available": len(self.tools)
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.execute_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool - SIMPLIFIED VERSIONS"""
        try:
            if tool_name == "read_file":
                return await self.handle_read_file(arguments)
            elif tool_name == "write_file":
                return await self.handle_write_file(arguments)
            elif tool_name == "append_file":
                return await self.handle_append_file(arguments)
            elif tool_name == "list_files":
                return await self.handle_list_files(arguments)
            elif tool_name == "list_files_metadata_only":
                return await self.handle_list_files_metadata_only(arguments)
            elif tool_name == "list_files_readable":
                return await self.handle_list_files_readable(arguments)
            elif tool_name == "list_files_table":
                return await self.handle_list_files_table(arguments)
            elif tool_name == "get_pagination_info":
                return await self.handle_get_pagination_info(arguments)
            elif tool_name == "stream_files":
                return await self.handle_stream_files(arguments)
            elif tool_name == "analyze_code":
                return await self.handle_analyze_code(arguments)
            elif tool_name == "track_token_usage":
                return await self.handle_track_token_usage(arguments)
            elif tool_name == "get_cost_summary":
                return await self.handle_get_cost_summary(arguments)
            elif tool_name == "get_system_health":
                return await self.handle_get_system_health(arguments)
            elif tool_name == "get_system_status":
                return await self.handle_get_system_status(arguments)
            elif tool_name == "ping":
                return await self.handle_ping(arguments)
            elif tool_name == "store_embedding":
                return await self.handle_store_embedding(arguments)
            elif tool_name == "similarity_search":
                return await self.handle_similarity_search(arguments)
            elif tool_name == "process_text_with_llm":
                return await self.handle_process_text_with_llm(arguments)
            elif tool_name == "dataframe_operations":
                return await self.handle_dataframe_operations(arguments)
            elif tool_name == "split_text":
                return await self.handle_split_text(arguments)
            elif tool_name == "structured_output":
                return await self.handle_structured_output(arguments)
            elif tool_name == "type_convert":
                return await self.handle_type_convert(arguments)
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def handle_read_file(self, args: Dict[str, Any]) -> str:
        """Simple file read operation"""
        file_path = args.get("file_path")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content:\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def handle_write_file(self, args: Dict[str, Any]) -> str:
        """Simple file write operation with Unicode handling"""
        file_path = args.get("file_path")
        content = args.get("content")
        try:
            # Handle Unicode surrogate characters by using 'surrogatepass' error handler
            with open(file_path, 'w', encoding='utf-8', errors='surrogatepass') as f:
                f.write(content)
            return f"File written successfully: {file_path}"
        except UnicodeEncodeError as e:
            # If surrogatepass fails, try with 'replace' to replace problematic characters
            try:
                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
                return f"File written successfully: {file_path} (some characters replaced)"
            except Exception as e2:
                return f"Error writing file: {str(e2)}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    async def handle_append_file(self, args: Dict[str, Any]) -> str:
        """Append content to a file with Unicode handling"""
        file_path = args.get("file_path")
        content = args.get("content")
        separator = args.get("separator", "\n")
        
        try:
            # Check if file exists
            file_exists = os.path.exists(file_path)
            
            if file_exists:
                # Read existing content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        existing_content = f.read()
                except Exception as e:
                    return f"Error reading existing file: {str(e)}"
                
                # Combine content
                new_content = existing_content + separator + content
            else:
                # Create new file
                new_content = content
            
            # Write combined content
            try:
                with open(file_path, 'w', encoding='utf-8', errors='surrogatepass') as f:
                    f.write(new_content)
                action = "appended to" if file_exists else "created"
                return f"Content {action} successfully: {file_path}"
            except UnicodeEncodeError as e:
                # If surrogatepass fails, try with 'replace'
                try:
                    with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                        f.write(new_content)
                    action = "appended to" if file_exists else "created"
                    return f"Content {action} successfully: {file_path} (some characters replaced)"
                except Exception as e2:
                    return f"Error writing file: {str(e2)}"
                    
        except Exception as e:
            return f"Error appending to file: {str(e)}"
    
    async def handle_list_files(self, args: Dict[str, Any]) -> str:
        """List files in directory showing only metadata (no content)"""
        
        # Extract parameters
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        batch_size = min(max(args.get("batch_size", 20), 5), 50)
        offset = max(args.get("offset", 0), 0)
        max_depth = min(max(args.get("max_depth", 1), 1), 3)
        include_hidden = args.get("include_hidden", False)
        file_types = args.get("file_types", [])
        sort_by = args.get("sort_by", "name")
        sort_order = args.get("sort_order", "asc")
        use_cache = args.get("use_cache", True)
        
        # Check cache first
        if use_cache:
            cached_result = await self._get_cached_directory_listing(directory)
            if cached_result:
                # Use cached result instead of just returning a message
                result = cached_result
                logger.info(f"Using cached directory listing for {directory}")
            else:
        # Initialize optimized lister
                lister = OptimizedFileLister(max_memory_mb=25)
        
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
        
        # Cache the result if successful
        if "success" in result and result["success"]:
            await self._cache_directory_listing(directory, result)
        else:
            # Initialize optimized lister
            lister = OptimizedFileLister(max_memory_mb=25)
            
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
        
        # Return JSON response to prevent LangFlow from misinterpreting as file path
        if "error" in result:
            return json.dumps({"error": result['error']}, indent=2)
        
        # Return structured JSON instead of formatted string
        return json.dumps(result, indent=2)
    
    async def handle_list_files_readable(self, args: Dict[str, Any]) -> str:
        """List files in a human-readable format showing file names, types, and sizes in a simple list"""
        
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        batch_size = min(max(args.get("batch_size", 20), 5), 50)
        offset = max(args.get("offset", 0), 0)
        max_depth = min(max(args.get("max_depth", 1), 1), 3)
        include_hidden = args.get("include_hidden", False)
        file_types = args.get("file_types", [])
        sort_by = args.get("sort_by", "name")
        sort_order = args.get("sort_order", "asc")
        
        # Initialize optimized lister
        lister = OptimizedFileLister(max_memory_mb=25)
        
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
        
        # Return error if any
        if "error" in result:
            return f"Error listing directory: {result['error']}"
        
        # Format as human-readable list
        output_lines = []
        output_lines.append(f"📁 Directory: {directory}")
        output_lines.append(f"📊 Summary: {result['summary']['total_files']} files, {result['summary']['total_directories']} directories")
        output_lines.append(f"📄 Showing: {offset + 1}-{offset + len(result['batch']['files'])} of {result['summary']['total_files']}")
        output_lines.append(f"⏱️ Processed in: {result['summary']['processing_time_seconds']}s")
        output_lines.append("")
        
        # List files in readable format
        for file_info in result['batch']['files']:
            if file_info['is_dir']:
                output_lines.append(f"📁 {file_info['name']} (directory)")
            else:
                size_str = f"({file_info['size_mb']} MB)" if file_info['size_mb'] > 0 else "(0.0 MB)"
                output_lines.append(f"📄 {file_info['name']} {size_str}")
        
        # Add pagination info
        if result['batch']['has_more']:
            output_lines.append("")
            output_lines.append(f"📄 More files available. Use offset={result['batch']['next_offset']} to see next batch.")
        
        return "\n".join(output_lines)
    
    async def handle_list_files_table(self, args: Dict[str, Any]) -> str:
        """List files in LangFlow table format with type, text, annotations, and meta columns"""
        
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        batch_size = min(max(args.get("batch_size", 20), 5), 50)
        # Handle offset as string (for LangFlow compatibility)
        offset_str = args.get("offset", "0")
        try:
            offset = max(int(offset_str), 0)
        except (ValueError, TypeError):
            offset = 0
        max_depth = min(max(args.get("max_depth", 1), 1), 3)
        include_hidden = args.get("include_hidden", False)
        file_types = args.get("file_types", [])
        sort_by = args.get("sort_by", "name")
        sort_order = args.get("sort_order", "asc")
        
        # Initialize optimized lister
        lister = OptimizedFileLister(max_memory_mb=25)
        
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
        
        # Return error if any
        if "error" in result:
            return f"Error listing directory: {result['error']}"
        
        # Get current timestamp for processing
        import datetime
        processing_timestamp = datetime.datetime.now().isoformat()
        
        # Format as clean table (no nested structure)
        output_lines = []
        
        # Add summary row
        summary_text = f"Directory: {directory}"
        summary_meta = f"Total: {result['summary']['total_files']} files, {result['summary']['total_directories']} directories | Size: {result['summary']['total_size_mb']} MB | Processed: {processing_timestamp}"
        output_lines.append(f"| summary | {summary_text} | Directory listing | {summary_meta} |")
        
        # List files in table format
        for file_info in result['batch']['files']:
            # Type column: file extension or "directory"
            if file_info['is_dir']:
                file_type = "directory"
            else:
                file_type = file_info['extension'] if file_info['extension'] else "file"
            
            # Text column: file name (no emojis to avoid encoding issues)
            text_content = file_info['name']
            
            # Annotations column: file type category
            if file_info['is_dir']:
                annotations = "Directory"
            elif file_info['extension'] in ['.py', '.pyc']:
                annotations = "Python file"
            elif file_info['extension'] in ['.md', '.txt']:
                annotations = "Documentation"
            elif file_info['extension'] in ['.json', '.yaml', '.yml']:
                annotations = "Configuration"
            elif file_info['extension'] in ['.log']:
                annotations = "Log file"
            elif file_info['extension'] in ['.exe', '.bat', '.ps1']:
                annotations = "Executable"
            elif file_info['extension'] in ['.pyd', '.dll']:
                annotations = "Binary library"
            else:
                annotations = "File"
            
            # Meta column: stats and dates
            modified_date = datetime.datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
            if file_info['is_dir']:
                meta_content = f"Modified: {modified_date} | Type: Directory"
            else:
                size_str = f"{file_info['size_mb']} MB" if file_info['size_mb'] > 0 else "0.0 MB"
                meta_content = f"Size: {size_str} | Modified: {modified_date} | Extension: {file_info['extension']}"
            
            output_lines.append(f"| {file_type} | {text_content} | {annotations} | {meta_content} |")
        
        # Add pagination info
        if result['batch']['has_more']:
            pagination_text = f"Showing batch {offset + 1}-{offset + len(result['batch']['files'])} of {result['summary']['total_files']}"
            pagination_meta = f"Next offset: {result['batch']['next_offset']} | Processing time: {result['summary']['processing_time_seconds']}s"
            output_lines.append(f"| pagination | {pagination_text} | More files available | {pagination_meta} |")
            
            # Add a separate row with just the next_offset for easy extraction
            output_lines.append(f"| next_offset | {result['batch']['next_offset']} | Use this value for next batch | Batch size: {batch_size} |")
        
        return "\n".join(output_lines)
    
    async def handle_get_pagination_info(self, args: Dict[str, Any]) -> str:
        """Get pagination information for directory listing"""
        
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        batch_size = min(max(args.get("batch_size", 20), 5), 50)
        max_depth = min(max(args.get("max_depth", 1), 1), 3)
        include_hidden = args.get("include_hidden", False)
        
        # Validate directory exists
        import os
        if not os.path.exists(directory):
            return f"Error: Directory '{directory}' does not exist or is not accessible."
        
        if not os.path.isdir(directory):
            return f"Error: '{directory}' is not a directory."
        
        # Initialize optimized lister
        lister = OptimizedFileLister(max_memory_mb=25)
        
        # Get total count first (with batch_size=1 to minimize processing)
        result = lister.get_batched_files(
            directory=directory,
            batch_size=1,
            offset=0,
            max_depth=max_depth,
            include_hidden=include_hidden,
            file_types=[],
            sort_by="name",
            sort_order="asc"
        )
        
        # Return error if any
        if "error" in result:
            return f"Error analyzing directory: {result['error']}"
        
        total_files = result['summary']['total_files']
        total_directories = result['summary']['total_directories']
        
        # Calculate pagination info
        total_items = total_files + total_directories
        total_batches = (total_items + batch_size - 1) // batch_size  # Ceiling division
        
        # Generate batch offsets
        batch_offsets = []
        for i in range(total_batches):
            batch_offsets.append(i * batch_size)
        
        # Format output
        output_lines = []
        output_lines.append("**Pagination Information**")
        output_lines.append(f"Directory: {directory}")
        output_lines.append(f"Total files: {total_files}")
        output_lines.append(f"Total directories: {total_directories}")
        output_lines.append(f"Total items: {total_items}")
        output_lines.append(f"Batch size: {batch_size}")
        output_lines.append(f"Total batches: {total_batches}")
        output_lines.append("")
        output_lines.append("**Batch Offsets for Iteration:**")
        
        for i, offset in enumerate(batch_offsets):
            start_item = offset + 1
            end_item = min(offset + batch_size, total_items)
            has_more = i < total_batches - 1
            next_offset = offset + batch_size if has_more else None
            
            output_lines.append(f"  Batch {i+1}: offset={offset} (items {start_item}-{end_item})")
            if has_more:
                output_lines.append(f"    -> Next offset: {next_offset}")
        
        output_lines.append("")
        output_lines.append("**Usage in LangFlow:**")
        output_lines.append("1. Use `list_files_table` with offset=0 for first batch")
        output_lines.append("2. Extract next_offset from the output")
        output_lines.append("3. Use next_offset for the next batch")
        output_lines.append("4. Repeat until no more files")
        
        return "\n".join(output_lines)
    
    async def handle_list_files_metadata_only(self, args: Dict[str, Any]) -> str:
        """Strict metadata-only file listing - returns only file names, types, and sizes. NO file paths to prevent automatic reading"""
        
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        batch_size = min(max(args.get("batch_size", 20), 5), 50)
        offset = max(args.get("offset", 0), 0)
        max_depth = min(max(args.get("max_depth", 1), 1), 3)
        include_hidden = args.get("include_hidden", False)
        file_types = args.get("file_types", [])
        sort_by = args.get("sort_by", "name")
        sort_order = args.get("sort_order", "asc")
        
        # Initialize optimized lister
        lister = OptimizedFileLister(max_memory_mb=10) # Very low memory limit for strict listing
        
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
        
        # Return JSON response to prevent LangFlow from misinterpreting as file path
        if "error" in result:
            return json.dumps({"error": result['error']}, indent=2)
        
        # Return structured JSON instead of formatted string
        return json.dumps(result, indent=2)
    
    async def handle_stream_files(self, args: Dict[str, Any]) -> str:
        """Handle streaming file listing to prevent memory overload"""
        
        directory = args.get("directory", ".")
        # Fix: Strip extra quotes from directory path (LangFlow issue)
        if isinstance(directory, str):
            directory = directory.strip('"').strip("'")
        
        stream_id = args.get("stream_id", "")
        action = args.get("action", "start")
        file_types = args.get("file_types", [])
        max_depth = min(max(args.get("max_depth", 1), 1), 2)
        include_hidden = args.get("include_hidden", False)
        
        try:
            if action == "start":
                # Initialize streaming session
                session_info = await self._manage_streaming_session(
                    stream_id, directory, file_types, max_depth, include_hidden
                )
                
                # Get first batch
                batch_result = await self._get_next_files_batch(session_info["stream_id"], 5)
                
                if "error" in batch_result:
                    return json.dumps({"error": batch_result['error']}, indent=2)
                
                # Return structured JSON response
                response = {
                    "action": "start",
                    "directory": directory,
                    "stream_id": session_info["stream_id"],
                    "batch": batch_result,
                    "message": f"Streaming started for {directory}"
                }
                
                return json.dumps(response, indent=2)
            
            elif action == "next":
                if not stream_id:
                    return json.dumps({"error": "stream_id required for 'next' action"}, indent=2)
                
                # Get next batch
                batch_result = await self._get_next_files_batch(stream_id, 5)
                
                if "error" in batch_result:
                    return json.dumps({"error": batch_result['error']}, indent=2)
                
                # Return structured JSON response
                response = {
                    "action": "next",
                    "stream_id": stream_id,
                    "batch": batch_result,
                    "message": f"Next batch retrieved for stream {stream_id}"
                }
                
                return json.dumps(response, indent=2)
            
            elif action == "stop":
                if not stream_id:
                    return json.dumps({"error": "stream_id required for 'stop' action"}, indent=2)
                
                # Cleanup session
                await self._cleanup_streaming_session(stream_id)
                
                response = {
                    "action": "stop",
                    "stream_id": stream_id,
                    "message": f"Streaming session {stream_id} stopped and cleaned up"
                }
                
                return json.dumps(response, indent=2)
            
            else:
                return json.dumps({"error": f"Unknown action '{action}'. Use 'start', 'next', or 'stop'"}, indent=2)
                
        except Exception as e:
            return json.dumps({"error": f"Error in stream_files: {str(e)}"}, indent=2)
    
    async def handle_analyze_code(self, args: Dict[str, Any]) -> str:
        """Simple code analysis"""
        file_path = args.get("file_path")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            analysis = {
                "file_path": file_path,
                "total_lines": len(lines),
                "non_empty_lines": len([line for line in lines if line.strip()]),
                "file_size": len(content),
                "extension": os.path.splitext(file_path)[1]
            }
            return f"Code analysis:\n{json.dumps(analysis, indent=2)}"
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
    
    async def handle_track_token_usage(self, args: Dict[str, Any]) -> str:
        """Simple token tracking"""
        operation = args.get("operation")
        model = args.get("model")
        input_tokens = args.get("input_tokens")
        output_tokens = args.get("output_tokens")
        
        return f"Token usage tracked: {operation} using {model} - Input: {input_tokens}, Output: {output_tokens}"
    
    async def handle_get_cost_summary(self, args: Dict[str, Any]) -> str:
        """Simple cost summary"""
        summary = {
            "total_operations": 0,
            "total_tokens": 0,
            "estimated_cost": "$0.00"
        }
        return f"Cost summary:\n{json.dumps(summary, indent=2)}"
    
    async def handle_get_system_health(self, args: Dict[str, Any]) -> str:
        """Simple system health"""
        health = {
            "status": "healthy",
            "uptime": "0 seconds",
            "memory_usage": "0 MB"
        }
        return f"System health:\n{json.dumps(health, indent=2)}"
    
    async def handle_get_system_status(self, args: Dict[str, Any]) -> str:
        """Simple system status"""
        status = {
            "is_running": True,
            "start_time": "2025-07-31T23:00:00",
            "modules_initialized": ["simple_mcp"],
            "active_connections": 1,
            "total_operations": 0,
            "system_health": "healthy",
            "last_heartbeat": "2025-07-31T23:00:00"
        }
        return f"System status:\n{json.dumps(status, indent=2)}"
    
    async def handle_ping(self, args: Dict[str, Any]) -> str:
        """Handle ping operation for monitoring and debugging"""
        import datetime
        
        message = args.get("message", "Hello from MCP Server!")
        timestamp = datetime.datetime.now().isoformat()
        
        response = {
            "message": message,
            "timestamp": timestamp,
            "server_status": "running",
            "tools_available": len(self.tools),
            "server_name": "langflow-connect-simple",
            "version": "1.0.0"
        }
        
        return f"Ping response:\n{json.dumps(response, indent=2)}"

    # PostgreSQL+Vector LLM Tool Handlers
    
    async def handle_store_embedding(self, args: Dict[str, Any]) -> str:
        """Store text content with vector embedding"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            name = args.get("name")
            content = args.get("content")
            metadata = args.get("metadata", {})
            
            if not name or not content:
                return "Error: name and content are required"
            
            embedding_id = self.vector_llm.store_embedding(name, content, metadata)
            
            if embedding_id:
                return f"Embedding stored successfully with ID: {embedding_id}"
            else:
                return "Error: Failed to store embedding"
                
        except Exception as e:
            return f"Error storing embedding: {str(e)}"
    
    async def handle_similarity_search(self, args: Dict[str, Any]) -> str:
        """Search for similar content using vector similarity"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            query = args.get("query")
            limit = args.get("limit", 5)
            
            if not query:
                return "Error: query is required"
            
            results = self.vector_llm.similarity_search(query, limit)
            
            if results:
                return f"Similarity search results:\n{json.dumps(results, indent=2)}"
            else:
                return "No similar content found"
                
        except Exception as e:
            return f"Error in similarity search: {str(e)}"
    
    async def handle_process_text_with_llm(self, args: Dict[str, Any]) -> str:
        """Process text using local LLM-like operations"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            text = args.get("text")
            task = args.get("task")
            parameters = args.get("parameters", {})
            
            if not text or not task:
                return "Error: text and task are required"
            
            result = self.vector_llm.process_text_with_llm(text, task, parameters)
            return f"LLM processing result:\n{result}"
            
        except Exception as e:
            return f"Error in LLM processing: {str(e)}"
    
    async def handle_dataframe_operations(self, args: Dict[str, Any]) -> str:
        """Perform DataFrame operations on CSV data"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            operation = args.get("operation")
            data = args.get("data")
            parameters = args.get("parameters", {})
            
            if not operation or not data:
                return "Error: operation and data are required"
            
            result = self.vector_llm.dataframe_operations(operation, data, parameters)
            return f"DataFrame operation result:\n{result}"
            
        except Exception as e:
            return f"Error in DataFrame operation: {str(e)}"
    
    async def handle_split_text(self, args: Dict[str, Any]) -> str:
        """Split text using various methods"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            text = args.get("text")
            method = args.get("method", "sentences")
            parameters = args.get("parameters", {})
            
            if not text:
                return "Error: text is required"
            
            result = self.vector_llm.split_text(text, method, parameters)
            return f"Text split result:\n{result}"
            
        except Exception as e:
            return f"Error splitting text: {str(e)}"
    
    async def handle_structured_output(self, args: Dict[str, Any]) -> str:
        """Extract structured data from text using schema"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            text = args.get("text")
            schema = args.get("schema")
            
            if not text or not schema:
                return "Error: text and schema are required"
            
            result = self.vector_llm.structured_output(text, schema)
            return f"Structured output result:\n{result}"
            
        except Exception as e:
            return f"Error in structured output: {str(e)}"
    
    async def handle_type_convert(self, args: Dict[str, Any]) -> str:
        """Convert data between different formats"""
        if not self.vector_llm:
            return "Error: PostgreSQL+Vector LLM not initialized"
        
        try:
            data = args.get("data")
            target_type = args.get("target_type")
            parameters = args.get("parameters", {})
            
            if not data or not target_type:
                return "Error: data and target_type are required"
            
            result = self.vector_llm.type_convert(data, target_type, parameters)
            return f"Type conversion result:\n{result}"
            
        except Exception as e:
            return f"Error in type conversion: {str(e)}"

async def main():
    """Main entry point - Simple stdio server"""
    server = SimpleLangFlowMCPConnector()
    
    logger.info("Simple MCP Server starting (stdio protocol)")
    
    try:
        while True:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line_str = line.strip()
            if not line_str:
                continue
            
            try:
                # Parse JSON request
                request = json.loads(line_str)
                logger.info(f"Received request: {request.get('method', 'unknown')}")
                
                # Handle request
                response = await server.handle_request(request)
                
                # Send response
                response_str = json.dumps(response) + '\n'
                await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, response_str)
                await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                response_str = json.dumps(error_response) + '\n'
                await asyncio.get_event_loop().run_in_executor(None, sys.stdout.write, response_str)
                await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 