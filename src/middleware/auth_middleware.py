"""
FastAPI middleware for Descope authentication
Handles automatic token validation and context injection
"""
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer
import structlog

from src.core.descope_auth import get_descope_client, AuthContext, TokenValidationError

logger = structlog.get_logger()
security = HTTPBearer()


class DescopeAuthMiddleware:
    """Middleware for automatic token validation and context injection"""
    
    def __init__(self, app: Callable, exclude_paths: Optional[list] = None):
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
    
    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        path = request.url.path
        
        # Skip authentication for excluded paths
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            await self.app(scope, receive, send)
            return
        
        # Extract and validate token
        try:
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
            
            token = auth_header.split(" ", 1)[1]
            descope_client = await get_descope_client()
            token_claims = await descope_client.validate_jwt_token(token)
            
            # Create auth context
            auth_context = AuthContext(token_claims)
            
            # Check if token is expired
            if auth_context.is_expired():
                raise HTTPException(status_code=401, detail="Token has expired")
            
            # Add auth context to request state
            request.state.auth_context = auth_context
            
            logger.info(
                "request_authenticated",
                user_id=auth_context.user_id,
                scopes=auth_context.scopes,
                path=path,
                correlation_id=auth_context.correlation_id
            )
            
        except TokenValidationError as e:
            logger.warning(
                "authentication_failed",
                path=path,
                error=str(e)
            )
            
            response = Response(
                content=f'{{"detail": "Authentication failed: {str(e)}"}}',
                status_code=401,
                media_type="application/json"
            )
            await response(scope, receive, send)
            return
        
        except HTTPException as e:
            response = Response(
                content=f'{{"detail": "{e.detail}"}}',
                status_code=e.status_code,
                media_type="application/json"
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)


async def get_auth_context(request: Request) -> AuthContext:
    """Dependency to get auth context from request"""
    if not hasattr(request.state, 'auth_context'):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return request.state.auth_context


def require_scopes(*required_scopes: str):
    """Dependency factory for scope-based authorization"""
    async def scope_checker(request: Request) -> AuthContext:
        auth_context = await get_auth_context(request)
        
        if not auth_context.has_all_scopes(list(required_scopes)):
            missing_scopes = set(required_scopes) - set(auth_context.scopes)
            logger.warning(
                "insufficient_scopes",
                user_id=auth_context.user_id,
                required_scopes=required_scopes,
                missing_scopes=list(missing_scopes),
                correlation_id=auth_context.correlation_id
            )
            
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Missing scopes: {', '.join(missing_scopes)}"
            )
        
        return auth_context
    
    return scope_checker
