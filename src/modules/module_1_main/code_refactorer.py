"""
Code Refactorer - Handles code refactoring operations
"""

import ast
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion structure"""
    type: str
    description: str
    line_start: int
    line_end: int
    severity: str
    suggested_code: str

class CodeRefactorer:
    """
    Handles code refactoring operations and suggestions
    """
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        self.refactoring_patterns = {
            'python': {
                'long_function': {'threshold': 50, 'severity': 'medium'},
                'long_class': {'threshold': 200, 'severity': 'medium'},
                'nested_functions': {'severity': 'low'},
                'magic_numbers': {'severity': 'low'},
                'duplicate_code': {'severity': 'high'}
            }
        }
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the code refactorer
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing code refactorer...")
            
            # Verify supported languages configuration
            if not self.supported_languages:
                logger.warning("No supported languages configured")
            
            # Verify refactoring patterns configuration
            if not self.refactoring_patterns:
                logger.warning("No refactoring patterns configured")
            
            self.initialized = True
            logger.info("Code refactorer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize code refactorer: {e}")
            return False
        
    async def analyze_refactoring_opportunities(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze code for refactoring opportunities
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Dictionary containing refactoring suggestions
        """
        try:
            # Read file content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            file_ext = Path(file_path).suffix.lower()
            language = self.supported_languages.get(file_ext, 'unknown')
            
            if language == 'python':
                suggestions = await self._analyze_python_refactoring(content, file_path)
            elif language in ['javascript', 'typescript']:
                suggestions = await self._analyze_javascript_refactoring(content, file_path)
            else:
                suggestions = await self._analyze_generic_refactoring(content, file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "language": language,
                "suggestions": suggestions,
                "total_suggestions": len(suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing refactoring opportunities for {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def _analyze_python_refactoring(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze Python code for refactoring opportunities
        
        Args:
            content: Python code content
            file_path: Path to the file
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Check for long functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.end_lineno and node.lineno:
                        function_length = node.end_lineno - node.lineno
                        if function_length > self.refactoring_patterns['python']['long_function']['threshold']:
                            suggestions.append({
                                "type": "long_function",
                                "description": f"Function '{node.name}' is {function_length} lines long. Consider breaking it into smaller functions.",
                                "line_start": node.lineno,
                                "line_end": node.end_lineno,
                                "severity": "medium",
                                "element_name": node.name,
                                "suggested_action": "Extract methods or split into smaller functions"
                            })
            
            # Check for long classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.end_lineno and node.lineno:
                        class_length = node.end_lineno - node.lineno
                        if class_length > self.refactoring_patterns['python']['long_class']['threshold']:
                            suggestions.append({
                                "type": "long_class",
                                "description": f"Class '{node.name}' is {class_length} lines long. Consider splitting it into multiple classes.",
                                "line_start": node.lineno,
                                "line_end": node.end_lineno,
                                "severity": "medium",
                                "element_name": node.name,
                                "suggested_action": "Split into multiple classes or extract mixins"
                            })
            
            # Check for magic numbers
            magic_numbers = re.findall(r'\b\d{2,}\b', content)
            if magic_numbers:
                unique_numbers = list(set(magic_numbers))
                suggestions.append({
                    "type": "magic_numbers",
                    "description": f"Found {len(unique_numbers)} magic numbers: {', '.join(unique_numbers[:5])}",
                    "line_start": 1,
                    "line_end": len(lines),
                    "severity": "low",
                    "element_name": "magic_numbers",
                    "suggested_action": "Define constants for these numbers"
                })
            
            # Check for nested functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for child in ast.walk(node):
                        if isinstance(child, ast.FunctionDef) and child != node:
                            suggestions.append({
                                "type": "nested_function",
                                "description": f"Nested function '{child.name}' found in '{node.name}'. Consider extracting it.",
                                "line_start": child.lineno,
                                "line_end": child.end_lineno,
                                "severity": "low",
                                "element_name": child.name,
                                "suggested_action": "Extract nested function to module level"
                            })
                            break
            
            # Check for duplicate code patterns
            duplicate_patterns = self._find_duplicate_patterns(content)
            if duplicate_patterns:
                suggestions.append({
                    "type": "duplicate_code",
                    "description": f"Found {len(duplicate_patterns)} potential duplicate code patterns",
                    "line_start": 1,
                    "line_end": len(lines),
                    "severity": "high",
                    "element_name": "duplicate_patterns",
                    "suggested_action": "Extract common code into functions or classes",
                    "patterns": duplicate_patterns
                })
            
        except SyntaxError as e:
            suggestions.append({
                "type": "syntax_error",
                "description": f"Syntax error: {str(e)}",
                "line_start": e.lineno,
                "line_end": e.lineno,
                "severity": "high",
                "element_name": "syntax_error",
                "suggested_action": "Fix syntax error before refactoring"
            })
        except Exception as e:
            logger.error(f"Error analyzing Python refactoring: {str(e)}")
        
        return suggestions
    
    async def _analyze_javascript_refactoring(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze JavaScript/TypeScript code for refactoring opportunities
        
        Args:
            content: JavaScript/TypeScript code content
            file_path: Path to the file
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        lines = content.split('\n')
        
        try:
            # Check for long functions
            function_patterns = [
                r'(?:function\s+)?(\w+)\s*\([^)]*\)\s*{',
                r'(\w+)\s*[:=]\s*(?:function|\([^)]*\)\s*=>)',
                r'(\w+)\s*[:=]\s*async\s*\([^)]*\)\s*=>'
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern in function_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match and match not in ['if', 'for', 'while', 'switch']:
                            # Simple check for function length (simplified)
                            suggestions.append({
                                "type": "function_analysis",
                                "description": f"Function '{match}' found. Consider analyzing its complexity.",
                                "line_start": i,
                                "line_end": i,
                                "severity": "low",
                                "element_name": match,
                                "suggested_action": "Review function complexity and length"
                            })
            
            # Check for magic numbers
            magic_numbers = re.findall(r'\b\d{2,}\b', content)
            if magic_numbers:
                unique_numbers = list(set(magic_numbers))
                suggestions.append({
                    "type": "magic_numbers",
                    "description": f"Found {len(unique_numbers)} magic numbers: {', '.join(unique_numbers[:5])}",
                    "line_start": 1,
                    "line_end": len(lines),
                    "severity": "low",
                    "element_name": "magic_numbers",
                    "suggested_action": "Define constants for these numbers"
                })
            
            # Check for long lines
            long_lines = []
            for i, line in enumerate(lines, 1):
                if len(line) > 120:  # Common threshold
                    long_lines.append(i)
            
            if long_lines:
                suggestions.append({
                    "type": "long_lines",
                    "description": f"Found {len(long_lines)} lines longer than 120 characters",
                    "line_start": min(long_lines),
                    "line_end": max(long_lines),
                    "severity": "low",
                    "element_name": "long_lines",
                    "suggested_action": "Break long lines for better readability"
                })
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript refactoring: {str(e)}")
        
        return suggestions
    
    async def _analyze_generic_refactoring(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze generic code for refactoring opportunities
        
        Args:
            content: Code content
            file_path: Path to the file
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        lines = content.split('\n')
        
        try:
            # Check for long lines
            long_lines = []
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    long_lines.append(i)
            
            if long_lines:
                suggestions.append({
                    "type": "long_lines",
                    "description": f"Found {len(long_lines)} lines longer than 120 characters",
                    "line_start": min(long_lines),
                    "line_end": max(long_lines),
                    "severity": "low",
                    "element_name": "long_lines",
                    "suggested_action": "Break long lines for better readability"
                })
            
            # Check for magic numbers
            magic_numbers = re.findall(r'\b\d{2,}\b', content)
            if magic_numbers:
                unique_numbers = list(set(magic_numbers))
                suggestions.append({
                    "type": "magic_numbers",
                    "description": f"Found {len(unique_numbers)} magic numbers: {', '.join(unique_numbers[:5])}",
                    "line_start": 1,
                    "line_end": len(lines),
                    "severity": "low",
                    "element_name": "magic_numbers",
                    "suggested_action": "Define constants for these numbers"
                })
            
        except Exception as e:
            logger.error(f"Error analyzing generic refactoring: {str(e)}")
        
        return suggestions
    
    def _find_duplicate_patterns(self, content: str) -> List[str]:
        """
        Find potential duplicate code patterns
        
        Args:
            content: Code content
            
        Returns:
            List of duplicate patterns
        """
        patterns = []
        lines = content.split('\n')
        
        # Simple pattern detection (can be enhanced)
        # Look for repeated 3+ line sequences
        for i in range(len(lines) - 2):
            pattern = '\n'.join(lines[i:i+3])
            if len(pattern.strip()) > 20:  # Minimum pattern length
                # Count occurrences
                count = content.count(pattern)
                if count > 1:
                    patterns.append(f"Pattern at line {i+1} (appears {count} times)")
        
        return patterns[:5]  # Limit to first 5 patterns
    
    async def apply_refactoring(self, file_path: str, refactoring_type: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a specific refactoring to the code
        
        Args:
            file_path: Path to the code file
            refactoring_type: Type of refactoring to apply
            parameters: Parameters for the refactoring
            
        Returns:
            Dictionary containing refactoring result
        """
        try:
            # Read original content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                original_content = await f.read()
            
            # Apply refactoring based on type
            if refactoring_type == "extract_function":
                result = await self._extract_function(original_content, parameters)
            elif refactoring_type == "extract_class":
                result = await self._extract_class(original_content, parameters)
            elif refactoring_type == "rename_variable":
                result = await self._rename_variable(original_content, parameters)
            elif refactoring_type == "extract_constant":
                result = await self._extract_constant(original_content, parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown refactoring type: {refactoring_type}"
                }
            
            if result["success"]:
                # Write refactored content
                backup_path = f"{file_path}.backup"
                async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                    await f.write(original_content)
                
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(result["refactored_content"])
                
                result["backup_path"] = backup_path
                result["file_path"] = file_path
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying refactoring to {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def _extract_function(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code into a new function"""
        try:
            start_line = parameters.get("start_line", 1)
            end_line = parameters.get("end_line", 1)
            function_name = parameters.get("function_name", "extracted_function")
            
            lines = content.split('\n')
            extracted_lines = lines[start_line-1:end_line]
            extracted_code = '\n'.join(extracted_lines)
            
            # Create function definition
            function_def = f"\ndef {function_name}():\n"
            function_def += '\n'.join(f"    {line}" for line in extracted_lines)
            function_def += f"\n\n# Call the extracted function\n{function_name}()\n"
            
            # Replace original code with function call
            new_lines = lines[:start_line-1] + [f"{function_name}()"] + lines[end_line:]
            refactored_content = '\n'.join(new_lines)
            
            return {
                "success": True,
                "refactored_content": refactored_content,
                "extracted_function": function_def,
                "description": f"Extracted lines {start_line}-{end_line} into function '{function_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_class(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code into a new class"""
        try:
            class_name = parameters.get("class_name", "ExtractedClass")
            methods = parameters.get("methods", [])
            
            # Create class definition
            class_def = f"\nclass {class_name}:\n"
            for method in methods:
                class_def += f"    def {method['name']}(self):\n"
                class_def += f"        {method.get('body', 'pass')}\n"
            
            refactored_content = content + class_def
            
            return {
                "success": True,
                "refactored_content": refactored_content,
                "extracted_class": class_def,
                "description": f"Extracted code into class '{class_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _rename_variable(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Rename a variable throughout the code"""
        try:
            old_name = parameters.get("old_name")
            new_name = parameters.get("new_name")
            
            if not old_name or not new_name:
                return {
                    "success": False,
                    "error": "Both old_name and new_name must be provided"
                }
            
            # Simple string replacement (can be enhanced with AST analysis)
            refactored_content = content.replace(old_name, new_name)
            
            return {
                "success": True,
                "refactored_content": refactored_content,
                "description": f"Renamed '{old_name}' to '{new_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_constant(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract magic numbers into constants"""
        try:
            magic_number = parameters.get("magic_number")
            constant_name = parameters.get("constant_name", "MAGIC_NUMBER")
            
            if not magic_number:
                return {
                    "success": False,
                    "error": "magic_number must be provided"
                }
            
            # Add constant definition at the top
            constant_def = f"{constant_name} = {magic_number}\n\n"
            refactored_content = constant_def + content.replace(str(magic_number), constant_name)
            
            return {
                "success": True,
                "refactored_content": refactored_content,
                "extracted_constant": constant_def,
                "description": f"Extracted {magic_number} into constant '{constant_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 