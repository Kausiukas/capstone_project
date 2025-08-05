import pytest
from fastapi.testclient import TestClient
from src.mcp_server_http import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_tools_list_endpoint():
    """Test tools list endpoint"""
    response = client.get("/tools/list", headers={"api-key": "demo_key_123"})
    assert response.status_code == 200
    assert "tools" in response.json()

def test_tool_call_endpoint():
    """Test tool call endpoint"""
    response = client.post(
        "/api/v1/tools/call",
        headers={"X-API-Key": "demo_key_123"},
        json={"name": "ping", "arguments": {}}
    )
    assert response.status_code == 200
    assert "content" in response.json()

def test_invalid_api_key():
    """Test invalid API key"""
    response = client.get("/tools/list", headers={"api-key": "invalid_key"})
    assert response.status_code == 401
