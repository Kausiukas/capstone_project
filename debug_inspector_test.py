#!/usr/bin/env python3
"""
Debug Inspector Test

Simple script to debug Inspector CLI issues from Python.
"""

import subprocess
import json
import os

def test_inspector_cli():
    """Test Inspector CLI directly"""
    print("Testing Inspector CLI...")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if file exists
    file_path = "mcp_langflow_connector_simple.py"
    print(f"File exists: {os.path.exists(file_path)}")
    
    # Test Inspector CLI
    command = [
        "npx", "@modelcontextprotocol/inspector",
        "python", "mcp_langflow_connector_simple.py",
        "--cli",
        "--method", "tools/list"
    ]
    
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.strip())
                print(f"Success! Found {len(response.get('tools', []))} tools")
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return False
        else:
            print("Command failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_inspector_cli()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}") 