# Langflow Connection Quick Start Guide

## 🚀 **Immediate Implementation Steps**

This guide provides the essential steps to begin implementing the secure Langflow connection and modular MCP system. Focus on Phase 1 critical tasks to establish the foundation.

---

## 📋 **Phase 1 Critical Tasks (This Week)**

### **Task 1: Set Up Development Environment**

#### **1.1 Create Module Structure**
```bash
# Create the modular directory structure
mkdir -p langflow_connection/modules/{module_1_main,module_2_support,module_3_economy,module_4_langflow}
mkdir -p langflow_connection/tests/{phase1,phase2,phase3,phase4}
mkdir -p langflow_connection/config
mkdir -p langflow_connection/docs
mkdir -p langflow_connection/deployment
```

#### **1.2 Install Required Dependencies**
```bash
# Install core dependencies
pip install websockets asyncio-mqtt jwt cryptography
pip install pytest pytest-asyncio pytest-mock
pip install psutil aiofiles python-dotenv

# Install Langflow-specific dependencies
pip install langflow-client langflow-sdk

# Install security dependencies
pip install certifi urllib3 requests
```

### **Task 2: Implement Module 4 - LangflowConnector Core**

#### **2.1 Create Basic LangflowConnector**
```python
# langflow_connection/modules/module_4_langflow/langflow_connector.py
import asyncio
import websockets
import json
import jwt
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class LangflowConnector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.websocket = None
        self.connected = False
        self.auth_token = None
        self.connection_health = {
            "last_heartbeat": None,
            "latency_ms": 0,
            "error_count": 0,
            "uptime": 0
        }
    
    async def connect(self) -> Dict[str, Any]:
        """Establish secure connection to Langflow"""
        try:
            # Create SSL context for secure connection
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Generate authentication token
            self.auth_token = self.generate_auth_token()
            
            # Connect to Langflow WebSocket
            self.websocket = await websockets.connect(
                self.config["websocket_url"],
                ssl=ssl_context,
                extra_headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            self.connected = True
            self.connection_health["last_heartbeat"] = datetime.now()
            
            # Start health monitoring
            asyncio.create_task(self.monitor_connection_health())
            
            return {"status": "connected", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_auth_token(self) -> str:
        """Generate JWT token for authentication"""
        payload = {
            "user_id": self.config.get("user_id", "mcp_client"),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.config["secret_key"], algorithm="HS256")
    
    async def send_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to Langflow"""
        if not self.connected or not self.websocket:
            return {"status": "error", "message": "Not connected"}
        
        try:
            message = {
                "type": "module_data",
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            await self.websocket.send(json.dumps(message))
            return {"status": "sent", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            self.connection_health["error_count"] += 1
            return {"status": "error", "message": str(e)}
    
    async def monitor_connection_health(self):
        """Monitor connection health and send heartbeats"""
        while self.connected:
            try:
                start_time = datetime.now()
                
                # Send heartbeat
                await self.send_data({"type": "heartbeat"})
                
                # Calculate latency
                latency = (datetime.now() - start_time).total_seconds() * 1000
                self.connection_health["latency_ms"] = latency
                self.connection_health["last_heartbeat"] = datetime.now()
                
                # Check for high latency
                if latency > 1000:  # >1 second
                    print(f"Warning: High latency detected: {latency}ms")
                
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                print(f"Connection health monitoring error: {e}")
                self.connection_health["error_count"] += 1
                await asyncio.sleep(5)
    
    async def disconnect(self):
        """Disconnect from Langflow"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
```

#### **2.2 Create Configuration Manager**
```python
# langflow_connection/config/langflow_config.py
import os
from typing import Dict, Any

class LangflowConfig:
    def __init__(self):
        self.config = {
            "websocket_url": os.getenv("LANGFLOW_WS_URL", "wss://localhost:3000/ws"),
            "api_url": os.getenv("LANGFLOW_API_URL", "http://localhost:3000/api"),
            "secret_key": os.getenv("LANGFLOW_SECRET_KEY", "your-secret-key-change-this"),
            "user_id": os.getenv("LANGFLOW_USER_ID", "mcp_client"),
            "connection_timeout": int(os.getenv("LANGFLOW_TIMEOUT", "60")),
            "keepalive_interval": int(os.getenv("LANGFLOW_KEEPALIVE", "30")),
            "max_reconnect_attempts": int(os.getenv("LANGFLOW_MAX_RETRIES", "5"))
        }
    
    def get_config(self) -> Dict[str, Any]:
        return self.config
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_fields = ["websocket_url", "secret_key"]
        for field in required_fields:
            if not self.config.get(field):
                return False
        return True
```

### **Task 3: Create Basic Testing Framework**

#### **3.1 Create Connection Test**
```python
# langflow_connection/tests/phase1/test_langflow_connection.py
import pytest
import asyncio
from modules.module_4_langflow.langflow_connector import LangflowConnector
from config.langflow_config import LangflowConfig

class TestLangflowConnection:
    @pytest.fixture
    async def connector(self):
        """Create LangflowConnector instance for testing"""
        config = LangflowConfig().get_config()
        connector = LangflowConnector(config)
        yield connector
        await connector.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self, connector):
        """Test basic connection establishment"""
        result = await connector.connect()
        assert result["status"] == "connected"
        assert connector.connected == True
    
    @pytest.mark.asyncio
    async def test_data_sending(self, connector):
        """Test sending data to Langflow"""
        await connector.connect()
        
        test_data = {
            "module": "test",
            "operation": "test_op",
            "data": {"test": "value"}
        }
        
        result = await connector.send_data(test_data)
        assert result["status"] == "sent"
    
    @pytest.mark.asyncio
    async def test_connection_health(self, connector):
        """Test connection health monitoring"""
        await connector.connect()
        
        # Wait for health monitoring to start
        await asyncio.sleep(2)
        
        assert connector.connection_health["last_heartbeat"] is not None
        assert connector.connection_health["latency_ms"] >= 0
```

#### **3.2 Create Security Test**
```python
# langflow_connection/tests/phase1/test_security.py
import pytest
import jwt
from modules.module_4_langflow.langflow_connector import LangflowConnector
from config.langflow_config import LangflowConfig

class TestSecurity:
    @pytest.fixture
    def config(self):
        return LangflowConfig().get_config()
    
    def test_auth_token_generation(self, config):
        """Test JWT token generation"""
        connector = LangflowConnector(config)
        token = connector.generate_auth_token()
        
        # Verify token can be decoded
        decoded = jwt.decode(token, config["secret_key"], algorithms=["HS256"])
        assert "user_id" in decoded
        assert "exp" in decoded
    
    def test_config_validation(self, config):
        """Test configuration validation"""
        config_manager = LangflowConfig()
        assert config_manager.validate_config() == True
    
    def test_invalid_config(self):
        """Test invalid configuration handling"""
        # Create config with missing required fields
        invalid_config = {"websocket_url": "wss://localhost:3000"}
        config_manager = LangflowConfig()
        config_manager.config = invalid_config
        
        assert config_manager.validate_config() == False
```

### **Task 4: Create Environment Setup**

#### **4.1 Environment Variables**
```bash
# .env file for Langflow connection
LANGFLOW_WS_URL=wss://localhost:3000/ws
LANGFLOW_API_URL=http://localhost:3000/api
LANGFLOW_SECRET_KEY=your-secret-key-change-this-in-production
LANGFLOW_USER_ID=mcp_client
LANGFLOW_TIMEOUT=60
LANGFLOW_KEEPALIVE=30
LANGFLOW_MAX_RETRIES=5

# Security settings
TLS_VERSION=1.3
JWT_EXPIRY=3600
MAX_RECONNECT_ATTEMPTS=5

# Module settings
MODULE_1_ENABLED=true
MODULE_2_ENABLED=true
MODULE_3_ENABLED=true
MODULE_4_ENABLED=true
```

#### **4.2 Quick Start Script**
```python
# langflow_connection/quick_start.py
#!/usr/bin/env python3
"""
Quick start script for Langflow connection setup
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_4_langflow.langflow_connector import LangflowConnector
from config.langflow_config import LangflowConfig

async def main():
    """Main quick start function"""
    print("🚀 Starting Langflow Connection Setup...")
    
    # Load configuration
    config_manager = LangflowConfig()
    if not config_manager.validate_config():
        print("❌ Invalid configuration. Please check your .env file.")
        return
    
    config = config_manager.get_config()
    print(f"✅ Configuration loaded: {config['websocket_url']}")
    
    # Create connector
    connector = LangflowConnector(config)
    
    # Test connection
    print("🔗 Testing connection to Langflow...")
    result = await connector.connect()
    
    if result["status"] == "connected":
        print("✅ Successfully connected to Langflow!")
        
        # Test data sending
        test_data = {
            "type": "test",
            "message": "Hello from MCP Server!",
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        send_result = await connector.send_data(test_data)
        if send_result["status"] == "sent":
            print("✅ Successfully sent test data to Langflow!")
        else:
            print(f"❌ Failed to send data: {send_result['message']}")
        
        # Keep connection alive for a few seconds
        print("⏳ Keeping connection alive for 10 seconds...")
        await asyncio.sleep(10)
        
        await connector.disconnect()
        print("✅ Disconnected from Langflow")
        
    else:
        print(f"❌ Failed to connect: {result['message']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 **Running the Tests**

### **Phase 1 Testing Commands**
```bash
# Navigate to project directory
cd langflow_connection

# Run Phase 1 tests
python -m pytest tests/phase1/ -v

# Run specific test files
python -m pytest tests/phase1/test_langflow_connection.py -v
python -m pytest tests/phase1/test_security.py -v

# Run with coverage
python -m pytest tests/phase1/ --cov=modules --cov-report=html
```

### **Quick Start Testing**
```bash
# Test the quick start script
python quick_start.py

# Expected output:
# 🚀 Starting Langflow Connection Setup...
# ✅ Configuration loaded: wss://localhost:3000/ws
# 🔗 Testing connection to Langflow...
# ✅ Successfully connected to Langflow!
# ✅ Successfully sent test data to Langflow!
# ⏳ Keeping connection alive for 10 seconds...
# ✅ Disconnected from Langflow
```

---

## 📊 **Phase 1 Success Criteria**

### **✅ Deliverables Checklist**
- [ ] **Secure WebSocket Connection**: TLS 1.3 encryption working
- [ ] **JWT Authentication**: Token generation and validation
- [ ] **Connection Health Monitoring**: Latency and uptime tracking
- [ ] **Basic Data Streaming**: Send/receive data with Langflow
- [ ] **Error Handling**: Graceful error recovery
- [ ] **Configuration Management**: Environment-based config
- [ ] **Test Suite**: Unit tests with >80% coverage
- [ ] **Documentation**: Basic API documentation

### **🔍 Validation Tests**
```bash
# Run all Phase 1 validation tests
python -m pytest tests/phase1/ -v --tb=short

# Expected results:
# test_langflow_connection.py::TestLangflowConnection::test_connection_establishment PASSED
# test_langflow_connection.py::TestLangflowConnection::test_data_sending PASSED
# test_langflow_connection.py::TestLangflowConnection::test_connection_health PASSED
# test_security.py::TestSecurity::test_auth_token_generation PASSED
# test_security.py::TestSecurity::test_config_validation PASSED
# test_security.py::TestSecurity::test_invalid_config PASSED
```

---

## 🚀 **Next Steps After Phase 1**

### **Week 2: Module Integration**
1. **Integrate Module 4 with existing MCP server**
2. **Create Module 1 workspace operations**
3. **Enhance Module 2 PostgreSQL vector agent**
4. **Integrate Module 3 cost tracking**

### **Week 3: Advanced Features**
1. **Real-time data visualization**
2. **Advanced flow management**
3. **Performance optimization**
4. **Advanced monitoring**

### **Week 4: Production Readiness**
1. **Docker containerization**
2. **Kubernetes deployment**
3. **Production monitoring**
4. **Documentation completion**

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Connection Refused**
```bash
# Check if Langflow is running
curl http://localhost:3000/api/health

# Check WebSocket endpoint
wscat -c ws://localhost:3000/ws
```

#### **Authentication Errors**
```bash
# Verify JWT token
python -c "
import jwt
token = 'your-token-here'
try:
    decoded = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
    print('Token valid:', decoded)
except Exception as e:
    print('Token invalid:', e)
"
```

#### **SSL/TLS Issues**
```bash
# Test SSL connection
openssl s_client -connect localhost:3000 -servername localhost

# Check certificate
openssl x509 -in cert.pem -text -noout
```

---

## 📞 **Support**

### **Immediate Help**
- **Configuration Issues**: Check `.env` file and environment variables
- **Connection Issues**: Verify Langflow is running and accessible
- **Test Failures**: Check test logs and ensure all dependencies installed

### **Documentation**
- **Full Strategy**: See `Langflow_connection.md`
- **API Reference**: See `docs/api_documentation.md`
- **Deployment Guide**: See `docs/deployment_guide.md`

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Implementation Phase  
**Next Review**: End of Week 1