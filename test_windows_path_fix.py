#!/usr/bin/env python3
"""
Test script to verify Windows path handling fix
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_enhanced_tools import PathResolver

def test_windows_path_detection():
    """Test Windows path detection"""
    print("Testing Windows path detection...")
    
    # Test cases
    test_paths = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\add_security_headers.py",
        "C:\\Users\\User\\Documents\\file.txt",
        "D:/GUI/System-Reference-Clean/LangFlow_Connect/add_security_headers.py",  # Mixed separators
        "/opt/render/project/src/file.py",  # Linux path
        "relative/path/file.txt",  # Relative path
        "https://github.com/user/repo",  # GitHub URL
        "http://example.com/file.txt"  # HTTP URL
    ]
    
    for path in test_paths:
        source_type = PathResolver.detect_source_type(path)
        print(f"Path: {path}")
        print(f"  Detected as: {source_type}")
        
        if source_type == 'local_absolute':
            try:
                path_info = PathResolver.resolve_path(path)
                print(f"  Resolved path: {path_info['path']}")
                print(f"  Exists: {path_info.get('exists', False)}")
                if 'original_windows_path' in path_info:
                    print(f"  Original Windows path: {path_info['original_windows_path']}")
            except Exception as e:
                print(f"  Error: {e}")
        
        print()

def test_path_conversion():
    """Test Windows to Linux path conversion"""
    print("Testing Windows to Linux path conversion...")
    
    windows_path = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\add_security_headers.py"
    
    # Manual conversion (same as in the code)
    linux_path = windows_path.replace('\\', '/').split(':', 1)[1]
    if linux_path.startswith('/'):
        linux_path = linux_path[1:]
    
    print(f"Windows path: {windows_path}")
    print(f"Converted to: {linux_path}")
    print(f"Expected Render path: /opt/render/project/{linux_path}")
    print()

if __name__ == "__main__":
    test_windows_path_detection()
    test_path_conversion()
