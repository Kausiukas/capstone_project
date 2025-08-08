# Integrated Dashboard Deployment Guide

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
