#!/usr/bin/env python3
"""
Tool Error Handling Testing Module

This module implements comprehensive tool error handling testing for the MCP server.
It validates how tools handle various error conditions, edge cases, invalid inputs,
and unexpected scenarios to ensure robust error handling.

Part of Task 2.3: Tool Execution Testing
"""

import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum

# Import Inspector CLI utilities
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandlingStatus(Enum):
    """Error handling status enumeration"""
    PROPER_ERROR = "proper_error"
    UNEXPECTED_SUCCESS = "unexpected_success"
    CRASH = "crash"
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"


@dataclass
class ErrorHandlingTestResult:
    """Result of a tool error handling test"""
    tool_name: str
    test_case: str
    error_handling_status: ErrorHandlingStatus
    expected_error: str
    actual_response: str
    test_duration_ms: float
    error_properly_handled: bool
    error_message: Optional[str] = None
    test_arguments: Optional[Dict] = None
    response_data: Optional[Dict] = None


@dataclass
class ToolErrorHandlingTestSuite:
    """Complete test suite for tool error handling"""
    total_test_cases: int
    proper_error_handling: int
    unexpected_success: int
    crashes: int
    timeouts: int
    invalid_responses: int
    average_test_duration_ms: float
    max_test_duration_ms: float
    min_test_duration_ms: float
    test_results: List[ErrorHandlingTestResult]
    test_timestamp: datetime
    test_duration_seconds: float
    error_handling_success_rate: float


class ToolErrorHandlingTester:
    """Comprehensive tool error handling testing system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool error handling tester
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ErrorHandlingTestResult] = []
        self.start_time: Optional[datetime] = None
        
        # Define comprehensive error handling test cases for each tool
        self.error_handling_test_cases = {
            # File Operations Error Tests
            "read_file": [
                {
                    "test_case": "read_nonexistent_file",
                    "arguments": {"file_path": "nonexistent_file_12345.txt"},
                    "expected_error": "File not found or access denied",
                    "should_fail": True
                },
                {
                    "test_case": "read_file_empty_path",
                    "arguments": {"file_path": ""},
                    "expected_error": "Invalid file path",
                    "should_fail": True
                },
                {
                    "test_case": "read_file_invalid_path",
                    "arguments": {"file_path": "/invalid/path/with/special/chars/\\*?<>|"},
                    "expected_error": "Invalid file path",
                    "should_fail": True
                }
            ],
            "write_file": [
                {
                    "test_case": "write_file_empty_content",
                    "arguments": {"file_path": "test_empty.txt", "content": ""},
                    "expected_error": "Empty content",
                    "should_fail": False  # Should succeed but warn
                },
                {
                    "test_case": "write_file_invalid_path",
                    "arguments": {"file_path": "/invalid/path/test.txt", "content": "test"},
                    "expected_error": "Invalid file path",
                    "should_fail": True
                },
                {
                    "test_case": "write_file_missing_content",
                    "arguments": {"file_path": "test_missing.txt"},
                    "expected_error": "Missing required parameter",
                    "should_fail": True
                }
            ],
            "list_files": [
                {
                    "test_case": "list_nonexistent_directory",
                    "arguments": {"directory": "/nonexistent/directory/12345"},
                    "expected_error": "Directory not found",
                    "should_fail": True
                },
                {
                    "test_case": "list_files_invalid_batch_size",
                    "arguments": {"directory": ".", "batch_size": -1},
                    "expected_error": "Invalid batch size",
                    "should_fail": True
                },
                {
                    "test_case": "list_files_invalid_max_depth",
                    "arguments": {"directory": ".", "max_depth": 10},
                    "expected_error": "Invalid max depth",
                    "should_fail": True
                }
            ],
            "list_files_table": [
                {
                    "test_case": "table_invalid_offset",
                    "arguments": {"directory": ".", "offset": "invalid_offset", "batch_size": 5},
                    "expected_error": "Invalid offset parameter",
                    "should_fail": True
                },
                {
                    "test_case": "table_missing_offset",
                    "arguments": {"directory": ".", "batch_size": 5},
                    "expected_error": "Missing required parameter",
                    "should_fail": True
                }
            ],
            
            # System Operations Error Tests
            "ping": [
                {
                    "test_case": "ping_with_invalid_args",
                    "arguments": {"invalid_param": "test"},
                    "expected_error": "Unexpected parameter",
                    "should_fail": False  # Should ignore extra params
                }
            ],
            "get_system_health": [
                {
                    "test_case": "health_with_invalid_args",
                    "arguments": {"invalid_param": "test"},
                    "expected_error": "Unexpected parameter",
                    "should_fail": False  # Should ignore extra params
                }
            ],
            
            # Analysis Operations Error Tests
            "analyze_code": [
                {
                    "test_case": "analyze_nonexistent_file",
                    "arguments": {"file_path": "nonexistent_file.py"},
                    "expected_error": "File not found",
                    "should_fail": True
                },
                {
                    "test_case": "analyze_missing_file_path",
                    "arguments": {},
                    "expected_error": "Missing required parameter",
                    "should_fail": True
                }
            ],
            "track_token_usage": [
                {
                    "test_case": "track_negative_tokens",
                    "arguments": {"operation": "test", "model": "gpt-3.5-turbo", "input_tokens": -10, "output_tokens": -5},
                    "expected_error": "Invalid token count",
                    "should_fail": True
                },
                {
                    "test_case": "track_missing_required_params",
                    "arguments": {"operation": "test"},
                    "expected_error": "Missing required parameters",
                    "should_fail": True
                }
            ],
            
            # Vector/LLM Operations Error Tests
            "store_embedding": [
                {
                    "test_case": "store_empty_content",
                    "arguments": {"name": "test", "content": ""},
                    "expected_error": "Empty content",
                    "should_fail": True
                },
                {
                    "test_case": "store_missing_name",
                    "arguments": {"content": "test content"},
                    "expected_error": "Missing required parameter",
                    "should_fail": True
                }
            ],
            "similarity_search": [
                {
                    "test_case": "search_empty_query",
                    "arguments": {"query": "", "limit": 3},
                    "expected_error": "Empty query",
                    "should_fail": True
                },
                {
                    "test_case": "search_invalid_limit",
                    "arguments": {"query": "test", "limit": 0},
                    "expected_error": "Invalid limit",
                    "should_fail": True
                }
            ],
            "process_text_with_llm": [
                {
                    "test_case": "process_empty_text",
                    "arguments": {"text": "", "task": "summarize"},
                    "expected_error": "Empty text",
                    "should_fail": True
                },
                {
                    "test_case": "process_invalid_task",
                    "arguments": {"text": "test text", "task": "invalid_task_type"},
                    "expected_error": "Invalid task type",
                    "should_fail": True
                }
            ],
            
            # Data Processing Operations Error Tests
            "dataframe_operations": [
                {
                    "test_case": "dataframe_invalid_operation",
                    "arguments": {"operation": "invalid_op", "data": "col1,col2\n1,2"},
                    "expected_error": "Invalid operation",
                    "should_fail": True
                },
                {
                    "test_case": "dataframe_empty_data",
                    "arguments": {"operation": "head", "data": ""},
                    "expected_error": "Empty data",
                    "should_fail": True
                }
            ],
            "split_text": [
                {
                    "test_case": "split_empty_text",
                    "arguments": {"text": "", "method": "sentences"},
                    "expected_error": "Empty text",
                    "should_fail": True
                },
                {
                    "test_case": "split_invalid_method",
                    "arguments": {"text": "test text", "method": "invalid_method"},
                    "expected_error": "Invalid split method",
                    "should_fail": True
                }
            ],
            "structured_output": [
                {
                    "test_case": "structured_empty_text",
                    "arguments": {"text": "", "schema": {"name": "string"}},
                    "expected_error": "Empty text",
                    "should_fail": True
                },
                {
                    "test_case": "structured_invalid_schema",
                    "arguments": {"text": "test", "schema": "invalid_schema"},
                    "expected_error": "Invalid schema",
                    "should_fail": True
                }
            ],
            "type_convert": [
                {
                    "test_case": "convert_invalid_type",
                    "arguments": {"data": '{"name": "test"}', "target_type": "invalid_type"},
                    "expected_error": "Invalid target type",
                    "should_fail": True
                },
                {
                    "test_case": "convert_invalid_data",
                    "arguments": {"data": "invalid json data", "target_type": "yaml"},
                    "expected_error": "Invalid data format",
                    "should_fail": True
                }
            ]
        }
        
    def test_all_tools_error_handling(self) -> ToolErrorHandlingTestSuite:
        """
        Test error handling of all available tools
        
        Returns:
            ToolErrorHandlingTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool error handling testing")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = inspector_cli.get_tools_list(self.mcp_server_path)
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with error handling testing")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to test for error handling")
        
        # Test each tool's error handling
        for tool_name in tools_list:
            if tool_name in self.error_handling_test_cases:
                test_cases = self.error_handling_test_cases[tool_name]
                for test_case in test_cases:
                    result = self._test_single_error_handling_case(tool_name, test_case)
                    self.test_results.append(result)
                    
                    # Log progress
                    if result.error_handling_status == ErrorHandlingStatus.PROPER_ERROR:
                        logger.info(f"✅ {tool_name} - {test_case['test_case']}: PROPER ERROR HANDLING")
                    elif result.error_handling_status == ErrorHandlingStatus.UNEXPECTED_SUCCESS:
                        logger.warning(f"⚠️ {tool_name} - {test_case['test_case']}: UNEXPECTED SUCCESS")
                    else:
                        logger.error(f"❌ {tool_name} - {test_case['test_case']}: {result.error_handling_status.value} - {result.error_message}")
            else:
                logger.warning(f"⚠️ No error handling test cases defined for tool: {tool_name}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool error handling testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.error_handling_success_rate:.1f}% ({test_suite.proper_error_handling}/{test_suite.total_test_cases})")
        
        return test_suite
    
    def _test_single_error_handling_case(self, tool_name: str, test_case: Dict) -> ErrorHandlingTestResult:
        """
        Test a single error handling case for a tool
        
        Args:
            tool_name: Name of the tool to test
            test_case: Test case definition
            
        Returns:
            ErrorHandlingTestResult with test details
        """
        start_time = time.time()
        
        try:
            # Execute the tool with error-inducing arguments
            success, response, error = inspector_cli.execute_tool(
                mcp_server_path=self.mcp_server_path,
                tool_name=tool_name,
                arguments=test_case["arguments"],
                timeout=30
            )
            
            test_duration = (time.time() - start_time) * 1000
            
            # Analyze the response to determine error handling status
            status, actual_response, error_properly_handled = self._analyze_error_handling_response(
                success, response, error, test_case
            )
            
            return ErrorHandlingTestResult(
                tool_name=tool_name,
                test_case=test_case["test_case"],
                error_handling_status=status,
                expected_error=test_case["expected_error"],
                actual_response=actual_response,
                test_duration_ms=test_duration,
                error_properly_handled=error_properly_handled,
                test_arguments=test_case["arguments"],
                response_data=response
            )
                
        except Exception as e:
            test_duration = (time.time() - start_time) * 1000
            return ErrorHandlingTestResult(
                tool_name=tool_name,
                test_case=test_case["test_case"],
                error_handling_status=ErrorHandlingStatus.CRASH,
                expected_error=test_case["expected_error"],
                actual_response="Tool crashed with exception",
                test_duration_ms=test_duration,
                error_properly_handled=False,
                error_message=str(e),
                test_arguments=test_case["arguments"]
            )
    
    def _analyze_error_handling_response(self, success: bool, response: Dict, error: str, test_case: Dict) -> Tuple[ErrorHandlingStatus, str, bool]:
        """
        Analyze the response to determine error handling quality
        
        Args:
            success: Whether the tool execution was successful
            response: Tool response data
            error: Error message if any
            test_case: Test case definition
            
        Returns:
            Tuple of (status, actual_response, error_properly_handled)
        """
        should_fail = test_case.get("should_fail", True)
        expected_error = test_case["expected_error"].lower()
        
        if success and response:
            # Tool executed successfully
            if should_fail:
                # Expected to fail but succeeded - this might be unexpected success
                response_str = str(response).lower()
                if any(keyword in response_str for keyword in ["error", "failed", "invalid", "missing"]):
                    return ErrorHandlingStatus.PROPER_ERROR, "Tool returned error in success response", True
                else:
                    return ErrorHandlingStatus.UNEXPECTED_SUCCESS, "Tool succeeded when it should have failed", False
            else:
                # Expected to succeed and did succeed
                return ErrorHandlingStatus.PROPER_ERROR, "Tool handled case correctly", True
        else:
            # Tool failed
            if should_fail:
                # Expected to fail and did fail - check if error is proper
                error_str = (error or "").lower()
                response_str = str(response or {}).lower()
                
                # Check if the error message contains expected keywords
                if any(keyword in error_str for keyword in expected_error.split()):
                    return ErrorHandlingStatus.PROPER_ERROR, f"Proper error: {error}", True
                elif any(keyword in response_str for keyword in expected_error.split()):
                    return ErrorHandlingStatus.PROPER_ERROR, f"Proper error in response: {response}", True
                else:
                    return ErrorHandlingStatus.INVALID_RESPONSE, f"Unexpected error: {error}", False
            else:
                # Expected to succeed but failed
                return ErrorHandlingStatus.INVALID_RESPONSE, f"Tool failed when it should have succeeded: {error}", False
    
    def _calculate_test_suite_results(self) -> ToolErrorHandlingTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            ToolErrorHandlingTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        # Count error handling statuses
        proper_errors = len([r for r in self.test_results if r.error_handling_status == ErrorHandlingStatus.PROPER_ERROR])
        unexpected_success = len([r for r in self.test_results if r.error_handling_status == ErrorHandlingStatus.UNEXPECTED_SUCCESS])
        crashes = len([r for r in self.test_results if r.error_handling_status == ErrorHandlingStatus.CRASH])
        timeouts = len([r for r in self.test_results if r.error_handling_status == ErrorHandlingStatus.TIMEOUT])
        invalid_responses = len([r for r in self.test_results if r.error_handling_status == ErrorHandlingStatus.INVALID_RESPONSE])
        
        # Calculate timing metrics
        test_durations = [r.test_duration_ms for r in self.test_results]
        avg_duration = sum(test_durations) / len(test_durations) if test_durations else 0
        max_duration = max(test_durations) if test_durations else 0
        min_duration = min(test_durations) if test_durations else 0
        
        # Calculate success rate (proper error handling as success)
        success_rate = (proper_errors / len(self.test_results)) * 100 if self.test_results else 0
        
        return ToolErrorHandlingTestSuite(
            total_test_cases=len(self.test_results),
            proper_error_handling=proper_errors,
            unexpected_success=unexpected_success,
            crashes=crashes,
            timeouts=timeouts,
            invalid_responses=invalid_responses,
            average_test_duration_ms=avg_duration,
            max_test_duration_ms=max_duration,
            min_test_duration_ms=min_duration,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration,
            error_handling_success_rate=success_rate
        )
    
    def _create_empty_test_suite(self) -> ToolErrorHandlingTestSuite:
        """Create an empty test suite for error cases"""
        return ToolErrorHandlingTestSuite(
            total_test_cases=0,
            proper_error_handling=0,
            unexpected_success=0,
            crashes=0,
            timeouts=0,
            invalid_responses=0,
            average_test_duration_ms=0.0,
            max_test_duration_ms=0.0,
            min_test_duration_ms=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0,
            error_handling_success_rate=0.0
        )
    
    def save_test_results(self, test_suite: ToolErrorHandlingTestSuite, 
                         output_file: str = "tool_error_handling_test_results.json"):
        """
        Save test results to JSON file
        
        Args:
            test_suite: Test suite results to save
            output_file: Output file path
        """
        try:
            # Ensure reports directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            results_dict = asdict(test_suite)
            
            # Convert datetime to string
            results_dict['test_timestamp'] = test_suite.test_timestamp.isoformat()
            
            # Convert enum values to strings
            for result in results_dict['test_results']:
                result['error_handling_status'] = result['error_handling_status'].value
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tool error handling test results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
    
    def generate_test_report(self, test_suite: ToolErrorHandlingTestSuite) -> str:
        """
        Generate a comprehensive test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL ERROR HANDLING TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Test Cases: {test_suite.total_test_cases}")
        report.append(f"Proper Error Handling: {test_suite.proper_error_handling}")
        report.append(f"Unexpected Success: {test_suite.unexpected_success}")
        report.append(f"Crashes: {test_suite.crashes}")
        report.append(f"Timeouts: {test_suite.timeouts}")
        report.append(f"Invalid Responses: {test_suite.invalid_responses}")
        report.append(f"Error Handling Success Rate: {test_suite.error_handling_success_rate:.1f}%")
        report.append("")
        
        # Performance metrics
        report.append("PERFORMANCE METRICS")
        report.append("-" * 40)
        report.append(f"Average Test Duration: {test_suite.average_test_duration_ms:.2f}ms")
        report.append(f"Maximum Test Duration: {test_suite.max_test_duration_ms:.2f}ms")
        report.append(f"Minimum Test Duration: {test_suite.min_test_duration_ms:.2f}ms")
        report.append("")
        
        # Detailed results by tool
        report.append("DETAILED RESULTS BY TOOL")
        report.append("-" * 40)
        
        # Group results by tool
        tool_results = {}
        for result in test_suite.test_results:
            if result.tool_name not in tool_results:
                tool_results[result.tool_name] = []
            tool_results[result.tool_name].append(result)
        
        for tool_name, results in tool_results.items():
            proper_count = len([r for r in results if r.error_handling_status == ErrorHandlingStatus.PROPER_ERROR])
            unexpected_count = len([r for r in results if r.error_handling_status == ErrorHandlingStatus.UNEXPECTED_SUCCESS])
            crash_count = len([r for r in results if r.error_handling_status == ErrorHandlingStatus.CRASH])
            
            report.append(f"🔧 {tool_name}")
            report.append(f"    Test Cases: {len(results)}")
            report.append(f"    Proper Error Handling: {proper_count}")
            report.append(f"    Unexpected Success: {unexpected_count}")
            report.append(f"    Crashes: {crash_count}")
            
            for result in results:
                status_icon = {
                    ErrorHandlingStatus.PROPER_ERROR: "✅",
                    ErrorHandlingStatus.UNEXPECTED_SUCCESS: "⚠️",
                    ErrorHandlingStatus.CRASH: "💥",
                    ErrorHandlingStatus.TIMEOUT: "⏰",
                    ErrorHandlingStatus.INVALID_RESPONSE: "❌"
                }[result.error_handling_status]
                
                report.append(f"    {status_icon} {result.test_case}")
                report.append(f"        Expected Error: {result.expected_error}")
                report.append(f"        Actual Response: {result.actual_response}")
                report.append(f"        Duration: {result.test_duration_ms:.2f}ms")
                report.append(f"        Properly Handled: {'✅' if result.error_properly_handled else '❌'}")
                
                if result.error_message:
                    report.append(f"        Error: {result.error_message}")
                
                report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool error handling tests"""
    try:
        logger.info("Starting Tool Error Handling Testing")
        
        # Initialize tester
        tester = ToolErrorHandlingTester()
        
        # Run comprehensive error handling tests
        test_suite = tester.test_all_tools_error_handling()
        
        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/tool_error_handling_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)
        
        # Final status
        if test_suite.error_handling_success_rate >= 80:
            logger.info("✅ Tool error handling testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Tool error handling testing completed with issues (success rate: {test_suite.error_handling_success_rate:.1f}%)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tool error handling testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 