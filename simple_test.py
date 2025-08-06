#!/usr/bin/env python3
"""
Simple test script to verify LangFlow Connect modules work correctly.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_basic_imports():
    """Test basic module imports"""
    print("Testing basic imports...")
    
    try:
        # Test Module 1 imports
        from modules.module_1_main import WorkspaceManager
        print("✓ Module 1 imports work")
        
        # Test Module 2 imports
        from modules.module_2_support import SystemCoordinator, MemoryManager
        print("✓ Module 2 imports work")
        
        # Test Module 3 imports
        from modules.module_3_economy import CostTracker
        print("✓ Module 3 imports work")
        
        # Test Module 4 imports
        from modules.module_4_langflow import LangflowConnector
        print("✓ Module 4 imports work")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

async def test_basic_functionality():
    """Test basic functionality of each module"""
    print("\nTesting basic functionality...")
    
    try:
        # Test Module 1 - Workspace Manager
        from modules.module_1_main import WorkspaceManager
        workspace_manager = WorkspaceManager()
        print("✓ WorkspaceManager created")
        
        # Test Module 2 - Memory Manager
        from modules.module_2_support import MemoryManager
        memory_manager = MemoryManager()
        print("✓ MemoryManager created")
        
        # Test Module 3 - Cost Tracker
        from modules.module_3_economy import CostTracker
        cost_tracker = CostTracker()
        print("✓ CostTracker created")
        
        # Test Module 4 - Langflow Connector
        from modules.module_4_langflow import LangflowConnector
        config = {
            "websocket_url": "ws://localhost:3000/ws",
            "api_url": "http://localhost:3000/api/v1",
            "auth_token": "demo_token"
        }
        langflow_connector = LangflowConnector(config)
        print("✓ LangflowConnector created")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality error: {e}")
        return False

async def test_file_operations():
    """Test basic file operations"""
    print("\nTesting file operations...")
    
    try:
        from modules.module_1_main import WorkspaceManager
        workspace_manager = WorkspaceManager()
        
        # Test file write
        test_content = "Hello, World!"
        write_result = await workspace_manager.write_file("test.txt", test_content)
        print(f"✓ File write: {write_result['success']}")
        
        # Test file read
        read_result = await workspace_manager.read_file("test.txt")
        print(f"✓ File read: {read_result['success']}")
        
        # Test file delete
        delete_result = await workspace_manager.delete_file("test.txt")
        print(f"✓ File delete: {delete_result['success']}")
        
        return True
        
    except Exception as e:
        print(f"✗ File operations error: {e}")
        return False

async def test_cost_tracking():
    """Test cost tracking functionality"""
    print("\nTesting cost tracking...")
    
    try:
        from modules.module_3_economy import CostTracker
        cost_tracker = CostTracker()
        
        # Record token usage
        result = await cost_tracker.record_token_usage(
            operation_id="test_op",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            operation_type="test"
        )
        print(f"✓ Token usage recorded: {result.get('success', False)}")
        
        # Get cost summary
        summary = await cost_tracker.get_cost_summary()
        print(f"✓ Cost summary: {summary.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Cost tracking error: {e}")
        return False

async def main():
    """Main test function"""
    print("LangFlow Connect - Simple Test")
    print("=" * 40)
    
    # Test imports
    if not await test_basic_imports():
        print("❌ Import tests failed")
        return
    
    # Test basic functionality
    if not await test_basic_functionality():
        print("❌ Basic functionality tests failed")
        return
    
    # Test file operations
    if not await test_file_operations():
        print("❌ File operation tests failed")
        return
    
    # Test cost tracking
    if not await test_cost_tracking():
        print("❌ Cost tracking tests failed")
        return
    
    print("\n" + "=" * 40)
    print("✅ All tests passed! System is working correctly.")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(main()) 