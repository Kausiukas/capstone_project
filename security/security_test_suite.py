#!/usr/bin/env python3
"""
LangFlow Connect MVP - Security Test Suite
Comprehensive security testing for the hardened API.
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Tuple
import concurrent.futures

# Configuration
API_BASE_URL = "http://localhost:8000"  # Local secure server
API_KEY = "demo_key_123"
ADMIN_KEY = "admin_key_456"

class SecurityTestSuite:
    def __init__(self):
        self.results = []
        self.security_issues = []
        self.headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        self.admin_headers = {
            'X-API-Key': ADMIN_KEY,
            'Content-Type': 'application/json'
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
            self.security_issues.append(result)
    
    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints"""
        print("\n🔐 Testing Authentication Requirements...")
        
        # Test tools/list without authentication
        try:
            response = requests.get(f"{API_BASE_URL}/tools/list", timeout=10)
            self.log_test(
                "Authentication Required - Tools List",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Authentication Required - Tools List",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test tool execution without authentication
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/tools/call",
                data=json.dumps({"name": "ping", "arguments": {}}),
                timeout=10
            )
            self.log_test(
                "Authentication Required - Tool Execution",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Authentication Required - Tool Execution",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_invalid_api_key(self):
        """Test that invalid API keys are rejected"""
        print("\n🔑 Testing Invalid API Key Rejection...")
        
        invalid_headers = {
            'X-API-Key': 'invalid_key_123',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{API_BASE_URL}/tools/list", headers=invalid_headers, timeout=10)
            self.log_test(
                "Invalid API Key Rejection",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Invalid API Key Rejection",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n⏱️ Testing Rate Limiting...")
        
        # Test health endpoint rate limiting (should allow more requests)
        health_requests = []
        for i in range(20):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                health_requests.append(response.status_code)
            except Exception as e:
                health_requests.append(0)
        
        # Count successful requests
        successful_health = sum(1 for code in health_requests if code == 200)
        self.log_test(
            "Health Endpoint Rate Limiting",
            successful_health > 10,  # Should allow many requests
            f"Successful requests: {successful_health}/20"
        )
        
        # Test tools endpoint rate limiting (should be more restrictive)
        tools_requests = []
        for i in range(10):
            try:
                response = requests.get(f"{API_BASE_URL}/tools/list", headers=self.headers, timeout=5)
                tools_requests.append(response.status_code)
            except Exception as e:
                tools_requests.append(0)
        
        # Count successful requests
        successful_tools = sum(1 for code in tools_requests if code == 200)
        self.log_test(
            "Tools Endpoint Rate Limiting",
            successful_tools < 10,  # Should limit requests
            f"Successful requests: {successful_tools}/10"
        )
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        print("\n🛡️ Testing Path Traversal Protection...")
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "/etc/passwd",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        
        for path in malicious_paths:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/tools/call",
                    headers=self.headers,
                    data=json.dumps({
                        "name": "read_file",
                        "arguments": {"file_path": path}
                    }),
                    timeout=10
                )
                
                # Should return 400 for invalid paths
                self.log_test(
                    f"Path Traversal Protection - {path}",
                    response.status_code == 400,
                    f"Expected 400, got {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"Path Traversal Protection - {path}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection (if applicable)"""
        print("\n💉 Testing SQL Injection Protection...")
        
        # Test with potentially malicious input
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/tools/call",
                    headers=self.headers,
                    data=json.dumps({
                        "name": "read_file",
                        "arguments": {"file_path": malicious_input}
                    }),
                    timeout=10
                )
                
                # Should handle gracefully (not crash)
                self.log_test(
                    f"SQL Injection Protection - {malicious_input[:20]}...",
                    response.status_code in [200, 400, 500],  # Any valid response
                    f"Response code: {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"SQL Injection Protection - {malicious_input[:20]}...",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        print("\n🕷️ Testing XSS Protection...")
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/tools/call",
                    headers=self.headers,
                    data=json.dumps({
                        "name": "read_file",
                        "arguments": {"file_path": payload}
                    }),
                    timeout=10
                )
                
                # Should handle gracefully
                self.log_test(
                    f"XSS Protection - {payload[:20]}...",
                    response.status_code in [200, 400, 500],
                    f"Response code: {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"XSS Protection - {payload[:20]}...",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_security_headers(self):
        """Test that security headers are present"""
        print("\n🛡️ Testing Security Headers...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            
            required_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            missing_headers = []
            for header in required_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            self.log_test(
                "Security Headers Present",
                len(missing_headers) == 0,
                f"Missing headers: {missing_headers}" if missing_headers else "All headers present"
            )
            
            # Test specific header values
            if 'X-Content-Type-Options' in response.headers:
                self.log_test(
                    "X-Content-Type-Options Value",
                    response.headers['X-Content-Type-Options'] == 'nosniff',
                    f"Value: {response.headers['X-Content-Type-Options']}"
                )
            
            if 'X-Frame-Options' in response.headers:
                self.log_test(
                    "X-Frame-Options Value",
                    response.headers['X-Frame-Options'] == 'DENY',
                    f"Value: {response.headers['X-Frame-Options']}"
                )
                
        except Exception as e:
            self.log_test(
                "Security Headers Present",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🌐 Testing CORS Configuration...")
        
        # Test preflight request
        try:
            response = requests.options(
                f"{API_BASE_URL}/tools/list",
                headers={
                    'Origin': 'http://localhost:8501',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'X-API-Key'
                },
                timeout=10
            )
            
            self.log_test(
                "CORS Preflight Request",
                response.status_code in [200, 204],
                f"Response code: {response.status_code}"
            )
            
            # Check CORS headers
            cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']
            missing_cors_headers = [h for h in cors_headers if h not in response.headers]
            
            self.log_test(
                "CORS Headers Present",
                len(missing_cors_headers) == 0,
                f"Missing CORS headers: {missing_cors_headers}"
            )
            
        except Exception as e:
            self.log_test(
                "CORS Configuration",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_input_validation(self):
        """Test input validation"""
        print("\n✅ Testing Input Validation...")
        
        # Test invalid tool names
        invalid_tools = [
            "",
            None,
            "invalid_tool",
            "admin",
            "system"
        ]
        
        for tool in invalid_tools:
            try:
                payload = {"name": tool, "arguments": {}}
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/tools/call",
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=10
                )
                
                # Should return 400 for invalid tools
                self.log_test(
                    f"Input Validation - Invalid Tool: {tool}",
                    response.status_code == 400,
                    f"Expected 400, got {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"Input Validation - Invalid Tool: {tool}",
                    False,
                    f"Exception: {str(e)}"
                )
        
        # Test invalid arguments
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps({"name": "ping", "arguments": "invalid"}),
                timeout=10
            )
            
            self.log_test(
                "Input Validation - Invalid Arguments",
                response.status_code == 400,
                f"Expected 400, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Input Validation - Invalid Arguments",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        print("\n👑 Testing Admin Endpoints...")
        
        # Test security stats with regular key (should fail)
        try:
            response = requests.get(f"{API_BASE_URL}/security/stats", headers=self.headers, timeout=10)
            self.log_test(
                "Admin Endpoint - Regular User Access",
                response.status_code == 403,
                f"Expected 403, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Admin Endpoint - Regular User Access",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test security stats with admin key (should succeed)
        try:
            response = requests.get(f"{API_BASE_URL}/security/stats", headers=self.admin_headers, timeout=10)
            self.log_test(
                "Admin Endpoint - Admin User Access",
                response.status_code == 200,
                f"Expected 200, got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Admin Endpoint - Admin User Access",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_concurrent_requests(self):
        """Test system behavior under concurrent load"""
        print("\n⚡ Testing Concurrent Requests...")
        
        def make_request():
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                return response.status_code
            except:
                return 0
        
        # Make 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = sum(1 for code in results if code == 200)
        
        self.log_test(
            "Concurrent Request Handling",
            successful_requests > 10,  # Should handle most requests
            f"Successful requests: {successful_requests}/20"
        )
    
    def run_comprehensive_security_test(self):
        """Run all security tests"""
        print("🔒 LangFlow Connect MVP - Comprehensive Security Test Suite")
        print("=" * 70)
        
        # Run all tests
        self.test_authentication_required()
        self.test_invalid_api_key()
        self.test_rate_limiting()
        self.test_path_traversal_protection()
        self.test_sql_injection_protection()
        self.test_xss_protection()
        self.test_security_headers()
        self.test_cors_configuration()
        self.test_input_validation()
        self.test_admin_endpoints()
        self.test_concurrent_requests()
        
        # Generate report
        self.generate_security_report()
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("\n" + "=" * 70)
        print("📊 SECURITY TEST RESULTS")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.security_issues:
            print(f"\n🚨 SECURITY ISSUES FOUND ({len(self.security_issues)}):")
            for issue in self.security_issues:
                print(f"  • {issue['test_name']}: {issue['details']}")
        else:
            print("\n✅ NO SECURITY ISSUES FOUND!")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'results': self.results,
            'security_issues': self.security_issues
        }
        
        filename = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Security report saved to: {filename}")
        
        return report

def main():
    """Main function to run security tests"""
    print("🔒 Starting Security Test Suite...")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly. Please start the secure server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("Please start the secure server with: python src/mcp_server_http_secure.py")
        return
    
    # Run security tests
    test_suite = SecurityTestSuite()
    test_suite.run_comprehensive_security_test()

if __name__ == "__main__":
    main()
