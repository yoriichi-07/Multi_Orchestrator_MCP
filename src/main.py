"""
Autonomous Software Foundry - MCP Server Entry Point
Enhanced with Descope OAuth 2.1 + PKCE Authentication, Cequence AI Gateway Integration, and Full MCP Protocol Support
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import structlog

from src.core.config import settings
from src.core.descope_auth import get_descope_client
from src.core.cequence_integration import CequenceMiddleware
from src.core.mcp_server import initialize_mcp_server
from src.middleware.auth_middleware import DescopeAuthMiddleware, get_auth_context
from src.tools.authenticated_tools import router as authenticated_router
from src.tools.basic import router as basic_router
from src.tools.monitored_tools import router as monitored_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting Autonomous Software Foundry MCP Server")
    await initialize_services()
    yield
    logger.info("Shutting down MCP Server")
    await cleanup_services()


# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Software Foundry",
    description="MCP Server with AI Agent Orchestration, Self-Healing Capabilities, Full MCP Protocol Support, and Cequence AI Gateway Integration",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Cequence AI Gateway middleware if configured
if settings.cequence_gateway_id and settings.cequence_api_key:
    app.add_middleware(
        CequenceMiddleware,
        gateway_id=settings.cequence_gateway_id,
        api_key=settings.cequence_api_key
    )
    logger.info("Cequence AI Gateway middleware enabled")
else:
    logger.warning("Cequence AI Gateway not configured - running without analytics")

# Add Descope authentication middleware
app.add_middleware(
    DescopeAuthMiddleware,
    exclude_paths=settings.auth_exclude_paths
)

# Initialize MCP server
mcp_server = initialize_mcp_server(app)

logger.info("MCP server initialized with full protocol support")

# Security
security = HTTPBearer()

# Include routers
app.include_router(authenticated_router, prefix="/mcp/v1")
app.include_router(basic_router, prefix="/mcp/v1/basic")
app.include_router(monitored_router, prefix="/mcp/v1")


@app.get("/dashboard")
async def dashboard():
    """Serve the Cequence analytics dashboard"""
    return FileResponse("static/cequence_dashboard.html")


@app.get("/health")
async def health_check():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy", 
        "service": "autonomous-software-foundry",
        "version": "2.0.0",
        "authentication": "Descope OAuth 2.1 + PKCE",
        "analytics": "Cequence AI Gateway" if settings.cequence_gateway_id else "Disabled",
        "mcp_protocol": "2024-11-05",
        "capabilities": {
            "tools": len(mcp_server.tools),
            "resources": len(mcp_server.resources)
        }
    }


@app.get("/mcp/capabilities")
async def mcp_capabilities(auth: get_auth_context = Depends(get_auth_context)):
    """MCP server capabilities endpoint"""
    return {
        "apiVersion": "2024-11-05",
        "capabilities": {
            "logging": {},
            "prompts": {
                "listChanged": True
            },
            "resources": {
                "subscribe": True,
                "listChanged": True
            },
            "tools": {
                "listChanged": True
            }
        },
        "serverInfo": {
            "name": "autonomous-software-foundry",
            "version": "2.0.0",
            "description": "MCP server with AI agent orchestration, self-healing capabilities, and Cequence AI Gateway integration"
        }
    }


async def initialize_services():
    """Initialize all required services"""
    logger.info("Initializing services", settings=settings.model_dump(exclude={"descope_client_secret", "descope_management_key", "cequence_api_key"}))
    
    # Initialize Descope client
    descope_client = await get_descope_client()
    logger.info("Descope client initialized", project_id=descope_client.project_id)
    
    # Log Cequence status
    if settings.cequence_gateway_id:
        logger.info("Cequence AI Gateway configured", gateway_id=settings.cequence_gateway_id)
    else:
        logger.info("Cequence AI Gateway not configured")
    
    # Register MCP tools and resources
    await register_mcp_tools()
    await register_mcp_resources()
    
    logger.info(
        "MCP server fully initialized",
        tools_count=len(mcp_server.tools),
        resources_count=len(mcp_server.resources)
    )


async def register_mcp_tools():
    """Register all MCP tools"""
    # Import tools to register them with the MCP server
    from src.tools import infrastructure_tools
    from src.tools import generation_tools  
    from src.tools import quality_tools
    
    # Register any deferred tools
    from src.core.tool_registry import register_deferred_tools
    register_deferred_tools()
    
    logger.info(f"MCP tools registered: {len(mcp_server.tools)} tools")


async def register_mcp_resources():
    """Register all MCP resources"""
    # Import resources to register them with the MCP server
    from src.resources import project_resources
    
    # Register any deferred resources
    from src.core.tool_registry import register_deferred_resources
    register_deferred_resources()
    
    logger.info(f"MCP resources registered: {len(mcp_server.resources)} resources")


async def cleanup_services():
    """Cleanup services on shutdown"""
    logger.info("Services cleaned up")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_config=None  # Use structlog instead
    )
