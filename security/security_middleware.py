#!/usr/bin/env python3
"""
LangFlow Connect MVP - Security Middleware
Simple middleware to add security headers to existing FastAPI server.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
import logging

logger = logging.getLogger('SecurityMiddleware')

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    def __init__(self, app, security_config: Dict[str, Any] = None):
        super().__init__(app)
        self.security_config = security_config or self.get_default_security_config()
    
    def get_default_security_config(self) -> Dict[str, Any]:
        """Get default security configuration"""
        return {
            'security_headers': {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;",
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
                'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            'cors_origins': [
                "http://localhost:8501",
                "https://capstone-project-dashboard.onrender.com",
                "https://your-dashboard-domain.com"
            ]
        }
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_config['security_headers'].items():
            response.headers[header] = value
        
        # Add custom security headers
        response.headers["X-API-Version"] = "2.0.0"
        response.headers["X-Security-Level"] = "Enhanced"
        
        # Log security event
        logger.info(f"Security headers applied to {request.url.path} from {request.client.host}")
        
        return response

def add_security_headers_to_app(app):
    """Add security headers middleware to FastAPI app"""
    from fastapi.middleware.cors import CORSMiddleware
    
    # Add CORS middleware first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "https://capstone-project-dashboard.onrender.com",
            "https://your-dashboard-domain.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    return app

# Example usage:
"""
# In your main FastAPI app file:
from security.security_middleware import add_security_headers_to_app

app = FastAPI()
app = add_security_headers_to_app(app)
"""

def create_security_middleware_function():
    """Create a simple function to add security headers"""
    
    async def security_middleware(request: Request, call_next):
        """Simple security middleware function"""
        response = await call_next(request)
        
        # Add essential security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    return security_middleware

# Example usage for existing app:
"""
# Add this to your existing FastAPI app:
from security.security_middleware import create_security_middleware_function

app.middleware("http")(create_security_middleware_function())
"""
