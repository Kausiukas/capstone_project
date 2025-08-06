#!/usr/bin/env python3
"""
Base Test Runner with Progress Tracking

This module provides a base class for all test runners with integrated progress tracking,
timeout detection, and status monitoring capabilities.

Reusable across all Inspector test modules.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce log level to prevent progress bar interference
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test status"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    RUNNING = "running"
    TIMEOUT = "timeout"

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_description: str
    status: TestStatus
    execution_time_ms: float
    details: str
    error_message: Optional[str] = None
    timestamp: datetime = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class TestSuite:
    """Test suite results"""
    suite_name: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    timeout_tests: int = 0
    overall_score: float = 0.0
    test_results: List[TestResult] = None
    summary: str = ""
    recommendations: List[str] = None
    timestamp: datetime = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_execution_time: float = 0.0
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
        if self.recommendations is None:
            self.recommendations = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def add_result(self, result: TestResult) -> None:
        """Add a test result to the suite"""
        self.test_results.append(result)
        self.total_tests += 1
        
        if result.status == TestStatus.PASSED:
            self.passed_tests += 1
        elif result.status == TestStatus.FAILED:
            self.failed_tests += 1
        elif result.status == TestStatus.ERROR:
            self.error_tests += 1
        elif result.status == TestStatus.SKIPPED:
            self.skipped_tests += 1
        elif result.status == TestStatus.TIMEOUT:
            self.timeout_tests += 1
        
        # Calculate overall score
        if self.total_tests > 0:
            self.overall_score = (self.passed_tests / self.total_tests) * 100

class ProgressTracker:
    """Progress tracking system with timeout detection and status monitoring"""
    
    def __init__(self, total_tests: int, timeout_seconds: int = 300):
        self.total_tests = total_tests
        self.completed_tests = 0
        self.current_test = ""
        self.start_time = datetime.now()
        self.timeout_seconds = timeout_seconds
        self.test_start_times: Dict[str, datetime] = {}
        self.test_timeouts: Dict[str, int] = {}
        self.last_progress_update = datetime.now()
        self.progress_update_interval = 2.0  # Update progress every 2 seconds
        
    def start_test(self, test_name: str, timeout_seconds: int = 60) -> None:
        """Start tracking a test"""
        self.current_test = test_name
        self.test_start_times[test_name] = datetime.now()
        self.test_timeouts[test_name] = timeout_seconds
        self._update_progress()
        
    def complete_test(self, test_name: str) -> None:
        """Mark a test as completed"""
        self.completed_tests += 1
        self.current_test = ""
        if test_name in self.test_start_times:
            del self.test_start_times[test_name]
        self._update_progress()
        
    def get_progress_info(self) -> Dict[str, Any]:
        """Get current progress information"""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        progress_percent = (self.completed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        # Calculate estimated completion time
        if self.completed_tests > 0:
            avg_time_per_test = elapsed_time / self.completed_tests
            remaining_tests = self.total_tests - self.completed_tests
            estimated_remaining = avg_time_per_test * remaining_tests
            estimated_completion = datetime.now() + timedelta(seconds=estimated_remaining)
        else:
            estimated_completion = None
            estimated_remaining = 0
            
        # Check for potential timeouts
        timeout_warnings = []
        for test_name, start_time in self.test_start_times.items():
            test_elapsed = (datetime.now() - start_time).total_seconds()
            timeout_limit = self.test_timeouts.get(test_name, 60)
            if test_elapsed > timeout_limit:
                timeout_warnings.append(f"{test_name}: {test_elapsed:.1f}s (timeout: {timeout_limit}s)")
            elif test_elapsed > timeout_limit * 0.8:
                timeout_warnings.append(f"{test_name}: {test_elapsed:.1f}s (approaching timeout: {timeout_limit}s)")
        
        return {
            'completed': self.completed_tests,
            'total': self.total_tests,
            'progress_percent': progress_percent,
            'elapsed_time': elapsed_time,
            'current_test': self.current_test,
            'estimated_completion': estimated_completion,
            'estimated_remaining': estimated_remaining,
            'timeout_warnings': timeout_warnings,
            'is_stuck': self._detect_stuck_condition()
        }
        
    def _detect_stuck_condition(self) -> bool:
        """Detect if tests appear to be stuck"""
        if not self.current_test:
            return False
            
        # Check if current test has been running too long
        if self.current_test in self.test_start_times:
            test_elapsed = (datetime.now() - self.test_start_times[self.current_test]).total_seconds()
            timeout_limit = self.test_timeouts.get(self.current_test, 60)
            return test_elapsed > timeout_limit * 1.5
            
        return False
        
    def _update_progress(self) -> None:
        """Update progress display"""
        now = datetime.now()
        if (now - self.last_progress_update).total_seconds() >= self.progress_update_interval:
            self._print_progress()
            self.last_progress_update = now
            
        # Force a periodic update to ensure visibility
        if hasattr(self, '_last_force_update'):
            if time.time() - self._last_force_update > 2.0:  # Every 2 seconds
                print(f"\rProgress: {self.completed_tests}/{self.total_tests} tests completed", end="", flush=True)
                self._last_force_update = time.time()
        else:
            self._last_force_update = time.time()
            
    def _print_progress(self) -> None:
        """Print current progress"""
        info = self.get_progress_info()
        
        # Clear the line first to ensure visibility
        print(f"\r{' ' * 150}", end="", flush=True)
        
        # Create progress bar with simpler characters for better compatibility
        bar_length = 40
        filled_length = int(bar_length * info['progress_percent'] / 100)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        
        # Format time
        elapsed_str = self._format_time(info['elapsed_time'])
        remaining_str = self._format_time(info['estimated_remaining']) if info['estimated_remaining'] > 0 else "N/A"
        
        # Status indicators
        status_indicators = []
        if info['timeout_warnings']:
            status_indicators.append("TIMEOUT WARNINGS")
        if info['is_stuck']:
            status_indicators.append("STUCK")
        if info['current_test']:
            status_indicators.append("RUNNING")
            
        status_str = " | ".join(status_indicators) if status_indicators else "NORMAL"
        
        # Print progress with better formatting
        progress_line = f"\r[{bar}] {info['progress_percent']:5.1f}% | Tests: {info['completed']}/{info['total']} | Time: {elapsed_str} | ETA: {remaining_str} | Status: {status_str}"
        
        if info['current_test']:
            progress_line += f" | Current: {info['current_test']}"
            
        print(progress_line, end="", flush=True)
        
        # Print timeout warnings on new lines
        if info['timeout_warnings']:
            print()
            for warning in info['timeout_warnings']:
                print(f"  WARNING: {warning}")
                
    def _format_time(self, seconds: float) -> str:
        """Format time in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
            
    def finalize(self) -> None:
        """Finalize progress tracking"""
        print()  # New line after progress bar
        info = self.get_progress_info()
        print(f"\n" + "="*80)
        print(f"TEST EXECUTION COMPLETED in {self._format_time(info['elapsed_time'])}")
        print(f"Total tests: {info['total']}, Completed: {info['completed']}")
        print("="*80)

class BaseTestRunner:
    """Base class for all test runners with progress tracking capabilities"""
    
    def __init__(self, suite_name: str, total_tests: int, timeout_seconds: int = 600):
        self.suite_name = suite_name
        self.test_suite = TestSuite(suite_name=suite_name)
        self.progress_tracker = ProgressTracker(total_tests, timeout_seconds)
        self.reports_dir = Path("reports/test_runs")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_test(self, test_name: str, test_description: str, test_function: Callable, timeout_seconds: int = 120) -> None:
        """Run a single test with progress tracking and timeout detection"""
        start_time = datetime.now()
        
        # Start progress tracking for this test
        self.progress_tracker.start_test(test_name, timeout_seconds)
        
        # Print initial progress to ensure visibility
        print(f"\nStarting test: {test_name}")
        print("Progress tracking initialized...")
        
        try:
            logger.info(f"Running test: {test_name}")
            
            # Run test with timeout
            await asyncio.wait_for(test_function(), timeout=timeout_seconds)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = TestResult(
                test_name=test_name,
                test_description=test_description,
                status=TestStatus.PASSED,
                execution_time_ms=execution_time,
                details=f"Test {test_name} completed successfully",
                start_time=start_time,
                end_time=datetime.now()
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = TestResult(
                test_name=test_name,
                test_description=test_description,
                status=TestStatus.TIMEOUT,
                execution_time_ms=execution_time,
                details=f"Test {test_name} timed out after {timeout_seconds} seconds",
                error_message="Test execution exceeded timeout limit",
                start_time=start_time,
                end_time=datetime.now()
            )
            
            logger.error(f"Test {test_name} timed out after {timeout_seconds} seconds")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = TestResult(
                test_name=test_name,
                test_description=test_description,
                status=TestStatus.FAILED,
                execution_time_ms=execution_time,
                details=f"Test {test_name} failed",
                error_message=str(e),
                start_time=start_time,
                end_time=datetime.now()
            )
            
            logger.error(f"Test {test_name} failed: {e}")
        
        # Complete progress tracking for this test
        self.progress_tracker.complete_test(test_name)
        
        self.test_suite.add_result(result)
        
    def generate_summary(self) -> None:
        """Generate test summary"""
        execution_time_str = self._format_time(self.test_suite.total_execution_time) if self.test_suite.total_execution_time > 0 else "N/A"
        
        self.test_suite.summary = f"""
{self.suite_name} Test Suite Summary

Overall Test Score: {self.test_suite.overall_score:.1f}%
Total Execution Time: {execution_time_str}

Total Tests: {self.test_suite.total_tests}
- Passed: {self.test_suite.passed_tests}
- Failed: {self.test_suite.failed_tests}
- Errors: {self.test_suite.error_tests}
- Skipped: {self.test_suite.skipped_tests}
- Timeouts: {self.test_suite.timeout_tests}

Test Results:
"""
        
        for result in self.test_suite.test_results:
            if result.status == TestStatus.PASSED:
                status_icon = "✅"
            elif result.status == TestStatus.FAILED:
                status_icon = "❌"
            elif result.status == TestStatus.TIMEOUT:
                status_icon = "⏰"
            elif result.status == TestStatus.ERROR:
                status_icon = "💥"
            else:
                status_icon = "⚠️"
                
            self.test_suite.summary += f"{status_icon} {result.test_name}: {result.status.value} ({result.execution_time_ms:.1f}ms)\n"
        
        self.test_suite.summary += f"""
Test suite completed at: {self.test_suite.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()
        
    def generate_recommendations(self) -> None:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failed tests
        failed_tests = [r for r in self.test_suite.test_results if r.status == TestStatus.FAILED]
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed tests")
            for test in failed_tests:
                recommendations.append(f"Fix {test.test_name}: {test.error_message}")
        
        # Analyze timeout tests
        timeout_tests = [r for r in self.test_suite.test_results if r.status == TestStatus.TIMEOUT]
        if timeout_tests:
            recommendations.append(f"Investigate {len(timeout_tests)} timeout issues")
            for test in timeout_tests:
                recommendations.append(f"Optimize {test.test_name}: execution time {test.execution_time_ms:.1f}ms exceeds limit")
        
        # Analyze error tests
        error_tests = [r for r in self.test_suite.test_results if r.status == TestStatus.ERROR]
        if error_tests:
            recommendations.append(f"Resolve {len(error_tests)} test errors")
        
        # Performance recommendations
        slow_tests = [r for r in self.test_suite.test_results if r.execution_time_ms > 30000]  # Tests taking > 30 seconds
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow tests (>30s)")
            for test in slow_tests:
                recommendations.append(f"Optimize {test.test_name}: {test.execution_time_ms:.1f}ms execution time")
        
        # Overall recommendations
        if self.test_suite.overall_score < 80:
            recommendations.append("Improve overall test coverage and reliability")
        elif self.test_suite.overall_score < 95:
            recommendations.append("Address remaining test failures for better reliability")
        else:
            recommendations.append("Excellent test results - maintain current standards")
        
        # Timeout prevention recommendations
        if timeout_tests or slow_tests:
            recommendations.append("Consider increasing timeout limits or optimizing test execution")
            recommendations.append("Implement test parallelization for better performance")
        
        self.test_suite.recommendations = recommendations
        
    async def save_results(self) -> None:
        """Save test results to file"""
        try:
            filename = f"{self.suite_name.lower().replace(' ', '_')}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.reports_dir / filename
            
            # Convert test suite to dict
            test_suite_dict = asdict(self.test_suite)
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(test_suite_dict, f, indent=2, default=str)
            
            logger.info(f"Test results saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            raise
            
    def finalize(self) -> None:
        """Finalize test execution"""
        self.test_suite.end_time = datetime.now()
        self.test_suite.total_execution_time = (self.test_suite.end_time - self.test_suite.start_time).total_seconds()
        self.progress_tracker.finalize()
        
    def _format_time(self, seconds: float) -> str:
        """Format time in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
            
    def print_results(self) -> None:
        """Print test results"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        print(self.test_suite.summary)
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        for i, rec in enumerate(self.test_suite.recommendations, 1):
            print(f"{i}. {rec}")
        
        # Determine overall status
        if self.test_suite.overall_score >= 90:
            status = "✅ EXCELLENT"
        elif self.test_suite.overall_score >= 80:
            status = "✅ GOOD"
        elif self.test_suite.overall_score >= 70:
            status = "⚠️ ACCEPTABLE"
        else:
            status = "❌ NEEDS IMPROVEMENT"
        
        print(f"\nOverall Status: {status}")
        print(f"Test Suite Completion: {self.test_suite.overall_score:.1f}%") 