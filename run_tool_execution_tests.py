#!/usr/bin/env python3
"""
Tool Execution Test Runner

This script runs all tool execution tests for Task 2.3:
- Tool execution testing (basic execution validation)
- Tool functionality testing (behavioral validation)
- Tool error handling testing (error condition validation)

Part of Task 2.3: Tool Execution Testing
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import test modules
from test_tool_execution import ToolExecutionTester
from test_tool_functionality import ToolFunctionalityTester
from test_tool_error_handling import ToolErrorHandlingTester

# Import Inspector CLI utilities
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolExecutionTestRunner:
    """Comprehensive tool execution test runner"""

    def __init__(self):
        """Initialize the test runner"""
        self.test_results = {}
        self.overall_score = 0.0
        self.total_tests = 0
        self.passed_tests = 0

    async def initialize(self) -> bool:
        """Initialize the test runner"""
        try:
            logger.info("Initializing Tool Execution Test Runner...")

            # Test Inspector CLI setup
            if not inspector_cli.npx_path:
                logger.error("❌ Inspector CLI setup failed - npx not found")
                return False

            logger.info("✅ Tool Execution Test Runner initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize test runner: {e}")
            return False

    async def run_tool_execution_tests(self) -> Dict[str, Any]:
        """Run tool execution tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING TOOL EXECUTION TESTS")
        logger.info("="*60)

        try:
            tester = ToolExecutionTester()
            test_suite = tester.test_all_tools_execution()

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/inspector/tool_execution_test_{timestamp}.json"
            tester.save_test_results(test_suite, output_file)

            result = {
                "test_suite": "Tool Execution Testing",
                "execution_success_rate": test_suite.execution_success_rate,
                "total_tools": test_suite.total_tools,
                "successful_executions": test_suite.successful_executions,
                "failed_executions": test_suite.failed_executions,
                "timeout_executions": test_suite.timeout_executions,
                "error_executions": test_suite.error_executions,
                "invalid_output_executions": test_suite.invalid_output_executions,
                "average_execution_time_ms": test_suite.average_execution_time_ms,
                "max_execution_time_ms": test_suite.max_execution_time_ms,
                "min_execution_time_ms": test_suite.min_execution_time_ms,
                "total_output_size_bytes": test_suite.total_output_size_bytes,
                "summary": f"Tool execution testing completed with {test_suite.execution_success_rate:.1f}% success rate",
                "status": "pass" if test_suite.execution_success_rate >= 80 else "fail"
            }

            logger.info(f"✅ Tool execution success rate: {test_suite.execution_success_rate:.1f}%")
            return result

        except Exception as e:
            logger.error(f"❌ Tool execution tests failed: {e}")
            return {
                "test_suite": "Tool Execution Testing",
                "execution_success_rate": 0.0,
                "total_tools": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "timeout_executions": 0,
                "error_executions": 0,
                "invalid_output_executions": 0,
                "average_execution_time_ms": 0.0,
                "max_execution_time_ms": 0.0,
                "min_execution_time_ms": 0.0,
                "total_output_size_bytes": 0,
                "summary": f"Tests failed with error: {e}",
                "status": "error"
            }

    async def run_tool_functionality_tests(self) -> Dict[str, Any]:
        """Run tool functionality tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING TOOL FUNCTIONALITY TESTS")
        logger.info("="*60)

        try:
            tester = ToolFunctionalityTester()
            test_suite = tester.test_all_tools_functionality()

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/inspector/tool_functionality_test_{timestamp}.json"
            tester.save_test_results(test_suite, output_file)

            result = {
                "test_suite": "Tool Functionality Testing",
                "functionality_success_rate": test_suite.functionality_success_rate,
                "total_test_cases": test_suite.total_test_cases,
                "passed_tests": test_suite.passed_tests,
                "failed_tests": test_suite.failed_tests,
                "partial_tests": test_suite.partial_tests,
                "error_tests": test_suite.error_tests,
                "timeout_tests": test_suite.timeout_tests,
                "average_test_duration_ms": test_suite.average_test_duration_ms,
                "max_test_duration_ms": test_suite.max_test_duration_ms,
                "min_test_duration_ms": test_suite.min_test_duration_ms,
                "summary": f"Tool functionality testing completed with {test_suite.functionality_success_rate:.1f}% success rate",
                "status": "pass" if test_suite.functionality_success_rate >= 80 else "fail"
            }

            logger.info(f"✅ Tool functionality success rate: {test_suite.functionality_success_rate:.1f}%")
            return result

        except Exception as e:
            logger.error(f"❌ Tool functionality tests failed: {e}")
            return {
                "test_suite": "Tool Functionality Testing",
                "functionality_success_rate": 0.0,
                "total_test_cases": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "partial_tests": 0,
                "error_tests": 0,
                "timeout_tests": 0,
                "average_test_duration_ms": 0.0,
                "max_test_duration_ms": 0.0,
                "min_test_duration_ms": 0.0,
                "summary": f"Tests failed with error: {e}",
                "status": "error"
            }

    async def run_tool_error_handling_tests(self) -> Dict[str, Any]:
        """Run tool error handling tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING TOOL ERROR HANDLING TESTS")
        logger.info("="*60)

        try:
            tester = ToolErrorHandlingTester()
            test_suite = tester.test_all_tools_error_handling()

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/inspector/tool_error_handling_test_{timestamp}.json"
            tester.save_test_results(test_suite, output_file)

            result = {
                "test_suite": "Tool Error Handling Testing",
                "error_handling_success_rate": test_suite.error_handling_success_rate,
                "total_test_cases": test_suite.total_test_cases,
                "proper_error_handling": test_suite.proper_error_handling,
                "unexpected_success": test_suite.unexpected_success,
                "crashes": test_suite.crashes,
                "timeouts": test_suite.timeouts,
                "invalid_responses": test_suite.invalid_responses,
                "average_test_duration_ms": test_suite.average_test_duration_ms,
                "max_test_duration_ms": test_suite.max_test_duration_ms,
                "min_test_duration_ms": test_suite.min_test_duration_ms,
                "summary": f"Tool error handling testing completed with {test_suite.error_handling_success_rate:.1f}% success rate",
                "status": "pass" if test_suite.error_handling_success_rate >= 80 else "fail"
            }

            logger.info(f"✅ Tool error handling success rate: {test_suite.error_handling_success_rate:.1f}%")
            return result

        except Exception as e:
            logger.error(f"❌ Tool error handling tests failed: {e}")
            return {
                "test_suite": "Tool Error Handling Testing",
                "error_handling_success_rate": 0.0,
                "total_test_cases": 0,
                "proper_error_handling": 0,
                "unexpected_success": 0,
                "crashes": 0,
                "timeouts": 0,
                "invalid_responses": 0,
                "average_test_duration_ms": 0.0,
                "max_test_duration_ms": 0.0,
                "min_test_duration_ms": 0.0,
                "summary": f"Tests failed with error: {e}",
                "status": "error"
            }

    async def run_all_tool_execution_tests(self) -> Dict[str, Any]:
        """Run all tool execution tests"""
        logger.info("="*80)
        logger.info("TOOL EXECUTION TEST SUITE - TASK 2.3")
        logger.info("="*80)
        logger.info("Running comprehensive tool execution testing...")

        # Run all test suites
        execution_result = await self.run_tool_execution_tests()
        functionality_result = await self.run_tool_functionality_tests()
        error_handling_result = await self.run_tool_error_handling_tests()

        # Collect all results
        self.test_results = {
            "execution": execution_result,
            "functionality": functionality_result,
            "error_handling": error_handling_result
        }

        # Calculate overall metrics
        self.total_tests = (
            execution_result.get("total_tools", 0) +
            functionality_result.get("total_test_cases", 0) +
            error_handling_result.get("total_test_cases", 0)
        )

        self.passed_tests = (
            execution_result.get("successful_executions", 0) +
            functionality_result.get("passed_tests", 0) +
            error_handling_result.get("proper_error_handling", 0)
        )

        # Calculate overall success score (weighted average)
        execution_score = execution_result.get("execution_success_rate", 0.0)
        functionality_score = functionality_result.get("functionality_success_rate", 0.0)
        error_handling_score = error_handling_result.get("error_handling_success_rate", 0.0)

        # Weight the scores (execution is most important, then functionality, then error handling)
        self.overall_score = (execution_score * 0.4 + functionality_score * 0.35 + error_handling_score * 0.25)

        # Generate overall report
        overall_report = {
            "test_suite": "Tool Execution Test Suite",
            "timestamp": datetime.now().isoformat(),
            "overall_success_score": self.overall_score,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "test_results": self.test_results,
            "summary": self._generate_overall_summary(),
            "recommendations": self._generate_overall_recommendations(),
            "status": "pass" if self.overall_score >= 80 else "fail"
        }

        return overall_report

    def _generate_overall_summary(self) -> str:
        """Generate overall test summary"""
        summary = f"Tool Execution Test Suite Results:\n"
        summary += f"- Overall Success Score: {self.overall_score:.1f}%\n"
        summary += f"- Total Tests: {self.total_tests}\n"
        summary += f"- Passed Tests: {self.passed_tests}\n"
        summary += f"- Failed Tests: {self.total_tests - self.passed_tests}\n"

        # Individual test suite scores
        execution_score = self.test_results["execution"].get("execution_success_rate", 0.0)
        functionality_score = self.test_results["functionality"].get("functionality_success_rate", 0.0)
        error_handling_score = self.test_results["error_handling"].get("error_handling_success_rate", 0.0)

        summary += f"\nIndividual Test Suite Scores:\n"
        summary += f"- Tool Execution: {execution_score:.1f}%\n"
        summary += f"- Tool Functionality: {functionality_score:.1f}%\n"
        summary += f"- Tool Error Handling: {error_handling_score:.1f}%\n"

        if self.overall_score >= 95:
            summary += "\n✅ Excellent tool execution - all tools working perfectly"
        elif self.overall_score >= 80:
            summary += "\n⚠️ Good tool execution with minor issues"
        elif self.overall_score >= 60:
            summary += "\n⚠️ Moderate tool execution with significant issues"
        else:
            summary += "\n❌ Poor tool execution - major issues need addressing"

        return summary

    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []

        # Check each test suite
        execution_score = self.test_results["execution"].get("execution_success_rate", 0.0)
        functionality_score = self.test_results["functionality"].get("functionality_success_rate", 0.0)
        error_handling_score = self.test_results["error_handling"].get("error_handling_success_rate", 0.0)

        if execution_score < 80:
            recommendations.append(f"Improve tool execution reliability (current: {execution_score:.1f}%)")
        if functionality_score < 80:
            recommendations.append(f"Improve tool functionality correctness (current: {functionality_score:.1f}%)")
        if error_handling_score < 80:
            recommendations.append(f"Improve tool error handling robustness (current: {error_handling_score:.1f}%)")

        # Add specific recommendations based on test results
        execution_result = self.test_results["execution"]
        if execution_result.get("failed_executions", 0) > 0:
            recommendations.append(f"Fix {execution_result['failed_executions']} failed tool executions")
        if execution_result.get("timeout_executions", 0) > 0:
            recommendations.append(f"Address {execution_result['timeout_executions']} tool execution timeouts")

        functionality_result = self.test_results["functionality"]
        if functionality_result.get("failed_tests", 0) > 0:
            recommendations.append(f"Fix {functionality_result['failed_tests']} failed functionality tests")

        error_handling_result = self.test_results["error_handling"]
        if error_handling_result.get("crashes", 0) > 0:
            recommendations.append(f"Fix {error_handling_result['crashes']} tool crashes during error handling")

        if not recommendations:
            recommendations.append("All tool execution tests passed - maintain current implementation")

        return recommendations

    async def save_overall_report(self, report: Dict[str, Any]) -> bool:
        """Save the overall test report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/inspector/tool_execution_overall_{timestamp}.json"

            # Ensure reports directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Overall tool execution report saved to: {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to save overall report: {e}")
            return False


async def main():
    """Main function to run all tool execution tests"""
    try:
        # Initialize test runner
        runner = ToolExecutionTestRunner()
        if not await runner.initialize():
            logger.error("❌ Failed to initialize test runner")
            return False

        # Run all tool execution tests
        overall_report = await runner.run_all_tool_execution_tests()

        # Print results
        print("\n" + "="*80)
        print("TOOL EXECUTION TEST SUITE RESULTS")
        print("="*80)
        print(overall_report["summary"])

        if overall_report["recommendations"]:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(overall_report["recommendations"], 1):
                print(f"{i}. {rec}")

        # Save overall report
        await runner.save_overall_report(overall_report)

        # Final status
        if overall_report["status"] == "pass":
            print(f"\n✅ TASK 2.3 COMPLETED SUCCESSFULLY!")
            print(f"Tool execution success score: {overall_report['overall_success_score']:.1f}%")
            return True
        else:
            print(f"\n⚠️ TASK 2.3 COMPLETED WITH ISSUES")
            print(f"Tool execution success score: {overall_report['overall_success_score']:.1f}%")
            print("Review recommendations above for improvements")
            return False

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 