#!/usr/bin/env python3
"""
Protocol Compliance Test Runner

This script runs all protocol compliance tests for Task 2.1:
- JSON-RPC 2.0 compliance testing
- MCP protocol compliance testing  
- Error handling compliance testing

Part of Task 2.1: Protocol Compliance Testing - Inspector CLI Integration Fix
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import test modules
from test_json_rpc_compliance import JSONRPCComplianceTester
from test_mcp_protocol_compliance import MCPProtocolComplianceTester
from test_error_handling_compliance import ErrorHandlingComplianceTester

# Import utilities
from inspector_config_manager import InspectorConfigManager
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProtocolComplianceTestRunner:
    """Comprehensive protocol compliance test runner"""
    
    def __init__(self):
        """Initialize the test runner"""
        self.config_manager = None
        self.test_results = {}
        self.overall_score = 0.0
        self.total_tests = 0
        self.passed_tests = 0
        
    async def initialize(self) -> bool:
        """Initialize the test runner"""
        try:
            logger.info("Initializing Protocol Compliance Test Runner...")
            
            # Initialize config manager
            self.config_manager = InspectorConfigManager()
            await self.config_manager.initialize()
            
            # Test Inspector CLI setup
            if not inspector_cli.npx_path:
                logger.error("❌ Inspector CLI setup failed - npx not found")
                return False
            
            logger.info("✅ Protocol Compliance Test Runner initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize test runner: {e}")
            return False
    
    async def run_jsonrpc_compliance_tests(self) -> Dict[str, Any]:
        """Run JSON-RPC 2.0 compliance tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING JSON-RPC 2.0 COMPLIANCE TESTS")
        logger.info("="*60)
        
        try:
            tester = JSONRPCComplianceTester(self.config_manager)
            await tester.initialize()
            
            report = await tester.run_compliance_tests()
            
            # Save report
            await tester.save_report(report)
            
            result = {
                "test_suite": "JSON-RPC 2.0 Compliance",
                "compliance_score": report.compliance_score,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "warning_tests": report.warning_tests,
                "error_tests": report.error_tests,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "status": "pass" if report.compliance_score >= 80 else "fail"
            }
            
            logger.info(f"✅ JSON-RPC compliance score: {report.compliance_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ JSON-RPC compliance tests failed: {e}")
            return {
                "test_suite": "JSON-RPC 2.0 Compliance",
                "compliance_score": 0.0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "warning_tests": 0,
                "error_tests": 0,
                "summary": f"Tests failed with error: {e}",
                "recommendations": ["Fix JSON-RPC compliance test execution"],
                "status": "error"
            }
    
    async def run_mcp_protocol_compliance_tests(self) -> Dict[str, Any]:
        """Run MCP protocol compliance tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING MCP PROTOCOL COMPLIANCE TESTS")
        logger.info("="*60)
        
        try:
            tester = MCPProtocolComplianceTester(self.config_manager)
            await tester.initialize()
            
            report = await tester.run_compliance_tests()
            
            # Save report
            await tester.save_report(report)
            
            result = {
                "test_suite": "MCP Protocol Compliance",
                "compliance_score": report.compliance_score,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "warning_tests": report.warning_tests,
                "error_tests": report.error_tests,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "status": "pass" if report.compliance_score >= 80 else "fail"
            }
            
            logger.info(f"✅ MCP protocol compliance score: {report.compliance_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP protocol compliance tests failed: {e}")
            return {
                "test_suite": "MCP Protocol Compliance",
                "compliance_score": 0.0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "warning_tests": 0,
                "error_tests": 0,
                "summary": f"Tests failed with error: {e}",
                "recommendations": ["Fix MCP protocol compliance test execution"],
                "status": "error"
            }
    
    async def run_error_handling_compliance_tests(self) -> Dict[str, Any]:
        """Run error handling compliance tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING ERROR HANDLING COMPLIANCE TESTS")
        logger.info("="*60)
        
        try:
            tester = ErrorHandlingComplianceTester(self.config_manager)
            await tester.initialize()
            
            report = await tester.run_compliance_tests()
            
            # Save report
            await tester.save_report(report)
            
            result = {
                "test_suite": "Error Handling Compliance",
                "compliance_score": report.compliance_score,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "warning_tests": report.warning_tests,
                "error_tests": report.error_tests,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "status": "pass" if report.compliance_score >= 80 else "fail"
            }
            
            logger.info(f"✅ Error handling compliance score: {report.compliance_score:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error handling compliance tests failed: {e}")
            return {
                "test_suite": "Error Handling Compliance",
                "compliance_score": 0.0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "warning_tests": 0,
                "error_tests": 0,
                "summary": f"Tests failed with error: {e}",
                "recommendations": ["Fix error handling compliance test execution"],
                "status": "error"
            }
    
    async def run_all_compliance_tests(self) -> Dict[str, Any]:
        """Run all protocol compliance tests"""
        logger.info("="*80)
        logger.info("PROTOCOL COMPLIANCE TEST SUITE - TASK 2.1")
        logger.info("="*80)
        logger.info("Running comprehensive protocol compliance testing...")
        
        # Run all test suites
        jsonrpc_result = await self.run_jsonrpc_compliance_tests()
        mcp_result = await self.run_mcp_protocol_compliance_tests()
        error_result = await self.run_error_handling_compliance_tests()
        
        # Collect all results
        self.test_results = {
            "jsonrpc": jsonrpc_result,
            "mcp_protocol": mcp_result,
            "error_handling": error_result
        }
        
        # Calculate overall metrics
        self.total_tests = (
            jsonrpc_result["total_tests"] + 
            mcp_result["total_tests"] + 
            error_result["total_tests"]
        )
        
        self.passed_tests = (
            jsonrpc_result["passed_tests"] + 
            mcp_result["passed_tests"] + 
            error_result["passed_tests"]
        )
        
        # Calculate overall compliance score
        total_score = (
            jsonrpc_result["compliance_score"] + 
            mcp_result["compliance_score"] + 
            error_result["compliance_score"]
        )
        self.overall_score = total_score / 3.0
        
        # Generate overall report
        overall_report = {
            "test_suite": "Protocol Compliance Test Suite",
            "timestamp": datetime.now().isoformat(),
            "overall_compliance_score": self.overall_score,
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
        summary = f"Protocol Compliance Test Suite Results:\n"
        summary += f"- Overall Compliance Score: {self.overall_score:.1f}%\n"
        summary += f"- Total Tests: {self.total_tests}\n"
        summary += f"- Passed Tests: {self.passed_tests}\n"
        summary += f"- Failed Tests: {self.total_tests - self.passed_tests}\n"
        
        if self.overall_score >= 95:
            summary += "\n✅ Excellent protocol compliance - all standards met"
        elif self.overall_score >= 80:
            summary += "\n⚠️ Good protocol compliance with minor issues"
        elif self.overall_score >= 60:
            summary += "\n⚠️ Moderate protocol compliance with significant issues"
        else:
            summary += "\n❌ Poor protocol compliance - major issues need addressing"
        
        return summary
    
    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        # Check each test suite
        for suite_name, result in self.test_results.items():
            if result["compliance_score"] < 80:
                recommendations.append(f"Improve {result['test_suite']} compliance (current: {result['compliance_score']:.1f}%)")
        
        # Add specific recommendations from each suite
        for result in self.test_results.values():
            if result.get("recommendations"):
                recommendations.extend(result["recommendations"][:2])  # Limit to top 2 per suite
        
        if not recommendations:
            recommendations.append("All protocol compliance tests passed - maintain current implementation")
        
        return recommendations
    
    async def save_overall_report(self, report: Dict[str, Any]) -> bool:
        """Save the overall compliance report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/inspector/protocol_compliance_overall_{timestamp}.json"
            
            # Ensure reports directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Overall compliance report saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save overall report: {e}")
            return False


async def main():
    """Main function to run all protocol compliance tests"""
    try:
        # Initialize test runner
        runner = ProtocolComplianceTestRunner()
        
        if not await runner.initialize():
            logger.error("❌ Failed to initialize test runner")
            return False
        
        # Run all compliance tests
        overall_report = await runner.run_all_compliance_tests()
        
        # Print results
        print("\n" + "="*80)
        print("PROTOCOL COMPLIANCE TEST SUITE RESULTS")
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
            print(f"\n✅ TASK 2.1 COMPLETED SUCCESSFULLY!")
            print(f"Protocol compliance score: {overall_report['overall_compliance_score']:.1f}%")
            return True
        else:
            print(f"\n⚠️ TASK 2.1 COMPLETED WITH ISSUES")
            print(f"Protocol compliance score: {overall_report['overall_compliance_score']:.1f}%")
            print("Review recommendations above for improvements")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 