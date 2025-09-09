#!/usr/bin/env python3
"""
Descope Configuration Helper for Multi-Agent Orchestrator MCP Server
This script helps you configure your legendary AI capabilities in Descope
"""

import json
import os
from typing import Dict, List, Any

class DescopeConfigHelper:
    def __init__(self, project_id: str, client_id: str):
        self.project_id = project_id
        self.client_id = client_id
        self.base_url = f"https://api.descope.com/v1/projects/{project_id}"
    
    def get_legendary_scopes_config(self) -> List[Dict[str, Any]]:
        """Get the complete legendary scopes configuration"""
        return [
            # Legendary Agent Scopes
            {
                "name": "legendary:autonomous_architect",
                "description": "Access to Autonomous Architect agent for revolutionary system design",
                "type": "permission",
                "roles": ["legendary_user", "admin_user"],
                "mandatory": False
            },
            {
                "name": "legendary:quality_framework", 
                "description": "Access to Proactive Quality Framework for intelligent QA",
                "type": "permission",
                "roles": ["legendary_user", "admin_user"],
                "mandatory": False
            },
            {
                "name": "legendary:prompt_engine",
                "description": "Access to Evolutionary Prompt Engine for self-improving prompts", 
                "type": "permission",
                "roles": ["legendary_user", "developer", "admin_user"],
                "mandatory": False
            },
            {
                "name": "legendary:cloud_agent",
                "description": "Access to Last Mile Cloud Agent for seamless deployment",
                "type": "permission", 
                "roles": ["legendary_user", "admin_user"],
                "mandatory": False
            },
            {
                "name": "legendary:app_generator",
                "description": "Access to Legendary Application Generator for full-stack creation",
                "type": "permission",
                "roles": ["legendary_user", "admin_user"], 
                "mandatory": False
            },
            
            # Enhanced Standard Tool Scopes
            {
                "name": "tools:basic",
                "description": "Access to basic connectivity and health check tools",
                "type": "permission",
                "roles": ["standard_user", "legendary_user", "developer", "admin_user"],
                "mandatory": True
            },
            {
                "name": "tools:generation", 
                "description": "Access to standard code generation tools",
                "type": "permission",
                "roles": ["standard_user", "legendary_user", "developer", "admin_user"],
                "mandatory": False
            },
            {
                "name": "tools:infrastructure",
                "description": "Access to infrastructure management tools",
                "type": "permission",
                "roles": ["legendary_user", "admin_user"],
                "mandatory": False
            },
            {
                "name": "tools:quality",
                "description": "Access to standard quality assurance tools", 
                "type": "permission",
                "roles": ["standard_user", "legendary_user", "developer", "admin_user"],
                "mandatory": False
            },
            
            # Enhanced Admin Scopes
            {
                "name": "admin:analytics",
                "description": "Access to analytics dashboard and performance monitoring",
                "type": "permission",
                "roles": ["admin_user"],
                "mandatory": False
            },
            {
                "name": "admin:full",
                "description": "Full administrative access to all system features",
                "type": "permission", 
                "roles": ["admin_user"],
                "mandatory": False
            },
            
            # User Information Scopes
            {
                "name": "profile",
                "description": "Access to user profile information",
                "type": "user_info",
                "user_attribute": "email",
                "roles": ["standard_user", "legendary_user", "developer", "admin_user"],
                "mandatory": True
            },
            {
                "name": "email", 
                "description": "Access to user email address",
                "type": "user_info",
                "user_attribute": "email",
                "roles": ["standard_user", "legendary_user", "developer", "admin_user"], 
                "mandatory": True
            }
        ]
    
    def get_user_roles_config(self) -> List[Dict[str, Any]]:
        """Get the user roles configuration for RBAC"""
        return [
            {
                "name": "legendary_user",
                "description": "Users with access to all legendary AI agents and advanced features",
                "permissions": [
                    "legendary:autonomous_architect",
                    "legendary:quality_framework", 
                    "legendary:prompt_engine",
                    "legendary:cloud_agent",
                    "legendary:app_generator",
                    "tools:basic",
                    "tools:generation",
                    "tools:infrastructure", 
                    "tools:quality"
                ]
            },
            {
                "name": "standard_user",
                "description": "Users with access to standard tools only",
                "permissions": [
                    "tools:basic",
                    "tools:generation",
                    "tools:quality"
                ]
            },
            {
                "name": "developer", 
                "description": "Developers with access to development and testing tools",
                "permissions": [
                    "tools:basic",
                    "tools:generation", 
                    "tools:quality",
                    "legendary:prompt_engine",
                    "legendary:quality_framework"
                ]
            },
            {
                "name": "admin_user",
                "description": "Administrators with full system access",
                "permissions": [
                    "admin:full",
                    "admin:analytics", 
                    "legendary:*",
                    "tools:*"
                ]
            }
        ]
    
    def get_environment_config(self) -> Dict[str, str]:
        """Get the complete environment configuration"""
        return {
            # Core Descope Configuration
            "DESCOPE_PROJECT_ID": self.project_id,
            "DESCOPE_CLIENT_ID": self.client_id,
            "DESCOPE_ISSUER": f"https://api.descope.com/v1/projects/{self.project_id}",
            "DESCOPE_AUDIENCE": "mcp-server",
            "DESCOPE_DISCOVERY_URL": f"https://api.descope.com/v1/apps/{self.project_id}/.well-known/openid_configuration",
            
            # OAuth 2.1 + PKCE Configuration
            "OAUTH_AUTHORIZATION_URL": f"https://api.descope.com/oauth2/v1/apps/authorize",
            "OAUTH_TOKEN_URL": f"https://api.descope.com/oauth2/v1/apps/token",
            "OAUTH_REDIRECT_URI": "http://localhost:8000/auth/callback",
            "OAUTH_SCOPE": "openid profile email legendary:* tools:* admin:analytics",
            "OAUTH_PKCE_ENABLED": "true",
            "OAUTH_PKCE_CODE_CHALLENGE_METHOD": "S256",
            
            # JWT Configuration
            "JWT_ALGORITHM": "RS256",
            "JWT_VERIFY_SIGNATURE": "true",
            "JWT_VERIFY_EXPIRATION": "true",
            "JWT_VERIFY_AUDIENCE": "true",
            "JWT_VERIFY_ISSUER": "true",
            "JWT_REQUIRE_CLAIMS": "exp,iat,sub,scope",
            
            # Security Configuration
            "SECURITY_RATE_LIMIT_ENABLED": "true",
            "SECURITY_RATE_LIMIT_REQUESTS": "100",
            "SECURITY_RATE_LIMIT_WINDOW": "60",
            "SECURITY_CORS_ENABLED": "true",
            "SECURITY_CORS_ORIGINS": "http://localhost:8000,http://localhost:3000",
            
            # Legendary Features Configuration
            "LEGENDARY_FEATURE_FLAG": "true",
            "REQUIRE_LEGENDARY_SCOPES": "true",
            "LEGENDARY_AUDIT_LOGGING": "true",
            "LEGENDARY_SECURITY_MODE": "enhanced",
            
            # Scope Requirements for Tools
            "DESCOPE_LEGENDARY_SCOPES": "legendary:autonomous_architect,legendary:quality_framework,legendary:prompt_engine,legendary:cloud_agent,legendary:app_generator",
            "DESCOPE_STANDARD_SCOPES": "tools:basic,tools:generation,tools:infrastructure,tools:quality",
            "DESCOPE_ADMIN_SCOPES": "admin:full,admin:analytics"
        }
    
    def generate_manual_configuration_guide(self) -> str:
        """Generate step-by-step manual configuration guide"""
        guide = """
# 🚀 Manual Descope Configuration Guide for Legendary AI Capabilities

## Step 1: Add Legendary Scopes to Your Descope Console

1. Go to https://app.descope.com/apps/inbound
2. Click on your "Autonomous Software Foundry" app
3. Navigate to the "Settings" tab
4. Scroll down to "Scopes" section
5. Click "+ Scope" for each scope below:

### Permission Scopes to Add:
"""
        
        scopes = self.get_legendary_scopes_config()
        for scope in scopes:
            if scope["type"] == "permission":
                guide += f"""
**{scope['name']}**
- Description: {scope['description']}
- Type: Permission Scope
- Roles: {', '.join(scope['roles'])}
- Mandatory: {'Yes' if scope['mandatory'] else 'No'}
"""
        
        guide += """
### User Information Scopes to Add:
"""
        for scope in scopes:
            if scope["type"] == "user_info":
                guide += f"""
**{scope['name']}**
- Description: {scope['description']}
- Type: User Information Scope  
- User Attribute: {scope['user_attribute']}
- Mandatory: {'Yes' if scope['mandatory'] else 'No'}
"""
        
        guide += f"""
## Step 2: Configure Redirect URIs

Ensure these redirect URIs are configured:
- http://localhost:8000/auth/callback (for development)
- http://localhost:3000/auth/callback (for frontend testing)
- https://auth.aigateway.cequence.ai/v1/outbound/oauth/callback (for Cequence)

## Step 3: Extract Your Configuration Values

From your Descope console, note these values:
- Project ID: {self.project_id}
- Client ID: {self.client_id}
- Client Secret: (visible in console - copy this securely)
- Management Key: (from Project Settings → Access Keys)

## Step 4: Update Your Environment Variables

Copy these values to your .env file:
"""
        
        env_config = self.get_environment_config()
        for key, value in env_config.items():
            guide += f"{key}={value}\n"
        
        guide += """
## Step 5: Test Your Configuration

Run the validation script:
```bash
python scripts/test_descope_configuration.py
```

🎯 Your legendary AI capabilities will be ready!
"""
        return guide
    
    def save_configuration_files(self):
        """Save all configuration files"""
        # Save scopes configuration with Access Key authentication metadata
        with open("descope_scopes_config.json", "w") as f:
            json.dump({
                "authentication_method": "descope_access_key",
                "description": "Descope Access Key authentication with scope-based authorization",
                "version": "2.0",
                "migration_from": "oauth_2.1_pkce",
                "access_key_usage": {
                    "description": "Access Keys provide direct JWT tokens with embedded scopes",
                    "token_format": "Bearer JWT",
                    "scope_validation": "server_side",
                    "cequence_integration": "passthrough_mode"
                },
                "scopes": self.get_legendary_scopes_config(),
                "roles": self.get_user_roles_config(),
                "access_key_integration": {
                    "scope_embedding": "Scopes are embedded in Access Key JWT tokens",
                    "validation_method": "JWT signature validation with Descope public keys",
                    "cequence_passthrough": "Cequence Gateway forwards Bearer tokens unchanged",
                    "demo_value": "All scope definitions preserved for authorization demo"
                }
            }, f, indent=2)
        
        # Save environment configuration
        with open("descope_env_config.env", "w") as f:
            env_config = self.get_environment_config()
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        # Save manual guide
        with open("DESCOPE_CONFIGURATION_GUIDE.md", "w", encoding='utf-8') as f:
            f.write(self.generate_manual_configuration_guide())
        
        print("✅ Configuration files generated:")
        print("  📄 descope_scopes_config.json - Access Key authentication with scopes and roles")
        print("  🔧 descope_env_config.env - Environment variables for Access Key setup")
        print("  📚 DESCOPE_CONFIGURATION_GUIDE.md - Access Key configuration guide")

def main():
    """Main configuration helper"""
    print("🔐 Descope Configuration Helper for Multi-Agent Orchestrator MCP")
    print("=" * 70)
    
    # Your actual Descope values
    project_id = "P31WC6A6Vybbt7N5NhnH4dZLQgXY"
    client_id = "UDMxV0M2TZWeWJidDd0NU5obkgDZFrpMUWdYWTpUUEEzMkJ1UG1UWVhDYm1UOWo5Q0SnBBc"
    
    helper = DescopeConfigHelper(project_id, client_id)
    
    print(f"📋 Project ID: {project_id}")
    print(f"🔑 Client ID: {client_id}")
    print()
    
    print("🎯 Generating configuration files...")
    helper.save_configuration_files()
    print()
    
    print("🚀 Next steps:")
    print("1. Review DESCOPE_CONFIGURATION_GUIDE.md")
    print("2. Add the legendary scopes to your Descope console")
    print("3. Update your .env file with values from descope_env_config.env")
    print("4. Test the configuration")
    print()
    
    print("💫 Your legendary AI capabilities are almost ready!")

if __name__ == "__main__":
    main()