#!/usr/bin/env python3
"""
Test script to verify MCP endpoint authentication behavior
"""

import requests
import json
import sys

def test_discovery_endpoint():
    """Test that tools/list endpoint works without authentication"""
    url = "http://localhost:8080/mcp/tools/list"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    print("Testing /mcp/tools/list without authentication...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Discovery endpoint works without authentication")
            return True
        else:
            print("❌ FAIL: Discovery endpoint rejected request")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_initialize_endpoint():
    """Test that initialize endpoint works without authentication"""
    url = "http://localhost:8080/mcp/initialize"
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("\nTesting /mcp/initialize without authentication...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Initialize endpoint works without authentication")
            return True
        else:
            print("❌ FAIL: Initialize endpoint rejected request")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_tool_call_without_auth():
    """Test that tools/call endpoint requires authentication"""
    url = "http://localhost:8080/mcp/tools/call"
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "ping",
            "arguments": {}
        }
    }
    
    print("\nTesting /mcp/tools/call WITHOUT authentication (should fail)...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Tool call correctly requires authentication")
            return True
        else:
            print("❌ FAIL: Tool call should have returned 401")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_health_endpoint():
    """Test that health endpoint works without authentication"""
    url = "http://localhost:8080/health"
    
    print("\nTesting /health endpoint...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Health endpoint works")
            return True
        else:
            print("❌ FAIL: Health endpoint failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MCP ENDPOINT AUTHENTICATION TEST")
    print("=" * 60)
    
    # Test all endpoints
    results = []
    results.append(test_health_endpoint())
    results.append(test_discovery_endpoint())
    results.append(test_initialize_endpoint())
    results.append(test_tool_call_without_auth())
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 Authentication middleware is working correctly!")
        sys.exit(0)
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print("🔧 Authentication middleware needs fixes")
        sys.exit(1)