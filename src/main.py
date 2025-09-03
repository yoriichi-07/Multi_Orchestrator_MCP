"""
Autonomous Software Foundry - MCP Server Entry Point
Enhanced with Descope OAuth 2.1 + PKCE Authentication
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.core.config import settings
from src.core.descope_auth import get_descope_client
from src.middleware.auth_middleware import DescopeAuthMiddleware, get_auth_context
from src.tools.authenticated_tools import router as authenticated_router
from src.tools.basic import router as basic_router

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
    description="MCP Server with AI Agent Orchestration and Self-Healing Capabilities",
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

# Add Descope authentication middleware
app.add_middleware(
    DescopeAuthMiddleware,
    exclude_paths=settings.auth_exclude_paths
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(authenticated_router, prefix="/mcp/v1")
app.include_router(basic_router, prefix="/mcp/v1/basic")


@app.get("/health")
async def health_check():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy", 
        "service": "autonomous-software-foundry",
        "version": "2.0.0",
        "authentication": "Descope OAuth 2.1 + PKCE"
    }


async def initialize_services():
    """Initialize all required services"""
    logger.info("Initializing services", settings=settings.dict(exclude={"descope_client_secret", "descope_management_key"}))
    
    # Initialize Descope client
    descope_client = await get_descope_client()
    logger.info("Descope client initialized", project_id=descope_client.project_id)


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
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.core.config import Settings
from src.core.auth import verify_token, AuthContext
from src.tools.basic import router as basic_router

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
    
    # Initialize services
    await initialize_services()
    
    yield
    
    # Cleanup
    logger.info("Shutting down MCP Server")
    await cleanup_services()


# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Software Foundry",
    description="MCP server for autonomous software generation with self-healing capabilities",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(basic_router, prefix="/mcp/v1", dependencies=[Security(verify_token)])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "autonomous-software-foundry"}


@app.get("/mcp/capabilities")
async def mcp_capabilities(auth: AuthContext = Depends(verify_token)):
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
            "version": "0.1.0"
        }
    }


async def initialize_services():
    """Initialize all required services"""
    settings = Settings()
    logger.info("Services initialized", settings=settings.model_dump())


async def cleanup_services():
    """Cleanup services on shutdown"""
    logger.info("Services cleaned up")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use structlog instead
    )
