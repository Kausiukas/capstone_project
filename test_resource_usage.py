#!/usr/bin/env python3
"""
Resource Usage Testing Module

This module implements comprehensive resource usage testing for the MCP server.
It monitors memory usage, tracks CPU usage, monitors network usage, and
detects resource leaks during tool execution.

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
import psutil
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import Inspector CLI utilities
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """Resource usage status enumeration"""
    NORMAL = "normal"           # Resource usage within normal limits
    ELEVATED = "elevated"       # Resource usage elevated but acceptable
    HIGH = "high"              # Resource usage high, monitor closely
    CRITICAL = "critical"       # Resource usage critical, potential issues
    LEAK_DETECTED = "leak_detected"  # Resource leak detected


@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    threads: int


@dataclass
class ResourceUsageResult:
    """Result of resource usage monitoring for a tool"""
    tool_name: str
    test_duration_seconds: float
    initial_snapshot: ResourceSnapshot
    final_snapshot: ResourceSnapshot
    peak_snapshot: ResourceSnapshot
    average_cpu_percent: float
    average_memory_mb: float
    average_memory_percent: float
    memory_growth_mb: float
    memory_growth_percent: float
    cpu_usage_trend: str  # "stable", "increasing", "decreasing", "fluctuating"
    memory_usage_trend: str  # "stable", "increasing", "decreasing", "fluctuating"
    resource_status: ResourceStatus
    potential_leak: bool
    leak_confidence: float  # 0-100, confidence in leak detection
    snapshots: List[ResourceSnapshot]


@dataclass
class ResourceUsageTestSuite:
    """Complete resource usage test suite"""
    total_tools: int
    successful_tests: int
    failed_tests: int
    normal_resource_usage: int
    elevated_resource_usage: int
    high_resource_usage: int
    critical_resource_usage: int
    leak_detected: int
    average_cpu_usage_percent: float
    average_memory_usage_mb: float
    average_memory_growth_mb: float
    max_memory_usage_mb: float
    max_cpu_usage_percent: float
    resource_efficiency_score: float  # 0-100
    leak_detection_score: float  # 0-100
    test_results: List[ResourceUsageResult]
    test_timestamp: datetime
    test_duration_seconds: float


class ResourceUsageTester:
    """Comprehensive resource usage testing system"""

    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the resource usage tester

        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ResourceUsageResult] = []
        self.start_time: Optional[datetime] = None
        self.monitoring_interval = 0.5  # Monitor every 0.5 seconds
        self.monitoring_thread = None
        self.stop_monitoring = False

        # Resource thresholds
        self.resource_thresholds = {
            "cpu_normal": 50,      # CPU usage below 50% is normal
            "cpu_elevated": 70,    # CPU usage 50-70% is elevated
            "cpu_high": 85,        # CPU usage 70-85% is high
            "memory_normal": 60,   # Memory usage below 60% is normal
            "memory_elevated": 75, # Memory usage 60-75% is elevated
            "memory_high": 85,     # Memory usage 75-85% is high
            "memory_growth_threshold": 50,  # 50MB growth threshold for leak detection
            "memory_growth_percent_threshold": 10  # 10% growth threshold for leak detection
        }

        # Test tools for resource monitoring
        self.test_tools = [
            "ping",  # Light resource usage
            "read_file",  # Medium resource usage
            "list_files",  # Medium resource usage
            "analyze_code",  # Higher resource usage
            "store_embedding",  # Variable resource usage
            "similarity_search",  # Higher resource usage
            "process_text_with_llm"  # Highest resource usage
        ]

        # Test arguments for each tool
        self.test_arguments = {
            "ping": {},
            "read_file": {"file_path": "README.md"},
            "list_files": {"directory": ".", "batch_size": 10},
            "analyze_code": {"file_path": "README.md"},
            "store_embedding": {"name": "test_embedding", "content": "Test content for resource monitoring"},
            "similarity_search": {"query": "test query", "limit": 5},
            "process_text_with_llm": {"text": "Test text for resource monitoring", "task": "summarize"}
        }

    def test_resource_usage(self) -> ResourceUsageTestSuite:
        """
        Test resource usage for all tools

        Returns:
            ResourceUsageTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive resource usage testing")
        self.start_time = datetime.now()

        # Get list of all tools first
        tools_list = inspector_cli.get_tools_list(self.mcp_server_path)
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with resource usage testing")
            return self._create_empty_test_suite()

        logger.info(f"Found {len(tools_list)} tools to test for resource usage")

        # Test each tool's resource usage
        for tool_name in tools_list:
            if tool_name in self.test_tools:
                logger.info(f"Testing resource usage for tool: {tool_name}")
                result = self._test_tool_resource_usage(tool_name)
                self.test_results.append(result)

                # Log progress
                status_icon = {
                    ResourceStatus.NORMAL: "🟢",
                    ResourceStatus.ELEVATED: "🟡",
                    ResourceStatus.HIGH: "🟠",
                    ResourceStatus.CRITICAL: "🔴",
                    ResourceStatus.LEAK_DETECTED: "💥"
                }[result.resource_status]

                logger.info(f"{status_icon} {tool_name}: "
                           f"CPU {result.average_cpu_percent:.1f}%, "
                           f"Memory {result.average_memory_mb:.1f}MB, "
                           f"{result.resource_status.value}")

        # Calculate overall test suite results
        test_suite = self._calculate_test_suite_results()

        logger.info(f"Resource usage testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Resource efficiency score: {test_suite.resource_efficiency_score:.1f}%")

        return test_suite

    def _test_tool_resource_usage(self, tool_name: str) -> ResourceUsageResult:
        """
        Test resource usage for a specific tool

        Args:
            tool_name: Name of the tool to test

        Returns:
            ResourceUsageResult with resource usage details
        """
        # Initialize monitoring
        snapshots = []
        self.stop_monitoring = False
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(
            target=self._monitor_resources,
            args=(snapshots,)
        )
        monitoring_thread.start()

        # Take initial snapshot
        initial_snapshot = self._take_resource_snapshot()
        snapshots.append(initial_snapshot)

        # Execute the tool
        start_time = time.time()
        try:
            arguments = self.test_arguments.get(tool_name, {})
            success, response, error = inspector_cli.execute_tool(
                mcp_server_path=self.mcp_server_path,
                tool_name=tool_name,
                arguments=arguments,
                timeout=30
            )
        except Exception as e:
            error = str(e)
            success = False

        test_duration = time.time() - start_time

        # Stop monitoring and wait for thread to finish
        self.stop_monitoring = True
        monitoring_thread.join(timeout=5)

        # Take final snapshot
        final_snapshot = self._take_resource_snapshot()
        snapshots.append(final_snapshot)

        # Analyze resource usage
        result = self._analyze_resource_usage(
            tool_name, test_duration, initial_snapshot, final_snapshot, snapshots
        )

        return result

    def _monitor_resources(self, snapshots: List[ResourceSnapshot]):
        """
        Monitor system resources in a separate thread

        Args:
            snapshots: List to store resource snapshots
        """
        while not self.stop_monitoring:
            snapshot = self._take_resource_snapshot()
            snapshots.append(snapshot)
            time.sleep(self.monitoring_interval)

    def _take_resource_snapshot(self) -> ResourceSnapshot:
        """
        Take a snapshot of current system resources

        Returns:
            ResourceSnapshot with current resource usage
        """
        process = psutil.Process(os.getpid())
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        
        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = psutil.virtual_memory().percent
        
        # Disk I/O
        try:
            disk_io = process.io_counters()
            disk_io_read_mb = disk_io.read_bytes / 1024 / 1024
            disk_io_write_mb = disk_io.write_bytes / 1024 / 1024
        except psutil.AccessDenied:
            disk_io_read_mb = disk_io_write_mb = 0
        
        # Network I/O
        try:
            network_io = process.io_counters()
            network_sent_mb = network_io.write_bytes / 1024 / 1024
            network_recv_mb = network_io.read_bytes / 1024 / 1024
        except psutil.AccessDenied:
            network_sent_mb = network_recv_mb = 0
        
        # Open files and threads
        try:
            open_files = len(process.open_files())
        except psutil.AccessDenied:
            open_files = 0
        
        try:
            threads = process.num_threads()
        except psutil.AccessDenied:
            threads = 0

        return ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            open_files=open_files,
            threads=threads
        )

    def _analyze_resource_usage(self, tool_name: str, test_duration: float,
                              initial_snapshot: ResourceSnapshot, 
                              final_snapshot: ResourceSnapshot,
                              snapshots: List[ResourceSnapshot]) -> ResourceUsageResult:
        """
        Analyze resource usage from snapshots

        Args:
            tool_name: Name of the tool tested
            test_duration: Duration of the test
            initial_snapshot: Initial resource snapshot
            final_snapshot: Final resource snapshot
            snapshots: List of all snapshots during test

        Returns:
            ResourceUsageResult with analysis
        """
        # Calculate averages
        cpu_values = [s.cpu_percent for s in snapshots]
        memory_values = [s.memory_mb for s in snapshots]
        memory_percent_values = [s.memory_percent for s in snapshots]

        avg_cpu = statistics.mean(cpu_values) if cpu_values else 0
        avg_memory = statistics.mean(memory_values) if memory_values else 0
        avg_memory_percent = statistics.mean(memory_percent_values) if memory_percent_values else 0

        # Calculate memory growth
        memory_growth_mb = final_snapshot.memory_mb - initial_snapshot.memory_mb
        memory_growth_percent = ((final_snapshot.memory_mb - initial_snapshot.memory_mb) / 
                                initial_snapshot.memory_mb * 100) if initial_snapshot.memory_mb > 0 else 0

        # Find peak snapshot
        peak_snapshot = max(snapshots, key=lambda s: s.memory_mb + s.cpu_percent)

        # Analyze trends
        cpu_trend = self._analyze_trend(cpu_values)
        memory_trend = self._analyze_trend(memory_values)

        # Determine resource status
        resource_status = self._determine_resource_status(
            avg_cpu, avg_memory_percent, memory_growth_mb, memory_growth_percent
        )

        # Detect potential leaks
        potential_leak, leak_confidence = self._detect_resource_leak(
            snapshots, memory_growth_mb, memory_growth_percent
        )

        return ResourceUsageResult(
            tool_name=tool_name,
            test_duration_seconds=test_duration,
            initial_snapshot=initial_snapshot,
            final_snapshot=final_snapshot,
            peak_snapshot=peak_snapshot,
            average_cpu_percent=avg_cpu,
            average_memory_mb=avg_memory,
            average_memory_percent=avg_memory_percent,
            memory_growth_mb=memory_growth_mb,
            memory_growth_percent=memory_growth_percent,
            cpu_usage_trend=cpu_trend,
            memory_usage_trend=memory_trend,
            resource_status=resource_status,
            potential_leak=potential_leak,
            leak_confidence=leak_confidence,
            snapshots=snapshots
        )

    def _analyze_trend(self, values: List[float]) -> str:
        """
        Analyze trend in a list of values

        Args:
            values: List of numeric values

        Returns:
            Trend description
        """
        if len(values) < 3:
            return "stable"

        # Calculate trend using linear regression
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "stable"
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine trend based on slope
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0.1:
            return "increasing"
        else:
            return "decreasing"

    def _determine_resource_status(self, avg_cpu: float, avg_memory_percent: float,
                                 memory_growth_mb: float, memory_growth_percent: float) -> ResourceStatus:
        """
        Determine resource status based on usage metrics

        Args:
            avg_cpu: Average CPU usage percentage
            avg_memory_percent: Average memory usage percentage
            memory_growth_mb: Memory growth in MB
            memory_growth_percent: Memory growth percentage

        Returns:
            ResourceStatus enum value
        """
        # Check for resource leaks first
        if (memory_growth_mb > self.resource_thresholds["memory_growth_threshold"] or
            memory_growth_percent > self.resource_thresholds["memory_growth_percent_threshold"]):
            return ResourceStatus.LEAK_DETECTED

        # Check CPU usage
        if avg_cpu > self.resource_thresholds["cpu_high"]:
            return ResourceStatus.CRITICAL
        elif avg_cpu > self.resource_thresholds["cpu_elevated"]:
            return ResourceStatus.HIGH
        elif avg_cpu > self.resource_thresholds["cpu_normal"]:
            return ResourceStatus.ELEVATED

        # Check memory usage
        if avg_memory_percent > self.resource_thresholds["memory_high"]:
            return ResourceStatus.CRITICAL
        elif avg_memory_percent > self.resource_thresholds["memory_elevated"]:
            return ResourceStatus.HIGH
        elif avg_memory_percent > self.resource_thresholds["memory_normal"]:
            return ResourceStatus.ELEVATED

        return ResourceStatus.NORMAL

    def _detect_resource_leak(self, snapshots: List[ResourceSnapshot],
                            memory_growth_mb: float, memory_growth_percent: float) -> Tuple[bool, float]:
        """
        Detect potential resource leaks

        Args:
            snapshots: List of resource snapshots
            memory_growth_mb: Memory growth in MB
            memory_growth_percent: Memory growth percentage

        Returns:
            Tuple of (potential_leak, confidence)
        """
        if len(snapshots) < 5:
            return False, 0

        # Check for continuous memory growth
        memory_values = [s.memory_mb for s in snapshots]
        memory_trend = self._analyze_trend(memory_values)

        # Calculate confidence based on multiple factors
        confidence = 0

        # Memory growth factor
        if memory_growth_mb > self.resource_thresholds["memory_growth_threshold"]:
            confidence += 30
        if memory_growth_percent > self.resource_thresholds["memory_growth_percent_threshold"]:
            confidence += 30

        # Trend factor
        if memory_trend == "increasing":
            confidence += 25
        elif memory_trend == "stable":
            confidence += 10

        # Check for non-releasing memory
        if memory_growth_mb > 0 and memory_growth_percent > 5:
            confidence += 15

        potential_leak = confidence >= 50

        return potential_leak, min(confidence, 100)

    def _calculate_test_suite_results(self) -> ResourceUsageTestSuite:
        """
        Calculate comprehensive test suite results

        Returns:
            ResourceUsageTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()

        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()

        # Count statuses
        normal_count = len([r for r in self.test_results if r.resource_status == ResourceStatus.NORMAL])
        elevated_count = len([r for r in self.test_results if r.resource_status == ResourceStatus.ELEVATED])
        high_count = len([r for r in self.test_results if r.resource_status == ResourceStatus.HIGH])
        critical_count = len([r for r in self.test_results if r.resource_status == ResourceStatus.CRITICAL])
        leak_count = len([r for r in self.test_results if r.resource_status == ResourceStatus.LEAK_DETECTED])

        # Calculate averages
        avg_cpu = statistics.mean([r.average_cpu_percent for r in self.test_results])
        avg_memory = statistics.mean([r.average_memory_mb for r in self.test_results])
        avg_memory_growth = statistics.mean([r.memory_growth_mb for r in self.test_results])

        # Find maximums
        max_memory = max([r.peak_snapshot.memory_mb for r in self.test_results])
        max_cpu = max([r.peak_snapshot.cpu_percent for r in self.test_results])

        # Calculate resource efficiency score
        efficiency_scores = []
        for result in self.test_results:
            if result.resource_status == ResourceStatus.NORMAL:
                score = 100
            elif result.resource_status == ResourceStatus.ELEVATED:
                score = 80
            elif result.resource_status == ResourceStatus.HIGH:
                score = 60
            elif result.resource_status == ResourceStatus.CRITICAL:
                score = 30
            else:
                score = 0

            # Penalty for memory growth
            growth_penalty = min(result.memory_growth_mb / 10, 20)  # Max 20% penalty
            final_score = max(0, score - growth_penalty)
            efficiency_scores.append(final_score)

        efficiency_score = statistics.mean(efficiency_scores) if efficiency_scores else 0

        # Calculate leak detection score
        leak_detection_scores = []
        for result in self.test_results:
            if result.potential_leak:
                score = result.leak_confidence
            else:
                score = 100  # No leak detected is good
            leak_detection_scores.append(score)

        leak_detection_score = statistics.mean(leak_detection_scores) if leak_detection_scores else 0

        return ResourceUsageTestSuite(
            total_tools=len(self.test_results),
            successful_tests=normal_count + elevated_count,
            failed_tests=high_count + critical_count + leak_count,
            normal_resource_usage=normal_count,
            elevated_resource_usage=elevated_count,
            high_resource_usage=high_count,
            critical_resource_usage=critical_count,
            leak_detected=leak_count,
            average_cpu_usage_percent=avg_cpu,
            average_memory_usage_mb=avg_memory,
            average_memory_growth_mb=avg_memory_growth,
            max_memory_usage_mb=max_memory,
            max_cpu_usage_percent=max_cpu,
            resource_efficiency_score=efficiency_score,
            leak_detection_score=leak_detection_score,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )

    def _create_empty_test_suite(self) -> ResourceUsageTestSuite:
        """Create an empty test suite for error cases"""
        return ResourceUsageTestSuite(
            total_tools=0,
            successful_tests=0,
            failed_tests=0,
            normal_resource_usage=0,
            elevated_resource_usage=0,
            high_resource_usage=0,
            critical_resource_usage=0,
            leak_detected=0,
            average_cpu_usage_percent=0.0,
            average_memory_usage_mb=0.0,
            average_memory_growth_mb=0.0,
            max_memory_usage_mb=0.0,
            max_cpu_usage_percent=0.0,
            resource_efficiency_score=0.0,
            leak_detection_score=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0
        )

    def save_test_results(self, test_suite: ResourceUsageTestSuite,
                         output_file: str = "resource_usage_test_results.json"):
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
                result['resource_status'] = result['resource_status'].value

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Resource usage test results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def generate_test_report(self, test_suite: ResourceUsageTestSuite) -> str:
        """
        Generate a comprehensive test report

        Args:
            test_suite: Test suite results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("RESOURCE USAGE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")

        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Successful Tests: {test_suite.successful_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests}")
        report.append(f"Resource Efficiency Score: {test_suite.resource_efficiency_score:.1f}%")
        report.append(f"Leak Detection Score: {test_suite.leak_detection_score:.1f}%")
        report.append(f"Average CPU Usage: {test_suite.average_cpu_usage_percent:.1f}%")
        report.append(f"Average Memory Usage: {test_suite.average_memory_usage_mb:.1f} MB")
        report.append(f"Average Memory Growth: {test_suite.average_memory_growth_mb:.1f} MB")
        report.append(f"Max Memory Usage: {test_suite.max_memory_usage_mb:.1f} MB")
        report.append(f"Max CPU Usage: {test_suite.max_cpu_usage_percent:.1f}%")
        report.append("")

        # Status distribution
        report.append("STATUS DISTRIBUTION")
        report.append("-" * 40)
        report.append(f"Normal Resource Usage: {test_suite.normal_resource_usage}")
        report.append(f"Elevated Resource Usage: {test_suite.elevated_resource_usage}")
        report.append(f"High Resource Usage: {test_suite.high_resource_usage}")
        report.append(f"Critical Resource Usage: {test_suite.critical_resource_usage}")
        report.append(f"Resource Leaks Detected: {test_suite.leak_detected}")
        report.append("")

        # Detailed results by tool
        report.append("DETAILED RESULTS BY TOOL")
        report.append("-" * 40)

        for result in test_suite.test_results:
            status_icon = {
                ResourceStatus.NORMAL: "🟢",
                ResourceStatus.ELEVATED: "🟡",
                ResourceStatus.HIGH: "🟠",
                ResourceStatus.CRITICAL: "🔴",
                ResourceStatus.LEAK_DETECTED: "💥"
            }[result.resource_status]

            report.append(f"{status_icon} {result.tool_name}")
            report.append(f"    Status: {result.resource_status.value}")
            report.append(f"    Test Duration: {result.test_duration_seconds:.2f}s")
            report.append(f"    Average CPU: {result.average_cpu_percent:.1f}%")
            report.append(f"    Average Memory: {result.average_memory_mb:.1f} MB ({result.average_memory_percent:.1f}%)")
            report.append(f"    Memory Growth: {result.memory_growth_mb:.1f} MB ({result.memory_growth_percent:.1f}%)")
            report.append(f"    CPU Trend: {result.cpu_usage_trend}")
            report.append(f"    Memory Trend: {result.memory_usage_trend}")
            
            if result.potential_leak:
                report.append(f"    ⚠️ Potential Leak: {result.leak_confidence:.1f}% confidence")
            
            report.append(f"    Peak CPU: {result.peak_snapshot.cpu_percent:.1f}%")
            report.append(f"    Peak Memory: {result.peak_snapshot.memory_mb:.1f} MB")
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run resource usage tests"""
    try:
        logger.info("Starting Resource Usage Testing")

        # Initialize tester
        tester = ResourceUsageTester()

        # Run comprehensive resource usage tests
        test_suite = tester.test_resource_usage()

        # Generate and print report
        report = tester.generate_test_report(test_suite)
        print(report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/resource_usage_test_{timestamp}.json"
        tester.save_test_results(test_suite, output_file)

        # Final status
        if test_suite.resource_efficiency_score >= 70:
            logger.info("✅ Resource usage testing completed successfully!")
            return True
        else:
            logger.warning(f"⚠️ Resource usage testing completed with efficiency issues "
                         f"(score: {test_suite.resource_efficiency_score:.1f}%)")
            return False

    except Exception as e:
        logger.error(f"❌ Resource usage testing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 