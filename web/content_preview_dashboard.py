#!/usr/bin/env python3
"""
Content Preview Dashboard
Streamlit application for testing and using the content preview system
"""

import streamlit as st
import requests
import json
import base64
from pathlib import Path
import time

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, params: dict = None):
    """Make API request with error handling"""
    try:
        headers = {"X-API-Key": API_KEY}
        
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    st.set_page_config(
        page_title="Content Preview Dashboard",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("👁️ Content Preview Dashboard")
    st.markdown("**Enhanced file content preview with syntax highlighting and rendering**")
    
    # Sidebar
    st.sidebar.header("🎛️ Preview Options")
    
    # File input
    file_path = st.sidebar.text_input(
        "📁 File Path",
        placeholder="Enter file path (local, GitHub, or HTTP URL)",
        help="Examples:\n- Local: D:\\path\\to\\file.py\n- GitHub: https://github.com/user/repo/blob/main/file.py\n- HTTP: https://example.com/file.txt"
    )
    
    # Preview type selection
    preview_type = st.sidebar.selectbox(
        "🎨 Preview Type",
        ["Auto-detect", "code", "image", "document", "markdown"],
        help="Select preview type or let the system auto-detect"
    )
    
    # Batch preview
    st.sidebar.header("📦 Batch Preview")
    batch_files = st.sidebar.text_area(
        "Multiple Files (one per line)",
        placeholder="file1.py\nfile2.js\nfile3.md",
        help="Enter multiple file paths for batch preview"
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🔍 File Analysis")
        
        if file_path:
            if st.button("🔍 Analyze File", type="primary"):
                with st.spinner("Analyzing file..."):
                    result = make_api_request("/preview/analyze", params={"file_path": file_path})
                    
                    if "error" not in result:
                        st.success("✅ File analysis completed!")
                        
                        # Display analysis results
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Preview Type", result.get("preview_type", "Unknown"))
                            st.metric("Language", result.get("language", "None"))
                            st.metric("Supported", "✅ Yes" if result.get("supported") else "❌ No")
                        
                        with col_b:
                            st.metric("Source Type", result.get("source_type", "Unknown"))
                            st.metric("File Extension", result.get("file_extension", "None"))
                            st.metric("Exists", "✅ Yes" if result.get("exists") else "❌ No")
                        
                        # Capabilities
                        st.subheader("🎯 Preview Capabilities")
                        capabilities = result.get("capabilities", {})
                        for capability, available in capabilities.items():
                            status = "✅" if available else "❌"
                            st.write(f"{status} {capability.replace('_', ' ').title()}")
                    else:
                        st.error(f"❌ Analysis failed: {result['error']}")
        
        # Supported types
        st.header("📋 Supported File Types")
        if st.button("📋 Get Supported Types"):
            with st.spinner("Fetching supported types..."):
                result = make_api_request("/preview/supported-types")
                
                if "error" not in result:
                    supported_types = result.get("supported_types", {})
                    
                    for preview_type_name, config in supported_types.items():
                        with st.expander(f"📁 {preview_type_name.title()}"):
                            st.write("**Extensions:**")
                            st.code(", ".join(config.get("extensions", [])))
                            st.write("**MIME Types:**")
                            st.code(", ".join(config.get("mime_types", [])))
                else:
                    st.error(f"❌ Failed to get supported types: {result['error']}")
    
    with col2:
        st.header("👁️ Content Preview")
        
        if file_path:
            # Preview parameters
            preview_params = {"file_path": file_path}
            if preview_type != "Auto-detect":
                preview_params["preview_type"] = preview_type
            
            if st.button("👁️ Preview File", type="primary"):
                with st.spinner("Generating preview..."):
                    result = make_api_request("/preview/file", params=preview_params)
                    
                    if "error" not in result:
                        st.success("✅ Preview generated successfully!")
                        
                        # File info
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric("File Type", result.get("file_type", "Unknown"))
                            st.metric("Language", result.get("language", "None"))
                        
                        with col_info2:
                            st.metric("Content Length", f"{result.get('content_length', 0):,} chars")
                            st.metric("Source", result.get("metadata", {}).get("source_type", "Unknown"))
                        
                        # Preview content
                        st.subheader("🎨 Preview")
                        preview_html = result.get("preview_html", "")
                        
                        if preview_html:
                            # Display HTML content
                            st.components.v1.html(preview_html, height=400, scrolling=True)
                        else:
                            st.warning("⚠️ No preview content available")
                        
                        # Raw content (collapsible)
                        with st.expander("📄 Raw Content"):
                            raw_content = result.get("content", "")
                            if raw_content:
                                st.code(raw_content, language=result.get("language", "text"))
                            else:
                                st.info("No raw content available")
                    else:
                        st.error(f"❌ Preview failed: {result['error']}")
        
        # Batch preview
        if batch_files:
            st.header("📦 Batch Preview")
            if st.button("📦 Preview Multiple Files"):
                file_list = [f.strip() for f in batch_files.split('\n') if f.strip()]
                
                if file_list:
                    with st.spinner(f"Processing {len(file_list)} files..."):
                        result = make_api_request("/preview/batch", method="POST", data={"file_paths": file_list})
                        
                        if "error" not in result:
                            st.success(f"✅ Batch preview completed! {result.get('successful_previews', 0)}/{result.get('total_files', 0)} successful")
                            
                            # Display results
                            results = result.get("results", [])
                            for i, file_result in enumerate(results):
                                with st.expander(f"📄 {file_result.get('file_path', f'File {i+1}')}"):
                                    if file_result.get("success"):
                                        col_b1, col_b2 = st.columns(2)
                                        with col_b1:
                                            st.metric("Type", file_result.get("file_type", "Unknown"))
                                            st.metric("Language", file_result.get("language", "None"))
                                        
                                        with col_b2:
                                            st.metric("Length", f"{file_result.get('content_length', 0):,} chars")
                                            st.metric("Status", "✅ Success")
                                        
                                        # Preview
                                        preview_html = file_result.get("preview_html", "")
                                        if preview_html:
                                            st.components.v1.html(preview_html, height=300, scrolling=True)
                                    else:
                                        st.error(f"❌ Failed: {file_result.get('error', 'Unknown error')}")
                        else:
                            st.error(f"❌ Batch preview failed: {result['error']}")
    
    # Examples section
    st.header("💡 Example Files")
    
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        st.subheader("🐍 Python Code")
        example_python = """def hello_world():
    \"\"\"Simple hello world function\"\"\"
    print("Hello, World!")
    return True

# Main execution
if __name__ == "__main__":
    hello_world()"""
        st.code(example_python, language="python")
        if st.button("Try Python Example"):
            st.session_state.example_file = "example.py"
            st.session_state.example_content = example_python
    
    with col_ex2:
        st.subheader("📝 Markdown")
        example_markdown = """# Sample Markdown

## Features
- **Bold text**
- *Italic text*
- `Code snippets`

## Code Block
```python
print("Hello from markdown!")
```

[Link to GitHub](https://github.com)"""
        st.code(example_markdown, language="markdown")
        if st.button("Try Markdown Example"):
            st.session_state.example_file = "example.md"
            st.session_state.example_content = example_markdown
    
    with col_ex3:
        st.subheader("🎨 JSON Data")
        example_json = """{
  "name": "Sample Project",
  "version": "1.0.0",
  "description": "A sample JSON file",
  "features": [
    "Syntax highlighting",
    "Content preview",
    "File analysis"
  ],
  "metadata": {
    "author": "Developer",
    "license": "MIT"
  }
}"""
        st.code(example_json, language="json")
        if st.button("Try JSON Example"):
            st.session_state.example_file = "example.json"
            st.session_state.example_content = example_json
    
    # Quick test section
    st.header("⚡ Quick Test")
    
    test_files = [
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\src\\mcp_server_enhanced_tools.py",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\README.md",
        "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\config\\langflow_config.py"
    ]
    
    test_col1, test_col2, test_col3 = st.columns(3)
    
    for i, test_file in enumerate(test_files):
        with [test_col1, test_col2, test_col3][i]:
            if st.button(f"Test {Path(test_file).name}", key=f"test_{i}"):
                with st.spinner(f"Testing {Path(test_file).name}..."):
                    result = make_api_request("/preview/file", params={"file_path": test_file})
                    
                    if "error" not in result:
                        st.success(f"✅ {Path(test_file).name} preview successful!")
                        st.metric("Type", result.get("file_type", "Unknown"))
                        st.metric("Length", f"{result.get('content_length', 0):,} chars")
                    else:
                        st.error(f"❌ {Path(test_file).name} failed: {result['error']}")
    
    # Footer
    st.markdown("---")
    st.markdown("**Content Preview System** - Enhanced file viewing with syntax highlighting and rendering")
    st.markdown("Built with FastAPI, Streamlit, and modern web technologies")

if __name__ == "__main__":
    main()
