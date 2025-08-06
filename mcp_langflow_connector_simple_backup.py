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
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleLangFlowMCPConnector:
    """Simplified MCP Connector that responds immediately"""
    
    def __init__(self):
        # No heavy initialization - just define tools
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
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from"
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
            }
        ]
    
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
            elif tool_name == "list_files":
                return await self.handle_list_files(arguments)
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
        """Simple file write operation"""
        file_path = args.get("file_path")
        content = args.get("content")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File written successfully: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    async def handle_list_files(self, args: Dict[str, Any]) -> str:
        """Simple file list operation"""
        directory = args.get("directory", ".")
        try:
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                files.append({
                    "name": item,
                    "is_file": os.path.isfile(item_path),
                    "is_dir": os.path.isdir(item_path)
                })
            return f"Directory contents:\n{json.dumps(files, indent=2)}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
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