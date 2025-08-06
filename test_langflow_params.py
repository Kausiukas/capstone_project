#!/usr/bin/env python3
"""
Test script to verify MCP server with LangFlow parameters
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_langflow_params():
    """Test with exact LangFlow parameters"""
    
    print("🧪 Testing MCP server with LangFlow parameters...")
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test directory (same as LangFlow)
    test_dir = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"
    
    print(f"\n📁 Testing directory: {test_dir}")
    
    # Test with exact LangFlow parameters
    print("\n1️⃣ Testing list_files with LangFlow params:")
    try:
        result = await connector.handle_list_files({
            "directory": test_dir,
            "batch_size": 5,  # Same as LangFlow
            "offset": 0,      # Same as LangFlow
            "max_depth": 1,   # Same as LangFlow
            "include_hidden": False,
            "file_types": [],
            "sort_by": "name",
            "sort_order": "asc",
            "use_cache": True
        })
        
        print(f"✅ list_files returned: {len(result)} characters")
        print(f"📄 First 500 chars: {result[:500]}...")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(result)
            print("✅ JSON is valid and parseable")
            print(f"📊 Summary: {parsed.get('summary', {}).get('total_files', 'N/A')} files, {parsed.get('summary', {}).get('total_directories', 'N/A')} directories")
            print(f"📄 Files in batch: {len(parsed.get('batch', {}).get('files', []))}")
            
            # Show first few files
            files = parsed.get('batch', {}).get('files', [])
            if files:
                print("\n📋 First few files:")
                for i, file in enumerate(files[:3]):
                    print(f"  {i+1}. {file.get('name', 'N/A')} ({'dir' if file.get('is_dir') else 'file'})")
            else:
                print("❌ No files found in batch")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
    except Exception as e:
        print(f"❌ Error testing list_files: {e}")
    
    # Test with current directory
    print("\n2️⃣ Testing list_files with current directory:")
    try:
        result = await connector.handle_list_files({
            "directory": ".",
            "batch_size": 5,
            "offset": 0,
            "max_depth": 1,
            "include_hidden": False,
            "file_types": [],
            "sort_by": "name",
            "sort_order": "asc",
            "use_cache": True
        })
        
        try:
            parsed = json.loads(result)
            print(f"📊 Current dir summary: {parsed.get('summary', {}).get('total_files', 'N/A')} files, {parsed.get('summary', {}).get('total_directories', 'N/A')} directories")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
    except Exception as e:
        print(f"❌ Error testing current directory: {e}")
    
    print("\n✅ LangFlow parameters testing completed!")

if __name__ == "__main__":
    asyncio.run(test_langflow_params()) 