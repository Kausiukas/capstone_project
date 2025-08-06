"""
System Coordinator - Manages inter-module communication and coordination
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable, Coroutine
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for inter-module communication"""
    COMMAND = "command"
    RESPONSE = "response"
    EVENT = "event"
    STATUS = "status"
    ERROR = "error"

@dataclass
class ModuleMessage:
    """Module message structure"""
    id: str
    source_module: str
    target_module: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 0
    requires_response: bool = False
    response_to: str = None

@dataclass
class ModuleStatus:
    """Module status structure"""
    module_name: str
    status: str  # "running", "stopped", "error", "initializing"
    last_heartbeat: datetime
    health_score: float
    error_count: int
    message_count: int
    uptime: timedelta

class SystemCoordinator:
    """
    Coordinates communication and operations between modules
    """
    
    def __init__(self):
        self.modules = {}
        self.message_queue = asyncio.Queue()
        self.message_handlers = {}
        self.module_status = {}
        self.coordination_tasks = []
        self.running = False
        self.message_id_counter = 0
        self.initialized = False

    async def initialize(self) -> bool:
        """
        Initialize the system coordinator

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing system coordinator...")

            # Clear existing state
            self.modules.clear()
            self.message_handlers.clear()
            self.module_status.clear()
            self.message_id_counter = 0

            # Initialize message queue
            if not self.message_queue.empty():
                # Clear the queue
                while not self.message_queue.empty():
                    try:
                        self.message_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

            self.initialized = True
            logger.info("System coordinator initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize system coordinator: {e}")
            return False
        
    async def start(self) -> Dict[str, Any]:
        """
        Start the system coordinator
        
        Returns:
            Dictionary containing start result
        """
        try:
            if self.running:
                return {
                    "success": False,
                    "error": "System coordinator already running"
                }
            
            self.running = True
            
            # Start coordination tasks
            self.coordination_tasks = [
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._status_broadcaster())
            ]
            
            return {
                "success": True,
                "message": "System coordinator started successfully",
                "tasks_started": len(self.coordination_tasks)
            }
            
        except Exception as e:
            logger.error(f"Error starting system coordinator: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop(self) -> Dict[str, Any]:
        """
        Stop the system coordinator
        
        Returns:
            Dictionary containing stop result
        """
        try:
            if not self.running:
                return {
                    "success": False,
                    "error": "System coordinator not running"
                }
            
            self.running = False
            
            # Cancel coordination tasks
            for task in self.coordination_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.coordination_tasks, return_exceptions=True)
            
            return {
                "success": True,
                "message": "System coordinator stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping system coordinator: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def register_module(self, module_name: str, 
                            message_handler: Callable[[ModuleMessage], Coroutine[Any, Any, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Register a module with the coordinator
        
        Args:
            module_name: Name of the module
            message_handler: Optional message handler function
            
        Returns:
            Dictionary containing registration result
        """
        try:
            if module_name in self.modules:
                return {
                    "success": False,
                    "error": f"Module '{module_name}' already registered"
                }
            
            self.modules[module_name] = {
                "name": module_name,
                "message_handler": message_handler,
                "registered_at": datetime.now()
            }
            
            self.module_status[module_name] = ModuleStatus(
                module_name=module_name,
                status="initializing",
                last_heartbeat=datetime.now(),
                health_score=100.0,
                error_count=0,
                message_count=0,
                uptime=timedelta(0)
            )
            
            return {
                "success": True,
                "module_name": module_name,
                "message": f"Module '{module_name}' registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error registering module {module_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "module_name": module_name
            }
    
    async def unregister_module(self, module_name: str) -> Dict[str, Any]:
        """
        Unregister a module from the coordinator
        
        Args:
            module_name: Name of the module to unregister
            
        Returns:
            Dictionary containing unregistration result
        """
        try:
            if module_name not in self.modules:
                return {
                    "success": False,
                    "error": f"Module '{module_name}' not registered"
                }
            
            del self.modules[module_name]
            
            if module_name in self.module_status:
                del self.module_status[module_name]
            
            return {
                "success": True,
                "module_name": module_name,
                "message": f"Module '{module_name}' unregistered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error unregistering module {module_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "module_name": module_name
            }
    
    async def send_message(self, source_module: str, target_module: str,
                          message_type: MessageType, payload: Dict[str, Any],
                          priority: int = 0, requires_response: bool = False) -> Dict[str, Any]:
        """
        Send a message to another module
        
        Args:
            source_module: Source module name
            target_module: Target module name
            message_type: Type of message
            payload: Message payload
            priority: Message priority (higher = more important)
            requires_response: Whether response is required
            
        Returns:
            Dictionary containing send result
        """
        try:
            if source_module not in self.modules:
                return {
                    "success": False,
                    "error": f"Source module '{source_module}' not registered"
                }
            
            if target_module not in self.modules:
                return {
                    "success": False,
                    "error": f"Target module '{target_module}' not registered"
                }
            
            # Generate message ID
            self.message_id_counter += 1
            message_id = f"msg_{self.message_id_counter}_{int(time.time())}"
            
            # Create message
            message = ModuleMessage(
                id=message_id,
                source_module=source_module,
                target_module=target_module,
                message_type=message_type,
                payload=payload,
                timestamp=datetime.now(),
                priority=priority,
                requires_response=requires_response
            )
            
            # Add to queue
            await self.message_queue.put(message)
            
            # Update module status
            if source_module in self.module_status:
                self.module_status[source_module].message_count += 1
            
            return {
                "success": True,
                "message_id": message_id,
                "message": "Message queued successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def broadcast_message(self, source_module: str, message_type: MessageType,
                               payload: Dict[str, Any], exclude_modules: List[str] = None) -> Dict[str, Any]:
        """
        Broadcast a message to all modules
        
        Args:
            source_module: Source module name
            message_type: Type of message
            payload: Message payload
            exclude_modules: Modules to exclude from broadcast
            
        Returns:
            Dictionary containing broadcast result
        """
        try:
            exclude_modules = exclude_modules or []
            target_modules = [name for name in self.modules.keys() 
                            if name != source_module and name not in exclude_modules]
            
            results = []
            for target_module in target_modules:
                result = await self.send_message(
                    source_module=source_module,
                    target_module=target_module,
                    message_type=message_type,
                    payload=payload
                )
                results.append({
                    "target_module": target_module,
                    "result": result
                })
            
            return {
                "success": True,
                "broadcast_results": results,
                "total_sent": len(target_modules)
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_module_status(self, module_name: str = None) -> Dict[str, Any]:
        """
        Get status of a module or all modules
        
        Args:
            module_name: Optional module name to get status for
            
        Returns:
            Dictionary containing module status
        """
        try:
            if module_name:
                if module_name not in self.module_status:
                    return {
                        "success": False,
                        "error": f"Module '{module_name}' not found"
                    }
                
                status = self.module_status[module_name]
                return {
                    "success": True,
                    "module_status": {
                        "module_name": status.module_name,
                        "status": status.status,
                        "last_heartbeat": status.last_heartbeat.isoformat(),
                        "health_score": status.health_score,
                        "error_count": status.error_count,
                        "message_count": status.message_count,
                        "uptime": str(status.uptime)
                    }
                }
            else:
                all_status = {}
                for name, status in self.module_status.items():
                    all_status[name] = {
                        "module_name": status.module_name,
                        "status": status.status,
                        "last_heartbeat": status.last_heartbeat.isoformat(),
                        "health_score": status.health_score,
                        "error_count": status.error_count,
                        "message_count": status.message_count,
                        "uptime": str(status.uptime)
                    }
                
                return {
                    "success": True,
                    "modules_status": all_status,
                    "total_modules": len(all_status)
                }
                
        except Exception as e:
            logger.error(f"Error getting module status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_module_heartbeat(self, module_name: str) -> Dict[str, Any]:
        """
        Update module heartbeat
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary containing heartbeat result
        """
        try:
            if module_name not in self.module_status:
                return {
                    "success": False,
                    "error": f"Module '{module_name}' not found"
                }
            
            status = self.module_status[module_name]
            status.last_heartbeat = datetime.now()
            status.status = "running"
            
            # Calculate uptime
            if module_name in self.modules:
                registered_at = self.modules[module_name]["registered_at"]
                status.uptime = datetime.now() - registered_at
            
            return {
                "success": True,
                "module_name": module_name,
                "heartbeat_time": status.last_heartbeat.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating module heartbeat: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _message_processor(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message
                await self._process_message(message)
                
                # Mark task as done
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message processor: {str(e)}")
    
    async def _process_message(self, message: ModuleMessage):
        """Process a single message"""
        try:
            target_module = message.target_module
            
            if target_module not in self.modules:
                logger.error(f"Target module '{target_module}' not found for message {message.id}")
                return
            
            module_info = self.modules[target_module]
            message_handler = module_info.get("message_handler")
            
            if message_handler:
                # Call message handler
                try:
                    response = await message_handler(message)
                    
                    # Send response if required
                    if message.requires_response:
                        response_message = ModuleMessage(
                            id=f"resp_{message.id}",
                            source_module=target_module,
                            target_module=message.source_module,
                            message_type=MessageType.RESPONSE,
                            payload=response,
                            timestamp=datetime.now(),
                            response_to=message.id
                        )
                        await self.message_queue.put(response_message)
                        
                except Exception as e:
                    logger.error(f"Error in message handler for module '{target_module}': {str(e)}")
                    
                    # Update module status
                    if target_module in self.module_status:
                        self.module_status[target_module].error_count += 1
                        self.module_status[target_module].health_score = max(0, 
                            self.module_status[target_module].health_score - 10)
            
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {str(e)}")
    
    async def _health_monitor(self):
        """Monitor module health"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for module_name, status in self.module_status.items():
                    # Check if module is responsive
                    time_since_heartbeat = current_time - status.last_heartbeat
                    
                    if time_since_heartbeat > timedelta(minutes=5):
                        status.status = "error"
                        status.health_score = max(0, status.health_score - 20)
                    elif time_since_heartbeat > timedelta(minutes=1):
                        status.status = "warning"
                        status.health_score = max(0, status.health_score - 5)
                    else:
                        status.status = "running"
                        status.health_score = min(100, status.health_score + 1)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitor: {str(e)}")
                await asyncio.sleep(30)
    
    async def _status_broadcaster(self):
        """Broadcast system status periodically"""
        while self.running:
            try:
                # Get overall system status
                system_status = {
                    "total_modules": len(self.modules),
                    "running_modules": sum(1 for status in self.module_status.values() 
                                         if status.status == "running"),
                    "error_modules": sum(1 for status in self.module_status.values() 
                                       if status.status == "error"),
                    "average_health_score": sum(status.health_score for status in self.module_status.values()) / 
                                          max(len(self.module_status), 1),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Broadcast status
                await self.broadcast_message(
                    source_module="system_coordinator",
                    message_type=MessageType.STATUS,
                    payload=system_status
                )
                
                await asyncio.sleep(60)  # Broadcast every minute
                
            except Exception as e:
                logger.error(f"Error in status broadcaster: {str(e)}")
                await asyncio.sleep(60) 