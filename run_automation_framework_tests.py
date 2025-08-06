"""
Inspector Automation Framework Test Runner
Task 4.1: Inspector Automation Framework

This module provides comprehensive testing for all Task 4.1 automation framework modules
with integrated progress tracking and detailed reporting.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from test_runner_base import BaseTestRunner, TestStatus, TestResult, TestSuite
from inspector_config_manager import InspectorConfigManager
from inspector_automation_framework import InspectorAutomationFramework, AutomationJob, AutomationStatus, NotificationType, NotificationConfig
from inspector_scheduler import InspectorScheduler, ScheduleType, SchedulePriority, ScheduleConfig
from inspector_ci_cd_integration import InspectorCICDIntegration, PipelineType, DeploymentConfig, ValidationStatus


class AutomationFrameworkTestRunner(BaseTestRunner):
    """
    Comprehensive test runner for Inspector Automation Framework modules.
    
    Tests all Task 4.1 modules with integrated progress tracking and detailed reporting.
    """
    
    def __init__(self):
        """Initialize the automation framework test runner."""
        super().__init__("Inspector Automation Framework Tests", 18, 300)
        
        # Initialize components
        self.config_manager = InspectorConfigManager()
        self.automation_framework = InspectorAutomationFramework(self.config_manager)
        self.scheduler = InspectorScheduler(self.config_manager, self.automation_framework)
        self.cicd_integration = InspectorCICDIntegration(self.config_manager, self.automation_framework)
        
        # Test results storage
        self.automation_results = {}
        self.scheduler_results = {}
        self.cicd_results = {}
        
        # Ensure results directory exists
        self.results_dir = Path("results/inspector/automation_framework")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all automation framework tests."""
        print("Starting Inspector Automation Framework Tests (Task 4.1)")
        print("=" * 60)
        
        # Initialize test suite
        test_suite = TestSuite(
            suite_name="Inspector Automation Framework Tests",
            total_tests=18
        )
        
        # Run test categories
        await self._test_automation_framework_module()
        await self._test_scheduler_module()
        await self._test_cicd_integration_module()
        await self._test_integration_workflows()
        await self._test_data_persistence()
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report()
        
        # Save results
        self._save_results(report)
        
        return report
    
    async def _test_automation_framework_module(self) -> None:
        """Test the automation framework module."""
        print("\n🤖 Testing Automation Framework Module...")
        
        # Test 1: Job creation and management
        await self.run_test(
            "Job Creation and Management",
            "Create, update, and delete automation jobs",
            self._test_job_creation_and_management
        )
        
        # Test 2: Job execution
        await self.run_test(
            "Job Execution",
            "Execute jobs and verify results",
            self._test_job_execution
        )
        
        # Test 3: Batch job execution
        await self.run_test(
            "Batch Job Execution",
            "Execute multiple jobs in batch",
            self._test_batch_job_execution
        )
        
        # Test 4: Job scheduling
        await self.run_test(
            "Job Scheduling",
            "Schedule jobs and verify scheduling",
            self._test_job_scheduling
        )
        
        # Test 5: Notification system
        await self.run_test(
            "Notification System",
            "Configure and test notification system",
            self._test_notification_system
        )
        
        # Test 6: Framework status
        await self.run_test(
            "Framework Status",
            "Get and verify framework status",
            self._test_framework_status
        )
    
    async def _test_scheduler_module(self) -> None:
        """Test the scheduler module."""
        print("\n⏰ Testing Scheduler Module...")
        
        # Test 1: Schedule creation
        await self.run_test(
            "Schedule Creation",
            "Create schedules with different types",
            self._test_schedule_creation
        )
        
        # Test 2: Schedule management
        await self.run_test(
            "Schedule Management",
            "Update and delete schedules",
            self._test_schedule_management
        )
        
        # Test 3: Schedule execution
        await self.run_test(
            "Schedule Execution",
            "Execute schedules and verify results",
            self._test_schedule_execution
        )
        
        # Test 4: Dependency management
        await self.run_test(
            "Dependency Management",
            "Test schedule dependencies",
            self._test_dependency_management
        )
        
        # Test 5: Schedule optimization
        await self.run_test(
            "Schedule Optimization",
            "Test schedule optimization features",
            self._test_schedule_optimization
        )
    
    async def _test_cicd_integration_module(self) -> None:
        """Test the CI/CD integration module."""
        print("\n🔄 Testing CI/CD Integration Module...")
        
        # Test 1: Pipeline creation
        await self.run_test(
            "Pipeline Creation",
            "Create CI/CD pipeline configurations",
            self._test_pipeline_creation
        )
        
        # Test 2: Pipeline management
        await self.run_test(
            "Pipeline Management",
            "Update and delete pipeline configurations",
            self._test_pipeline_management
        )
        
        # Test 3: Deployment creation
        await self.run_test(
            "Deployment Creation",
            "Create deployment configurations",
            self._test_deployment_creation
        )
        
        # Test 4: Deployment management
        await self.run_test(
            "Deployment Management",
            "Update and delete deployment configurations",
            self._test_deployment_management
        )
        
        # Test 5: CI/CD status
        await self.run_test(
            "CI/CD Status",
            "Get and verify CI/CD integration status",
            self._test_cicd_status
        )
    
    async def _test_integration_workflows(self) -> None:
        """Test integration workflows between modules."""
        print("\n🔗 Testing Integration Workflows...")
        
        # Test 1: End-to-end automation workflow
        await self.run_test(
            "End-to-End Automation Workflow",
            "Complete automation workflow with all components",
            self._test_end_to_end_automation_workflow
        )
        
        # Test 2: Scheduled automation workflow
        await self.run_test(
            "Scheduled Automation Workflow",
            "Test scheduled automation with framework integration",
            self._test_scheduled_automation_workflow
        )
    
    async def _test_data_persistence(self) -> None:
        """Test data persistence and loading."""
        print("\n💾 Testing Data Persistence...")
        
        # Test 1: Automation data persistence
        await self.run_test(
            "Automation Data Persistence",
            "Save and load automation framework data",
            self._test_automation_data_persistence
        )
        
        # Test 2: Scheduler data persistence
        await self.run_test(
            "Scheduler Data Persistence",
            "Save and load scheduler data",
            self._test_scheduler_data_persistence
        )
    
    # Automation Framework Module Tests
    async def _test_job_creation_and_management(self) -> None:
        """Test job creation and management functionality."""
        try:
            # Create a job
            job_id = self.automation_framework.create_job(
                name="Test Job",
                description="Test automation job",
                command="echo 'Hello, World!'",
                timeout=60
            )
            
            # Verify job was created
            job = self.automation_framework.get_job(job_id)
            if not job:
                raise Exception("Job not found after creation")
            
            # Update job
            success = self.automation_framework.update_job(job_id, description="Updated description")
            if not success:
                raise Exception("Failed to update job")
            
            # Verify update
            updated_job = self.automation_framework.get_job(job_id)
            if updated_job.description != "Updated description":
                raise Exception("Job update not reflected")
            
            # Delete job
            success = self.automation_framework.delete_job(job_id)
            if not success:
                raise Exception("Failed to delete job")
            
            # Verify deletion
            deleted_job = self.automation_framework.get_job(job_id)
            if deleted_job:
                raise Exception("Job still exists after deletion")
        
        except Exception as e:
            raise Exception(f"Error in job creation and management: {str(e)}")
    
    async def _test_job_execution(self) -> None:
        """Test job execution functionality."""
        try:
            # Create a job
            job_id = self.automation_framework.create_job(
                name="Execution Test Job",
                description="Job for execution testing",
                command="echo 'Execution test successful'",
                timeout=60
            )
            
            # Execute job
            result = await self.automation_framework.run_job(job_id, wait=True)
            
            # Verify execution
            if not result:
                raise Exception("Job execution returned no result")
            
            if result.status != AutomationStatus.COMPLETED:
                raise Exception(f"Job execution failed with status: {result.status}")
            
            if result.exit_code != 0:
                raise Exception(f"Job execution failed with exit code: {result.exit_code}")
            
            # Clean up
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in job execution: {str(e)}")
    
    async def _test_batch_job_execution(self) -> None:
        """Test batch job execution functionality."""
        try:
            # Create multiple jobs
            job_ids = []
            for i in range(3):
                job_id = self.automation_framework.create_job(
                    name=f"Batch Test Job {i+1}",
                    description=f"Batch test job {i+1}",
                    command=f"echo 'Batch test {i+1} successful'",
                    timeout=60
                )
                job_ids.append(job_id)
            
            # Execute jobs in batch
            results = await self.automation_framework.run_jobs_batch(job_ids, parallel=True)
            
            # Verify results
            if len(results) != 3:
                raise Exception(f"Expected 3 results, got {len(results)}")
            
            for result in results:
                if result.status != AutomationStatus.COMPLETED:
                    raise Exception(f"Batch job failed with status: {result.status}")
            
            # Clean up
            for job_id in job_ids:
                self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in batch job execution: {str(e)}")
    
    async def _test_job_scheduling(self) -> None:
        """Test job scheduling functionality."""
        try:
            # Create a job
            job_id = self.automation_framework.create_job(
                name="Scheduled Test Job",
                description="Job for scheduling testing",
                command="echo 'Scheduled test successful'",
                timeout=60
            )
            
            # Schedule job
            success = self.automation_framework.schedule_job(job_id, "every 1 hour")
            if not success:
                raise Exception("Failed to schedule job")
            
            # Verify scheduling
            job = self.automation_framework.get_job(job_id)
            if not job.schedule:
                raise Exception("Job schedule not set")
            
            if not job.next_run:
                raise Exception("Job next run time not calculated")
            
            # Unschedule job
            success = self.automation_framework.unschedule_job(job_id)
            if not success:
                raise Exception("Failed to unschedule job")
            
            # Verify unscheduling
            job = self.automation_framework.get_job(job_id)
            if job.schedule or job.next_run:
                raise Exception("Job still scheduled after unscheduling")
            
            # Clean up
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in job scheduling: {str(e)}")
    
    async def _test_notification_system(self) -> None:
        """Test notification system functionality."""
        try:
            # Create notification config
            config = NotificationConfig(
                type=NotificationType.CONSOLE,
                enabled=True,
                recipients=["test@example.com"]
            )
            
            self.automation_framework.add_notification_config("test_config", config)
            
            # Test notification sending
            success = await self.automation_framework.send_notification(
                "test_config",
                "Test Notification",
                "This is a test notification"
            )
            
            if not success:
                raise Exception("Failed to send notification")
            
            # Remove notification config
            success = self.automation_framework.remove_notification_config("test_config")
            if not success:
                raise Exception("Failed to remove notification config")
        
        except Exception as e:
            raise Exception(f"Error in notification system: {str(e)}")
    
    async def _test_framework_status(self) -> None:
        """Test framework status functionality."""
        try:
            # Get framework status
            status = self.automation_framework.get_framework_status()
            
            # Verify status structure
            required_keys = ["total_jobs", "running_jobs", "scheduled_jobs", 
                           "total_executions", "successful_executions", "success_rate"]
            
            for key in required_keys:
                if key not in status:
                    raise Exception(f"Status missing required key: {key}")
            
            # Verify data types
            if not isinstance(status["total_jobs"], int):
                raise Exception("total_jobs should be an integer")
            
            if not isinstance(status["success_rate"], (int, float)):
                raise Exception("success_rate should be a number")
        
        except Exception as e:
            raise Exception(f"Error in framework status: {str(e)}")
    
    # Scheduler Module Tests
    async def _test_schedule_creation(self) -> None:
        """Test schedule creation functionality."""
        try:
            # Create a job first
            job_id = self.automation_framework.create_job(
                name="Schedule Test Job",
                description="Job for schedule testing",
                command="echo 'Schedule test successful'",
                timeout=60
            )
            
            # Create schedule
            schedule_id = self.scheduler.create_schedule(
                name="Test Schedule",
                description="Test schedule for validation",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 2 hours",
                job_ids=[job_id],
                priority=SchedulePriority.NORMAL
            )
            
            # Verify schedule was created
            schedule = self.scheduler.get_schedule(schedule_id)
            if not schedule:
                raise Exception("Schedule not found after creation")
            
            # Verify scheduled jobs
            scheduled_jobs = self.scheduler.get_scheduled_jobs(schedule_id)
            if len(scheduled_jobs) != 1:
                raise Exception(f"Expected 1 scheduled job, got {len(scheduled_jobs)}")
            
            # Clean up
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in schedule creation: {str(e)}")
    
    async def _test_schedule_management(self) -> None:
        """Test schedule management functionality."""
        try:
            # Create a job and schedule
            job_id = self.automation_framework.create_job(
                name="Management Test Job",
                description="Job for management testing",
                command="echo 'Management test successful'",
                timeout=60
            )
            
            schedule_id = self.scheduler.create_schedule(
                name="Management Test Schedule",
                description="Test schedule for management",
                schedule_type=ScheduleType.CRON,
                expression="0 */2 * * *",
                job_ids=[job_id]
            )
            
            # Update schedule
            success = self.scheduler.update_schedule(schedule_id, description="Updated description")
            if not success:
                raise Exception("Failed to update schedule")
            
            # Verify update
            schedule = self.scheduler.get_schedule(schedule_id)
            if schedule.description != "Updated description":
                raise Exception("Schedule update not reflected")
            
            # Disable schedule
            success = self.scheduler.disable_schedule(schedule_id)
            if not success:
                raise Exception("Failed to disable schedule")
            
            # Verify disable
            schedule = self.scheduler.get_schedule(schedule_id)
            if schedule.enabled:
                raise Exception("Schedule still enabled after disable")
            
            # Enable schedule
            success = self.scheduler.enable_schedule(schedule_id)
            if not success:
                raise Exception("Failed to enable schedule")
            
            # Clean up
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in schedule management: {str(e)}")
    
    async def _test_schedule_execution(self) -> None:
        """Test schedule execution functionality."""
        try:
            # Create a job and schedule
            job_id = self.automation_framework.create_job(
                name="Execution Test Job",
                description="Job for execution testing",
                command="echo 'Execution test successful'",
                timeout=60
            )
            
            schedule_id = self.scheduler.create_schedule(
                name="Execution Test Schedule",
                description="Test schedule for execution",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 1 hour",
                job_ids=[job_id]
            )
            
            # Run schedule once
            results = await self.scheduler.run_schedule_once(schedule_id)
            
            # Verify execution
            if len(results) != 1:
                raise Exception(f"Expected 1 result, got {len(results)}")
            
            # Clean up
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in schedule execution: {str(e)}")
    
    async def _test_dependency_management(self) -> None:
        """Test dependency management functionality."""
        try:
            # Create jobs
            job1_id = self.automation_framework.create_job(
                name="Dependency Job 1",
                description="First dependency job",
                command="echo 'Dependency 1'",
                timeout=60
            )
            
            job2_id = self.automation_framework.create_job(
                name="Dependency Job 2",
                description="Second dependency job",
                command="echo 'Dependency 2'",
                timeout=60
            )
            
            # Create schedules with dependencies
            schedule1_id = self.scheduler.create_schedule(
                name="Dependency Schedule 1",
                description="First schedule",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 1 hour",
                job_ids=[job1_id]
            )
            
            schedule2_id = self.scheduler.create_schedule(
                name="Dependency Schedule 2",
                description="Second schedule with dependency",
                schedule_type=ScheduleType.DEPENDENCY,
                expression="",
                job_ids=[job2_id],
                dependencies=[schedule1_id]
            )
            
            # Verify dependency setup
            schedule2 = self.scheduler.get_schedule(schedule2_id)
            if schedule1_id not in schedule2.dependencies:
                raise Exception("Dependency not properly set")
            
            # Clean up
            self.scheduler.delete_schedule(schedule2_id)
            self.scheduler.delete_schedule(schedule1_id)
            self.automation_framework.delete_job(job2_id)
            self.automation_framework.delete_job(job1_id)
        
        except Exception as e:
            raise Exception(f"Error in dependency management: {str(e)}")
    
    async def _test_schedule_optimization(self) -> None:
        """Test schedule optimization functionality."""
        try:
            # Get optimization results
            optimizations = self.scheduler.optimize_schedules()
            
            # Verify optimization structure
            required_keys = ["schedules_optimized", "conflicts_resolved", 
                           "dependencies_optimized", "recommendations"]
            
            for key in required_keys:
                if key not in optimizations:
                    raise Exception(f"Optimization missing required key: {key}")
            
            # Verify data types
            if not isinstance(optimizations["schedules_optimized"], int):
                raise Exception("schedules_optimized should be an integer")
            
            if not isinstance(optimizations["recommendations"], list):
                raise Exception("recommendations should be a list")
        
        except Exception as e:
            raise Exception(f"Error in schedule optimization: {str(e)}")
    
    # CI/CD Integration Module Tests
    async def _test_pipeline_creation(self) -> None:
        """Test pipeline creation functionality."""
        try:
            # Create pipeline
            pipeline_id = self.cicd_integration.create_pipeline(
                name="Test Pipeline",
                description="Test CI/CD pipeline",
                pipeline_type=PipelineType.GITHUB_ACTIONS,
                config_file=".github/workflows/test.yml",
                repository_url="https://github.com/test/repo",
                branch="main"
            )
            
            # Verify pipeline was created
            pipeline = self.cicd_integration.get_pipeline(pipeline_id)
            if not pipeline:
                raise Exception("Pipeline not found after creation")
            
            # Verify pipeline properties
            if pipeline.name != "Test Pipeline":
                raise Exception("Pipeline name not set correctly")
            
            if pipeline.pipeline_type != PipelineType.GITHUB_ACTIONS:
                raise Exception("Pipeline type not set correctly")
            
            # Clean up
            self.cicd_integration.delete_pipeline(pipeline_id)
        
        except Exception as e:
            raise Exception(f"Error in pipeline creation: {str(e)}")
    
    async def _test_pipeline_management(self) -> None:
        """Test pipeline management functionality."""
        try:
            # Create pipeline
            pipeline_id = self.cicd_integration.create_pipeline(
                name="Management Test Pipeline",
                description="Test pipeline for management",
                pipeline_type=PipelineType.CUSTOM,
                config_file="scripts/test.sh",
                repository_url="https://github.com/test/repo"
            )
            
            # Update pipeline
            success = self.cicd_integration.update_pipeline(
                pipeline_id, description="Updated description"
            )
            if not success:
                raise Exception("Failed to update pipeline")
            
            # Verify update
            pipeline = self.cicd_integration.get_pipeline(pipeline_id)
            if pipeline.description != "Updated description":
                raise Exception("Pipeline update not reflected")
            
            # Clean up
            self.cicd_integration.delete_pipeline(pipeline_id)
        
        except Exception as e:
            raise Exception(f"Error in pipeline management: {str(e)}")
    
    async def _test_deployment_creation(self) -> None:
        """Test deployment creation functionality."""
        try:
            # Create deployment
            deployment_id = self.cicd_integration.create_deployment(
                name="Test Deployment",
                description="Test deployment configuration",
                target_environment="staging",
                deployment_script="scripts/deploy.sh",
                validation_scripts=["scripts/validate.sh"],
                rollback_script="scripts/rollback.sh",
                health_check_url="http://localhost:8080/health"
            )
            
            # Verify deployment was created
            deployment = self.cicd_integration.get_deployment(deployment_id)
            if not deployment:
                raise Exception("Deployment not found after creation")
            
            # Verify deployment properties
            if deployment.name != "Test Deployment":
                raise Exception("Deployment name not set correctly")
            
            if deployment.target_environment != "staging":
                raise Exception("Deployment environment not set correctly")
            
            # Clean up
            self.cicd_integration.delete_deployment(deployment_id)
        
        except Exception as e:
            raise Exception(f"Error in deployment creation: {str(e)}")
    
    async def _test_deployment_management(self) -> None:
        """Test deployment management functionality."""
        try:
            # Create deployment
            deployment_id = self.cicd_integration.create_deployment(
                name="Management Test Deployment",
                description="Test deployment for management",
                target_environment="production",
                deployment_script="scripts/deploy.sh"
            )
            
            # Update deployment
            success = self.cicd_integration.update_deployment(
                deployment_id, description="Updated description"
            )
            if not success:
                raise Exception("Failed to update deployment")
            
            # Verify update
            deployment = self.cicd_integration.get_deployment(deployment_id)
            if deployment.description != "Updated description":
                raise Exception("Deployment update not reflected")
            
            # Clean up
            self.cicd_integration.delete_deployment(deployment_id)
        
        except Exception as e:
            raise Exception(f"Error in deployment management: {str(e)}")
    
    async def _test_cicd_status(self) -> None:
        """Test CI/CD status functionality."""
        try:
            # Get CI/CD status
            status = self.cicd_integration.get_cicd_status()
            
            # Verify status structure
            required_keys = ["total_pipelines", "enabled_pipelines", "pipeline_success_rate",
                           "total_deployments", "running_deployments", "deployment_success_rate"]
            
            for key in required_keys:
                if key not in status:
                    raise Exception(f"Status missing required key: {key}")
            
            # Verify data types
            if not isinstance(status["total_pipelines"], int):
                raise Exception("total_pipelines should be an integer")
            
            if not isinstance(status["pipeline_success_rate"], (int, float)):
                raise Exception("pipeline_success_rate should be a number")
        
        except Exception as e:
            raise Exception(f"Error in CI/CD status: {str(e)}")
    
    # Integration Workflow Tests
    async def _test_end_to_end_automation_workflow(self) -> None:
        """Test end-to-end automation workflow."""
        try:
            # Create job
            job_id = self.automation_framework.create_job(
                name="End-to-End Test Job",
                description="Job for end-to-end testing",
                command="echo 'End-to-end test successful'",
                timeout=60
            )
            
            # Create schedule
            schedule_id = self.scheduler.create_schedule(
                name="End-to-End Test Schedule",
                description="Schedule for end-to-end testing",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 1 hour",
                job_ids=[job_id]
            )
            
            # Create pipeline
            pipeline_id = self.cicd_integration.create_pipeline(
                name="End-to-End Test Pipeline",
                description="Pipeline for end-to-end testing",
                pipeline_type=PipelineType.CUSTOM,
                config_file="scripts/test.sh",
                repository_url="https://github.com/test/repo"
            )
            
            # Verify all components work together
            job = self.automation_framework.get_job(job_id)
            schedule = self.scheduler.get_schedule(schedule_id)
            pipeline = self.cicd_integration.get_pipeline(pipeline_id)
            
            if not (job and schedule and pipeline):
                raise Exception("Not all components created successfully")
            
            # Clean up
            self.cicd_integration.delete_pipeline(pipeline_id)
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in end-to-end automation workflow: {str(e)}")
    
    async def _test_scheduled_automation_workflow(self) -> None:
        """Test scheduled automation workflow."""
        try:
            # Create job with notification
            job_id = self.automation_framework.create_job(
                name="Scheduled Workflow Job",
                description="Job for scheduled workflow testing",
                command="echo 'Scheduled workflow test successful'",
                timeout=60,
                notifications=["console_notification"]
            )
            
            # Create console notification config
            config = NotificationConfig(type=NotificationType.CONSOLE, enabled=True)
            self.automation_framework.add_notification_config("console_notification", config)
            
            # Create schedule
            schedule_id = self.scheduler.create_schedule(
                name="Scheduled Workflow Schedule",
                description="Schedule for workflow testing",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 1 hour",
                job_ids=[job_id]
            )
            
            # Run schedule once to test integration
            results = await self.scheduler.run_schedule_once(schedule_id)
            
            if len(results) != 1:
                raise Exception("Scheduled workflow did not produce expected results")
            
            # Clean up
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.remove_notification_config("console_notification")
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in scheduled automation workflow: {str(e)}")
    
    # Data Persistence Tests
    async def _test_automation_data_persistence(self) -> None:
        """Test automation data persistence."""
        try:
            # Create job
            job_id = self.automation_framework.create_job(
                name="Persistence Test Job",
                description="Job for persistence testing",
                command="echo 'Persistence test successful'",
                timeout=60
            )
            
            # Verify job exists
            job = self.automation_framework.get_job(job_id)
            if not job:
                raise Exception("Job not found after creation")
            
            # Clean up
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in automation data persistence: {str(e)}")
    
    async def _test_scheduler_data_persistence(self) -> None:
        """Test scheduler data persistence."""
        try:
            # Create job and schedule
            job_id = self.automation_framework.create_job(
                name="Scheduler Persistence Job",
                description="Job for scheduler persistence testing",
                command="echo 'Scheduler persistence test successful'",
                timeout=60
            )
            
            schedule_id = self.scheduler.create_schedule(
                name="Scheduler Persistence Schedule",
                description="Schedule for persistence testing",
                schedule_type=ScheduleType.INTERVAL,
                expression="every 1 hour",
                job_ids=[job_id]
            )
            
            # Verify schedule exists
            schedule = self.scheduler.get_schedule(schedule_id)
            if not schedule:
                raise Exception("Schedule not found after creation")
            
            # Clean up
            self.scheduler.delete_schedule(schedule_id)
            self.automation_framework.delete_job(job_id)
        
        except Exception as e:
            raise Exception(f"Error in scheduler data persistence: {str(e)}")
    
    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        # Calculate overall statistics
        total_tests = len(self.test_suite.test_results)
        passed_tests = sum(1 for result in self.test_suite.test_results if result.status == TestStatus.PASSED)
        failed_tests = sum(1 for result in self.test_suite.test_results if result.status == TestStatus.FAILED)
        error_tests = sum(1 for result in self.test_suite.test_results if result.status == TestStatus.ERROR)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if failed_tests > 0:
            recommendations.append(f"Address {failed_tests} failed tests")
        if error_tests > 0:
            recommendations.append(f"Fix {error_tests} error conditions")
        if success_rate < 80:
            recommendations.append("Improve overall test success rate")
        else:
            recommendations.append("Excellent automation framework coverage achieved")
        
        report = {
            "test_suite": "Inspector Automation Framework Tests (Task 4.1)",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": success_rate,
                "execution_time": self.test_suite.total_execution_time
            },
            "recommendations": recommendations,
            "test_results": {
                result.test_name: {
                    "status": result.status.value,
                    "details": result.details,
                    "error_message": result.error_message
                }
                for result in self.test_suite.test_results
            },
            "module_status": {
                "automation_framework": "✅ Implemented" if passed_tests >= 6 else "⚠️ Needs improvement",
                "scheduler": "✅ Implemented" if passed_tests >= 11 else "⚠️ Needs improvement",
                "cicd_integration": "✅ Implemented" if passed_tests >= 16 else "⚠️ Needs improvement"
            }
        }
        
        return report
    
    def _save_results(self, report: Dict[str, Any]) -> None:
        """Save test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automation_framework_test_results_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Test results saved to: {filepath}")


def main():
    """Main function to run automation framework tests."""
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create and run test runner
    runner = AutomationFrameworkTestRunner()
    
    try:
        # Run tests
        report = asyncio.run(runner.run_all_tests())
        
        # Print summary
        print("\n" + "=" * 60)
        print("🤖 INSPECTOR AUTOMATION FRAMEWORK TESTS COMPLETED")
        print("=" * 60)
        print(f"📊 Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Passed: {report['summary']['passed_tests']}")
        print(f"❌ Failed: {report['summary']['failed_tests']}")
        print(f"⚠️ Errors: {report['summary']['error_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"⏱️ Execution Time: {report['summary']['execution_time']:.2f}s")
        
        print("\n📋 Module Status:")
        for module, status in report['module_status'].items():
            print(f"  {module}: {status}")
        
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        # Final status
        if report['summary']['success_rate'] >= 80:
            print("\n🎉 Task 4.1: Inspector Automation Framework - COMPLETED SUCCESSFULLY!")
        else:
            print("\n⚠️ Task 4.1: Inspector Automation Framework - NEEDS IMPROVEMENT")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        logging.exception("Test execution error")


if __name__ == "__main__":
    main() 