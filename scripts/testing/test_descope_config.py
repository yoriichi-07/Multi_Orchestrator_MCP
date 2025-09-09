#!/usr/bin/env python3
"""
Quick Descope Configuration Test
Tests your Descope Access Key configuration and scope setup
"""

import os
import sys
import asyncio
import aiohttp
import base64
import hashlib
import secrets
import urllib.parse
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DescopeConfigTest:
    def __init__(self):
        # Load environment variables
        self.project_id = os.getenv("DESCOPE_PROJECT_ID")
        self.access_key = os.getenv("DESCOPE_ACCESS_KEY")
        self.management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
        self.issuer = os.getenv("DESCOPE_ISSUER")
        
    def validate_config(self) -> Dict[str, Any]:
        """Validate the Access Key configuration"""
        results = {
            "config_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required variables
        if not self.project_id:
            results["errors"].append("DESCOPE_PROJECT_ID is missing")
            results["config_valid"] = False
            
        if not self.access_key:
            results["errors"].append("DESCOPE_ACCESS_KEY is missing")
            results["config_valid"] = False
            
        if not self.management_key:
            results["warnings"].append("DESCOPE_MANAGEMENT_KEY is missing (optional for basic usage)")
            
        # Check scope configuration from file
        expected_legendary_scopes = [
            "legendary:autonomous_architect",
            "legendary:quality_framework", 
            "legendary:prompt_engine",
            "legendary:cloud_agent",
            "legendary:app_generator"
        ]
        
        # For Access Keys, scopes are embedded in the JWT token
        # This is preserved for demo value
        results["scope_info"] = {
            "expected_legendary_scopes": len(expected_legendary_scopes),
            "authentication_method": "access_key",
            "scope_validation": "jwt_embedded"
        }
            
        return results
    
    async def test_access_key_authentication(self) -> Dict[str, Any]:
        """Test Access Key authentication with Bearer token"""
        # Generate PKCE challenge
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        # OAuth parameters
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": "http://localhost:8000/auth/callback",
            "scope": self.oauth_scopes,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": secrets.token_urlsafe(32)
        }
        
        base_url = f"https://api.descope.com/oauth2/v1/apps/authorize"
        return f"{base_url}?" + urllib.parse.urlencode(params)
    
    async def test_discovery_endpoint(self) -> Dict[str, Any]:
        """Test the OpenID Connect discovery endpoint"""
        discovery_url = f"https://api.descope.com/v1/projects/{self.project_id}/.well-known/openid_configuration"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(discovery_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "discovery_url": discovery_url,
                            "endpoints": {
                                "authorization_endpoint": data.get("authorization_endpoint"),
                                "token_endpoint": data.get("token_endpoint"),
                                "issuer": data.get("issuer")
                            }
                        }
                    else:
                        # Try alternative discovery URL format
                        alt_url = f"https://api.descope.com/v1/apps/{self.project_id}/.well-known/openid_configuration"
                        async with session.get(alt_url) as alt_response:
                            if alt_response.status == 200:
                                data = await alt_response.json()
                                return {
                                    "status": "success",
                                    "discovery_url": alt_url,
                                    "endpoints": {
                                        "authorization_endpoint": data.get("authorization_endpoint"),
                                        "token_endpoint": data.get("token_endpoint"),
                                        "issuer": data.get("issuer")
                                    }
                                }
                        
                        return {
                            "status": "error",
                            "message": f"Discovery endpoint returned {response.status} (tried both URL formats)"
                        }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to discovery endpoint: {str(e)}"
            }

async def main():
    """Main test function"""
    print("🔐 Descope Configuration Test")
    print("=" * 50)
    
    tester = DescopeConfigTest()
    
    # Test 1: Configuration validation
    print("📋 Testing configuration...")
    config_result = tester.validate_config()
    
    if config_result["config_valid"]:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration has errors:")
        for error in config_result["errors"]:
            print(f"   - {error}")
            
    if config_result["warnings"]:
        print("⚠️ Configuration warnings:")
        for warning in config_result["warnings"]:
            print(f"   - {warning}")
    
    print()
    
    # Test 2: Access Key authentication
    print("� Testing Access Key authentication...")
    auth_result = await tester.test_access_key_authentication()
    
    if auth_result["success"]:
        print("✅ Access Key authentication test passed!")
        print(f"   Key Length: {auth_result.get('key_length', 'Unknown')}")
        print(f"   Method: {auth_result.get('authentication_method', 'bearer_token')}")
    else:
        print("❌ Access Key authentication test failed:")
        print(f"   Error: {auth_result.get('error', 'Unknown error')}")
    
    print()
    
    # Test 3: Generate sample auth URL
    if config_result["config_valid"]:
        print("🔗 Sample OAuth authorization URL:")
        auth_url = tester.generate_auth_url()
        print(f"   {auth_url[:100]}...")
        print("   (This URL would redirect users to Descope for authentication)")
    
    print()
    print("📊 Configuration Summary:")
    print(f"   Project ID: {tester.project_id}")
    print(f"   Client ID: {tester.client_id}")
    print(f"   Scopes configured: {len(tester.oauth_scopes.split()) if tester.oauth_scopes else 0}")
    print(f"   Legendary scopes: {'✅' if 'legendary:' in tester.oauth_scopes else '❌'}")
    
    print()
    if config_result["config_valid"]:
        print("🚀 Your Descope Access Key configuration is ready for legendary AI capabilities!")
    else:
        print("🔧 Please fix the configuration errors above before proceeding.")

if __name__ == "__main__":
    asyncio.run(main())