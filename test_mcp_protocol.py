#!/usr/bin/env python3
"""
Test MCP Protocol Communication with LangFlow Connector
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_protocol():
    """Test MCP protocol communication"""
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, "mcp_langflow_connector.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Test 1: Initialize
        print("Testing MCP initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialization request
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Init response: {response.strip()}")
        
        # Test 2: List tools
        print("\nTesting tool listing...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        # Send tools request
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Tools response: {response.strip()}")
        
        # Test 3: Call a tool
        print("\nTesting tool execution...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_files",
                "arguments": {
                    "directory": "."
                }
            }
        }
        
        # Send call request
        process.stdin.write(json.dumps(call_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Call response: {response.strip()}")
        
        print("\nMCP Protocol test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing MCP protocol: {e}")
        return False
    
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_protocol())
    sys.exit(0 if success else 1) 