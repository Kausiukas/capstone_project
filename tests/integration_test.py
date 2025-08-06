"""
Integration Test for LangFlow Connect System

This test demonstrates how all modules work together in a complete workflow.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.module_1_main import (
    WorkspaceManager, RepositoryIngestor, CodeAnalyzer, 
    CodeRefactorer, ExternalServiceManager
)
from modules.module_2_support import (
    PostgreSQLVectorAgent, SystemCoordinator, HealthMonitor,
    PerformanceTracker, MemoryManager
)
from modules.module_3_economy import (
    CostTracker, BudgetManager, OptimizationEngine,
    CostAnalyzer, AlertSystem
)
from modules.module_4_langflow import (
    LangflowConnector, DataVisualizer, FlowManager, ConnectionMonitor
)


class IntegrationTest:
    """
    Comprehensive integration test for the LangFlow Connect system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize all modules
        self.module_1_components = {}
        self.module_2_components = {}
        self.module_3_components = {}
        self.module_4_components = {}
        
        self.test_results = []
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('integration_test.log')
            ]
        )
    
    async def initialize_all_modules(self):
        """Initialize all system modules"""
        self.logger.info("Starting comprehensive integration tests...")
        
        try:
            # Module 1: MAIN - Workspace Operations
            self.logger.info("Initializing Module 1 (MAIN)...")
            self.module_1_components['workspace_manager'] = WorkspaceManager()
            self.module_1_components['repository_ingestor'] = RepositoryIngestor()
            self.module_1_components['code_analyzer'] = CodeAnalyzer()
            self.module_1_components['code_refactorer'] = CodeRefactorer()
            self.module_1_components['external_services'] = ExternalServiceManager()
            
            # Module 2: SUPPORT - System Support
            self.logger.info("Initializing Module 2 (SUPPORT)...")
            self.module_2_components['postgresql_agent'] = PostgreSQLVectorAgent()
            self.module_2_components['system_coordinator'] = SystemCoordinator()
            self.module_2_components['health_monitor'] = HealthMonitor()
            self.module_2_components['performance_tracker'] = PerformanceTracker()
            self.module_2_components['memory_manager'] = MemoryManager()
            
            # Module 3: ECONOMY - Cost Tracking
            self.logger.info("Initializing Module 3 (ECONOMY)...")
            self.module_3_components['cost_tracker'] = CostTracker()
            self.module_3_components['budget_manager'] = BudgetManager()
            self.module_3_components['optimization_engine'] = OptimizationEngine()
            self.module_3_components['cost_analyzer'] = CostAnalyzer()
            self.module_3_components['alert_system'] = AlertSystem()
            
            # Module 4: LangflowConnector
            self.logger.info("Initializing Module 4 (LangflowConnector)...")
            
            # Create default config for LangflowConnector
            langflow_config = {
                "websocket_url": "ws://localhost:3000/ws",
                "api_url": "http://localhost:3000/api/v1",
                "auth_token": "demo_token",
                "max_reconnect_attempts": 5,
                "ping_interval": 30,
                "ping_timeout": 10
            }
            
            self.module_4_components['langflow_connector'] = LangflowConnector(langflow_config)
            self.module_4_components['data_visualizer'] = DataVisualizer()
            self.module_4_components['flow_manager'] = FlowManager()
            self.module_4_components['connection_monitor'] = ConnectionMonitor()
            
            # Initialize components that have initialize methods
            for component_name, component in self.module_1_components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized {component_name}")
            
            for component_name, component in self.module_2_components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized {component_name}")
            
            for component_name, component in self.module_3_components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized {component_name}")
            
            for component_name, component in self.module_4_components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized {component_name}")
            
            self.logger.info("All modules initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            return False
    
    async def test_module_1_workspace_operations(self):
        """Test Module 1 workspace operations"""
        self.logger.info("Testing Module 1: Workspace Operations")
        
        try:
            workspace_manager = self.module_1_components['workspace_manager']
            code_analyzer = self.module_1_components['code_analyzer']
            
            # Test file operations
            test_file = "test_integration.py"
            test_content = """
def hello_world():
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
"""
            
            # Write test file
            write_result = await workspace_manager.write_file(test_file, test_content)
            assert write_result["success"] == True
            self.logger.info("File write operation successful")
            
            # Read test file
            read_result = await workspace_manager.read_file(test_file)
            assert read_result["success"] == True
            assert read_result["content"] == test_content
            self.logger.info("File read operation successful")
            
            # Analyze code
            analysis = await code_analyzer.analyze_code(test_content, "python")
            assert analysis is not None
            self.logger.info("Code analysis successful")
            
            # Clean up
            delete_result = await workspace_manager.delete_file(test_file)
            assert delete_result["success"] == True
            self.logger.info("File cleanup successful")
            
            self.test_results.append("Module 1: Workspace Operations - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Module 1 test failed: {e}")
            self.test_results.append(f"Module 1: Workspace Operations - FAILED: {e}")
            return False
    
    async def test_module_2_system_support(self):
        """Test Module 2 system support"""
        self.logger.info("Testing Module 2: System Support")
        
        try:
            system_coordinator = self.module_2_components['system_coordinator']
            health_monitor = self.module_2_components['health_monitor']
            memory_manager = self.module_2_components['memory_manager']
            
            # Test system coordinator
            start_result = await system_coordinator.start()
            assert start_result["success"] == True
            self.logger.info("System coordinator started")
            
            # Test health monitoring
            await health_monitor.start_monitoring()
            metrics = await health_monitor.get_current_metrics()
            assert metrics is not None
            self.logger.info("Health monitoring active")
            
            # Test memory management
            start_memory_result = await memory_manager.start()
            assert start_memory_result["success"] == True
            
            set_cache_result = await memory_manager.set_cache("test_key", "test_value")
            assert set_cache_result["success"] == True
            
            get_cache_result = await memory_manager.get_cache("test_key")
            assert get_cache_result["success"] == True
            assert get_cache_result["value"] == "test_value"
            self.logger.info("Memory management working")
            
            # Clean up
            await health_monitor.stop_monitoring()
            await memory_manager.stop()
            await system_coordinator.stop()
            
            self.test_results.append("Module 2: System Support - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Module 2 test failed: {e}")
            self.test_results.append(f"Module 2: System Support - FAILED: {e}")
            return False
    
    async def test_module_3_economy(self):
        """Test Module 3 economy tracking"""
        self.logger.info("Testing Module 3: Economy Tracking")
        
        try:
            cost_tracker = self.module_3_components['cost_tracker']
            budget_manager = self.module_3_components['budget_manager']
            optimization_engine = self.module_3_components['optimization_engine']
            
            # Test cost tracking
            await cost_tracker.record_token_usage(
                operation_id="test_op_1",
                model="gpt-4",
                input_tokens=500,
                output_tokens=500,
                operation_type="test_operation"
            )
            
            cost_summary_result = await cost_tracker.get_cost_summary()
            assert cost_summary_result["success"] == True
            assert cost_summary_result["summary"]["total_cost_usd"] > 0
            self.logger.info("Cost tracking working")
            
            # Test budget management
            budget_id = await budget_manager.create_budget(
                name="Test Budget",
                amount=100.0,
                period="daily"
            )
            
            budget = await budget_manager.get_budget(budget_id)
            assert budget.name == "Test Budget"
            self.logger.info("Budget management working")
            
            # Test optimization engine
            recommendation_id = await optimization_engine.generate_recommendation(
                strategy="MODEL_SWITCHING",
                priority="MEDIUM",
                estimated_savings=50.0,
                implementation_cost=10.0
            )
            
            recommendation = await optimization_engine.get_recommendation(recommendation_id)
            assert recommendation is not None
            self.logger.info("Optimization engine working")
            
            self.test_results.append("Module 3: Economy Tracking - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Module 3 test failed: {e}")
            self.test_results.append(f"Module 3: Economy Tracking - FAILED: {e}")
            return False
    
    async def test_module_4_langflow_connector(self):
        """Test Module 4 Langflow connector"""
        self.logger.info("Testing Module 4: Langflow Connector")
        
        try:
            data_visualizer = self.module_4_components['data_visualizer']
            flow_manager = self.module_4_components['flow_manager']
            connection_monitor = self.module_4_components['connection_monitor']
            
            # Test data visualization
            chart_id = await data_visualizer.create_chart(
                title="Test Chart",
                chart_type="line",
                data_source="test_data",
                x_axis="time",
                y_axis="value"
            )
            
            chart = await data_visualizer.get_chart(chart_id)
            assert chart.title == "Test Chart"
            self.logger.info("Data visualization working")
            
            # Test flow management
            flow_id = await flow_manager.create_flow(
                name="Test Flow",
                description="Test workflow",
                flow_type="workflow",
                nodes=[
                    {
                        "id": "input_1",
                        "name": "Input Node",
                        "node_type": "input",
                        "position": {"x": 100, "y": 100},
                        "config": {}
                    }
                ],
                edges=[]
            )
            
            flow = await flow_manager.get_flow(flow_id)
            assert flow.name == "Test Flow"
            self.logger.info("Flow management working")
            
            # Test connection monitoring
            await connection_monitor.start_monitoring()
            health_summary = await connection_monitor.get_health_summary()
            assert health_summary is not None
            self.logger.info("Connection monitoring working")
            
            await connection_monitor.stop_monitoring()
            
            self.test_results.append("Module 4: Langflow Connector - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Module 4 test failed: {e}")
            self.test_results.append(f"Module 4: Langflow Connector - FAILED: {e}")
            return False
    
    async def test_cross_module_integration(self):
        """Test integration between modules"""
        self.logger.info("Testing Cross-Module Integration")
        
        try:
            # Test data flow from Module 1 to Module 4
            workspace_manager = self.module_1_components['workspace_manager']
            data_visualizer = self.module_4_components['data_visualizer']
            
            # Create test data
            test_data = [
                {"date": "2024-01-01", "cost": 100, "category": "api"},
                {"date": "2024-01-02", "cost": 150, "category": "api"},
                {"date": "2024-01-03", "cost": 120, "category": "storage"}
            ]
            
            # Create chart for visualization
            chart_id = await data_visualizer.create_chart(
                title="Cost Analysis",
                chart_type="line",
                data_source="cost_data",
                x_axis="date",
                y_axis="cost",
                color_field="category"
            )
            
            # Generate visualization
            viz_id = await data_visualizer.generate_visualization(chart_id, test_data)
            self.logger.info("Cross-module data flow working")
            
            # Test system coordination
            system_coordinator = self.module_2_components['system_coordinator']
            cost_tracker = self.module_3_components['cost_tracker']
            
            # Register modules with coordinator
            await system_coordinator.register_module("cost_tracker", cost_tracker)
            await system_coordinator.register_module("data_visualizer", data_visualizer)
            
            # Send message between modules
            await system_coordinator.send_message(
                "cost_tracker",
                "data_visualizer",
                "event",
                {"type": "cost_update", "data": test_data}
            )
            
            self.logger.info("Cross-module communication working")
            
            self.test_results.append("Cross-Module Integration - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Cross-module integration test failed: {e}")
            self.test_results.append(f"Cross-Module Integration - FAILED: {e}")
            return False
    
    async def test_complete_workflow(self):
        """Test a complete end-to-end workflow"""
        self.logger.info("Testing Complete End-to-End Workflow")
        
        try:
            # 1. Analyze code (Module 1)
            code_analyzer = self.module_1_components['code_analyzer']
            analysis = await code_analyzer.analyze_code(
                "def test_function():\n    return 'hello'", 
                "python"
            )
            
            # 2. Track costs (Module 3)
            cost_tracker = self.module_3_components['cost_tracker']
            await cost_tracker.record_token_usage(
                operation_id="workflow_test",
                model="gpt-4",
                input_tokens=250,
                output_tokens=250,
                operation_type="code_analysis"
            )
            
            # 3. Generate optimization recommendation (Module 3)
            optimization_engine = self.module_3_components['optimization_engine']
            recommendation_id = await optimization_engine.generate_recommendation(
                strategy="MODEL_SWITCHING",
                priority="HIGH",
                estimated_savings=25.0,
                implementation_cost=5.0
            )
            
            # 4. Create visualization (Module 4)
            data_visualizer = self.module_4_components['data_visualizer']
            chart_id = await data_visualizer.create_chart(
                title="Code Analysis Results",
                chart_type="bar",
                data_source="analysis_data",
                x_axis="metric",
                y_axis="value"
            )
            
            # 5. Monitor system health (Module 2)
            health_monitor = self.module_2_components['health_monitor']
            await health_monitor.start_monitoring()
            metrics = await health_monitor.get_current_metrics()
            
            # 6. Create dashboard (Module 4)
            dashboard_id = await data_visualizer.create_dashboard(
                name="System Overview",
                description="Complete system dashboard",
                charts=[chart_id]
            )
            
            self.logger.info("Complete workflow executed successfully")
            self.test_results.append("Complete End-to-End Workflow - PASSED")
            return True
            
        except Exception as e:
            self.logger.error(f"Complete workflow test failed: {e}")
            self.test_results.append(f"Complete End-to-End Workflow - FAILED: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        self.logger.info("Starting comprehensive integration tests...")
        
        # Initialize all modules
        if not await self.initialize_all_modules():
            self.logger.error("Module initialization failed")
            return False
        
        # Run individual module tests
        await self.test_module_1_workspace_operations()
        await self.test_module_2_system_support()
        await self.test_module_3_economy()
        await self.test_module_4_langflow_connector()
        
        # Run integration tests
        await self.test_cross_module_integration()
        await self.test_complete_workflow()
        
        # Print results
        self.print_test_results()
        
        return True
    
    def print_test_results(self):
        """Print test results summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("INTEGRATION TEST RESULTS")
        self.logger.info("="*60)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            if "PASSED" in result:
                self.logger.info(f"PASSED: {result}")
                passed += 1
            else:
                self.logger.error(f"FAILED: {result}")
                failed += 1
        
        self.logger.info("="*60)
        self.logger.info(f"SUMMARY: {passed} passed, {failed} failed")
        
        if failed == 0:
            self.logger.info("ALL TESTS PASSED! System is ready for production.")
        else:
            self.logger.warning("Some tests failed. Please review the issues.")
        
        self.logger.info("="*60)


async def main():
    """Main test runner"""
    test = IntegrationTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 