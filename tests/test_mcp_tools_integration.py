"""
Integration tests for MCP tools
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.main import app, mcp_server
from src.tools.infrastructure_tools import ping_tool, system_status_tool, list_capabilities_tool, server_metrics_tool
from src.tools.generation_tools import generate_application_tool, generate_component_tool, enhance_application_tool, deploy_application_tool
from src.tools.quality_tools import test_application_tool, self_heal_tool, code_review_tool


class TestMCPToolsIntegration:
    """Test MCP tools integration"""
    
    @pytest.fixture
    def app(self, initialized_services):
        """Use main FastAPI app with initialized services"""
        return app
    
    @pytest.fixture
    def mcp_server_instance(self, initialized_services):
        """Use initialized MCP server"""
        return mcp_server
    
    @pytest.fixture
    def client(self, app, mcp_server_instance):
        """Create test client"""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_infrastructure_tools_registration(self, initialized_services):
        """Test infrastructure tools are properly registered"""
        from src.main import mcp_server
        
        # Check that the MCP server has the expected tools registered
        expected_tools = ["ping", "system_status", "list_capabilities", "server_metrics"]
        tool_names = list(mcp_server.tools.keys())
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool '{tool_name}' not found in registered tools: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_generation_tools_registration(self, initialized_services):
        """Test generation tools are properly registered"""
        from src.main import mcp_server
        
        expected_tools = ["generate_application", "generate_component", "enhance_application", "deploy_application"]
        tool_names = list(mcp_server.tools.keys())
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool '{tool_name}' not found in registered tools: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_quality_tools_registration(self, initialized_services):
        """Test quality tools are properly registered"""
        from src.main import mcp_server
        
        expected_tools = ["test_application", "self_heal", "code_review"]
        tool_names = list(mcp_server.tools.keys())
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool '{tool_name}' not found in registered tools: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_ping_tool_execution(self, client):
        """Test ping tool execution"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ping",
                "arguments": {}
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            response = client.post("/mcp/tools/call", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "content" in data["result"]
        
        # Check ping response format
        content = data["result"]["content"]
        assert len(content) > 0
        assert content[0]["type"] == "text"
        assert "pong" in content[0]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_system_status_tool_execution(self, client):
        """Test system status tool execution"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "system_status",
                "arguments": {}
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            with patch('psutil.cpu_percent', return_value=25.5):
                with patch('psutil.virtual_memory') as mock_memory:
                    mock_memory.return_value.percent = 45.2
                    with patch('psutil.disk_usage') as mock_disk:
                        mock_disk.return_value.percent = 67.8
                        response = client.post("/mcp/tools/call", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        content = data["result"]["content"]
        
        # Check that system metrics are included
        text_content = content[0]["text"]
        assert "CPU Usage" in text_content
        assert "Memory Usage" in text_content
        assert "Disk Usage" in text_content
    
    @pytest.mark.asyncio
    async def test_generate_application_tool_structure(self, client):
        """Test generate application tool input schema"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = client.post("/mcp/tools/list", json=request_data)
        data = response.json()
        tools = data["result"]["tools"]
        
        # Find generate_application tool
        generate_tool = None
        for tool in tools:
            if tool["name"] == "generate_application":
                generate_tool = tool
                break
        
        assert generate_tool is not None
        assert "inputSchema" in generate_tool
        
        # Check input schema structure
        schema = generate_tool["inputSchema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        
        properties = schema["properties"]
        assert "app_name" in properties
        assert "app_type" in properties
        assert "requirements" in properties
        assert "user_id" in properties
    
    @pytest.mark.asyncio
    async def test_tool_schema_validation(self, client):
        """Test tool input schema validation"""
        # Test with invalid arguments (missing required fields)
        request_data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "generate_application",
                "arguments": {
                    # Missing required fields
                    "incomplete": "data"
                }
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            response = client.post("/mcp/tools/call", json=request_data)
        
        # Should handle validation errors gracefully
        assert response.status_code in [400, 422, 500]  # Various error codes are acceptable for validation
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, client):
        """Test tool error handling"""
        # Test calling non-existent tool
        request_data = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool",
                "arguments": {}
            }
        }
        
        response = client.post("/mcp/tools/call", json=request_data)
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found
    
    @pytest.mark.asyncio
    async def test_tool_authentication_integration(self, client):
        """Test tool authentication integration"""
        # Mock authentication failure
        with patch('src.tools.infrastructure_tools.verify_user_auth') as mock_auth:
            mock_auth.side_effect = Exception("Authentication failed")
            
            request_data = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "server_metrics",
                    "arguments": {}
                }
            }
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/tools/call", json=request_data)
            
            # Should handle authentication errors
            assert response.status_code in [401, 403, 500]
    
    @pytest.mark.asyncio
    async def test_tool_analytics_integration(self, client):
        """Test tool analytics integration"""
        with patch('src.core.tool_registry.AnalyticsTracker.track_tool_call') as mock_track:
            request_data = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "ping",
                    "arguments": {}
                }
            }
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/tools/call", json=request_data)
            
            # Verify analytics tracking was called
            mock_track.assert_called()
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, client):
        """Test concurrent tool execution"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request():
            request_data = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "ping",
                    "arguments": {}
                }
            }
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                return client.post("/mcp/tools/call", json=request_data)
        
        # Execute multiple concurrent requests
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "result" in data