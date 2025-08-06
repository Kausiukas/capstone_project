"""
External Service Manager - Handles integration with external services and APIs
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Service configuration structure"""
    name: str
    base_url: str
    api_key: str
    timeout: int
    max_retries: int
    rate_limit: int

@dataclass
class ServiceResponse:
    """Service response structure"""
    success: bool
    data: Any
    status_code: int
    response_time: float
    error: str = None

class ExternalServiceManager:
    """
    Manages external service integrations and API calls
    """
    
    def __init__(self):
        self.services = {}
        self.session = None
        self.rate_limiters = {}
        self.service_stats = {}
        self.initialized = False

    async def initialize(self) -> bool:
        """
        Initialize the external service manager

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing external service manager...")

            # Clear existing services and stats
            self.services.clear()
            self.service_stats.clear()
            self.rate_limiters.clear()

            # Create aiohttp session
            if not self.session:
                self.session = aiohttp.ClientSession()

            self.initialized = True
            logger.info("External service manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize external service manager: {e}")
            return False
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def register_service(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """
        Register an external service
        
        Args:
            service_config: Service configuration
            
        Returns:
            Dictionary containing registration result
        """
        try:
            self.services[service_config.name] = service_config
            self.service_stats[service_config.name] = {
                "calls": 0,
                "errors": 0,
                "total_response_time": 0,
                "last_call": None
            }
            
            return {
                "success": True,
                "service_name": service_config.name,
                "message": f"Service '{service_config.name}' registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error registering service {service_config.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service_name": service_config.name
            }
    
    async def call_service(self, service_name: str, endpoint: str, 
                          method: str = "GET", data: Dict = None, 
                          headers: Dict = None) -> ServiceResponse:
        """
        Make a call to an external service
        
        Args:
            service_name: Name of the registered service
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            headers: Request headers
            
        Returns:
            ServiceResponse object
        """
        if service_name not in self.services:
            return ServiceResponse(
                success=False,
                data=None,
                status_code=0,
                response_time=0,
                error=f"Service '{service_name}' not registered"
            )
        
        service_config = self.services[service_name]
        stats = self.service_stats[service_name]
        
        # Check rate limiting
        if not await self._check_rate_limit(service_name):
            return ServiceResponse(
                success=False,
                data=None,
                status_code=429,
                response_time=0,
                error="Rate limit exceeded"
            )
        
        # Prepare request
        url = f"{service_config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "LangFlow-Connect/1.0"
        }
        
        if service_config.api_key:
            request_headers["Authorization"] = f"Bearer {service_config.api_key}"
        
        if headers:
            request_headers.update(headers)
        
        # Make request
        start_time = time.time()
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=service_config.timeout)
            ) as response:
                response_time = time.time() - start_time
                
                # Update stats
                stats["calls"] += 1
                stats["total_response_time"] += response_time
                stats["last_call"] = time.time()
                
                if response.status >= 400:
                    stats["errors"] += 1
                    error_text = await response.text()
                    return ServiceResponse(
                        success=False,
                        data=None,
                        status_code=response.status,
                        response_time=response_time,
                        error=f"HTTP {response.status}: {error_text}"
                    )
                
                response_data = await response.json()
                return ServiceResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status,
                    response_time=response_time
                )
                
        except asyncio.TimeoutError:
            stats["errors"] += 1
            return ServiceResponse(
                success=False,
                data=None,
                status_code=408,
                response_time=time.time() - start_time,
                error="Request timeout"
            )
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"Error calling service {service_name}: {str(e)}")
            return ServiceResponse(
                success=False,
                data=None,
                status_code=0,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _check_rate_limit(self, service_name: str) -> bool:
        """Check if service call is within rate limits"""
        if service_name not in self.rate_limiters:
            self.rate_limiters[service_name] = {
                "last_call": 0,
                "call_count": 0,
                "window_start": time.time()
            }
        
        limiter = self.rate_limiters[service_name]
        service_config = self.services[service_name]
        
        current_time = time.time()
        
        # Reset window if needed
        if current_time - limiter["window_start"] >= 60:  # 1 minute window
            limiter["call_count"] = 0
            limiter["window_start"] = current_time
        
        # Check rate limit
        if limiter["call_count"] >= service_config.rate_limit:
            return False
        
        limiter["call_count"] += 1
        limiter["last_call"] = current_time
        
        return True
    
    async def get_service_stats(self, service_name: str = None) -> Dict[str, Any]:
        """
        Get statistics for a service or all services
        
        Args:
            service_name: Optional service name to get stats for
            
        Returns:
            Dictionary containing service statistics
        """
        try:
            if service_name:
                if service_name not in self.service_stats:
                    return {
                        "success": False,
                        "error": f"Service '{service_name}' not found"
                    }
                
                stats = self.service_stats[service_name]
                avg_response_time = (stats["total_response_time"] / stats["calls"] 
                                   if stats["calls"] > 0 else 0)
                
                return {
                    "success": True,
                    "service_name": service_name,
                    "stats": {
                        "total_calls": stats["calls"],
                        "error_count": stats["errors"],
                        "success_rate": ((stats["calls"] - stats["errors"]) / stats["calls"] * 100 
                                       if stats["calls"] > 0 else 0),
                        "average_response_time": round(avg_response_time, 3),
                        "last_call": stats["last_call"]
                    }
                }
            else:
                all_stats = {}
                for name, stats in self.service_stats.items():
                    avg_response_time = (stats["total_response_time"] / stats["calls"] 
                                       if stats["calls"] > 0 else 0)
                    all_stats[name] = {
                        "total_calls": stats["calls"],
                        "error_count": stats["errors"],
                        "success_rate": ((stats["calls"] - stats["errors"]) / stats["calls"] * 100 
                                       if stats["calls"] > 0 else 0),
                        "average_response_time": round(avg_response_time, 3),
                        "last_call": stats["last_call"]
                    }
                
                return {
                    "success": True,
                    "services": all_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting service stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_service_connection(self, service_name: str) -> Dict[str, Any]:
        """
        Test connection to a service
        
        Args:
            service_name: Name of the service to test
            
        Returns:
            Dictionary containing test result
        """
        try:
            if service_name not in self.services:
                return {
                    "success": False,
                    "error": f"Service '{service_name}' not registered"
                }
            
            # Make a simple test call
            response = await self.call_service(service_name, "health", "GET")
            
            return {
                "success": response.success,
                "service_name": service_name,
                "status_code": response.status_code,
                "response_time": response.response_time,
                "error": response.error
            }
            
        except Exception as e:
            logger.error(f"Error testing service connection {service_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service_name": service_name
            }
    
    async def list_services(self) -> Dict[str, Any]:
        """
        List all registered services
        
        Returns:
            Dictionary containing list of services
        """
        try:
            services = []
            for name, config in self.services.items():
                services.append({
                    "name": name,
                    "base_url": config.base_url,
                    "timeout": config.timeout,
                    "max_retries": config.max_retries,
                    "rate_limit": config.rate_limit,
                    "has_api_key": bool(config.api_key)
                })
            
            return {
                "success": True,
                "services": services,
                "total_count": len(services)
            }
            
        except Exception as e:
            logger.error(f"Error listing services: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def remove_service(self, service_name: str) -> Dict[str, Any]:
        """
        Remove a service registration
        
        Args:
            service_name: Name of the service to remove
            
        Returns:
            Dictionary containing removal result
        """
        try:
            if service_name not in self.services:
                return {
                    "success": False,
                    "error": f"Service '{service_name}' not found"
                }
            
            # Remove service
            del self.services[service_name]
            
            # Remove stats
            if service_name in self.service_stats:
                del self.service_stats[service_name]
            
            # Remove rate limiter
            if service_name in self.rate_limiters:
                del self.rate_limiters[service_name]
            
            return {
                "success": True,
                "service_name": service_name,
                "message": f"Service '{service_name}' removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing service {service_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "service_name": service_name
            }
    
    async def batch_call_services(self, calls: List[Dict[str, Any]]) -> List[ServiceResponse]:
        """
        Make multiple service calls in parallel
        
        Args:
            calls: List of call specifications
            
        Returns:
            List of ServiceResponse objects
        """
        try:
            tasks = []
            for call in calls:
                task = self.call_service(
                    service_name=call["service_name"],
                    endpoint=call["endpoint"],
                    method=call.get("method", "GET"),
                    data=call.get("data"),
                    headers=call.get("headers")
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to ServiceResponse objects
            processed_responses = []
            for response in responses:
                if isinstance(response, Exception):
                    processed_responses.append(ServiceResponse(
                        success=False,
                        data=None,
                        status_code=0,
                        response_time=0,
                        error=str(response)
                    ))
                else:
                    processed_responses.append(response)
            
            return processed_responses
            
        except Exception as e:
            logger.error(f"Error in batch service calls: {str(e)}")
            return [ServiceResponse(
                success=False,
                data=None,
                status_code=0,
                response_time=0,
                error=str(e)
            )]
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get overall health status of all services
        
        Returns:
            Dictionary containing health information
        """
        try:
            health_status = {
                "total_services": len(self.services),
                "healthy_services": 0,
                "unhealthy_services": 0,
                "service_details": {}
            }
            
            for service_name in self.services.keys():
                test_result = await self.test_service_connection(service_name)
                is_healthy = test_result["success"]
                
                if is_healthy:
                    health_status["healthy_services"] += 1
                else:
                    health_status["unhealthy_services"] += 1
                
                health_status["service_details"][service_name] = {
                    "healthy": is_healthy,
                    "last_test": time.time(),
                    "error": test_result.get("error")
                }
            
            # Calculate overall health score
            if health_status["total_services"] > 0:
                health_score = (health_status["healthy_services"] / 
                              health_status["total_services"] * 100)
            else:
                health_score = 100
            
            health_status["health_score"] = round(health_score, 2)
            
            return {
                "success": True,
                "health_status": health_status
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 