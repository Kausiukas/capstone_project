"""
Inspector Standards Compliance Guide Module

This module provides comprehensive guidance and validation tools for ensuring
compliance with JSON-RPC 2.0, MCP (Model Context Protocol), and other relevant
standards for the Inspector system.

Author: Inspector Development Team
Date: 2025-01-30
Version: 1.0.0
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance level enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class StandardType(Enum):
    """Standard type enumeration."""
    JSON_RPC_2_0 = "JSON-RPC 2.0"
    MCP = "Model Context Protocol"
    HTTP = "HTTP"
    WEBSOCKET = "WebSocket"
    SECURITY = "Security"
    PERFORMANCE = "Performance"


class ValidationStatus(Enum):
    """Validation status enumeration."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ComplianceRule:
    """Compliance rule data structure."""
    id: str
    name: str
    description: str
    standard: StandardType
    level: ComplianceLevel
    category: str
    rule_type: str  # 'format', 'semantic', 'security', 'performance'
    validation_logic: str
    examples: List[Dict[str, Any]]
    references: List[str]
    created_date: str = None
    version: str = "1.0.0"


@dataclass
class ComplianceCheck:
    """Compliance check data structure."""
    rule_id: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    timestamp: str
    execution_time: float


@dataclass
class ComplianceReport:
    """Compliance report data structure."""
    id: str
    title: str
    description: str
    standard: StandardType
    checks: List[ComplianceCheck]
    summary: Dict[str, Any]
    recommendations: List[str]
    execution_date: str
    duration: float


class InspectorStandardsComplianceGuide:
    """Main class for managing standards compliance guidance and validation."""
    
    def __init__(self):
        """Initialize the compliance guide."""
        self.rules: Dict[str, ComplianceRule] = {}
        self.initialize_compliance_rules()
    
    def initialize_compliance_rules(self):
        """Initialize the standard compliance rules."""
        
        # JSON-RPC 2.0 Rules
        self.add_compliance_rule(ComplianceRule(
            id="JSON-RPC-001",
            name="JSON-RPC 2.0 Message Format",
            description="Validate that messages follow JSON-RPC 2.0 specification format",
            standard=StandardType.JSON_RPC_2_0,
            level=ComplianceLevel.CRITICAL,
            category="Message Format",
            rule_type="format",
            validation_logic="Check for required fields: jsonrpc, method, params, id",
            examples=[
                {
                    "valid": {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 1
                    },
                    "invalid": {
                        "method": "tools/list",
                        "params": {}
                    }
                }
            ],
            references=["https://www.jsonrpc.org/specification"],
            created_date="2025-01-30"
        ))
        
        self.add_compliance_rule(ComplianceRule(
            id="JSON-RPC-002",
            name="JSON-RPC 2.0 Response Format",
            description="Validate that responses follow JSON-RPC 2.0 specification format",
            standard=StandardType.JSON_RPC_2_0,
            level=ComplianceLevel.CRITICAL,
            category="Response Format",
            rule_type="format",
            validation_logic="Check for required fields: jsonrpc, result/error, id",
            examples=[
                {
                    "valid": {
                        "jsonrpc": "2.0",
                        "result": {"tools": []},
                        "id": 1
                    },
                    "invalid": {
                        "result": {"tools": []},
                        "id": 1
                    }
                }
            ],
            references=["https://www.jsonrpc.org/specification"],
            created_date="2025-01-30"
        ))
        
        self.add_compliance_rule(ComplianceRule(
            id="JSON-RPC-003",
            name="JSON-RPC 2.0 Error Handling",
            description="Validate proper error handling according to JSON-RPC 2.0 specification",
            standard=StandardType.JSON_RPC_2_0,
            level=ComplianceLevel.HIGH,
            category="Error Handling",
            rule_type="semantic",
            validation_logic="Check error object has code, message, and optional data",
            examples=[
                {
                    "valid": {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": "Method not found"
                        },
                        "id": 1
                    },
                    "invalid": {
                        "jsonrpc": "2.0",
                        "error": "Method not found",
                        "id": 1
                    }
                }
            ],
            references=["https://www.jsonrpc.org/specification"],
            created_date="2025-01-30"
        ))
        
        # MCP Rules
        self.add_compliance_rule(ComplianceRule(
            id="MCP-001",
            name="MCP Tool Registration",
            description="Validate proper tool registration according to MCP specification",
            standard=StandardType.MCP,
            level=ComplianceLevel.CRITICAL,
            category="Tool Management",
            rule_type="semantic",
            validation_logic="Check tool registration includes name, description, inputSchema",
            examples=[
                {
                    "valid": {
                        "name": "list_files",
                        "description": "List files in a directory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            }
                        }
                    },
                    "invalid": {
                        "name": "list_files",
                        "description": "List files in a directory"
                    }
                }
            ],
            references=["https://modelcontextprotocol.io/spec"],
            created_date="2025-01-30"
        ))
        
        self.add_compliance_rule(ComplianceRule(
            id="MCP-002",
            name="MCP Tool Execution",
            description="Validate proper tool execution according to MCP specification",
            standard=StandardType.MCP,
            level=ComplianceLevel.CRITICAL,
            category="Tool Execution",
            rule_type="semantic",
            validation_logic="Check tool execution includes proper arguments and error handling",
            examples=[
                {
                    "valid": {
                        "name": "list_files",
                        "arguments": {"path": "/tmp"}
                    },
                    "invalid": {
                        "name": "list_files",
                        "args": {"path": "/tmp"}
                    }
                }
            ],
            references=["https://modelcontextprotocol.io/spec"],
            created_date="2025-01-30"
        ))
        
        # Security Rules
        self.add_compliance_rule(ComplianceRule(
            id="SEC-001",
            name="Input Validation",
            description="Validate all inputs to prevent injection attacks",
            standard=StandardType.SECURITY,
            level=ComplianceLevel.CRITICAL,
            category="Input Security",
            rule_type="security",
            validation_logic="Check for proper input sanitization and validation",
            examples=[
                {
                    "valid": "Sanitized input with proper validation",
                    "invalid": "Raw user input without validation"
                }
            ],
            references=["OWASP Input Validation Guidelines"],
            created_date="2025-01-30"
        ))
        
        self.add_compliance_rule(ComplianceRule(
            id="SEC-002",
            name="Authentication and Authorization",
            description="Validate proper authentication and authorization mechanisms",
            standard=StandardType.SECURITY,
            level=ComplianceLevel.CRITICAL,
            category="Access Control",
            rule_type="security",
            validation_logic="Check for proper authentication and authorization checks",
            examples=[
                {
                    "valid": "Proper token validation and role-based access",
                    "invalid": "No authentication or authorization checks"
                }
            ],
            references=["OWASP Authentication Guidelines"],
            created_date="2025-01-30"
        ))
        
        # Performance Rules
        self.add_compliance_rule(ComplianceRule(
            id="PERF-001",
            name="Response Time",
            description="Validate response times meet performance requirements",
            standard=StandardType.PERFORMANCE,
            level=ComplianceLevel.HIGH,
            category="Performance",
            rule_type="performance",
            validation_logic="Check response time is within acceptable limits",
            examples=[
                {
                    "valid": "Response time < 1000ms",
                    "invalid": "Response time > 5000ms"
                }
            ],
            references=["Performance Best Practices"],
            created_date="2025-01-30"
        ))
        
        self.add_compliance_rule(ComplianceRule(
            id="PERF-002",
            name="Resource Usage",
            description="Validate resource usage is within acceptable limits",
            standard=StandardType.PERFORMANCE,
            level=ComplianceLevel.MEDIUM,
            category="Resource Management",
            rule_type="performance",
            validation_logic="Check memory and CPU usage are within limits",
            examples=[
                {
                    "valid": "Memory usage < 512MB, CPU < 50%",
                    "invalid": "Memory usage > 2GB, CPU > 90%"
                }
            ],
            references=["Resource Management Guidelines"],
            created_date="2025-01-30"
        ))
    
    def add_compliance_rule(self, rule: ComplianceRule):
        """Add a compliance rule to the guide.
        
        Args:
            rule: ComplianceRule object to add
        """
        self.rules[rule.id] = rule
        logger.info(f"Added compliance rule: {rule.id} - {rule.name}")
    
    def get_rules_by_standard(self, standard: StandardType) -> List[ComplianceRule]:
        """Get all rules for a specific standard.
        
        Args:
            standard: Standard type to filter by
            
        Returns:
            List of compliance rules for the standard
        """
        return [rule for rule in self.rules.values() if rule.standard == standard]
    
    def get_rules_by_level(self, level: ComplianceLevel) -> List[ComplianceRule]:
        """Get all rules for a specific compliance level.
        
        Args:
            level: Compliance level to filter by
            
        Returns:
            List of compliance rules for the level
        """
        return [rule for rule in self.rules.values() if rule.level == level]
    
    def validate_json_rpc_message(self, message: Dict[str, Any]) -> ComplianceCheck:
        """Validate a JSON-RPC 2.0 message.
        
        Args:
            message: JSON-RPC message to validate
            
        Returns:
            ComplianceCheck result
        """
        import time
        start_time = time.time()
        
        # Get JSON-RPC rules
        json_rpc_rules = self.get_rules_by_standard(StandardType.JSON_RPC_2_0)
        
        for rule in json_rpc_rules:
            if rule.id == "JSON-RPC-001":  # Message Format
                # Check required fields
                required_fields = ["jsonrpc", "method", "params", "id"]
                missing_fields = [field for field in required_fields if field not in message]
                
                if missing_fields:
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message=f"Missing required fields: {missing_fields}",
                        details={"missing_fields": missing_fields, "message": message},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                # Check jsonrpc version
                if message.get("jsonrpc") != "2.0":
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Invalid jsonrpc version, must be '2.0'",
                        details={"expected": "2.0", "actual": message.get("jsonrpc")},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
        
        return ComplianceCheck(
            rule_id="JSON-RPC-001",
            status=ValidationStatus.PASSED,
            message="JSON-RPC message format is valid",
            details={"message": message},
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            execution_time=time.time() - start_time
        )
    
    def validate_json_rpc_response(self, response: Dict[str, Any]) -> ComplianceCheck:
        """Validate a JSON-RPC 2.0 response.
        
        Args:
            response: JSON-RPC response to validate
            
        Returns:
            ComplianceCheck result
        """
        import time
        start_time = time.time()
        
        # Get JSON-RPC rules
        json_rpc_rules = self.get_rules_by_standard(StandardType.JSON_RPC_2_0)
        
        for rule in json_rpc_rules:
            if rule.id == "JSON-RPC-002":  # Response Format
                # Check required fields
                required_fields = ["jsonrpc", "id"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if missing_fields:
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message=f"Missing required fields: {missing_fields}",
                        details={"missing_fields": missing_fields, "response": response},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                # Check jsonrpc version
                if response.get("jsonrpc") != "2.0":
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Invalid jsonrpc version, must be '2.0'",
                        details={"expected": "2.0", "actual": response.get("jsonrpc")},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                # Check for result or error (but not both)
                has_result = "result" in response
                has_error = "error" in response
                
                if not has_result and not has_error:
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Response must contain either 'result' or 'error'",
                        details={"response": response},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                if has_result and has_error:
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Response cannot contain both 'result' and 'error'",
                        details={"response": response},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
        
        return ComplianceCheck(
            rule_id="JSON-RPC-002",
            status=ValidationStatus.PASSED,
            message="JSON-RPC response format is valid",
            details={"response": response},
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            execution_time=time.time() - start_time
        )
    
    def validate_mcp_tool_registration(self, tool: Dict[str, Any]) -> ComplianceCheck:
        """Validate MCP tool registration.
        
        Args:
            tool: MCP tool registration to validate
            
        Returns:
            ComplianceCheck result
        """
        import time
        start_time = time.time()
        
        # Get MCP rules
        mcp_rules = self.get_rules_by_standard(StandardType.MCP)
        
        for rule in mcp_rules:
            if rule.id == "MCP-001":  # Tool Registration
                # Check required fields
                required_fields = ["name", "description", "inputSchema"]
                missing_fields = [field for field in required_fields if field not in tool]
                
                if missing_fields:
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message=f"Missing required fields: {missing_fields}",
                        details={"missing_fields": missing_fields, "tool": tool},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                # Check field types
                if not isinstance(tool.get("name"), str):
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Tool name must be a string",
                        details={"tool": tool},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                if not isinstance(tool.get("description"), str):
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Tool description must be a string",
                        details={"tool": tool},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
                
                if not isinstance(tool.get("inputSchema"), dict):
                    return ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Tool inputSchema must be an object",
                        details={"tool": tool},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    )
        
        return ComplianceCheck(
            rule_id="MCP-001",
            status=ValidationStatus.PASSED,
            message="MCP tool registration is valid",
            details={"tool": tool},
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            execution_time=time.time() - start_time
        )
    
    def validate_performance_metrics(self, metrics: Dict[str, Any]) -> List[ComplianceCheck]:
        """Validate performance metrics.
        
        Args:
            metrics: Performance metrics to validate
            
        Returns:
            List of ComplianceCheck results
        """
        import time
        checks = []
        
        # Get performance rules
        perf_rules = self.get_rules_by_standard(StandardType.PERFORMANCE)
        
        for rule in perf_rules:
            start_time = time.time()
            
            if rule.id == "PERF-001":  # Response Time
                response_time = metrics.get("response_time", 0)
                if response_time > 1000:  # 1 second threshold
                    checks.append(ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message=f"Response time {response_time}ms exceeds 1000ms threshold",
                        details={"response_time": response_time, "threshold": 1000},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    ))
                else:
                    checks.append(ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.PASSED,
                        message=f"Response time {response_time}ms is within acceptable limits",
                        details={"response_time": response_time, "threshold": 1000},
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    ))
            
            elif rule.id == "PERF-002":  # Resource Usage
                memory_usage = metrics.get("memory_usage", 0)
                cpu_usage = metrics.get("cpu_usage", 0)
                
                memory_ok = memory_usage < 512  # 512MB threshold
                cpu_ok = cpu_usage < 50  # 50% threshold
                
                if not memory_ok or not cpu_ok:
                    checks.append(ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.FAILED,
                        message="Resource usage exceeds limits",
                        details={
                            "memory_usage": memory_usage,
                            "cpu_usage": cpu_usage,
                            "memory_threshold": 512,
                            "cpu_threshold": 50
                        },
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    ))
                else:
                    checks.append(ComplianceCheck(
                        rule_id=rule.id,
                        status=ValidationStatus.PASSED,
                        message="Resource usage is within acceptable limits",
                        details={
                            "memory_usage": memory_usage,
                            "cpu_usage": cpu_usage,
                            "memory_threshold": 512,
                            "cpu_threshold": 50
                        },
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        execution_time=time.time() - start_time
                    ))
        
        return checks
    
    def generate_compliance_report(self, checks: List[ComplianceCheck], 
                                 standard: StandardType) -> ComplianceReport:
        """Generate a compliance report from validation checks.
        
        Args:
            checks: List of compliance checks
            standard: Standard type for the report
            
        Returns:
            ComplianceReport object
        """
        import time
        
        # Calculate summary statistics
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check.status == ValidationStatus.PASSED)
        failed_checks = sum(1 for check in checks if check.status == ValidationStatus.FAILED)
        warning_checks = sum(1 for check in checks if check.status == ValidationStatus.WARNING)
        
        total_time = sum(check.execution_time for check in checks)
        
        # Determine overall status
        if failed_checks > 0:
            status = "FAILED"
        elif passed_checks == total_checks:
            status = "PASSED"
        else:
            status = "PARTIAL"
        
        summary = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'warning_checks': warning_checks,
            'compliance_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }
        
        # Generate recommendations
        recommendations = []
        if failed_checks > 0:
            recommendations.append(f"Address {failed_checks} failed compliance checks")
        if warning_checks > 0:
            recommendations.append(f"Review {warning_checks} warning compliance checks")
        if passed_checks < total_checks:
            recommendations.append("Improve overall compliance rate")
        
        report = ComplianceReport(
            id=f"CR-{int(time.time())}",
            title=f"{standard.value} Compliance Report",
            description=f"Compliance validation report for {standard.value}",
            standard=standard,
            checks=checks,
            summary=summary,
            recommendations=recommendations,
            execution_date=time.strftime('%Y-%m-%d %H:%M:%S'),
            duration=total_time
        )
        
        return report
    
    def export_compliance_guide(self, output_file: str = "compliance_guide.md"):
        """Export the compliance guide to Markdown format.
        
        Args:
            output_file: Output file path
        """
        md_content = """# Inspector Standards Compliance Guide

This guide provides comprehensive information about compliance requirements for the Inspector system.

## Overview

The Inspector system must comply with multiple standards to ensure interoperability, security, and performance.

## Standards Covered

"""
        
        # Group rules by standard
        standards = {}
        for rule in self.rules.values():
            if rule.standard not in standards:
                standards[rule.standard] = []
            standards[rule.standard].append(rule)
        
        for standard, rules in standards.items():
            md_content += f"### {standard.value}\n\n"
            
            for rule in rules:
                md_content += f"#### {rule.name} (ID: {rule.id})\n\n"
                md_content += f"**Level**: {rule.level.value}\n\n"
                md_content += f"**Category**: {rule.category}\n\n"
                md_content += f"**Description**: {rule.description}\n\n"
                md_content += f"**Validation Logic**: {rule.validation_logic}\n\n"
                
                if rule.examples:
                    md_content += "**Examples**:\n\n"
                    for example in rule.examples:
                        for key, value in example.items():
                            md_content += f"- **{key.title()}**:\n"
                            md_content += f"  ```json\n"
                            md_content += f"  {json.dumps(value, indent=2)}\n"
                            md_content += f"  ```\n\n"
                
                if rule.references:
                    md_content += "**References**:\n"
                    for ref in rule.references:
                        md_content += f"- {ref}\n"
                    md_content += "\n"
                
                md_content += "---\n\n"
        
        # Add usage section
        md_content += """## Usage

### Validation Functions

The compliance guide provides several validation functions:

- `validate_json_rpc_message()` - Validate JSON-RPC 2.0 messages
- `validate_json_rpc_response()` - Validate JSON-RPC 2.0 responses
- `validate_mcp_tool_registration()` - Validate MCP tool registrations
- `validate_performance_metrics()` - Validate performance metrics

### Example Usage

```python
from inspector_standards_compliance_guide import InspectorStandardsComplianceGuide

guide = InspectorStandardsComplianceGuide()

# Validate JSON-RPC message
message = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}
check = guide.validate_json_rpc_message(message)
print(f"Status: {check.status}")
print(f"Message: {check.message}")
```

## Compliance Levels

- **CRITICAL**: Must be implemented for basic functionality
- **HIGH**: Important for production use
- **MEDIUM**: Recommended for best practices
- **LOW**: Optional improvements

---
*Generated by Inspector Standards Compliance Guide*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Compliance guide exported to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to export compliance guide: {e}")
            raise


def main():
    """Main function to demonstrate the compliance guide system."""
    print("Inspector Standards Compliance Guide System")
    print("=" * 50)
    
    # Initialize the compliance guide
    guide = InspectorStandardsComplianceGuide()
    
    print(f"Loaded {len(guide.rules)} compliance rules")
    
    # Test JSON-RPC validation
    print("\nTesting JSON-RPC validation...")
    
    # Valid message
    valid_message = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    check = guide.validate_json_rpc_message(valid_message)
    print(f"Valid message check: {check.status} - {check.message}")
    
    # Invalid message
    invalid_message = {
        "method": "tools/list",
        "params": {}
    }
    
    check = guide.validate_json_rpc_message(invalid_message)
    print(f"Invalid message check: {check.status} - {check.message}")
    
    # Test MCP validation
    print("\nTesting MCP validation...")
    
    # Valid tool registration
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
    print(f"Valid tool check: {check.status} - {check.message}")
    
    # Test performance validation
    print("\nTesting performance validation...")
    
    metrics = {
        "response_time": 500,  # 500ms
        "memory_usage": 256,   # 256MB
        "cpu_usage": 25        # 25%
    }
    
    checks = guide.validate_performance_metrics(metrics)
    for check in checks:
        print(f"Performance check {check.rule_id}: {check.status} - {check.message}")
    
    # Generate compliance report
    print("\nGenerating compliance report...")
    all_checks = [check] + checks  # Combine checks from different validations
    report = guide.generate_compliance_report(all_checks, StandardType.JSON_RPC_2_0)
    
    print(f"Report ID: {report.id}")
    print(f"Status: {report.status}")
    print(f"Compliance Rate: {report.summary['compliance_rate']:.1f}%")
    
    # Export compliance guide
    print("\nExporting compliance guide...")
    guide.export_compliance_guide()
    
    print("\nCompliance guide system ready for use!")


if __name__ == "__main__":
    main() 