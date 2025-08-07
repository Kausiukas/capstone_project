#!/usr/bin/env python3
"""
LangFlow Connect MVP - Security Enhanced MCP Server
Enhanced version with comprehensive security headers and protection.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import time
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import psutil

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

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Connect MVP - Secure API",
    description="AI-Powered Development Tools with Enhanced Security",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security configuration
SECURITY_CONFIG = {
    'api_keys': {
        'demo_key_123': {
            'name': 'Demo User',
            'permissions': ['read', 'execute']
        },
        'admin_key_456': {
            'name': 'Admin User',
            'permissions': ['read', 'execute', 'admin']
        }
    },
    'security_headers': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    },
    'cors_origins': [
        "http://localhost:8501",
        "https://capstone-project-dashboard.onrender.com",
        "https://your-dashboard-domain.com"
    ]
}

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=SECURITY_CONFIG['cors_origins'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    return api_key in SECURITY_CONFIG['api_keys']

def get_api_key_info(api_key: str) -> Optional[Dict[str, Any]]:
    """Get API key information"""
    return SECURITY_CONFIG['api_keys'].get(api_key)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add comprehensive security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    for header, value in SECURITY_CONFIG['security_headers'].items():
        response.headers[header] = value
    
    # Add custom security headers
    response.headers["X-API-Version"] = "2.0.0"
    response.headers["X-Security-Level"] = "Enhanced"
    
    # Log security events
    logger.info(f"Request from {request.client.host} to {request.url.path} - Headers applied")
    
    return response

@app.middleware("http")
async def security_validation_middleware(request: Request, call_next):
    """Security validation middleware"""
    # Extract API key
    api_key = request.headers.get('X-API-Key', '')
    
    # Skip validation for health endpoint
    if request.url.path == "/health":
        return await call_next(request)
    
    # Validate API key for protected endpoints
    if not validate_api_key(api_key):
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful authentication
    api_info = get_api_key_info(api_key)
    logger.info(f"Authenticated request from {request.client.host} using key {api_info['name'] if api_info else 'Unknown'}")
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Health check endpoint with security headers"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "security": "enhanced",
        "tools_count": 5,
        "security_headers": "enabled"
    }

@app.get("/tools/list")
async def get_tools_list(request: Request):
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
async def execute_tool(request: Request):
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
        result = await execute_tool_secure(tool_name, arguments)
        
        return {
            "success": True,
            "tool": tool_name,
            "content": result,
            "security": "enhanced"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

async def execute_tool_secure(tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute tool with security validation"""
    
    # Validate file paths for file-related tools
    if tool_name in ['read_file', 'list_files', 'analyze_code']:
        file_path = arguments.get('file_path') or arguments.get('directory')
        if file_path:
            # Prevent directory traversal attacks
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
                raise HTTPException(status_code=400, detail="Invalid file path")
            
            # Prevent Windows drive letters
            if len(file_path) > 1 and file_path[1] == ':':
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
            "text": f"System Status:\nCPU Usage: {cpu_percent}%\nMemory Usage: {memory.percent}%\nAvailable Memory: {memory.available / (1024**3):.1f} GB\nTotal Memory: {memory.total / (1024**3):.1f} GB\nStatus: Healthy\nSecurity: Enhanced"
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
            
            analysis = f"Code Analysis for {file_path}:\nLines: {len(lines)}\nCharacters: {char_count}\nWords: {word_count}\nFile size: {len(content.encode('utf-8'))} bytes\nSecurity: Validated"
            
            return [{"type": "text", "text": analysis}]
        except FileNotFoundError:
            return [{"type": "text", "text": f"Error: File {file_path} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error analyzing code: {str(e)}"}]
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

@app.get("/security/status")
async def get_security_status(request: Request):
    """Get security status (admin only)"""
    api_key = request.headers.get('X-API-Key', '')
    api_info = get_api_key_info(api_key)
    
    if not api_info or 'admin' not in api_info.get('permissions', []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "security_status": "enhanced",
        "headers_enabled": True,
        "cors_configured": True,
        "api_key_validation": True,
        "path_traversal_protection": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/security/headers")
async def get_security_headers_info():
    """Get information about security headers"""
    return {
        "security_headers": SECURITY_CONFIG['security_headers'],
        "description": "Comprehensive security headers for protection against various attacks",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting LangFlow Connect MVP - Security Enhanced API Server")
    logger.info("Security headers enabled")
    logger.info("CORS configured")
    logger.info("API key validation active")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
