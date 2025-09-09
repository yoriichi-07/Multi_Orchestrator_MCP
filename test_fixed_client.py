#!/usr/bin/env python3
"""
Test the fixed MCP server running on localhost:8081
"""
import requests
import json

def test_fixed_mcp_server():
    """Test the fixed MCP server"""
    base_url = "http://localhost:8081"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Test 1: MCP Initialize
    print("🤝 Testing MCP initialization...")
    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": "test-init",
        "params": {
            "protocolVersion": "2024-11-05"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/mcp", headers=headers, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                print("   ✅ MCP initialization successful!")
                print(f"   Server capabilities: {data['result'].get('capabilities', {})}")
                return True
            else:
                print(f"   ❌ Unexpected response format: {data}")
                return False
        else:
            print(f"   ❌ MCP initialization failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Fixed MCP Server")
    print("=" * 50)
    result = test_fixed_mcp_server()
    if result:
        print("\n🎉 SUCCESS! The lifespan fix worked!")
    else:
        print("\n❌ Still having issues...")