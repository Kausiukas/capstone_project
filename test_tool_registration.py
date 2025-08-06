#!/usr/bin/env python3
"""
Tool Registration Testing Module

This module implements comprehensive tool registration testing for the MCP server.
It validates that all 81 tools register correctly, tests tool discovery,
categorization, and registration performance.

Part of Task 2.2: Tool Registration Testing
"""

import json
import subprocess
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolRegistrationResult:
    """Result of a tool registration test"""
    tool_name: str
    registration_success: bool
    discovery_success: bool
    categorization_success: bool
    registration_time_ms: float
    error_message: Optional[str] = None
    tool_schema: Optional[Dict] = None
    tool_metadata: Optional[Dict] = None


@dataclass
class ToolRegistrationTestSuite:
    """Complete test suite for tool registration"""
    total_tools: int
    successful_registrations: int
    successful_discoveries: int
    successful_categorizations: int
    average_registration_time_ms: float
    max_registration_time_ms: float
    min_registration_time_ms: float
    failed_tools: List[str]
    test_results: List[ToolRegistrationResult]
    test_timestamp: datetime
    test_duration_seconds: float


class ToolRegistrationTester:
    """Comprehensive tool registration testing system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool registration tester
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[ToolRegistrationResult] = []
        self.start_time: Optional[datetime] = None
        
    def test_all_tools_registration(self) -> ToolRegistrationTestSuite:
        """
        Test registration of all 81 tools
        
        Returns:
            ToolRegistrationTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool registration testing")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = self._get_tools_list()
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with registration testing")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to test")
        
        # Test each tool registration
        for tool_name in tools_list:
            result = self._test_single_tool_registration(tool_name)
            self.test_results.append(result)
            
            # Log progress
            if result.registration_success:
                logger.info(f"✅ Tool '{tool_name}' registered successfully ({result.registration_time_ms:.2f}ms)")
            else:
                logger.error(f"❌ Tool '{tool_name}' registration failed: {result.error_message}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool registration testing completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.successful_registrations}/{test_suite.total_tools} tools registered successfully")
        
        return test_suite
    
    def _get_tools_list(self) -> List[str]:
        """
        Get list of all available tools from the MCP server
        
        Returns:
            List of tool names
        """
        try:
            command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", self.mcp_server_path,
                "--cli",
                "--method", "tools/list"
            ]
            
            logger.debug(f"Executing command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout.strip())
                    tools = response.get('tools', [])
                    tool_names = [tool.get('name', '') for tool in tools if tool.get('name')]
                    logger.info(f"Retrieved {len(tool_names)} tools from server")
                    return tool_names
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tools list response: {e}")
                    return []
            else:
                logger.error(f"Failed to get tools list: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout getting tools list")
            return []
        except Exception as e:
            logger.error(f"Exception getting tools list: {e}")
            return []
    
    def _test_single_tool_registration(self, tool_name: str) -> ToolRegistrationResult:
        """
        Test registration of a single tool
        
        Args:
            tool_name: Name of the tool to test
            
        Returns:
            ToolRegistrationResult with test results
        """
        start_time = time.time()
        
        try:
            # Test tool discovery
            discovery_success = self._test_tool_discovery(tool_name)
            
            # Test tool categorization
            categorization_success = self._test_tool_categorization(tool_name)
            
            # Get tool schema and metadata
            tool_schema = self._get_tool_schema(tool_name)
            tool_metadata = self._get_tool_metadata(tool_name)
            
            # Determine overall registration success
            registration_success = discovery_success and categorization_success
            
            registration_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return ToolRegistrationResult(
                tool_name=tool_name,
                registration_success=registration_success,
                discovery_success=discovery_success,
                categorization_success=categorization_success,
                registration_time_ms=registration_time,
                tool_schema=tool_schema,
                tool_metadata=tool_metadata
            )
            
        except Exception as e:
            registration_time = (time.time() - start_time) * 1000
            return ToolRegistrationResult(
                tool_name=tool_name,
                registration_success=False,
                discovery_success=False,
                categorization_success=False,
                registration_time_ms=registration_time,
                error_message=str(e)
            )
    
    def _test_tool_discovery(self, tool_name: str) -> bool:
        """
        Test if a tool can be discovered in the tools list
        
        Args:
            tool_name: Name of the tool to test
            
        Returns:
            True if tool is discoverable, False otherwise
        """
        try:
            command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", self.mcp_server_path,
                "--cli",
                "--method", "tools/list"
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                tools = response.get('tools', [])
                
                # Check if tool exists in the list
                for tool in tools:
                    if tool.get('name') == tool_name:
                        return True
                
                return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error testing tool discovery for '{tool_name}': {e}")
            return False
    
    def _test_tool_categorization(self, tool_name: str) -> bool:
        """
        Test if a tool has proper categorization
        
        Args:
            tool_name: Name of the tool to test
            
        Returns:
            True if tool has proper categorization, False otherwise
        """
        try:
            command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", self.mcp_server_path,
                "--cli",
                "--method", "tools/list"
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                tools = response.get('tools', [])
                
                # Find the tool and check its categorization
                for tool in tools:
                    if tool.get('name') == tool_name:
                        # Check if tool has required categorization fields
                        description = tool.get('description', '')
                        input_schema = tool.get('inputSchema', {})
                        
                        # Basic categorization validation
                        has_description = bool(description and description.strip())
                        has_input_schema = bool(input_schema)
                        
                        return has_description and has_input_schema
                
                return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error testing tool categorization for '{tool_name}': {e}")
            return False
    
    def _get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """
        Get the input schema for a specific tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool input schema or None if not found
        """
        try:
            command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", self.mcp_server_path,
                "--cli",
                "--method", "tools/list"
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                tools = response.get('tools', [])
                
                for tool in tools:
                    if tool.get('name') == tool_name:
                        return tool.get('inputSchema', {})
                
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting tool schema for '{tool_name}': {e}")
            return None
    
    def _get_tool_metadata(self, tool_name: str) -> Optional[Dict]:
        """
        Get metadata for a specific tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool metadata or None if not found
        """
        try:
            command = [
                "npx", "@modelcontextprotocol/inspector",
                "python", self.mcp_server_path,
                "--cli",
                "--method", "tools/list"
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
                tools = response.get('tools', [])
                
                for tool in tools:
                    if tool.get('name') == tool_name:
                        # Extract relevant metadata
                        metadata = {
                            'description': tool.get('description', ''),
                            'inputSchema': tool.get('inputSchema', {}),
                            'name': tool.get('name', ''),
                            'displayName': tool.get('displayName', ''),
                            'descriptionForHuman': tool.get('descriptionForHuman', ''),
                            'descriptionForModel': tool.get('descriptionForModel', '')
                        }
                        return metadata
                
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting tool metadata for '{tool_name}': {e}")
            return None
    
    def _calculate_test_suite_results(self) -> ToolRegistrationTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            ToolRegistrationTestSuite with aggregated results
        """
        if not self.start_time:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        total_tools = len(self.test_results)
        successful_registrations = sum(1 for r in self.test_results if r.registration_success)
        successful_discoveries = sum(1 for r in self.test_results if r.discovery_success)
        successful_categorizations = sum(1 for r in self.test_results if r.categorization_success)
        
        registration_times = [r.registration_time_ms for r in self.test_results]
        avg_registration_time = sum(registration_times) / len(registration_times) if registration_times else 0
        max_registration_time = max(registration_times) if registration_times else 0
        min_registration_time = min(registration_times) if registration_times else 0
        
        failed_tools = [r.tool_name for r in self.test_results if not r.registration_success]
        
        return ToolRegistrationTestSuite(
            total_tools=total_tools,
            successful_registrations=successful_registrations,
            successful_discoveries=successful_discoveries,
            successful_categorizations=successful_categorizations,
            average_registration_time_ms=avg_registration_time,
            max_registration_time_ms=max_registration_time,
            min_registration_time_ms=min_registration_time,
            failed_tools=failed_tools,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )
    
    def _create_empty_test_suite(self) -> ToolRegistrationTestSuite:
        """Create an empty test suite for error cases"""
        return ToolRegistrationTestSuite(
            total_tools=0,
            successful_registrations=0,
            successful_discoveries=0,
            successful_categorizations=0,
            average_registration_time_ms=0,
            max_registration_time_ms=0,
            min_registration_time_ms=0,
            failed_tools=[],
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0
        )
    
    def save_test_results(self, test_suite: ToolRegistrationTestSuite, output_file: str = "tool_registration_test_results.json"):
        """
        Save test results to JSON file
        
        Args:
            test_suite: Test suite results to save
            output_file: Output file path
        """
        try:
            # Convert dataclass to dict for JSON serialization
            results_dict = asdict(test_suite)
            
            # Convert datetime to ISO format
            results_dict['test_timestamp'] = test_suite.test_timestamp.isoformat()
            
            with open(output_file, 'w') as f:
                json.dump(results_dict, f, indent=2)
            
            logger.info(f"Test results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
    
    def generate_test_report(self, test_suite: ToolRegistrationTestSuite) -> str:
        """
        Generate a human-readable test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL REGISTRATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Successful Registrations: {test_suite.successful_registrations}")
        report.append(f"Successful Discoveries: {test_suite.successful_discoveries}")
        report.append(f"Successful Categorizations: {test_suite.successful_categorizations}")
        report.append(f"Success Rate: {(test_suite.successful_registrations/test_suite.total_tools*100):.1f}%" if test_suite.total_tools > 0 else "N/A")
        report.append("")
        
        # Performance
        report.append("PERFORMANCE METRICS")
        report.append("-" * 40)
        report.append(f"Average Registration Time: {test_suite.average_registration_time_ms:.2f} ms")
        report.append(f"Fastest Registration: {test_suite.min_registration_time_ms:.2f} ms")
        report.append(f"Slowest Registration: {test_suite.max_registration_time_ms:.2f} ms")
        report.append("")
        
        # Failed tools
        if test_suite.failed_tools:
            report.append("FAILED TOOLS")
            report.append("-" * 40)
            for tool_name in test_suite.failed_tools:
                report.append(f"❌ {tool_name}")
            report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 40)
        for result in test_suite.test_results:
            status = "✅" if result.registration_success else "❌"
            report.append(f"{status} {result.tool_name}")
            report.append(f"    Discovery: {'✅' if result.discovery_success else '❌'}")
            report.append(f"    Categorization: {'✅' if result.categorization_success else '❌'}")
            report.append(f"    Time: {result.registration_time_ms:.2f} ms")
            if result.error_message:
                report.append(f"    Error: {result.error_message}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool registration tests"""
    logger.info("Starting Tool Registration Testing")
    
    # Initialize tester
    tester = ToolRegistrationTester()
    
    # Run comprehensive tests
    test_suite = tester.test_all_tools_registration()
    
    # Generate and display report
    report = tester.generate_test_report(test_suite)
    print(report)
    
    # Save results
    tester.save_test_results(test_suite)
    
    # Return success/failure based on results
    success_rate = test_suite.successful_registrations / test_suite.total_tools if test_suite.total_tools > 0 else 0
    logger.info(f"Tool registration testing completed with {success_rate*100:.1f}% success rate")
    
    return success_rate >= 0.95  # 95% success threshold


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 