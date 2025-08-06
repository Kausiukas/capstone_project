#!/usr/bin/env python3
"""
LangFlow Environment Diagnostic Script
=====================================

This script helps diagnose why file listing tools return "0 files" in LangFlow
when they work correctly locally.
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 40)

def check_working_directory():
    """Check current working directory and permissions"""
    print_section("Working Directory Analysis")
    
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    print(f"Directory exists: {os.path.exists(cwd)}")
    print(f"Directory is readable: {os.access(cwd, os.R_OK)}")
    print(f"Directory is writable: {os.access(cwd, os.W_OK)}")
    
    # Check if we're in the expected directory
    expected_dir = r"D:\GUI\System-Reference-Clean\LangFlow_Connect"
    if cwd == expected_dir:
        print("✅ Working directory matches expected path")
    else:
        print(f"⚠️  Working directory differs from expected: {expected_dir}")
    
    # List immediate contents
    try:
        items = os.listdir(cwd)
        print(f"📁 Items in current directory: {len(items)}")
        print(f"   Directories: {len([i for i in items if os.path.isdir(os.path.join(cwd, i))])}")
        print(f"   Files: {len([i for i in items if os.path.isfile(os.path.join(cwd, i))])}")
        
        # Show first few items
        print("   Sample items:")
        for i, item in enumerate(items[:10]):
            item_path = os.path.join(cwd, item)
            item_type = "📁" if os.path.isdir(item_path) else "📄"
            print(f"     {item_type} {item}")
        if len(items) > 10:
            print(f"     ... and {len(items) - 10} more")
            
    except PermissionError:
        print("❌ Permission denied accessing directory contents")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")

def check_python_environment():
    """Check Python environment details"""
    print_section("Python Environment")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check if running in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("ℹ️  Not running in virtual environment")

def check_mcp_server_process():
    """Check if MCP server is running and its environment"""
    print_section("MCP Server Process Check")
    
    try:
        # Check for Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            python_processes = [line for line in lines if line.strip()]
            
            print(f"🐍 Python processes running: {len(python_processes)}")
            
            for i, process in enumerate(python_processes[:5]):  # Show first 5
                print(f"   Process {i+1}: {process}")
            
            if len(python_processes) > 5:
                print(f"   ... and {len(python_processes) - 5} more")
        else:
            print("❌ Could not check Python processes")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def test_file_listing_directly():
    """Test file listing directly without MCP tools"""
    print_section("Direct File Listing Test")
    
    try:
        # Test with os.listdir
        items = os.listdir('.')
        files = [f for f in items if os.path.isfile(f)]
        dirs = [d for d in items if os.path.isdir(d)]
        
        print(f"📁 Direct os.listdir results:")
        print(f"   Total items: {len(items)}")
        print(f"   Files: {len(files)}")
        print(f"   Directories: {len(dirs)}")
        
        # Test with pathlib
        path = Path('.')
        path_files = list(path.iterdir())
        path_file_count = len([p for p in path_files if p.is_file()])
        path_dir_count = len([p for p in path_files if p.is_dir()])
        
        print(f"📁 Pathlib results:")
        print(f"   Total items: {len(path_files)}")
        print(f"   Files: {path_file_count}")
        print(f"   Directories: {path_dir_count}")
        
        # Test with glob
        glob_files = list(path.glob('*'))
        glob_file_count = len([p for p in glob_files if p.is_file()])
        glob_dir_count = len([p for p in glob_files if p.is_dir()])
        
        print(f"📁 Glob results:")
        print(f"   Total items: {len(glob_files)}")
        print(f"   Files: {glob_file_count}")
        print(f"   Directories: {glob_dir_count}")
        
    except Exception as e:
        print(f"❌ Error in direct file listing: {e}")

def test_optimized_file_lister():
    """Test the OptimizedFileLister class directly"""
    print_section("OptimizedFileLister Direct Test")
    
    try:
        # Import the class
        sys.path.append('.')
        from mcp_langflow_connector_simple import OptimizedFileLister
        
        # Create instance
        lister = OptimizedFileLister(max_memory_mb=25)
        
        # Test listing
        result = lister.get_batched_files(
            directory='.',
            batch_size=20,
            offset=0,
            max_depth=1,
            include_hidden=False
        )
        
        print(f"📊 OptimizedFileLister results:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Total files: {result.get('total_files', 0)}")
        print(f"   Total directories: {result.get('total_directories', 0)}")
        print(f"   Files in batch: {len(result.get('files', []))}")
        print(f"   Directories in batch: {len(result.get('directories', []))}")
        
        if result.get('success'):
            print("✅ OptimizedFileLister working correctly")
        else:
            print("❌ OptimizedFileLister failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Could not import OptimizedFileLister: {e}")
    except Exception as e:
        print(f"❌ Error testing OptimizedFileLister: {e}")

def check_langflow_connection():
    """Check LangFlow connection details"""
    print_section("LangFlow Connection Check")
    
    # Check if there are any MCP-related environment variables
    mcp_vars = {k: v for k, v in os.environ.items() if 'MCP' in k.upper()}
    
    if mcp_vars:
        print("🔧 MCP-related environment variables found:")
        for k, v in mcp_vars.items():
            print(f"   {k}: {v}")
    else:
        print("ℹ️  No MCP-related environment variables found")
    
    # Check for LangFlow-specific variables
    langflow_vars = {k: v for k, v in os.environ.items() if 'LANGFLOW' in k.upper()}
    
    if langflow_vars:
        print("🔧 LangFlow-related environment variables found:")
        for k, v in langflow_vars.items():
            print(f"   {k}: {v}")
    else:
        print("ℹ️  No LangFlow-related environment variables found")

def generate_recommendations():
    """Generate recommendations based on findings"""
    print_section("Recommendations")
    
    print("🔧 Based on the diagnostic results, here are potential solutions:")
    print()
    print("1. **Working Directory Issue**:")
    print("   - Ensure LangFlow is running the MCP server from the correct directory")
    print("   - Check if LangFlow changes the working directory when starting the server")
    print()
    print("2. **Permission Issues**:")
    print("   - Verify that the MCP server process has read permissions to the directory")
    print("   - Check Windows file permissions and security settings")
    print()
    print("3. **Python Environment**:")
    print("   - Ensure LangFlow uses the same Python environment as local tests")
    print("   - Check for virtual environment conflicts")
    print()
    print("4. **Process Isolation**:")
    print("   - LangFlow might be running the MCP server in a different context")
    print("   - Check if multiple MCP server instances are running")
    print()
    print("5. **Immediate Actions**:")
    print("   - Restart LangFlow completely")
    print("   - Restart the MCP server using start_mcp_server.py")
    print("   - Check LangFlow logs for any error messages")
    print("   - Try using absolute paths in the MCP server configuration")

def main():
    """Run the complete diagnostic"""
    print_header("LangFlow Environment Diagnostic")
    print("This script helps identify why file listing tools return '0 files' in LangFlow")
    print("when they work correctly in local testing.")
    
    check_working_directory()
    check_python_environment()
    check_mcp_server_process()
    test_file_listing_directly()
    test_optimized_file_lister()
    check_langflow_connection()
    generate_recommendations()
    
    print_header("Diagnostic Complete")
    print("Review the results above to identify the root cause of the issue.")
    print("The most likely causes are working directory differences or permission issues.")

if __name__ == "__main__":
    main() 