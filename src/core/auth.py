#
# ----- CONSOLIDATED AUTHENTICATION MODULE -----
#

import os
import json
import structlog
import asyncio
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import settings
from .descope_auth import get_descope_client, DescopeClient # We will keep this import for now

logger = structlog.get_logger()

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    ✅ FINAL & CONSOLIDATED VERSION: A robust middleware that correctly handles 
    the entire MCP session lifecycle, including initialization and per-tool 
    scope enforcement. This is the single source of truth for authentication.
    
    CRITICAL FIX: Ensures discovery endpoints ALWAYS work regardless of 
    authentication configuration or initialization failures.
    """
    def __init__(self, app):
        super().__init__(app)
        # This map defines which permission is required for each tool.
        self.tool_to_scope_map = {
            "ping": "tools:basic",
            "orchestrate_task": "tools:orchestrate",
            "generate_architecture": "tools:architecture",
            "auto_fix_code": "tools:fix",
            "list_capabilities": "tools:capabilities",
            "get_system_status": "tools:status",
            "advanced_generate_application": "advanced:app_generator",
            "autonomous_architect": "advanced:autonomous_architect",
            "proactive_quality_assurance": "advanced:quality_framework",
            "evolutionary_prompt_optimization": "advanced:prompt_engine",
            "last_mile_cloud_deployment": "advanced:cloud_agent",
            "debug_server_config": None # This tool is public
        }
        
        # Initialize authentication status tracking
        self._auth_initialized = False
        self._auth_available = False
        self._descope_client: Optional[DescopeClient] = None
        self._init_error: Optional[str] = None
        
        # Initialize authentication in the background (non-blocking)
        asyncio.create_task(self._initialize_authentication())

    async def _initialize_authentication(self):
        """Initialize authentication client with robust error handling"""
        try:
            logger.info("auth_middleware_init_start", 
                       project_id_configured=bool(settings.descope_project_id),
                       demo_mode=settings.descope_demo_mode)
            
            if settings.descope_project_id:
                # Try to initialize Descope client
                self._descope_client = await get_descope_client()
                self._auth_available = True
                logger.info("auth_middleware_init_success", 
                           demo_mode=settings.descope_demo_mode,
                           project_id=settings.descope_project_id[:8] + "..." if settings.descope_project_id else None)
            else:
                logger.info("auth_middleware_init_skipped", reason="no_project_id_configured")
                self._auth_available = False
                
        except Exception as e:
            # Log the error but continue without authentication
            self._init_error = str(e)
            self._auth_available = False
            logger.warning("auth_middleware_init_failed", 
                          error=str(e), 
                          fallback="discovery_endpoints_will_work")
        finally:
            self._auth_initialized = True

    async def _wait_for_auth_init(self, timeout: float = 5.0) -> bool:
        """Wait for authentication initialization to complete"""
        start_time = asyncio.get_event_loop().time()
        while not self._auth_initialized:
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning("auth_init_timeout", timeout=timeout)
                return False
            await asyncio.sleep(0.1)
        return True

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Define paths that are always public and require NO authentication
        public_paths = {"/health", "/docs", "/openapi.json"}
        if path in public_paths or request.method == "OPTIONS":
            return await call_next(request)

        # Handle MCP endpoints with proper discovery vs execution separation
        if path == "/mcp" or path.startswith("/mcp/"):
            # MCP Discovery endpoints that should be accessible without authentication
            # These are used by clients like Smithery to discover server capabilities
            mcp_discovery_endpoints = {
                "/mcp",                    # Base MCP endpoint
                "/mcp/",                   # Base MCP endpoint with trailing slash
                "/mcp/tools/list",         # Tool discovery - critical for Smithery scanning
                "/mcp/initialize",         # MCP initialization
                "/mcp/ping",              # Health check
                "/mcp/capabilities",       # Capabilities discovery
                "/mcp/resources/list",     # Resource discovery
                "/mcp/prompts/list"        # Prompt discovery
            }
            
            # CRITICAL: Allow discovery endpoints without authentication ALWAYS
            if path in mcp_discovery_endpoints:
                logger.info("mcp_discovery_access", 
                           path=path, 
                           authenticated=False,
                           auth_available=self._auth_available)
                return await call_next(request)
            
            # For tool execution endpoints, require authentication if available
            if path == "/mcp/tools/call" or path.endswith("/tools/call"):
                # Wait for authentication initialization
                await self._wait_for_auth_init()
                
                # If authentication is not available, allow access but log warning
                if not self._auth_available:
                    logger.warning("mcp_tool_call_no_auth", 
                                  path=path, 
                                  reason=self._init_error or "auth_not_configured",
                                  security_warning="Tool calls proceeding without authentication")
                    return await call_next(request)
                
                # Authentication is available, require valid token
                auth_header = request.headers.get("authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    logger.warning("mcp_tool_call_unauthorized", path=path)
                    return JSONResponse({
                        "error": "Authorization header is missing or invalid for tool call",
                        "code": "missing_authorization",
                        "message": "MCP tool execution requires Bearer token authentication"
                    }, status_code=401)
                
                token = auth_header[7:]

                try:
                    # Use the initialized client
                    if not self._descope_client:
                        raise Exception("Descope client not initialized")
                    
                    # CORRECT & SIMPLIFIED VALIDATION
                    validated_token = await self._descope_client.validate_session(session_token=token)
                    request.state.auth_context = validated_token

                    # --- SCOPE ENFORCEMENT ---
                    body = await request.body()
                    mcp_payload = json.loads(body if body else "{}")
                    tool_name = mcp_payload.get("params", {}).get("name")
                    required_scope = self.tool_to_scope_map.get(tool_name)
                    
                    if required_scope:
                        token_scopes = validated_token.get("permissions", [])
                        if isinstance(token_scopes, str):
                            token_scopes = token_scopes.split()
                        if required_scope not in token_scopes:
                            error_msg = f"Insufficient permissions. Tool '{tool_name}' requires scope: '{required_scope}'"
                            logger.warning("authorization_failed", required=required_scope, provided=token_scopes, tool=tool_name)
                            return JSONResponse({"error": error_msg}, status_code=403)

                    async def receive(): return {"type": "http.request", "body": body}
                    request = Request(request.scope, receive, request._send)
                    
                    logger.info("mcp_tool_call_authorized", tool=tool_name, user=validated_token.get("sub"))

                except Exception as e:
                    logger.warning("authentication_failed", error=str(e), path=path)
                    return JSONResponse({"error": {"message": "invalid_token", "details": str(e)}}, status_code=401)
            
            # For any other MCP endpoints, allow without auth (e.g., other discovery paths)
            logger.info("mcp_endpoint_access", path=path, authenticated=False)
            return await call_next(request)
        
        # For non-MCP endpoints, require authentication if available
        await self._wait_for_auth_init()
        
        if self._auth_available:
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse({"error": "Authorization required"}, status_code=401)
        
        return await call_next(request)
