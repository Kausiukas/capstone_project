#!/usr/bin/env python3
"""
Test script to verify JSON output from file listing tools
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_json_output():
    """Test that file listing tools return valid JSON"""
    
    print("🧪 Testing JSON output from file listing tools...")
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test directory
    test_dir = "."
    
    print(f"\n📁 Testing directory: {test_dir}")
    
    # Test list_files
    print("\n1️⃣ Testing list_files tool:")
    try:
        result = await connector.handle_list_files({
            "directory": test_dir,
            "batch_size": 10,
            "offset": 0,
            "max_depth": 1,
            "include_hidden": False
        })
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            print("✅ list_files returned valid JSON")
            print(f"📊 Summary: {parsed.get('summary', {}).get('total_files', 'N/A')} files, {parsed.get('summary', {}).get('total_directories', 'N/A')} directories")
            print(f"📄 Files in batch: {len(parsed.get('batch', {}).get('files', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ list_files did not return valid JSON: {e}")
            print(f"Raw output: {result[:200]}...")
            
    except Exception as e:
        print(f"❌ Error testing list_files: {e}")
    
    # Test list_files_metadata_only
    print("\n2️⃣ Testing list_files_metadata_only tool:")
    try:
        result = await connector.handle_list_files_metadata_only({
            "directory": test_dir,
            "batch_size": 10,
            "offset": 0,
            "max_depth": 1,
            "include_hidden": False
        })
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            print("✅ list_files_metadata_only returned valid JSON")
            print(f"📊 Summary: {parsed.get('summary', {}).get('total_files', 'N/A')} files, {parsed.get('summary', {}).get('total_directories', 'N/A')} directories")
            print(f"📄 Files in batch: {len(parsed.get('batch', {}).get('files', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ list_files_metadata_only did not return valid JSON: {e}")
            print(f"Raw output: {result[:200]}...")
            
    except Exception as e:
        print(f"❌ Error testing list_files_metadata_only: {e}")
    
    # Test stream_files
    print("\n3️⃣ Testing stream_files tool:")
    try:
        result = await connector.handle_stream_files({
            "directory": test_dir,
            "action": "start",
            "max_depth": 1,
            "include_hidden": False
        })
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            print("✅ stream_files returned valid JSON")
            print(f"🔄 Action: {parsed.get('action', 'N/A')}")
            print(f"📋 Stream ID: {parsed.get('stream_id', 'N/A')}")
            if 'batch' in parsed:
                print(f"📄 Files in batch: {len(parsed['batch'].get('files', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ stream_files did not return valid JSON: {e}")
            print(f"Raw output: {result[:200]}...")
            
    except Exception as e:
        print(f"❌ Error testing stream_files: {e}")
    
    print("\n✅ JSON output testing completed!")

if __name__ == "__main__":
    asyncio.run(test_json_output()) 