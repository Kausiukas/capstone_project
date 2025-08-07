#!/usr/bin/env python3
"""
Quick script to check current performance metrics
"""

import requests
import json

API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def check_metrics():
    """Check current performance metrics"""
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/performance/metrics", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("📊 Current Performance Metrics:")
            print("=" * 50)
            
            metrics = data.get('metrics', {})
            overview = metrics.get('overview', {})
            
            print(f"📈 Total Requests: {overview.get('total_requests', 0)}")
            print(f"✅ Success Rate: {overview.get('overall_success_rate', 0):.1f}%")
            print(f"❌ Total Errors: {overview.get('total_errors', 0)}")
            print(f"⏱️ Uptime: {overview.get('uptime_seconds', 0)/3600:.1f} hours")
            
            print("\n🛠️ Tool Metrics:")
            print("-" * 30)
            tools = metrics.get('tools', {})
            for tool_name, tool_metrics in tools.items():
                if tool_metrics.get('total_requests', 0) > 0:
                    print(f"📋 {tool_name}:")
                    print(f"   Requests: {tool_metrics.get('total_requests', 0)}")
                    print(f"   Success Rate: {tool_metrics.get('success_rate', 0):.1f}%")
                    print(f"   Avg Response Time: {tool_metrics.get('avg_response_time', 0):.2f}ms")
                    print(f"   Errors: {tool_metrics.get('error_count', 0)}")
                    print()
            
            print("💻 System Metrics:")
            print("-" * 30)
            system = metrics.get('system_metrics', {})
            cpu = system.get('cpu_usage', {})
            memory = system.get('memory_usage', {})
            disk = system.get('disk_usage', {})
            
            print(f"🖥️ CPU: {cpu.get('current', 0):.1f}% (avg: {cpu.get('average', 0):.1f}%)")
            print(f"🧠 Memory: {memory.get('current', 0):.1f}% (avg: {memory.get('average', 0):.1f}%)")
            print(f"💾 Disk: {disk.get('current', 0):.1f}% (avg: {disk.get('average', 0):.1f}%)")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_metrics()
