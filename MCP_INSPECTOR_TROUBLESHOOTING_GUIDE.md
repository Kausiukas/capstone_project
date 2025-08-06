# MCP Inspector Troubleshooting Guide

## Executive Summary

This guide provides comprehensive troubleshooting procedures for MCP server issues when using the official MCP Inspector. Based on the [official MCP Inspector documentation](https://modelcontextprotocol.io/legacy/tools/inspector) and our current server startup problems, this guide addresses common issues and provides step-by-step solutions.

## Current Issue Analysis

### **Problem Statement**
Our MCP server is failing to start with exit code: 1, preventing Inspector testing:
```
🚀 Starting MCP server...
✅ MCP server started with PID: [PID]
⚠️ MCP server stopped (exit code: 1)
```

### **Root Cause Assessment**
Based on the official Inspector documentation and our server behavior, the issue is likely:
1. **PostgreSQL+Vector LLM Integration Problems** - Database connection issues
2. **Protocol Compliance Issues** - JSON-RPC 2.0 or MCP protocol violations
3. **Dependency Issues** - Missing or incompatible packages
4. **Configuration Problems** - Invalid server configuration

## Inspector Installation and Basic Usage

### **Official Inspector Installation**
According to the [official documentation](https://modelcontextprotocol.io/legacy/tools/inspector), the Inspector runs directly through `npx`:

```bash
# Basic Inspector usage
npx @modelcontextprotocol/inspector <command>

# With arguments
npx @modelcontextprotocol/inspector <command> <arg1> <arg2>
```

### **Inspecting Locally Developed Servers**
For our locally developed server, the recommended approach is:

```bash
# Python server inspection
npx @modelcontextprotocol/inspector python path/to/server/script.py args...

# For our specific server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py
```

## Step-by-Step Troubleshooting Process

### **Step 1: Verify Inspector Installation**

#### **1.1 Check Inspector Availability**
```bash
# Verify Inspector is available
npx @modelcontextprotocol/inspector --version

# Check if Inspector can run
npx @modelcontextprotocol/inspector --help
```

#### **1.2 Test Inspector with Working Server**
```bash
# Test with official filesystem server
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /Users/username/Desktop
```

**Expected Result**: Inspector should connect and show tools/resources

### **Step 2: Isolate Server Issues**

#### **2.1 Test Server Without Inspector**
```bash
# Test server directly
python mcp_langflow_connector_simple.py

# Check for immediate errors
python -c "import mcp_langflow_connector_simple; print('Import successful')"
```

#### **2.2 Create Minimal Test Server**
Create a minimal MCP server to test basic functionality:

```python
# minimal_mcp_server.py
#!/usr/bin/env python3
import asyncio
import json
import sys

class MinimalMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "ping",
                "description": "Ping the server",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def handle_request(self, request):
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"tools": self.tools}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            if tool_name == "ping":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": "pong"}]}
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": "Method not found"}
        }

async def main():
    server = MinimalMCPServer()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: sys.stdout.write(json.dumps(response) + "\n")
            )
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            break

if __name__ == "__main__":
    asyncio.run(main())
```

#### **2.3 Test Minimal Server with Inspector**
```bash
# Test minimal server
npx @modelcontextprotocol/inspector python minimal_mcp_server.py
```

**Expected Result**: Inspector should connect and show the "ping" tool

### **Step 3: Diagnose PostgreSQL Issues**

#### **3.1 Test Database Connection Separately**
```python
# test_db_connection.py
import psycopg2
import os

def test_postgresql_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user=os.getenv('USERNAME', 'postgres')
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ PostgreSQL connection successful: {version[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_postgresql_connection()
```

#### **3.2 Test pgvector Extension**
```python
# test_pgvector.py
import psycopg2
import os

def test_pgvector_extension():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user=os.getenv('USERNAME', 'postgres')
        )
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        result = cur.fetchone()
        if result:
            print("✅ pgvector extension available")
            return True
        else:
            print("❌ pgvector extension not found")
            return False
    except Exception as e:
        print(f"❌ pgvector test failed: {e}")
        return False

if __name__ == "__main__":
    test_pgvector_extension()
```

### **Step 4: Create Server Without PostgreSQL**

#### **4.1 Modify Server to Skip PostgreSQL**
Create a version of our server that skips PostgreSQL initialization:

```python
# mcp_server_no_postgres.py
# Copy mcp_langflow_connector_simple.py and comment out PostgreSQL initialization
# In __init__ method, comment out:
# self.vector_llm = PostgreSQLVectorLLM()
```

#### **4.2 Test Server Without PostgreSQL**
```bash
# Test server without PostgreSQL
npx @modelcontextprotocol/inspector python mcp_server_no_postgres.py
```

### **Step 5: Protocol Compliance Testing**

#### **5.1 Test JSON-RPC 2.0 Compliance**
Create a protocol compliance test:

```python
# test_protocol_compliance.py
import json
import asyncio
import sys

async def test_protocol_compliance():
    # Test basic JSON-RPC 2.0 format
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    print(f"Testing request: {json.dumps(test_request, indent=2)}")
    
    # Send to server and validate response
    # Implementation depends on server interface

if __name__ == "__main__":
    asyncio.run(test_protocol_compliance())
```

## Inspector Feature Testing

### **Server Connection Pane Testing**
According to the [official documentation](https://modelcontextprotocol.io/legacy/tools/inspector), the Inspector provides:

1. **Transport Selection**: Choose connection method
2. **Command-line Arguments**: Customize server startup
3. **Environment Variables**: Set server environment

### **Tools Tab Testing**
The Tools tab should show:
- All available tools
- Tool schemas and descriptions
- Tool testing capabilities
- Execution results

### **Notifications Pane Testing**
Monitor for:
- Server logs
- Error messages
- Protocol violations
- Connection issues

## Development Workflow (Official Guidelines)

Based on the [official Inspector documentation](https://modelcontextprotocol.io/legacy/tools/inspector), follow this workflow:

### **1. Start Development**
```bash
# Launch Inspector with server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py

# Verify basic connectivity
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
- Error handling verification

## Common Issues and Solutions

### **Issue 1: Server Won't Start**
**Symptoms**: Exit code: 1, immediate termination

**Solutions**:
1. **Check Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip list | grep psycopg2
   pip list | grep numpy
   ```

2. **Test Imports**:
   ```python
   python -c "import psycopg2; print('psycopg2 OK')"
   python -c "import numpy; print('numpy OK')"
   ```

3. **Check Python Version**:
   ```bash
   python --version
   # Should be Python 3.8+
   ```

### **Issue 2: Inspector Can't Connect**
**Symptoms**: Inspector shows connection errors

**Solutions**:
1. **Verify Server Protocol**:
   - Ensure server follows JSON-RPC 2.0
   - Check stdin/stdout communication
   - Validate message format

2. **Test with Minimal Server**:
   ```bash
   npx @modelcontextprotocol/inspector python minimal_mcp_server.py
   ```

3. **Check Server Output**:
   ```bash
   python mcp_langflow_connector_simple.py 2>&1 | tee server.log
   ```

### **Issue 3: Tools Not Appearing**
**Symptoms**: Inspector connects but no tools shown

**Solutions**:
1. **Check Tool Registration**:
   - Verify tools list in server
   - Check tool schema format
   - Validate tool names

2. **Test tools/list Method**:
   ```python
   # Send tools/list request manually
   request = {
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/list",
       "params": {}
   }
   ```

### **Issue 4: Tool Execution Fails**
**Symptoms**: Tools appear but don't execute

**Solutions**:
1. **Check Tool Implementation**:
   - Verify tool handlers exist
   - Check parameter validation
   - Test error handling

2. **Test Individual Tools**:
   ```python
   # Test specific tool
   request = {
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
           "name": "ping",
           "arguments": {}
       }
   }
   ```

## Advanced Troubleshooting

### **Debug Mode Testing**
Enable debug logging in server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Protocol Validation**
Use the official MCP protocol validator:

```bash
# Install MCP tools
pip install mcp

# Validate server protocol
mcp validate-server python mcp_langflow_connector_simple.py
```

### **Performance Testing**
Test server performance under Inspector load:

```bash
# Run multiple Inspector instances
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py &
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py &
```

## Inspector Best Practices

### **Development Workflow**
1. **Start with Minimal Server**: Begin with basic functionality
2. **Add Features Incrementally**: Add tools one by one
3. **Test Each Addition**: Verify with Inspector after each change
4. **Monitor Logs**: Watch for errors and warnings
5. **Validate Protocol**: Ensure compliance with MCP standards

### **Testing Strategy**
1. **Unit Testing**: Test individual tools
2. **Integration Testing**: Test tool interactions
3. **Protocol Testing**: Validate MCP compliance
4. **Performance Testing**: Test under load
5. **Error Testing**: Test error conditions

### **Documentation**
1. **Tool Documentation**: Document each tool thoroughly
2. **Error Documentation**: Document error codes and messages
3. **Protocol Documentation**: Document protocol compliance
4. **Testing Documentation**: Document test procedures

## Success Criteria

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
- [ ] Documentation is complete

## Next Steps

### **Immediate Actions**
1. **Fix Server Startup**: Resolve exit code: 1 issue
2. **Test with Minimal Server**: Verify basic Inspector functionality
3. **Incremental Testing**: Add features one by one
4. **Protocol Validation**: Ensure MCP compliance

### **Long-term Goals**
1. **Full Inspector Integration**: Complete 81-tool validation
2. **Automated Testing**: Implement CI/CD with Inspector
3. **Performance Optimization**: Optimize for Inspector usage
4. **Documentation**: Complete Inspector documentation

## Conclusion

This troubleshooting guide provides a systematic approach to resolving MCP server issues with Inspector. By following the official [MCP Inspector documentation](https://modelcontextprotocol.io/legacy/tools/inspector) and our specific troubleshooting procedures, we can:

1. **Identify Root Causes**: Systematic diagnosis of server issues
2. **Resolve Problems**: Step-by-step solutions for common issues
3. **Validate Functionality**: Ensure proper Inspector integration
4. **Maintain Quality**: Follow best practices for development

The key is to start with a minimal working server and gradually add features while testing with Inspector at each step. This ensures that we maintain protocol compliance and functionality throughout the development process.

**References**:
- [Official MCP Inspector Documentation](https://modelcontextprotocol.io/legacy/tools/inspector)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Inspector Repository](https://github.com/modelcontextprotocol/inspector) 