#!/usr/bin/env python3
"""
Debug script to test the file_generator method
"""

import os
import sys
from pathlib import Path

# Add current directory to path to import the class
sys.path.append('.')

from mcp_langflow_connector_simple import OptimizedFileLister

def test_file_generator():
    """Test the file_generator method directly"""
    print("🔍 Testing file_generator method...")
    
    # Create instance
    lister = OptimizedFileLister(max_memory_mb=25)
    
    # Test with current directory
    directory = "."
    print(f"📁 Testing directory: {directory}")
    print(f"📁 Absolute path: {os.path.abspath(directory)}")
    
    # Test the file_generator directly
    file_count = 0
    dir_count = 0
    
    print("\n📋 Generated files and directories:")
    for entry in lister.file_generator(directory, max_depth=1, include_hidden=False):
        if "error" in entry:
            print(f"❌ Error: {entry['error']}")
            break
        
        if entry["is_file"]:
            file_count += 1
            print(f"   📄 {entry['name']} ({entry['path']})")
        else:
            dir_count += 1
            print(f"   📁 {entry['name']} ({entry['path']})")
    
    print(f"\n📊 Summary:")
    print(f"   Files found: {file_count}")
    print(f"   Directories found: {dir_count}")
    print(f"   Total items: {file_count + dir_count}")

def test_os_walk():
    """Test os.walk directly to compare"""
    print("\n🔍 Testing os.walk directly...")
    
    directory = "."
    file_count = 0
    dir_count = 0
    
    print(f"📁 Testing directory: {directory}")
    print(f"📁 Absolute path: {os.path.abspath(directory)}")
    
    for root, dirs, files in os.walk(directory):
        # Calculate depth
        depth = root.replace(directory, '').count(os.sep)
        print(f"   📁 Root: {root}, Depth: {depth}")
        
        if depth > 1:  # This is the issue!
            print(f"   ⚠️  Skipping due to depth > 1")
            continue
        
        # Filter hidden
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.')]
        
        for file in files:
            file_count += 1
            print(f"      📄 {file}")
        
        for dir_name in dirs:
            dir_count += 1
            print(f"      📁 {dir_name}")
    
    print(f"\n📊 os.walk Summary:")
    print(f"   Files found: {file_count}")
    print(f"   Directories found: {dir_count}")
    print(f"   Total items: {file_count + dir_count}")

def test_simple_listdir():
    """Test simple os.listdir for comparison"""
    print("\n🔍 Testing os.listdir directly...")
    
    directory = "."
    items = os.listdir(directory)
    
    files = [f for f in items if os.path.isfile(f)]
    dirs = [d for d in items if os.path.isdir(d)]
    
    print(f"📁 Directory: {directory}")
    print(f"📊 Total items: {len(items)}")
    print(f"📄 Files: {len(files)}")
    print(f"📁 Directories: {len(dirs)}")
    
    print("\n📋 Sample items:")
    for item in items[:10]:
        item_type = "📁" if os.path.isdir(item) else "📄"
        print(f"   {item_type} {item}")

if __name__ == "__main__":
    test_simple_listdir()
    test_os_walk()
    test_file_generator() 