"""
Flow Manager for Module 4: LangflowConnector

This module handles Langflow flow management and operations.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum

import aiofiles


class FlowStatus(Enum):
    """Flow status types"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    ERROR = "error"


class FlowType(Enum):
    """Flow types"""
    CHATBOT = "chatbot"
    WORKFLOW = "workflow"
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    INTEGRATION = "integration"


class NodeType(Enum):
    """Node types in flows"""
    INPUT = "input"
    OUTPUT = "output"
    PROCESSOR = "processor"
    CONDITION = "condition"
    LOOP = "loop"
    API = "api"
    DATABASE = "database"
    CUSTOM = "custom"


@dataclass
class FlowNode:
    """Flow node configuration"""
    id: str
    name: str
    node_type: NodeType
    position: Dict[str, int]  # x, y coordinates
    config: Dict[str, Any]
    connections: List[str]  # Connected node IDs
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Flow:
    """Flow configuration"""
    id: str
    name: str
    description: str
    flow_type: FlowType
    status: FlowStatus
    nodes: List[FlowNode]
    edges: List[Dict[str, Any]]  # Connections between nodes
    variables: Dict[str, Any]  # Flow variables
    settings: Dict[str, Any]  # Flow settings
    created_at: datetime = None
    updated_at: datetime = None
    version: str = "1.0.0"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class FlowExecution:
    """Flow execution record"""
    id: str
    flow_id: str
    status: str  # "running", "completed", "failed", "cancelled"
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None  # in seconds
    node_executions: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}
        if self.node_executions is None:
            self.node_executions = []


class FlowManager:
    """
    Manages Langflow flows and their execution.
    """
    
    def __init__(self, data_dir: str = "data/flows"):
        self.data_dir = data_dir
        self.flows: Dict[str, Flow] = {}
        self.executions: Dict[str, FlowExecution] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Default flow templates
        self.default_flows = {
            "cost_analysis": {
                "name": "Cost Analysis Workflow",
                "description": "Automated cost analysis and reporting workflow",
                "flow_type": FlowType.ANALYSIS,
                "nodes": [
                    {
                        "id": "input_1",
                        "name": "Cost Data Input",
                        "node_type": NodeType.INPUT,
                        "position": {"x": 100, "y": 100},
                        "config": {"data_type": "cost_data"}
                    },
                    {
                        "id": "processor_1",
                        "name": "Cost Analyzer",
                        "node_type": NodeType.PROCESSOR,
                        "position": {"x": 300, "y": 100},
                        "config": {"analysis_type": "trend_analysis"}
                    },
                    {
                        "id": "output_1",
                        "name": "Analysis Report",
                        "node_type": NodeType.OUTPUT,
                        "position": {"x": 500, "y": 100},
                        "config": {"format": "json"}
                    }
                ],
                "edges": [
                    {"from": "input_1", "to": "processor_1"},
                    {"from": "processor_1", "to": "output_1"}
                ]
            },
            "optimization_workflow": {
                "name": "Optimization Workflow",
                "description": "Automated optimization recommendation workflow",
                "flow_type": FlowType.WORKFLOW,
                "nodes": [
                    {
                        "id": "input_1",
                        "name": "Performance Data",
                        "node_type": NodeType.INPUT,
                        "position": {"x": 100, "y": 100},
                        "config": {"data_type": "performance_metrics"}
                    },
                    {
                        "id": "condition_1",
                        "name": "Threshold Check",
                        "node_type": NodeType.CONDITION,
                        "position": {"x": 300, "y": 100},
                        "config": {"threshold": 0.8}
                    },
                    {
                        "id": "processor_1",
                        "name": "Optimization Engine",
                        "node_type": NodeType.PROCESSOR,
                        "position": {"x": 500, "y": 50},
                        "config": {"optimization_type": "cost_reduction"}
                    },
                    {
                        "id": "output_1",
                        "name": "Recommendations",
                        "node_type": NodeType.OUTPUT,
                        "position": {"x": 700, "y": 100},
                        "config": {"format": "json"}
                    }
                ],
                "edges": [
                    {"from": "input_1", "to": "condition_1"},
                    {"from": "condition_1", "to": "processor_1", "condition": "true"},
                    {"from": "processor_1", "to": "output_1"}
                ]
            }
        }
    
    async def initialize(self) -> None:
        """Initialize the flow manager"""
        self.logger.info("Initializing flow manager...")
        
        try:
            await self._ensure_data_dir()
            await self._load_flows()
            await self._load_executions()
            
            # Create default flows if none exist
            if not self.flows:
                await self._create_default_flows()
            
            self.logger.info("Flow manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize flow manager: {e}")
            raise
    
    async def create_flow(
        self,
        name: str,
        description: str,
        flow_type: FlowType,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new flow"""
        async with self._lock:
            try:
                flow_id = f"flow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
                
                # Convert node dictionaries to FlowNode objects
                flow_nodes = []
                for node_data in nodes:
                    node = FlowNode(
                        id=node_data["id"],
                        name=node_data["name"],
                        node_type=NodeType(node_data["node_type"]),
                        position=node_data["position"],
                        config=node_data.get("config", {}),
                        connections=node_data.get("connections", [])
                    )
                    flow_nodes.append(node)
                
                flow = Flow(
                    id=flow_id,
                    name=name,
                    description=description,
                    flow_type=flow_type,
                    status=FlowStatus.DRAFT,
                    nodes=flow_nodes,
                    edges=edges,
                    variables=variables or {},
                    settings=settings or {}
                )
                
                self.flows[flow_id] = flow
                await self._save_flows()
                
                self.logger.info(f"Created flow: {flow_id} - {name}")
                return flow_id
                
            except Exception as e:
                self.logger.error(f"Failed to create flow: {e}")
                raise
    
    async def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Get flow by ID"""
        return self.flows.get(flow_id)
    
    async def list_flows(
        self,
        flow_type: Optional[FlowType] = None,
        status: Optional[FlowStatus] = None
    ) -> List[Flow]:
        """List flows with optional filtering"""
        flows = list(self.flows.values())
        
        if flow_type:
            flows = [f for f in flows if f.flow_type == flow_type]
        if status:
            flows = [f for f in flows if f.status == status]
        
        return flows
    
    async def update_flow(
        self,
        flow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[FlowStatus] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        variables: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update flow configuration"""
        async with self._lock:
            try:
                if flow_id not in self.flows:
                    return False
                
                flow = self.flows[flow_id]
                
                if name is not None:
                    flow.name = name
                if description is not None:
                    flow.description = description
                if status is not None:
                    flow.status = status
                if nodes is not None:
                    # Convert node dictionaries to FlowNode objects
                    flow_nodes = []
                    for node_data in nodes:
                        node = FlowNode(
                            id=node_data["id"],
                            name=node_data["name"],
                            node_type=NodeType(node_data["node_type"]),
                            position=node_data["position"],
                            config=node_data.get("config", {}),
                            connections=node_data.get("connections", [])
                        )
                        flow_nodes.append(node)
                    flow.nodes = flow_nodes
                if edges is not None:
                    flow.edges = edges
                if variables is not None:
                    flow.variables = variables
                if settings is not None:
                    flow.settings = settings
                
                flow.updated_at = datetime.utcnow()
                await self._save_flows()
                
                self.logger.info(f"Updated flow: {flow_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update flow: {e}")
                return False
    
    async def delete_flow(self, flow_id: str) -> bool:
        """Delete flow"""
        async with self._lock:
            try:
                if flow_id not in self.flows:
                    return False
                
                del self.flows[flow_id]
                await self._save_flows()
                
                self.logger.info(f"Deleted flow: {flow_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete flow: {e}")
                return False
    
    async def execute_flow(
        self,
        flow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a flow"""
        async with self._lock:
            try:
                if flow_id not in self.flows:
                    raise ValueError(f"Flow {flow_id} not found")
                
                flow = self.flows[flow_id]
                if flow.status != FlowStatus.ACTIVE:
                    raise ValueError(f"Flow {flow_id} is not active")
                
                execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{flow_id}"
                
                execution = FlowExecution(
                    id=execution_id,
                    flow_id=flow_id,
                    status="running",
                    start_time=datetime.utcnow(),
                    input_data=input_data or {}
                )
                
                self.executions[execution_id] = execution
                await self._save_executions()
                
                # Start execution in background
                asyncio.create_task(self._execute_flow_background(execution))
                
                self.logger.info(f"Started flow execution: {execution_id}")
                return execution_id
                
            except Exception as e:
                self.logger.error(f"Failed to execute flow: {e}")
                raise
    
    async def get_execution(self, execution_id: str) -> Optional[FlowExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)
    
    async def list_executions(
        self,
        flow_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[FlowExecution]:
        """List executions with optional filtering"""
        executions = list(self.executions.values())
        
        if flow_id:
            executions = [e for e in executions if e.flow_id == flow_id]
        if status:
            executions = [e for e in executions if e.status == status]
        if start_date:
            executions = [e for e in executions if e.start_time >= start_date]
        if end_date:
            executions = [e for e in executions if e.start_time <= end_date]
        
        return sorted(executions, key=lambda x: x.start_time, reverse=True)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        async with self._lock:
            try:
                if execution_id not in self.executions:
                    return False
                
                execution = self.executions[execution_id]
                if execution.status != "running":
                    return False
                
                execution.status = "cancelled"
                execution.end_time = datetime.utcnow()
                if execution.start_time:
                    execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
                
                await self._save_executions()
                
                self.logger.info(f"Cancelled execution: {execution_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to cancel execution: {e}")
                return False
    
    async def get_flow_statistics(self, flow_id: str) -> Dict[str, Any]:
        """Get flow execution statistics"""
        try:
            flow_executions = [e for e in self.executions.values() if e.flow_id == flow_id]
            
            if not flow_executions:
                return {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "average_execution_time": 0,
                    "last_execution": None
                }
            
            total_executions = len(flow_executions)
            successful_executions = len([e for e in flow_executions if e.status == "completed"])
            failed_executions = len([e for e in flow_executions if e.status == "failed"])
            
            execution_times = [e.execution_time for e in flow_executions if e.execution_time is not None]
            average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            last_execution = max(flow_executions, key=lambda x: x.start_time)
            
            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
                "average_execution_time": average_execution_time,
                "last_execution": last_execution.start_time.isoformat() if last_execution else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get flow statistics: {e}")
            return {}
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'flows.json': [],
            'executions.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_flows(self) -> None:
        """Load flows from file"""
        filepath = os.path.join(self.data_dir, 'flows.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    flows_data = json.loads(data)
                    
                    for flow_data in flows_data:
                        # Reconstruct nodes
                        nodes = []
                        for node_data in flow_data['nodes']:
                            node = FlowNode(
                                id=node_data['id'],
                                name=node_data['name'],
                                node_type=NodeType(node_data['node_type']),
                                position=node_data['position'],
                                config=node_data['config'],
                                connections=node_data['connections'],
                                metadata=node_data.get('metadata', {})
                            )
                            nodes.append(node)
                        
                        flow = Flow(
                            id=flow_data['id'],
                            name=flow_data['name'],
                            description=flow_data['description'],
                            flow_type=FlowType(flow_data['flow_type']),
                            status=FlowStatus(flow_data['status']),
                            nodes=nodes,
                            edges=flow_data['edges'],
                            variables=flow_data.get('variables', {}),
                            settings=flow_data.get('settings', {}),
                            created_at=datetime.fromisoformat(flow_data['created_at']),
                            updated_at=datetime.fromisoformat(flow_data['updated_at']),
                            version=flow_data.get('version', '1.0.0')
                        )
                        self.flows[flow.id] = flow
            else:
                # Create default file
                await self._save_flows()
        except Exception as e:
            self.logger.error(f"Failed to load flows: {e}")
            # Create default file on error
            await self._save_flows()

    async def _save_flows(self) -> None:
        """Save flows to file"""
        try:
            flows_file = f"{self.data_dir}/flows.json"
            flows_data = []
            for flow in self.flows.values():
                flow_dict = asdict(flow)
                flow_dict['flow_type'] = flow_dict['flow_type'].value
                flow_dict['status'] = flow_dict['status'].value
                flow_dict['created_at'] = flow_dict['created_at'].isoformat()
                flow_dict['updated_at'] = flow_dict['updated_at'].isoformat()
                
                # Convert FlowNode objects to dictionaries
                nodes_data = []
                for node in flow.nodes:
                    node_dict = asdict(node)
                    node_dict['node_type'] = node_dict['node_type'].value
                    nodes_data.append(node_dict)
                flow_dict['nodes'] = nodes_data
                
                flows_data.append(flow_dict)
            
            async with aiofiles.open(flows_file, 'w') as f:
                await f.write(json.dumps(flows_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save flows: {e}")
    
    async def _load_executions(self) -> None:
        """Load executions from file"""
        filepath = os.path.join(self.data_dir, 'executions.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    executions_data = json.loads(data)
                    
                    for exec_data in executions_data:
                        execution = FlowExecution(
                            id=exec_data['id'],
                            flow_id=exec_data['flow_id'],
                            status=exec_data['status'],
                            start_time=datetime.fromisoformat(exec_data['start_time']),
                            end_time=datetime.fromisoformat(exec_data['end_time']) if exec_data.get('end_time') else None,
                            input_data=exec_data.get('input_data', {}),
                            output_data=exec_data.get('output_data', {}),
                            error_message=exec_data.get('error_message'),
                            execution_time=exec_data.get('execution_time'),
                            node_executions=exec_data.get('node_executions', [])
                        )
                        self.executions[execution.id] = execution
            else:
                # Create default file
                await self._save_executions()
        except Exception as e:
            self.logger.error(f"Failed to load executions: {e}")
            # Create default file on error
            await self._save_executions()
    
    async def _save_executions(self) -> None:
        """Save executions to file"""
        try:
            executions_file = f"{self.data_dir}/executions.json"
            executions_data = []
            for execution in self.executions.values():
                exec_dict = asdict(execution)
                exec_dict['start_time'] = exec_dict['start_time'].isoformat()
                if exec_dict['end_time']:
                    exec_dict['end_time'] = exec_dict['end_time'].isoformat()
                executions_data.append(exec_dict)
            
            async with aiofiles.open(executions_file, 'w') as f:
                await f.write(json.dumps(executions_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save executions: {e}")
    
    async def _create_default_flows(self) -> None:
        """Create default flow templates"""
        for flow_name, flow_config in self.default_flows.items():
            await self.create_flow(
                name=flow_config["name"],
                description=flow_config["description"],
                flow_type=flow_config["flow_type"],
                nodes=flow_config["nodes"],
                edges=flow_config["edges"]
            )
    
    async def _execute_flow_background(self, execution: FlowExecution) -> None:
        """Execute flow in background"""
        try:
            flow = self.flows[execution.flow_id]
            
            # Simulate flow execution
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update execution status
            execution.status = "completed"
            execution.end_time = datetime.utcnow()
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            # Generate mock output data
            execution.output_data = {
                "result": "success",
                "processed_nodes": len(flow.nodes),
                "execution_time": execution.execution_time,
                "timestamp": execution.end_time.isoformat()
            }
            
            # Add node execution details
            for node in flow.nodes:
                execution.node_executions.append({
                    "node_id": node.id,
                    "node_name": node.name,
                    "status": "completed",
                    "execution_time": execution.execution_time / len(flow.nodes),
                    "output": f"Processed {node.name}"
                })
            
            await self._save_executions()
            
            self.logger.info(f"Completed flow execution: {execution.id}")
            
        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.utcnow()
            execution.error_message = str(e)
            if execution.start_time:
                execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            await self._save_executions()
            self.logger.error(f"Failed flow execution {execution.id}: {e}") 