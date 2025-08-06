#!/usr/bin/env python3
"""
LangFlow Automatic File Reading Troubleshooting Script
Helps diagnose and fix issues with LangFlow automatically reading files
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

class LangFlowTroubleshooter:
    """Troubleshoot LangFlow automatic file reading issues"""
    
    def __init__(self):
        self.connector = None
        self.test_results = []
    
    async def test_list_files_tool(self) -> Dict[str, Any]:
        """Test the list_files tool to ensure it returns metadata only"""
        try:
            # Import the connector
            sys.path.append('.')
            from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector
            
            self.connector = SimpleLangFlowMCPConnector()
            
            # Test basic directory listing
            result = await self.connector.handle_list_files({"directory": "."})
            
            # Check if result contains file content (which it shouldn't)
            content_indicators = [
                "file_path text",
                "ACTUAL_STATUS.md",
                "clean_demo.py",
                "# LangFlow Connect"
            ]
            
            has_content = any(indicator in result for indicator in content_indicators)
            
            return {
                "success": True,
                "has_file_content": has_content,
                "result_preview": result[:500] + "..." if len(result) > 500 else result,
                "result_length": len(result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_metadata_only_tool(self) -> Dict[str, Any]:
        """Test the new list_files_metadata_only tool"""
        try:
            if not self.connector:
                return {"success": False, "error": "Connector not initialized"}
            
            result = await self.connector.handle_list_files_metadata_only({"directory": "."})
            
            # Check for strict metadata indicators
            metadata_indicators = [
                "STRICT METADATA ONLY",
                "FILE_METADATA_ONLY",
                "No file paths are returned"
            ]
            
            has_metadata_indicators = all(indicator in result for indicator in metadata_indicators)
            
            return {
                "success": True,
                "has_metadata_indicators": has_metadata_indicators,
                "result_preview": result[:500] + "..." if len(result) > 500 else result,
                "result_length": len(result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_langflow_config_recommendations(self) -> List[str]:
        """Generate recommendations for LangFlow configuration"""
        recommendations = [
            "🔧 LangFlow Configuration Recommendations:",
            "",
            "1. **Disable Automatic File Reading**:",
            "   - In LangFlow settings, look for 'Auto-read files' or 'Automatic file processing'",
            "   - Disable this feature to prevent automatic file content reading",
            "",
            "2. **Use Metadata-Only Tools**:",
            "   - Use 'list_files_metadata_only' instead of 'list_files'",
            "   - This tool explicitly prevents file path exposure",
            "",
            "3. **Configure Memory Limits**:",
            "   - Set lower batch sizes (5-10) for file listings",
            "   - Use pagination with offset parameters",
            "",
            "4. **Agent Configuration**:",
            "   - Configure agents to use explicit 'read_file' calls only when needed",
            "   - Avoid automatic file processing based on file listings",
            "",
            "5. **Tool Selection**:",
            "   - Prefer 'list_files_metadata_only' for directory exploration",
            "   - Use 'read_file' only for specific files you need to analyze",
            "",
            "6. **Memory Management**:",
            "   - Restart LangFlow if memory usage becomes high",
            "   - Monitor system resources during file operations",
            "",
            "7. **Error Handling**:",
            "   - If LangFlow crashes, check the logs for memory-related errors",
            "   - Use smaller directories for initial testing"
        ]
        return recommendations
    
    def generate_workaround_instructions(self) -> List[str]:
        """Generate workaround instructions for the automatic file reading issue"""
        instructions = [
            "🛠️ Workaround Instructions:",
            "",
            "**Immediate Fix**:",
            "1. Use 'list_files_metadata_only' tool instead of 'list_files'",
            "2. Set batch_size=5 to minimize memory usage",
            "3. Use offset parameter for pagination",
            "",
            "**Example Usage**:",
            "```",
            "list_files_metadata_only:",
            "  directory: '.'",
            "  batch_size: 5",
            "  offset: 0",
            "  max_depth: 1",
            "```",
            "",
            "**For Reading Specific Files**:",
            "```",
            "read_file:",
            "  file_path: 'specific_file.py'",
            "```",
            "",
            "**Memory-Safe Directory Exploration**:",
            "1. Start with small directories",
            "2. Use file type filters to reduce results",
            "3. Process directories in chunks using offset",
            "4. Monitor memory usage and restart if needed"
        ]
        return instructions
    
    async def run_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic for LangFlow automatic file reading issues"""
        print("🔍 Running LangFlow Automatic File Reading Diagnostic...")
        
        # Test list_files tool
        print("\n1. Testing list_files tool...")
        list_files_result = await self.test_list_files_tool()
        self.test_results.append(("list_files", list_files_result))
        
        # Test metadata_only tool
        print("2. Testing list_files_metadata_only tool...")
        metadata_result = await self.test_metadata_only_tool()
        self.test_results.append(("list_files_metadata_only", metadata_result))
        
        # Generate recommendations
        recommendations = self.generate_langflow_config_recommendations()
        workarounds = self.generate_workaround_instructions()
        
        return {
            "test_results": self.test_results,
            "recommendations": recommendations,
            "workarounds": workarounds,
            "summary": {
                "list_files_has_content": list_files_result.get("has_file_content", False),
                "metadata_only_working": metadata_result.get("success", False),
                "recommendation": "Use list_files_metadata_only tool to prevent automatic file reading"
            }
        }
    
    def print_report(self, diagnostic_result: Dict[str, Any]):
        """Print the diagnostic report"""
        print("\n" + "="*60)
        print("🔍 LANGFLOW AUTOMATIC FILE READING DIAGNOSTIC REPORT")
        print("="*60)
        
        # Test Results
        print("\n📊 TEST RESULTS:")
        for tool_name, result in diagnostic_result["test_results"]:
            print(f"\n{tool_name}:")
            if result["success"]:
                print(f"  ✅ Success: {result.get('result_length', 0)} characters")
                if "has_file_content" in result:
                    print(f"  📄 Contains file content: {result['has_file_content']}")
                if "has_metadata_indicators" in result:
                    print(f"  🔒 Has metadata indicators: {result['has_metadata_indicators']}")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Summary
        summary = diagnostic_result["summary"]
        print(f"\n📋 SUMMARY:")
        print(f"  • list_files contains content: {summary['list_files_has_content']}")
        print(f"  • metadata_only tool working: {summary['metadata_only_working']}")
        print(f"  • Recommendation: {summary['recommendation']}")
        
        # Recommendations
        print(f"\n" + "\n".join(diagnostic_result["recommendations"]))
        
        # Workarounds
        print(f"\n" + "\n".join(diagnostic_result["workarounds"]))
        
        print("\n" + "="*60)
        print("✅ Diagnostic complete!")
        print("="*60)

async def main():
    """Main function to run the diagnostic"""
    troubleshooter = LangFlowTroubleshooter()
    diagnostic_result = await troubleshooter.run_diagnostic()
    troubleshooter.print_report(diagnostic_result)

if __name__ == "__main__":
    asyncio.run(main()) 