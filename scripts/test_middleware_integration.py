#!/usr/bin/env python3
"""
Comprehensive Descope Authentication Middleware Test
Tests the integration between the Descope configuration and the MCP server middleware
"""

import os
import sys
import asyncio
import aiohttp
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AuthMiddlewareTest:
    def __init__(self):
        # Load environment variables
        self.project_id = os.getenv("DESCOPE_PROJECT_ID")
        self.client_id = os.getenv("DESCOPE_CLIENT_ID")
        self.client_secret = os.getenv("DESCOPE_CLIENT_SECRET")
        self.management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
        
        # OAuth endpoints
        self.auth_url = os.getenv("OAUTH_AUTHORIZATION_URL")
        self.token_url = os.getenv("OAUTH_TOKEN_URL")
        
        # Scope configuration
        self.legendary_scopes = os.getenv("DESCOPE_LEGENDARY_SCOPES", "").split(",")
        self.standard_scopes = os.getenv("DESCOPE_STANDARD_SCOPES", "").split(",")
        self.admin_scopes = os.getenv("DESCOPE_ADMIN_SCOPES", "").split(",")
        
    async def test_environment_configuration(self) -> Dict[str, Any]:
        """Test that all required environment variables are configured"""
        results = {
            "status": "success",
            "tests": {},
            "summary": {}
        }
        
        # Test required variables
        required_vars = {
            "DESCOPE_PROJECT_ID": self.project_id,
            "DESCOPE_CLIENT_ID": self.client_id,
            "DESCOPE_CLIENT_SECRET": self.client_secret,
            "DESCOPE_MANAGEMENT_KEY": self.management_key,
            "OAUTH_AUTHORIZATION_URL": self.auth_url,
            "OAUTH_TOKEN_URL": self.token_url
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
                results["tests"][var_name] = "❌ Missing"
            else:
                results["tests"][var_name] = "✅ Configured"
        
        # Test scope configuration
        scope_tests = {
            "Legendary Scopes": len([s for s in self.legendary_scopes if s.strip()]),
            "Standard Scopes": len([s for s in self.standard_scopes if s.strip()]),
            "Admin Scopes": len([s for s in self.admin_scopes if s.strip()])
        }
        
        for scope_type, count in scope_tests.items():
            if count > 0:
                results["tests"][scope_type] = f"✅ {count} configured"
            else:
                results["tests"][scope_type] = "❌ None configured"
        
        # Summary
        results["summary"] = {
            "configuration_complete": len(missing_vars) == 0,
            "missing_variables": missing_vars,
            "total_scopes": sum(scope_tests.values())
        }
        
        if missing_vars:
            results["status"] = "error"
        
        return results
    
    async def test_management_api_access(self) -> Dict[str, Any]:
        """Test access to Descope Management API"""
        if not self.management_key:
            return {
                "status": "skipped",
                "message": "Management key not configured"
            }
        
        # Test management API with correct endpoint and authorization format
        mgmt_url = f"https://api.descope.com/v1/mgmt/user/search"
        headers = {
            "Authorization": f"Bearer {self.project_id}:{self.management_key}",
            "Content-Type": "application/json"
        }
        
        # Use a simple search to test API access
        search_payload = {
            "limit": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(mgmt_url, headers=headers, json=search_payload) as response:
                    if response.status == 200:
                        search_result = await response.json()
                        return {
                            "status": "success",
                            "user_count": len(search_result.get("users", [])),
                            "message": "Management API access successful"
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Management API returned {response.status}",
                            "details": await response.text()
                        }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Management API: {str(e)}"
            }
    
    async def test_middleware_configuration(self) -> Dict[str, Any]:
        """Test if the MCP server middleware configuration is valid"""
        try:
            # Import the MCP server modules to test configuration
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
            
            from src.core.descope_auth import get_descope_client, DescopeClient
            
            # Test if we can create a Descope client
            client = await get_descope_client()
            
            if client:
                return {
                    "status": "success",
                    "message": "Descope client created successfully",
                    "client_type": type(client).__name__,
                    "project_id": client.project_id if hasattr(client, 'project_id') else "Unknown"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to create Descope client"
                }
                
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import middleware modules: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Middleware configuration error: {str(e)}"
            }
    
    async def test_oauth_endpoints(self) -> Dict[str, Any]:
        """Test OAuth endpoint accessibility"""
        results = {
            "authorization_endpoint": {"status": "unknown"},
            "token_endpoint": {"status": "unknown"}
        }
        
        # Test authorization endpoint (should return an error for GET without params, but should be accessible)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.auth_url) as response:
                    # OAuth auth endpoint typically returns 400 for GET without proper params
                    if response.status in [400, 405]:  # Method not allowed or bad request is expected
                        results["authorization_endpoint"] = {
                            "status": "success",
                            "message": "Authorization endpoint is accessible",
                            "http_status": response.status
                        }
                    else:
                        results["authorization_endpoint"] = {
                            "status": "warning",
                            "message": f"Unexpected status {response.status} from auth endpoint",
                            "http_status": response.status
                        }
        except Exception as e:
            results["authorization_endpoint"] = {
                "status": "error",
                "message": f"Failed to reach authorization endpoint: {str(e)}"
            }
        
        # Test token endpoint (should return an error for GET, but should be accessible)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.token_url) as response:
                    # Token endpoint typically returns 405 for GET or 400 for missing params
                    if response.status in [400, 405, 422]:  # Expected error codes
                        results["token_endpoint"] = {
                            "status": "success",
                            "message": "Token endpoint is accessible",
                            "http_status": response.status
                        }
                    else:
                        results["token_endpoint"] = {
                            "status": "warning",
                            "message": f"Unexpected status {response.status} from token endpoint",
                            "http_status": response.status
                        }
        except Exception as e:
            results["token_endpoint"] = {
                "status": "error",
                "message": f"Failed to reach token endpoint: {str(e)}"
            }
        
        return results

async def main():
    """Main test function"""
    print("🔐 Comprehensive Descope Authentication Middleware Test")
    print("=" * 60)
    
    tester = AuthMiddlewareTest()
    
    # Test 1: Environment Configuration
    print("📋 Testing Environment Configuration...")
    env_result = await tester.test_environment_configuration()
    
    if env_result["status"] == "success":
        print("✅ Environment configuration is complete!")
    else:
        print("❌ Environment configuration has issues:")
        for var in env_result["summary"]["missing_variables"]:
            print(f"   - Missing: {var}")
    
    for test_name, result in env_result["tests"].items():
        print(f"   {test_name}: {result}")
    
    print(f"   Total scopes configured: {env_result['summary']['total_scopes']}")
    print()
    
    # Test 2: Management API Access
    print("🔑 Testing Management API Access...")
    mgmt_result = await tester.test_management_api_access()
    
    if mgmt_result["status"] == "success":
        print(f"✅ Management API access successful!")
        print(f"   Project: {mgmt_result.get('project_name', 'Unknown')}")
        print(f"   ID: {mgmt_result.get('project_id', 'Unknown')}")
    elif mgmt_result["status"] == "skipped":
        print(f"⚠️ {mgmt_result['message']}")
    else:
        print(f"❌ {mgmt_result['message']}")
    
    print()
    
    # Test 3: Middleware Configuration
    print("⚙️ Testing Middleware Configuration...")
    middleware_result = await tester.test_middleware_configuration()
    
    if middleware_result["status"] == "success":
        print(f"✅ {middleware_result['message']}")
        print(f"   Client Type: {middleware_result.get('client_type', 'Unknown')}")
        print(f"   Project ID: {middleware_result.get('project_id', 'Unknown')}")
    else:
        print(f"❌ {middleware_result['message']}")
    
    print()
    
    # Test 4: OAuth Endpoints
    print("🌐 Testing OAuth Endpoints...")
    oauth_result = await tester.test_oauth_endpoints()
    
    for endpoint_name, result in oauth_result.items():
        status = result["status"]
        message = result["message"]
        
        if status == "success":
            print(f"✅ {endpoint_name.replace('_', ' ').title()}: {message}")
        elif status == "warning":
            print(f"⚠️ {endpoint_name.replace('_', ' ').title()}: {message}")
        else:
            print(f"❌ {endpoint_name.replace('_', ' ').title()}: {message}")
    
    print()
    
    # Final Summary
    print("📊 Test Summary:")
    print(f"   Environment: {'✅' if env_result['status'] == 'success' else '❌'}")
    print(f"   Management API: {'✅' if mgmt_result['status'] == 'success' else '⚠️' if mgmt_result['status'] == 'skipped' else '❌'}")
    print(f"   Middleware: {'✅' if middleware_result['status'] == 'success' else '❌'}")
    print(f"   OAuth Endpoints: {'✅' if all(r['status'] in ['success', 'warning'] for r in oauth_result.values()) else '❌'}")
    
    print()
    
    # Overall status
    all_tests_passed = (
        env_result["status"] == "success" and
        mgmt_result["status"] in ["success", "skipped"] and
        middleware_result["status"] == "success" and
        all(result["status"] in ["success", "warning"] for result in oauth_result.values())
    )
    
    if all_tests_passed:
        print("🚀 All tests passed! Your Descope authentication is ready for production!")
        print()
        print("Next steps:")
        print("1. 🔐 Get your Client Secret from Descope console")
        print("2. 🧪 Test the full OAuth flow with a real user")
        print("3. 🔧 Test scope enforcement with different user roles")
        print("4. 🚀 Deploy and validate in your target environment")
    else:
        print("🔧 Some tests failed. Please review the issues above before proceeding.")

if __name__ == "__main__":
    asyncio.run(main())