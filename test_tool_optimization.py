#!/usr/bin/env python3
"""
LangFlow Connect MVP - Tool Optimization and Configuration Tests
This script tests and optimizes all tools and resources for better performance and reliability.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any
import threading
import concurrent.futures

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"
TIMEOUT = 30
MAX_RETRIES = 3

class ToolOptimizationTester:
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.error_log = []
        self.headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
    
    def log_error(self, tool: str, error: str, context: str = ""):
        """Log errors for analysis"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool,
            'error': error,
            'context': context
        }
        self.error_log.append(error_entry)
        print(f"❌ {tool}: {error}")
    
    def test_api_connectivity(self) -> bool:
        """Test basic API connectivity"""
        print("🔍 Testing API Connectivity...")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                print("✅ API connectivity: SUCCESS")
                return True
            else:
                self.log_error("API", f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("API", f"Connection failed: {str(e)}")
            return False
    
    def test_tool_list(self) -> Dict[str, Any]:
        """Test tools/list endpoint and analyze available tools"""
        print("🛠️ Testing Tools List...")
        try:
            response = requests.get(f"{API_BASE_URL}/tools/list", headers=self.headers, timeout=10)
            if response.status_code == 200:
                tools_data = response.json()
                tools = tools_data.get('tools', [])
                print(f"✅ Tools list: SUCCESS ({len(tools)} tools found)")
                
                # Analyze tool schemas
                tool_analysis = {}
                for tool in tools:
                    tool_analysis[tool['name']] = {
                        'description': tool.get('description', ''),
                        'has_schema': 'inputSchema' in tool,
                        'schema_properties': len(tool.get('inputSchema', {}).get('properties', {})),
                        'required_fields': len(tool.get('inputSchema', {}).get('required', []))
                    }
                
                return {
                    'success': True,
                    'tools_count': len(tools),
                    'tools': tools,
                    'analysis': tool_analysis
                }
            else:
                self.log_error("Tools List", f"Failed: {response.status_code}")
                return {'success': False, 'error': f"Status {response.status_code}"}
        except Exception as e:
            self.log_error("Tools List", f"Exception: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_tool_execution(self, tool_name: str, arguments: Dict[str, Any], expected_success: bool = True) -> Dict[str, Any]:
        """Test individual tool execution with performance measurement"""
        print(f"⚡ Testing {tool_name}...")
        
        start_time = time.time()
        try:
            payload = {
                'name': tool_name,
                'arguments': arguments
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=TIMEOUT
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                success = True
                print(f"✅ {tool_name}: SUCCESS ({response_time:.2f}ms)")
            else:
                result = {'error': f"Status {response.status_code}: {response.text}"}
                success = False
                print(f"❌ {tool_name}: FAILED ({response_time:.2f}ms)")
            
            return {
                'tool': tool_name,
                'success': success,
                'response_time': response_time,
                'status_code': response.status_code,
                'result': result,
                'expected_success': expected_success
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            self.log_error(tool_name, f"Exception: {str(e)}")
            return {
                'tool': tool_name,
                'success': False,
                'response_time': response_time,
                'error': str(e),
                'expected_success': expected_success
            }
    
    def test_ping_tool(self) -> Dict[str, Any]:
        """Test ping tool with various scenarios"""
        print("🏓 Testing Ping Tool...")
        
        # Test basic ping
        basic_result = self.test_tool_execution("ping", {})
        
        # Test ping with retries
        retry_results = []
        for i in range(3):
            result = self.test_tool_execution("ping", {})
            retry_results.append(result)
        
        # Calculate average response time
        avg_response_time = sum(r['response_time'] for r in retry_results) / len(retry_results)
        
        return {
            'basic_test': basic_result,
            'retry_tests': retry_results,
            'average_response_time': avg_response_time,
            'success_rate': sum(1 for r in retry_results if r['success']) / len(retry_results)
        }
    
    def test_list_files_tool(self) -> Dict[str, Any]:
        """Test list_files tool with various directory paths"""
        print("📁 Testing List Files Tool...")
        
        test_paths = [
            ".",  # Current directory
            "/",  # Root directory
            "/tmp",  # Temp directory
            "nonexistent_path",  # Invalid path
            "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"  # Windows path
        ]
        
        results = {}
        for path in test_paths:
            result = self.test_tool_execution("list_files", {"directory": path})
            results[path] = result
            
            # Analyze the result
            if result['success']:
                print(f"✅ list_files ({path}): SUCCESS")
            else:
                print(f"❌ list_files ({path}): FAILED")
        
        return results
    
    def test_read_file_tool(self) -> Dict[str, Any]:
        """Test read_file tool with various file paths"""
        print("📖 Testing Read File Tool...")
        
        test_files = [
            "README.md",  # Common file
            "requirements.txt",  # Common file
            "nonexistent_file.txt",  # Invalid file
            "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md",  # Windows path
            "/etc/passwd",  # System file (should fail)
            "src/mcp_server_http.py"  # Source file
        ]
        
        results = {}
        for file_path in test_files:
            result = self.test_tool_execution("read_file", {"file_path": file_path})
            results[file_path] = result
            
            if result['success']:
                print(f"✅ read_file ({file_path}): SUCCESS")
            else:
                print(f"❌ read_file ({file_path}): FAILED")
        
        return results
    
    def test_system_status_tool(self) -> Dict[str, Any]:
        """Test get_system_status tool"""
        print("💻 Testing System Status Tool...")
        
        # Test multiple times to check consistency
        results = []
        for i in range(3):
            result = self.test_tool_execution("get_system_status", {})
            results.append(result)
        
        # Analyze system metrics
        successful_results = [r for r in results if r['success']]
        if successful_results:
            avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results)
            success_rate = len(successful_results) / len(results)
        else:
            avg_response_time = 0
            success_rate = 0
        
        return {
            'tests': results,
            'average_response_time': avg_response_time,
            'success_rate': success_rate,
            'total_tests': len(results)
        }
    
    def test_analyze_code_tool(self) -> Dict[str, Any]:
        """Test analyze_code tool with various file types"""
        print("🔍 Testing Analyze Code Tool...")
        
        test_files = [
            "src/mcp_server_http.py",  # Python file
            "streamlit_app.py",  # Python file
            "README.md",  # Markdown file
            "requirements.txt",  # Text file
            "nonexistent_file.py",  # Invalid file
            "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_http.py"  # Windows path
        ]
        
        results = {}
        for file_path in test_files:
            result = self.test_tool_execution("analyze_code", {"file_path": file_path})
            results[file_path] = result
            
            if result['success']:
                print(f"✅ analyze_code ({file_path}): SUCCESS")
            else:
                print(f"❌ analyze_code ({file_path}): FAILED")
        
        return results
    
    def run_performance_test(self, tool_name: str, arguments: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """Run performance test for a specific tool"""
        print(f"🏃‍♂️ Running Performance Test for {tool_name} ({iterations} iterations)...")
        
        response_times = []
        success_count = 0
        errors = []
        
        for i in range(iterations):
            result = self.test_tool_execution(tool_name, arguments)
            response_times.append(result['response_time'])
            
            if result['success']:
                success_count += 1
            else:
                errors.append(result.get('error', 'Unknown error'))
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            success_rate = success_count / iterations
        else:
            avg_time = min_time = max_time = 0
            success_rate = 0
        
        return {
            'tool': tool_name,
            'iterations': iterations,
            'success_count': success_count,
            'success_rate': success_rate,
            'average_response_time': avg_time,
            'min_response_time': min_time,
            'max_response_time': max_time,
            'errors': errors
        }
    
    def run_load_test(self, concurrent_requests: int = 10) -> Dict[str, Any]:
        """Run load test with concurrent requests"""
        print(f"🔄 Running Load Test ({concurrent_requests} concurrent requests)...")
        
        def make_request():
            return self.test_tool_execution("ping", {})
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        
        success_count = sum(1 for r in results if r['success'])
        success_rate = success_count / len(results)
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        
        return {
            'concurrent_requests': concurrent_requests,
            'total_time': total_time,
            'success_count': success_count,
            'success_rate': success_rate,
            'average_response_time': avg_response_time,
            'requests_per_second': len(results) / (total_time / 1000)
        }
    
    def generate_optimization_recommendations(self) -> Dict[str, Any]:
        """Generate optimization recommendations based on test results"""
        print("📊 Generating Optimization Recommendations...")
        
        recommendations = {
            'performance': [],
            'reliability': [],
            'security': [],
            'user_experience': []
        }
        
        # Analyze performance data
        if 'ping_performance' in self.performance_data:
            ping_data = self.performance_data['ping_performance']
            if ping_data['average_response_time'] > 500:
                recommendations['performance'].append({
                    'issue': 'High ping response time',
                    'current': f"{ping_data['average_response_time']:.2f}ms",
                    'target': '<500ms',
                    'action': 'Optimize API server performance'
                })
        
        # Analyze error patterns
        if self.error_log:
            error_types = {}
            for error in self.error_log:
                error_type = error['tool']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for tool, count in error_types.items():
                if count > 3:
                    recommendations['reliability'].append({
                        'issue': f'High error rate for {tool}',
                        'current': f"{count} errors",
                        'target': '<3 errors',
                        'action': f'Investigate and fix {tool} reliability issues'
                    })
        
        # File path handling issues
        file_path_errors = [e for e in self.error_log if 'file' in e['error'].lower() or 'path' in e['error'].lower()]
        if file_path_errors:
            recommendations['user_experience'].append({
                'issue': 'File path handling issues',
                'current': f"{len(file_path_errors)} path-related errors",
                'target': '0 path errors',
                'action': 'Improve file path validation and error handling'
            })
        
        return recommendations
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print("🚀 Starting Comprehensive Tool Optimization Test Suite...")
        print("=" * 60)
        
        # Test API connectivity
        if not self.test_api_connectivity():
            print("❌ API connectivity failed. Aborting tests.")
            return {'success': False, 'error': 'API connectivity failed'}
        
        # Test tools list
        tools_result = self.test_tool_list()
        self.results['tools_list'] = tools_result
        
        # Test individual tools
        print("\n" + "=" * 60)
        print("🧪 Testing Individual Tools...")
        
        self.results['ping_tool'] = self.test_ping_tool()
        self.results['list_files_tool'] = self.test_list_files_tool()
        self.results['read_file_tool'] = self.test_read_file_tool()
        self.results['system_status_tool'] = self.test_system_status_tool()
        self.results['analyze_code_tool'] = self.test_analyze_code_tool()
        
        # Performance tests
        print("\n" + "=" * 60)
        print("🏃‍♂️ Running Performance Tests...")
        
        self.performance_data['ping_performance'] = self.run_performance_test("ping", {}, 10)
        self.performance_data['system_status_performance'] = self.run_performance_test("get_system_status", {}, 5)
        
        # Load test
        print("\n" + "=" * 60)
        print("🔄 Running Load Tests...")
        
        self.performance_data['load_test'] = self.run_load_test(10)
        
        # Generate recommendations
        print("\n" + "=" * 60)
        print("📊 Generating Recommendations...")
        
        recommendations = self.generate_optimization_recommendations()
        
        # Compile final report
        report = {
            'timestamp': datetime.now().isoformat(),
            'api_url': API_BASE_URL,
            'success': True,
            'results': self.results,
            'performance_data': self.performance_data,
            'error_log': self.error_log,
            'recommendations': recommendations,
            'summary': self.generate_summary()
        }
        
        return report
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = 0
        successful_tests = 0
        
        # Count tests from results
        for tool_name, result in self.results.items():
            if isinstance(result, dict):
                if 'success' in result:
                    total_tests += 1
                    if result['success']:
                        successful_tests += 1
                elif 'tests' in result:
                    total_tests += len(result['tests'])
                    successful_tests += sum(1 for t in result['tests'] if t['success'])
        
        # Count performance tests
        for perf_name, perf_data in self.performance_data.items():
            if 'iterations' in perf_data:
                total_tests += perf_data['iterations']
                successful_tests += perf_data['success_count']
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_errors': len(self.error_log),
            'performance_score': self.calculate_performance_score()
        }
    
    def calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self.performance_data:
            return 0.0
        
        scores = []
        
        # Response time score
        for perf_data in self.performance_data.values():
            if 'average_response_time' in perf_data:
                response_time = perf_data['average_response_time']
                if response_time < 200:
                    scores.append(100)
                elif response_time < 500:
                    scores.append(80)
                elif response_time < 1000:
                    scores.append(60)
                else:
                    scores.append(40)
            
            # Success rate score
            if 'success_rate' in perf_data:
                success_rate = perf_data['success_rate']
                scores.append(success_rate * 100)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tool_optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filename}")
        return filename

def main():
    """Main function to run the tool optimization tests"""
    print("🎯 LangFlow Connect MVP - Tool Optimization and Configuration Tests")
    print("=" * 70)
    
    tester = ToolOptimizationTester()
    
    try:
        # Run comprehensive test suite
        report = tester.run_comprehensive_test_suite()
        
        # Display summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        summary = report['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Performance Score: {summary['performance_score']:.1f}/100")
        
        # Display recommendations
        if report['recommendations']:
            print("\n" + "=" * 70)
            print("💡 OPTIMIZATION RECOMMENDATIONS")
            print("=" * 70)
            
            for category, recs in report['recommendations'].items():
                if recs:
                    print(f"\n{category.upper()}:")
                    for rec in recs:
                        print(f"  • {rec['issue']}")
                        print(f"    Current: {rec['current']}")
                        print(f"    Target: {rec['target']}")
                        print(f"    Action: {rec['action']}")
        
        # Save report
        filename = tester.save_report(report)
        
        print(f"\n✅ Test suite completed successfully!")
        print(f"📄 Detailed report saved to: {filename}")
        
        return report
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    main()
