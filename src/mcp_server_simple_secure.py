#!/usr/bin/env python3
"""
LangFlow Connect MVP - Simple Secure Server
Enhanced version with security headers and basic protection.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
import psutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SimpleSecureAPI')

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Connect MVP - Simple Secure API",
    description="AI-Powered Development Tools with Security Headers",
    version="2.0.0"
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
    response.headers["X-API-Version"] = "2.0.0"
    response.headers["X-Security-Level"] = "Enhanced"
    
    logger.info(f"Security headers applied to {request.url.path}")
    
    return response

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    valid_keys = ['demo_key_123', 'admin_key_456']
    return api_key in valid_keys

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "security": "enhanced",
        "tools_count": 5
    }

@app.get("/tools/list")
async def get_tools_list(request: Request):
    """Get list of available tools"""
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
    """Execute a tool"""
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
        
        result = await execute_tool_secure(tool_name, arguments)
        
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

async def execute_tool_secure(tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute tool with security validation"""
    
    # Validate file paths
    if tool_name in ['read_file', 'list_files', 'analyze_code']:
        file_path = arguments.get('file_path') or arguments.get('directory')
        if file_path:
            # Prevent directory traversal
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
                raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Execute tool
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
async def get_security_status():
    """Get security status"""
    return {
        "security_status": "enhanced",
        "headers_enabled": True,
        "cors_configured": True,
        "api_key_validation": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting LangFlow Connect MVP - Simple Secure API Server")
    logger.info("Security headers enabled")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
