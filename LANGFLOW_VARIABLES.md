# 🔧 LangFlow Variables Configuration Guide

## 🎯 **Objective**
Expose current directory and PostgreSQL database connection as variables in LangFlow for use in workflows and MCP tools.

---

## 📊 **Current System Analysis**

### **Current Directory Structure**:
```
D:\GUI\System-Reference-Clean\LangFlow_Connect\
├── config/                    # Configuration files
├── src/                       # Source code
├── deployment/               # Deployment configs
├── data/                     # Data storage
├── logs/                     # Log files
├── cost_data/               # Cost tracking data
├── test_data/               # Test data
├── test_files/              # Test files
├── repositories/            # Repository data
├── cache/                   # Cache storage
├── temp/                    # Temporary files
└── venv/                    # Virtual environment
```

### **PostgreSQL Configuration** (from `config/langflow_config.py`):
```python
"database": {
    "host": os.getenv("POSTGRESQL_HOST", "localhost"),
    "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
    "database": os.getenv("POSTGRESQL_DATABASE", "langflow_connect"),
    "user": os.getenv("POSTGRESQL_USER", "postgres"),
    "password": os.getenv("POSTGRESQL_PASSWORD", ""),
    "ssl_mode": os.getenv("POSTGRESQL_SSL_MODE", "prefer"),
    "pool_size": int(os.getenv("POSTGRESQL_POOL_SIZE", "10")),
    "max_overflow": int(os.getenv("POSTGRESQL_MAX_OVERFLOW", "20")),
    "timeout": int(os.getenv("POSTGRESQL_TIMEOUT", "30")),
}
```

---

## 🚀 **Step-by-Step Implementation**

### **Step 1: Create LangFlow Variables Configuration**

#### **1.1 Create Variables Configuration File**
Create `langflow_variables_config.json`:

```json
{
  "variables": {
    "current_directory": {
      "name": "CURRENT_DIRECTORY",
      "value": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",
      "description": "Current working directory for LangFlow Connect",
      "type": "string",
      "category": "system"
    },
    "workspace_root": {
      "name": "WORKSPACE_ROOT",
      "value": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect",
      "description": "Root directory of the LangFlow Connect workspace",
      "type": "string",
      "category": "system"
    },
    "postgresql_host": {
      "name": "POSTGRESQL_HOST",
      "value": "localhost",
      "description": "PostgreSQL database host",
      "type": "string",
      "category": "database"
    },
    "postgresql_port": {
      "name": "POSTGRESQL_PORT",
      "value": "5432",
      "description": "PostgreSQL database port",
      "type": "integer",
      "category": "database"
    },
    "postgresql_database": {
      "name": "POSTGRESQL_DATABASE",
      "value": "langflow_connect",
      "description": "PostgreSQL database name",
      "type": "string",
      "category": "database"
    },
    "postgresql_user": {
      "name": "POSTGRESQL_USER",
      "value": "postgres",
      "description": "PostgreSQL database user",
      "type": "string",
      "category": "database"
    },
    "postgresql_connection_string": {
      "name": "POSTGRESQL_CONNECTION_STRING",
      "value": "postgresql://postgres:password@localhost:5432/langflow_connect",
      "description": "Complete PostgreSQL connection string",
      "type": "string",
      "category": "database"
    },
    "data_directory": {
      "name": "DATA_DIRECTORY",
      "value": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\data",
      "description": "Data storage directory",
      "type": "string",
      "category": "system"
    },
    "logs_directory": {
      "name": "LOGS_DIRECTORY",
      "value": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\logs",
      "description": "Log files directory",
      "type": "string",
      "category": "system"
    },
    "config_directory": {
      "name": "CONFIG_DIRECTORY",
      "value": "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect\\config",
      "description": "Configuration files directory",
      "type": "string",
      "category": "system"
    }
  },
  "categories": {
    "system": {
      "name": "System Variables",
      "description": "System-level configuration variables"
    },
    "database": {
      "name": "Database Variables",
      "description": "Database connection and configuration variables"
    }
  }
}
```

#### **1.2 Create Environment Variables File**
Create `.env` file with current values:

```env
# Current Directory and Workspace
CURRENT_DIRECTORY=D:\GUI\System-Reference-Clean\LangFlow_Connect
WORKSPACE_ROOT=D:\GUI\System-Reference-Clean\LangFlow_Connect
DATA_DIRECTORY=D:\GUI\System-Reference-Clean\LangFlow_Connect\data
LOGS_DIRECTORY=D:\GUI\System-Reference-Clean\LangFlow_Connect\logs
CONFIG_DIRECTORY=D:\GUI\System-Reference-Clean\LangFlow_Connect\config

# PostgreSQL Database Configuration
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=langflow_connect
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password_here
POSTGRESQL_SSL_MODE=prefer
POSTGRESQL_POOL_SIZE=10
POSTGRESQL_MAX_OVERFLOW=20
POSTGRESQL_TIMEOUT=30

# PostgreSQL Connection String (update password)
POSTGRESQL_CONNECTION_STRING=postgresql://postgres:your_password_here@localhost:5432/langflow_connect
```

### **Step 2: Extend MCP Server with Variable Tools**

#### **2.1 Add Variable Management Tools to MCP Server**
Add these tools to `mcp_langflow_connector_simple.py`:

```python
# Add to tools list
{
    "name": "get_system_variables",
    "description": "Get all system variables including current directory and database config",
    "inputSchema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category of variables to retrieve (system, database, all)",
                "enum": ["system", "database", "all"]
            }
        }
    }
},
{
    "name": "get_current_directory",
    "description": "Get current working directory information",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
},
{
    "name": "get_database_config",
    "description": "Get PostgreSQL database configuration",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_password": {
                "type": "boolean",
                "description": "Include password in output (default: false)",
                "default": false
            }
        }
    }
},
{
    "name": "test_database_connection",
    "description": "Test PostgreSQL database connection",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
}
```

#### **2.2 Implement Variable Management Methods**

```python
import os
import asyncio
import asyncpg
from typing import Dict, Any

class VariableManager:
    """Manages system variables and database configuration"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.workspace_root = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"
        self.load_environment_variables()
    
    def load_environment_variables(self):
        """Load environment variables from .env file"""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.system_variables = {
            "CURRENT_DIRECTORY": self.current_directory,
            "WORKSPACE_ROOT": self.workspace_root,
            "DATA_DIRECTORY": os.path.join(self.workspace_root, "data"),
            "LOGS_DIRECTORY": os.path.join(self.workspace_root, "logs"),
            "CONFIG_DIRECTORY": os.path.join(self.workspace_root, "config"),
        }
        
        self.database_variables = {
            "POSTGRESQL_HOST": os.getenv("POSTGRESQL_HOST", "localhost"),
            "POSTGRESQL_PORT": os.getenv("POSTGRESQL_PORT", "5432"),
            "POSTGRESQL_DATABASE": os.getenv("POSTGRESQL_DATABASE", "langflow_connect"),
            "POSTGRESQL_USER": os.getenv("POSTGRESQL_USER", "postgres"),
            "POSTGRESQL_PASSWORD": os.getenv("POSTGRESQL_PASSWORD", ""),
            "POSTGRESQL_SSL_MODE": os.getenv("POSTGRESQL_SSL_MODE", "prefer"),
        }
    
    def get_system_variables(self, category: str = "all") -> Dict[str, Any]:
        """Get system variables by category"""
        if category == "system":
            return self.system_variables
        elif category == "database":
            return {k: v for k, v in self.database_variables.items() if k != "POSTGRESQL_PASSWORD"}
        else:
            return {
                "system": self.system_variables,
                "database": {k: v for k, v in self.database_variables.items() if k != "POSTGRESQL_PASSWORD"}
            }
    
    async def test_database_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL database connection"""
        try:
            connection_string = f"postgresql://{self.database_variables['POSTGRESQL_USER']}:{self.database_variables['POSTGRESQL_PASSWORD']}@{self.database_variables['POSTGRESQL_HOST']}:{self.database_variables['POSTGRESQL_PORT']}/{self.database_variables['POSTGRESQL_DATABASE']}"
            
            conn = await asyncpg.connect(connection_string)
            await conn.close()
            
            return {
                "success": True,
                "message": "Database connection successful",
                "host": self.database_variables['POSTGRESQL_HOST'],
                "port": self.database_variables['POSTGRESQL_PORT'],
                "database": self.database_variables['POSTGRESQL_DATABASE']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": self.database_variables['POSTGRESQL_HOST'],
                "port": self.database_variables['POSTGRESQL_PORT'],
                "database": self.database_variables['POSTGRESQL_DATABASE']
            }
```

### **Step 3: Register Variables in LangFlow**

#### **3.1 Create LangFlow Variables Registration Script**
Create `register_langflow_variables.py`:

```python
#!/usr/bin/env python3
"""
LangFlow Variables Registration Script
Registers system and database variables in LangFlow
"""

import json
import os
import requests
from typing import Dict, Any

class LangFlowVariableManager:
    """Manages LangFlow variables registration"""
    
    def __init__(self, langflow_url: str = "http://localhost:7860"):
        self.langflow_url = langflow_url
        self.api_base = f"{langflow_url}/api/v1"
        
    def load_variables_config(self, config_file: str = "langflow_variables_config.json") -> Dict[str, Any]:
        """Load variables configuration from file"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def register_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register variables in LangFlow"""
        results = {
            "success": [],
            "failed": [],
            "total": 0
        }
        
        for var_id, var_config in config["variables"].items():
            try:
                # Register variable in LangFlow
                response = self._register_single_variable(var_config)
                
                if response.get("success"):
                    results["success"].append({
                        "variable": var_id,
                        "name": var_config["name"],
                        "category": var_config["category"]
                    })
                else:
                    results["failed"].append({
                        "variable": var_id,
                        "name": var_config["name"],
                        "error": response.get("error", "Unknown error")
                    })
                
                results["total"] += 1
                
            except Exception as e:
                results["failed"].append({
                    "variable": var_id,
                    "name": var_config.get("name", var_id),
                    "error": str(e)
                })
                results["total"] += 1
        
        return results
    
    def _register_single_variable(self, var_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a single variable in LangFlow"""
        try:
            # LangFlow variables API endpoint
            url = f"{self.api_base}/variables"
            
            payload = {
                "name": var_config["name"],
                "value": var_config["value"],
                "description": var_config["description"],
                "type": var_config["type"],
                "category": var_config["category"]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_registered_variables(self) -> Dict[str, Any]:
        """List all registered variables in LangFlow"""
        try:
            url = f"{self.api_base}/variables"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "variables": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main function to register variables"""
    print("🔧 LangFlow Variables Registration")
    print("=" * 50)
    
    # Initialize variable manager
    manager = LangFlowVariableManager()
    
    # Load configuration
    try:
        config = manager.load_variables_config()
        print(f"✅ Loaded configuration with {len(config['variables'])} variables")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Register variables
    print("\n📝 Registering variables in LangFlow...")
    results = manager.register_variables(config)
    
    # Display results
    print(f"\n📊 Registration Results:")
    print(f"   Total: {results['total']}")
    print(f"   Success: {len(results['success'])}")
    print(f"   Failed: {len(results['failed'])}")
    
    if results['success']:
        print(f"\n✅ Successfully registered:")
        for item in results['success']:
            print(f"   - {item['name']} ({item['category']})")
    
    if results['failed']:
        print(f"\n❌ Failed to register:")
        for item in results['failed']:
            print(f"   - {item['name']}: {item['error']}")
    
    # List registered variables
    print(f"\n📋 Current registered variables:")
    list_result = manager.list_registered_variables()
    
    if list_result['success']:
        for var in list_result['variables']:
            print(f"   - {var['name']}: {var['value']} ({var['type']})")
    else:
        print(f"   Error listing variables: {list_result['error']}")

if __name__ == "__main__":
    main()
```

### **Step 4: Create LangFlow Variables Component**

#### **4.1 Create Custom LangFlow Component**
Create `langflow_variables_component.py`:

```python
#!/usr/bin/env python3
"""
LangFlow Variables Component
Custom component for managing system and database variables
"""

from langflow import CustomComponent
from typing import Dict, Any, Optional
import os
import json

class SystemVariablesComponent(CustomComponent):
    """Custom component for system variables"""
    
    display_name = "System Variables"
    description = "Access system variables including current directory and database configuration"
    
    def build_config(self):
        return {
            "category": {
                "display_name": "Variable Category",
                "type": "str",
                "options": ["system", "database", "all"],
                "default": "all"
            },
            "include_sensitive": {
                "display_name": "Include Sensitive Data",
                "type": "bool",
                "default": False
            }
        }
    
    def build(self, category: str = "all", include_sensitive: bool = False) -> Dict[str, Any]:
        """Build the component output"""
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        current_dir = os.getcwd()
        workspace_root = "D:\\GUI\\System-Reference-Clean\\LangFlow_Connect"
        
        system_vars = {
            "CURRENT_DIRECTORY": current_dir,
            "WORKSPACE_ROOT": workspace_root,
            "DATA_DIRECTORY": os.path.join(workspace_root, "data"),
            "LOGS_DIRECTORY": os.path.join(workspace_root, "logs"),
            "CONFIG_DIRECTORY": os.path.join(workspace_root, "config"),
        }
        
        database_vars = {
            "POSTGRESQL_HOST": os.getenv("POSTGRESQL_HOST", "localhost"),
            "POSTGRESQL_PORT": os.getenv("POSTGRESQL_PORT", "5432"),
            "POSTGRESQL_DATABASE": os.getenv("POSTGRESQL_DATABASE", "langflow_connect"),
            "POSTGRESQL_USER": os.getenv("POSTGRESQL_USER", "postgres"),
        }
        
        if include_sensitive:
            database_vars["POSTGRESQL_PASSWORD"] = os.getenv("POSTGRESQL_PASSWORD", "")
        
        if category == "system":
            return {"variables": system_vars, "category": "system"}
        elif category == "database":
            return {"variables": database_vars, "category": "database"}
        else:
            return {
                "system_variables": system_vars,
                "database_variables": database_vars,
                "category": "all"
            }

class DatabaseConnectionComponent(CustomComponent):
    """Custom component for database connection testing"""
    
    display_name = "Database Connection Test"
    description = "Test PostgreSQL database connection"
    
    def build_config(self):
        return {}
    
    def build(self) -> Dict[str, Any]:
        """Test database connection"""
        try:
            import asyncpg
            import asyncio
            
            # Get database configuration
            from dotenv import load_dotenv
            load_dotenv()
            
            host = os.getenv("POSTGRESQL_HOST", "localhost")
            port = os.getenv("POSTGRESQL_PORT", "5432")
            database = os.getenv("POSTGRESQL_DATABASE", "langflow_connect")
            user = os.getenv("POSTGRESQL_USER", "postgres")
            password = os.getenv("POSTGRESQL_PASSWORD", "")
            
            # Test connection
            async def test_connection():
                connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                conn = await asyncpg.connect(connection_string)
                await conn.close()
                return True
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(test_connection())
            loop.close()
            
            if success:
                return {
                    "success": True,
                    "message": "Database connection successful",
                    "host": host,
                    "port": port,
                    "database": database
                }
            else:
                return {
                    "success": False,
                    "message": "Database connection failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Database connection test failed"
            }
```

---

## 🎯 **Success Metrics**

### **Primary Success Criteria**:
- [ ] **Variable Registration**: All 10 variables successfully registered in LangFlow
- [ ] **MCP Integration**: New variable tools accessible in MCP server
- [ ] **Database Connection**: PostgreSQL connection test successful
- [ ] **Directory Access**: Current directory and workspace paths accessible
- [ ] **Security**: Sensitive data (passwords) properly masked

### **Secondary Success Criteria**:
- [ ] **Performance**: Variable retrieval < 100ms
- [ ] **Reliability**: 99% uptime for variable access
- [ ] **Usability**: Variables easily accessible in LangFlow workflows
- [ ] **Documentation**: Complete documentation and examples

### **Error Handling**:
- [ ] **Graceful Degradation**: System continues working if variables unavailable
- [ ] **Error Logging**: All errors properly logged and reported
- [ ] **Fallback Values**: Default values provided for missing variables
- [ ] **Security Validation**: No sensitive data exposed in logs

---

## 🧪 **Testing Strategy**

### **Test 1: Variable Registration**
```bash
# Test variable registration
python register_langflow_variables.py
```

**Expected Result**: All variables registered successfully

### **Test 2: MCP Server Integration**
```bash
# Test MCP server with new tools
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py
```

**Test Commands**:
- `get_system_variables` with category "system"
- `get_current_directory`
- `get_database_config`
- `test_database_connection`

### **Test 3: LangFlow Workflow Integration**
Create test workflow in LangFlow:
1. **System Variables Component** → Get system variables
2. **Database Connection Component** → Test database connection
3. **Chat Output** → Display results

### **Test 4: Variable Usage in Workflows**
Test variables in existing workflows:
1. **Workflow 1**: Use `CURRENT_DIRECTORY` variable
2. **Workflow 2**: Use `DATA_DIRECTORY` variable
3. **Workflow 3**: Use database configuration variables

### **Test 5: Security Testing**
- Verify passwords not exposed in logs
- Test with `include_sensitive=false`
- Validate proper masking of sensitive data

---

## 📋 **Implementation Checklist**

### **Phase 1: Configuration Setup**
- [ ] Create `langflow_variables_config.json`
- [ ] Create `.env` file with current values
- [ ] Update PostgreSQL password in configuration
- [ ] Validate configuration file format

### **Phase 2: MCP Server Extension**
- [ ] Add variable management tools to MCP server
- [ ] Implement `VariableManager` class
- [ ] Add database connection testing
- [ ] Test MCP server with Inspector

### **Phase 3: LangFlow Integration**
- [ ] Create variable registration script
- [ ] Register variables in LangFlow
- [ ] Create custom LangFlow components
- [ ] Test variable access in workflows

### **Phase 4: Testing & Validation**
- [ ] Run all test scenarios
- [ ] Validate success metrics
- [ ] Test error handling
- [ ] Document results

### **Phase 5: Documentation & Deployment**
- [ ] Update documentation
- [ ] Create usage examples
- [ ] Deploy to production
- [ ] Monitor performance

---

## 🚀 **Quick Start Commands**

### **1. Setup Configuration**
```bash
# Create configuration files
cp langflow_variables_config.json.example langflow_variables_config.json
# Edit configuration with your values
```

### **2. Register Variables**
```bash
# Register variables in LangFlow
python register_langflow_variables.py
```

### **3. Test Integration**
```bash
# Test MCP server
npx @modelcontextprotocol/inspector python mcp_langflow_connector_simple.py
```

### **4. Create Test Workflow**
1. Open LangFlow at `http://localhost:7860`
2. Add "System Variables" component
3. Add "Database Connection Test" component
4. Connect to Chat Output
5. Run workflow

---

*LangFlow Variables Guide Created: August 1, 2025*  
*Status: READY FOR IMPLEMENTATION*  
*Next: Begin with Phase 1 Configuration Setup* 