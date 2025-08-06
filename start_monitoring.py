#!/usr/bin/env python3
"""
LangFlow Connect MVP - Monitoring Startup Script
Simple script to start the monitoring system with default settings.
"""

import sys
import os
from monitoring.monitoring_system import MonitoringSystem

def main():
    """Start monitoring system with default configuration"""
    print("🔍 Starting LangFlow Connect MVP Monitoring System")
    print("=" * 60)
    
    # Create monitoring system
    monitor = MonitoringSystem()
    
    print("📊 Configuration:")
    print(f"  API URL: {monitor.api_url}")
    print(f"  Check Interval: 5 minutes")
    print(f"  Alert Threshold: 3 consecutive failures")
    print(f"  Log File: {monitor.logger.handlers[0].baseFilename}")
    
    print("\n🚀 Starting monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        # Run initial check
        result = monitor.run_health_check_cycle()
        print(f"✅ Initial health check: {result['successful_checks']}/{result['total_checks']} successful")
        
        # Start continuous monitoring
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        
        # Save final data
        filename = monitor.save_monitoring_data()
        print(f"📄 Final monitoring data saved to: {filename}")
        
        # Display final status
        status = monitor.get_system_status()
        print(f"\n📊 Final System Status: {status['status']}")
        print(f"Success Rate: {status['success_rate']:.1f}%")
        print(f"Average Response Time: {status['average_response_time']:.2f}ms")
        print(f"Uptime: {status['uptime_percentage']:.1f}%")
        
    except Exception as e:
        print(f"❌ Monitoring error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
