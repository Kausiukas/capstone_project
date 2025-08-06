# 🎨 Render Configuration - Quick Reference Card

## ⚠️ **CRITICAL SETTINGS TO CHANGE**

| Setting | Current | Should Be | Why |
|---------|---------|-----------|-----|
| **Language** | Docker | **Python 3** | Our app is Python FastAPI |
| **Health Check** | /healthz | **/health** | Matches our FastAPI endpoint |
| **Instance Type** | - | **Free** | Perfect for MVP demo |

## ✅ **CORRECT CONFIGURATION**

```
Name: capstone-project-mvp
Language: Python 3 ← CHANGE THIS!
Branch: master
Region: Frankfurt (EU Central)
Instance Type: Free ← SELECT THIS!
Health Check Path: /health ← SET THIS!
Auto-Deploy: On Commit
```

## 🚀 **DEPLOYMENT COMMANDS**

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT
```

## 🧪 **TEST ENDPOINTS**

```bash
# Health Check
https://capstone-project-mvp.onrender.com/health

# API Base
https://capstone-project-mvp.onrender.com/

# Tools List
https://capstone-project-mvp.onrender.com/tools/list
```

## 🆘 **COMMON ISSUES**

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` |
| App crashes | Check logs, verify `/health` endpoint |
| Wrong language | Change from Docker to Python 3 |
| Port issues | Use `$PORT` environment variable | 