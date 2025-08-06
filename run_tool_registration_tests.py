#!/usr/bin/env python3
"""
Tool Registration Testing Runner

This script orchestrates and runs all three modules for Task 2.2: Tool Registration Testing:
1. test_tool_registration.py - Tests all 81 tools registration
2. test_tool_schema_validation.py - Validates all tool input schemas
3. test_tool_metadata.py - Tests tool descriptions and metadata

Part of Task 2.2: Tool Registration Testing
"""

import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import the test modules
from test_tool_registration import ToolRegistrationTester, ToolRegistrationTestSuite
from test_tool_schema_validation import ToolSchemaValidator, SchemaValidationTestSuite
from test_tool_metadata import ToolMetadataValidator, MetadataValidationTestSuite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolRegistrationOverallResult:
    """Overall result for all tool registration tests"""
    registration_success: bool
    schema_validation_success: bool
    metadata_validation_success: bool
    overall_success: bool
    total_tools_tested: int
    registration_success_rate: float
    schema_validation_success_rate: float
    metadata_validation_success_rate: float
    overall_success_rate: float
    test_duration_seconds: float
    test_timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class ToolRegistrationComprehensiveReport:
    """Comprehensive report for all tool registration tests"""
    overall_result: ToolRegistrationOverallResult
    registration_results: Optional[ToolRegistrationTestSuite] = None
    schema_validation_results: Optional[SchemaValidationTestSuite] = None
    metadata_validation_results: Optional[MetadataValidationTestSuite] = None


class ToolRegistrationTestRunner:
    """Comprehensive tool registration test runner"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the test runner
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.start_time: Optional[datetime] = None
        self.registration_tester = ToolRegistrationTester(mcp_server_path)
        self.schema_validator = ToolSchemaValidator(mcp_server_path)
        self.metadata_validator = ToolMetadataValidator(mcp_server_path)
    
    def run_all_tool_registration_tests(self) -> ToolRegistrationComprehensiveReport:
        """
        Run all tool registration tests
        
        Returns:
            ToolRegistrationComprehensiveReport with all results
        """
        logger.info("Starting comprehensive Tool Registration Testing (Task 2.2)")
        self.start_time = datetime.now()
        
        overall_result = ToolRegistrationOverallResult(
            registration_success=False,
            schema_validation_success=False,
            metadata_validation_success=False,
            overall_success=False,
            total_tools_tested=0,
            registration_success_rate=0.0,
            schema_validation_success_rate=0.0,
            metadata_validation_success_rate=0.0,
            overall_success_rate=0.0,
            test_duration_seconds=0.0,
            test_timestamp=self.start_time
        )
        
        registration_results = None
        schema_validation_results = None
        metadata_validation_results = None
        
        try:
            # Test 1: Tool Registration Testing
            logger.info("=" * 60)
            logger.info("TEST 1: Tool Registration Testing")
            logger.info("=" * 60)
            
            try:
                registration_results = self.registration_tester.test_all_tools_registration()
                overall_result.registration_success = True
                overall_result.total_tools_tested = registration_results.total_tools
                overall_result.registration_success_rate = (
                    registration_results.successful_registrations / registration_results.total_tools
                    if registration_results.total_tools > 0 else 0.0
                )
                logger.info(f"✅ Tool Registration Testing completed successfully")
                logger.info(f"   Success Rate: {overall_result.registration_success_rate*100:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Tool Registration Testing failed: {e}")
                overall_result.error_message = f"Tool Registration Testing failed: {e}"
            
            # Test 2: Tool Schema Validation Testing
            logger.info("=" * 60)
            logger.info("TEST 2: Tool Schema Validation Testing")
            logger.info("=" * 60)
            
            try:
                schema_validation_results = self.schema_validator.validate_all_tool_schemas()
                overall_result.schema_validation_success = True
                overall_result.schema_validation_success_rate = (
                    schema_validation_results.valid_schemas / schema_validation_results.total_tools
                    if schema_validation_results.total_tools > 0 else 0.0
                )
                logger.info(f"✅ Tool Schema Validation Testing completed successfully")
                logger.info(f"   Success Rate: {overall_result.schema_validation_success_rate*100:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Tool Schema Validation Testing failed: {e}")
                if overall_result.error_message:
                    overall_result.error_message += f"; Schema Validation failed: {e}"
                else:
                    overall_result.error_message = f"Schema Validation failed: {e}"
            
            # Test 3: Tool Metadata Testing
            logger.info("=" * 60)
            logger.info("TEST 3: Tool Metadata Testing")
            logger.info("=" * 60)
            
            try:
                metadata_validation_results = self.metadata_validator.validate_all_tool_metadata()
                overall_result.metadata_validation_success = True
                overall_result.metadata_validation_success_rate = (
                    metadata_validation_results.complete_metadata / metadata_validation_results.total_tools
                    if metadata_validation_results.total_tools > 0 else 0.0
                )
                logger.info(f"✅ Tool Metadata Testing completed successfully")
                logger.info(f"   Success Rate: {overall_result.metadata_validation_success_rate*100:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Tool Metadata Testing failed: {e}")
                if overall_result.error_message:
                    overall_result.error_message += f"; Metadata Testing failed: {e}"
                else:
                    overall_result.error_message = f"Metadata Testing failed: {e}"
            
            # Calculate overall results
            end_time = datetime.now()
            overall_result.test_duration_seconds = (end_time - self.start_time).total_seconds()
            overall_result.test_timestamp = end_time
            
            # Calculate overall success rate (average of all three tests)
            success_rates = []
            if overall_result.registration_success:
                success_rates.append(overall_result.registration_success_rate)
            if overall_result.schema_validation_success:
                success_rates.append(overall_result.schema_validation_success_rate)
            if overall_result.metadata_validation_success:
                success_rates.append(overall_result.metadata_validation_success_rate)
            
            if success_rates:
                overall_result.overall_success_rate = sum(success_rates) / len(success_rates)
                overall_result.overall_success = overall_result.overall_success_rate >= 0.90  # 90% threshold
            
            logger.info("=" * 60)
            logger.info("COMPREHENSIVE TOOL REGISTRATION TESTING COMPLETED")
            logger.info("=" * 60)
            logger.info(f"Overall Success Rate: {overall_result.overall_success_rate*100:.1f}%")
            logger.info(f"Overall Status: {'✅ PASSED' if overall_result.overall_success else '❌ FAILED'}")
            logger.info(f"Test Duration: {overall_result.test_duration_seconds:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Comprehensive testing failed with exception: {e}")
            overall_result.error_message = f"Comprehensive testing failed: {e}"
            end_time = datetime.now()
            overall_result.test_duration_seconds = (end_time - self.start_time).total_seconds()
            overall_result.test_timestamp = end_time
        
        return ToolRegistrationComprehensiveReport(
            overall_result=overall_result,
            registration_results=registration_results,
            schema_validation_results=schema_validation_results,
            metadata_validation_results=metadata_validation_results
        )
    
    def save_comprehensive_report(self, report: ToolRegistrationComprehensiveReport, output_file: str = "tool_registration_comprehensive_results.json"):
        """
        Save comprehensive test results to JSON file
        
        Args:
            report: Comprehensive test report to save
            output_file: Output file path
        """
        try:
            # Convert dataclass to dict for JSON serialization
            report_dict = asdict(report)
            
            # Convert datetime to ISO format
            report_dict['overall_result']['test_timestamp'] = report.overall_result.test_timestamp.isoformat()
            
            # Convert nested dataclasses
            if report.registration_results:
                report_dict['registration_results']['test_timestamp'] = report.registration_results.test_timestamp.isoformat()
            
            if report.schema_validation_results:
                report_dict['schema_validation_results']['test_timestamp'] = report.schema_validation_results.test_timestamp.isoformat()
            
            if report.metadata_validation_results:
                report_dict['metadata_validation_results']['test_timestamp'] = report.metadata_validation_results.test_timestamp.isoformat()
            
            with open(output_file, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            logger.info(f"Comprehensive test results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving comprehensive test results: {e}")
    
    def generate_comprehensive_report(self, report: ToolRegistrationComprehensiveReport) -> str:
        """
        Generate a comprehensive human-readable test report
        
        Args:
            report: Comprehensive test report
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("COMPREHENSIVE TOOL REGISTRATION TESTING REPORT")
        report_lines.append("Task 2.2: Tool Registration Testing")
        report_lines.append("=" * 100)
        report_lines.append(f"Test Date: {report.overall_result.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Test Duration: {report.overall_result.test_duration_seconds:.2f} seconds")
        report_lines.append("")
        
        # Overall Summary
        report_lines.append("OVERALL SUMMARY")
        report_lines.append("-" * 50)
        report_lines.append(f"Total Tools Tested: {report.overall_result.total_tools_tested}")
        report_lines.append(f"Overall Success Rate: {report.overall_result.overall_success_rate*100:.1f}%")
        report_lines.append(f"Overall Status: {'✅ PASSED' if report.overall_result.overall_success else '❌ FAILED'}")
        report_lines.append("")
        
        # Individual Test Results
        report_lines.append("INDIVIDUAL TEST RESULTS")
        report_lines.append("-" * 50)
        
        # Test 1: Tool Registration
        status1 = "✅ PASSED" if report.overall_result.registration_success else "❌ FAILED"
        report_lines.append(f"1. Tool Registration Testing: {status1}")
        if report.overall_result.registration_success:
            report_lines.append(f"   Success Rate: {report.overall_result.registration_success_rate*100:.1f}%")
        report_lines.append("")
        
        # Test 2: Schema Validation
        status2 = "✅ PASSED" if report.overall_result.schema_validation_success else "❌ FAILED"
        report_lines.append(f"2. Tool Schema Validation Testing: {status2}")
        if report.overall_result.schema_validation_success:
            report_lines.append(f"   Success Rate: {report.overall_result.schema_validation_success_rate*100:.1f}%")
        report_lines.append("")
        
        # Test 3: Metadata Validation
        status3 = "✅ PASSED" if report.overall_result.metadata_validation_success else "❌ FAILED"
        report_lines.append(f"3. Tool Metadata Testing: {status3}")
        if report.overall_result.metadata_validation_success:
            report_lines.append(f"   Success Rate: {report.overall_result.metadata_validation_success_rate*100:.1f}%")
        report_lines.append("")
        
        # Detailed Results
        if report.registration_results:
            report_lines.append("DETAILED RESULTS - TOOL REGISTRATION")
            report_lines.append("-" * 50)
            report_lines.append(f"Successful Registrations: {report.registration_results.successful_registrations}/{report.registration_results.total_tools}")
            report_lines.append(f"Successful Discoveries: {report.registration_results.successful_discoveries}/{report.registration_results.total_tools}")
            report_lines.append(f"Successful Categorizations: {report.registration_results.successful_categorizations}/{report.registration_results.total_tools}")
            report_lines.append(f"Average Registration Time: {report.registration_results.average_registration_time_ms:.2f} ms")
            if report.registration_results.failed_tools:
                report_lines.append(f"Failed Tools: {', '.join(report.registration_results.failed_tools[:5])}")
                if len(report.registration_results.failed_tools) > 5:
                    report_lines.append(f"   ... and {len(report.registration_results.failed_tools) - 5} more")
            report_lines.append("")
        
        if report.schema_validation_results:
            report_lines.append("DETAILED RESULTS - SCHEMA VALIDATION")
            report_lines.append("-" * 50)
            report_lines.append(f"Valid Schemas: {report.schema_validation_results.valid_schemas}/{report.schema_validation_results.total_tools}")
            report_lines.append(f"Valid Parameter Types: {report.schema_validation_results.valid_parameter_types}/{report.schema_validation_results.total_tools}")
            report_lines.append(f"Valid Required Parameters: {report.schema_validation_results.valid_required_parameters}/{report.schema_validation_results.total_tools}")
            report_lines.append(f"Valid Optional Parameters: {report.schema_validation_results.valid_optional_parameters}/{report.schema_validation_results.total_tools}")
            report_lines.append(f"Valid Schema Versions: {report.schema_validation_results.valid_schema_versions}/{report.schema_validation_results.total_tools}")
            report_lines.append(f"Average Validation Time: {report.schema_validation_results.average_validation_time_ms:.2f} ms")
            if report.schema_validation_results.failed_tools:
                report_lines.append(f"Failed Tools: {', '.join(report.schema_validation_results.failed_tools[:5])}")
                if len(report.schema_validation_results.failed_tools) > 5:
                    report_lines.append(f"   ... and {len(report.schema_validation_results.failed_tools) - 5} more")
            report_lines.append("")
        
        if report.metadata_validation_results:
            report_lines.append("DETAILED RESULTS - METADATA VALIDATION")
            report_lines.append("-" * 50)
            report_lines.append(f"Valid Descriptions: {report.metadata_validation_results.valid_descriptions}/{report.metadata_validation_results.total_tools}")
            report_lines.append(f"Valid Documentation: {report.metadata_validation_results.valid_documentation}/{report.metadata_validation_results.total_tools}")
            report_lines.append(f"Valid Examples: {report.metadata_validation_results.valid_examples}/{report.metadata_validation_results.total_tools}")
            report_lines.append(f"Complete Metadata: {report.metadata_validation_results.complete_metadata}/{report.metadata_validation_results.total_tools}")
            report_lines.append(f"Average Validation Time: {report.metadata_validation_results.average_validation_time_ms:.2f} ms")
            if report.metadata_validation_results.failed_tools:
                report_lines.append(f"Failed Tools: {', '.join(report.metadata_validation_results.failed_tools[:5])}")
                if len(report.metadata_validation_results.failed_tools) > 5:
                    report_lines.append(f"   ... and {len(report.metadata_validation_results.failed_tools) - 5} more")
            report_lines.append("")
        
        # Error Information
        if report.overall_result.error_message:
            report_lines.append("ERRORS AND ISSUES")
            report_lines.append("-" * 50)
            report_lines.append(report.overall_result.error_message)
            report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 50)
        
        if report.overall_result.overall_success:
            report_lines.append("✅ All tool registration tests passed successfully!")
            report_lines.append("   The MCP server is ready for tool execution testing (Task 2.3).")
        else:
            report_lines.append("❌ Some tool registration tests failed.")
            report_lines.append("   Recommendations:")
            
            if not report.overall_result.registration_success:
                report_lines.append("   - Fix tool registration issues before proceeding")
            
            if not report.overall_result.schema_validation_success:
                report_lines.append("   - Validate and fix tool input schemas")
            
            if not report.overall_result.metadata_validation_success:
                report_lines.append("   - Improve tool descriptions and documentation")
            
            report_lines.append("   - Review failed tools and address issues")
            report_lines.append("   - Re-run tests after fixes are implemented")
        
        report_lines.append("")
        report_lines.append("=" * 100)
        
        return "\n".join(report_lines)


def main():
    """Main function to run comprehensive tool registration tests"""
    logger.info("Starting Comprehensive Tool Registration Testing (Task 2.2)")
    
    # Initialize test runner
    runner = ToolRegistrationTestRunner()
    
    # Run all tests
    comprehensive_report = runner.run_all_tool_registration_tests()
    
    # Generate and display comprehensive report
    report_text = runner.generate_comprehensive_report(comprehensive_report)
    print(report_text)
    
    # Save comprehensive results
    runner.save_comprehensive_report(comprehensive_report)
    
    # Return success/failure based on overall results
    success = comprehensive_report.overall_result.overall_success
    logger.info(f"Comprehensive tool registration testing completed with overall success: {success}")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 