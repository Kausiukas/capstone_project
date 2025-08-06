# 🚀 LangFlow Connect MVP - Single URL Deployment Guide

## 🎯 Goal
Deploy a **single URL** where users can access both the API and an interactive Streamlit dashboard.

## 📋 Current Setup
- **API Service**: `https://capstone-project-i1xm.onrender.com` ✅ (Already deployed)
- **Dashboard Service**: Need to deploy (This guide)

## 🛠️ Deployment Options

### **Option 1: Deploy to Render (Recommended)**

#### Step 1: Create New Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `langflow-connect-dashboard`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

**Environment Variables:**
```
PYTHON_VERSION=3.9.18
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

#### Step 2: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your dashboard will be available at: `https://langflow-connect-dashboard.onrender.com`

### **Option 2: Deploy to Your Custom Domain**

#### Step 1: Set Up Custom Domain
1. In your Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain (e.g., `dashboard.yourdomain.com`)
4. Configure DNS records as instructed by Render

#### Step 2: Update Configuration
In `streamlit_app.py`, update the API URL if needed:
```python
API_BASE_URL = "https://capstone-project-i1xm.onrender.com"  # Your existing API
```

## 🎯 Final Result

After deployment, you'll have:

### **Single URL Access:**
- **Dashboard**: `https://yourdomain.com` (or your Render URL)
- **API**: `https://capstone-project-i1xm.onrender.com` (backend)

### **User Experience:**
1. User visits your domain
2. Sees the beautiful Streamlit dashboard
3. Can interact with all tools through the web interface
4. API runs in the background (transparent to users)

## 🧪 Testing Your Deployment

### **Local Testing:**
```bash
# Test the dashboard locally
streamlit run streamlit_app.py

# Test the API
curl https://capstone-project-i1xm.onrender.com/health
```

### **Deployed Testing:**
1. Visit your dashboard URL
2. Click "🏥 Health Check" to verify API connection
3. Try the "🛠️ Tool Testing" section
4. Run performance tests

## 📊 Dashboard Features

The deployed dashboard includes:

### **🏠 Dashboard Page**
- Service status overview
- Quick action buttons
- Project information
- Real-time metrics

### **🛠️ Tool Testing Page**
- Interactive tool execution
- Parameter input forms
- Real-time results display
- Response time metrics

### **📊 Performance Page**
- Speed testing
- Load testing
- API endpoint validation
- Performance metrics

### **📚 API Docs Page**
- Complete API documentation
- Example curl commands
- Tool descriptions
- Authentication guide

### **🔧 System Status Page**
- Real-time system metrics
- Service health monitoring
- Configuration details
- Status updates

## 🔧 Troubleshooting

### **Common Issues:**

1. **Dashboard not loading:**
   - Check Render logs
   - Verify environment variables
   - Ensure `streamlit_app.py` is in root directory

2. **API connection failed:**
   - Verify API URL in `streamlit_app.py`
   - Check if API service is running
   - Test API directly with curl

3. **Port issues:**
   - Ensure `$PORT` environment variable is set
   - Check Render service configuration

### **Debug Commands:**
```bash
# Test API directly
curl https://capstone-project-i1xm.onrender.com/health

# Test dashboard locally
streamlit run streamlit_app.py --server.port 8501

# Check requirements
pip list | grep streamlit
```

## 🎉 Success Criteria

Your deployment is successful when:

✅ **Dashboard loads** at your domain  
✅ **Health check passes** from dashboard  
✅ **All tools work** through the interface  
✅ **Performance tests pass**  
✅ **API docs are accessible**  
✅ **System status shows** real-time data  

## 🚀 Next Steps

1. **Deploy the dashboard** using the guide above
2. **Test all functionality** through the web interface
3. **Share your domain** with users
4. **Monitor performance** and usage
5. **Gather feedback** and iterate

## 📞 Support

If you encounter issues:
1. Check Render deployment logs
2. Verify all environment variables
3. Test API connectivity
4. Review this guide for troubleshooting steps

---

**🎯 Result:** Users will have a single, beautiful URL where they can interact with your LangFlow Connect MVP through an intuitive web interface! 