#!/usr/bin/env python3
"""
Simple Stability Monitor for LangFlow MCP Connector
Monitors system health and performance
"""

import asyncio
import psutil
import json
import time
from pathlib import Path

class SimpleStabilityMonitor:
    def __init__(self):
        self.monitoring_data = []
        self.alert_thresholds = {
            "memory_percent": 85,
            "cpu_percent": 80,
            "disk_percent": 90
        }
    
    async def monitor_system_health(self):
        """Monitor system health continuously"""
        print("📊 Starting system health monitoring...")
        
        while True:
            try:
                # Collect system metrics
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=1)
                disk = psutil.disk_usage('.')
                
                metrics = {
                    "timestamp": time.time(),
                    "memory_percent": memory.percent,
                    "cpu_percent": cpu,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "available_memory_gb": memory.available / (1024**3)
                }
                
                # Check for alerts
                alerts = []
                if metrics["memory_percent"] > self.alert_thresholds["memory_percent"]:
                    alerts.append(f"High memory usage: {metrics['memory_percent']:.1f}%")
                
                if metrics["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
                    alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
                
                if metrics["disk_percent"] > self.alert_thresholds["disk_percent"]:
                    alerts.append(f"High disk usage: {metrics['disk_percent']:.1f}%")
                
                metrics["alerts"] = alerts
                self.monitoring_data.append(metrics)
                
                # Save monitoring data
                self.save_monitoring_data()
                
                # Log status
                if alerts:
                    print(f"⚠️ Alerts: {', '.join(alerts)}")
                else:
                    print(f"✅ System healthy - Memory: {metrics['memory_percent']:.1f}%, CPU: {metrics['cpu_percent']:.1f}%")
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)
    
    def save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            Path("logs").mkdir(exist_ok=True)
            monitoring_file = "logs/stability_monitoring.json"
            with open(monitoring_file, 'w') as f:
                json.dump(self.monitoring_data[-100:], f, indent=2)  # Keep last 100 entries
        except Exception as e:
            print(f"❌ Failed to save monitoring data: {e}")

async def main():
    monitor = SimpleStabilityMonitor()
    await monitor.monitor_system_health()

if __name__ == "__main__":
    asyncio.run(main()) 