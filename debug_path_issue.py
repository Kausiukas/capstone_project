#!/usr/bin/env python3
"""
Debug script to test directory path resolution
"""

import os
from pathlib import Path

def test_directory_path():
    """Test different directory path formats"""
    
    print("🔍 Testing directory path resolution...")
    
    # Test the exact path from LangFlow output
    test_paths = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",
        "\"D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\"",
        "D:/GUI/System-Reference-Clean/LangFlow_Connect",
        ".",
        os.getcwd()
    ]
    
    for i, path in enumerate(test_paths, 1):
        print(f"\n{i}️⃣ Testing path: '{path}'")
        
        try:
            # Test if path exists
            path_obj = Path(path)
            exists = path_obj.exists()
            print(f"   ✅ Path exists: {exists}")
            
            if exists:
                # Test if it's a directory
                is_dir = path_obj.is_dir()
                print(f"   📁 Is directory: {is_dir}")
                
                if is_dir:
                    # Try to list contents
                    try:
                        items = list(path_obj.iterdir())
                        print(f"   📋 Items found: {len(items)}")
                        
                        # Show first few items
                        for j, item in enumerate(items[:5]):
                            item_type = "📁" if item.is_dir() else "📄"
                            print(f"      {j+1}. {item_type} {item.name}")
                            
                    except PermissionError:
                        print("   ❌ Permission denied")
                    except Exception as e:
                        print(f"   ❌ Error listing: {e}")
                else:
                    print("   ❌ Not a directory")
            else:
                print("   ❌ Path does not exist")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_directory_path() 