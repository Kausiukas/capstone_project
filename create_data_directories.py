#!/usr/bin/env python3
"""
Data Directory Setup Script

This script creates all necessary data directories and default JSON files
to prevent FileNotFoundError during MCP server startup.
"""

import os
import json
import asyncio
import aiofiles
from pathlib import Path

# Define all required data directories and their default files
DATA_STRUCTURE = {
    "data/budgets": {
        "budgets.json": [],
        "usage.json": [],
        "alerts.json": []
    },
    "data/optimization": {
        "recommendations.json": [],
        "actions.json": []
    },
    "data/analysis": {
        "reports.json": []
    },
    "data/alerts": {
        "rules.json": [],
        "alerts.json": [],
        "notifications.json": {}
    },
    "data/visualizations": {
        "charts.json": [],
        "dashboards.json": [],
        "visualizations.json": []
    },
    "data/flows": {
        "flows.json": [],
        "executions.json": []
    },
    "logs": {
        # Log files will be created automatically by logging handlers
    }
}

async def create_data_structure():
    """Create all data directories and default JSON files"""
    print("Creating data directories and default files...")
    
    for directory, files in DATA_STRUCTURE.items():
        # Create directory
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
        
        # Create default JSON files
        for filename, default_data in files.items():
            filepath = os.path.join(directory, filename)
            if not os.path.exists(filepath):
                try:
                    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(default_data, indent=2, default=str))
                    print(f"  ✓ Created file: {filename}")
                except Exception as e:
                    print(f"  ✗ Failed to create {filename}: {e}")
            else:
                print(f"  - File already exists: {filename}")

async def verify_data_structure():
    """Verify that all required directories and files exist"""
    print("\nVerifying data structure...")
    
    all_good = True
    for directory, files in DATA_STRUCTURE.items():
        if not os.path.exists(directory):
            print(f"✗ Directory missing: {directory}")
            all_good = False
            continue
            
        for filename in files.keys():
            filepath = os.path.join(directory, filename)
            if not os.path.exists(filepath):
                print(f"✗ File missing: {filepath}")
                all_good = False
            else:
                print(f"✓ File exists: {filepath}")
    
    if all_good:
        print("\n✅ All data directories and files are properly set up!")
    else:
        print("\n❌ Some files or directories are missing. Please run the script again.")
    
    return all_good

async def main():
    """Main function"""
    print("Data Directory Setup Script")
    print("=" * 50)
    
    # Create data structure
    await create_data_structure()
    
    # Verify the structure
    success = await verify_data_structure()
    
    if success:
        print("\n🎉 Data setup completed successfully!")
        print("The MCP server should now start without FileNotFoundError issues.")
    else:
        print("\n⚠️  Data setup completed with warnings.")
        print("Some files may need to be created manually.")

if __name__ == "__main__":
    asyncio.run(main()) 