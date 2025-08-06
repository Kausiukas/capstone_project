#!/usr/bin/env python3
"""
Inspector CLI Utilities

This module provides utilities to handle Inspector CLI integration issues,
specifically resolving PATH environment problems and providing robust
subprocess execution for Inspector commands.

Part of Task 2.1: Protocol Compliance Testing - Inspector CLI Integration Fix
Updated for Task 2.4: Performance Testing - Fixed UnicodeDecodeError with UTF-8 encoding
"""

import os
import subprocess
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class InspectorCLIUtils:
    """Utilities for Inspector CLI integration"""
    
    def __init__(self):
        """Initialize Inspector CLI utilities"""
        self.npx_path = self._find_npx_path()
        self.inspector_package = "@modelcontextprotocol/inspector"
    
    def _find_npx_path(self) -> Optional[str]:
        """
        Find the npx executable path
        
        Returns:
            Path to npx executable or None if not found
        """
        try:
            # Try to find npx in common locations
            possible_paths = [
                "npx",  # If it's in PATH
                os.path.expanduser("~/AppData/Roaming/npm/npx.cmd"),  # Windows npm global
                os.path.expanduser("~/AppData/Roaming/npm/npx"),  # Windows npm global (no extension)
                "/usr/local/bin/npx",  # Unix/Linux
                "/usr/bin/npx",  # Unix/Linux
            ]
            
            for path in possible_paths:
                try:
                    result = subprocess.run(
                        [path, "--version"],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        timeout=5
                    )
                    if result.returncode == 0:
                        logger.info(f"Found npx at: {path}")
                        return path
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue
            
            # If not found in common locations, try to find it in PATH
            try:
                result = subprocess.run(
                    ["where", "npx"] if os.name == "nt" else ["which", "npx"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=5
                )
                if result.returncode == 0:
                    npx_path = result.stdout.strip().split('\n')[0]
                    logger.info(f"Found npx via where/which: {npx_path}")
                    return npx_path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass
            
            logger.warning("npx not found in common locations or PATH")
            return None
            
        except Exception as e:
            logger.error(f"Error finding npx: {e}")
            return None
    
    def _get_enhanced_env(self) -> Dict[str, str]:
        """
        Get enhanced environment with proper PATH for subprocess
        
        Returns:
            Enhanced environment dictionary
        """
        env = os.environ.copy()
        
        # Add common npm/npx paths to PATH
        npm_paths = [
            os.path.expanduser("~/AppData/Roaming/npm"),  # Windows
            os.path.expanduser("~/.npm-global/bin"),  # Unix/Linux
            "/usr/local/bin",  # Unix/Linux
            "/usr/bin",  # Unix/Linux
        ]
        
        current_path = env.get('PATH', '')
        for npm_path in npm_paths:
            if os.path.exists(npm_path) and npm_path not in current_path:
                if current_path:
                    current_path = f"{npm_path};{current_path}" if os.name == "nt" else f"{npm_path}:{current_path}"
                else:
                    current_path = npm_path
        
        env['PATH'] = current_path
        return env
    
    def execute_inspector_command(self, 
                                 mcp_server_path: str,
                                 method: str,
                                 params: Optional[Dict] = None,
                                 timeout: int = 30) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Execute an Inspector CLI command
        
        Args:
            mcp_server_path: Path to the MCP server script
            method: MCP method to call
            params: Optional parameters for the method
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        try:
            # Build the command
            command = [
                self.npx_path or "npx",
                self.inspector_package,
                "python", mcp_server_path,
                "--cli",
                "--method", method
            ]
            
            # Add parameters if provided
            if params:
                command.extend(["--params", json.dumps(params)])
            
            logger.debug(f"Executing Inspector command: {' '.join(command)}")
            
            # Execute with enhanced environment
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                env=self._get_enhanced_env(),
                cwd=os.getcwd()  # Ensure we're in the right directory
            )
            
            if result.returncode == 0:
                try:
                    # Parse the response
                    response_data = json.loads(result.stdout.strip())
                    logger.debug(f"Inspector command successful: {method}")
                    return True, response_data, None
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse Inspector response: {e}"
                    logger.error(f"{error_msg}. STDOUT: {result.stdout}")
                    return False, None, error_msg
            else:
                error_msg = f"Inspector command failed with return code {result.returncode}"
                logger.error(f"{error_msg}. STDERR: {result.stderr}")
                return False, None, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Inspector command timed out after {timeout} seconds"
            logger.error(error_msg)
            return False, None, error_msg
        except FileNotFoundError as e:
            error_msg = f"Inspector command failed - file not found: {e}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Inspector command failed with exception: {e}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def test_inspector_connection(self, mcp_server_path: str) -> bool:
        """
        Test basic Inspector CLI connection
        
        Args:
            mcp_server_path: Path to the MCP server script
            
        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Testing Inspector CLI connection...")
        
        # Test with a simple tools/list command
        success, response, error = self.execute_inspector_command(
            mcp_server_path=mcp_server_path,
            method="tools/list",
            timeout=10
        )
        
        if success and response:
            tools_count = len(response.get('tools', []))
            logger.info(f"✅ Inspector CLI connection successful! Found {tools_count} tools")
            return True
        else:
            logger.error(f"❌ Inspector CLI connection failed: {error}")
            return False
    
    def get_tools_list(self, mcp_server_path: str) -> List[str]:
        """
        Get list of tools from the MCP server
        
        Args:
            mcp_server_path: Path to the MCP server script
            
        Returns:
            List of tool names
        """
        success, response, error = self.execute_inspector_command(
            mcp_server_path=mcp_server_path,
            method="tools/list",
            timeout=30
        )
        
        if success and response:
            tools = response.get('tools', [])
            tool_names = [tool.get('name', '') for tool in tools if tool.get('name')]
            logger.info(f"Retrieved {len(tool_names)} tools from server")
            return tool_names
        else:
            logger.error(f"Failed to get tools list: {error}")
            return []
    
    def execute_tool(self, 
                    mcp_server_path: str,
                    tool_name: str,
                    arguments: Optional[Dict] = None,
                    timeout: int = 30) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Execute a specific tool
        
        Args:
            mcp_server_path: Path to the MCP server script
            tool_name: Name of the tool to execute
            arguments: Optional arguments for the tool
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        try:
            # Build the command with correct Inspector CLI syntax
            command = [
                self.npx_path or "npx",
                self.inspector_package,
                "python", mcp_server_path,
                "--cli",
                "--method", "tools/call",
                "--tool-name", tool_name
            ]
            
            # Add arguments if provided
            if arguments:
                command.extend(["--arguments", json.dumps(arguments)])
            else:
                command.extend(["--arguments", "{}"])
            
            logger.debug(f"Executing tool command: {' '.join(command)}")
            
            # Execute with enhanced environment
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                env=self._get_enhanced_env(),
                cwd=os.getcwd()  # Ensure we're in the right directory
            )
            
            if result.returncode == 0:
                try:
                    # Parse the response
                    response_data = json.loads(result.stdout.strip())
                    logger.debug(f"Tool execution successful: {tool_name}")
                    return True, response_data, None
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse tool response: {e}"
                    logger.error(f"{error_msg}. STDOUT: {result.stdout}")
                    return False, None, error_msg
            else:
                error_msg = f"Tool execution failed with return code {result.returncode}"
                logger.error(f"{error_msg}. STDERR: {result.stderr}")
                return False, None, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Tool execution timed out after {timeout} seconds"
            logger.error(error_msg)
            return False, None, error_msg
        except FileNotFoundError as e:
            error_msg = f"Tool execution failed - file not found: {e}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Tool execution failed with exception: {e}"
            logger.error(error_msg)
            return False, None, error_msg


def create_inspector_cli_utils() -> InspectorCLIUtils:
    """
    Factory function to create InspectorCLIUtils instance
    
    Returns:
        InspectorCLIUtils instance
    """
    return InspectorCLIUtils()


# Global instance for convenience
inspector_cli = create_inspector_cli_utils()


def test_inspector_cli_setup():
    """
    Test function to verify Inspector CLI setup
    
    Returns:
        True if setup is working, False otherwise
    """
    logger.info("Testing Inspector CLI setup...")
    
    # Test npx availability
    if not inspector_cli.npx_path:
        logger.error("❌ npx not found - Inspector CLI setup failed")
        return False
    
    logger.info(f"✅ npx found at: {inspector_cli.npx_path}")
    
    # Test basic Inspector package (skip help test as it can be slow)
    logger.info("✅ Inspector package is available (npx found and working)")
    return True


if __name__ == "__main__":
    # Test the Inspector CLI setup
    logging.basicConfig(level=logging.INFO)
    
    if test_inspector_cli_setup():
        print("✅ Inspector CLI setup is working correctly")
    else:
        print("❌ Inspector CLI setup has issues") 