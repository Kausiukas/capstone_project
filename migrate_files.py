#!/usr/bin/env python3
"""
File Migration Script for Capstone Project
Migrates essential files from current directory to new capstone project structure
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class FileMigrator:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.backup_dir = self.current_dir.parent / "capstone-project-backup"
        self.essential_files = [
            'mcp_server_fixed.py',
            'test_fixed_server_performance.py',
            'inspector_cli_utils.py',
            'INSPECTOR_TASK_STATUS_REVIEW.md',
            'PERFORMANCE_ISSUES_RESOLVED.md'
        ]
        
        # New structure mapping
        self.file_mapping = {
            'mcp_server_fixed.py': 'src/mcp_server_http.py',
            'test_fixed_server_performance.py': 'tests/test_mcp_server.py',
            'inspector_cli_utils.py': 'src/utils/cli_utils.py',
            'INSPECTOR_TASK_STATUS_REVIEW.md': 'docs/project_status.md',
            'PERFORMANCE_ISSUES_RESOLVED.md': 'docs/performance_analysis.md'
        }
    
    def print_status(self, message, status="INFO"):
        """Print colored status messages"""
        colors = {
            "SUCCESS": "\033[92m✅",
            "WARNING": "\033[93m⚠️",
            "ERROR": "\033[91m❌",
            "INFO": "\033[94mℹ️"
        }
        color = colors.get(status, colors["INFO"])
        print(f"{color} {message}\033[0m")
    
    def create_backup(self):
        """Create backup of current files"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.print_status("Creating backup directory", "INFO")
        
        # Copy all files to backup
        for item in self.current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', 'venv', '.venv']:
                if item.is_file():
                    shutil.copy2(item, self.backup_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, self.backup_dir / item.name, dirs_exist_ok=True)
        
        self.print_status(f"Backup created at {self.backup_dir}", "SUCCESS")
    
    def create_directory_structure(self):
        """Create new directory structure"""
        directories = [
            'src/tools',
            'src/utils',
            'web/pages',
            'web/static/css',
            'web/static/images',
            'tests',
            'docs',
            'config',
            'scripts',
            'docker',
            '.github/workflows'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        init_files = [
            'src/__init__.py',
            'src/tools/__init__.py',
            'src/utils/__init__.py',
            'tests/__init__.py',
            'web/__init__.py',
            'web/pages/__init__.py'
        ]
        
        for init_file in init_files:
            Path(init_file).touch()
        
        self.print_status("Directory structure created", "SUCCESS")
    
    def migrate_essential_files(self):
        """Migrate essential files to new structure"""
        migrated_count = 0
        
        for source_file, dest_path in self.file_mapping.items():
            source_path = Path(source_file)
            dest_path = Path(dest_path)
            
            if source_path.exists():
                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                self.print_status(f"Migrated {source_file} to {dest_path}", "SUCCESS")
                migrated_count += 1
            else:
                self.print_status(f"Source file {source_file} not found", "WARNING")
        
        self.print_status(f"Migrated {migrated_count} files", "SUCCESS")
    
    def create_requirements_txt(self):
        """Create requirements.txt file"""
        requirements_content = """# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
streamlit==1.28.0
requests==2.31.0

# Development dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0

# Optional dependencies
python-dotenv==1.0.0
"""
        
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        self.print_status("requirements.txt created", "SUCCESS")
    
    def create_gitignore(self):
        """Create .gitignore file"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.production

# Coverage
.coverage
htmlcov/
coverage.xml

# Temporary files
*.tmp
*.temp
temp/

# Backup files
*.bak
*.backup

# Development artifacts
__pycache__/
.pytest_cache/
reports/
results/
inspector_metrics/
static/
"""
        
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        self.print_status(".gitignore created", "SUCCESS")
    
    def create_readme(self):
        """Create README.md file"""
        readme_content = f"""# LangFlow Connect MCP Server - Capstone Project

## 🎯 Project Overview

This is a **Capstone Project** demonstration of the LangFlow Connect MCP (Model Context Protocol) server. The project showcases a functional MCP server that can be accessed globally via HTTP/HTTPS, providing basic tool functionality through a simple web interface.

## 🚀 Live Demo

- **Web Interface**: [Demo URL - To be added after deployment]
- **API Documentation**: [API Docs URL - To be added after deployment]
- **GitHub Repository**: https://github.com/Kausiukas/capstone_project

## 🛠 Features

- **5 Core Tools**: ping, read_file, list_files, get_system_status, analyze_code
- **Global Accessibility**: Deployed on cloud platform with HTTPS
- **Web Interface**: Streamlit-based demo interface for easy testing
- **API Access**: RESTful API for programmatic access
- **MCP Compliance**: Follows Model Context Protocol standards

## 📋 Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/Kausiukas/capstone_project.git
cd capstone_project

# Install dependencies
pip install -r requirements.txt

# Run MCP server
python src/mcp_server_http.py

# Run web interface (in another terminal)
streamlit run web/app.py
```

### API Testing
```bash
# Test API endpoints
curl -X GET "http://localhost:8000/health"
curl -X POST "http://localhost:8000/api/v1/tools/call" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: demo_key_123" \\
  -d '{{"name": "ping", "arguments": {{}}}}'
```

## 🔧 Technical Stack

- **Backend**: FastAPI with MCP protocol implementation
- **Frontend**: Streamlit web interface
- **Deployment**: Railway/Render with automatic CI/CD
- **Testing**: pytest with coverage reporting
- **Documentation**: Comprehensive API and deployment guides

## 📊 Project Status

- ✅ MCP Server Implementation
- ✅ HTTP Protocol Conversion
- 🔄 Web Interface Development (In Progress)
- 🔄 Automated Testing (In Progress)
- 🔄 Cloud Deployment (In Progress)
- 🔄 Documentation (In Progress)

## 🤝 Contributing

This is a capstone project demonstration. For contributions to the main LangFlow Connect project, please refer to the main repository.

## 📄 License

MIT License - see LICENSE file for details.

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.print_status("README.md created", "SUCCESS")
    
    def create_github_workflows(self):
        """Create GitHub Actions workflows"""
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Test workflow
        test_workflow = """name: Test MVP Application

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""
        
        with open(workflows_dir / 'test.yml', 'w', encoding='utf-8') as f:
            f.write(test_workflow)
        
        # Deploy workflow
        deploy_workflow = """name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Railway
      uses: bervProject/railway-deploy@v1.0.0
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
        service: capstone-project
"""
        
        with open(workflows_dir / 'deploy.yml', 'w', encoding='utf-8') as f:
            f.write(deploy_workflow)
        
        self.print_status("GitHub Actions workflows created", "SUCCESS")
    
    def create_deployment_configs(self):
        """Create deployment configuration files"""
        
        # Railway configuration
        railway_config = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT",
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        
        with open('railway.json', 'w', encoding='utf-8') as f:
            json.dump(railway_config, f, indent=2)
        
        # Render configuration
        render_config = """services:
  - type: web
    name: capstone-project
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
"""
        
        with open('render.yaml', 'w', encoding='utf-8') as f:
            f.write(render_config)
        
        self.print_status("Deployment configuration files created", "SUCCESS")
    
    def create_web_interface(self):
        """Create initial web interface"""
        web_dir = Path('web')
        web_dir.mkdir(exist_ok=True)
        
        app_content = '''import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="LangFlow Connect MCP Server Demo",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 LangFlow Connect MCP Server Demo")
st.markdown("A minimal viable product demonstration of the MCP server")

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
    if tool == "read_file":
        file_path = st.text_input("File Path", "README.md")
    elif tool == "list_files":
        directory = st.text_input("Directory", ".")
    elif tool == "analyze_code":
        file_path = st.text_input("File Path", "src/mcp_server_http.py")
    
    # Execute tool
    if st.button("🚀 Execute Tool", type="primary"):
        with st.spinner("Executing tool..."):
            try:
                # For demo purposes, simulate API call
                if tool == "ping":
                    result = {"content": [{"type": "text", "text": "pong"}]}
                elif tool == "read_file":
                    result = {"content": [{"type": "text", "text": f"File contents of {file_path} (simulated)"}]}
                elif tool == "list_files":
                    result = {"content": [{"type": "text", "text": f"Files in {directory}: README.md, app.py, requirements.txt"}]}
                elif tool == "get_system_status":
                    result = {"content": [{"type": "text", "text": json.dumps({
                        "status": "healthy",
                        "uptime": "1 hour",
                        "memory_usage": "45%",
                        "cpu_usage": "12%"
                    }, indent=2)}]}
                elif tool == "analyze_code":
                    result = {"content": [{"type": "text", "text": json.dumps({
                        "file_path": file_path,
                        "language": "python",
                        "lines_of_code": 150,
                        "complexity": "medium",
                        "analysis": "Code appears well-structured"
                    }, indent=2)}]}
                
                st.success("✅ Tool executed successfully!")
                st.json(result)
                
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
    - **Repository**: [GitHub](https://github.com/yourusername/langflow-connect-mvp)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>LangFlow Connect MCP Server - MVP Demo | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)
'''
        
        with open(web_dir / 'app.py', 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        self.print_status("Web interface created", "SUCCESS")
    
    def create_test_files(self):
        """Create initial test files"""
        tests_dir = Path('tests')
        tests_dir.mkdir(exist_ok=True)
        
        test_content = '''import pytest
from fastapi.testclient import TestClient
from src.mcp_server_http import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_tools_list_endpoint():
    """Test tools list endpoint"""
    response = client.get("/tools/list", headers={"api-key": "demo_key_123"})
    assert response.status_code == 200
    assert "tools" in response.json()

def test_tool_call_endpoint():
    """Test tool call endpoint"""
    response = client.post(
        "/api/v1/tools/call",
        headers={"X-API-Key": "demo_key_123"},
        json={"name": "ping", "arguments": {}}
    )
    assert response.status_code == 200
    assert "content" in response.json()

def test_invalid_api_key():
    """Test invalid API key"""
    response = client.get("/tools/list", headers={"api-key": "invalid_key"})
    assert response.status_code == 401
'''
        
        with open(tests_dir / 'test_basic.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        self.print_status("Test files created", "SUCCESS")
    
    def create_config_files(self):
        """Create configuration files"""
        config_dir = Path('config')
        config_dir.mkdir(exist_ok=True)
        
        settings_content = '''import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    app_name: str = "LangFlow Connect MCP Server MVP"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Authentication
    demo_api_key: str = "demo_key_123"
    
    # CORS settings
    allowed_origins: list = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
        
        with open(config_dir / 'settings.py', 'w', encoding='utf-8') as f:
            f.write(settings_content)
        
        self.print_status("Configuration files created", "SUCCESS")
    
    def run_migration(self):
        """Run complete migration process"""
        self.print_status("Starting file migration process...", "INFO")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Create directory structure
            self.create_directory_structure()
            
            # Step 3: Migrate essential files
            self.migrate_essential_files()
            
            # Step 4: Create new files
            self.create_requirements_txt()
            self.create_gitignore()
            self.create_readme()
            self.create_github_workflows()
            self.create_deployment_configs()
            self.create_web_interface()
            self.create_test_files()
            self.create_config_files()
            
            self.print_status("Migration completed successfully!", "SUCCESS")
            
            # Print next steps
            print("\n" + "="*50)
            self.print_status("Next steps:", "INFO")
            print("1. GitHub repository: https://github.com/Kausiukas/capstone_project")
            print("2. Initialize git: git init && git add . && git commit -m 'Initial capstone project setup'")
            print("3. Push to GitHub: git remote add origin https://github.com/Kausiukas/capstone_project.git && git push -u origin main")
            print("4. Set up deployment: Configure Railway/Render secrets in GitHub")
            print("5. Test locally: python src/mcp_server_http.py")
            print("6. Test web interface: streamlit run web/app.py")
            print("="*50)
            
        except Exception as e:
            self.print_status(f"Migration failed: {str(e)}", "ERROR")
            raise

def main():
    """Main function"""
    migrator = FileMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main() 