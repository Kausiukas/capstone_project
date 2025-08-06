#!/usr/bin/env python3
"""
Quick Demo - LangFlow Connect System

This script demonstrates the key capabilities of the LangFlow Connect system.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def demo_workspace_operations():
    """Demo Module 1: Workspace Operations"""
    print("\n🔧 Module 1: Workspace Operations")
    print("-" * 40)
    
    from modules.module_1_main import WorkspaceManager, CodeAnalyzer
    
    # Initialize components
    workspace_manager = WorkspaceManager()
    code_analyzer = CodeAnalyzer()
    
    # Create and analyze a Python file
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
"""
    
    # Write file
    await workspace_manager.write_file("demo_fibonacci.py", python_code)
    print("✓ Created demo_fibonacci.py")
    
    # Analyze code
    analysis = await code_analyzer.analyze_code(python_code, "python")
    print("✓ Code analysis completed")
    
    # Clean up
    await workspace_manager.delete_file("demo_fibonacci.py")
    print("✓ Cleaned up demo file")

async def demo_cost_tracking():
    """Demo Module 3: Cost Tracking"""
    print("\n💰 Module 3: Cost Tracking")
    print("-" * 40)
    
    from modules.module_3_economy import CostTracker, BudgetManager
    
    # Initialize components
    cost_tracker = CostTracker()
    budget_manager = BudgetManager()
    
    # Record some token usage
    operations = [
        ("code_analysis", "gpt-4", 500, 200),
        ("code_generation", "gpt-4", 300, 400),
        ("documentation", "gpt-3.5-turbo", 200, 150)
    ]
    
    for op_type, model, input_tokens, output_tokens in operations:
        await cost_tracker.record_token_usage(
            operation_id=f"demo_{op_type}",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            operation_type=op_type
        )
        print(f"✓ Recorded {op_type} operation")
    
    # Get cost summary
    summary = await cost_tracker.get_cost_summary()
    total_cost = summary["summary"]["total_cost_usd"]
    print(f"✓ Total cost: ${total_cost:.4f}")
    
    # Create a budget
    budget_id = await budget_manager.create_budget(
        name="Demo Budget",
        amount=50.0,
        period="daily"
    )
    print(f"✓ Created budget: {budget_id}")

async def demo_memory_management():
    """Demo Module 2: Memory Management"""
    print("\n🧠 Module 2: Memory Management")
    print("-" * 40)
    
    from modules.module_2_support import MemoryManager
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    await memory_manager.start()
    
    # Store some data
    test_data = {
        "user_id": "demo_user",
        "preferences": {"theme": "dark", "language": "python"},
        "last_login": "2024-01-15T10:30:00Z"
    }
    
    await memory_manager.set_cache("user_data", test_data, ttl_seconds=3600)
    print("✓ Stored user data in cache")
    
    # Retrieve data
    cached_data = await memory_manager.get_cache("user_data")
    if cached_data["success"]:
        print("✓ Retrieved user data from cache")
    
    # Get cache stats
    stats = await memory_manager.get_cache_stats()
    print(f"✓ Cache hits: {stats['hits']}, misses: {stats['misses']}")
    
    await memory_manager.stop()

async def demo_langflow_connection():
    """Demo Module 4: Langflow Connection"""
    print("\n🔗 Module 4: Langflow Connection")
    print("-" * 40)
    
    from modules.module_4_langflow import LangflowConnector, DataVisualizer
    
    # Initialize components
    config = {
        "websocket_url": "ws://localhost:3000/ws",
        "api_url": "http://localhost:3000/api/v1",
        "auth_token": "demo_token"
    }
    
    connector = LangflowConnector(config)
    data_visualizer = DataVisualizer()
    
    print("✓ LangflowConnector initialized")
    print("✓ DataVisualizer initialized")
    
    # Create a sample chart
    chart_id = await data_visualizer.create_chart(
        title="Demo Cost Analysis",
        chart_type="line",
        data_source="demo_data",
        x_axis="time",
        y_axis="cost"
    )
    print(f"✓ Created chart: {chart_id}")

async def main():
    """Main demo function"""
    print("🚀 LangFlow Connect - Quick Demo")
    print("=" * 50)
    print("This demo showcases the key capabilities of the LangFlow Connect system.")
    
    try:
        # Demo each module
        await demo_workspace_operations()
        await demo_cost_tracking()
        await demo_memory_management()
        await demo_langflow_connection()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("The LangFlow Connect system is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Please check the system configuration and dependencies.")

if __name__ == "__main__":
    asyncio.run(main()) 