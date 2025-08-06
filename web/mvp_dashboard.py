#!/usr/bin/env python3
"""
MVP Dashboard - Streamlit Interface for Testing Deployed MCP Server
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://capstone-project-i1xm.onrender.com"
API_KEY = "demo_key_123"
HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_tools_list():
    """Get list of available tools"""
    try:
        response = requests.get(f"{API_BASE_URL}/tools/list", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def execute_tool(tool_name, arguments):
    """Execute a tool with given arguments"""
    try:
        payload = {
            'name': tool_name,
            'arguments': arguments
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/tools/call",
            headers=HEADERS,
            data=json.dumps(payload),
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    st.set_page_config(
        page_title="LangFlow Connect MVP Dashboard",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 LangFlow Connect MVP Dashboard")
    st.markdown("**Live Deployment Testing Interface**")
    
    # Sidebar
    st.sidebar.header("🎯 Quick Actions")
    
    # Health Check
    if st.sidebar.button("🏥 Health Check"):
        with st.spinner("Checking health..."):
            success, result = test_health_endpoint()
            if success:
                st.sidebar.success("✅ Service is healthy!")
                st.sidebar.json(result)
            else:
                st.sidebar.error(f"❌ Health check failed: {result}")
    
    # Tools List
    if st.sidebar.button("🛠️ List Tools"):
        with st.spinner("Fetching tools..."):
            success, result = get_tools_list()
            if success:
                st.sidebar.success(f"✅ Found {len(result)} tools")
                st.sidebar.json(result)
            else:
                st.sidebar.error(f"❌ Failed to get tools: {result}")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🧪 Tool Testing")
        
        # Tool selection
        tool_name = st.selectbox(
            "Select Tool to Test",
            ["ping", "list_files", "system_status"]
        )
        
        # Tool-specific parameters
        if tool_name == "list_files":
            path = st.text_input("Path to list", value=".")
            arguments = {"path": path}
        elif tool_name == "system_status":
            arguments = {}
        else:  # ping
            arguments = {}
        
        # Execute button
        if st.button(f"🚀 Execute {tool_name}"):
            with st.spinner(f"Executing {tool_name}..."):
                start_time = time.time()
                success, result = execute_tool(tool_name, arguments)
                end_time = time.time()
                
                if success:
                    st.success(f"✅ {tool_name} executed successfully!")
                    st.metric("Response Time", f"{(end_time - start_time)*1000:.2f}ms")
                    
                    # Display result
                    if isinstance(result, dict) and 'result' in result:
                        st.subheader("Result:")
                        st.json(result['result'])
                    else:
                        st.json(result)
                else:
                    st.error(f"❌ {tool_name} failed: {result}")
    
    with col2:
        st.header("📊 Status")
        
        # Service status
        st.subheader("Service Status")
        success, health_data = test_health_endpoint()
        if success:
            st.success("🟢 Online")
            st.metric("Version", health_data.get('version', 'Unknown'))
            st.metric("Status", health_data.get('status', 'Unknown'))
        else:
            st.error("🔴 Offline")
        
        # Last updated
        st.subheader("Last Updated")
        st.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Quick stats
        st.subheader("Quick Stats")
        success, tools = get_tools_list()
        if success:
            st.metric("Available Tools", len(tools))
        else:
            st.metric("Available Tools", "Error")
    
    # Performance testing
    st.header("⚡ Performance Testing")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🏃‍♂️ Speed Test"):
            with st.spinner("Testing response time..."):
                times = []
                for i in range(5):
                    start = time.time()
                    success, _ = test_health_endpoint()
                    end = time.time()
                    if success:
                        times.append((end - start) * 1000)
                
                if times:
                    avg_time = sum(times) / len(times)
                    st.metric("Average Response Time", f"{avg_time:.2f}ms")
                    st.metric("Min Response Time", f"{min(times):.2f}ms")
                    st.metric("Max Response Time", f"{max(times):.2f}ms")
    
    with col4:
        if st.button("🔄 Load Test"):
            with st.spinner("Running load test..."):
                import threading
                
                results = []
                def test_request():
                    success, _ = test_health_endpoint()
                    results.append(success)
                
                threads = []
                for i in range(10):
                    t = threading.Thread(target=test_request)
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
                
                success_count = sum(results)
                st.metric("Successful Requests", f"{success_count}/10")
                st.metric("Success Rate", f"{success_count/10*100:.1f}%")
    
    with col5:
        if st.button("🔍 API Test"):
            with st.spinner("Testing API endpoints..."):
                tests = [
                    ("Health", lambda: test_health_endpoint()),
                    ("Tools List", lambda: get_tools_list()),
                    ("Ping Tool", lambda: execute_tool("ping", {})),
                ]
                
                results = []
                for test_name, test_func in tests:
                    success, _ = test_func()
                    results.append((test_name, success))
                
                st.subheader("API Test Results")
                for test_name, success in results:
                    if success:
                        st.success(f"✅ {test_name}")
                    else:
                        st.error(f"❌ {test_name}")
    
    # Error testing
    st.header("🔍 Error Handling Test")
    
    col6, col7 = st.columns(2)
    
    with col6:
        if st.button("🚫 Test Invalid Tool"):
            with st.spinner("Testing invalid tool..."):
                success, result = execute_tool("invalid_tool", {})
                if not success:
                    st.success("✅ Properly handled invalid tool")
                    st.text(f"Error: {result}")
                else:
                    st.warning("⚠️ Should have failed")
    
    with col7:
        if st.button("🔑 Test No API Key"):
            with st.spinner("Testing without API key..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/tools/call",
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps({"name": "ping", "arguments": {}}),
                        timeout=10
                    )
                    if response.status_code in [401, 403]:
                        st.success("✅ Properly rejected request without API key")
                    else:
                        st.warning(f"⚠️ Unexpected status: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Deployment URL:** {API_BASE_URL}")
    st.markdown("**Dashboard Version:** 1.0.0")

if __name__ == "__main__":
    main() 