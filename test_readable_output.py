#!/usr/bin/env python3
"""
Test script to verify the list_files_readable tool
"""

import asyncio
import sys
import os

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_readable_output():
    """Test the new list_files_readable tool"""
    
    print("🧪 Testing list_files_readable tool...")
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test directory
    test_dir = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"
    
    print(f"\n📁 Testing directory: {test_dir}")
    
    # Test with exact LangFlow parameters
    print("\n1️⃣ Testing list_files_readable:")
    try:
        result = await connector.handle_list_files_readable({
            "directory": test_dir,
            "batch_size": 5,  # Same as LangFlow
            "offset": 0,      # Same as LangFlow
            "max_depth": 1,   # Same as LangFlow
            "include_hidden": False
        })
        
        print("✅ list_files_readable returned:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error testing list_files_readable: {e}")
    
    print("\n✅ Readable output testing completed!")

if __name__ == "__main__":
    asyncio.run(test_readable_output()) 