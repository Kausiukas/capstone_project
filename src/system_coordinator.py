"""
Main System Coordinator for LangFlow Connect

This module serves as the central coordinator for all system modules,
providing a unified interface and managing the overall system lifecycle.
"""

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Import all modules
from modules.module_1_main import (
    WorkspaceManager, RepositoryIngestor, CodeAnalyzer,
    CodeRefactorer, ExternalServiceManager
)
from modules.module_2_support import (
    PostgreSQLVectorAgent, SystemCoordinator, HealthMonitor,
    PerformanceTracker, MemoryManager
)
from modules.module_3_economy import (
    CostTracker, BudgetManager, OptimizationEngine,
    CostAnalyzer, AlertSystem
)
from modules.module_4_langflow import (
    LangflowConnector, DataVisualizer, FlowManager, ConnectionMonitor
)


@dataclass
class SystemStatus:
    """System status information"""
    is_running: bool
    start_time: datetime
    modules_initialized: List[str]
    active_connections: int
    total_operations: int
    system_health: str  # "healthy", "warning", "critical"
    last_heartbeat: datetime


class LangFlowSystemCoordinator:
    """
    Main system coordinator for the LangFlow Connect system.
    
    This class manages the initialization, coordination, and lifecycle
    of all system modules, providing a unified interface for the entire system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "config/system_config.json"
        
        # Module containers
        self.module_1_components: Dict[str, Any] = {}
        self.module_2_components: Dict[str, Any] = {}
        self.module_3_components: Dict[str, Any] = {}
        self.module_4_components: Dict[str, Any] = {}
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.system_status = SystemStatus(
            is_running=False,
            start_time=datetime.now(timezone.utc),
            modules_initialized=[],
            active_connections=0,
            total_operations=0,
            system_health="unknown",
            last_heartbeat=datetime.now(timezone.utc)
        )
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Configure logging to handle Unicode properly
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/system_coordinator.log', encoding='utf-8')
            ]
        )
    
    async def initialize_system(self) -> bool:
        """Initialize the entire system"""
        self.logger.info("Initializing LangFlow Connect System...")
        
        try:
            # Create necessary directories
            await self._ensure_directories()
            
            # Initialize Module 1: MAIN
            await self._initialize_module_1()
            
            # Initialize Module 2: SUPPORT
            await self._initialize_module_2()
            
            # Initialize Module 3: ECONOMY
            await self._initialize_module_3()
            
            # Initialize Module 4: LangflowConnector
            await self._initialize_module_4()
            
            # Setup inter-module communication
            await self._setup_module_communication()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            self.start_time = datetime.now(timezone.utc)
            self.system_status.start_time = self.start_time
            self.system_status.modules_initialized = [
                "module_1_main", "module_2_support", 
                "module_3_economy", "module_4_langflow"
            ]
            
            self.logger.info("LangFlow Connect System initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False
    
    async def start_system(self) -> bool:
        """Start the system"""
        if not self.is_initialized:
            self.logger.error("System not initialized. Call initialize_system() first.")
            return False
        
        self.logger.info("Starting LangFlow Connect System...")
        
        try:
            # Start all modules
            await self._start_module_1()
            await self._start_module_2()
            await self._start_module_3()
            await self._start_module_4()
            
            self.is_running = True
            self.system_status.is_running = True
            self.system_status.system_health = "healthy"
            
            self.logger.info("LangFlow Connect System started successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            return False
    
    async def stop_system(self) -> bool:
        """Stop the system"""
        self.logger.info("Stopping LangFlow Connect System...")
        
        try:
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Stop all modules
            await self._stop_module_1()
            await self._stop_module_2()
            await self._stop_module_3()
            await self._stop_module_4()
            
            self.is_running = False
            self.system_status.is_running = False
            
            self.logger.info("LangFlow Connect System stopped successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop system: {e}")
            return False
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        if self.is_running:
            # Update status from active modules
            await self._update_system_status()
        
        return self.system_status
    
    async def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Get status of a specific module"""
        try:
            if module_name == "module_1_main":
                return await self._get_module_1_status()
            elif module_name == "module_2_support":
                return await self._get_module_2_status()
            elif module_name == "module_3_economy":
                return await self._get_module_3_status()
            elif module_name == "module_4_langflow":
                return await self._get_module_4_status()
            else:
                raise ValueError(f"Unknown module: {module_name}")
        except Exception as e:
            self.logger.error(f"Failed to get status for {module_name}: {e}")
            return {"error": str(e)}
    
    async def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        self.logger.info(f"Executing workflow: {workflow_name}")
        
        try:
            if workflow_name == "code_analysis_workflow":
                return await self._execute_code_analysis_workflow(parameters)
            elif workflow_name == "cost_optimization_workflow":
                return await self._execute_cost_optimization_workflow(parameters)
            elif workflow_name == "system_health_check_workflow":
                return await self._execute_system_health_check_workflow(parameters)
            elif workflow_name == "langflow_visualization_workflow":
                return await self._execute_langflow_visualization_workflow(parameters)
            else:
                raise ValueError(f"Unknown workflow: {workflow_name}")
        except Exception as e:
            self.logger.error(f"Failed to execute workflow {workflow_name}: {e}")
            return {"error": str(e)}
    
    async def _ensure_directories(self):
        """Ensure necessary directories exist"""
        directories = [
            "logs", "data", "config", "temp",
            "data/workspace", "data/repositories", "data/costs",
            "data/budgets", "data/optimization", "data/analysis",
            "data/alerts", "data/visualizations", "data/flows",
            "data/monitoring"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def _initialize_module_1(self):
        """Initialize Module 1: MAIN"""
        self.logger.info("Initializing Module 1 (MAIN)...")
        
        self.module_1_components['workspace_manager'] = WorkspaceManager()
        self.module_1_components['repository_ingestor'] = RepositoryIngestor()
        self.module_1_components['code_analyzer'] = CodeAnalyzer()
        self.module_1_components['code_refactorer'] = CodeRefactorer()
        self.module_1_components['external_services'] = ExternalServiceManager()
        
        for name, component in self.module_1_components.items():
            await component.initialize()
            self.logger.info(f"Initialized {name}")
    
    async def _initialize_module_2(self):
        """Initialize Module 2: SUPPORT"""
        self.logger.info("Initializing Module 2 (SUPPORT)...")
        
        self.module_2_components['postgresql_agent'] = PostgreSQLVectorAgent()
        self.module_2_components['system_coordinator'] = SystemCoordinator()
        self.module_2_components['health_monitor'] = HealthMonitor()
        self.module_2_components['performance_tracker'] = PerformanceTracker()
        self.module_2_components['memory_manager'] = MemoryManager()
        
        for name, component in self.module_2_components.items():
            await component.initialize()
            self.logger.info(f"Initialized {name}")
    
    async def _initialize_module_3(self):
        """Initialize Module 3: ECONOMY"""
        self.logger.info("Initializing Module 3 (ECONOMY)...")
        
        self.module_3_components['cost_tracker'] = CostTracker()
        self.module_3_components['budget_manager'] = BudgetManager()
        self.module_3_components['optimization_engine'] = OptimizationEngine()
        self.module_3_components['cost_analyzer'] = CostAnalyzer()
        self.module_3_components['alert_system'] = AlertSystem()
        
        for name, component in self.module_3_components.items():
            await component.initialize()
            self.logger.info(f"Initialized {name}")
    
    async def _initialize_module_4(self):
        """Initialize Module 4: LangflowConnector"""
        self.logger.info("Initializing Module 4 (LangflowConnector)...")
        
        self.module_4_components['langflow_connector'] = LangflowConnector()
        self.module_4_components['data_visualizer'] = DataVisualizer()
        self.module_4_components['flow_manager'] = FlowManager()
        self.module_4_components['connection_monitor'] = ConnectionMonitor()
        
        for name, component in self.module_4_components.items():
            await component.initialize()
            self.logger.info(f"Initialized {name}")
    
    async def _setup_module_communication(self):
        """Setup inter-module communication"""
        self.logger.info("Setting up inter-module communication...")
        
        system_coordinator = self.module_2_components['system_coordinator']
        
        # Register all modules with the system coordinator
        for module_name, components in [
            ("module_1", self.module_1_components),
            ("module_2", self.module_2_components),
            ("module_3", self.module_3_components),
            ("module_4", self.module_4_components)
        ]:
            for component_name, component in components.items():
                await system_coordinator.register_module(
                    f"{module_name}_{component_name}", 
                    component
                )
        
        self.logger.info("Inter-module communication setup complete")
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        self.logger.info("Starting background tasks...")
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.background_tasks.append(self.heartbeat_task)
        
        # Start health monitoring
        health_monitor = self.module_2_components['health_monitor']
        health_task = asyncio.create_task(health_monitor.start_monitoring())
        self.background_tasks.append(health_task)
        
        # Start connection monitoring
        connection_monitor = self.module_4_components['connection_monitor']
        connection_task = asyncio.create_task(connection_monitor.start_monitoring())
        self.background_tasks.append(connection_task)
        
        self.logger.info("Background tasks started")
    
    async def _stop_background_tasks(self):
        """Stop background tasks"""
        self.logger.info("Stopping background tasks...")
        
        for task in self.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.background_tasks.clear()
        self.logger.info("Background tasks stopped")
    
    async def _start_module_1(self):
        """Start Module 1 components"""
        self.logger.info("Starting Module 1 components...")
        # Module 1 components are stateless, no specific start needed
        self.logger.info("Module 1 components ready")
    
    async def _start_module_2(self):
        """Start Module 2 components"""
        self.logger.info("Starting Module 2 components...")
        
        system_coordinator = self.module_2_components['system_coordinator']
        await system_coordinator.start()
        
        memory_manager = self.module_2_components['memory_manager']
        await memory_manager.start()
        
        self.logger.info("Module 2 components started")
    
    async def _start_module_3(self):
        """Start Module 3 components"""
        self.logger.info("Starting Module 3 components...")
        # Module 3 components are stateless, no specific start needed
        self.logger.info("Module 3 components ready")
    
    async def _start_module_4(self):
        """Start Module 4 components"""
        self.logger.info("Starting Module 4 components...")
        
        # Start connection monitoring
        connection_monitor = self.module_4_components['connection_monitor']
        await connection_monitor.start_monitoring()
        
        self.logger.info("Module 4 components started")
    
    async def _stop_module_1(self):
        """Stop Module 1 components"""
        self.logger.info("Stopping Module 1 components...")
        # Module 1 components are stateless, no specific stop needed
        self.logger.info("Module 1 components stopped")
    
    async def _stop_module_2(self):
        """Stop Module 2 components"""
        self.logger.info("Stopping Module 2 components...")
        
        system_coordinator = self.module_2_components['system_coordinator']
        await system_coordinator.stop()
        
        memory_manager = self.module_2_components['memory_manager']
        await memory_manager.stop()
        
        health_monitor = self.module_2_components['health_monitor']
        await health_monitor.stop_monitoring()
        
        self.logger.info("Module 2 components stopped")
    
    async def _stop_module_3(self):
        """Stop Module 3 components"""
        self.logger.info("Stopping Module 3 components...")
        # Module 3 components are stateless, no specific stop needed
        self.logger.info("Module 3 components stopped")
    
    async def _stop_module_4(self):
        """Stop Module 4 components"""
        self.logger.info("Stopping Module 4 components...")
        
        connection_monitor = self.module_4_components['connection_monitor']
        await connection_monitor.stop_monitoring()
        
        self.logger.info("Module 4 components stopped")
    
    async def _heartbeat_loop(self):
        """Heartbeat loop for system monitoring"""
        while self.is_running:
            try:
                self.system_status.last_heartbeat = datetime.now(timezone.utc)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(60)
    
    async def _update_system_status(self):
        """Update system status from active modules"""
        try:
            # Get health monitor status
            health_monitor = self.module_2_components['health_monitor']
            health_metrics = await health_monitor.get_current_metrics()
            
            # Determine system health
            if health_metrics and health_metrics.get('cpu_percentage', 0) > 90:
                self.system_status.system_health = "critical"
            elif health_metrics and health_metrics.get('cpu_percentage', 0) > 70:
                self.system_status.system_health = "warning"
            else:
                self.system_status.system_health = "healthy"
            
            # Update operation count
            self.system_status.total_operations += 1
            
        except Exception as e:
            self.logger.error(f"Failed to update system status: {e}")
    
    async def _get_module_1_status(self) -> Dict[str, Any]:
        """Get Module 1 status"""
        return {
            "module": "module_1_main",
            "status": "active",
            "components": list(self.module_1_components.keys()),
            "operations": self.system_status.total_operations
        }
    
    async def _get_module_2_status(self) -> Dict[str, Any]:
        """Get Module 2 status"""
        health_monitor = self.module_2_components['health_monitor']
        metrics = await health_monitor.get_current_metrics()
        
        return {
            "module": "module_2_support",
            "status": "active",
            "components": list(self.module_2_components.keys()),
            "health_metrics": metrics,
            "operations": self.system_status.total_operations
        }
    
    async def _get_module_3_status(self) -> Dict[str, Any]:
        """Get Module 3 status"""
        cost_tracker = self.module_3_components['cost_tracker']
        cost_summary = await cost_tracker.get_cost_summary()
        
        return {
            "module": "module_3_economy",
            "status": "active",
            "components": list(self.module_3_components.keys()),
            "cost_summary": cost_summary.__dict__ if cost_summary else None,
            "operations": self.system_status.total_operations
        }
    
    async def _get_module_4_status(self) -> Dict[str, Any]:
        """Get Module 4 status"""
        connection_monitor = self.module_4_components['connection_monitor']
        health_summary = await connection_monitor.get_health_summary()
        
        return {
            "module": "module_4_langflow",
            "status": "active",
            "components": list(self.module_4_components.keys()),
            "connection_health": health_summary,
            "operations": self.system_status.total_operations
        }
    
    async def _execute_code_analysis_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code analysis workflow"""
        try:
            # 1. Analyze code
            code_analyzer = self.module_1_components['code_analyzer']
            code_content = parameters.get('code_content', '')
            language = parameters.get('language', 'python')
            
            analysis = await code_analyzer.analyze_code(code_content, language)
            
            # 2. Track costs
            cost_tracker = self.module_3_components['cost_tracker']
            await cost_tracker.record_token_usage(
                model="gpt-4",
                tokens_used=len(code_content.split()),
                cost_per_token=0.00003,
                operation="code_analysis"
            )
            
            # 3. Create visualization
            data_visualizer = self.module_4_components['data_visualizer']
            chart_id = await data_visualizer.create_chart(
                title="Code Analysis Results",
                chart_type="bar",
                data_source="analysis_data",
                x_axis="metric",
                y_axis="value"
            )
            
            return {
                "workflow": "code_analysis_workflow",
                "status": "completed",
                "analysis": analysis,
                "chart_id": chart_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "workflow": "code_analysis_workflow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_cost_optimization_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cost optimization workflow"""
        try:
            # 1. Analyze costs
            cost_analyzer = self.module_3_components['cost_analyzer']
            cost_data = parameters.get('cost_data', [])
            
            report_id = await cost_analyzer.analyze_costs(cost_data)
            report = await cost_analyzer.get_report(report_id)
            
            # 2. Generate optimization recommendations
            optimization_engine = self.module_3_components['optimization_engine']
            recommendation_id = await optimization_engine.generate_recommendation(
                strategy="model_switching",
                priority="high",
                estimated_savings=50.0,
                implementation_cost=10.0
            )
            
            # 3. Create visualization
            data_visualizer = self.module_4_components['data_visualizer']
            chart_id = await data_visualizer.create_chart(
                title="Cost Optimization Analysis",
                chart_type="line",
                data_source="cost_data",
                x_axis="date",
                y_axis="cost"
            )
            
            return {
                "workflow": "cost_optimization_workflow",
                "status": "completed",
                "report": report.__dict__ if report else None,
                "recommendation_id": recommendation_id,
                "chart_id": chart_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "workflow": "cost_optimization_workflow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_system_health_check_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system health check workflow"""
        try:
            # 1. Get system health metrics
            health_monitor = self.module_2_components['health_monitor']
            metrics = await health_monitor.get_current_metrics()
            
            # 2. Get connection health
            connection_monitor = self.module_4_components['connection_monitor']
            connection_health = await connection_monitor.get_health_summary()
            
            # 3. Create health dashboard
            data_visualizer = self.module_4_components['data_visualizer']
            chart_id = await data_visualizer.create_chart(
                title="System Health Overview",
                chart_type="gauge",
                data_source="health_data",
                x_axis="metric",
                y_axis="value"
            )
            
            return {
                "workflow": "system_health_check_workflow",
                "status": "completed",
                "health_metrics": metrics,
                "connection_health": connection_health,
                "chart_id": chart_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "workflow": "system_health_check_workflow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_langflow_visualization_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Langflow visualization workflow"""
        try:
            # 1. Get data from other modules
            cost_tracker = self.module_3_components['cost_tracker']
            cost_summary = await cost_tracker.get_cost_summary()
            
            # 2. Create multiple visualizations
            data_visualizer = self.module_4_components['data_visualizer']
            
            # Cost trends chart
            cost_chart_id = await data_visualizer.create_chart(
                title="Cost Trends",
                chart_type="line",
                data_source="cost_data",
                x_axis="date",
                y_axis="cost"
            )
            
            # Performance metrics chart
            perf_chart_id = await data_visualizer.create_chart(
                title="Performance Metrics",
                chart_type="bar",
                data_source="performance_data",
                x_axis="metric",
                y_axis="value"
            )
            
            # 3. Create dashboard
            dashboard_id = await data_visualizer.create_dashboard(
                name="System Overview Dashboard",
                description="Comprehensive system overview",
                charts=[cost_chart_id, perf_chart_id]
            )
            
            return {
                "workflow": "langflow_visualization_workflow",
                "status": "completed",
                "cost_summary": cost_summary.__dict__ if cost_summary else None,
                "dashboard_id": dashboard_id,
                "charts": [cost_chart_id, perf_chart_id],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "workflow": "langflow_visualization_workflow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Convenience functions for easy system management
async def create_system_coordinator(config_path: Optional[str] = None) -> LangFlowSystemCoordinator:
    """Create and initialize a system coordinator"""
    coordinator = LangFlowSystemCoordinator(config_path)
    await coordinator.initialize_system()
    return coordinator


async def start_system(config_path: Optional[str] = None) -> LangFlowSystemCoordinator:
    """Create, initialize, and start the system"""
    coordinator = await create_system_coordinator(config_path)
    await coordinator.start_system()
    return coordinator


async def stop_system(coordinator: LangFlowSystemCoordinator) -> bool:
    """Stop the system"""
    return await coordinator.stop_system() 