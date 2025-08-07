#!/usr/bin/env python3
"""
Content Preview System Test
Test script for the content preview functionality
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, params: dict = None):
    """Make API request with error handling"""
    try:
        headers = {"X-API-Key": API_KEY}
        
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def test_supported_types():
    """Test getting supported file types"""
    print("🔍 Testing supported file types...")
    result = make_api_request("/preview/supported-types")
    
    if "error" not in result:
        print("✅ Supported types retrieved successfully!")
        supported_types = result.get("supported_types", {})
        
        for preview_type, config in supported_types.items():
            print(f"📁 {preview_type.title()}:")
            print(f"   Extensions: {', '.join(config.get('extensions', [])[:5])}...")
            print(f"   MIME Types: {', '.join(config.get('mime_types', [])[:3])}...")
        return True
    else:
        print(f"❌ Failed to get supported types: {result['error']}")
        return False

def test_file_analysis():
    """Test file analysis functionality"""
    print("\n🔍 Testing file analysis...")
    
    test_files = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_enhanced_tools.py",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\config\\langflow_config.py"
    ]
    
    success_count = 0
    for file_path in test_files:
        print(f"📄 Analyzing: {Path(file_path).name}")
        result = make_api_request("/preview/analyze", params={"file_path": file_path})
        
        if "error" not in result:
            print(f"✅ {Path(file_path).name}:")
            print(f"   Type: {result.get('preview_type', 'Unknown')}")
            print(f"   Language: {result.get('language', 'None')}")
            print(f"   Supported: {result.get('supported', False)}")
            success_count += 1
        else:
            print(f"❌ {Path(file_path).name}: {result['error']}")
    
    print(f"\n📊 Analysis Results: {success_count}/{len(test_files)} successful")
    return success_count == len(test_files)

def test_single_preview():
    """Test single file preview"""
    print("\n👁️ Testing single file preview...")
    
    test_file = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_enhanced_tools.py"
    print(f"📄 Previewing: {Path(test_file).name}")
    
    result = make_api_request("/preview/file", params={"file_path": test_file})
    
    if "error" not in result:
        print(f"✅ Preview successful!")
        print(f"   Type: {result.get('file_type', 'Unknown')}")
        print(f"   Language: {result.get('language', 'None')}")
        print(f"   Content Length: {result.get('content_length', 0):,} chars")
        print(f"   Has Preview HTML: {'Yes' if result.get('preview_html') else 'No'}")
        return True
    else:
        print(f"❌ Preview failed: {result['error']}")
        return False

def test_batch_preview():
    """Test batch file preview"""
    print("\n📦 Testing batch preview...")
    
    test_files = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_enhanced_tools.py",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\config\\langflow_config.py"
    ]
    
    result = make_api_request("/preview/batch", method="POST", data={"file_paths": test_files})
    
    if "error" not in result:
        print(f"✅ Batch preview successful!")
        print(f"   Total Files: {result.get('total_files', 0)}")
        print(f"   Successful: {result.get('successful_previews', 0)}")
        
        results = result.get("results", [])
        for file_result in results:
            file_path = file_result.get('file_path', 'Unknown')
            if file_result.get("success"):
                print(f"   ✅ {Path(file_path).name}: {file_result.get('file_type', 'Unknown')}")
            else:
                print(f"   ❌ {Path(file_path).name}: {file_result.get('error', 'Unknown error')}")
        
        return result.get('successful_previews', 0) == len(test_files)
    else:
        print(f"❌ Batch preview failed: {result['error']}")
        return False

def test_different_file_types():
    """Test different file types"""
    print("\n🎨 Testing different file types...")
    
    test_cases = [
        {
            "name": "Python Code",
            "file": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_enhanced_tools.py",
            "expected_type": "code",
            "expected_language": "python"
        },
        {
            "name": "Markdown",
            "file": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md",
            "expected_type": "code",
            "expected_language": "markdown"
        },
        {
            "name": "Configuration",
            "file": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\config\\langflow_config.py",
            "expected_type": "code",
            "expected_language": "python"
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"📄 Testing {test_case['name']}: {Path(test_case['file']).name}")
        result = make_api_request("/preview/file", params={"file_path": test_case['file']})
        
        if "error" not in result:
            actual_type = result.get('file_type', 'Unknown')
            actual_language = result.get('language', 'None')
            
            type_match = actual_type == test_case['expected_type']
            language_match = actual_language == test_case['expected_language']
            
            if type_match and language_match:
                print(f"✅ {test_case['name']}: Type={actual_type}, Language={actual_language}")
                success_count += 1
            else:
                print(f"⚠️ {test_case['name']}: Expected ({test_case['expected_type']}, {test_case['expected_language']}), Got ({actual_type}, {actual_language})")
        else:
            print(f"❌ {test_case['name']}: {result['error']}")
    
    print(f"\n📊 File Type Results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_preview_with_type_override():
    """Test preview with type override"""
    print("\n🎛️ Testing preview with type override...")
    
    test_file = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md"
    
    # Test with auto-detect
    print("📄 Testing auto-detect...")
    result1 = make_api_request("/preview/file", params={"file_path": test_file})
    
    # Test with explicit type
    print("📄 Testing explicit type...")
    result2 = make_api_request("/preview/file", params={"file_path": test_file, "preview_type": "code"})
    
    if "error" not in result1 and "error" not in result2:
        print(f"✅ Both previews successful!")
        print(f"   Auto-detect: {result1.get('file_type', 'Unknown')}")
        print(f"   Explicit: {result2.get('file_type', 'Unknown')}")
        return True
    else:
        print(f"❌ Preview override failed")
        if "error" in result1:
            print(f"   Auto-detect error: {result1['error']}")
        if "error" in result2:
            print(f"   Explicit error: {result2['error']}")
        return False

def main():
    """Run all content preview tests"""
    print("🚀 Content Preview System Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run tests
    tests = [
        ("Supported Types", test_supported_types),
        ("File Analysis", test_file_analysis),
        ("Single Preview", test_single_preview),
        ("Batch Preview", test_batch_preview),
        ("Different File Types", test_different_file_types),
        ("Type Override", test_preview_with_type_override)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    print(f"⏱️ Total Time: {time.time() - start_time:.2f} seconds")
    
    if passed == total:
        print("🎉 All tests passed! Content Preview System is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()
