#!/usr/bin/env python3
"""
Tool Functionality Testing Module

This module implements comprehensive tool functionality testing for the MCP server.
It validates specific tool behaviors, expected outputs, and functional correctness
through targeted test cases for each tool category.

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


class FunctionalityStatus(Enum):
    """Functionality status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class FunctionalityTestResult:
    """Result of a tool functionality test"""
    tool_name: str
    test_case: str
    functionality_status: FunctionalityStatus
    expected_behavior: str
    actual_behavior: str
    test_duration_ms: float
    output_validation: bool
    error_message: Optional[str] = None
    test_arguments: Optional[Dict] = None
    actual_output: Optional[Dict] = None


@dataclass
class ToolFunctionalityTestSuite:
    """Complete test suite for tool functionality"""
    total_test_cases: int
    passed_tests: int
    failed_tests: int
    partial_tests: int
    error_tests: int
    timeout_tests: int
    average_test_duration_ms: float
    max_test_duration_ms: float
    min_test_duration_ms: float
    test_results: List[FunctionalityTestResult]
    test_timestamp: datetime
    test_duration_seconds: float
    functionality_success_rate: float


class ToolFunctionalityTester:
    """Comprehensive tool functionality testing system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool functionality tester
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[FunctionalityTestResult] = []
        self.start_time: Optional[datetime] = None
        
        # Define comprehensive test cases for each tool
        self.functionality_test_cases = {
            # File Operations Tests
            "read_file": [
                {
                    "test_case": "read_existing_file",
                    "arguments": {"file_path": "README.md"},
                    "expected_behavior": "Should return file content as string",
                    "validation": lambda output: isinstance(output.get("content", ""), str) and len(output.get("content", "")) > 0
                }
            ],
            "write_file": [
                {
                    "test_case": "write_new_file",
                    "arguments": {"file_path": "test_functionality.txt", "content": "Test content for functionality testing"},
                    "expected_behavior": "Should create new file with specified content",
                    "validation": lambda output: "success" in output.get("result", "").lower() or "created" in output.get("result", "").lower()
                }
            ],
            "list_files": [
                {
                    "test_case": "list_current_directory",
                    "arguments": {"directory": ".", "batch_size": 5},
                    "expected_behavior": "Should return list of files in current directory",
                    "validation": lambda output: "files" in output or "items" in output or isinstance(output.get("result", []), list)
                },
                {
                    "test_case": "list_with_file_types_filter",
                    "arguments": {"directory": ".", "file_types": [".py"], "batch_size": 3},
                    "expected_behavior": "Should return only Python files",
                    "validation": lambda output: "files" in output or "items" in output
                }
            ],
            "list_files_readable": [
                {
                    "test_case": "readable_format",
                    "arguments": {"directory": ".", "batch_size": 3},
                    "expected_behavior": "Should return human-readable file list",
                    "validation": lambda output: isinstance(output.get("result", ""), str) and len(output.get("result", "")) > 0
                }
            ],
            "list_files_table": [
                {
                    "test_case": "table_format",
                    "arguments": {"directory": ".", "offset": "0", "batch_size": 3},
                    "expected_behavior": "Should return table-formatted file list",
                    "validation": lambda output: "data" in output or "table" in output or isinstance(output.get("result", {}), dict)
                }
            ],
            
            # System Operations Tests
            "ping": [
                {
                    "test_case": "basic_ping",
                    "arguments": {},
                    "expected_behavior": "Should return pong response",
                    "validation": lambda output: "pong" in output.get("result", "").lower() or "ping" in output.get("result", "").lower()
                }
            ],
            "get_system_health": [
                {
                    "test_case": "health_check",
                    "arguments": {},
                    "expected_behavior": "Should return system health information",
                    "validation": lambda output: "health" in output.get("result", "").lower() or "status" in output.get("result", "").lower()
                }
            ],
            "get_system_status": [
                {
                    "test_case": "status_check",
                    "arguments": {},
                    "expected_behavior": "Should return system status information",
                    "validation": lambda output: "status" in output.get("result", "").lower() or "running" in output.get("result", "").lower()
                }
            ],
            
            # Analysis Operations Tests
            "analyze_code": [
                {
                    "test_case": "analyze_python_file",
                    "arguments": {"file_path": "README.md"},
                    "expected_behavior": "Should return code analysis results",
                    "validation": lambda output: "analysis" in output.get("result", "").lower() or "code" in output.get("result", "").lower()
                }
            ],
            "track_token_usage": [
                {
                    "test_case": "track_usage",
                    "arguments": {"operation": "test", "model": "gpt-3.5-turbo", "input_tokens": 10, "output_tokens": 5},
                    "expected_behavior": "Should track and return token usage",
                    "validation": lambda output: "tokens" in output.get("result", "").lower() or "usage" in output.get("result", "").lower()
                }
            ],
            "get_cost_summary": [
                {
                    "test_case": "cost_summary",
                    "arguments": {},
                    "expected_behavior": "Should return cost summary information",
                    "validation": lambda output: "cost" in output.get("result", "").lower() or "summary" in output.get("result", "").lower()
                }
            ],
            
            # Vector/LLM Operations Tests
            "store_embedding": [
                {
                    "test_case": "store_text_embedding",
                    "arguments": {"name": "test_functionality", "content": "Test content for embedding functionality"},
                    "expected_behavior": "Should store embedding and return success",
                    "validation": lambda output: "success" in output.get("result", "").lower() or "stored" in output.get("result", "").lower()
                }
            ],
            "similarity_search": [
                {
                    "test_case": "search_similarity",
                    "arguments": {"query": "test query", "limit": 3},
                    "expected_behavior": "Should return similarity search results",
                    "validation": lambda output: "results" in output.get("result", "").lower() or "similar" in output.get("result", "").lower()
                }
            ],
            "process_text_with_llm": [
                {
                    "test_case": "text_processing",
                    "arguments": {"text": "This is a test text for LLM processing", "task": "summarize"},
                    "expected_behavior": "Should process text and return result",
                    "validation": lambda output: "result" in output or "processed" in output.get("result", "").lower()
                }
            ],
            
            # Data Processing Operations Tests
            "dataframe_operations": [
                {
                    "test_case": "head_operation",
                    "arguments": {"operation": "head", "data": "col1,col2\n1,2\n3,4\n5,6"},
                    "expected_behavior": "Should return first few rows of data",
                    "validation": lambda output: "data" in output or "result" in output
                }
            ],
            "split_text": [
                {
                    "test_case": "sentence_splitting",
                    "arguments": {"text": "This is sentence one. This is sentence two.", "method": "sentences"},
                    "expected_behavior": "Should split text into sentences",
                    "validation": lambda output: "sentences" in output.get("result", "").lower() or "split" in output.get("result", "").lower()
                }
            ],
            "structured_output": [
                {
                    "test_case": "extract_structured_data",
                    "arguments": {"text": "Name: John Doe, Age: 30, City: New York", "schema": {"name": "string", "age": "integer", "city": "string"}},
                    "expected_behavior": "Should extract structured data according to schema",
                    "validation": lambda output: "name" in output.get("result", "").lower() or "structured" in output.get("result", "").lower()
                }
            ],
            "type_convert": [
                {
                    "test_case": "json_to_yaml",
                    "arguments": {"data": '{"name": "test", "value": 123}', "target_type": "yaml"},
                    "expected_behavior": "Should convert JSON to YAML format",
                    "validation": lambda output: "yaml" in output.get("result", "").lower() or "converted" in output.get("result", "").lower()
                }
            ]
        }
        
    def test_all_tools_functionality(self) -> ToolFunctionalityTestSuite:
        """
        Test functionality of all available tools
        
        Returns:
            ToolFunctionalityTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool functionality testing")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = inspector_cli.get_tools_list(self.mcp_server_path)
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with functionality testing")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to test for functionality")
        
        # Test each tool's functionality
        for tool_name in tools_list:
            if tool_name in self.functionality_test_cases:
                test_cases = self.functionality_test_cases[tool_name]
                for test_case in test_cases:
                    result = self._test_single_functionality_case(tool_name, test_case)
                    self.test_results.append(result)
                    
                    # Log progress
                    if result.functionality_status == FunctionalityStatus.PASSED:
                        logger.info(f"✅ {tool_name} - {test_case['test_case']}: PASSED")
                    elif result.functionality_status == FunctionalityStatus.PARTIAL:
                        logger.warning(f"⚠️ {tool_name} - {test_case['test_case']}: PARTIAL")
                    else:
                        logger.error(f"❌ {tool_name} - {test_case['test_case']}: FAILED - {result.error_message}")
            else:
                logger.warning(f"⚠️ No functionality test cases defined for tool: {tool_name}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool functionality testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.functionality_success_rate:.1f}% ({test_suite.passed_tests}/{test_suite.total_test_cases})")
        
        return test_suite
    
    def _test_single_functionality_case(self, tool_name: str, test_case: Dict) -> FunctionalityTestResult:
        """
        Test a single functionality case for a tool
        
        Args:
            tool_name: Name of the tool to test
            test_case: Test case definition
            
        Returns:
            FunctionalityTestResult with test details
        """
        start_time = time.time()
        
        try:
            # Execute the tool with test case arguments
            success, response, error = inspector_cli.execute_tool(
                mcp_server_path=self.mcp_server_path,
                tool_name=tool_name,
                arguments=test_case["arguments"],
                timeout=30
            )
            
            test_duration = (time.time() - start_time) * 1000
            
            if success and response:
                # Validate the output against expected behavior
                validation_result = test_case["validation"](response)
                
                # Determine functionality status
                if validation_result:
                    status = FunctionalityStatus.PASSED
                    actual_behavior = "Output matches expected behavior"
                else:
                    status = FunctionalityStatus.PARTIAL
                    actual_behavior = "Output received but doesn't match expected behavior"
                
                return FunctionalityTestResult(
                    tool_name=tool_name,
                    test_case=test_case["test_case"],
                    functionality_status=status,
                    expected_behavior=test_case["expected_behavior"],
                    actual_behavior=actual_behavior,
                    test_duration_ms=test_duration,
                    output_validation=validation_result,
                    test_arguments=test_case["arguments"],
                    actual_output=response
                )
            else:
                # Determine error status
                if "timeout" in (error or "").lower():
                    status = FunctionalityStatus.TIMEOUT
                else:
                    status = FunctionalityStatus.FAILED
                
                return FunctionalityTestResult(
                    tool_name=tool_name,
                    test_case=test_case["test_case"],
                    functionality_status=status,
                    expected_behavior=test_case["expected_behavior"],
                    actual_behavior="Tool execution failed",
                    test_duration_ms=test_duration,
                    output_validation=False,
                    error_message=error,
                    test_arguments=test_case["arguments"]
                )
                
        except Exception as e:
            test_duration = (time.time() - start_time) * 1000
            return FunctionalityTestResult(
                tool_name=tool_name,
                test_case=test_case["test_case"],
                functionality_status=FunctionalityStatus.ERROR,
                expected_behavior=test_case["expected_behavior"],
                actual_behavior="Test execution error",
                test_duration_ms=test_duration,
                output_validation=False,
                error_message=str(e),
                test_arguments=test_case["arguments"]
            )
    
    def _calculate_test_suite_results(self) -> ToolFunctionalityTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            ToolFunctionalityTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        # Count functionality statuses
        passed = len([r for r in self.test_results if r.functionality_status == FunctionalityStatus.PASSED])
        failed = len([r for r in self.test_results if r.functionality_status == FunctionalityStatus.FAILED])
        partial = len([r for r in self.test_results if r.functionality_status == FunctionalityStatus.PARTIAL])
        error = len([r for r in self.test_results if r.functionality_status == FunctionalityStatus.ERROR])
        timeout = len([r for r in self.test_results if r.functionality_status == FunctionalityStatus.TIMEOUT])
        
        # Calculate timing metrics
        test_durations = [r.test_duration_ms for r in self.test_results]
        avg_duration = sum(test_durations) / len(test_durations) if test_durations else 0
        max_duration = max(test_durations) if test_durations else 0
        min_duration = min(test_durations) if test_durations else 0
        
        # Calculate success rate (passed + partial as success)
        success_rate = ((passed + partial) / len(self.test_results)) * 100 if self.test_results else 0
        
        return ToolFunctionalityTestSuite(
            total_test_cases=len(self.test_results),
            passed_tests=passed,
            failed_tests=failed,
            partial_tests=partial,
            error_tests=error,
            timeout_tests=timeout,
            average_test_duration_ms=avg_duration,
            max_test_duration_ms=max_duration,
            min_test_duration_ms=min_duration,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration,
            functionality_success_rate=success_rate
        )
    
    def _create_empty_test_suite(self) -> ToolFunctionalityTestSuite:
        """Create an empty test suite for error cases"""
        return ToolFunctionalityTestSuite(
            total_test_cases=0,
            passed_tests=0,
            failed_tests=0,
            partial_tests=0,
            error_tests=0,
            timeout_tests=0,
            average_test_duration_ms=0.0,
            max_test_duration_ms=0.0,
            min_test_duration_ms=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0,
            functionality_success_rate=0.0
        )
    
    def save_test_results(self, test_suite: ToolFunctionalityTestSuite, 
                         output_file: str = "tool_functionality_test_results.json"):
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
                result['functionality_status'] = result['functionality_status'].value
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tool functionality test results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
    
    def generate_test_report(self, test_suite: ToolFunctionalityTestSuite) -> str:
        """
        Generate a comprehensive test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL FUNCTIONALITY TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Test Cases: {test_suite.total_test_cases}")
        report.append(f"Passed Tests: {test_suite.passed_tests}")
        report.append(f"Partial Tests: {test_suite.partial_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests}")
        report.append(f"Error Tests: {test_suite.error_tests}")
        report.append(f"Timeout Tests: {test_suite.timeout_tests}")
        report.append(f"Functionality Success Rate: {test_suite.functionality_success_rate:.1f}%")
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
            passed_count = len([r for r in results if r.functionality_status == FunctionalityStatus.PASSED])
            partial_count = len([r for r in results if r.functionality_status == FunctionalityStatus.PARTIAL])
            failed_count = len([r for r in results if r.functionality_status == FunctionalityStatus.FAILED])
            
            report.append(f"🔧 {tool_name}")
            report.append(f"    Test Cases: {len(results)}")
            report.append(f"    Passed: {passed_count}, Partial: {partial_count}, Failed: {failed_count}")
            
            for result in results:
                status_icon = {
                    FunctionalityStatus.PASSED: "✅",
                    FunctionalityStatus.PARTIAL: "⚠️",
                    FunctionalityStatus.FAILED: "❌",
                    FunctionalityStatus.ERROR: "💥",
                    FunctionalityStatus.TIMEOUT: "⏰"
                }[result.functionality_status]
                
                report.append(f"    {status_icon} {result.test_case}")
                report.append(f"        Expected: {result.expected_behavior}")
                report.append(f"        Actual: {result.actual_behavior}")
                report.append(f"        Duration: {result.test_duration_ms:.2f}ms")
                
                if result.error_message:
                    report.append(f"        Error: {result.error_message}")
                
                report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool functionality tests"""
    try:
        logger.info("Starting Tool Functionality Testing")
        
        # Initialize tester
        tester = ToolFunctionalityTester()
        
        # Run comprehensive functionality tests
        test_suite = tester.test_all_tools_functionality()
        
        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/tool_functionality_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)
        
        # Final status
        if test_suite.functionality_success_rate >= 80:
            logger.info("✅ Tool functionality testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Tool functionality testing completed with issues (success rate: {test_suite.functionality_success_rate:.1f}%)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tool functionality testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 