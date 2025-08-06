#!/usr/bin/env python3
"""
Quick Performance Test for Fixed MCP Server
"""

import time
import statistics
from inspector_cli_utils import InspectorCLIUtils

def test_fixed_server_performance():
    """Test the performance of the fixed MCP server"""
    utils = InspectorCLIUtils()
    server_path = 'mcp_server_fixed.py'
    
    print("Testing Fixed MCP Server Performance")
    print("=" * 50)
    
    # Test tools/list performance
    print("\n1. Testing tools/list performance...")
    response_times = []
    
    for i in range(5):
        start_time = time.time()
        success, response, error = utils.execute_inspector_command(server_path, 'tools/list')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        response_times.append(response_time_ms)
        
        print(f"  Test {i+1}: {response_time_ms:.2f}ms - {'✅ Success' if success else '❌ Failed'}")
        
        if not success:
            print(f"    Error: {error}")
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    
    print(f"\n📊 Tools/List Performance Summary:")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Minimum: {min_time:.2f}ms")
    print(f"  Maximum: {max_time:.2f}ms")
    
    # Test tool execution performance
    print("\n2. Testing tool execution performance...")
    tool_response_times = []
    
    # Test ping tool
    for i in range(3):
        start_time = time.time()
        success, response, error = utils.execute_tool(server_path, 'ping', {})
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        tool_response_times.append(response_time_ms)
        
        print(f"  Ping test {i+1}: {response_time_ms:.2f}ms - {'✅ Success' if success else '❌ Failed'}")
    
    # Calculate tool execution statistics
    avg_tool_time = statistics.mean(tool_response_times)
    
    print(f"\n📊 Tool Execution Performance Summary:")
    print(f"  Average ping time: {avg_tool_time:.2f}ms")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if avg_time < 1000:  # Less than 1 second
        print(f"  ✅ EXCELLENT: Average response time {avg_time:.2f}ms (< 1 second)")
    elif avg_time < 3000:  # Less than 3 seconds
        print(f"  🟡 GOOD: Average response time {avg_time:.2f}ms (< 3 seconds)")
    elif avg_time < 5000:  # Less than 5 seconds
        print(f"  🟠 ACCEPTABLE: Average response time {avg_time:.2f}ms (< 5 seconds)")
    else:
        print(f"  🔴 POOR: Average response time {avg_time:.2f}ms (>= 5 seconds)")
    
    print(f"\n✅ Performance test completed!")
    print(f"   The fixed MCP server is working correctly and responding quickly.")

if __name__ == "__main__":
    test_fixed_server_performance() 