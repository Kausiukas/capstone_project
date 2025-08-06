#!/usr/bin/env python3
"""
Automated MVP Testing Script
Tests the deployed LangFlow Connect MCP Server
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class MVPTester:
    def __init__(self, base_url: str = "https://capstone-project-i1xm.onrender.com"):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': 'demo_key_123',
            'Content-Type': 'application/json'
        }
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') in ['running', 'healthy'] and data.get('version') == '1.0.0':
                    self.log_test("Health Endpoint", True)
                    return True
                else:
                    self.log_test("Health Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Error: {str(e)}")
            return False
            
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        try:
            response = requests.get(self.base_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'LangFlow Connect' in data['message']:
                    self.log_test("Root Endpoint", True)
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False
            
    def test_tools_list(self) -> bool:
        """Test the tools list endpoint"""
        try:
            response = requests.get(f"{self.base_url}/tools/list", headers=self.headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Handle both array format and object with 'tools' key
                tools = data if isinstance(data, list) else data.get('tools', [])
                if isinstance(tools, list) and len(tools) > 0:
                    self.log_test("Tools List", True, f"Found {len(tools)} tools")
                    return True
                else:
                    self.log_test("Tools List", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Tools List", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Tools List", False, f"Error: {str(e)}")
            return False
            
    def test_ping_tool(self) -> bool:
        """Test the ping tool"""
        try:
            payload = {
                'name': 'ping',
                'arguments': {}
            }
            response = requests.post(
                f"{self.base_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                result = data.get('result', data)
                if isinstance(result, dict) and 'content' in result:
                    content = result['content']
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get('text', '')
                        if 'pong' in text_content.lower():
                            self.log_test("Ping Tool", True)
                            return True
                elif isinstance(result, str) and 'pong' in result.lower():
                    self.log_test("Ping Tool", True)
                    return True
                else:
                    self.log_test("Ping Tool", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Ping Tool", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Ping Tool", False, f"Error: {str(e)}")
            return False
            
    def test_list_files_tool(self) -> bool:
        """Test the list files tool"""
        try:
            payload = {
                'name': 'list_files',
                'arguments': {'path': '.'}
            }
            response = requests.post(
                f"{self.base_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                result = data.get('result', data)
                if isinstance(result, dict) and 'content' in result:
                    content = result['content']
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get('text', '')
                        if 'Files in' in text_content or '📁' in text_content:
                            self.log_test("List Files Tool", True, f"Found file listing")
                            return True
                elif isinstance(result, list):
                    self.log_test("List Files Tool", True, f"Found {len(result)} files")
                    return True
                else:
                    self.log_test("List Files Tool", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("List Files Tool", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("List Files Tool", False, f"Error: {str(e)}")
            return False
            
    def test_system_status_tool(self) -> bool:
        """Test the system status tool"""
        try:
            payload = {
                'name': 'get_system_status',
                'arguments': {}
            }
            response = requests.post(
                f"{self.base_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                result = data.get('result', data)
                if isinstance(result, dict):
                    self.log_test("System Status Tool", True)
                    return True
                else:
                    self.log_test("System Status Tool", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("System Status Tool", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("System Status Tool", False, f"Error: {str(e)}")
            return False
            
    def test_error_handling(self) -> bool:
        """Test error handling with invalid requests"""
        try:
            # Test invalid tool name
            payload = {
                'name': 'invalid_tool',
                'arguments': {}
            }
            response = requests.post(
                f"{self.base_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            if response.status_code in [400, 404, 422]:
                self.log_test("Error Handling", True, "Properly handled invalid tool")
                return True
            else:
                self.log_test("Error Handling", False, f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
            
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 Starting MVP Automated Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_tools_list,
            self.test_ping_tool,
            self.test_list_files_tool,
            self.test_system_status_tool,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Small delay between tests
            
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        success_rate = (passed / total) * 100
        if success_rate >= 80:
            print("🎉 MVP is working excellently!")
        elif success_rate >= 60:
            print("⚠️  MVP has some issues but is functional")
        else:
            print("❌ MVP has significant issues")
            
        return {
            'total_tests': total,
            'passed_tests': passed,
            'success_rate': success_rate,
            'test_results': self.test_results,
            'deployment_url': self.base_url
        }

def main():
    """Main function"""
    tester = MVPTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('mvp_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\n📄 Results saved to: mvp_test_results.json")
    print(f"🌐 Deployment URL: {results['deployment_url']}")
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main() 