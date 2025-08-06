#!/usr/bin/env python3
"""
Test Security Headers on LangFlow Connect MVP API
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def test_security_headers():
    """Test security headers on the API"""
    print("🔒 Testing Security Headers on LangFlow Connect MVP API")
    print("=" * 60)
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        
        # Check security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        print("\n🛡️ Security Headers Check:")
        print("-" * 40)
        
        found_headers = []
        missing_headers = []
        
        for header in security_headers:
            if header in response.headers:
                value = response.headers[header]
                print(f"✅ {header}: {value}")
                found_headers.append(header)
            else:
                print(f"❌ {header}: MISSING")
                missing_headers.append(header)
        
        # Summary
        print(f"\n📊 Security Headers Summary:")
        print(f"Found: {len(found_headers)}/{len(security_headers)}")
        print(f"Missing: {len(missing_headers)}")
        
        if missing_headers:
            print(f"\n🚨 Missing Headers: {', '.join(missing_headers)}")
        else:
            print("\n✅ All security headers present!")
        
        # Test authenticated endpoint
        print(f"\n🔐 Testing Authenticated Endpoint:")
        headers = {'X-API-Key': API_KEY}
        auth_response = requests.get(f"{API_BASE_URL}/tools/list", headers=headers, timeout=10)
        print(f"Tools endpoint: {auth_response.status_code}")
        
        # Check headers on authenticated response
        auth_found = []
        for header in security_headers:
            if header in auth_response.headers:
                auth_found.append(header)
        
        print(f"Security headers on authenticated response: {len(auth_found)}/{len(security_headers)}")
        
        return {
            'health_status': response.status_code,
            'found_headers': found_headers,
            'missing_headers': missing_headers,
            'auth_status': auth_response.status_code,
            'auth_headers_found': len(auth_found)
        }
        
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return None

def test_security_headers_enhanced():
    """Test with enhanced security headers"""
    print("\n🔒 Testing Enhanced Security Headers")
    print("=" * 60)
    
    # Test various endpoints
    endpoints = [
        "/health",
        "/tools/list",
        "/api/v1/tools/call"
    ]
    
    headers = {'X-API-Key': API_KEY}
    
    for endpoint in endpoints:
        try:
            if endpoint == "/health":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            elif endpoint == "/tools/list":
                response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
            else:
                # Test tool execution
                payload = {"name": "ping", "arguments": {}}
                response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json=payload, timeout=10)
            
            print(f"\n📡 {endpoint}: {response.status_code}")
            
            # Check for security headers
            security_headers_present = []
            for header in ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']:
                if header in response.headers:
                    security_headers_present.append(header)
            
            print(f"   Security headers: {len(security_headers_present)}/3")
            
            if len(security_headers_present) == 3:
                print(f"   ✅ All critical headers present")
            else:
                print(f"   ⚠️  Missing: {set(['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']) - set(security_headers_present)}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def generate_security_report():
    """Generate security headers report"""
    print("\n📋 Generating Security Headers Report")
    print("=" * 60)
    
    # Test current headers
    results = test_security_headers()
    
    if results:
        report = {
            'timestamp': datetime.now().isoformat(),
            'api_url': API_BASE_URL,
            'results': results,
            'recommendations': []
        }
        
        # Generate recommendations
        if results['missing_headers']:
            report['recommendations'].append("Implement missing security headers")
        
        if results['found_headers']:
            report['recommendations'].append("Security headers are working correctly")
        
        # Save report
        filename = f"security_headers_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {filename}")
        
        return report
    
    return None

if __name__ == "__main__":
    # Run comprehensive security headers test
    test_security_headers()
    test_security_headers_enhanced()
    generate_security_report()
    
    print("\n🎯 Next Steps:")
    print("1. If headers are missing, implement them in your API server")
    print("2. If headers are present, your API is well-protected!")
    print("3. Consider implementing additional security features")
