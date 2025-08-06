# Critical Issue Resolution Plan

## Executive Summary

The MCP server is currently failing to start (exit code: 1) after the PostgreSQL+Vector LLM integration. This critical issue must be resolved before any new tool implementation can proceed. This document provides a systematic approach to diagnose and fix the problem.

## Current Issue Analysis

### Problem Statement
- **Issue**: MCP server stops with exit code: 1 immediately after startup
- **Impact**: All 22 existing tools are non-functional
- **Root Cause**: Likely PostgreSQL+Vector LLM integration issues
- **Priority**: CRITICAL - Blocks all development

### Error Pattern
```
🚀 Starting MCP server...
✅ MCP server started with PID: [PID]
⚠️ MCP server stopped (exit code: 1)
```

## Diagnostic Approach

### Step 1: Isolate the Problem
**Objective**: Determine if the issue is with PostgreSQL+Vector LLM integration or other components

#### 1.1 Test MCP Server Without PostgreSQL Integration
**Action**: Temporarily disable PostgreSQL+Vector LLM initialization
**Method**: Comment out the `PostgreSQLVectorLLM` initialization in the MCP server
**Expected Result**: Server should start successfully with basic tools only

#### 1.2 Test Database Connection Separately
**Action**: Create a standalone database connection test
**Method**: Create `test_db_connection.py` to test PostgreSQL+pgvector setup
**Expected Result**: Database connection should work independently

#### 1.3 Check Dependencies
**Action**: Verify all required packages are installed
**Method**: Check `requirements.txt` and installed packages
**Expected Result**: All dependencies should be available

### Step 2: Database Integration Diagnosis
**Objective**: Identify specific database-related issues

#### 2.1 PostgreSQL Service Status
**Action**: Check if PostgreSQL service is running
**Method**: Use system commands to verify service status
**Expected Result**: PostgreSQL should be running and accessible

#### 2.2 pgvector Extension
**Action**: Verify pgvector extension is installed and enabled
**Method**: Connect to database and check extensions
**Expected Result**: pgvector extension should be available

#### 2.3 Connection Parameters
**Action**: Validate database connection parameters
**Method**: Test connection with different parameter combinations
**Expected Result**: Connection should succeed with correct parameters

### Step 3: Code-Level Diagnosis
**Objective**: Identify specific code issues causing the crash

#### 3.1 Exception Handling
**Action**: Add comprehensive exception handling to PostgreSQL+Vector LLM initialization
**Method**: Wrap initialization code in try-catch blocks with detailed logging
**Expected Result**: Should catch and log specific errors

#### 3.2 Memory Issues
**Action**: Check for memory-related issues during initialization
**Method**: Monitor memory usage during startup
**Expected Result**: Memory usage should be reasonable

#### 3.3 Import Issues
**Action**: Verify all imports are working correctly
**Method**: Test imports individually
**Expected Result**: All imports should succeed

## Implementation Plan

### Phase 1: Immediate Fixes (Day 1)

#### 1.1 Create Diagnostic Script
**File**: `diagnose_mcp_issues.py`
```python
#!/usr/bin/env python3
"""
MCP Server Diagnostic Script
Identifies and resolves startup issues
"""

import sys
import os
import logging
import psycopg2
import traceback
from pathlib import Path

def test_imports():
    """Test all required imports"""
    try:
        import asyncio
        import json
        import psutil
        import numpy as np
        import pandas as pd
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_postgresql_connection():
    """Test PostgreSQL connection"""
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

def test_pgvector_extension():
    """Test pgvector extension"""
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

def test_mcp_server_startup():
    """Test MCP server startup without PostgreSQL"""
    try:
        # Import MCP server without PostgreSQL initialization
        sys.path.append('.')
        from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
        
        # Create instance without PostgreSQL
        connector = SimpleLangFlowMCPConnector()
        print("✅ MCP server initialization successful (without PostgreSQL)")
        return True
    except Exception as e:
        print(f"❌ MCP server initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🔍 MCP Server Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("PostgreSQL Connection", test_postgresql_connection),
        ("pgvector Extension", test_pgvector_extension),
        ("MCP Server Startup", test_mcp_server_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Diagnostic Results:")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    failed_tests = [name for name, result in results if not result]
    if failed_tests:
        print(f"\n🚨 Issues found in: {', '.join(failed_tests)}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

#### 1.2 Create Minimal MCP Server
**File**: `mcp_server_minimal.py`
```python
#!/usr/bin/env python3
"""
Minimal MCP Server for Testing
Basic functionality without PostgreSQL integration
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalMCPConnector:
    """Minimal MCP connector with basic tools only"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "ping",
                "description": "Ping the system for connectivity",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_files",
                "description": "List files in directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list"
                        }
                    },
                    "required": ["directory"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
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
                arguments = params.get("arguments", {})
                
                result = await self.execute_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute tool calls"""
        try:
            if tool_name == "ping":
                return "pong"
            elif tool_name == "list_files":
                directory = arguments.get("directory", ".")
                if os.path.exists(directory) and os.path.isdir(directory):
                    files = os.listdir(directory)
                    return f"Files in {directory}: {', '.join(files[:10])}"
                else:
                    return f"Directory {directory} not found"
            else:
                return f"Tool {tool_name} not implemented"
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

async def main():
    """Main function"""
    connector = MinimalMCPConnector()
    
    # Read from stdin, write to stdout
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await connector.handle_request(request)
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: sys.stdout.write(json.dumps(response) + "\n")
            )
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
```

### Phase 2: Database Fixes (Day 2)

#### 2.1 Fix PostgreSQL Connection Issues
**Action**: Update connection parameters and error handling
**Method**: Modify `PostgreSQLVectorLLM` class with better error handling

#### 2.2 Fix pgvector Extension Issues
**Action**: Ensure pgvector extension is properly installed
**Method**: Create installation script for pgvector

#### 2.3 Fix Table Creation Issues
**Action**: Ensure all required tables are created properly
**Method**: Update table creation with better error handling

### Phase 3: Integration Testing (Day 3)

#### 3.1 Test Minimal Server
**Action**: Test minimal MCP server functionality
**Method**: Run minimal server and test basic tools

#### 3.2 Test with PostgreSQL
**Action**: Gradually add PostgreSQL functionality
**Method**: Add PostgreSQL features one by one

#### 3.3 Test Full Server
**Action**: Test complete MCP server
**Method**: Run full server with all features

## Rollback Strategy

### Immediate Rollback
**Action**: Revert to working MCP server version
**Method**: Use backup of working server
**Trigger**: If minimal server also fails

### Partial Rollback
**Action**: Disable PostgreSQL features temporarily
**Method**: Comment out PostgreSQL integration
**Trigger**: If PostgreSQL is the only issue

### Gradual Rollback
**Action**: Disable problematic tools one by one
**Method**: Identify and disable specific tools
**Trigger**: If specific tools cause issues

## Success Criteria

### Phase 1 Success
- [ ] Diagnostic script runs without errors
- [ ] All basic imports work
- [ ] Minimal MCP server starts successfully
- [ ] Basic tools (ping, list_files) work

### Phase 2 Success
- [ ] PostgreSQL connection works
- [ ] pgvector extension is available
- [ ] Database tables are created successfully
- [ ] No connection errors in logs

### Phase 3 Success
- [ ] Full MCP server starts successfully
- [ ] All 22 existing tools work
- [ ] No exit code: 1 errors
- [ ] Server runs stably for extended periods

## Monitoring and Validation

### Continuous Monitoring
- **Server Status**: Monitor server process status
- **Error Logs**: Track all error messages
- **Performance**: Monitor memory and CPU usage
- **Tool Functionality**: Test all tools regularly

### Validation Tests
- **Startup Test**: Server starts without errors
- **Tool Test**: All tools respond correctly
- **Stress Test**: Server handles multiple requests
- **Stability Test**: Server runs for extended periods

## Next Steps After Resolution

### Immediate Actions
1. **Document the Fix**: Record what caused the issue and how it was resolved
2. **Update Dependencies**: Ensure all required packages are properly documented
3. **Create Backup**: Create a working backup of the fixed server
4. **Test All Tools**: Verify all 22 existing tools work correctly

### Preparation for New Tools
1. **Validate System Stability**: Ensure system is stable before adding new tools
2. **Update Implementation Plan**: Adjust timeline based on resolution time
3. **Begin Phase 1**: Start implementing high-priority tools
4. **Monitor Performance**: Watch for any performance issues

## Risk Mitigation

### High-Risk Scenarios
1. **Database Unavailable**: Fallback to file-based storage
2. **Memory Issues**: Implement memory monitoring and limits
3. **Import Failures**: Create alternative implementations
4. **Service Dependencies**: Implement graceful degradation

### Contingency Plans
1. **Alternative Database**: Use SQLite if PostgreSQL fails
2. **Simplified Tools**: Create simplified versions of complex tools
3. **External Services**: Use external APIs as fallbacks
4. **Manual Processes**: Provide manual alternatives for critical functions

## Conclusion

This critical issue resolution plan provides a systematic approach to fixing the MCP server startup problems. The phased approach ensures that:

1. **Root cause is identified** through comprehensive diagnostics
2. **Minimal functionality is restored** quickly
3. **Full functionality is restored** systematically
4. **System stability is maintained** throughout the process

Once this critical issue is resolved, the implementation of the 59 new tools can proceed according to the main implementation plan. The resolution of this issue is the foundation for all future development work. 