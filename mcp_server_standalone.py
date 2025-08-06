#!/usr/bin/env python3
"""
Standalone LangFlow Connect MCP Server

This script runs the MCP server in standalone mode for proper integration with LangFlow.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastmcp import FastMCP
    from mcp import StdioServerParameters
except ImportError as e:
    print(f"Error: Missing MCP dependencies. Please install: pip install fastmcp mcp")
    print(f"Import error: {e}")
    sys.exit(1)

# Import LangFlow Connect components
try:
    from src.system_coordinator import LangFlowSystemCoordinator
    from src.modules.module_1_main import WorkspaceOperations
    from src.modules.module_3_economy import CostTracker, BudgetManager
    from src.modules.module_4_langflow import LangflowConnector
    from src.modules.module_2_support import HealthMonitor
except ImportError as e:
    print(f"Error: Missing LangFlow Connect components. Please ensure src/ directory is properly set up.")
    print(f"Import error: {e}")
    sys.exit(1)

class LangFlowConnectMCPServer:
    """Standalone MCP Server for LangFlow Connect integration"""

    def __init__(self):
        self.fastmcp = FastMCP()
        self.system_coordinator = None
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.setup_tools()

    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/mcp_server.log')
            ]
        )

    def setup_tools(self):
        """Register all MCP tools"""
        self.logger.info("Setting up MCP tools...")

        # Workspace Operations
        @self.fastmcp.tool("workspace_read_file")
        async def read_file_tool(file_path: str) -> str:
            return await self.read_file_tool_impl(file_path)

        @self.fastmcp.tool("workspace_write_file")
        async def write_file_tool(file_path: str, content: str) -> str:
            return await self.write_file_tool_impl(file_path, content)

        @self.fastmcp.tool("workspace_analyze_code")
        async def analyze_code_tool(file_path: str) -> str:
            return await self.analyze_code_tool_impl(file_path)

        @self.fastmcp.tool("workspace_list_files")
        async def list_files_tool(directory: str = ".") -> str:
            return await self.list_files_tool_impl(directory)

        # Cost Tracking
        @self.fastmcp.tool("cost_track_usage")
        async def track_cost_tool(operation_id: str, model: str, 
                                 input_tokens: int, output_tokens: int, 
                                 operation_type: str) -> str:
            return await self.track_cost_tool_impl(operation_id, model, input_tokens, output_tokens, operation_type)

        @self.fastmcp.tool("cost_get_summary")
        async def get_cost_summary_tool() -> str:
            return await self.get_cost_summary_tool_impl()

        @self.fastmcp.tool("cost_get_budget_status")
        async def get_budget_status_tool() -> str:
            return await self.get_budget_status_tool_impl()

        # LangFlow Integration
        @self.fastmcp.tool("langflow_connect")
        async def connect_to_langflow_tool(websocket_url: str, auth_token: str) -> str:
            return await self.connect_to_langflow_tool_impl(websocket_url, auth_token)

        @self.fastmcp.tool("langflow_send_data")
        async def send_to_langflow_tool(data: str) -> str:
            return await self.send_to_langflow_tool_impl(data)

        @self.fastmcp.tool("langflow_get_connection_status")
        async def get_connection_status_tool() -> str:
            return await self.get_connection_status_tool_impl()

        # System Management
        @self.fastmcp.tool("system_get_status")
        async def get_system_status_tool() -> str:
            return await self.get_system_status_tool_impl()

        @self.fastmcp.tool("system_get_health")
        async def get_system_health_tool() -> str:
            return await self.get_system_health_tool_impl()

        self.logger.info("MCP tools registered successfully")

    async def initialize_system(self):
        """Initialize the LangFlow Connect system"""
        try:
            self.logger.info("Initializing LangFlow Connect system...")
            self.system_coordinator = LangFlowSystemCoordinator()
            await self.system_coordinator.initialize_system()
            self.logger.info("LangFlow Connect system initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False

    # Tool implementations (same as in mcp_server.py)
    async def read_file_tool_impl(self, file_path: str) -> str:
        """Read file content"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
            result = await workspace_manager.read_file(file_path)
            
            if result['success']:
                return result['content']
            else:
                return f"Error reading file: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in read_file_tool: {e}")
            return f"Error: {str(e)}"

    async def write_file_tool_impl(self, file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
            result = await workspace_manager.write_file(file_path, content)
            
            if result['success']:
                return f"File written successfully: {file_path}"
            else:
                return f"Error writing file: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in write_file_tool: {e}")
            return f"Error: {str(e)}"

    async def analyze_code_tool_impl(self, file_path: str) -> str:
        """Analyze code file"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            code_analyzer = self.system_coordinator.module_1_components['code_analyzer']
            result = await code_analyzer.analyze_file(file_path)
            
            if result['success']:
                analysis = result['analysis']
                return json.dumps(analysis, indent=2)
            else:
                return f"Error analyzing code: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in analyze_code_tool: {e}")
            return f"Error: {str(e)}"

    async def list_files_tool_impl(self, directory: str = ".") -> str:
        """List files in directory"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
            result = await workspace_manager.list_files(directory)
            
            if result['success']:
                files = result['files']
                return json.dumps(files, indent=2)
            else:
                return f"Error listing files: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in list_files_tool: {e}")
            return f"Error: {str(e)}"

    async def track_cost_tool_impl(self, operation_id: str, model: str, 
                                  input_tokens: int, output_tokens: int, 
                                  operation_type: str) -> str:
        """Track token usage and costs"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            cost_tracker = self.system_coordinator.module_3_components['cost_tracker']
            result = await cost_tracker.record_token_usage(
                operation_id=operation_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                operation_type=operation_type
            )
            
            if result['success']:
                return f"Cost tracked: ${result['cost_usd']:.4f}"
            else:
                return f"Error tracking cost: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in track_cost_tool: {e}")
            return f"Error: {str(e)}"

    async def get_cost_summary_tool_impl(self) -> str:
        """Get cost analysis summary"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            cost_tracker = self.system_coordinator.module_3_components['cost_tracker']
            result = await cost_tracker.get_cost_summary()
            
            if result['success']:
                summary = result['summary']
                return json.dumps(summary, indent=2)
            else:
                return f"Error getting cost summary: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in get_cost_summary_tool: {e}")
            return f"Error: {str(e)}"

    async def get_budget_status_tool_impl(self) -> str:
        """Get budget status and alerts"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            budget_manager = self.system_coordinator.module_3_components['budget_manager']
            result = await budget_manager.get_budget_status()
            
            if result['success']:
                status = result['status']
                return json.dumps(status, indent=2)
            else:
                return f"Error getting budget status: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in get_budget_status_tool: {e}")
            return f"Error: {str(e)}"

    async def connect_to_langflow_tool_impl(self, websocket_url: str, auth_token: str) -> str:
        """Connect to LangFlow"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            connector = self.system_coordinator.module_4_components['langflow_connector']
            config = {
                "websocket_url": websocket_url,
                "auth_token": auth_token
            }
            connector.config.update(config)
            
            result = await connector.connect()
            if result['status'] == 'connected':
                return "Successfully connected to LangFlow"
            else:
                return f"Error connecting to LangFlow: {result['message']}"
        except Exception as e:
            self.logger.error(f"Error in connect_to_langflow_tool: {e}")
            return f"Error: {str(e)}"

    async def send_to_langflow_tool_impl(self, data: str) -> str:
        """Send data to LangFlow"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            connector = self.system_coordinator.module_4_components['langflow_connector']
            data_dict = json.loads(data) if isinstance(data, str) else data
            result = await connector.send_data(data_dict)
            
            if result['success']:
                return "Data sent successfully to LangFlow"
            else:
                return f"Error sending data: {result['message']}"
        except Exception as e:
            self.logger.error(f"Error in send_to_langflow_tool: {e}")
            return f"Error: {str(e)}"

    async def get_connection_status_tool_impl(self) -> str:
        """Get LangFlow connection status"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            connector = self.system_coordinator.module_4_components['langflow_connector']
            status = {
                "connected": connector.connected,
                "connection_health": connector.connection_health,
                "reconnect_attempts": connector.reconnect_attempts
            }
            return json.dumps(status, indent=2)
        except Exception as e:
            self.logger.error(f"Error in get_connection_status_tool: {e}")
            return f"Error: {str(e)}"

    async def get_system_status_tool_impl(self) -> str:
        """Get overall system status"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            status = await self.system_coordinator.get_system_status()
            return json.dumps(status, indent=2)
        except Exception as e:
            self.logger.error(f"Error in get_system_status_tool: {e}")
            return f"Error: {str(e)}"

    async def get_system_health_tool_impl(self) -> str:
        """Get detailed system health"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            health_monitor = self.system_coordinator.module_2_components['health_monitor']
            result = await health_monitor.get_system_health()
            
            if result['success']:
                health = result['health']
                return json.dumps(health, indent=2)
            else:
                return f"Error getting system health: {result['error']}"
        except Exception as e:
            self.logger.error(f"Error in get_system_health_tool: {e}")
            return f"Error: {str(e)}"

    async def run(self):
        """Run the MCP server"""
        self.logger.info("Starting LangFlow Connect MCP Server...")

        if not await self.initialize_system():
            self.logger.error("Failed to initialize system, exiting")
            return

        self.logger.info("MCP Server ready!")
        self.logger.info("All tools registered successfully:")
        self.logger.info("  - Workspace Operations: 4 tools")
        self.logger.info("  - Cost Tracking: 3 tools")
        self.logger.info("  - LangFlow Integration: 3 tools")
        self.logger.info("  - System Management: 2 tools")
        self.logger.info("")
        self.logger.info("MCP Server is ready for LangFlow integration!")
        self.logger.info("")
        self.logger.info("To use with LangFlow:")
        self.logger.info("1. Configure LangFlow to connect to this server")
        self.logger.info("2. Use the provided langflow_config.json as a template")
        self.logger.info("3. All 12 tools are available for use")

        # Run the FastMCP server
        try:
            self.logger.info("Starting FastMCP server...")
            await self.fastmcp.run()
        except KeyboardInterrupt:
            self.logger.info("MCP Server interrupted by user")
        except Exception as e:
            self.logger.error(f"Error running FastMCP server: {e}")
        finally:
            # Cleanup
            if self.system_coordinator:
                await self.system_coordinator.stop_system()
            self.logger.info("MCP Server stopped")

def main():
    """Main entry point"""
    try:
        server = LangFlowConnectMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nMCP Server interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 