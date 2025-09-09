#!/usr/bin/env python3
"""
MCP Client with Automatic Descope Authentication

This script acts as a proxy between Cursor IDE and the actual MCP server,
automatically handling JWT token refresh and authentication. It eliminates
the need for manual JWT token management.

Usage:
    python mcp_client_with_auth.py <mcp_server_url>
    
Environment Variables:
    DESCOPE_ACCESS_KEY - Your Descope Access Key (required)
    DESCOPE_PROJECT_ID - Your Descope project ID (default: P32RbAyKnfcvEJYS69SfSEk6GPKk)
    MCP_AUTH_PORT - Port for the auth proxy (default: 8090)
    MCP_AUTH_LOG_LEVEL - Logging level (default: INFO)

Example:
    python mcp_client_with_auth.py https://your-mcp-server.com
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from aiohttp import web, ClientTimeout
from aiohttp.web import Request, Response, json_response

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.descope_auth import get_descope_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('MCP_AUTH_LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_auth_proxy')


class MCPAuthProxy:
    """
    MCP Authentication Proxy that handles automatic JWT token refresh.
    """
    
    def __init__(self, mcp_server_url: str, access_key: str, project_id: str = None):
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.access_key = access_key
        self.project_id = project_id or 'P32RbAyKnfcvEJYS69SfSEk6GPKk'
        
        # Token management
        self.current_jwt_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.token_refresh_threshold = 300  # Refresh 5 minutes before expiry
        
        # HTTP client
        self.client_session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"Initialized MCP Auth Proxy for server: {self.mcp_server_url}")
        logger.info(f"Project ID: {self.project_id}")
        logger.info(f"Access Key: {self.access_key[:10]}...{self.access_key[-10:]}")
    
    async def start(self):
        """
        Start the proxy and initialize the HTTP client session.
        """
        timeout = ClientTimeout(total=30, connect=10)
        self.client_session = aiohttp.ClientSession(timeout=timeout)
        
        # Get initial JWT token
        await self.refresh_jwt_token()
        
        logger.info("MCP Auth Proxy started successfully")
    
    async def stop(self):
        """
        Stop the proxy and cleanup resources.
        """
        if self.client_session:
            await self.client_session.close()
        
        logger.info("MCP Auth Proxy stopped")
    
    async def refresh_jwt_token(self) -> bool:
        """
        Refresh the JWT token using the Descope access key.
        
        Returns:
            True if token refresh was successful, False otherwise
        """
        try:
            logger.info("Refreshing JWT token...")
            
            descope_client = await get_descope_client()
            result = await descope_client.create_machine_token(self.access_key)
            
            self.current_jwt_token = result.get('access_token')
            expires_in = result.get('expires_in', 3600)  # Default to 1 hour
            self.token_expires_at = time.time() + expires_in
            
            logger.info(f"JWT token refreshed successfully (expires in {expires_in}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh JWT token: {e}")
            return False
    
    async def ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid JWT token, refreshing if necessary.
        
        Returns:
            True if we have a valid token, False otherwise
        """
        current_time = time.time()
        
        # Check if we need to refresh the token
        if (not self.current_jwt_token or 
            not self.token_expires_at or 
            current_time >= (self.token_expires_at - self.token_refresh_threshold)):
            
            return await self.refresh_jwt_token()
        
        return True
    
    async def forward_request(self, request: Request) -> Response:
        """
        Forward a request to the MCP server with proper authentication.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            The response from the MCP server
        """
        try:
            # Ensure we have a valid JWT token
            if not await self.ensure_valid_token():
                return json_response(
                    {'error': 'Failed to obtain valid JWT token'}, 
                    status=500
                )
            
            # Prepare the forwarded request
            url = f"{self.mcp_server_url}{request.path_qs}"
            headers = dict(request.headers)
            
            # Add JWT authentication
            headers['Authorization'] = f'Bearer {self.current_jwt_token}'
            
            # Remove hop-by-hop headers
            hop_by_hop = {
                'connection', 'keep-alive', 'proxy-authenticate',
                'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
                'upgrade', 'host'
            }
            headers = {k: v for k, v in headers.items() if k.lower() not in hop_by_hop}
            
            # Read request body
            body = await request.read() if request.can_read_body else None
            
            logger.debug(f"Forwarding {request.method} {url}")
            
            # Forward the request
            async with self.client_session.request(
                method=request.method,
                url=url,
                headers=headers,
                data=body
            ) as response:
                
                # Read response body
                response_body = await response.read()
                
                # Prepare response headers
                response_headers = dict(response.headers)
                response_headers.pop('transfer-encoding', None)
                response_headers.pop('content-encoding', None)
                
                logger.debug(f"Response: {response.status} {len(response_body)} bytes")
                
                return Response(
                    body=response_body,
                    status=response.status,
                    headers=response_headers
                )
                
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            return json_response(
                {'error': f'Proxy error: {str(e)}'}, 
                status=500
            )
    
    async def health_check(self, request: Request) -> Response:
        """
        Health check endpoint for the proxy.
        """
        token_valid = await self.ensure_valid_token()
        
        health_data = {
            'status': 'healthy' if token_valid else 'unhealthy',
            'proxy_version': '1.0.0',
            'mcp_server_url': self.mcp_server_url,
            'jwt_token_valid': token_valid,
            'token_expires_at': self.token_expires_at,
            'current_time': time.time()
        }
        
        return json_response(health_data)


async def create_app(mcp_server_url: str, access_key: str, project_id: str = None) -> web.Application:
    """
    Create the web application with the MCP auth proxy.
    """
    proxy = MCPAuthProxy(mcp_server_url, access_key, project_id)
    await proxy.start()
    
    app = web.Application()
    
    # Health check endpoint
    app.router.add_get('/health', proxy.health_check)
    app.router.add_get('/_proxy/health', proxy.health_check)
    
    # Proxy all other requests
    app.router.add_route('*', '/{path:.*}', proxy.forward_request)
    
    # Cleanup on shutdown
    async def cleanup_handler(app):
        await proxy.stop()
    
    app.on_cleanup.append(cleanup_handler)
    
    return app


async def main():
    """
    Main function to start the MCP authentication proxy.
    """
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: MCP server URL required")
        print("\nUsage:")
        print("   python mcp_client_with_auth.py <mcp_server_url>")
        print("\nExample:")
        print("   python mcp_client_with_auth.py https://your-mcp-server.com")
        print("\nEnvironment Variables:")
        print("   DESCOPE_ACCESS_KEY - Your Descope Access Key (required)")
        print("   DESCOPE_PROJECT_ID - Your Descope project ID (optional)")
        print("   MCP_AUTH_PORT - Port for the auth proxy (default: 8090)")
        sys.exit(1)
    
    mcp_server_url = sys.argv[1]
    access_key = os.getenv('DESCOPE_ACCESS_KEY')
    project_id = os.getenv('DESCOPE_PROJECT_ID')
    port = int(os.getenv('MCP_AUTH_PORT', 8090))
    
    if not access_key:
        print("❌ Error: DESCOPE_ACCESS_KEY environment variable required")
        print("\nSet the environment variable:")
        print("   export DESCOPE_ACCESS_KEY=your_access_key_here")
        sys.exit(1)
    
    try:
        # Create and start the application
        app = await create_app(mcp_server_url, access_key, project_id)
        
        print("\n" + "="*60)
        print("🚀 MCP AUTHENTICATION PROXY STARTED")
        print("="*60)
        print(f"📡 Proxy URL: http://localhost:{port}")
        print(f"🎯 Target MCP Server: {mcp_server_url}")
        print(f"🔐 Project ID: {project_id or 'P32RbAyKnfcvEJYS69SfSEk6GPKk'}")
        print(f"🗝️  Access Key: {access_key[:10]}...{access_key[-10:]}")
        print(f"\n💡 Use this URL in your Cursor IDE mcp.json:")
        print(f"   http://localhost:{port}")
        print(f"\n🔧 Health Check: http://localhost:{port}/health")
        print("\n⚠️  Press Ctrl+C to stop the proxy")
        print("="*60)
        
        # Start the web server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Proxy stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting proxy: {e}")
        logger.exception("Failed to start proxy")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())