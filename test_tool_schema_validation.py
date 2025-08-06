

#!/usr/bin/env python3
"""
Tool Schema Validation Testing Module

This module implements comprehensive tool schema validation testing for the MCP server.
It validates all tool input schemas, tests parameter type validation,
validates required vs optional parameters, and adds schema version testing.

Part of Task 2.2: Tool Registration Testing
"""

import json
import subprocess
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationResult:
    """Result of a schema validation test"""
    tool_name: str
    schema_valid: bool
    parameter_types_valid: bool
    required_parameters_valid: bool
    optional_parameters_valid: bool
    schema_version_valid: bool
    validation_time_ms: float
    error_message: Optional[str] = None
    schema_details: Optional[Dict] = None
    validation_errors: List[str] = None


@dataclass
class SchemaValidationTestSuite:
    """Complete test suite for schema validation"""
    total_tools: int
    valid_schemas: int
    valid_parameter_types: int
    valid_required_parameters: int
    valid_optional_parameters: int
    valid_schema_versions: int
    average_validation_time_ms: float
    max_validation_time_ms: float
    min_validation_time_ms: float
    failed_tools: List[str]
    test_results: List[SchemaValidationResult]
    test_timestamp: datetime
    test_duration_seconds: float


class ToolSchemaValidator:
    """Comprehensive tool schema validation system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool schema validator
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[SchemaValidationResult] = []
        self.start_time: Optional[datetime] = None
        
        # Define valid JSON Schema types
        self.valid_types = {
            'string', 'number', 'integer', 'boolean', 'object', 'array', 'null'
        }
        
        # Define valid JSON Schema formats
        self.valid_formats = {
            'date-time', 'date', 'time', 'email', 'uri', 'uri-reference',
            'uuid', 'ipv4', 'ipv6', 'hostname', 'regex'
        }
    
    def validate_all_tool_schemas(self) -> SchemaValidationTestSuite:
        """
        Validate schemas for all tools
        
        Returns:
            SchemaValidationTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool schema validation")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = self._get_tools_list()
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with schema validation")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to validate")
        
        # Validate each tool schema
        for tool_name in tools_list:
            result = self._validate_single_tool_schema(tool_name)
            self.test_results.append(result)
            
            # Log progress
            if result.schema_valid:
                logger.info(f"✅ Tool '{tool_name}' schema validated successfully ({result.validation_time_ms:.2f}ms)")
            else:
                logger.error(f"❌ Tool '{tool_name}' schema validation failed: {result.error_message}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool schema validation completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.valid_schemas}/{test_suite.total_tools} schemas validated successfully")
        
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
    
    def _validate_single_tool_schema(self, tool_name: str) -> SchemaValidationResult:
        """
        Validate schema for a single tool
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            SchemaValidationResult with validation results
        """
        start_time = time.time()
        validation_errors = []
        
        try:
            # Get tool schema
            tool_schema = self._get_tool_schema(tool_name)
            if not tool_schema:
                return SchemaValidationResult(
                    tool_name=tool_name,
                    schema_valid=False,
                    parameter_types_valid=False,
                    required_parameters_valid=False,
                    optional_parameters_valid=False,
                    schema_version_valid=False,
                    validation_time_ms=(time.time() - start_time) * 1000,
                    error_message="Failed to retrieve tool schema",
                    validation_errors=validation_errors
                )
            
            # Validate overall schema structure
            schema_valid = self._validate_schema_structure(tool_schema, validation_errors)
            
            # Validate parameter types
            parameter_types_valid = self._validate_parameter_types(tool_schema, validation_errors)
            
            # Validate required parameters
            required_parameters_valid = self._validate_required_parameters(tool_schema, validation_errors)
            
            # Validate optional parameters
            optional_parameters_valid = self._validate_optional_parameters(tool_schema, validation_errors)
            
            # Validate schema version
            schema_version_valid = self._validate_schema_version(tool_schema, validation_errors)
            
            validation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return SchemaValidationResult(
                tool_name=tool_name,
                schema_valid=schema_valid,
                parameter_types_valid=parameter_types_valid,
                required_parameters_valid=required_parameters_valid,
                optional_parameters_valid=optional_parameters_valid,
                schema_version_valid=schema_version_valid,
                validation_time_ms=validation_time,
                schema_details=tool_schema,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            validation_time = (time.time() - start_time) * 1000
            return SchemaValidationResult(
                tool_name=tool_name,
                schema_valid=False,
                parameter_types_valid=False,
                required_parameters_valid=False,
                optional_parameters_valid=False,
                schema_version_valid=False,
                validation_time_ms=validation_time,
                error_message=str(e),
                validation_errors=validation_errors
            )
    
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
    
    def _validate_schema_structure(self, schema: Dict, errors: List[str]) -> bool:
        """
        Validate basic schema structure
        
        Args:
            schema: Schema to validate
            errors: List to collect validation errors
            
        Returns:
            True if schema structure is valid, False otherwise
        """
        try:
            # Check if schema is a dictionary
            if not isinstance(schema, dict):
                errors.append("Schema must be a dictionary")
                return False
            
            # Check for required top-level fields
            required_fields = ['type']
            for field in required_fields:
                if field not in schema:
                    errors.append(f"Missing required field: {field}")
                    return False
            
            # Validate type field
            schema_type = schema.get('type')
            if schema_type not in self.valid_types:
                errors.append(f"Invalid schema type: {schema_type}")
                return False
            
            # For object types, check properties
            if schema_type == 'object':
                properties = schema.get('properties', {})
                if not isinstance(properties, dict):
                    errors.append("Properties must be a dictionary")
                    return False
            
            # For array types, check items
            elif schema_type == 'array':
                if 'items' not in schema:
                    errors.append("Array schema must have 'items' field")
                    return False
            
            return True
            
        except Exception as e:
            errors.append(f"Schema structure validation error: {e}")
            return False
    
    def _validate_parameter_types(self, schema: Dict, errors: List[str]) -> bool:
        """
        Validate parameter types in the schema
        
        Args:
            schema: Schema to validate
            errors: List to collect validation errors
            
        Returns:
            True if parameter types are valid, False otherwise
        """
        try:
            schema_type = schema.get('type')
            
            if schema_type == 'object':
                properties = schema.get('properties', {})
                for prop_name, prop_schema in properties.items():
                    if not isinstance(prop_schema, dict):
                        errors.append(f"Property '{prop_name}' schema must be a dictionary")
                        continue
                    
                    prop_type = prop_schema.get('type')
                    if prop_type and prop_type not in self.valid_types:
                        errors.append(f"Property '{prop_name}' has invalid type: {prop_type}")
                        continue
                    
                    # Validate format if present
                    prop_format = prop_schema.get('format')
                    if prop_format and prop_format not in self.valid_formats:
                        errors.append(f"Property '{prop_name}' has invalid format: {prop_format}")
                        continue
                    
                    # Recursively validate nested objects and arrays
                    if prop_type == 'object':
                        if not self._validate_parameter_types(prop_schema, errors):
                            return False
                    elif prop_type == 'array':
                        items_schema = prop_schema.get('items', {})
                        if not self._validate_parameter_types(items_schema, errors):
                            return False
            
            elif schema_type == 'array':
                items_schema = schema.get('items', {})
                if not self._validate_parameter_types(items_schema, errors):
                    return False
            
            return len(errors) == 0
            
        except Exception as e:
            errors.append(f"Parameter type validation error: {e}")
            return False
    
    def _validate_required_parameters(self, schema: Dict, errors: List[str]) -> bool:
        """
        Validate required parameters in the schema
        
        Args:
            schema: Schema to validate
            errors: List to collect validation errors
            
        Returns:
            True if required parameters are valid, False otherwise
        """
        try:
            schema_type = schema.get('type')
            
            if schema_type == 'object':
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                
                # Check if required list is valid
                if not isinstance(required, list):
                    errors.append("Required field must be a list")
                    return False
                
                # Check if all required properties exist
                for req_prop in required:
                    if not isinstance(req_prop, str):
                        errors.append(f"Required property name must be a string: {req_prop}")
                        continue
                    
                    if req_prop not in properties:
                        errors.append(f"Required property '{req_prop}' not found in properties")
                        continue
                    
                    # Check if required property has a valid schema
                    prop_schema = properties[req_prop]
                    if not isinstance(prop_schema, dict):
                        errors.append(f"Required property '{req_prop}' schema must be a dictionary")
                        continue
                    
                    # Check if required property has a type
                    if 'type' not in prop_schema:
                        errors.append(f"Required property '{req_prop}' must have a type")
                        continue
                
                # Check for duplicate required properties
                if len(required) != len(set(required)):
                    errors.append("Duplicate properties in required list")
                    return False
            
            return len(errors) == 0
            
        except Exception as e:
            errors.append(f"Required parameters validation error: {e}")
            return False
    
    def _validate_optional_parameters(self, schema: Dict, errors: List[str]) -> bool:
        """
        Validate optional parameters in the schema
        
        Args:
            schema: Schema to validate
            errors: List to collect validation errors
            
        Returns:
            True if optional parameters are valid, False otherwise
        """
        try:
            schema_type = schema.get('type')
            
            if schema_type == 'object':
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                
                # Check all properties that are not required
                for prop_name, prop_schema in properties.items():
                    if prop_name in required:
                        continue  # Skip required properties
                    
                    # Optional properties should have valid schemas
                    if not isinstance(prop_schema, dict):
                        errors.append(f"Optional property '{prop_name}' schema must be a dictionary")
                        continue
                    
                    # Optional properties should have a type
                    if 'type' not in prop_schema:
                        errors.append(f"Optional property '{prop_name}' must have a type")
                        continue
                    
                    # Optional properties can have default values
                    if 'default' in prop_schema:
                        default_value = prop_schema['default']
                        prop_type = prop_schema['type']
                        
                        # Validate default value type
                        if not self._validate_default_value_type(default_value, prop_type):
                            errors.append(f"Optional property '{prop_name}' has invalid default value type")
                            continue
            
            return len(errors) == 0
            
        except Exception as e:
            errors.append(f"Optional parameters validation error: {e}")
            return False
    
    def _validate_default_value_type(self, default_value: Any, expected_type: str) -> bool:
        """
        Validate that a default value matches the expected type
        
        Args:
            default_value: The default value to validate
            expected_type: The expected JSON Schema type
            
        Returns:
            True if default value type matches, False otherwise
        """
        try:
            if expected_type == 'string':
                return isinstance(default_value, str)
            elif expected_type == 'number':
                return isinstance(default_value, (int, float)) and not isinstance(default_value, bool)
            elif expected_type == 'integer':
                return isinstance(default_value, int) and not isinstance(default_value, bool)
            elif expected_type == 'boolean':
                return isinstance(default_value, bool)
            elif expected_type == 'object':
                return isinstance(default_value, dict)
            elif expected_type == 'array':
                return isinstance(default_value, list)
            elif expected_type == 'null':
                return default_value is None
            else:
                return True  # Unknown type, assume valid
                
        except Exception:
            return False
    
    def _validate_schema_version(self, schema: Dict, errors: List[str]) -> bool:
        """
        Validate schema version information
        
        Args:
            schema: Schema to validate
            errors: List to collect validation errors
            
        Returns:
            True if schema version is valid, False otherwise
        """
        try:
            # Check for $schema field (JSON Schema version)
            schema_version = schema.get('$schema')
            if schema_version:
                valid_versions = [
                    'http://json-schema.org/draft-07/schema#',
                    'http://json-schema.org/draft-06/schema#',
                    'http://json-schema.org/draft-04/schema#',
                    'https://json-schema.org/draft/2020-12/schema',
                    'https://json-schema.org/draft/2019-09/schema'
                ]
                
                if schema_version not in valid_versions:
                    errors.append(f"Invalid JSON Schema version: {schema_version}")
                    return False
            
            # Check for custom version field
            custom_version = schema.get('version')
            if custom_version and not isinstance(custom_version, str):
                errors.append("Custom version field must be a string")
                return False
            
            return True
            
        except Exception as e:
            errors.append(f"Schema version validation error: {e}")
            return False
    
    def _calculate_test_suite_results(self) -> SchemaValidationTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            SchemaValidationTestSuite with aggregated results
        """
        if not self.start_time:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        total_tools = len(self.test_results)
        valid_schemas = sum(1 for r in self.test_results if r.schema_valid)
        valid_parameter_types = sum(1 for r in self.test_results if r.parameter_types_valid)
        valid_required_parameters = sum(1 for r in self.test_results if r.required_parameters_valid)
        valid_optional_parameters = sum(1 for r in self.test_results if r.optional_parameters_valid)
        valid_schema_versions = sum(1 for r in self.test_results if r.schema_version_valid)
        
        validation_times = [r.validation_time_ms for r in self.test_results]
        avg_validation_time = sum(validation_times) / len(validation_times) if validation_times else 0
        max_validation_time = max(validation_times) if validation_times else 0
        min_validation_time = min(validation_times) if validation_times else 0
        
        failed_tools = [r.tool_name for r in self.test_results if not r.schema_valid]
        
        return SchemaValidationTestSuite(
            total_tools=total_tools,
            valid_schemas=valid_schemas,
            valid_parameter_types=valid_parameter_types,
            valid_required_parameters=valid_required_parameters,
            valid_optional_parameters=valid_optional_parameters,
            valid_schema_versions=valid_schema_versions,
            average_validation_time_ms=avg_validation_time,
            max_validation_time_ms=max_validation_time,
            min_validation_time_ms=min_validation_time,
            failed_tools=failed_tools,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )
    
    def _create_empty_test_suite(self) -> SchemaValidationTestSuite:
        """Create an empty test suite for error cases"""
        return SchemaValidationTestSuite(
            total_tools=0,
            valid_schemas=0,
            valid_parameter_types=0,
            valid_required_parameters=0,
            valid_optional_parameters=0,
            valid_schema_versions=0,
            average_validation_time_ms=0,
            max_validation_time_ms=0,
            min_validation_time_ms=0,
            failed_tools=[],
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0
        )
    
    def save_test_results(self, test_suite: SchemaValidationTestSuite, output_file: str = "tool_schema_validation_results.json"):
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
    
    def generate_test_report(self, test_suite: SchemaValidationTestSuite) -> str:
        """
        Generate a human-readable test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL SCHEMA VALIDATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Valid Schemas: {test_suite.valid_schemas}")
        report.append(f"Valid Parameter Types: {test_suite.valid_parameter_types}")
        report.append(f"Valid Required Parameters: {test_suite.valid_required_parameters}")
        report.append(f"Valid Optional Parameters: {test_suite.valid_optional_parameters}")
        report.append(f"Valid Schema Versions: {test_suite.valid_schema_versions}")
        report.append(f"Overall Success Rate: {(test_suite.valid_schemas/test_suite.total_tools*100):.1f}%" if test_suite.total_tools > 0 else "N/A")
        report.append("")
        
        # Performance
        report.append("PERFORMANCE METRICS")
        report.append("-" * 40)
        report.append(f"Average Validation Time: {test_suite.average_validation_time_ms:.2f} ms")
        report.append(f"Fastest Validation: {test_suite.min_validation_time_ms:.2f} ms")
        report.append(f"Slowest Validation: {test_suite.max_validation_time_ms:.2f} ms")
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
            status = "✅" if result.schema_valid else "❌"
            report.append(f"{status} {result.tool_name}")
            report.append(f"    Schema Structure: {'✅' if result.schema_valid else '❌'}")
            report.append(f"    Parameter Types: {'✅' if result.parameter_types_valid else '❌'}")
            report.append(f"    Required Parameters: {'✅' if result.required_parameters_valid else '❌'}")
            report.append(f"    Optional Parameters: {'✅' if result.optional_parameters_valid else '❌'}")
            report.append(f"    Schema Version: {'✅' if result.schema_version_valid else '❌'}")
            report.append(f"    Time: {result.validation_time_ms:.2f} ms")
            if result.validation_errors:
                for error in result.validation_errors:
                    report.append(f"    Error: {error}")
            if result.error_message:
                report.append(f"    Error: {result.error_message}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool schema validation tests"""
    logger.info("Starting Tool Schema Validation Testing")
    
    # Initialize validator
    validator = ToolSchemaValidator()
    
    # Run comprehensive validation
    test_suite = validator.validate_all_tool_schemas()
    
    # Generate and display report
    report = validator.generate_test_report(test_suite)
    print(report)
    
    # Save results
    validator.save_test_results(test_suite)
    
    # Return success/failure based on results
    success_rate = test_suite.valid_schemas / test_suite.total_tools if test_suite.total_tools > 0 else 0
    logger.info(f"Tool schema validation completed with {success_rate*100:.1f}% success rate")
    
    return success_rate >= 0.95  # 95% success threshold


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 