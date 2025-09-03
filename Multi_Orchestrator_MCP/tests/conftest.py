"""
Pytest configuration and shared fixtures
"""
import asyncio
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app
from src.core.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings override"""
    return Settings(
        debug=True,
        descope_project_id="test_project",
        output_base_path="./test_outputs",
        openai_api_key="test_key"
    )


@pytest.fixture
def test_client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def async_client():
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
