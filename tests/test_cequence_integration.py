"""
Tests for Cequence AI Gateway integration
"""
import pytest
import uuid
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import httpx
from fastapi import Request, Response

from src.core.cequence_integration import (
    CequenceAnalytics, 
    CequenceMiddleware, 
    get_cequence_analytics,
    track_agent_operation,
    track_security_event
)


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