#!/usr/bin/env python3
"""
Performance Testing Runner

This script runs all performance testing modules for Task 2.4:
- Response time testing (test_response_times.py)
- Concurrent execution testing (test_concurrent_execution.py)
- Load handling testing (test_load_handling.py)
- Resource usage testing (test_resource_usage.py)

Part of Task 2.4: Performance Testing
"""

import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum

# Import performance testing modules
from test_response_times import ResponseTimeTester, ResponseTimeTestSuite
from test_concurrent_execution import ConcurrentExecutionTester, ConcurrencyTestSuite
from test_load_handling import LoadHandlingTester, LoadHandlingTestSuite
from test_resource_usage import ResourceUsageTester, ResourceUsageTestSuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTestStatus(Enum):
    """Performance test status enumeration"""
    PASSED = "passed"
    PARTIAL = "partial"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class PerformanceTestResult:
    """Result of a performance test module"""
    test_name: str
    status: PerformanceTestStatus
    score: float  # 0-100
    duration_seconds: float
    details: str
    output_file: Optional[str] = None


@dataclass
class PerformanceTestSuite:
    """Complete performance test suite"""
    total_tests: int
    passed_tests: int
    partial_tests: int
    failed_tests: int
    error_tests: int
    overall_score: float
    test_results: List[PerformanceTestResult]
    test_timestamp: datetime
    test_duration_seconds: float
    performance_grade: str  # A, B, C, D, F


class PerformanceTestRunner:
    """Comprehensive performance testing runner"""

    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the performance test runner

        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[PerformanceTestResult] = []
        self.start_time: Optional[datetime] = None

        # Define test modules and their configurations
        self.test_modules = {
            "response_times": {
                "description": "Response Time Testing",
                "tester_class": ResponseTimeTester,
                "test_method": "test_all_tools_response_times",
                "weight": 0.25  # 25% of overall score
            },
            "concurrent_execution": {
                "description": "Concurrent Execution Testing",
                "tester_class": ConcurrentExecutionTester,
                "test_method": "test_concurrent_execution",
                "weight": 0.25  # 25% of overall score
            },
            "load_handling": {
                "description": "Load Handling Testing",
                "tester_class": LoadHandlingTester,
                "test_method": "test_load_handling",
                "weight": 0.25  # 25% of overall score
            },
            "resource_usage": {
                "description": "Resource Usage Testing",
                "tester_class": ResourceUsageTester,
                "test_method": "test_resource_usage",
                "weight": 0.25  # 25% of overall score
            }
        }

    def run_all_performance_tests(self) -> PerformanceTestSuite:
        """
        Run all performance tests

        Returns:
            PerformanceTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive performance testing suite")
        self.start_time = datetime.now()

        # Run each test module
        for test_name, config in self.test_modules.items():
            logger.info(f"Running {config['description']}...")
            result = self._run_single_test(test_name, config)
            self.test_results.append(result)

            # Log progress
            status_icon = {
                PerformanceTestStatus.PASSED: "✅",
                PerformanceTestStatus.PARTIAL: "⚠️",
                PerformanceTestStatus.FAILED: "❌",
                PerformanceTestStatus.ERROR: "💥"
            }[result.status]

            logger.info(f"{status_icon} {test_name}: {result.score:.1f}% - {result.status.value}")

        # Calculate overall test suite results
        test_suite = self._calculate_test_suite_results()

        logger.info(f"Performance testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Overall performance score: {test_suite.overall_score:.1f}% ({test_suite.performance_grade})")

        return test_suite

    def _run_single_test(self, test_name: str, config: Dict) -> PerformanceTestResult:
        """
        Run a single performance test module

        Args:
            test_name: Name of the test module
            config: Test configuration

        Returns:
            PerformanceTestResult with test details
        """
        start_time = time.time()

        try:
            # Initialize tester
            tester_class = config["tester_class"]
            test_method = config["test_method"]
            
            tester = tester_class(mcp_server_path=self.mcp_server_path)
            
            # Run the test
            test_suite = getattr(tester, test_method)()
            
            test_duration = time.time() - start_time

            # Determine score based on test type
            if test_name == "response_times":
                score = test_suite.overall_performance_score
            elif test_name == "concurrent_execution":
                score = test_suite.system_stability_score
            elif test_name == "load_handling":
                score = test_suite.load_handling_score
            elif test_name == "resource_usage":
                score = test_suite.resource_efficiency_score
            else:
                score = 0

            # Determine status
            if score >= 80:
                status = PerformanceTestStatus.PASSED
            elif score >= 60:
                status = PerformanceTestStatus.PARTIAL
            else:
                status = PerformanceTestStatus.FAILED

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/inspector/{test_name}_test_{timestamp}.json"
            tester.save_test_results(test_suite, output_file)

            # Generate details
            details = self._generate_test_details(test_name, test_suite)

            return PerformanceTestResult(
                test_name=test_name,
                status=status,
                score=score,
                duration_seconds=test_duration,
                details=details,
                output_file=output_file
            )

        except Exception as e:
            test_duration = time.time() - start_time
            logger.error(f"Error running {test_name}: {e}")
            
            return PerformanceTestResult(
                test_name=test_name,
                status=PerformanceTestStatus.ERROR,
                score=0,
                duration_seconds=test_duration,
                details=f"Error: {str(e)}"
            )

    def _generate_test_details(self, test_name: str, test_suite) -> str:
        """
        Generate detailed information for a test

        Args:
            test_name: Name of the test
            test_suite: Test suite results

        Returns:
            Detailed information string
        """
        if test_name == "response_times":
            return (f"Response Time Testing: {test_suite.total_tools} tools tested, "
                   f"{test_suite.overall_performance_score:.1f}% performance score, "
                   f"{test_suite.average_response_time_ms:.2f}ms average response time")
        
        elif test_name == "concurrent_execution":
            return (f"Concurrent Execution Testing: {test_suite.total_tests} tests, "
                   f"{test_suite.system_stability_score:.1f}% stability score, "
                   f"{test_suite.average_throughput_ops_per_second:.2f} ops/sec average throughput")
        
        elif test_name == "load_handling":
            return (f"Load Handling Testing: {test_suite.total_tests} tests, "
                   f"{test_suite.load_handling_score:.1f}% load handling score, "
                   f"{test_suite.max_sustainable_load} max sustainable load")
        
        elif test_name == "resource_usage":
            return (f"Resource Usage Testing: {test_suite.total_tools} tools tested, "
                   f"{test_suite.resource_efficiency_score:.1f}% efficiency score, "
                   f"{test_suite.average_cpu_usage_percent:.1f}% average CPU usage")
        
        else:
            return "Test completed"

    def _calculate_test_suite_results(self) -> PerformanceTestSuite:
        """
        Calculate comprehensive test suite results

        Returns:
            PerformanceTestSuite with calculated metrics
        """
        if not self.test_results:
            return self._create_empty_test_suite()

        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()

        # Count statuses
        passed_count = len([r for r in self.test_results if r.status == PerformanceTestStatus.PASSED])
        partial_count = len([r for r in self.test_results if r.status == PerformanceTestStatus.PARTIAL])
        failed_count = len([r for r in self.test_results if r.status == PerformanceTestStatus.FAILED])
        error_count = len([r for r in self.test_results if r.status == PerformanceTestStatus.ERROR])

        # Calculate weighted overall score
        total_weight = 0
        weighted_score = 0

        for result in self.test_results:
            if result.status != PerformanceTestStatus.ERROR:
                weight = self.test_modules[result.test_name]["weight"]
                total_weight += weight
                weighted_score += result.score * weight

        overall_score = weighted_score / total_weight if total_weight > 0 else 0

        # Determine performance grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"

        return PerformanceTestSuite(
            total_tests=len(self.test_results),
            passed_tests=passed_count,
            partial_tests=partial_count,
            failed_tests=failed_count,
            error_tests=error_count,
            overall_score=overall_score,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration,
            performance_grade=grade
        )

    def _create_empty_test_suite(self) -> PerformanceTestSuite:
        """Create an empty test suite for error cases"""
        return PerformanceTestSuite(
            total_tests=0,
            passed_tests=0,
            partial_tests=0,
            failed_tests=0,
            error_tests=0,
            overall_score=0.0,
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0.0,
            performance_grade="F"
        )

    def save_test_results(self, test_suite: PerformanceTestSuite,
                         output_file: str = "performance_test_results.json"):
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
                result['status'] = result['status'].value

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Performance test results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

    def generate_test_report(self, test_suite: PerformanceTestSuite) -> str:
        """
        Generate a comprehensive test report

        Args:
            test_suite: Test suite results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE TESTING SUITE REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")

        # Overall summary
        report.append("OVERALL SUMMARY")
        report.append("-" * 40)
        report.append(f"Overall Performance Score: {test_suite.overall_score:.1f}%")
        report.append(f"Performance Grade: {test_suite.performance_grade}")
        report.append(f"Total Tests: {test_suite.total_tests}")
        report.append(f"Passed Tests: {test_suite.passed_tests}")
        report.append(f"Partial Tests: {test_suite.partial_tests}")
        report.append(f"Failed Tests: {test_suite.failed_tests}")
        report.append(f"Error Tests: {test_suite.error_tests}")
        report.append("")

        # Test results summary
        report.append("TEST RESULTS SUMMARY")
        report.append("-" * 40)

        for result in test_suite.test_results:
            status_icon = {
                PerformanceTestStatus.PASSED: "✅",
                PerformanceTestStatus.PARTIAL: "⚠️",
                PerformanceTestStatus.FAILED: "❌",
                PerformanceTestStatus.ERROR: "💥"
            }[result.status]

            test_name = self.test_modules[result.test_name]["description"]
            weight = self.test_modules[result.test_name]["weight"] * 100

            report.append(f"{status_icon} {test_name}")
            report.append(f"    Score: {result.score:.1f}% (Weight: {weight:.0f}%)")
            report.append(f"    Status: {result.status.value}")
            report.append(f"    Duration: {result.duration_seconds:.2f}s")
            report.append(f"    Details: {result.details}")
            if result.output_file:
                report.append(f"    Output: {result.output_file}")
            report.append("")

        # Performance recommendations
        report.append("PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 40)

        if test_suite.overall_score >= 90:
            report.append("🎉 Excellent performance! The system is performing optimally.")
            report.append("   Continue monitoring for any degradation over time.")
        elif test_suite.overall_score >= 80:
            report.append("👍 Good performance with room for improvement.")
            report.append("   Consider optimizing areas with lower scores.")
        elif test_suite.overall_score >= 70:
            report.append("⚠️ Acceptable performance but needs attention.")
            report.append("   Focus on improving failed and partial tests.")
        elif test_suite.overall_score >= 60:
            report.append("🔧 Performance needs significant improvement.")
            report.append("   Prioritize fixing failed tests and optimizing bottlenecks.")
        else:
            report.append("🚨 Critical performance issues detected.")
            report.append("   Immediate attention required for all failed tests.")

        # Specific recommendations based on test results
        for result in test_suite.test_results:
            if result.status in [PerformanceTestStatus.FAILED, PerformanceTestStatus.PARTIAL]:
                if result.test_name == "response_times":
                    report.append(f"   • Optimize response times for slow tools")
                elif result.test_name == "concurrent_execution":
                    report.append(f"   • Improve system stability under concurrent load")
                elif result.test_name == "load_handling":
                    report.append(f"   • Enhance system capacity and recovery capabilities")
                elif result.test_name == "resource_usage":
                    report.append(f"   • Optimize resource usage and fix memory leaks")

        report.append("")

        return "\n".join(report)


def main():
    """Main function to run all performance tests"""
    try:
        logger.info("Starting Performance Testing Suite")

        # Initialize runner
        runner = PerformanceTestRunner()

        # Run all performance tests
        test_suite = runner.run_all_performance_tests()

        # Generate and print report
        report = runner.generate_test_report(test_suite)
        print(report)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/inspector/performance_test_suite_{timestamp}.json"
        runner.save_test_results(test_suite, output_file)

        # Final status
        if test_suite.overall_score >= 80:
            logger.info("✅ Performance testing suite completed successfully!")
            return True
        elif test_suite.overall_score >= 60:
            logger.warning(f"⚠️ Performance testing suite completed with issues "
                         f"(score: {test_suite.overall_score:.1f}%)")
            return True
        else:
            logger.error(f"❌ Performance testing suite completed with critical issues "
                        f"(score: {test_suite.overall_score:.1f}%)")
            return False

    except Exception as e:
        logger.error(f"❌ Performance testing suite failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 