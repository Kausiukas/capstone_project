# Inspector Troubleshooting Quick Reference

## Quick Start Commands

### **1. Run Diagnostic Script**
```bash
python diagnose_mcp_server.py
```

### **2. Test Minimal Server**
```bash
npx @modelcontextprotocol/inspector python minimal_mcp_server.py
```

### **3. Test Full Server**
```bash
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py
```

## Common Issues & Solutions

### **Issue: Server Won't Start (Exit Code: 1)**

**Quick Fix**:
1. Run diagnostic: `python diagnose_mcp_server.py`
2. Check PostgreSQL connection
3. Test minimal server first
4. Fix identified issues

**Common Causes**:
- PostgreSQL not running
- Missing dependencies
- Import errors
- Configuration issues

### **Issue: Inspector Can't Connect**

**Quick Fix**:
1. Verify Inspector installation: `npx @modelcontextprotocol/inspector --help`
2. Test with minimal server
3. Check server protocol compliance
4. Monitor server logs

**Common Causes**:
- Server not following JSON-RPC 2.0
- Protocol violations
- Server crashes on startup

### **Issue: Tools Not Appearing**

**Quick Fix**:
1. Check tool registration in server
2. Verify tool schema format
3. Test tools/list method
4. Check server logs

**Common Causes**:
- Tool registration errors
- Invalid tool schemas
- Server initialization failures

## Official Inspector Commands

### **Basic Inspector Usage**
```bash
# Basic usage
npx @modelcontextprotocol/inspector <command>

# With arguments
npx @modelcontextprotocol/inspector <command> <arg1> <arg2>
```

### **Testing Locally Developed Servers**
```bash
# Python server
npx @modelcontextprotocol/inspector python path/to/server.py

# Our server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py
```

### **Testing Official Servers**
```bash
# Filesystem server
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /path/to/directory
```

## Inspector Features to Test

### **Server Connection Pane**
- Transport selection
- Command-line arguments
- Environment variables

### **Tools Tab**
- Tool discovery
- Schema validation
- Tool execution
- Result display

### **Notifications Pane**
- Server logs
- Error messages
- Protocol violations

## Development Workflow

### **1. Start Development**
```bash
# Launch Inspector with server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py

# Verify connectivity
# Check capability negotiation
```

### **2. Iterative Testing**
```bash
# Make server changes
# Rebuild server
# Reconnect Inspector
# Test affected features
# Monitor messages
```

### **3. Test Edge Cases**
- Invalid inputs
- Missing parameters
- Concurrent operations
- Error handling

## Troubleshooting Checklist

### **Pre-Testing**
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] PostgreSQL running
- [ ] pgvector extension available

### **Server Testing**
- [ ] Server imports successfully
- [ ] Server initializes without errors
- [ ] Server follows JSON-RPC 2.0
- [ ] Tools register correctly
- [ ] Tools execute properly

### **Inspector Testing**
- [ ] Inspector installed and available
- [ ] Inspector connects to server
- [ ] Tools appear in Inspector
- [ ] Tools execute in Inspector
- [ ] Results display correctly

## Error Codes Reference

### **JSON-RPC 2.0 Error Codes**
- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

### **MCP Protocol Errors**
- Tool registration failures
- Tool execution errors
- Protocol violations
- Connection issues

## Performance Targets

### **Response Times**
- Simple tools: < 1 second
- Medium tools: < 3 seconds
- Complex tools: < 5 seconds

### **Resource Usage**
- Memory: < 500MB
- CPU: < 80%
- Network: < 100MB/s

## Success Indicators

### **Basic Success**
- [ ] Inspector connects to server
- [ ] Server starts without errors
- [ ] Tools are discoverable
- [ ] Basic tools execute successfully

### **Full Success**
- [ ] All 81 tools work with Inspector
- [ ] Protocol compliance verified
- [ ] Performance meets targets
- [ ] Error handling works correctly

## Next Steps After Troubleshooting

### **If Minimal Server Works**
1. Test full server
2. Add features incrementally
3. Test each addition with Inspector
4. Monitor for issues

### **If Full Server Fails**
1. Identify specific issues
2. Fix PostgreSQL problems
3. Resolve import errors
4. Test again with Inspector

### **If Inspector Issues Persist**
1. Check Node.js installation
2. Verify Inspector installation
3. Test with official servers
4. Check network connectivity

## References

- [Official MCP Inspector Documentation](https://modelcontextprotocol.io/legacy/tools/inspector)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Inspector Repository](https://github.com/modelcontextprotocol/inspector)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

## Emergency Procedures

### **Server Won't Start**
1. Run diagnostic script
2. Check error logs
3. Test minimal server
4. Fix identified issues

### **Inspector Won't Connect**
1. Test with official server
2. Check server protocol
3. Verify JSON-RPC compliance
4. Monitor server output

### **Tools Not Working**
1. Check tool registration
2. Verify tool schemas
3. Test individual tools
4. Check error handling

## Quick Commands Summary

```bash
# Diagnostic
python diagnose_mcp_server.py

# Test minimal server
npx @modelcontextprotocol/inspector python minimal_mcp_server.py

# Test full server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py

# Test official server
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /path

# Check Inspector
npx @modelcontextprotocol/inspector --help
``` 