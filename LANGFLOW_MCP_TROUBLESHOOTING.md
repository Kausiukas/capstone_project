# 🔧 LangFlow MCP Connection Troubleshooting Guide

## 📋 Overview

This guide provides comprehensive troubleshooting steps for connecting our hybrid MCP solution to LangFlow, based on the [official LangFlow MCP documentation](https://docs.langflow.org/mcp-server#troubleshooting-mcp-server) and our implementation experience.

## 🚨 Common LangFlow MCP Connection Issues

### 1. **"No valid MCP server found in the input"**

**Symptoms:**
- LangFlow shows error when trying to add MCP server
- Configuration appears invalid
- Server doesn't appear in MCP server list

**Causes:**
- Incorrect JSON format in configuration
- Missing required fields
- Invalid command or arguments

**Solutions:**

#### A. Verify JSON Format
```bash
# Check configuration syntax
python -m json.tool langflow_client_config.json
```

**Correct Format:**
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "python",
      "args": ["mcp_langflow_connector.py"],
      "env": {
        "PYTHONPATH": ".",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

#### B. Check Required Fields
- ✅ `mcpServers` (root object)
- ✅ Server name (e.g., "langflow-connect")
- ✅ `command` (e.g., "python")
- ✅ `args` (array of arguments)
- ✅ `env` (optional but recommended)

### 2. **"Command not found" or "Executable not found"**

**Symptoms:**
- LangFlow can't execute the MCP server
- Process fails to start
- Connection timeout

**Solutions:**

#### A. Verify Python Path
```bash
# Check if Python is available
python --version
which python  # On Unix/Linux
where python  # On Windows
```

#### B. Use Absolute Paths
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "C:\\Python312\\python.exe",  // Windows
      "args": ["mcp_langflow_connector.py"],
      "env": {
        "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

#### C. Check Virtual Environment
```bash
# Ensure virtual environment is activated
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate   # Unix/Linux

# Use venv Python
{
  "mcpServers": {
    "langflow-connect": {
      "command": "venv\\Scripts\\python.exe",  // Windows
      "args": ["mcp_langflow_connector.py"],
      "env": {
        "PYTHONPATH": ".",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

### 3. **"Import errors" or "Module not found"**

**Symptoms:**
- MCP server starts but fails to import modules
- Component initialization errors
- Missing dependency errors

**Solutions:**

#### A. Check Dependencies
```bash
# Verify all dependencies are installed
pip list | grep -E "(fastmcp|asyncio|aiohttp)"

# Install missing dependencies
pip install -r requirements.txt
```

#### B. Verify PYTHONPATH
```bash
# Test import manually
python -c "import sys; sys.path.insert(0, 'src'); from modules.module_1_main.workspace_manager import WorkspaceManager; print('Import successful')"
```

#### C. Use Absolute PYTHONPATH
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "python",
      "args": ["mcp_langflow_connector.py"],
      "env": {
        "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect;D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

### 4. **"Connection timeout" or "Server not responding"**

**Symptoms:**
- LangFlow can't connect to MCP server
- Connection hangs or times out
- Server appears but tools don't work

**Solutions:**

#### A. Test Server Independently
```bash
# Test the connector directly
python test_connector.py

# Test stdio communication
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python mcp_langflow_connector.py
```

#### B. Check Server Logs
```bash
# Run server with verbose logging
python mcp_langflow_connector.py 2>&1 | tee server.log
```

#### C. Verify Port/Firewall
- Check if any firewall is blocking the connection
- Ensure no antivirus is interfering
- Verify LangFlow and MCP server are on same machine (for stdio)

### 5. **"Tools not available" or "Empty tool list"**

**Symptoms:**
- MCP server connects but shows no tools
- Tools list is empty
- Tool execution fails

**Solutions:**

#### A. Verify Tool Registration
```bash
# Test tool listing
python -c "
import asyncio
from mcp_langflow_connector import LangFlowMCPConnector

async def test():
    connector = LangFlowMCPConnector()
    await connector.initialize_components()
    print(f'Available tools: {len(connector.tools)}')
    for tool in connector.tools:
        print(f'  - {tool[\"name\"]}: {tool[\"description\"]}')

asyncio.run(test())
"
```

#### B. Check Component Initialization
```bash
# Test component initialization
python test_connector.py
```

#### C. Verify MCP Protocol
```bash
# Test MCP protocol compliance
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python mcp_langflow_connector.py
```

## 🔍 LangFlow-Specific Troubleshooting

### **Primary Testing Method: MCP Inspector**

The [MCP Inspector](https://modelcontextprotocol.io/legacy/tools/inspector#python) is the **official and recommended** testing tool for MCP servers. It provides comprehensive debugging capabilities and should be used as the primary method for testing our MCP server before attempting LangFlow integration.

#### **Why Use MCP Inspector?**
- **Official Tool**: Developed by the MCP team
- **Comprehensive Testing**: Tests all MCP protocol features
- **Interactive Interface**: Easy-to-use GUI for testing
- **Real-time Logging**: Monitor server logs and errors
- **Edge Case Testing**: Test invalid inputs and error handling

#### **Quick Start with MCP Inspector**
```bash
# Run MCP Inspector directly
npx @modelcontextprotocol/inspector

# Or run with our server directly
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

#### **Configuration for Our Server**
1. **Transport**: STDIO
2. **Command**: `python`
3. **Arguments**: `mcp_langflow_connector.py`
4. **Environment Variables**:
   - `PYTHONPATH`: `D:\GUI\System-Reference-Clean\LangFlow_Connect;D:\GUI\System-Reference-Clean\LangFlow_Connect\src`
   - `LANGFLOW_CONNECT_ENV`: `production`

#### **Testing Workflow**
1. **Connect**: Verify server connection
2. **Tools Tab**: Test all 8 tools individually
3. **Notifications**: Monitor server logs
4. **Edge Cases**: Test error conditions

### **Using MCP Inspector (Recommended Testing Tool)**

The [MCP Inspector](https://modelcontextprotocol.io/legacy/tools/inspector#python) is the official testing tool for MCP servers and is highly recommended for debugging MCP connections with LangFlow.

#### A. Install and Run MCP Inspector
```bash
# Run directly without installation
npx @modelcontextprotocol/inspector

# For Python servers specifically
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

#### B. Configure for Our Server
1. **Transport Type**: Select **STDIO**
2. **Command**: `python`
3. **Arguments**: `mcp_langflow_connector.py`
4. **Environment Variables**:
   - `PYTHONPATH`: `D:\GUI\System-Reference-Clean\LangFlow_Connect;D:\GUI\System-Reference-Clean\LangFlow_Connect\src`
   - `LANGFLOW_CONNECT_ENV`: `production`

#### C. Test Features
- **Server Connection Pane**: Verify stdio communication
- **Tools Tab**: List and test all 8 available tools
- **Resources Tab**: Check available resources
- **Notifications Pane**: Monitor server logs and errors

#### D. Development Workflow
1. **Start Development**: Launch Inspector with your server
2. **Verify Connectivity**: Check basic connection and capability negotiation
3. **Iterative Testing**: Make changes, reconnect, test affected features
4. **Edge Case Testing**: Test invalid inputs, missing arguments, concurrent operations

### **LangFlow Startup and Installation Issues**

#### A. LangFlow Command Not Found
If you get `langflow : The term 'langflow' is not recognized`:

```bash
# Try using Python module directly
python -m langflow run --port 7860

# Or use the full path to langflow.exe
C:\Users\OCPC\AppData\Roaming\Python\Python312\Scripts\langflow.exe run --port 7860

# Or add the Scripts directory to PATH
set PATH=%PATH%;C:\Users\OCPC\AppData\Roaming\Python\Python312\Scripts
```

#### B. LangFlow Module Issues
If you get `No module named langflow.__main__`:

```bash
# Reinstall LangFlow with dependencies
pip install langflow --upgrade

# Or install with specific version
pip install langflow==1.5.0.post1
```

#### C. Same Machine Requirement
- Auto-installation only works if LangFlow and MCP server are on the same machine
- For different machines, use manual JSON configuration

#### D. Manual Configuration Steps
1. Start LangFlow successfully
2. Open LangFlow dashboard (http://localhost:7860)
3. Go to **MCP Server** tab
4. Use **JSON** configuration method
5. Copy and paste the contents of `langflow_client_config.json`

### **Known LangFlow Issues**

#### A. Critical Bug in LangFlow 1.5.0
There's a [known critical bug](https://github.com/langflow-ai/langflow/issues/9128) in LangFlow 1.5.0 where adding MCP Google Sheet via JSON breaks all MCP tools, causing persistent build_output errors.

**Workaround:**
- Use MCP Inspector for testing instead of LangFlow initially
- Test with other MCP clients if available
- Consider using LangFlow Desktop for better MCP support

#### B. MCP Tools (SSE) Command Issues
There are reported issues with MCP tools using Server-Sent Events (SSE) in LangFlow. Our stdio-based approach should avoid these issues.

### **Authentication Issues**

If LangFlow requires authentication:

#### A. API Key Configuration
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "python",
      "args": [
        "mcp_langflow_connector.py"
      ],
      "env": {
        "PYTHONPATH": ".",
        "LANGFLOW_CONNECT_ENV": "production",
        "LANGFLOW_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### B. Generate API Key
- In LangFlow dashboard, click **Generate API key**
- Copy the generated key
- Add to environment variables

## 🛠️ Debug Steps for Our Hybrid Solution

### **Step 1: Verify Connector**
```bash
# Test connector functionality
python test_connector.py
```

**Expected Output:**
```
Testing connector initialization...
Available tools: 8
  - read_file: Read file contents from the workspace
  - write_file: Write content to a file in the workspace
  - list_files: List files in a directory
  - analyze_code: Analyze code structure and metrics
  - track_token_usage: Track token usage and costs
  - get_cost_summary: Get cost summary and statistics
  - get_system_health: Get system health status
  - get_system_status: Get overall system status

Testing file listing...
Result: Directory contents: [files listed successfully]

Connector test completed successfully!
```

### **Step 2: Test with MCP Inspector (Recommended)**
```bash
# Launch MCP Inspector for comprehensive testing
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

**Inspector Features to Test:**
- **Server Connection**: Verify stdio communication
- **Tools Tab**: List and test all 8 tools individually
- **Notifications**: Monitor server logs and errors
- **Edge Cases**: Test invalid inputs and error handling

### **Step 3: Test MCP Protocol**
```bash
# Test initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python mcp_langflow_connector.py

# Test tool listing
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python mcp_langflow_connector.py

# Test tool execution
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_files", "arguments": {"directory": "."}}}' | python mcp_langflow_connector.py
```

### **Step 4: Check Configuration**
```bash
# Validate JSON syntax
python -c "import json; config = json.load(open('langflow_client_config.json')); print('Configuration is valid JSON'); print(json.dumps(config, indent=2))"
```

### **Step 5: Test LangFlow Integration**
1. **Start LangFlow** (see LangFlow Startup Issues section)
2. **Add MCP Server** using `langflow_client_config.json`
3. **Check MCP Server tab** for connection status
4. **Test available tools**

## 📞 Getting Help

### **LangFlow Resources:**
- [Official MCP Documentation](https://docs.langflow.org/mcp-server#troubleshooting-mcp-server)
- [LangFlow GitHub Issues](https://github.com/logspace-ai/langflow/issues)
- [LangFlow Discord Community](https://discord.gg/langflow)
- [LangFlow MCP Integration Blog](https://www.langflow.org/blog/introducing-mcp-integration-in-langflow)

### **MCP Resources:**
- [MCP Inspector Documentation](https://modelcontextprotocol.io/legacy/tools/inspector#python) - Official testing tool
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### **Our Solution Resources:**
- `HYBRID_MCP_SOLUTION_GUIDE.md` - Complete solution guide
- `test_connector.py` - Validation script
- `test_mcp_protocol.py` - MCP protocol testing
- `mcp_langflow_connector.py` - Connector implementation
- `langflow_client_config.json` - Ready configuration

### **Debug Information to Collect:**
1. **LangFlow version** and installation method
2. **Python version and path**
3. **Operating system**
4. **Error messages and logs**
5. **Configuration file contents**
6. **Test results from `test_connector.py`**
7. **MCP Inspector test results**
8. **LangFlow startup method used**

## 🎯 **Recommended Testing Strategy**

### **1. Start with MCP Inspector**
```bash
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```
- Test all tools individually
- Verify protocol compliance
- Check error handling

### **2. Test LangFlow Integration**
- Use MCP Inspector results as baseline
- Start LangFlow with proper command
- Add MCP server via JSON configuration
- Compare tool availability with Inspector results

### **3. Troubleshoot Issues**
- Use MCP Inspector for protocol-level debugging
- Check LangFlow logs for integration issues
- Verify configuration and paths

---

*Based on LangFlow Official Documentation, MCP Inspector Documentation, and Our Implementation Experience*  
*Last Updated: July 31, 2025* 