#!/usr/bin/env python3
"""
Minimal MVP Setup Script
Creates only the essential files for the capstone project MVP demo
"""

import os
import shutil
from pathlib import Path

def create_minimal_mvp():
    """Create minimal MVP structure with only essential files"""
    
    print("🚀 Creating Minimal MVP for Capstone Project")
    print("=" * 50)
    
    # Create essential directories
    directories = [
        'src',
        'web',
        'tests',
        'docs',
        '.github/workflows'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Copy essential files
    essential_files = {
        'mcp_server_fixed.py': 'src/mcp_server_http.py',
        'test_fixed_server_performance.py': 'tests/test_mcp_server.py'
    }
    
    for source, dest in essential_files.items():
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"✅ Copied {source} to {dest}")
        else:
            print(f"⚠️  Source file {source} not found")
    
    # Create minimal requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.0
requests==2.31.0
pytest==7.4.3
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt")
    
    # Create minimal README.md
    readme_content = """# LangFlow Connect MCP Server - Capstone Project

## 🎯 Project Overview

This is a **Capstone Project** demonstration of the LangFlow Connect MCP (Model Context Protocol) server.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server
python src/mcp_server_http.py

# Run web interface (in another terminal)
streamlit run web/app.py
```

## 🛠 Features

- **5 Core Tools**: ping, read_file, list_files, get_system_status, analyze_code
- **Web Interface**: Streamlit-based demo interface
- **API Access**: RESTful API for programmatic access

## 📄 License

MIT License
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ Created README.md")
    
    # Create minimal .gitignore
    gitignore_content = """__pycache__/
*.pyc
venv/
.env
*.log
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    # Create minimal web interface
    web_app_content = '''import streamlit as st

st.title("🚀 LangFlow Connect MCP Server Demo")
st.markdown("Capstone Project - Basic MCP Server Demo")

st.header("Available Tools")
st.markdown("""
- **ping**: Test server connectivity
- **read_file**: Read file contents
- **list_files**: List directory contents
- **get_system_status**: Get server status
- **analyze_code**: Analyze code files
""")

st.header("Quick Test")
if st.button("Test Ping"):
    st.success("✅ Server is running!")
'''
    
    with open('web/app.py', 'w', encoding='utf-8') as f:
        f.write(web_app_content)
    print("✅ Created web/app.py")
    
    print("\n🎉 Minimal MVP setup complete!")
    print("\nNext steps:")
    print("1. git init")
    print("2. git add .")
    print("3. git commit -m 'Initial MVP setup'")
    print("4. git remote add origin https://github.com/Kausiukas/capstone_project.git")
    print("5. git push -u origin main")

if __name__ == "__main__":
    create_minimal_mvp() 