"""
Tests for basic MCP tools
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "autonomous-software-foundry"


def test_mcp_capabilities_without_auth(test_client: TestClient):
    """Test MCP capabilities endpoint without authentication"""
    response = test_client.get("/mcp/capabilities")
    assert response.status_code == 403  # FastAPI returns 403 for missing credentials


def test_mcp_capabilities_with_auth(test_client: TestClient, mock_auth_token: str):
    """Test MCP capabilities endpoint with authentication"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    response = test_client.get("/mcp/capabilities", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["apiVersion"] == "2024-11-05"
    assert "capabilities" in data
    assert "serverInfo" in data


def test_ping_tool_without_auth(test_client: TestClient):
    """Test ping tool without authentication"""
    response = test_client.post("/mcp/v1/tools/ping")
    assert response.status_code == 403  # FastAPI returns 403 for missing credentials


def test_ping_tool_with_auth(test_client: TestClient, mock_auth_token: str):
    """Test ping tool with authentication"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    response = test_client.post("/mcp/v1/tools/ping", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
    assert "correlation_id" in data
    assert "timestamp" in data
    assert data["authenticated_user"] == "test_user"


def test_health_check_tool(test_client: TestClient, mock_auth_token: str):
    """Test health check tool"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    response = test_client.post("/mcp/v1/tools/health_check", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "checks" in data
    assert "correlation_id" in data


def test_echo_tool_with_auth(test_client: TestClient, mock_auth_token: str):
    """Test echo tool with authentication"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    test_message = "Hello, MCP Server!"
    response = test_client.post(
        "/mcp/v1/tools/echo", 
        headers=headers,
        params={"message": test_message}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["echo"] == test_message
    assert data["user_id"] == "test_user"
    assert data["message_length"] == len(test_message)
    assert "correlation_id" in data
    assert "timestamp" in data


def test_ping_tool_without_required_scope(test_client: TestClient):
    """Test ping tool with token missing required scope"""
    import jwt
    payload = {
        "sub": "test_user",
        "permissions": ["tools:generate"],  # Missing tools:ping scope
        "jti": "test_correlation_id",
        "exp": 9999999999
    }
    token = jwt.encode(payload, "your-descope-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post("/mcp/v1/tools/ping", headers=headers)
    assert response.status_code == 403
    assert "Missing required scopes" in response.json()["detail"]
