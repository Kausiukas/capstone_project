#!/usr/bin/env python3
"""
Debug content preview error
"""

import requests
import json

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def debug_preview_error():
    """Debug the content preview error"""
    headers = {"X-API-Key": API_KEY}
    
    # Test with a simple file path
    test_file = "README.md"
    
    print(f"🔍 Debugging preview error for: {test_file}")
    
    # Test analyze endpoint with detailed error
    try:
        params = {"file_path": test_file}
        response = requests.get(f"{API_BASE_URL}/preview/analyze", headers=headers, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis successful: {data}")
        else:
            print(f"❌ Analysis failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test preview endpoint with detailed error
    try:
        params = {"file_path": test_file}
        response = requests.get(f"{API_BASE_URL}/preview/file", headers=headers, params=params, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preview successful: {data}")
        else:
            print(f"❌ Preview failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Preview error: {e}")

def main():
    print("🚀 Debug Content Preview Error")
    print("=" * 40)
    debug_preview_error()

if __name__ == "__main__":
    main()
