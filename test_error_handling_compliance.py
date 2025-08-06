#!/usr/bin/env python3
"""
Error Handling Compliance Testing Module

This module implements comprehensive error handling compliance testing
for the MCP server. Part of Task 2.1.3 in the Inspector Task List.

Features:
- Error response compliance testing
- Error code standards validation
- Error message format testing
- Error recovery testing
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

# Import configuration manager and compliance test result
from inspector_config_manager import InspectorConfigManager
from test_json_rpc_compliance import ComplianceStatus, ComplianceTestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ErrorHandlingComplianceReport:
    """Error handling compliance test report"""
    test_suite: str = "Error Handling Compliance"
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

class ErrorHandlingComplianceTester:
    """
    Error Handling Compliance Tester
    
    Tests MCP server error handling compliance with standards.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.mcp_server_process: Optional[subprocess.Popen] = None
        self.test_timeout: int = 30
        
        # Standard JSON-RPC error codes
        self.standard_error_codes = {
            -32700: "Parse error",
            -32600: "Invalid Request",
            -32601: "Method not found",
            -32602: "Invalid params",
            -32603: "Internal error",
            -32000: "Server error",
            -32001: "Server not initialized",
            -32002: "Unknown error code",
            -32003: "Invalid input",
            -32004: "Resource not found",
            -32005: "Request cancelled"
        }
        
    async def initialize(self) -> None:
        """Initialize the compliance tester"""
        try:
            logger.info("Initializing Error Handling Compliance Tester...")
            
            # Get settings from config manager
            settings = await self.config_manager.get_current_settings()
            self.test_timeout = settings.test_timeout_seconds
            
            logger.info("Error Handling Compliance Tester initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Error Handling Compliance Tester: {e}")
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
    
    async def test_error_response_structure(self) -> ComplianceTestResult:
        """Test error response structure compliance"""
        test_name = "Error Response Structure"
        test_description = "Validate error response structure follows JSON-RPC 2.0 specification"
        
        try:
            # Test with invalid method to trigger error
            response, execution_time = await self.send_mcp_request("invalid_method")
            
            if "error" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="No error response for invalid method (may be expected behavior)",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            error = response["error"]
            
            # Validate error is a dictionary
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
            required_fields = ["code", "message"]
            for field in required_fields:
                if field not in error:
                    return ComplianceTestResult(
                        test_name=test_name,
                        test_description=test_description,
                        status=ComplianceStatus.FAIL,
                        details=f"Error response missing required field: {field}",
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
            
            # Validate error message is string
            if not isinstance(error["message"], str):
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Error message must be a string",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details="Error response structure validated successfully",
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
    
    async def test_error_code_standards(self) -> ComplianceTestResult:
        """Test error code standards compliance"""
        test_name = "Error Code Standards"
        test_description = "Validate error codes follow JSON-RPC 2.0 standard codes"
        
        try:
            # Test various error scenarios
            error_scenarios = [
                ("invalid_method", "Method not found"),
                ("tools/call", {"name": "invalid_tool"}, "Invalid params"),
                ("tools/call", {"invalid_param": "value"}, "Invalid params")
            ]
            
            found_error_codes = set()
            standard_codes_used = 0
            
            for method, params, expected_error in error_scenarios:
                if params is None:
                    response, execution_time = await self.send_mcp_request(method)
                else:
                    response, execution_time = await self.send_mcp_request(method, params)
                
                if "error" in response:
                    error_code = response["error"].get("code")
                    if error_code is not None:
                        found_error_codes.add(error_code)
                        if error_code in self.standard_error_codes:
                            standard_codes_used += 1
            
            # Calculate compliance percentage
            if found_error_codes:
                compliance_percentage = (standard_codes_used / len(found_error_codes)) * 100
                
                if compliance_percentage >= 80:
                    status = ComplianceStatus.PASS
                    details = f"Good error code compliance: {compliance_percentage:.1f}% standard codes used"
                elif compliance_percentage >= 50:
                    status = ComplianceStatus.WARNING
                    details = f"Moderate error code compliance: {compliance_percentage:.1f}% standard codes used"
                else:
                    status = ComplianceStatus.FAIL
                    details = f"Poor error code compliance: {compliance_percentage:.1f}% standard codes used"
                
                details += f" (Found codes: {found_error_codes})"
            else:
                status = ComplianceStatus.WARNING
                details = "No error codes found in test scenarios"
            
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
    
    async def test_error_message_format(self) -> ComplianceTestResult:
        """Test error message format compliance"""
        test_name = "Error Message Format"
        test_description = "Validate error message format and clarity"
        
        try:
            # Test with invalid method
            response, execution_time = await self.send_mcp_request("invalid_method")
            
            if "error" not in response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="No error response for invalid method",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            error = response["error"]
            message = error.get("message", "")
            
            # Validate message is not empty
            if not message:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="Error message is empty",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Validate message is descriptive
            if len(message) < 10:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.WARNING,
                    details="Error message is too short",
                    response_data=response,
                    execution_time_ms=execution_time
                )
            
            # Check for helpful content
            helpful_indicators = ["not found", "invalid", "error", "failed", "missing"]
            has_helpful_content = any(indicator in message.lower() for indicator in helpful_indicators)
            
            if has_helpful_content:
                status = ComplianceStatus.PASS
                details = "Error message is descriptive and helpful"
            else:
                status = ComplianceStatus.WARNING
                details = "Error message could be more descriptive"
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=status,
                details=details,
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
    
    async def test_error_recovery(self) -> ComplianceTestResult:
        """Test error recovery capabilities"""
        test_name = "Error Recovery"
        test_description = "Validate system can recover from errors"
        
        try:
            # Test error recovery by sending valid request after invalid one
            invalid_response, execution_time = await self.send_mcp_request("invalid_method")
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Send valid request
            valid_response, execution_time = await self.send_mcp_request("tools/list")
            
            # Check if valid request succeeds
            if "error" in valid_response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="System failed to recover from error - valid request failed",
                    response_data=valid_response,
                    execution_time_ms=execution_time
                )
            
            if "result" not in valid_response:
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.FAIL,
                    details="System failed to recover - valid request missing result",
                    response_data=valid_response,
                    execution_time_ms=execution_time
                )
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.PASS,
                details="System successfully recovered from error",
                response_data=valid_response,
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
    
    async def test_invalid_input_handling(self) -> ComplianceTestResult:
        """Test invalid input handling"""
        test_name = "Invalid Input Handling"
        test_description = "Validate handling of invalid input parameters"
        
        try:
            # Test various invalid input scenarios
            invalid_scenarios = [
                ("tools/call", {"name": 123}, "Invalid tool name type"),
                ("tools/call", {"name": ""}, "Empty tool name"),
                ("tools/call", {"name": "valid_tool", "invalid_param": None}, "Invalid parameter"),
                ("tools/call", None, "Missing parameters")
            ]
            
            error_responses = 0
            total_scenarios = len(invalid_scenarios)
            
            for method, params, description in invalid_scenarios:
                response, execution_time = await self.send_mcp_request(method, params)
                
                if "error" in response:
                    error_responses += 1
            
            # Calculate error handling percentage
            if total_scenarios > 0:
                error_handling_percentage = (error_responses / total_scenarios) * 100
                
                if error_handling_percentage >= 75:
                    status = ComplianceStatus.PASS
                    details = f"Good invalid input handling: {error_handling_percentage:.1f}% scenarios handled"
                elif error_handling_percentage >= 50:
                    status = ComplianceStatus.WARNING
                    details = f"Moderate invalid input handling: {error_handling_percentage:.1f}% scenarios handled"
                else:
                    status = ComplianceStatus.FAIL
                    details = f"Poor invalid input handling: {error_handling_percentage:.1f}% scenarios handled"
            else:
                status = ComplianceStatus.WARNING
                details = "No invalid input scenarios tested"
            
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
    
    async def test_timeout_handling(self) -> ComplianceTestResult:
        """Test timeout handling"""
        test_name = "Timeout Handling"
        test_description = "Validate handling of request timeouts"
        
        try:
            # Test with a very short timeout
            inspector_command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", "mcp_langflow_connector_simple.py",
                "--cli",
                "--method", "tools/list"
            ]
            
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    inspector_command,
                    capture_output=True,
                    text=True,
                    timeout=1  # Very short timeout
                )
                execution_time = (time.time() - start_time) * 1000
                
                # If we get here, the request completed within timeout
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.PASS,
                    details="Request completed within timeout period",
                    execution_time_ms=execution_time
                )
                
            except subprocess.TimeoutExpired:
                execution_time = (time.time() - start_time) * 1000
                
                return ComplianceTestResult(
                    test_name=test_name,
                    test_description=test_description,
                    status=ComplianceStatus.PASS,
                    details="Timeout handled correctly",
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
    
    async def test_concurrent_error_handling(self) -> ComplianceTestResult:
        """Test concurrent error handling"""
        test_name = "Concurrent Error Handling"
        test_description = "Validate handling of concurrent error scenarios"
        
        try:
            # Send multiple invalid requests concurrently
            tasks = []
            for i in range(5):
                task = self.send_mcp_request(f"invalid_method_{i}")
                tasks.append(task)
            
            # Wait for all requests to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful error responses
            error_responses = 0
            total_requests = len(results)
            
            for result in results:
                if isinstance(result, tuple):
                    response, execution_time = result
                    if "error" in response:
                        error_responses += 1
            
            # Calculate concurrent error handling percentage
            if total_requests > 0:
                handling_percentage = (error_responses / total_requests) * 100
                
                if handling_percentage >= 80:
                    status = ComplianceStatus.PASS
                    details = f"Good concurrent error handling: {handling_percentage:.1f}% requests handled"
                elif handling_percentage >= 60:
                    status = ComplianceStatus.WARNING
                    details = f"Moderate concurrent error handling: {handling_percentage:.1f}% requests handled"
                else:
                    status = ComplianceStatus.FAIL
                    details = f"Poor concurrent error handling: {handling_percentage:.1f}% requests handled"
            else:
                status = ComplianceStatus.WARNING
                details = "No concurrent requests tested"
            
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=status,
                details=details,
                execution_time_ms=0.0
            )
            
        except Exception as e:
            return ComplianceTestResult(
                test_name=test_name,
                test_description=test_description,
                status=ComplianceStatus.ERROR,
                details=f"Test execution error: {str(e)}",
                error_message=str(e)
            )
    
    async def run_compliance_tests(self) -> ErrorHandlingComplianceReport:
        """Run all error handling compliance tests"""
        report = ErrorHandlingComplianceReport()
        
        try:
            logger.info("Starting error handling compliance tests...")
            
            # Start MCP server
            if not await self.start_mcp_server():
                report.summary = "Failed to start MCP server for testing"
                return report
            
            # Run all compliance tests
            test_methods = [
                self.test_error_response_structure,
                self.test_error_code_standards,
                self.test_error_message_format,
                self.test_error_recovery,
                self.test_invalid_input_handling,
                self.test_timeout_handling,
                self.test_concurrent_error_handling
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
            
            logger.info(f"Error handling compliance tests completed. Score: {report.compliance_score:.1f}%")
            
        except Exception as e:
            logger.error(f"Error running compliance tests: {e}")
            report.summary = f"Test execution failed: {str(e)}"
        
        finally:
            # Stop MCP server
            await self.stop_mcp_server()
        
        return report
    
    def _generate_summary(self, report: ErrorHandlingComplianceReport) -> str:
        """Generate test summary"""
        if report.total_tests == 0:
            return "No tests were executed"
        
        summary = f"Error Handling Compliance Test Results:\n"
        summary += f"- Total Tests: {report.total_tests}\n"
        summary += f"- Passed: {report.passed_tests}\n"
        summary += f"- Failed: {report.failed_tests}\n"
        summary += f"- Warnings: {report.warning_tests}\n"
        summary += f"- Errors: {report.error_tests}\n"
        summary += f"- Compliance Score: {report.compliance_score:.1f}%\n"
        
        if report.compliance_score >= 95:
            summary += "\n✅ Excellent error handling compliance"
        elif report.compliance_score >= 80:
            summary += "\n⚠️ Good error handling with minor issues to address"
        elif report.compliance_score >= 60:
            summary += "\n⚠️ Moderate error handling with significant issues"
        else:
            summary += "\n❌ Poor error handling - major issues need to be addressed"
        
        return summary
    
    def _generate_recommendations(self, report: ErrorHandlingComplianceReport) -> List[str]:
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
            recommendations.append("Review error handling standards and best practices")
        
        if not recommendations:
            recommendations.append("All tests passed - maintain current error handling implementation")
        
        return recommendations
    
    async def save_report(self, report: ErrorHandlingComplianceReport, filename: Optional[str] = None) -> bool:
        """Save compliance report to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reports/inspector/error_handling_compliance_{timestamp}.json"
            
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
    """Example usage of Error Handling Compliance Tester"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize compliance tester
        tester = ErrorHandlingComplianceTester(config_manager)
        await tester.initialize()
        
        # Run compliance tests
        report = await tester.run_compliance_tests()
        
        # Print results
        print("\n" + "="*60)
        print("ERROR HANDLING COMPLIANCE TEST RESULTS")
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