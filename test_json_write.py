#!/usr/bin/env python3
"""
Test script to verify JSON output can be written to files without encoding issues
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the MCP connector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_json_write():
    """Test that JSON output can be written to files"""
    
    print("🧪 Testing JSON output file writing...")
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    # Test directory
    test_dir = "."
    
    print(f"\n📁 Testing directory: {test_dir}")
    
    # Test list_files and write to file
    print("\n1️⃣ Testing list_files -> write_file workflow:")
    try:
        # Get JSON output from list_files
        result = await connector.handle_list_files({
            "directory": test_dir,
            "batch_size": 10,
            "offset": 0,
            "max_depth": 1,
            "include_hidden": False
        })
        
        print(f"✅ list_files returned: {len(result)} characters")
        print(f"📄 First 200 chars: {result[:200]}...")
        
        # Try to parse as JSON to verify it's valid
        try:
            parsed = json.loads(result)
            print("✅ JSON is valid and parseable")
            print(f"📊 Summary: {parsed.get('summary', {}).get('total_files', 'N/A')} files")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            return
        
        # Write to file
        write_result = await connector.handle_write_file({
            "file_path": "test_directory_listing.json",
            "content": result
        })
        
        print(f"📝 Write result: {write_result}")
        
        # Verify file was written
        if os.path.exists("test_directory_listing.json"):
            file_size = os.path.getsize("test_directory_listing.json")
            print(f"✅ File written successfully: {file_size} bytes")
            
            # Read back and verify
            with open("test_directory_listing.json", 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ File read back successfully: {len(content)} characters")
                
                # Try to parse again
                try:
                    parsed_again = json.loads(content)
                    print("✅ File content is valid JSON")
                except json.JSONDecodeError as e:
                    print(f"❌ File content JSON parsing failed: {e}")
        else:
            print("❌ File was not created")
            
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
    
    # Test list_files_metadata_only and write to file
    print("\n2️⃣ Testing list_files_metadata_only -> write_file workflow:")
    try:
        # Get JSON output from list_files_metadata_only
        result = await connector.handle_list_files_metadata_only({
            "directory": test_dir,
            "batch_size": 10,
            "offset": 0,
            "max_depth": 1,
            "include_hidden": False
        })
        
        print(f"✅ list_files_metadata_only returned: {len(result)} characters")
        
        # Write to file
        write_result = await connector.handle_write_file({
            "file_path": "test_metadata_only.json",
            "content": result
        })
        
        print(f"📝 Write result: {write_result}")
        
        # Verify file was written
        if os.path.exists("test_metadata_only.json"):
            file_size = os.path.getsize("test_metadata_only.json")
            print(f"✅ File written successfully: {file_size} bytes")
        else:
            print("❌ File was not created")
            
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
    
    print("\n✅ JSON write testing completed!")

if __name__ == "__main__":
    asyncio.run(test_json_write()) 