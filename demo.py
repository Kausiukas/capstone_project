"""
LangFlow Connect System Demo

This script demonstrates the complete LangFlow Connect system functionality
with practical examples of all modules working together.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from system_coordinator import LangFlowSystemCoordinator, start_system, stop_system


class LangFlowDemo:
    """
    Demo class for showcasing LangFlow Connect system capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.system_coordinator: Optional[LangFlowSystemCoordinator] = None
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/demo.log')
            ]
        )
    
    async def run_demo(self):
        """Run the complete demo"""
        self.logger.info("🎬 Starting LangFlow Connect System Demo")
        
        try:
            # 1. Start the system
            await self.start_system_demo()
            
            # 2. Run individual module demos
            await self.demo_module_1_workspace_operations()
            await self.demo_module_2_system_support()
            await self.demo_module_3_economy_tracking()
            await self.demo_module_4_langflow_connector()
            
            # 3. Run integration demos
            await self.demo_cross_module_integration()
            await self.demo_complete_workflows()
            
            # 4. Show system status
            await self.show_system_status()
            
            # 5. Stop the system
            await self.stop_system_demo()
            
            self.logger.info("🎉 Demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {e}")
            if self.system_coordinator:
                await stop_system(self.system_coordinator)
    
    async def start_system_demo(self):
        """Demo system startup"""
        self.logger.info("🚀 Starting LangFlow Connect System...")
        
        self.system_coordinator = await start_system()
        
        # Wait a moment for system to stabilize
        await asyncio.sleep(2)
        
        status = await self.system_coordinator.get_system_status()
        self.logger.info(f"✅ System Status: {status.system_health}")
        self.logger.info(f"📊 Modules Initialized: {len(status.modules_initialized)}")
    
    async def demo_module_1_workspace_operations(self):
        """Demo Module 1: Workspace Operations"""
        self.logger.info("\n📁 Demo: Module 1 - Workspace Operations")
        
        try:
            # Get Module 1 components
            workspace_manager = self.system_coordinator.module_1_components['workspace_manager']
            code_analyzer = self.system_coordinator.module_1_components['code_analyzer']
            
            # Demo file operations
            test_file = "demo_test.py"
            test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        return self.history
"""
            
            # Write file
            await workspace_manager.write_file(test_file, test_code)
            self.logger.info("✅ File written successfully")
            
            # Read file
            content = await workspace_manager.read_file(test_file)
            self.logger.info(f"✅ File read successfully ({len(content)} characters)")
            
            # Analyze code
            analysis = await code_analyzer.analyze_code(test_code, "python")
            self.logger.info(f"✅ Code analysis completed")
            self.logger.info(f"   - Functions: {len(analysis.get('functions', []))}")
            self.logger.info(f"   - Classes: {len(analysis.get('classes', []))}")
            self.logger.info(f"   - Lines of code: {analysis.get('metrics', {}).get('lines_of_code', 0)}")
            
            # Clean up
            await workspace_manager.delete_file(test_file)
            self.logger.info("✅ File cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Module 1 demo failed: {e}")
    
    async def demo_module_2_system_support(self):
        """Demo Module 2: System Support"""
        self.logger.info("\n🔧 Demo: Module 2 - System Support")
        
        try:
            # Get Module 2 components
            health_monitor = self.system_coordinator.module_2_components['health_monitor']
            memory_manager = self.system_coordinator.module_2_components['memory_manager']
            
            # Demo health monitoring
            metrics = await health_monitor.get_current_metrics()
            self.logger.info("✅ Health monitoring active")
            self.logger.info(f"   - CPU Usage: {metrics.get('cpu_percentage', 0):.1f}%")
            self.logger.info(f"   - Memory Usage: {metrics.get('memory_percentage', 0):.1f}%")
            self.logger.info(f"   - Disk Usage: {metrics.get('disk_percentage', 0):.1f}%")
            
            # Demo memory management
            await memory_manager.set_cache("demo_key", {"data": "test_value", "timestamp": datetime.utcnow().isoformat()})
            cached_data = await memory_manager.get_cache("demo_key")
            self.logger.info("✅ Memory management working")
            self.logger.info(f"   - Cached data retrieved: {cached_data is not None}")
            
            # Get memory stats
            stats = await memory_manager.get_cache_stats()
            self.logger.info(f"   - Cache hits: {stats.get('hits', 0)}")
            self.logger.info(f"   - Cache misses: {stats.get('misses', 0)}")
            
        except Exception as e:
            self.logger.error(f"❌ Module 2 demo failed: {e}")
    
    async def demo_module_3_economy_tracking(self):
        """Demo Module 3: Economy Tracking"""
        self.logger.info("\n💰 Demo: Module 3 - Economy Tracking")
        
        try:
            # Get Module 3 components
            cost_tracker = self.system_coordinator.module_3_components['cost_tracker']
            budget_manager = self.system_coordinator.module_3_components['budget_manager']
            optimization_engine = self.system_coordinator.module_3_components['optimization_engine']
            
            # Demo cost tracking
            await cost_tracker.record_token_usage(
                model="gpt-4",
                tokens_used=1500,
                cost_per_token=0.00003,
                operation="demo_operation"
            )
            
            await cost_tracker.record_token_usage(
                model="gpt-3.5-turbo",
                tokens_used=2000,
                cost_per_token=0.000002,
                operation="demo_operation"
            )
            
            cost_summary = await cost_tracker.get_cost_summary()
            self.logger.info("✅ Cost tracking working")
            self.logger.info(f"   - Total cost: ${cost_summary.total_cost:.4f}")
            self.logger.info(f"   - Total tokens: {cost_summary.total_tokens}")
            self.logger.info(f"   - Operations: {cost_summary.total_operations}")
            
            # Demo budget management
            budget_id = await budget_manager.create_budget(
                name="Demo Budget",
                amount=100.0,
                period="daily",
                description="Demo budget for testing"
            )
            
            await budget_manager.record_expense(
                budget_id=budget_id,
                amount=25.0,
                description="Demo expense",
                category="testing"
            )
            
            budget_usage = await budget_manager.get_budget_usage(budget_id)
            self.logger.info("✅ Budget management working")
            self.logger.info(f"   - Budget: ${budget_usage.allocated_amount}")
            self.logger.info(f"   - Used: ${budget_usage.used_amount}")
            self.logger.info(f"   - Remaining: ${budget_usage.remaining_amount}")
            self.logger.info(f"   - Usage: {budget_usage.usage_percentage:.1f}%")
            
            # Demo optimization engine
            recommendation_id = await optimization_engine.generate_recommendation(
                strategy="model_switching",
                priority="high",
                estimated_savings=30.0,
                implementation_cost=5.0,
                custom_title="Switch to GPT-3.5 for non-critical tasks",
                custom_description="Use GPT-3.5 for routine operations to reduce costs"
            )
            
            recommendation = await optimization_engine.get_recommendation(recommendation_id)
            self.logger.info("✅ Optimization engine working")
            self.logger.info(f"   - Recommendation: {recommendation.title}")
            self.logger.info(f"   - Estimated savings: ${recommendation.estimated_savings}")
            self.logger.info(f"   - ROI: {recommendation.roi_percentage:.1f}%")
            
        except Exception as e:
            self.logger.error(f"❌ Module 3 demo failed: {e}")
    
    async def demo_module_4_langflow_connector(self):
        """Demo Module 4: Langflow Connector"""
        self.logger.info("\n🔗 Demo: Module 4 - Langflow Connector")
        
        try:
            # Get Module 4 components
            data_visualizer = self.system_coordinator.module_4_components['data_visualizer']
            flow_manager = self.system_coordinator.module_4_components['flow_manager']
            connection_monitor = self.system_coordinator.module_4_components['connection_monitor']
            
            # Demo data visualization
            chart_id = await data_visualizer.create_chart(
                title="Demo Cost Analysis",
                chart_type="line",
                data_source="demo_data",
                x_axis="date",
                y_axis="cost",
                color_field="category"
            )
            
            # Generate sample data
            sample_data = [
                {"date": "2024-01-01", "cost": 50, "category": "api"},
                {"date": "2024-01-02", "cost": 75, "category": "api"},
                {"date": "2024-01-03", "cost": 60, "category": "storage"},
                {"date": "2024-01-04", "cost": 90, "category": "api"},
                {"date": "2024-01-05", "cost": 45, "category": "storage"}
            ]
            
            viz_id = await data_visualizer.generate_visualization(chart_id, sample_data)
            self.logger.info("✅ Data visualization working")
            self.logger.info(f"   - Chart created: {chart_id}")
            self.logger.info(f"   - Visualization generated: {viz_id}")
            
            # Demo flow management
            flow_id = await flow_manager.create_flow(
                name="Demo Workflow",
                description="Demo workflow for testing",
                flow_type="workflow",
                nodes=[
                    {
                        "id": "input_1",
                        "name": "Data Input",
                        "node_type": "input",
                        "position": {"x": 100, "y": 100},
                        "config": {"data_type": "cost_data"}
                    },
                    {
                        "id": "processor_1",
                        "name": "Cost Analyzer",
                        "node_type": "processor",
                        "position": {"x": 300, "y": 100},
                        "config": {"analysis_type": "trend_analysis"}
                    },
                    {
                        "id": "output_1",
                        "name": "Results Output",
                        "node_type": "output",
                        "position": {"x": 500, "y": 100},
                        "config": {"format": "json"}
                    }
                ],
                edges=[
                    {"from": "input_1", "to": "processor_1"},
                    {"from": "processor_1", "to": "output_1"}
                ]
            )
            
            flow = await flow_manager.get_flow(flow_id)
            self.logger.info("✅ Flow management working")
            self.logger.info(f"   - Flow created: {flow.name}")
            self.logger.info(f"   - Nodes: {len(flow.nodes)}")
            self.logger.info(f"   - Status: {flow.status.value}")
            
            # Demo connection monitoring
            health_summary = await connection_monitor.get_health_summary()
            self.logger.info("✅ Connection monitoring working")
            self.logger.info(f"   - Total checks: {health_summary.get('total_checks', 0)}")
            self.logger.info(f"   - Healthy checks: {health_summary.get('healthy_checks', 0)}")
            self.logger.info(f"   - Overall health: {health_summary.get('overall_health', 0):.1%}")
            
        except Exception as e:
            self.logger.error(f"❌ Module 4 demo failed: {e}")
    
    async def demo_cross_module_integration(self):
        """Demo cross-module integration"""
        self.logger.info("\n🔗 Demo: Cross-Module Integration")
        
        try:
            # Execute a complete workflow that uses multiple modules
            workflow_result = await self.system_coordinator.execute_workflow(
                "code_analysis_workflow",
                {
                    "code_content": """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    for i in range(10):
        print(f"Fibonacci({i}) = {calculate_fibonacci(i)}")

if __name__ == "__main__":
    main()
""",
                    "language": "python"
                }
            )
            
            self.logger.info("✅ Cross-module workflow executed")
            self.logger.info(f"   - Workflow: {workflow_result['workflow']}")
            self.logger.info(f"   - Status: {workflow_result['status']}")
            if workflow_result['status'] == 'completed':
                self.logger.info(f"   - Chart created: {workflow_result['chart_id']}")
            
            # Execute cost optimization workflow
            cost_workflow_result = await self.system_coordinator.execute_workflow(
                "cost_optimization_workflow",
                {
                    "cost_data": [
                        {"date": "2024-01-01", "cost": 100, "category": "api"},
                        {"date": "2024-01-02", "cost": 150, "category": "api"},
                        {"date": "2024-01-03", "cost": 120, "category": "storage"}
                    ]
                }
            )
            
            self.logger.info("✅ Cost optimization workflow executed")
            self.logger.info(f"   - Workflow: {cost_workflow_result['workflow']}")
            self.logger.info(f"   - Status: {cost_workflow_result['status']}")
            
        except Exception as e:
            self.logger.error(f"❌ Cross-module integration demo failed: {e}")
    
    async def demo_complete_workflows(self):
        """Demo complete end-to-end workflows"""
        self.logger.info("\n🔄 Demo: Complete End-to-End Workflows")
        
        try:
            # Demo system health check workflow
            health_workflow = await self.system_coordinator.execute_workflow(
                "system_health_check_workflow",
                {}
            )
            
            self.logger.info("✅ System health check workflow executed")
            self.logger.info(f"   - Status: {health_workflow['status']}")
            
            # Demo Langflow visualization workflow
            viz_workflow = await self.system_coordinator.execute_workflow(
                "langflow_visualization_workflow",
                {}
            )
            
            self.logger.info("✅ Langflow visualization workflow executed")
            self.logger.info(f"   - Status: {viz_workflow['status']}")
            if viz_workflow['status'] == 'completed':
                self.logger.info(f"   - Dashboard created: {viz_workflow['dashboard_id']}")
                self.logger.info(f"   - Charts: {len(viz_workflow['charts'])}")
            
        except Exception as e:
            self.logger.error(f"❌ Complete workflows demo failed: {e}")
    
    async def show_system_status(self):
        """Show comprehensive system status"""
        self.logger.info("\n📊 System Status Overview")
        
        try:
            # Overall system status
            system_status = await self.system_coordinator.get_system_status()
            self.logger.info(f"🔄 System Running: {system_status.is_running}")
            self.logger.info(f"🏥 System Health: {system_status.system_health}")
            self.logger.info(f"📈 Total Operations: {system_status.total_operations}")
            self.logger.info(f"⏰ Uptime: {datetime.utcnow() - system_status.start_time}")
            
            # Individual module status
            for module_name in ["module_1_main", "module_2_support", "module_3_economy", "module_4_langflow"]:
                module_status = await self.system_coordinator.get_module_status(module_name)
                self.logger.info(f"📦 {module_name}: {module_status.get('status', 'unknown')}")
                if 'components' in module_status:
                    self.logger.info(f"   - Components: {len(module_status['components'])}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get system status: {e}")
    
    async def stop_system_demo(self):
        """Demo system shutdown"""
        self.logger.info("\n🛑 Stopping LangFlow Connect System...")
        
        if self.system_coordinator:
            await stop_system(self.system_coordinator)
            self.logger.info("✅ System stopped successfully")


async def main():
    """Main demo runner"""
    demo = LangFlowDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main()) 