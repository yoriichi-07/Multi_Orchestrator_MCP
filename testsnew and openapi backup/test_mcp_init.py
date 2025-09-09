#!/usr/bin/env python3
"""
Test script to verify MCP initialization works without authentication
"""
import json
import requests

def test_mcp_initialization():
    """Test MCP initialization endpoint"""
    url = "http://localhost:8080/mcp"
    
    # Test initialization request (should work without auth)
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": "test-init-1",
        "params": {
            "protocolVersion": "2024-11-05"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("Testing MCP initialization without authentication...")
    try:
        response = requests.post(url, json=init_payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ MCP initialization successful!")
            return True
        else:
            print(f"❌ MCP initialization failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP initialization: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    url = "http://localhost:8080/health"
    
    print("Testing health endpoint...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            return True
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MCP Server Endpoints")
    print("=" * 50)
    
    health_ok = test_health_endpoint()
    print()
    mcp_ok = test_mcp_initialization()
    
    print()
    print("=" * 50)
    if health_ok and mcp_ok:
        print("✅ All tests passed! Server is ready for Smithery deployment.")
    else:
        print("❌ Some tests failed. Server needs fixes before deployment.")