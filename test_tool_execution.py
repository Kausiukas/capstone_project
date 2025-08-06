#!/usr/bin/env python3
"""
Tool Execution Testing Module

This module implements comprehensive tool execution testing for the MCP server.
It validates that all tools can be executed successfully through the Inspector CLI,
tests execution performance, and validates output formats.

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


class ExecutionStatus(Enum):
    """Execution status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"
    INVALID_OUTPUT = "invalid_output"


@dataclass
class ToolExecutionResult:
    """Result of a tool execution test"""
    tool_name: str
    execution_success: bool
    execution_status: ExecutionStatus
    execution_time_ms: float
    output_size_bytes: int
    output_format_valid: bool
    error_message: Optional[str] = None
    output_preview: Optional[str] = None
    arguments_used: Optional[Dict] = None


@dataclass
class ToolExecutionTestSuite:
    """Complete test suite for tool execution"""
    total_tools: int
    successful_executions: int
    failed_executions: int
    timeout_executions: int
    error_executions: int
    invalid_output_executions: int
    average_execution_time_ms: float
    max_execution_time_ms: float
    min_execution_time_ms: float
    total_output_size_bytes: int
    test_results: List[ToolExecutionResult]
    test_timestamp: datetime
    test_duration_seconds: float
    execution_success_rate: float


class ToolExecutionTester:
    """Comprehensive tool execution testing system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool execution tester
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ToolExecutionResult] = []
        self.start_time: Optional[datetime] = None
        
        # Test arguments for different tool categories
        self.test_arguments = {
            # File operations
            "read_file": {"file_path": "README.md"},
            "write_file": {"file_path": "test_output.txt", "content": "Test content for execution testing"},
            "append_file": {"file_path": "test_append.txt", "content": "Appended content"},
            "list_files": {"directory": ".", "batch_size": 5},
            "list_files_readable": {"directory": ".", "batch_size": 5},
            "list_files_table": {"directory": ".", "offset": "0", "batch_size": 5},
            "list_files_metadata_only": {"directory": ".", "batch_size": 5},
            "stream_files": {"directory": ".", "action": "start"},
            
            # System operations
            "ping": {},
            "get_system_health": {},
            "get_system_status": {},
            "get_pagination_info": {"directory": "."},
            
            # Analysis operations
            "analyze_code": {"file_path": "README.md"},
            "track_token_usage": {"operation": "test", "model": "gpt-3.5-turbo", "input_tokens": 10, "output_tokens": 5},
            "get_cost_summary": {},
            
            # Vector/LLM operations
            "store_embedding": {"name": "test_embedding", "content": "Test content for embedding"},
            "similarity_search": {"query": "test query", "limit": 3},
            "process_text_with_llm": {"text": "Test text", "task": "summarize"},
            
            # Data processing operations
            "dataframe_operations": {"operation": "head", "data": "col1,col2\n1,2\n3,4"},
            "split_text": {"text": "This is a test sentence. This is another sentence.", "method": "sentences"},
            "structured_output": {"text": "Name: John, Age: 30", "schema": {"name": "string", "age": "integer"}},
            "type_convert": {"data": '{"name": "test"}', "target_type": "yaml"}
        }
        
    def test_all_tools_execution(self) -> ToolExecutionTestSuite:
        """
        Test execution of all available tools
        
        Returns:
            ToolExecutionTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool execution testing")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = inspector_cli.get_tools_list(self.mcp_server_path)
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with execution testing")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to test for execution")
        
        # Test each tool execution
        for tool_name in tools_list:
            result = self._test_single_tool_execution(tool_name)
            self.test_results.append(result)
            
            # Log progress
            if result.execution_success:
                logger.info(f"✅ Tool '{tool_name}' executed successfully ({result.execution_time_ms:.2f}ms)")
            else:
                logger.error(f"❌ Tool '{tool_name}' execution failed: {result.error_message}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool execution testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.execution_success_rate:.1f}% ({test_suite.successful_executions}/{test_suite.total_tools})")
        
        return test_suite
    
    def _test_single_tool_execution(self, tool_name: str) -> ToolExecutionResult:
        """
        Test execution of a single tool
        
        Args:
            tool_name: Name of the tool to test
            
        Returns:
            ToolExecutionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Get test arguments for this tool
            arguments = self.test_arguments.get(tool_name, {})
            
            # Execute the tool
            success, response, error = inspector_cli.execute_tool(
                mcp_server_path=self.mcp_server_path,
                tool_name=tool_name,
                arguments=arguments,
                timeout=30
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if success and response:
                # Validate output format
                output_valid = self._validate_output_format(response)
                output_size = len(json.dumps(response))
                output_preview = self._get_output_preview(response)
                
                return ToolExecutionResult(
                    tool_name=tool_name,
                    execution_success=True,
                    execution_status=ExecutionStatus.SUCCESS,
                    execution_time_ms=execution_time,
                    output_size_bytes=output_size,
                    output_format_valid=output_valid,
                    output_preview=output_preview,
                    arguments_used=arguments
                )
            else:
                # Determine execution status
                if "timeout" in (error or "").lower():
                    status = ExecutionStatus.TIMEOUT
                elif "error" in (error or "").lower():
                    status = ExecutionStatus.ERROR
                else:
                    status = ExecutionStatus.FAILED
                
                return ToolExecutionResult(
                    tool_name=tool_name,
                    execution_success=False,
                    execution_status=status,
                    execution_time_ms=execution_time,
                    output_size_bytes=0,
                    output_format_valid=False,
                    error_message=error,
                    arguments_used=arguments
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolExecutionResult(
                tool_name=tool_name,
                execution_success=False,
                execution_status=ExecutionStatus.ERROR,
                execution_time_ms=execution_time,
                output_size_bytes=0,
                output_format_valid=False,
                error_message=str(e),
                arguments_used=arguments
            )
    
    def _validate_output_format(self, response: Dict) -> bool:
        """
        Validate that the tool output has a valid format
        
        Args:
            response: Tool execution response
            
        Returns:
            True if output format is valid, False otherwise
        """
        try:
            # Check if response is a dictionary
            if not isinstance(response, dict):
                return False
            
            # Check for required fields in successful response
            if "result" in response:
                return True
            elif "error" in response:
                return True
            elif "content" in response:
                return True
            elif "data" in response:
                return True
            elif "files" in response:
                return True
            elif "status" in response:
                return True
            
            # If none of the expected fields are present, check if it's a valid JSON structure
            return len(response) > 0
            
        except Exception:
            return False
    
    def _get_output_preview(self, response: Dict, max_length: int = 200) -> str:
        """
        Get a preview of the tool output
        
        Args:
            response: Tool execution response
            max_length: Maximum length of preview
            
        Returns:
            String preview of the output
        """
        try:
            response_str = json.dumps(response, indent=2)
            if len(response_str) <= max_length:
                return response_str
            else:
                return response_str[:max_length] + "..."
        except Exception:
            return str(response)[:max_length] + "..."
    
    def _calculate_test_suite_results(self) -> ToolExecutionTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            ToolExecutionTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        # Count execution statuses
        successful = len([r for r in self.test_results if r.execution_status == ExecutionStatus.SUCCESS])
        failed = len([r for r in self.test_results if r.execution_status == ExecutionStatus.FAILED])
        timeout = len([r for r in self.test_results if r.execution_status == ExecutionStatus.TIMEOUT])
        error = len([r for r in self.test_results if r.execution_status == ExecutionStatus.ERROR])
        invalid_output = len([r for r in self.test_results if r.execution_status == ExecutionStatus.INVALID_OUTPUT])
        
        # Calculate timing metrics
        execution_times = [r.execution_time_ms for r in self.test_results if r.execution_success]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0
        
        # Calculate output size
        total_output_size = sum(r.output_size_bytes for r in self.test_results)
        
        # Calculate success rate
        success_rate = (successful / len(self.test_results)) * 100 if self.test_results else 0
        
        return ToolExecutionTestSuite(
            total_tools=len(self.test_results),
            successful_executions=successful,
            failed_executions=failed,
            timeout_executions=timeout,
            error_executions=error,
            invalid_output_executions=invalid_output,
            average_execution_time_ms=avg_time,
            max_execution_time_ms=max_time,
            min_execution_time_ms=min_time,
            total_output_size_bytes=total_output_size,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration,
            execution_success_rate=success_rate
        )
    
    def _create_empty_test_suite(self) -> ToolExecutionTestSuite:
        """Create an empty test suite for error cases"""
        return ToolExecutionTestSuite(
            total_tools=0,
            successful_executions=0,
            failed_executions=0,
            timeout_executions=0,
            error_executions=0,
            invalid_output_executions=0,
            average_execution_time_ms=0.0,
            max_execution_time_ms=0.0,
            min_execution_time_ms=0.0,
            total_output_size_bytes=0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0,
            execution_success_rate=0.0
        )
    
    def save_test_results(self, test_suite: ToolExecutionTestSuite, 
                         output_file: str = "tool_execution_test_results.json"):
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
                result['execution_status'] = result['execution_status'].value
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tool execution test results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
    
    def generate_test_report(self, test_suite: ToolExecutionTestSuite) -> str:
        """
        Generate a comprehensive test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL EXECUTION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Successful Executions: {test_suite.successful_executions}")
        report.append(f"Failed Executions: {test_suite.failed_executions}")
        report.append(f"Timeout Executions: {test_suite.timeout_executions}")
        report.append(f"Error Executions: {test_suite.error_executions}")
        report.append(f"Invalid Output Executions: {test_suite.invalid_output_executions}")
        report.append(f"Execution Success Rate: {test_suite.execution_success_rate:.1f}%")
        report.append("")
        
        # Performance metrics
        report.append("PERFORMANCE METRICS")
        report.append("-" * 40)
        report.append(f"Average Execution Time: {test_suite.average_execution_time_ms:.2f}ms")
        report.append(f"Maximum Execution Time: {test_suite.max_execution_time_ms:.2f}ms")
        report.append(f"Minimum Execution Time: {test_suite.min_execution_time_ms:.2f}ms")
        report.append(f"Total Output Size: {test_suite.total_output_size_bytes:,} bytes")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        
        for result in test_suite.test_results:
            status_icon = "✅" if result.execution_success else "❌"
            report.append(f"{status_icon} {result.tool_name}")
            report.append(f"    Status: {result.execution_status.value}")
            report.append(f"    Execution Time: {result.execution_time_ms:.2f}ms")
            report.append(f"    Output Size: {result.output_size_bytes:,} bytes")
            
            if result.execution_success:
                report.append(f"    Output Valid: {'✅' if result.output_format_valid else '❌'}")
                if result.output_preview:
                    preview = result.output_preview.replace('\n', '\\n')
                    report.append(f"    Output Preview: {preview[:100]}...")
            else:
                report.append(f"    Error: {result.error_message}")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool execution tests"""
    try:
        logger.info("Starting Tool Execution Testing")
        
        # Initialize tester
        tester = ToolExecutionTester()
        
        # Run comprehensive execution tests
        test_suite = tester.test_all_tools_execution()
        
        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/tool_execution_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)
        
        # Final status
        if test_suite.execution_success_rate >= 80:
            logger.info("✅ Tool execution testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Tool execution testing completed with issues (success rate: {test_suite.execution_success_rate:.1f}%)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tool execution testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 