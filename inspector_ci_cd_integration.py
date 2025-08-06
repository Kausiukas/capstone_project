"""
Inspector CI/CD Integration
Task 4.1.3: Inspector CI/CD Integration

This module provides CI/CD pipeline integration for the Inspector automation framework,
including automated testing, deployment validation, and rollback testing capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

from inspector_config_manager import InspectorConfigManager
from inspector_automation_framework import InspectorAutomationFramework, AutomationJob, AutomationStatus


class PipelineType(Enum):
    """Types of CI/CD pipelines."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"
    CUSTOM = "custom"


class DeploymentStage(Enum):
    """Deployment stages."""
    BUILD = "build"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
    ROLLBACK = "rollback"


class ValidationStatus(Enum):
    """Validation status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineConfig:
    """Configuration for a CI/CD pipeline."""
    pipeline_id: str
    name: str
    description: str
    pipeline_type: PipelineType
    config_file: str  # Path to pipeline configuration file
    repository_url: str
    branch: str = "main"
    triggers: List[str] = None  # List of trigger events
    environment_vars: Dict[str, str] = None
    timeout: int = 3600  # 1 hour
    max_retries: int = 3
    enabled: bool = True
    created_at: datetime = None
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = ["push", "pull_request"]
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class DeploymentConfig:
    """Configuration for deployment validation."""
    deployment_id: str
    name: str
    description: str
    target_environment: str
    deployment_script: str
    validation_scripts: List[str] = None
    rollback_script: str = None
    health_check_url: Optional[str] = None
    health_check_timeout: int = 300  # 5 minutes
    deployment_timeout: int = 1800  # 30 minutes
    auto_rollback: bool = True
    rollback_threshold: int = 3  # Number of failed validations before rollback
    created_at: datetime = None
    last_deployment: Optional[datetime] = None
    last_status: Optional[str] = None
    
    def __post_init__(self):
        if self.validation_scripts is None:
            self.validation_scripts = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_id: str
    deployment_id: str
    validation_name: str
    status: ValidationStatus
    start_time: datetime
    end_time: datetime
    duration: float
    output: str
    error_output: str
    exit_code: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DeploymentResult:
    """Result of a deployment."""
    deployment_id: str
    deployment_config: DeploymentConfig
    start_time: datetime
    end_time: datetime
    status: str
    validation_results: List[ValidationResult]
    rollback_triggered: bool = False
    rollback_successful: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class InspectorCICDIntegration:
    """
    CI/CD pipeline integration for Inspector automation framework.
    
    Provides automated testing, deployment validation, and rollback testing capabilities.
    """
    
    def __init__(self, config_manager: InspectorConfigManager, 
                 automation_framework: InspectorAutomationFramework):
        """Initialize the CI/CD integration."""
        self.config_manager = config_manager
        self.automation_framework = automation_framework
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        self.deployment_results: Dict[str, List[DeploymentResult]] = {}
        self.validation_results: Dict[str, List[ValidationResult]] = {}
        self.running_deployments: Dict[str, asyncio.Task] = {}
        
        # Setup directories
        self.data_dir = Path("data/cicd")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Load existing configurations
        self._load_pipelines()
        self._load_deployments()
        self._load_results()
    
    def create_pipeline(self, name: str, description: str, pipeline_type: PipelineType,
                       config_file: str, repository_url: str, branch: str = "main",
                       triggers: List[str] = None, environment_vars: Dict[str, str] = None,
                       timeout: int = 3600, max_retries: int = 3) -> str:
        """
        Create a new CI/CD pipeline configuration.
        
        Args:
            name: Pipeline name
            description: Pipeline description
            pipeline_type: Type of pipeline
            config_file: Path to pipeline configuration file
            repository_url: Git repository URL
            branch: Branch to monitor
            triggers: List of trigger events
            environment_vars: Environment variables
            timeout: Pipeline timeout in seconds
            max_retries: Maximum number of retries
            
        Returns:
            Pipeline ID
        """
        pipeline_id = f"pipeline_{int(time.time())}_{name.lower().replace(' ', '_')}"
        
        pipeline_config = PipelineConfig(
            pipeline_id=pipeline_id,
            name=name,
            description=description,
            pipeline_type=pipeline_type,
            config_file=config_file,
            repository_url=repository_url,
            branch=branch,
            triggers=triggers or ["push", "pull_request"],
            environment_vars=environment_vars or {},
            timeout=timeout,
            max_retries=max_retries
        )
        
        self.pipelines[pipeline_id] = pipeline_config
        self._save_pipelines()
        
        self.logger.info(f"Created pipeline: {pipeline_id} - {name}")
        return pipeline_id
    
    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineConfig]:
        """Get a pipeline by ID."""
        return self.pipelines.get(pipeline_id)
    
    def list_pipelines(self, enabled_only: bool = False) -> List[PipelineConfig]:
        """List all pipelines, optionally filtered by enabled status."""
        if enabled_only:
            return [pipeline for pipeline in self.pipelines.values() if pipeline.enabled]
        return list(self.pipelines.values())
    
    def update_pipeline(self, pipeline_id: str, **kwargs) -> bool:
        """Update pipeline properties."""
        if pipeline_id not in self.pipelines:
            return False
        
        pipeline = self.pipelines[pipeline_id]
        for key, value in kwargs.items():
            if hasattr(pipeline, key):
                setattr(pipeline, key, value)
        
        self._save_pipelines()
        self.logger.info(f"Updated pipeline: {pipeline_id}")
        return True
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        if pipeline_id not in self.pipelines:
            return False
        
        del self.pipelines[pipeline_id]
        self._save_pipelines()
        self.logger.info(f"Deleted pipeline: {pipeline_id}")
        return True
    
    def create_deployment(self, name: str, description: str, target_environment: str,
                         deployment_script: str, validation_scripts: List[str] = None,
                         rollback_script: str = None, health_check_url: Optional[str] = None,
                         health_check_timeout: int = 300, deployment_timeout: int = 1800,
                         auto_rollback: bool = True, rollback_threshold: int = 3) -> str:
        """
        Create a new deployment configuration.
        
        Args:
            name: Deployment name
            description: Deployment description
            target_environment: Target environment (staging, production, etc.)
            deployment_script: Path to deployment script
            validation_scripts: List of validation script paths
            rollback_script: Path to rollback script
            health_check_url: URL for health checks
            health_check_timeout: Health check timeout in seconds
            deployment_timeout: Deployment timeout in seconds
            auto_rollback: Whether to automatically rollback on failure
            rollback_threshold: Number of failed validations before rollback
            
        Returns:
            Deployment ID
        """
        deployment_id = f"deployment_{int(time.time())}_{name.lower().replace(' ', '_')}"
        
        deployment_config = DeploymentConfig(
            deployment_id=deployment_id,
            name=name,
            description=description,
            target_environment=target_environment,
            deployment_script=deployment_script,
            validation_scripts=validation_scripts or [],
            rollback_script=rollback_script,
            health_check_url=health_check_url,
            health_check_timeout=health_check_timeout,
            deployment_timeout=deployment_timeout,
            auto_rollback=auto_rollback,
            rollback_threshold=rollback_threshold
        )
        
        self.deployments[deployment_id] = deployment_config
        self._save_deployments()
        
        self.logger.info(f"Created deployment: {deployment_id} - {name}")
        return deployment_id
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentConfig]:
        """Get a deployment by ID."""
        return self.deployments.get(deployment_id)
    
    def list_deployments(self, environment: Optional[str] = None) -> List[DeploymentConfig]:
        """List all deployments, optionally filtered by environment."""
        if environment:
            return [deployment for deployment in self.deployments.values() 
                   if deployment.target_environment == environment]
        return list(self.deployments.values())
    
    def update_deployment(self, deployment_id: str, **kwargs) -> bool:
        """Update deployment properties."""
        if deployment_id not in self.deployments:
            return False
        
        deployment = self.deployments[deployment_id]
        for key, value in kwargs.items():
            if hasattr(deployment, key):
                setattr(deployment, key, value)
        
        self._save_deployments()
        self.logger.info(f"Updated deployment: {deployment_id}")
        return True
    
    def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment."""
        if deployment_id not in self.deployments:
            return False
        
        del self.deployments[deployment_id]
        self._save_deployments()
        self.logger.info(f"Deleted deployment: {deployment_id}")
        return True
    
    async def trigger_pipeline(self, pipeline_id: str, trigger_event: str = "manual",
                             commit_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger a pipeline execution.
        
        Args:
            pipeline_id: Pipeline ID to trigger
            trigger_event: Event that triggered the pipeline
            commit_hash: Git commit hash (optional)
            
        Returns:
            Pipeline execution result
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        pipeline = self.pipelines[pipeline_id]
        
        # Create automation job for pipeline execution
        job_name = f"Pipeline: {pipeline.name}"
        job_description = f"Execute {pipeline.pipeline_type.value} pipeline"
        
        # Build command based on pipeline type
        command = self._build_pipeline_command(pipeline, trigger_event, commit_hash)
        
        # Create job
        job_id = self.automation_framework.create_job(
            name=job_name,
            description=job_description,
            command=command,
            timeout=pipeline.timeout
        )
        
        # Execute job
        result = await self.automation_framework.run_job(job_id, wait=True)
        
        # Update pipeline status
        pipeline.last_run = datetime.now()
        pipeline.last_status = result.status.value if result else "unknown"
        self._save_pipelines()
        
        return {
            "pipeline_id": pipeline_id,
            "job_id": job_id,
            "trigger_event": trigger_event,
            "commit_hash": commit_hash,
            "status": result.status.value if result else "unknown",
            "duration": result.duration if result else 0,
            "output": result.output if result else "",
            "error_output": result.error_output if result else ""
        }
    
    async def execute_deployment(self, deployment_id: str, wait: bool = True) -> Optional[DeploymentResult]:
        """
        Execute a deployment with validation and rollback capabilities.
        
        Args:
            deployment_id: Deployment ID to execute
            wait: Whether to wait for completion
            
        Returns:
            DeploymentResult if wait=True, None otherwise
        """
        if deployment_id not in self.deployments:
            raise ValueError(f"Deployment not found: {deployment_id}")
        
        deployment = self.deployments[deployment_id]
        
        # Check if already running
        if deployment_id in self.running_deployments:
            raise ValueError(f"Deployment already running: {deployment_id}")
        
        # Create execution task
        task = asyncio.create_task(self._execute_deployment(deployment))
        self.running_deployments[deployment_id] = task
        
        if wait:
            try:
                result = await task
                return result
            finally:
                if deployment_id in self.running_deployments:
                    del self.running_deployments[deployment_id]
        else:
            return None
    
    async def rollback_deployment(self, deployment_id: str) -> bool:
        """
        Rollback a deployment.
        
        Args:
            deployment_id: Deployment ID to rollback
            
        Returns:
            True if rollback was successful
        """
        if deployment_id not in self.deployments:
            raise ValueError(f"Deployment not found: {deployment_id}")
        
        deployment = self.deployments[deployment_id]
        
        if not deployment.rollback_script:
            self.logger.error(f"No rollback script configured for deployment: {deployment_id}")
            return False
        
        try:
            # Execute rollback script
            process = await asyncio.create_subprocess_shell(
                deployment.rollback_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=deployment.deployment_timeout
            )
            
            success = process.returncode == 0
            
            if success:
                self.logger.info(f"Rollback successful for deployment: {deployment_id}")
            else:
                self.logger.error(f"Rollback failed for deployment: {deployment_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during rollback for deployment {deployment_id}: {e}")
            return False
    
    def get_deployment_history(self, deployment_id: str, limit: int = 10) -> List[DeploymentResult]:
        """Get deployment history."""
        if deployment_id not in self.deployment_results:
            return []
        
        results = self.deployment_results[deployment_id]
        return sorted(results, key=lambda r: r.start_time, reverse=True)[:limit]
    
    def get_validation_history(self, deployment_id: str, limit: int = 10) -> List[ValidationResult]:
        """Get validation history for a deployment."""
        if deployment_id not in self.validation_results:
            return []
        
        results = self.validation_results[deployment_id]
        return sorted(results, key=lambda r: r.start_time, reverse=True)[:limit]
    
    def get_cicd_status(self) -> Dict[str, Any]:
        """Get overall CI/CD integration status."""
        total_pipelines = len(self.pipelines)
        enabled_pipelines = sum(1 for p in self.pipelines.values() if p.enabled)
        total_deployments = len(self.deployments)
        running_deployments = len(self.running_deployments)
        
        # Calculate success rates
        pipeline_successes = sum(1 for p in self.pipelines.values() 
                               if p.last_status == "completed")
        deployment_successes = 0
        
        for deployment_results in self.deployment_results.values():
            if deployment_results:
                latest = max(deployment_results, key=lambda r: r.start_time)
                if latest.status == "success":
                    deployment_successes += 1
        
        return {
            "total_pipelines": total_pipelines,
            "enabled_pipelines": enabled_pipelines,
            "pipeline_success_rate": (pipeline_successes / total_pipelines * 100) if total_pipelines > 0 else 0,
            "total_deployments": total_deployments,
            "running_deployments": running_deployments,
            "deployment_success_rate": (deployment_successes / total_deployments * 100) if total_deployments > 0 else 0
        }
    
    def _build_pipeline_command(self, pipeline: PipelineConfig, trigger_event: str,
                               commit_hash: Optional[str] = None) -> str:
        """Build command for pipeline execution based on type."""
        env_vars = " ".join([f"{k}={v}" for k, v in pipeline.environment_vars.items()])
        
        if pipeline.pipeline_type == PipelineType.GITHUB_ACTIONS:
            # Use GitHub CLI or act for local execution
            return f"{env_vars} act -W {pipeline.config_file} --eventpath /tmp/event.json"
        
        elif pipeline.pipeline_type == PipelineType.GITLAB_CI:
            # Use GitLab Runner
            return f"{env_vars} gitlab-runner exec docker --config {pipeline.config_file}"
        
        elif pipeline.pipeline_type == PipelineType.JENKINS:
            # Use Jenkins CLI
            return f"{env_vars} jenkins-cli build {pipeline.name}"
        
        elif pipeline.pipeline_type == PipelineType.AZURE_DEVOPS:
            # Use Azure DevOps CLI
            return f"{env_vars} az pipelines run --name {pipeline.name}"
        
        else:  # CUSTOM
            # Execute custom script
            return f"{env_vars} {pipeline.config_file}"
    
    async def _execute_deployment(self, deployment: DeploymentConfig) -> DeploymentResult:
        """Execute a deployment with validation and rollback."""
        start_time = datetime.now()
        validation_results = []
        rollback_triggered = False
        rollback_successful = False
        error_message = None
        
        try:
            self.logger.info(f"Starting deployment: {deployment.deployment_id} - {deployment.name}")
            
            # Step 1: Execute deployment script
            deployment_success = await self._execute_script(
                deployment.deployment_script,
                f"Deployment script for {deployment.name}",
                deployment.deployment_timeout
            )
            
            if not deployment_success:
                raise Exception("Deployment script failed")
            
            # Step 2: Run validation scripts
            failed_validations = 0
            for i, validation_script in enumerate(deployment.validation_scripts):
                validation_id = f"validation_{deployment.deployment_id}_{i}"
                
                validation_result = await self._execute_validation(
                    validation_id, deployment.deployment_id, validation_script,
                    f"Validation {i+1} for {deployment.name}"
                )
                
                validation_results.append(validation_result)
                
                if validation_result.status == ValidationStatus.FAILED:
                    failed_validations += 1
                
                # Check if we should trigger rollback
                if (deployment.auto_rollback and 
                    failed_validations >= deployment.rollback_threshold):
                    self.logger.warning(f"Rollback threshold reached for deployment: {deployment.deployment_id}")
                    rollback_triggered = True
                    break
            
            # Step 3: Health check if configured
            if deployment.health_check_url and not rollback_triggered:
                health_check_result = await self._execute_health_check(
                    deployment.deployment_id, deployment.health_check_url,
                    deployment.health_check_timeout
                )
                validation_results.append(health_check_result)
                
                if health_check_result.status == ValidationStatus.FAILED:
                    failed_validations += 1
                    if deployment.auto_rollback:
                        rollback_triggered = True
            
            # Step 4: Rollback if needed
            if rollback_triggered and deployment.rollback_script:
                self.logger.info(f"Executing rollback for deployment: {deployment.deployment_id}")
                rollback_successful = await self.rollback_deployment(deployment.deployment_id)
            
            # Determine final status
            if rollback_triggered:
                status = "rolled_back" if rollback_successful else "rollback_failed"
            elif failed_validations == 0:
                status = "success"
            else:
                status = "validation_failed"
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create deployment result
            result = DeploymentResult(
                deployment_id=deployment.deployment_id,
                deployment_config=deployment,
                start_time=start_time,
                end_time=end_time,
                status=status,
                validation_results=validation_results,
                rollback_triggered=rollback_triggered,
                rollback_successful=rollback_successful,
                error_message=error_message
            )
            
            # Store results
            if deployment.deployment_id not in self.deployment_results:
                self.deployment_results[deployment.deployment_id] = []
            self.deployment_results[deployment.deployment_id].append(result)
            
            if deployment.deployment_id not in self.validation_results:
                self.validation_results[deployment.deployment_id] = []
            self.validation_results[deployment.deployment_id].extend(validation_results)
            
            # Update deployment status
            deployment.last_deployment = datetime.now()
            deployment.last_status = status
            self._save_deployments()
            self._save_results()
            
            self.logger.info(f"Completed deployment: {deployment.deployment_id} - Status: {status}")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_message = str(e)
            
            # Create failed deployment result
            result = DeploymentResult(
                deployment_id=deployment.deployment_id,
                deployment_config=deployment,
                start_time=start_time,
                end_time=end_time,
                status="failed",
                validation_results=validation_results,
                rollback_triggered=rollback_triggered,
                rollback_successful=rollback_successful,
                error_message=error_message
            )
            
            # Store results
            if deployment.deployment_id not in self.deployment_results:
                self.deployment_results[deployment.deployment_id] = []
            self.deployment_results[deployment.deployment_id].append(result)
            
            # Update deployment status
            deployment.last_deployment = datetime.now()
            deployment.last_status = "failed"
            self._save_deployments()
            self._save_results()
            
            self.logger.error(f"Deployment failed: {deployment.deployment_id} - Error: {e}")
            return result
    
    async def _execute_script(self, script_path: str, description: str, timeout: int) -> bool:
        """Execute a script and return success status."""
        try:
            process = await asyncio.create_subprocess_shell(
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return process.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error executing script {script_path}: {e}")
            return False
    
    async def _execute_validation(self, validation_id: str, deployment_id: str,
                                validation_script: str, description: str) -> ValidationResult:
        """Execute a validation script."""
        start_time = datetime.now()
        
        try:
            process = await asyncio.create_subprocess_shell(
                validation_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minutes timeout for validations
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            status = ValidationStatus.PASSED if process.returncode == 0 else ValidationStatus.FAILED
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            
            result = ValidationResult(
                validation_id=validation_id,
                deployment_id=deployment_id,
                validation_name=description,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                output=output,
                error_output=error_output,
                exit_code=process.returncode
            )
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ValidationResult(
                validation_id=validation_id,
                deployment_id=deployment_id,
                validation_name=description,
                status=ValidationStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                output="",
                error_output=str(e),
                exit_code=-1
            )
            
            return result
    
    async def _execute_health_check(self, deployment_id: str, health_check_url: str,
                                  timeout: int) -> ValidationResult:
        """Execute a health check."""
        start_time = datetime.now()
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_check_url, timeout=timeout) as response:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    status = ValidationStatus.PASSED if response.status == 200 else ValidationStatus.FAILED
                    output = f"HTTP {response.status}"
                    error_output = "" if response.status == 200 else f"Health check failed with status {response.status}"
                    
                    result = ValidationResult(
                        validation_id=f"health_check_{deployment_id}",
                        deployment_id=deployment_id,
                        validation_name="Health Check",
                        status=status,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        output=output,
                        error_output=error_output,
                        exit_code=0 if response.status == 200 else 1
                    )
                    
                    return result
                    
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ValidationResult(
                validation_id=f"health_check_{deployment_id}",
                deployment_id=deployment_id,
                validation_name="Health Check",
                status=ValidationStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                output="",
                error_output=str(e),
                exit_code=-1
            )
            
            return result
    
    def _save_pipelines(self) -> None:
        """Save pipelines to file."""
        pipelines_file = self.data_dir / "pipelines.json"
        pipelines_data = {pipeline_id: asdict(pipeline) for pipeline_id, pipeline in self.pipelines.items()}
        
        with open(pipelines_file, 'w', encoding='utf-8') as f:
            json.dump(pipelines_data, f, indent=2, default=str)
    
    def _load_pipelines(self) -> None:
        """Load pipelines from file."""
        pipelines_file = self.data_dir / "pipelines.json"
        if not pipelines_file.exists():
            return
        
        try:
            with open(pipelines_file, 'r', encoding='utf-8') as f:
                pipelines_data = json.load(f)
            
            for pipeline_id, pipeline_dict in pipelines_data.items():
                # Convert string dates back to datetime
                if 'created_at' in pipeline_dict and pipeline_dict['created_at']:
                    pipeline_dict['created_at'] = datetime.fromisoformat(pipeline_dict['created_at'])
                if 'last_run' in pipeline_dict and pipeline_dict['last_run']:
                    pipeline_dict['last_run'] = datetime.fromisoformat(pipeline_dict['last_run'])
                
                # Convert enum string back to enum
                if 'pipeline_type' in pipeline_dict:
                    pipeline_dict['pipeline_type'] = PipelineType(pipeline_dict['pipeline_type'])
                
                self.pipelines[pipeline_id] = PipelineConfig(**pipeline_dict)
        except Exception as e:
            self.logger.error(f"Error loading pipelines: {e}")
    
    def _save_deployments(self) -> None:
        """Save deployments to file."""
        deployments_file = self.data_dir / "deployments.json"
        deployments_data = {deployment_id: asdict(deployment) for deployment_id, deployment in self.deployments.items()}
        
        with open(deployments_file, 'w', encoding='utf-8') as f:
            json.dump(deployments_data, f, indent=2, default=str)
    
    def _load_deployments(self) -> None:
        """Load deployments from file."""
        deployments_file = self.data_dir / "deployments.json"
        if not deployments_file.exists():
            return
        
        try:
            with open(deployments_file, 'r', encoding='utf-8') as f:
                deployments_data = json.load(f)
            
            for deployment_id, deployment_dict in deployments_data.items():
                # Convert string dates back to datetime
                if 'created_at' in deployment_dict and deployment_dict['created_at']:
                    deployment_dict['created_at'] = datetime.fromisoformat(deployment_dict['created_at'])
                if 'last_deployment' in deployment_dict and deployment_dict['last_deployment']:
                    deployment_dict['last_deployment'] = datetime.fromisoformat(deployment_dict['last_deployment'])
                
                self.deployments[deployment_id] = DeploymentConfig(**deployment_dict)
        except Exception as e:
            self.logger.error(f"Error loading deployments: {e}")
    
    def _save_results(self) -> None:
        """Save results to file."""
        # Save deployment results
        deployment_results_file = self.data_dir / "deployment_results.json"
        deployment_results_data = {}
        
        for deployment_id, results in self.deployment_results.items():
            deployment_results_data[deployment_id] = []
            for result in results:
                result_dict = asdict(result)
                # Remove the deployment_config object as it's not serializable
                result_dict.pop('deployment_config', None)
                deployment_results_data[deployment_id].append(result_dict)
        
        with open(deployment_results_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_results_data, f, indent=2, default=str)
        
        # Save validation results
        validation_results_file = self.data_dir / "validation_results.json"
        validation_results_data = {}
        
        for deployment_id, results in self.validation_results.items():
            validation_results_data[deployment_id] = [asdict(result) for result in results]
        
        with open(validation_results_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results_data, f, indent=2, default=str)
    
    def _load_results(self) -> None:
        """Load results from file."""
        # Load deployment results
        deployment_results_file = self.data_dir / "deployment_results.json"
        if deployment_results_file.exists():
            try:
                with open(deployment_results_file, 'r', encoding='utf-8') as f:
                    deployment_results_data = json.load(f)
                
                for deployment_id, results_data in deployment_results_data.items():
                    self.deployment_results[deployment_id] = []
                    for result_dict in results_data:
                        # Convert string dates back to datetime
                        if 'start_time' in result_dict:
                            result_dict['start_time'] = datetime.fromisoformat(result_dict['start_time'])
                        if 'end_time' in result_dict:
                            result_dict['end_time'] = datetime.fromisoformat(result_dict['end_time'])
                        
                        # Reconstruct deployment_config object
                        if deployment_id in self.deployments:
                            result_dict['deployment_config'] = self.deployments[deployment_id]
                        
                        self.deployment_results[deployment_id].append(DeploymentResult(**result_dict))
            except Exception as e:
                self.logger.error(f"Error loading deployment results: {e}")
        
        # Load validation results
        validation_results_file = self.data_dir / "validation_results.json"
        if validation_results_file.exists():
            try:
                with open(validation_results_file, 'r', encoding='utf-8') as f:
                    validation_results_data = json.load(f)
                
                for deployment_id, results_data in validation_results_data.items():
                    self.validation_results[deployment_id] = []
                    for result_dict in results_data:
                        # Convert string dates back to datetime
                        if 'start_time' in result_dict:
                            result_dict['start_time'] = datetime.fromisoformat(result_dict['start_time'])
                        if 'end_time' in result_dict:
                            result_dict['end_time'] = datetime.fromisoformat(result_dict['end_time'])
                        
                        # Convert enum string back to enum
                        if 'status' in result_dict:
                            result_dict['status'] = ValidationStatus(result_dict['status'])
                        
                        self.validation_results[deployment_id].append(ValidationResult(**result_dict))
            except Exception as e:
                self.logger.error(f"Error loading validation results: {e}") 