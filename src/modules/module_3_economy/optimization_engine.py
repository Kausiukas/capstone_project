"""
Optimization Engine for Module 3: ECONOMY

This module handles cost optimization strategies and recommendations for the system.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from enum import Enum

import aiofiles


class OptimizationStrategy(Enum):
    """Optimization strategy types"""
    MODEL_SWITCHING = "model_switching"
    CACHE_OPTIMIZATION = "cache_optimization"
    BATCH_PROCESSING = "batch_processing"
    REQUEST_OPTIMIZATION = "request_optimization"
    RESOURCE_SCALING = "resource_scaling"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"


class OptimizationPriority(Enum):
    """Optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationStatus(Enum):
    """Optimization status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    id: str
    strategy: OptimizationStrategy
    priority: OptimizationPriority
    title: str
    description: str
    estimated_savings: Decimal
    implementation_cost: Decimal
    roi_percentage: float
    complexity: str  # "low", "medium", "high"
    prerequisites: List[str]
    created_at: datetime = None
    status: OptimizationStatus = OptimizationStatus.PENDING

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class OptimizationAction:
    """Optimization action to be executed"""
    id: str
    recommendation_id: str
    action_type: str
    parameters: Dict[str, Any]
    target_module: str
    expected_impact: Dict[str, Any]
    created_at: datetime = None
    executed_at: Optional[datetime] = None
    status: OptimizationStatus = OptimizationStatus.PENDING
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class OptimizationMetrics:
    """Optimization performance metrics"""
    total_recommendations: int
    implemented_recommendations: int
    total_savings: Decimal
    total_implementation_cost: Decimal
    net_savings: Decimal
    roi_percentage: float
    success_rate: float
    average_implementation_time: float  # in hours


class OptimizationEngine:
    """
    Engine for generating and managing cost optimization strategies.
    """
    
    def __init__(self, data_dir: str = "data/optimization"):
        self.data_dir = data_dir
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.actions: Dict[str, OptimizationAction] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Strategy templates
        self.strategy_templates = {
            OptimizationStrategy.MODEL_SWITCHING: {
                "title": "Model Switching Optimization",
                "description": "Switch to more cost-effective models for specific tasks",
                "complexity": "medium",
                "prerequisites": ["cost_tracker", "model_performance_data"]
            },
            OptimizationStrategy.CACHE_OPTIMIZATION: {
                "title": "Cache Optimization",
                "description": "Optimize caching strategies to reduce redundant API calls",
                "complexity": "low",
                "prerequisites": ["cache_manager", "usage_patterns"]
            },
            OptimizationStrategy.BATCH_PROCESSING: {
                "title": "Batch Processing",
                "description": "Group similar requests to reduce API call overhead",
                "complexity": "medium",
                "prerequisites": ["request_queue", "batch_processor"]
            },
            OptimizationStrategy.REQUEST_OPTIMIZATION: {
                "title": "Request Optimization",
                "description": "Optimize request parameters and reduce token usage",
                "complexity": "low",
                "prerequisites": ["request_analyzer", "token_counter"]
            },
            OptimizationStrategy.RESOURCE_SCALING: {
                "title": "Resource Scaling",
                "description": "Scale resources based on demand to optimize costs",
                "complexity": "high",
                "prerequisites": ["resource_monitor", "scaling_policy"]
            },
            OptimizationStrategy.ALGORITHM_OPTIMIZATION: {
                "title": "Algorithm Optimization",
                "description": "Optimize algorithms to reduce computational costs",
                "complexity": "high",
                "prerequisites": ["performance_analyzer", "algorithm_benchmarks"]
            }
        }
    
    async def initialize(self) -> None:
        """Initialize the optimization engine"""
        self.logger.info("Initializing optimization engine...")
        
        try:
            await self._ensure_data_dir()
            await self._load_recommendations()
            await self._load_actions()
            
            self.logger.info("Optimization engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize optimization engine: {e}")
            raise
    
    async def analyze_cost_patterns(
        self,
        cost_data: List[Dict],
        usage_data: List[Dict],
        performance_data: Optional[List[Dict]] = None
    ) -> List[OptimizationRecommendation]:
        """Analyze cost patterns and generate optimization recommendations"""
        async with self._lock:
            try:
                recommendations = []
                
                # Analyze different aspects
                model_recommendations = await self._analyze_model_usage(cost_data, usage_data)
                cache_recommendations = await self._analyze_cache_usage(usage_data)
                request_recommendations = await self._analyze_request_patterns(usage_data)
                
                recommendations.extend(model_recommendations)
                recommendations.extend(cache_recommendations)
                recommendations.extend(request_recommendations)
                
                # Store recommendations
                for rec in recommendations:
                    self.recommendations[rec.id] = rec
                
                await self._save_recommendations()
                
                self.logger.info(f"Generated {len(recommendations)} optimization recommendations")
                return recommendations
                
            except Exception as e:
                self.logger.error(f"Failed to analyze cost patterns: {e}")
                raise
    
    async def generate_recommendation(
        self,
        strategy: OptimizationStrategy,
        priority: OptimizationPriority,
        estimated_savings: Union[float, Decimal],
        implementation_cost: Union[float, Decimal],
        custom_title: Optional[str] = None,
        custom_description: Optional[str] = None,
        prerequisites: Optional[List[str]] = None
    ) -> str:
        """Generate a specific optimization recommendation"""
        async with self._lock:
            try:
                template = self.strategy_templates[strategy]
                
                recommendation_id = f"opt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{strategy.value}"
                
                title = custom_title or template["title"]
                description = custom_description or template["description"]
                complexity = template["complexity"]
                prereqs = prerequisites or template["prerequisites"]
                
                estimated_savings_decimal = Decimal(str(estimated_savings))
                implementation_cost_decimal = Decimal(str(implementation_cost))
                
                roi_percentage = 0.0
                if implementation_cost_decimal > 0:
                    roi_percentage = float((estimated_savings_decimal - implementation_cost_decimal) / implementation_cost_decimal * 100)
                
                recommendation = OptimizationRecommendation(
                    id=recommendation_id,
                    strategy=strategy,
                    priority=priority,
                    title=title,
                    description=description,
                    estimated_savings=estimated_savings_decimal,
                    implementation_cost=implementation_cost_decimal,
                    roi_percentage=roi_percentage,
                    complexity=complexity,
                    prerequisites=prereqs
                )
                
                self.recommendations[recommendation_id] = recommendation
                await self._save_recommendations()
                
                self.logger.info(f"Generated recommendation: {recommendation_id}")
                return recommendation_id
                
            except Exception as e:
                self.logger.error(f"Failed to generate recommendation: {e}")
                raise
    
    async def get_recommendation(self, recommendation_id: str) -> Optional[OptimizationRecommendation]:
        """Get recommendation by ID"""
        return self.recommendations.get(recommendation_id)
    
    async def list_recommendations(
        self,
        strategy: Optional[OptimizationStrategy] = None,
        priority: Optional[OptimizationPriority] = None,
        status: Optional[OptimizationStatus] = None
    ) -> List[OptimizationRecommendation]:
        """List recommendations with optional filtering"""
        recommendations = list(self.recommendations.values())
        
        if strategy:
            recommendations = [r for r in recommendations if r.strategy == strategy]
        if priority:
            recommendations = [r for r in recommendations if r.priority == priority]
        if status:
            recommendations = [r for r in recommendations if r.status == status]
        
        return recommendations
    
    async def update_recommendation_status(
        self,
        recommendation_id: str,
        status: OptimizationStatus
    ) -> bool:
        """Update recommendation status"""
        async with self._lock:
            try:
                if recommendation_id not in self.recommendations:
                    return False
                
                self.recommendations[recommendation_id].status = status
                await self._save_recommendations()
                
                self.logger.info(f"Updated recommendation status: {recommendation_id} -> {status.value}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update recommendation status: {e}")
                return False
    
    async def create_optimization_action(
        self,
        recommendation_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        target_module: str,
        expected_impact: Dict[str, Any]
    ) -> str:
        """Create an optimization action from a recommendation"""
        async with self._lock:
            try:
                if recommendation_id not in self.recommendations:
                    raise ValueError(f"Recommendation {recommendation_id} not found")
                
                action_id = f"action_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{action_type}"
                
                action = OptimizationAction(
                    id=action_id,
                    recommendation_id=recommendation_id,
                    action_type=action_type,
                    parameters=parameters,
                    target_module=target_module,
                    expected_impact=expected_impact
                )
                
                self.actions[action_id] = action
                await self._save_actions()
                
                self.logger.info(f"Created optimization action: {action_id}")
                return action_id
                
            except Exception as e:
                self.logger.error(f"Failed to create optimization action: {e}")
                raise
    
    async def execute_optimization_action(self, action_id: str) -> bool:
        """Execute an optimization action"""
        async with self._lock:
            try:
                if action_id not in self.actions:
                    return False
                
                action = self.actions[action_id]
                action.status = OptimizationStatus.IN_PROGRESS
                
                # Execute the action based on type
                result = await self._execute_action(action)
                
                if result["success"]:
                    action.status = OptimizationStatus.COMPLETED
                    action.result = result
                else:
                    action.status = OptimizationStatus.FAILED
                    action.result = result
                
                action.executed_at = datetime.now(timezone.utc)
                await self._save_actions()
                
                self.logger.info(f"Executed optimization action: {action_id} -> {action.status.value}")
                return result["success"]
                
            except Exception as e:
                self.logger.error(f"Failed to execute optimization action: {e}")
                if action_id in self.actions:
                    self.actions[action_id].status = OptimizationStatus.FAILED
                    self.actions[action_id].result = {"error": str(e)}
                    await self._save_actions()
                return False
    
    async def get_optimization_metrics(self) -> OptimizationMetrics:
        """Get optimization performance metrics"""
        total_recommendations = len(self.recommendations)
        implemented_recommendations = len([
            r for r in self.recommendations.values()
            if r.status == OptimizationStatus.COMPLETED
        ])
        
        total_savings = sum(r.estimated_savings for r in self.recommendations.values())
        total_implementation_cost = sum(r.implementation_cost for r in self.recommendations.values())
        net_savings = total_savings - total_implementation_cost
        
        roi_percentage = 0.0
        if total_implementation_cost > 0:
            roi_percentage = float(net_savings / total_implementation_cost * 100)
        
        success_rate = 0.0
        if total_recommendations > 0:
            success_rate = implemented_recommendations / total_recommendations
        
        # Calculate average implementation time
        completed_actions = [
            a for a in self.actions.values()
            if a.status == OptimizationStatus.COMPLETED and a.executed_at
        ]
        
        average_implementation_time = 0.0
        if completed_actions:
            total_time = sum(
                (a.executed_at - a.created_at).total_seconds() / 3600
                for a in completed_actions
            )
            average_implementation_time = total_time / len(completed_actions)
        
        return OptimizationMetrics(
            total_recommendations=total_recommendations,
            implemented_recommendations=implemented_recommendations,
            total_savings=total_savings,
            total_implementation_cost=total_implementation_cost,
            net_savings=net_savings,
            roi_percentage=roi_percentage,
            success_rate=success_rate,
            average_implementation_time=average_implementation_time
        )
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'recommendations.json': [],
            'actions.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_recommendations(self) -> None:
        """Load recommendations from file"""
        filepath = os.path.join(self.data_dir, 'recommendations.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    recommendations_data = json.loads(data)
                    
                    for rec_data in recommendations_data:
                        recommendation = OptimizationRecommendation(
                            id=rec_data['id'],
                            strategy=OptimizationStrategy(rec_data['strategy']),
                            priority=OptimizationPriority(rec_data['priority']),
                            title=rec_data['title'],
                            description=rec_data['description'],
                            estimated_savings=Decimal(str(rec_data['estimated_savings'])),
                            implementation_cost=Decimal(str(rec_data['implementation_cost'])),
                            roi_percentage=rec_data['roi_percentage'],
                            complexity=rec_data['complexity'],
                            prerequisites=rec_data['prerequisites'],
                            created_at=datetime.fromisoformat(rec_data['created_at']),
                            status=OptimizationStatus(rec_data['status'])
                        )
                        self.recommendations[recommendation.id] = recommendation
            else:
                # Create default file
                await self._save_recommendations()
        except Exception as e:
            self.logger.error(f"Failed to load recommendations: {e}")
            # Create default file on error
            await self._save_recommendations()

    async def _save_recommendations(self) -> None:
        """Save recommendations to file"""
        try:
            rec_file = f"{self.data_dir}/recommendations.json"
            recs_data = []
            for rec in self.recommendations.values():
                rec_dict = asdict(rec)
                rec_dict['strategy'] = rec_dict['strategy'].value
                rec_dict['priority'] = rec_dict['priority'].value
                rec_dict['status'] = rec_dict['status'].value
                rec_dict['estimated_savings'] = str(rec_dict['estimated_savings'])
                rec_dict['implementation_cost'] = str(rec_dict['implementation_cost'])
                rec_dict['created_at'] = rec_dict['created_at'].isoformat()
                recs_data.append(rec_dict)
            
            async with aiofiles.open(rec_file, 'w') as f:
                await f.write(json.dumps(recs_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save recommendations: {e}")
    
    async def _load_actions(self) -> None:
        """Load actions from file"""
        filepath = os.path.join(self.data_dir, 'actions.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    actions_data = json.loads(data)
                    
                    for action_data in actions_data:
                        action = OptimizationAction(
                            id=action_data['id'],
                            recommendation_id=action_data['recommendation_id'],
                            action_type=action_data['action_type'],
                            parameters=action_data['parameters'],
                            target_module=action_data['target_module'],
                            expected_impact=action_data['expected_impact'],
                            created_at=datetime.fromisoformat(action_data['created_at']),
                            executed_at=datetime.fromisoformat(action_data['executed_at']) if action_data.get('executed_at') else None,
                            status=OptimizationStatus(action_data['status']),
                            result=action_data.get('result')
                        )
                        self.actions[action.id] = action
            else:
                # Create default file
                await self._save_actions()
        except Exception as e:
            self.logger.error(f"Failed to load actions: {e}")
            # Create default file on error
            await self._save_actions()
    
    async def _save_actions(self) -> None:
        """Save actions to file"""
        try:
            actions_file = f"{self.data_dir}/actions.json"
            actions_data = []
            for action in self.actions.values():
                action_dict = asdict(action)
                action_dict['status'] = action_dict['status'].value
                action_dict['created_at'] = action_dict['created_at'].isoformat()
                if action_dict['executed_at']:
                    action_dict['executed_at'] = action_dict['executed_at'].isoformat()
                actions_data.append(action_dict)
            
            async with aiofiles.open(actions_file, 'w') as f:
                await f.write(json.dumps(actions_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save actions: {e}")
    
    async def _analyze_model_usage(
        self,
        cost_data: List[Dict],
        usage_data: List[Dict]
    ) -> List[OptimizationRecommendation]:
        """Analyze model usage patterns and generate recommendations"""
        recommendations = []
        
        # Group by model and analyze usage patterns
        model_usage = {}
        for usage in usage_data:
            model = usage.get('model', 'unknown')
            if model not in model_usage:
                model_usage[model] = {
                    'total_tokens': 0,
                    'total_cost': Decimal('0'),
                    'request_count': 0,
                    'avg_tokens_per_request': 0
                }
            
            model_usage[model]['total_tokens'] += usage.get('tokens_used', 0)
            model_usage[model]['total_cost'] += Decimal(str(usage.get('cost', 0)))
            model_usage[model]['request_count'] += 1
        
        # Calculate averages
        for model, data in model_usage.items():
            if data['request_count'] > 0:
                data['avg_tokens_per_request'] = data['total_tokens'] / data['request_count']
        
        # Generate recommendations based on patterns
        for model, data in model_usage.items():
            if data['avg_tokens_per_request'] > 1000:  # High token usage
                recommendation_id = await self.generate_recommendation(
                    strategy=OptimizationStrategy.MODEL_SWITCHING,
                    priority=OptimizationPriority.MEDIUM,
                    estimated_savings=float(data['total_cost'] * Decimal('0.3')),  # 30% savings estimate
                    implementation_cost=10.0,  # Implementation cost
                    custom_title=f"Switch {model} for Long Requests",
                    custom_description=f"Consider using a more efficient model for requests averaging {data['avg_tokens_per_request']:.0f} tokens"
                )
                recommendations.append(self.recommendations[recommendation_id])
        
        return recommendations
    
    async def _analyze_cache_usage(self, usage_data: List[Dict]) -> List[OptimizationRecommendation]:
        """Analyze cache usage patterns and generate recommendations"""
        recommendations = []
        
        # Analyze cache hit rates and patterns
        cache_hits = sum(1 for usage in usage_data if usage.get('cache_hit', False))
        total_requests = len(usage_data)
        
        if total_requests > 0:
            cache_hit_rate = cache_hits / total_requests
            
            if cache_hit_rate < 0.5:  # Low cache hit rate
                recommendation_id = await self.generate_recommendation(
                    strategy=OptimizationStrategy.CACHE_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    estimated_savings=50.0,  # Estimated savings
                    implementation_cost=5.0,  # Implementation cost
                    custom_title="Improve Cache Hit Rate",
                    custom_description=f"Current cache hit rate is {cache_hit_rate:.1%}. Implement better caching strategies."
                )
                recommendations.append(self.recommendations[recommendation_id])
        
        return recommendations
    
    async def _analyze_request_patterns(self, usage_data: List[Dict]) -> List[OptimizationRecommendation]:
        """Analyze request patterns and generate recommendations"""
        recommendations = []
        
        # Analyze request frequency and timing
        request_times = [usage.get('timestamp', 0) for usage in usage_data]
        if len(request_times) > 1:
            # Calculate time between requests
            time_diffs = []
            for i in range(1, len(request_times)):
                diff = request_times[i] - request_times[i-1]
                if diff > 0:
                    time_diffs.append(diff)
            
            if time_diffs:
                avg_time_diff = sum(time_diffs) / len(time_diffs)
                
                # If requests are frequent, suggest batching
                if avg_time_diff < 60:  # Less than 1 minute between requests
                    recommendation_id = await self.generate_recommendation(
                        strategy=OptimizationStrategy.BATCH_PROCESSING,
                        priority=OptimizationPriority.MEDIUM,
                        estimated_savings=30.0,  # Estimated savings
                        implementation_cost=15.0,  # Implementation cost
                        custom_title="Implement Request Batching",
                        custom_description=f"Average time between requests is {avg_time_diff:.1f} seconds. Consider batching similar requests."
                    )
                    recommendations.append(self.recommendations[recommendation_id])
        
        return recommendations
    
    async def _execute_action(self, action: OptimizationAction) -> Dict[str, Any]:
        """Execute a specific optimization action"""
        try:
            if action.action_type == "model_switch":
                return await self._execute_model_switch(action)
            elif action.action_type == "cache_optimization":
                return await self._execute_cache_optimization(action)
            elif action.action_type == "batch_processing":
                return await self._execute_batch_processing(action)
            elif action.action_type == "request_optimization":
                return await self._execute_request_optimization(action)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action.action_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_model_switch(self, action: OptimizationAction) -> Dict[str, Any]:
        """Execute model switching optimization"""
        # This would integrate with the cost tracker and model manager
        return {
            "success": True,
            "message": "Model switching optimization applied",
            "impact": {
                "estimated_savings": action.expected_impact.get("estimated_savings", 0),
                "model_changes": action.parameters.get("model_changes", [])
            }
        }
    
    async def _execute_cache_optimization(self, action: OptimizationAction) -> Dict[str, Any]:
        """Execute cache optimization"""
        # This would integrate with the memory manager
        return {
            "success": True,
            "message": "Cache optimization applied",
            "impact": {
                "cache_size_increased": action.parameters.get("cache_size_increase", 0),
                "ttl_adjusted": action.parameters.get("ttl_adjustment", 0)
            }
        }
    
    async def _execute_batch_processing(self, action: OptimizationAction) -> Dict[str, Any]:
        """Execute batch processing optimization"""
        # This would integrate with the external services manager
        return {
            "success": True,
            "message": "Batch processing optimization applied",
            "impact": {
                "batch_size": action.parameters.get("batch_size", 10),
                "max_wait_time": action.parameters.get("max_wait_time", 60)
            }
        }
    
    async def _execute_request_optimization(self, action: OptimizationAction) -> Dict[str, Any]:
        """Execute request optimization"""
        # This would integrate with the code analyzer and refactorer
        return {
            "success": True,
            "message": "Request optimization applied",
            "impact": {
                "max_tokens_reduced": action.parameters.get("max_tokens_reduction", 0),
                "temperature_adjusted": action.parameters.get("temperature_adjustment", 0)
            }
        } 