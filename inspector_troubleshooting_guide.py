"""
Inspector Troubleshooting Guide Module

This module provides comprehensive troubleshooting procedures and solutions
for common issues encountered with the Inspector system.

Author: Inspector Development Team
Date: 2025-01-30
Version: 1.0.0
"""

import os
import json
import time
import subprocess
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Issue severity enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IssueCategory(Enum):
    """Issue category enumeration."""
    CONNECTION = "CONNECTION"
    PERFORMANCE = "PERFORMANCE"
    CONFIGURATION = "CONFIGURATION"
    SECURITY = "SECURITY"
    COMPATIBILITY = "COMPATIBILITY"
    RESOURCE = "RESOURCE"
    NETWORK = "NETWORK"
    SOFTWARE = "SOFTWARE"


class ResolutionStatus(Enum):
    """Resolution status enumeration."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


@dataclass
class TroubleshootingStep:
    """Troubleshooting step data structure."""
    step_number: int
    description: str
    command: Optional[str] = None
    expected_output: Optional[str] = None
    notes: Optional[str] = None
    risk_level: str = "LOW"


@dataclass
class IssueSolution:
    """Issue solution data structure."""
    id: str
    title: str
    description: str
    steps: List[TroubleshootingStep]
    verification_steps: List[str]
    prevention_tips: List[str]
    related_issues: List[str]
    created_date: str = None
    last_updated: str = None
    success_rate: float = 0.0
    version: str = "1.0.0"


@dataclass
class KnownIssue:
    """Known issue data structure."""
    id: str
    title: str
    description: str
    category: IssueCategory
    severity: IssueSeverity
    symptoms: List[str]
    root_cause: str
    solutions: List[IssueSolution]
    affected_versions: List[str]
    workarounds: List[str]
    status: ResolutionStatus
    created_date: str = None
    last_updated: str = None
    version: str = "1.0.0"


@dataclass
class DiagnosticResult:
    """Diagnostic result data structure."""
    issue_id: str
    diagnostic_id: str
    timestamp: str
    status: str
    findings: List[str]
    recommendations: List[str]
    execution_time: float
    environment_info: Dict[str, str] = None


class InspectorTroubleshootingGuide:
    """Main class for managing troubleshooting procedures and solutions."""
    
    def __init__(self, issues_dir: str = "docs/troubleshooting"):
        """Initialize the troubleshooting guide manager.
        
        Args:
            issues_dir: Directory to store troubleshooting data
        """
        self.issues_dir = issues_dir
        self.known_issues: Dict[str, KnownIssue] = {}
        self.solutions: Dict[str, IssueSolution] = {}
        
        # Create directory
        os.makedirs(issues_dir, exist_ok=True)
        
        # Initialize known issues
        self.initialize_known_issues()
    
    def initialize_known_issues(self):
        """Initialize known issues and their solutions."""
        
        # MCP Server Connection Issues
        self.add_known_issue(KnownIssue(
            id="KI-MCP-001",
            title="MCP Server Connection Refused",
            description="Unable to connect to MCP server - connection refused error",
            category=IssueCategory.CONNECTION,
            severity=IssueSeverity.CRITICAL,
            symptoms=[
                "Connection refused error when trying to connect to MCP server",
                "Server not responding on expected port",
                "Timeout errors during connection attempts"
            ],
            root_cause="MCP server is not running or not listening on the expected port",
            solutions=[],
            affected_versions=["All versions"],
            workarounds=[
                "Check if MCP server process is running",
                "Verify port configuration",
                "Check firewall settings"
            ],
            status=ResolutionStatus.RESOLVED,
            created_date="2025-01-30"
        ))
        
        # Add solution for MCP connection issue
        connection_solution = IssueSolution(
            id="SOL-MCP-001",
            title="Start MCP Server",
            description="Step-by-step procedure to start the MCP server and resolve connection issues",
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    description="Check if MCP server process is running",
                    command="ps aux | grep mcp_server",
                    expected_output="Process list showing mcp_server.py",
                    notes="Look for mcp_server.py in the process list"
                ),
                TroubleshootingStep(
                    step_number=2,
                    description="Navigate to project directory",
                    command="cd /path/to/project",
                    expected_output="Directory changed successfully",
                    notes="Replace with actual project path"
                ),
                TroubleshootingStep(
                    step_number=3,
                    description="Activate virtual environment",
                    command="source venv/bin/activate",
                    expected_output="Virtual environment activated",
                    notes="Use appropriate activation command for your OS"
                ),
                TroubleshootingStep(
                    step_number=4,
                    description="Start MCP server",
                    command="python mcp_server.py",
                    expected_output="Server started successfully on port 8000",
                    notes="Check for any error messages during startup"
                ),
                TroubleshootingStep(
                    step_number=5,
                    description="Verify server is responding",
                    command="curl http://localhost:8000/health",
                    expected_output="HTTP 200 OK response",
                    notes="Test basic connectivity to the server"
                )
            ],
            verification_steps=[
                "Server process is running",
                "Server responds to health check",
                "No error messages in server logs",
                "Port 8000 is listening"
            ],
            prevention_tips=[
                "Use systemd service for automatic startup",
                "Monitor server process with health checks",
                "Implement automatic restart on failure",
                "Use proper logging for debugging"
            ],
            related_issues=["KI-MCP-002", "KI-MCP-003"],
            created_date="2025-01-30",
            success_rate=95.0
        )
        
        self.add_solution(connection_solution)
        
        # Update the known issue with the solution
        self.known_issues["KI-MCP-001"].solutions.append(connection_solution)
        
        # MCP Server Performance Issues
        self.add_known_issue(KnownIssue(
            id="KI-MCP-002",
            title="MCP Server High Response Time",
            description="MCP server responding slowly to requests",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.HIGH,
            symptoms=[
                "Response times > 1000ms",
                "Server becomes unresponsive under load",
                "High CPU or memory usage",
                "Request timeouts"
            ],
            root_cause="Resource constraints, inefficient code, or high system load",
            solutions=[],
            affected_versions=["All versions"],
            workarounds=[
                "Restart the server",
                "Reduce concurrent requests",
                "Monitor system resources"
            ],
            status=ResolutionStatus.IN_PROGRESS,
            created_date="2025-01-30"
        ))
        
        # Add solution for performance issue
        performance_solution = IssueSolution(
            id="SOL-MCP-002",
            title="Optimize MCP Server Performance",
            description="Steps to diagnose and resolve performance issues",
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    description="Monitor system resources",
                    command="top -p $(pgrep -f mcp_server)",
                    expected_output="Resource usage statistics",
                    notes="Check CPU and memory usage"
                ),
                TroubleshootingStep(
                    step_number=2,
                    description="Check server logs for errors",
                    command="tail -f logs/mcp_server.log",
                    expected_output="Recent log entries",
                    notes="Look for error messages or warnings"
                ),
                TroubleshootingStep(
                    step_number=3,
                    description="Test response time",
                    command="curl -w '@-' -o /dev/null -s http://localhost:8000/health",
                    expected_output="Response time < 100ms",
                    notes="Measure actual response time"
                ),
                TroubleshootingStep(
                    step_number=4,
                    description="Check for memory leaks",
                    command="ps aux | grep mcp_server",
                    expected_output="Memory usage not increasing",
                    notes="Monitor memory usage over time"
                ),
                TroubleshootingStep(
                    step_number=5,
                    description="Restart server if needed",
                    command="pkill -f mcp_server && python mcp_server.py",
                    expected_output="Server restarted successfully",
                    notes="Restart if performance issues persist"
                )
            ],
            verification_steps=[
                "Response time < 100ms",
                "CPU usage < 50%",
                "Memory usage < 512MB",
                "No error messages in logs"
            ],
            prevention_tips=[
                "Implement connection pooling",
                "Use async/await for I/O operations",
                "Monitor performance metrics",
                "Implement caching where appropriate"
            ],
            related_issues=["KI-MCP-001", "KI-MCP-003"],
            created_date="2025-01-30",
            success_rate=85.0
        )
        
        self.add_solution(performance_solution)
        self.known_issues["KI-MCP-002"].solutions.append(performance_solution)
        
        # Configuration Issues
        self.add_known_issue(KnownIssue(
            id="KI-MCP-003",
            title="MCP Server Configuration Error",
            description="Server fails to start due to configuration issues",
            category=IssueCategory.CONFIGURATION,
            severity=IssueSeverity.HIGH,
            symptoms=[
                "Server fails to start",
                "Configuration file not found",
                "Invalid configuration parameters",
                "Permission denied errors"
            ],
            root_cause="Missing or invalid configuration files, incorrect permissions",
            solutions=[],
            affected_versions=["All versions"],
            workarounds=[
                "Check configuration file syntax",
                "Verify file permissions",
                "Use default configuration"
            ],
            status=ResolutionStatus.RESOLVED,
            created_date="2025-01-30"
        ))
        
        # Add solution for configuration issue
        config_solution = IssueSolution(
            id="SOL-MCP-003",
            title="Fix MCP Server Configuration",
            description="Steps to resolve configuration issues",
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    description="Check configuration file exists",
                    command="ls -la config/",
                    expected_output="Configuration files listed",
                    notes="Verify config directory and files exist"
                ),
                TroubleshootingStep(
                    step_number=2,
                    description="Validate configuration syntax",
                    command="python -c \"import yaml; yaml.safe_load(open('config/config.yaml'))\"",
                    expected_output="No syntax errors",
                    notes="Check for YAML syntax errors"
                ),
                TroubleshootingStep(
                    step_number=3,
                    description="Check file permissions",
                    command="ls -la config/config.yaml",
                    expected_output="Readable by current user",
                    notes="Ensure proper read permissions"
                ),
                TroubleshootingStep(
                    step_number=4,
                    description="Create default configuration if missing",
                    command="cp config/config.yaml.example config/config.yaml",
                    expected_output="Default config created",
                    notes="Use example config as template"
                ),
                TroubleshootingStep(
                    step_number=5,
                    description="Test configuration",
                    command="python -c \"from config import load_config; load_config()\"",
                    expected_output="Configuration loaded successfully",
                    notes="Verify configuration can be loaded"
                )
            ],
            verification_steps=[
                "Configuration file exists",
                "No syntax errors in config",
                "Proper file permissions",
                "Server starts successfully"
            ],
            prevention_tips=[
                "Use configuration validation",
                "Implement configuration templates",
                "Document configuration options",
                "Use environment variables for sensitive data"
            ],
            related_issues=["KI-MCP-001", "KI-MCP-002"],
            created_date="2025-01-30",
            success_rate=90.0
        )
        
        self.add_solution(config_solution)
        self.known_issues["KI-MCP-003"].solutions.append(config_solution)
        
        # Security Issues
        self.add_known_issue(KnownIssue(
            id="KI-MCP-004",
            title="MCP Server Security Vulnerability",
            description="Potential security vulnerabilities in MCP server",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.CRITICAL,
            symptoms=[
                "Unauthorized access attempts",
                "Suspicious log entries",
                "Unexpected file access",
                "Authentication failures"
            ],
            root_cause="Missing security measures, weak authentication, or input validation issues",
            solutions=[],
            affected_versions=["All versions"],
            workarounds=[
                "Enable authentication",
                "Implement rate limiting",
                "Review access logs"
            ],
            status=ResolutionStatus.IN_PROGRESS,
            created_date="2025-01-30"
        ))
        
        # Add solution for security issue
        security_solution = IssueSolution(
            id="SOL-MCP-004",
            title="Implement MCP Server Security",
            description="Steps to implement security measures",
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    description="Review current security settings",
                    command="grep -r 'auth\\|security' config/",
                    expected_output="Security configuration found",
                    notes="Check existing security settings"
                ),
                TroubleshootingStep(
                    step_number=2,
                    description="Enable authentication",
                    command="Add authentication middleware to server",
                    expected_output="Authentication enabled",
                    notes="Implement proper authentication"
                ),
                TroubleshootingStep(
                    step_number=3,
                    description="Implement rate limiting",
                    command="Add rate limiting to API endpoints",
                    expected_output="Rate limiting active",
                    notes="Prevent abuse and DoS attacks"
                ),
                TroubleshootingStep(
                    step_number=4,
                    description="Validate input data",
                    command="Add input validation to all endpoints",
                    expected_output="Input validation active",
                    notes="Prevent injection attacks"
                ),
                TroubleshootingStep(
                    step_number=5,
                    description="Monitor security logs",
                    command="tail -f logs/security.log",
                    expected_output="Security events logged",
                    notes="Monitor for suspicious activity"
                )
            ],
            verification_steps=[
                "Authentication is required",
                "Rate limiting is active",
                "Input validation works",
                "Security logs are generated"
            ],
            prevention_tips=[
                "Regular security audits",
                "Keep dependencies updated",
                "Use HTTPS in production",
                "Implement proper logging"
            ],
            related_issues=["KI-MCP-001", "KI-MCP-003"],
            created_date="2025-01-30",
            success_rate=80.0
        )
        
        self.add_solution(security_solution)
        self.known_issues["KI-MCP-004"].solutions.append(security_solution)
    
    def add_known_issue(self, issue: KnownIssue):
        """Add a known issue to the guide.
        
        Args:
            issue: KnownIssue object to add
        """
        self.known_issues[issue.id] = issue
        logger.info(f"Added known issue: {issue.id} - {issue.title}")
    
    def add_solution(self, solution: IssueSolution):
        """Add a solution to the guide.
        
        Args:
            solution: IssueSolution object to add
        """
        self.solutions[solution.id] = solution
        logger.info(f"Added solution: {solution.id} - {solution.title}")
    
    def search_issues(self, keywords: List[str]) -> List[KnownIssue]:
        """Search for issues by keywords.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching known issues
        """
        matching_issues = []
        
        for issue in self.known_issues.values():
            # Search in title, description, and symptoms
            search_text = f"{issue.title} {issue.description} {' '.join(issue.symptoms)}".lower()
            
            for keyword in keywords:
                if keyword.lower() in search_text:
                    matching_issues.append(issue)
                    break
        
        return matching_issues
    
    def get_issues_by_category(self, category: IssueCategory) -> List[KnownIssue]:
        """Get all issues for a specific category.
        
        Args:
            category: Issue category to filter by
            
        Returns:
            List of known issues for the category
        """
        return [issue for issue in self.known_issues.values() if issue.category == category]
    
    def get_issues_by_severity(self, severity: IssueSeverity) -> List[KnownIssue]:
        """Get all issues for a specific severity.
        
        Args:
            severity: Issue severity to filter by
            
        Returns:
            List of known issues for the severity
        """
        return [issue for issue in self.known_issues.values() if issue.severity == severity]
    
    def run_diagnostic(self, issue_id: str, environment_info: Dict[str, str] = None) -> DiagnosticResult:
        """Run diagnostic tests for a specific issue.
        
        Args:
            issue_id: ID of the issue to diagnose
            environment_info: Environment information
            
        Returns:
            DiagnosticResult object
        """
        if issue_id not in self.known_issues:
            raise ValueError(f"Known issue {issue_id} not found")
        
        issue = self.known_issues[issue_id]
        diagnostic_id = f"DIAG-{int(time.time())}"
        start_time = time.time()
        
        findings = []
        recommendations = []
        
        logger.info(f"Running diagnostic for issue {issue_id}")
        
        try:
            # Run diagnostic based on issue category
            if issue.category == IssueCategory.CONNECTION:
                findings, recommendations = self._diagnose_connection_issue()
            elif issue.category == IssueCategory.PERFORMANCE:
                findings, recommendations = self._diagnose_performance_issue()
            elif issue.category == IssueCategory.CONFIGURATION:
                findings, recommendations = self._diagnose_configuration_issue()
            elif issue.category == IssueCategory.SECURITY:
                findings, recommendations = self._diagnose_security_issue()
            else:
                findings = ["Generic diagnostic completed"]
                recommendations = ["Review issue details and apply appropriate solutions"]
            
            execution_time = time.time() - start_time
            
            result = DiagnosticResult(
                issue_id=issue_id,
                diagnostic_id=diagnostic_id,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                status="COMPLETED",
                findings=findings,
                recommendations=recommendations,
                execution_time=execution_time,
                environment_info=environment_info or {}
            )
            
            logger.info(f"Diagnostic completed for issue {issue_id}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = DiagnosticResult(
                issue_id=issue_id,
                diagnostic_id=diagnostic_id,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                status="FAILED",
                findings=[f"Diagnostic failed: {str(e)}"],
                recommendations=["Review error and retry diagnostic"],
                execution_time=execution_time,
                environment_info=environment_info or {}
            )
            
            logger.error(f"Diagnostic failed for issue {issue_id}: {e}")
            return result
    
    def _diagnose_connection_issue(self) -> tuple[List[str], List[str]]:
        """Diagnose connection-related issues.
        
        Returns:
            Tuple of (findings, recommendations)
        """
        findings = []
        recommendations = []
        
        try:
            # Check if server is running
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'mcp_server' in result.stdout:
                findings.append("MCP server process is running")
            else:
                findings.append("MCP server process is not running")
                recommendations.append("Start the MCP server")
            
            # Check if port is listening
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            if ':8000' in result.stdout:
                findings.append("Port 8000 is listening")
            else:
                findings.append("Port 8000 is not listening")
                recommendations.append("Check server configuration and restart")
            
            # Test connectivity
            result = subprocess.run(['curl', '-s', 'http://localhost:8000/health'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                findings.append("Server responds to health check")
            else:
                findings.append("Server does not respond to health check")
                recommendations.append("Check server logs for errors")
                
        except Exception as e:
            findings.append(f"Diagnostic error: {str(e)}")
            recommendations.append("Review system environment and permissions")
        
        return findings, recommendations
    
    def _diagnose_performance_issue(self) -> tuple[List[str], List[str]]:
        """Diagnose performance-related issues.
        
        Returns:
            Tuple of (findings, recommendations)
        """
        findings = []
        recommendations = []
        
        try:
            # Check system resources
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            if result.returncode == 0:
                findings.append("System resource information collected")
                # Parse CPU and memory usage (simplified)
                if 'load average' in result.stdout:
                    findings.append("System load information available")
            else:
                findings.append("Unable to collect system resource information")
            
            # Check server process
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'mcp_server' in result.stdout:
                findings.append("MCP server process found")
                recommendations.append("Monitor server resource usage")
            else:
                findings.append("MCP server process not found")
                recommendations.append("Start the MCP server")
            
            # Test response time
            start_time = time.time()
            result = subprocess.run(['curl', '-s', 'http://localhost:8000/health'], 
                                  capture_output=True, text=True, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                findings.append(f"Response time: {response_time:.2f}ms")
                if response_time > 1000:
                    recommendations.append("Response time is high - investigate performance bottlenecks")
                else:
                    findings.append("Response time is acceptable")
            else:
                findings.append("Unable to measure response time")
                recommendations.append("Check server connectivity")
                
        except Exception as e:
            findings.append(f"Performance diagnostic error: {str(e)}")
            recommendations.append("Review system environment and permissions")
        
        return findings, recommendations
    
    def _diagnose_configuration_issue(self) -> tuple[List[str], List[str]]:
        """Diagnose configuration-related issues.
        
        Returns:
            Tuple of (findings, recommendations)
        """
        findings = []
        recommendations = []
        
        try:
            # Check if config directory exists
            if os.path.exists('config'):
                findings.append("Configuration directory exists")
                
                # Check for config files
                config_files = os.listdir('config')
                if config_files:
                    findings.append(f"Found {len(config_files)} configuration files")
                    
                    # Check for main config file
                    if 'config.yaml' in config_files:
                        findings.append("Main configuration file found")
                        
                        # Try to load config
                        try:
                            with open('config/config.yaml', 'r') as f:
                                content = f.read()
                            findings.append("Configuration file is readable")
                            
                            # Basic YAML validation
                            if 'yaml' in content.lower() or ':' in content:
                                findings.append("Configuration appears to be valid YAML")
                            else:
                                findings.append("Configuration may not be valid YAML")
                                recommendations.append("Check configuration file syntax")
                                
                        except Exception as e:
                            findings.append(f"Error reading configuration: {str(e)}")
                            recommendations.append("Check file permissions and syntax")
                    else:
                        findings.append("Main configuration file not found")
                        recommendations.append("Create or restore configuration file")
                else:
                    findings.append("No configuration files found")
                    recommendations.append("Create configuration files")
            else:
                findings.append("Configuration directory not found")
                recommendations.append("Create configuration directory and files")
                
        except Exception as e:
            findings.append(f"Configuration diagnostic error: {str(e)}")
            recommendations.append("Review file system permissions")
        
        return findings, recommendations
    
    def _diagnose_security_issue(self) -> tuple[List[str], List[str]]:
        """Diagnose security-related issues.
        
        Returns:
            Tuple of (findings, recommendations)
        """
        findings = []
        recommendations = []
        
        try:
            # Check for authentication
            result = subprocess.run(['curl', '-s', 'http://localhost:8000/health'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                findings.append("Server is accessible without authentication")
                recommendations.append("Implement authentication if required")
            else:
                findings.append("Server may have authentication enabled")
            
            # Check for HTTPS
            result = subprocess.run(['curl', '-s', 'https://localhost:8000/health'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                findings.append("HTTPS is available")
            else:
                findings.append("HTTPS is not available")
                recommendations.append("Enable HTTPS for production use")
            
            # Check for rate limiting (simplified)
            findings.append("Rate limiting status unknown")
            recommendations.append("Implement rate limiting to prevent abuse")
            
            # Check for input validation
            findings.append("Input validation status unknown")
            recommendations.append("Implement input validation for all endpoints")
                
        except Exception as e:
            findings.append(f"Security diagnostic error: {str(e)}")
            recommendations.append("Review security configuration")
        
        return findings, recommendations
    
    def save_known_issue(self, issue: KnownIssue) -> str:
        """Save a known issue to file.
        
        Args:
            issue: KnownIssue object to save
            
        Returns:
            Path to the saved file
        """
        filename = f"{issue.id}.json"
        filepath = os.path.join(self.issues_dir, filename)
        
        try:
            # Convert to dictionary with enum values as strings
            data = asdict(issue)
            data['category'] = issue.category.value
            data['severity'] = issue.severity.value
            data['status'] = issue.status.value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Known issue saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save known issue {issue.id}: {e}")
            raise
    
    def export_troubleshooting_guide(self, output_file: str = "troubleshooting_guide.md"):
        """Export the troubleshooting guide to Markdown format.
        
        Args:
            output_file: Output file path
        """
        md_content = """# Inspector Troubleshooting Guide

This guide provides comprehensive troubleshooting procedures and solutions for common Inspector system issues.

## Overview

The Inspector system may encounter various issues during operation. This guide provides step-by-step procedures to diagnose and resolve these issues.

## Issue Categories

"""
        
        # Group issues by category
        categories = {}
        for issue in self.known_issues.values():
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)
        
        for category, issues in categories.items():
            md_content += f"### {category.value} Issues\n\n"
            
            for issue in issues:
                md_content += f"#### {issue.title} (ID: {issue.id})\n\n"
                md_content += f"**Severity**: {issue.severity.value}\n\n"
                md_content += f"**Status**: {issue.status.value}\n\n"
                md_content += f"**Description**: {issue.description}\n\n"
                
                md_content += "**Symptoms**:\n"
                for symptom in issue.symptoms:
                    md_content += f"- {symptom}\n"
                md_content += "\n"
                
                md_content += f"**Root Cause**: {issue.root_cause}\n\n"
                
                md_content += "**Affected Versions**:\n"
                for version in issue.affected_versions:
                    md_content += f"- {version}\n"
                md_content += "\n"
                
                if issue.workarounds:
                    md_content += "**Workarounds**:\n"
                    for workaround in issue.workarounds:
                        md_content += f"- {workaround}\n"
                    md_content += "\n"
                
                if issue.solutions:
                    md_content += "**Solutions**:\n"
                    for solution in issue.solutions:
                        md_content += f"- [{solution.title}](#{solution.id.lower()})\n"
                    md_content += "\n"
                
                md_content += "---\n\n"
        
        # Add solutions section
        md_content += "## Solutions\n\n"
        
        for solution in self.solutions.values():
            md_content += f"### {solution.title} (ID: {solution.id})\n\n"
            md_content += f"**Success Rate**: {solution.success_rate}%\n\n"
            md_content += f"**Description**: {solution.description}\n\n"
            
            md_content += "**Steps**:\n"
            for step in solution.steps:
                md_content += f"{step.step_number}. {step.description}\n"
                if step.command:
                    md_content += f"   Command: `{step.command}`\n"
                if step.expected_output:
                    md_content += f"   Expected: {step.expected_output}\n"
                if step.notes:
                    md_content += f"   Notes: {step.notes}\n"
                md_content += "\n"
            
            md_content += "**Verification Steps**:\n"
            for step in solution.verification_steps:
                md_content += f"- {step}\n"
            md_content += "\n"
            
            md_content += "**Prevention Tips**:\n"
            for tip in solution.prevention_tips:
                md_content += f"- {tip}\n"
            md_content += "\n"
            
            md_content += "---\n\n"
        
        # Add diagnostic section
        md_content += """## Diagnostic Procedures

### Running Diagnostics

```python
from inspector_troubleshooting_guide import InspectorTroubleshootingGuide

guide = InspectorTroubleshootingGuide()

# Run diagnostic for a specific issue
result = guide.run_diagnostic("KI-MCP-001")
print(f"Status: {result.status}")
print(f"Findings: {result.findings}")
print(f"Recommendations: {result.recommendations}")
```

### Searching Issues

```python
# Search for issues by keywords
issues = guide.search_issues(["connection", "timeout"])
for issue in issues:
    print(f"{issue.id}: {issue.title}")
```

## Best Practices

### General Troubleshooting

1. **Document the Issue**: Record symptoms, error messages, and environment details
2. **Check Logs**: Review system and application logs for error messages
3. **Isolate the Problem**: Determine if the issue is system-wide or specific to Inspector
4. **Test Incrementally**: Make one change at a time and test the result
5. **Keep Backups**: Backup configuration and data before making changes

### Issue Resolution

1. **Follow Procedures**: Use the step-by-step procedures provided in this guide
2. **Verify Solutions**: Always verify that the solution resolves the issue
3. **Update Documentation**: Update this guide with new issues and solutions
4. **Share Knowledge**: Document lessons learned for future reference

### Prevention

1. **Regular Monitoring**: Monitor system health and performance regularly
2. **Proactive Maintenance**: Perform regular maintenance and updates
3. **Testing**: Test changes in a safe environment before production
4. **Documentation**: Keep documentation up to date

---
*Generated by Inspector Troubleshooting Guide*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Troubleshooting guide exported to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to export troubleshooting guide: {e}")
            raise


def main():
    """Main function to demonstrate the troubleshooting guide system."""
    print("Inspector Troubleshooting Guide System")
    print("=" * 50)
    
    # Initialize the troubleshooting guide
    guide = InspectorTroubleshootingGuide()
    
    print(f"Loaded {len(guide.known_issues)} known issues")
    print(f"Loaded {len(guide.solutions)} solutions")
    
    # Search for issues
    print("\nSearching for connection issues...")
    connection_issues = guide.search_issues(["connection", "refused"])
    for issue in connection_issues:
        print(f"  {issue.id}: {issue.title}")
    
    # Run diagnostic
    print("\nRunning diagnostic for connection issue...")
    environment_info = {
        "OS": "Windows 10",
        "Python": "3.12.0",
        "Environment": "Development"
    }
    
    result = guide.run_diagnostic("KI-MCP-001", environment_info)
    print(f"Diagnostic status: {result.status}")
    print(f"Findings: {len(result.findings)}")
    for finding in result.findings:
        print(f"  - {finding}")
    print(f"Recommendations: {len(result.recommendations)}")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    # Get issues by category
    print("\nPerformance issues:")
    perf_issues = guide.get_issues_by_category(IssueCategory.PERFORMANCE)
    for issue in perf_issues:
        print(f"  {issue.id}: {issue.title}")
    
    # Save a known issue
    print("\nSaving known issue...")
    issue = guide.known_issues["KI-MCP-001"]
    filepath = guide.save_known_issue(issue)
    print(f"Issue saved to: {filepath}")
    
    # Export troubleshooting guide
    print("\nExporting troubleshooting guide...")
    guide.export_troubleshooting_guide()
    
    print("\nTroubleshooting guide system ready for use!")


if __name__ == "__main__":
    main() 