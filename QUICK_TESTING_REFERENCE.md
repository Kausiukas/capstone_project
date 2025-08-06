# ⚡ Quick Testing Reference - MCP Inspector

## 🚀 **Start Testing Now**

### **1. Launch MCP Inspector**
```bash
# In PowerShell terminal (ensure venv is activated)
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

### **2. Quick Test Checklist**

#### **✅ Protocol Test (30 seconds)**
- [ ] Server connects successfully
- [ ] No initialization errors in "Notifications" pane
- [ ] "Server Connection" shows "Connected"

#### **✅ Tool Discovery Test (1 minute)**
- [ ] Go to "Tools" tab
- [ ] Verify all 8 tools appear:
  - `read_file`
  - `write_file` 
  - `list_files`
  - `analyze_code`
  - `track_token_usage`
  - `get_cost_summary`
  - `get_system_health`
  - `get_system_status`

#### **✅ Quick Tool Test (2 minutes)**
- [ ] Test `read_file` with `mcp_langflow_connector.py`
- [ ] Test `list_files` with `.` (current directory)
- [ ] Test `get_system_health` (no parameters)

## 🎯 **Expected Results**

### **If Everything Works:**
- ✅ All 8 tools visible in Inspector
- ✅ Tools execute successfully
- ✅ No protocol errors
- ✅ Fast response times (< 3 seconds)

### **If Issues Found:**
- ❌ Tools missing → Check server initialization
- ❌ Tool execution fails → Check tool implementation
- ❌ Protocol errors → Check JSON-RPC compliance
- ❌ Slow responses → Check performance optimization

## 📊 **Quick Performance Check**

### **Response Time Targets:**
- **Fast (< 1s)**: `read_file`, `list_files`, `get_system_health`
- **Medium (< 3s)**: `write_file`, `analyze_code`, `get_system_status`
- **Complex (< 5s)**: `track_token_usage`, `get_cost_summary`

## 🔧 **Common Test Scenarios**

### **Test 1: File Operations**
```
Tool: read_file
File: mcp_langflow_connector.py
Expected: File contents returned
```

### **Test 2: System Status**
```
Tool: get_system_health
Parameters: None
Expected: Health status returned
```

### **Test 3: Error Handling**
```
Tool: read_file
File: nonexistent_file.txt
Expected: Clear error message
```

## 📝 **Documentation Template**

### **Quick Test Results**
```
Date: [Today's Date]
MCP Inspector: [Version]
Server: mcp_langflow_connector.py

Results:
- Protocol Compliance: [PASS/FAIL]
- Tool Registration: [PASS/FAIL] 
- Tool Execution: [PASS/FAIL]
- Performance: [PASS/FAIL]

Issues Found:
- [List any issues]

Next Steps:
- [What to do next]
```

## 🚨 **Troubleshooting Quick Fixes**

### **Issue: Inspector Won't Start**
```bash
# Check if Inspector is installed
npm list -g @modelcontextprotocol/inspector

# Reinstall if needed
npm install -g @modelcontextprotocol/inspector
```

### **Issue: Server Won't Connect**
```bash
# Check if venv is activated
.\venv\Scripts\Activate.ps1

# Test server manually
python mcp_langflow_connector.py
```

### **Issue: Tools Not Appearing**
- Check "Notifications" pane for errors
- Verify server initialization completed
- Restart Inspector and server

## 🎯 **Success Indicators**

### **✅ Ready for LangFlow Integration**
- All 8 tools working in Inspector
- No protocol errors
- Fast response times
- Proper error handling

### **✅ Ready for Production**
- All tests pass
- Performance targets met
- Comprehensive error handling
- Documentation complete

---

## 📞 **Next Steps After Testing**

### **If All Tests Pass:**
1. Document successful results
2. Proceed with LangFlow integration
3. Test with LangFlow (when available)

### **If Issues Found:**
1. Document specific issues
2. Fix problems in MCP server
3. Retest with Inspector
4. Repeat until all tests pass

---

*Quick Reference Created: July 31, 2025*  
*Status: READY FOR IMMEDIATE USE* 