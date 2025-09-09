#!/usr/bin/env python3
"""
Test MCP Client for the Simple Server
"""
import requests
import json

def test_simple_mcp_server():
    """Test the simple MCP server running on localhost:9000"""
    base_url = "http://localhost:9000"
    
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
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ MCP initialization successful!")
            return True
        else:
            print(f"   ❌ MCP initialization failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_mcp_server()