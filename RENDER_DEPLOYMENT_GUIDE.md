# 🎨 Render Deployment Guide - LangFlow Connect MVP

## Quick Deploy to Render (Free Tier)

### Step 1: Sign Up
1. Go to [https://render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. **No credit card required!** ✅

### Step 2: Create Web Service
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository: `https://github.com/Kausiukas/capstone_project`

### Step 3: Configure Service
```
Name: capstone-project-mvp
Environment: Python 3
Region: Choose closest to you
Branch: master
Root Directory: (leave empty)
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://capstone-project-mvp.onrender.com`

## 🎯 What You Get (Free Tier)

- ✅ **750 hours/month** (enough for 24/7 usage)
- ✅ **512MB RAM**
- ✅ **Shared CPU**
- ✅ **Automatic deployments** from GitHub
- ✅ **Free SSL certificate**
- ✅ **Custom domain support**
- ✅ **Environment variables**
- ✅ **Logs and monitoring**

## 🧪 Testing Your Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://capstone-project-mvp.onrender.com/health

# List tools
curl -H "X-API-Key: demo_key_123" https://capstone-project-mvp.onrender.com/tools/list

# Test ping
curl -X POST -H "X-API-Key: demo_key_123" -H "Content-Type: application/json" \
  -d '{"name":"ping","arguments":{}}' \
  https://capstone-project-mvp.onrender.com/api/v1/tools/call
```

## 🚀 Next Steps

1. **Test the API endpoints**
2. **Update your documentation** with the live URL
3. **Share the demo** with stakeholders
4. **Monitor usage** in Render dashboard

## 💡 Pro Tips

- **Environment Variables**: Add any API keys in Render dashboard
- **Custom Domain**: You can add your own domain later
- **Scaling**: Easy to upgrade to paid plan if needed
- **Monitoring**: Check logs in Render dashboard for debugging

## 🆘 Troubleshooting

**Common Issues:**
- **Build fails**: Check `requirements.txt` is correct
- **App crashes**: Check logs in Render dashboard
- **Port issues**: Make sure using `$PORT` environment variable
- **Import errors**: Verify all dependencies in `requirements.txt`

**Need Help?**
- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com 