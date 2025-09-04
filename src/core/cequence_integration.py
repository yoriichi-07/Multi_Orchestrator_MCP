"""
Cequence AI Gateway integration for enhanced observability
"""
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings

logger = structlog.get_logger()


class CequenceConfig:
    """Cequence AI Gateway configuration"""
    ANALYTICS_ENDPOINT = "https://api.cequence.ai/v1/analytics"
    SECURITY_ENDPOINT = "https://api.cequence.ai/v1/security"
    METRICS_ENDPOINT = "https://api.cequence.ai/v1/metrics"


class CequenceAnalytics:
    """Enhanced analytics client for Cequence integration"""
    
    def __init__(self, gateway_id: str, api_key: str):
        self.gateway_id = gateway_id
        self.api_key = api_key
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self._metrics_buffer: List[Dict[str, Any]] = []
        self._buffer_size = 100
        self._last_flush = datetime.utcnow()
    
    async def track_request(
        self, 
        request: Request,
        response: Response,
        correlation_id: str,
        auth_context: Optional[Dict[str, Any]] = None,
        processing_time_ms: float = 0
    ):
        """Track individual request metrics"""
        try:
            request_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "gateway_id": self.gateway_id,
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                    "headers": self._sanitize_headers(dict(request.headers)),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown")
                },
                "response": {
                    "status_code": response.status_code,
                    "headers": self._sanitize_headers(dict(response.headers)),
                    "processing_time_ms": processing_time_ms
                },
                "authentication": auth_context or {},
                "security": {
                    "threats_detected": [],
                    "risk_score": self._calculate_risk_score(request, auth_context)
                }
            }
            
            # Add to buffer
            self._metrics_buffer.append(request_data)
            
            # Flush if buffer is full or enough time has passed
            if (len(self._metrics_buffer) >= self._buffer_size or 
                (datetime.utcnow() - self._last_flush).seconds > 60):
                await self._flush_metrics()
            
            logger.info(
                "request_tracked",
                correlation_id=correlation_id,
                path=request.url.path,
                status_code=response.status_code,
                processing_time_ms=processing_time_ms,
                user_id=auth_context.get("user_id") if auth_context else None
            )
            
        except Exception as e:
            logger.error(
                "request_tracking_failed",
                correlation_id=correlation_id,
                error=str(e)
            )
    
    async def track_agent_operation(
        self,
        operation_type: str,
        agent_type: str,
        correlation_id: str,
        duration_ms: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track agent-specific operations"""
        try:
            operation_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "gateway_id": self.gateway_id,
                "operation": {
                    "type": operation_type,
                    "agent_type": agent_type,
                    "duration_ms": duration_ms,
                    "success": success,
                    "metadata": metadata or {}
                }
            }
            
            await self._send_metrics([operation_data], endpoint="operations")
            
            logger.info(
                "agent_operation_tracked",
                operation_type=operation_type,
                agent_type=agent_type,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                success=success
            )
            
        except Exception as e:
            logger.error(
                "agent_operation_tracking_failed",
                correlation_id=correlation_id,
                error=str(e)
            )
    
    async def track_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        correlation_id: str,
        client_ip: str,
        user_id: Optional[str] = None
    ):
        """Track security-related events"""
        try:
            security_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "gateway_id": self.gateway_id,
                "security_event": {
                    "type": event_type,
                    "severity": severity,
                    "description": description,
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "risk_indicators": self._analyze_security_risk(event_type, client_ip)
                }
            }
            
            await self._send_metrics([security_event], endpoint="security")
            
            logger.warning(
                "security_event_tracked",
                event_type=event_type,
                severity=severity,
                correlation_id=correlation_id,
                client_ip=client_ip,
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(
                "security_event_tracking_failed",
                correlation_id=correlation_id,
                error=str(e)
            )
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logging"""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", 
            "x-auth-token", "x-access-token"
        }
        
        return {
            key: "***REDACTED***" if key.lower() in sensitive_headers else value
            for key, value in headers.items()
        }
    
    def _calculate_risk_score(
        self, 
        request: Request, 
        auth_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate risk score for the request"""
        score = 0.0
        
        # Check for admin operations
        if "/admin/" in request.url.path:
            score += 0.3
        
        # Check for generation operations
        if "/generate" in request.url.path:
            score += 0.2
        
        # Check authentication status
        if not auth_context:
            score += 0.5
        elif auth_context.get("is_machine"):
            score += 0.1  # Machine tokens are slightly riskier
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB+
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _analyze_security_risk(self, event_type: str, client_ip: str) -> List[str]:
        """Analyze security risk indicators"""
        indicators = []
        
        if event_type in ["authentication_failure", "authorization_failure"]:
            indicators.append("auth_failure")
        
        if event_type == "rate_limit_exceeded":
            indicators.append("excessive_requests")
        
        # Check for known bad IP patterns (simplified)
        if client_ip.startswith("10.") or client_ip.startswith("192.168."):
            indicators.append("internal_network")
        elif client_ip.startswith("127."):
            indicators.append("localhost")
        
        return indicators
    
    async def _flush_metrics(self):
        """Flush accumulated metrics to Cequence"""
        if not self._metrics_buffer:
            return
        
        try:
            await self._send_metrics(self._metrics_buffer.copy())
            self._metrics_buffer.clear()
            self._last_flush = datetime.utcnow()
            
            logger.debug("metrics_flushed", count=len(self._metrics_buffer))
            
        except Exception as e:
            logger.error("metrics_flush_failed", error=str(e))
    
    async def _send_metrics(
        self, 
        metrics: List[Dict[str, Any]], 
        endpoint: str = "requests"
    ):
        """Send metrics to Cequence API"""
        if not self.gateway_id or not self.api_key:
            # Skip sending if not configured
            return
            
        try:
            url = f"{CequenceConfig.ANALYTICS_ENDPOINT}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "gateway_id": self.gateway_id,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self.http_client.post(
                url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
        except httpx.HTTPError as e:
            logger.error(
                "metrics_send_failed",
                endpoint=endpoint,
                error=str(e),
                metrics_count=len(metrics)
            )


class CequenceMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for Cequence integration"""
    
    def __init__(self, app, gateway_id: str, api_key: str):
        super().__init__(app)
        self.analytics = CequenceAnalytics(gateway_id, api_key)
    
    async def dispatch(self, request: Request, call_next):
        """Process request through Cequence analytics"""
        start_time = datetime.utcnow()
        correlation_id = str(uuid.uuid4())
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Get auth context if available
            auth_context = None
            if hasattr(request.state, 'auth_context'):
                auth_context = {
                    "user_id": request.state.auth_context.user_id,
                    "client_id": request.state.auth_context.client_id,
                    "is_machine": request.state.auth_context.is_machine,
                    "scopes": request.state.auth_context.scopes
                }
            
            # Track the request
            await self.analytics.track_request(
                request=request,
                response=response,
                correlation_id=correlation_id,
                auth_context=auth_context,
                processing_time_ms=processing_time
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Track error
            await self.analytics.track_security_event(
                event_type="request_processing_error",
                severity="error",
                description=str(e),
                correlation_id=correlation_id,
                client_ip=request.client.host if request.client else "unknown"
            )
            
            raise


# Global analytics instance
_cequence_analytics: Optional[CequenceAnalytics] = None


async def get_cequence_analytics() -> CequenceAnalytics:
    """Get singleton Cequence analytics instance"""
    global _cequence_analytics
    
    if _cequence_analytics is None:
        _cequence_analytics = CequenceAnalytics(
            gateway_id=settings.cequence_gateway_id,
            api_key=settings.cequence_api_key
        )
    
    return _cequence_analytics


async def track_agent_operation(
    operation_type: str,
    agent_type: str,
    correlation_id: str,
    duration_ms: float,
    success: bool,
    metadata: Optional[Dict[str, Any]] = None
):
    """Helper function to track agent operations"""
    analytics = await get_cequence_analytics()
    await analytics.track_agent_operation(
        operation_type=operation_type,
        agent_type=agent_type,
        correlation_id=correlation_id,
        duration_ms=duration_ms,
        success=success,
        metadata=metadata
    )


async def track_security_event(
    event_type: str,
    severity: str,
    description: str,
    correlation_id: str,
    client_ip: str,
    user_id: Optional[str] = None
):
    """Helper function to track security events"""
    analytics = await get_cequence_analytics()
    await analytics.track_security_event(
        event_type=event_type,
        severity=severity,
        description=description,
        correlation_id=correlation_id,
        client_ip=client_ip,
        user_id=user_id
    )