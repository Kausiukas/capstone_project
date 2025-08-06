#!/usr/bin/env python3
"""
Test script to verify the quoted path fix
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_quoted_path_fix():
    """Test that quoted paths are handled correctly"""
    
    print("🧪 Testing quoted path fix...")
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test the problematic path format from LangFlow
    test_paths = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",
        "\"D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\"",
        "'D:\\GUI\\System-Reference-Clean\\LangFlow_Connect'"
    ]
    
    for i, path in enumerate(test_paths, 1):
        print(f"\n{i}️⃣ Testing path: '{path}'")
        
        try:
            result = await connector.handle_list_files({
                "directory": path,
                "batch_size": 5,
                "offset": 0,
                "max_depth": 1,
                "include_hidden": False
            })
            
            try:
                parsed = json.loads(result)
                total_files = parsed.get('summary', {}).get('total_files', 0)
                total_dirs = parsed.get('summary', {}).get('total_directories', 0)
                files_in_batch = len(parsed.get('batch', {}).get('files', []))
                
                print(f"   ✅ Success: {total_files} files, {total_dirs} directories")
                print(f"   📄 Files in batch: {files_in_batch}")
                
                if files_in_batch > 0:
                    print("   📋 First few files:")
                    for j, file in enumerate(parsed['batch']['files'][:3]):
                        file_type = "📁" if file.get('is_dir') else "📄"
                        print(f"      {j+1}. {file_type} {file.get('name', 'N/A')}")
                else:
                    print("   ❌ No files in batch")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Quoted path fix testing completed!")

if __name__ == "__main__":
    asyncio.run(test_quoted_path_fix()) 