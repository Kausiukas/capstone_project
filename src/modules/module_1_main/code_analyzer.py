"""
Code Analyzer - Handles code explanation, analysis, and semantic understanding
"""

import ast
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CodeElement:
    """Code element information"""
    name: str
    type: str
    line_start: int
    line_end: int
    complexity: int
    description: str

@dataclass
class CodeMetrics:
    """Code metrics structure"""
    lines_of_code: int
    functions: int
    classes: int
    imports: int
    complexity: float
    maintainability_index: float

class CodeAnalyzer:
    """
    Analyzes code for understanding, explanation, and metrics
    """
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }
        self.analysis_cache = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the code analyzer
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing code analyzer...")
            
            # Clear analysis cache
            self.analysis_cache.clear()
            
            # Verify supported languages configuration
            if not self.supported_languages:
                logger.warning("No supported languages configured")
            
            self.initialized = True
            logger.info("Code analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize code analyzer: {e}")
            return False
        
    async def analyze_code(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        Analyze code file for structure, metrics, and understanding
        
        Args:
            file_path: Path to the code file
            content: Optional file content (if not provided, will read from file)
            
        Returns:
            Dictionary containing code analysis results
        """
        try:
            # Read content if not provided
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            file_ext = Path(file_path).suffix.lower()
            language = self.supported_languages.get(file_ext, 'unknown')
            
            # Check cache
            cache_key = f"{file_path}_{hash(content)}"
            if cache_key in self.analysis_cache:
                return {
                    "success": True,
                    "cached": True,
                    "analysis": self.analysis_cache[cache_key]
                }
            
            # Perform analysis based on language
            if language == 'python':
                analysis = await self._analyze_python_code(content, file_path)
            elif language in ['javascript', 'typescript']:
                analysis = await self._analyze_javascript_code(content, file_path)
            else:
                analysis = await self._analyze_generic_code(content, file_path)
            
            # Add common metrics
            analysis["language"] = language
            analysis["file_path"] = file_path
            analysis["file_size"] = len(content)
            
            # Cache analysis
            self.analysis_cache[cache_key] = analysis
            
            return {
                "success": True,
                "cached": False,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def _analyze_python_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python code specifically
        
        Args:
            content: Python code content
            file_path: Path to the file
            
        Returns:
            Dictionary containing Python-specific analysis
        """
        try:
            tree = ast.parse(content)
            
            analysis = {
                "elements": [],
                "metrics": {},
                "structure": {},
                "dependencies": [],
                "issues": []
            }
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            analysis["dependencies"] = imports
            
            # Extract functions and classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [d.id for d in node.decorator_list if hasattr(d, 'id')],
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            methods.append({
                                "name": child.name,
                                "line_start": child.lineno,
                                "line_end": child.end_lineno,
                                "args": [arg.arg for arg in child.args.args],
                                "docstring": ast.get_docstring(child)
                            })
                    
                    classes.append({
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "bases": [base.id for base in node.bases if hasattr(base, 'id')],
                        "methods": methods,
                        "docstring": ast.get_docstring(node)
                    })
            
            analysis["structure"]["functions"] = functions
            analysis["structure"]["classes"] = classes
            
            # Calculate metrics
            lines = content.split('\n')
            loc = len([line for line in lines if line.strip()])
            comments = len([line for line in lines if line.strip().startswith('#')])
            
            # Calculate cyclomatic complexity
            complexity = self._calculate_python_complexity(tree)
            
            analysis["metrics"] = {
                "lines_of_code": loc,
                "comment_lines": comments,
                "functions": len(functions),
                "classes": len(classes),
                "imports": len(imports),
                "cyclomatic_complexity": complexity,
                "maintainability_index": self._calculate_maintainability_index(loc, complexity, comments)
            }
            
            # Detect potential issues
            issues = self._detect_python_issues(tree)
            analysis["issues"] = issues
            
            return analysis
            
        except SyntaxError as e:
            return {
                "error": f"Syntax error: {str(e)}",
                "line": e.lineno,
                "offset": e.offset
            }
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_javascript_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript code
        
        Args:
            content: JavaScript/TypeScript code content
            file_path: Path to the file
            
        Returns:
            Dictionary containing JavaScript-specific analysis
        """
        try:
            analysis = {
                "elements": [],
                "metrics": {},
                "structure": {},
                "dependencies": [],
                "issues": []
            }
            
            lines = content.split('\n')
            
            # Extract imports
            imports = []
            import_patterns = [
                r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                r'import\s+[\'"]([^\'"]+)[\'"]'
            ]
            
            for line in lines:
                for pattern in import_patterns:
                    matches = re.findall(pattern, line)
                    imports.extend(matches)
            
            analysis["dependencies"] = list(set(imports))
            
            # Extract functions
            functions = []
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
                            functions.append({
                                "name": match,
                                "line_start": i,
                                "line_end": i,  # Simplified
                                "type": "function"
                            })
            
            # Extract classes
            classes = []
            class_pattern = r'class\s+(\w+)'
            
            for i, line in enumerate(lines, 1):
                matches = re.findall(class_pattern, line)
                for match in matches:
                    classes.append({
                        "name": match,
                        "line_start": i,
                        "line_end": i,  # Simplified
                        "type": "class"
                    })
            
            analysis["structure"]["functions"] = functions
            analysis["structure"]["classes"] = classes
            
            # Calculate metrics
            loc = len([line for line in lines if line.strip()])
            comments = len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')])
            
            analysis["metrics"] = {
                "lines_of_code": loc,
                "comment_lines": comments,
                "functions": len(functions),
                "classes": len(classes),
                "imports": len(imports),
                "cyclomatic_complexity": self._calculate_js_complexity(content),
                "maintainability_index": self._calculate_maintainability_index(loc, 1, comments)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript code: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_generic_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze generic code (fallback for unsupported languages)
        
        Args:
            content: Code content
            file_path: Path to the file
            
        Returns:
            Dictionary containing generic analysis
        """
        try:
            lines = content.split('\n')
            
            analysis = {
                "elements": [],
                "metrics": {},
                "structure": {},
                "dependencies": [],
                "issues": []
            }
            
            # Basic metrics
            loc = len([line for line in lines if line.strip()])
            comment_patterns = ['//', '/*', '#', '--', '<!--']
            comments = len([line for line in lines 
                          if any(line.strip().startswith(pattern) for pattern in comment_patterns)])
            
            analysis["metrics"] = {
                "lines_of_code": loc,
                "comment_lines": comments,
                "file_size_bytes": len(content),
                "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing generic code: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.AsyncWith):
                complexity += 1
        
        return complexity
    
    def _calculate_js_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity for JavaScript code"""
        complexity = 1  # Base complexity
        
        # Count control flow statements
        patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bswitch\b', r'\bcatch\b', r'\bcase\b', r'\b&&\b', r'\b\|\|\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            complexity += len(matches)
        
        return complexity
    
    def _calculate_maintainability_index(self, loc: int, complexity: int, comments: int) -> float:
        """Calculate maintainability index"""
        # Simplified maintainability index calculation
        if loc == 0:
            return 100.0
        
        # Halstead volume approximation
        volume = loc * complexity
        
        # Maintainability index formula (simplified)
        mi = 171 - 5.2 * complexity - 0.23 * volume - 16.2 * (loc / 100)
        
        return max(0.0, min(100.0, mi))
    
    def _detect_python_issues(self, tree: ast.AST) -> List[str]:
        """Detect potential issues in Python code"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for long functions
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and node.lineno:
                    if node.end_lineno - node.lineno > 50:
                        issues.append(f"Long function '{node.name}' ({node.end_lineno - node.lineno} lines)")
            
            # Check for long classes
            elif isinstance(node, ast.ClassDef):
                if node.end_lineno and node.lineno:
                    if node.end_lineno - node.lineno > 200:
                        issues.append(f"Long class '{node.name}' ({node.end_lineno - node.lineno} lines)")
            
            # Check for nested functions (potential issue)
            elif isinstance(node, ast.FunctionDef):
                if any(isinstance(parent, ast.FunctionDef) for parent in ast.walk(node)):
                    issues.append(f"Nested function '{node.name}' detected")
        
        return issues
    
    async def explain_code(self, file_path: str, target_element: str = None) -> Dict[str, Any]:
        """
        Generate explanation for code or specific element
        
        Args:
            file_path: Path to the code file
            target_element: Specific element to explain (function, class, etc.)
            
        Returns:
            Dictionary containing code explanation
        """
        try:
            # First analyze the code
            analysis_result = await self.analyze_code(file_path)
            
            if not analysis_result["success"]:
                return analysis_result
            
            analysis = analysis_result["analysis"]
            
            if target_element:
                # Explain specific element
                explanation = await self._explain_element(analysis, target_element)
            else:
                # Explain entire file
                explanation = await self._explain_file(analysis)
            
            return {
                "success": True,
                "file_path": file_path,
                "target_element": target_element,
                "explanation": explanation,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error explaining code {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def _explain_file(self, analysis: Dict[str, Any]) -> str:
        """Generate explanation for entire file"""
        explanation = []
        
        # File overview
        metrics = analysis.get("metrics", {})
        explanation.append(f"This is a {analysis.get('language', 'unknown')} file with {metrics.get('lines_of_code', 0)} lines of code.")
        
        # Structure overview
        structure = analysis.get("structure", {})
        functions = structure.get("functions", [])
        classes = structure.get("classes", [])
        
        if functions:
            explanation.append(f"It contains {len(functions)} function(s).")
        if classes:
            explanation.append(f"It contains {len(classes)} class(es).")
        
        # Dependencies
        dependencies = analysis.get("dependencies", [])
        if dependencies:
            explanation.append(f"It imports {len(dependencies)} dependency(ies).")
        
        # Issues
        issues = analysis.get("issues", [])
        if issues:
            explanation.append(f"Potential issues detected: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                explanation.append(f"- {issue}")
        
        return " ".join(explanation)
    
    async def _explain_element(self, analysis: Dict[str, Any], element_name: str) -> str:
        """Generate explanation for specific element"""
        structure = analysis.get("structure", {})
        
        # Look for function
        for func in structure.get("functions", []):
            if func["name"] == element_name:
                return f"Function '{element_name}' is defined at line {func.get('line_start', 'unknown')}. " \
                       f"It has {len(func.get('args', []))} parameters. " \
                       f"{'Has docstring.' if func.get('docstring') else 'No docstring.'}"
        
        # Look for class
        for cls in structure.get("classes", []):
            if cls["name"] == element_name:
                return f"Class '{element_name}' is defined at line {cls.get('line_start', 'unknown')}. " \
                       f"It has {len(cls.get('methods', []))} methods. " \
                       f"{'Has docstring.' if cls.get('docstring') else 'No docstring.'}"
        
        return f"Element '{element_name}' not found in the code."
    
    async def cleanup(self):
        """
        Cleanup resources and reset state
        """
        try:
            # Clear analysis cache
            self.analysis_cache.clear()
            self.initialized = False
            logger.info("Code analyzer cleanup completed")
        except Exception as e:
            logger.error(f"Error during code analyzer cleanup: {e}") 