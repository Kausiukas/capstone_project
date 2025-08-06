#!/usr/bin/env python3
"""
Test script for the LangFlow MCP Connector
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_connector():
    """Test the MCP connector functionality"""
    try:
        from mcp_langflow_connector import LangFlowMCPConnector
        
        # Create connector instance
        connector = LangFlowMCPConnector()
        
        # Test initialization
        print("Testing connector initialization...")
        await connector.initialize_components()
        
        # Test tool listing
        print("\nTesting tool listing...")
        tools = connector.tools
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test a simple tool execution
        print("\nTesting file listing...")
        result = await connector.execute_tool("list_files", {"directory": "."})
        print(f"Result: {result[:200]}...")  # Show first 200 chars
        
        print("\nConnector test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing connector: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connector())
    sys.exit(0 if success else 1) 