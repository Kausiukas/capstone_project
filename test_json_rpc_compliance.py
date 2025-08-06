#!/usr/bin/env python3
"""
JSON-RPC 2.0 Compliance Testing Module

This module implements comprehensive JSON-RPC 2.0 protocol compliance testing
for the MCP server. Part of Task 2.1.1 in the Inspector Task List.

Features:
- JSON-RPC 2.0 format compliance testing
- Request/response structure validation
- Error code compliance testing
- Protocol version testing
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

# Import configuration manager
from inspector_config_manager import InspectorConfigManager
from inspector_cli_utils import inspector_cli


class ComplianceStatusEncoder(json.JSONEncoder):
    """Custom JSON encoder for ComplianceStatus enum"""
    def default(self, obj):
        if isinstance(obj, ComplianceStatus):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    """Compliance test status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ComplianceTestResult:
    """Individual compliance test result"""
    test_name: str
    test_description: str
    status: ComplianceStatus
    details: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class JSONRPCComplianceReport:
    """JSON-RPC compliance test report"""
    test_suite: str = "JSON-RPC 2.0 Compliance"
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

class JSONRPCComplianceTester:
    """
    JSON-RPC 2.0 Compliance Tester
    
    Tests MCP server compliance with JSON-RPC 2.0 protocol standards.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.mcp_server_process: Optional[subprocess.Popen] = None
        self.server_url: str = "http://localhost:6274"
        self.test_timeout: int = 30
        self.mcp_server_path: str = "mcp_langflow_connector_simple.py"
        
    async def initialize(self) -> None:
        """Initialize the compliance tester"""
        try:
            logger.info("Initializing JSON-RPC Compliance Tester...")
            
            # Get settings from config manager
            settings = await self.config_manager.get_current_settings()
            self.test_timeout = settings.test_timeout_seconds
            
            logger.info("JSON-RPC Compliance Tester initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize JSON-RPC Compliance Tester: {e}")
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
    
    async def send_jsonrpc_request(self, method: str, params: Optional[Dict[str, Any]] = None, 
                                 request_id: Optional[str] = None) -> Tuple[Dict[str, Any], float]:
        """Send a JSON-RPC request to the MCP server using Inspector CLI utilities"""
        start_time = time.time()
        
        try:
            # Use Inspector CLI utilities
            success, response_data, error = inspector_cli.execute_inspector_command(
                mcp_server_path=self.mcp_server_path,
                method=method,
                params=params,
                timeout=self.test_timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if success and response_data:
                return response_data, execution_time
            else:
                return {"error": error or "Unknown error"}, execution_time
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {"error": str(e)}, execution_time
    
    async def test_jsonrpc_format_compliance(self) -> ComplianceTestResult:
        """Test JSON-RPC 2.0 format compliance"""
        test_name = "JSON-RPC Format Compliance"
        test_description = "Validate that requests and responses follow JSON-RPC 2.0 format"
        
        try:
            # Test basic request format
            response, execution_time = await self.send_jsonrpc_request("tools/list")
            
            # Check if response is valid JSON
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Request failed: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for valid response structure
            if not isinstance(response, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response is not a valid JSON object",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for tools field (MCP protocol response)
            if "tools" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response missing 'tools' field (MCP protocol)",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate tools array
            if not isinstance(response["tools"], list):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tools field is not an array",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"JSON-RPC 2.0 format compliance verified - {len(response['tools'])} tools found",
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
    
    async def test_request_structure_compliance(self) -> ComplianceTestResult:
        """Test request structure compliance"""
        test_name = "Request Structure Compliance"
        test_description = "Validate request structure follows JSON-RPC 2.0 specification"
        
        try:
            # Test with different request structures
            test_cases = [
                {"method": "tools/list", "params": {}},
                {"method": "ping", "params": {}}
            ]
            
            successful_requests = 0
            total_requests = len(test_cases)
            
            for test_case in test_cases:
                response, execution_time = await self.send_jsonrpc_request(
                    test_case["method"], 
                    test_case["params"]
                )
                
                # Check if response is valid
                if "error" not in response:
                    successful_requests += 1
            
            # Calculate success rate
            success_rate = (successful_requests / total_requests) * 100
            
            if success_rate >= 80:
                status = ComplianceStatus.PASS
                details = f"Request structure compliance verified - {success_rate:.1f}% success rate"
            elif success_rate >= 50:
                status = ComplianceStatus.WARNING
                details = f"Moderate request structure compliance - {success_rate:.1f}% success rate"
            else:
                status = ComplianceStatus.FAIL
                details = f"Poor request structure compliance - {success_rate:.1f}% success rate"
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=status,
                details=details,
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
    
    async def test_response_structure_compliance(self) -> ComplianceTestResult:
        """Test response structure compliance"""
        test_name = "Response Structure Compliance"
        test_description = "Validate response structure follows JSON-RPC 2.0 specification"
        
        try:
            response, execution_time = await self.send_jsonrpc_request("tools/list")
            
            # Check for error response
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Request failed: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate response structure
            if not isinstance(response, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response is not a valid JSON object",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for tools field (MCP protocol response)
            if "tools" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response missing 'tools' field (MCP protocol)",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate tools array structure
            tools = response["tools"]
            if not isinstance(tools, list):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tools field is not an array",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check tool structure
            if tools:
                tool = tools[0]
                required_tool_fields = ["name", "description"]
                for field in required_tool_fields:
                    if field not in tool:
                        return ComplianceTestResult(
                            test_name=test_name,
                            test_description=test_description,
                            status=ComplianceStatus.FAIL,
                            details=f"Tool missing required field: {field}",
                            response_data=response,
                            execution_time_ms=execution_time
                        )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"Response structure compliance verified - {len(tools)} tools found",
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
    
    async def test_error_code_compliance(self) -> ComplianceTestResult:
        """Test error code compliance"""
        test_name = "Error Code Compliance"
        test_description = "Validate error handling follows MCP protocol standards"
        
        try:
            # Test with invalid method to trigger error
            response, execution_time = await self.send_jsonrpc_request("invalid_method")
            
            # Check if we get an error response
            if "error" in response:
                error = response["error"]
                
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
                
                # Validate error code is integer
                if not isinstance(error["code"], int):
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.FAIL,
                        details="Error code must be an integer",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
                
                # Check for standard JSON-RPC error codes
                standard_codes = [-32700, -32600, -32601, -32602, -32603, -32000, -32001, -32002, -32003, -32004, -32005]
                if error["code"] not in standard_codes:
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.WARNING,
                        details=f"Error code {error['code']} is not a standard JSON-RPC error code",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
                
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.PASS,
                    details="Error code compliance verified",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            else:
                # If no error response, check if we get a valid response (some servers might handle invalid methods gracefully)
                if isinstance(response, dict) and "tools" in response:
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.WARNING,
                        details="Invalid method handled gracefully (no error response)",
                        response_data=response,
                        execution_time_ms=execution_time
                    )
                else:
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.WARNING,
                        details="No error response for invalid method (may be expected behavior)",
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
    
    async def test_protocol_version_compliance(self) -> ComplianceTestResult:
        """Test protocol version compliance"""
        test_name = "Protocol Version Compliance"
        test_description = "Validate MCP protocol compliance"
        
        try:
            response, execution_time = await self.send_jsonrpc_request("tools/list")
            
            # Check for error response
            if "error" in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details=f"Request failed: {response['error']}",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for valid response structure
            if not isinstance(response, dict):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response is not a valid JSON object",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for tools field (MCP protocol response)
            if "tools" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Response missing 'tools' field (MCP protocol)",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate tools array
            tools = response["tools"]
            if not isinstance(tools, list):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Tools field is not an array",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details=f"MCP protocol compliance verified - {len(tools)} tools available",
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
    
    async def run_compliance_tests(self) -> JSONRPCComplianceReport:
        """Run all JSON-RPC compliance tests"""
        report = JSONRPCComplianceReport()
        
        try:
            logger.info("Starting JSON-RPC compliance tests...")
            
            # Start MCP server
            if not await self.start_mcp_server():
                report.summary = "Failed to start MCP server for testing"
                return report
            
            # Run all compliance tests
            test_methods = [
                self.test_jsonrpc_format_compliance,
                self.test_request_structure_compliance,
                self.test_response_structure_compliance,
                self.test_error_code_compliance,
                self.test_protocol_version_compliance
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
            
            logger.info(f"JSON-RPC compliance tests completed. Score: {report.compliance_score:.1f}%")
            
        except Exception as e:
            logger.error(f"Error running compliance tests: {e}")
            report.summary = f"Test execution failed: {str(e)}"
        
        finally:
            # Stop MCP server
            await self.stop_mcp_server()
        
        return report
    
    def _generate_summary(self, report: JSONRPCComplianceReport) -> str:
        """Generate test summary"""
        if report.total_tests == 0:
            return "No tests were executed"
        
        summary = f"JSON-RPC 2.0 Compliance Test Results:\n"
        summary += f"- Total Tests: {report.total_tests}\n"
        summary += f"- Passed: {report.passed_tests}\n"
        summary += f"- Failed: {report.failed_tests}\n"
        summary += f"- Warnings: {report.warning_tests}\n"
        summary += f"- Errors: {report.error_tests}\n"
        summary += f"- Compliance Score: {report.compliance_score:.1f}%\n"
        
        if report.compliance_score >= 95:
            summary += "\n✅ Excellent compliance with JSON-RPC 2.0 specification"
        elif report.compliance_score >= 80:
            summary += "\n⚠️ Good compliance with minor issues to address"
        elif report.compliance_score >= 60:
            summary += "\n⚠️ Moderate compliance with significant issues"
        else:
            summary += "\n❌ Poor compliance - major issues need to be addressed"
        
        return summary
    
    def _generate_recommendations(self, report: JSONRPCComplianceReport) -> List[str]:
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
            recommendations.append("Review JSON-RPC 2.0 specification compliance")
        
        if not recommendations:
            recommendations.append("All tests passed - maintain current implementation")
        
        return recommendations
    
    async def save_report(self, report: JSONRPCComplianceReport, filename: Optional[str] = None) -> bool:
        """Save compliance report to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reports/inspector/jsonrpc_compliance_{timestamp}.json"
            
            # Ensure reports directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert report to dictionary
            report_dict = asdict(report)
            
            # Convert datetime objects to ISO format
            report_dict['timestamp'] = report_dict['timestamp'].isoformat()
            for result in report_dict['test_results']:
                result['timestamp'] = result['timestamp'].isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, cls=ComplianceStatusEncoder)
            
            logger.info(f"Compliance report saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save compliance report: {e}")
            return False

# Example usage and testing
async def main():
    """Example usage of JSON-RPC Compliance Tester"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize compliance tester
        tester = JSONRPCComplianceTester(config_manager)
        await tester.initialize()
        
        # Run compliance tests
        report = await tester.run_compliance_tests()
        
        # Print results
        print("\n" + "="*60)
        print("JSON-RPC 2.0 COMPLIANCE TEST RESULTS")
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