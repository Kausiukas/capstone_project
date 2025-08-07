#!/usr/bin/env python3
"""
Enhanced Tools Dashboard with Universal File Access
Comprehensive tool testing interface with instructions and examples.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"  # Update with your deployed URL
API_KEY = "demo_key_123"

# Tool instructions and examples
TOOL_INSTRUCTIONS = {
    "ping": {
        "description": "Test server connectivity",
        "examples": [],
        "capabilities": ["basic"],
        "help_text": "Simple connectivity test - no parameters needed."
    },
    "read_file": {
        "description": "Read contents of a file from any source (local, GitHub, HTTP)",
        "examples": [
            "README.md (local file)",
            "src/main.py (relative path)",
            "https://github.com/Kausiukas/capstone_project/blob/main/README.md (GitHub file)",
            "https://raw.githubusercontent.com/Kausiukas/capstone_project/main/README.md (HTTP file)",
            "D:/Projects/file.txt (absolute path)"
        ],
        "capabilities": ["universal_access", "github", "http", "local"],
        "help_text": "Supports local files, GitHub repositories, HTTP URLs, and absolute paths. For GitHub, use the full repository URL or specific file URLs."
    },
    "list_files": {
        "description": "List files in a directory or repository from any source",
        "examples": [
            ". (current directory)",
            "src/ (specific directory)",
            "https://github.com/Kausiukas/capstone_project (GitHub repository)",
            "D:/Projects/MyProject (absolute path)"
        ],
        "capabilities": ["universal_access", "github", "http", "local"],
        "help_text": "Lists files and directories. For GitHub repositories, shows the repository structure. For local paths, shows directory contents."
    },
    "get_system_status": {
        "description": "Get system status and metrics",
        "examples": [],
        "capabilities": ["basic"],
        "help_text": "Returns system information including CPU, memory usage, and security status."
    },
    "analyze_code": {
        "description": "Analyze code files from any source with comprehensive metrics",
        "examples": [
            "src/main.py (local file)",
            "https://github.com/Kausiukas/capstone_project/blob/main/src/mcp_server_fixed.py (GitHub file)",
            "https://example.com/script.js (HTTP file)"
        ],
        "capabilities": ["universal_access", "github", "http", "local", "code_analysis"],
        "help_text": "Performs comprehensive code analysis including lines, characters, words, file size, and file type detection."
    }
}

def main():
    st.set_page_config(
        page_title="Enhanced Tools Dashboard",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Enhanced Tools Dashboard")
    st.markdown("**Universal File Access with GitHub, HTTP, and Local Support**")
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 Tool Information")
        st.markdown("""
        ### 🚀 Enhanced Capabilities
        - **Universal File Access**: Local, GitHub, HTTP
        - **Smart Path Resolution**: Automatic source detection
        - **Comprehensive Error Handling**: Clear feedback
        - **Security Enhanced**: Safe path validation
        
        ### 🔒 Security Features
        - Path traversal protection
        - API key authentication
        - Rate limiting (planned)
        - Audit logging
        """)
        
        st.header("🔗 Quick Links")
        if st.button("📊 System Status"):
            st.session_state.selected_tool = "get_system_status"
        
        if st.button("🏓 Ping Test"):
            st.session_state.selected_tool = "ping"
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🛠️ Interactive Tool Testing")
        
        # Tool selection
        selected_tool = st.selectbox(
            "Select Tool to Test",
            list(TOOL_INSTRUCTIONS.keys()),
            key="tool_selector"
        )
        
        # Show tool information
        tool_info = TOOL_INSTRUCTIONS[selected_tool]
        
        st.markdown(f"**Description:** {tool_info['description']}")
        
        # Show capabilities
        if tool_info['capabilities']:
            capabilities_text = ", ".join(tool_info['capabilities'])
            st.markdown(f"**Capabilities:** {capabilities_text}")
        
        # Show help text
        if tool_info['help_text']:
            st.info(tool_info['help_text'])
        
        # Show examples
        if tool_info['examples']:
            st.markdown("**Examples:**")
            for example in tool_info['examples']:
                st.code(example, language="bash")
        
        # Tool-specific input
        if selected_tool == "read_file":
            file_path = st.text_input(
                "File path",
                placeholder="Enter file path (local, GitHub, or HTTP URL)",
                help="Supports local files, GitHub URLs, and HTTP URLs"
            )
            
            if st.button("📖 Execute read_file", type="primary"):
                if file_path:
                    execute_tool("read_file", {"file_path": file_path})
                else:
                    st.error("Please enter a file path")
        
        elif selected_tool == "list_files":
            directory = st.text_input(
                "Directory path",
                placeholder="Enter directory path (local, GitHub, or HTTP URL)",
                help="Supports local directories, GitHub repositories, and HTTP URLs"
            )
            
            if st.button("📁 Execute list_files", type="primary"):
                if directory:
                    execute_tool("list_files", {"directory": directory})
                else:
                    st.error("Please enter a directory path")
        
        elif selected_tool == "analyze_code":
            file_path = st.text_input(
                "Code file path",
                placeholder="Enter code file path (local, GitHub, or HTTP URL)",
                help="Supports local files, GitHub URLs, and HTTP URLs"
            )
            
            if st.button("🔍 Execute analyze_code", type="primary"):
                if file_path:
                    execute_tool("analyze_code", {"file_path": file_path})
                else:
                    st.error("Please enter a file path")
        
        elif selected_tool in ["ping", "get_system_status"]:
            if st.button(f"⚡ Execute {selected_tool}", type="primary"):
                execute_tool(selected_tool, {})
    
    with col2:
        st.header("📊 Quick Tests")
        
        # Quick test buttons
        st.markdown("**Common Tests:**")
        
        if st.button("🏠 Local README"):
            execute_tool("read_file", {"file_path": "README.md"})
        
        if st.button("📁 Local Directory"):
            execute_tool("list_files", {"directory": "."})
        
        if st.button("🐙 GitHub README"):
            execute_tool("read_file", {"file_path": "https://github.com/Kausiukas/capstone_project/blob/main/README.md"})
        
        if st.button("📂 GitHub Repo"):
            execute_tool("list_files", {"directory": "https://github.com/Kausiukas/capstone_project"})
        
        if st.button("🔍 Analyze Local Code"):
            execute_tool("analyze_code", {"file_path": "src/mcp_server_enhanced_tools.py"})
        
        st.markdown("---")
        
        # API Status
        st.header("🔌 API Status")
        if st.button("Check API Health"):
            check_api_health()

def execute_tool(tool_name: str, arguments: dict):
    """Execute a tool and display results"""
    
    st.markdown("---")
    st.subheader(f"🔧 Executing {tool_name}")
    
    # Show request details
    with st.expander("📤 Request Details", expanded=False):
        st.json({
            "tool": tool_name,
            "arguments": arguments,
            "timestamp": datetime.now().isoformat()
        })
    
    # Execute tool
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/tools/call",
            headers={'X-API-Key': API_KEY},
            json={
                "name": tool_name,
                "arguments": arguments
            },
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            # Success message
            st.success(f"✅ {tool_name} executed successfully!")
            
            # Response time
            st.metric("Response Time", f"{response_time:.2f}ms")
            
            # Results
            st.subheader("📄 Result:")
            
            if result['content']:
                content = result['content'][0]['text']
                
                # Format output based on tool
                if tool_name == "list_files":
                    st.markdown("**Files and Directories:**")
                    st.text_area("Output", content, height=300)
                elif tool_name == "read_file":
                    st.markdown("**File Content:**")
                    st.text_area("Output", content, height=400)
                elif tool_name == "analyze_code":
                    st.markdown("**Code Analysis:**")
                    st.text_area("Output", content, height=300)
                else:
                    st.text_area("Output", content, height=200)
            
            # Response details
            with st.expander("📥 Response Details", expanded=False):
                st.json(result)
        
        else:
            st.error(f"❌ Error: {response.status_code}")
            st.text_area("Error Details", response.text, height=200)
    
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please check the API URL.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

def check_api_health():
    """Check API health status"""
    
    st.markdown("---")
    st.subheader("🏥 API Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            
            st.success("✅ API is healthy!")
            
            # Health metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", health_data.get('status', 'Unknown'))
            
            with col2:
                st.metric("Version", health_data.get('version', 'Unknown'))
            
            with col3:
                st.metric("Tools", health_data.get('tools_count', 'Unknown'))
            
            # Capabilities
            if 'capabilities' in health_data:
                st.markdown("**Capabilities:**")
                for capability in health_data['capabilities']:
                    st.markdown(f"- ✅ {capability}")
            
            # Health details
            with st.expander("📊 Health Details", expanded=False):
                st.json(health_data)
        
        else:
            st.error(f"❌ API Health Check Failed: {response.status_code}")
            st.text_area("Error Details", response.text, height=200)
    
    except Exception as e:
        st.error(f"❌ Health Check Error: {str(e)}")

def show_tools_capabilities():
    """Show detailed tools capabilities"""
    
    st.markdown("---")
    st.subheader("🔧 Tools Capabilities")
    
    try:
        response = requests.get(f"{API_BASE_URL}/tools/capabilities", timeout=10)
        
        if response.status_code == 200:
            capabilities = response.json()
            
            # Universal file access
            if capabilities.get('universal_file_access', {}).get('enabled'):
                st.success("✅ Universal File Access Enabled")
                
                sources = capabilities['universal_file_access']['sources']
                st.markdown(f"**Supported Sources:** {', '.join(sources)}")
                
                features = capabilities['universal_file_access']['features']
                st.markdown(f"**Features:** {', '.join(features)}")
            
            # GitHub integration
            if capabilities.get('github_integration', {}).get('enabled'):
                st.success("✅ GitHub Integration Enabled")
                
                features = capabilities['github_integration']['features']
                st.markdown(f"**GitHub Features:** {', '.join(features)}")
            
            # HTTP support
            if capabilities.get('http_support', {}).get('enabled'):
                st.success("✅ HTTP Support Enabled")
                
                features = capabilities['http_support']['features']
                st.markdown(f"**HTTP Features:** {', '.join(features)}")
            
            # Security
            security = capabilities.get('security', {})
            st.markdown("**Security Features:**")
            for feature, enabled in security.items():
                status = "✅" if enabled else "❌"
                st.markdown(f"- {status} {feature}")
            
            # Full capabilities
            with st.expander("📋 Full Capabilities", expanded=False):
                st.json(capabilities)
        
        else:
            st.error(f"❌ Capabilities Check Failed: {response.status_code}")
    
    except Exception as e:
        st.error(f"❌ Capabilities Check Error: {str(e)}")

if __name__ == "__main__":
    main()
