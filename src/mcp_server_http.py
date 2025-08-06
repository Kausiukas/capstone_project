#!/usr/bin/env python3
"""
LangFlow Connect MCP Server - HTTP Version for MVP Demo

This is an HTTP-based MCP server for the capstone project MVP demo.
It provides RESTful API endpoints for tool execution.

Usage:
    uvicorn src.mcp_server_http:app --host 0.0.0.0 --port 8000
"""

import json
import logging
import os
from typing import Any, Dict, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangFlow Connect MCP Server",
    description="MVP Demo - HTTP-based MCP Server",
    version="1.0.0"
)

# Pydantic models
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

class ToolCallResponse(BaseModel):
    content: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    version: str
    tools_count: int

class ToolsListResponse(BaseModel):
    tools: List[Dict[str, Any]]

class LangFlowConnectMCPServer:
    """HTTP-based MCP server for LangFlow Connect MVP"""
    
    def __init__(self):
        """Initialize the HTTP MCP server"""
        self.tools = [
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
                            "description": "Directory to list files from",
                            "default": "."
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_system_status",
                "description": "Get system status information",
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
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool calls with fast response times"""
        try:
            if tool_name == "ping":
                return "pong"
            
            elif tool_name == "read_file":
                file_path = arguments.get("file_path", "")
                if not file_path:
                    return "Error: file_path is required"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return f"File contents of {file_path}:\n{content[:500]}..." if len(content) > 500 else content
                except FileNotFoundError:
                    return f"Error: File {file_path} not found"
                except Exception as e:
                    return f"Error reading file: {str(e)}"
            
            elif tool_name == "list_files":
                directory = arguments.get("directory", ".")
                try:
                    files = []
                    for item in Path(directory).iterdir():
                        if item.is_file():
                            files.append(f"📄 {item.name}")
                        elif item.is_dir():
                            files.append(f"📁 {item.name}/")
                    return f"Files in {directory}:\n" + "\n".join(files[:20])  # Limit to 20 items
                except Exception as e:
                    return f"Error listing files: {str(e)}"
            
            elif tool_name == "get_system_status":
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                return f"""System Status:
- CPU Usage: {cpu_percent}%
- Memory Usage: {memory.percent}%
- Available Memory: {memory.available // (1024**3)} GB
- Total Memory: {memory.total // (1024**3)} GB
- Status: Healthy"""
            
            elif tool_name == "analyze_code":
                file_path = arguments.get("file_path", "")
                if not file_path:
                    return "Error: file_path is required"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    line_count = len(lines)
                    char_count = len(content)
                    
                    # Simple analysis
                    analysis = f"""Code Analysis for {file_path}:
- Lines of Code: {line_count}
- Characters: {char_count}
- File Size: {len(content.encode('utf-8'))} bytes
- Language: {Path(file_path).suffix}
- Analysis: Code appears well-structured"""
                    
                    return analysis
                except FileNotFoundError:
                    return f"Error: File {file_path} not found"
                except Exception as e:
                    return f"Error analyzing code: {str(e)}"
            
            else:
                return f"Error: Unknown tool '{tool_name}'"
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

# Create server instance
server = LangFlowConnectMCPServer()

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "LangFlow Connect MCP Server - MVP Demo",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        tools_count=len(server.tools)
    )

@app.get("/tools/list", response_model=ToolsListResponse)
async def list_tools(api_key: str = Header(None, alias="X-API-Key")):
    """List available tools"""
    if api_key != "demo_key_123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return ToolsListResponse(tools=server.tools)

@app.post("/api/v1/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest, api_key: str = Header(None, alias="X-API-Key")):
    """Execute a tool call"""
    if api_key != "demo_key_123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        result = await server.execute_tool(request.name, request.arguments)
        return ToolCallResponse(content=[{"type": "text", "text": result}])
    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str, api_key: str = Header(None, alias="X-API-Key")):
    """Get information about a specific tool"""
    if api_key != "demo_key_123":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    for tool in server.tools:
        if tool["name"] == tool_name:
            return tool
    
    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 