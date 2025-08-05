"""
LangFlow Connect Configuration Manager

This module provides centralized configuration management for the
LangFlow Connect system, including environment variable handling
and configuration validation.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class LangflowConfig:
    """
    Configuration manager for LangFlow Connect system.
    
    Handles environment variable loading, configuration validation,
    and provides centralized access to all system settings.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Optional path to .env file to load
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        logger.info("LangflowConfig initialized")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Configuration dictionary
        """
        config = {
            # Langflow Connection Configuration
            "websocket_url": os.getenv("LANGFLOW_WS_URL", "wss://localhost:3000/ws"),
            "api_url": os.getenv("LANGFLOW_API_URL", "http://localhost:3000/api"),
            "secret_key": os.getenv("LANGFLOW_SECRET_KEY", "your-secret-key-change-this"),
            "user_id": os.getenv("LANGFLOW_USER_ID", "mcp_client"),
            "connection_timeout": int(os.getenv("LANGFLOW_TIMEOUT", "60")),
            "keepalive_interval": int(os.getenv("LANGFLOW_KEEPALIVE", "30")),
            "max_reconnect_attempts": int(os.getenv("LANGFLOW_MAX_RETRIES", "5")),
            
            # Security Configuration
            "tls_version": os.getenv("TLS_VERSION", "1.3"),
            "jwt_expiry": int(os.getenv("JWT_EXPIRY", "3600")),
            "certificate_path": os.getenv("CERTIFICATE_PATH"),
            "private_key_path": os.getenv("PRIVATE_KEY_PATH"),
            
            # Module Configuration
            "modules": {
                "module_1_enabled": os.getenv("MODULE_1_ENABLED", "true").lower() == "true",
                "module_2_enabled": os.getenv("MODULE_2_ENABLED", "true").lower() == "true",
                "module_3_enabled": os.getenv("MODULE_3_ENABLED", "true").lower() == "true",
                "module_4_enabled": os.getenv("MODULE_4_ENABLED", "true").lower() == "true",
                
                # Module 1 (MAIN) - Workspace Operations
                "module_1_max_workers": int(os.getenv("MODULE_1_MAX_WORKERS", "4")),
                "module_1_timeout": int(os.getenv("MODULE_1_TIMEOUT", "30")),
                "module_1_batch_size": int(os.getenv("MODULE_1_BATCH_SIZE", "100")),
                
                # Module 2 (SUPPORT) - System Coordination
                "module_2_monitoring_interval": int(os.getenv("MODULE_2_MONITORING_INTERVAL", "30")),
                "module_2_health_check_interval": int(os.getenv("MODULE_2_HEALTH_CHECK_INTERVAL", "60")),
                "module_2_performance_interval": int(os.getenv("MODULE_2_PERFORMANCE_INTERVAL", "120")),
                
                # Module 3 (ECONOMY) - Cost Tracking
                "module_3_tracking_interval": int(os.getenv("MODULE_3_TRACKING_INTERVAL", "60")),
                "module_3_budget_limit": float(os.getenv("MODULE_3_BUDGET_LIMIT", "1000")),
                "module_3_alert_threshold": float(os.getenv("MODULE_3_ALERT_THRESHOLD", "0.8")),
                
                # Module 4 (LANGFLOW) - Connection Management
                "module_4_streaming_interval": int(os.getenv("MODULE_4_STREAMING_INTERVAL", "5")),
                "module_4_buffer_size": int(os.getenv("MODULE_4_BUFFER_SIZE", "1000")),
                "module_4_max_retries": int(os.getenv("MODULE_4_MAX_RETRIES", "3")),
            },
            
            # Database Configuration
            "database": {
                "host": os.getenv("POSTGRESQL_HOST", "localhost"),
                "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
                "database": os.getenv("POSTGRESQL_DATABASE", "langflow_connect"),
                "user": os.getenv("POSTGRESQL_USER", "postgres"),
                "password": os.getenv("POSTGRESQL_PASSWORD", ""),
                "ssl_mode": os.getenv("POSTGRESQL_SSL_MODE", "prefer"),
                "pool_size": int(os.getenv("POSTGRESQL_POOL_SIZE", "10")),
                "max_overflow": int(os.getenv("POSTGRESQL_MAX_OVERFLOW", "20")),
                "timeout": int(os.getenv("POSTGRESQL_TIMEOUT", "30")),
            },
            
            # Vector Database Configuration
            "vector_db": {
                "enabled": os.getenv("VECTOR_DB_ENABLED", "true").lower() == "true",
                "path": os.getenv("VECTOR_DB_PATH", "data/vectorstore"),
                "chroma_host": os.getenv("CHROMA_HOST", "localhost"),
                "chroma_port": int(os.getenv("CHROMA_PORT", "8000")),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            },
            
            # OpenAI Configuration
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            },
            
            # Monitoring & Logging
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": os.getenv("LOG_FORMAT", "json"),
                "file": os.getenv("LOG_FILE", "logs/langflow_connect.log"),
            },
            
            "monitoring": {
                "metrics_enabled": os.getenv("METRICS_ENABLED", "true").lower() == "true",
                "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
                "health_check_port": int(os.getenv("HEALTH_CHECK_PORT", "8080")),
            },
            
            # Development Settings
            "development": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "dev_mode": os.getenv("DEV_MODE", "false").lower() == "true",
                "mock_data": os.getenv("MOCK_DATA", "false").lower() == "true",
            },
            
            # Testing Configuration
            "testing": {
                "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
                "test_database": os.getenv("TEST_DATABASE", "langflow_connect_test"),
                "test_timeout": int(os.getenv("TEST_TIMEOUT", "30")),
                "coverage_enabled": os.getenv("COVERAGE_ENABLED", "true").lower() == "true",
            },
            
            # Deployment Configuration
            "deployment": {
                "docker_image": os.getenv("DOCKER_IMAGE", "langflow-connect:latest"),
                "kubernetes_namespace": os.getenv("KUBERNETES_NAMESPACE", "langflow-connect"),
                "service_port": int(os.getenv("SERVICE_PORT", "8000")),
                "health_check_path": os.getenv("HEALTH_CHECK_PATH", "/health"),
            }
        }
        
        return config
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific module.
        
        Args:
            module_name: Name of the module (e.g., "module_1", "module_2")
            
        Returns:
            Module-specific configuration dictionary
        """
        module_key = f"{module_name}_enabled"
        if module_key not in self.config["modules"]:
            raise ValueError(f"Unknown module: {module_name}")
        
        # Get module-specific settings
        module_config = {}
        for key, value in self.config["modules"].items():
            if key.startswith(module_name):
                module_config[key] = value
        
        return module_config
    
    def validate_config(self) -> bool:
        """
        Validate configuration for required fields and values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_fields = [
            "websocket_url",
            "secret_key"
        ]
        
        for field in required_fields:
            if not self.config.get(field):
                logger.error(f"Missing required configuration field: {field}")
                return False
        
        # Validate URLs
        if not self.config["websocket_url"].startswith(("ws://", "wss://")):
            logger.error("Invalid WebSocket URL format")
            return False
        
        # Validate numeric fields
        numeric_fields = [
            "connection_timeout",
            "keepalive_interval",
            "max_reconnect_attempts"
        ]
        
        for field in numeric_fields:
            if not isinstance(self.config[field], int) or self.config[field] <= 0:
                logger.error(f"Invalid numeric value for field: {field}")
                return False
        
        logger.info("Configuration validation passed")
        return True
    
    def get_database_url(self) -> str:
        """
        Get PostgreSQL database connection URL.
        
        Returns:
            Database connection URL string
        """
        db_config = self.config["database"]
        return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    def is_development(self) -> bool:
        """
        Check if running in development mode.
        
        Returns:
            True if in development mode
        """
        return self.config["development"]["environment"] == "development"
    
    def is_testing(self) -> bool:
        """
        Check if running in test mode.
        
        Returns:
            True if in test mode
        """
        return self.config["testing"]["test_mode"]
    
    def get_log_level(self) -> str:
        """
        Get logging level.
        
        Returns:
            Logging level string
        """
        return self.config["logging"]["level"]
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        def update_nested_dict(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    update_nested_dict(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        update_nested_dict(self.config, updates)
        logger.info("Configuration updated")
    
    def export_env_vars(self) -> Dict[str, str]:
        """
        Export configuration as environment variables.
        
        Returns:
            Dictionary of environment variable key-value pairs
        """
        env_vars = {}
        
        # Flatten nested configuration
        def flatten_dict(d: Dict[str, Any], prefix: str = "") -> None:
            for key, value in d.items():
                if isinstance(value, dict):
                    flatten_dict(value, f"{prefix}{key.upper()}_")
                else:
                    env_vars[f"{prefix}{key.upper()}"] = str(value)
        
        flatten_dict(self.config)
        return env_vars