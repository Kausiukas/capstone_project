#!/usr/bin/env python3
"""
Test script to verify the new get_pagination_info and append_file tools
"""

import asyncio
import sys
import os

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_new_tools():
    """Test the new get_pagination_info and append_file tools"""

    print("🧪 Testing new tools: get_pagination_info and append_file...")

    # Initialize connector
    connector = SimpleLangFlowMCPConnector()

    # Test directory
    test_dir = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"

    print(f"\n📁 Testing directory: {test_dir}")

    # Test 1: get_pagination_info
    print("\n1️⃣ Testing get_pagination_info:")
    try:
        result = await connector.handle_get_pagination_info({
            "directory": test_dir,
            "batch_size": 10,  # Small batch for testing
            "max_depth": 1,
            "include_hidden": False
        })

        print("✅ get_pagination_info returned:")
        print("=" * 80)
        print(result)
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error testing get_pagination_info: {e}")

    # Test 2: append_file
    print("\n2️⃣ Testing append_file:")
    try:
        # First, create a test file
        test_file = "test_append.txt"
        initial_content = "This is the initial content.\n"
        
        # Write initial content
        write_result = await connector.handle_write_file({
            "file_path": test_file,
            "content": initial_content
        })
        print(f"📝 Write result: {write_result}")

        # Append content
        append_content = "This is appended content.\nAnd another line."
        append_result = await connector.handle_append_file({
            "file_path": test_file,
            "content": append_content,
            "separator": "\n---\n"
        })
        print(f"📝 Append result: {append_result}")

        # Read the final file
        read_result = await connector.handle_read_file({
            "file_path": test_file
        })
        print(f"📖 Final file content:\n{read_result}")

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 Cleaned up {test_file}")

    except Exception as e:
        print(f"❌ Error testing append_file: {e}")

    print("\n✅ New tools testing completed!")

if __name__ == "__main__":
    asyncio.run(test_new_tools()) 