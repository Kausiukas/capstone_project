#!/usr/bin/env python3
"""
LangFlow Connect MVP - Security Hardened MCP Server
Enhanced version with comprehensive security features.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import json
import time
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import secrets
from dataclasses import dataclass
import psutil

# Security configuration
SECURITY_CONFIG = {
    'rate_limit': {
        'health': "1000/hour",      # Health endpoint: 1000 requests per hour
        'tools_list': "500/hour",   # Tools list: 500 requests per hour
        'tool_execution': "200/hour" # Tool execution: 200 requests per hour
    },
    'api_keys': {
        'demo_key_123': {
            'name': 'Demo User',
            'permissions': ['read', 'execute'],
            'rate_limit_multiplier': 1.0
        },
        'admin_key_456': {
            'name': 'Admin User',
            'permissions': ['read', 'execute', 'admin'],
            'rate_limit_multiplier': 2.0
        }
    },
    'security_headers': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
}

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Connect MVP - Secure API",
    description="AI-Powered Development Tools with Enhanced Security",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
security = HTTPBearer(auto_error=False)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/secure_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SecureAPI')

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit dashboard
        "https://your-dashboard-domain.com",  # Production dashboard
        "http://localhost:3000",  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@dataclass
class SecurityAuditLog:
    timestamp: str
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    api_key: str
    success: bool
    response_time: float
    error_message: Optional[str] = None

class SecurityManager:
    def __init__(self):
        self.audit_logs = []
        self.failed_attempts = {}
        self.blocked_ips = set()
        self.api_key_usage = {}
    
    def log_request(self, request: Request, api_key: str, success: bool, response_time: float, error_message: str = None):
        """Log security audit information"""
        audit_log = SecurityAuditLog(
            timestamp=datetime.now().isoformat(),
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent', 'Unknown'),
            endpoint=request.url.path,
            method=request.method,
            api_key=api_key,
            success=success,
            response_time=response_time,
            error_message=error_message
        )
        
        self.audit_logs.append(audit_log)
        
        # Keep only last 1000 logs
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-1000:]
        
        # Track API key usage
        if api_key not in self.api_key_usage:
            self.api_key_usage[api_key] = {'requests': 0, 'last_used': None}
        
        self.api_key_usage[api_key]['requests'] += 1
        self.api_key_usage[api_key]['last_used'] = datetime.now().isoformat()
        
        # Log security events
        if not success:
            logger.warning(f"Failed request from {request.client.host}: {error_message}")
        else:
            logger.info(f"Successful request from {request.client.host} using key {api_key[:8]}...")
    
    def check_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked due to suspicious activity"""
        return ip_address in self.blocked_ips
    
    def record_failed_attempt(self, ip_address: str):
        """Record failed authentication attempt"""
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {'count': 0, 'first_attempt': datetime.now()}
        
        self.failed_attempts[ip_address]['count'] += 1
        
        # Block IP after 10 failed attempts in 1 hour
        if self.failed_attempts[ip_address]['count'] >= 10:
            time_since_first = datetime.now() - self.failed_attempts[ip_address]['first_attempt']
            if time_since_first < timedelta(hours=1):
                self.blocked_ips.add(ip_address)
                logger.warning(f"IP {ip_address} blocked due to multiple failed attempts")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        return {
            'total_requests': len(self.audit_logs),
            'failed_requests': len([log for log in self.audit_logs if not log.success]),
            'blocked_ips': len(self.blocked_ips),
            'active_api_keys': len(self.api_key_usage),
            'recent_failures': len([log for log in self.audit_logs[-100:] if not log.success])
        }

# Initialize security manager
security_manager = SecurityManager()

def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate API key and return the key if valid"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    if api_key not in SECURITY_CONFIG['api_keys']:
        security_manager.record_failed_attempt("unknown")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key

def get_api_key_info(api_key: str = Depends(validate_api_key)) -> Dict[str, Any]:
    """Get API key information"""
    return SECURITY_CONFIG['api_keys'][api_key]

def validate_request_origin(request: Request):
    """Validate request origin"""
    origin = request.headers.get('origin')
    referer = request.headers.get('referer')
    
    # Log suspicious requests
    if origin and origin not in ["http://localhost:8501", "https://your-dashboard-domain.com"]:
        logger.warning(f"Suspicious origin: {origin} from {request.client.host}")

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    for header, value in SECURITY_CONFIG['security_headers'].items():
        response.headers[header] = value
    
    return response

@app.middleware("http")
async def security_audit_middleware(request: Request, call_next):
    """Security audit middleware"""
    start_time = time.time()
    
    # Check if IP is blocked
    if security_manager.check_ip_blocked(request.client.host):
        logger.warning(f"Blocked request from {request.client.host}")
        return Response(
            content=json.dumps({"error": "Access denied"}),
            status_code=403,
            media_type="application/json"
        )
    
    # Validate request origin
    validate_request_origin(request)
    
    # Process request
    try:
        response = await call_next(request)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # Extract API key from authorization header
        auth_header = request.headers.get('authorization', '')
        api_key = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else 'none'
        
        # Log the request
        security_manager.log_request(
            request=request,
            api_key=api_key,
            success=response.status_code < 400,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        # Log the error
        security_manager.log_request(
            request=request,
            api_key='none',
            success=False,
            response_time=response_time,
            error_message=str(e)
        )
        
        raise

@app.get("/health")
@limiter.limit(SECURITY_CONFIG['rate_limit']['health'])
async def health_check(request: Request):
    """Health check endpoint with rate limiting"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "security": "enabled",
        "tools_count": 5
    }

@app.get("/tools/list")
@limiter.limit(SECURITY_CONFIG['rate_limit']['tools_list'])
async def get_tools_list(
    request: Request,
    api_key_info: Dict[str, Any] = Depends(get_api_key_info)
):
    """Get list of available tools with authentication"""
    tools = [
        {
            "name": "ping",
            "description": "Test server connectivity",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "read_file",
            "description": "Read contents of a file",
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
            "name": "list_files",
            "description": "List files in a directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list"
                    }
                },
                "required": ["directory"]
            }
        },
        {
            "name": "get_system_status",
            "description": "Get system status and metrics",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "analyze_code",
            "description": "Analyze code files",
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
        }
    ]
    
    return {"tools": tools}

@app.post("/api/v1/tools/call")
@limiter.limit(SECURITY_CONFIG['rate_limit']['tool_execution'])
async def execute_tool(
    request: Request,
    api_key_info: Dict[str, Any] = Depends(get_api_key_info)
):
    """Execute a tool with enhanced security"""
    try:
        body = await request.json()
        tool_name = body.get('name')
        arguments = body.get('arguments', {})
        
        # Validate tool name
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        # Validate arguments
        if not isinstance(arguments, dict):
            raise HTTPException(status_code=400, detail="Arguments must be an object")
        
        # Execute tool with security context
        result = await execute_tool_secure(tool_name, arguments, api_key_info)
        
        return {
            "success": True,
            "tool": tool_name,
            "content": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

async def execute_tool_secure(tool_name: str, arguments: Dict[str, Any], api_key_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute tool with security validation"""
    
    # Validate file paths for file-related tools
    if tool_name in ['read_file', 'list_files', 'analyze_code']:
        file_path = arguments.get('file_path') or arguments.get('directory')
        if file_path:
            # Prevent directory traversal attacks
            if '..' in file_path or file_path.startswith('/'):
                raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Execute tool based on name
    if tool_name == "ping":
        return [{"type": "text", "text": "pong"}]
    
    elif tool_name == "read_file":
        file_path = arguments.get('file_path', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [{"type": "text", "text": content}]
        except FileNotFoundError:
            return [{"type": "text", "text": f"Error: File {file_path} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error reading file: {str(e)}"}]
    
    elif tool_name == "list_files":
        directory = arguments.get('directory', '.')
        try:
            files = os.listdir(directory)
            return [{"type": "text", "text": f"Files in {directory}: {', '.join(files)}"}]
        except FileNotFoundError:
            return [{"type": "text", "text": f"Error: Directory {directory} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error listing files: {str(e)}"}]
    
    elif tool_name == "get_system_status":
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        return [{
            "type": "text",
            "text": f"System Status:\nCPU Usage: {cpu_percent}%\nMemory Usage: {memory.percent}%\nAvailable Memory: {memory.available / (1024**3):.1f} GB\nTotal Memory: {memory.total / (1024**3):.1f} GB\nStatus: Healthy"
        }]
    
    elif tool_name == "analyze_code":
        file_path = arguments.get('file_path', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple code analysis
            lines = content.split('\n')
            char_count = len(content)
            word_count = len(content.split())
            
            analysis = f"Code Analysis for {file_path}:\nLines: {len(lines)}\nCharacters: {char_count}\nWords: {word_count}\nFile size: {len(content.encode('utf-8'))} bytes"
            
            return [{"type": "text", "text": analysis}]
        except FileNotFoundError:
            return [{"type": "text", "text": f"Error: File {file_path} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error analyzing code: {str(e)}"}]
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

@app.get("/security/stats")
async def get_security_stats(
    api_key_info: Dict[str, Any] = Depends(get_api_key_info)
):
    """Get security statistics (admin only)"""
    if 'admin' not in api_key_info.get('permissions', []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return security_manager.get_security_stats()

@app.get("/security/audit")
async def get_audit_logs(
    api_key_info: Dict[str, Any] = Depends(get_api_key_info),
    limit: int = 100
):
    """Get audit logs (admin only)"""
    if 'admin' not in api_key_info.get('permissions', []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return recent audit logs
    recent_logs = security_manager.audit_logs[-limit:]
    return {
        "logs": [
            {
                "timestamp": log.timestamp,
                "ip_address": log.ip_address,
                "endpoint": log.endpoint,
                "method": log.method,
                "api_key": log.api_key[:8] + "..." if log.api_key != 'none' else 'none',
                "success": log.success,
                "response_time": log.response_time,
                "error_message": log.error_message
            }
            for log in recent_logs
        ]
    }

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
