#!/usr/bin/env python3
"""
LangFlow Connect MVP - Integrated Dashboard
Unified dashboard with Content Preview and Performance Monitoring
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import threading
import queue

# Configuration
DEFAULT_API_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"
REFRESH_INTERVAL = 30

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SHARED UTILITY FUNCTIONS
# ============================================================================

def get_api_url():
    """Get API URL from session state or default"""
    return st.session_state.get('api_url', DEFAULT_API_URL)

def get_headers():
    """Get headers with current API key"""
    return {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, params: dict = None, timeout: int = 30):
    """Unified API request function"""
    try:
        api_url = get_api_url()
        headers = get_headers()
        
        if method == "GET":
            response = requests.get(f"{api_url}{endpoint}", headers=headers, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(f"{api_url}{endpoint}", headers=headers, json=data, timeout=timeout)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def test_health_endpoint():
    return make_api_request("/health", timeout=10)

def get_tools_list():
    return make_api_request("/tools/list", timeout=10)

def execute_tool(tool_name, arguments):
    payload = {'name': tool_name, 'arguments': arguments}
    return make_api_request("/api/v1/tools/call", method="POST", data=payload, timeout=30)

# ============================================================================
# CONTENT PREVIEW FUNCTIONS
# ============================================================================

def preview_file(file_path: str, preview_type: str = None):
    params = {"file_path": file_path}
    if preview_type and preview_type != "Auto-detect":
        params["preview_type"] = preview_type
    return make_api_request("/preview/file", params=params)

def analyze_file(file_path: str):
    return make_api_request("/preview/analyze", params={"file_path": file_path})

def preview_batch_files(file_paths: list):
    return make_api_request("/preview/batch", method="POST", data={"file_paths": file_paths})

def get_supported_preview_types():
    return make_api_request("/preview/supported-types")

# ============================================================================
# PERFORMANCE MONITORING FUNCTIONS
# ============================================================================

def get_performance_metrics(tool_name: str = None):
    params = {"tool_name": tool_name} if tool_name else {}
    return make_api_request("/performance/metrics", params=params)

def get_performance_alerts():
    return make_api_request("/performance/alerts")

def get_performance_dashboard():
    return make_api_request("/performance/dashboard")

def get_performance_health():
    return make_api_request("/performance/health")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    st.set_page_config(
        page_title="LangFlow Connect MVP - Integrated Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main header
    st.markdown("""
    <div class="header">
        <h1>🚀 LangFlow Connect MVP - Integrated Dashboard</h1>
        <p>Capstone Project - AI-Powered Development Tools with Content Preview & Performance Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.header("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        [
            "🏠 Dashboard", 
            "🛠️ Tool Testing", 
            "👁️ Content Preview", 
            "📊 Performance Monitoring", 
            "📚 API Docs", 
            "🔧 System Status"
        ]
    )
    
    # API Configuration
    st.sidebar.header("🔧 API Configuration")
    current_api_url = get_api_url()
    new_api_url = st.sidebar.text_input("API Base URL", value=current_api_url)
    
    if st.sidebar.button("🔄 Update API URL"):
        if new_api_url != current_api_url:
            st.session_state['api_url'] = new_api_url
            st.sidebar.success("✅ API URL updated!")
            st.rerun()
    
    if st.sidebar.button("🧪 Test Connection"):
        with st.spinner("Testing API connection..."):
            success, result = test_health_endpoint()
            if success:
                st.sidebar.success("✅ API connection successful!")
            else:
                st.sidebar.error(f"❌ API connection failed: {result}")
    
    # ============================================================================
    # DASHBOARD PAGE
    # ============================================================================
    if page == "🏠 Dashboard":
        st.header("🏠 Welcome to LangFlow Connect MVP")
        
        # Status overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Status", "🟢 Online")
            st.metric("Available Tools", "5")
        
        with col2:
            st.metric("Content Preview", "✅ Active")
            st.metric("Performance Monitoring", "✅ Active")
        
        with col3:
            st.metric("Version", "2.0.0")
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
            if st.button("👁️ Preview Test", use_container_width=True):
                with st.spinner("Testing content preview..."):
                    success, result = preview_file("README.md")
                    if success:
                        st.success("✅ Content preview working!")
                        st.metric("File Type", result.get("file_type", "Unknown"))
                    else:
                        st.error(f"❌ Content preview failed: {result}")
        
        with col6:
            if st.button("📊 Performance Check", use_container_width=True):
                with st.spinner("Checking performance..."):
                    success, result = get_performance_health()
                    if success:
                        st.success("✅ Performance monitoring active!")
                        st.metric("Status", result.get("status", "Unknown"))
                    else:
                        st.error(f"❌ Performance check failed: {result}")
        
        # Project info
        st.subheader("📋 Project Information")
        st.markdown("""
        **LangFlow Connect MVP** is a comprehensive capstone project demonstrating:
        - 🤖 **AI-powered development tools** with MCP integration
        - 👁️ **Content Preview System** with syntax highlighting and rendering
        - 📊 **Performance Monitoring** with real-time metrics and alerts
        - 🔌 **RESTful API** with authentication and universal file access
        - 🎯 **Unified Web Interface** with integrated dashboard
        
        **Available Tools:**
        - `ping` - Test server connectivity
        - `list_files` - List directory contents (local, GitHub, HTTP)
        - `read_file` - Read file contents (local, GitHub, HTTP)
        - `get_system_status` - Get system metrics
        - `analyze_code` - Analyze code files
        
        **New Features:**
        - **Content Preview** - Syntax highlighting, markdown rendering, image preview
        - **Performance Monitoring** - Real-time metrics, alerts, health monitoring
        - **Universal File Access** - Local, GitHub, and HTTP file support
        """)
    
    # ============================================================================
    # TOOL TESTING PAGE
    # ============================================================================
    elif page == "🛠️ Tool Testing":
        st.header("🛠️ Interactive Tool Testing")
        
        tool_name = st.selectbox(
            "Select Tool to Test",
            ["ping", "list_files", "read_file", "get_system_status", "analyze_code"]
        )
        
        arguments = {}
        
        if tool_name == "list_files":
            path = st.text_input("Directory path", value=".", help="Can be local path, GitHub URL, or HTTP URL")
            arguments = {"directory": path}
        elif tool_name == "read_file":
            file_path = st.text_input("File path", value="README.md", help="Can be local path, GitHub URL, or HTTP URL")
            arguments = {"file_path": file_path}
        elif tool_name == "analyze_code":
            file_path = st.text_input("Code file path", value="src/mcp_server_http.py", help="Can be local path, GitHub URL, or HTTP URL")
            arguments = {"file_path": file_path}
        
        if st.button(f"🚀 Execute {tool_name}", type="primary"):
            with st.spinner(f"Executing {tool_name}..."):
                start_time = time.time()
                success, result = execute_tool(tool_name, arguments)
                end_time = time.time()
                
                if success:
                    st.success(f"✅ {tool_name} executed successfully!")
                    st.metric("Response Time", f"{(end_time - start_time)*1000:.2f}ms")
                    
                    if isinstance(result, dict) and 'content' in result:
                        st.subheader("Result:")
                        for content in result['content']:
                            if content['type'] == 'text':
                                st.text_area("Output", content['text'], height=200)
                    else:
                        st.json(result)
                else:
                    st.error(f"❌ {tool_name} failed: {result}")
    
    # ============================================================================
    # CONTENT PREVIEW PAGE
    # ============================================================================
    elif page == "👁️ Content Preview":
        st.header("👁️ Content Preview System")
        
        # Sidebar options
        st.sidebar.header("🎛️ Preview Options")
        file_path = st.sidebar.text_input(
            "📁 File Path",
            placeholder="Enter file path (local, GitHub, or HTTP URL)"
        )
        preview_type = st.sidebar.selectbox(
            "🎨 Preview Type",
            ["Auto-detect", "code", "image", "document", "markdown"]
        )
        
        # Main content
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("🔍 File Analysis")
            
            if file_path and st.button("🔍 Analyze File", type="primary"):
                with st.spinner("Analyzing file..."):
                    success, result = analyze_file(file_path)
                    
                    if success:
                        st.success("✅ File analysis completed!")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Preview Type", result.get("preview_type", "Unknown"))
                            st.metric("Language", result.get("language", "None"))
                        with col_b:
                            st.metric("Supported", "✅ Yes" if result.get("supported") else "❌ No")
                            st.metric("Source Type", result.get("source_type", "Unknown"))
                    else:
                        st.error(f"❌ Analysis failed: {result}")
            
            if st.button("📋 Get Supported Types"):
                with st.spinner("Fetching supported types..."):
                    success, result = get_supported_preview_types()
                    if success:
                        supported_types = result.get("supported_types", {})
                        for preview_type_name, config in supported_types.items():
                            with st.expander(f"📁 {preview_type_name.title()}"):
                                st.write("**Extensions:**", ", ".join(config.get("extensions", [])[:5]))
                                st.write("**MIME Types:**", ", ".join(config.get("mime_types", [])[:3]))
                    else:
                        st.error(f"❌ Failed to get supported types: {result}")
        
        with col2:
            st.header("👁️ Content Preview")
            
            if file_path and st.button("👁️ Preview File", type="primary"):
                with st.spinner("Generating preview..."):
                    success, result = preview_file(file_path, preview_type if preview_type != "Auto-detect" else None)
                    
                    if success:
                        st.success("✅ Preview generated successfully!")
                        
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric("File Type", result.get("file_type", "Unknown"))
                            st.metric("Language", result.get("language", "None"))
                        with col_info2:
                            st.metric("Content Length", f"{result.get('content_length', 0):,} chars")
                            st.metric("Source", result.get("metadata", {}).get("source_type", "Unknown"))
                        
                        preview_html = result.get("preview_html", "")
                        if preview_html:
                            st.components.v1.html(preview_html, height=400, scrolling=True)
                        else:
                            st.warning("⚠️ No preview content available")
                        
                        with st.expander("📄 Raw Content"):
                            raw_content = result.get("content", "")
                            if raw_content:
                                st.code(raw_content, language=result.get("language", "text"))
                    else:
                        st.error(f"❌ Preview failed: {result}")
    
    # ============================================================================
    # PERFORMANCE MONITORING PAGE
    # ============================================================================
    elif page == "📊 Performance Monitoring":
        st.header("📊 Performance Monitoring Dashboard")
        
        # Performance overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Get Metrics", use_container_width=True):
                with st.spinner("Fetching performance metrics..."):
                    success, result = get_performance_metrics()
                    if success:
                        st.success("✅ Metrics retrieved!")
                        overall_metrics = result.get("overall", {})
                        st.metric("Success Rate", f"{overall_metrics.get('success_rate', 0):.1f}%")
                        st.metric("Avg Response Time", f"{overall_metrics.get('avg_response_time', 0):.2f}ms")
                        st.metric("Total Requests", f"{overall_metrics.get('total_requests', 0):,}")
                    else:
                        st.error(f"❌ Failed to get metrics: {result}")
        
        with col2:
            if st.button("🚨 Get Alerts", use_container_width=True):
                with st.spinner("Fetching alerts..."):
                    success, result = get_performance_alerts()
                    if success:
                        alerts = result.get("alerts", [])
                        if alerts:
                            st.success(f"✅ Found {len(alerts)} alerts!")
                            for alert in alerts:
                                st.warning(f"🚨 {alert.get('title', 'Alert')}: {alert.get('message', '')}")
                        else:
                            st.info("✅ No active alerts")
                    else:
                        st.error(f"❌ Failed to get alerts: {result}")
        
        with col3:
            if st.button("🏥 Health Check", use_container_width=True):
                with st.spinner("Checking performance health..."):
                    success, result = get_performance_health()
                    if success:
                        health_status = result.get("status", "unknown")
                        st.success(f"✅ Performance health: {health_status}")
                        metrics = result.get("metrics", {})
                        st.metric("CPU Usage", f"{metrics.get('cpu_usage', 0):.1f}%")
                        st.metric("Memory Usage", f"{metrics.get('memory_usage', 0):.1f}%")
                    else:
                        st.error(f"❌ Health check failed: {result}")
        
        with col4:
            if st.button("📈 Dashboard Data", use_container_width=True):
                with st.spinner("Fetching dashboard data..."):
                    success, result = get_performance_dashboard()
                    if success:
                        st.success("✅ Dashboard data retrieved!")
                        dashboard_data = result.get("dashboard", {})
                        st.metric("Active Tools", f"{dashboard_data.get('active_tools', 0)}")
                        st.metric("System Uptime", f"{dashboard_data.get('uptime_hours', 0):.1f}h")
                        st.metric("Error Rate", f"{dashboard_data.get('error_rate', 0):.2f}%")
                    else:
                        st.error(f"❌ Dashboard data failed: {result}")
        
        # Tool-specific metrics
        st.subheader("🔧 Tool-Specific Metrics")
        tool_name = st.selectbox(
            "Select Tool for Detailed Metrics",
            ["All Tools", "ping", "list_files", "read_file", "get_system_status", "analyze_code"]
        )
        
        if st.button(f"📊 Get {tool_name} Metrics"):
            with st.spinner(f"Fetching {tool_name} metrics..."):
                if tool_name == "All Tools":
                    success, result = get_performance_metrics()
                else:
                    success, result = get_performance_metrics(tool_name)
                
                if success:
                    if tool_name == "All Tools":
                        tools_data = result.get("tools", {})
                        for tool, metrics in tools_data.items():
                            with st.expander(f"🔧 {tool}"):
                                col_t1, col_t2, col_t3 = st.columns(3)
                                with col_t1:
                                    st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1f}%")
                                with col_t2:
                                    st.metric("Avg Response Time", f"{metrics.get('avg_response_time', 0):.2f}ms")
                                with col_t3:
                                    st.metric("Total Requests", f"{metrics.get('total_requests', 0):,}")
                    else:
                        tool_metrics = result.get("tool_metrics", {})
                        col_t1, col_t2, col_t3 = st.columns(3)
                        with col_t1:
                            st.metric("Success Rate", f"{tool_metrics.get('success_rate', 0):.1f}%")
                        with col_t2:
                            st.metric("Avg Response Time", f"{tool_metrics.get('avg_response_time', 0):.2f}ms")
                        with col_t3:
                            st.metric("Total Requests", f"{tool_metrics.get('total_requests', 0):,}")
                else:
                    st.error(f"❌ Failed to get {tool_name} metrics: {result}")
    
    # ============================================================================
    # API DOCS PAGE
    # ============================================================================
    elif page == "📚 API Docs":
        st.header("📚 API Documentation")
        
        st.subheader("Base URL")
        st.code(get_api_url())
        
        st.subheader("Authentication")
        st.markdown("All API requests require the `X-API-Key` header:")
        st.code("X-API-Key: demo_key_123")
        
        st.subheader("Core Endpoints")
        
        with st.expander("🏥 Health Check"):
            st.markdown("**GET** `/health`")
            st.code(f"curl -X GET {get_api_url()}/health")
        
        with st.expander("🛠️ List Tools"):
            st.markdown("**GET** `/tools/list`")
            st.code(f"""curl -X GET {get_api_url()}/tools/list \\
  -H "X-API-Key: demo_key_123" """)
        
        with st.expander("⚡ Execute Tool"):
            st.markdown("**POST** `/api/v1/tools/call`")
            st.code(f"""curl -X POST {get_api_url()}/api/v1/tools/call \\
  -H "X-API-Key: demo_key_123" \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "ping", "arguments": {{}}}}' """)
        
        st.subheader("Content Preview Endpoints")
        
        with st.expander("👁️ Preview File"):
            st.markdown("**GET** `/preview/file`")
            st.code(f"""curl -X GET "{get_api_url()}/preview/file?file_path=README.md" \\
  -H "X-API-Key: demo_key_123" """)
        
        with st.expander("🔍 Analyze File"):
            st.markdown("**GET** `/preview/analyze`")
            st.code(f"""curl -X GET "{get_api_url()}/preview/analyze?file_path=README.md" \\
  -H "X-API-Key: demo_key_123" """)
        
        st.subheader("Performance Monitoring Endpoints")
        
        with st.expander("📊 Performance Metrics"):
            st.markdown("**GET** `/performance/metrics`")
            st.code(f"""curl -X GET {get_api_url()}/performance/metrics \\
  -H "X-API-Key: demo_key_123" """)
        
        with st.expander("🚨 Performance Alerts"):
            st.markdown("**GET** `/performance/alerts`")
            st.code(f"""curl -X GET {get_api_url()}/performance/alerts \\
  -H "X-API-Key: demo_key_123" """)
    
    # ============================================================================
    # SYSTEM STATUS PAGE
    # ============================================================================
    elif page == "🔧 System Status":
        st.header("🔧 System Status")
        
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
        - **Dashboard Version:** 2.0.0 (Unified)
        - **Status:** 🟢 Online
        - **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        - **Features:** Content Preview ✅, Performance Monitoring ✅
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
        
        # Feature status
        st.subheader("🎯 Feature Status")
        col_feat1, col_feat2, col_feat3 = st.columns(3)
        
        with col_feat1:
            st.markdown("**Core Tools**")
            st.success("✅ All 5 tools operational")
            st.info("ping, list_files, read_file, get_system_status, analyze_code")
        
        with col_feat2:
            st.markdown("**Content Preview**")
            st.success("✅ Syntax highlighting active")
            st.info("Code, markdown, images, documents")
        
        with col_feat3:
            st.markdown("**Performance Monitoring**")
            st.success("✅ Real-time metrics active")
            st.info("Response times, success rates, alerts")

if __name__ == "__main__":
    main()
