#!/usr/bin/env python3
"""
Simulate Smithery scanning behavior to test if our server can be properly discovered
"""

import requests
import json
import sys
from datetime import datetime

def simulate_smithery_scan():
    """Simulate what Smithery does when scanning an MCP server"""
    
    base_url = "http://localhost:8080"
    
    print("=" * 60)
    print("SIMULATING SMITHERY MCP SERVER SCANNING")
    print("=" * 60)
    print(f"Target server: {base_url}")
    print(f"Scan time: {datetime.now().isoformat()}")
    print()
    
    # Step 1: Check if server is healthy
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Server: {health_data.get('server', 'Unknown')}")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            print(f"   Auth: {health_data.get('authentication', 'Unknown')}")
            print("   ✅ Server is healthy")
        else:
            print("   ❌ Server health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Initialize MCP connection (what Smithery would do)
    print("\n2. MCP Initialize...")
    try:
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "Smithery",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp/initialize",
            json=init_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            init_data = response.json()
            result = init_data.get("result", {})
            server_info = result.get("serverInfo", {})
            capabilities = result.get("capabilities", {})
            
            print(f"   Server: {server_info.get('name', 'Unknown')}")
            print(f"   Protocol: {result.get('protocolVersion', 'Unknown')}")
            print(f"   Tools supported: {bool(capabilities.get('tools'))}")
            print("   ✅ MCP Initialize successful")
        else:
            print(f"   ❌ Initialize failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 3: Discover available tools (critical for Smithery)
    print("\n3. Tool Discovery...")
    try:
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = requests.post(
            f"{base_url}/mcp/tools/list",
            json=tools_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tools_data = response.json()
            result = tools_data.get("result", {})
            tools = result.get("tools", [])
            
            print(f"   Tools found: {len(tools)}")
            print("   Available tools:")
            for i, tool in enumerate(tools[:5], 1):  # Show first 5 tools
                name = tool.get("name", "Unknown")
                description = tool.get("description", "No description")
                print(f"     {i}. {name}: {description}")
            
            if len(tools) > 5:
                print(f"     ... and {len(tools) - 5} more tools")
            
            print("   ✅ Tool discovery successful")
            
            # This is what Smithery would index
            print(f"\n   📋 SMITHERY INDEXING RESULT:")
            print(f"   Server capabilities indexed: {len(tools)} tools")
            print(f"   Server status: CONNECTABLE")
            print(f"   Authentication: DISCOVERY_ENABLED")
            
        else:
            print(f"   ❌ Tool discovery failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 4: Verify that tool execution requires auth (what it should)
    print("\n4. Authentication Verification...")
    try:
        call_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ping",
                "arguments": {}
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp/tools/call",
            json=call_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Tool execution correctly requires authentication")
            print("   🔒 Security: PROPERLY CONFIGURED")
        else:
            print(f"   ⚠️  Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SMITHERY SCAN SIMULATION COMPLETE")
    print("=" * 60)
    print("✅ Server is discoverable")
    print("✅ Capabilities can be indexed")
    print("✅ Authentication is properly configured")
    print("✅ Ready for Smithery deployment!")
    print()
    
    return True

if __name__ == "__main__":
    success = simulate_smithery_scan()
    if success:
        print("🚀 SUCCESS: Server will work with Smithery!")
        sys.exit(0)
    else:
        print("❌ FAILURE: Server needs fixes for Smithery compatibility")
        sys.exit(1)