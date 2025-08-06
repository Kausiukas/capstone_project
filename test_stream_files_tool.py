#!/usr/bin/env python3
"""
Test script for stream_files tool to identify session management issues
"""

import asyncio
from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_stream_files():
    """Test stream_files tool with proper session management"""
    
    print("🔍 Testing stream_files tool...")
    
    # Create connector instance (this should persist for the entire session)
    connector = SimpleLangFlowMCPConnector()
    
    # Test 1: Start streaming
    print("\n📋 Test 1: Starting stream...")
    start_result = await connector.handle_stream_files({
        'directory': '.',
        'action': 'start',
        'max_depth': 1,
        'include_hidden': False
    })
    print("Start Result:")
    print(start_result)
    
    # Extract stream_id from the result
    lines = start_result.split('\n')
    stream_id = None
    for line in lines:
        if 'Stream ID:' in line:
            stream_id = line.split(':')[1].strip()
            break
    
    if not stream_id:
        print("❌ Error: Could not extract stream_id from start result")
        return
    
    print(f"\n📋 Extracted Stream ID: {stream_id}")
    
    # Test 2: Get next batch
    print("\n📋 Test 2: Getting next batch...")
    next_result = await connector.handle_stream_files({
        'stream_id': stream_id,
        'action': 'next'
    })
    print("Next Result:")
    print(next_result)
    
    # Test 3: Get another batch
    print("\n📋 Test 3: Getting another batch...")
    next_result2 = await connector.handle_stream_files({
        'stream_id': stream_id,
        'action': 'next'
    })
    print("Next Result 2:")
    print(next_result2)
    
    # Test 4: Stop streaming
    print("\n📋 Test 4: Stopping stream...")
    stop_result = await connector.handle_stream_files({
        'stream_id': stream_id,
        'action': 'stop'
    })
    print("Stop Result:")
    print(stop_result)
    
    # Test 5: Try to use the same stream_id after stopping
    print("\n📋 Test 5: Trying to use stopped stream...")
    error_result = await connector.handle_stream_files({
        'stream_id': stream_id,
        'action': 'next'
    })
    print("Error Result (expected):")
    print(error_result)

def test_stream_files_issue():
    """Test to demonstrate the session management issue"""
    print("\n🔍 Testing session management issue...")
    
    # This demonstrates the problem: different connector instances
    connector1 = SimpleLangFlowMCPConnector()
    connector2 = SimpleLangFlowMCPConnector()
    
    async def run_test():
        # Start with connector1
        start_result = await connector1.handle_stream_files({
            'directory': '.',
            'action': 'start'
        })
        print("Start Result:")
        print(start_result)
        
        # Extract stream_id
        lines = start_result.split('\n')
        stream_id = None
        for line in lines:
            if 'Stream ID:' in line:
                stream_id = line.split(':')[1].strip()
                break
        
        # Try to continue with connector2 (this will fail)
        next_result = await connector2.handle_stream_files({
            'stream_id': stream_id,
            'action': 'next'
        })
        print("\nNext Result (with different connector - should fail):")
        print(next_result)
    
    asyncio.run(run_test())

if __name__ == "__main__":
    print("🚀 Starting stream_files tool tests...")
    
    # Test proper usage
    asyncio.run(test_stream_files())
    
    # Test the issue
    test_stream_files_issue()
    
    print("\n✅ Tests completed!") 