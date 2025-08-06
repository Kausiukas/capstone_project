#!/usr/bin/env python3
"""
Test Inspector Connection

This script tests the Inspector CLI connection to our MCP server
to verify that the integration issues have been resolved.

Part of Task 2.1: Protocol Compliance Testing - Inspector CLI Integration Fix
"""

import logging
from inspector_cli_utils import inspector_cli

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mcp_server_connection():
    """Test connection to the MCP server"""
    logger.info("Testing MCP server connection with Inspector CLI...")
    
    # Test with the simple MCP server
    mcp_server_path = "mcp_langflow_connector_simple.py"
    
    # Test basic connection
    if inspector_cli.test_inspector_connection(mcp_server_path):
        logger.info("✅ MCP server connection successful!")
        
        # Get tools list
        tools = inspector_cli.get_tools_list(mcp_server_path)
        if tools:
            logger.info(f"✅ Successfully retrieved {len(tools)} tools from MCP server")
            logger.info(f"First 5 tools: {tools[:5]}")
            return True
        else:
            logger.error("❌ Failed to retrieve tools list")
            return False
    else:
        logger.error("❌ MCP server connection failed")
        return False


def test_specific_tool_execution():
    """Test execution of a specific tool"""
    logger.info("Testing specific tool execution...")
    
    mcp_server_path = "mcp_langflow_connector_simple.py"
    
    # Get tools list first
    tools = inspector_cli.get_tools_list(mcp_server_path)
    if not tools:
        logger.error("❌ No tools available for testing")
        return False
    
    # Test with the first tool
    test_tool = tools[0]
    logger.info(f"Testing tool: {test_tool}")
    
    success, response, error = inspector_cli.execute_tool(
        mcp_server_path=mcp_server_path,
        tool_name=test_tool,
        arguments={},  # Empty arguments for testing
        timeout=30
    )
    
    if success:
        logger.info(f"✅ Tool execution successful: {test_tool}")
        logger.info(f"Response: {response}")
        return True
    else:
        logger.error(f"❌ Tool execution failed: {error}")
        return False


def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("INSPECTOR CLI INTEGRATION TEST")
    logger.info("=" * 60)
    
    # Test 1: Basic connection
    logger.info("\nTest 1: Basic MCP Server Connection")
    logger.info("-" * 40)
    connection_success = test_mcp_server_connection()
    
    # Test 2: Tool execution
    logger.info("\nTest 2: Tool Execution")
    logger.info("-" * 40)
    execution_success = test_specific_tool_execution()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    if connection_success and execution_success:
        logger.info("✅ ALL TESTS PASSED - Inspector CLI integration is working!")
        logger.info("Task 2.1 Inspector CLI integration issues have been resolved.")
        return True
    else:
        logger.error("❌ SOME TESTS FAILED - Inspector CLI integration needs more work")
        if not connection_success:
            logger.error("   - MCP server connection failed")
        if not execution_success:
            logger.error("   - Tool execution failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 