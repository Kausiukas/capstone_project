#!/usr/bin/env python3
"""
Load Handling Testing Module

This module implements comprehensive load handling testing for the MCP server.
It validates system behavior under high load, performance degradation patterns,
system recovery capabilities, and provides capacity planning data.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os

# Import Inspector CLI utilities
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadStatus(Enum):
    """Load handling status enumeration"""
    NORMAL = "normal"           # System operating normally
    STRESSED = "stressed"       # System under stress but functional
    OVERLOADED = "overloaded"   # System overloaded, performance degraded
    FAILING = "failing"         # System failing under load
    RECOVERED = "recovered"     # System recovered after load reduction


@dataclass
class LoadTestResult:
    """Result of a load test"""
    test_name: str
    load_level: str  # "low", "medium", "high", "extreme"
    concurrent_operations: int
    duration_seconds: int
    total_operations: int
    successful_operations: int
    failed_operations: int
    timeout_operations: int
    average_response_time_ms: float
    median_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    throughput_ops_per_second: float
    error_rate_percent: float
    timeout_rate_percent: float
    load_status: LoadStatus
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    system_stability_score: float  # 0-100
    performance_degradation_percent: float
    recovery_time_seconds: Optional[float] = None


@dataclass
class LoadHandlingTestSuite:
    """Complete load handling test suite"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    normal_load_tests: int
    stressed_tests: int
    overloaded_tests: int
    failing_tests: int
    recovered_tests: int
    average_throughput_ops_per_second: float
    max_sustainable_load: int
    system_capacity_score: float  # 0-100
    recovery_capability_score: float  # 0-100
    load_handling_score: float  # 0-100
    test_results: List[LoadTestResult]
    test_timestamp: datetime
    test_duration_seconds: float


class LoadHandlingTester:
    """Comprehensive load handling testing system"""

    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the load handling tester

        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[LoadTestResult] = []
        self.start_time: Optional[datetime] = None
        self.baseline_performance: Optional[float] = None

        # Load test configurations
        self.load_levels = {
            "low": {"concurrent_ops": 5, "duration": 30, "description": "Low load"},
            "medium": {"concurrent_ops": 15, "duration": 60, "description": "Medium load"},
            "high": {"concurrent_ops": 30, "duration": 120, "description": "High load"},
            "extreme": {"concurrent_ops": 50, "duration": 180, "description": "Extreme load"}
        }

        # Test tools for load testing (mix of different operation types)
        self.test_tools = [
            "ping",  # Fast operation
            "read_file",  # Medium operation
            "list_files",  # Medium operation
            "analyze_code",  # Slower operation
            "store_embedding",  # Variable speed operation
            "similarity_search",  # Slower operation
            "process_text_with_llm"  # Slowest operation
        ]

        # Test arguments for each tool
        self.test_arguments = {
            "ping": {},
            "read_file": {"file_path": "README.md"},
            "list_files": {"directory": ".", "batch_size": 5},
            "analyze_code": {"file_path": "README.md"},
            "store_embedding": {"name": "test_embedding", "content": "Test content for load testing"},
            "similarity_search": {"query": "test query", "limit": 3},
            "process_text_with_llm": {"text": "Test text for load testing", "task": "summarize"}
        }

    def test_load_handling(self) -> LoadHandlingTestSuite:
        """
        Test load handling capabilities

        Returns:
            LoadHandlingTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive load handling testing")
        self.start_time = datetime.now()

        # First, establish baseline performance
        logger.info("Establishing baseline performance...")
        self.baseline_performance = self._establish_baseline_performance()

        # Test each load level
        for load_level, config in self.load_levels.items():
            logger.info(f"Testing {config['description']} ({load_level})")
            result = self._test_load_level(load_level, config)
            self.test_results.append(result)

            # Log progress
            status_icon = {
                LoadStatus.NORMAL: "🟢",
                LoadStatus.STRESSED: "🟡",
                LoadStatus.OVERLOADED: "🟠",
                LoadStatus.FAILING: "🔴",
                LoadStatus.RECOVERED: "🟢"
            }[result.load_status]

            logger.info(f"{status_icon} {load_level} load: "
                       f"{result.throughput_ops_per_second:.2f} ops/sec, "
                       f"{result.load_status.value}")

        # Test recovery capability
        logger.info("Testing system recovery capability...")
        recovery_result = self._test_system_recovery()
        if recovery_result:
            self.test_results.append(recovery_result)

        # Calculate overall test suite results
        test_suite = self._calculate_test_suite_results()

        logger.info(f"Load handling testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"System capacity score: {test_suite.system_capacity_score:.1f}%")

        return test_suite

    def _establish_baseline_performance(self) -> float:
        """
        Establish baseline performance with minimal load

        Returns:
            Baseline throughput in operations per second
        """
        logger.info("Running baseline performance test...")
        
        start_time = time.time()
        successful_operations = 0
        total_operations = 0

        # Run baseline operations with minimal concurrency
        for _ in range(10):
            for tool_name in self.test_tools:
                try:
                    arguments = self.test_arguments.get(tool_name, {})
                    success, _, _ = inspector_cli.execute_tool(
                        mcp_server_path=self.mcp_server_path,
                        tool_name=tool_name,
                        arguments=arguments,
                        timeout=30
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

    def _test_load_level(self, load_level: str, config: Dict) -> LoadTestResult:
        """
        Test a specific load level

        Args:
            load_level: Load level name
            config: Load configuration

        Returns:
            LoadTestResult with test details
        """
        test_name = f"load_test_{load_level}"
        concurrent_ops = config["concurrent_ops"]
        duration = config["duration"]
        
        logger.info(f"Starting {load_level} load test: {concurrent_ops} concurrent ops for {duration}s")
        
        start_time = time.time()
        
        # Monitor system resources
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_memory_percent = psutil.virtual_memory().percent

        # Generate operations for the duration
        operations = self._generate_operations_for_duration(duration, concurrent_ops)
        
        # Execute operations under load
        results = self._execute_load_operations(operations, concurrent_ops, duration)
        
        test_duration = time.time() - start_time
        
        # Calculate final resource usage
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_memory_percent = psutil.virtual_memory().percent

        # Analyze results
        successful_ops = len([r for r in results if r['success']])
        failed_ops = len([r for r in results if not r['success'] and not r['timeout']])
        timeout_ops = len([r for r in results if r['timeout']])
        total_ops = len(results)
        
        response_times = [r['response_time'] for r in results if r['success']]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            avg_time = median_time = min_time = max_time = 0

        throughput = successful_ops / test_duration if test_duration > 0 else 0
        error_rate = (failed_ops / total_ops * 100) if total_ops > 0 else 0
        timeout_rate = (timeout_ops / total_ops * 100) if total_ops > 0 else 0
        
        # Calculate performance degradation
        if self.baseline_performance and self.baseline_performance > 0:
            degradation = ((self.baseline_performance - throughput) / self.baseline_performance) * 100
        else:
            degradation = 0

        # Determine load status
        status = self._determine_load_status(
            successful_ops, failed_ops, timeout_ops, degradation, 
            final_cpu, final_memory_percent, load_level
        )

        # Calculate system stability score
        stability_score = self._calculate_stability_score(
            successful_ops, total_ops, error_rate, timeout_rate, degradation
        )

        return LoadTestResult(
            test_name=test_name,
            load_level=load_level,
            concurrent_operations=concurrent_ops,
            duration_seconds=duration,
            total_operations=total_ops,
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            timeout_operations=timeout_ops,
            average_response_time_ms=avg_time * 1000,
            median_response_time_ms=median_time * 1000,
            min_response_time_ms=min_time * 1000,
            max_response_time_ms=max_time * 1000,
            throughput_ops_per_second=throughput,
            error_rate_percent=error_rate,
            timeout_rate_percent=timeout_rate,
            load_status=status,
            cpu_usage_percent=(initial_cpu + final_cpu) / 2,
            memory_usage_mb=(initial_memory + final_memory) / 2,
            memory_usage_percent=(initial_memory_percent + final_memory_percent) / 2,
            system_stability_score=stability_score,
            performance_degradation_percent=degradation
        )

    def _generate_operations_for_duration(self, duration: int, concurrent_ops: int) -> List[Tuple[str, Dict]]:
        """
        Generate operations to run for the specified duration

        Args:
            duration: Test duration in seconds
            concurrent_ops: Number of concurrent operations

        Returns:
            List of (tool_name, arguments) tuples
        """
        operations = []
        estimated_ops_per_second = concurrent_ops * 2  # Estimate 2 ops per second per concurrent worker
        total_ops = int(duration * estimated_ops_per_second)
        
        for _ in range(total_ops):
            tool_name = self.test_tools[_ % len(self.test_tools)]
            arguments = self.test_arguments.get(tool_name, {})
            operations.append((tool_name, arguments))
        
        return operations

    def _execute_load_operations(self, operations: List[Tuple[str, Dict]], 
                               max_workers: int, duration: int) -> List[Dict]:
        """
        Execute operations under load for the specified duration

        Args:
            operations: List of operations to execute
            max_workers: Maximum number of concurrent workers
            duration: Test duration in seconds

        Returns:
            List of operation results
        """
        results = []
        start_time = time.time()

        def execute_operation(operation):
            tool_name, arguments = operation
            op_start_time = time.time()
            
            try:
                success, response, error = inspector_cli.execute_tool(
                    mcp_server_path=self.mcp_server_path,
                    tool_name=tool_name,
                    arguments=arguments,
                    timeout=30
                )
                
                response_time = time.time() - op_start_time
                
                return {
                    'success': success,
                    'response_time': response_time,
                    'timeout': False,
                    'error': error if not success else None
                }
                
            except Exception as e:
                response_time = time.time() - op_start_time
                return {
                    'success': False,
                    'response_time': response_time,
                    'timeout': response_time >= 30,
                    'error': str(e)
                }

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit operations and collect results until duration is reached
            future_to_operation = {}
            
            for operation in operations:
                if time.time() - start_time >= duration:
                    break
                    
                future = executor.submit(execute_operation, operation)
                future_to_operation[future] = operation
            
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

    def _test_system_recovery(self) -> Optional[LoadTestResult]:
        """
        Test system recovery after high load

        Returns:
            LoadTestResult for recovery test, or None if test fails
        """
        logger.info("Testing system recovery after high load...")
        
        # First, apply high load
        high_load_config = self.load_levels["high"]
        high_load_result = self._test_load_level("high", high_load_config)
        
        # Wait for system to stabilize
        logger.info("Waiting for system to stabilize...")
        time.sleep(10)
        
        # Test recovery with low load
        recovery_start = time.time()
        low_load_config = self.load_levels["low"]
        recovery_result = self._test_load_level("recovery", low_load_config)
        recovery_time = time.time() - recovery_start
        
        # Check if system recovered
        if recovery_result.load_status in [LoadStatus.NORMAL, LoadStatus.STRESSED]:
            recovery_result.load_status = LoadStatus.RECOVERED
            recovery_result.recovery_time_seconds = recovery_time
            logger.info(f"System recovered in {recovery_time:.2f} seconds")
            return recovery_result
        else:
            logger.warning("System did not recover properly")
            return None

    def _determine_load_status(self, successful_ops: int, failed_ops: int, 
                             timeout_ops: int, degradation: float, 
                             cpu_usage: float, memory_usage: float, 
                             load_level: str) -> LoadStatus:
        """
        Determine the load status based on test results

        Args:
            successful_ops: Number of successful operations
            failed_ops: Number of failed operations
            timeout_ops: Number of timeout operations
            degradation: Performance degradation percentage
            cpu_usage: CPU usage percentage
            memory_usage: Memory usage percentage
            load_level: Current load level

        Returns:
            LoadStatus enum value
        """
        total_ops = successful_ops + failed_ops + timeout_ops
        if total_ops == 0:
            return LoadStatus.FAILING

        success_rate = successful_ops / total_ops

        # Determine status based on success rate, degradation, and resource usage
        if success_rate >= 0.95 and degradation < 20 and cpu_usage < 80:
            return LoadStatus.NORMAL
        elif success_rate >= 0.80 and degradation < 50 and cpu_usage < 90:
            return LoadStatus.STRESSED
        elif success_rate >= 0.60 and degradation < 80:
            return LoadStatus.OVERLOADED
        else:
            return LoadStatus.FAILING

    def _calculate_stability_score(self, successful_ops: int, total_ops: int,
                                 error_rate: float, timeout_rate: float, 
                                 degradation: float) -> float:
        """
        Calculate system stability score

        Args:
            successful_ops: Number of successful operations
            total_ops: Total number of operations
            error_rate: Error rate percentage
            timeout_rate: Timeout rate percentage
            degradation: Performance degradation percentage

        Returns:
            Stability score (0-100)
        """
        if total_ops == 0:
            return 0

        # Base score from success rate
        success_score = (successful_ops / total_ops) * 100
        
        # Penalty for errors and timeouts
        error_penalty = error_rate + timeout_rate
        
        # Penalty for performance degradation
        degradation_penalty = min(degradation / 2, 20)  # Max 20% penalty for degradation
        
        # Calculate final score
        final_score = max(0, success_score - error_penalty - degradation_penalty)
        
        return final_score

    def _calculate_test_suite_results(self) -> LoadHandlingTestSuite:
        """
        Calculate comprehensive test suite results

        Returns:
            LoadHandlingTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()

        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()

        # Count statuses
        normal_count = len([r for r in self.test_results if r.load_status == LoadStatus.NORMAL])
        stressed_count = len([r for r in self.test_results if r.load_status == LoadStatus.STRESSED])
        overloaded_count = len([r for r in self.test_results if r.load_status == LoadStatus.OVERLOADED])
        failing_count = len([r for r in self.test_results if r.load_status == LoadStatus.FAILING])
        recovered_count = len([r for r in self.test_results if r.load_status == LoadStatus.RECOVERED])

        # Calculate throughput metrics
        throughputs = [r.throughput_ops_per_second for r in self.test_results if r.throughput_ops_per_second > 0]
        avg_throughput = statistics.mean(throughputs) if throughputs else 0

        # Calculate system capacity score
        capacity_scores = []
        for result in self.test_results:
            if result.load_status == LoadStatus.NORMAL:
                score = 100
            elif result.load_status == LoadStatus.STRESSED:
                score = 80
            elif result.load_status == LoadStatus.OVERLOADED:
                score = 50
            else:
                score = 0
            
            # Weight by load level
            load_weights = {"low": 1, "medium": 2, "high": 3, "extreme": 4}
            weight = load_weights.get(result.load_level, 1)
            weighted_score = score * weight
            capacity_scores.append(weighted_score)

        capacity_score = statistics.mean(capacity_scores) if capacity_scores else 0

        # Calculate recovery capability score
        recovery_results = [r for r in self.test_results if r.load_status == LoadStatus.RECOVERED]
        if recovery_results:
            recovery_score = 100
        else:
            recovery_score = 0

        # Calculate overall load handling score
        load_handling_score = (capacity_score + recovery_score) / 2

        # Find max sustainable load
        sustainable_loads = []
        for result in self.test_results:
            if result.load_status in [LoadStatus.NORMAL, LoadStatus.STRESSED]:
                sustainable_loads.append(result.concurrent_operations)
        
        max_sustainable_load = max(sustainable_loads) if sustainable_loads else 0

        return LoadHandlingTestSuite(
            total_tests=len(self.test_results),
            successful_tests=normal_count + stressed_count + overloaded_count,
            failed_tests=failing_count,
            normal_load_tests=normal_count,
            stressed_tests=stressed_count,
            overloaded_tests=overloaded_count,
            failing_tests=failing_count,
            recovered_tests=recovered_count,
            average_throughput_ops_per_second=avg_throughput,
            max_sustainable_load=max_sustainable_load,
            system_capacity_score=capacity_score,
            recovery_capability_score=recovery_score,
            load_handling_score=load_handling_score,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )

    def _create_empty_test_suite(self) -> LoadHandlingTestSuite:
        """Create an empty test suite for error cases"""
        return LoadHandlingTestSuite(
            total_tests=0,
            successful_tests=0,
            failed_tests=0,
            normal_load_tests=0,
            stressed_tests=0,
            overloaded_tests=0,
            failing_tests=0,
            recovered_tests=0,
            average_throughput_ops_per_second=0.0,
            max_sustainable_load=0,
            system_capacity_score=0.0,
            recovery_capability_score=0.0,
            load_handling_score=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0
        )

    def save_test_results(self, test_suite: LoadHandlingTestSuite,
                         output_file: str = "load_handling_test_results.json"):
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
                result['load_status'] = result['load_status'].value

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Load handling test results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def generate_test_report(self, test_suite: LoadHandlingTestSuite) -> str:
        """
        Generate a comprehensive test report

        Args:
            test_suite: Test suite results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("LOAD HANDLING TEST REPORT")
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
        report.append(f"System Capacity Score: {test_suite.system_capacity_score:.1f}%")
        report.append(f"Recovery Capability Score: {test_suite.recovery_capability_score:.1f}%")
        report.append(f"Load Handling Score: {test_suite.load_handling_score:.1f}%")
        report.append(f"Average Throughput: {test_suite.average_throughput_ops_per_second:.2f} ops/sec")
        report.append(f"Max Sustainable Load: {test_suite.max_sustainable_load} concurrent operations")
        report.append("")

        # Status distribution
        report.append("STATUS DISTRIBUTION")
        report.append("-" * 40)
        report.append(f"Normal Load Tests: {test_suite.normal_load_tests}")
        report.append(f"Stressed Tests: {test_suite.stressed_tests}")
        report.append(f"Overloaded Tests: {test_suite.overloaded_tests}")
        report.append(f"Failing Tests: {test_suite.failing_tests}")
        report.append(f"Recovered Tests: {test_suite.recovered_tests}")
        report.append("")

        # Detailed results by load level
        report.append("DETAILED RESULTS BY LOAD LEVEL")
        report.append("-" * 40)

        for result in test_suite.test_results:
            status_icon = {
                LoadStatus.NORMAL: "🟢",
                LoadStatus.STRESSED: "🟡",
                LoadStatus.OVERLOADED: "🟠",
                LoadStatus.FAILING: "🔴",
                LoadStatus.RECOVERED: "🟢"
            }[result.load_status]

            report.append(f"{status_icon} {result.load_level.upper()} Load Test")
            report.append(f"    Status: {result.load_status.value}")
            report.append(f"    Concurrent Operations: {result.concurrent_operations}")
            report.append(f"    Duration: {result.duration_seconds}s")
            report.append(f"    Throughput: {result.throughput_ops_per_second:.2f} ops/sec")
            report.append(f"    Success Rate: {result.successful_operations}/{result.total_operations}")
            report.append(f"    Error Rate: {result.error_rate_percent:.1f}%")
            report.append(f"    Timeout Rate: {result.timeout_rate_percent:.1f}%")
            report.append(f"    Average Response Time: {result.average_response_time_ms:.2f}ms")
            report.append(f"    Performance Degradation: {result.performance_degradation_percent:.1f}%")
            report.append(f"    CPU Usage: {result.cpu_usage_percent:.1f}%")
            report.append(f"    Memory Usage: {result.memory_usage_mb:.1f} MB ({result.memory_usage_percent:.1f}%)")
            report.append(f"    System Stability Score: {result.system_stability_score:.1f}%")
            
            if result.recovery_time_seconds:
                report.append(f"    Recovery Time: {result.recovery_time_seconds:.2f}s")
            
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run load handling tests"""
    try:
        logger.info("Starting Load Handling Testing")

        # Initialize tester
        tester = LoadHandlingTester()

        # Run comprehensive load handling tests
        test_suite = tester.test_load_handling()

        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/load_handling_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)

        # Final status
        if test_suite.load_handling_score >= 70:
            logger.info("✅ Load handling testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Load handling testing completed with capacity issues "
                         f"(score: {test_suite.load_handling_score:.1f}%)")
            return False

    except Exception as e:
        logger.error(f"❌ Load handling testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 