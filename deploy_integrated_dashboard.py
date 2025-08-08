#!/usr/bin/env python3
"""
Deploy Integrated Dashboard to GitHub Repository
This script updates the capstone project with the unified dashboard
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
import time

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed: {e.stderr}"

def check_git_status():
    """Check if we're in a git repository and get status"""
    success, output = run_command("git status --porcelain")
    if not success:
        return False, "Not a git repository or git not available"
    
    return True, output

def commit_and_push_changes(commit_message):
    """Commit and push changes to GitHub"""
    print(f"🔄 Committing changes: {commit_message}")
    
    # Add all files
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {output}")
        return False
    
    # Commit
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {output}")
        return False
    
    # Push
    success, output = run_command("git push origin master")
    if not success:
        print(f"❌ Failed to push: {output}")
        return False
    
    print("✅ Changes committed and pushed successfully!")
    return True

def backup_existing_files():
    """Backup existing dashboard files"""
    backup_dir = "backup_dashboards"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "streamlit_app.py",
        "web/content_preview_dashboard.py",
        "web/performance_dashboard.py",
        "web/enhanced_tools_dashboard.py",
        "web/mvp_dashboard.py"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"📦 Backed up: {file_path} -> {backup_path}")
    
    return backup_dir

def remove_duplicate_files():
    """Remove duplicate dashboard files"""
    files_to_remove = [
        "web/content_preview_dashboard.py",
        "web/performance_dashboard.py", 
        "web/enhanced_tools_dashboard.py",
        "web/mvp_dashboard.py"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removed duplicate: {file_path}")

def update_requirements():
    """Update requirements.txt with necessary dependencies"""
    requirements_content = """fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
requests==2.31.0
pandas==2.1.3
plotly==5.17.0
aiofiles==23.2.1
aiohttp==3.9.1
PyJWT==2.8.0
psutil==5.9.6
"""
    
    with open("requirements.txt", "w", encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("📝 Updated requirements.txt")

def update_readme():
    """Update README.md with integrated dashboard information"""
    readme_content = """# LangFlow Connect MVP - Integrated Dashboard

## 🎯 Project Overview

This is a **Capstone Project** demonstration of the LangFlow Connect MCP (Model Context Protocol) server with integrated Content Preview and Performance Monitoring systems.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server
python src/mcp_server_enhanced_tools.py

# Run integrated dashboard
streamlit run streamlit_app_integrated.py
```

## 🛠 Features

### Core Tools
- **5 Core Tools**: ping, read_file, list_files, get_system_status, analyze_code
- **Universal File Access**: Local, GitHub, and HTTP file support
- **Web Interface**: Streamlit-based unified dashboard
- **API Access**: RESTful API for programmatic access

### Content Preview System
- **Syntax Highlighting**: Support for 20+ programming languages
- **Markdown Rendering**: Full markdown to HTML conversion
- **Image Preview**: Base64 encoding for inline display
- **Batch Processing**: Preview multiple files simultaneously
- **File Analysis**: Automatic type detection and capabilities

### Performance Monitoring
- **Real-time Metrics**: Response times, success rates, error counts
- **System Monitoring**: CPU, memory, disk usage tracking
- **Performance Alerts**: Automated alerting for issues
- **Health Monitoring**: Comprehensive system health checks
- **Tool-specific Metrics**: Individual tool performance tracking

## 📊 Dashboard Sections

1. **🏠 Dashboard** - Overview and quick actions
2. **🛠️ Tool Testing** - Interactive tool execution
3. **👁️ Content Preview** - File preview and analysis
4. **📊 Performance Monitoring** - Real-time metrics and alerts
5. **📚 API Docs** - Complete API documentation
6. **🔧 System Status** - System health and configuration

## 🔧 Configuration

The dashboard automatically connects to the deployed API at:
`https://capstone-project-api-jg3n.onrender.com`

You can change the API URL in the sidebar configuration.

## 📄 License

MIT License

## 🎯 Capstone Project Status

✅ **Complete** - All systems integrated and functional
- Core MCP tools operational
- Content Preview System active
- Performance Monitoring active
- Unified dashboard deployed
- Universal file access working
- Real-time metrics collection
- Comprehensive error handling
"""
    
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📝 Updated README.md")

def create_deployment_guide():
    """Create a deployment guide for the integrated system"""
    guide_content = """# Integrated Dashboard Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the integrated LangFlow Connect MVP dashboard with Content Preview and Performance Monitoring systems.

## 📋 Prerequisites

- Python 3.9+
- Git repository access
- Render.com account (for API deployment)
- Streamlit Cloud account (for dashboard deployment)

## 🔧 Backend API Deployment

### 1. Deploy to Render

1. **Create New Web Service**
   - Service Name: `capstone-project-api`
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.mcp_server_enhanced_tools:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   ```
   PYTHON_VERSION=3.9
   ```

3. **Deploy**
   - Connect your GitHub repository
   - Deploy the service
   - Note the generated URL

### 2. Verify API Deployment

Test the API endpoints:
```bash
curl -X GET https://your-api.onrender.com/health
curl -X GET https://your-api.onrender.com/tools/list -H "X-API-Key: demo_key_123"
```

## 🎨 Dashboard Deployment

### 1. Deploy to Streamlit Cloud

1. **Create New App**
   - App Name: `capstone-project-dashboard`
   - Repository: Your GitHub repository
   - Main file path: `streamlit_app_integrated.py`

2. **Configuration**
   - Python version: 3.9
   - Dependencies: `requirements.txt`

3. **Deploy**
   - Deploy the app
   - Note the generated URL

### 2. Update API URL

In the deployed dashboard:
1. Go to the System Status page
2. Update the API URL to match your Render deployment
3. Test the connection

## 🔄 Integration Steps

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/Kausiukas/capstone_project.git
cd capstone_project

# Create integrated dashboard
python deploy_integrated_dashboard.py
```

### 2. File Structure

```
capstone_project/
├── streamlit_app_integrated.py    # Main unified dashboard
├── src/
│   └── mcp_server_enhanced_tools.py  # Backend API with all features
├── web/                           # Legacy dashboards (backed up)
├── requirements.txt               # Updated dependencies
├── README.md                      # Updated documentation
└── deployment/                    # Deployment configurations
```

### 3. Remove Duplicates

The deployment script automatically:
- ✅ Backs up existing dashboard files
- ✅ Removes duplicate dashboard files
- ✅ Updates requirements.txt
- ✅ Updates README.md
- ✅ Commits changes to GitHub

## 🧪 Testing

### 1. Local Testing

```bash
# Test backend API
python src/mcp_server_enhanced_tools.py

# Test dashboard
streamlit run streamlit_app_integrated.py
```

### 2. Feature Testing

1. **Core Tools**
   - Test ping, list_files, read_file, get_system_status, analyze_code
   - Verify universal file access (local, GitHub, HTTP)

2. **Content Preview**
   - Test file analysis and preview
   - Verify syntax highlighting
   - Test markdown rendering
   - Test batch preview

3. **Performance Monitoring**
   - Test metrics collection
   - Verify alerts system
   - Test health monitoring
   - Check real-time updates

## 🔧 Configuration

### API Configuration

Update the API URL in the dashboard:
```python
DEFAULT_API_URL = "https://your-api.onrender.com"
```

### Environment Variables

For production deployment:
```bash
API_BASE_URL=https://your-api.onrender.com
API_KEY=your_secure_api_key
```

## 📊 Monitoring

### Dashboard Monitoring

- **Health Checks**: Regular API connectivity tests
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Failed request monitoring
- **User Analytics**: Dashboard usage statistics

### API Monitoring

- **System Metrics**: CPU, memory, disk usage
- **Request Metrics**: Response times, success rates
- **Error Tracking**: Failed requests and exceptions
- **Resource Usage**: File access patterns and performance

## 🚨 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check API URL configuration
   - Verify API is running on Render
   - Check API key authentication

2. **Content Preview Not Working**
   - Verify file paths are accessible
   - Check file permissions
   - Test with simple text files first

3. **Performance Metrics Missing**
   - Check performance monitoring is enabled
   - Verify metrics collection is running
   - Check for any error logs

### Debug Commands

```bash
# Check API health
curl -X GET https://your-api.onrender.com/health

# Test content preview
curl -X GET "https://your-api.onrender.com/preview/file?file_path=README.md" -H "X-API-Key: demo_key_123"

# Test performance metrics
curl -X GET https://your-api.onrender.com/performance/metrics -H "X-API-Key: demo_key_123"
```

## 🎯 Success Criteria

✅ **Deployment Complete** when:
- Backend API is accessible and responding
- Dashboard is deployed and functional
- All features are working (tools, preview, monitoring)
- Documentation is updated
- Repository is clean and organized

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Test individual components
4. Check deployment logs
"""
    
    with open("INTEGRATED_DEPLOYMENT_GUIDE.md", "w", encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📝 Created INTEGRATED_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment function"""
    print("🚀 LangFlow Connect MVP - Integrated Dashboard Deployment")
    print("=" * 60)
    
    # Check git status
    print("🔍 Checking git status...")
    success, status = check_git_status()
    if not success:
        print(f"❌ Git status check failed: {status}")
        return False
    
    print("✅ Git repository ready")
    
    # Backup existing files
    print("\n📦 Backing up existing dashboard files...")
    backup_dir = backup_existing_files()
    print(f"✅ Backup completed: {backup_dir}")
    
    # Remove duplicate files
    print("\n🗑️ Removing duplicate dashboard files...")
    remove_duplicate_files()
    print("✅ Duplicate files removed")
    
    # Rename integrated dashboard
    if os.path.exists("streamlit_app_integrated.py"):
        shutil.move("streamlit_app_integrated.py", "streamlit_app.py")
        print("✅ Renamed integrated dashboard to streamlit_app.py")
    
    # Update requirements
    print("\n📝 Updating requirements.txt...")
    update_requirements()
    
    # Update README
    print("\n📝 Updating README.md...")
    update_readme()
    
    # Create deployment guide
    print("\n📝 Creating deployment guide...")
    create_deployment_guide()
    
    # Commit and push changes
    print("\n🔄 Committing changes to GitHub...")
    commit_message = "feat: Integrate Content Preview and Performance Monitoring into unified dashboard"
    success = commit_and_push_changes(commit_message)
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Summary:")
        print("✅ Integrated dashboard created")
        print("✅ Duplicate files removed")
        print("✅ Requirements updated")
        print("✅ Documentation updated")
        print("✅ Changes committed to GitHub")
        print("\n🚀 Next steps:")
        print("1. Deploy to Streamlit Cloud using streamlit_app.py")
        print("2. Update API URL in the deployed dashboard")
        print("3. Test all features (tools, preview, monitoring)")
        print("4. Verify integration is working correctly")
    else:
        print("\n❌ Deployment failed!")
        print("Check the error messages above and try again.")
    
    return success

if __name__ == "__main__":
    main()
