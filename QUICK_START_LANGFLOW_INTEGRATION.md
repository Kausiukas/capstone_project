# ⚡ Quick Start: LangFlow MCP Integration

## 🚀 **Ready to Execute - Follow These Steps**

### **Step 1: Start LangFlow** (Choose one method)

```bash
# Method 1: Python module (RECOMMENDED)
python -m langflow run --port 7860

# Method 2: Direct command (if PATH is set)
langflow run --port 7860

# Method 3: Full path (if needed)
C:\Users\OCPC\AppData\Roaming\Python\Python312\Scripts\langflow.exe run --port 7860
```

### **Step 2: Verify LangFlow is Running**

```bash
# Check if port 7860 is listening
netstat -an | findstr :7860
```

**Expected Output**: Should show `LISTENING` on port 7860

### **Step 3: Access LangFlow Dashboard**

1. Open browser: **http://localhost:7860**
2. Wait for dashboard to load
3. Look for **MCP Server** tab

### **Step 4: Add MCP Server**

1. Click **MCP Server** tab
2. Find **JSON** configuration option
3. Copy and paste this configuration:

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

### **Step 5: Verify Integration**

1. **Check Connection Status**: Should show connected
2. **Verify Tools**: Look for all 8 tools:
   - `read_file`, `write_file`, `list_files`
   - `analyze_code`, `track_token_usage`
   - `get_cost_summary`, `get_system_health`, `get_system_status`
3. **Test Tool**: Try `list_files` with input `{"directory": "."}`

## 🔧 **If Something Goes Wrong**

### **LangFlow Won't Start?**
```bash
# Try this instead:
python -m langflow run --port 7860
```

### **MCP Server Connection Fails?**
```bash
# Test our server first:
python test_connector.py
python test_mcp_protocol.py
```

### **Tools Not Appearing?**
```bash
# Use MCP Inspector to test:
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

### **Need Absolute Paths?**
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

## ✅ **Success Indicators**

- ✅ LangFlow dashboard loads at http://localhost:7860
- ✅ MCP server shows as connected
- ✅ All 8 tools appear in tools list
- ✅ Tool execution works (e.g., `list_files` returns file list)
- ✅ No persistent error messages

## 📞 **Need Help?**

- **Full Guide**: See `MCP_LANGFLOW_INTEGRATION_PLAN.md`
- **Troubleshooting**: See `LANGFLOW_MCP_TROUBLESHOOTING.md`
- **Test Scripts**: Run `python test_connector.py` to verify server

---

**Status**: ✅ **READY TO EXECUTE**  
**LangFlow**: 1.5.0.post1 installed  
**MCP Server**: 8 tools tested and working  
**Configuration**: Ready to paste 