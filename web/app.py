import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="LangFlow Connect MCP Server Demo",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 LangFlow Connect MCP Server Demo")
st.markdown("Capstone Project - Basic MCP Server Demo")

# Sidebar
st.sidebar.header("Server Status")
st.sidebar.markdown("""
### Available Tools:
- **ping**: Test server connectivity
- **read_file**: Read file contents
- **list_files**: List directory contents
- **get_system_status**: Get server status
- **analyze_code**: Analyze code files
""")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Tool Testing")
    
    # Tool selection
    tool = st.selectbox(
        "Select Tool to Test",
        ["ping", "read_file", "list_files", "get_system_status", "analyze_code"]
    )
    
    # Tool-specific inputs
    arguments = {}
    
    if tool == "read_file":
        file_path = st.text_input("File Path", "README.md")
        arguments = {"file_path": file_path}
        
    elif tool == "list_files":
        directory = st.text_input("Directory", ".")
        arguments = {"directory": directory}
        
    elif tool == "analyze_code":
        file_path = st.text_input("File Path", "src/mcp_server_http.py")
        arguments = {"file_path": file_path}
    
    # Execute tool
    if st.button("🚀 Execute Tool", type="primary"):
        with st.spinner("Executing tool..."):
            try:
                # API call to the MCP server
                api_url = "http://localhost:8000/api/v1/tools/call"
                headers = {
                    "X-API-Key": "demo_key_123",
                    "Content-Type": "application/json"
                }
                payload = {
                    "name": tool,
                    "arguments": arguments
                }
                
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Tool executed successfully!")
                    st.json(result)
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to MCP server. Please start the server first:")
                st.code("python src/mcp_server_http.py")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col2:
    st.header("API Information")
    st.markdown("""
    ### API Endpoint:
    `POST /api/v1/tools/call`
    
    ### Authentication:
    Header: `X-API-Key: demo_key_123`
    
    ### Example Request:
    ```json
    {
      "name": "ping",
      "arguments": {}
    }
    ```
    """)
    
    st.header("Project Info")
    st.markdown("""
    - **Status**: MVP Demo
    - **Version**: 1.0.0
    - **Last Updated**: ''' + datetime.now().strftime('%Y-%m-%d') + '''
    - **Repository**: [GitHub](https://github.com/Kausiukas/capstone_project)
    """)

# Quick test section
st.header("Quick Test")
col3, col4 = st.columns(2)

with col3:
    if st.button("Test Ping", type="secondary"):
        with st.spinner("Testing ping..."):
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/tools/call",
                    headers={"X-API-Key": "demo_key_123", "Content-Type": "application/json"},
                    json={"name": "ping", "arguments": {}}
                )
                if response.status_code == 200:
                    st.success("✅ Server is running!")
                else:
                    st.error("❌ Server connection failed")
            except:
                st.error("❌ Cannot connect to server")

with col4:
    if st.button("Test Health", type="secondary"):
        with st.spinner("Checking health..."):
            try:
                response = requests.get("http://localhost:8000/health")
                if response.status_code == 200:
                    health_data = response.json()
                    st.success(f"✅ Server Health: {health_data['status']}")
                    st.info(f"Tools Available: {health_data['tools_count']}")
                else:
                    st.error("❌ Health check failed")
            except:
                st.error("❌ Cannot connect to server")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>LangFlow Connect MCP Server - MVP Demo | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)
