#!/usr/bin/env python3
"""
Minimal test to verify MCP authentication behavior directly
"""

import asyncio
import json
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

# Import our authentication middleware
from src.core.auth import AuthenticationMiddleware

async def mock_health(request):
    return JSONResponse({"status": "ok"})

async def mock_tools_list(request):
    """Mock MCP tools/list endpoint"""
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {
                    "name": "ping",
                    "description": "Test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    })

async def mock_tools_call(request):
    """Mock MCP tools/call endpoint"""
    return JSONResponse({
        "jsonrpc": "2.0", 
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "pong"}],
            "isError": False
        }
    })

async def mock_initialize(request):
    """Mock MCP initialize endpoint"""
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "test-server", "version": "1.0.0"}
        }
    })

def test_authentication_middleware():
    """Test the authentication middleware directly"""
    
    # Create a minimal Starlette app
    app = Starlette(
        routes=[
            Route("/health", mock_health, methods=["GET"]),
            Route("/mcp/tools/list", mock_tools_list, methods=["POST"]),
            Route("/mcp/tools/call", mock_tools_call, methods=["POST"]),
            Route("/mcp/initialize", mock_initialize, methods=["POST"]),
        ]
    )
    
    # Add our authentication middleware
    app.add_middleware(AuthenticationMiddleware)
    
    # Create test client
    client = TestClient(app)
    
    print("Testing Authentication Middleware Behavior")
    print("=" * 50)
    
    # Test 1: Health endpoint (should work)
    print("1. Testing /health endpoint (should work without auth)...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ PASS: Health endpoint accessible")
    else:
        print("   ❌ FAIL: Health endpoint blocked")
    
    # Test 2: MCP tools/list (should work without auth after our fix)
    print("\n2. Testing /mcp/tools/list endpoint (should work without auth)...")
    response = client.post("/mcp/tools/list", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    if response.status_code == 200:
        print("   ✅ PASS: Tools list accessible without auth")
    else:
        print("   ❌ FAIL: Tools list blocked")
    
    # Test 3: MCP initialize (should work without auth after our fix)
    print("\n3. Testing /mcp/initialize endpoint (should work without auth)...")
    response = client.post("/mcp/initialize", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"roots": {"listChanged": True}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    if response.status_code == 200:
        print("   ✅ PASS: Initialize accessible without auth")
    else:
        print("   ❌ FAIL: Initialize blocked")
    
    # Test 4: MCP tools/call (should require auth)
    print("\n4. Testing /mcp/tools/call endpoint without auth (should fail)...")
    response = client.post("/mcp/tools/call", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "ping",
            "arguments": {}
        }
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    if response.status_code == 401:
        print("   ✅ PASS: Tools call correctly requires auth")
    else:
        print("   ❌ FAIL: Tools call should require auth")
    
    print("\n" + "=" * 50)
    print("Authentication Middleware Test Complete")

if __name__ == "__main__":
    test_authentication_middleware()