# 🔗 LangFlow MCP Integration Guide

## 🎉 **Current Status: BOTH SERVERS RUNNING!**

### ✅ **LangFlow Server**
- **Status**: ✅ RUNNING
- **Port**: 7860
- **URL**: http://localhost:7860
- **Installation**: ✅ SUCCESSFUL

### ✅ **MCP Server**
- **Status**: ✅ RUNNING
- **Protocol**: JSON-RPC 2.0 over stdio
- **Tools**: 8 advanced tools available
- **Validation**: ✅ MCP Inspector tested

---

## 🚀 **Integration Steps**

### **Step 1: Access LangFlow Web Interface**
1. **Open Browser**: Navigate to `http://localhost:7860`
2. **Wait for Load**: LangFlow interface should load completely
3. **Verify Access**: You should see the LangFlow dashboard

### **Step 2: Configure MCP Server Integration**
1. **Navigate to Settings**:
   - Look for a settings icon (gear/cog) or menu
   - Find "MCP Servers" or "External Tools" section
   - Look for "Add Server" or "Configure" options

2. **Add Our MCP Server**:
   ```json
   {
     "name": "langflow-connect",
     "command": "python",
     "args": ["mcp_langflow_connector.py"],
     "env": {
       "PYTHONPATH": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect;D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src",
       "LANGFLOW_CONNECT_ENV": "production"
     }
   }
   ```

### **Step 3: Verify Integration**
1. **Check Connection**: Look for connection status indicators
2. **Verify Tools**: All 8 tools should appear in the interface
3. **Test Tools**: Try executing a simple tool

---

## 🛠️ **Available Tools**

### **File Operations**
- **`read_file`**: Read file contents from workspace
- **`write_file`**: Write content to a file
- **`list_files`**: List files in a directory

### **Code Analysis**
- **`analyze_code`**: Analyze code structure and metrics

### **System Monitoring**
- **`get_system_health`**: Get system health status
- **`get_system_status`**: Get detailed system status

### **Token Tracking**
- **`track_token_usage`**: Track token usage and costs
- **`get_cost_summary`**: Get cost summary and statistics

---

## 🧪 **Testing Workflow**

### **Test 1: Basic File Operations**
1. **Use `list_files`**:
   - Directory: `.` (current directory)
   - Expected: List of files in workspace

2. **Use `read_file`**:
   - File: `mcp_langflow_connector.py`
   - Expected: File contents displayed

3. **Use `write_file`**:
   - File: `test_integration.txt`
   - Content: `LangFlow MCP Integration Test`
   - Expected: File created successfully

### **Test 2: System Monitoring**
1. **Use `get_system_health`**:
   - Expected: System health status returned

2. **Use `get_system_status`**:
   - Expected: Detailed system status with JSON

### **Test 3: Code Analysis**
1. **Use `analyze_code`**:
   - File: `mcp_langflow_connector.py`
   - Expected: Code analysis results

### **Test 4: Token Tracking**
1. **Use `track_token_usage`**:
   - Operation: "test_operation"
   - Model: "gpt-4"
   - Input tokens: 100
   - Output tokens: 50
   - Expected: Token usage tracked

2. **Use `get_cost_summary`**:
   - Expected: Cost summary returned

---

## 🔍 **Troubleshooting**

### **Issue 1: Tools Don't Appear**
**Symptoms**: MCP server tools not visible in LangFlow
**Solutions**:
1. Check MCP server is running: `netstat -an | findstr :7860`
2. Verify LangFlow can connect to MCP server
3. Check LangFlow logs for connection errors
4. Restart both servers if needed

### **Issue 2: Tool Execution Fails**
**Symptoms**: Tools appear but don't execute
**Solutions**:
1. Check MCP server logs for errors
2. Verify tool implementation
3. Test tools with MCP Inspector
4. Check JSON-RPC compliance

### **Issue 3: Connection Issues**
**Symptoms**: LangFlow can't connect to MCP server
**Solutions**:
1. Verify `PYTHONPATH` in configuration
2. Check MCP server is running
3. Verify file paths are correct
4. Restart MCP server

---

## 📊 **Success Indicators**

### **✅ Integration Success**
- [ ] LangFlow web interface accessible
- [ ] MCP server configuration added
- [ ] All 8 tools appear in interface
- [ ] Tools execute successfully
- [ ] No connection errors

### **✅ Performance Success**
- [ ] Tool response time < 5 seconds
- [ ] Stable connection maintained
- [ ] No memory leaks
- [ ] Error handling works

---

## 🎯 **Next Steps After Integration**

### **Immediate (Once Integration Works)**
1. **Document Success**: Record working configuration
2. **Test All Tools**: Verify each tool works
3. **Create Sample Workflow**: Build a simple LangFlow workflow

### **Short-term**
1. **Performance Testing**: Measure response times
2. **Error Testing**: Test error scenarios
3. **Workflow Creation**: Build complex workflows

### **Long-term**
1. **Production Deployment**: Deploy to production
2. **User Documentation**: Create user guides
3. **Maintenance Plan**: Plan for updates

---

## 📞 **Support Resources**

### **LangFlow Documentation**
- [LangFlow Docs](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)

### **MCP Documentation**
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Inspector](https://modelcontextprotocol.io/legacy/tools/inspector)

### **Our Documentation**
- `MCP_INSPECTOR_TEST_RESULTS.md` - MCP server validation
- `LANGFLOW_INTEGRATION_STATUS.md` - Integration progress
- `mcp_langflow_connector.py` - MCP server implementation

---

*Integration Guide Created: July 31, 2025*  
*Status: BOTH SERVERS RUNNING*  
*Ready for Integration Testing* 