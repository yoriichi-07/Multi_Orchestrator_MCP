"""
Tests for MCP server core implementation
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.core.mcp_server import MCPServer, initialize_mcp_server, get_mcp_server
from src.core.tool_registry import mcp_tool, mcp_resource


class TestMCPServer:
    """Test MCP server core functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app"""
        app = FastAPI()
        return app
    
    @pytest.fixture
    def mcp_server(self, app):
        """Create test MCP server"""
        return MCPServer(app)
    
    @pytest.fixture
    def test_client(self, app, mcp_server):
        """Create test client"""
        return TestClient(app)
    
    def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initializes correctly"""
        assert mcp_server.tools == {}
        assert mcp_server.resources == {}
        assert mcp_server.server_info.name == "autonomous-software-foundry"
        assert mcp_server.server_info.version == "1.0.0"
        assert mcp_server.capabilities.tools is not None
        assert mcp_server.capabilities.resources is not None
    
    @pytest.mark.asyncio
    async def test_mcp_initialize_endpoint(self, test_client):
        """Test MCP initialization handshake"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = test_client.post("/mcp/initialize", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in data["result"]
        assert "serverInfo" in data["result"]
    
    @pytest.mark.asyncio
    async def test_mcp_tools_list_endpoint(self, test_client, mcp_server):
        """Test MCP tools listing"""
        # Manually register a test tool with the local server
        async def test_tool_func():
            return {"test": "result"}
        
        # Register the tool directly with the mcp_server instance
        mcp_server.register_tool(
            name="test_tool",
            description="Test tool for testing",
            input_schema={"type": "object", "properties": {}},
            required_scopes=["test:scope"]
        )(test_tool_func)
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = test_client.post("/mcp/tools/list", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        assert "tools" in data["result"]
        
        # Check if our test tool is listed
        tools = data["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]
        assert "test_tool" in tool_names
    
    @pytest.mark.asyncio
    async def test_mcp_tool_call_endpoint(self, test_client, mcp_server):
        """Test MCP tool execution"""
        # Mock a request object
        mock_request = Mock()
        mock_request.state = Mock()
        mock_request.state.correlation_id = "test-correlation-id"
        
        # Register a test tool that doesn't require auth for testing
        async def test_tool_handler(request, test_param="default"):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Test result with param: {test_param}"
                    }
                ]
            }
        
        # Manually register the tool
        mcp_server.tools["test_tool"] = test_tool_handler
        test_tool_handler._mcp_tool_info = Mock()
        test_tool_handler._mcp_tool_info.name = "test_tool"
        test_tool_handler._mcp_tool_info.description = "Test tool"
        test_tool_handler._mcp_tool_info.inputSchema = {
            "type": "object",
            "properties": {
                "test_param": {"type": "string"}
            }
        }
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {
                    "test_param": "test_value"
                }
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            response = test_client.post("/mcp/tools/call", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "result" in data
        assert "content" in data["result"]
    
    @pytest.mark.asyncio
    async def test_mcp_resources_list_endpoint(self, test_client, mcp_server):
        """Test MCP resources listing"""
        # Register a test resource
        async def test_resource_handler(request):
            return {"test": "resource_data"}
        
        # Manually register the resource
        mcp_server.resources["test://resource"] = test_resource_handler
        test_resource_handler._mcp_resource_info = Mock()
        test_resource_handler._mcp_resource_info.uri = "test://resource"
        test_resource_handler._mcp_resource_info.name = "Test Resource"
        test_resource_handler._mcp_resource_info.description = "Test resource for testing"
        test_resource_handler._mcp_resource_info.mimeType = "application/json"
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/list"
        }
        
        response = test_client.post("/mcp/resources/list", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 4
        assert "result" in data
        assert "resources" in data["result"]
        
        # Check if our test resource is listed
        resources = data["result"]["resources"]
        resource_uris = [resource["uri"] for resource in resources]
        assert "test://resource" in resource_uris
    
    @pytest.mark.asyncio
    async def test_mcp_resource_read_endpoint(self, test_client, mcp_server):
        """Test MCP resource reading"""
        # Register a test resource
        async def test_resource_handler(request):
            return {
                "uri": "test://resource",
                "mimeType": "application/json",
                "text": json.dumps({"test": "resource_data"})
            }
        
        # Manually register the resource
        mcp_server.resources["test://resource"] = test_resource_handler
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {
                "uri": "test://resource"
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            response = test_client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 5
        assert "result" in data
        assert "contents" in data["result"]
    
    def test_tool_registration_decorator(self, mcp_server):
        """Test tool registration decorator"""
        # Test manual registration instead of decorator since decorator needs global server
        async def decorated_tool_func(test_param: str):
            return {"result": test_param}
        
        # Manually register the tool
        tool_count_before = len(mcp_server.tools)
        mcp_server.register_tool(
            name="decorated_tool",
            description="Tool registered with decorator",
            input_schema={"type": "object", "properties": {"test_param": {"type": "string"}}},
            required_scopes=["test:scope"]
        )(decorated_tool_func)
        
        # Verify the tool was registered
        assert len(mcp_server.tools) == tool_count_before + 1
        assert "decorated_tool" in mcp_server.tools
    
    def test_resource_registration_decorator(self, mcp_server):
        """Test resource registration decorator"""
        # Test manual registration instead of decorator since decorator needs global server
        async def decorated_resource_func(request):
            return {"resource": "data"}
        
        # Manually register the resource
        resource_count_before = len(mcp_server.resources)
        mcp_server.register_resource(
            uri="test://decorated_resource",
            name="Decorated Resource",
            description="Resource registered with decorator"
        )(decorated_resource_func)
        
        # Verify the resource was registered
        assert len(mcp_server.resources) == resource_count_before + 1
        assert "test://decorated_resource" in mcp_server.resources
    
    def test_error_handling_invalid_method(self, test_client):
        """Test error handling for invalid methods"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "invalid_method"
        }
        
        response = test_client.post("/mcp/initialize", json=request_data)
        assert response.status_code == 400
    
    def test_error_handling_tool_not_found(self, test_client):
        """Test error handling for non-existent tools"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool",
                "arguments": {}
            }
        }
        
        response = test_client.post("/mcp/tools/call", json=request_data)
        assert response.status_code == 404
    
    def test_error_handling_resource_not_found(self, test_client):
        """Test error handling for non-existent resources"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "resources/read",
            "params": {
                "uri": "non://existent/resource"
            }
        }
        
        response = test_client.post("/mcp/resources/read", json=request_data)
        assert response.status_code == 404
    
    def test_global_mcp_server_functions(self, app):
        """Test global MCP server functions"""
        # Test initialization
        server = initialize_mcp_server(app)
        assert server is not None
        
        # Test getter
        retrieved_server = get_mcp_server()
        assert retrieved_server is server
        
        # Test error when not initialized
        import src.core.mcp_server as mcp_module
        original_server = mcp_module.mcp_server
        mcp_module.mcp_server = None
        
        try:
            with pytest.raises(RuntimeError, match="MCP server not initialized"):
                get_mcp_server()
        finally:
            # Restore original server
            mcp_module.mcp_server = original_server


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance"""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app"""
        app = FastAPI()
        return app
    
    @pytest.fixture
    def mcp_server(self, app):
        """Create test MCP server"""
        return MCPServer(app)
    
    @pytest.fixture
    def test_client(self, app, mcp_server):
        """Create test client"""
        return TestClient(app)
    
    def test_jsonrpc_format(self, test_client):
        """Test JSON-RPC 2.0 format compliance"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        response = test_client.post("/mcp/initialize", json=request_data)
        data = response.json()
        
        # Check JSON-RPC 2.0 compliance
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        assert data["id"] == request_data["id"]
        assert "result" in data or "error" in data
    
    def test_protocol_version_support(self, test_client):
        """Test protocol version support"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        response = test_client.post("/mcp/initialize", json=request_data)
        data = response.json()
        
        assert data["result"]["protocolVersion"] == "2024-11-05"
    
    def test_capabilities_structure(self, test_client):
        """Test capabilities structure compliance"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        response = test_client.post("/mcp/initialize", json=request_data)
        data = response.json()
        
        capabilities = data["result"]["capabilities"]
        
        # Check required capability structure
        assert "tools" in capabilities
        assert "resources" in capabilities
        assert "prompts" in capabilities
        
        # Check capability properties
        assert capabilities["tools"]["listChanged"] is True
        assert capabilities["resources"]["listChanged"] is True
        assert capabilities["prompts"]["listChanged"] is True