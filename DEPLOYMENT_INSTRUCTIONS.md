
# 🚀 Deploy Enhanced Server to Render

## Method 1: Update Existing Service (Recommended)

1. **Go to your Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your existing API service

2. **Update Start Command**
   - Go to Settings → Build & Deploy
   - Change Start Command to: `python src/mcp_server_simple_secure.py`
   - Click "Save Changes"

3. **Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for deployment to complete

## Method 2: Create New Service

1. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Name: `capstone-project-api-enhanced`

2. **Configure Service**
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/mcp_server_simple_secure.py`

3. **Environment Variables**
   - API_KEY: `demo_key_123`
   - PORT: `8000` (or leave empty for auto)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment

## Method 3: Using render.yaml (Advanced)

1. **Push render.yaml to your repository**
2. **Create Blueprint in Render**
3. **Deploy using Blueprint**

## Verification Steps

After deployment:

1. **Test Health Endpoint**
   ```bash
   curl https://your-service-url.onrender.com/health
   ```

2. **Test Security Headers**
   ```bash
   python test_security_headers.py
   ```

3. **Expected Results**
   - ✅ All 7 security headers present
   - ✅ Security score: 95%+
   - ✅ All tools working correctly

## Troubleshooting

### Common Issues:

1. **Server Won't Start**
   - Check logs for dependency issues
   - Verify Python version compatibility
   - Ensure all files are committed

2. **Security Headers Missing**
   - Verify middleware is loaded
   - Check CORS configuration
   - Test locally first

3. **Dashboard Connection Issues**
   - Update dashboard API URL
   - Check CORS origins
   - Verify authentication

### Rollback Plan:
If issues occur, change start command back to:
```bash
python src/mcp_server_fixed.py
```

## Security Headers Implemented

✅ X-Content-Type-Options: nosniff
✅ X-Frame-Options: DENY  
✅ X-XSS-Protection: 1; mode=block
✅ Strict-Transport-Security: max-age=31536000; includeSubDomains
✅ Content-Security-Policy: default-src 'self'
✅ Referrer-Policy: strict-origin-when-cross-origin
✅ Permissions-Policy: geolocation=(), microphone=(), camera=()

## Expected Improvements

- Security Score: 91.3% → 95.7% (+4.4%)
- Clickjacking Protection: ✅ Added
- XSS Protection: ✅ Enhanced
- MIME Sniffing Protection: ✅ Added
- HTTPS Enforcement: ✅ Added

---
Generated: 2025-08-07 01:43:38
