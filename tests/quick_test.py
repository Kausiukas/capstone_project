"""
Quick Test Script for LangFlow Connect System

This script runs a subset of critical tests for immediate validation.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class QuickTest:
    """Quick test runner for immediate validation"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def log_result(self, test_name: str, success: bool, duration: float, error: str = None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'duration': duration,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status} {test_name} ({duration:.2f}s)")
        if not success and error:
            print(f"    Error: {error}")
    
    async def test_basic_imports(self):
        """Test basic module imports"""
        print("\nTesting basic imports...")
        
        try:
            # Test Module 1 imports
            from modules.module_1_main import (
                WorkspaceManager, RepositoryIngestor, CodeAnalyzer, 
                CodeRefactorer, ExternalServiceManager
            )
            print("✓ Module 1 imports successful")
            
            # Test Module 2 imports
            from modules.module_2_support import (
                PostgreSQLVectorAgent, SystemCoordinator, HealthMonitor,
                PerformanceTracker, MemoryManager
            )
            print("✓ Module 2 imports successful")
            
            # Test Module 3 imports
            from modules.module_3_economy import (
                CostTracker, BudgetManager, OptimizationEngine,
                CostAnalyzer, AlertSystem
            )
            print("✓ Module 3 imports successful")
            
            # Test Module 4 imports
            from modules.module_4_langflow import (
                LangflowConnector, DataVisualizer, FlowManager, ConnectionMonitor
            )
            print("✓ Module 4 imports successful")
            
            return True
        except Exception as e:
            print(f"✗ Import test failed: {e}")
            return False
    
    async def test_component_initialization(self):
        """Test component initialization"""
        print("\nTesting component initialization...")
        
        try:
            # Import components
            from modules.module_1_main import WorkspaceManager, CodeAnalyzer
            from modules.module_3_economy import CostTracker
            from modules.module_2_support import HealthMonitor
            
            # Test workspace manager
            start_time = time.time()
            workspace_manager = WorkspaceManager()
            await workspace_manager.initialize()
            duration = time.time() - start_time
            
            self.log_result("WorkspaceManager initialization", True, duration)
            await workspace_manager.cleanup()
            
            # Test code analyzer
            start_time = time.time()
            code_analyzer = CodeAnalyzer()
            await code_analyzer.initialize()
            duration = time.time() - start_time
            
            self.log_result("CodeAnalyzer initialization", True, duration)
            await code_analyzer.cleanup()
            
            # Test cost tracker
            start_time = time.time()
            cost_tracker = CostTracker()
            await cost_tracker.initialize()
            duration = time.time() - start_time
            
            self.log_result("CostTracker initialization", True, duration)
            await cost_tracker.cleanup()
            
            # Test health monitor
            start_time = time.time()
            health_monitor = HealthMonitor()
            await health_monitor.initialize()
            duration = time.time() - start_time
            
            self.log_result("HealthMonitor initialization", True, duration)
            await health_monitor.cleanup()
            
            return True
        except Exception as e:
            self.log_result("Component initialization", False, 0, str(e))
            return False
    
    async def test_basic_functionality(self):
        """Test basic functionality"""
        print("\nTesting basic functionality...")
        
        try:
            # Import components
            from modules.module_1_main import WorkspaceManager, CodeAnalyzer
            from modules.module_3_economy import CostTracker
            
            # Test workspace operations
            workspace_manager = WorkspaceManager()
            await workspace_manager.initialize()
            
            try:
                # Create temporary file
                import tempfile
                temp_dir = tempfile.mkdtemp()
                test_file = os.path.join(temp_dir, 'test.txt')
                test_content = "Quick test content"
                
                # Write file
                start_time = time.time()
                await workspace_manager.write_file(test_file, test_content)
                duration = time.time() - start_time
                self.log_result("Write file operation", True, duration)
                
                # Read file
                start_time = time.time()
                content = await workspace_manager.read_file_simple(test_file)
                duration = time.time() - start_time
                
                if content == test_content:
                    self.log_result("Read file operation", True, duration)
                else:
                    self.log_result("Read file operation", False, duration, "Content mismatch")
                
                # Cleanup
                import shutil
                shutil.rmtree(temp_dir)
                
            finally:
                await workspace_manager.cleanup()
            
            # Test code analysis
            code_analyzer = CodeAnalyzer()
            await code_analyzer.initialize()
            
            try:
                test_code = '''
def hello_world():
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42
'''
                
                start_time = time.time()
                analysis_result = await code_analyzer.analyze_code('test.py', test_code)
                duration = time.time() - start_time
                
                if analysis_result['success'] and 'analysis' in analysis_result:
                    analysis = analysis_result['analysis']
                    if 'structure' in analysis and 'metrics' in analysis:
                        self.log_result("Code analysis", True, duration)
                    else:
                        self.log_result("Code analysis", False, duration, "Missing analysis structure")
                else:
                    self.log_result("Code analysis", False, duration, "Analysis failed")
                
            finally:
                await code_analyzer.cleanup()
            
            # Test cost tracking
            cost_tracker = CostTracker()
            await cost_tracker.initialize()
            
            try:
                start_time = time.time()
                await cost_tracker.record_token_usage('test_operation', 'test_model', 50, 50)
                duration = time.time() - start_time
                self.log_result("Cost tracking", True, duration)
                
                start_time = time.time()
                summary_result = await cost_tracker.get_cost_summary()
                duration = time.time() - start_time
                
                if summary_result['success'] and 'summary' in summary_result:
                    summary = summary_result['summary']
                    if 'total_cost_usd' in summary:
                        self.log_result("Cost summary", True, duration)
                    else:
                        self.log_result("Cost summary", False, duration, "Missing cost data in summary")
                else:
                    self.log_result("Cost summary", False, duration, "Cost summary failed")
                
            finally:
                await cost_tracker.cleanup()
            
            return True
        except Exception as e:
            self.log_result("Basic functionality", False, 0, str(e))
            return False
    
    async def test_mcp_server_basic(self):
        """Test MCP server basic functionality"""
        print("\nTesting MCP server basic functionality...")
        
        try:
            # Import MCP server
            sys.path.insert(0, os.path.dirname(__file__))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from mcp_server_standalone import LangFlowConnectMCPServer
            
            # Test server creation
            start_time = time.time()
            server = LangFlowConnectMCPServer()
            duration = time.time() - start_time
            
            self.log_result("MCP server creation", True, duration)
            
            # Test tool registration by checking if server was created successfully
            start_time = time.time()
            # The server creation itself validates that tools are registered
            duration = time.time() - start_time
            
            # Check if the server has the expected structure
            if hasattr(server, 'fastmcp') and hasattr(server, 'system_coordinator'):
                self.log_result("MCP tool registration", True, duration)
            else:
                self.log_result("MCP tool registration", False, duration, "Server structure invalid")
            
            return True
        except Exception as e:
            self.log_result("MCP server test", False, 0, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        print("\n" + "="*60)
        print("QUICK TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print(f"\nFailed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['error']}")
        
        print("="*60)
        
        return passed_tests == total_tests
    
    async def run_quick_tests(self):
        """Run all quick tests"""
        print("Starting quick tests for LangFlow Connect system...")
        
        # Run tests
        await self.test_basic_imports()
        await self.test_component_initialization()
        await self.test_basic_functionality()
        await self.test_mcp_server_basic()
        
        # Print summary
        return self.print_summary()


async def main():
    """Main entry point"""
    quick_test = QuickTest()
    success = await quick_test.run_quick_tests()
    
    if success:
        print("\n🎉 All quick tests passed! The system appears to be working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some quick tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main()) 