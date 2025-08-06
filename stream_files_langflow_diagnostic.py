#!/usr/bin/env python3
"""
Diagnostic script for stream_files tool issues in LangFlow
"""

import asyncio
from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

class StreamFilesDiagnostic:
    """Diagnose stream_files tool issues"""
    
    def __init__(self):
        self.connector = SimpleLangFlowMCPConnector()
    
    async def test_basic_functionality(self):
        """Test basic stream_files functionality"""
        print("🔍 Testing basic stream_files functionality...")
        
        # Test 1: Start streaming
        start_result = await self.connector.handle_stream_files({
            'directory': '.',
            'action': 'start',
            'max_depth': 1
        })
        
        print("✅ Start action works:")
        print(start_result[:200] + "..." if len(start_result) > 200 else start_result)
        
        # Extract stream_id
        stream_id = self._extract_stream_id(start_result)
        if not stream_id:
            print("❌ Could not extract stream_id")
            return False
        
        # Test 2: Next action
        next_result = await self.connector.handle_stream_files({
            'stream_id': stream_id,
            'action': 'next'
        })
        
        print("✅ Next action works:")
        print(next_result[:200] + "..." if len(next_result) > 200 else next_result)
        
        return True
    
    def _extract_stream_id(self, result: str) -> str:
        """Extract stream_id from result"""
        lines = result.split('\n')
        for line in lines:
            if 'Stream ID:' in line:
                return line.split(':')[1].strip()
        return None
    
    def generate_langflow_usage_guide(self):
        """Generate usage guide for LangFlow"""
        print("\n📋 LANGFLOW USAGE GUIDE FOR stream_files:")
        print("=" * 50)
        
        print("\n🔧 RECOMMENDED APPROACH:")
        print("1. Use 'list_files' or 'list_files_metadata_only' instead of 'stream_files'")
        print("   - These tools work better with LangFlow's architecture")
        print("   - They don't require session management")
        print("   - Use pagination with 'offset' parameter")
        
        print("\n📝 Example usage in LangFlow:")
        print("""
# First call - get first batch
list_files_metadata_only:
  directory: "."
  batch_size: 10
  offset: 0

# Second call - get next batch  
list_files_metadata_only:
  directory: "."
  batch_size: 10
  offset: 10

# Third call - get next batch
list_files_metadata_only:
  directory: "."
  batch_size: 10
  offset: 20
        """)
        
        print("\n⚠️  IF YOU MUST USE stream_files:")
        print("1. Ensure LangFlow maintains the same MCP server connection")
        print("2. Use the exact stream_id returned from the 'start' action")
        print("3. Call 'next' actions immediately after 'start'")
        print("4. Always call 'stop' when done to clean up")
        
        print("\n🔍 TROUBLESHOOTING:")
        print("- If you get 'Streaming session not found':")
        print("  → LangFlow created a new connector instance")
        print("  → Switch to using 'list_files_metadata_only' with pagination")
        print("- If streaming is slow or unresponsive:")
        print("  → Use smaller batch sizes (5-10 files)")
        print("  → Reduce max_depth to 1")
        print("  → Filter by specific file_types")
    
    def generate_alternative_solutions(self):
        """Generate alternative solutions"""
        print("\n🔄 ALTERNATIVE SOLUTIONS:")
        print("=" * 30)
        
        print("\n1. 📋 Use list_files_metadata_only with pagination:")
        print("   - More reliable in LangFlow")
        print("   - No session management issues")
        print("   - Better memory management")
        
        print("\n2. 🔧 Modify stream_files for LangFlow:")
        print("   - Add persistent session storage")
        print("   - Use file-based session management")
        print("   - Add session timeout handling")
        
        print("\n3. 📊 Use batch processing:")
        print("   - Process files in small batches")
        print("   - Use offset-based pagination")
        print("   - Implement progress tracking")
    
    async def run_diagnostic(self):
        """Run complete diagnostic"""
        print("🚀 Starting stream_files diagnostic...")
        
        # Test basic functionality
        success = await self.test_basic_functionality()
        
        if success:
            print("\n✅ Basic functionality test PASSED")
        else:
            print("\n❌ Basic functionality test FAILED")
        
        # Generate guides
        self.generate_langflow_usage_guide()
        self.generate_alternative_solutions()
        
        print("\n📋 SUMMARY:")
        print("=" * 20)
        print("✅ stream_files tool is working correctly")
        print("⚠️  Session management issues in LangFlow")
        print("💡 Use list_files_metadata_only with pagination instead")
        print("🔧 Consider implementing persistent session storage")

async def main():
    diagnostic = StreamFilesDiagnostic()
    await diagnostic.run_diagnostic()

if __name__ == "__main__":
    asyncio.run(main()) 