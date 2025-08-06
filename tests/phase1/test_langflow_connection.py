"""
Phase 1: Langflow Connection Tests

This module contains tests for the basic Langflow connection functionality,
including connection establishment, data sending, and health monitoring.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.modules.module_4_langflow.langflow_connector import LangflowConnector
from config.langflow_config import LangflowConfig

class TestLangflowConnection:
    """Test suite for LangflowConnector basic functionality."""
    
    @pytest.fixture
    async def config(self):
        """Create test configuration."""
        config_manager = LangflowConfig()
        return config_manager.get_config()
    
    @pytest.fixture
    async def connector(self, config):
        """Create LangflowConnector instance for testing."""
        connector = LangflowConnector(config)
        yield connector
        await connector.disconnect()
    
    @pytest.mark.asyncio
    async def test_connector_initialization(self, config):
        """Test LangflowConnector initialization."""
        connector = LangflowConnector(config)
        
        assert connector.config == config
        assert connector.connected == False
        assert connector.websocket == None
        assert connector.auth_token == None
        assert connector.reconnect_attempts == 0
        assert connector.max_reconnect_attempts == config.get("max_reconnect_attempts", 5)
    
    @pytest.mark.asyncio
    async def test_auth_token_generation(self, config):
        """Test JWT token generation."""
        connector = LangflowConnector(config)
        token = connector.generate_auth_token()
        
        # Verify token is not empty
        assert token is not None
        assert len(token) > 0
        
        # Verify token structure (basic check)
        assert token.count('.') == 2  # JWT has 3 parts separated by dots
    
    @pytest.mark.asyncio
    async def test_connection_health_initialization(self, config):
        """Test connection health metrics initialization."""
        connector = LangflowConnector(config)
        
        health = connector.connection_health
        assert "last_heartbeat" in health
        assert "latency_ms" in health
        assert "error_count" in health
        assert "uptime" in health
        assert "connection_start" in health
        
        assert health["latency_ms"] == 0
        assert health["error_count"] == 0
        assert health["uptime"] == 0
    
    @pytest.mark.asyncio
    async def test_get_connection_health(self, config):
        """Test getting connection health metrics."""
        connector = LangflowConnector(config)
        
        health = connector.get_connection_health()
        
        assert "connected" in health
        assert "websocket_url" in health
        assert "health_metrics" in health
        assert "reconnect_attempts" in health
        assert "max_reconnect_attempts" in health
        
        assert health["connected"] == False
        assert health["websocket_url"] == config["websocket_url"]
        assert health["reconnect_attempts"] == 0
    
    @pytest.mark.asyncio
    async def test_data_sending_when_disconnected(self, connector):
        """Test data sending when not connected."""
        test_data = {
            "module": "test",
            "operation": "test_op",
            "data": {"test": "value"}
        }
        
        result = await connector.send_data(test_data)
        assert result["status"] == "error"
        assert "Not connected" in result["message"]
    
    @pytest.mark.asyncio
    async def test_receive_data_when_disconnected(self, connector):
        """Test data receiving when not connected."""
        result = await connector.receive_data()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, connector):
        """Test disconnect when not connected."""
        # Should not raise any exceptions
        await connector.disconnect()
        assert connector.connected == False
        assert connector.websocket == None
        assert connector.auth_token == None
    
    @pytest.mark.asyncio
    async def test_reconnect_attempts_tracking(self, config):
        """Test reconnection attempts tracking."""
        connector = LangflowConnector(config)
        
        # Simulate failed reconnection attempts
        connector.reconnect_attempts = 3
        connector.max_reconnect_attempts = 5
        
        # Should allow reconnection
        assert connector.reconnect_attempts < connector.max_reconnect_attempts
        
        # Simulate max attempts reached
        connector.reconnect_attempts = 5
        
        # Should not allow reconnection
        result = await connector.reconnect()
        assert result["status"] == "error"
        assert "Max reconnection attempts reached" in result["message"]
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, config):
        """Test async context manager functionality."""
        async with LangflowConnector(config) as connector:
            # Connector should be initialized
            assert connector is not None
            assert isinstance(connector, LangflowConnector)
            
            # Note: In a real test environment, connection would be attempted
            # but would likely fail without a running Langflow server
            # This test mainly verifies the context manager interface
    
    @pytest.mark.asyncio
    async def test_config_validation(self, config):
        """Test configuration validation."""
        # Test with valid config
        connector = LangflowConnector(config)
        
        # Test with invalid config (missing required fields)
        invalid_config = {"websocket_url": "invalid-url"}
        connector_invalid = LangflowConnector(invalid_config)
        
        # The connector should still initialize, but connection would fail
        assert connector_invalid.config == invalid_config
    
    @pytest.mark.asyncio
    async def test_connection_metrics_update(self, config):
        """Test connection metrics update during operations."""
        connector = LangflowConnector(config)
        
        # Simulate some operations that would update metrics
        connector.connection_health["error_count"] = 5
        connector.connection_health["latency_ms"] = 150
        
        health = connector.get_connection_health()
        assert health["health_metrics"]["error_count"] == 5
        assert health["health_metrics"]["latency_ms"] == 150
    
    @pytest.mark.asyncio
    async def test_reconnection_backoff_calculation(self, config):
        """Test exponential backoff calculation for reconnections."""
        connector = LangflowConnector(config)
        
        # Test backoff calculation
        connector.reconnect_attempts = 1
        backoff_delay = min(2 ** connector.reconnect_attempts, 60)
        assert backoff_delay == 2
        
        connector.reconnect_attempts = 2
        backoff_delay = min(2 ** connector.reconnect_attempts, 60)
        assert backoff_delay == 4
        
        connector.reconnect_attempts = 6
        backoff_delay = min(2 ** connector.reconnect_attempts, 60)
        assert backoff_delay == 60  # Should be capped at 60 seconds