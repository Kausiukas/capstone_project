#!/usr/bin/env python3
"""
Test script to check Render API and directory structure
"""

import requests
import json

API_BASE = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_debug_directory():
    """Test debug directory structure endpoint"""
    try:
        response = requests.get(f"{API_BASE}/debug/directory-structure")
        print(f"Debug directory: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Debug directory failed: {e}")
        return False

def test_list_files(directory):
    """Test list_files tool"""
    try:
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "name": "list_files",
            "arguments": {"directory": directory}
        }
        
        response = requests.post(f"{API_BASE}/api/v1/tools/call", 
                               headers=headers, 
                               json=data)
        print(f"list_files '{directory}': {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"list_files failed: {e}")
        return False

def main():
    print("Testing Render API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("Health check failed, stopping tests")
        return
    
    print("\n" + "=" * 50)
    
    # Test debug directory
    test_debug_directory()
    
    print("\n" + "=" * 50)
    
    # Test list_files with different paths
    test_paths = [
        ".",  # Current directory
        "/opt/render/project",  # Project root
        "src",  # Source directory
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",  # Windows path
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\add_security_headers.py"  # Windows file path
    ]
    
    for path in test_paths:
        print(f"\nTesting path: {path}")
        test_list_files(path)
        print("-" * 30)

if __name__ == "__main__":
    main()
