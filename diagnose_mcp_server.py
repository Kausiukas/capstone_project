#!/usr/bin/env python3
"""
MCP Server Diagnostic Script

This script diagnoses issues with our MCP server to help troubleshoot
problems with the MCP Inspector. Based on the official documentation at:
https://modelcontextprotocol.io/legacy/tools/inspector

Usage:
    python diagnose_mcp_server.py
"""

import sys
import os
import logging
import traceback
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServerDiagnostic:
    """Diagnostic tool for MCP server issues"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if details:
            print(f"  Details: {details}")
        print()
    
    def test_python_environment(self) -> bool:
        """Test Python environment"""
        try:
            print("🧪 Testing Python Environment...")
            
            # Check Python version
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                self.log_result("Python Version", False, f"Python 3.8+ required, found {version.major}.{version.minor}")
                return False
            else:
                self.log_result("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}")
            
            # Check if we're in a virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            self.log_result("Virtual Environment", in_venv, "Virtual environment detected" if in_venv else "No virtual environment")
            
            return True
            
        except Exception as e:
            self.log_result("Python Environment", False, f"Error: {e}")
            return False
    
    def test_imports(self) -> bool:
        """Test all required imports"""
        try:
            print("🧪 Testing Required Imports...")
            
            required_imports = [
                ("asyncio", "asyncio"),
                ("json", "json"),
                ("logging", "logging"),
                ("sys", "sys"),
                ("os", "os"),
                ("pathlib", "pathlib"),
                ("typing", "typing"),
                ("psycopg2", "psycopg2-binary"),
                ("numpy", "numpy"),
                ("pandas", "pandas"),
                ("psutil", "psutil")
            ]
            
            all_imports_ok = True
            
            for module_name, package_name in required_imports:
                try:
                    if module_name == "psycopg2":
                        # Special handling for psycopg2
                        import psycopg2
                        self.log_result(f"Import {module_name}", True, f"Successfully imported {package_name}")
                    else:
                        __import__(module_name)
                        self.log_result(f"Import {module_name}", True, f"Successfully imported {package_name}")
                except ImportError as e:
                    self.log_result(f"Import {module_name}", False, f"Failed to import {package_name}: {e}")
                    all_imports_ok = False
            
            return all_imports_ok
            
        except Exception as e:
            self.log_result("Import Testing", False, f"Error: {e}")
            return False
    
    def test_postgresql_connection(self) -> bool:
        """Test PostgreSQL connection"""
        try:
            print("🧪 Testing PostgreSQL Connection...")
            
            # First check if psycopg2 is available
            try:
                import psycopg2
            except ImportError:
                self.log_result("PostgreSQL Connection", False, "psycopg2 not available")
                return False
            
            # Test connection
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="postgres",
                user=os.getenv('USERNAME', 'postgres')
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            
            self.log_result("PostgreSQL Connection", True, f"Connected successfully: {version[0]}")
            
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log_result("PostgreSQL Connection", False, f"Connection failed: {e}")
            return False
    
    def test_pgvector_extension(self) -> bool:
        """Test pgvector extension"""
        try:
            print("🧪 Testing pgvector Extension...")
            
            # First check if psycopg2 is available
            try:
                import psycopg2
            except ImportError:
                self.log_result("pgvector Extension", False, "psycopg2 not available")
                return False
            
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="postgres",
                user=os.getenv('USERNAME', 'postgres')
            )
            
            cur = conn.cursor()
            
            # Try to create extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Check if extension exists
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            result = cur.fetchone()
            
            if result:
                self.log_result("pgvector Extension", True, "pgvector extension is available")
                cur.close()
                conn.close()
                return True
            else:
                self.log_result("pgvector Extension", False, "pgvector extension not found")
                cur.close()
                conn.close()
                return False
                
        except Exception as e:
            self.log_result("pgvector Extension", False, f"Extension test failed: {e}")
            return False
    
    def test_mcp_server_import(self) -> bool:
        """Test importing our MCP server"""
        try:
            print("🧪 Testing MCP Server Import...")
            
            # Add current directory to path
            sys.path.insert(0, os.getcwd())
            
            # Try to import the server module
            import mcp_langflow_connector_simple
            
            self.log_result("MCP Server Import", True, "Successfully imported MCP server module")
            return True
            
        except Exception as e:
            self.log_result("MCP Server Import", False, f"Import failed: {e}")
            traceback.print_exc()
            return False
    
    def test_mcp_server_initialization(self) -> bool:
        """Test MCP server initialization"""
        try:
            print("🧪 Testing MCP Server Initialization...")
            
            import mcp_langflow_connector_simple
            from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
            
            # Try to create an instance
            connector = SimpleLangFlowMCPConnector()
            
            self.log_result("MCP Server Initialization", True, "Successfully created MCP server instance")
            return True
            
        except Exception as e:
            self.log_result("MCP Server Initialization", False, f"Initialization failed: {e}")
            traceback.print_exc()
            return False
    
    def test_minimal_server(self) -> bool:
        """Test minimal MCP server"""
        try:
            print("🧪 Testing Minimal MCP Server...")
            
            # Check if minimal server exists
            minimal_server_path = Path("minimal_mcp_server.py")
            if not minimal_server_path.exists():
                self.log_result("Minimal Server File", False, "minimal_mcp_server.py not found")
                return False
            
            # Try to import minimal server
            import minimal_mcp_server
            from minimal_mcp_server import MinimalMCPServer
            
            # Try to create instance
            server = MinimalMCPServer()
            
            self.log_result("Minimal Server", True, "Minimal MCP server works correctly")
            return True
            
        except Exception as e:
            self.log_result("Minimal Server", False, f"Minimal server test failed: {e}")
            return False
    
    def test_inspector_availability(self) -> bool:
        """Test if MCP Inspector is available"""
        try:
            print("🧪 Testing MCP Inspector Availability...")
            
            # Try to run Inspector help command
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/inspector", "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_result("MCP Inspector", True, "MCP Inspector is available")
                return True
            else:
                self.log_result("MCP Inspector", False, f"Inspector not available: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("MCP Inspector", False, "Inspector command timed out")
            return False
        except FileNotFoundError:
            self.log_result("MCP Inspector", False, "npx not found - Node.js may not be installed")
            return False
        except Exception as e:
            self.log_result("MCP Inspector", False, f"Inspector test failed: {e}")
            return False
    
    def test_server_startup(self) -> bool:
        """Test server startup process"""
        try:
            print("🧪 Testing Server Startup Process...")
            
            # Try to start server with timeout
            result = subprocess.run(
                ["python", "mcp_langflow_connector_simple.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check if server started and then stopped (expected behavior)
            if result.returncode == 1:
                self.log_result("Server Startup", False, f"Server failed to start: {result.stderr}")
                return False
            else:
                self.log_result("Server Startup", True, "Server startup process completed")
                return True
                
        except subprocess.TimeoutExpired:
            self.log_result("Server Startup", True, "Server started and is running (timeout)")
            return True
        except Exception as e:
            self.log_result("Server Startup", False, f"Startup test failed: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate diagnostic report"""
        report = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": len([r for r in self.results if r["success"]]),
                "failed_tests": len([r for r in self.results if not r["success"]]),
                "success_rate": len([r for r in self.results if r["success"]]) / len(self.results) * 100 if self.results else 0
            },
            "results": self.results,
            "recommendations": []
        }
        
        # Generate recommendations based on failures
        failed_tests = [r for r in self.results if not r["success"]]
        
        for test in failed_tests:
            if "Python Version" in test["test"]:
                report["recommendations"].append("Upgrade Python to version 3.8 or higher")
            elif "Import" in test["test"]:
                report["recommendations"].append(f"Install missing package: {test['details']}")
            elif "PostgreSQL" in test["test"]:
                report["recommendations"].append("Install and configure PostgreSQL database")
            elif "pgvector" in test["test"]:
                report["recommendations"].append("Install pgvector extension for PostgreSQL")
            elif "MCP Server" in test["test"]:
                report["recommendations"].append("Fix MCP server code issues")
            elif "Inspector" in test["test"]:
                report["recommendations"].append("Install Node.js and MCP Inspector")
        
        return report
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🔍 MCP Server Diagnostic Tool")
        print("=" * 50)
        print()
        
        tests = [
            ("Python Environment", self.test_python_environment),
            ("Required Imports", self.test_imports),
            ("PostgreSQL Connection", self.test_postgresql_connection),
            ("pgvector Extension", self.test_pgvector_extension),
            ("MCP Server Import", self.test_mcp_server_import),
            ("MCP Server Initialization", self.test_mcp_server_initialization),
            ("Minimal Server", self.test_minimal_server),
            ("MCP Inspector", self.test_inspector_availability),
            ("Server Startup", self.test_server_startup)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Test error: {e}")
        
        # Generate and display report
        report = self.generate_report()
        
        print("📊 Diagnostic Report")
        print("=" * 50)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print()
        
        if report["recommendations"]:
            print("🔧 Recommendations:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"  {i}. {rec}")
            print()
        
        # Save report to file
        with open("mcp_diagnostic_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: mcp_diagnostic_report.json")
        
        return report["summary"]["success_rate"] >= 80  # 80% success threshold

def main():
    """Main function"""
    diagnostic = MCPServerDiagnostic()
    
    try:
        success = diagnostic.run_all_tests()
        
        if success:
            print("✅ Diagnostic completed successfully")
            print("🚀 Ready to test with MCP Inspector")
            print()
            print("Next steps:")
            print("1. Test minimal server: npx @modelcontextprotocol/inspector python minimal_mcp_server.py")
            print("2. Fix any issues identified above")
            print("3. Test full server when ready")
            sys.exit(0)
        else:
            print("❌ Diagnostic found issues")
            print("🔧 Please fix the issues above before testing with Inspector")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 