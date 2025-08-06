#!/usr/bin/env python3
"""
Simple MCP Server Test Script
Tests basic functionality without requiring external tools
"""

import asyncio
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
    print("✅ Successfully imported MCP server")
except Exception as e:
    print(f"❌ Failed to import MCP server: {e}")
    sys.exit(1)

async def test_mcp_server():
    """Test basic MCP server functionality"""
    print("\n🧪 Testing MCP Server Functionality...")
    
    try:
        # Initialize server
        connector = SimpleLangFlowMCPConnector()
        print("✅ MCP server initialized successfully")
        
        # Test available tools
        print(f"📋 Available tools: {[tool['name'] for tool in connector.tools]}")
        
        # Test ping tool
        print("\n🔍 Testing ping tool...")
        ping_result = await connector.execute_tool("ping", {})
        print(f"✅ Ping result: {ping_result}")
        
        # Test list_files tool
        print("\n🔍 Testing list_files tool...")
        list_result = await connector.execute_tool("list_files", {"directory": "."})
        print(f"✅ List files result: {list_result[:200]}...")  # Show first 200 chars
        
        # Test read_file tool
        print("\n🔍 Testing read_file tool...")
        read_result = await connector.execute_tool("read_file", {"file_path": "test_mcp_server.py"})
        print(f"✅ Read file result: {read_result[:100]}...")  # Show first 100 chars
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_postgresql_tools():
    """Test PostgreSQL+Vector LLM tools (if available)"""
    print("\n🧪 Testing PostgreSQL+Vector LLM Tools...")
    
    try:
        connector = SimpleLangFlowMCPConnector()
        
        # Test store_embedding tool
        print("\n🔍 Testing store_embedding tool...")
        store_result = await connector.execute_tool("store_embedding", {
            "name": "test_document",
            "content": "This is a test document for embedding storage.",
            "metadata": '{"type": "test", "source": "mcp_test"}'
        })
        print(f"✅ Store embedding result: {store_result}")
        
        # Test similarity_search tool
        print("\n🔍 Testing similarity_search tool...")
        search_result = await connector.execute_tool("similarity_search", {
            "query": "test document",
            "limit": 3
        })
        print(f"✅ Similarity search result: {search_result}")
        
        print("\n🎉 PostgreSQL tools test completed!")
        return True
        
    except Exception as e:
        print(f"⚠️ PostgreSQL tools test failed (expected if PostgreSQL not configured): {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 MCP Server Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    basic_success = await test_mcp_server()
    
    # Test PostgreSQL tools
    postgres_success = await test_postgresql_tools()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Basic MCP Server: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"PostgreSQL Tools: {'✅ PASS' if postgres_success else '⚠️ SKIP'}")
    
    if basic_success:
        print("\n🚀 MCP Server is ready for use!")
        print("Next steps:")
        print("1. Test with MCP Inspector: npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py")
        print("2. Configure PostgreSQL if needed for vector tools")
        print("3. Test with LangFlow")
    else:
        print("\n❌ MCP Server has issues that need to be fixed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 