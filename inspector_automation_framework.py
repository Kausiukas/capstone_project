"""
Inspector Automation Framework
Task 4.1.1: Inspector Automation Framework

This module provides comprehensive automation capabilities for the Inspector system,
including test automation, scheduled testing, automated reporting, and notification systems.
"""

import asyncio
import json
import logging
import os
import smtplib
import subprocess
import sys
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from inspector_config_manager import InspectorConfigManager


class AutomationStatus(Enum):
    """Automation execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(Enum):
    """Types of notifications."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class AutomationJob:
    """Represents an automation job."""
    job_id: str
    name: str
    description: str
    command: str
    schedule: Optional[str] = None
    dependencies: List[str] = None
    timeout: int = 300
    retry_count: int = 3
    retry_delay: int = 60
    notifications: List[str] = None
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: AutomationStatus = AutomationStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.notifications is None:
            self.notifications = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AutomationResult:
    """Result of an automation job execution."""
    job_id: str
    execution_id: str
    start_time: datetime
    end_time: datetime
    status: AutomationStatus
    exit_code: int
    output: str
    error_output: str
    duration: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class NotificationConfig:
    """Configuration for notifications."""
    type: NotificationType
    enabled: bool = True
    recipients: List[str] = None
    template: str = None
    webhook_url: Optional[str] = None
    slack_token: Optional[str] = None
    slack_channel: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []


class InspectorAutomationFramework:
    """
    Comprehensive automation framework for Inspector system.
    
    Provides test automation, scheduled testing, automated reporting,
    and notification system capabilities.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        """Initialize the automation framework."""
        self.config_manager = config_manager
        self.jobs: Dict[str, AutomationJob] = {}
        self.results: Dict[str, List[AutomationResult]] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        
        # Setup directories
        self.data_dir = Path("data/automation")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Load existing jobs and results
        self._load_jobs()
        self._load_results()
        self._load_notification_configs()
    
    def create_job(self, name: str, description: str, command: str, 
                   schedule: Optional[str] = None, dependencies: List[str] = None,
                   timeout: int = 300, retry_count: int = 3, 
                   notifications: List[str] = None) -> str:
        """
        Create a new automation job.
        
        Args:
            name: Job name
            description: Job description
            command: Command to execute
            schedule: Cron-like schedule string (optional)
            dependencies: List of job IDs this job depends on
            timeout: Job timeout in seconds
            retry_count: Number of retries on failure
            notifications: List of notification config names
            
        Returns:
            Job ID
        """
        job_id = f"job_{int(time.time())}_{name.lower().replace(' ', '_')}"
        
        job = AutomationJob(
            job_id=job_id,
            name=name,
            description=description,
            command=command,
            schedule=schedule,
            dependencies=dependencies or [],
            timeout=timeout,
            retry_count=retry_count,
            notifications=notifications or []
        )
        
        self.jobs[job_id] = job
        self._save_jobs()
        
        self.logger.info(f"Created automation job: {job_id} - {name}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[AutomationJob]:
        """Get a job by ID."""
        return self.jobs.get(job_id)
    
    def list_jobs(self, status: Optional[AutomationStatus] = None) -> List[AutomationJob]:
        """List all jobs, optionally filtered by status."""
        if status is None:
            return list(self.jobs.values())
        return [job for job in self.jobs.values() if job.status == status]
    
    def update_job(self, job_id: str, **kwargs) -> bool:
        """Update job properties."""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        self._save_jobs()
        self.logger.info(f"Updated automation job: {job_id}")
        return True
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id not in self.jobs:
            return False
        
        # Cancel if running
        if job_id in self.running_jobs:
            self.running_jobs[job_id].cancel()
            del self.running_jobs[job_id]
        
        del self.jobs[job_id]
        self._save_jobs()
        self.logger.info(f"Deleted automation job: {job_id}")
        return True
    
    async def run_job(self, job_id: str, wait: bool = True) -> Optional[AutomationResult]:
        """
        Run a job immediately.
        
        Args:
            job_id: Job ID to run
            wait: Whether to wait for completion
            
        Returns:
            AutomationResult if wait=True, None otherwise
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self.jobs[job_id]
        
        # Check dependencies
        if not await self._check_dependencies(job):
            raise ValueError(f"Job dependencies not met: {job_id}")
        
        # Check if already running
        if job_id in self.running_jobs:
            raise ValueError(f"Job already running: {job_id}")
        
        # Create execution task
        task = asyncio.create_task(self._execute_job(job))
        self.running_jobs[job_id] = task
        
        if wait:
            try:
                result = await task
                return result
            finally:
                if job_id in self.running_jobs:
                    del self.running_jobs[job_id]
        else:
            return None
    
    async def run_jobs_batch(self, job_ids: List[str], 
                           parallel: bool = True) -> List[AutomationResult]:
        """
        Run multiple jobs in batch.
        
        Args:
            job_ids: List of job IDs to run
            parallel: Whether to run jobs in parallel
            
        Returns:
            List of AutomationResult objects
        """
        if parallel:
            # For parallel execution, we need to wait for all jobs to complete
            tasks = [self.run_job(job_id, wait=True) for job_id in job_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if isinstance(r, AutomationResult)]
        else:
            results = []
            for job_id in job_ids:
                try:
                    result = await self.run_job(job_id, wait=True)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error running job {job_id}: {e}")
            return results
    
    def schedule_job(self, job_id: str, schedule: str) -> bool:
        """Schedule a job to run periodically."""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.schedule = schedule
        job.next_run = self._calculate_next_run(schedule)
        job.status = AutomationStatus.PENDING
        
        self._save_jobs()
        self.logger.info(f"Scheduled job {job_id} with schedule: {schedule}")
        return True
    
    def unschedule_job(self, job_id: str) -> bool:
        """Remove scheduling from a job."""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.schedule = None
        job.next_run = None
        job.status = AutomationStatus.PENDING
        
        self._save_jobs()
        self.logger.info(f"Unscheduled job {job_id}")
        return True
    
    async def run_scheduled_jobs(self) -> List[AutomationResult]:
        """Run all jobs that are due according to their schedule."""
        now = datetime.now()
        due_jobs = []
        
        for job in self.jobs.values():
            if (job.schedule and job.next_run and 
                job.next_run <= now and 
                job.status != AutomationStatus.RUNNING):
                due_jobs.append(job.job_id)
        
        if due_jobs:
            self.logger.info(f"Running {len(due_jobs)} scheduled jobs")
            return await self.run_jobs_batch(due_jobs, parallel=True)
        
        return []
    
    def get_job_results(self, job_id: str, limit: int = 10) -> List[AutomationResult]:
        """Get recent results for a job."""
        if job_id not in self.results:
            return []
        
        results = self.results[job_id]
        return sorted(results, key=lambda r: r.start_time, reverse=True)[:limit]
    
    def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get statistics for a job."""
        if job_id not in self.results:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "average_duration": 0,
                "last_run": None
            }
        
        results = self.results[job_id]
        if not results:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "average_duration": 0,
                "last_run": None
            }
        
        successful_runs = sum(1 for r in results if r.status == AutomationStatus.COMPLETED)
        failed_runs = sum(1 for r in results if r.status == AutomationStatus.FAILED)
        total_duration = sum(r.duration for r in results)
        
        return {
            "total_runs": len(results),
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": (successful_runs / len(results)) * 100 if results else 0,
            "average_duration": total_duration / len(results) if results else 0,
            "last_run": results[0].start_time if results else None
        }
    
    def add_notification_config(self, name: str, config: NotificationConfig) -> None:
        """Add a notification configuration."""
        self.notification_configs[name] = config
        self._save_notification_configs()
        self.logger.info(f"Added notification config: {name}")
    
    def remove_notification_config(self, name: str) -> bool:
        """Remove a notification configuration."""
        if name not in self.notification_configs:
            return False
        
        del self.notification_configs[name]
        self._save_notification_configs()
        self.logger.info(f"Removed notification config: {name}")
        return True
    
    async def send_notification(self, config_name: str, subject: str, 
                              message: str, job_result: Optional[AutomationResult] = None) -> bool:
        """Send a notification using the specified configuration."""
        if config_name not in self.notification_configs:
            self.logger.error(f"Notification config not found: {config_name}")
            return False
        
        config = self.notification_configs[config_name]
        if not config.enabled:
            return True
        
        try:
            if config.type == NotificationType.EMAIL:
                return await self._send_email_notification(config, subject, message, job_result)
            elif config.type == NotificationType.SLACK:
                return await self._send_slack_notification(config, subject, message, job_result)
            elif config.type == NotificationType.WEBHOOK:
                return await self._send_webhook_notification(config, subject, message, job_result)
            elif config.type == NotificationType.CONSOLE:
                return self._send_console_notification(config, subject, message, job_result)
            else:
                self.logger.error(f"Unsupported notification type: {config.type}")
                return False
        except Exception as e:
            self.logger.error(f"Error sending notification {config_name}: {e}")
            return False
    
    async def _execute_job(self, job: AutomationJob) -> AutomationResult:
        """Execute a job and return the result."""
        execution_id = f"exec_{int(time.time())}_{job.job_id}"
        start_time = datetime.now()
        
        # Update job status
        job.status = AutomationStatus.RUNNING
        job.last_run = start_time
        self._save_jobs()
        
        self.logger.info(f"Starting job execution: {execution_id} - {job.name}")
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                job.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=job.timeout
                )
                exit_code = process.returncode
                output = stdout.decode('utf-8', errors='ignore')
                error_output = stderr.decode('utf-8', errors='ignore')
                
            except asyncio.TimeoutError:
                process.kill()
                exit_code = -1
                output = ""
                error_output = f"Job timed out after {job.timeout} seconds"
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Determine status
            if exit_code == 0:
                status = AutomationStatus.COMPLETED
            else:
                status = AutomationStatus.FAILED
            
            # Create result
            result = AutomationResult(
                job_id=job.job_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status=status,
                exit_code=exit_code,
                output=output,
                error_output=error_output,
                duration=duration,
                metadata={
                    "command": job.command,
                    "timeout": job.timeout,
                    "retry_count": job.retry_count
                }
            )
            
            # Store result
            if job.job_id not in self.results:
                self.results[job.job_id] = []
            self.results[job.job_id].append(result)
            self._save_results()
            
            # Update job status
            job.status = status
            job.result = asdict(result)
            if job.schedule:
                job.next_run = self._calculate_next_run(job.schedule)
            self._save_jobs()
            
            # Send notifications
            await self._send_job_notifications(job, result)
            
            self.logger.info(f"Completed job execution: {execution_id} - Status: {status.value}")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = AutomationResult(
                job_id=job.job_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status=AutomationStatus.FAILED,
                exit_code=-1,
                output="",
                error_output=str(e),
                duration=duration
            )
            
            # Store result
            if job.job_id not in self.results:
                self.results[job.job_id] = []
            self.results[job.job_id].append(result)
            self._save_results()
            
            # Update job status
            job.status = AutomationStatus.FAILED
            job.result = asdict(result)
            job.error_message = str(e)
            self._save_jobs()
            
            self.logger.error(f"Failed job execution: {execution_id} - Error: {e}")
            return result
    
    async def _check_dependencies(self, job: AutomationJob) -> bool:
        """Check if job dependencies are met."""
        for dep_id in job.dependencies:
            if dep_id not in self.jobs:
                return False
            
            dep_job = self.jobs[dep_id]
            if not dep_job.result or dep_job.result.get('status') != AutomationStatus.COMPLETED.value:
                return False
        
        return True
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time based on schedule."""
        # Simple schedule parsing for now (can be enhanced with cron-like parsing)
        # Format: "every X minutes/hours/days"
        now = datetime.now()
        
        if schedule.startswith("every "):
            parts = schedule.split()
            if len(parts) >= 3:
                try:
                    amount = int(parts[1])
                    unit = parts[2].lower()
                    
                    if unit.startswith("minute"):
                        return now + timedelta(minutes=amount)
                    elif unit.startswith("hour"):
                        return now + timedelta(hours=amount)
                    elif unit.startswith("day"):
                        return now + timedelta(days=amount)
                except ValueError:
                    pass
        
        # Default: run in 1 hour
        return now + timedelta(hours=1)
    
    async def _send_job_notifications(self, job: AutomationJob, result: AutomationResult) -> None:
        """Send notifications for job completion."""
        for config_name in job.notifications:
            if result.status == AutomationStatus.COMPLETED:
                subject = f"Job Completed: {job.name}"
                message = f"Job {job.name} completed successfully in {result.duration:.2f} seconds."
            else:
                subject = f"Job Failed: {job.name}"
                message = f"Job {job.name} failed with exit code {result.exit_code}."
                if result.error_output:
                    message += f"\nError: {result.error_output}"
            
            await self.send_notification(config_name, subject, message, result)
    
    async def _send_email_notification(self, config: NotificationConfig, subject: str, 
                                     message: str, job_result: Optional[AutomationResult] = None) -> bool:
        """Send email notification."""
        if not all([config.email_smtp_server, config.email_username, config.email_password]):
            self.logger.error("Email notification config incomplete")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config.email_username
            msg['To'] = ', '.join(config.recipients)
            msg['Subject'] = subject
            
            body = message
            if job_result:
                body += f"\n\nJob Details:\n"
                body += f"Execution ID: {job_result.execution_id}\n"
                body += f"Duration: {job_result.duration:.2f} seconds\n"
                body += f"Exit Code: {job_result.exit_code}\n"
                if job_result.error_output:
                    body += f"Error: {job_result.error_output}\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config.email_smtp_server, config.email_smtp_port)
            server.starttls()
            server.login(config.email_username, config.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            self.logger.error(f"Email notification failed: {e}")
            return False
    
    async def _send_slack_notification(self, config: NotificationConfig, subject: str, 
                                     message: str, job_result: Optional[AutomationResult] = None) -> bool:
        """Send Slack notification."""
        # This would require the slack-sdk package
        # For now, just log the notification
        self.logger.info(f"Slack notification (not implemented): {subject} - {message}")
        return True
    
    async def _send_webhook_notification(self, config: NotificationConfig, subject: str, 
                                       message: str, job_result: Optional[AutomationResult] = None) -> bool:
        """Send webhook notification."""
        if not config.webhook_url:
            self.logger.error("Webhook URL not configured")
            return False
        
        try:
            import aiohttp
            
            payload = {
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if job_result:
                payload["job_result"] = asdict(job_result)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(config.webhook_url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
            return False
    
    def _send_console_notification(self, config: NotificationConfig, subject: str, 
                                 message: str, job_result: Optional[AutomationResult] = None) -> bool:
        """Send console notification."""
        print(f"\n{'='*50}")
        print(f"NOTIFICATION: {subject}")
        print(f"{'='*50}")
        print(message)
        if job_result:
            print(f"\nJob Details:")
            print(f"  Execution ID: {job_result.execution_id}")
            print(f"  Duration: {job_result.duration:.2f} seconds")
            print(f"  Exit Code: {job_result.exit_code}")
            if job_result.error_output:
                print(f"  Error: {job_result.error_output}")
        print(f"{'='*50}\n")
        return True
    
    def _save_jobs(self) -> None:
        """Save jobs to file."""
        jobs_file = self.data_dir / "jobs.json"
        jobs_data = {}
        
        for job_id, job in self.jobs.items():
            job_dict = asdict(job)
            # Convert enum values to strings for JSON serialization
            job_dict['status'] = job.status.value
            jobs_data[job_id] = job_dict
        
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, default=str)
    
    def _load_jobs(self) -> None:
        """Load jobs from file."""
        jobs_file = self.data_dir / "jobs.json"
        if not jobs_file.exists():
            return
        
        try:
            with open(jobs_file, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            for job_id, job_dict in jobs_data.items():
                # Convert string dates back to datetime
                if 'created_at' in job_dict and job_dict['created_at']:
                    job_dict['created_at'] = datetime.fromisoformat(job_dict['created_at'])
                if 'last_run' in job_dict and job_dict['last_run']:
                    job_dict['last_run'] = datetime.fromisoformat(job_dict['last_run'])
                if 'next_run' in job_dict and job_dict['next_run']:
                    job_dict['next_run'] = datetime.fromisoformat(job_dict['next_run'])
                
                # Convert status string back to enum
                if 'status' in job_dict:
                    job_dict['status'] = AutomationStatus(job_dict['status'])
                
                self.jobs[job_id] = AutomationJob(**job_dict)
        except Exception as e:
            self.logger.error(f"Error loading jobs: {e}")
    
    def _save_results(self) -> None:
        """Save results to file."""
        results_file = self.data_dir / "results.json"
        results_data = {}
        
        for job_id, job_results in self.results.items():
            results_data[job_id] = []
            for result in job_results:
                result_dict = asdict(result)
                # Convert enum values to strings for JSON serialization
                result_dict['status'] = result.status.value
                results_data[job_id].append(result_dict)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, default=str)
    
    def _load_results(self) -> None:
        """Load results from file."""
        results_file = self.data_dir / "results.json"
        if not results_file.exists():
            return
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results_data = json.load(f)
            
            for job_id, job_results in results_data.items():
                self.results[job_id] = []
                for result_dict in job_results:
                    # Convert string dates back to datetime
                    if 'start_time' in result_dict:
                        result_dict['start_time'] = datetime.fromisoformat(result_dict['start_time'])
                    if 'end_time' in result_dict:
                        result_dict['end_time'] = datetime.fromisoformat(result_dict['end_time'])
                    
                    # Convert status string back to enum
                    if 'status' in result_dict:
                        result_dict['status'] = AutomationStatus(result_dict['status'])
                    
                    self.results[job_id].append(AutomationResult(**result_dict))
        except Exception as e:
            self.logger.error(f"Error loading results: {e}")
    
    def _save_notification_configs(self) -> None:
        """Save notification configurations to file."""
        configs_file = self.data_dir / "notification_configs.json"
        configs_data = {}
        
        for name, config in self.notification_configs.items():
            config_dict = asdict(config)
            # Convert enum values to strings for JSON serialization
            config_dict['type'] = config.type.value
            configs_data[name] = config_dict
        
        with open(configs_file, 'w', encoding='utf-8') as f:
            json.dump(configs_data, f, indent=2, default=str)
    
    def _load_notification_configs(self) -> None:
        """Load notification configurations from file."""
        configs_file = self.data_dir / "notification_configs.json"
        if not configs_file.exists():
            return
        
        try:
            with open(configs_file, 'r', encoding='utf-8') as f:
                configs_data = json.load(f)
            
            for name, config_dict in configs_data.items():
                # Convert type string back to enum
                if 'type' in config_dict:
                    config_dict['type'] = NotificationType(config_dict['type'])
                
                self.notification_configs[name] = NotificationConfig(**config_dict)
        except Exception as e:
            self.logger.error(f"Error loading notification configs: {e}")
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get overall framework status."""
        total_jobs = len(self.jobs)
        running_jobs = len(self.running_jobs)
        scheduled_jobs = sum(1 for job in self.jobs.values() if job.schedule)
        
        total_results = sum(len(results) for results in self.results.values())
        successful_results = sum(
            sum(1 for result in results if result.status == AutomationStatus.COMPLETED)
            for results in self.results.values()
        )
        
        return {
            "total_jobs": total_jobs,
            "running_jobs": running_jobs,
            "scheduled_jobs": scheduled_jobs,
            "total_executions": total_results,
            "successful_executions": successful_results,
            "success_rate": (successful_results / total_results * 100) if total_results > 0 else 0,
            "notification_configs": len(self.notification_configs)
        } 