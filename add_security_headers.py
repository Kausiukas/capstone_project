#!/usr/bin/env python3
"""
Add Security Headers to LangFlow Connect MVP API
Simple script to add security headers to existing FastAPI server.
"""

import os
import shutil
from datetime import datetime

def add_security_headers_to_server():
    """Add security headers to the existing server"""
    
    print("🔒 Adding Security Headers to LangFlow Connect MVP API")
    print("=" * 60)
    
    # Check if the server file exists
    server_files = [
        "src/mcp_server_fixed.py",
        "src/mcp_server.py",
        "mcp_server_fixed.py"
    ]
    
    server_file = None
    for file_path in server_files:
        if os.path.exists(file_path):
            server_file = file_path
            break
    
    if not server_file:
        print("❌ No server file found. Please check the file paths.")
        return False
    
    print(f"✅ Found server file: {server_file}")
    
    # Create backup
    backup_file = f"{server_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(server_file, backup_file)
    print(f"📄 Backup created: {backup_file}")
    
    # Read the server file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if security headers are already added
    if "X-Content-Type-Options" in content:
        print("✅ Security headers already present in server file")
        return True
    
    # Add security headers middleware
    security_middleware_code = '''
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
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
    
    return response
'''
    
    # Find the right place to insert the middleware
    if "app = FastAPI(" in content:
        # Insert after FastAPI initialization
        insert_point = content.find("app = FastAPI(")
        end_point = content.find(")", insert_point) + 1
        
        # Find the next line after FastAPI initialization
        next_line = content.find("\n", end_point)
        if next_line != -1:
            insert_position = next_line + 1
        else:
            insert_position = end_point
        
        # Insert the middleware
        new_content = content[:insert_position] + security_middleware_code + content[insert_position:]
        
        # Write the updated content
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Security headers middleware added successfully!")
        return True
    
    else:
        print("❌ Could not find FastAPI app initialization in the file")
        return False

def create_enhanced_server():
    """Create an enhanced version of the server with security headers"""
    
    print("\n🔧 Creating Enhanced Server with Security Headers")
    print("=" * 60)
    
    enhanced_server_content = '''#!/usr/bin/env python3
"""
LangFlow Connect MVP - Enhanced API Server with Security Headers
"""

from fastapi import FastAPI, HTTPException, Request
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
        logging.FileHandler('logs/enhanced_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EnhancedAPI')

# Initialize FastAPI app
app = FastAPI(
    title="LangFlow Connect MVP - Enhanced API",
    description="AI-Powered Development Tools with Enhanced Security",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://capstone-project-dashboard.onrender.com",
        "https://your-dashboard-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add comprehensive security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    for header, value in security_headers.items():
        response.headers[header] = value
    
    # Add custom security headers
    response.headers["X-API-Version"] = "2.0.0"
    response.headers["X-Security-Level"] = "Enhanced"
    
    logger.info(f"Security headers applied to {request.url.path} from {request.client.host}")
    
    return response

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    valid_keys = ['demo_key_123', 'admin_key_456']
    return api_key in valid_keys

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
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
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
    """Execute a tool with enhanced security"""
    api_key = request.headers.get('X-API-Key', '')
    
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\\\'):
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
            "text": f"System Status:\\nCPU Usage: {cpu_percent}%\\nMemory Usage: {memory.percent}%\\nAvailable Memory: {memory.available / (1024**3):.1f} GB\\nTotal Memory: {memory.total / (1024**3):.1f} GB\\nStatus: Healthy\\nSecurity: Enhanced"
        }]
    
    elif tool_name == "analyze_code":
        file_path = arguments.get('file_path', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple code analysis
            lines = content.split('\\n')
            char_count = len(content)
            word_count = len(content.split())
            
            analysis = f"Code Analysis for {file_path}:\\nLines: {len(lines)}\\nCharacters: {char_count}\\nWords: {word_count}\\nFile size: {len(content.encode('utf-8'))} bytes\\nSecurity: Validated"
            
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
        "path_traversal_protection": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting LangFlow Connect MVP - Enhanced API Server")
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
'''
    
    # Write the enhanced server
    enhanced_file = "src/mcp_server_enhanced.py"
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_server_content)
    
    print(f"✅ Enhanced server created: {enhanced_file}")
    return True

def main():
    """Main function"""
    print("🔒 LangFlow Connect MVP - Security Headers Implementation")
    print("=" * 70)
    
    # Try to add security headers to existing server
    success = add_security_headers_to_server()
    
    if not success:
        print("\n🔄 Creating enhanced server with security headers...")
        create_enhanced_server()
    
    print("\n🎯 Next Steps:")
    print("1. Deploy the enhanced server to Render")
    print("2. Test security headers with: python test_security_headers.py")
    print("3. Verify security score improvement")
    
    print("\n📋 Security Headers Added:")
    print("- X-Content-Type-Options: nosniff")
    print("- X-Frame-Options: DENY")
    print("- X-XSS-Protection: 1; mode=block")
    print("- Strict-Transport-Security: max-age=31536000; includeSubDomains")
    print("- Content-Security-Policy: default-src 'self'")
    print("- Referrer-Policy: strict-origin-when-cross-origin")
    print("- Permissions-Policy: geolocation=(), microphone=(), camera=()")

if __name__ == "__main__":
    main()
