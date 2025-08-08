#!/usr/bin/env python3
"""
Quick Setup Script for Local Resource Integration
Helps configure and start the local resource integration system.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_postgresql_connection():
    """Check if PostgreSQL is accessible"""
    try:
        import psycopg2
        print("✅ psycopg2 is available")
        return True
    except ImportError:
        print("❌ psycopg2 not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        return True

def create_database_config():
    """Create database configuration file"""
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'langflow_agent',
        'user': 'postgres',
        'password': input("Enter your PostgreSQL password: ").strip()
    }
    
    # Save config to file
    with open('database_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Database configuration saved to database_config.json")
    return config

def create_database_if_not_exists(config):
    """Create database if it doesn't exist"""
    try:
        import psycopg2
        
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database='postgres',
            user=config['user'],
            password=config['password']
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {config['database']}")
            print(f"✅ Created database: {config['database']}")
        else:
            print(f"✅ Database {config['database']} already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False
    
    return True

def install_requirements():
    """Install required packages"""
    requirements = [
        'psycopg2-binary',
        'numpy',
        'pathlib'
    ]
    
    print("📦 Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def create_directories():
    """Create necessary directories"""
    directories = [
        'src/layers',
        'src/layers/local_resources',
        'logs',
        'data',
        'config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Local Resource Integration...")
    print("=" * 50)
    
    # 1. Install requirements
    install_requirements()
    
    # 2. Check PostgreSQL connection
    if not check_postgresql_connection():
        print("❌ PostgreSQL connection failed")
        return
    
    # 3. Create directories
    create_directories()
    
    # 4. Create database configuration
    config = create_database_config()
    
    # 5. Create database
    if not create_database_if_not_exists(config):
        print("❌ Database setup failed")
        return
    
    # 6. Test the integration
    print("\n🧪 Testing local resource integration...")
    try:
        from local_resource_integration import LocalResourceIntegration
        
        lri = LocalResourceIntegration(config)
        discovered = lri.discover_local_resources()
        
        print("\n✅ Setup completed successfully!")
        print(f"📊 Discovered {sum(len(v) for v in discovered.values())} resources")
        
        # Show what was discovered
        for resource_type, resources in discovered.items():
            if resources:
                print(f"  {resource_type}: {len(resources)} items")
        
        print("\n🎯 Next steps:")
        print("1. Run: python local_resource_integration.py")
        print("2. Check the database for stored knowledge")
        print("3. Review generated learning goals")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Please check your database configuration and try again.")

if __name__ == "__main__":
    main()
