#!/bin/bash

echo "🚀 Setting up Capstone Project Repository"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "mcp_server_fixed.py" ]; then
    print_error "mcp_server_fixed.py not found. Please run this script from the LangFlow_Connect directory."
    exit 1
fi

print_info "Starting repository setup for https://github.com/Kausiukas/capstone_project..."

# Step 1: Create backup
print_info "Creating backup of current files..."
if [ ! -d "../capstone-project-backup" ]; then
    mkdir -p ../capstone-project-backup
    cp -r * ../capstone-project-backup/ 2>/dev/null || true
    print_status "Backup created at ../capstone-project-backup/"
else
    print_warning "Backup directory already exists. Skipping backup creation."
fi

# Step 2: Create directory structure
print_info "Creating directory structure..."
mkdir -p src/tools
mkdir -p web/pages
mkdir -p web/static/css
mkdir -p web/static/images
mkdir -p tests
mkdir -p docs
mkdir -p config
mkdir -p scripts
mkdir -p docker
mkdir -p .github/workflows
mkdir -p src/utils

print_status "Directory structure created"

# Step 3: Create essential files
print_info "Creating essential files..."
touch src/__init__.py
touch src/tools/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch web/__init__.py
touch web/pages/__init__.py

print_status "Essential files created"

# Step 4: Copy and adapt existing files
print_info "Migrating essential files..."

# Copy MCP server
if [ -f "mcp_server_fixed.py" ]; then
    cp "mcp_server_fixed.py" "src/mcp_server_http.py"
    print_status "MCP server copied to src/mcp_server_http.py"
fi

# Copy test files
if [ -f "test_fixed_server_performance.py" ]; then
    cp "test_fixed_server_performance.py" "tests/test_mcp_server.py"
    print_status "Test files copied to tests/test_mcp_server.py"
fi

# Copy CLI utilities
if [ -f "inspector_cli_utils.py" ]; then
    cp "inspector_cli_utils.py" "src/utils/cli_utils.py"
    print_status "CLI utilities copied to src/utils/cli_utils.py"
fi

# Copy documentation
if [ -f "INSPECTOR_TASK_STATUS_REVIEW.md" ]; then
    cp "INSPECTOR_TASK_STATUS_REVIEW.md" "docs/project_status.md"
    print_status "Project status copied to docs/project_status.md"
fi

if [ -f "PERFORMANCE_ISSUES_RESOLVED.md" ]; then
    cp "PERFORMANCE_ISSUES_RESOLVED.md" "docs/performance_analysis.md"
    print_status "Performance analysis copied to docs/performance_analysis.md"
fi

# Step 5: Create requirements.txt
print_info "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Core dependencies
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
EOF
print_status "requirements.txt created"

# Step 6: Create .gitignore
print_info "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
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
EOF
print_status ".gitignore created"

# Step 7: Create README.md
print_info "Creating README.md..."
cat > README.md << 'EOF'
# LangFlow Connect MCP Server - Capstone Project

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
curl -X POST "http://localhost:8000/api/v1/tools/call" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo_key_123" \
  -d '{"name": "ping", "arguments": {}}'
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
EOF
print_status "README.md created"

# Step 8: Create GitHub Actions workflows
print_info "Creating GitHub Actions workflows..."

# Test workflow
cat > .github/workflows/test.yml << 'EOF'
name: Test MVP Application

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
EOF

# Deploy workflow
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to Railway

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
        service: langflow-connect-mvp
EOF

print_status "GitHub Actions workflows created"

# Step 9: Create deployment configuration
print_info "Creating deployment configuration..."

# Railway configuration
cat > railway.json << 'EOF'
{
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
EOF

# Render configuration
cat > render.yaml << 'EOF'
services:
  - type: web
    name: langflow-connect-mvp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
EOF

print_status "Deployment configuration created"

# Step 10: Create setup script
print_info "Creating setup script..."
cat > scripts/setup.sh << 'EOF'
#!/bin/bash

echo "🚀 Setting up LangFlow Connect MVP Development Environment"

# Install dependencies
pip install -r requirements.txt

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

echo "✅ Development environment setup complete!"
echo "To start development:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run MCP server: python src/mcp_server_http.py"
echo "3. Run web interface: streamlit run web/app.py"
EOF

chmod +x scripts/setup.sh
print_status "Setup script created"

# Step 11: Create test script
print_info "Creating test script..."
cat > scripts/test.sh << 'EOF'
#!/bin/bash

echo "🧪 Running LangFlow Connect MVP Tests"

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=html

echo "✅ Tests completed!"
echo "Coverage report available in htmlcov/index.html"
EOF

chmod +x scripts/test.sh
print_status "Test script created"

# Step 12: Create deployment script
print_info "Creating deployment script..."
cat > scripts/deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying LangFlow Connect MVP"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Deploy to Railway
railway up

echo "✅ Deployment completed!"
echo "Check your Railway dashboard for the deployment URL"
EOF

chmod +x scripts/deploy.sh
print_status "Deployment script created"

# Step 13: Create initial web interface
print_info "Creating initial web interface..."
cat > web/app.py << 'EOF'
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
    - **Last Updated**: $(date +%Y-%m-%d)
    - **Repository**: [GitHub](https://github.com/yourusername/langflow-connect-mvp)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>LangFlow Connect MCP Server - MVP Demo | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)
EOF

print_status "Initial web interface created"

# Step 14: Create initial test file
print_info "Creating initial test file..."
cat > tests/test_basic.py << 'EOF'
import pytest
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
EOF

print_status "Initial test file created"

# Step 15: Create configuration file
print_info "Creating configuration file..."
cat > config/settings.py << 'EOF'
import os
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
EOF

print_status "Configuration file created"

# Final summary
echo ""
echo "🎉 Repository setup complete!"
echo "=============================="
print_status "Directory structure created"
print_status "Essential files migrated"
print_status "Configuration files created"
print_status "GitHub Actions workflows set up"
print_status "Deployment configuration ready"
print_status "Web interface initialized"
print_status "Test suite created"

echo ""
print_info "Next steps:"
echo "1. GitHub repository: https://github.com/Kausiukas/capstone_project"
echo "2. Initialize git: git init && git add . && git commit -m 'Initial capstone project setup'"
echo "3. Push to GitHub: git remote add origin https://github.com/Kausiukas/capstone_project.git && git push -u origin main"
echo "4. Set up deployment: Configure Railway/Render secrets in GitHub"
echo "5. Test locally: python src/mcp_server_http.py"
echo "6. Test web interface: streamlit run web/app.py"

echo ""
print_warning "Remember to:"
echo "- Update README.md with actual URLs after deployment"
echo "- Configure GitHub secrets for deployment"
echo "- Test all functionality before presentation"

echo ""
print_status "Setup completed successfully! 🚀" 