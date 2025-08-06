#!/usr/bin/env python3
"""
LangFlow MCP Connector - Bridges LangFlow to our advanced MCP server
Uses the working stdio protocol while preserving all our functionality
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, List
import importlib.util

# Configure logging without Unicode characters to avoid encoding issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LangFlowMCPConnector:
    """MCP Connector that bridges LangFlow to our advanced server functionality"""
    
    def __init__(self):
        # Initialize basic components - heavy initialization will happen later
        self.workspace_manager = None
        self.code_analyzer = None
        self.cost_tracker = None
        self.health_monitor = None
        self.system_coordinator = None
        self._initialized = False
        
        # Define tools that LangFlow will see
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
            }
        ]
    
    async def initialize_advanced_server(self):
        """Initialize our advanced MCP server functionality"""
        try:
            # Import our advanced server components
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
            
            # Import the modules we need
            from modules.module_1_main.workspace_manager import WorkspaceManager
            from modules.module_1_main.code_analyzer import CodeAnalyzer
            from modules.module_3_economy.cost_tracker import CostTracker
            from modules.module_2_support.health_monitor import HealthMonitor
            from system_coordinator import LangFlowSystemCoordinator
            
            # Initialize components
            self.workspace_manager = WorkspaceManager()
            self.code_analyzer = CodeAnalyzer()
            self.cost_tracker = CostTracker()
            self.health_monitor = HealthMonitor()
            self.system_coordinator = LangFlowSystemCoordinator()
            
            logger.info("Advanced server components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing advanced server: {e}")
            self.workspace_manager = None
            self.code_analyzer = None
            self.cost_tracker = None
            self.health_monitor = None
            self.system_coordinator = None
    
    async def initialize_components(self):
        """Initialize all components asynchronously"""
        try:
            if self.workspace_manager:
                await self.workspace_manager.initialize()
            if self.code_analyzer:
                await self.code_analyzer.initialize()
            if self.cost_tracker:
                await self.cost_tracker.initialize()
            if self.health_monitor:
                await self.health_monitor.initialize()
            if self.system_coordinator:
                await self.system_coordinator.initialize_system()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                # Initialize components when LangFlow connects
                if not self._initialized:
                    await self.initialize_advanced_server()
                    await self.initialize_components()
                    self._initialized = True
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "langflow-connect",
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
        """Execute a tool using our advanced server functionality"""
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
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def handle_read_file(self, args: Dict[str, Any]) -> str:
        """Handle file read operation"""
        if not self.workspace_manager:
            return "Workspace manager not available"
        
        file_path = args.get("file_path")
        try:
            result = await self.workspace_manager.read_file(file_path)
            if result.get('success'):
                return f"File content:\n{result.get('content', '')}"
            else:
                return f"Error reading file: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    async def handle_write_file(self, args: Dict[str, Any]) -> str:
        """Handle file write operation"""
        if not self.workspace_manager:
            return "Workspace manager not available"
        
        file_path = args.get("file_path")
        content = args.get("content")
        try:
            result = await self.workspace_manager.write_file(file_path, content)
            if result.get('success'):
                return f"File written successfully: {file_path}"
            else:
                return f"Error writing file: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    async def handle_list_files(self, args: Dict[str, Any]) -> str:
        """Handle file list operation"""
        if not self.workspace_manager:
            return "Workspace manager not available"
        
        directory = args.get("directory", ".")
        try:
            files = await self.workspace_manager.list_files(directory)
            return f"Directory contents:\n{json.dumps(files, indent=2)}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    async def handle_analyze_code(self, args: Dict[str, Any]) -> str:
        """Handle code analysis operation"""
        if not self.code_analyzer:
            return "Code analyzer not available"
        
        file_path = args.get("file_path")
        try:
            # Read the file first
            if self.workspace_manager:
                read_result = await self.workspace_manager.read_file(file_path)
                if read_result.get('success'):
                    content = read_result.get('content', '')
                    result = await self.code_analyzer.analyze_code(file_path, content)
                    if result.get('success'):
                        return f"Code analysis:\n{json.dumps(result.get('analysis', {}), indent=2)}"
                    else:
                        return f"Error analyzing code: {result.get('error', 'Unknown error')}"
                else:
                    return f"Error reading file for analysis: {read_result.get('error', 'Unknown error')}"
            else:
                return "Workspace manager not available"
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
    
    async def handle_track_token_usage(self, args: Dict[str, Any]) -> str:
        """Handle token usage tracking"""
        if not self.cost_tracker:
            return "Cost tracker not available"
        
        operation = args.get("operation")
        model = args.get("model")
        input_tokens = args.get("input_tokens")
        output_tokens = args.get("output_tokens")
        
        try:
            result = await self.cost_tracker.record_token_usage(operation, model, input_tokens, output_tokens)
            if result.get('success'):
                return f"Token usage tracked successfully for {operation}"
            else:
                return f"Error tracking token usage: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error tracking token usage: {str(e)}"
    
    async def handle_get_cost_summary(self, args: Dict[str, Any]) -> str:
        """Handle cost summary retrieval"""
        if not self.cost_tracker:
            return "Cost tracker not available"
        
        try:
            result = await self.cost_tracker.get_cost_summary()
            if result.get('success'):
                return f"Cost summary:\n{json.dumps(result.get('summary', {}), indent=2)}"
            else:
                return f"Error getting cost summary: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting cost summary: {str(e)}"
    
    async def handle_get_system_health(self, args: Dict[str, Any]) -> str:
        """Handle system health check"""
        if not self.health_monitor:
            return "Health monitor not available"
        
        try:
            result = await self.health_monitor.get_system_health()
            if result.get('success'):
                return f"System health:\n{json.dumps(result.get('health', {}), indent=2)}"
            else:
                return f"Error getting system health: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting system health: {str(e)}"
    
    async def handle_get_system_status(self, args: Dict[str, Any]) -> str:
        """Handle system status check"""
        if not self.system_coordinator:
            return "System coordinator not available"
        
        try:
            result = await self.system_coordinator.get_system_status()
            
            # Convert dataclass to dictionary and handle datetime serialization
            status_dict = {
                "is_running": result.is_running,
                "start_time": result.start_time.isoformat() if result.start_time else None,
                "modules_initialized": result.modules_initialized,
                "active_connections": result.active_connections,
                "total_operations": result.total_operations,
                "system_health": result.system_health,
                "last_heartbeat": result.last_heartbeat.isoformat() if result.last_heartbeat else None
            }
            
            return f"System status:\n{json.dumps(status_dict, indent=2)}"
        except Exception as e:
            return f"Error getting system status: {str(e)}"

async def main():
    """Main entry point - Simple stdio server"""
    server = LangFlowMCPConnector()
    
    logger.info("MCP Server starting (stdio protocol)")
    
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