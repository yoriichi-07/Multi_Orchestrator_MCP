"""
Pytest configuration and shared fixtures
"""
import asyncio
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import Settings


"""
Pytest configuration and shared fixtures for MCP server testing
"""
import asyncio
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
def mock_mcp_server():
    """Mock MCP server for testing"""
    server = MagicMock()
    server.list_tools = AsyncMock(return_value=[])
    server.call_tool = AsyncMock(return_value={"success": True})
    server.list_resources = AsyncMock(return_value=[])
    server.read_resource = AsyncMock(return_value={"content": "test content"})
    return server


@pytest.fixture
def mock_auth_context():
    """Mock authentication context for testing"""
    from src.core.auth import AuthContext
    return AuthContext(
        user_id="test_user",
        scopes=["tools:ping", "tools:generate", "admin:metrics"],
        token_claims={"sub": "test_user", "permissions": ["tools:ping", "tools:generate", "admin:metrics"]},
        correlation_id="test_correlation"
    )
