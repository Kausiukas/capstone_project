"""
Inspector Scheduler
Task 4.1.2: Inspector Scheduler

This module provides advanced scheduling capabilities for the Inspector automation framework,
including cron-like scheduling, dependency management, and schedule optimization.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from croniter import croniter

from inspector_config_manager import InspectorConfigManager
from inspector_automation_framework import InspectorAutomationFramework, AutomationJob, AutomationStatus


class ScheduleType(Enum):
    """Types of schedules."""
    CRON = "cron"
    INTERVAL = "interval"
    ONCE = "once"
    DEPENDENCY = "dependency"


class SchedulePriority(Enum):
    """Schedule priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScheduleConfig:
    """Configuration for a schedule."""
    schedule_id: str
    name: str
    description: str
    schedule_type: ScheduleType
    expression: str  # Cron expression or interval string
    timezone: str = "UTC"
    enabled: bool = True
    priority: SchedulePriority = SchedulePriority.NORMAL
    max_concurrent: int = 1
    retry_failed: bool = True
    retry_count: int = 3
    retry_delay: int = 300  # 5 minutes
    timeout: int = 3600  # 1 hour
    dependencies: List[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ScheduledJob:
    """A job that has been scheduled."""
    schedule_id: str
    job_id: str
    schedule_config: ScheduleConfig
    job: AutomationJob
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    status: str = "pending"
    error_count: int = 0
    total_duration: float = 0.0


class InspectorScheduler:
    """
    Advanced scheduler for Inspector automation framework.
    
    Provides cron-like scheduling, dependency management, and schedule optimization.
    """
    
    def __init__(self, config_manager: InspectorConfigManager, 
                 automation_framework: InspectorAutomationFramework):
        """Initialize the scheduler."""
        self.config_manager = config_manager
        self.automation_framework = automation_framework
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.scheduled_jobs: Dict[str, ScheduledJob] = {}
        self.running_schedules: Set[str] = set()
        self.scheduler_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Setup directories
        self.data_dir = Path("data/scheduler")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Load existing schedules
        self._load_schedules()
        self._load_scheduled_jobs()
    
    def create_schedule(self, name: str, description: str, schedule_type: ScheduleType,
                       expression: str, job_ids: List[str], timezone: str = "UTC",
                       priority: SchedulePriority = SchedulePriority.NORMAL,
                       max_concurrent: int = 1, retry_failed: bool = True,
                       retry_count: int = 3, retry_delay: int = 300,
                       timeout: int = 3600, dependencies: List[str] = None,
                       tags: List[str] = None) -> str:
        """
        Create a new schedule configuration.
        
        Args:
            name: Schedule name
            description: Schedule description
            schedule_type: Type of schedule (cron, interval, once, dependency)
            expression: Schedule expression (cron string, interval, etc.)
            job_ids: List of job IDs to schedule
            timezone: Timezone for the schedule
            priority: Schedule priority
            max_concurrent: Maximum concurrent executions
            retry_failed: Whether to retry failed jobs
            retry_count: Number of retries
            retry_delay: Delay between retries in seconds
            timeout: Job timeout in seconds
            dependencies: List of schedule IDs this schedule depends on
            tags: List of tags for categorization
            
        Returns:
            Schedule ID
        """
        schedule_id = f"schedule_{int(time.time())}_{name.lower().replace(' ', '_')}"
        
        schedule_config = ScheduleConfig(
            schedule_id=schedule_id,
            name=name,
            description=description,
            schedule_type=schedule_type,
            expression=expression,
            timezone=timezone,
            priority=priority,
            max_concurrent=max_concurrent,
            retry_failed=retry_failed,
            retry_count=retry_count,
            retry_delay=retry_delay,
            timeout=timeout,
            dependencies=dependencies or [],
            tags=tags or []
        )
        
        # Calculate next run time
        schedule_config.next_run = self._calculate_next_run(schedule_config)
        
        self.schedules[schedule_id] = schedule_config
        
        # Create scheduled jobs for each job ID
        for job_id in job_ids:
            if job_id in self.automation_framework.jobs:
                job = self.automation_framework.jobs[job_id]
                scheduled_job = ScheduledJob(
                    schedule_id=schedule_id,
                    job_id=job_id,
                    schedule_config=schedule_config,
                    job=job,
                    next_execution=schedule_config.next_run
                )
                
                scheduled_job_id = f"{schedule_id}_{job_id}"
                self.scheduled_jobs[scheduled_job_id] = scheduled_job
        
        self._save_schedules()
        self._save_scheduled_jobs()
        
        self.logger.info(f"Created schedule: {schedule_id} - {name}")
        return schedule_id
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleConfig]:
        """Get a schedule by ID."""
        return self.schedules.get(schedule_id)
    
    def list_schedules(self, enabled_only: bool = False) -> List[ScheduleConfig]:
        """List all schedules, optionally filtered by enabled status."""
        if enabled_only:
            return [schedule for schedule in self.schedules.values() if schedule.enabled]
        return list(self.schedules.values())
    
    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """Update schedule properties."""
        if schedule_id not in self.schedules:
            return False
        
        schedule = self.schedules[schedule_id]
        for key, value in kwargs.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        # Recalculate next run if expression changed
        if 'expression' in kwargs or 'schedule_type' in kwargs:
            schedule.next_run = self._calculate_next_run(schedule)
        
        self._save_schedules()
        self.logger.info(f"Updated schedule: {schedule_id}")
        return True
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule and all its scheduled jobs."""
        if schedule_id not in self.schedules:
            return False
        
        # Remove all scheduled jobs for this schedule
        scheduled_job_ids = [sj_id for sj_id in self.scheduled_jobs.keys() 
                           if sj_id.startswith(schedule_id)]
        for sj_id in scheduled_job_ids:
            del self.scheduled_jobs[sj_id]
        
        del self.schedules[schedule_id]
        self._save_schedules()
        self._save_scheduled_jobs()
        self.logger.info(f"Deleted schedule: {schedule_id}")
        return True
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        return self.update_schedule(schedule_id, enabled=True)
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        return self.update_schedule(schedule_id, enabled=False)
    
    def get_scheduled_jobs(self, schedule_id: Optional[str] = None) -> List[ScheduledJob]:
        """Get scheduled jobs, optionally filtered by schedule ID."""
        if schedule_id:
            return [sj for sj in self.scheduled_jobs.values() if sj.schedule_id == schedule_id]
        return list(self.scheduled_jobs.values())
    
    def get_due_jobs(self) -> List[ScheduledJob]:
        """Get all jobs that are due for execution."""
        now = datetime.now()
        due_jobs = []
        
        for scheduled_job in self.scheduled_jobs.values():
            schedule = scheduled_job.schedule_config
            
            if (schedule.enabled and 
                scheduled_job.next_execution and 
                scheduled_job.next_execution <= now and
                scheduled_job.status != "running"):
                
                # Check dependencies
                if self._check_schedule_dependencies(schedule):
                    due_jobs.append(scheduled_job)
        
        # Sort by priority
        due_jobs.sort(key=lambda sj: self._get_priority_value(sj.schedule_config.priority), reverse=True)
        return due_jobs
    
    async def start_scheduler(self) -> None:
        """Start the scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Scheduler started")
    
    async def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Scheduler stopped")
    
    async def run_schedule_once(self, schedule_id: str) -> List[Any]:
        """Run a schedule once immediately."""
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        schedule = self.schedules[schedule_id]
        scheduled_jobs = self.get_scheduled_jobs(schedule_id)
        
        if not scheduled_jobs:
            self.logger.warning(f"No jobs found for schedule: {schedule_id}")
            return []
        
        # Check dependencies
        if not self._check_schedule_dependencies(schedule):
            raise ValueError(f"Schedule dependencies not met: {schedule_id}")
        
        # Run jobs
        job_ids = [sj.job_id for sj in scheduled_jobs]
        results = await self.automation_framework.run_jobs_batch(job_ids, parallel=True)
        
        # Update scheduled job status
        for scheduled_job in scheduled_jobs:
            scheduled_job.last_execution = datetime.now()
            scheduled_job.execution_count += 1
            scheduled_job.next_execution = self._calculate_next_run(schedule)
            
            # Find corresponding result
            for result in results:
                if result.job_id == scheduled_job.job_id:
                    if result.status == AutomationStatus.COMPLETED:
                        scheduled_job.status = "completed"
                        scheduled_job.total_duration += result.duration
                    else:
                        scheduled_job.status = "failed"
                        scheduled_job.error_count += 1
                    break
        
        self._save_scheduled_jobs()
        return results
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        total_schedules = len(self.schedules)
        enabled_schedules = sum(1 for s in self.schedules.values() if s.enabled)
        total_scheduled_jobs = len(self.scheduled_jobs)
        running_schedules = len(self.running_schedules)
        
        due_jobs = self.get_due_jobs()
        
        return {
            "is_running": self.is_running,
            "total_schedules": total_schedules,
            "enabled_schedules": enabled_schedules,
            "total_scheduled_jobs": total_scheduled_jobs,
            "running_schedules": running_schedules,
            "due_jobs": len(due_jobs),
            "next_due_job": min([sj.next_execution for sj in due_jobs]) if due_jobs else None
        }
    
    def optimize_schedules(self) -> Dict[str, Any]:
        """Optimize schedule execution for better performance."""
        optimizations = {
            "schedules_optimized": 0,
            "conflicts_resolved": 0,
            "dependencies_optimized": 0,
            "recommendations": []
        }
        
        # Analyze schedule conflicts
        conflicts = self._find_schedule_conflicts()
        if conflicts:
            optimizations["conflicts_resolved"] = len(conflicts)
            optimizations["recommendations"].append(f"Found {len(conflicts)} schedule conflicts")
        
        # Optimize dependencies
        dependency_optimizations = self._optimize_dependencies()
        optimizations["dependencies_optimized"] = dependency_optimizations
        
        # Optimize execution times
        time_optimizations = self._optimize_execution_times()
        optimizations["schedules_optimized"] = time_optimizations
        
        return optimizations
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Get due jobs
                due_jobs = self.get_due_jobs()
                
                if due_jobs:
                    self.logger.info(f"Found {len(due_jobs)} due jobs")
                    
                    # Group by schedule to respect max_concurrent
                    schedule_groups = {}
                    for scheduled_job in due_jobs:
                        schedule_id = scheduled_job.schedule_id
                        if schedule_id not in schedule_groups:
                            schedule_groups[schedule_id] = []
                        schedule_groups[schedule_id].append(scheduled_job)
                    
                    # Execute each schedule group
                    for schedule_id, scheduled_jobs in schedule_groups.items():
                        if schedule_id in self.running_schedules:
                            continue
                        
                        schedule = scheduled_jobs[0].schedule_config
                        if len(scheduled_jobs) > schedule.max_concurrent:
                            # Limit to max_concurrent
                            scheduled_jobs = scheduled_jobs[:schedule.max_concurrent]
                        
                        # Execute schedule
                        asyncio.create_task(self._execute_schedule(schedule_id, scheduled_jobs))
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _execute_schedule(self, schedule_id: str, scheduled_jobs: List[ScheduledJob]) -> None:
        """Execute a schedule with its jobs."""
        self.running_schedules.add(schedule_id)
        
        try:
            schedule = scheduled_jobs[0].schedule_config
            
            # Update status
            for scheduled_job in scheduled_jobs:
                scheduled_job.status = "running"
            
            # Run jobs
            job_ids = [sj.job_id for sj in scheduled_jobs]
            results = await self.automation_framework.run_jobs_batch(job_ids, parallel=True)
            
            # Update scheduled job status
            for scheduled_job in scheduled_jobs:
                scheduled_job.last_execution = datetime.now()
                scheduled_job.execution_count += 1
                scheduled_job.next_execution = self._calculate_next_run(schedule)
                
                # Find corresponding result
                for result in results:
                    if result.job_id == scheduled_job.job_id:
                        if result.status == AutomationStatus.COMPLETED:
                            scheduled_job.status = "completed"
                            scheduled_job.total_duration += result.duration
                        else:
                            scheduled_job.status = "failed"
                            scheduled_job.error_count += 1
                        break
            
            # Update schedule
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(schedule)
            
            self._save_schedules()
            self._save_scheduled_jobs()
            
            self.logger.info(f"Executed schedule: {schedule_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing schedule {schedule_id}: {e}")
        finally:
            self.running_schedules.discard(schedule_id)
    
    def _calculate_next_run(self, schedule: ScheduleConfig) -> Optional[datetime]:
        """Calculate next run time for a schedule."""
        if not schedule.enabled:
            return None
        
        now = datetime.now()
        
        if schedule.schedule_type == ScheduleType.CRON:
            try:
                cron = croniter(schedule.expression, now)
                return cron.get_next(datetime)
            except Exception as e:
                self.logger.error(f"Invalid cron expression: {schedule.expression} - {e}")
                return None
        
        elif schedule.schedule_type == ScheduleType.INTERVAL:
            try:
                # Parse interval expression (e.g., "every 5 minutes", "2 hours", "1 day")
                expression = schedule.expression.lower().strip()
                
                # Handle "every X" format
                if expression.startswith("every "):
                    expression = expression[6:]  # Remove "every "
                
                parts = expression.split()
                if len(parts) >= 2:
                    amount = int(parts[0])
                    unit = parts[1].lower()
                    
                    if unit.startswith("minute"):
                        return now + timedelta(minutes=amount)
                    elif unit.startswith("hour"):
                        return now + timedelta(hours=amount)
                    elif unit.startswith("day"):
                        return now + timedelta(days=amount)
                    elif unit.startswith("week"):
                        return now + timedelta(weeks=amount)
                return now + timedelta(hours=1)  # Default
            except Exception as e:
                self.logger.error(f"Invalid interval expression: {schedule.expression} - {e}")
                return None
        
        elif schedule.schedule_type == ScheduleType.ONCE:
            try:
                # Parse datetime string
                return datetime.fromisoformat(schedule.expression)
            except Exception as e:
                self.logger.error(f"Invalid datetime expression: {schedule.expression} - {e}")
                return None
        
        elif schedule.schedule_type == ScheduleType.DEPENDENCY:
            # For dependency-based schedules, next run is calculated when dependencies complete
            return None
        
        return None
    
    def _check_schedule_dependencies(self, schedule: ScheduleConfig) -> bool:
        """Check if schedule dependencies are met."""
        for dep_id in schedule.dependencies:
            if dep_id not in self.schedules:
                return False
            
            dep_schedule = self.schedules[dep_id]
            if not dep_schedule.last_run:
                return False
        
        return True
    
    def _get_priority_value(self, priority: SchedulePriority) -> int:
        """Get numeric value for priority sorting."""
        priority_values = {
            SchedulePriority.LOW: 1,
            SchedulePriority.NORMAL: 2,
            SchedulePriority.HIGH: 3,
            SchedulePriority.CRITICAL: 4
        }
        return priority_values.get(priority, 2)
    
    def _find_schedule_conflicts(self) -> List[Dict[str, Any]]:
        """Find conflicts between schedules."""
        conflicts = []
        
        # Check for overlapping execution times
        schedules = list(self.schedules.values())
        for i, schedule1 in enumerate(schedules):
            for schedule2 in schedules[i+1:]:
                if (schedule1.schedule_type == ScheduleType.CRON and 
                    schedule2.schedule_type == ScheduleType.CRON):
                    
                    # Check if cron expressions might conflict
                    try:
                        cron1 = croniter(schedule1.expression, datetime.now())
                        cron2 = croniter(schedule2.expression, datetime.now())
                        
                        # Check next few executions for overlap
                        for _ in range(5):
                            next1 = cron1.get_next(datetime)
                            next2 = cron2.get_next(datetime)
                            
                            if abs((next1 - next2).total_seconds()) < 60:  # Within 1 minute
                                conflicts.append({
                                    "schedule1": schedule1.schedule_id,
                                    "schedule2": schedule2.schedule_id,
                                    "type": "execution_overlap",
                                    "next1": next1,
                                    "next2": next2
                                })
                                break
                    except Exception:
                        pass
        
        return conflicts
    
    def _optimize_dependencies(self) -> int:
        """Optimize schedule dependencies."""
        optimizations = 0
        
        # Find circular dependencies
        for schedule in self.schedules.values():
            if self._has_circular_dependency(schedule.schedule_id, set()):
                self.logger.warning(f"Circular dependency detected in schedule: {schedule.schedule_id}")
                optimizations += 1
        
        return optimizations
    
    def _has_circular_dependency(self, schedule_id: str, visited: Set[str]) -> bool:
        """Check for circular dependencies."""
        if schedule_id in visited:
            return True
        
        if schedule_id not in self.schedules:
            return False
        
        visited.add(schedule_id)
        schedule = self.schedules[schedule_id]
        
        for dep_id in schedule.dependencies:
            if self._has_circular_dependency(dep_id, visited.copy()):
                return True
        
        return False
    
    def _optimize_execution_times(self) -> int:
        """Optimize execution times for better resource utilization."""
        optimizations = 0
        
        # Simple optimization: spread out schedules that run at the same time
        cron_schedules = [s for s in self.schedules.values() 
                         if s.schedule_type == ScheduleType.CRON]
        
        for schedule in cron_schedules:
            # Add small random offset to avoid exact overlaps
            if schedule.expression.endswith(" * * * *"):  # Every minute
                # Change to every 2-3 minutes to reduce load
                new_expression = schedule.expression.replace(" * * * *", " */2 * * * *")
                schedule.expression = new_expression
                schedule.next_run = self._calculate_next_run(schedule)
                optimizations += 1
        
        return optimizations
    
    def _save_schedules(self) -> None:
        """Save schedules to file."""
        schedules_file = self.data_dir / "schedules.json"
        schedules_data = {}
        
        for schedule_id, schedule in self.schedules.items():
            schedule_dict = asdict(schedule)
            # Convert enum values to strings for JSON serialization
            schedule_dict['schedule_type'] = schedule.schedule_type.value
            schedule_dict['priority'] = schedule.priority.value
            schedules_data[schedule_id] = schedule_dict
        
        with open(schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules_data, f, indent=2, default=str)
    
    def _load_schedules(self) -> None:
        """Load schedules from file."""
        schedules_file = self.data_dir / "schedules.json"
        if not schedules_file.exists():
            return
        
        try:
            with open(schedules_file, 'r', encoding='utf-8') as f:
                schedules_data = json.load(f)
            
            for schedule_id, schedule_dict in schedules_data.items():
                # Convert string dates back to datetime
                if 'created_at' in schedule_dict and schedule_dict['created_at']:
                    schedule_dict['created_at'] = datetime.fromisoformat(schedule_dict['created_at'])
                if 'last_run' in schedule_dict and schedule_dict['last_run']:
                    schedule_dict['last_run'] = datetime.fromisoformat(schedule_dict['last_run'])
                if 'next_run' in schedule_dict and schedule_dict['next_run']:
                    schedule_dict['next_run'] = datetime.fromisoformat(schedule_dict['next_run'])
                
                # Convert enum strings back to enums
                if 'schedule_type' in schedule_dict:
                    schedule_dict['schedule_type'] = ScheduleType(schedule_dict['schedule_type'])
                if 'priority' in schedule_dict:
                    schedule_dict['priority'] = SchedulePriority(schedule_dict['priority'])
                
                self.schedules[schedule_id] = ScheduleConfig(**schedule_dict)
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")
    
    def _save_scheduled_jobs(self) -> None:
        """Save scheduled jobs to file."""
        jobs_file = self.data_dir / "scheduled_jobs.json"
        jobs_data = {}
        
        for job_id, scheduled_job in self.scheduled_jobs.items():
            job_dict = asdict(scheduled_job)
            # Remove the job object as it's not serializable
            job_dict.pop('job', None)
            job_dict.pop('schedule_config', None)
            jobs_data[job_id] = job_dict
        
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, default=str)
    
    def _load_scheduled_jobs(self) -> None:
        """Load scheduled jobs from file."""
        jobs_file = self.data_dir / "scheduled_jobs.json"
        if not jobs_file.exists():
            return
        
        try:
            with open(jobs_file, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            for job_id, job_dict in jobs_data.items():
                # Convert string dates back to datetime
                if 'last_execution' in job_dict and job_dict['last_execution']:
                    job_dict['last_execution'] = datetime.fromisoformat(job_dict['last_execution'])
                if 'next_execution' in job_dict and job_dict['next_execution']:
                    job_dict['next_execution'] = datetime.fromisoformat(job_dict['next_execution'])
                
                # Reconstruct job and schedule_config objects
                schedule_id = job_dict.get('schedule_id')
                job_id_inner = job_dict.get('job_id')
                
                if schedule_id in self.schedules and job_id_inner in self.automation_framework.jobs:
                    job_dict['schedule_config'] = self.schedules[schedule_id]
                    job_dict['job'] = self.automation_framework.jobs[job_id_inner]
                    
                    self.scheduled_jobs[job_id] = ScheduledJob(**job_dict)
        except Exception as e:
            self.logger.error(f"Error loading scheduled jobs: {e}") 