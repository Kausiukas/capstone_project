#!/usr/bin/env python3
"""
Simple test for content preview system
"""

import requests
import json

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def test_simple_preview():
    """Test content preview with simple file paths"""
    headers = {"X-API-Key": API_KEY}
    
    # Test with a simple file path
    test_files = [
        "README.md",
        "src/mcp_server_enhanced_tools.py",
        "config/langflow_config.py"
    ]
    
    for file_path in test_files:
        print(f"\n🔍 Testing: {file_path}")
        
        # Test analysis
        try:
            params = {"file_path": file_path}
            response = requests.get(f"{API_BASE_URL}/preview/analyze", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis successful:")
                print(f"   Type: {data.get('preview_type', 'Unknown')}")
                print(f"   Language: {data.get('language', 'None')}")
                print(f"   Supported: {data.get('supported', False)}")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Analysis error: {e}")
        
        # Test preview
        try:
            params = {"file_path": file_path}
            response = requests.get(f"{API_BASE_URL}/preview/file", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Preview successful:")
                print(f"   Type: {data.get('file_type', 'Unknown')}")
                print(f"   Language: {data.get('language', 'None')}")
                print(f"   Content Length: {data.get('content_length', 0):,} chars")
                print(f"   Has Preview HTML: {'Yes' if data.get('preview_html') else 'No'}")
            else:
                print(f"❌ Preview failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Preview error: {e}")

def main():
    print("🚀 Simple Content Preview Test")
    print("=" * 40)
    test_simple_preview()

if __name__ == "__main__":
    main()
