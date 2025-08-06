#!/usr/bin/env python3
"""
MCP Protocol Compliance Testing Module

This module implements comprehensive MCP protocol compliance testing
for the MCP server. Part of Task 2.1.2 in the Inspector Task List.

Features:
- MCP protocol compliance testing
- Tool registration format validation
- Tool execution protocol testing
- Protocol extension testing
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

# Import configuration manager and JSON-RPC tester
from inspector_config_manager import InspectorConfigManager
from test_json_rpc_compliance import ComplianceStatus, ComplianceTestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MCPComplianceReport:
    """MCP protocol compliance test report"""
    test_suite: str = "MCP Protocol Compliance"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    warning_tests: int = 0
    error_tests: int = 0
    compliance_score: float = 0.0
    test_results: List[ComplianceTestResult] = None
    summary: str = ""
    recommendations: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
        if self.recommendations is None:
            self.recommendations = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def add_result(self, result: ComplianceTestResult) -> None:
        """Add a test result to the report"""
        self.test_results.append(result)
        self.total_tests += 1
        
        if result.status == ComplianceStatus.PASS:
            self.passed_tests += 1
        elif result.status == ComplianceStatus.FAIL:
            self.failed_tests += 1
        elif result.status == ComplianceStatus.WARNING:
            self.warning_tests += 1
        elif result.status == ComplianceStatus.ERROR:
            self.error_tests += 1
        
        # Calculate compliance score
        if self.total_tests > 0:
            self.compliance_score = (self.passed_tests / self.total_tests) * 100

class MCPProtocolComplianceTester:
    """
    MCP Protocol Compliance Tester
    
    Tests MCP server compliance with MCP protocol standards.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.mcp_server_process: Optional[subprocess.Popen] = None
        self.test_timeout: int = 30
        
    async def initialize(self) -> None:
        """Initialize the compliance tester"""
        try:
            logger.info("Initializing MCP Protocol Compliance Tester...")
            
            # Get settings from config manager
            settings = await self.config_manager.get_current_settings()
            self.test_timeout = settings.test_timeout_seconds
            
            logger.info("MCP Protocol Compliance Tester initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Protocol Compliance Tester: {e}")
            raise
    
    async def start_mcp_server(self) -> bool:
        """Start the MCP server for testing"""
        try:
            logger.info("MCP server testing mode - using Inspector CLI directly")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize testing mode: {e}")
            return False
    
    async def stop_mcp_server(self) -> None:
        """Stop the MCP server"""
        logger.info("MCP server testing mode cleanup completed")
    
    async def send_mcp_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], float]:
        """Send an MCP request to the server"""
        try:
            # Use Inspector CLI to send request
            inspector_command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", "mcp_langflow_connector_simple.py",
                "--cli",
                "--method", method
            ]
            
            if params:
                inspector_command.extend(["--params", json.dumps(params)])
            
            start_time = time.time()
            
            result = subprocess.run(
                inspector_command,
                capture_output=True,
                text=True,
                timeout=self.test_timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Parse response
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout.strip())
                    return response, execution_time
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "raw_output": result.stdout}, execution_time
            else:
                return {"error": result.stderr, "returncode": result.returncode}, execution_time
                
        except subprocess.TimeoutExpired:
            return {"error": "Request timeout"}, 0.0
        except Exception as e:
            return {"error": str(e)}, 0.0
    
    async def test_tool_registration_format(self) -> ComplianceTestResult:
        """Test tool registration format compliance"""
        test_name = "Tool Registration Format"
        test_description = "Validate tool registration follows MCP protocol format"
        
        try:
            # Get tools list
            response, execution_time = await self.send_mcp_request("tools/list")
            
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Failed to get tools list: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            if "result" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response missing 'result' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            tools = response["result"]
            
            if not isinstance(tools, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tools result is not a dictionary",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate tool format
            for tool_name, tool_info in tools.items():
                if not isinstance(tool_info, dict):
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.FAIL,
                        details=f"Tool '{tool_name}' info is not a dictionary",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
                
                # Check for required tool fields
                required_fields = ["description"]
                for field in required_fields:
                    if field not in tool_info:
                        return ComplianceTestResult(
                            test_name=test_name,
                            test_description=test_description,
                            status=ComplianceStatus.FAIL,
                            details=f"Tool '{tool_name}' missing required field: {field}",
                            response_data=response,
                            execution_time_ms=execution_time
                        )
                
                # Check inputSchema if present
                if "inputSchema" in tool_info:
                    input_schema = tool_info["inputSchema"]
                    if not isinstance(input_schema, dict):
                        return ComplianceTestResult(
                            test_name=test_name,
                            test_description=test_description,
                            status=ComplianceStatus.FAIL,
                            details=f"Tool '{tool_name}' inputSchema is not a dictionary",
                            response_data=response,
                            execution_time_ms=execution_time
                        )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"Tool registration format validated for {len(tools)} tools",
                response_data=response,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def test_tool_execution_protocol(self) -> ComplianceTestResult:
        """Test tool execution protocol compliance"""
        test_name = "Tool Execution Protocol"
        test_description = "Validate tool execution follows MCP protocol"
        
        try:
            # Test with a simple tool (ping)
            response, execution_time = await self.send_mcp_request("tools/call", {
                "name": "ping"
            })
            
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Tool execution failed: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            if "result" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tool execution response missing 'result' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            result = response["result"]
            
            # Validate result format
            if not isinstance(result, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tool execution result is not a dictionary",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for content field in result
            if "content" not in result:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tool execution result missing 'content' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details="Tool execution protocol validated successfully",
                response_data=response,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def test_protocol_extensions(self) -> ComplianceTestResult:
        """Test MCP protocol extensions"""
        test_name = "Protocol Extensions"
        test_description = "Validate MCP protocol extension support"
        
        try:
            # Test server info method (extension)
            response, execution_time = await self.send_mcp_request("server/info")
            
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details=f"Server info method not supported: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            if "result" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="Server info response missing 'result' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            result = response["result"]
            
            # Validate server info format
            if not isinstance(result, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="Server info result is not a dictionary",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for common server info fields
            expected_fields = ["name", "version"]
            found_fields = [field for field in expected_fields if field in result]
            
            if not found_fields:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="Server info missing expected fields",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"Protocol extensions validated with fields: {found_fields}",
                response_data=response,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def test_method_availability(self) -> ComplianceTestResult:
        """Test required MCP methods availability"""
        test_name = "Method Availability"
        test_description = "Validate required MCP methods are available"
        
        try:
            # Test required MCP methods
            required_methods = ["tools/list", "tools/call"]
            available_methods = []
            failed_methods = []
            
            for method in required_methods:
                response, execution_time = await self.send_mcp_request(method)
                
                if "error" in response:
                    failed_methods.append(f"{method}: {response['error']}")
                else:
                    available_methods.append(method)
            
            if failed_methods:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Failed methods: {', '.join(failed_methods)}",
                    execution_time_ms=execution_time
                )
            
            if len(available_methods) < len(required_methods):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details=f"Only {len(available_methods)}/{len(required_methods)} required methods available",
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"All required methods available: {', '.join(available_methods)}",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def test_error_handling_protocol(self) -> ComplianceTestResult:
        """Test MCP protocol error handling"""
        test_name = "Error Handling Protocol"
        test_description = "Validate MCP protocol error handling"
        
        try:
            # Test with invalid tool name
            response, execution_time = await self.send_mcp_request("tools/call", {
                "name": "invalid_tool_name"
            })
            
            if "error" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="No error response for invalid tool (may be expected behavior)",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            error = response["error"]
            
            # Validate error structure
            if not isinstance(error, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Error response is not a dictionary",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for required error fields
            if "code" not in error:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Error response missing 'code' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            if "message" not in error:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Error response missing 'message' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details="Error handling protocol validated successfully",
                response_data=response,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def test_content_format_compliance(self) -> ComplianceTestResult:
        """Test content format compliance"""
        test_name = "Content Format Compliance"
        test_description = "Validate content format follows MCP protocol"
        
        try:
            # Test with a tool that returns content
            response, execution_time = await self.send_mcp_request("tools/call", {
                "name": "ping"
            })
            
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Tool execution failed: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            if "result" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response missing 'result' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            result = response["result"]
            
            if "content" not in result:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Result missing 'content' field",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            content = result["content"]
            
            # Validate content format
            if not isinstance(content, list):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Content is not a list",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check content items
            for i, item in enumerate(content):
                if not isinstance(item, dict):
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.FAIL,
                        details=f"Content item {i} is not a dictionary",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
                
                # Check for required content fields
                if "type" not in item:
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.FAIL,
                        details=f"Content item {i} missing 'type' field",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"Content format validated for {len(content)} items",
                response_data=response,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def run_compliance_tests(self) -> MCPComplianceReport:
        """Run all MCP protocol compliance tests"""
        report = MCPComplianceReport()
        
        try:
            logger.info("Starting MCP protocol compliance tests...")
            
            # Start MCP server
            if not await self.start_mcp_server():
                report.summary = "Failed to start MCP server for testing"
                return report
            
            # Run all compliance tests
            test_methods = [
                self.test_tool_registration_format,
                self.test_tool_execution_protocol,
                self.test_protocol_extensions,
                self.test_method_availability,
                self.test_error_handling_protocol,
                self.test_content_format_compliance
            ]
            
            for test_method in test_methods:
                try:
                    result = await test_method()
                    report.add_result(result)
                    logger.info(f"Test '{result.test_name}': {result.status.value}")
                except Exception as e:
                    error_result = ComplianceTestResult(
                        test_name=test_method.__name__,
                        test_description="Test execution failed",
                        status=ComplianceStatus.ERROR,
                        details=f"Test execution error: {str(e)}",
                        error_message=str(e)
                    )
                    report.add_result(error_result)
            
            # Generate summary and recommendations
            report.summary = self._generate_summary(report)
            report.recommendations = self._generate_recommendations(report)
            
            logger.info(f"MCP protocol compliance tests completed. Score: {report.compliance_score:.1f}%")
            
        except Exception as e:
            logger.error(f"Error running compliance tests: {e}")
            report.summary = f"Test execution failed: {str(e)}"
        
        finally:
            # Stop MCP server
            await self.stop_mcp_server()
        
        return report
    
    def _generate_summary(self, report: MCPComplianceReport) -> str:
        """Generate test summary"""
        if report.total_tests == 0:
            return "No tests were executed"
        
        summary = f"MCP Protocol Compliance Test Results:\n"
        summary += f"- Total Tests: {report.total_tests}\n"
        summary += f"- Passed: {report.passed_tests}\n"
        summary += f"- Failed: {report.failed_tests}\n"
        summary += f"- Warnings: {report.warning_tests}\n"
        summary += f"- Errors: {report.error_tests}\n"
        summary += f"- Compliance Score: {report.compliance_score:.1f}%\n"
        
        if report.compliance_score >= 95:
            summary += "\n✅ Excellent compliance with MCP protocol specification"
        elif report.compliance_score >= 80:
            summary += "\n⚠️ Good compliance with minor issues to address"
        elif report.compliance_score >= 60:
            summary += "\n⚠️ Moderate compliance with significant issues"
        else:
            summary += "\n❌ Poor compliance - major issues need to be addressed"
        
        return summary
    
    def _generate_recommendations(self, report: MCPComplianceReport) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failed tests
        failed_tests = [r for r in report.test_results if r.status == ComplianceStatus.FAIL]
        for test in failed_tests:
            recommendations.append(f"Fix {test.test_name}: {test.details}")
        
        # Analyze warning tests
        warning_tests = [r for r in report.test_results if r.status == ComplianceStatus.WARNING]
        for test in warning_tests:
            recommendations.append(f"Review {test.test_name}: {test.details}")
        
        # General recommendations
        if report.compliance_score < 95:
            recommendations.append("Review MCP protocol specification compliance")
        
        if not recommendations:
            recommendations.append("All tests passed - maintain current implementation")
        
        return recommendations
    
    async def save_report(self, report: MCPComplianceReport, filename: Optional[str] = None) -> bool:
        """Save compliance report to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reports/inspector/mcp_protocol_compliance_{timestamp}.json"
            
            # Ensure reports directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert report to dictionary
            report_dict = asdict(report)
            
            # Convert datetime objects to ISO format
            report_dict['timestamp'] = report_dict['timestamp'].isoformat()
            for result in report_dict['test_results']:
                result['timestamp'] = result['timestamp'].isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2)
            
            logger.info(f"Compliance report saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save compliance report: {e}")
            return False

# Example usage and testing
async def main():
    """Example usage of MCP Protocol Compliance Tester"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize compliance tester
        tester = MCPProtocolComplianceTester(config_manager)
        await tester.initialize()
        
        # Run compliance tests
        report = await tester.run_compliance_tests()
        
        # Print results
        print("\n" + "="*60)
        print("MCP PROTOCOL COMPLIANCE TEST RESULTS")
        print("="*60)
        print(report.summary)
        
        if report.recommendations:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"{i}. {rec}")
        
        # Save report
        await tester.save_report(report)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 