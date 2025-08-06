# MCP Server Integration Requirements for LangFlow Connect

## 📋 Executive Summary

The LangFlow Connect system is **architecturally complete** and **functionally sound** but requires **MCP (Model Context Protocol) server implementation** to properly integrate with LangFlow applications. The current system has all the necessary components but lacks the MCP server layer that would enable seamless communication with LangFlow.

## 🎯 Current System State Analysis

### ✅ **What's Working**
- **Complete 4-Module Architecture**: All modules implemented and functional
- **Core Functionality**: File operations, cost tracking, memory management, LangFlow connection
- **Security Features**: TLS 1.3 encryption, JWT authentication
- **Async Operations**: Non-blocking I/O throughout the system
- **Testing Framework**: Comprehensive test suite with working demos
- **Dependencies**: All required packages installed (fastmcp, asyncio-mqtt, websockets, etc.)

### ⚠️ **What's Missing**
- **MCP Server Implementation**: No actual MCP server exposing the system capabilities
- **Tool Definitions**: MCP tools not defined for LangFlow integration
- **Protocol Compliance**: Not following MCP specification for tool registration
- **Client Integration**: No MCP client setup for LangFlow connection

## 🏗️ MCP Server Architecture Requirements

### 1. **Core MCP Server Structure**

```python
# Required MCP Server Implementation
from fastmcp import FastMCP
from mcp import StdioServerParameters
from mcp.types import Tool, TextContent

class LangFlowConnectMCPServer:
    def __init__(self):
        self.fastmcp = FastMCP()
        self.system_coordinator = None
        self.setup_tools()
    
    def setup_tools(self):
        """Register all MCP tools"""
        # Module 1: Workspace Operations
        self.fastmcp.tool(
            "workspace_read_file",
            self.read_file_tool,
            description="Read file content from workspace"
        )
        self.fastmcp.tool(
            "workspace_write_file", 
            self.write_file_tool,
            description="Write content to file in workspace"
        )
        self.fastmcp.tool(
            "workspace_analyze_code",
            self.analyze_code_tool,
            description="Analyze code structure and metrics"
        )
        
        # Module 3: Cost Tracking
        self.fastmcp.tool(
            "cost_track_usage",
            self.track_cost_tool,
            description="Track token usage and costs"
        )
        self.fastmcp.tool(
            "cost_get_summary",
            self.get_cost_summary_tool,
            description="Get cost analysis summary"
        )
        
        # Module 4: LangFlow Integration
        self.fastmcp.tool(
            "langflow_connect",
            self.connect_to_langflow_tool,
            description="Establish secure connection to LangFlow"
        )
        self.fastmcp.tool(
            "langflow_send_data",
            self.send_to_langflow_tool,
            description="Send data to LangFlow application"
        )
```

### 2. **Tool Implementation Requirements**

#### **Workspace Operations Tools**
```python
async def read_file_tool(self, file_path: str) -> str:
    """MCP tool for reading files"""
    try:
        workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
        result = await workspace_manager.read_file(file_path)
        if result['success']:
            return result['content']
        else:
            raise Exception(result['error'])
    except Exception as e:
        return f"Error reading file: {str(e)}"

async def write_file_tool(self, file_path: str, content: str) -> str:
    """MCP tool for writing files"""
    try:
        workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
        result = await workspace_manager.write_file(file_path, content)
        if result['success']:
            return f"Successfully wrote {len(content)} characters to {file_path}"
        else:
            raise Exception(result['error'])
    except Exception as e:
        return f"Error writing file: {str(e)}"
```

#### **Cost Tracking Tools**
```python
async def track_cost_tool(self, operation_id: str, model: str, 
                         input_tokens: int, output_tokens: int, 
                         operation_type: str) -> str:
    """MCP tool for tracking costs"""
    try:
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
            raise Exception(result['error'])
    except Exception as e:
        return f"Error tracking cost: {str(e)}"
```

#### **LangFlow Integration Tools**
```python
async def connect_to_langflow_tool(self, websocket_url: str, 
                                  auth_token: str) -> str:
    """MCP tool for connecting to LangFlow"""
    try:
        connector = self.system_coordinator.module_4_components['langflow_connector']
        config = {
            "websocket_url": websocket_url,
            "auth_token": auth_token
        }
        result = await connector.connect()
        if result['status'] == 'connected':
            return "Successfully connected to LangFlow"
        else:
            raise Exception(result['message'])
    except Exception as e:
        return f"Error connecting to LangFlow: {str(e)}"
```

## 🔧 Implementation Best Practices

### 1. **Error Handling**
```python
# Always wrap tool implementations with proper error handling
async def safe_tool_execution(self, tool_func, *args, **kwargs):
    """Safe wrapper for tool execution"""
    try:
        result = await tool_func(*args, **kwargs)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 2. **Async Operations**
```python
# Ensure all tools are async and non-blocking
@self.fastmcp.tool("async_operation")
async def async_tool(self, param: str) -> str:
    """Example of proper async tool implementation"""
    # Use asyncio.sleep for non-blocking operations
    await asyncio.sleep(0.1)
    return f"Processed: {param}"
```

### 3. **Resource Management**
```python
# Proper resource cleanup in tools
async def resource_intensive_tool(self, file_path: str) -> str:
    """Tool with proper resource management"""
    try:
        # Acquire resources
        file_handle = await self.get_file_handle(file_path)
        
        # Process
        result = await self.process_file(file_handle)
        
        return result
    finally:
        # Always cleanup
        await self.cleanup_resources()
```

## 📋 Required MCP Server Implementation

### 1. **Main Server File** (`mcp_server.py`)

```python
#!/usr/bin/env python3
"""
LangFlow Connect MCP Server

This module implements the MCP server that exposes LangFlow Connect
capabilities to LangFlow applications.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from mcp import StdioServerParameters

# Import LangFlow Connect components
from src.system_coordinator import LangFlowSystemCoordinator
from src.modules.module_1_main import WorkspaceManager, CodeAnalyzer
from src.modules.module_3_economy import CostTracker
from src.modules.module_4_langflow import LangflowConnector

class LangFlowConnectMCPServer:
    """MCP Server for LangFlow Connect integration"""
    
    def __init__(self):
        self.fastmcp = FastMCP()
        self.system_coordinator = None
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.setup_tools()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def setup_tools(self):
        """Register all MCP tools"""
        # Workspace Operations
        self.fastmcp.tool(
            "workspace_read_file",
            self.read_file_tool,
            description="Read file content from workspace"
        )
        self.fastmcp.tool(
            "workspace_write_file",
            self.write_file_tool,
            description="Write content to file in workspace"
        )
        self.fastmcp.tool(
            "workspace_analyze_code",
            self.analyze_code_tool,
            description="Analyze code structure and metrics"
        )
        
        # Cost Tracking
        self.fastmcp.tool(
            "cost_track_usage",
            self.track_cost_tool,
            description="Track token usage and costs"
        )
        self.fastmcp.tool(
            "cost_get_summary",
            self.get_cost_summary_tool,
            description="Get cost analysis summary"
        )
        
        # LangFlow Integration
        self.fastmcp.tool(
            "langflow_connect",
            self.connect_to_langflow_tool,
            description="Establish secure connection to LangFlow"
        )
        self.fastmcp.tool(
            "langflow_send_data",
            self.send_to_langflow_tool,
            description="Send data to LangFlow application"
        )
    
    async def initialize_system(self):
        """Initialize the LangFlow Connect system"""
        try:
            self.system_coordinator = LangFlowSystemCoordinator()
            await self.system_coordinator.initialize_system()
            self.logger.info("LangFlow Connect system initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False
    
    # Tool implementations...
    async def read_file_tool(self, file_path: str) -> str:
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
            return f"Error: {str(e)}"
    
    async def write_file_tool(self, file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
            result = await workspace_manager.write_file(file_path, content)
            
            if result['success']:
                return f"Successfully wrote {len(content)} characters to {file_path}"
            else:
                return f"Error writing file: {result['error']}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def analyze_code_tool(self, file_path: str) -> str:
        """Analyze code structure"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            code_analyzer = self.system_coordinator.module_1_components['code_analyzer']
            result = await code_analyzer.analyze_code(file_path)
            
            if result['success']:
                analysis = result['analysis']
                return json.dumps(analysis, indent=2)
            else:
                return f"Error analyzing code: {result['error']}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def track_cost_tool(self, operation_id: str, model: str, 
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
            return f"Error: {str(e)}"
    
    async def get_cost_summary_tool(self) -> str:
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
            return f"Error: {str(e)}"
    
    async def connect_to_langflow_tool(self, websocket_url: str, 
                                      auth_token: str) -> str:
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
            return f"Error: {str(e)}"
    
    async def send_to_langflow_tool(self, data: str) -> str:
        """Send data to LangFlow"""
        try:
            if not self.system_coordinator:
                return "Error: System not initialized"
            
            connector = self.system_coordinator.module_4_components['langflow_connector']
            data_dict = json.loads(data) if isinstance(data, str) else data
            
            result = await connector.send_data(data_dict)
            if result['status'] == 'sent':
                return "Data sent successfully to LangFlow"
            else:
                return f"Error sending data: {result['message']}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def run(self):
        """Run the MCP server"""
        # Initialize system
        if not await self.initialize_system():
            self.logger.error("Failed to initialize system")
            return
        
        # Run MCP server
        params = StdioServerParameters()
        await self.fastmcp.run(params)

async def main():
    """Main entry point"""
    server = LangFlowConnectMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. **Configuration File** (`mcp_config.json`)

```json
{
  "server": {
    "name": "LangFlow Connect MCP Server",
    "version": "1.0.0",
    "description": "MCP server for LangFlow Connect integration"
  },
  "tools": {
    "workspace_operations": {
      "enabled": true,
      "max_file_size": "10MB",
      "allowed_extensions": [".py", ".js", ".ts", ".json", ".md", ".txt"]
    },
    "cost_tracking": {
      "enabled": true,
      "default_currency": "USD",
      "alert_threshold": 100.0
    },
    "langflow_integration": {
      "enabled": true,
      "default_websocket_url": "ws://localhost:3000/ws",
      "connection_timeout": 30
    }
  },
  "security": {
    "jwt_secret": "your_jwt_secret_here",
    "tls_enabled": true,
    "allowed_origins": ["http://localhost:3000"]
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mcp_server.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

### 3. **Docker Configuration** (`Dockerfile.mcp`)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY mcp_server.py .
COPY mcp_config.json .

# Create necessary directories
RUN mkdir -p logs data cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose MCP server port (if using TCP instead of stdio)
EXPOSE 8000

# Run MCP server
CMD ["python", "mcp_server.py"]
```

## 🔗 LangFlow Integration Setup

### 1. **LangFlow Configuration**

```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/langflow-connect",
        "LANGFLOW_WEBSOCKET_URL": "ws://localhost:3000/ws"
      }
    }
  }
}
```

### 2. **Connection Testing**

```python
# Test script for MCP server
import asyncio
import json
from mcp import ClientSession, StdioServerParameters

async def test_mcp_connection():
    """Test MCP server connection"""
    params = StdioServerParameters()
    
    async with ClientSession(params) as session:
        # List tools
        tools = await session.list_tools()
        print("Available tools:", [tool.name for tool in tools.tools])
        
        # Test file read
        result = await session.call_tool("workspace_read_file", {"file_path": "test.txt"})
        print("Read result:", result.content)
        
        # Test cost tracking
        result = await session.call_tool("cost_track_usage", {
            "operation_id": "test_001",
            "model": "gpt-4",
            "input_tokens": 100,
            "output_tokens": 50,
            "operation_type": "test"
        })
        print("Cost tracking result:", result.content)

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
```

## 📊 Testing and Validation

### 1. **Unit Tests** (`test_mcp_server.py`)

```python
import pytest
import asyncio
from mcp_server import LangFlowConnectMCPServer

@pytest.mark.asyncio
async def test_server_initialization():
    """Test server initialization"""
    server = LangFlowConnectMCPServer()
    assert server.fastmcp is not None
    assert server.system_coordinator is None

@pytest.mark.asyncio
async def test_system_initialization():
    """Test system initialization"""
    server = LangFlowConnectMCPServer()
    result = await server.initialize_system()
    assert result is True
    assert server.system_coordinator is not None

@pytest.mark.asyncio
async def test_read_file_tool():
    """Test file read tool"""
    server = LangFlowConnectMCPServer()
    await server.initialize_system()
    
    # Create test file
    test_content = "Hello, World!"
    await server.write_file_tool("test.txt", test_content)
    
    # Read file
    result = await server.read_file_tool("test.txt")
    assert result == test_content
```

### 2. **Integration Tests**

```python
# Integration test with actual LangFlow
async def test_langflow_integration():
    """Test full LangFlow integration"""
    server = LangFlowConnectMCPServer()
    await server.initialize_system()
    
    # Connect to LangFlow
    result = await server.connect_to_langflow_tool(
        "ws://localhost:3000/ws",
        "test_token"
    )
    assert "connected" in result.lower()
    
    # Send data
    test_data = {"type": "test", "message": "Hello LangFlow"}
    result = await server.send_to_langflow_tool(json.dumps(test_data))
    assert "sent" in result.lower()
```

## 🚀 Deployment Instructions

### 1. **Development Setup**

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install additional MCP dependencies
pip install fastmcp mcp

# Run MCP server
python mcp_server.py
```

### 2. **Production Deployment**

```bash
# Build Docker image
docker build -f Dockerfile.mcp -t langflow-connect-mcp .

# Run container
docker run -d \
  --name langflow-connect-mcp \
  -p 8000:8000 \
  -v /path/to/data:/app/data \
  langflow-connect-mcp
```

### 3. **Systemd Service**

```ini
[Unit]
Description=LangFlow Connect MCP Server
After=network.target

[Service]
Type=simple
User=langflow
WorkingDirectory=/opt/langflow-connect
ExecStart=/opt/langflow-connect/venv/bin/python mcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Performance Considerations

### 1. **Resource Management**
- **Memory**: Implement proper cleanup in tools
- **CPU**: Use async operations for I/O-bound tasks
- **Network**: Implement connection pooling for external services

### 2. **Caching Strategy**
- **Tool Results**: Cache expensive operations
- **File Content**: Cache frequently accessed files
- **Cost Data**: Cache cost calculations

### 3. **Error Handling**
- **Graceful Degradation**: Handle partial failures
- **Retry Logic**: Implement exponential backoff
- **Logging**: Comprehensive error logging

## 🔒 Security Requirements

### 1. **Authentication**
- **JWT Tokens**: Secure token-based authentication
- **API Keys**: Secure storage of external service keys
- **Access Control**: Role-based access control

### 2. **Data Protection**
- **Encryption**: TLS 1.3 for all communications
- **Input Validation**: Validate all tool inputs
- **Output Sanitization**: Sanitize all tool outputs

### 3. **Audit Logging**
- **Operation Logging**: Log all tool executions
- **Access Logging**: Log all authentication attempts
- **Error Logging**: Log all security-related errors

## 📋 Implementation Checklist

### ✅ **Phase 1: Core MCP Server**
- [ ] Create `mcp_server.py` with basic structure
- [ ] Implement tool registration system
- [ ] Add workspace operation tools
- [ ] Add cost tracking tools
- [ ] Add LangFlow integration tools
- [ ] Implement error handling

### ✅ **Phase 2: Integration**
- [ ] Connect to existing LangFlow Connect system
- [ ] Test all tool implementations
- [ ] Add configuration management
- [ ] Implement logging system

### ✅ **Phase 3: Testing**
- [ ] Write unit tests for all tools
- [ ] Write integration tests
- [ ] Test with actual LangFlow instance
- [ ] Performance testing

### ✅ **Phase 4: Deployment**
- [ ] Create Docker configuration
- [ ] Create systemd service
- [ ] Setup monitoring and logging
- [ ] Security hardening

## 🎯 Success Metrics

### **Technical Metrics**
- **Tool Response Time**: < 100ms for simple operations
- **System Uptime**: > 99.9%
- **Error Rate**: < 0.1%
- **Memory Usage**: < 512MB

### **Functional Metrics**
- **Tool Coverage**: 100% of LangFlow Connect capabilities
- **Integration Success**: Seamless LangFlow connection
- **Cost Tracking**: Accurate real-time cost monitoring
- **File Operations**: Reliable workspace management

## 📚 Additional Resources

### **MCP Documentation**
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangFlow Documentation](https://docs.langflow.org/)

### **Implementation Examples**
- [MCP Server Examples](https://github.com/modelcontextprotocol/server-examples)
- [LangFlow MCP Integration](https://github.com/langflow-ai/langflow)

---

**Document Version**: 1.0.0  
**Last Updated**: July 30, 2025  
**Status**: Ready for Implementation  
**Next Steps**: Begin Phase 1 implementation 