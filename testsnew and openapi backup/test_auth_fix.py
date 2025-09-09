#!/usr/bin/env python3
"""
Test script to verify the authentication fix works correctly
"""
import json
import requests
import time

# Configuration - using the new port
BASE_URL = "http://localhost:8082"
BEARER_TOKEN = "K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ"

def test_health_endpoint():
    """Test the health endpoint (should always work)"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ Health check passed")
            return True
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_mcp_initialization():
    """Test MCP initialization (should work without auth based on our fix)"""
    print("\n🤝 Testing MCP initialization...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": "test-init-001",
        "params": {
            "protocolVersion": "2024-11-05"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mcp", 
                               headers=headers, 
                               json=payload, 
                               timeout=15)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                print("   ✅ MCP initialization successful!")
                return True
            else:
                print(f"   ❌ Unexpected response format: {data}")
                return False
        else:
            print(f"   ❌ MCP initialization failed")
            return False
            
    except Exception as e:
        print(f"   ❌ MCP initialization error: {e}")
        return False

def test_ping_tool_with_auth():
    """Test calling the ping tool with authentication"""
    print("\n🏓 Testing ping tool with authentication...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream", 
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": "test-ping-001",
        "params": {
            "name": "ping",
            "arguments": {}
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mcp",
                               headers=headers,
                               json=payload,
                               timeout=15)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                print(f"   ✅ Ping successful: {data['result']}")
                return True
            else:
                print(f"   ❌ Unexpected ping response: {data}")
                return False
        else:
            print(f"   ❌ Ping failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ping error: {e}")
        return False

def main():
    """Run authentication fix test suite"""
    print("🧪 Authentication Fix Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health_endpoint()
    
    # Test 2: MCP Initialization (should work without auth)
    init_ok = test_mcp_initialization()
    
    # Test 3: Tool call with auth (this is where the fix should work)
    ping_ok = test_ping_tool_with_auth()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Health Endpoint: {'✅' if health_ok else '❌'}")
    print(f"   MCP Initialization: {'✅' if init_ok else '❌'}")
    print(f"   Tool Call with Auth: {'✅' if ping_ok else '❌'}")
    
    if all([health_ok, init_ok, ping_ok]):
        print("\n🎉 ALL TESTS PASSED! Authentication fix is working!")
        return True
    else:
        print(f"\n⚠️  Some tests failed. The invalid_token error may still be present.")
        return False

if __name__ == "__main__":
    main()