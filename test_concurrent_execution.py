#!/usr/bin/env python3
"""
Concurrent Execution Testing Module

This module implements comprehensive concurrent execution testing for the MCP server.
It validates system stability under concurrent load, tests resource usage,
and validates concurrency limits and performance degradation patterns.

Part of Task 2.4: Performance Testing
"""

import json
import time
import asyncio
import threading
import statistics
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os

# Import Inspector CLI utilities
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConcurrencyStatus(Enum):
    """Concurrency status enumeration"""
    STABLE = "stable"           # System remains stable under load
    DEGRADED = "degraded"       # Performance degraded but functional
    UNSTABLE = "unstable"       # System becomes unstable
    FAILED = "failed"           # System fails under load
    TIMEOUT = "timeout"         # Operations timeout


@dataclass
class ConcurrentExecutionResult:
    """Result of a concurrent execution test"""
    test_name: str
    concurrency_level: int
    total_operations: int
    successful_operations: int
    failed_operations: int
    timeout_operations: int
    average_response_time_ms: float
    median_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    throughput_ops_per_second: float
    concurrency_status: ConcurrencyStatus
    cpu_usage_percent: float
    memory_usage_mb: float
    test_duration_seconds: float
    error_messages: List[str]
    performance_degradation_percent: float


@dataclass
class ConcurrencyTestSuite:
    """Complete concurrency test suite"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    stable_tests: int
    degraded_tests: int
    unstable_tests: int
    failed_tests_count: int
    timeout_tests: int
    average_throughput_ops_per_second: float
    max_concurrency_level_tested: int
    system_stability_score: float  # 0-100
    performance_degradation_score: float  # 0-100 (lower is better)
    test_results: List[ConcurrentExecutionResult]
    test_timestamp: datetime
    test_duration_seconds: float


class ConcurrentExecutionTester:
    """Comprehensive concurrent execution testing system"""

    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the concurrent execution tester

        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ConcurrentExecutionResult] = []
        self.start_time: Optional[datetime] = None
        self.baseline_performance: Optional[float] = None

        # Concurrency test configurations
        self.concurrency_levels = [1, 2, 4, 8, 16, 32]  # Test different concurrency levels
        self.operations_per_level = 10  # Number of operations per concurrency level
        self.timeout_seconds = 30  # Timeout for individual operations

        # Test tools for concurrency testing (mix of fast and slow operations)
        self.test_tools = [
            "ping",  # Fast operation
            "read_file",  # Medium operation
            "list_files",  # Medium operation
            "analyze_code",  # Slower operation
            "store_embedding"  # Variable speed operation
        ]

        # Test arguments for each tool
        self.test_arguments = {
            "ping": {},
            "read_file": {"file_path": "README.md"},
            "list_files": {"directory": ".", "batch_size": 5},
            "analyze_code": {"file_path": "README.md"},
            "store_embedding": {"name": "test_embedding", "content": "Test content for concurrent testing"}
        }

    def test_concurrent_execution(self) -> ConcurrencyTestSuite:
        """
        Test concurrent execution capabilities

        Returns:
            ConcurrencyTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive concurrent execution testing")
        self.start_time = datetime.now()

        # First, establish baseline performance with single-threaded execution
        logger.info("Establishing baseline performance...")
        self.baseline_performance = self._establish_baseline_performance()

        # Test each concurrency level
        for concurrency_level in self.concurrency_levels:
            logger.info(f"Testing concurrency level: {concurrency_level}")
            result = self._test_concurrency_level(concurrency_level)
            self.test_results.append(result)

            # Log progress
            status_icon = {
                ConcurrencyStatus.STABLE: "🟢",
                ConcurrencyStatus.DEGRADED: "🟡",
                ConcurrencyStatus.UNSTABLE: "🟠",
                ConcurrencyStatus.FAILED: "🔴",
                ConcurrencyStatus.TIMEOUT: "⏰"
            }[result.concurrency_status]

            logger.info(f"{status_icon} Concurrency {concurrency_level}: "
                       f"{result.throughput_ops_per_second:.2f} ops/sec, "
                       f"{result.concurrency_status.value}")

        # Calculate overall test suite results
        test_suite = self._calculate_test_suite_results()

        logger.info(f"Concurrent execution testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"System stability score: {test_suite.system_stability_score:.1f}%")

        return test_suite

    def _establish_baseline_performance(self) -> float:
        """
        Establish baseline performance with single-threaded execution

        Returns:
            Baseline throughput in operations per second
        """
        logger.info("Running baseline performance test...")
        
        start_time = time.time()
        successful_operations = 0
        total_operations = 0

        # Run baseline operations
        for _ in range(self.operations_per_level):
            for tool_name in self.test_tools:
                try:
                    arguments = self.test_arguments.get(tool_name, {})
                    success, _, _ = inspector_cli.execute_tool(
                        mcp_server_path=self.mcp_server_path,
                        tool_name=tool_name,
                        arguments=arguments,
                        timeout=self.timeout_seconds
                    )
                    if success:
                        successful_operations += 1
                    total_operations += 1
                except Exception:
                    total_operations += 1

        baseline_duration = time.time() - start_time
        baseline_throughput = successful_operations / baseline_duration if baseline_duration > 0 else 0

        logger.info(f"Baseline performance: {baseline_throughput:.2f} ops/sec")
        return baseline_throughput

    def _test_concurrency_level(self, concurrency_level: int) -> ConcurrentExecutionResult:
        """
        Test a specific concurrency level

        Args:
            concurrency_level: Number of concurrent operations

        Returns:
            ConcurrentExecutionResult with test details
        """
        test_name = f"concurrency_level_{concurrency_level}"
        start_time = time.time()
        
        # Monitor system resources
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Prepare operations
        operations = []
        for _ in range(self.operations_per_level):
            for tool_name in self.test_tools:
                operations.append((tool_name, self.test_arguments.get(tool_name, {})))

        # Execute operations concurrently
        results = self._execute_concurrent_operations(operations, concurrency_level)
        
        test_duration = time.time() - start_time
        
        # Calculate final resource usage
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Analyze results
        successful_ops = len([r for r in results if r['success']])
        failed_ops = len([r for r in results if not r['success'] and not r['timeout']])
        timeout_ops = len([r for r in results if r['timeout']])
        
        response_times = [r['response_time'] for r in results if r['success']]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            avg_time = median_time = min_time = max_time = 0

        throughput = successful_ops / test_duration if test_duration > 0 else 0
        
        # Calculate performance degradation
        if self.baseline_performance and self.baseline_performance > 0:
            degradation = ((self.baseline_performance - throughput) / self.baseline_performance) * 100
        else:
            degradation = 0

        # Determine concurrency status
        status = self._determine_concurrency_status(
            successful_ops, failed_ops, timeout_ops, degradation, concurrency_level
        )

        # Collect error messages
        error_messages = [r['error'] for r in results if r['error']]

        return ConcurrentExecutionResult(
            test_name=test_name,
            concurrency_level=concurrency_level,
            total_operations=len(results),
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            timeout_operations=timeout_ops,
            average_response_time_ms=avg_time * 1000,
            median_response_time_ms=median_time * 1000,
            min_response_time_ms=min_time * 1000,
            max_response_time_ms=max_time * 1000,
            throughput_ops_per_second=throughput,
            concurrency_status=status,
            cpu_usage_percent=(initial_cpu + final_cpu) / 2,
            memory_usage_mb=(initial_memory + final_memory) / 2,
            test_duration_seconds=test_duration,
            error_messages=error_messages,
            performance_degradation_percent=degradation
        )

    def _execute_concurrent_operations(self, operations: List[Tuple[str, Dict]], 
                                     max_workers: int) -> List[Dict]:
        """
        Execute operations concurrently using ThreadPoolExecutor

        Args:
            operations: List of (tool_name, arguments) tuples
            max_workers: Maximum number of concurrent workers

        Returns:
            List of operation results
        """
        results = []

        def execute_operation(operation):
            tool_name, arguments = operation
            start_time = time.time()
            
            try:
                success, response, error = inspector_cli.execute_tool(
                    mcp_server_path=self.mcp_server_path,
                    tool_name=tool_name,
                    arguments=arguments,
                    timeout=self.timeout_seconds
                )
                
                response_time = time.time() - start_time
                
                return {
                    'success': success,
                    'response_time': response_time,
                    'timeout': False,
                    'error': error if not success else None
                }
                
            except Exception as e:
                response_time = time.time() - start_time
                return {
                    'success': False,
                    'response_time': response_time,
                    'timeout': response_time >= self.timeout_seconds,
                    'error': str(e)
                }

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all operations
            future_to_operation = {
                executor.submit(execute_operation, operation): operation 
                for operation in operations
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_operation):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'response_time': 0,
                        'timeout': False,
                        'error': str(e)
                    })

        return results

    def _determine_concurrency_status(self, successful_ops: int, failed_ops: int, 
                                    timeout_ops: int, degradation: float, 
                                    concurrency_level: int) -> ConcurrencyStatus:
        """
        Determine the concurrency status based on test results

        Args:
            successful_ops: Number of successful operations
            failed_ops: Number of failed operations
            timeout_ops: Number of timeout operations
            degradation: Performance degradation percentage
            concurrency_level: Current concurrency level

        Returns:
            ConcurrencyStatus enum value
        """
        total_ops = successful_ops + failed_ops + timeout_ops
        if total_ops == 0:
            return ConcurrencyStatus.FAILED

        success_rate = successful_ops / total_ops

        # Determine status based on success rate, timeouts, and degradation
        if success_rate >= 0.95 and degradation < 20:
            return ConcurrencyStatus.STABLE
        elif success_rate >= 0.80 and degradation < 50:
            return ConcurrencyStatus.DEGRADED
        elif success_rate >= 0.50:
            return ConcurrencyStatus.UNSTABLE
        elif timeout_ops > failed_ops:
            return ConcurrencyStatus.TIMEOUT
        else:
            return ConcurrencyStatus.FAILED

    def _calculate_test_suite_results(self) -> ConcurrencyTestSuite:
        """
        Calculate comprehensive test suite results

        Returns:
            ConcurrencyTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()

        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()

        # Count statuses
        stable_count = len([r for r in self.test_results if r.concurrency_status == ConcurrencyStatus.STABLE])
        degraded_count = len([r for r in self.test_results if r.concurrency_status == ConcurrencyStatus.DEGRADED])
        unstable_count = len([r for r in self.test_results if r.concurrency_status == ConcurrencyStatus.UNSTABLE])
        failed_count = len([r for r in self.test_results if r.concurrency_status == ConcurrencyStatus.FAILED])
        timeout_count = len([r for r in self.test_results if r.concurrency_status == ConcurrencyStatus.TIMEOUT])

        # Calculate throughput metrics
        throughputs = [r.throughput_ops_per_second for r in self.test_results if r.throughput_ops_per_second > 0]
        avg_throughput = statistics.mean(throughputs) if throughputs else 0

        # Calculate stability score (weighted by concurrency level)
        stability_scores = []
        for result in self.test_results:
            if result.concurrency_status == ConcurrencyStatus.STABLE:
                score = 100
            elif result.concurrency_status == ConcurrencyStatus.DEGRADED:
                score = 70
            elif result.concurrency_status == ConcurrencyStatus.UNSTABLE:
                score = 40
            else:
                score = 0
            
            # Weight by concurrency level (higher concurrency = more important)
            weighted_score = score * (result.concurrency_level / max(r.concurrency_level for r in self.test_results))
            stability_scores.append(weighted_score)

        stability_score = statistics.mean(stability_scores) if stability_scores else 0

        # Calculate performance degradation score (lower is better)
        degradations = [r.performance_degradation_percent for r in self.test_results]
        avg_degradation = statistics.mean(degradations) if degradations else 0
        degradation_score = max(0, 100 - avg_degradation)

        return ConcurrencyTestSuite(
            total_tests=len(self.test_results),
            successful_tests=stable_count + degraded_count,
            failed_tests=failed_count + timeout_count,
            stable_tests=stable_count,
            degraded_tests=degraded_count,
            unstable_tests=unstable_count,
            failed_tests_count=failed_count,
            timeout_tests=timeout_count,
            average_throughput_ops_per_second=avg_throughput,
            max_concurrency_level_tested=max(r.concurrency_level for r in self.test_results),
            system_stability_score=stability_score,
            performance_degradation_score=degradation_score,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )

    def _create_empty_test_suite(self) -> ConcurrencyTestSuite:
        """Create an empty test suite for error cases"""
        return ConcurrencyTestSuite(
            total_tests=0,
            successful_tests=0,
            failed_tests=0,
            stable_tests=0,
            degraded_tests=0,
            unstable_tests=0,
            failed_tests_count=0,
            timeout_tests=0,
            average_throughput_ops_per_second=0.0,
            max_concurrency_level_tested=0,
            system_stability_score=0.0,
            performance_degradation_score=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0
        )

    def save_test_results(self, test_suite: ConcurrencyTestSuite,
                         output_file: str = "concurrent_execution_test_results.json"):
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
                result['concurrency_status'] = result['concurrency_status'].value

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Concurrent execution test results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def generate_test_report(self, test_suite: ConcurrencyTestSuite) -> str:
        """
        Generate a comprehensive test report

        Args:
            test_suite: Test suite results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("CONCURRENT EXECUTION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")

        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Tests: {test_suite.total_tests}")
        report.append(f"Successful Tests: {test_suite.successful_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests}")
        report.append(f"System Stability Score: {test_suite.system_stability_score:.1f}%")
        report.append(f"Performance Degradation Score: {test_suite.performance_degradation_score:.1f}%")
        report.append(f"Average Throughput: {test_suite.average_throughput_ops_per_second:.2f} ops/sec")
        report.append(f"Max Concurrency Level Tested: {test_suite.max_concurrency_level_tested}")
        report.append("")

        # Status distribution
        report.append("STATUS DISTRIBUTION")
        report.append("-" * 40)
        report.append(f"Stable Tests: {test_suite.stable_tests}")
        report.append(f"Degraded Tests: {test_suite.degraded_tests}")
        report.append(f"Unstable Tests: {test_suite.unstable_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests_count}")
        report.append(f"Timeout Tests: {test_suite.timeout_tests}")
        report.append("")

        # Detailed results by concurrency level
        report.append("DETAILED RESULTS BY CONCURRENCY LEVEL")
        report.append("-" * 40)

        for result in test_suite.test_results:
            status_icon = {
                ConcurrencyStatus.STABLE: "🟢",
                ConcurrencyStatus.DEGRADED: "🟡",
                ConcurrencyStatus.UNSTABLE: "🟠",
                ConcurrencyStatus.FAILED: "🔴",
                ConcurrencyStatus.TIMEOUT: "⏰"
            }[result.concurrency_status]

            report.append(f"{status_icon} Concurrency Level {result.concurrency_level}")
            report.append(f"    Status: {result.concurrency_status.value}")
            report.append(f"    Throughput: {result.throughput_ops_per_second:.2f} ops/sec")
            report.append(f"    Success Rate: {result.successful_operations}/{result.total_operations}")
            report.append(f"    Average Response Time: {result.average_response_time_ms:.2f}ms")
            report.append(f"    Performance Degradation: {result.performance_degradation_percent:.1f}%")
            report.append(f"    CPU Usage: {result.cpu_usage_percent:.1f}%")
            report.append(f"    Memory Usage: {result.memory_usage_mb:.1f} MB")
            report.append(f"    Test Duration: {result.test_duration_seconds:.2f}s")
            
            if result.error_messages:
                report.append(f"    Errors: {len(result.error_messages)} errors")
                for error in result.error_messages[:3]:  # Show first 3 errors
                    report.append(f"        - {error[:100]}...")
            
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run concurrent execution tests"""
    try:
        logger.info("Starting Concurrent Execution Testing")

        # Initialize tester
        tester = ConcurrentExecutionTester()

        # Run comprehensive concurrent execution tests
        test_suite = tester.test_concurrent_execution()

        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/concurrent_execution_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)

        # Final status
        if test_suite.system_stability_score >= 70:
            logger.info("✅ Concurrent execution testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Concurrent execution testing completed with stability issues "
                         f"(score: {test_suite.system_stability_score:.1f}%)")
            return False

    except Exception as e:
        logger.error(f"❌ Concurrent execution testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 