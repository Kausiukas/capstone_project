"""
Cost Tracker - Tracks token usage and costs
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Token usage structure"""
    operation_id: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime
    operation_type: str
    module: str

@dataclass
class CostSummary:
    """Cost summary structure"""
    total_cost_usd: float
    total_tokens: int
    operations_count: int
    average_cost_per_operation: float
    cost_by_model: Dict[str, float]
    cost_by_module: Dict[str, float]
    period_start: datetime
    period_end: datetime

class CostTracker:
    """
    Tracks token usage and costs
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / "cost_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.usage_records = []
        self.max_records = 10000
        self.model_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
        }
        self.tracking_enabled = True
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the cost tracker
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info(f"Initializing cost tracker for data directory: {self.data_dir}")
            
            # Ensure data directory exists
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Clear usage records
            self.usage_records.clear()
            
            # Load existing usage records if any
            usage_file = self.data_dir / "usage_records.json"
            if usage_file.exists():
                try:
                    async with aiofiles.open(usage_file, 'r') as f:
                        content = await f.read()
                        if content.strip():
                            records = json.loads(content)
                            self.usage_records = records[-self.max_records:]  # Keep only recent records
                            logger.info(f"Loaded {len(self.usage_records)} existing usage records")
                except Exception as e:
                    logger.warning(f"Could not load existing usage records: {e}")
            
            self.initialized = True
            logger.info("Cost tracker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cost tracker: {e}")
            return False
        
    async def record_token_usage(self, operation_id: str, model: str, 
                               input_tokens: int, output_tokens: int,
                               operation_type: str = "unknown", 
                               module: str = "unknown") -> Dict[str, Any]:
        """
        Record token usage for an operation
        
        Args:
            operation_id: Unique operation identifier
            model: Model used (e.g., "gpt-4", "claude-3")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            operation_type: Type of operation
            module: Module that performed the operation
            
        Returns:
            Dictionary containing recording result
        """
        try:
            if not self.tracking_enabled:
                return {
                    "success": True,
                    "message": "Cost tracking disabled"
                }
            
            # Calculate cost
            total_tokens = input_tokens + output_tokens
            cost_usd = await self._calculate_cost(model, input_tokens, output_tokens)
            
            # Create usage record
            usage = TokenUsage(
                operation_id=operation_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                timestamp=datetime.now(),
                operation_type=operation_type,
                module=module
            )
            
            # Store record
            self.usage_records.append(usage)
            
            # Limit records
            if len(self.usage_records) > self.max_records:
                self.usage_records.pop(0)
            
            # Save to disk
            await self._save_usage_record(usage)
            
            return {
                "success": True,
                "operation_id": operation_id,
                "total_tokens": total_tokens,
                "cost_usd": cost_usd,
                "timestamp": usage.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording token usage: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_cost_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get cost summary for specified hours
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing cost summary
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter records by time
            recent_records = [
                record for record in self.usage_records
                if record.timestamp >= cutoff_time
            ]
            
            if not recent_records:
                return {
                    "success": True,
                    "summary": {
                        "total_cost_usd": 0.0,
                        "total_tokens": 0,
                        "operations_count": 0,
                        "average_cost_per_operation": 0.0,
                        "cost_by_model": {},
                        "cost_by_module": {},
                        "period_start": cutoff_time.isoformat(),
                        "period_end": datetime.now().isoformat()
                    }
                }
            
            # Calculate summary
            total_cost = sum(record.cost_usd for record in recent_records)
            total_tokens = sum(record.total_tokens for record in recent_records)
            operations_count = len(recent_records)
            average_cost = total_cost / operations_count if operations_count > 0 else 0
            
            # Cost by model
            cost_by_model = {}
            for record in recent_records:
                if record.model not in cost_by_model:
                    cost_by_model[record.model] = 0
                cost_by_model[record.model] += record.cost_usd
            
            # Cost by module
            cost_by_module = {}
            for record in recent_records:
                if record.module not in cost_by_module:
                    cost_by_module[record.module] = 0
                cost_by_module[record.module] += record.cost_usd
            
            summary = CostSummary(
                total_cost_usd=total_cost,
                total_tokens=total_tokens,
                operations_count=operations_count,
                average_cost_per_operation=average_cost,
                cost_by_model=cost_by_model,
                cost_by_module=cost_by_module,
                period_start=cutoff_time,
                period_end=datetime.now()
            )
            
            return {
                "success": True,
                "summary": {
                    "total_cost_usd": round(total_cost, 4),
                    "total_tokens": total_tokens,
                    "operations_count": operations_count,
                    "average_cost_per_operation": round(average_cost, 4),
                    "cost_by_model": {k: round(v, 4) for k, v in cost_by_model.items()},
                    "cost_by_module": {k: round(v, 4) for k, v in cost_by_module.items()},
                    "period_start": summary.period_start.isoformat(),
                    "period_end": summary.period_end.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cost summary: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_usage_by_model(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get usage statistics by model
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing usage by model
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter records by time
            recent_records = [
                record for record in self.usage_records
                if record.timestamp >= cutoff_time
            ]
            
            # Group by model
            model_stats = {}
            for record in recent_records:
                if record.model not in model_stats:
                    model_stats[record.model] = {
                        "operations": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "total_cost_usd": 0.0
                    }
                
                stats = model_stats[record.model]
                stats["operations"] += 1
                stats["input_tokens"] += record.input_tokens
                stats["output_tokens"] += record.output_tokens
                stats["total_tokens"] += record.total_tokens
                stats["total_cost_usd"] += record.cost_usd
            
            # Calculate averages
            for model, stats in model_stats.items():
                stats["average_tokens_per_operation"] = stats["total_tokens"] / stats["operations"]
                stats["average_cost_per_operation"] = stats["total_cost_usd"] / stats["operations"]
                stats["total_cost_usd"] = round(stats["total_cost_usd"], 4)
                stats["average_tokens_per_operation"] = round(stats["average_tokens_per_operation"], 2)
                stats["average_cost_per_operation"] = round(stats["average_cost_per_operation"], 4)
            
            return {
                "success": True,
                "model_stats": model_stats,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting usage by model: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_usage_by_module(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get usage statistics by module
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing usage by module
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter records by time
            recent_records = [
                record for record in self.usage_records
                if record.timestamp >= cutoff_time
            ]
            
            # Group by module
            module_stats = {}
            for record in recent_records:
                if record.module not in module_stats:
                    module_stats[record.module] = {
                        "operations": 0,
                        "total_tokens": 0,
                        "total_cost_usd": 0.0,
                        "models_used": set()
                    }
                
                stats = module_stats[record.module]
                stats["operations"] += 1
                stats["total_tokens"] += record.total_tokens
                stats["total_cost_usd"] += record.cost_usd
                stats["models_used"].add(record.model)
            
            # Convert sets to lists and round values
            for module, stats in module_stats.items():
                stats["models_used"] = list(stats["models_used"])
                stats["total_cost_usd"] = round(stats["total_cost_usd"], 4)
                stats["average_tokens_per_operation"] = round(stats["total_tokens"] / stats["operations"], 2)
                stats["average_cost_per_operation"] = round(stats["total_cost_usd"] / stats["operations"], 4)
            
            return {
                "success": True,
                "module_stats": module_stats,
                "period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Error getting usage by module: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def set_model_cost(self, model: str, input_cost: float, output_cost: float) -> Dict[str, Any]:
        """
        Set cost for a model
        
        Args:
            model: Model name
            input_cost: Cost per 1K input tokens
            output_cost: Cost per 1K output tokens
            
        Returns:
            Dictionary containing set result
        """
        try:
            self.model_costs[model] = {
                "input": input_cost,
                "output": output_cost
            }
            
            return {
                "success": True,
                "model": model,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "message": f"Cost set for model '{model}'"
            }
            
        except Exception as e:
            logger.error(f"Error setting model cost: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_model_costs(self) -> Dict[str, Any]:
        """
        Get all model costs
        
        Returns:
            Dictionary containing model costs
        """
        try:
            return {
                "success": True,
                "model_costs": self.model_costs
            }
            
        except Exception as e:
            logger.error(f"Error getting model costs: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def enable_tracking(self, enabled: bool = True) -> Dict[str, Any]:
        """
        Enable or disable cost tracking
        
        Args:
            enabled: Whether to enable tracking
            
        Returns:
            Dictionary containing enable result
        """
        try:
            self.tracking_enabled = enabled
            
            return {
                "success": True,
                "tracking_enabled": enabled,
                "message": f"Cost tracking {'enabled' if enabled else 'disabled'}"
            }
            
        except Exception as e:
            logger.error(f"Error enabling tracking: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def clear_usage_records(self, hours: int = None) -> Dict[str, Any]:
        """
        Clear usage records
        
        Args:
            hours: Clear records older than this many hours (None = clear all)
            
        Returns:
            Dictionary containing clear result
        """
        try:
            if hours is None:
                # Clear all records
                cleared_count = len(self.usage_records)
                self.usage_records.clear()
            else:
                # Clear records older than specified hours
                cutoff_time = datetime.now() - timedelta(hours=hours)
                original_count = len(self.usage_records)
                self.usage_records = [
                    record for record in self.usage_records
                    if record.timestamp >= cutoff_time
                ]
                cleared_count = original_count - len(self.usage_records)
            
            return {
                "success": True,
                "cleared_count": cleared_count,
                "remaining_records": len(self.usage_records)
            }
            
        except Exception as e:
            logger.error(f"Error clearing usage records: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""
        try:
            if model not in self.model_costs:
                # Use default cost if model not found
                model = "gpt-3.5-turbo"
            
            costs = self.model_costs[model]
            
            # Calculate costs (per 1K tokens)
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (output_tokens / 1000) * costs["output"]
            
            return input_cost + output_cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0
    
    async def _save_usage_record(self, usage: TokenUsage):
        """Save usage record to disk"""
        try:
            # Create daily file
            date_str = usage.timestamp.strftime("%Y-%m-%d")
            file_path = self.data_dir / f"usage_{date_str}.jsonl"
            
            # Prepare record data
            record_data = {
                "operation_id": usage.operation_id,
                "model": usage.model,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": usage.cost_usd,
                "timestamp": usage.timestamp.isoformat(),
                "operation_type": usage.operation_type,
                "module": usage.module
            }
            
            # Append to file
            async with aiofiles.open(file_path, 'a') as f:
                await f.write(json.dumps(record_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving usage record: {str(e)}")
    
    async def cleanup(self):
        """
        Cleanup resources and reset state
        """
        try:
            # Clear usage records
            self.usage_records.clear()
            self.initialized = False
            logger.info("Cost tracker cleanup completed")
        except Exception as e:
            logger.error(f"Error during cost tracker cleanup: {e}") 