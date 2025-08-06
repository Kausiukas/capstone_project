#!/usr/bin/env python3
"""
LangFlow Connect MVP - Monitoring System
Comprehensive monitoring and alerting system for maintaining excellent performance.
"""

import requests
import json
import time
import smtplib
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"
CHECK_INTERVAL = 300  # 5 minutes
ALERT_THRESHOLD = 3   # 3 consecutive failures
LOG_FILE = "logs/monitoring.log"

@dataclass
class HealthCheck:
    timestamp: str
    endpoint: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class Alert:
    timestamp: str
    type: str
    message: str
    severity: str
    resolved: bool = False

class MonitoringSystem:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        self.health_checks = []
        self.alerts = []
        self.failure_count = 0
        self.last_success = datetime.now()
        
        # Setup logging
        self.setup_logging()
        
        # Email configuration (optional)
        self.email_config = {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': os.getenv('MONITORING_EMAIL'),
            'password': os.getenv('MONITORING_PASSWORD'),
            'recipients': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MonitoringSystem')
    
    def check_health(self) -> HealthCheck:
        """Check API health endpoint"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            success = response.status_code == 200
            error_message = None if success else f"Status code: {response.status_code}"
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint="/health",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error_message=error_message
            )
            
            self.health_checks.append(health_check)
            
            if success:
                self.failure_count = 0
                self.last_success = datetime.now()
                self.logger.info(f"Health check passed: {response_time:.2f}ms")
            else:
                self.failure_count += 1
                self.logger.warning(f"Health check failed: {error_message}")
            
            return health_check
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            self.failure_count += 1
            self.logger.error(f"Health check exception: {str(e)}")
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint="/health",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            
            self.health_checks.append(health_check)
            return health_check
    
    def check_tools_endpoint(self) -> HealthCheck:
        """Check tools/list endpoint"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/tools/list", headers=self.headers, timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            success = response.status_code == 200
            error_message = None if success else f"Status code: {response.status_code}"
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint="/tools/list",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error_message=error_message
            )
            
            self.health_checks.append(health_check)
            
            if success:
                self.logger.info(f"Tools endpoint check passed: {response_time:.2f}ms")
            else:
                self.logger.warning(f"Tools endpoint check failed: {error_message}")
            
            return health_check
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            self.logger.error(f"Tools endpoint check exception: {str(e)}")
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint="/tools/list",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            
            self.health_checks.append(health_check)
            return health_check
    
    def test_tool_execution(self, tool_name: str = "ping") -> HealthCheck:
        """Test tool execution"""
        start_time = time.time()
        
        try:
            payload = {
                'name': tool_name,
                'arguments': {}
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            success = response.status_code == 200
            error_message = None if success else f"Status code: {response.status_code}"
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint=f"/api/v1/tools/call ({tool_name})",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error_message=error_message
            )
            
            self.health_checks.append(health_check)
            
            if success:
                self.logger.info(f"Tool execution test passed ({tool_name}): {response_time:.2f}ms")
            else:
                self.logger.warning(f"Tool execution test failed ({tool_name}): {error_message}")
            
            return health_check
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            self.logger.error(f"Tool execution test exception ({tool_name}): {str(e)}")
            
            health_check = HealthCheck(
                timestamp=datetime.now().isoformat(),
                endpoint=f"/api/v1/tools/call ({tool_name})",
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            
            self.health_checks.append(health_check)
            return health_check
    
    def check_alert_conditions(self):
        """Check if alerts should be triggered"""
        if self.failure_count >= ALERT_THRESHOLD:
            # Check if we already have an active alert
            active_alerts = [a for a in self.alerts if not a.resolved and a.type == 'service_down']
            
            if not active_alerts:
                alert = Alert(
                    timestamp=datetime.now().isoformat(),
                    type='service_down',
                    message=f'API service has been down for {self.failure_count} consecutive checks',
                    severity='critical'
                )
                self.alerts.append(alert)
                self.logger.critical(f"ALERT: {alert.message}")
                self.send_alert(alert)
        
        # Check for performance degradation
        recent_checks = [h for h in self.health_checks if h.success and 
                        datetime.fromisoformat(h.timestamp) > datetime.now() - timedelta(hours=1)]
        
        if recent_checks:
            avg_response_time = sum(h.response_time for h in recent_checks) / len(recent_checks)
            if avg_response_time > 1000:  # 1 second threshold
                alert = Alert(
                    timestamp=datetime.now().isoformat(),
                    type='performance_degradation',
                    message=f'Average response time is {avg_response_time:.2f}ms (threshold: 1000ms)',
                    severity='warning'
                )
                self.alerts.append(alert)
                self.logger.warning(f"ALERT: {alert.message}")
                self.send_alert(alert)
    
    def send_alert(self, alert: Alert):
        """Send alert via email"""
        if not self.email_config['enabled'] or not self.email_config['recipients']:
            self.logger.info(f"Email alerts not configured. Alert: {alert.message}")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(self.email_config['recipients'])
            msg['Subject'] = f"LangFlow Connect Alert: {alert.type}"
            
            body = f"""
            LangFlow Connect MVP - System Alert
            
            Type: {alert.type}
            Severity: {alert.severity}
            Message: {alert.message}
            Timestamp: {alert.timestamp}
            
            Please check the system immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alert email sent: {alert.type}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {str(e)}")
    
    def run_health_check_cycle(self):
        """Run a complete health check cycle"""
        self.logger.info("Starting health check cycle...")
        
        # Check health endpoint
        health_result = self.check_health()
        
        # Check tools endpoint
        tools_result = self.check_tools_endpoint()
        
        # Test tool execution
        tool_result = self.test_tool_execution("ping")
        
        # Check alert conditions
        self.check_alert_conditions()
        
        # Log summary
        successful_checks = sum(1 for check in [health_result, tools_result, tool_result] if check.success)
        total_checks = 3
        
        self.logger.info(f"Health check cycle completed: {successful_checks}/{total_checks} successful")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'successful_checks': successful_checks,
            'total_checks': total_checks,
            'failure_count': self.failure_count,
            'last_success': self.last_success.isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        recent_checks = [h for h in self.health_checks if 
                        datetime.fromisoformat(h.timestamp) > datetime.now() - timedelta(hours=1)]
        
        if recent_checks:
            successful_checks = [h for h in recent_checks if h.success]
            success_rate = len(successful_checks) / len(recent_checks) * 100
            avg_response_time = sum(h.response_time for h in successful_checks) / len(successful_checks) if successful_checks else 0
        else:
            success_rate = 0
            avg_response_time = 0
        
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        return {
            'status': 'healthy' if self.failure_count == 0 else 'degraded' if self.failure_count < ALERT_THRESHOLD else 'down',
            'success_rate': success_rate,
            'average_response_time': avg_response_time,
            'failure_count': self.failure_count,
            'last_success': self.last_success.isoformat(),
            'active_alerts': len(active_alerts),
            'total_health_checks': len(self.health_checks),
            'uptime_percentage': self.calculate_uptime()
        }
    
    def calculate_uptime(self) -> float:
        """Calculate uptime percentage"""
        if not self.health_checks:
            return 100.0
        
        total_checks = len(self.health_checks)
        successful_checks = sum(1 for check in self.health_checks if check.success)
        
        return (successful_checks / total_checks) * 100 if total_checks > 0 else 100.0
    
    def save_monitoring_data(self, filename: str = None):
        """Save monitoring data to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_data_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.get_system_status(),
            'health_checks': [asdict(check) for check in self.health_checks[-100:]],  # Last 100 checks
            'alerts': [asdict(alert) for alert in self.alerts[-50:]],  # Last 50 alerts
            'configuration': {
                'api_url': self.api_url,
                'check_interval': CHECK_INTERVAL,
                'alert_threshold': ALERT_THRESHOLD
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Monitoring data saved to: {filename}")
        return filename
    
    def start_monitoring(self, run_once: bool = False):
        """Start the monitoring system"""
        self.logger.info("Starting LangFlow Connect monitoring system...")
        
        if run_once:
            self.run_health_check_cycle()
            return
        
        # Schedule regular health checks
        schedule.every(CHECK_INTERVAL).seconds.do(self.run_health_check_cycle)
        
        # Run initial check
        self.run_health_check_cycle()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    """Main function to run the monitoring system"""
    print("🔍 LangFlow Connect MVP - Monitoring System")
    print("=" * 50)
    
    # Create monitoring system
    monitor = MonitoringSystem()
    
    # Configure email alerts (optional)
    email_enabled = input("Enable email alerts? (y/n): ").lower().startswith('y')
    if email_enabled:
        monitor.email_config['enabled'] = True
        monitor.email_config['username'] = input("Email username: ")
        monitor.email_config['password'] = input("Email password: ")
        recipients = input("Alert recipients (comma-separated): ").split(',')
        monitor.email_config['recipients'] = [r.strip() for r in recipients]
    
    # Run mode
    run_mode = input("Run mode (once/continuous): ").lower()
    
    if run_mode == 'once':
        print("Running single health check...")
        result = monitor.run_health_check_cycle()
        print(f"✅ Health check completed: {result['successful_checks']}/{result['total_checks']} successful")
        
        # Save data
        filename = monitor.save_monitoring_data()
        print(f"📄 Monitoring data saved to: {filename}")
        
        # Display status
        status = monitor.get_system_status()
        print(f"\n📊 System Status: {status['status']}")
        print(f"Success Rate: {status['success_rate']:.1f}%")
        print(f"Average Response Time: {status['average_response_time']:.2f}ms")
        print(f"Uptime: {status['uptime_percentage']:.1f}%")
        
    else:
        print("Starting continuous monitoring...")
        print(f"Health checks every {CHECK_INTERVAL} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            
            # Save final data
            filename = monitor.save_monitoring_data()
            print(f"📄 Final monitoring data saved to: {filename}")

if __name__ == "__main__":
    main()
