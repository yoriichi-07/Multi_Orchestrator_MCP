#!/usr/bin/env python3
"""
Test script to verify the Smithery deployment fix
Simulates Smithery's MCP scanning process with proper JSON-RPC protocol
"""

import os
import sys
import json
import time
import requests
import subprocess
from typing import Dict, Any, Optional

def test_mcp_json_rpc_endpoints(base_url: str = "http://localhost:8080") -> Dict[str, Any]:
    """Test MCP JSON-RPC endpoints that Smithery uses for scanning"""
    
    results = {
        "base_url": base_url,
        "tests": {},
        "overall_success": True,
        "smithery_compatible": True
    }
    
    mcp_endpoint = f"{base_url}/mcp"
    
    print(f"🔍 Testing MCP JSON-RPC Protocol for Smithery compatibility...")
    print(f"🌐 MCP Endpoint: {mcp_endpoint}")
    print()
    
    # Standard MCP headers required by the protocol
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-06-18"
    }
    
    # Critical MCP JSON-RPC requests that Smithery uses
    mcp_requests = {
        "initialize": {
            "description": "MCP initialization - CRITICAL for Smithery",
            "payload": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "smithery-test-client",
                        "version": "1.0.0"
                    }
                }
            },
            "critical": True
        },
        "tools_list": {
            "description": "Tool discovery - CRITICAL for Smithery",
            "payload": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            },
            "critical": True
        },
        "resources_list": {
            "description": "Resource discovery - Optional",
            "payload": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
                "params": {}
            },
            "critical": False
        },
        "prompts_list": {
            "description": "Prompt discovery - Optional",
            "payload": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/list",
                "params": {}
            },
            "critical": False
        }
    }
    
    for test_name, test_info in mcp_requests.items():
        try:
            print(f"📡 Testing {test_name} - {test_info['description']}")
            
            # Make JSON-RPC request without authentication (as Smithery would during discovery)
            response = requests.post(
                mcp_endpoint, 
                headers=headers,
                json=test_info["payload"],
                timeout=10
            )
            
            test_result = {
                "endpoint": mcp_endpoint,
                "description": test_info["description"],
                "request": test_info["payload"],
                "status_code": response.status_code,
                "success": False,
                "response_data": None,
                "error": None,
                "smithery_critical": test_info["critical"]
            }
            
            # Check if response is successful (200-299 range)
            if 200 <= response.status_code < 300:
                test_result["success"] = True
                try:
                    response_data = response.json()
                    test_result["response_data"] = response_data
                    
                    # Validate JSON-RPC response
                    if "jsonrpc" in response_data and "id" in response_data:
                        if "result" in response_data:
                            print(f"   ✅ SUCCESS (HTTP {response.status_code}) - Valid JSON-RPC response")
                        elif "error" in response_data:
                            print(f"   ⚠️  JSON-RPC ERROR: {response_data['error']}")
                            if test_info["critical"]:
                                results["smithery_compatible"] = False
                        else:
                            print(f"   ⚠️  Invalid JSON-RPC response format")
                    else:
                        print(f"   ⚠️  Non-JSON-RPC response: {str(response_data)[:100]}")
                except:
                    test_result["response_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"   ✅ SUCCESS (HTTP {response.status_code}) - Non-JSON response")
                    
            elif response.status_code == 401:
                print(f"   ❌ AUTHENTICATION REQUIRED (HTTP 401) - Discovery should be open!")
                test_result["error"] = f"HTTP 401 - Authentication required for discovery"
                results["smithery_compatible"] = False
                if test_info["critical"]:
                    results["overall_success"] = False
            elif response.status_code == 403:
                print(f"   ❌ FORBIDDEN (HTTP 403) - Discovery should be accessible!")
                test_result["error"] = f"HTTP 403 - Forbidden"
                results["smithery_compatible"] = False
                if test_info["critical"]:
                    results["overall_success"] = False
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND (HTTP 404) - MCP endpoint not available")
                test_result["error"] = f"HTTP 404 - MCP endpoint not found"
                results["smithery_compatible"] = False
                if test_info["critical"]:
                    results["overall_success"] = False
            elif response.status_code == 405:
                print(f"   ❌ METHOD NOT ALLOWED (HTTP 405) - POST should be supported")
                test_result["error"] = f"HTTP 405 - Method not allowed"
                results["smithery_compatible"] = False
                if test_info["critical"]:
                    results["overall_success"] = False
            elif response.status_code == 406:
                print(f"   ❌ NOT ACCEPTABLE (HTTP 406) - Headers issue")
                test_result["error"] = f"HTTP 406 - Not acceptable"
                results["smithery_compatible"] = False
                if test_info["critical"]:
                    results["overall_success"] = False
            else:
                print(f"   ❌ FAILED (HTTP {response.status_code})")
                test_result["error"] = f"HTTP {response.status_code}"
                if test_info["critical"]:
                    results["smithery_compatible"] = False
                    results["overall_success"] = False
            
            results["tests"][test_name] = test_result
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR: {str(e)}")
            results["tests"][test_name] = {
                "endpoint": mcp_endpoint,
                "description": test_info["description"],
                "status_code": None,
                "success": False,
                "error": str(e),
                "smithery_critical": test_info["critical"]
            }
            results["overall_success"] = False
            if test_info["critical"]:
                results["smithery_compatible"] = False
        
        print()
    
    return results

def test_http_endpoints(base_url: str = "http://localhost:8080") -> Dict[str, Any]:
    """Test basic HTTP endpoints for server health"""
    
    results = {
        "base_url": base_url,
        "tests": {},
        "overall_success": True
    }
    
    print(f"🔍 Testing Basic HTTP Endpoints...")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Basic HTTP endpoints
    endpoints = {
        "/health": "Server health check"
    }
    
    for endpoint, description in endpoints.items():
        test_name = endpoint.replace("/", "_").strip("_") or "root"
        url = f"{base_url}{endpoint}"
        
        try:
            print(f"📡 Testing {endpoint} - {description}")
            
            response = requests.get(url, timeout=10)
            
            test_result = {
                "url": url,
                "description": description,
                "status_code": response.status_code,
                "success": False,
                "response_data": None,
                "error": None
            }
            
            if 200 <= response.status_code < 300:
                test_result["success"] = True
                try:
                    test_result["response_data"] = response.json()
                except:
                    test_result["response_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"   ✅ SUCCESS (HTTP {response.status_code})")
            else:
                print(f"   ❌ FAILED (HTTP {response.status_code})")
                test_result["error"] = f"HTTP {response.status_code}"
                results["overall_success"] = False
            
            results["tests"][test_name] = test_result
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR: {str(e)}")
            results["tests"][test_name] = {
                "url": url,
                "description": description,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
            results["overall_success"] = False
        
        print()
    
    return results

def test_production_simulation():
    """Test with simulated production environment variables (as Smithery would set them)"""
    
    print("🧪 TESTING PRODUCTION SIMULATION")
    print("=" * 50)
    
    # Backup original environment
    original_env = {
        "DESCOPE_PROJECT_ID": os.environ.get("DESCOPE_PROJECT_ID"),
        "DESCOPE_MANAGEMENT_KEY": os.environ.get("DESCOPE_MANAGEMENT_KEY")
    }
    
    try:
        # Set simulated Smithery production credentials
        os.environ["DESCOPE_PROJECT_ID"] = "P2l8xGh4KQf3wXr9mN5yZ1vB"  # Fake production-like project ID
        os.environ["DESCOPE_MANAGEMENT_KEY"] = "K1:fake_management_key_for_testing_purposes_only"  # Fake management key
        
        print(f"🔧 Set simulated production credentials:")
        print(f"   DESCOPE_PROJECT_ID: P2l8xGh4KQf3wXr9mN5yZ1vB")  
        print(f"   DESCOPE_MANAGEMENT_KEY: K1:fake_management_key...")
        print()
        
        # Test server startup with production credentials
        print("🚀 Testing server startup with production credentials...")
        
        # Start server as subprocess
        server_process = subprocess.Popen([
            sys.executable, "mcp_server.py"
        ], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait for server to start
        time.sleep(3)
        
        if server_process.poll() is None:
            print("✅ Server started successfully with production credentials")
            
            # Test basic endpoints first
            http_results = test_http_endpoints()
            
            # Test MCP protocol endpoints
            mcp_results = test_mcp_json_rpc_endpoints()
            
            # Stop server
            server_process.terminate()
            server_process.wait(timeout=5)
            
            return {
                "server_startup": True,
                "http_tests": http_results,
                "mcp_tests": mcp_results,
                "smithery_compatible": mcp_results.get("smithery_compatible", False)
            }
        else:
            print("❌ Server failed to start with production credentials")
            output, _ = server_process.communicate()
            print(f"Server output: {output}")
            return {
                "server_startup": False, 
                "error": "Server startup failed",
                "output": output,
                "smithery_compatible": False
            }
            
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

def main():
    """Main test function"""
    print("🔥 SMITHERY DEPLOYMENT FIX VERIFICATION")
    print("=" * 60)
    print()
    
    # Test 1: Current demo mode
    print("📋 TEST 1: Demo Mode (Current Configuration)")
    print("-" * 40)
    try:
        http_results = test_http_endpoints()
        mcp_results = test_mcp_json_rpc_endpoints()
        demo_compatible = mcp_results.get("smithery_compatible", False)
    except Exception as e:
        print(f"❌ Demo mode test failed: {e}")
        demo_compatible = False
    
    print("\n📋 TEST 2: Production Mode Simulation") 
    print("-" * 40)
    prod_results = test_production_simulation()
    prod_compatible = prod_results.get("smithery_compatible", False) if isinstance(prod_results, dict) else False
    
    # Summary
    print("\n📊 FINAL RESULTS")
    print("=" * 30)
    
    print(f"Demo Mode Smithery Compatible: {'✅ YES' if demo_compatible else '❌ NO'}")
    print(f"Production Mode Smithery Compatible: {'✅ YES' if prod_compatible else '❌ NO'}")
    
    overall_fix_success = demo_compatible and prod_compatible
    print(f"\n🎯 OVERALL FIX STATUS: {'✅ SUCCESS' if overall_fix_success else '❌ NEEDS MORE WORK'}")
    
    if overall_fix_success:
        print("\n🎉 Smithery deployment should now work successfully!")
        print("   • MCP JSON-RPC discovery endpoints are accessible without authentication")
        print("   • Server starts reliably with any credential configuration")
        print("   • Graceful degradation prevents startup failures")
        print("   • Proper MCP protocol support for tool discovery")
    else:
        print("\n⚠️  Issues still need to be resolved:")
        if not demo_compatible:
            print("   • Demo mode MCP discovery endpoints are not working")
        if not prod_compatible:
            print("   • Production mode has issues with credential handling")
    
    return overall_fix_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)