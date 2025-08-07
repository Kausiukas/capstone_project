#!/usr/bin/env python3
"""
Quick script to check current performance alerts
"""

import requests
import json

API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

def check_alerts():
    """Check current performance alerts"""
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/performance/alerts", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("🚨 Current Performance Alerts:")
            print("=" * 50)
            
            alerts = data.get('alerts', [])
            if not alerts:
                print("✅ No active alerts - System performing well!")
            else:
                for alert in alerts:
                    print(f"🔴 Type: {alert.get('type', 'Unknown')}")
                    print(f"   Tool: {alert.get('tool', 'Unknown')}")
                    print(f"   Message: {alert.get('message', 'No message')}")
                    print(f"   Severity: {alert.get('severity', 'Unknown')}")
                    print(f"   Time: {alert.get('timestamp', 'Unknown')}")
                    print("-" * 30)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_alerts()
