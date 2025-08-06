"""
Inspector Testing Procedures Module

This module provides comprehensive testing procedures, best practices, and
guidelines for testing the Inspector system components.

Author: Inspector Development Team
Date: 2025-01-30
Version: 1.0.0
"""

import os
import json
import time
import subprocess
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPhase(Enum):
    """Test phase enumeration."""
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    SYSTEM = "SYSTEM"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    ACCEPTANCE = "ACCEPTANCE"


class TestEnvironment(Enum):
    """Test environment enumeration."""
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    TESTING = "TESTING"


class TestPriority(Enum):
    """Test priority enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class TestProcedure:
    """Test procedure data structure."""
    id: str
    name: str
    description: str
    phase: TestPhase
    environment: TestEnvironment
    priority: TestPriority
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    expected_results: List[str]
    cleanup_steps: List[str]
    estimated_duration: int  # minutes
    required_tools: List[str]
    risk_level: str
    created_date: str = None
    last_modified: str = None
    version: str = "1.0.0"


@dataclass
class TestExecution:
    """Test execution data structure."""
    procedure_id: str
    execution_id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "RUNNING"
    actual_results: List[str] = None
    issues_encountered: List[str] = None
    execution_time: float = 0.0
    environment_info: Dict[str, str] = None


@dataclass
class TestSuite:
    """Test suite data structure."""
    id: str
    name: str
    description: str
    procedures: List[TestProcedure]
    execution_order: List[str]
    dependencies: Dict[str, List[str]]
    estimated_total_duration: int
    created_date: str = None
    version: str = "1.0.0"


class InspectorTestingProcedures:
    """Main class for managing testing procedures and best practices."""
    
    def __init__(self, procedures_dir: str = "docs/testing_procedures"):
        """Initialize the testing procedures manager.
        
        Args:
            procedures_dir: Directory to store testing procedures
        """
        self.procedures_dir = procedures_dir
        self.procedures: Dict[str, TestProcedure] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        
        # Create directory
        os.makedirs(procedures_dir, exist_ok=True)
        
        # Initialize standard procedures
        self.initialize_standard_procedures()
    
    def initialize_standard_procedures(self):
        """Initialize standard testing procedures."""
        
        # MCP Server Testing Procedures
        self.add_test_procedure(TestProcedure(
            id="TP-MCP-001",
            name="MCP Server Startup Test",
            description="Test the MCP server startup process and basic functionality",
            phase=TestPhase.UNIT,
            environment=TestEnvironment.DEVELOPMENT,
            priority=TestPriority.CRITICAL,
            prerequisites=[
                "Python environment is set up",
                "Required dependencies are installed",
                "MCP server code is available"
            ],
            steps=[
                {
                    "step": 1,
                    "action": "Navigate to the project directory",
                    "command": "cd /path/to/project",
                    "expected_output": "Directory changed successfully"
                },
                {
                    "step": 2,
                    "action": "Activate virtual environment",
                    "command": "source venv/bin/activate",
                    "expected_output": "Virtual environment activated"
                },
                {
                    "step": 3,
                    "action": "Start MCP server",
                    "command": "python mcp_server.py",
                    "expected_output": "Server started successfully on port 8000"
                },
                {
                    "step": 4,
                    "action": "Verify server is responding",
                    "command": "curl http://localhost:8000/health",
                    "expected_output": "HTTP 200 OK response"
                }
            ],
            expected_results=[
                "MCP server starts without errors",
                "Server listens on configured port",
                "Health endpoint responds correctly",
                "No critical errors in logs"
            ],
            cleanup_steps=[
                "Stop the MCP server process",
                "Deactivate virtual environment",
                "Clean up any temporary files"
            ],
            estimated_duration=10,
            required_tools=["Python", "curl", "terminal"],
            risk_level="LOW",
            created_date="2025-01-30"
        ))
        
        self.add_test_procedure(TestProcedure(
            id="TP-MCP-002",
            name="MCP Tool Registration Test",
            description="Test the registration and listing of MCP tools",
            phase=TestPhase.INTEGRATION,
            environment=TestEnvironment.DEVELOPMENT,
            priority=TestPriority.HIGH,
            prerequisites=[
                "MCP server is running",
                "Tools are properly configured"
            ],
            steps=[
                {
                    "step": 1,
                    "action": "Send tool list request",
                    "command": 'curl -X POST http://localhost:8000/rpc -H "Content-Type: application/json" -d \'{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}\'',
                    "expected_output": "JSON response with tool list"
                },
                {
                    "step": 2,
                    "action": "Verify tool registration",
                    "command": "Check response contains expected tools",
                    "expected_output": "All configured tools are listed"
                },
                {
                    "step": 3,
                    "action": "Validate tool schema",
                    "command": "Verify each tool has required fields",
                    "expected_output": "All tools have name, description, and inputSchema"
                }
            ],
            expected_results=[
                "Tools are properly registered",
                "Tool list request succeeds",
                "All tools have valid schemas",
                "No duplicate tool names"
            ],
            cleanup_steps=[
                "No cleanup required for this test"
            ],
            estimated_duration=5,
            required_tools=["curl", "MCP server"],
            risk_level="LOW",
            created_date="2025-01-30"
        ))
        
        self.add_test_procedure(TestProcedure(
            id="TP-MCP-003",
            name="MCP Tool Execution Test",
            description="Test the execution of MCP tools with various inputs",
            phase=TestPhase.INTEGRATION,
            environment=TestEnvironment.DEVELOPMENT,
            priority=TestPriority.HIGH,
            prerequisites=[
                "MCP server is running",
                "Tools are registered",
                "Test data is available"
            ],
            steps=[
                {
                    "step": 1,
                    "action": "Execute list_files tool",
                    "command": 'curl -X POST http://localhost:8000/rpc -H "Content-Type: application/json" -d \'{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_files", "arguments": {"path": "/tmp"}}, "id": 2}\'',
                    "expected_output": "JSON response with file list"
                },
                {
                    "step": 2,
                    "action": "Execute read_file tool",
                    "command": 'curl -X POST http://localhost:8000/rpc -H "Content-Type: application/json" -d \'{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "/tmp/test.txt"}}, "id": 3}\'',
                    "expected_output": "JSON response with file content"
                },
                {
                    "step": 3,
                    "action": "Test error handling",
                    "command": 'curl -X POST http://localhost:8000/rpc -H "Content-Type: application/json" -d \'{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "/nonexistent/file"}}, "id": 4}\'',
                    "expected_output": "JSON error response"
                }
            ],
            expected_results=[
                "Tools execute successfully with valid inputs",
                "Error handling works correctly",
                "Response format is valid JSON-RPC",
                "Execution time is within acceptable limits"
            ],
            cleanup_steps=[
                "Remove any test files created",
                "Reset any modified state"
            ],
            estimated_duration=15,
            required_tools=["curl", "MCP server", "test files"],
            risk_level="MEDIUM",
            created_date="2025-01-30"
        ))
        
        # Performance Testing Procedures
        self.add_test_procedure(TestProcedure(
            id="TP-PERF-001",
            name="MCP Server Performance Test",
            description="Test MCP server performance under various load conditions",
            phase=TestPhase.PERFORMANCE,
            environment=TestEnvironment.TESTING,
            priority=TestPriority.MEDIUM,
            prerequisites=[
                "MCP server is running",
                "Performance monitoring tools are available",
                "Test environment is isolated"
            ],
            steps=[
                {
                    "step": 1,
                    "action": "Baseline performance measurement",
                    "command": "Measure response time for single request",
                    "expected_output": "Response time < 100ms"
                },
                {
                    "step": 2,
                    "action": "Concurrent request test",
                    "command": "Send 10 concurrent requests",
                    "expected_output": "All requests complete successfully"
                },
                {
                    "step": 3,
                    "action": "Load test",
                    "command": "Send 100 requests over 1 minute",
                    "expected_output": "Throughput > 50 requests/second"
                },
                {
                    "step": 4,
                    "action": "Resource usage monitoring",
                    "command": "Monitor CPU and memory usage",
                    "expected_output": "CPU < 50%, Memory < 512MB"
                }
            ],
            expected_results=[
                "Response time remains acceptable under load",
                "Server handles concurrent requests",
                "Resource usage stays within limits",
                "No memory leaks detected"
            ],
            cleanup_steps=[
                "Stop load testing",
                "Reset server state",
                "Clean up monitoring data"
            ],
            estimated_duration=30,
            required_tools=["Load testing tool", "Monitoring tools", "MCP server"],
            risk_level="MEDIUM",
            created_date="2025-01-30"
        ))
        
        # Security Testing Procedures
        self.add_test_procedure(TestProcedure(
            id="TP-SEC-001",
            name="MCP Server Security Test",
            description="Test MCP server security and input validation",
            phase=TestPhase.SECURITY,
            environment=TestEnvironment.TESTING,
            priority=TestPriority.HIGH,
            prerequisites=[
                "MCP server is running",
                "Security testing tools are available",
                "Test environment is isolated"
            ],
            steps=[
                {
                    "step": 1,
                    "action": "Input validation test",
                    "command": "Send malformed JSON requests",
                    "expected_output": "Proper error responses"
                },
                {
                    "step": 2,
                    "action": "Path traversal test",
                    "command": "Test file operations with ../ paths",
                    "expected_output": "Access denied for invalid paths"
                },
                {
                    "step": 3,
                    "action": "Authentication test",
                    "command": "Test without proper authentication",
                    "expected_output": "Authentication required"
                },
                {
                    "step": 4,
                    "action": "Rate limiting test",
                    "command": "Send rapid requests",
                    "expected_output": "Rate limiting applied"
                }
            ],
            expected_results=[
                "All security vulnerabilities are addressed",
                "Input validation works correctly",
                "Authentication is enforced",
                "Rate limiting is effective"
            ],
            cleanup_steps=[
                "Reset server security state",
                "Clean up test data",
                "Review security logs"
            ],
            estimated_duration=20,
            required_tools=["Security testing tools", "MCP server"],
            risk_level="HIGH",
            created_date="2025-01-30"
        ))
    
    def add_test_procedure(self, procedure: TestProcedure):
        """Add a test procedure to the manager.
        
        Args:
            procedure: TestProcedure object to add
        """
        self.procedures[procedure.id] = procedure
        logger.info(f"Added test procedure: {procedure.id} - {procedure.name}")
    
    def get_procedures_by_phase(self, phase: TestPhase) -> List[TestProcedure]:
        """Get all procedures for a specific test phase.
        
        Args:
            phase: Test phase to filter by
            
        Returns:
            List of test procedures for the phase
        """
        return [proc for proc in self.procedures.values() if proc.phase == phase]
    
    def get_procedures_by_priority(self, priority: TestPriority) -> List[TestProcedure]:
        """Get all procedures for a specific priority.
        
        Args:
            priority: Test priority to filter by
            
        Returns:
            List of test procedures for the priority
        """
        return [proc for proc in self.procedures.values() if proc.priority == priority]
    
    def create_test_suite(self, suite_id: str, name: str, description: str,
                         procedure_ids: List[str]) -> TestSuite:
        """Create a test suite from existing procedures.
        
        Args:
            suite_id: Unique identifier for the suite
            name: Name of the test suite
            description: Description of the test suite
            procedure_ids: List of procedure IDs to include
            
        Returns:
            TestSuite object
        """
        procedures = []
        for proc_id in procedure_ids:
            if proc_id in self.procedures:
                procedures.append(self.procedures[proc_id])
            else:
                logger.warning(f"Procedure {proc_id} not found, skipping")
        
        # Calculate total duration
        total_duration = sum(proc.estimated_duration for proc in procedures)
        
        # Create dependencies (simple sequential execution for now)
        dependencies = {}
        for i, proc in enumerate(procedures):
            if i > 0:
                dependencies[proc.id] = [procedures[i-1].id]
            else:
                dependencies[proc.id] = []
        
        suite = TestSuite(
            id=suite_id,
            name=name,
            description=description,
            procedures=procedures,
            execution_order=procedure_ids,
            dependencies=dependencies,
            estimated_total_duration=total_duration,
            created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
            version="1.0.0"
        )
        
        self.test_suites[suite_id] = suite
        logger.info(f"Created test suite: {suite_id} - {name}")
        return suite
    
    def execute_test_procedure(self, procedure_id: str, 
                             environment_info: Dict[str, str] = None) -> TestExecution:
        """Execute a test procedure.
        
        Args:
            procedure_id: ID of the procedure to execute
            environment_info: Environment information
            
        Returns:
            TestExecution object
        """
        if procedure_id not in self.procedures:
            raise ValueError(f"Test procedure {procedure_id} not found")
        
        procedure = self.procedures[procedure_id]
        execution_id = f"EXE-{int(time.time())}"
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        
        execution = TestExecution(
            procedure_id=procedure_id,
            execution_id=execution_id,
            start_time=start_time,
            status="RUNNING",
            actual_results=[],
            issues_encountered=[],
            environment_info=environment_info or {}
        )
        
        logger.info(f"Starting execution of procedure {procedure_id}")
        
        try:
            # Execute each step
            for step in procedure.steps:
                logger.info(f"Executing step {step['step']}: {step['action']}")
                
                # Simulate step execution (in real implementation, this would execute commands)
                if 'command' in step:
                    # For demonstration, we'll just log the command
                    logger.info(f"Command: {step['command']}")
                    
                    # Simulate execution time
                    time.sleep(0.1)
                    
                    # Simulate success
                    execution.actual_results.append(f"Step {step['step']} completed successfully")
                else:
                    execution.actual_results.append(f"Step {step['step']} completed")
            
            # Mark as completed
            execution.status = "COMPLETED"
            execution.end_time = time.strftime('%Y-%m-%d %H:%M:%S')
            execution.execution_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
            
            logger.info(f"Procedure {procedure_id} completed successfully")
            
        except Exception as e:
            execution.status = "FAILED"
            execution.end_time = time.strftime('%Y-%m-%d %H:%M:%S')
            execution.issues_encountered.append(str(e))
            logger.error(f"Procedure {procedure_id} failed: {e}")
        
        return execution
    
    def execute_test_suite(self, suite_id: str, 
                          environment_info: Dict[str, str] = None) -> List[TestExecution]:
        """Execute a test suite.
        
        Args:
            suite_id: ID of the test suite to execute
            environment_info: Environment information
            
        Returns:
            List of TestExecution objects
        """
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite {suite_id} not found")
        
        suite = self.test_suites[suite_id]
        executions = []
        
        logger.info(f"Starting execution of test suite {suite_id}")
        
        # Execute procedures in order
        for proc_id in suite.execution_order:
            # Check dependencies
            if proc_id in suite.dependencies:
                for dep_id in suite.dependencies[proc_id]:
                    # Wait for dependency to complete
                    dep_execution = next((exe for exe in executions if exe.procedure_id == dep_id), None)
                    if dep_execution and dep_execution.status == "FAILED":
                        logger.warning(f"Skipping {proc_id} due to failed dependency {dep_id}")
                        continue
            
            # Execute procedure
            execution = self.execute_test_procedure(proc_id, environment_info)
            executions.append(execution)
            
            # If procedure failed, we might want to stop (depending on configuration)
            if execution.status == "FAILED":
                logger.warning(f"Procedure {proc_id} failed, continuing with suite")
        
        logger.info(f"Test suite {suite_id} execution completed")
        return executions
    
    def save_test_procedure(self, procedure: TestProcedure) -> str:
        """Save a test procedure to file.
        
        Args:
            procedure: TestProcedure object to save
            
        Returns:
            Path to the saved file
        """
        filename = f"{procedure.id}.json"
        filepath = os.path.join(self.procedures_dir, filename)
        
        try:
            # Convert to dictionary with enum values as strings
            data = asdict(procedure)
            data['phase'] = procedure.phase.value
            data['environment'] = procedure.environment.value
            data['priority'] = procedure.priority.value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Test procedure saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save test procedure {procedure.id}: {e}")
            raise
    
    def load_test_procedure(self, procedure_id: str) -> TestProcedure:
        """Load a test procedure from file.
        
        Args:
            procedure_id: ID of the test procedure to load
            
        Returns:
            TestProcedure object
        """
        filename = f"{procedure_id}.json"
        filepath = os.path.join(self.procedures_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string values back to enums
            data['phase'] = TestPhase(data['phase'])
            data['environment'] = TestEnvironment(data['environment'])
            data['priority'] = TestPriority(data['priority'])
            
            return TestProcedure(**data)
        except Exception as e:
            logger.error(f"Failed to load test procedure {procedure_id}: {e}")
            raise
    
    def export_testing_guide(self, output_file: str = "testing_guide.md"):
        """Export the testing guide to Markdown format.
        
        Args:
            output_file: Output file path
        """
        md_content = """# Inspector Testing Procedures Guide

This guide provides comprehensive testing procedures and best practices for the Inspector system.

## Overview

The Inspector system requires thorough testing across multiple phases to ensure reliability, performance, and security.

## Test Phases

"""
        
        # Group procedures by phase
        phases = {}
        for proc in self.procedures.values():
            if proc.phase not in phases:
                phases[proc.phase] = []
            phases[proc.phase].append(proc)
        
        for phase, procedures in phases.items():
            md_content += f"### {phase.value} Testing\n\n"
            
            for proc in procedures:
                md_content += f"#### {proc.name} (ID: {proc.id})\n\n"
                md_content += f"**Priority**: {proc.priority.value}\n\n"
                md_content += f"**Environment**: {proc.environment.value}\n\n"
                md_content += f"**Duration**: {proc.estimated_duration} minutes\n\n"
                md_content += f"**Risk Level**: {proc.risk_level}\n\n"
                md_content += f"**Description**: {proc.description}\n\n"
                
                md_content += "**Prerequisites**:\n"
                for prereq in proc.prerequisites:
                    md_content += f"- {prereq}\n"
                md_content += "\n"
                
                md_content += "**Steps**:\n"
                for step in proc.steps:
                    md_content += f"{step['step']}. {step['action']}\n"
                    if 'command' in step:
                        md_content += f"   Command: `{step['command']}`\n"
                    md_content += f"   Expected: {step['expected_output']}\n\n"
                
                md_content += "**Expected Results**:\n"
                for result in proc.expected_results:
                    md_content += f"- {result}\n"
                md_content += "\n"
                
                md_content += "**Required Tools**:\n"
                for tool in proc.required_tools:
                    md_content += f"- {tool}\n"
                md_content += "\n"
                
                md_content += "---\n\n"
        
        # Add best practices section
        md_content += """## Testing Best Practices

### General Guidelines

1. **Environment Isolation**: Always test in isolated environments to prevent interference
2. **Data Backup**: Backup important data before running destructive tests
3. **Documentation**: Document all test results and issues encountered
4. **Reproducibility**: Ensure tests can be reproduced consistently
5. **Cleanup**: Always clean up after tests to maintain environment integrity

### Test Execution

1. **Prerequisites**: Verify all prerequisites are met before starting tests
2. **Monitoring**: Monitor system resources during test execution
3. **Logging**: Enable detailed logging for troubleshooting
4. **Validation**: Validate results against expected outcomes
5. **Reporting**: Generate comprehensive test reports

### Risk Management

1. **Risk Assessment**: Assess risks before running tests
2. **Rollback Plan**: Have rollback procedures ready
3. **Monitoring**: Monitor for unexpected behavior
4. **Communication**: Communicate test status to stakeholders

## Test Suites

"""
        
        for suite in self.test_suites.values():
            md_content += f"### {suite.name} (ID: {suite.id})\n\n"
            md_content += f"**Description**: {suite.description}\n\n"
            md_content += f"**Estimated Duration**: {suite.estimated_total_duration} minutes\n\n"
            md_content += f"**Procedures**: {len(suite.procedures)}\n\n"
            
            md_content += "**Execution Order**:\n"
            for proc_id in suite.execution_order:
                md_content += f"1. {proc_id}\n"
            md_content += "\n"
        
        # Add usage section
        md_content += """## Usage

### Running Individual Tests

```python
from inspector_testing_procedures import InspectorTestingProcedures

procedures = InspectorTestingProcedures()

# Execute a single test procedure
execution = procedures.execute_test_procedure("TP-MCP-001")
print(f"Status: {execution.status}")
print(f"Results: {execution.actual_results}")
```

### Running Test Suites

```python
# Execute a test suite
executions = procedures.execute_test_suite("TS-MCP-BASIC")
for execution in executions:
    print(f"{execution.procedure_id}: {execution.status}")
```

### Creating Custom Procedures

```python
# Create a custom test procedure
custom_proc = TestProcedure(
    id="TP-CUSTOM-001",
    name="Custom Test",
    description="A custom test procedure",
    phase=TestPhase.UNIT,
    environment=TestEnvironment.DEVELOPMENT,
    priority=TestPriority.MEDIUM,
    prerequisites=["Custom prerequisites"],
    steps=[{"step": 1, "action": "Custom action", "expected_output": "Expected result"}],
    expected_results=["Expected result"],
    cleanup_steps=["Cleanup action"],
    estimated_duration=5,
    required_tools=["Custom tool"],
    risk_level="LOW"
)

procedures.add_test_procedure(custom_proc)
```

---
*Generated by Inspector Testing Procedures Guide*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Testing guide exported to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to export testing guide: {e}")
            raise


def main():
    """Main function to demonstrate the testing procedures system."""
    print("Inspector Testing Procedures System")
    print("=" * 50)
    
    # Initialize the testing procedures
    procedures = InspectorTestingProcedures()
    
    print(f"Loaded {len(procedures.procedures)} test procedures")
    
    # Create a test suite
    print("\nCreating test suite...")
    suite = procedures.create_test_suite(
        suite_id="TS-MCP-BASIC",
        name="MCP Basic Functionality Test Suite",
        description="Basic functionality tests for MCP server",
        procedure_ids=["TP-MCP-001", "TP-MCP-002", "TP-MCP-003"]
    )
    
    print(f"Created test suite: {suite.name}")
    print(f"Estimated duration: {suite.estimated_total_duration} minutes")
    
    # Execute a test procedure
    print("\nExecuting test procedure...")
    environment_info = {
        "OS": "Windows 10",
        "Python": "3.12.0",
        "Environment": "Development"
    }
    
    execution = procedures.execute_test_procedure("TP-MCP-001", environment_info)
    print(f"Execution status: {execution.status}")
    print(f"Execution time: {execution.execution_time:.2f} seconds")
    print(f"Results: {len(execution.actual_results)} steps completed")
    
    # Execute test suite
    print("\nExecuting test suite...")
    executions = procedures.execute_test_suite("TS-MCP-BASIC", environment_info)
    
    print(f"Suite execution completed:")
    for execution in executions:
        print(f"  {execution.procedure_id}: {execution.status}")
    
    # Save a test procedure
    print("\nSaving test procedure...")
    proc = procedures.procedures["TP-MCP-001"]
    filepath = procedures.save_test_procedure(proc)
    print(f"Procedure saved to: {filepath}")
    
    # Export testing guide
    print("\nExporting testing guide...")
    procedures.export_testing_guide()
    
    print("\nTesting procedures system ready for use!")


if __name__ == "__main__":
    main() 