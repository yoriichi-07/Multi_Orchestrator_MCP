"""
Pytest configuration and shared fixtures
"""
import asyncio
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app, initialize_services
from src.core.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def initialized_services():
    """Initialize services for testing"""
    await initialize_services()
    yield
    # Cleanup if needed


@pytest.fixture
def test_settings():
    """Test settings override"""
    return Settings(
        debug=True,
        descope_project_id="test_project",
        output_base_path="./test_outputs",
        openai_api_key="test_key",
        auth_exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico", "/mcp/initialize", "/mcp/tools/list", "/mcp/tools/call", "/mcp/resources/list", "/mcp/resources/read"]
    )


@pytest.fixture
def test_client(initialized_services):
    """Test client for FastAPI app with mocked authentication"""
    from src.main import app
    from unittest.mock import patch
    from src.core.auth import AuthContext
    
    # Create mock auth context
    mock_auth_context = AuthContext(
        user_id="test_user",
        scopes=["tools:ping", "tools:generate", "admin:metrics"],
        token_claims={"sub": "test_user", "permissions": ["tools:ping", "tools:generate", "admin:metrics"]},
        correlation_id="test_correlation"
    )
    
    # Mock the authentication middleware to always return the mock context
    with patch('src.middleware.auth_middleware.DescopeAuthMiddleware.__call__') as mock_middleware:
        async def mock_call(self, scope, receive, send):
            # Add auth context to request state
            if scope["type"] == "http":
                from fastapi import Request
                request = Request(scope, receive)
                request.state.auth_context = mock_auth_context
                request.state.correlation_id = "test_correlation"
            await self.app(scope, receive, send)
        
        mock_middleware.side_effect = mock_call
        
        return TestClient(app)


@pytest.fixture
async def async_client(initialized_services):
    """Async test client for FastAPI app"""
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing"""
    import jwt
    payload = {
        "sub": "test_user",
        "permissions": ["tools:ping", "tools:generate"],
        "jti": "test_correlation_id",
        "exp": 9999999999  # Far future
    }
    return jwt.encode(payload, "your-descope-secret", algorithm="HS256")
