#!/usr/bin/env python3
"""
Tool Metadata Testing Module

This module implements comprehensive tool metadata testing for the MCP server.
It tests tool descriptions, validates tool documentation, tests tool examples,
and adds metadata completeness validation.

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
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetadataValidationResult:
    """Result of a metadata validation test"""
    tool_name: str
    description_valid: bool
    documentation_valid: bool
    examples_valid: bool
    metadata_complete: bool
    validation_time_ms: float
    error_message: Optional[str] = None
    metadata_details: Optional[Dict] = None
    validation_errors: List[str] = None


@dataclass
class MetadataValidationTestSuite:
    """Complete test suite for metadata validation"""
    total_tools: int
    valid_descriptions: int
    valid_documentation: int
    valid_examples: int
    complete_metadata: int
    average_validation_time_ms: float
    max_validation_time_ms: float
    min_validation_time_ms: float
    failed_tools: List[str]
    test_results: List[MetadataValidationResult]
    test_timestamp: datetime
    test_duration_seconds: float


class ToolMetadataValidator:
    """Comprehensive tool metadata validation system"""
    
    def __init__(self, mcp_server_path: str = "mcp_langflow_connector_simple.py"):
        """
        Initialize the tool metadata validator
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
        self.test_results: List[MetadataValidationResult] = []
        self.start_time: Optional[datetime] = None
        
        # Define metadata quality thresholds
        self.min_description_length = 10
        self.min_documentation_length = 20
        self.required_metadata_fields = {
            'name', 'description', 'inputSchema'
        }
        self.recommended_metadata_fields = {
            'displayName', 'descriptionForHuman', 'descriptionForModel'
        }
    
    def validate_all_tool_metadata(self) -> MetadataValidationTestSuite:
        """
        Validate metadata for all tools
        
        Returns:
            MetadataValidationTestSuite with comprehensive results
        """
        logger.info("Starting comprehensive tool metadata validation")
        self.start_time = datetime.now()
        
        # Get list of all tools first
        tools_list = self._get_tools_list()
        if not tools_list:
            logger.error("Failed to get tools list - cannot proceed with metadata validation")
            return self._create_empty_test_suite()
        
        logger.info(f"Found {len(tools_list)} tools to validate")
        
        # Validate each tool metadata
        for tool_name in tools_list:
            result = self._validate_single_tool_metadata(tool_name)
            self.test_results.append(result)
            
            # Log progress
            if result.metadata_complete:
                logger.info(f"✅ Tool '{tool_name}' metadata validated successfully ({result.validation_time_ms:.2f}ms)")
            else:
                logger.error(f"❌ Tool '{tool_name}' metadata validation failed: {result.error_message}")
        
        # Calculate test suite results
        test_suite = self._calculate_test_suite_results()
        
        logger.info(f"Tool metadata validation completed in {test_suite.test_duration_seconds:.2f} seconds")
        logger.info(f"Success rate: {test_suite.complete_metadata}/{test_suite.total_tools} tools have complete metadata")
        
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
    
    def _validate_single_tool_metadata(self, tool_name: str) -> MetadataValidationResult:
        """
        Validate metadata for a single tool
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            MetadataValidationResult with validation results
        """
        start_time = time.time()
        validation_errors = []
        
        try:
            # Get tool metadata
            tool_metadata = self._get_tool_metadata(tool_name)
            if not tool_metadata:
                return MetadataValidationResult(
                    tool_name=tool_name,
                    description_valid=False,
                    documentation_valid=False,
                    examples_valid=False,
                    metadata_complete=False,
                    validation_time_ms=(time.time() - start_time) * 1000,
                    error_message="Failed to retrieve tool metadata",
                    validation_errors=validation_errors
                )
            
            # Validate description
            description_valid = self._validate_description(tool_metadata, validation_errors)
            
            # Validate documentation
            documentation_valid = self._validate_documentation(tool_metadata, validation_errors)
            
            # Validate examples
            examples_valid = self._validate_examples(tool_metadata, validation_errors)
            
            # Validate metadata completeness
            metadata_complete = self._validate_metadata_completeness(tool_metadata, validation_errors)
            
            validation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return MetadataValidationResult(
                tool_name=tool_name,
                description_valid=description_valid,
                documentation_valid=documentation_valid,
                examples_valid=examples_valid,
                metadata_complete=metadata_complete,
                validation_time_ms=validation_time,
                metadata_details=tool_metadata,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            validation_time = (time.time() - start_time) * 1000
            return MetadataValidationResult(
                tool_name=tool_name,
                description_valid=False,
                documentation_valid=False,
                examples_valid=False,
                metadata_complete=False,
                validation_time_ms=validation_time,
                error_message=str(e),
                validation_errors=validation_errors
            )
    
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
                        return tool
                
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting tool metadata for '{tool_name}': {e}")
            return None
    
    def _validate_description(self, metadata: Dict, errors: List[str]) -> bool:
        """
        Validate tool description
        
        Args:
            metadata: Tool metadata
            errors: List to collect validation errors
            
        Returns:
            True if description is valid, False otherwise
        """
        try:
            # Check for description field
            description = metadata.get('description', '')
            if not description:
                errors.append("Missing description field")
                return False
            
            # Check description length
            if len(description.strip()) < self.min_description_length:
                errors.append(f"Description too short (minimum {self.min_description_length} characters)")
                return False
            
            # Check for description quality indicators
            description_lower = description.lower()
            
            # Check for placeholder text
            placeholder_indicators = ['todo', 'placeholder', 'tbd', 'to be determined']
            for indicator in placeholder_indicators:
                if indicator in description_lower:
                    errors.append(f"Description contains placeholder text: {indicator}")
                    return False
            
            # Check for repetitive text
            words = description.split()
            if len(words) > 3:
                word_counts = {}
                for word in words:
                    word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
                
                for word, count in word_counts.items():
                    if count > len(words) * 0.3:  # More than 30% repetition
                        errors.append(f"Description has repetitive text: '{word}' appears {count} times")
                        return False
            
            # Check for proper sentence structure
            if not description.strip().endswith(('.', '!', '?')):
                errors.append("Description should end with proper punctuation")
                return False
            
            return True
            
        except Exception as e:
            errors.append(f"Description validation error: {e}")
            return False
    
    def _validate_documentation(self, metadata: Dict, errors: List[str]) -> bool:
        """
        Validate tool documentation
        
        Args:
            metadata: Tool metadata
            errors: List to collect validation errors
            
        Returns:
            True if documentation is valid, False otherwise
        """
        try:
            # Check for descriptionForHuman field
            description_for_human = metadata.get('descriptionForHuman', '')
            description_for_model = metadata.get('descriptionForModel', '')
            
            # At least one description should be present
            if not description_for_human and not description_for_model:
                errors.append("Missing both descriptionForHuman and descriptionForModel")
                return False
            
            # Validate descriptionForHuman if present
            if description_for_human:
                if len(description_for_human.strip()) < self.min_documentation_length:
                    errors.append(f"descriptionForHuman too short (minimum {self.min_documentation_length} characters)")
                    return False
                
                # Check for technical terms that should be explained
                technical_terms = ['api', 'endpoint', 'parameter', 'schema', 'json', 'xml']
                found_terms = []
                for term in technical_terms:
                    if term in description_for_human.lower():
                        found_terms.append(term)
                
                if found_terms and len(description_for_human) < 50:
                    errors.append(f"Technical terms found but documentation too brief: {found_terms}")
                    return False
            
            # Validate descriptionForModel if present
            if description_for_model:
                if len(description_for_model.strip()) < self.min_documentation_length:
                    errors.append(f"descriptionForModel too short (minimum {self.min_documentation_length} characters)")
                    return False
                
                # Check for model-specific formatting
                if not any(char in description_for_model for char in ['(', ')', '[', ']', '{', '}']):
                    # No structured formatting found
                    if len(description_for_model) < 30:
                        errors.append("descriptionForModel should include structured information for models")
                        return False
            
            return True
            
        except Exception as e:
            errors.append(f"Documentation validation error: {e}")
            return False
    
    def _validate_examples(self, metadata: Dict, errors: List[str]) -> bool:
        """
        Validate tool examples
        
        Args:
            metadata: Tool metadata
            errors: List to collect validation errors
            
        Returns:
            True if examples are valid, False otherwise
        """
        try:
            # Check for examples in description or documentation
            description = metadata.get('description', '')
            description_for_human = metadata.get('descriptionForHuman', '')
            description_for_model = metadata.get('descriptionForModel', '')
            
            all_text = f"{description} {description_for_human} {description_for_model}".lower()
            
            # Look for example indicators
            example_indicators = [
                'example:', 'examples:', 'for example', 'e.g.', 'such as',
                'sample:', 'usage:', 'usage example'
            ]
            
            has_example_indicators = any(indicator in all_text for indicator in example_indicators)
            
            # Check for code-like patterns
            code_patterns = [
                r'\{[^}]*\}',  # Curly braces
                r'\[[^\]]*\]',  # Square brackets
                r'"[^"]*"',     # Quoted strings
                r'\d+',         # Numbers
            ]
            
            has_code_patterns = any(re.search(pattern, all_text) for pattern in code_patterns)
            
            # Check input schema for examples
            input_schema = metadata.get('inputSchema', {})
            schema_has_examples = self._check_schema_for_examples(input_schema)
            
            # Determine if examples are present
            has_examples = has_example_indicators or has_code_patterns or schema_has_examples
            
            if not has_examples:
                errors.append("No examples found in tool documentation or schema")
                return False
            
            return True
            
        except Exception as e:
            errors.append(f"Examples validation error: {e}")
            return False
    
    def _check_schema_for_examples(self, schema: Dict) -> bool:
        """
        Check if schema contains examples
        
        Args:
            schema: Input schema to check
            
        Returns:
            True if schema contains examples, False otherwise
        """
        try:
            if not isinstance(schema, dict):
                return False
            
            # Check for examples field
            if 'examples' in schema:
                return True
            
            # Check for example field
            if 'example' in schema:
                return True
            
            # Check for default values (can serve as examples)
            if 'default' in schema:
                return True
            
            # Recursively check properties
            if schema.get('type') == 'object':
                properties = schema.get('properties', {})
                for prop_schema in properties.values():
                    if self._check_schema_for_examples(prop_schema):
                        return True
            
            # Check array items
            elif schema.get('type') == 'array':
                items_schema = schema.get('items', {})
                if self._check_schema_for_examples(items_schema):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _validate_metadata_completeness(self, metadata: Dict, errors: List[str]) -> bool:
        """
        Validate metadata completeness
        
        Args:
            metadata: Tool metadata
            errors: List to collect validation errors
            
        Returns:
            True if metadata is complete, False otherwise
        """
        try:
            # Check required fields
            missing_required = []
            for field in self.required_metadata_fields:
                if field not in metadata or not metadata[field]:
                    missing_required.append(field)
            
            if missing_required:
                errors.append(f"Missing required metadata fields: {missing_required}")
                return False
            
            # Check recommended fields
            missing_recommended = []
            for field in self.recommended_metadata_fields:
                if field not in metadata or not metadata[field]:
                    missing_recommended.append(field)
            
            if missing_recommended:
                errors.append(f"Missing recommended metadata fields: {missing_recommended}")
                # This is a warning, not a failure
            
            # Check for displayName quality
            display_name = metadata.get('displayName', '')
            if display_name:
                if len(display_name.strip()) < 3:
                    errors.append("displayName too short (minimum 3 characters)")
                    return False
                
                # Check for proper capitalization
                if not display_name[0].isupper():
                    errors.append("displayName should start with uppercase letter")
                    return False
            
            # Check for inputSchema completeness
            input_schema = metadata.get('inputSchema', {})
            if not input_schema:
                errors.append("Missing inputSchema")
                return False
            
            if not isinstance(input_schema, dict):
                errors.append("inputSchema must be a dictionary")
                return False
            
            # Check for schema type
            if 'type' not in input_schema:
                errors.append("inputSchema missing 'type' field")
                return False
            
            return True
            
        except Exception as e:
            errors.append(f"Metadata completeness validation error: {e}")
            return False
    
    def _calculate_test_suite_results(self) -> MetadataValidationTestSuite:
        """
        Calculate comprehensive test suite results
        
        Returns:
            MetadataValidationTestSuite with aggregated results
        """
        if not self.start_time:
            return self._create_empty_test_suite()
        
        end_time = datetime.now()
        test_duration = (end_time - self.start_time).total_seconds()
        
        total_tools = len(self.test_results)
        valid_descriptions = sum(1 for r in self.test_results if r.description_valid)
        valid_documentation = sum(1 for r in self.test_results if r.documentation_valid)
        valid_examples = sum(1 for r in self.test_results if r.examples_valid)
        complete_metadata = sum(1 for r in self.test_results if r.metadata_complete)
        
        validation_times = [r.validation_time_ms for r in self.test_results]
        avg_validation_time = sum(validation_times) / len(validation_times) if validation_times else 0
        max_validation_time = max(validation_times) if validation_times else 0
        min_validation_time = min(validation_times) if validation_times else 0
        
        failed_tools = [r.tool_name for r in self.test_results if not r.metadata_complete]
        
        return MetadataValidationTestSuite(
            total_tools=total_tools,
            valid_descriptions=valid_descriptions,
            valid_documentation=valid_documentation,
            valid_examples=valid_examples,
            complete_metadata=complete_metadata,
            average_validation_time_ms=avg_validation_time,
            max_validation_time_ms=max_validation_time,
            min_validation_time_ms=min_validation_time,
            failed_tools=failed_tools,
            test_results=self.test_results,
            test_timestamp=end_time,
            test_duration_seconds=test_duration
        )
    
    def _create_empty_test_suite(self) -> MetadataValidationTestSuite:
        """Create an empty test suite for error cases"""
        return MetadataValidationTestSuite(
            total_tools=0,
            valid_descriptions=0,
            valid_documentation=0,
            valid_examples=0,
            complete_metadata=0,
            average_validation_time_ms=0,
            max_validation_time_ms=0,
            min_validation_time_ms=0,
            failed_tools=[],
            test_results=[],
            test_timestamp=datetime.now(),
            test_duration_seconds=0
        )
    
    def save_test_results(self, test_suite: MetadataValidationTestSuite, output_file: str = "tool_metadata_validation_results.json"):
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
    
    def generate_test_report(self, test_suite: MetadataValidationTestSuite) -> str:
        """
        Generate a human-readable test report
        
        Args:
            test_suite: Test suite results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("TOOL METADATA VALIDATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {test_suite.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Duration: {test_suite.test_duration_seconds:.2f} seconds")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tools Tested: {test_suite.total_tools}")
        report.append(f"Valid Descriptions: {test_suite.valid_descriptions}")
        report.append(f"Valid Documentation: {test_suite.valid_documentation}")
        report.append(f"Valid Examples: {test_suite.valid_examples}")
        report.append(f"Complete Metadata: {test_suite.complete_metadata}")
        report.append(f"Overall Success Rate: {(test_suite.complete_metadata/test_suite.total_tools*100):.1f}%" if test_suite.total_tools > 0 else "N/A")
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
            status = "✅" if result.metadata_complete else "❌"
            report.append(f"{status} {result.tool_name}")
            report.append(f"    Description: {'✅' if result.description_valid else '❌'}")
            report.append(f"    Documentation: {'✅' if result.documentation_valid else '❌'}")
            report.append(f"    Examples: {'✅' if result.examples_valid else '❌'}")
            report.append(f"    Metadata Complete: {'✅' if result.metadata_complete else '❌'}")
            report.append(f"    Time: {result.validation_time_ms:.2f} ms")
            if result.validation_errors:
                for error in result.validation_errors:
                    report.append(f"    Error: {error}")
            if result.error_message:
                report.append(f"    Error: {result.error_message}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tool metadata validation tests"""
    logger.info("Starting Tool Metadata Validation Testing")
    
    # Initialize validator
    validator = ToolMetadataValidator()
    
    # Run comprehensive validation
    test_suite = validator.validate_all_tool_metadata()
    
    # Generate and display report
    report = validator.generate_test_report(test_suite)
    print(report)
    
    # Save results
    validator.save_test_results(test_suite)
    
    # Return success/failure based on results
    success_rate = test_suite.complete_metadata / test_suite.total_tools if test_suite.total_tools > 0 else 0
    logger.info(f"Tool metadata validation completed with {success_rate*100:.1f}% success rate")
    
    return success_rate >= 0.90  # 90% success threshold (metadata can be improved over time)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 