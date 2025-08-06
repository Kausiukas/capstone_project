#!/usr/bin/env python3
"""
Cloud Deployment Script for LangFlow Connect MVP
Automates deployment to Railway, Render, and Heroku
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check if git is available
    if not run_command("git --version", "Checking Git"):
        print("❌ Git is not installed or not in PATH")
        return False
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not in a git repository")
        return False
    
    print("✅ Prerequisites check passed")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    railway_check = run_command("railway --version", "Checking Railway CLI")
    if not railway_check:
        print("📦 Installing Railway CLI...")
        install_result = run_command("npm install -g @railway/cli", "Installing Railway CLI")
        if not install_result:
            print("❌ Failed to install Railway CLI")
            return False
    
    # Login to Railway
    print("🔐 Please login to Railway in the browser that opens...")
    login_result = run_command("railway login", "Logging into Railway")
    if not login_result:
        print("❌ Railway login failed")
        return False
    
    # Initialize Railway project
    init_result = run_command("railway init", "Initializing Railway project")
    if not init_result:
        print("❌ Railway project initialization failed")
        return False
    
    # Deploy to Railway
    deploy_result = run_command("railway up", "Deploying to Railway")
    if not deploy_result:
        print("❌ Railway deployment failed")
        return False
    
    # Get the deployment URL
    url_result = run_command("railway domain", "Getting Railway URL")
    if url_result:
        print(f"🌐 Railway deployment URL: {url_result.strip()}")
    
    return True

def deploy_to_render():
    """Deploy to Render"""
    print("\n🎨 Deploying to Render...")
    
    print("📋 Render deployment instructions:")
    print("1. Go to https://render.com")
    print("2. Sign up/Login with your GitHub account")
    print("3. Click 'New +' and select 'Web Service'")
    print("4. Connect your GitHub repository: https://github.com/Kausiukas/capstone_project")
    print("5. Configure the service:")
    print("   - Name: capstone-project")
    print("   - Environment: Python")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: uvicorn src.mcp_server_http:app --host 0.0.0.0 --port $PORT")
    print("6. Click 'Create Web Service'")
    
    return True

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("\n⚡ Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    heroku_check = run_command("heroku --version", "Checking Heroku CLI")
    if not heroku_check:
        print("📦 Installing Heroku CLI...")
        print("Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Login to Heroku
    login_result = run_command("heroku login", "Logging into Heroku")
    if not login_result:
        print("❌ Heroku login failed")
        return False
    
    # Create Heroku app
    app_name = "capstone-project-mvp"
    create_result = run_command(f"heroku create {app_name}", "Creating Heroku app")
    if not create_result:
        print("❌ Heroku app creation failed")
        return False
    
    # Add buildpack
    buildpack_result = run_command("heroku buildpacks:set heroku/python", "Setting Python buildpack")
    if not buildpack_result:
        print("❌ Buildpack setting failed")
        return False
    
    # Deploy to Heroku
    deploy_result = run_command("git push heroku master", "Deploying to Heroku")
    if not deploy_result:
        print("❌ Heroku deployment failed")
        return False
    
    # Open the app
    open_result = run_command("heroku open", "Opening Heroku app")
    
    return True

def main():
    """Main deployment function"""
    print("🚀 LangFlow Connect MVP - Cloud Deployment")
    print("=" * 50)
    
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install required tools.")
        return
    
    print("\n📋 Available deployment options:")
    print("1. Railway (Recommended - Easy setup)")
    print("2. Render (Free tier available)")
    print("3. Heroku (Requires credit card)")
    print("4. All platforms")
    
    choice = input("\nSelect deployment option (1-4): ").strip()
    
    success_count = 0
    
    if choice in ["1", "4"]:
        if deploy_to_railway():
            success_count += 1
    
    if choice in ["2", "4"]:
        if deploy_to_render():
            success_count += 1
    
    if choice in ["3", "4"]:
        if deploy_to_heroku():
            success_count += 1
    
    print(f"\n🎉 Deployment completed! {success_count} platform(s) deployed successfully.")
    print("\n📚 Next steps:")
    print("1. Test the deployed applications")
    print("2. Update documentation with live URLs")
    print("3. Share the demo with stakeholders")

if __name__ == "__main__":
    main() 