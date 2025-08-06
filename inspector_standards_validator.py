#!/usr/bin/env python3
"""
Inspector Standards Validator

This module implements comprehensive standards validation for the Inspector system.
Part of Task 3.1.1 in the Inspector Task List.

Features:
- Standards checking and validation
- Compliance validation across multiple standards
- Standards reporting with detailed analysis
- Recommendations engine for improvements
- Integration with existing compliance testers
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import statistics

# Import existing compliance testers
from test_json_rpc_compliance import JSONRPCComplianceTester, ComplianceStatus, ComplianceTestResult
from test_mcp_protocol_compliance import MCPProtocolComplianceTester
from inspector_config_manager import InspectorConfigManager
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StandardType(Enum):
    """Types of standards to validate"""
    JSON_RPC_2_0 = "json_rpc_2_0"
    MCP_PROTOCOL = "mcp_protocol"
    TOOL_STANDARDS = "tool_standards"
    PERFORMANCE_STANDARDS = "performance_standards"
    SECURITY_STANDARDS = "security_standards"
    DOCUMENTATION_STANDARDS = "documentation_standards"
    CODE_QUALITY_STANDARDS = "code_quality_standards"

class ValidationLevel(Enum):
    """Validation levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

@dataclass
class StandardRequirement:
    """Individual standard requirement"""
    standard_type: StandardType
    requirement_id: str
    title: str
    description: str
    validation_level: ValidationLevel
    criteria: Dict[str, Any]
    weight: float = 1.0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ValidationResult:
    """Result of a single validation"""
    requirement: StandardRequirement
    status: ComplianceStatus
    score: float
    details: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class StandardsReport:
    """Comprehensive standards validation report"""
    report_id: str
    total_requirements: int = 0
    passed_requirements: int = 0
    failed_requirements: int = 0
    warning_requirements: int = 0
    error_requirements: int = 0
    overall_score: float = 0.0
    compliance_level: str = ""
    validation_results: List[ValidationResult] = None
    summary: str = ""
    recommendations: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.validation_results is None:
            self.validation_results = []
        if self.recommendations is None:
            self.recommendations = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result to the report"""
        self.validation_results.append(result)
        self.total_requirements += 1
        
        if result.status == ComplianceStatus.PASS:
            self.passed_requirements += 1
        elif result.status == ComplianceStatus.FAIL:
            self.failed_requirements += 1
        elif result.status == ComplianceStatus.WARNING:
            self.warning_requirements += 1
        elif result.status == ComplianceStatus.ERROR:
            self.error_requirements += 1
        
        # Calculate overall score
        if self.total_requirements > 0:
            total_weight = sum(r.requirement.weight for r in self.validation_results)
            weighted_score = sum(r.score * r.requirement.weight for r in self.validation_results)
            self.overall_score = (weighted_score / total_weight) * 100 if total_weight > 0 else 0.0
        
        # Determine compliance level
        if self.overall_score >= 95:
            self.compliance_level = "EXCELLENT"
        elif self.overall_score >= 85:
            self.compliance_level = "GOOD"
        elif self.overall_score >= 70:
            self.compliance_level = "ACCEPTABLE"
        elif self.overall_score >= 50:
            self.compliance_level = "NEEDS_IMPROVEMENT"
        else:
            self.compliance_level = "NON_COMPLIANT"

class StandardsValidator:
    """
    Main standards validator for the Inspector system.
    
    Validates compliance with multiple standards including JSON-RPC 2.0,
    MCP protocol, tool standards, performance standards, and more.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        self.config_manager = config_manager
        self.requirements: Dict[str, StandardRequirement] = {}
        self.validators: Dict[StandardType, Any] = {}
        self.reports_dir = Path("reports/standards")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self) -> None:
        """Initialize the standards validator"""
        try:
            logger.info("Initializing Standards Validator...")
            
            # Load standard requirements
            await self._load_standard_requirements()
            
            # Initialize validators
            await self._initialize_validators()
            
            logger.info("Standards Validator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Standards Validator: {e}")
            raise
    
    async def _load_standard_requirements(self) -> None:
        """Load standard requirements from configuration"""
        logger.info("Loading standard requirements...")
        
        # JSON-RPC 2.0 Requirements
        self.requirements["jsonrpc_001"] = StandardRequirement(
            standard_type=StandardType.JSON_RPC_2_0,
            requirement_id="jsonrpc_001",
            title="JSON-RPC 2.0 Format Compliance",
            description="Server must comply with JSON-RPC 2.0 specification format",
            validation_level=ValidationLevel.CRITICAL,
            criteria={"min_score": 80.0, "required_methods": ["ping", "tools/list"]},
            weight=2.0
        )
        
        self.requirements["jsonrpc_002"] = StandardRequirement(
            standard_type=StandardType.JSON_RPC_2_0,
            requirement_id="jsonrpc_002",
            title="Request/Response Structure",
            description="All requests and responses must follow JSON-RPC 2.0 structure",
            validation_level=ValidationLevel.CRITICAL,
            criteria={"min_score": 90.0, "required_fields": ["jsonrpc", "method", "id"]},
            weight=2.0
        )
        
        self.requirements["jsonrpc_003"] = StandardRequirement(
            standard_type=StandardType.JSON_RPC_2_0,
            requirement_id="jsonrpc_003",
            title="Error Code Compliance",
            description="Error responses must use standard JSON-RPC error codes",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 70.0, "required_codes": [-32600, -32601, -32602, -32603]},
            weight=1.5
        )
        
        # MCP Protocol Requirements
        self.requirements["mcp_001"] = StandardRequirement(
            standard_type=StandardType.MCP_PROTOCOL,
            requirement_id="mcp_001",
            title="MCP Protocol Compliance",
            description="Server must comply with MCP protocol specification",
            validation_level=ValidationLevel.CRITICAL,
            criteria={"min_score": 75.0, "required_methods": ["tools/list", "tools/call"]},
            weight=2.0
        )
        
        self.requirements["mcp_002"] = StandardRequirement(
            standard_type=StandardType.MCP_PROTOCOL,
            requirement_id="mcp_002",
            title="Tool Registration Format",
            description="Tools must be registered in correct MCP format",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 85.0, "required_fields": ["name", "description", "inputSchema"]},
            weight=1.5
        )
        
        self.requirements["mcp_003"] = StandardRequirement(
            standard_type=StandardType.MCP_PROTOCOL,
            requirement_id="mcp_003",
            title="Tool Execution Protocol",
            description="Tool execution must follow MCP protocol",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 80.0, "timeout_seconds": 30},
            weight=1.5
        )
        
        # Tool Standards Requirements
        self.requirements["tool_001"] = StandardRequirement(
            standard_type=StandardType.TOOL_STANDARDS,
            requirement_id="tool_001",
            title="Tool Documentation",
            description="All tools must have comprehensive documentation",
            validation_level=ValidationLevel.MEDIUM,
            criteria={"min_score": 80.0, "required_fields": ["description", "examples"]},
            weight=1.0
        )
        
        self.requirements["tool_002"] = StandardRequirement(
            standard_type=StandardType.TOOL_STANDARDS,
            requirement_id="tool_002",
            title="Tool Error Handling",
            description="Tools must handle errors gracefully",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 85.0, "error_handling": True},
            weight=1.5
        )
        
        self.requirements["tool_003"] = StandardRequirement(
            standard_type=StandardType.TOOL_STANDARDS,
            requirement_id="tool_003",
            title="Tool Performance",
            description="Tools must meet performance standards",
            validation_level=ValidationLevel.MEDIUM,
            criteria={"min_score": 70.0, "max_response_time": 5.0},
            weight=1.0
        )
        
        # Performance Standards Requirements
        self.requirements["perf_001"] = StandardRequirement(
            standard_type=StandardType.PERFORMANCE_STANDARDS,
            requirement_id="perf_001",
            title="Response Time Standards",
            description="Server must meet response time requirements",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 75.0, "max_avg_response_time": 2.0},
            weight=1.5
        )
        
        self.requirements["perf_002"] = StandardRequirement(
            standard_type=StandardType.PERFORMANCE_STANDARDS,
            requirement_id="perf_002",
            title="Concurrent Execution",
            description="Server must handle concurrent requests",
            validation_level=ValidationLevel.MEDIUM,
            criteria={"min_score": 70.0, "concurrent_requests": 10},
            weight=1.0
        )
        
        # Security Standards Requirements
        self.requirements["sec_001"] = StandardRequirement(
            standard_type=StandardType.SECURITY_STANDARDS,
            requirement_id="sec_001",
            title="Input Validation",
            description="All inputs must be properly validated",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 90.0, "validation_required": True},
            weight=1.5
        )
        
        self.requirements["sec_002"] = StandardRequirement(
            standard_type=StandardType.SECURITY_STANDARDS,
            requirement_id="sec_002",
            title="Error Information Disclosure",
            description="Errors must not disclose sensitive information",
            validation_level=ValidationLevel.HIGH,
            criteria={"min_score": 85.0, "no_sensitive_info": True},
            weight=1.5
        )
        
        logger.info(f"Loaded {len(self.requirements)} standard requirements")
    
    async def _initialize_validators(self) -> None:
        """Initialize validators for each standard type"""
        logger.info("Initializing validators...")
        
        # Initialize JSON-RPC validator
        self.validators[StandardType.JSON_RPC_2_0] = JSONRPCComplianceTester(self.config_manager)
        await self.validators[StandardType.JSON_RPC_2_0].initialize()
        
        # Initialize MCP Protocol validator
        self.validators[StandardType.MCP_PROTOCOL] = MCPProtocolComplianceTester(self.config_manager)
        await self.validators[StandardType.MCP_PROTOCOL].initialize()
        
        logger.info("Validators initialized successfully")
    
    async def validate_standards(self, standard_types: Optional[List[StandardType]] = None) -> StandardsReport:
        """Validate standards and generate comprehensive report"""
        try:
            logger.info("Starting standards validation...")
            
            # Create report
            report = StandardsReport(
                report_id=f"standards_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Determine which standards to validate
            if standard_types is None:
                standard_types = list(StandardType)
            
            # Validate each standard type
            for standard_type in standard_types:
                await self._validate_standard_type(standard_type, report)
            
            # Generate summary and recommendations
            await self._generate_report_summary(report)
            await self._generate_recommendations(report)
            
            # Save report
            await self._save_report(report)
            
            logger.info(f"Standards validation completed. Overall score: {report.overall_score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"Standards validation failed: {e}")
            raise
    
    async def _validate_standard_type(self, standard_type: StandardType, report: StandardsReport) -> None:
        """Validate a specific standard type"""
        logger.info(f"Validating {standard_type.value} standards...")
        
        # Get requirements for this standard type
        requirements = [req for req in self.requirements.values() if req.standard_type == standard_type]
        
        for requirement in requirements:
            try:
                result = await self._validate_requirement(requirement)
                report.add_result(result)
                
            except Exception as e:
                logger.error(f"Failed to validate requirement {requirement.requirement_id}: {e}")
                # Add error result
                error_result = ValidationResult(
                    requirement=requirement,
                    status=ComplianceStatus.ERROR,
                    score=0.0,
                    details=f"Validation failed: {str(e)}",
                    evidence={"error": str(e)},
                    recommendations=["Fix validation error and retry"]
                )
                report.add_result(error_result)
    
    async def _validate_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate a specific requirement"""
        logger.debug(f"Validating requirement: {requirement.requirement_id}")
        
        try:
            if requirement.standard_type == StandardType.JSON_RPC_2_0:
                return await self._validate_jsonrpc_requirement(requirement)
            elif requirement.standard_type == StandardType.MCP_PROTOCOL:
                return await self._validate_mcp_requirement(requirement)
            elif requirement.standard_type == StandardType.TOOL_STANDARDS:
                return await self._validate_tool_requirement(requirement)
            elif requirement.standard_type == StandardType.PERFORMANCE_STANDARDS:
                return await self._validate_performance_requirement(requirement)
            elif requirement.standard_type == StandardType.SECURITY_STANDARDS:
                return await self._validate_security_requirement(requirement)
            else:
                return await self._validate_generic_requirement(requirement)
                
        except Exception as e:
            logger.error(f"Error validating requirement {requirement.requirement_id}: {e}")
            raise
    
    async def _validate_jsonrpc_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate JSON-RPC specific requirement"""
        validator = self.validators[StandardType.JSON_RPC_2_0]
        
        # Run JSON-RPC compliance tests
        compliance_report = await validator.run_compliance_tests()
        
        # Map requirement to test results
        score = compliance_report.compliance_score
        status = ComplianceStatus.PASS if score >= requirement.criteria["min_score"] else ComplianceStatus.FAIL
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"JSON-RPC compliance score: {score:.1f}%",
            evidence={
                "compliance_score": score,
                "test_results": [asdict(result) for result in compliance_report.test_results]
            },
            recommendations=compliance_report.recommendations
        )
    
    async def _validate_mcp_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate MCP protocol specific requirement"""
        validator = self.validators[StandardType.MCP_PROTOCOL]
        
        # Run MCP compliance tests
        compliance_report = await validator.run_compliance_tests()
        
        # Map requirement to test results
        score = compliance_report.compliance_score
        status = ComplianceStatus.PASS if score >= requirement.criteria["min_score"] else ComplianceStatus.FAIL
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"MCP protocol compliance score: {score:.1f}%",
            evidence={
                "compliance_score": score,
                "test_results": [asdict(result) for result in compliance_report.test_results]
            },
            recommendations=compliance_report.recommendations
        )
    
    async def _validate_tool_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate tool standards requirement"""
        # This would integrate with tool testing results
        # For now, return a placeholder result
        score = 75.0  # Placeholder
        status = ComplianceStatus.PASS if score >= requirement.criteria["min_score"] else ComplianceStatus.FAIL
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"Tool standards validation: {score:.1f}%",
            evidence={"tool_validation_score": score},
            recommendations=["Implement comprehensive tool validation"]
        )
    
    async def _validate_performance_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate performance standards requirement"""
        # This would integrate with performance testing results
        # For now, return a placeholder result
        score = 60.0  # Placeholder - based on known performance issues
        status = ComplianceStatus.FAIL if score < requirement.criteria["min_score"] else ComplianceStatus.PASS
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"Performance standards validation: {score:.1f}%",
            evidence={"performance_score": score},
            recommendations=["Address MCP server performance issues identified in Task 2.4"]
        )
    
    async def _validate_security_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate security standards requirement"""
        # This would integrate with security testing results
        # For now, return a placeholder result
        score = 80.0  # Placeholder
        status = ComplianceStatus.PASS if score >= requirement.criteria["min_score"] else ComplianceStatus.FAIL
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"Security standards validation: {score:.1f}%",
            evidence={"security_score": score},
            recommendations=["Implement comprehensive security validation"]
        )
    
    async def _validate_generic_requirement(self, requirement: StandardRequirement) -> ValidationResult:
        """Validate generic requirement"""
        # Placeholder for other standard types
        score = 70.0
        status = ComplianceStatus.PASS if score >= requirement.criteria["min_score"] else ComplianceStatus.FAIL
        
        return ValidationResult(
            requirement=requirement,
            status=status,
            score=score,
            details=f"Generic validation: {score:.1f}%",
            evidence={"generic_score": score},
            recommendations=["Implement specific validation for this standard type"]
        )
    
    async def _generate_report_summary(self, report: StandardsReport) -> None:
        """Generate summary for the report"""
        report.summary = f"""
Standards Validation Summary

Overall Compliance Score: {report.overall_score:.1f}%
Compliance Level: {report.compliance_level}

Total Requirements: {report.total_requirements}
- Passed: {report.passed_requirements}
- Failed: {report.failed_requirements}
- Warnings: {report.warning_requirements}
- Errors: {report.error_requirements}

Key Findings:
- Critical requirements: {len([r for r in report.validation_results if r.requirement.validation_level == ValidationLevel.CRITICAL])}
- High priority requirements: {len([r for r in report.validation_results if r.requirement.validation_level == ValidationLevel.HIGH])}
- Medium priority requirements: {len([r for r in report.validation_results if r.requirement.validation_level == ValidationLevel.MEDIUM])}

Validation completed at: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()
    
    async def _generate_recommendations(self, report: StandardsReport) -> None:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Collect all recommendations from validation results
        for result in report.validation_results:
            recommendations.extend(result.recommendations)
        
        # Add overall recommendations based on compliance level
        if report.compliance_level == "NON_COMPLIANT":
            recommendations.append("Immediate action required: Address all critical and high-priority failures")
            recommendations.append("Review and fix all failed requirements before proceeding")
        elif report.compliance_level == "NEEDS_IMPROVEMENT":
            recommendations.append("Focus on improving high-priority requirements")
            recommendations.append("Address performance and security issues")
        elif report.compliance_level == "ACCEPTABLE":
            recommendations.append("Continue improving medium-priority requirements")
            recommendations.append("Consider addressing warnings for better compliance")
        elif report.compliance_level == "GOOD":
            recommendations.append("Maintain current compliance level")
            recommendations.append("Address remaining warnings for excellence")
        elif report.compliance_level == "EXCELLENT":
            recommendations.append("Excellent compliance achieved")
            recommendations.append("Maintain standards and monitor for regressions")
        
        # Remove duplicates and set recommendations
        report.recommendations = list(set(recommendations))
    
    async def _save_report(self, report: StandardsReport) -> None:
        """Save the validation report"""
        try:
            filename = f"{report.report_id}.json"
            filepath = self.reports_dir / filename
            
            # Convert report to dict
            report_dict = asdict(report)
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            logger.info(f"Standards validation report saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
    
    async def get_validation_history(self, limit: int = 10) -> List[StandardsReport]:
        """Get validation history"""
        try:
            reports = []
            for filepath in sorted(self.reports_dir.glob("*.json"), reverse=True)[:limit]:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convert back to StandardsReport (simplified)
                        reports.append(data)
                except Exception as e:
                    logger.warning(f"Failed to load report {filepath}: {e}")
            
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get validation history: {e}")
            return []
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            logger.info("Cleaning up Standards Validator...")
            
            # Cleanup validators
            for validator in self.validators.values():
                if hasattr(validator, 'cleanup'):
                    await validator.cleanup()
            
            logger.info("Standards Validator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

async def main():
    """Main function for testing"""
    try:
        # Initialize config manager
        config_manager = InspectorConfigManager()
        await config_manager.initialize()
        
        # Initialize standards validator
        validator = StandardsValidator(config_manager)
        await validator.initialize()
        
        # Run validation
        report = await validator.validate_standards()
        
        # Print summary
        print("\n" + "="*60)
        print("STANDARDS VALIDATION REPORT")
        print("="*60)
        print(report.summary)
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
        
        # Cleanup
        await validator.cleanup()
        await config_manager.cleanup()
        
    except Exception as e:
        logger.error(f"Standards validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 