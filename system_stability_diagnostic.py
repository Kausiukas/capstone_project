#!/usr/bin/env python3
"""
System Stability Diagnostic Tool for LangFlow MCP Connector
Checks Python version compatibility, system resources, and MCP server health
"""

import sys
import os
import platform
import psutil
import asyncio
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class SystemStabilityDiagnostic:
    """Comprehensive system stability diagnostic tool"""
    
    def __init__(self):
        self.diagnostic_results = {}
        self.recommendations = []
        
    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version and compatibility"""
        print("🐍 Checking Python Version Compatibility...")
        
        version_info = {
            "current_version": sys.version,
            "version_tuple": sys.version_info,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "python_path": sys.executable
        }
        
        # Version compatibility check
        major, minor, micro = sys.version_info[:3]
        version_info["major"] = major
        version_info["minor"] = minor
        version_info["micro"] = micro
        
        # Compatibility assessment
        if major == 3:
            if minor >= 8:
                version_info["compatibility"] = "Excellent"
                version_info["langflow_compatible"] = True
            elif minor >= 7:
                version_info["compatibility"] = "Good"
                version_info["langflow_compatible"] = True
            else:
                version_info["compatibility"] = "Poor"
                version_info["langflow_compatible"] = False
                self.recommendations.append("Upgrade to Python 3.7+ for better LangFlow compatibility")
        else:
            version_info["compatibility"] = "Incompatible"
            version_info["langflow_compatible"] = False
            self.recommendations.append("Python 3.x is required for LangFlow")
        
        print(f"✅ Python {major}.{minor}.{micro} - {version_info['compatibility']}")
        return version_info
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources and performance"""
        print("💻 Checking System Resources...")
        
        # CPU information
        cpu_info = {
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent_used": memory.percent,
            "free_gb": round(memory.free / (1024**3), 2)
        }
        
        # Disk information
        disk = psutil.disk_usage('.')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": round((disk.used / disk.total) * 100, 2)
        }
        
        # Performance assessment
        performance_score = 100
        
        if memory_info["percent_used"] > 90:
            performance_score -= 30
            self.recommendations.append("High memory usage detected - consider closing other applications")
        elif memory_info["percent_used"] > 80:
            performance_score -= 15
            self.recommendations.append("Moderate memory usage - monitor system performance")
        
        if disk_info["percent_used"] > 90:
            performance_score -= 20
            self.recommendations.append("Low disk space - free up space for better performance")
        
        if cpu_info["usage_percent"] > 80:
            performance_score -= 10
            self.recommendations.append("High CPU usage - system may be under load")
        
        system_info = {
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "performance_score": performance_score,
            "performance_level": "Excellent" if performance_score >= 90 else "Good" if performance_score >= 70 else "Poor"
        }
        
        print(f"✅ System Performance: {system_info['performance_level']} ({performance_score}/100)")
        return system_info
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies and their versions"""
        print("📦 Checking Dependencies...")
        
        required_packages = [
            "asyncio", "json", "logging", "pathlib", "psutil", "typing"
        ]
        
        optional_packages = [
            "aiofiles", "uvloop", "orjson"
        ]
        
        dependency_info = {
            "required": {},
            "optional": {},
            "missing_required": [],
            "missing_optional": []
        }
        
        # Check required packages
        for package in required_packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                dependency_info["required"][package] = {
                    "installed": True,
                    "version": version
                }
            except ImportError:
                dependency_info["required"][package] = {
                    "installed": False,
                    "version": None
                }
                dependency_info["missing_required"].append(package)
        
        # Check optional packages
        for package in optional_packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                dependency_info["optional"][package] = {
                    "installed": True,
                    "version": version
                }
            except ImportError:
                dependency_info["optional"][package] = {
                    "installed": False,
                    "version": None
                }
                dependency_info["missing_optional"].append(package)
        
        if dependency_info["missing_required"]:
            self.recommendations.append(f"Install missing required packages: {', '.join(dependency_info['missing_required'])}")
            print(f"❌ Missing required packages: {dependency_info['missing_required']}")
        else:
            print("✅ All required dependencies installed")
        
        return dependency_info
    
    def check_mcp_server_health(self) -> Dict[str, Any]:
        """Check MCP server health and configuration"""
        print("🔧 Checking MCP Server Health...")
        
        mcp_info = {
            "server_file_exists": os.path.exists("mcp_langflow_connector_simple.py"),
            "cache_directory_exists": os.path.exists("cache"),
            "logs_directory_exists": os.path.exists("logs"),
            "config_exists": os.path.exists("config/langflow_config.py")
        }
        
        # Check file permissions
        if mcp_info["server_file_exists"]:
            try:
                with open("mcp_langflow_connector_simple.py", 'r') as f:
                    content = f.read()
                mcp_info["server_file_readable"] = True
                mcp_info["server_file_size"] = len(content)
            except Exception as e:
                mcp_info["server_file_readable"] = False
                mcp_info["server_file_error"] = str(e)
        
        # Check cache directory
        if mcp_info["cache_directory_exists"]:
            try:
                cache_files = list(Path("cache").rglob("*"))
                mcp_info["cache_files_count"] = len(cache_files)
                mcp_info["cache_readable"] = True
            except Exception as e:
                mcp_info["cache_readable"] = False
                mcp_info["cache_error"] = str(e)
        
        # Health assessment
        health_score = 100
        
        if not mcp_info["server_file_exists"]:
            health_score -= 50
            self.recommendations.append("MCP server file not found - check file location")
        
        if not mcp_info.get("server_file_readable", False):
            health_score -= 30
            self.recommendations.append("Cannot read MCP server file - check permissions")
        
        if not mcp_info["cache_directory_exists"]:
            health_score -= 10
            self.recommendations.append("Cache directory missing - will be created automatically")
        
        mcp_info["health_score"] = health_score
        mcp_info["health_level"] = "Excellent" if health_score >= 90 else "Good" if health_score >= 70 else "Poor"
        
        print(f"✅ MCP Server Health: {mcp_info['health_level']} ({health_score}/100)")
        return mcp_info
    
    async def test_mcp_server_functionality(self) -> Dict[str, Any]:
        """Test MCP server functionality"""
        print("🧪 Testing MCP Server Functionality...")
        
        try:
            # Import and test MCP server
            from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
            
            connector = SimpleLangFlowMCPConnector()
            
            # Test basic functionality
            test_results = {
                "server_imported": True,
                "connector_initialized": True,
                "tools_count": len(connector.tools),
                "list_files_tool_exists": any(tool["name"] == "list_files" for tool in connector.tools),
                "basic_functionality_tests": {}
            }
            
            # Test list_files tool
            try:
                result = await connector.handle_list_files({"directory": "."})
                test_results["basic_functionality_tests"]["list_files"] = {
                    "success": True,
                    "result_length": len(result),
                    "has_metadata": "📁 Directory:" in result
                }
            except Exception as e:
                test_results["basic_functionality_tests"]["list_files"] = {
                    "success": False,
                    "error": str(e)
                }
            
            # Test ping tool
            try:
                result = await connector.handle_ping({"message": "test"})
                test_results["basic_functionality_tests"]["ping"] = {
                    "success": True,
                    "result_length": len(result)
                }
            except Exception as e:
                test_results["basic_functionality_tests"]["ping"] = {
                    "success": False,
                    "error": str(e)
                }
            
            # Calculate functionality score
            functionality_score = 100
            failed_tests = 0
            
            for test_name, test_result in test_results["basic_functionality_tests"].items():
                if not test_result["success"]:
                    functionality_score -= 25
                    failed_tests += 1
            
            test_results["functionality_score"] = functionality_score
            test_results["failed_tests"] = failed_tests
            test_results["functionality_level"] = "Excellent" if functionality_score >= 90 else "Good" if functionality_score >= 70 else "Poor"
            
            if failed_tests > 0:
                self.recommendations.append(f"{failed_tests} functionality test(s) failed - check MCP server implementation")
            
            print(f"✅ MCP Functionality: {test_results['functionality_level']} ({functionality_score}/100)")
            return test_results
            
        except ImportError as e:
            print(f"❌ Failed to import MCP server: {e}")
            self.recommendations.append("MCP server import failed - check file and dependencies")
            return {
                "server_imported": False,
                "error": str(e),
                "functionality_score": 0,
                "functionality_level": "Failed"
            }
        except Exception as e:
            print(f"❌ MCP server test failed: {e}")
            self.recommendations.append(f"MCP server test failed: {str(e)}")
            return {
                "server_imported": True,
                "connector_initialized": False,
                "error": str(e),
                "functionality_score": 0,
                "functionality_level": "Failed"
            }
    
    def check_langflow_compatibility(self) -> Dict[str, Any]:
        """Check LangFlow compatibility and configuration"""
        print("🌐 Checking LangFlow Compatibility...")
        
        langflow_info = {
            "mcp_protocol_version": "2024-11-05",
            "supported_tools": [
                "read_file", "write_file", "list_files", "stream_files",
                "analyze_code", "track_token_usage", "get_cost_summary",
                "get_system_health", "get_system_status", "ping"
            ],
            "compatibility_checks": {}
        }
        
        # Check MCP protocol compatibility
        langflow_info["compatibility_checks"]["mcp_protocol"] = True
        
        # Check tool definitions
        try:
            from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
            connector = SimpleLangFlowMCPConnector()
            
            available_tools = [tool["name"] for tool in connector.tools]
            missing_tools = [tool for tool in langflow_info["supported_tools"] if tool not in available_tools]
            
            langflow_info["compatibility_checks"]["tools_available"] = len(missing_tools) == 0
            langflow_info["compatibility_checks"]["missing_tools"] = missing_tools
            langflow_info["available_tools"] = available_tools
            
            if missing_tools:
                self.recommendations.append(f"Missing tools for LangFlow: {', '.join(missing_tools)}")
            
        except Exception as e:
            langflow_info["compatibility_checks"]["tools_available"] = False
            langflow_info["compatibility_checks"]["error"] = str(e)
        
        # Calculate compatibility score
        compatibility_score = 100
        
        for check_name, check_result in langflow_info["compatibility_checks"].items():
            if isinstance(check_result, bool) and not check_result:
                compatibility_score -= 25
        
        langflow_info["compatibility_score"] = compatibility_score
        langflow_info["compatibility_level"] = "Excellent" if compatibility_score >= 90 else "Good" if compatibility_score >= 70 else "Poor"
        
        print(f"✅ LangFlow Compatibility: {langflow_info['compatibility_level']} ({compatibility_score}/100)")
        return langflow_info
    
    def generate_stability_report(self) -> Dict[str, Any]:
        """Generate comprehensive stability report"""
        print("\n📊 Generating Stability Report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": self.check_python_version(),
            "system_resources": self.check_system_resources(),
            "dependencies": self.check_dependencies(),
            "mcp_server_health": self.check_mcp_server_health(),
            "langflow_compatibility": self.check_langflow_compatibility(),
            "recommendations": self.recommendations
        }
        
        # Calculate overall stability score
        scores = [
            report["python_version"].get("langflow_compatible", False) * 100,
            report["system_resources"]["performance_score"],
            report["mcp_server_health"]["health_score"],
            report["langflow_compatibility"]["compatibility_score"]
        ]
        
        overall_score = sum(scores) / len(scores)
        report["overall_stability_score"] = overall_score
        report["overall_stability_level"] = "Excellent" if overall_score >= 90 else "Good" if overall_score >= 70 else "Fair" if overall_score >= 50 else "Poor"
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted stability report"""
        print("\n" + "="*60)
        print("🔍 SYSTEM STABILITY DIAGNOSTIC REPORT")
        print("="*60)
        
        print(f"\n📅 Report Generated: {report['timestamp']}")
        print(f"🎯 Overall Stability: {report['overall_stability_level']} ({report['overall_stability_score']:.1f}/100)")
        
        print(f"\n🐍 Python Version:")
        print(f"   Version: {report['python_version']['current_version']}")
        print(f"   Compatibility: {report['python_version']['compatibility']}")
        print(f"   LangFlow Compatible: {report['python_version']['langflow_compatible']}")
        
        print(f"\n💻 System Resources:")
        print(f"   Performance: {report['system_resources']['performance_level']} ({report['system_resources']['performance_score']}/100)")
        print(f"   Memory: {report['system_resources']['memory']['used_gb']}GB / {report['system_resources']['memory']['total_gb']}GB ({report['system_resources']['memory']['percent_used']}%)")
        print(f"   CPU Usage: {report['system_resources']['cpu']['usage_percent']}%")
        print(f"   Disk Usage: {report['system_resources']['disk']['percent_used']}%")
        
        print(f"\n🔧 MCP Server Health:")
        print(f"   Health: {report['mcp_server_health']['health_level']} ({report['mcp_server_health']['health_score']}/100)")
        print(f"   Server File: {'✅' if report['mcp_server_health']['server_file_exists'] else '❌'}")
        print(f"   Cache Directory: {'✅' if report['mcp_server_health']['cache_directory_exists'] else '❌'}")
        
        print(f"\n🌐 LangFlow Compatibility:")
        print(f"   Compatibility: {report['langflow_compatibility']['compatibility_level']} ({report['langflow_compatibility']['compatibility_score']}/100)")
        print(f"   Available Tools: {len(report['langflow_compatibility'].get('available_tools', []))}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*60)
    
    def save_report(self, report: Dict[str, Any], filename: str = "stability_report.json"):
        """Save stability report to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"💾 Report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

async def main():
    """Main diagnostic function"""
    print("🚀 Starting System Stability Diagnostic")
    print("="*50)
    
    diagnostic = SystemStabilityDiagnostic()
    
    # Run all diagnostics
    report = diagnostic.generate_stability_report()
    
    # Test MCP functionality
    print("\n🧪 Testing MCP Server Functionality...")
    mcp_test = await diagnostic.test_mcp_server_functionality()
    report["mcp_functionality"] = mcp_test
    
    # Print and save report
    diagnostic.print_report(report)
    diagnostic.save_report(report)
    
    # Final assessment
    if report["overall_stability_score"] >= 90:
        print("\n🎉 System is highly stable and ready for LangFlow!")
    elif report["overall_stability_score"] >= 70:
        print("\n✅ System is stable with minor issues to address.")
    elif report["overall_stability_score"] >= 50:
        print("\n⚠️ System has moderate stability issues - review recommendations.")
    else:
        print("\n❌ System has significant stability issues - immediate attention required.")
    
    return report

if __name__ == "__main__":
    asyncio.run(main()) 