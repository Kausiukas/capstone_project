#!/usr/bin/env python3
"""
Final Working MCP Server for Langflow Integration
Uses the proper MCP library and protocol
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalMCPServer:
    """Final Working MCP Server"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "file_read",
                "description": "Read a file and return its contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "file_list",
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the directory"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "system_info",
                "description": "Get basic system information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "ai-help-agent-mcp",
                            "version": "1.0.0"
                        }
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
        """Execute a tool and return the result"""
        try:
            if tool_name == "file_read":
                return await self.handle_file_read(arguments)
            elif tool_name == "file_list":
                return await self.handle_file_list(arguments)
            elif tool_name == "system_info":
                return await self.handle_system_info(arguments)
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def handle_file_read(self, args: Dict[str, Any]) -> str:
        """Handle file read operation"""
        path = args.get("path")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content:\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def handle_file_list(self, args: Dict[str, Any]) -> str:
        """Handle file list operation"""
        path = args.get("path")
        try:
            path_obj = Path(path)
            if path_obj.is_dir():
                files = [f.name for f in path_obj.iterdir()]
                return f"Directory contents:\n{json.dumps(files, indent=2)}"
            else:
                return f"Path {path} is not a directory"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    async def handle_system_info(self, args: Dict[str, Any]) -> str:
        """Handle system info operation"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            system_info = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used // 1024**3,
                "memory_total_gb": memory.total // 1024**3
            }
            
            return f"System info:\n{json.dumps(system_info, indent=2)}"
        except ImportError:
            return "psutil not available for system monitoring"
        except Exception as e:
            return f"Error getting system info: {str(e)}"

async def main():
    """Main entry point - Simple stdio server"""
    server = FinalMCPServer()
    
    logger.info("🚀 MCP Server starting (stdio protocol)")
    
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
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 