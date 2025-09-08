#!/usr/bin/env python3
"""
Multi-Agent Orchestrator MCP Server - Production Entry Point
Supports both STDIO (development) and HTTP (production) modes
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings

def main():
    """Main entry point - auto-detect mode based on environment"""
    
    # Check if running in container/production (has PORT env var or specific mode)
    port = os.environ.get("PORT", "8080")
    mode = os.environ.get("MCP_MODE", "auto")
    
    if mode == "http" or (mode == "auto" and (os.environ.get("PORT") or os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER"))):
        # Production HTTP mode
        print(f"🌐 Starting MCP Server in HTTP mode on port {port}")
        start_http_server(int(port))
    else:
        # Development STDIO mode  
        print("📺 Starting MCP Server in STDIO mode")
        start_stdio_server()

def start_http_server(port: int):
    """Start HTTP server for production deployment"""
    import uvicorn
    from src.main import app
    
    print(f"🚀 Multi-Agent Orchestrator MCP Server (HTTP)")
    print(f"📍 Port: {port}")
    print(f"🔐 Descope Project: {settings.descope_project_id}")
    print(f"📊 Cequence Gateway: {settings.cequence_gateway_id or 'Demo mode'}")
    print(f"🐛 Debug Mode: {settings.debug}")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True
    )

def start_stdio_server():
    """Start STDIO server for development/MCP client usage"""
    from mcp_server import mcp
    
    print(f"🚀 Multi-Agent Orchestrator MCP Server (STDIO)")
    print(f"🔐 Descope Project: {settings.descope_project_id}")
    print(f"📊 Cequence Gateway: {settings.cequence_gateway_id or 'Demo mode'}")
    print(f"🐛 Debug Mode: {settings.debug}")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()