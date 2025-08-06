"""
Test Runner for Task 5.1: Inspector Documentation

This script tests all four documentation modules:
- inspector_test_documentation_template.py
- inspector_standards_compliance_guide.py
- inspector_testing_procedures.py
- inspector_troubleshooting_guide.py

Author: Inspector Development Team
Date: 2025-01-30
Version: 1.0.0
"""

import sys
import time
import traceback
from typing import List, Dict, Any


class DocumentationTestRunner:
    """Test runner for Inspector documentation modules."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.total_tests = 18
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()
        self.test_results = []
    
    def _print_progress(self, current_test: int, test_name: str):
        """Print progress information."""
        progress = (current_test / self.total_tests) * 100
        elapsed_time = time.time() - self.start_time
        estimated_total = (elapsed_time / current_test) * self.total_tests if current_test > 0 else 0
        remaining_time = estimated_total - elapsed_time
        
        print(f"\r[{current_test}/{self.total_tests}] {progress:.1f}% - {test_name} "
              f"(Elapsed: {elapsed_time:.1f}s, Remaining: {remaining_time:.1f}s)", end="", flush=True)
    
    def _record_success(self, test_name: str, details: str = ""):
        """Record a successful test."""
        self.passed_tests += 1
        self.test_results.append({
            'test': test_name,
            'status': 'PASSED',
            'details': details
        })
        print(f" ✅ PASSED")
    
    def _record_failure(self, test_name: str, error: str):
        """Record a failed test."""
        self.failed_tests += 1
        self.test_results.append({
            'test': test_name,
            'status': 'FAILED',
            'error': error
        })
        print(f" ❌ FAILED: {error}")
    
    def run_tests(self):
        """Run all documentation tests."""
        print("Inspector Documentation Test Suite")
        print("=" * 50)
        print(f"Running {self.total_tests} tests...")
        print()
        
        current_test = 0
        
        # Test 1: Documentation Template Module
        current_test += 1
        self._print_progress(current_test, "Documentation Template Module Import")
        try:
            from inspector_test_documentation_template import (
                InspectorTestDocumentationTemplate, TestStatus, TestPriority, TestCategory
            )
            self._record_success("Documentation Template Module Import")
        except Exception as e:
            self._record_failure("Documentation Template Module Import", str(e))
            return
        
        # Test 2: Documentation Template Initialization
        current_test += 1
        self._print_progress(current_test, "Documentation Template Initialization")
        try:
            doc_manager = InspectorTestDocumentationTemplate()
            assert doc_manager is not None
            assert hasattr(doc_manager, 'output_dir')
            self._record_success("Documentation Template Initialization")
        except Exception as e:
            self._record_failure("Documentation Template Initialization", str(e))
        
        # Test 3: Documentation Template Structure Creation
        current_test += 1
        self._print_progress(current_test, "Documentation Template Structure Creation")
        try:
            doc_manager = InspectorTestDocumentationTemplate()
            created_files = doc_manager.initialize_documentation_structure()
            assert len(created_files) > 0
            assert 'readme' in created_files
            self._record_success("Documentation Template Structure Creation", f"Created {len(created_files)} files")
        except Exception as e:
            self._record_failure("Documentation Template Structure Creation", str(e))
        
        # Test 4: Test Case Creation
        current_test += 1
        self._print_progress(current_test, "Test Case Creation")
        try:
            doc_manager = InspectorTestDocumentationTemplate()
            test_data = {
                'id': 'TC-TEST-001',
                'name': 'Test Case Creation Test',
                'description': 'Test the creation of test cases',
                'category': TestCategory.UNIT,
                'priority': TestPriority.HIGH,
                'prerequisites': ['Test environment'],
                'steps': ['Step 1', 'Step 2'],
                'expected_results': ['Expected result 1', 'Expected result 2'],
                'tags': ['test', 'creation']
            }
            test_case = doc_manager.create_test_case(test_data)
            assert test_case.id == 'TC-TEST-001'
            assert test_case.name == 'Test Case Creation Test'
            self._record_success("Test Case Creation")
        except Exception as e:
            self._record_failure("Test Case Creation", str(e))
        
        # Test 5: Standards Compliance Guide Module
        current_test += 1
        self._print_progress(current_test, "Standards Compliance Guide Module Import")
        try:
            from inspector_standards_compliance_guide import (
                InspectorStandardsComplianceGuide, ComplianceLevel, StandardType, ValidationStatus
            )
            self._record_success("Standards Compliance Guide Module Import")
        except Exception as e:
            self._record_failure("Standards Compliance Guide Module Import", str(e))
            return
        
        # Test 6: Standards Compliance Guide Initialization
        current_test += 1
        self._print_progress(current_test, "Standards Compliance Guide Initialization")
        try:
            guide = InspectorStandardsComplianceGuide()
            assert guide is not None
            assert len(guide.rules) > 0
            self._record_success("Standards Compliance Guide Initialization", f"Loaded {len(guide.rules)} rules")
        except Exception as e:
            self._record_failure("Standards Compliance Guide Initialization", str(e))
        
        # Test 7: JSON-RPC Validation
        current_test += 1
        self._print_progress(current_test, "JSON-RPC Message Validation")
        try:
            guide = InspectorStandardsComplianceGuide()
            valid_message = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            check = guide.validate_json_rpc_message(valid_message)
            assert check.status == ValidationStatus.PASSED
            self._record_success("JSON-RPC Message Validation")
        except Exception as e:
            self._record_failure("JSON-RPC Message Validation", str(e))
        
        # Test 8: MCP Tool Validation
        current_test += 1
        self._print_progress(current_test, "MCP Tool Registration Validation")
        try:
            guide = InspectorStandardsComplianceGuide()
            valid_tool = {
                "name": "list_files",
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    }
                }
            }
            check = guide.validate_mcp_tool_registration(valid_tool)
            assert check.status == ValidationStatus.PASSED
            self._record_success("MCP Tool Registration Validation")
        except Exception as e:
            self._record_failure("MCP Tool Registration Validation", str(e))
        
        # Test 9: Testing Procedures Module
        current_test += 1
        self._print_progress(current_test, "Testing Procedures Module Import")
        try:
            from inspector_testing_procedures import (
                InspectorTestingProcedures, TestPhase, TestEnvironment, TestPriority
            )
            self._record_success("Testing Procedures Module Import")
        except Exception as e:
            self._record_failure("Testing Procedures Module Import", str(e))
            return
        
        # Test 10: Testing Procedures Initialization
        current_test += 1
        self._print_progress(current_test, "Testing Procedures Initialization")
        try:
            procedures = InspectorTestingProcedures()
            assert procedures is not None
            assert len(procedures.procedures) > 0
            self._record_success("Testing Procedures Initialization", f"Loaded {len(procedures.procedures)} procedures")
        except Exception as e:
            self._record_failure("Testing Procedures Initialization", str(e))
        
        # Test 11: Test Suite Creation
        current_test += 1
        self._print_progress(current_test, "Test Suite Creation")
        try:
            procedures = InspectorTestingProcedures()
            suite = procedures.create_test_suite(
                suite_id="TS-TEST-001",
                name="Test Suite Creation Test",
                description="Test the creation of test suites",
                procedure_ids=["TP-MCP-001", "TP-MCP-002"]
            )
            assert suite.id == "TS-TEST-001"
            assert len(suite.procedures) > 0
            self._record_success("Test Suite Creation")
        except Exception as e:
            self._record_failure("Test Suite Creation", str(e))
        
        # Test 12: Test Procedure Execution
        current_test += 1
        self._print_progress(current_test, "Test Procedure Execution")
        try:
            procedures = InspectorTestingProcedures()
            environment_info = {"OS": "Windows", "Python": "3.12"}
            execution = procedures.execute_test_procedure("TP-MCP-001", environment_info)
            assert execution.procedure_id == "TP-MCP-001"
            assert execution.status in ["COMPLETED", "FAILED"]
            self._record_success("Test Procedure Execution")
        except Exception as e:
            self._record_failure("Test Procedure Execution", str(e))
        
        # Test 13: Troubleshooting Guide Module
        current_test += 1
        self._print_progress(current_test, "Troubleshooting Guide Module Import")
        try:
            from inspector_troubleshooting_guide import (
                InspectorTroubleshootingGuide, IssueSeverity, IssueCategory, ResolutionStatus
            )
            self._record_success("Troubleshooting Guide Module Import")
        except Exception as e:
            self._record_failure("Troubleshooting Guide Module Import", str(e))
            return
        
        # Test 14: Troubleshooting Guide Initialization
        current_test += 1
        self._print_progress(current_test, "Troubleshooting Guide Initialization")
        try:
            guide = InspectorTroubleshootingGuide()
            assert guide is not None
            assert len(guide.known_issues) > 0
            assert len(guide.solutions) > 0
            self._record_success("Troubleshooting Guide Initialization", 
                               f"Loaded {len(guide.known_issues)} issues, {len(guide.solutions)} solutions")
        except Exception as e:
            self._record_failure("Troubleshooting Guide Initialization", str(e))
        
        # Test 15: Issue Search
        current_test += 1
        self._print_progress(current_test, "Issue Search Functionality")
        try:
            guide = InspectorTroubleshootingGuide()
            issues = guide.search_issues(["connection", "refused"])
            assert len(issues) > 0
            assert any("connection" in issue.title.lower() for issue in issues)
            self._record_success("Issue Search Functionality", f"Found {len(issues)} matching issues")
        except Exception as e:
            self._record_failure("Issue Search Functionality", str(e))
        
        # Test 16: Diagnostic Execution
        current_test += 1
        self._print_progress(current_test, "Diagnostic Execution")
        try:
            guide = InspectorTroubleshootingGuide()
            environment_info = {"OS": "Windows", "Python": "3.12"}
            result = guide.run_diagnostic("KI-MCP-001", environment_info)
            assert result.issue_id == "KI-MCP-001"
            assert result.status in ["COMPLETED", "FAILED"]
            assert len(result.findings) > 0
            self._record_success("Diagnostic Execution")
        except Exception as e:
            self._record_failure("Diagnostic Execution", str(e))
        
        # Test 17: Documentation Export
        current_test += 1
        self._print_progress(current_test, "Documentation Export")
        try:
            # Test export from troubleshooting guide
            guide = InspectorTroubleshootingGuide()
            guide.export_troubleshooting_guide("test_troubleshooting_guide.md")
            
            # Test export from compliance guide
            comp_guide = InspectorStandardsComplianceGuide()
            comp_guide.export_compliance_guide("test_compliance_guide.md")
            
            # Test export from testing procedures
            proc_guide = InspectorTestingProcedures()
            proc_guide.export_testing_guide("test_testing_guide.md")
            
            self._record_success("Documentation Export", "All guides exported successfully")
        except Exception as e:
            self._record_failure("Documentation Export", str(e))
        
        # Test 18: Data Persistence
        current_test += 1
        self._print_progress(current_test, "Data Persistence")
        try:
            # Test saving and loading test case
            doc_manager = InspectorTestDocumentationTemplate()
            test_data = {
                'id': 'TC-PERSIST-001',
                'name': 'Persistence Test',
                'description': 'Test data persistence',
                'category': TestCategory.UNIT,
                'priority': TestPriority.MEDIUM,
                'prerequisites': ['Test environment'],
                'steps': ['Step 1'],
                'expected_results': ['Expected result'],
                'tags': ['persistence']
            }
            test_case = doc_manager.create_test_case(test_data)
            filepath = doc_manager.save_test_case(test_case)
            
            # Load the test case
            loaded_case = doc_manager.load_test_case('TC-PERSIST-001')
            assert loaded_case.id == test_case.id
            assert loaded_case.name == test_case.name
            
            self._record_success("Data Persistence")
        except Exception as e:
            self._record_failure("Data Persistence", str(e))
        
        # Print final results
        print("\n" + "=" * 50)
        print("TEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests / self.total_tests * 100):.1f}%")
        print(f"Total Time: {time.time() - self.start_time:.2f} seconds")
        
        if self.failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n" + "=" * 50)
        
        # Return success/failure
        return self.failed_tests == 0


def main():
    """Main function to run the documentation tests."""
    try:
        runner = DocumentationTestRunner()
        success = runner.run_tests()
        
        if success:
            print("🎉 All documentation tests passed!")
            sys.exit(0)
        else:
            print("❌ Some documentation tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test runner failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 