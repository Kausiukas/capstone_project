# LangFlow Connect - Deployment Quick Reference

## 🚀 Quick Start Commands

### 1. Development Setup (5 minutes)
```bash
# Clone and setup
cd LangFlow_Connect
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Test functionality
python clean_demo.py
python simple_test.py

# Start system
python -m src.system_coordinator
```

### 2. Production Deployment
```bash
# Using deployment script (Linux/Mac)
./deployment/scripts/deploy.sh production deploy

# Manual production setup
sudo mkdir -p /opt/langflow-connect
sudo cp -r * /opt/langflow-connect/
sudo chown -R langflow:langflow /opt/langflow-connect
sudo systemctl enable langflow-connect
sudo systemctl start langflow-connect
```

### 3. Docker Deployment
```bash
# Build and run
cd deployment/docker
docker-compose up -d --build

# Check status
docker-compose ps
docker logs langflow-connect
```

### 4. Kubernetes Deployment
```bash
# Deploy to cluster
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods -n langflow-system
kubectl logs -n langflow-system deployment/langflow-connect
```

## 🔧 Essential Configuration

### Environment Variables (.env)
```env
# Required
LANGFLOW_WEBSOCKET_URL=ws://localhost:3000/ws
LANGFLOW_API_URL=http://localhost:3000/api/v1
JWT_SECRET_KEY=your_secret_here

# Optional
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

### Security Setup
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate TLS certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

## 📊 Monitoring Commands

### Health Checks
```bash
# Service status
systemctl status langflow-connect

# Health endpoint
curl http://localhost:8000/health

# Log monitoring
tail -f logs/langflow_connect.log
journalctl -u langflow-connect -f
```

### Performance Monitoring
```bash
# Resource usage
htop
docker stats langflow-connect
kubectl top pods -n langflow-system

# Database status
psql -h localhost -U langflow_user -d langflow_connect -c "SELECT version();"
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Issue: asyncpg Import Error
```bash
# Solution 1: Install asyncpg
pip install asyncpg

# Solution 2: Use clean demo (no PostgreSQL)
python clean_demo.py
```

#### Issue: Permission Denied
```bash
# Fix permissions
chmod +x deployment/scripts/deploy.sh
chmod 755 logs/
chmod 644 .env
```

#### Issue: Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8000
lsof -i :8000

# Kill process or change port
LANGFLOW_PORT=8001
```

#### Issue: Service Won't Start
```bash
# Check logs
journalctl -u langflow-connect --since "5 minutes ago"

# Restart service
systemctl restart langflow-connect
systemctl status langflow-connect
```

## 🔄 Maintenance Commands

### Updates
```bash
# Backup current installation
cp -r /opt/langflow-connect /opt/langflow-connect.backup

# Update code
git pull origin main
pip install -r requirements.txt --upgrade

# Restart service
systemctl restart langflow-connect
```

### Rollback
```bash
# Using deployment script
./deployment/scripts/deploy.sh production rollback

# Manual rollback
systemctl stop langflow-connect
rm -rf /opt/langflow-connect
cp -r /opt/langflow-connect.backup /opt/langflow-connect
systemctl start langflow-connect
```

### Backup & Restore
```bash
# Create backup
tar -czf langflow-backup-$(date +%Y%m%d).tar.gz /opt/langflow-connect

# Restore from backup
tar -xzf langflow-backup-20250101.tar.gz -C /
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Tests passing (`python clean_demo.py`)

### Production Deployment
- [ ] System user created (langflow)
- [ ] Installation directory created (/opt/langflow-connect)
- [ ] Files copied with correct permissions
- [ ] Systemd service configured
- [ ] Service enabled and started
- [ ] Health check passing

### Post-Deployment
- [ ] Service status verified
- [ ] Logs checked for errors
- [ ] Health endpoint responding
- [ ] Langflow connection tested
- [ ] Monitoring configured

## 🎯 Integration with Existing MCP Server

### Quick Integration
```python
# Add to existing MCP server (D:\GUI\2025-05-27\mcp_final_server.py)
from LangFlow_Connect.src.modules import *

# Initialize LangFlow Connect
langflow_system = LangFlowSystemCoordinator()
await langflow_system.initialize_system()

# Add tools to MCP server
tools.extend([
    "workspace_operations",
    "cost_tracking",
    "memory_management", 
    "langflow_connection"
])
```

## 📞 Support Commands

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python -u src/system_coordinator.py --verbose
```

### System Information
```bash
# Check system status
python -c "from src.system_coordinator import LangFlowSystemCoordinator; import asyncio; asyncio.run(LangFlowSystemCoordinator().get_system_status())"

# Module status
python -c "from src.modules import *; print('All modules imported successfully')"
```

---

**Quick Reference Version**: 1.0.0  
**Last Updated**: July 29, 2025  
**For detailed instructions**: See `DEPLOYMENT_GUIDE.md` 