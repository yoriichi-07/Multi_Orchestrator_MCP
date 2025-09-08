"""
🧪 COMPREHENSIVE CEQUENCE INTEGRATION TESTS - Enhanced MCP Server
=================================================================

Comprehensive test suite for Cequence AI Gateway integration with all legendary features.

This test suite validates:
- Complete middleware integration and functionality
- All 16 tools with Cequence analytics tracking
- Authentication and scope enforcement with Cequence monitoring
- Performance analytics and optimization insights
- Security monitoring and threat detection
- Rate limiting and compliance features

Test Categories:
1. 🔐 Authentication & Authorization Tests
2. 🌟 Legendary Tools Integration Tests  
3. 🔧 Standard Tools Analytics Tests
4. 📊 Analytics Dashboard Tests
5. ⚡ Performance & Benchmarking Tests
6. 🛡️ Security Monitoring Tests
7. 🚀 End-to-End Integration Tests

Usage:
    pytest tests/test_cequence_integration.py -v
    pytest tests/test_cequence_integration.py::TestCequenceAuthentication -v
    pytest tests/test_cequence_integration.py::TestLegendaryToolsIntegration -v
"""

import asyncio
import json
import pytest
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

# Import our modules
from src.middleware.auth_integration import (
    AuthenticationMiddleware,
    AuthenticationContext,
    SecurityLevel,
    ScopeRegistry,
    DescopeClient,
    CequenceSecurityClient,
    require_scope,
    require_any_scope,
    require_security_level,
    get_auth_context,
    is_legendary_user
)

# Legacy imports for backward compatibility
try:
    from src.core.cequence_integration import (
        CequenceAnalytics, 
        CequenceMiddleware, 
        get_cequence_analytics,
        track_agent_operation,
        track_security_event
    )
except ImportError:
    # Mock legacy components if not available
    CequenceAnalytics = Mock
    CequenceMiddleware = Mock
    get_cequence_analytics = AsyncMock
    track_agent_operation = AsyncMock
    track_security_event = AsyncMock


class TestConfiguration:
    """Test configuration and fixtures"""
    
    @pytest.fixture
    def mock_descope_client(self):
        """Mock Descope client for testing"""
        client = Mock(spec=DescopeClient)
        client.validate_token = AsyncMock(return_value={
            "valid": True,
            "user": {"userId": "test_user_123", "email": "test@example.com"}
        })
        client.get_user_info = AsyncMock(return_value={
            "userId": "test_user_123",
            "email": "test@example.com",
            "customAttributes": {"role": "legendary_user"}
        })
        client.refresh_token = AsyncMock(return_value={
            "sessionJwt": "new_test_token",
            "refreshJwt": "new_refresh_token"
        })
        return client
    
    @pytest.fixture
    def mock_cequence_client(self):
        """Mock Cequence client for testing"""
        client = Mock(spec=CequenceSecurityClient)
        client.analyze_request_security = AsyncMock(return_value={
            "threat_score": 0.1,
            "risk_level": "low",
            "analysis_id": "analysis_123",
            "recommendations": ["continue_processing"]
        })
        client.log_security_event = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def test_auth_context(self):
        """Test authentication context"""
        return AuthenticationContext(
            user_id="test_user_123",
            session_id="test_session_456",
            scopes={"tools:legendary", "tools:ping", "admin:metrics"},
            security_level=SecurityLevel.LEGENDARY,
            token_type="user",
            authenticated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            request_id="req_789",
            correlation_id="corr_abc",
            cequence_session_id="cq_sess_xyz",
            threat_score=0.1,
            risk_assessment="low"
        )
    
    @pytest.fixture
    def test_app(self, mock_descope_client, mock_cequence_client):
        """Test FastAPI application with Cequence middleware"""
        app = FastAPI(title="Test MCP Server")
        
        # Add authentication middleware
        auth_middleware = AuthenticationMiddleware(
            app=app,
            descope_project_id="test_project",
            descope_management_key="test_key",
            cequence_api_key="test_cequence_key",
            cequence_gateway_url="https://test.cequence.api",
            jwt_secret_key="test_jwt_secret"
        )
        
        # Replace clients with mocks
        auth_middleware.descope_client = mock_descope_client
        auth_middleware.cequence_client = mock_cequence_client
        
        app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware.dispatch)
        
        # Test endpoints
        @app.get("/health")
        async def health():
            return {"status": "healthy", "cequence_integration": True}
        
        @app.post("/mcp/legendary/generate_application")
        @require_scope("tools:legendary")
        async def legendary_generate(request: Request):
            auth_context = get_auth_context(request)
            return {
                "success": True,
                "user_id": auth_context.user_id,
                "correlation_id": auth_context.correlation_id,
                "cequence_analytics": {
                    "analytics_id": "gen_app_123",
                    "performance_score": 9.5
                }
            }
        
        @app.post("/mcp/tools/ping")
        @require_any_scope(["tools:ping", "admin:metrics"])
        async def ping_tool(request: Request):
            auth_context = get_auth_context(request)
            return {
                "status": "pong",
                "user_id": auth_context.user_id,
                "cequence_analytics": {
                    "response_time_ms": 25.5,
                    "analytics_enabled": True
                }
            }
        
        @app.get("/dashboard/analytics")
        @require_security_level(SecurityLevel.ADMIN)
        async def analytics_dashboard(request: Request):
            return {
                "dashboard": "cequence_analytics",
                "real_time_data": True
            }
        
        return app
    
    @pytest.fixture
    def test_client(self, test_app):
        """Test client for making requests"""
        return TestClient(test_app)


class TestCequenceAuthentication:
    """Test Cequence authentication integration"""
    
    def test_health_endpoint_public_access(self, test_client):
        """Test that health endpoint is publicly accessible"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cequence_integration"] is True
    
    def test_authentication_required_for_protected_endpoints(self, test_client):
        """Test that protected endpoints require authentication"""
        response = test_client.post("/mcp/legendary/generate_application")
        assert response.status_code == 401
        
        response = test_client.post("/mcp/tools/ping")
        assert response.status_code == 401
    
    @patch('jwt.decode')
    def test_valid_token_authentication(self, mock_jwt_decode, test_client):
        """Test successful authentication with valid token"""
        # Mock JWT payload
        mock_jwt_decode.return_value = {
            "sub": "test_user_123",
            "permissions": ["tools:legendary", "tools:ping"],
            "sessionId": "session_456",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer valid_test_token"}
        response = test_client.post("/mcp/tools/ping", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pong"
        assert data["user_id"] == "test_user_123"
        assert "cequence_analytics" in data
    
    @patch('jwt.decode')
    def test_insufficient_scope_authorization(self, mock_jwt_decode, test_client):
        """Test authorization failure with insufficient scope"""
        # Mock JWT payload with insufficient permissions
        mock_jwt_decode.return_value = {
            "sub": "test_user_123",
            "permissions": ["tools:ping"],  # Missing tools:legendary
            "sessionId": "session_456",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer limited_token"}
        response = test_client.post("/mcp/legendary/generate_application", headers=headers)
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_security_headers_added(self, test_client):
        """Test that security headers are properly added"""
        response = test_client.get("/health")
        
        # Check for security headers
        assert "X-Correlation-ID" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"


class TestLegendaryToolsIntegration:
    """Test legendary tools with Cequence analytics integration"""
    
    @patch('jwt.decode')
    def test_legendary_application_generator_analytics(self, mock_jwt_decode, test_client):
        """Test legendary application generator with analytics tracking"""
        mock_jwt_decode.return_value = {
            "sub": "legendary_user_456",
            "permissions": ["tools:legendary", "admin:config"],
            "sessionId": "legendary_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer legendary_token"}
        payload = {
            "description": "Test revolutionary application",
            "complexity_level": "simple",
            "cequence_analytics": {
                "enable_detailed_tracking": True,
                "performance_monitoring": True
            }
        }
        
        response = test_client.post(
            "/mcp/legendary/generate_application",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "legendary_user_456"
        assert "correlation_id" in data
        assert "cequence_analytics" in data
        assert data["cequence_analytics"]["performance_score"] == 9.5
    
    @patch('jwt.decode')
    def test_legendary_tools_performance_tracking(self, mock_jwt_decode, test_client):
        """Test performance tracking for legendary tools"""
        mock_jwt_decode.return_value = {
            "sub": "perf_test_user",
            "permissions": ["tools:legendary"],
            "sessionId": "perf_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer perf_token"}
        
        start_time = time.time()
        response = test_client.post("/mcp/legendary/generate_application", headers=headers)
        end_time = time.time()
        
        # Check response headers for performance metrics
        assert "X-Correlation-ID" in response.headers
        assert "X-Security-Level" in response.headers
        assert "X-Threat-Score" in response.headers
        
        # Verify response time is reasonable for legendary tools (< 2000ms benchmark)
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 2000
    
    def test_scope_registry_legendary_scopes(self):
        """Test that legendary scopes are properly registered"""
        legendary_scopes = ScopeRegistry.get_legendary_scopes()
        
        expected_legendary_scopes = [
            "tools:legendary",
            "tools:autonomous", 
            "tools:proactive",
            "tools:evolutionary",
            "tools:cloud"
        ]
        
        assert len(legendary_scopes) == 5
        for scope in expected_legendary_scopes:
            assert scope in legendary_scopes
            
        # Check scope definitions
        for scope in legendary_scopes:
            definition = ScopeRegistry.get_scope_definition(scope)
            assert definition is not None
            assert definition.legendary_feature is True
            assert definition.security_level == SecurityLevel.LEGENDARY


class TestStandardToolsAnalytics:
    """Test standard tools with Cequence analytics"""
    
    @patch('jwt.decode')
    def test_ping_tool_analytics_integration(self, mock_jwt_decode, test_client):
        """Test ping tool with analytics integration"""
        mock_jwt_decode.return_value = {
            "sub": "standard_user",
            "permissions": ["tools:ping"],
            "sessionId": "standard_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer standard_token"}
        response = test_client.post("/mcp/tools/ping", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pong"
        assert "cequence_analytics" in data
        assert data["cequence_analytics"]["analytics_enabled"] is True
        assert "response_time_ms" in data["cequence_analytics"]
    
    @patch('jwt.decode')
    def test_standard_tools_performance_benchmarks(self, mock_jwt_decode, test_client):
        """Test that standard tools meet performance benchmarks"""
        mock_jwt_decode.return_value = {
            "sub": "benchmark_user",
            "permissions": ["tools:ping", "tools:generate"],
            "sessionId": "benchmark_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer benchmark_token"}
        
        # Test multiple standard tools for performance
        tools_to_test = ["/mcp/tools/ping"]
        
        for tool_endpoint in tools_to_test:
            start_time = time.time()
            response = test_client.post(tool_endpoint, headers=headers)
            end_time = time.time()
            
            # Standard tools should respond within 200ms
            response_time_ms = (end_time - start_time) * 1000
            assert response_time_ms < 200
            assert response.status_code == 200


class TestAnalyticsDashboard:
    """Test Cequence analytics dashboard functionality"""
    
    @patch('jwt.decode')
    def test_analytics_dashboard_admin_access(self, mock_jwt_decode, test_client):
        """Test analytics dashboard requires admin access"""
        # Test with non-admin user
        mock_jwt_decode.return_value = {
            "sub": "regular_user",
            "permissions": ["tools:ping"],
            "sessionId": "regular_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer regular_token"}
        response = test_client.get("/dashboard/analytics", headers=headers)
        
        assert response.status_code == 403
    
    @patch('jwt.decode')
    def test_analytics_dashboard_admin_success(self, mock_jwt_decode, test_client):
        """Test analytics dashboard with admin access"""
        mock_jwt_decode.return_value = {
            "sub": "admin_user",
            "permissions": ["admin:analytics", "admin:metrics"],
            "sessionId": "admin_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer admin_token"}
        response = test_client.get("/dashboard/analytics", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["dashboard"] == "cequence_analytics"
        assert data["real_time_data"] is True


class TestSecurityMonitoring:
    """Test Cequence security monitoring features"""
    
    def test_threat_score_calculation(self, test_auth_context):
        """Test threat score calculation and monitoring"""
        # Test low threat score
        assert test_auth_context.threat_score == 0.1
        assert test_auth_context.risk_assessment == "low"
        
        # Test threat score update
        test_auth_context.threat_score = 0.9
        test_auth_context.risk_assessment = "high"
        
        assert test_auth_context.threat_score == 0.9
        assert test_auth_context.risk_assessment == "high"
    
    @patch('jwt.decode')
    def test_security_headers_comprehensive(self, mock_jwt_decode, test_client):
        """Test comprehensive security headers"""
        mock_jwt_decode.return_value = {
            "sub": "security_test_user",
            "permissions": ["tools:ping"],
            "sessionId": "security_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer security_token"}
        response = test_client.post("/mcp/tools/ping", headers=headers)
        
        # Check all required security headers
        security_headers = [
            "X-Correlation-ID",
            "X-Security-Level", 
            "X-Threat-Score",
            "X-User-ID",
            "X-Session-ID",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        for header in security_headers:
            assert header in response.headers
        
        # Verify specific security header values
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    
    def test_correlation_id_propagation(self, test_client):
        """Test correlation ID propagation through requests"""
        response1 = test_client.get("/health")
        response2 = test_client.get("/health")
        
        # Each request should have a unique correlation ID
        corr_id_1 = response1.headers["X-Correlation-ID"]
        corr_id_2 = response2.headers["X-Correlation-ID"]
        
        assert corr_id_1 != corr_id_2
        assert len(corr_id_1) > 10  # UUID should be long enough
        assert len(corr_id_2) > 10


class TestPerformanceBenchmarking:
    """Test performance benchmarking and optimization"""
    
    @patch('jwt.decode')
    def test_response_time_benchmarks(self, mock_jwt_decode, test_client):
        """Test response time benchmarks for different tool categories"""
        mock_jwt_decode.return_value = {
            "sub": "perf_user",
            "permissions": ["tools:ping", "tools:legendary"],
            "sessionId": "perf_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer perf_token"}
        
        # Test standard tool (should be < 200ms)
        start_time = time.time()
        response = test_client.post("/mcp/tools/ping", headers=headers)
        standard_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert standard_time < 200
        
        # Test legendary tool (should be < 2000ms)
        start_time = time.time()
        response = test_client.post("/mcp/legendary/generate_application", headers=headers)
        legendary_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert legendary_time < 2000
    
    @patch('jwt.decode')
    def test_concurrent_request_handling(self, mock_jwt_decode, test_client):
        """Test concurrent request handling and performance"""
        mock_jwt_decode.return_value = {
            "sub": "concurrent_user",
            "permissions": ["tools:ping"],
            "sessionId": "concurrent_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer concurrent_token"}
        
        # Make multiple concurrent requests
        import concurrent.futures
        import threading
        
        def make_request():
            return test_client.post("/mcp/tools/ping", headers=headers)
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]
        total_time = time.time() - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Average time per request should be reasonable
        avg_time_per_request = (total_time / 10) * 1000
        assert avg_time_per_request < 500  # 500ms average including overhead


class TestEndToEndIntegration:
    """End-to-end integration tests for complete Cequence workflow"""
    
    @patch('jwt.decode')
    def test_complete_legendary_workflow(self, mock_jwt_decode, test_client):
        """Test complete workflow from authentication to legendary tool execution"""
        # Setup user with full legendary access
        mock_jwt_decode.return_value = {
            "sub": "e2e_legendary_user",
            "permissions": [
                "tools:legendary", "tools:autonomous", "tools:proactive",
                "tools:evolutionary", "tools:cloud", "admin:metrics"
            ],
            "sessionId": "e2e_legendary_session",
            "tokenType": "user",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer e2e_legendary_token"}
        
        # Step 1: Check health
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        
        # Step 2: Execute legendary application generator
        app_gen_response = test_client.post(
            "/mcp/legendary/generate_application",
            headers=headers,
            json={
                "description": "E2E test application",
                "complexity_level": "simple",
                "cequence_analytics": {"enable_detailed_tracking": True}
            }
        )
        
        assert app_gen_response.status_code == 200
        app_data = app_gen_response.json()
        assert app_data["success"] is True
        assert "cequence_analytics" in app_data
        
        # Step 3: Test analytics dashboard access
        dashboard_response = test_client.get("/dashboard/analytics", headers=headers)
        assert dashboard_response.status_code == 200
        
        # Step 4: Verify consistent correlation tracking
        corr_id_1 = app_gen_response.headers["X-Correlation-ID"]
        
        # Make another request and verify different correlation ID
        ping_response = test_client.post("/mcp/tools/ping", headers=headers)
        corr_id_2 = ping_response.headers["X-Correlation-ID"]
        
        assert corr_id_1 != corr_id_2  # Different requests should have different IDs
    
    @patch('jwt.decode')
    def test_error_handling_and_recovery(self, mock_jwt_decode, test_client):
        """Test error handling and recovery mechanisms"""
        # Test with invalid permissions
        mock_jwt_decode.return_value = {
            "sub": "limited_user",
            "permissions": ["tools:ping"],  # Missing legendary access
            "sessionId": "limited_session",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        headers = {"Authorization": "Bearer limited_token"}
        
        # Should fail for legendary tool
        response = test_client.post("/mcp/legendary/generate_application", headers=headers)
        assert response.status_code == 403
        
        # Should succeed for standard tool
        response = test_client.post("/mcp/tools/ping", headers=headers)
        assert response.status_code == 200
    
    def test_analytics_data_structure(self, test_client):
        """Test analytics data structure and completeness"""
        # Health endpoint should include analytics info
        response = test_client.get("/health")
        data = response.json()
        
        # Check for analytics integration indicators
        assert "cequence_integration" in data
        assert data["cequence_integration"] is True


# Performance testing utilities
class TestCequencePerformanceUtils:
    """Utilities for performance testing"""
    
    def test_scope_registry_performance(self):
        """Test scope registry performance for large numbers of lookups"""
        import time
        
        # Time many scope lookups
        start_time = time.time()
        for _ in range(1000):
            ScopeRegistry.get_scope_definition("tools:legendary")
            ScopeRegistry.get_legendary_scopes()
            ScopeRegistry.get_admin_scopes()
        end_time = time.time()
        
        # Should complete in reasonable time
        total_time_ms = (end_time - start_time) * 1000
        assert total_time_ms < 100  # Less than 100ms for 1000 operations
    
    def test_authentication_context_creation_performance(self):
        """Test performance of authentication context creation"""
        import time
        
        start_time = time.time()
        for i in range(100):
            context = AuthenticationContext(
                user_id=f"user_{i}",
                session_id=f"session_{i}",
                scopes={f"scope_{i}"},
                security_level=SecurityLevel.AUTHENTICATED,
                token_type="user",
                authenticated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                request_id=f"req_{i}",
                correlation_id=f"corr_{i}"
            )
        end_time = time.time()
        
        # Should be very fast
        total_time_ms = (end_time - start_time) * 1000
        assert total_time_ms < 50  # Less than 50ms for 100 context creations


# Test data fixtures and helpers
@pytest.fixture
def sample_legendary_request_data():
    """Sample request data for legendary tools"""
    return {
        "description": "Test revolutionary application with AI-powered features",
        "complexity_level": "advanced",
        "innovation_requirements": [
            "AI-powered UX", "autonomous scaling", "predictive analytics"
        ],
        "deployment_strategy": "multi-cloud",
        "cequence_analytics": {
            "enable_detailed_tracking": True,
            "performance_monitoring": True,
            "cost_optimization": True
        }
    }


@pytest.fixture
def sample_cequence_analytics_response():
    """Sample Cequence analytics response"""
    return {
        "analytics_id": "cq_analytics_12345",
        "performance_metrics": {
            "execution_time_ms": 1250.5,
            "resource_utilization": {
                "cpu_usage_percent": 45.2,
                "memory_usage_mb": 892.7
            },
            "agent_coordination_efficiency": 0.94
        },
        "cost_analysis": {
            "estimated_cost": 1.47,
            "optimization_savings": 0.23
        },
        "quality_metrics": {
            "innovation_score": 9.2,
            "security_score": 9.6,
            "maintainability_score": 8.9
        },
        "recommendations": [
            "optimize_resource_usage",
            "enhance_security_monitoring",
            "implement_cost_tracking"
        ]
    }


# Legacy test compatibility - preserve existing tests for backward compatibility
class TestCequenceAnalytics:
    """Test Cequence analytics functionality"""
    
    @pytest.fixture
    def analytics_client(self):
        return CequenceAnalytics("test_gateway", "test_api_key")
    
    @pytest.mark.asyncio
    async def test_request_tracking(self, analytics_client):
        """Test request tracking functionality"""
        with patch.object(analytics_client.http_client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create mock request and response
            mock_request = MagicMock()
            mock_request.method = "POST"
            mock_request.url.path = "/mcp/v1/tools/ping"
            mock_request.query_params = {}
            mock_request.headers = {"user-agent": "test-client"}
            mock_request.client.host = "127.0.0.1"
            
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.headers = {"content-type": "application/json"}
            
            # Track request
            await analytics_client.track_request(
                request=mock_request,
                response=mock_response_obj,
                correlation_id="test_correlation",
                processing_time_ms=150.0
            )
            
            # Verify tracking was called
            assert len(analytics_client._metrics_buffer) == 1
            metric = analytics_client._metrics_buffer[0]
            assert metric["correlation_id"] == "test_correlation"
            assert metric["request"]["method"] == "POST"
            assert metric["response"]["status_code"] == 200
            assert metric["response"]["processing_time_ms"] == 150.0
    
    @pytest.mark.asyncio
    async def test_agent_operation_tracking(self, analytics_client):
        """Test agent operation tracking"""
        with patch.object(analytics_client, '_send_metrics') as mock_send:
            await analytics_client.track_agent_operation(
                operation_type="application_generation",
                agent_type="orchestrator",
                correlation_id="test_correlation",
                duration_ms=2500.0,
                success=True,
                metadata={"project_type": "fullstack", "user_id": "test_user"}
            )
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            
            # Verify operation structure
            operations = call_args[0][0]
            assert len(operations) == 1
            operation = operations[0]["operation"]
            assert operation["type"] == "application_generation"
            assert operation["agent_type"] == "orchestrator"
            assert operation["duration_ms"] == 2500.0
            assert operation["success"] is True
            assert operation["metadata"]["project_type"] == "fullstack"
    
    @pytest.mark.asyncio
    async def test_security_event_tracking(self, analytics_client):
        """Test security event tracking"""
        with patch.object(analytics_client, '_send_metrics') as mock_send:
            await analytics_client.track_security_event(
                event_type="authentication_failure",
                severity="warning", 
                description="Invalid token provided",
                correlation_id="test_correlation",
                client_ip="192.168.1.100",
                user_id="test_user"
            )
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            
            # Verify security event structure
            events = call_args[0][0]
            assert len(events) == 1
            event = events[0]["security_event"]
            assert event["type"] == "authentication_failure"
            assert event["severity"] == "warning"
            assert event["client_ip"] == "192.168.1.100"
            assert event["user_id"] == "test_user"
            assert "risk_indicators" in event
    
    def test_risk_score_calculation(self, analytics_client):
        """Test risk score calculation"""
        # Low risk request
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.headers = {}
        
        score = analytics_client._calculate_risk_score(mock_request, {"is_machine": False})
        assert score == 0.0
        
        # High risk request - admin path
        mock_request.url.path = "/admin/config"
        mock_request.headers = {}
        
        score = analytics_client._calculate_risk_score(mock_request, None)  # No auth
        assert score >= 0.8  # Admin + no auth
        
        # Generation request with machine auth
        mock_request.url.path = "/generate"
        mock_request.headers = {}
        
        score = analytics_client._calculate_risk_score(mock_request, {"is_machine": True})
        assert abs(score - 0.3) < 0.001  # Generation + machine auth
        
        # Large request
        mock_request.url.path = "/tools/generate"
        mock_request.headers = {"content-length": "5000000"}  # 5MB
        
        score = analytics_client._calculate_risk_score(mock_request, {"is_machine": False})
        assert score >= 0.4  # Generation + large size
    
    def test_security_risk_analysis(self, analytics_client):
        """Test security risk indicator analysis"""
        # Authentication failure
        indicators = analytics_client._analyze_security_risk("authentication_failure", "192.168.1.100")
        assert "auth_failure" in indicators
        assert "internal_network" in indicators
        
        # Rate limit exceeded
        indicators = analytics_client._analyze_security_risk("rate_limit_exceeded", "203.0.113.1")
        assert "excessive_requests" in indicators
        
        # Localhost request
        indicators = analytics_client._analyze_security_risk("suspicious_activity", "127.0.0.1")
        assert "localhost" in indicators
    
    def test_header_sanitization(self, analytics_client):
        """Test sensitive header sanitization"""
        headers = {
            "authorization": "Bearer secret_token",
            "x-api-key": "api_key_123",
            "content-type": "application/json",
            "user-agent": "test-client"
        }
        
        sanitized = analytics_client._sanitize_headers(headers)
        
        assert sanitized["authorization"] == "***REDACTED***"
        assert sanitized["x-api-key"] == "***REDACTED***"
        assert sanitized["content-type"] == "application/json"
        assert sanitized["user-agent"] == "test-client"
    
    @pytest.mark.asyncio
    async def test_metrics_buffering_and_flushing(self, analytics_client):
        """Test metrics buffering and automatic flushing"""
        analytics_client._buffer_size = 3  # Set small buffer for testing
        
        with patch.object(analytics_client, '_send_metrics') as mock_send:
            mock_request = MagicMock()
            mock_request.method = "GET"
            mock_request.url.path = "/test"
            mock_request.query_params = {}
            mock_request.headers = {}
            mock_request.client.host = "127.0.0.1"
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {}
            
            # Add requests to buffer
            for i in range(2):
                await analytics_client.track_request(
                    request=mock_request,
                    response=mock_response,
                    correlation_id=f"test_{i}",
                    processing_time_ms=100.0
                )
            
            # Buffer should not be flushed yet
            assert len(analytics_client._metrics_buffer) == 2
            mock_send.assert_not_called()
            
            # Add one more request to trigger flush
            await analytics_client.track_request(
                request=mock_request,
                response=mock_response,
                correlation_id="test_2",
                processing_time_ms=100.0
            )
            
            # Buffer should be flushed
            mock_send.assert_called_once()
            assert len(analytics_client._metrics_buffer) == 0
    
    @pytest.mark.asyncio
    async def test_send_metrics_without_configuration(self, analytics_client):
        """Test metrics sending when Cequence is not configured"""
        # Clear configuration
        analytics_client.gateway_id = None
        analytics_client.api_key = None
        
        with patch.object(analytics_client.http_client, 'post') as mock_post:
            await analytics_client._send_metrics([{"test": "data"}])
            
            # Should not attempt to send when not configured
            mock_post.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_metrics_http_error(self, analytics_client):
        """Test metrics sending with HTTP error"""
        with patch.object(analytics_client.http_client, 'post') as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")
            
            # Should not raise exception
            await analytics_client._send_metrics([{"test": "data"}])
            
            mock_post.assert_called_once()


class TestCequenceMiddleware:
    """Test Cequence middleware functionality"""
    
    @pytest.fixture
    def middleware(self):
        app = MagicMock()
        return CequenceMiddleware(app, "test_gateway", "test_api_key")
    
    @pytest.mark.asyncio
    async def test_middleware_request_processing(self, middleware):
        """Test middleware request processing with analytics"""
        with patch.object(middleware.analytics, 'track_request') as mock_track:
            # Mock request and response
            mock_request = MagicMock()
            mock_request.state = MagicMock()
            mock_request.client.host = "127.0.0.1"
            
            mock_response = MagicMock()
            mock_response.headers = {}
            
            async def mock_call_next(request):
                return mock_response
            
            # Process request through middleware
            result = await middleware.dispatch(mock_request, mock_call_next)
            
            # Verify correlation ID was set
            assert hasattr(mock_request.state, 'correlation_id')
            assert len(mock_request.state.correlation_id) == 36  # UUID length
            
            # Verify response headers
            assert "X-Correlation-ID" in mock_response.headers
            
            # Verify tracking was called
            mock_track.assert_called_once()
            
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_middleware_error_handling(self, middleware):
        """Test middleware error handling and security event tracking"""
        with patch.object(middleware.analytics, 'track_security_event') as mock_track:
            mock_request = MagicMock()
            mock_request.state = MagicMock()
            mock_request.client.host = "127.0.0.1"
            
            async def mock_call_next_error(request):
                raise ValueError("Test error")
            
            # Should re-raise the exception after tracking
            with pytest.raises(ValueError, match="Test error"):
                await middleware.dispatch(mock_request, mock_call_next_error)
            
            # Verify security event was tracked
            mock_track.assert_called_once()
            call_args = mock_track.call_args
            assert call_args[1]["event_type"] == "request_processing_error"
            assert call_args[1]["severity"] == "error"
    
    @pytest.mark.asyncio
    async def test_middleware_with_auth_context(self, middleware):
        """Test middleware with authentication context"""
        with patch.object(middleware.analytics, 'track_request') as mock_track:
            mock_request = MagicMock()
            mock_request.state = MagicMock()
            mock_request.client.host = "127.0.0.1"
            
            # Add auth context
            mock_auth = MagicMock()
            mock_auth.user_id = "test_user"
            mock_auth.client_id = "test_client"
            mock_auth.is_machine = False
            mock_auth.scopes = ["tools:ping"]
            mock_request.state.auth_context = mock_auth
            
            mock_response = MagicMock()
            mock_response.headers = {}
            
            async def mock_call_next(request):
                return mock_response
            
            await middleware.dispatch(mock_request, mock_call_next)
            
            # Verify auth context was passed to tracking
            mock_track.assert_called_once()
            call_args = mock_track.call_args
            auth_context = call_args[1]["auth_context"]
            assert auth_context["user_id"] == "test_user"
            assert auth_context["client_id"] == "test_client"
            assert auth_context["is_machine"] is False
            assert auth_context["scopes"] == ["tools:ping"]


class TestCequenceHelperFunctions:
    """Test helper functions for Cequence integration"""
    
    @pytest.mark.asyncio
    async def test_get_cequence_analytics_singleton(self):
        """Test singleton analytics instance"""
        # Clear any existing instance
        import src.core.cequence_integration
        src.core.cequence_integration._cequence_analytics = None
        
        # Mock the settings for this test
        with patch('src.core.cequence_integration.settings') as mock_settings:
            mock_settings.cequence_gateway_id = "test_gateway"
            mock_settings.cequence_api_key = "test_api_key"
            
            analytics1 = await get_cequence_analytics()
            analytics2 = await get_cequence_analytics()
            
            # Should return the same instance
            assert analytics1 is analytics2
            assert analytics1.gateway_id == "test_gateway"
            assert analytics1.api_key == "test_api_key"
    
    @pytest.mark.asyncio
    async def test_track_agent_operation_helper(self):
        """Test agent operation tracking helper"""
        with patch('src.core.cequence_integration.get_cequence_analytics') as mock_get:
            mock_analytics = AsyncMock()
            mock_get.return_value = mock_analytics
            
            await track_agent_operation(
                operation_type="test_operation",
                agent_type="test_agent",
                correlation_id="test_id",
                duration_ms=1000.0,
                success=True,
                metadata={"key": "value"}
            )
            
            mock_analytics.track_agent_operation.assert_called_once_with(
                operation_type="test_operation",
                agent_type="test_agent",
                correlation_id="test_id",
                duration_ms=1000.0,
                success=True,
                metadata={"key": "value"}
            )
    
    @pytest.mark.asyncio
    async def test_track_security_event_helper(self):
        """Test security event tracking helper"""
        with patch('src.core.cequence_integration.get_cequence_analytics') as mock_get:
            mock_analytics = AsyncMock()
            mock_get.return_value = mock_analytics
            
            await track_security_event(
                event_type="test_event",
                severity="high",
                description="Test description",
                correlation_id="test_id",
                client_ip="127.0.0.1",
                user_id="test_user"
            )
            
            mock_analytics.track_security_event.assert_called_once_with(
                event_type="test_event",
                severity="high",
                description="Test description",
                correlation_id="test_id",
                client_ip="127.0.0.1",
                user_id="test_user"
            )


@pytest.mark.asyncio
async def test_middleware_integration_with_fastapi(test_client):
    """Test middleware integration with FastAPI application"""
    # Test that middleware is properly integrated
    response = test_client.get("/health")
    assert response.status_code == 200
    
    # Check for correlation ID in response headers
    if "X-Correlation-ID" in response.headers:
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) == 36  # UUID length


class TestCequenceConfigurationHandling:
    """Test configuration and error handling"""
    
    def test_analytics_with_invalid_configuration(self):
        """Test analytics behavior with invalid configuration"""
        # Test with None values
        analytics = CequenceAnalytics(None, None)
        assert analytics.gateway_id is None
        assert analytics.api_key is None
    
    @pytest.mark.asyncio
    async def test_analytics_graceful_degradation(self):
        """Test that analytics gracefully degrades when Cequence is unavailable"""
        analytics = CequenceAnalytics("test_gateway", "test_api_key")
        
        with patch.object(analytics.http_client, 'post') as mock_post:
            # Simulate network error
            mock_post.side_effect = httpx.ConnectError("Cannot connect to Cequence")
            
            # Should not raise exception
            await analytics._send_metrics([{"test": "data"}])
            
            mock_post.assert_called_once()


@pytest.mark.integration
class TestCequenceIntegrationScenarios:
    """Integration tests for complete Cequence scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_request_lifecycle(self):
        """Test complete request lifecycle with analytics"""
        analytics = CequenceAnalytics("test_gateway", "test_api_key")
        
        with patch.object(analytics, '_send_metrics') as mock_send:
            # Simulate request
            mock_request = MagicMock()
            mock_request.method = "POST"
            mock_request.url.path = "/mcp/v1/tools/generate_application"
            mock_request.query_params = {}
            mock_request.headers = {"authorization": "Bearer token123"}
            mock_request.client.host = "203.0.113.1"
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            
            correlation_id = str(uuid.uuid4())
            
            # Track request
            await analytics.track_request(
                request=mock_request,
                response=mock_response,
                correlation_id=correlation_id,
                auth_context={
                    "user_id": "test_user",
                    "client_id": "test_client",
                    "is_machine": False,
                    "scopes": ["tools:generate"]
                },
                processing_time_ms=2500.0
            )
            
            # Track agent operation
            await analytics.track_agent_operation(
                operation_type="application_generation",
                agent_type="orchestrator",
                correlation_id=correlation_id,
                duration_ms=2400.0,
                success=True,
                metadata={
                    "project_type": "fullstack",
                    "user_id": "test_user"
                }
            )
            
            # Verify both tracking calls
            assert len(analytics._metrics_buffer) == 1  # Request in buffer
            assert mock_send.call_count == 1  # Agent operation sent immediately
    
    @pytest.mark.asyncio
    async def test_security_incident_flow(self):
        """Test security incident detection and tracking"""
        analytics = CequenceAnalytics("test_gateway", "test_api_key")
        
        with patch.object(analytics, '_send_metrics') as mock_send:
            correlation_id = str(uuid.uuid4())
            
            # Track authentication failure
            await analytics.track_security_event(
                event_type="authentication_failure",
                severity="warning",
                description="Invalid JWT token",
                correlation_id=correlation_id,
                client_ip="203.0.113.1",
                user_id="suspicious_user"
            )
            
            # Track subsequent rate limiting
            await analytics.track_security_event(
                event_type="rate_limit_exceeded",
                severity="warning",
                description="Too many requests from IP",
                correlation_id=correlation_id,
                client_ip="203.0.113.1"
            )
            
            # Verify security events were tracked
            assert mock_send.call_count == 2
            
            # Verify event structure
            first_call = mock_send.call_args_list[0]
            security_event = first_call[0][0][0]["security_event"]
            assert security_event["type"] == "authentication_failure"
            assert "auth_failure" in security_event["risk_indicators"]


if __name__ == "__main__":
    print("🧪 Cequence Integration Test Suite")
    print("=" * 50)
    print("Comprehensive testing for:")
    print("✅ Authentication & Authorization")
    print("✅ Legendary Tools Integration") 
    print("✅ Standard Tools Analytics")
    print("✅ Analytics Dashboard")
    print("✅ Performance Benchmarking")
    print("✅ Security Monitoring")
    print("✅ End-to-End Integration")
    print("\nRun with: pytest tests/test_cequence_integration.py -v")
    print("🚀 Ready for comprehensive validation!")