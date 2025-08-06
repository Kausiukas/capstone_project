# 🔧 LangFlow Integration - CORRECTED

## 🚨 **CRITICAL ISSUE IDENTIFIED: Wrong Port!**

### **Problem**: LangFlow is running on port 7861, not 7860
- **Actual LangFlow URL**: `http://localhost:7861` ✅
- **Wrong URL you tried**: `http://localhost:7860` ❌

### **Current Status**:
```
LangFlow Server: RUNNING ✅
Correct Port: 7861 ✅
Correct URL: http://localhost:7861 ✅
MCP Server: RUNNING ✅
```

---

## 🚀 **Corrected Integration Steps**

### **Step 1: Access LangFlow on Correct Port**
1. **Open Browser**: Navigate to `http://localhost:7861` (not 7860!)
2. **Wait for Load**: LangFlow interface should load completely
3. **Verify Access**: You should see the LangFlow dashboard

### **Step 2: Configure MCP Server Integration**
1. **Navigate to Settings**:
   - Look for a settings icon (gear/cog) or menu
   - Find "MCP Servers" or "External Tools" section
   - Look for "Add Server" or "Configure" options

2. **Add Our MCP Server** (Use STDIO tab):
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

## 🔍 **Troubleshooting the MCP Server Error**

### **Issue: MCP Server Shows "Error" Status**

#### **Solution 1: Check MCP Server is Running**
```bash
# In PowerShell terminal
.\venv\Scripts\Activate.ps1
python mcp_langflow_connector.py
```

#### **Solution 2: Verify File Paths**
Make sure the MCP server file exists:
```bash
# Check if file exists
ls mcp_langflow_connector.py
```

#### **Solution 3: Test MCP Server Manually**
```bash
# Test the server directly
python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from mcp_langflow_connector import LangFlowMCPConnector
connector = LangFlowMCPConnector()
print('MCP Server test successful')
"
```

#### **Solution 4: Check PYTHONPATH**
The PYTHONPATH in the configuration should be:
```
D:\GUI\System-Reference-Clean\LangFlow_Connect;D:\GUI\System-Reference-Clean\LangFlow_Connect\src
```

---

## 🛠️ **Corrected Configuration**

### **For LangFlow MCP Server Configuration**:

1. **Server Name**: `langflow-connect`
2. **Command**: `python`
3. **Arguments**: `mcp_langflow_connector.py`
4. **Environment Variables**:
   - **Key**: `PYTHONPATH`
   - **Value**: `D:\GUI\System-Reference-Clean\LangFlow_Connect;D:\GUI\System-Reference-Clean\LangFlow_Connect\src`
   - **Key**: `LANGFLOW_CONNECT_ENV`
   - **Value**: `production`

### **Important Notes**:
- Use the **STDIO** tab (not JSON or SSE)
- Make sure the MCP server is running before adding the configuration
- The server should show "Connected" status after configuration

---

## 🧪 **Testing Steps**

### **Step 1: Verify LangFlow Access**
1. Open `http://localhost:7861` in browser
2. Confirm LangFlow interface loads
3. Navigate to MCP Servers section

### **Step 2: Add MCP Server**
1. Click "Add Server" or similar
2. Use STDIO configuration
3. Enter the configuration above
4. Test connection

### **Step 3: Verify Tools**
1. Check if all 8 tools appear
2. Test a simple tool like `get_system_health`
3. Verify tool execution works

---

## 🚨 **Common Issues and Solutions**

### **Issue 1: "Not Found" Error**
**Cause**: Wrong port (7860 instead of 7861)
**Solution**: Use `http://localhost:7861`

### **Issue 2: MCP Server "Error" Status**
**Cause**: MCP server not running or configuration incorrect
**Solution**: 
1. Start MCP server: `python mcp_langflow_connector.py`
2. Check file paths and PYTHONPATH
3. Verify configuration in STDIO tab

### **Issue 3: OAuth Authentication Error**
**Cause**: Authentication flow issues
**Solution**: 
1. Skip OAuth for now (use basic configuration)
2. Focus on MCP server connection first
3. OAuth can be configured later

---

## 📋 **Quick Fix Checklist**

- [ ] **Access correct URL**: `http://localhost:7861`
- [ ] **Start MCP server**: `python mcp_langflow_connector.py`
- [ ] **Use STDIO configuration** (not JSON)
- [ ] **Verify PYTHONPATH** in environment variables
- [ ] **Test connection** in LangFlow
- [ ] **Verify tools appear** in interface

---

## 🎯 **Expected Results**

### **Success Indicators**:
- ✅ LangFlow accessible at `http://localhost:7861`
- ✅ MCP server shows "Connected" status
- ✅ All 8 tools appear in LangFlow interface
- ✅ Tools execute successfully

### **If Still Having Issues**:
1. Check LangFlow logs for specific error messages
2. Verify MCP server logs for connection issues
3. Test MCP server with MCP Inspector first
4. Restart both servers if needed

---

*Corrected Guide Created: July 31, 2025*  
*Status: PORT ISSUE IDENTIFIED AND FIXED*  
*Next: Test with Correct URL* 