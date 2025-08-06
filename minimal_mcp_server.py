#!/usr/bin/env python3
"""
Minimal MCP Server for Inspector Testing

This is a minimal MCP server that follows the official MCP protocol standards
for testing with the MCP Inspector. Based on the official documentation at:
https://modelcontextprotocol.io/legacy/tools/inspector

Usage:
    npx @modelcontextprotocol/inspector python minimal_mcp_server.py
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinimalMCPServer:
    """Minimal MCP server for testing with Inspector"""
    
    def __init__(self):
        """Initialize the minimal MCP server"""
        self.tools = [
            {
                "name": "ping",
                "description": "Ping the server for connectivity testing",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "echo",
                "description": "Echo back the input message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "get_server_info",
                "description": "Get basic server information",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        logger.info("Minimal MCP Server initialized")
        logger.info(f"Available tools: {[tool['name'] for tool in self.tools]}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests following JSON-RPC 2.0 specification"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                # Handle initialization request
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Minimal MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
                
                result = await self.execute_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            
            else:
                logger.warning(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            request_id = request.get("id")
            if request_id is None:
                request_id = 0  # Use 0 for requests without ID
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool calls"""
        try:
            if tool_name == "ping":
                return "pong"
            
            elif tool_name == "echo":
                message = arguments.get("message", "")
                return f"Echo: {message}"
            
            elif tool_name == "get_server_info":
                return json.dumps({
                    "server_name": "Minimal MCP Server",
                    "version": "1.0.0",
                    "tools_count": len(self.tools),
                    "tools": [tool["name"] for tool in self.tools],
                    "protocol": "JSON-RPC 2.0",
                    "status": "running"
                }, indent=2)
            
            else:
                return f"Tool '{tool_name}' not implemented"
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

async def main():
    """Main function for the MCP server"""
    server = MinimalMCPServer()
    
    logger.info("Minimal MCP Server starting...")
    logger.info("Ready to receive requests on stdin")
    
    # Read from stdin, write to stdout (following MCP protocol)
    while True:
        try:
            # Read request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                logger.info("No more input, shutting down")
                break
            
            # Parse JSON request
            request = json.loads(line.strip())
            
            # Handle request
            response = await server.handle_request(request)
            
            # Write response to stdout
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: sys.stdout.write(json.dumps(response) + "\n")
            )
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": 0,  # Use 0 instead of None for JSON-RPC compliance
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: sys.stdout.write(json.dumps(error_response) + "\n")
            )
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1) 