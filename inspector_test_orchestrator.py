#!/usr/bin/env python3
"""
Inspector Test Orchestrator

This module implements comprehensive Inspector test orchestration system
for the MCP server Inspector integration. Part of Task 1.2 in the Inspector Task List.

Features:
- Test scheduling and execution
- Test result aggregation
- Test reporting system
- Test dependency management
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import aiofiles

# Import configuration manager
from inspector_config_manager import InspectorConfigManager, InspectorSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    ERROR = "error"

class TestType(Enum):
    """Test types"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"

@dataclass
class TestResult:
    """Test execution result"""
    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    output: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.end_time and self.start_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    test_types: List[TestType]
    tests: List[str]  # List of test IDs
    dependencies: List[str] = None  # Dependencies on other test suites
    timeout_seconds: int = 300
    retry_attempts: int = 1
    parallel_execution: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class InspectorTestOrchestrator:
    """
    Inspector Test Orchestrator
    
    Manages test execution, scheduling, and result aggregation for the MCP server Inspector.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.settings: InspectorSettings = None
        
        # Test execution state
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.running_tests: Dict[str, asyncio.Task] = {}
        self.test_queue: asyncio.Queue = None
        
        # Execution control
        self.is_running = False
        self.execution_start_time: Optional[datetime] = None
        self.execution_end_time: Optional[datetime] = None
        
        # Callbacks
        self.on_test_start: Optional[Callable] = None
        self.on_test_complete: Optional[Callable] = None
        self.on_suite_complete: Optional[Callable] = None
        
        # Results storage
        self.results_dir = Path("results/inspector")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Inspector Test Orchestrator initialized")
    
    async def initialize(self) -> None:
        """Initialize the test orchestrator"""
        try:
            logger.info("Initializing Inspector Test Orchestrator...")
            
            # Get current settings
            self.settings = await self.config_manager.get_current_settings()
            
            # Initialize test queue
            self.test_queue = asyncio.Queue()
            
            # Create default test suites
            await self.create_default_test_suites()
            
            logger.info("Inspector Test Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Inspector Test Orchestrator: {e}")
            raise
    
    async def create_default_test_suites(self) -> None:
        """Create default test suites"""
        try:
            # Unit test suite
            unit_suite = TestSuite(
                name="unit_tests",
                description="Unit tests for individual MCP tools",
                test_types=[TestType.UNIT],
                tests=[
                    "test_tool_registration",
                    "test_tool_schema_validation",
                    "test_tool_execution",
                    "test_error_handling"
                ],
                timeout_seconds=60,
                retry_attempts=2,
                parallel_execution=True
            )
            
            # Integration test suite
            integration_suite = TestSuite(
                name="integration_tests",
                description="Integration tests for tool interactions",
                test_types=[TestType.INTEGRATION],
                tests=[
                    "test_tool_workflow",
                    "test_data_flow",
                    "test_state_management",
                    "test_concurrent_execution"
                ],
                dependencies=["unit_tests"],
                timeout_seconds=120,
                retry_attempts=1,
                parallel_execution=False
            )
            
            # Performance test suite
            performance_suite = TestSuite(
                name="performance_tests",
                description="Performance and load testing",
                test_types=[TestType.PERFORMANCE],
                tests=[
                    "test_response_times",
                    "test_concurrent_load",
                    "test_memory_usage",
                    "test_cpu_usage"
                ],
                dependencies=["unit_tests"],
                timeout_seconds=300,
                retry_attempts=1,
                parallel_execution=False
            )
            
            # Compliance test suite
            compliance_suite = TestSuite(
                name="compliance_tests",
                description="MCP protocol compliance testing",
                test_types=[TestType.COMPLIANCE],
                tests=[
                    "test_json_rpc_compliance",
                    "test_mcp_protocol_compliance",
                    "test_error_handling_compliance",
                    "test_tool_registration_compliance"
                ],
                timeout_seconds=90,
                retry_attempts=2,
                parallel_execution=True
            )
            
            # Add test suites
            self.test_suites = {
                "unit_tests": unit_suite,
                "integration_tests": integration_suite,
                "performance_tests": performance_suite,
                "compliance_tests": compliance_suite
            }
            
            logger.info(f"Created {len(self.test_suites)} default test suites")
            
        except Exception as e:
            logger.error(f"Failed to create default test suites: {e}")
            raise
    
    async def add_test_suite(self, suite: TestSuite) -> bool:
        """Add a new test suite"""
        try:
            if suite.name in self.test_suites:
                logger.error(f"Test suite '{suite.name}' already exists")
                return False
            
            self.test_suites[suite.name] = suite
            logger.info(f"Added test suite: {suite.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add test suite: {e}")
            return False
    
    async def remove_test_suite(self, suite_name: str) -> bool:
        """Remove a test suite"""
        try:
            if suite_name not in self.test_suites:
                logger.error(f"Test suite '{suite_name}' not found")
                return False
            
            del self.test_suites[suite_name]
            logger.info(f"Removed test suite: {suite_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove test suite: {e}")
            return False
    
    async def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        try:
            if suite_name not in self.test_suites:
                raise ValueError(f"Test suite '{suite_name}' not found")
            
            suite = self.test_suites[suite_name]
            
            # Check dependencies
            if suite.dependencies:
                for dep in suite.dependencies:
                    if dep not in self.test_suites:
                        raise ValueError(f"Dependency '{dep}' not found")
                    
                    # Run dependency first
                    dep_result = await self.run_test_suite(dep)
                    if not dep_result["success"]:
                        raise ValueError(f"Dependency '{dep}' failed")
            
            logger.info(f"Running test suite: {suite_name}")
            
            # Create test tasks
            test_tasks = []
            for test_id in suite.tests:
                task = asyncio.create_task(self._run_single_test(test_id, suite))
                test_tasks.append(task)
            
            # Execute tests
            if suite.parallel_execution:
                results = await asyncio.gather(*test_tasks, return_exceptions=True)
            else:
                results = []
                for task in test_tasks:
                    try:
                        result = await task
                        results.append(result)
                    except Exception as e:
                        results.append(e)
            
            # Aggregate results
            suite_result = await self._aggregate_suite_results(suite_name, results)
            
            # Call completion callback
            if self.on_suite_complete:
                await self.on_suite_complete(suite_name, suite_result)
            
            return suite_result
            
        except Exception as e:
            logger.error(f"Failed to run test suite '{suite_name}': {e}")
            return {
                "suite_name": suite_name,
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        try:
            if self.is_running:
                raise RuntimeError("Test execution already in progress")
            
            self.is_running = True
            self.execution_start_time = datetime.now(timezone.utc)
            
            logger.info("Starting execution of all test suites")
            
            # Get execution order based on dependencies
            execution_order = await self._get_execution_order()
            
            # Run test suites in order
            all_results = {}
            for suite_name in execution_order:
                if suite_name in self.test_suites:
                    result = await self.run_test_suite(suite_name)
                    all_results[suite_name] = result
            
            self.execution_end_time = datetime.now(timezone.utc)
            self.is_running = False
            
            # Generate overall report
            overall_result = await self._generate_overall_report(all_results)
            
            logger.info("Completed execution of all test suites")
            return overall_result
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to run all tests: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": {}
            }
    
    async def _get_execution_order(self) -> List[str]:
        """Get execution order based on dependencies"""
        try:
            # Simple topological sort for dependencies
            visited = set()
            order = []
            
            def visit(suite_name):
                if suite_name in visited:
                    return
                
                suite = self.test_suites[suite_name]
                for dep in suite.dependencies:
                    visit(dep)
                
                visited.add(suite_name)
                order.append(suite_name)
            
            for suite_name in self.test_suites:
                visit(suite_name)
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to get execution order: {e}")
            return list(self.test_suites.keys())
    
    async def _run_single_test(self, test_id: str, suite: TestSuite) -> TestResult:
        """Run a single test"""
        try:
            test_name = f"{suite.name}_{test_id}"
            start_time = datetime.now(timezone.utc)
            
            # Create test result
            test_result = TestResult(
                test_id=test_id,
                test_name=test_name,
                test_type=suite.test_types[0] if suite.test_types else TestType.UNIT,
                status=TestStatus.RUNNING,
                start_time=start_time
            )
            
            # Store result
            self.test_results[test_id] = test_result
            
            # Call start callback
            if self.on_test_start:
                await self.on_test_start(test_id, test_result)
            
            logger.info(f"Running test: {test_name}")
            
            # Execute test based on type
            if test_result.test_type == TestType.UNIT:
                result = await self._execute_unit_test(test_id)
            elif test_result.test_type == TestType.INTEGRATION:
                result = await self._execute_integration_test(test_id)
            elif test_result.test_type == TestType.PERFORMANCE:
                result = await self._execute_performance_test(test_id)
            elif test_result.test_type == TestType.COMPLIANCE:
                result = await self._execute_compliance_test(test_id)
            else:
                result = await self._execute_generic_test(test_id)
            
            # Update test result
            test_result.end_time = datetime.now(timezone.utc)
            test_result.status = result["status"]
            test_result.output = result.get("output")
            test_result.error_message = result.get("error")
            
            # Call completion callback
            if self.on_test_complete:
                await self.on_test_complete(test_id, test_result)
            
            logger.info(f"Completed test: {test_name} - {test_result.status.value}")
            return test_result
            
        except Exception as e:
            logger.error(f"Failed to run test {test_id}: {e}")
            
            # Create error result
            test_result = TestResult(
                test_id=test_id,
                test_name=test_name if 'test_name' in locals() else test_id,
                test_type=suite.test_types[0] if suite.test_types else TestType.UNIT,
                status=TestStatus.ERROR,
                start_time=start_time if 'start_time' in locals() else datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                error_message=str(e)
            )
            
            self.test_results[test_id] = test_result
            return test_result
    
    async def _execute_unit_test(self, test_id: str) -> Dict[str, Any]:
        """Execute a unit test"""
        try:
            # Mock unit test execution
            await asyncio.sleep(1)  # Simulate test execution
            
            # Random success/failure for demonstration
            import random
            success = random.random() > 0.2  # 80% success rate
            
            if success:
                return {
                    "status": TestStatus.PASSED,
                    "output": f"Unit test {test_id} passed successfully"
                }
            else:
                return {
                    "status": TestStatus.FAILED,
                    "output": f"Unit test {test_id} failed",
                    "error": "Test assertion failed"
                }
                
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e)
            }
    
    async def _execute_integration_test(self, test_id: str) -> Dict[str, Any]:
        """Execute an integration test"""
        try:
            # Mock integration test execution
            await asyncio.sleep(2)  # Simulate longer test execution
            
            # Random success/failure for demonstration
            import random
            success = random.random() > 0.3  # 70% success rate
            
            if success:
                return {
                    "status": TestStatus.PASSED,
                    "output": f"Integration test {test_id} passed successfully"
                }
            else:
                return {
                    "status": TestStatus.FAILED,
                    "output": f"Integration test {test_id} failed",
                    "error": "Integration test failed"
                }
                
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e)
            }
    
    async def _execute_performance_test(self, test_id: str) -> Dict[str, Any]:
        """Execute a performance test"""
        try:
            # Mock performance test execution
            await asyncio.sleep(3)  # Simulate performance test execution
            
            # Random success/failure for demonstration
            import random
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                return {
                    "status": TestStatus.PASSED,
                    "output": f"Performance test {test_id} passed successfully",
                    "metadata": {
                        "response_time_ms": random.randint(100, 1000),
                        "memory_usage_mb": random.randint(50, 200),
                        "cpu_usage_percent": random.randint(10, 50)
                    }
                }
            else:
                return {
                    "status": TestStatus.FAILED,
                    "output": f"Performance test {test_id} failed",
                    "error": "Performance threshold exceeded"
                }
                
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e)
            }
    
    async def _execute_compliance_test(self, test_id: str) -> Dict[str, Any]:
        """Execute a compliance test"""
        try:
            # Mock compliance test execution
            await asyncio.sleep(1.5)  # Simulate compliance test execution
            
            # Random success/failure for demonstration
            import random
            success = random.random() > 0.15  # 85% success rate
            
            if success:
                return {
                    "status": TestStatus.PASSED,
                    "output": f"Compliance test {test_id} passed successfully"
                }
            else:
                return {
                    "status": TestStatus.FAILED,
                    "output": f"Compliance test {test_id} failed",
                    "error": "Compliance requirement not met"
                }
                
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e)
            }
    
    async def _execute_generic_test(self, test_id: str) -> Dict[str, Any]:
        """Execute a generic test"""
        try:
            await asyncio.sleep(1)
            
            return {
                "status": TestStatus.PASSED,
                "output": f"Generic test {test_id} passed successfully"
            }
                
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e)
            }
    
    async def _aggregate_suite_results(self, suite_name: str, results: List[Any]) -> Dict[str, Any]:
        """Aggregate results for a test suite"""
        try:
            # Filter out exceptions
            valid_results = [r for r in results if not isinstance(r, Exception)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            # Count results by status
            status_counts = {}
            for status in TestStatus:
                status_counts[status.value] = 0
            
            for result in valid_results:
                if hasattr(result, 'status'):
                    status_counts[result.status.value] += 1
            
            # Calculate success rate
            total_tests = len(valid_results)
            passed_tests = status_counts.get(TestStatus.PASSED.value, 0)
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Calculate average duration
            durations = [r.duration_ms for r in valid_results if r.duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "suite_name": suite_name,
                "success": success_rate >= self.settings.alert_threshold_percent,
                "success_rate": success_rate,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": status_counts.get(TestStatus.FAILED.value, 0),
                "error_tests": status_counts.get(TestStatus.ERROR.value, 0),
                "skipped_tests": status_counts.get(TestStatus.SKIPPED.value, 0),
                "average_duration_ms": avg_duration,
                "exceptions": len(exceptions),
                "results": valid_results
            }
            
        except Exception as e:
            logger.error(f"Failed to aggregate suite results: {e}")
            return {
                "suite_name": suite_name,
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def _generate_overall_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall execution report"""
        try:
            total_suites = len(all_results)
            successful_suites = sum(1 for r in all_results.values() if r.get("success", False))
            success_rate = (successful_suites / total_suites * 100) if total_suites > 0 else 0
            
            total_tests = sum(r.get("total_tests", 0) for r in all_results.values())
            total_passed = sum(r.get("passed_tests", 0) for r in all_results.values())
            overall_test_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            execution_duration = None
            if self.execution_start_time and self.execution_end_time:
                execution_duration = (self.execution_end_time - self.execution_start_time).total_seconds()
            
            return {
                "success": success_rate >= self.settings.alert_threshold_percent,
                "execution_start_time": self.execution_start_time.isoformat() if self.execution_start_time else None,
                "execution_end_time": self.execution_end_time.isoformat() if self.execution_end_time else None,
                "execution_duration_seconds": execution_duration,
                "total_suites": total_suites,
                "successful_suites": successful_suites,
                "suite_success_rate": success_rate,
                "total_tests": total_tests,
                "total_passed_tests": total_passed,
                "overall_test_success_rate": overall_test_success_rate,
                "results": all_results
            }
            
        except Exception as e:
            logger.error(f"Failed to generate overall report: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": {}
            }
    
    async def get_test_results(self, test_id: Optional[str] = None) -> Dict[str, Any]:
        """Get test results"""
        if test_id:
            return self.test_results.get(test_id)
        return self.test_results
    
    async def clear_results(self) -> None:
        """Clear all test results"""
        self.test_results.clear()
        logger.info("Test results cleared")
    
    async def save_results(self, filename: Optional[str] = None) -> bool:
        """Save test results to file"""
        try:
            if not filename:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                filename = f"test_results_{timestamp}.json"
            
            filepath = self.results_dir / filename
            
            # Convert results to serializable format
            serializable_results = {}
            for test_id, result in self.test_results.items():
                result_dict = asdict(result)
                result_dict['start_time'] = result_dict['start_time'].isoformat()
                if result_dict['end_time']:
                    result_dict['end_time'] = result_dict['end_time'].isoformat()
                # Convert enum values to strings for JSON serialization
                if 'status' in result_dict:
                    result_dict['status'] = result_dict['status'].value
                if 'test_type' in result_dict:
                    result_dict['test_type'] = result_dict['test_type'].value
                serializable_results[test_id] = result_dict
            
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(serializable_results, indent=2))
            
            logger.info(f"Test results saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            return False
    
    async def load_results(self, filename: str) -> bool:
        """Load test results from file"""
        try:
            filepath = self.results_dir / filename
            
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                data = await f.read()
                results_data = json.loads(data)
            
            # Convert back to TestResult objects
            self.test_results = {}
            for test_id, result_dict in results_data.items():
                # Convert datetime strings back to datetime objects
                if 'start_time' in result_dict:
                    result_dict['start_time'] = datetime.fromisoformat(result_dict['start_time'])
                if 'end_time' in result_dict:
                    result_dict['end_time'] = datetime.fromisoformat(result_dict['end_time'])
                
                # Convert enum strings back to enum objects
                if 'status' in result_dict:
                    result_dict['status'] = TestStatus(result_dict['status'])
                if 'test_type' in result_dict:
                    result_dict['test_type'] = TestType(result_dict['test_type'])
                
                result = TestResult(**result_dict)
                self.test_results[test_id] = result
            
            logger.info(f"Test results loaded from: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load test results: {e}")
            return False

# Example usage and testing
async def main():
    """Example usage of Inspector Test Orchestrator"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize test orchestrator
        orchestrator = InspectorTestOrchestrator(config_manager)
        await orchestrator.initialize()
        
        # Run all tests
        print("Running all test suites...")
        results = await orchestrator.run_all_tests()
        
        print(f"Overall success: {results['success']}")
        print(f"Suite success rate: {results['suite_success_rate']:.1f}%")
        print(f"Test success rate: {results['overall_test_success_rate']:.1f}%")
        print(f"Total tests: {results['total_tests']}")
        print(f"Execution time: {results['execution_duration_seconds']:.1f}s")
        
        # Save results
        await orchestrator.save_results()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 