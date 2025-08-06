#!/usr/bin/env python3
"""
Response Time Testing Module

This module implements comprehensive response time testing for the MCP server.
It validates individual tool response times, performance targets, consistency,
and provides trend analysis for performance optimization.

Part of Task 2.4: Performance Testing
"""

import json
import time
import statistics
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


class ResponseTimeStatus(Enum):
    """Response time status enumeration"""
    EXCELLENT = "excellent"  # < 1 second
    GOOD = "good"           # 1-3 seconds
    ACCEPTABLE = "acceptable"  # 3-5 seconds
    SLOW = "slow"           # 5-10 seconds
    UNACCEPTABLE = "unacceptable"  # > 10 seconds


@dataclass
class ResponseTimeResult:
    """Result of a response time test"""
    tool_name: str
    test_iteration: int
    response_time_ms: float
    response_time_status: ResponseTimeStatus
    success: bool
    error_message: Optional[str] = None
    response_size_bytes: Optional[int] = None
    arguments_used: Optional[Dict] = None


@dataclass
class ToolResponseTimeSummary:
    """Summary of response time tests for a tool"""
    tool_name: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    average_response_time_ms: float
    median_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    standard_deviation_ms: float
    percentile_95_ms: float
    percentile_99_ms: float
    response_time_status: ResponseTimeStatus
    consistency_score: float  # 0-100, higher is more consistent
    performance_score: float  # 0-100, based on speed and consistency
    test_results: List[ResponseTimeResult]


@dataclass
class ResponseTimeTestSuite:
    """Complete response time test suite"""
    total_tools: int
    total_tests: int
    successful_tests: int
    failed_tests: int
    average_response_time_ms: float
    median_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    tools_with_excellent_performance: int
    tools_with_good_performance: int
    tools_with_acceptable_performance: int
    tools_with_slow_performance: int
    tools_with_unacceptable_performance: int
    overall_performance_score: float
    tool_summaries: List[ToolResponseTimeSummary]
    test_timestamp: datetime
    test_duration_seconds: float


class ResponseTimeTester:
    """Comprehensive response time testing system"""

    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the response time tester

        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ResponseTimeResult] = []
        self.tool_summaries: List[ToolResponseTimeSummary] = []
        self.start_time: Optional[datetime] = None

        # Performance targets (in milliseconds)
        self.performance_targets = {
            "excellent": 1000,    # < 1 second
            "good": 3000,         # < 3 seconds
            "acceptable": 5000,   # < 5 seconds
            "slow": 10000,        # < 10 seconds
            "unacceptable": float('inf')  # > 10 seconds
        }

        # Test arguments for different tool categories
        self.test_arguments = {
            # File operations (typically fast)
            "read_file": {"file_path": "README.md"},
            "list_files": {"directory": ".", "batch_size": 5},
            "ping": {},

            # System operations (typically fast)
            "get_system_health": {},
            "get_system_status": {},

            # Analysis operations (may be slower)
            "analyze_code": {"file_path": "README.md"},
            "track_token_usage": {"operation": "test", "model": "gpt-3.5-turbo", "input_tokens": 10, "output_tokens": 5},

            # Vector/LLM operations (may be slower)
            "store_embedding": {"name": "test_embedding", "content": "Test content for embedding"},
            "similarity_search": {"query": "test query", "limit": 3},
            "process_text_with_llm": {"text": "Test text", "task": "summarize"},

            # Data processing operations (variable speed)
            "dataframe_operations": {"operation": "head", "data": "col1,col2\n1,2\n3,4"},
            "split_text": {"text": "This is a test sentence. This is another sentence.", "method": "sentences"},
            "structured_output": {"text": "Name: John, Age: 30", "schema": {"name": "string", "age": "integer"}},
            "type_convert": {"data": '{"name": "test"}', "target_type": "yaml"}
        }

    def test_all_tools_response_times(self, iterations_per_tool: int = 5) -> ResponseTimeTestSuite:
        """
        Test response times for all available tools

        Args:
            iterations_per_tool: Number of test iterations per tool

        Returns:
            ResponseTimeTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive response time testing")
        self.start_time = datetime.now()

        # Get list of all tools first
        tools_list = inspector_cli.get_tools_list(self.mcp_server_path)
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with response time testing")
            return self._create_empty_test_suite()

        logger.info(f"Found {len(tools_list)} tools to test for response times")
        logger.info(f"Testing {iterations_per_tool} iterations per tool")

        # Test each tool's response times
        for tool_name in tools_list:
            logger.info(f"Testing response times for tool: {tool_name}")
            tool_results = self._test_tool_response_times(tool_name, iterations_per_tool)
            self.test_results.extend(tool_results)

            # Create summary for this tool
            tool_summary = self._create_tool_summary(tool_name, tool_results)
            self.tool_summaries.append(tool_summary)

            # Log progress
            logger.info(f"✅ {tool_name}: {tool_summary.response_time_status.value} "
                       f"({tool_summary.average_response_time_ms:.2f}ms avg)")

        # Calculate overall test suite results
        test_suite = self._calculate_test_suite_results()

        logger.info(f"Response time testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Overall performance score: {test_suite.overall_performance_score:.1f}%")

        return test_suite

    def _test_tool_response_times(self, tool_name: str, iterations: int) -> List[ResponseTimeResult]:
        """
        Test response times for a specific tool

        Args:
            tool_name: Name of the tool to test
            iterations: Number of test iterations

        Returns:
            List of ResponseTimeResult objects
        """
        results = []

        for iteration in range(1, iterations + 1):
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

                response_time = (time.time() - start_time) * 1000

                if success and response:
                    # Calculate response size
                    response_size = len(json.dumps(response))
                    
                    # Determine response time status
                    status = self._determine_response_time_status(response_time)

                    result = ResponseTimeResult(
                        tool_name=tool_name,
                        test_iteration=iteration,
                        response_time_ms=response_time,
                        response_time_status=status,
                        success=True,
                        response_size_bytes=response_size,
                        arguments_used=arguments
                    )
                else:
                    # Determine response time status for failed tests
                    status = self._determine_response_time_status(response_time)

                    result = ResponseTimeResult(
                        tool_name=tool_name,
                        test_iteration=iteration,
                        response_time_ms=response_time,
                        response_time_status=status,
                        success=False,
                        error_message=error,
                        arguments_used=arguments
                    )

                results.append(result)

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                result = ResponseTimeResult(
                    tool_name=tool_name,
                    test_iteration=iteration,
                    response_time_ms=response_time,
                    response_time_status=ResponseTimeStatus.UNACCEPTABLE,
                    success=False,
                    error_message=str(e),
                    arguments_used=arguments
                )
                results.append(result)

        return results

    def _determine_response_time_status(self, response_time_ms: float) -> ResponseTimeStatus:
        """
        Determine the status of a response time

        Args:
            response_time_ms: Response time in milliseconds

        Returns:
            ResponseTimeStatus enum value
        """
        if response_time_ms < self.performance_targets["excellent"]:
            return ResponseTimeStatus.EXCELLENT
        elif response_time_ms < self.performance_targets["good"]:
            return ResponseTimeStatus.GOOD
        elif response_time_ms < self.performance_targets["acceptable"]:
            return ResponseTimeStatus.ACCEPTABLE
        elif response_time_ms < self.performance_targets["slow"]:
            return ResponseTimeStatus.SLOW
        else:
            return ResponseTimeStatus.UNACCEPTABLE

    def _create_tool_summary(self, tool_name: str, results: List[ResponseTimeResult]) -> ToolResponseTimeSummary:
        """
        Create a summary for a tool's response time tests

        Args:
            tool_name: Name of the tool
            results: List of test results for the tool

        Returns:
            ToolResponseTimeSummary object
        """
        if not results:
            return self._create_empty_tool_summary(tool_name)

        # Filter successful tests for statistics
        successful_results = [r for r in results if r.success]
        response_times = [r.response_time_ms for r in successful_results]

        if not response_times:
            return self._create_empty_tool_summary(tool_name)

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0

        # Calculate percentiles
        sorted_times = sorted(response_times)
        percentile_95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0
        percentile_99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0

        # Determine overall status (most common status)
        status_counts = {}
        for result in results:
            status = result.response_time_status
            status_counts[status] = status_counts.get(status, 0) + 1

        overall_status = max(status_counts, key=status_counts.get)

        # Calculate consistency score (lower std dev = higher consistency)
        consistency_score = max(0, 100 - (std_dev / avg_time * 100)) if avg_time > 0 else 100

        # Calculate performance score (based on speed and consistency)
        speed_score = max(0, 100 - (avg_time / self.performance_targets["good"] * 100))
        performance_score = (speed_score + consistency_score) / 2

        return ToolResponseTimeSummary(
            tool_name=tool_name,
            total_tests=len(results),
            successful_tests=len(successful_results),
            failed_tests=len(results) - len(successful_results),
            average_response_time_ms=avg_time,
            median_response_time_ms=median_time,
            min_response_time_ms=min_time,
            max_response_time_ms=max_time,
            standard_deviation_ms=std_dev,
            percentile_95_ms=percentile_95,
            percentile_99_ms=percentile_99,
            response_time_status=overall_status,
            consistency_score=consistency_score,
            performance_score=performance_score,
            test_results=results
        )

    def _create_empty_tool_summary(self, tool_name: str) -> ToolResponseTimeSummary:
        """Create an empty tool summary for error cases"""
        return ToolResponseTimeSummary(
            tool_name=tool_name,
            total_tests=0,
            successful_tests=0,
            failed_tests=0,
            average_response_time_ms=0.0,
            median_response_time_ms=0.0,
            min_response_time_ms=0.0,
            max_response_time_ms=0.0,
            standard_deviation_ms=0.0,
            percentile_95_ms=0.0,
            percentile_99_ms=0.0,
            response_time_status=ResponseTimeStatus.UNACCEPTABLE,
            consistency_score=0.0,
            performance_score=0.0,
            test_results=[]
        )

    def _calculate_test_suite_results(self) -> ResponseTimeTestSuite:
        """
        Calculate comprehensive test suite results

        Returns:
            ResponseTimeTestSuite with calculated metrics
        """
        if not self.tool_summaries:
            return self._create_empty_test_suite()

        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()

        # Aggregate statistics across all tools
        all_response_times = []
        for summary in self.tool_summaries:
            all_response_times.extend([r.response_time_ms for r in summary.test_results if r.success])

        if not all_response_times:
            return self._create_empty_test_suite()

        # Calculate overall statistics
        avg_time = statistics.mean(all_response_times)
        median_time = statistics.median(all_response_times)
        min_time = min(all_response_times)
        max_time = max(all_response_times)

        # Count tools by performance category
        excellent_count = len([s for s in self.tool_summaries if s.response_time_status == ResponseTimeStatus.EXCELLENT])
        good_count = len([s for s in self.tool_summaries if s.response_time_status == ResponseTimeStatus.GOOD])
        acceptable_count = len([s for s in self.tool_summaries if s.response_time_status == ResponseTimeStatus.ACCEPTABLE])
        slow_count = len([s for s in self.tool_summaries if s.response_time_status == ResponseTimeStatus.SLOW])
        unacceptable_count = len([s for s in self.tool_summaries if s.response_time_status == ResponseTimeStatus.UNACCEPTABLE])

        # Calculate overall performance score
        total_tools = len(self.tool_summaries)
        performance_scores = [s.performance_score for s in self.tool_summaries]
        overall_performance_score = statistics.mean(performance_scores) if performance_scores else 0

        # Calculate total test counts
        total_tests = sum(s.total_tests for s in self.tool_summaries)
        successful_tests = sum(s.successful_tests for s in self.tool_summaries)
        failed_tests = sum(s.failed_tests for s in self.tool_summaries)

        return ResponseTimeTestSuite(
            total_tools=total_tools,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            average_response_time_ms=avg_time,
            median_response_time_ms=median_time,
            min_response_time_ms=min_time,
            max_response_time_ms=max_time,
            tools_with_excellent_performance=excellent_count,
            tools_with_good_performance=good_count,
            tools_with_acceptable_performance=acceptable_count,
            tools_with_slow_performance=slow_count,
            tools_with_unacceptable_performance=unacceptable_count,
            overall_performance_score=overall_performance_score,
            tool_summaries=self.tool_summaries,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )

    def _create_empty_test_suite(self) -> ResponseTimeTestSuite:
        """Create an empty test suite for error cases"""
        return ResponseTimeTestSuite(
            total_tools=0,
            total_tests=0,
            successful_tests=0,
            failed_tests=0,
            average_response_time_ms=0.0,
            median_response_time_ms=0.0,
            min_response_time_ms=0.0,
            max_response_time_ms=0.0,
            tools_with_excellent_performance=0,
            tools_with_good_performance=0,
            tools_with_acceptable_performance=0,
            tools_with_slow_performance=0,
            tools_with_unacceptable_performance=0,
            overall_performance_score=0.0,
            tool_summaries=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0
        )

    def save_test_results(self, test_suite: ResponseTimeTestSuite,
                         output_file: str = "response_time_test_results.json"):
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
            for summary in results_dict['tool_summaries']:
                summary['response_time_status'] = summary['response_time_status'].value
                for result in summary['test_results']:
                    result['response_time_status'] = result['response_time_status'].value

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Response time test results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def generate_test_report(self, test_suite: ResponseTimeTestSuite) -> str:
        """
        Generate a comprehensive test report

        Args:
            test_suite: Test suite results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("RESPONSE TIME TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")

        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Total Tests: {test_suite.total_tests}")
        report.append(f"Successful Tests: {test_suite.successful_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests}")
        report.append(f"Overall Performance Score: {test_suite.overall_performance_score:.1f}%")
        report.append("")

        # Performance distribution
        report.append("PERFORMANCE DISTRIBUTION")
        report.append("-" * 40)
        report.append(f"Excellent Performance (< 1s): {test_suite.tools_with_excellent_performance} tools")
        report.append(f"Good Performance (1-3s): {test_suite.tools_with_good_performance} tools")
        report.append(f"Acceptable Performance (3-5s): {test_suite.tools_with_acceptable_performance} tools")
        report.append(f"Slow Performance (5-10s): {test_suite.tools_with_slow_performance} tools")
        report.append(f"Unacceptable Performance (> 10s): {test_suite.tools_with_unacceptable_performance} tools")
        report.append("")

        # Overall timing metrics
        report.append("OVERALL TIMING METRICS")
        report.append("-" * 40)
        report.append(f"Average Response Time: {test_suite.average_response_time_ms:.2f}ms")
        report.append(f"Median Response Time: {test_suite.median_response_time_ms:.2f}ms")
        report.append(f"Minimum Response Time: {test_suite.min_response_time_ms:.2f}ms")
        report.append(f"Maximum Response Time: {test_suite.max_response_time_ms:.2f}ms")
        report.append("")

        # Detailed results by tool
        report.append("DETAILED RESULTS BY TOOL")
        report.append("-" * 40)

        for summary in test_suite.tool_summaries:
            status_icon = {
                ResponseTimeStatus.EXCELLENT: "🟢",
                ResponseTimeStatus.GOOD: "🟡",
                ResponseTimeStatus.ACCEPTABLE: "🟠",
                ResponseTimeStatus.SLOW: "🔴",
                ResponseTimeStatus.UNACCEPTABLE: "⚫"
            }[summary.response_time_status]

            report.append(f"{status_icon} {summary.tool_name}")
            report.append(f"    Performance Score: {summary.performance_score:.1f}%")
            report.append(f"    Consistency Score: {summary.consistency_score:.1f}%")
            report.append(f"    Average Response Time: {summary.average_response_time_ms:.2f}ms")
            report.append(f"    Median Response Time: {summary.median_response_time_ms:.2f}ms")
            report.append(f"    Min/Max: {summary.min_response_time_ms:.2f}ms / {summary.max_response_time_ms:.2f}ms")
            report.append(f"    Standard Deviation: {summary.standard_deviation_ms:.2f}ms")
            report.append(f"    95th Percentile: {summary.percentile_95_ms:.2f}ms")
            report.append(f"    99th Percentile: {summary.percentile_99_ms:.2f}ms")
            report.append(f"    Success Rate: {summary.successful_tests}/{summary.total_tests}")
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run response time tests"""
    try:
        logger.info("Starting Response Time Testing")

        # Initialize tester
        tester = ResponseTimeTester()

        # Run comprehensive response time tests
        test_suite = tester.test_all_tools_response_times(iterations_per_tool=5)

        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/response_time_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)

        # Final status
        if test_suite.overall_performance_score >= 80:
            logger.info("✅ Response time testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Response time testing completed with performance issues "
                         f"(score: {test_suite.overall_performance_score:.1f}%)")
            return False

    except Exception as e:
        logger.error(f"❌ Response time testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 