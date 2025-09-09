#!/usr/bin/env python3
"""
Complete MCP Protocol Test Suite
Tests the full MCP initialization and tool calling flow
"""
import json
import requests
import time

# Configuration
BASE_URL = "https://ztaip-s7grmddl-4xp4r634bq-uc.a.run.app"
BEARER_TOKEN = "K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ"

def test_health_endpoint():
    """Test the health endpoint (should always work)"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Server: {data.get('server', 'Unknown')}")
            print("   ✅ Health check passed")
            return True
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_mcp_initialization():
    """Test MCP initialization (Step 1 of MCP protocol)"""
    print("\n🤝 Testing MCP initialization...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {BEARER_TOKEN}"
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
        print(f"   Response: {response.text[:200]}...")
        
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
            print(f"   ❌ MCP initialization failed")
            return False
            
    except Exception as e:
        print(f"   ❌ MCP initialization error: {e}")
        return False

def test_tools_list():
    """Test listing tools (Step 2 - requires initialization first)"""
    print("\n🔧 Testing tools list...")
    
    headers = {
        "Content-Type": "application/json", 
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "test-tools-001",
        "params": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mcp",
                               headers=headers,
                               json=payload,
                               timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"   ✅ Found {len(tools)} tools!")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"      - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                return True
            else:
                print(f"   ❌ Unexpected response: {data}")
                return False
        else:
            print(f"   ❌ Tools list failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Tools list error: {e}")
        return False

def test_ping_tool():
    """Test calling the ping tool"""
    print("\n🏓 Testing ping tool...")
    
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
    """Run complete MCP protocol test suite"""
    print("🧪 Complete MCP Protocol Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health_endpoint()
    
    # Test 2: MCP Initialization  
    init_ok = test_mcp_initialization()
    
    # Test 3: Tools list (only if init worked)
    tools_ok = False
    if init_ok:
        tools_ok = test_tools_list()
    else:
        print("\n🔧 Skipping tools list (initialization failed)")
    
    # Test 4: Tool call (only if everything else worked)
    ping_ok = False
    if init_ok and tools_ok:
        ping_ok = test_ping_tool()
    else:
        print("\n🏓 Skipping ping tool (prerequisites failed)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Health Endpoint: {'✅' if health_ok else '❌'}")
    print(f"   MCP Initialization: {'✅' if init_ok else '❌'}")
    print(f"   Tools List: {'✅' if tools_ok else '❌'}")
    print(f"   Tool Call (ping): {'✅' if ping_ok else '❌'}")
    
    if all([health_ok, init_ok, tools_ok, ping_ok]):
        print("\n🎉 ALL TESTS PASSED! MCP server is fully functional!")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    main()