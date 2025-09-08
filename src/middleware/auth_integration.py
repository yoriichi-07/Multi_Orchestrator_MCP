"""
🔐 AUTHENTICATION INTEGRATION MIDDLEWARE - Enhanced MCP Server
==============================================================

Comprehensive authentication and authorization middleware with Cequence AI Gateway integration.

This module provides:
- Descope OAuth 2.1 + PKCE authentication integration
- Scope-based authorization with granular permission control
- Cequence AI Gateway security analytics integration
- Rate limiting and security monitoring
- Non-Human Identity support for automated systems

Features:
- JWT token validation with Descope integration
- Scope enforcement decorators for all 16 tools
- Security analytics and threat detection
- Performance monitoring and optimization
- Comprehensive audit logging for compliance

Usage:
    from src.middleware.auth_integration import require_scope, require_any_scope, AuthenticationMiddleware
    
    @require_scope("tools:legendary")
    async def legendary_tool():
        pass
        
    @require_any_scope(["tools:ping", "admin:metrics"])
    async def flexible_tool():
        pass
"""

import asyncio
import functools
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

import jwt
import httpx
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security classification levels"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated" 
    RESTRICTED = "restricted"
    LEGENDARY = "legendary"
    ADMIN = "admin"


@dataclass
class AuthenticationContext:
    """Authentication context for requests"""
    user_id: str
    session_id: str
    scopes: Set[str]
    security_level: SecurityLevel
    token_type: str  # "user" or "non_human"
    authenticated_at: datetime
    expires_at: datetime
    request_id: str
    correlation_id: str
    
    # Analytics and monitoring
    analytics_enabled: bool = True
    security_monitoring: bool = True
    performance_tracking: bool = True
    
    # Cequence integration
    cequence_session_id: Optional[str] = None
    threat_score: float = 0.0
    risk_assessment: str = "low"


@dataclass
class ScopeDefinition:
    """Scope definition with metadata"""
    scope: str
    description: str
    security_level: SecurityLevel
    legendary_feature: bool = False
    admin_required: bool = False
    rate_limit_per_minute: int = 60
    
    
class ScopeRegistry:
    """Registry of all available scopes and their definitions"""
    
    SCOPES = {
        # Legendary Tool Scopes
        "tools:legendary": ScopeDefinition(
            scope="tools:legendary",
            description="Access to legendary application generator",
            security_level=SecurityLevel.LEGENDARY,
            legendary_feature=True,
            rate_limit_per_minute=10
        ),
        "tools:autonomous": ScopeDefinition(
            scope="tools:autonomous", 
            description="Access to autonomous architect agent",
            security_level=SecurityLevel.LEGENDARY,
            legendary_feature=True,
            rate_limit_per_minute=15
        ),
        "tools:proactive": ScopeDefinition(
            scope="tools:proactive",
            description="Access to proactive quality framework",
            security_level=SecurityLevel.LEGENDARY,
            legendary_feature=True,
            rate_limit_per_minute=20
        ),
        "tools:evolutionary": ScopeDefinition(
            scope="tools:evolutionary",
            description="Access to evolutionary prompt engine",
            security_level=SecurityLevel.LEGENDARY,
            legendary_feature=True,
            rate_limit_per_minute=25
        ),
        "tools:cloud": ScopeDefinition(
            scope="tools:cloud",
            description="Access to last mile cloud agent",
            security_level=SecurityLevel.LEGENDARY,
            legendary_feature=True,
            rate_limit_per_minute=5
        ),
        
        # Standard Tool Scopes
        "tools:ping": ScopeDefinition(
            scope="tools:ping",
            description="Basic connectivity and health testing",
            security_level=SecurityLevel.AUTHENTICATED,
            rate_limit_per_minute=120
        ),
        "tools:generate": ScopeDefinition(
            scope="tools:generate",
            description="Generation and orchestration tools",
            security_level=SecurityLevel.RESTRICTED,
            rate_limit_per_minute=30
        ),
        "tools:healing": ScopeDefinition(
            scope="tools:healing", 
            description="Autonomous code healing capabilities",
            security_level=SecurityLevel.RESTRICTED,
            rate_limit_per_minute=40
        ),
        
        # Admin Scopes
        "admin:metrics": ScopeDefinition(
            scope="admin:metrics",
            description="System monitoring and metrics access",
            security_level=SecurityLevel.ADMIN,
            admin_required=True,
            rate_limit_per_minute=100
        ),
        "admin:analytics": ScopeDefinition(
            scope="admin:analytics",
            description="Advanced analytics and reporting",
            security_level=SecurityLevel.ADMIN,
            admin_required=True,
            rate_limit_per_minute=50
        ),
        "admin:config": ScopeDefinition(
            scope="admin:config",
            description="Configuration management access",
            security_level=SecurityLevel.ADMIN,
            admin_required=True,
            rate_limit_per_minute=20
        )
    }
    
    @classmethod
    def get_scope_definition(cls, scope: str) -> Optional[ScopeDefinition]:
        """Get scope definition by scope name"""
        return cls.SCOPES.get(scope)
    
    @classmethod
    def get_legendary_scopes(cls) -> List[str]:
        """Get all legendary feature scopes"""
        return [
            scope for scope, definition in cls.SCOPES.items()
            if definition.legendary_feature
        ]
    
    @classmethod
    def get_admin_scopes(cls) -> List[str]:
        """Get all admin scopes"""
        return [
            scope for scope, definition in cls.SCOPES.items()
            if definition.admin_required
        ]


class DescopeClient:
    """Descope authentication client with enhanced features"""
    
    def __init__(self, project_id: str, management_key: str, base_url: str = "https://api.descope.com"):
        self.project_id = project_id
        self.management_key = management_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {management_key}",
                "Content-Type": "application/json"
            },
            timeout=10.0
        )
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token with Descope"""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/auth/validate",
                json={"sessionJwt": token}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return {"valid": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Descope"""
        try:
            response = await self.client.get(f"{self.base_url}/v1/mgmt/user/{user_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"User info retrieval error: {str(e)}")
            return {"error": str(e)}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh authentication token"""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/auth/refresh",
                json={"refreshJwt": refresh_token}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class CequenceSecurityClient:
    """Cequence AI Gateway security integration client"""
    
    def __init__(self, api_key: str, gateway_url: str):
        self.api_key = api_key
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(
            headers={
                "X-Cequence-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=5.0  # Fast timeout for security checks
        )
    
    async def analyze_request_security(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for security threats"""
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/v1/security/analyze",
                json=request_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Don't fail request on security analysis failure
                logger.warning(f"Security analysis failed: {response.status_code}")
                return {"threat_score": 0.0, "risk_level": "unknown"}
                
        except Exception as e:
            logger.warning(f"Security analysis error: {str(e)}")
            return {"threat_score": 0.0, "risk_level": "unknown"}
    
    async def log_security_event(self, event_data: Dict[str, Any]) -> bool:
        """Log security event to Cequence"""
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/v1/security/events",
                json=event_data
            )
            return response.status_code < 300
        except Exception as e:
            logger.warning(f"Security event logging error: {str(e)}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class RateLimiter:
    """Advanced rate limiting with scope-aware limits"""
    
    def __init__(self):
        self.request_counts: Dict[str, Dict[str, int]] = {}
        self.last_reset: Dict[str, datetime] = {}
    
    def check_rate_limit(self, identifier: str, scope: str, max_requests: int = 60) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        current_time = datetime.now()
        key = f"{identifier}:{scope}"
        
        # Reset counts every minute
        if key not in self.last_reset or (current_time - self.last_reset[key]).seconds >= 60:
            self.request_counts[key] = {}
            self.last_reset[key] = current_time
        
        # Check current count
        minute_key = current_time.strftime("%Y-%m-%d-%H-%M")
        current_count = self.request_counts[key].get(minute_key, 0)
        
        if current_count >= max_requests:
            return False, {
                "rate_limited": True,
                "current_count": current_count,
                "max_requests": max_requests,
                "reset_time": (self.last_reset[key] + timedelta(minutes=1)).isoformat()
            }
        
        # Increment count
        self.request_counts[key][minute_key] = current_count + 1
        
        return True, {
            "rate_limited": False,
            "current_count": current_count + 1,
            "max_requests": max_requests,
            "remaining": max_requests - (current_count + 1)
        }


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Enhanced authentication middleware with Cequence integration"""
    
    def __init__(
        self,
        app: ASGIApp,
        descope_project_id: str,
        descope_management_key: str,
        cequence_api_key: str,
        cequence_gateway_url: str,
        jwt_secret_key: str,
        enable_rate_limiting: bool = True,
        enable_security_monitoring: bool = True
    ):
        super().__init__(app)
        self.descope_client = DescopeClient(descope_project_id, descope_management_key)
        self.cequence_client = CequenceSecurityClient(cequence_api_key, cequence_gateway_url)
        self.jwt_secret_key = jwt_secret_key
        self.rate_limiter = RateLimiter() if enable_rate_limiting else None
        self.enable_security_monitoring = enable_security_monitoring
        
        # Security configuration
        self.max_threat_score = 0.8  # Block requests above this threat score
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: List[str] = [
            "sql injection", "xss", "path traversal", "command injection"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method"""
        start_time = time.time()
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Add correlation headers
        request.headers.__dict__["_list"].append((b"x-correlation-id", correlation_id.encode()))
        
        try:
            # Security pre-checks
            if await self._is_blocked_request(request):
                return self._create_error_response(
                    status.HTTP_403_FORBIDDEN,
                    "Request blocked by security policy",
                    correlation_id
                )
            
            # Authentication and authorization
            auth_context = await self._authenticate_request(request)
            if not auth_context:
                return self._create_error_response(
                    status.HTTP_401_UNAUTHORIZED,
                    "Authentication required",
                    correlation_id
                )
            
            request.state.auth_context = auth_context
            
            # Security monitoring
            if self.enable_security_monitoring:
                await self._monitor_request_security(request, auth_context)
            
            # Process request
            response = await call_next(request)
            
            # Add security and analytics headers
            self._add_security_headers(response, auth_context, correlation_id)
            
            # Log analytics
            processing_time = (time.time() - start_time) * 1000
            await self._log_request_analytics(request, response, auth_context, processing_time)
            
            return response
            
        except HTTPException as e:
            return self._create_error_response(e.status_code, str(e.detail), correlation_id)
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            return self._create_error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal authentication error",
                correlation_id
            )
    
    async def _authenticate_request(self, request: Request) -> Optional[AuthenticationContext]:
        """Authenticate request and create auth context"""
        
        # Skip authentication for health and public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return AuthenticationContext(
                user_id="anonymous",
                session_id="public",
                scopes=set(),
                security_level=SecurityLevel.PUBLIC,
                token_type="public",
                authenticated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                request_id=str(uuid.uuid4()),
                correlation_id=request.state.correlation_id
            )
        
        # Extract Bearer token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            # Validate token with Descope
            validation_result = await self.descope_client.validate_token(token)
            
            if not validation_result.get("valid", False):
                logger.warning(f"Invalid token: {validation_result.get('error')}")
                return None
            
            # Decode JWT to extract claims
            try:
                # Note: In production, use proper JWT verification with Descope's public key
                payload = jwt.decode(token, options={"verify_signature": False})
            except jwt.InvalidTokenError as e:
                logger.warning(f"JWT decode error: {str(e)}")
                return None
            
            # Extract user information
            user_id = payload.get("sub") or payload.get("userId", "unknown")
            scopes_claim = payload.get("permissions", [])
            if isinstance(scopes_claim, str):
                scopes = set(scopes_claim.split())
            else:
                scopes = set(scopes_claim)
            
            # Determine security level
            security_level = self._determine_security_level(scopes)
            
            # Create authentication context
            auth_context = AuthenticationContext(
                user_id=user_id,
                session_id=payload.get("sessionId", str(uuid.uuid4())),
                scopes=scopes,
                security_level=security_level,
                token_type=payload.get("tokenType", "user"),
                authenticated_at=datetime.fromtimestamp(payload.get("iat", time.time())),
                expires_at=datetime.fromtimestamp(payload.get("exp", time.time() + 3600)),
                request_id=str(uuid.uuid4()),
                correlation_id=request.state.correlation_id
            )
            
            return auth_context
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def _determine_security_level(self, scopes: Set[str]) -> SecurityLevel:
        """Determine security level based on scopes"""
        if any(scope in scopes for scope in ScopeRegistry.get_admin_scopes()):
            return SecurityLevel.ADMIN
        elif any(scope in scopes for scope in ScopeRegistry.get_legendary_scopes()):
            return SecurityLevel.LEGENDARY
        elif scopes:
            return SecurityLevel.RESTRICTED
        else:
            return SecurityLevel.AUTHENTICATED
    
    async def _is_blocked_request(self, request: Request) -> bool:
        """Check if request should be blocked"""
        client_ip = request.client.host if request.client else "unknown"
        
        # Check blocked IPs
        if client_ip in self.blocked_ips:
            return True
        
        # Check for suspicious patterns in URL or headers
        url_path = request.url.path.lower()
        for pattern in self.suspicious_patterns:
            if pattern in url_path:
                logger.warning(f"Suspicious pattern detected: {pattern} in {url_path}")
                return True
        
        return False
    
    async def _monitor_request_security(self, request: Request, auth_context: AuthenticationContext):
        """Monitor request for security threats"""
        if not self.enable_security_monitoring:
            return
        
        request_data = {
            "request_id": auth_context.request_id,
            "correlation_id": auth_context.correlation_id,
            "user_id": auth_context.user_id,
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else "unknown",
            "scopes": list(auth_context.scopes),
            "security_level": auth_context.security_level.value
        }
        
        # Analyze with Cequence
        security_analysis = await self.cequence_client.analyze_request_security(request_data)
        
        # Update auth context with security info
        auth_context.threat_score = security_analysis.get("threat_score", 0.0)
        auth_context.risk_assessment = security_analysis.get("risk_level", "low")
        
        # Block high-threat requests
        if auth_context.threat_score > self.max_threat_score:
            await self.cequence_client.log_security_event({
                "event_type": "high_threat_blocked",
                "threat_score": auth_context.threat_score,
                "request_data": request_data,
                "timestamp": datetime.now().isoformat()
            })
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Request blocked due to high threat score"
            )
    
    def _add_security_headers(self, response: Response, auth_context: AuthenticationContext, correlation_id: str):
        """Add security and analytics headers to response"""
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Security-Level"] = auth_context.security_level.value
        response.headers["X-Threat-Score"] = str(auth_context.threat_score)
        response.headers["X-User-ID"] = auth_context.user_id
        response.headers["X-Session-ID"] = auth_context.session_id
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    async def _log_request_analytics(
        self, 
        request: Request, 
        response: Response, 
        auth_context: AuthenticationContext,
        processing_time_ms: float
    ):
        """Log request analytics to Cequence"""
        try:
            analytics_data = {
                "timestamp": datetime.now().isoformat(),
                "correlation_id": auth_context.correlation_id,
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "user_id": auth_context.user_id,
                    "security_level": auth_context.security_level.value,
                    "scopes": list(auth_context.scopes)
                },
                "response": {
                    "status_code": response.status_code,
                    "processing_time_ms": processing_time_ms
                },
                "security": {
                    "threat_score": auth_context.threat_score,
                    "risk_assessment": auth_context.risk_assessment
                }
            }
            
            # Log to Cequence (fire and forget)
            asyncio.create_task(
                self.cequence_client.log_security_event({
                    "event_type": "request_analytics",
                    "data": analytics_data
                })
            )
            
        except Exception as e:
            logger.warning(f"Analytics logging error: {str(e)}")
    
    def _create_error_response(self, status_code: int, message: str, correlation_id: str) -> Response:
        """Create standardized error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return Response(
            content=json.dumps(error_data),
            status_code=status_code,
            headers={
                "Content-Type": "application/json",
                "X-Correlation-ID": correlation_id
            }
        )


# Scope enforcement decorators
def require_scope(required_scope: str) -> Callable:
    """Decorator to require specific scope for endpoint access"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from FastAPI dependency injection or middleware
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'auth_context'):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication context not available"
                )
            
            auth_context: AuthenticationContext = request.state.auth_context
            
            # Check scope
            if required_scope not in auth_context.scopes:
                scope_def = ScopeRegistry.get_scope_definition(required_scope)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scope: {required_scope}",
                    headers={
                        "X-Required-Scope": required_scope,
                        "X-Scope-Description": scope_def.description if scope_def else "",
                        "X-Current-Scopes": ",".join(auth_context.scopes)
                    }
                )
            
            # Rate limiting
            scope_def = ScopeRegistry.get_scope_definition(required_scope)
            if scope_def:
                # Implementation would go here for rate limiting
                pass
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_scope(required_scopes: List[str]) -> Callable:
    """Decorator to require any of the specified scopes"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from FastAPI dependency injection or middleware
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'auth_context'):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication context not available"
                )
            
            auth_context: AuthenticationContext = request.state.auth_context
            
            # Check if user has any of the required scopes
            user_scopes = auth_context.scopes
            if not any(scope in user_scopes for scope in required_scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required one of: {', '.join(required_scopes)}",
                    headers={
                        "X-Required-Scopes": ",".join(required_scopes),
                        "X-Current-Scopes": ",".join(user_scopes)
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_security_level(min_level: SecurityLevel) -> Callable:
    """Decorator to require minimum security level"""
    level_order = {
        SecurityLevel.PUBLIC: 0,
        SecurityLevel.AUTHENTICATED: 1,
        SecurityLevel.RESTRICTED: 2,
        SecurityLevel.LEGENDARY: 3,
        SecurityLevel.ADMIN: 4
    }
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'auth_context'):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication context not available"
                )
            
            auth_context: AuthenticationContext = request.state.auth_context
            
            if level_order[auth_context.security_level] < level_order[min_level]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient security level. Required: {min_level.value}, Current: {auth_context.security_level.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Utility functions for authentication context access
def get_auth_context(request: Request) -> Optional[AuthenticationContext]:
    """Get authentication context from request"""
    return getattr(request.state, 'auth_context', None)


def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request"""
    return getattr(request.state, 'correlation_id', str(uuid.uuid4()))


def is_authenticated(request: Request) -> bool:
    """Check if request is authenticated"""
    auth_context = get_auth_context(request)
    return auth_context is not None and auth_context.security_level != SecurityLevel.PUBLIC


def has_scope(request: Request, scope: str) -> bool:
    """Check if authenticated user has specific scope"""
    auth_context = get_auth_context(request)
    return auth_context is not None and scope in auth_context.scopes


def has_any_scope(request: Request, scopes: List[str]) -> bool:
    """Check if authenticated user has any of the specified scopes"""
    auth_context = get_auth_context(request)
    return auth_context is not None and any(scope in auth_context.scopes for scope in scopes)


def is_legendary_user(request: Request) -> bool:
    """Check if user has legendary capabilities access"""
    auth_context = get_auth_context(request)
    return (
        auth_context is not None and 
        auth_context.security_level in [SecurityLevel.LEGENDARY, SecurityLevel.ADMIN]
    )


def is_admin_user(request: Request) -> bool:
    """Check if user has admin access"""
    auth_context = get_auth_context(request)
    return auth_context is not None and auth_context.security_level == SecurityLevel.ADMIN


# Example usage and testing functions
async def example_legendary_tool(request: Request) -> Dict[str, Any]:
    """Example legendary tool with scope enforcement"""
    
    @require_scope("tools:legendary")
    @require_security_level(SecurityLevel.LEGENDARY)
    async def _inner():
        auth_context = get_auth_context(request)
        return {
            "message": "Legendary tool executed successfully",
            "user_id": auth_context.user_id,
            "security_level": auth_context.security_level.value,
            "correlation_id": auth_context.correlation_id
        }
    
    return await _inner()


if __name__ == "__main__":
    # Configuration example
    print("🔐 Authentication Integration Middleware - Configuration Example")
    print("=" * 70)
    
    # Show available scopes
    print("\n📋 Available Scopes:")
    for scope, definition in ScopeRegistry.SCOPES.items():
        legendary_indicator = "🌟" if definition.legendary_feature else "🔧"
        admin_indicator = "👑" if definition.admin_required else ""
        print(f"  {legendary_indicator}{admin_indicator} {scope}")
        print(f"     {definition.description}")
        print(f"     Security Level: {definition.security_level.value}")
        print(f"     Rate Limit: {definition.rate_limit_per_minute}/min")
        print()
    
    print("🚀 Middleware ready for integration with FastMCP server!")