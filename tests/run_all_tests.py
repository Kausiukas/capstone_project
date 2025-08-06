"""
Master Test Runner for LangFlow Connect System

This script orchestrates all test suites and provides a unified testing interface.
"""

import asyncio
import sys
import os
import argparse
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestRunner:
    """Master test runner for all test suites"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_comprehensive_tests(self):
        """Run the comprehensive test suite"""
        print("\n" + "="*80)
        print("RUNNING COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        try:
            from comprehensive_test_suite import ComprehensiveTestSuite
            test_suite = ComprehensiveTestSuite()
            await test_suite.run_all_tests()
            
            # Read results
            if os.path.exists('comprehensive_test_results.json'):
                with open('comprehensive_test_results.json', 'r') as f:
                    self.test_results['comprehensive'] = json.load(f)
            
            return True
        except Exception as e:
            print(f"Comprehensive test suite failed: {e}")
            return False
    
    def run_unit_tests(self):
        """Run the unit test suite"""
        print("\n" + "="*80)
        print("RUNNING UNIT TESTS")
        print("="*80)
        
        try:
            from unit_tests import run_unit_tests
            result = run_unit_tests()
            
            # Store results
            self.test_results['unit_tests'] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                'failures_details': [(str(test), traceback) for test, traceback in result.failures],
                'errors_details': [(str(test), traceback) for test, traceback in result.errors]
            }
            
            return True
        except Exception as e:
            print(f"Unit tests failed: {e}")
            return False
    
    async def run_performance_tests(self):
        """Run the performance test suite"""
        print("\n" + "="*80)
        print("RUNNING PERFORMANCE TESTS")
        print("="*80)
        
        try:
            from performance_tests import PerformanceTestSuite
            test_suite = PerformanceTestSuite()
            await test_suite.run_performance_tests()
            
            # Read results
            if os.path.exists('performance_test_report.json'):
                with open('performance_test_report.json', 'r') as f:
                    self.test_results['performance'] = json.load(f)
            
            return True
        except Exception as e:
            print(f"Performance tests failed: {e}")
            return False
    
    async def run_mcp_server_tests(self):
        """Run MCP server specific tests"""
        print("\n" + "="*80)
        print("RUNNING MCP SERVER TESTS")
        print("="*80)
        
        try:
            # Test MCP server startup
            import subprocess
            import time
            
            # Start MCP server in background
            process = subprocess.Popen(
                [sys.executable, 'mcp_server_standalone.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is running
            if process.poll() is None:
                print("✓ MCP server started successfully")
                
                # Test basic functionality
                try:
                    # Import and test MCP server
                    sys.path.insert(0, os.path.dirname(__file__))
                    from mcp_server_standalone import LangFlowConnectMCPServer
                    
                    server = LangFlowConnectMCPServer()
                    
                    # Test tool registration
                    tools = server.fastmcp.tools
                    expected_tools = [
                        'read_file', 'write_file', 'list_files', 'analyze_code',
                        'suggest_refactoring', 'track_cost', 'get_health_status',
                        'get_performance_metrics', 'get_cost_summary', 'optimize_workflow',
                        'get_system_status', 'get_workspace_info'
                    ]
                    
                    registered_tools = [tool.name for tool in tools]
                    missing_tools = [tool for tool in expected_tools if tool not in registered_tools]
                    
                    if not missing_tools:
                        print("✓ All expected MCP tools are registered")
                        self.test_results['mcp_server'] = {
                            'status': 'success',
                            'tools_registered': len(registered_tools),
                            'expected_tools': expected_tools,
                            'registered_tools': registered_tools
                        }
                    else:
                        print(f"✗ Missing MCP tools: {missing_tools}")
                        self.test_results['mcp_server'] = {
                            'status': 'failed',
                            'missing_tools': missing_tools
                        }
                
                except Exception as e:
                    print(f"✗ MCP server test failed: {e}")
                    self.test_results['mcp_server'] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                
                # Terminate server
                process.terminate()
                process.wait()
            else:
                print("✗ MCP server failed to start")
                stdout, stderr = process.communicate()
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                self.test_results['mcp_server'] = {
                    'status': 'failed',
                    'error': 'Server failed to start'
                }
            
            return True
        except Exception as e:
            print(f"MCP server tests failed: {e}")
            self.test_results['mcp_server'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def run_integration_tests(self):
        """Run integration tests"""
        print("\n" + "="*80)
        print("RUNNING INTEGRATION TESTS")
        print("="*80)
        
        try:
            # Test module interactions
            from modules.module_1_main import WorkspaceManager, CodeAnalyzer
            from modules.module_3_economy import CostTracker, BudgetManager
            from modules.module_2_support import HealthMonitor
            
            # Initialize components
            workspace_manager = WorkspaceManager()
            code_analyzer = CodeAnalyzer()
            cost_tracker = CostTracker()
            budget_manager = BudgetManager()
            health_monitor = HealthMonitor()
            
            await workspace_manager.initialize()
            await code_analyzer.initialize()
            await cost_tracker.initialize()
            await budget_manager.initialize()
            await health_monitor.initialize()
            
            try:
                # Test integrated workflow
                import tempfile
                import os
                
                # Create temporary workspace
                temp_dir = tempfile.mkdtemp()
                
                # Test file operations
                test_file = os.path.join(temp_dir, 'integration_test.py')
                test_code = '''
def test_function():
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42
'''
                
                await workspace_manager.write_file(test_file, test_code)
                content = await workspace_manager.read_file(test_file)
                
                # Test code analysis
                analysis = await code_analyzer.analyze_code(test_code, 'python')
                
                # Test cost tracking
                await cost_tracker.track_token_usage('integration_test', 100, 0.001)
                await budget_manager.set_budget_limit('daily', 10.0)
                
                # Test health monitoring
                health_status = await health_monitor.check_system_health()
                
                # Verify integration
                assert content == test_code
                assert analysis['functions'] > 0
                assert analysis['classes'] > 0
                
                cost_summary = await cost_tracker.get_cost_summary()
                budget_status = await budget_manager.get_budget_status()
                
                assert cost_summary['total_cost'] > 0
                assert 'daily' in budget_status
                assert health_status['status'] in ['healthy', 'warning', 'critical']
                
                print("✓ Integration tests passed")
                self.test_results['integration'] = {
                    'status': 'success',
                    'components_tested': ['workspace_manager', 'code_analyzer', 'cost_tracker', 'budget_manager', 'health_monitor']
                }
                
                # Cleanup
                import shutil
                shutil.rmtree(temp_dir)
                
            finally:
                # Cleanup components
                await workspace_manager.cleanup()
                await code_analyzer.cleanup()
                await cost_tracker.cleanup()
                await budget_manager.cleanup()
                await health_monitor.cleanup()
            
            return True
        except Exception as e:
            print(f"Integration tests failed: {e}")
            self.test_results['integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def generate_final_report(self):
        """Generate final comprehensive test report"""
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_duration_seconds': total_duration,
            'test_suites': self.test_results,
            'summary': self.generate_summary()
        }
        
        # Save report
        with open('final_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_final_summary(report)
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            'total_suites': len(self.test_results),
            'successful_suites': 0,
            'failed_suites': 0,
            'overall_status': 'unknown'
        }
        
        for suite_name, results in self.test_results.items():
            if suite_name == 'unit_tests':
                if results.get('success_rate', 0) >= 90:  # 90% success rate threshold
                    summary['successful_suites'] += 1
                else:
                    summary['failed_suites'] += 1
            elif suite_name == 'comprehensive':
                if results.get('test_stats', {}).get('failed_tests', 0) == 0:
                    summary['successful_suites'] += 1
                else:
                    summary['failed_suites'] += 1
            elif suite_name in ['performance', 'mcp_server', 'integration']:
                if results.get('status') == 'success':
                    summary['successful_suites'] += 1
                else:
                    summary['failed_suites'] += 1
        
        # Determine overall status
        if summary['failed_suites'] == 0:
            summary['overall_status'] = 'PASSED'
        elif summary['successful_suites'] > summary['failed_suites']:
            summary['overall_status'] = 'PARTIAL'
        else:
            summary['overall_status'] = 'FAILED'
        
        return summary
    
    def print_final_summary(self, report: Dict[str, Any]):
        """Print final test summary"""
        print("\n" + "="*80)
        print("FINAL TEST REPORT")
        print("="*80)
        
        summary = report['summary']
        print(f"\nOverall Status: {summary['overall_status']}")
        print(f"Total Duration: {report['total_duration_seconds']:.2f} seconds")
        print(f"Test Suites: {summary['total_suites']}")
        print(f"Successful: {summary['successful_suites']}")
        print(f"Failed: {summary['failed_suites']}")
        
        print(f"\nDetailed Results:")
        for suite_name, results in self.test_results.items():
            if suite_name == 'unit_tests':
                success_rate = results.get('success_rate', 0)
                print(f"  {suite_name}: {success_rate:.1f}% success rate")
            elif suite_name == 'comprehensive':
                stats = results.get('test_stats', {})
                passed = stats.get('passed_tests', 0)
                failed = stats.get('failed_tests', 0)
                total = stats.get('total_tests', 0)
                print(f"  {suite_name}: {passed}/{total} tests passed")
            elif suite_name in ['performance', 'mcp_server', 'integration']:
                status = results.get('status', 'unknown')
                print(f"  {suite_name}: {status}")
        
        print(f"\nDetailed report saved to: final_test_report.json")
        print("="*80)
    
    async def run_all_tests(self, test_types: List[str] = None):
        """Run all test suites"""
        self.start_time = time.time()
        
        if test_types is None:
            test_types = ['comprehensive', 'unit', 'performance', 'mcp', 'integration']
        
        print(f"Starting test execution for: {', '.join(test_types)}")
        
        # Run requested test suites
        if 'comprehensive' in test_types:
            await self.run_comprehensive_tests()
        
        if 'unit' in test_types:
            self.run_unit_tests()
        
        if 'performance' in test_types:
            await self.run_performance_tests()
        
        if 'mcp' in test_types:
            await self.run_mcp_server_tests()
        
        if 'integration' in test_types:
            await self.run_integration_tests()
        
        # Generate final report
        self.generate_final_report()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run LangFlow Connect test suites')
    parser.add_argument(
        '--test-types',
        nargs='+',
        choices=['comprehensive', 'unit', 'performance', 'mcp', 'integration', 'all'],
        default=['all'],
        help='Types of tests to run'
    )
    
    args = parser.parse_args()
    
    # Handle 'all' option
    if 'all' in args.test_types:
        test_types = ['comprehensive', 'unit', 'performance', 'mcp', 'integration']
    else:
        test_types = args.test_types
    
    # Run tests
    runner = TestRunner()
    asyncio.run(runner.run_all_tests(test_types))


if __name__ == '__main__':
    main() 