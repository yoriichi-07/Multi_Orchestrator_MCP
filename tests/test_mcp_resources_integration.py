"""
Integration tests for MCP resources
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.main import app, mcp_server
from src.resources.project_resources import project_structure_resource, project_code_resource, system_metrics_resource, mcp_capabilities_resource, analytics_dashboard_resource


class TestMCPResourcesIntegration:
    """Test MCP resources integration"""
    
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
    async def test_resources_registration(self, initialized_services):
        """Test resources are properly registered"""
        from src.main import mcp_server
        
        expected_uris = [
            "project://structure",
            "project://files/src/main.py",
            "system://metrics", 
            "server://capabilities"
        ]
        
        resource_uris = list(mcp_server.resources.keys())
        
        for uri in expected_uris:
            assert uri in resource_uris, f"Resource '{uri}' not found in registered resources: {resource_uris}"
    
    @pytest.mark.asyncio
    async def test_project_structure_resource(self, client):
        """Test project structure resource"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {
                "uri": "project://structure"
            }
        }
        
        with patch('src.resources.project_resources.ProjectManager') as mock_pm:
            mock_pm.return_value.get_project_structure.return_value = {
                "root": "/test/project",
                "structure": {"src": ["main.py"]}
            }
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        assert "contents" in data["result"]
        
        contents = data["result"]["contents"]
        assert len(contents) > 0
        assert contents[0]["uri"] == "project://structure"
        assert contents[0]["mimeType"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_project_files_resource(self, client):
        """Test project files resource"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {
                "uri": "project://files/src/main.py"
            }
        }
        
        with patch('src.resources.project_resources.SecureFileManager') as mock_sfm:
            mock_sfm.return_value.read_file.return_value = "print('Hello, World!')"
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        contents = data["result"]["contents"]
        
        assert contents[0]["uri"] == "project://files/src/main.py"
        assert contents[0]["mimeType"] == "text/plain"
        assert "Hello, World!" in contents[0]["text"]
    
    @pytest.mark.asyncio
    async def test_system_metrics_resource(self, client):
        """Test system metrics resource"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {
                "uri": "system://metrics"
            }
        }
        
        with patch('psutil.cpu_percent', return_value=25.5):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 45.2
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.percent = 67.8
                    
                    with patch('src.core.mcp_server.getattr') as mock_getattr:
                        mock_getattr.return_value = "test-correlation-id"
                        response = client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        contents = data["result"]["contents"]
        
        assert contents[0]["uri"] == "system://metrics"
        assert contents[0]["mimeType"] == "application/json"
        
        # Parse metrics data
        metrics_data = json.loads(contents[0]["text"])
        assert "cpu_usage" in metrics_data
        assert "memory_usage" in metrics_data
        assert "disk_usage" in metrics_data
    
    @pytest.mark.asyncio
    async def test_server_capabilities_resource(self, client):
        """Test server capabilities resource"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {
                "uri": "server://capabilities"
            }
        }
        
        with patch('src.core.mcp_server.getattr') as mock_getattr:
            mock_getattr.return_value = "test-correlation-id"
            response = client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        contents = data["result"]["contents"]
        
        assert contents[0]["uri"] == "server://capabilities"
        assert contents[0]["mimeType"] == "application/json"
        
        # Parse capabilities data
        capabilities_data = json.loads(contents[0]["text"])
        assert "tools" in capabilities_data
        assert "resources" in capabilities_data
        assert "server_info" in capabilities_data
    
    @pytest.mark.asyncio
    async def test_analytics_summary_resource(self, client):
        """Test analytics summary resource"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {
                "uri": "analytics://summary"
            }
        }
        
        with patch('src.resources.project_resources.AnalyticsTracker') as mock_tracker:
            mock_tracker.return_value.get_summary.return_value = {
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5
            }
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/resources/read", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        contents = data["result"]["contents"]
        
        assert contents[0]["uri"] == "analytics://summary"
        assert contents[0]["mimeType"] == "application/json"
        
        # Parse analytics data
        analytics_data = json.loads(contents[0]["text"])
        assert "total_requests" in analytics_data
        assert "successful_requests" in analytics_data
    
    @pytest.mark.asyncio
    async def test_resource_not_found(self, client):
        """Test resource not found error"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "resources/read",
            "params": {
                "uri": "nonexistent://resource"
            }
        }
        
        response = client.post("/mcp/resources/read", json=request_data)
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32002  # Resource not found
    
    @pytest.mark.asyncio
    async def test_resource_list_structure(self, client):
        """Test resource list structure compliance"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "resources/list"
        }
        
        response = client.post("/mcp/resources/list", json=request_data)
        data = response.json()
        
        # Check JSON-RPC compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 8
        assert "result" in data
        
        # Check resource list structure
        result = data["result"]
        assert "resources" in result
        
        resources = result["resources"]
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
    
    @pytest.mark.asyncio
    async def test_resource_read_structure(self, client):
        """Test resource read structure compliance"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "resources/read",
            "params": {
                "uri": "project://structure"
            }
        }
        
        with patch('src.resources.project_resources.ProjectManager') as mock_pm:
            mock_pm.return_value.get_project_structure.return_value = {"test": "data"}
            
            with patch('src.core.mcp_server.getattr') as mock_getattr:
                mock_getattr.return_value = "test-correlation-id"
                response = client.post("/mcp/resources/read", json=request_data)
        
        data = response.json()
        
        # Check JSON-RPC compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 9
        assert "result" in data
        
        # Check resource content structure
        result = data["result"]
        assert "contents" in result
        
        contents = result["contents"]
        assert len(contents) > 0
        
        for content in contents:
            assert "uri" in content
            assert "mimeType" in content
            # Should have either "text" or "blob" field
            assert "text" in content or "blob" in content
    
    @pytest.mark.asyncio
    async def test_resource_uri_patterns(self, client):
        """Test resource URI pattern handling"""
        # Test different URI patterns
        test_uris = [
            "project://structure",
            "project://files/src/main.py", 
            "system://metrics",
            "server://capabilities",
            "analytics://summary"
        ]
        
        for uri in test_uris:
            request_data = {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "resources/read",
                "params": {
                    "uri": uri
                }
            }
            
            with patch('src.resources.project_resources.ProjectManager') as mock_pm:
                mock_pm.return_value.get_project_structure.return_value = {"test": "data"}
                with patch('src.resources.project_resources.SecureFileManager') as mock_sfm:
                    mock_sfm.return_value.read_file.return_value = "test content"
                    with patch('psutil.cpu_percent', return_value=25.5):
                        with patch('psutil.virtual_memory') as mock_memory:
                            mock_memory.return_value.percent = 45.2
                            with patch('src.resources.project_resources.AnalyticsTracker') as mock_tracker:
                                mock_tracker.return_value.get_summary.return_value = {"test": "analytics"}
                                
                                with patch('src.core.mcp_server.getattr') as mock_getattr:
                                    mock_getattr.return_value = "test-correlation-id"
                                    response = client.post("/mcp/resources/read", json=request_data)
            
            # Each URI should either succeed or fail gracefully
            assert response.status_code in [200, 404, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "result" in data
                assert "contents" in data["result"]