"""
Inspector Test Documentation Template Module

This module provides standardized templates and utilities for documenting
Inspector test cases, results, and procedures.

Author: Inspector Development Team
Date: 2025-01-30
Version: 1.0.0
"""

import os
import json
import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test status enumeration."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


class TestPriority(Enum):
    """Test priority enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TestCategory(Enum):
    """Test category enumeration."""
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    SYSTEM = "SYSTEM"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"


@dataclass
class TestCase:
    """Test case data structure."""
    id: str
    name: str
    description: str
    category: TestCategory
    priority: TestPriority
    prerequisites: List[str]
    steps: List[str]
    expected_results: List[str]
    actual_results: Optional[List[str]] = None
    status: TestStatus = TestStatus.SKIPPED
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    created_date: str = None
    last_modified: str = None
    tags: List[str] = None
    author: str = "Inspector Team"
    version: str = "1.0.0"


@dataclass
class TestSuite:
    """Test suite data structure."""
    id: str
    name: str
    description: str
    test_cases: List[TestCase]
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    execution_time: float = 0.0
    created_date: str = None
    last_modified: str = None
    version: str = "1.0.0"


@dataclass
class TestReport:
    """Test report data structure."""
    id: str
    title: str
    description: str
    test_suites: List[TestSuite]
    summary: Dict[str, Any]
    environment_info: Dict[str, str]
    execution_date: str
    duration: float
    status: str
    recommendations: List[str] = None


class InspectorTestDocumentationTemplate:
    """Main class for managing test documentation templates."""
    
    def __init__(self, output_dir: str = "docs/test_documentation"):
        """Initialize the documentation template manager.
        
        Args:
            output_dir: Directory to store documentation files
        """
        self.output_dir = output_dir
        self.templates_dir = os.path.join(output_dir, "templates")
        self.reports_dir = os.path.join(output_dir, "reports")
        self.cases_dir = os.path.join(output_dir, "test_cases")
        
        # Create directories
        for directory in [self.output_dir, self.templates_dir, 
                         self.reports_dir, self.cases_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def create_test_case_template(self, category: TestCategory = TestCategory.UNIT) -> str:
        """Create a standardized test case template.
        
        Args:
            category: Test category for the template
            
        Returns:
            Template content as string
        """
        template = f"""# Test Case Template - {category.value}

## Basic Information
- **Test ID**: TC-{datetime.datetime.now().strftime('%Y%m%d')}-001
- **Test Name**: [Enter test name]
- **Category**: {category.value}
- **Priority**: [CRITICAL/HIGH/MEDIUM/LOW]
- **Author**: [Enter author name]
- **Version**: 1.0.0
- **Created Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}
- **Last Modified**: {datetime.datetime.now().strftime('%Y-%m-%d')}

## Test Description
[Provide a clear description of what this test is designed to verify]

## Prerequisites
- [List all prerequisites that must be met before running this test]
- [Include system requirements, data setup, etc.]

## Test Steps
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]
   ...

## Expected Results
- [Expected outcome 1]
- [Expected outcome 2]
- [Expected outcome 3]
   ...

## Test Data
[Describe any specific test data required]

## Test Environment
- **Operating System**: [OS version]
- **Python Version**: [Python version]
- **Dependencies**: [List key dependencies]
- **Configuration**: [Any specific configuration]

## Tags
[Add relevant tags for categorization]

## Notes
[Any additional notes or special considerations]

---
*This template follows Inspector documentation standards*
"""
        return template
    
    def create_test_suite_template(self) -> str:
        """Create a standardized test suite template.
        
        Returns:
            Template content as string
        """
        template = f"""# Test Suite Template

## Suite Information
- **Suite ID**: TS-{datetime.datetime.now().strftime('%Y%m%d')}-001
- **Suite Name**: [Enter suite name]
- **Description**: [Provide suite description]
- **Version**: 1.0.0
- **Created Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}
- **Last Modified**: {datetime.datetime.now().strftime('%Y-%m-%d')}

## Test Cases
[List all test cases included in this suite]

### Test Case 1
- **ID**: [Test case ID]
- **Name**: [Test case name]
- **Status**: [PASSED/FAILED/SKIPPED/ERROR]

### Test Case 2
- **ID**: [Test case ID]
- **Name**: [Test case name]
- **Status**: [PASSED/FAILED/SKIPPED/ERROR]

## Execution Summary
- **Total Tests**: [Number]
- **Passed**: [Number]
- **Failed**: [Number]
- **Skipped**: [Number]
- **Execution Time**: [Duration]

## Prerequisites
[Suite-level prerequisites]

## Setup Instructions
[Instructions for setting up the test suite]

## Cleanup Instructions
[Instructions for cleaning up after test suite execution]

---
*This template follows Inspector documentation standards*
"""
        return template
    
    def create_test_report_template(self) -> str:
        """Create a standardized test report template.
        
        Returns:
            Template content as string
        """
        template = f"""# Test Report Template

## Report Information
- **Report ID**: TR-{datetime.datetime.now().strftime('%Y%m%d')}-001
- **Title**: [Enter report title]
- **Description**: [Provide report description]
- **Execution Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Duration**: [Total execution time]

## Executive Summary
[High-level summary of test execution results]

## Test Results Summary
| Metric | Count | Percentage |
|--------|-------|------------|
| Total Tests | [Number] | 100% |
| Passed | [Number] | [Percentage]% |
| Failed | [Number] | [Percentage]% |
| Skipped | [Number] | [Percentage]% |
| Errors | [Number] | [Percentage]% |

## Test Suites
[Details of each test suite executed]

### Suite 1: [Suite Name]
- **Status**: [Overall status]
- **Tests**: [Passed/Failed/Skipped counts]
- **Duration**: [Execution time]

### Suite 2: [Suite Name]
- **Status**: [Overall status]
- **Tests**: [Passed/Failed/Skipped counts]
- **Duration**: [Execution time]

## Failed Tests
[Details of failed tests]

### Failed Test 1
- **Test ID**: [ID]
- **Error**: [Error description]
- **Impact**: [Impact assessment]

## Environment Information
- **OS**: [Operating system]
- **Python**: [Python version]
- **Dependencies**: [Key dependencies]
- **Configuration**: [Configuration details]

## Recommendations
[Recommendations based on test results]

## Next Steps
[Recommended next steps]

---
*This template follows Inspector documentation standards*
"""
        return template
    
    def save_template(self, template_content: str, filename: str) -> str:
        """Save a template to file.
        
        Args:
            template_content: Template content to save
            filename: Name of the file to save
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.templates_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template_content)
            logger.info(f"Template saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save template {filename}: {e}")
            raise
    
    def create_test_case(self, test_data: Dict[str, Any]) -> TestCase:
        """Create a TestCase object from data.
        
        Args:
            test_data: Dictionary containing test case data
            
        Returns:
            TestCase object
        """
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Set default values
        test_data.setdefault('created_date', current_time)
        test_data.setdefault('last_modified', current_time)
        test_data.setdefault('tags', [])
        test_data.setdefault('author', 'Inspector Team')
        test_data.setdefault('version', '1.0.0')
        
        return TestCase(**test_data)
    
    def save_test_case(self, test_case: TestCase) -> str:
        """Save a test case to file.
        
        Args:
            test_case: TestCase object to save
            
        Returns:
            Path to the saved file
        """
        filename = f"{test_case.id}.json"
        filepath = os.path.join(self.cases_dir, filename)
        
        try:
            # Convert to dictionary with enum values as strings
            data = asdict(test_case)
            data['category'] = test_case.category.value
            data['priority'] = test_case.priority.value
            data['status'] = test_case.status.value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Test case saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save test case {test_case.id}: {e}")
            raise
    
    def load_test_case(self, test_id: str) -> TestCase:
        """Load a test case from file.
        
        Args:
            test_id: ID of the test case to load
            
        Returns:
            TestCase object
        """
        filename = f"{test_id}.json"
        filepath = os.path.join(self.cases_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string values back to enums
            data['category'] = TestCategory(data['category'])
            data['priority'] = TestPriority(data['priority'])
            data['status'] = TestStatus(data['status'])
            
            return TestCase(**data)
        except Exception as e:
            logger.error(f"Failed to load test case {test_id}: {e}")
            raise
    
    def generate_test_report(self, test_suites: List[TestSuite], 
                           environment_info: Dict[str, str]) -> TestReport:
        """Generate a test report from test suites.
        
        Args:
            test_suites: List of test suites
            environment_info: Environment information
            
        Returns:
            TestReport object
        """
        # Calculate summary statistics
        total_tests = sum(suite.total_tests for suite in test_suites)
        passed_tests = sum(suite.passed_tests for suite in test_suites)
        failed_tests = sum(suite.failed_tests for suite in test_suites)
        skipped_tests = sum(suite.skipped_tests for suite in test_suites)
        total_duration = sum(suite.execution_time for suite in test_suites)
        
        # Determine overall status
        if failed_tests > 0:
            status = "FAILED"
        elif passed_tests == total_tests:
            status = "PASSED"
        else:
            status = "PARTIAL"
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        report = TestReport(
            id=f"TR-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="Inspector Test Execution Report",
            description="Comprehensive test execution report for Inspector system",
            test_suites=test_suites,
            summary=summary,
            environment_info=environment_info,
            execution_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            duration=total_duration,
            status=status,
            recommendations=[]
        )
        
        return report
    
    def save_test_report(self, report: TestReport) -> str:
        """Save a test report to file.
        
        Args:
            report: TestReport object to save
            
        Returns:
            Path to the saved file
        """
        filename = f"{report.id}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            # Convert to dictionary with enum values as strings
            data = asdict(report)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Test report saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save test report {report.id}: {e}")
            raise
    
    def export_to_markdown(self, report: TestReport) -> str:
        """Export a test report to Markdown format.
        
        Args:
            report: TestReport object to export
            
        Returns:
            Markdown content as string
        """
        md_content = f"""# {report.title}

**Report ID**: {report.id}  
**Execution Date**: {report.execution_date}  
**Duration**: {report.duration:.2f} seconds  
**Status**: {report.status}

## Executive Summary

{report.description}

## Test Results Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Tests | {report.summary['total_tests']} | 100% |
| Passed | {report.summary['passed_tests']} | {report.summary['success_rate']:.1f}% |
| Failed | {report.summary['failed_tests']} | {(report.summary['failed_tests'] / report.summary['total_tests'] * 100) if report.summary['total_tests'] > 0 else 0:.1f}% |
| Skipped | {report.summary['skipped_tests']} | {(report.summary['skipped_tests'] / report.summary['total_tests'] * 100) if report.summary['total_tests'] > 0 else 0:.1f}% |

## Test Suites

"""
        
        for suite in report.test_suites:
            md_content += f"""### {suite.name}

- **Suite ID**: {suite.id}
- **Status**: {suite.passed_tests}/{suite.total_tests} passed
- **Duration**: {suite.execution_time:.2f} seconds
- **Description**: {suite.description}

"""
        
        md_content += f"""## Environment Information

"""
        for key, value in report.environment_info.items():
            md_content += f"- **{key}**: {value}\n"
        
        if report.recommendations:
            md_content += f"""
## Recommendations

"""
            for i, rec in enumerate(report.recommendations, 1):
                md_content += f"{i}. {rec}\n"
        
        md_content += """
---
*Generated by Inspector Test Documentation Template*
"""
        
        return md_content
    
    def get_all_templates(self) -> Dict[str, str]:
        """Get all available templates.
        
        Returns:
            Dictionary mapping template names to their content
        """
        templates = {}
        
        # Create standard templates
        templates['test_case_unit'] = self.create_test_case_template(TestCategory.UNIT)
        templates['test_case_integration'] = self.create_test_case_template(TestCategory.INTEGRATION)
        templates['test_case_system'] = self.create_test_case_template(TestCategory.SYSTEM)
        templates['test_case_performance'] = self.create_test_case_template(TestCategory.PERFORMANCE)
        templates['test_case_security'] = self.create_test_case_template(TestCategory.SECURITY)
        templates['test_case_compliance'] = self.create_test_case_template(TestCategory.COMPLIANCE)
        templates['test_suite'] = self.create_test_suite_template()
        templates['test_report'] = self.create_test_report_template()
        
        return templates
    
    def initialize_documentation_structure(self) -> Dict[str, str]:
        """Initialize the complete documentation structure.
        
        Returns:
            Dictionary of created files and their paths
        """
        created_files = {}
        
        # Create all templates
        templates = self.get_all_templates()
        for name, content in templates.items():
            filename = f"{name}_template.md"
            filepath = self.save_template(content, filename)
            created_files[name] = filepath
        
        # Create README for documentation
        readme_content = """# Inspector Test Documentation

This directory contains standardized templates and documentation for Inspector testing.

## Structure

- `templates/` - Standardized templates for test cases, suites, and reports
- `reports/` - Generated test reports
- `test_cases/` - Individual test case definitions

## Usage

1. Use the templates in `templates/` as starting points for new documentation
2. Save test cases in `test_cases/` directory
3. Generate reports in `reports/` directory

## Standards

All documentation follows Inspector documentation standards for consistency and clarity.
"""
        
        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files['readme'] = readme_path
        
        logger.info(f"Documentation structure initialized with {len(created_files)} files")
        return created_files


def main():
    """Main function to demonstrate the documentation template system."""
    print("Inspector Test Documentation Template System")
    print("=" * 50)
    
    # Initialize the documentation system
    doc_manager = InspectorTestDocumentationTemplate()
    
    # Create documentation structure
    print("Creating documentation structure...")
    created_files = doc_manager.initialize_documentation_structure()
    
    print(f"Created {len(created_files)} files:")
    for name, path in created_files.items():
        print(f"  - {name}: {path}")
    
    # Create a sample test case
    print("\nCreating sample test case...")
    sample_test_data = {
        'id': 'TC-20250130-001',
        'name': 'MCP Server Connection Test',
        'description': 'Test the MCP server connection functionality',
        'category': TestCategory.INTEGRATION,
        'priority': TestPriority.HIGH,
        'prerequisites': ['MCP server is running', 'Network connectivity'],
        'steps': [
            'Start the MCP server',
            'Establish connection to server',
            'Send test request',
            'Verify response'
        ],
        'expected_results': [
            'Server starts successfully',
            'Connection established',
            'Request processed correctly',
            'Valid response received'
        ],
        'tags': ['mcp', 'connection', 'integration']
    }
    
    test_case = doc_manager.create_test_case(sample_test_data)
    test_case_path = doc_manager.save_test_case(test_case)
    print(f"Sample test case saved: {test_case_path}")
    
    print("\nDocumentation template system ready for use!")


if __name__ == "__main__":
    main() 