#!/usr/bin/env python3
"""
LangFlow Connect MVP - Enhanced Tools Server
Universal file access with GitHub, HTTP, and local file support.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import logging
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
from urllib.parse import urlparse, unquote
import tempfile
import shutil
import time
import statistics
from collections import defaultdict, deque
import threading
import asyncio
import mimetypes
import base64
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EnhancedToolsAPI')

# Content Preview System
class ContentPreviewManager:
    """Manage file content preview with syntax highlighting and rendering"""
    
    # Supported file types for preview
    SUPPORTED_PREVIEW_TYPES = {
        # Code files with syntax highlighting
        'code': {
            'extensions': ['.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sh', '.bash', '.sql', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift', '.kt'],
            'mime_types': ['text/plain', 'application/json', 'text/xml', 'text/yaml', 'text/markdown']
        },
        # Image files
        'image': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/svg+xml', 'image/webp']
        },
        # Document files
        'document': {
            'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
            'mime_types': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        }
    }
    
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detect file type for preview"""
        file_ext = Path(file_path).suffix.lower()
        
        # Check extensions first
        for preview_type, config in ContentPreviewManager.SUPPORTED_PREVIEW_TYPES.items():
            if file_ext in config['extensions']:
                return preview_type
        
        # Check MIME type as fallback
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            for preview_type, config in ContentPreviewManager.SUPPORTED_PREVIEW_TYPES.items():
                if mime_type in config['mime_types']:
                    return preview_type
        
        return 'unknown'
    
    @staticmethod
    def get_syntax_highlighting_language(file_path: str) -> str:
        """Get syntax highlighting language for code files"""
        file_ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sh': 'bash',
            '.bash': 'bash',
            '.sql': 'sql',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'cpp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        return language_map.get(file_ext, 'text')
    
    @staticmethod
    def format_code_with_syntax_highlighting(content: str, language: str) -> str:
        """Format code with syntax highlighting (simplified version)"""
        # This is a simplified syntax highlighting implementation
        # In a production environment, you might want to use libraries like Pygments
        
        if language == 'python':
            # Basic Python syntax highlighting
            keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'True', 'False', 'None']
            content = ContentPreviewManager._highlight_keywords(content, keywords, 'keyword')
            content = ContentPreviewManager._highlight_strings(content)
            content = ContentPreviewManager._highlight_comments(content)
        elif language == 'javascript':
            # Basic JavaScript syntax highlighting
            keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'return', 'class', 'import', 'export', 'default']
            content = ContentPreviewManager._highlight_keywords(content, keywords, 'keyword')
            content = ContentPreviewManager._highlight_strings(content)
            content = ContentPreviewManager._highlight_comments(content)
        elif language == 'json':
            # JSON syntax highlighting
            content = ContentPreviewManager._highlight_json(content)
        elif language == 'html':
            # HTML syntax highlighting
            content = ContentPreviewManager._highlight_html(content)
        elif language == 'css':
            # CSS syntax highlighting
            content = ContentPreviewManager._highlight_css(content)
        
        return content
    
    @staticmethod
    def _highlight_keywords(content: str, keywords: List[str], class_name: str) -> str:
        """Highlight keywords in content"""
        for keyword in keywords:
            content = re.sub(r'\b' + re.escape(keyword) + r'\b', f'<span class="{class_name}">{keyword}</span>', content)
        return content
    
    @staticmethod
    def _highlight_strings(content: str) -> str:
        """Highlight string literals"""
        # Highlight single and double quoted strings
        content = re.sub(r'(".*?")', r'<span class="string">\1</span>', content)
        content = re.sub(r"('.*?')", r'<span class="string">\1</span>', content)
        return content
    
    @staticmethod
    def _highlight_comments(content: str) -> str:
        """Highlight comments"""
        # Highlight Python comments
        content = re.sub(r'(#.*?)$', r'<span class="comment">\1</span>', content, flags=re.MULTILINE)
        # Highlight JavaScript comments
        content = re.sub(r'(//.*?)$', r'<span class="comment">\1</span>', content, flags=re.MULTILINE)
        content = re.sub(r'(/\*.*?\*/)', r'<span class="comment">\1</span>', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def _highlight_json(content: str) -> str:
        """Highlight JSON syntax"""
        content = re.sub(r'(".*?":)', r'<span class="key">\1</span>', content)
        content = re.sub(r'(".*?")', r'<span class="string">\1</span>', content)
        content = re.sub(r'\b(true|false|null)\b', r'<span class="keyword">\1</span>', content)
        return content
    
    @staticmethod
    def _highlight_html(content: str) -> str:
        """Highlight HTML syntax"""
        content = re.sub(r'(<.*?>)', r'<span class="tag">\1</span>', content)
        content = re.sub(r'(".*?")', r'<span class="string">\1</span>', content)
        return content
    
    @staticmethod
    def _highlight_css(content: str) -> str:
        """Highlight CSS syntax"""
        content = re.sub(r'([a-zA-Z-]+):', r'<span class="property">\1</span>:', content)
        content = re.sub(r'(".*?")', r'<span class="string">\1</span>', content)
        content = re.sub(r'(/\*.*?\*/)', r'<span class="comment">\1</span>', content, flags=re.DOTALL)
        return content
    
    @staticmethod
    def render_markdown(content: str) -> str:
        """Render markdown content to HTML"""
        # This is a simplified markdown renderer
        # In production, you might want to use libraries like markdown2 or mistune
        
        # Headers
        content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Bold and italic
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        
        # Code blocks
        content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
        content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
        
        # Links
        content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', content)
        
        # Lists
        content = re.sub(r'^\* (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'^- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        
        # Paragraphs
        content = re.sub(r'\n\n', r'</p><p>', content)
        content = f'<p>{content}</p>'
        
        return content
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """Encode image to base64 for inline display"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                mime_type, _ = mimetypes.guess_type(image_path)
                return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return ""
    
    @staticmethod
    def create_preview_html(content: str, file_type: str, language: str = None) -> str:
        """Create HTML preview for file content"""
        css_styles = """
        <style>
            .preview-container {
                font-family: 'Courier New', monospace;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                overflow-x: auto;
            }
            .code-content {
                white-space: pre-wrap;
                line-height: 1.5;
            }
            .keyword { color: #007bff; font-weight: bold; }
            .string { color: #28a745; }
            .comment { color: #6c757d; font-style: italic; }
            .key { color: #dc3545; font-weight: bold; }
            .tag { color: #fd7e14; }
            .property { color: #6f42c1; }
            .image-preview {
                max-width: 100%;
                height: auto;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            .markdown-content {
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }
            .markdown-content h1, .markdown-content h2, .markdown-content h3 {
                color: #333;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .markdown-content code {
                background-color: #f1f3f4;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .markdown-content pre {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
        """
        
        if file_type == 'code':
            highlighted_content = ContentPreviewManager.format_code_with_syntax_highlighting(content, language or 'text')
            return f"""
            {css_styles}
            <div class="preview-container">
                <div class="code-content">{highlighted_content}</div>
            </div>
            """
        elif file_type == 'image':
            return f"""
            {css_styles}
            <div class="preview-container">
                <img src="{content}" alt="Image Preview" class="image-preview">
            </div>
            """
        elif file_type == 'document':
            return f"""
            {css_styles}
            <div class="preview-container">
                <p><strong>Document Preview:</strong> This file type requires external viewer.</p>
                <p>File content length: {len(content)} characters</p>
            </div>
            """
        else:
            return f"""
            {css_styles}
            <div class="preview-container">
                <div class="code-content">{content}</div>
            </div>
            """

# Performance Monitoring System
class PerformanceMonitor:
    """Real-time performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {
            'response_times': defaultdict(lambda: deque(maxlen=100)),  # Last 100 requests per tool
            'success_rates': defaultdict(lambda: deque(maxlen=100)),   # Last 100 results per tool
            'error_counts': defaultdict(int),                          # Total errors per tool
            'total_requests': defaultdict(int),                        # Total requests per tool
            'start_time': datetime.now(),
            'system_metrics': {
                'cpu_usage': deque(maxlen=50),
                'memory_usage': deque(maxlen=50),
                'disk_usage': deque(maxlen=50)
            }
        }
        self.lock = threading.Lock()
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    memory_percent = memory.percent
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    
                    with self.lock:
                        self.metrics['system_metrics']['cpu_usage'].append(cpu_percent)
                        self.metrics['system_metrics']['memory_usage'].append(memory_percent)
                        self.metrics['system_metrics']['disk_usage'].append(disk_percent)
                    
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def record_request(self, tool_name: str, response_time: float, success: bool):
        """Record a tool request with performance metrics"""
        with self.lock:
            self.metrics['response_times'][tool_name].append(response_time)
            self.metrics['success_rates'][tool_name].append(1 if success else 0)
            self.metrics['total_requests'][tool_name] += 1
            
            if not success:
                self.metrics['error_counts'][tool_name] += 1
    
    def get_tool_metrics(self, tool_name: str = None) -> Dict[str, Any]:
        """Get performance metrics for a specific tool or all tools"""
        with self.lock:
            if tool_name:
                return self._get_single_tool_metrics(tool_name)
            else:
                return self._get_all_tools_metrics()
    
    def _get_single_tool_metrics(self, tool_name: str) -> Dict[str, Any]:
        """Get metrics for a single tool"""
        response_times = list(self.metrics['response_times'][tool_name])
        success_rates = list(self.metrics['success_rates'][tool_name])
        
        if not response_times:
            return {
                'tool_name': tool_name,
                'total_requests': 0,
                'error_count': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'recent_performance': []
            }
        
        return {
            'tool_name': tool_name,
            'total_requests': self.metrics['total_requests'][tool_name],
            'error_count': self.metrics['error_counts'][tool_name],
            'success_rate': (sum(success_rates) / len(success_rates)) * 100 if success_rates else 0.0,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'recent_performance': [
                {
                    'timestamp': datetime.now() - timedelta(seconds=i*30),
                    'response_time': response_times[-(i+1)] if i < len(response_times) else 0,
                    'success': success_rates[-(i+1)] if i < len(success_rates) else 0
                }
                for i in range(min(10, len(response_times)))  # Last 10 requests
            ]
        }
    
    def _get_all_tools_metrics(self) -> Dict[str, Any]:
        """Get metrics for all tools"""
        all_tools = set(self.metrics['total_requests'].keys())
        tools_metrics = {}
        
        for tool in all_tools:
            tools_metrics[tool] = self._get_single_tool_metrics(tool)
        
        # System metrics
        cpu_usage = list(self.metrics['system_metrics']['cpu_usage'])
        memory_usage = list(self.metrics['system_metrics']['memory_usage'])
        disk_usage = list(self.metrics['system_metrics']['disk_usage'])
        
        return {
            'overview': {
                'total_requests': sum(self.metrics['total_requests'].values()),
                'total_errors': sum(self.metrics['error_counts'].values()),
                'overall_success_rate': self._calculate_overall_success_rate(),
                'uptime_seconds': (datetime.now() - self.metrics['start_time']).total_seconds(),
                'start_time': self.metrics['start_time'].isoformat()
            },
            'system_metrics': {
                'cpu_usage': {
                    'current': cpu_usage[-1] if cpu_usage else 0,
                    'average': statistics.mean(cpu_usage) if cpu_usage else 0,
                    'max': max(cpu_usage) if cpu_usage else 0
                },
                'memory_usage': {
                    'current': memory_usage[-1] if memory_usage else 0,
                    'average': statistics.mean(memory_usage) if memory_usage else 0,
                    'max': max(memory_usage) if memory_usage else 0
                },
                'disk_usage': {
                    'current': disk_usage[-1] if disk_usage else 0,
                    'average': statistics.mean(disk_usage) if disk_usage else 0,
                    'max': max(disk_usage) if disk_usage else 0
                }
            },
            'tools': tools_metrics
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all tools"""
        total_success = 0
        total_requests = 0
        
        for tool_name in self.metrics['success_rates']:
            success_rates = list(self.metrics['success_rates'][tool_name])
            total_success += sum(success_rates)
            total_requests += len(success_rates)
        
        return (total_success / total_requests * 100) if total_requests > 0 else 0.0
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        alerts = []
        
        with self.lock:
            # Check response time alerts
            for tool_name, response_times in self.metrics['response_times'].items():
                if response_times:
                    avg_time = statistics.mean(response_times)
                    if avg_time > 2000:  # Alert if average > 2 seconds
                        alerts.append({
                            'type': 'high_response_time',
                            'tool': tool_name,
                            'message': f'High average response time: {avg_time:.2f}ms',
                            'severity': 'warning',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Check success rate alerts
            for tool_name, success_rates in self.metrics['success_rates'].items():
                if success_rates:
                    success_rate = (sum(success_rates) / len(success_rates)) * 100
                    if success_rate < 90:  # Alert if success rate < 90%
                        alerts.append({
                            'type': 'low_success_rate',
                            'tool': tool_name,
                            'message': f'Low success rate: {success_rate:.1f}%',
                            'severity': 'error',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Check system resource alerts
            cpu_usage = list(self.metrics['system_metrics']['cpu_usage'])
            memory_usage = list(self.metrics['system_metrics']['memory_usage'])
            
            if cpu_usage and cpu_usage[-1] > 80:
                alerts.append({
                    'type': 'high_cpu_usage',
                    'tool': 'system',
                    'message': f'High CPU usage: {cpu_usage[-1]:.1f}%',
                    'severity': 'warning',
                    'timestamp': datetime.now().isoformat()
                })
            
            if memory_usage and memory_usage[-1] > 80:
                alerts.append({
                    'type': 'high_memory_usage',
                    'tool': 'system',
                    'message': f'High memory usage: {memory_usage[-1]:.1f}%',
                    'severity': 'warning',
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts

# Initialize performance monitor
performance_monitor = PerformanceMonitor()

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Connect MVP - Enhanced Tools API",
    description="AI-Powered Development Tools with Universal File Access",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://capstone-project-dashboard.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add essential security headers
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    for header, value in security_headers.items():
        response.headers[header] = value
    
    # Add custom headers
    response.headers["X-API-Version"] = "3.0.0"
    response.headers["X-Security-Level"] = "Enhanced"
    response.headers["X-Tools-Capability"] = "Universal"
    
    logger.info(f"Security headers applied to {request.url.path}")
    
    return response

@app.middleware("http")
async def performance_monitoring_middleware(request: Request, call_next):
    """Monitor performance of all requests"""
    start_time = time.time()
    
    # Extract tool name from path only (avoid reading request body)
    tool_name = "unknown"
    if request.url.path == "/api/v1/tools/call":
        tool_name = "tool_call"  # Generic name for all tool calls
    elif request.url.path.startswith("/health"):
        tool_name = "health_check"
    elif request.url.path.startswith("/debug"):
        tool_name = "debug_endpoint"
    elif request.url.path.startswith("/tools"):
        tool_name = "tools_endpoint"
    elif request.url.path.startswith("/security"):
        tool_name = "security_endpoint"
    elif request.url.path.startswith("/performance"):
        tool_name = "performance_endpoint"
    else:
        tool_name = "other"
    
    # Process the request
    response = await call_next(request)
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Determine if request was successful
    success = 200 <= response.status_code < 400
    
    # Record performance metrics
    performance_monitor.record_request(tool_name, response_time, success)
    
    # Add performance headers
    response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
    response.headers["X-Request-Success"] = str(success).lower()
    
    # Log performance for slow requests
    if response_time > 1000:  # Log requests taking more than 1 second
        logger.warning(f"Slow request: {tool_name} took {response_time:.2f}ms")
    
    return response

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    valid_keys = ['demo_key_123', 'admin_key_456']
    return api_key in valid_keys

class PathResolver:
    """Smart path resolution with multiple source support"""
    
    @staticmethod
    def detect_source_type(path: str) -> str:
        """Detect the type of source (local, github, http)"""
        if path.startswith(('http://', 'https://')):
            if 'github.com' in path:
                return 'github'
            else:
                return 'http'
        elif os.path.isabs(path):
            return 'local_absolute'
        elif ':' in path and len(path) > 2 and path[1] == ':':
            # Windows-style absolute path (e.g., D:\path\to\file)
            return 'local_absolute'
        else:
            return 'local_relative'
    
    @staticmethod
    def resolve_path(path: str) -> Dict[str, Any]:
        """Resolve path and return metadata"""
        source_type = PathResolver.detect_source_type(path)
        
        if source_type == 'github':
            return PathResolver._parse_github_url(path)
        elif source_type == 'http':
            return PathResolver._parse_http_url(path)
        elif source_type == 'local_absolute':
            return PathResolver._validate_absolute_path(path)
        else:
            return PathResolver._normalize_relative_path(path)
    
    @staticmethod
    def _parse_github_url(url: str) -> Dict[str, Any]:
        """Parse GitHub URL and extract repository/file info"""
        try:
            # Handle different GitHub URL formats
            if '/blob/' in url:
                # File URL: https://github.com/user/repo/blob/branch/path
                parts = url.split('/blob/')
                repo_url = parts[0]
                file_path = parts[1].split('/', 1)[1] if len(parts[1].split('/', 1)) > 1 else ""
                branch = parts[1].split('/')[0]
            else:
                # Repository URL: https://github.com/user/repo
                repo_url = url
                file_path = ""
                branch = "main"
            
            # Extract owner and repo name
            repo_parts = repo_url.split('github.com/')[-1].split('/')
            owner = repo_parts[0]
            repo_name = repo_parts[1]
            
            return {
                'source_type': 'github',
                'owner': owner,
                'repo_name': repo_name,
                'branch': branch,
                'file_path': file_path,
                'original_url': url,
                'api_url': f"https://api.github.com/repos/{owner}/{repo_name}",
                'raw_url': f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid GitHub URL: {str(e)}")
    
    @staticmethod
    def _parse_http_url(url: str) -> Dict[str, Any]:
        """Parse HTTP URL"""
        try:
            parsed = urlparse(url)
            return {
                'source_type': 'http',
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'original_url': url
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid HTTP URL: {str(e)}")
    
    @staticmethod
    def _validate_absolute_path(path: str) -> Dict[str, Any]:
        """Validate and normalize absolute path"""
        try:
            # Handle Windows-style paths on Linux
            if ':' in path and len(path) > 2 and path[1] == ':':
                # Convert Windows path to Linux-style path
                # Remove drive letter and convert backslashes to forward slashes
                linux_path = path.replace('\\', '/').split(':', 1)[1]
                # Remove leading slash if present
                if linux_path.startswith('/'):
                    linux_path = linux_path[1:]
                
                # Extract the path components
                path_parts = linux_path.split('/')
                
                # Determine if this is likely a file or directory
                # If the path ends with a common file extension, treat as file
                # Otherwise, treat as directory
                has_file_extension = any(path_parts[-1].lower().endswith(ext) for ext in 
                                       ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml'])
                
                if has_file_extension:
                    # This is likely a file path
                    filename = path_parts[-1]
                    directory = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ""
                    
                    # Try to find the file in common locations
                    possible_paths = [
                        f"/opt/render/project/src/{filename}",  # Most likely location
                        f"/opt/render/project/{filename}",
                        f"/app/{filename}",
                        f"/home/render/{filename}",
                        linux_path  # Try as-is
                    ]
                    
                    # Add directory-based paths if directory exists
                    if directory:
                        possible_paths.extend([
                            f"/opt/render/project/src/{directory}/{filename}",
                            f"/opt/render/project/{directory}/{filename}"
                        ])
                else:
                    # This is likely a directory path
                    directory_name = path_parts[-1] if path_parts else ""
                    
                    # For directory paths, map to the current working directory
                    # since the Windows path structure doesn't match the Render structure
                    # The Windows path D:\GUI\System-Reference-Clean\LangFlow_Connect should map to /opt/render/project/src
                    possible_paths = [
                        "/opt/render/project/src",  # Current working directory where server runs (most likely)
                        "/opt/render/project",      # Project root
                        f"/opt/render/project/src/{directory_name}",
                        f"/opt/render/project/{directory_name}",
                        f"/app/{directory_name}",
                        f"/home/render/{directory_name}",
                        linux_path  # Try as-is
                    ]
                    
                    # Special case: if the directory name matches common project names,
                    # prioritize mapping to the current working directory
                    if directory_name.lower() in ['langflow_connect', 'langflow', 'connect', 'project']:
                        possible_paths.insert(0, "/opt/render/project/src")
                
                # Test each possible path
                for test_path in possible_paths:
                    if os.path.exists(test_path):
                        return {
                            'source_type': 'local_absolute',
                            'path': test_path,
                            'original_windows_path': path,
                            'exists': True
                        }
                
                # If not found, return the most likely path for better error reporting
                if has_file_extension:
                    most_likely_path = f"/opt/render/project/src/{filename}"
                else:
                    most_likely_path = "/opt/render/project/src"  # Default to current directory
                
                return {
                    'source_type': 'local_absolute',
                    'path': most_likely_path,
                    'original_windows_path': path,
                    'exists': False,
                    'tried_paths': possible_paths
                }
            else:
                # Standard absolute path handling
                normalized = os.path.normpath(path)
                if os.path.exists(normalized):
                    return {
                        'source_type': 'local_absolute',
                        'path': normalized,
                        'exists': True
                    }
                else:
                    return {
                        'source_type': 'local_absolute',
                        'path': normalized,
                        'exists': False
                    }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid absolute path: {str(e)}")
    
    @staticmethod
    def _normalize_relative_path(path: str) -> Dict[str, Any]:
        """Normalize relative path"""
        try:
            normalized = os.path.normpath(path)
            full_path = os.path.abspath(normalized)
            
            if os.path.exists(full_path):
                return {
                    'source_type': 'local_relative',
                    'path': full_path,
                    'relative_path': normalized,
                    'exists': True
                }
            else:
                return {
                    'source_type': 'local_relative',
                    'path': full_path,
                    'relative_path': normalized,
                    'exists': False
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid relative path: {str(e)}")

class FileAccessManager:
    """Universal file access manager"""
    
    @staticmethod
    async def get_file_content(path_info: Dict[str, Any]) -> str:
        """Get file content from any source"""
        source_type = path_info['source_type']
        
        if source_type == 'github':
            return await FileAccessManager._get_github_content(path_info)
        elif source_type == 'http':
            return await FileAccessManager._get_http_content(path_info)
        else:
            return await FileAccessManager._get_local_content(path_info)
    
    @staticmethod
    async def _get_github_content(path_info: Dict[str, Any]) -> str:
        """Get content from GitHub"""
        try:
            if path_info['file_path']:
                # Get specific file
                raw_url = f"{path_info['raw_url']}/{path_info['file_path']}"
                response = requests.get(raw_url, timeout=10)
                response.raise_for_status()
                return response.text
            else:
                # Get repository info
                response = requests.get(path_info['api_url'], timeout=10)
                response.raise_for_status()
                repo_info = response.json()
                return f"Repository: {repo_info['name']}\nDescription: {repo_info.get('description', 'No description')}\nURL: {repo_info['html_url']}"
        except requests.RequestException as e:
            raise HTTPException(status_code=404, detail=f"GitHub content not found: {str(e)}")
    
    @staticmethod
    async def _get_http_content(path_info: Dict[str, Any]) -> str:
        """Get content from HTTP URL"""
        try:
            response = requests.get(path_info['original_url'], timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise HTTPException(status_code=404, detail=f"HTTP content not found: {str(e)}")
    
    @staticmethod
    async def _get_local_content(path_info: Dict[str, Any]) -> str:
        """Get content from local file"""
        try:
            if not path_info.get('exists', False):
                original_path = path_info.get('original_windows_path', path_info['path'])
                error_msg = f"File not found: {path_info['path']}"
                if 'original_windows_path' in path_info:
                    error_msg += f" (converted from Windows path: {original_path})"
                if 'tried_paths' in path_info:
                    error_msg += f" (tried paths: {path_info['tried_paths']})"
                raise FileNotFoundError(error_msg)
            
            with open(path_info['path'], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            original_path = path_info.get('original_windows_path', path_info['path'])
            error_msg = f"Local file not found: {str(e)}"
            if 'original_windows_path' in path_info:
                error_msg += f" (converted from Windows path: {original_path})"
            if 'tried_paths' in path_info:
                error_msg += f" (tried paths: {path_info['tried_paths']})"
            raise HTTPException(status_code=404, detail=error_msg)
    
    @staticmethod
    async def list_directory(path_info: Dict[str, Any]) -> List[str]:
        """List directory contents from any source"""
        source_type = path_info['source_type']
        
        if source_type == 'github':
            return await FileAccessManager._list_github_directory(path_info)
        elif source_type == 'http':
            return await FileAccessManager._list_http_directory(path_info)
        else:
            return await FileAccessManager._list_local_directory(path_info)
    
    @staticmethod
    async def _list_github_directory(path_info: Dict[str, Any]) -> List[str]:
        """List GitHub repository contents"""
        try:
            api_url = f"{path_info['api_url']}/contents"
            if path_info['file_path']:
                api_url += f"/{path_info['file_path']}"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            contents = response.json()
            
            if isinstance(contents, list):
                return [item['name'] for item in contents]
            else:
                return [contents['name']]
        except requests.RequestException as e:
            raise HTTPException(status_code=404, detail=f"GitHub directory not found: {str(e)}")
    
    @staticmethod
    async def _list_http_directory(path_info: Dict[str, Any]) -> List[str]:
        """List HTTP directory contents (basic implementation)"""
        # For HTTP, we'll return a basic message since directory listing isn't always available
        return ["HTTP directory listing not available", "Use direct file URLs instead"]
    
    @staticmethod
    async def _list_local_directory(path_info: Dict[str, Any]) -> List[str]:
        """List local directory contents"""
        try:
            if not path_info.get('exists', False):
                original_path = path_info.get('original_windows_path', path_info['path'])
                error_msg = f"Directory not found: {path_info['path']}"
                if 'original_windows_path' in path_info:
                    error_msg += f" (converted from Windows path: {original_path})"
                if 'tried_paths' in path_info:
                    error_msg += f" (tried paths: {path_info['tried_paths']})"
                raise FileNotFoundError(error_msg)
            
            if not os.path.isdir(path_info['path']):
                raise NotADirectoryError(f"Path is not a directory: {path_info['path']}")
            
            return os.listdir(path_info['path'])
        except Exception as e:
            original_path = path_info.get('original_windows_path', path_info['path'])
            error_msg = f"Local directory not found: {str(e)}"
            if 'original_windows_path' in path_info:
                error_msg += f" (converted from Windows path: {original_path})"
            if 'tried_paths' in path_info:
                error_msg += f" (tried paths: {path_info['tried_paths']})"
            raise HTTPException(status_code=404, detail=error_msg)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "security": "enhanced",
        "tools_count": 5,
        "capabilities": ["universal_file_access", "github_integration", "http_support"]
    }

@app.get("/debug/directory-structure")
async def debug_directory_structure():
    """Debug endpoint to understand directory structure on Render"""
    try:
        current_dir = os.getcwd()
        project_root = "/opt/render/project"
        
        # Get current directory contents
        current_contents = []
        if os.path.exists(current_dir):
            current_contents = os.listdir(current_dir)
        
        # Get project root contents
        project_contents = []
        if os.path.exists(project_root):
            project_contents = os.listdir(project_root)
        
        # Get src directory contents
        src_contents = []
        src_path = os.path.join(project_root, "src")
        if os.path.exists(src_path):
            src_contents = os.listdir(src_path)
        
        return {
            "current_directory": current_dir,
            "current_contents": current_contents,
            "project_root": project_root,
            "project_contents": project_contents,
            "src_directory": src_path,
            "src_contents": src_contents,
            "environment": {
                "platform": os.name,
                "cwd": os.getcwd(),
                "env_vars": {k: v for k, v in os.environ.items() if 'RENDER' in k or 'PATH' in k}
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/tools/list")
async def get_tools_list(request: Request):
    """Get list of available tools with enhanced capabilities"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    tools = [
        {
            "name": "ping",
            "description": "Test server connectivity",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "capabilities": ["basic"]
        },
        {
            "name": "read_file",
            "description": "Read contents of a file from any source (local, GitHub, HTTP)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read (supports local paths, GitHub URLs, HTTP URLs)"
                    }
                },
                "required": ["file_path"]
            },
            "capabilities": ["universal_access", "github", "http", "local"],
            "examples": [
                "README.md (local file)",
                "src/main.py (relative path)",
                "https://github.com/user/repo/blob/main/file.md (GitHub file)",
                "https://example.com/file.txt (HTTP file)"
            ]
        },
        {
            "name": "list_files",
            "description": "List files in a directory or repository from any source",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list (supports local paths, GitHub URLs, HTTP URLs)"
                    }
                },
                "required": ["directory"]
            },
            "capabilities": ["universal_access", "github", "http", "local"],
            "examples": [
                ". (current directory)",
                "src/ (specific directory)",
                "https://github.com/user/repo (GitHub repository)",
                "D:/Projects/MyProject (absolute path)"
            ]
        },
        {
            "name": "get_system_status",
            "description": "Get system status and metrics",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "capabilities": ["basic"]
        },
        {
            "name": "analyze_code",
            "description": "Analyze code files from any source with comprehensive metrics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze (supports local paths, GitHub URLs, HTTP URLs)"
                    }
                },
                "required": ["file_path"]
            },
            "capabilities": ["universal_access", "github", "http", "local", "code_analysis"],
            "examples": [
                "src/main.py (local file)",
                "https://github.com/user/repo/blob/main/app.py (GitHub file)",
                "https://example.com/script.js (HTTP file)"
            ]
        }
    ]
    
    return {"tools": tools}

@app.post("/api/v1/tools/call")
async def execute_tool(request: Request):
    """Execute a tool with universal file access"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    try:
        body = await request.json()
        tool_name = body.get('name')
        arguments = body.get('arguments', {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        if not isinstance(arguments, dict):
            raise HTTPException(status_code=400, detail="Arguments must be an object")
        
        # Record specific tool execution for detailed metrics
        start_time = time.time()
        try:
            result = await execute_tool_enhanced(tool_name, arguments)
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_request(tool_name, execution_time, True)
            
            return {
                "success": True,
                "tool": tool_name,
                "content": result
            }
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_request(tool_name, execution_time, False)
            raise e
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

async def execute_tool_enhanced(tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute tool with universal file access"""
    
    if tool_name == "ping":
        return [{"type": "text", "text": "pong"}]
    
    elif tool_name == "read_file":
        file_path = arguments.get('file_path', '')
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        # Resolve path
        path_info = PathResolver.resolve_path(file_path)
        
        # Get content
        content = await FileAccessManager.get_file_content(path_info)
        
        # Add metadata
        metadata = f"Source: {path_info['source_type']}\n"
        if path_info['source_type'] == 'github':
            metadata += f"Repository: {path_info['owner']}/{path_info['repo_name']}\n"
            metadata += f"Branch: {path_info['branch']}\n"
        elif path_info['source_type'] == 'local_absolute':
            metadata += f"Path: {path_info['path']}\n"
        
        return [{"type": "text", "text": f"{metadata}\n--- Content ---\n{content}"}]
    
    elif tool_name == "list_files":
        directory = arguments.get('directory', '.')
        
        # Resolve path
        path_info = PathResolver.resolve_path(directory)
        
        # List contents
        files = await FileAccessManager.list_directory(path_info)
        
        # Format output
        metadata = f"Source: {path_info['source_type']}\n"
        if path_info['source_type'] == 'github':
            metadata += f"Repository: {path_info['owner']}/{path_info['repo_name']}\n"
            metadata += f"Branch: {path_info['branch']}\n"
        elif path_info['source_type'] == 'local_absolute':
            metadata += f"Path: {path_info['path']}\n"
        
        files_list = "\n".join([f"- {file}" for file in files])
        
        return [{"type": "text", "text": f"{metadata}\n--- Files ---\n{files_list}"}]
    
    elif tool_name == "get_system_status":
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        return [{
            "type": "text",
            "text": f"System Status:\nCPU Usage: {cpu_percent}%\nMemory Usage: {memory.percent}%\nAvailable Memory: {memory.available / (1024**3):.1f} GB\nTotal Memory: {memory.total / (1024**3):.1f} GB\nStatus: Healthy\nSecurity: Enhanced\nTools: Universal Access Enabled"
        }]
    
    elif tool_name == "analyze_code":
        file_path = arguments.get('file_path', '')
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        # Resolve path
        path_info = PathResolver.resolve_path(file_path)
        
        # Get content
        content = await FileAccessManager.get_file_content(path_info)
        
        # Analyze code
        lines = content.split('\n')
        char_count = len(content)
        word_count = len(content.split())
        file_size = len(content.encode('utf-8'))
        
        # Detect file type
        file_extension = os.path.splitext(path_info.get('file_path', '') or path_info.get('path', ''))[1].lower()
        
        analysis = f"Code Analysis:\n"
        analysis += f"Source: {path_info['source_type']}\n"
        if path_info['source_type'] == 'github':
            analysis += f"Repository: {path_info['owner']}/{path_info['repo_name']}\n"
            analysis += f"File: {path_info['file_path']}\n"
        elif path_info['source_type'] == 'local_absolute':
            analysis += f"Path: {path_info['path']}\n"
        
        analysis += f"File Type: {file_extension or 'Unknown'}\n"
        analysis += f"Lines: {len(lines)}\n"
        analysis += f"Characters: {char_count}\n"
        analysis += f"Words: {word_count}\n"
        analysis += f"File Size: {file_size} bytes\n"
        analysis += f"Security: Validated\n"
        analysis += f"Access: Universal"
        
        return [{"type": "text", "text": analysis}]
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

@app.get("/security/status")
async def get_security_status():
    """Get security status"""
    return {
        "security_status": "enhanced",
        "headers_enabled": True,
        "cors_configured": True,
        "api_key_validation": True,
        "universal_access": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tools/capabilities")
async def get_tools_capabilities():
    """Get tools capabilities and supported features"""
    return {
        "capabilities": [
            "universal_file_access",
            "github_integration", 
            "http_support",
            "windows_path_handling",
            "performance_monitoring",
            "real_time_metrics"
        ],
        "supported_sources": ["local", "github", "http", "windows_paths"],
        "performance_features": [
            "response_time_tracking",
            "success_rate_monitoring", 
            "system_resource_monitoring",
            "performance_alerts",
            "real_time_dashboard"
        ],
        "version": "3.0.0",
        "status": "enhanced"
    }

@app.get("/performance/metrics")
async def get_performance_metrics(tool_name: Optional[str] = None):
    """Get performance metrics for all tools or a specific tool"""
    try:
        metrics = performance_monitor.get_tool_metrics(tool_name)
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")

@app.get("/performance/alerts")
async def get_performance_alerts():
    """Get current performance alerts"""
    try:
        alerts = performance_monitor.get_performance_alerts()
        return {
            "success": True,
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance alerts: {str(e)}")

@app.get("/performance/dashboard")
async def get_performance_dashboard():
    """Get comprehensive performance dashboard data"""
    try:
        # Get all metrics
        all_metrics = performance_monitor.get_tool_metrics()
        alerts = performance_monitor.get_performance_alerts()
        
        # Calculate summary statistics
        total_requests = all_metrics['overview']['total_requests']
        total_errors = all_metrics['overview']['total_errors']
        overall_success_rate = all_metrics['overview']['overall_success_rate']
        uptime_seconds = all_metrics['overview']['uptime_seconds']
        
        # Get system health status
        system_metrics = all_metrics['system_metrics']
        cpu_usage = system_metrics['cpu_usage']['current']
        memory_usage = system_metrics['memory_usage']['current']
        disk_usage = system_metrics['disk_usage']['current']
        
        # Determine system health
        system_health = "healthy"
        if cpu_usage > 80 or memory_usage > 80 or disk_usage > 90:
            system_health = "warning"
        if cpu_usage > 95 or memory_usage > 95 or disk_usage > 95:
            system_health = "critical"
        
        # Get top performing and problematic tools
        tools_metrics = all_metrics['tools']
        tool_performance = []
        
        for tool_name, metrics in tools_metrics.items():
            if metrics['total_requests'] > 0:
                tool_performance.append({
                    'tool_name': tool_name,
                    'total_requests': metrics['total_requests'],
                    'success_rate': metrics['success_rate'],
                    'avg_response_time': metrics['avg_response_time'],
                    'error_count': metrics['error_count']
                })
        
        # Sort by total requests (most used first)
        tool_performance.sort(key=lambda x: x['total_requests'], reverse=True)
        
        return {
            "success": True,
            "dashboard": {
                "overview": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "overall_success_rate": overall_success_rate,
                    "uptime_hours": round(uptime_seconds / 3600, 2),
                    "system_health": system_health
                },
                "system_metrics": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                    "status": system_health
                },
                "alerts": {
                    "count": len(alerts),
                    "critical": len([a for a in alerts if a['severity'] == 'critical']),
                    "warnings": len([a for a in alerts if a['severity'] == 'warning']),
                    "errors": len([a for a in alerts if a['severity'] == 'error'])
                },
                "top_tools": tool_performance[:5],  # Top 5 most used tools
                "problematic_tools": [
                    tool for tool in tool_performance 
                    if tool['success_rate'] < 90 or tool['avg_response_time'] > 2000
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance dashboard: {str(e)}")

@app.get("/performance/health")
async def get_performance_health():
    """Get performance health status"""
    try:
        alerts = performance_monitor.get_performance_alerts()
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        error_alerts = [a for a in alerts if a['severity'] == 'error']
        
        # Determine overall health
        if critical_alerts:
            health_status = "critical"
        elif error_alerts:
            health_status = "error"
        elif alerts:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "success": True,
            "health": {
                "status": health_status,
                "alerts_count": len(alerts),
                "critical_count": len(critical_alerts),
                "error_count": len(error_alerts),
                "warning_count": len([a for a in alerts if a['severity'] == 'warning'])
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance health: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance health: {str(e)}")

# Content Preview Endpoints
@app.get("/preview/file")
async def preview_file(request: Request, file_path: str, preview_type: Optional[str] = None):
    """Preview file content with syntax highlighting and rendering"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    try:
        # Resolve path
        path_info = PathResolver.resolve_path(file_path)
        
        # Get file content
        content = await FileAccessManager.get_file_content(path_info)
        
        # Detect file type if not provided
        if not preview_type:
            preview_type = ContentPreviewManager.detect_file_type(file_path)
        
        # Get language for syntax highlighting
        language = None
        if preview_type == 'code':
            language = ContentPreviewManager.get_syntax_highlighting_language(file_path)
        
        # Create preview based on file type
        if preview_type == 'code':
            if language == 'markdown':
                # Render markdown
                rendered_content = ContentPreviewManager.render_markdown(content)
                preview_html = ContentPreviewManager.create_preview_html(rendered_content, 'markdown')
            else:
                # Syntax highlighting for code
                preview_html = ContentPreviewManager.create_preview_html(content, 'code', language)
        elif preview_type == 'image':
            # For images, we need to encode to base64
            if path_info['source_type'] == 'local_absolute':
                image_data = ContentPreviewManager.encode_image_to_base64(path_info['path'])
                preview_html = ContentPreviewManager.create_preview_html(image_data, 'image')
            else:
                # For remote images, use the URL directly
                preview_html = ContentPreviewManager.create_preview_html(content, 'image')
        else:
            # Default preview
            preview_html = ContentPreviewManager.create_preview_html(content, preview_type)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_type": preview_type,
            "language": language,
            "content_length": len(content),
            "preview_html": preview_html,
            "metadata": {
                "source_type": path_info['source_type'],
                "resolved_path": path_info.get('path', ''),
                "file_extension": Path(file_path).suffix.lower()
            }
        }
        
    except Exception as e:
        logger.error(f"Error previewing file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error previewing file: {str(e)}")

@app.get("/preview/supported-types")
async def get_supported_preview_types(request: Request):
    """Get list of supported file types for preview"""
    return {
        "success": True,
        "supported_types": ContentPreviewManager.SUPPORTED_PREVIEW_TYPES,
        "languages": {
            "python": [".py"],
            "javascript": [".js"],
            "typescript": [".ts"],
            "html": [".html"],
            "css": [".css"],
            "json": [".json"],
            "markdown": [".md"],
            "yaml": [".yaml", ".yml"],
            "bash": [".sh", ".bash"],
            "sql": [".sql"],
            "java": [".java"],
            "cpp": [".cpp", ".c", ".h"],
            "php": [".php"],
            "ruby": [".rb"],
            "go": [".go"],
            "rust": [".rs"],
            "swift": [".swift"],
            "kotlin": [".kt"]
        }
    }

@app.post("/preview/batch")
async def preview_multiple_files(request: Request):
    """Preview multiple files in batch"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    try:
        body = await request.json()
        file_paths = body.get('file_paths', [])
        
        if not file_paths or not isinstance(file_paths, list):
            raise HTTPException(status_code=400, detail="file_paths must be a non-empty list")
        
        if len(file_paths) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
        
        results = []
        for file_path in file_paths:
            try:
                # Resolve path
                path_info = PathResolver.resolve_path(file_path)
                
                # Get file content
                content = await FileAccessManager.get_file_content(path_info)
                
                # Detect file type
                preview_type = ContentPreviewManager.detect_file_type(file_path)
                
                # Get language
                language = None
                if preview_type == 'code':
                    language = ContentPreviewManager.get_syntax_highlighting_language(file_path)
                
                # Create preview
                if preview_type == 'code' and language == 'markdown':
                    rendered_content = ContentPreviewManager.render_markdown(content)
                    preview_html = ContentPreviewManager.create_preview_html(rendered_content, 'markdown')
                else:
                    preview_html = ContentPreviewManager.create_preview_html(content, preview_type, language)
                
                results.append({
                    "file_path": file_path,
                    "success": True,
                    "file_type": preview_type,
                    "language": language,
                    "content_length": len(content),
                    "preview_html": preview_html
                })
                
            except Exception as e:
                results.append({
                    "file_path": file_path,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total_files": len(file_paths),
            "successful_previews": len([r for r in results if r['success']])
        }
        
    except Exception as e:
        logger.error(f"Error in batch preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error in batch preview: {str(e)}")

@app.get("/preview/analyze")
async def analyze_file_for_preview(request: Request, file_path: str):
    """Analyze file to determine preview capabilities"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    try:
        # Detect file type
        preview_type = ContentPreviewManager.detect_file_type(file_path)
        
        # Get language if applicable
        language = None
        if preview_type == 'code':
            language = ContentPreviewManager.get_syntax_highlighting_language(file_path)
        
        # Check if file exists and is accessible
        path_info = PathResolver.resolve_path(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "preview_type": preview_type,
            "language": language,
            "supported": preview_type != 'unknown',
            "file_extension": Path(file_path).suffix.lower(),
            "source_type": path_info['source_type'],
            "exists": path_info.get('exists', False),
            "capabilities": {
                "syntax_highlighting": preview_type == 'code',
                "markdown_rendering": language == 'markdown',
                "image_preview": preview_type == 'image',
                "document_preview": preview_type == 'document'
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting LangFlow Connect MVP - Enhanced Tools API Server")
    logger.info("Universal file access enabled")
    logger.info("GitHub integration enabled")
    logger.info("HTTP support enabled")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
