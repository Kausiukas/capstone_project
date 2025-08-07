#!/usr/bin/env python3
"""
Test script for Performance Monitoring System
"""

import requests
import json
import time
import random

API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def test_performance_endpoints():
    """Test all performance monitoring endpoints"""
    print("🧪 Testing Performance Monitoring System...")
    print("=" * 60)
    
    headers = {"X-API-Key": API_KEY}
    
    # Test 1: Performance Metrics
    print("\n1️⃣ Testing Performance Metrics Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/performance/metrics", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   📊 Metrics available: {len(data.get('metrics', {}))} items")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Performance Alerts
    print("\n2️⃣ Testing Performance Alerts Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/performance/alerts", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   🚨 Alerts: {data.get('alert_count', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Performance Dashboard
    print("\n3️⃣ Testing Performance Dashboard Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/performance/dashboard", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            dashboard = data.get('dashboard', {})
            overview = dashboard.get('overview', {})
            print(f"   📈 Total Requests: {overview.get('total_requests', 0)}")
            print(f"   ✅ Success Rate: {overview.get('overall_success_rate', 0):.1f}%")
            print(f"   🖥️ System Health: {overview.get('system_health', 'unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Performance Health
    print("\n4️⃣ Testing Performance Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/performance/health", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            health = data.get('health', {})
            print(f"   🏥 Health Status: {health.get('status', 'unknown')}")
            print(f"   🚨 Total Alerts: {health.get('alerts_count', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def generate_test_load():
    """Generate test load to populate performance metrics"""
    print("\n🔄 Generating Test Load...")
    print("=" * 60)
    
    headers = {"X-API-Key": API_KEY}
    
    # Test tools to call
    test_tools = [
        {"name": "ping", "arguments": {}},
        {"name": "get_system_status", "arguments": {}},
        {"name": "list_files", "arguments": {"directory": "."}},
        {"name": "read_file", "arguments": {"file_path": "README.md"}},
        {"name": "analyze_code", "arguments": {"file_path": "src/mcp_server_enhanced_tools.py"}}
    ]
    
    for i in range(5):  # Generate 5 test requests
        tool = random.choice(test_tools)
        print(f"   Testing {tool['name']}...")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/tools/call",
                headers=headers,
                json=tool,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ {tool['name']} - Success")
                # Check performance headers
                response_time = response.headers.get('X-Response-Time', 'N/A')
                success = response.headers.get('X-Request-Success', 'N/A')
                print(f"   ⏱️ Response Time: {response_time}")
                print(f"   ✅ Success: {success}")
            else:
                print(f"   ❌ {tool['name']} - Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {tool['name']} - Exception: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_specific_tool_metrics():
    """Test metrics for specific tools"""
    print("\n🔍 Testing Specific Tool Metrics...")
    print("=" * 60)
    
    headers = {"X-API-Key": API_KEY}
    
    tools_to_test = ["ping", "list_files", "read_file", "analyze_code"]
    
    for tool in tools_to_test:
        print(f"\n   📊 Metrics for {tool}:")
        try:
            response = requests.get(f"{API_BASE_URL}/performance/metrics?tool_name={tool}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                print(f"   ✅ Total Requests: {metrics.get('total_requests', 0)}")
                print(f"   📈 Success Rate: {metrics.get('success_rate', 0):.1f}%")
                print(f"   ⏱️ Avg Response Time: {metrics.get('avg_response_time', 0):.2f}ms")
                print(f"   ❌ Error Count: {metrics.get('error_count', 0)}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Main test function"""
    print("🚀 Performance Monitoring System Test Suite")
    print("=" * 60)
    
    # Test 1: Check if API is accessible
    print("\n🔗 Checking API Accessibility...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ API is accessible")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ API Connection Failed: {e}")
        return
    
    # Test 2: Test performance endpoints
    test_performance_endpoints()
    
    # Test 3: Generate test load
    generate_test_load()
    
    # Test 4: Test specific tool metrics
    test_specific_tool_metrics()
    
    print("\n" + "=" * 60)
    print("🎉 Performance Monitoring System Test Complete!")
    print("\n📊 To view the performance dashboard, run:")
    print("   streamlit run web/performance_dashboard.py")

if __name__ == "__main__":
    main()
