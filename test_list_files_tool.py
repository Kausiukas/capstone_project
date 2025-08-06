#!/usr/bin/env python3
"""
Test script for the updated list_files tool in mcp_langflow_connector_simple.py
Tests the metadata-only file listing functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_list_files_tool():
    """Test the list_files tool functionality"""
    
    print("🧪 Testing list_files tool - Metadata Only")
    print("=" * 50)
    
    # Initialize the MCP connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test cases
    test_cases = [
        {
            "name": "Current Directory (Default)",
            "args": {"directory": "."}
        },
        {
            "name": "Src Directory",
            "args": {"directory": "src"}
        },
        {
            "name": "Small Batch Size",
            "args": {"directory": ".", "batch_size": 5}
        },
        {
            "name": "With File Type Filter",
            "args": {"directory": ".", "file_types": [".py"]}
        },
        {
            "name": "Include Hidden Files",
            "args": {"directory": ".", "include_hidden": True}
        },
        {
            "name": "Sort by Size",
            "args": {"directory": ".", "sort_by": "size", "sort_order": "desc"}
        },
        {
            "name": "Deeper Directory Scan",
            "args": {"directory": ".", "max_depth": 2}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Execute the list_files tool
            result = await connector.handle_list_files(test_case['args'])
            
            # Display the result
            print(result)
            
            # Basic validation
            if "Error:" in result:
                print(f"❌ Test {i} failed with error")
            else:
                print(f"✅ Test {i} completed successfully")
                
        except Exception as e:
            print(f"❌ Test {i} failed with exception: {str(e)}")
        
        print()

async def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 30)
    
    connector = SimpleLangFlowMCPConnector()
    
    edge_cases = [
        {
            "name": "Non-existent Directory",
            "args": {"directory": "non_existent_dir"}
        },
        {
            "name": "Empty Directory",
            "args": {"directory": "temp"}  # Assuming temp directory exists
        },
        {
            "name": "Very Large Batch Size",
            "args": {"directory": ".", "batch_size": 100}
        },
        {
            "name": "Invalid File Types",
            "args": {"directory": ".", "file_types": [".xyz", ".invalid"]}
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n🔍 Edge Case {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = await connector.handle_list_files(test_case['args'])
            print(result)
            
            if "Error:" in result:
                print(f"⚠️ Expected error handled correctly")
            else:
                print(f"✅ Edge case handled successfully")
                
        except Exception as e:
            print(f"❌ Edge case failed with exception: {str(e)}")
        
        print()

async def test_performance():
    """Test performance with different directory sizes"""
    
    print("\n⚡ Performance Testing")
    print("=" * 25)
    
    connector = SimpleLangFlowMCPConnector()
    
    # Test with different directories
    performance_tests = [
        {
            "name": "Root Directory (Large)",
            "args": {"directory": ".", "batch_size": 10}
        },
        {
            "name": "Src Directory (Medium)",
            "args": {"directory": "src", "batch_size": 15}
        },
        {
            "name": "Small Directory",
            "args": {"directory": "config", "batch_size": 20}
        }
    ]
    
    for i, test_case in enumerate(performance_tests, 1):
        print(f"\n⚡ Performance Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            import time
            start_time = time.time()
            
            result = await connector.handle_list_files(test_case['args'])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"⏱️ Execution time: {execution_time:.3f} seconds")
            print(f"📊 Result length: {len(result)} characters")
            
            # Show first 200 characters of result
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"📋 Preview:\n{preview}")
            
            if execution_time < 1.0:
                print(f"✅ Performance test {i} passed (fast execution)")
            else:
                print(f"⚠️ Performance test {i} slow ({execution_time:.3f}s)")
                
        except Exception as e:
            print(f"❌ Performance test {i} failed: {str(e)}")
        
        print()

async def main():
    """Main test function"""
    
    print("🚀 Starting list_files Tool Testing")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("mcp_langflow_connector_simple.py"):
        print("❌ Error: mcp_langflow_connector_simple.py not found in current directory")
        print("Please run this test from the LangFlow_Connect directory")
        return
    
    # Run all tests
    await test_list_files_tool()
    await test_edge_cases()
    await test_performance()
    
    print("\n🎉 Testing Complete!")
    print("=" * 25)
    print("✅ All tests completed. Check the results above.")
    print("📝 If all tests pass, the tool is ready for LangFlow platform testing.")

if __name__ == "__main__":
    asyncio.run(main()) 