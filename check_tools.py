#!/usr/bin/env python3
"""
Check available tools in the MCP connector
"""

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

def main():
    print("🔍 Checking available tools in MCP connector...")
    
    # Create connector instance
    connector = SimpleLangFlowMCPConnector()
    
    print(f"\n📋 Total tools available: {len(connector.tools)}")
    print("\n📝 Available tools:")
    print("-" * 40)
    
    for i, tool in enumerate(connector.tools, 1):
        print(f"{i:2d}. {tool['name']}")
        print(f"    Description: {tool['description']}")
        print()
    
    # Check specifically for list_files_metadata_only
    metadata_tool = None
    for tool in connector.tools:
        if tool['name'] == 'list_files_metadata_only':
            metadata_tool = tool
            break
    
    if metadata_tool:
        print("✅ list_files_metadata_only tool is available!")
        print(f"   Description: {metadata_tool['description']}")
    else:
        print("❌ list_files_metadata_only tool is NOT available!")
        print("   This indicates the MCP server needs to be restarted.")

if __name__ == "__main__":
    main() 