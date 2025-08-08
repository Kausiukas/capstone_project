#!/usr/bin/env python3
"""
Check server status and test content preview endpoints
"""

import requests
import json

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def check_server_status():
    """Check if the server is running and accessible"""
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{API_BASE_URL}/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_content_preview_endpoints():
    """Test content preview endpoints"""
    headers = {"X-API-Key": API_KEY}
    
    # Test supported types endpoint
    print("\n🔍 Testing /preview/supported-types...")
    try:
        response = requests.get(f"{API_BASE_URL}/preview/supported-types", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Supported types endpoint working")
        else:
            print(f"❌ Supported types endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Supported types endpoint error: {e}")
    
    # Test file analysis endpoint
    print("\n🔍 Testing /preview/analyze...")
    try:
        params = {"file_path": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md"}
        response = requests.get(f"{API_BASE_URL}/preview/analyze", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ File analysis endpoint working")
        else:
            print(f"❌ File analysis endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ File analysis endpoint error: {e}")

def main():
    print("🚀 Checking server status...")
    
    if check_server_status():
        test_content_preview_endpoints()
    else:
        print("\n⚠️ Server is not accessible. Please wait for deployment to complete.")

if __name__ == "__main__":
    main()
