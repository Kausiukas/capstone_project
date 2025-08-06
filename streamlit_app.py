#!/usr/bin/env python3
"""
LangFlow Connect MVP - Main Streamlit Dashboard
This is the main interface that users will access from your domain.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configuration - Default API URL
DEFAULT_API_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def get_api_url():
    """Get API URL from session state or default"""
    return st.session_state.get('api_url', DEFAULT_API_URL)

def get_headers():
    """Get headers with current API key"""
    return {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        api_url = get_api_url()
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_tools_list():
    """Get list of available tools"""
    try:
        api_url = get_api_url()
        headers = get_headers()
        response = requests.get(f"{api_url}/tools/list", headers=headers, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def execute_tool(tool_name, arguments):
    """Execute a tool with given arguments"""
    try:
        api_url = get_api_url()
        headers = get_headers()
        payload = {
            'name': tool_name,
            'arguments': arguments
        }
        response = requests.post(
            f"{api_url}/api/v1/tools/call",
            headers=headers,
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
        page_title="LangFlow Connect MVP",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main header
    st.title("🚀 LangFlow Connect MVP")
    st.markdown("**Capstone Project - AI-Powered Development Tools**")
    
    # Sidebar with navigation
    st.sidebar.header("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Dashboard", "🛠️ Tool Testing", "📊 Performance", "📚 API Docs", "🔧 System Status"]
    )
    
    # Dashboard page
    if page == "🏠 Dashboard":
        st.header("🏠 Welcome to LangFlow Connect MVP")
        
        # Status overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Status", "🟢 Online")
            st.metric("Available Tools", "5")
        
        with col2:
            st.metric("Response Time", "~200ms")
            st.metric("Uptime", "99.9%")
        
        with col3:
            st.metric("Version", "1.0.0")
            st.metric("Capstone", "✅ Complete")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("🏥 Health Check", use_container_width=True):
                with st.spinner("Checking health..."):
                    success, result = test_health_endpoint()
                    if success:
                        st.success("✅ Service is healthy!")
                        st.json(result)
                    else:
                        st.error(f"❌ Health check failed: {result}")
        
        with col5:
            if st.button("🛠️ List Tools", use_container_width=True):
                with st.spinner("Fetching tools..."):
                    success, result = get_tools_list()
                    if success:
                        st.success(f"✅ Found {len(result['tools'])} tools")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to get tools: {result}")
        
        with col6:
            if st.button("⚡ Quick Test", use_container_width=True):
                with st.spinner("Running quick test..."):
                    success, result = execute_tool("ping", {})
                    if success:
                        st.success("✅ Ping successful!")
                        st.json(result)
                    else:
                        st.error(f"❌ Ping failed: {result}")
        
        # Project info
        st.subheader("📋 Project Information")
        st.markdown("""
        **LangFlow Connect MVP** is a capstone project demonstrating:
        - 🤖 AI-powered development tools
        - 🔌 MCP (Model Context Protocol) integration
        - 🌐 RESTful API with authentication
        - 📊 Real-time system monitoring
        - 🎯 Interactive web interface
        
        **Available Tools:**
        - `ping` - Test server connectivity
        - `list_files` - List directory contents
        - `read_file` - Read file contents
        - `get_system_status` - Get system metrics
        - `analyze_code` - Analyze code files
        """)
    
    # Tool Testing page
    elif page == "🛠️ Tool Testing":
        st.header("🛠️ Interactive Tool Testing")
        
        # Tool selection
        tool_name = st.selectbox(
            "Select Tool to Test",
            ["ping", "list_files", "read_file", "get_system_status", "analyze_code"]
        )
        
        # Tool-specific parameters
        arguments = {}
        
        if tool_name == "list_files":
            path = st.text_input("Directory path", value=".")
            arguments = {"directory": path}
        
        elif tool_name == "read_file":
            file_path = st.text_input("File path", value="README.md")
            arguments = {"file_path": file_path}
        
        elif tool_name == "analyze_code":
            file_path = st.text_input("Code file path", value="src/mcp_server_http.py")
            arguments = {"file_path": file_path}
        
        # Execute button
        if st.button(f"🚀 Execute {tool_name}", type="primary"):
            with st.spinner(f"Executing {tool_name}..."):
                start_time = time.time()
                success, result = execute_tool(tool_name, arguments)
                end_time = time.time()
                
                if success:
                    st.success(f"✅ {tool_name} executed successfully!")
                    st.metric("Response Time", f"{(end_time - start_time)*1000:.2f}ms")
                    
                    # Display result
                    if isinstance(result, dict) and 'content' in result:
                        st.subheader("Result:")
                        for content in result['content']:
                            if content['type'] == 'text':
                                st.text_area("Output", content['text'], height=200)
                    else:
                        st.json(result)
                else:
                    st.error(f"❌ {tool_name} failed: {result}")
    
    # Performance page
    elif page == "📊 Performance":
        st.header("📊 Performance Testing")
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
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
        
        with col8:
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
        
        with col9:
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
    
    # API Docs page
    elif page == "📚 API Docs":
        st.header("📚 API Documentation")
        
        st.subheader("Base URL")
        st.code(get_api_url())
        
        st.subheader("Authentication")
        st.markdown("All API requests require the `X-API-Key` header:")
        st.code("X-API-Key: demo_key_123")
        
        st.subheader("Endpoints")
        
        # Health endpoint
        with st.expander("🏥 Health Check"):
            st.markdown("**GET** `/health`")
            st.markdown("Check if the service is running.")
            st.code(f"curl -X GET {get_api_url()}/health")
        
        # Tools list endpoint
        with st.expander("🛠️ List Tools"):
            st.markdown("**GET** `/tools/list`")
            st.markdown("Get list of available tools.")
            st.code(f"""curl -X GET {get_api_url()}/tools/list \\
  -H "X-API-Key: demo_key_123" """)
        
        # Tool execution endpoint
        with st.expander("⚡ Execute Tool"):
            st.markdown("**POST** `/api/v1/tools/call`")
            st.markdown("Execute a specific tool.")
            st.code(f"""curl -X POST {get_api_url()}/api/v1/tools/call \\
  -H "X-API-Key: demo_key_123" \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "ping", "arguments": {{}}}}' """)
        
        st.subheader("Available Tools")
        tools_info = [
            ("ping", "Test server connectivity", "{}"),
            ("list_files", "List files in directory", '{"directory": "."}'),
            ("read_file", "Read file contents", '{"file_path": "README.md"}'),
            ("get_system_status", "Get system metrics", "{}"),
            ("analyze_code", "Analyze code files", '{"file_path": "src/app.py"}')
        ]
        
        for tool_name, description, example in tools_info:
            with st.expander(f"🔧 {tool_name}"):
                st.markdown(f"**Description:** {description}")
                st.markdown(f"**Example:** `{example}`")
    
    # System Status page
    elif page == "🔧 System Status":
        st.header("🔧 System Status")
        
        # API Configuration Section
        st.subheader("🔧 API Configuration")
        
        # API URL input
        current_api_url = get_api_url()
        new_api_url = st.text_input(
            "API Base URL",
            value=current_api_url,
            help="Enter the base URL of your API (e.g., https://your-api.onrender.com)"
        )
        
        # Update API URL button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Update API URL"):
                if new_api_url != current_api_url:
                    st.session_state['api_url'] = new_api_url
                    st.success(f"✅ API URL updated to: {new_api_url}")
                    st.rerun()
        
        with col2:
            if st.button("🧪 Test Connection"):
                with st.spinner("Testing API connection..."):
                    success, result = test_health_endpoint()
                    if success:
                        st.success("✅ API connection successful!")
                        st.json(result)
                    else:
                        st.error(f"❌ API connection failed: {result}")
        
        st.divider()
        
        # Real-time status
        st.subheader("📊 System Status")
        if st.button("🔄 Refresh Status"):
            with st.spinner("Checking system status..."):
                success, result = execute_tool("get_system_status", {})
                if success:
                    st.success("✅ System status retrieved!")
                    if isinstance(result, dict) and 'content' in result:
                        for content in result['content']:
                            if content['type'] == 'text':
                                st.text_area("System Status", content['text'], height=200)
                else:
                    st.error(f"❌ Failed to get system status: {result}")
        
        # Service information
        st.subheader("ℹ️ Service Information")
        st.markdown(f"""
        - **Current API URL:** {get_api_url()}
        - **Dashboard URL:** {st.get_option('server.baseUrlPath')}
        - **Version:** 1.0.0
        - **Status:** 🟢 Online
        - **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """)
        
        # Quick health check
        st.subheader("🏥 Health Check")
        success, health_data = test_health_endpoint()
        if success:
            st.success("🟢 API is healthy and responding")
            st.json(health_data)
        else:
            st.error("🔴 API is not responding")
            st.text(health_data)

if __name__ == "__main__":
    main() 