# 🎨 Detailed Render Configuration Guide - LangFlow Connect MVP

## Complete Step-by-Step Configuration

### **Step 1: Source Code Section**
```
Repository: Kausiukas/capstone_project
Last commit: [shows recent commit time]
```
- **Action**: Click "Edit" if you need to change the repository
- **Note**: This should already be connected to your GitHub repo

### **Step 2: Name Section**
```
Name: capstone-project-mvp
```
- **Purpose**: Unique identifier for your service
- **Recommendation**: Use `capstone-project-mvp` or `langflow-connect-demo`
- **Note**: This will be part of your URL: `https://capstone-project-mvp.onrender.com`

### **Step 3: Project Section (Optional)**
```
Project: capstone_project
Type: Production
```
- **Purpose**: Organize multiple services together
- **Recommendation**: Leave as `capstone_project` or create a new project
- **Types Available**: Production, Development, Staging

### **Step 4: Language Section** ⚠️ **IMPORTANT**
```
Language: Python 3 (NOT Docker)
```
- **Current Setting**: Shows "Docker" - **CHANGE THIS!**
- **Correct Setting**: Select "Python 3" from dropdown
- **Why**: Our app is a Python FastAPI application, not a Docker container

### **Step 5: Branch Section**
```
Branch: master
```
- **Purpose**: Which Git branch to deploy from
- **Current**: Should be `master` (correct for our repo)
- **Note**: Any commits to this branch will trigger auto-deployment

### **Step 6: Region Section**
```
Region: Frankfurt (EU Central)
```
- **Purpose**: Where your server will be hosted
- **Recommendations**:
  - **Europe**: Frankfurt (EU Central) - Good for EU users
  - **US East**: Virginia (US East) - Good for US users
  - **Asia**: Singapore (Asia Pacific) - Good for Asian users
- **Note**: Services in same region can communicate privately

### **Step 7: Root Directory (Optional)**
```
Root Directory: [leave empty]
```
- **Purpose**: If your app is in a subdirectory
- **Our Case**: Leave empty (app is in root directory)
- **Example**: If app was in `src/` folder, you'd put `src`

### **Step 8: Dockerfile Path (IGNORE THIS SECTION)**
```
Dockerfile Path: [leave empty]
```
- **Why Ignore**: We're using Python, not Docker
- **Note**: This section is only relevant for Docker deployments

### **Step 9: Instance Type Section** 💰 **COST IMPORTANT**
```
For hobby projects:
✅ Free - 512 MB (RAM), 0.1 CPU, $0/month
```
- **Recommendation**: Select "Free" tier
- **What you get**:
  - 512 MB RAM
  - 0.1 CPU (shared)
  - 750 hours/month
  - Perfect for demos and MVPs
- **Limitations**:
  - Spins down after inactivity
  - No SSH access
  - No scaling
  - No persistent disks

### **Step 10: Environment Variables Section**
```
NAME_OF_VARIABLE: [leave empty for now]
value: [leave empty for now]
```
- **Purpose**: Store secrets and configuration
- **For our MVP**: We don't need any for basic functionality
- **Common uses**:
  - `DATABASE_URL` - Database connection strings
  - `API_KEY` - External service keys
  - `SECRET_KEY` - Application secrets

### **Step 11: Advanced Section** (Click to expand)

#### **11.1 Secret Files**
```
Secret Files: [leave empty]
```
- **Purpose**: Store files like `.env`, private keys
- **Our Case**: Not needed for basic MVP

#### **11.2 Health Check Path**
```
Health Check Path: /health
```
- **Purpose**: Endpoint for Render to check if app is running
- **Our Setting**: `/health` (matches our FastAPI health endpoint)
- **Why**: Render will ping this URL to ensure app is healthy

#### **11.3 Registry Credential**
```
Registry Credential: No credential
```
- **Purpose**: For private Docker images
- **Our Case**: Not needed (we're using Python)

#### **11.4 Docker Build Context Directory**
```
Docker Build Context Directory: [leave empty]
```
- **Purpose**: For Docker builds only
- **Our Case**: Not needed

#### **11.5 Dockerfile Path**
```
Dockerfile Path: [leave empty]
```
- **Purpose**: For Docker builds only
- **Our Case**: Not needed

#### **11.6 Docker Command**
```
Docker Command: [leave empty]
```
- **Purpose**: Override Docker CMD
- **Our Case**: Not needed

#### **11.7 Pre-Deploy Command**
```
Pre-Deploy Command: [leave empty]
```
- **Purpose**: Run before deployment (migrations, setup)
- **Our Case**: Not needed for basic MVP
- **Common uses**: Database migrations, asset compilation

#### **11.8 Auto-Deploy**
```
Auto-Deploy: On Commit
```
- **Purpose**: Automatically deploy when code changes
- **Recommendation**: Keep "On Commit"
- **Options**: On Commit, Manual

#### **11.9 Build Filters**
```
Included Paths: [leave empty]
Ignored Paths: [leave empty]
```
- **Purpose**: Control what triggers deployments
- **Our Case**: Leave empty (deploy on any change)

## 🎯 **Final Configuration Summary**

Here's exactly what your configuration should look like:

```
✅ Source Code: Kausiukas/capstone_project
✅ Name: capstone-project-mvp
✅ Project: capstone_project
✅ Language: Python 3 (CHANGE FROM DOCKER!)
✅ Branch: master
✅ Region: Frankfurt (EU Central) or your preferred region
✅ Root Directory: [empty]
✅ Instance Type: Free
✅ Environment Variables: [empty]
✅ Health Check Path: /health
✅ Auto-Deploy: On Commit
```

## 🚨 **Critical Steps to Fix**

1. **Change Language from Docker to Python 3**
2. **Set Health Check Path to `/health`**
3. **Select Free instance type**
4. **Verify branch is `master`**

## 🚀 **After Configuration**

1. Click **"Deploy Web Service"**
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://capstone-project-mvp.onrender.com`

## 🧪 **Testing After Deployment**

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

## 🆘 **Troubleshooting**

**If deployment fails:**
1. Check logs in Render dashboard
2. Verify `requirements.txt` is correct
3. Ensure `src/mcp_server_http.py` exists
4. Check that port is set to `$PORT` in start command

**If app crashes:**
1. Check health endpoint: `/health`
2. Review logs in Render dashboard
3. Verify all dependencies are in `requirements.txt` 