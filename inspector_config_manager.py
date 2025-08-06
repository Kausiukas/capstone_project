#!/usr/bin/env python3
"""
Inspector Configuration Manager

This module implements comprehensive Inspector configuration management system
for the MCP server Inspector integration. Part of Task 1.1 in the Inspector Task List.

Features:
- Configuration loading from files
- Environment-specific settings
- Configuration validation
- Configuration hot-reloading
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class InspectorSettings:
    """Inspector configuration settings"""
    # Performance thresholds
    max_response_time_ms: int = 5000
    max_concurrent_tests: int = 10
    test_timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Logging levels
    log_level: str = "INFO"
    log_file: str = "logs/inspector.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Test configuration
    test_batch_size: int = 5
    test_parallel_workers: int = 3
    test_retry_delay_seconds: int = 5
    
    # Reporting
    report_format: str = "json"  # json, html, xml
    report_output_dir: str = "reports/inspector"
    report_retention_days: int = 30
    
    # Monitoring
    monitoring_interval_seconds: int = 60
    alert_threshold_percent: float = 95.0
    performance_degradation_threshold: float = 20.0
    
    # MCP Server settings
    mcp_server_command: str = "python mcp_langflow_connector_simple.py"
    mcp_server_timeout: int = 30
    mcp_server_retries: int = 3
    
    # Inspector specific
    inspector_command: str = "npx @modelcontextprotocol/inspector"
    inspector_cli_mode: bool = True
    inspector_debug_mode: bool = False
    
    def __post_init__(self):
        """Validate settings after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration settings"""
        if self.max_response_time_ms <= 0:
            raise ValueError("max_response_time_ms must be positive")
        if self.max_concurrent_tests <= 0:
            raise ValueError("max_concurrent_tests must be positive")
        if self.test_timeout_seconds <= 0:
            raise ValueError("test_timeout_seconds must be positive")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")
        if self.alert_threshold_percent < 0 or self.alert_threshold_percent > 100:
            raise ValueError("alert_threshold_percent must be between 0 and 100")

@dataclass
class TestProfile:
    """Test profile configuration"""
    name: str
    description: str
    test_types: List[str]  # unit, integration, performance, compliance
    environment: str  # dev, staging, prod
    settings: InspectorSettings
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

class InspectorConfigManager:
    """
    Inspector Configuration Manager
    
    Manages Inspector configuration, settings, and profiles for the MCP server.
    """
    
    def __init__(self, config_dir: str = "config/inspector"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "inspector_config.json"
        self.settings_file = self.config_dir / "inspector_settings.yaml"
        self.profiles_file = self.config_dir / "inspector_profiles.json"
        
        # Default settings
        self.default_settings = InspectorSettings()
        
        # Current configuration
        self.settings: InspectorSettings = self.default_settings
        self.profiles: Dict[str, TestProfile] = {}
        self.current_profile: Optional[str] = None
        
        # Hot reloading
        self.observer: Optional[Observer] = None
        self.watch_callback: Optional[callable] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Inspector Config Manager initialized with config dir: {self.config_dir}")
    
    async def initialize(self) -> None:
        """Initialize the configuration manager"""
        try:
            logger.info("Initializing Inspector Config Manager...")
            
            # Load configuration
            await self.load_configuration()
            
            # Create default profiles if none exist
            if not self.profiles:
                await self.create_default_profiles()
            
            # Set default profile
            if not self.current_profile and self.profiles:
                self.current_profile = list(self.profiles.keys())[0]
            
            logger.info("Inspector Config Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Inspector Config Manager: {e}")
            raise
    
    async def load_configuration(self) -> None:
        """Load configuration from files"""
        try:
            # Load settings
            if self.settings_file.exists():
                await self.load_settings()
            else:
                await self.save_settings()
            
            # Load profiles
            if self.profiles_file.exists():
                await self.load_profiles()
            
            # Load main config
            if self.config_file.exists():
                await self.load_main_config()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def load_settings(self) -> None:
        """Load settings from YAML file"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings_data = yaml.safe_load(f)
            
            if settings_data:
                # Update default settings with loaded data
                for key, value in settings_data.items():
                    if hasattr(self.default_settings, key):
                        setattr(self.default_settings, key, value)
                
                self.settings = self.default_settings
                self.settings.validate()
                
                logger.info("Settings loaded from YAML file")
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            # Use default settings on error
            self.settings = self.default_settings
    
    async def save_settings(self) -> None:
        """Save settings to YAML file"""
        try:
            settings_data = asdict(self.settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(settings_data, f, default_flow_style=False, indent=2)
            
            logger.info("Settings saved to YAML file")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise
    
    async def load_profiles(self) -> None:
        """Load test profiles from JSON file"""
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
            
            self.profiles = {}
            for profile_name, profile_data in profiles_data.items():
                # Convert datetime strings back to datetime objects
                if 'created_at' in profile_data:
                    profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                if 'updated_at' in profile_data:
                    profile_data['updated_at'] = datetime.fromisoformat(profile_data['updated_at'])
                
                # Create settings object
                if 'settings' in profile_data:
                    settings = InspectorSettings(**profile_data['settings'])
                    profile_data['settings'] = settings
                
                profile = TestProfile(**profile_data)
                self.profiles[profile_name] = profile
            
            logger.info(f"Loaded {len(self.profiles)} test profiles")
            
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            self.profiles = {}
    
    async def save_profiles(self) -> None:
        """Save test profiles to JSON file"""
        try:
            profiles_data = {}
            for profile_name, profile in self.profiles.items():
                profile_dict = asdict(profile)
                # Convert datetime objects to ISO format strings
                profile_dict['created_at'] = profile_dict['created_at'].isoformat()
                profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
                profiles_data[profile_name] = profile_dict
            
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2)
            
            logger.info("Profiles saved to JSON file")
            
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            raise
    
    async def load_main_config(self) -> None:
        """Load main configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if 'current_profile' in config_data:
                self.current_profile = config_data['current_profile']
            
            logger.info("Main configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load main config: {e}")
    
    async def save_main_config(self) -> None:
        """Save main configuration to JSON file"""
        try:
            config_data = {
                'current_profile': self.current_profile,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("Main configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save main config: {e}")
            raise
    
    async def create_default_profiles(self) -> None:
        """Create default test profiles"""
        try:
            # Unit test profile
            unit_settings = InspectorSettings(
                test_timeout_seconds=10,
                max_concurrent_tests=5,
                test_batch_size=3,
                log_level="DEBUG"
            )
            
            unit_profile = TestProfile(
                name="unit",
                description="Unit testing profile for individual tool validation",
                test_types=["unit"],
                environment="dev",
                settings=unit_settings
            )
            
            # Integration test profile
            integration_settings = InspectorSettings(
                test_timeout_seconds=30,
                max_concurrent_tests=3,
                test_batch_size=2,
                log_level="INFO"
            )
            
            integration_profile = TestProfile(
                name="integration",
                description="Integration testing profile for tool interaction validation",
                test_types=["integration"],
                environment="staging",
                settings=integration_settings
            )
            
            # Performance test profile
            performance_settings = InspectorSettings(
                test_timeout_seconds=60,
                max_concurrent_tests=2,
                test_batch_size=1,
                log_level="WARNING",
                max_response_time_ms=10000
            )
            
            performance_profile = TestProfile(
                name="performance",
                description="Performance testing profile for load and stress testing",
                test_types=["performance"],
                environment="prod",
                settings=performance_settings
            )
            
            # Compliance test profile
            compliance_settings = InspectorSettings(
                test_timeout_seconds=45,
                max_concurrent_tests=4,
                test_batch_size=2,
                log_level="INFO"
            )
            
            compliance_profile = TestProfile(
                name="compliance",
                description="Compliance testing profile for MCP protocol validation",
                test_types=["compliance"],
                environment="staging",
                settings=compliance_settings
            )
            
            # Add profiles
            self.profiles = {
                "unit": unit_profile,
                "integration": integration_profile,
                "performance": performance_profile,
                "compliance": compliance_profile
            }
            
            # Save profiles
            await self.save_profiles()
            
            logger.info("Default test profiles created")
            
        except Exception as e:
            logger.error(f"Failed to create default profiles: {e}")
            raise
    
    async def get_profile(self, profile_name: str) -> Optional[TestProfile]:
        """Get a test profile by name"""
        return self.profiles.get(profile_name)
    
    async def list_profiles(self) -> List[str]:
        """List all available profile names"""
        return list(self.profiles.keys())
    
    async def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different test profile"""
        if profile_name not in self.profiles:
            logger.error(f"Profile '{profile_name}' not found")
            return False
        
        self.current_profile = profile_name
        self.settings = self.profiles[profile_name].settings
        
        # Update profile timestamp
        self.profiles[profile_name].updated_at = datetime.now(timezone.utc)
        
        # Save configuration
        await self.save_main_config()
        await self.save_profiles()
        
        logger.info(f"Switched to profile: {profile_name}")
        return True
    
    async def create_profile(self, name: str, description: str, test_types: List[str], 
                           environment: str, settings: Optional[InspectorSettings] = None) -> bool:
        """Create a new test profile"""
        if name in self.profiles:
            logger.error(f"Profile '{name}' already exists")
            return False
        
        if settings is None:
            settings = InspectorSettings()
        
        profile = TestProfile(
            name=name,
            description=description,
            test_types=test_types,
            environment=environment,
            settings=settings
        )
        
        self.profiles[name] = profile
        await self.save_profiles()
        
        logger.info(f"Created new profile: {name}")
        return True
    
    async def update_profile(self, name: str, **kwargs) -> bool:
        """Update an existing test profile"""
        if name not in self.profiles:
            logger.error(f"Profile '{name}' not found")
            return False
        
        profile = self.profiles[name]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now(timezone.utc)
        
        await self.save_profiles()
        
        logger.info(f"Updated profile: {name}")
        return True
    
    async def delete_profile(self, name: str) -> bool:
        """Delete a test profile"""
        if name not in self.profiles:
            logger.error(f"Profile '{name}' not found")
            return False
        
        if self.current_profile == name:
            logger.error(f"Cannot delete current profile: {name}")
            return False
        
        del self.profiles[name]
        await self.save_profiles()
        
        logger.info(f"Deleted profile: {name}")
        return True
    
    async def get_current_settings(self) -> InspectorSettings:
        """Get current settings (from current profile or default)"""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile].settings
        return self.settings
    
    async def update_settings(self, **kwargs) -> bool:
        """Update current settings"""
        try:
            current_settings = await self.get_current_settings()
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(current_settings, key):
                    setattr(current_settings, key, value)
            
            # Validate settings
            current_settings.validate()
            
            # Save settings
            await self.save_settings()
            
            logger.info("Settings updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return False
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "profile": self.current_profile,
            "settings_valid": True,
            "profiles_count": len(self.profiles)
        }
        
        try:
            # Validate current settings
            current_settings = await self.get_current_settings()
            current_settings.validate()
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["settings_valid"] = False
            validation_results["errors"].append(f"Settings validation failed: {e}")
        
        # Check for warnings
        if not self.profiles:
            validation_results["warnings"].append("No test profiles configured")
        
        if not self.current_profile:
            validation_results["warnings"].append("No current profile selected")
        
        logger.info(f"Configuration validation completed: {validation_results['valid']}")
        return validation_results
    
    async def start_hot_reload(self, callback: Optional[callable] = None) -> None:
        """Start hot reload monitoring for configuration files"""
        if self.observer:
            logger.warning("Hot reload already running")
            return
        
        self.watch_callback = callback
        
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager
            
            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml')):
                    logger.info(f"Configuration file changed: {event.src_path}")
                    asyncio.create_task(self.manager._reload_config())
        
        self.observer = Observer()
        self.observer.schedule(ConfigFileHandler(self), str(self.config_dir), recursive=False)
        self.observer.start()
        
        logger.info("Hot reload monitoring started")
    
    async def stop_hot_reload(self) -> None:
        """Stop hot reload monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.watch_callback = None
            logger.info("Hot reload monitoring stopped")
    
    async def _reload_config(self) -> None:
        """Reload configuration when files change"""
        try:
            await self.load_configuration()
            
            if self.watch_callback:
                await self.watch_callback()
            
            logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
    
    async def export_configuration(self, export_path: str) -> bool:
        """Export current configuration to a file"""
        try:
            export_data = {
                "settings": asdict(await self.get_current_settings()),
                "profiles": {},
                "current_profile": self.current_profile,
                "exported_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Export profiles
            for name, profile in self.profiles.items():
                profile_dict = asdict(profile)
                profile_dict['created_at'] = profile_dict['created_at'].isoformat()
                profile_dict['updated_at'] = profile_dict['updated_at'].isoformat()
                export_data["profiles"][name] = profile_dict
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    async def import_configuration(self, import_path: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import settings
            if 'settings' in import_data:
                self.settings = InspectorSettings(**import_data['settings'])
            
            # Import profiles
            if 'profiles' in import_data:
                self.profiles = {}
                for name, profile_data in import_data['profiles'].items():
                    # Convert datetime strings
                    if 'created_at' in profile_data:
                        profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                    if 'updated_at' in profile_data:
                        profile_data['updated_at'] = datetime.fromisoformat(profile_data['updated_at'])
                    
                    # Create settings object
                    if 'settings' in profile_data:
                        settings = InspectorSettings(**profile_data['settings'])
                        profile_data['settings'] = settings
                    
                    profile = TestProfile(**profile_data)
                    self.profiles[name] = profile
            
            # Set current profile
            if 'current_profile' in import_data:
                self.current_profile = import_data['current_profile']
            
            # Save imported configuration
            await self.save_settings()
            await self.save_profiles()
            await self.save_main_config()
            
            logger.info(f"Configuration imported from: {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

# Example usage and testing
async def main():
    """Example usage of Inspector Config Manager"""
    config_manager = InspectorConfigManager()
    
    try:
        # Initialize
        await config_manager.initialize()
        
        # List profiles
        profiles = await config_manager.list_profiles()
        print(f"Available profiles: {profiles}")
        
        # Switch to unit profile
        await config_manager.switch_profile("unit")
        
        # Get current settings
        settings = await config_manager.get_current_settings()
        print(f"Current timeout: {settings.test_timeout_seconds}s")
        
        # Validate configuration
        validation = await config_manager.validate_configuration()
        print(f"Configuration valid: {validation['valid']}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 