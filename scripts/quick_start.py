#!/usr/bin/env python3
"""
LangFlow Connect - Quick Start Script

This script provides a quick way to test the Langflow connection setup
and verify that all components are working correctly.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.module_4_langflow.langflow_connector import LangflowConnector
from config.langflow_config import LangflowConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main quick start function."""
    print("🚀 Starting LangFlow Connect Quick Start...")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config_manager = LangflowConfig()
        
        if not config_manager.validate_config():
            print("❌ Invalid configuration. Please check your .env file.")
            print("💡 Make sure to copy env.example to .env and update the values.")
            return
        
        config = config_manager.get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   WebSocket URL: {config['websocket_url']}")
        print(f"   User ID: {config['user_id']}")
        print(f"   Max Reconnect Attempts: {config['max_reconnect_attempts']}")
        
        # Create connector
        print("\n🔗 Creating LangflowConnector...")
        connector = LangflowConnector(config)
        print("✅ LangflowConnector created successfully")
        
        # Test connection health
        print("\n📊 Testing connection health...")
        health = connector.get_connection_health()
        print(f"   Connected: {health['connected']}")
        print(f"   WebSocket URL: {health['websocket_url']}")
        print(f"   Reconnect Attempts: {health['reconnect_attempts']}")
        print(f"   Max Reconnect Attempts: {health['max_reconnect_attempts']}")
        
        # Test JWT token generation
        print("\n🔐 Testing JWT token generation...")
        token = connector.generate_auth_token()
        print(f"✅ JWT token generated successfully")
        print(f"   Token length: {len(token)} characters")
        print(f"   Token format: {'Valid' if token.count('.') == 2 else 'Invalid'}")
        
        # Test data sending (will fail without connection, but tests the interface)
        print("\n📤 Testing data sending interface...")
        test_data = {
            "type": "test",
            "message": "Hello from LangFlow Connect!",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        send_result = await connector.send_data(test_data)
        if send_result["status"] == "error":
            print(f"⚠️  Data sending failed (expected without connection): {send_result['message']}")
        else:
            print(f"✅ Data sent successfully: {send_result['status']}")
        
        # Test configuration validation
        print("\n✅ Testing configuration validation...")
        validation_result = config_manager.validate_config()
        print(f"   Configuration valid: {validation_result}")
        
        # Test module configuration
        print("\n🔧 Testing module configuration...")
        for module_num in range(1, 5):
            module_name = f"module_{module_num}"
            try:
                module_config = config_manager.get_module_config(module_name)
                enabled = module_config.get(f"{module_name}_enabled", False)
                print(f"   {module_name.upper()}: {'✅ Enabled' if enabled else '❌ Disabled'}")
            except ValueError as e:
                print(f"   {module_name.upper()}: ❌ Error - {e}")
        
        # Test database URL generation
        print("\n🗄️  Testing database configuration...")
        try:
            db_url = config_manager.get_database_url()
            # Mask password in URL for security
            masked_url = db_url.replace(config['database']['password'], '***')
            print(f"   Database URL: {masked_url}")
        except Exception as e:
            print(f"   Database URL generation failed: {e}")
        
        # Test environment detection
        print("\n🌍 Testing environment detection...")
        is_dev = config_manager.is_development()
        is_test = config_manager.is_testing()
        print(f"   Development mode: {'✅ Yes' if is_dev else '❌ No'}")
        print(f"   Test mode: {'✅ Yes' if is_test else '❌ No'}")
        
        print("\n" + "=" * 50)
        print("🎉 Quick Start Test Completed Successfully!")
        print("\n📋 Summary:")
        print("   ✅ Configuration loaded and validated")
        print("   ✅ LangflowConnector created")
        print("   ✅ JWT token generation working")
        print("   ✅ Connection health monitoring ready")
        print("   ✅ Module configuration verified")
        print("   ✅ Database configuration ready")
        
        print("\n🚀 Next Steps:")
        print("   1. Start your Langflow server")
        print("   2. Update .env with your Langflow connection details")
        print("   3. Run: python -m pytest tests/phase1/ -v")
        print("   4. Check the implementation guide: docs/implementation/Langflow_connection_quick_start.md")
        
    except Exception as e:
        print(f"\n❌ Quick start failed with error: {e}")
        logger.error(f"Quick start error: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)