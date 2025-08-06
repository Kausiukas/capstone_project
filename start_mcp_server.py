#!/usr/bin/env python3
"""
Simple Startup Script for LangFlow MCP Connector
Ensures stable startup and basic error handling
"""

import sys
import os
import subprocess
import time
import signal
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    
    # Check required files
    required_files = [
        "mcp_langflow_connector_simple.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All prerequisites met")
    return True

def start_mcp_server():
    """Start the MCP server with error handling"""
    print("🚀 Starting MCP server...")
    
    try:
        # Start the MCP server
        process = subprocess.Popen([
            sys.executable, "mcp_langflow_connector_simple.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ MCP server started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        return None

def monitor_server(process):
    """Monitor server process and restart if needed"""
    print("📊 Monitoring MCP server...")
    
    max_restarts = 3
    restart_count = 0
    
    while restart_count < max_restarts:
        if process.poll() is not None:
            print(f"⚠️ MCP server stopped (exit code: {process.returncode})")
            restart_count += 1
            
            if restart_count < max_restarts:
                print(f"🔄 Restarting MCP server (attempt {restart_count}/{max_restarts})...")
                time.sleep(5)  # Wait before restart
                process = start_mcp_server()
                if process is None:
                    break
            else:
                print("❌ Maximum restart attempts reached")
                break
        else:
            time.sleep(10)  # Check every 10 seconds
    
    return process

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutdown signal received, stopping MCP server...")
    sys.exit(0)

def main():
    """Main startup function"""
    print("🚀 LangFlow MCP Connector Startup")
    print("="*40)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed")
        sys.exit(1)
    
    # Start MCP server
    process = start_mcp_server()
    if process is None:
        print("❌ Failed to start MCP server")
        sys.exit(1)
    
    # Monitor and restart if needed
    try:
        process = monitor_server(process)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait()
            print("✅ MCP server stopped")

if __name__ == "__main__":
    main() 