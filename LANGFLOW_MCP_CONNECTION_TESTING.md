# 🔧 LangFlow MCP Connection Testing & Troubleshooting Guide

## 📋 Current Status

✅ **MCP Connector Working**: Our `mcp_langflow_connector.py` is fully functional  
✅ **MCP Protocol Valid**: Successfully tested with stdio communication  
✅ **LangFlow Installed**: Version 1.5.0.post1 installed successfully  
✅ **8 Tools Available**: All advanced system tools are operational  

## 🧪 Testing Results

### 1. **MCP Connector Test** ✅
```bash
python test_connector.py
```
**Result**: All 8 tools initialized successfully
- read_file, write_file, list_files, analyze_code
- track_token_usage, get_cost_summary, get_system_health, get_system_status

### 2. **MCP Protocol Test** ✅
```bash
python test_mcp_protocol.py
```
**Result**: Full MCP protocol compliance verified
- ✅ Initialize method working
- ✅ Tools/list method working  
- ✅ Tools/call method working
- ✅ Proper JSON-RPC 2.0 responses

### 3. **LangFlow Installation** ✅
```bash
pip install --no-deps langflow
```
**Result**: LangFlow 1.5.0.post1 installed successfully

## 🔧 Configuration Files

### **langflow_client_config.json** (Updated)
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "python",
      "args": [
        "mcp_langflow_connector.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect;D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

## 🚀 Next Steps for LangFlow Integration

### **Step 1: Start LangFlow**
```bash
# Start LangFlow server
langflow run

# Or with specific port
langflow run --port 7860
```

### **Step 2: Add MCP Server in LangFlow**
1. Open LangFlow dashboard (usually http://localhost:7860)
2. Go to **MCP Server** tab
3. Use the **JSON** configuration method
4. Copy and paste the contents of `langflow_client_config.json`

### **Step 3: Verify Connection**
1. Check MCP Server status in LangFlow
2. Verify tools appear in the tools list
3. Test tool execution

## 🔍 Troubleshooting Steps

### **If LangFlow Can't Find MCP Server**

#### **A. Check Python Path**
```bash
# Verify Python is available
python --version
where python  # Windows
which python  # Unix/Linux
```

#### **B. Test MCP Server Independently**
```bash
# Test our connector directly
python test_connector.py

# Test MCP protocol
python test_mcp_protocol.py
```

#### **C. Use Absolute Paths**
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "C:\\Python312\\python.exe",
      "args": [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\mcp_langflow_connector.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect;D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

### **If Tools Don't Appear**

#### **A. Check LangFlow Logs**
- Look for MCP-related errors in LangFlow console
- Check for import errors or missing dependencies

#### **B. Verify Tool Registration**
```bash
# Test tool listing manually
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

### **If Connection Times Out**

#### **A. Check Firewall/Antivirus**
- Ensure no firewall is blocking the connection
- Check if antivirus is interfering with Python processes

#### **B. Test stdio Communication**
```bash
# Test direct stdio communication
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python mcp_langflow_connector.py
```

## 🛠️ Advanced Configuration

### **Using Virtual Environment**
```json
{
  "mcpServers": {
    "langflow-connect": {
      "command": "venv\\Scripts\\python.exe",
      "args": [
        "mcp_langflow_connector.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect;D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src",
        "LANGFLOW_CONNECT_ENV": "production"
      }
    }
  }
}
```

### **Using MCP Inspector (Recommended)**
```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Configure for stdio:
# - Transport: STDIO
# - Command: python
# - Arguments: mcp_langflow_connector.py
# - Environment: PYTHONPATH=.
```

## 📊 Available Tools

Our MCP server provides 8 advanced tools:

1. **read_file** - Read file contents from workspace
2. **write_file** - Write content to files
3. **list_files** - List directory contents
4. **analyze_code** - Analyze code structure and metrics
5. **track_token_usage** - Track token usage and costs
6. **get_cost_summary** - Get cost statistics
7. **get_system_health** - Check system health
8. **get_system_status** - Get overall system status

## 🔗 Useful Resources

- **LangFlow MCP Documentation**: https://docs.langflow.org/mcp-server
- **MCP Protocol Specification**: https://modelcontextprotocol.io/
- **Our Troubleshooting Guide**: `LANGFLOW_MCP_TROUBLESHOOTING.md`
- **Test Scripts**: `test_connector.py`, `test_mcp_protocol.py`

## 📞 Getting Help

### **Debug Information to Collect**
1. LangFlow version and installation method
2. Python version and path
3. Operating system details
4. Error messages from LangFlow console
5. Results from test scripts
6. MCP configuration file contents

### **Common Issues & Solutions**
- **"Command not found"**: Use absolute paths
- **"Import errors"**: Check PYTHONPATH configuration
- **"Connection timeout"**: Verify stdio communication
- **"No tools available"**: Test tool registration manually

---

*Last Updated: July 31, 2025*  
*Status: Ready for LangFlow Integration Testing* 