#!/usr/bin/env python3
"""
LangFlow Connect MVP - Security Enhancement Module
Security features that can be added to the existing API server.
"""

import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limit_requests: int = 100  # requests per hour
    rate_limit_window: int = 3600   # 1 hour in seconds
    max_failed_attempts: int = 5    # max failed auth attempts
    block_duration: int = 1800      # 30 minutes block duration
    api_keys: Dict[str, Dict[str, Any]] = None

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # ip -> list of timestamps
    
    def is_allowed(self, ip_address: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        if ip_address in self.requests:
            self.requests[ip_address] = [
                ts for ts in self.requests[ip_address]
                if now - ts < self.window_seconds
            ]
        else:
            self.requests[ip_address] = []
        
        # Check if under limit
        if len(self.requests[ip_address]) < self.max_requests:
            self.requests[ip_address].append(now)
            return True
        
        return False

class SecurityManager:
    """Security manager for API protection"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rate_limiters = {
            'health': RateLimiter(1000, 3600),      # 1000 requests per hour
            'tools_list': RateLimiter(500, 3600),   # 500 requests per hour
            'tool_execution': RateLimiter(200, 3600) # 200 requests per hour
        }
        self.failed_attempts = {}  # ip -> (count, first_attempt_time)
        self.blocked_ips = set()
        self.api_key_usage = {}
        self.logger = logging.getLogger('SecurityManager')
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        if not self.config.api_keys:
            # Default validation
            return api_key in ['demo_key_123', 'admin_key_456']
        
        return api_key in self.config.api_keys
    
    def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Check rate limit for endpoint"""
        if endpoint in self.rate_limiters:
            return self.rate_limiters[endpoint].is_allowed(ip_address)
        return True
    
    def record_failed_attempt(self, ip_address: str):
        """Record failed authentication attempt"""
        now = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {'count': 0, 'first_attempt': now}
        
        self.failed_attempts[ip_address]['count'] += 1
        
        # Check if should be blocked
        if self.failed_attempts[ip_address]['count'] >= self.config.max_failed_attempts:
            time_since_first = now - self.failed_attempts[ip_address]['first_attempt']
            if time_since_first < self.config.block_duration:
                self.blocked_ips.add(ip_address)
                self.logger.warning(f"IP {ip_address} blocked due to multiple failed attempts")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            if ip_address in self.failed_attempts:
                del self.failed_attempts[ip_address]
    
    def track_api_key_usage(self, api_key: str, ip_address: str):
        """Track API key usage"""
        if api_key not in self.api_key_usage:
            self.api_key_usage[api_key] = {
                'requests': 0,
                'last_used': None,
                'ips': set()
            }
        
        self.api_key_usage[api_key]['requests'] += 1
        self.api_key_usage[api_key]['last_used'] = datetime.now().isoformat()
        self.api_key_usage[api_key]['ips'].add(ip_address)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'failed_attempts': len(self.failed_attempts),
            'active_api_keys': len(self.api_key_usage),
            'rate_limiters': {
                endpoint: {
                    'active_ips': len(limiter.requests),
                    'total_requests': sum(len(requests) for requests in limiter.requests.values())
                }
                for endpoint, limiter in self.rate_limiters.items()
            }
        }

class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path for security"""
        if not file_path:
            return False
        
        # Prevent directory traversal
        if '..' in file_path:
            return False
        
        # Prevent absolute paths
        if file_path.startswith('/') or file_path.startswith('\\'):
            return False
        
        # Prevent Windows drive letters
        if len(file_path) > 1 and file_path[1] == ':':
            return False
        
        return True
    
    @staticmethod
    def validate_tool_name(tool_name: str) -> bool:
        """Validate tool name"""
        if not tool_name:
            return False
        
        # Prevent reserved names
        reserved_names = ['admin', 'system', 'root', 'config', 'internal']
        if tool_name.lower() in reserved_names:
            return False
        
        # Only allow alphanumeric and underscores
        return tool_name.replace('_', '').isalnum()
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        
        return input_str

class SecurityLogger:
    """Security event logging"""
    
    def __init__(self, log_file: str = 'logs/security.log'):
        self.logger = logging.getLogger('SecurityLogger')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        import os
        os.makedirs('logs', exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        self.logger.info(f"SECURITY_EVENT: {event_type} - {details}")
    
    def log_failed_auth(self, ip_address: str, api_key: str, reason: str):
        """Log failed authentication"""
        self.log_security_event('FAILED_AUTH', {
            'ip_address': ip_address,
            'api_key': api_key[:8] + '...' if api_key else 'none',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit exceeded"""
        self.log_security_event('RATE_LIMIT_EXCEEDED', {
            'ip_address': ip_address,
            'endpoint': endpoint,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_suspicious_activity(self, ip_address: str, activity: str):
        """Log suspicious activity"""
        self.log_security_event('SUSPICIOUS_ACTIVITY', {
            'ip_address': ip_address,
            'activity': activity,
            'timestamp': datetime.now().isoformat()
        })

# Example usage and integration
def create_security_config() -> SecurityConfig:
    """Create default security configuration"""
    return SecurityConfig(
        api_keys={
            'demo_key_123': {
                'name': 'Demo User',
                'permissions': ['read', 'execute'],
                'rate_limit_multiplier': 1.0
            },
            'admin_key_456': {
                'name': 'Admin User',
                'permissions': ['read', 'execute', 'admin'],
                'rate_limit_multiplier': 2.0
            }
        }
    )

def apply_security_headers(response_headers: Dict[str, str]) -> Dict[str, str]:
    """Apply security headers to response"""
    security_headers = SecurityHeaders.get_security_headers()
    response_headers.update(security_headers)
    return response_headers

def validate_request_security(
    ip_address: str,
    api_key: str,
    endpoint: str,
    security_manager: SecurityManager,
    security_logger: SecurityLogger
) -> tuple[bool, str]:
    """Validate request security"""
    
    # Check if IP is blocked
    if security_manager.is_ip_blocked(ip_address):
        security_logger.log_suspicious_activity(ip_address, "Blocked IP attempt")
        return False, "IP address is blocked"
    
    # Validate API key
    if not security_manager.validate_api_key(api_key):
        security_manager.record_failed_attempt(ip_address)
        security_logger.log_failed_auth(ip_address, api_key, "Invalid API key")
        return False, "Invalid API key"
    
    # Check rate limit
    if not security_manager.check_rate_limit(ip_address, endpoint):
        security_logger.log_rate_limit_exceeded(ip_address, endpoint)
        return False, "Rate limit exceeded"
    
    # Track usage
    security_manager.track_api_key_usage(api_key, ip_address)
    
    return True, "OK"

# Example integration with FastAPI
def create_security_middleware(security_manager: SecurityManager, security_logger: SecurityLogger):
    """Create security middleware for FastAPI"""
    
    async def security_middleware(request, call_next):
        # Extract IP address
        ip_address = request.client.host
        
        # Extract API key
        api_key = request.headers.get('X-API-Key', '')
        
        # Validate security
        is_valid, message = validate_request_security(
            ip_address, api_key, request.url.path, security_manager, security_logger
        )
        
        if not is_valid:
            return {
                "error": message,
                "status_code": 429 if "Rate limit" in message else 401
            }
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers.update(SecurityHeaders.get_security_headers())
        
        return response
    
    return security_middleware
