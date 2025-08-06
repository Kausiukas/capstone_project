# 🔍 MCP Inspector Testing Plan

## 📋 **Testing Overview**

**Objective**: Comprehensive validation of our local MCP server using the official MCP Inspector  
**Server**: `mcp_langflow_connector.py`  
**Tools**: 8 advanced tools for LangFlow integration  
**Protocol**: JSON-RPC 2.0 over stdio  

## 🎯 **Test Categories**

### **1. Protocol Compliance Testing**
### **2. Tool Registration Testing**  
### **3. Tool Execution Testing**
### **4. Error Handling Testing**
### **5. Performance Testing**

---

## 🔧 **Setup Instructions**

### **Prerequisites**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Verify MCP Inspector is installed
npm list -g @modelcontextprotocol/inspector
```

### **Start Testing Session**
```bash
# Launch MCP Inspector with our server
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

---

## 📊 **Test Suite 1: Protocol Compliance**

### **Test 1.1: Server Initialization**
**Objective**: Verify server starts and responds to initialization request

**Steps**:
1. Launch MCP Inspector
2. Check "Server Connection" pane
3. Verify server status shows "Connected"
4. Check for any initialization errors

**Expected Results**:
- ✅ Server connects successfully
- ✅ No initialization errors
- ✅ Protocol version compatibility confirmed

**Test Command**:
```bash
npx @modelcontextprotocol/inspector python mcp_langflow_connector.py
```

### **Test 1.2: JSON-RPC 2.0 Compliance**
**Objective**: Verify all requests/responses follow JSON-RPC 2.0 specification

**Steps**:
1. Monitor "Notifications" pane for protocol errors
2. Check request/response format
3. Verify error handling for malformed requests

**Expected Results**:
- ✅ All messages follow JSON-RPC 2.0 format
- ✅ Proper error codes returned for invalid requests
- ✅ No protocol violations

---

## 🛠️ **Test Suite 2: Tool Registration**

### **Test 2.1: Tool Discovery**
**Objective**: Verify all 8 tools are properly registered and discoverable

**Steps**:
1. Navigate to "Tools" tab in Inspector
2. Check tool list for all 8 expected tools
3. Verify tool names and descriptions

**Expected Tools**:
- ✅ `read_file` - Read file contents from workspace
- ✅ `write_file` - Write content to a file
- ✅ `list_files` - List files in a directory
- ✅ `analyze_code` - Analyze code structure and complexity
- ✅ `track_token_usage` - Track token usage for AI operations
- ✅ `get_cost_summary` - Get cost summary for AI operations
- ✅ `get_system_health` - Get system health status
- ✅ `get_system_status` - Get detailed system status

### **Test 2.2: Tool Schema Validation**
**Objective**: Verify each tool has proper input schema

**Steps**:
1. Click on each tool in Inspector
2. Check input schema definition
3. Verify required vs optional parameters
4. Check parameter types and descriptions

**Expected Results**:
- ✅ All tools have valid input schemas
- ✅ Required parameters clearly marked
- ✅ Parameter types match expected values
- ✅ Descriptions are clear and helpful

---

## ⚡ **Test Suite 3: Tool Execution**

### **Test 3.1: File Operations**
**Objective**: Test file-related tools

#### **Test 3.1.1: read_file Tool**
**Steps**:
1. Select `read_file` tool
2. Enter file path: `mcp_langflow_connector.py`
3. Execute tool
4. Verify response contains file contents

**Expected Results**:
- ✅ Tool executes successfully
- ✅ File contents returned
- ✅ No errors for valid file path

#### **Test 3.1.2: list_files Tool**
**Steps**:
1. Select `list_files` tool
2. Enter directory: `.` (current directory)
3. Execute tool
4. Verify response contains file list

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Directory contents returned
- ✅ File list is accurate

#### **Test 3.1.3: write_file Tool**
**Steps**:
1. Select `write_file` tool
2. Enter file path: `test_output.txt`
3. Enter content: `Test content from MCP Inspector`
4. Execute tool
5. Verify file was created
6. Use `read_file` to verify content

**Expected Results**:
- ✅ Tool executes successfully
- ✅ File created with correct content
- ✅ No errors during write operation

### **Test 3.2: Code Analysis**
**Objective**: Test code analysis tool

#### **Test 3.2.1: analyze_code Tool**
**Steps**:
1. Select `analyze_code` tool
2. Enter file path: `mcp_langflow_connector.py`
3. Execute tool
4. Verify analysis results

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Code analysis returned
- ✅ Results include complexity metrics
- ✅ No errors for valid Python file

### **Test 3.3: System Monitoring**
**Objective**: Test system monitoring tools

#### **Test 3.3.1: get_system_health Tool**
**Steps**:
1. Select `get_system_health` tool
2. Execute tool (no parameters needed)
3. Verify health status returned

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Health status returned
- ✅ Status indicates system is healthy

#### **Test 3.3.2: get_system_status Tool**
**Steps**:
1. Select `get_system_status` tool
2. Execute tool (no parameters needed)
3. Verify detailed status returned

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Detailed status information returned
- ✅ Includes memory, CPU, and other metrics

### **Test 3.4: Token Tracking**
**Objective**: Test token tracking tools

#### **Test 3.4.1: track_token_usage Tool**
**Steps**:
1. Select `track_token_usage` tool
2. Enter parameters:
   - `operation`: "test_operation"
   - `tokens_used`: 100
   - `model`: "gpt-4"
3. Execute tool
4. Verify tracking response

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Token usage tracked
- ✅ Confirmation message returned

#### **Test 3.4.2: get_cost_summary Tool**
**Steps**:
1. Select `get_cost_summary` tool
2. Execute tool (no parameters needed)
3. Verify cost summary returned

**Expected Results**:
- ✅ Tool executes successfully
- ✅ Cost summary returned
- ✅ Includes total costs and usage statistics

---

## 🚨 **Test Suite 4: Error Handling**

### **Test 4.1: Invalid File Paths**
**Objective**: Test error handling for invalid file operations

#### **Test 4.1.1: read_file with Invalid Path**
**Steps**:
1. Select `read_file` tool
2. Enter invalid file path: `nonexistent_file.txt`
3. Execute tool
4. Verify proper error response

**Expected Results**:
- ✅ Tool handles error gracefully
- ✅ Clear error message returned
- ✅ No server crash

#### **Test 4.1.2: list_files with Invalid Directory**
**Steps**:
1. Select `list_files` tool
2. Enter invalid directory: `/invalid/path`
3. Execute tool
4. Verify proper error response

**Expected Results**:
- ✅ Tool handles error gracefully
- ✅ Clear error message returned
- ✅ No server crash

### **Test 4.2: Invalid Parameters**
**Objective**: Test error handling for invalid parameters

#### **Test 4.2.1: Missing Required Parameters**
**Steps**:
1. Select `read_file` tool
2. Leave file_path empty
3. Execute tool
4. Verify validation error

**Expected Results**:
- ✅ Parameter validation works
- ✅ Clear error message about missing parameter
- ✅ No server crash

#### **Test 4.2.2: Invalid Parameter Types**
**Steps**:
1. Select `track_token_usage` tool
2. Enter invalid token count: "not_a_number"
3. Execute tool
4. Verify type validation error

**Expected Results**:
- ✅ Type validation works
- ✅ Clear error message about invalid type
- ✅ No server crash

---

## ⚡ **Test Suite 5: Performance Testing**

### **Test 5.1: Response Time**
**Objective**: Measure tool execution response times

**Steps**:
1. Execute each tool 3 times
2. Record response times
3. Calculate average response time
4. Verify performance is acceptable

**Performance Targets**:
- ✅ Simple tools (< 1 second): `read_file`, `list_files`, `get_system_health`
- ✅ Medium tools (< 3 seconds): `write_file`, `analyze_code`, `get_system_status`
- ✅ Complex tools (< 5 seconds): `track_token_usage`, `get_cost_summary`

### **Test 5.2: Concurrent Execution**
**Objective**: Test server stability under concurrent requests

**Steps**:
1. Execute multiple tools simultaneously
2. Monitor for race conditions
3. Verify all requests complete successfully
4. Check for any deadlocks or crashes

**Expected Results**:
- ✅ All concurrent requests complete
- ✅ No race conditions
- ✅ Server remains stable
- ✅ No memory leaks

---

## 📋 **Test Execution Checklist**

### **Pre-Testing Setup**
- [ ] Virtual environment activated
- [ ] MCP Inspector installed
- [ ] All test files available
- [ ] Test directory prepared

### **Protocol Testing**
- [ ] Server initialization test
- [ ] JSON-RPC 2.0 compliance test
- [ ] Error handling test

### **Tool Registration Testing**
- [ ] All 8 tools discovered
- [ ] Tool schemas validated
- [ ] Parameter definitions checked

### **Tool Execution Testing**
- [ ] File operations tested
- [ ] Code analysis tested
- [ ] System monitoring tested
- [ ] Token tracking tested

### **Error Handling Testing**
- [ ] Invalid file paths tested
- [ ] Invalid parameters tested
- [ ] Missing parameters tested

### **Performance Testing**
- [ ] Response times measured
- [ ] Concurrent execution tested
- [ ] Memory usage monitored

---

## 📊 **Test Results Template**

### **Test Session Information**
- **Date**: [Date]
- **Tester**: [Name]
- **MCP Inspector Version**: [Version]
- **Server Version**: [Version]

### **Test Results Summary**
```
Protocol Compliance: [PASS/FAIL]
Tool Registration: [PASS/FAIL]
Tool Execution: [PASS/FAIL]
Error Handling: [PASS/FAIL]
Performance: [PASS/FAIL]
```

### **Detailed Results**
```
Tool 1 - read_file: [PASS/FAIL] - [Notes]
Tool 2 - write_file: [PASS/FAIL] - [Notes]
Tool 3 - list_files: [PASS/FAIL] - [Notes]
Tool 4 - analyze_code: [PASS/FAIL] - [Notes]
Tool 5 - track_token_usage: [PASS/FAIL] - [Notes]
Tool 6 - get_cost_summary: [PASS/FAIL] - [Notes]
Tool 7 - get_system_health: [PASS/FAIL] - [Notes]
Tool 8 - get_system_status: [PASS/FAIL] - [Notes]
```

### **Issues Found**
- [ ] Issue 1: [Description]
- [ ] Issue 2: [Description]
- [ ] Issue 3: [Description]

### **Performance Metrics**
- Average Response Time: [Time]
- Memory Usage: [Usage]
- Concurrent Request Success Rate: [Percentage]

---

## 🎯 **Success Criteria**

### **Minimum Success Criteria**
- ✅ All 8 tools register successfully
- ✅ All tools execute without crashes
- ✅ Protocol compliance verified
- ✅ Basic error handling works

### **Full Success Criteria**
- ✅ All tests pass
- ✅ Performance targets met
- ✅ No critical issues found
- ✅ Ready for LangFlow integration

---

## 🚨 **Troubleshooting Guide**

### **Common Issues**

#### **Issue: Tools Not Appearing**
**Solution**: Check server initialization and tool registration logic

#### **Issue: Tool Execution Fails**
**Solution**: Check tool implementation and error handling

#### **Issue: Protocol Errors**
**Solution**: Verify JSON-RPC 2.0 compliance

#### **Issue: Performance Issues**
**Solution**: Optimize tool implementations and add caching

---

*Testing Plan Created: July 31, 2025*  
*Status: READY FOR EXECUTION* 