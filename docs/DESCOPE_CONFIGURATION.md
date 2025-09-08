# Descope Authentication Configuration Guide

## Overview

This guide provides comprehensive instructions for configuring Descope authentication with OAuth 2.1 + PKCE for the Multi-Agent Orchestrator MCP server. Descope integration enables secure authentication for all 16 tools with scope-based authorization.

## 🔐 Authentication Architecture

```
Client Request → Descope OAuth 2.1 + PKCE → MCP Server → Scope Validation → Tool Execution
```

### Key Features
- **OAuth 2.1 + PKCE**: Enhanced security for public clients
- **Scope-Based Authorization**: Granular permissions per tool
- **JWT Token Validation**: Secure token verification
- **Rate Limiting**: Protection against abuse
- **Audit Logging**: Complete request tracking

## 📋 Prerequisites

1. **Descope Account**: Register at [descope.com](https://descope.com)
2. **Project Setup**: Create new Descope project
3. **Domain Configuration**: Configure allowed domains
4. **Application Registration**: Register MCP server as application

## 🚀 Descope Project Setup

### Step 1: Create Descope Project

1. **Login to Descope Console**
   ```
   URL: https://app.descope.com
   ```

2. **Create New Project**
   - Navigate to "Projects" → "Create Project"
   - Project Name: `Multi-Agent-Orchestrator-MCP`
   - Description: `MCP Server with 5 Legendary Agents`

3. **Project Configuration**
   ```yaml
   Project Settings:
     Environment: Production
     Region: US (or closest to your deployment)
     Security Level: High
   ```

### Step 2: Application Registration

1. **Create OAuth Application**
   ```yaml
   Application Details:
     Name: "MCP Server Authentication"
     Type: "Web Application"
     Grant Types:
       - authorization_code
       - refresh_token
     PKCE: Required
   ```

2. **Redirect URIs**
   ```
   Development:
     - http://localhost:8000/auth/callback
     - http://localhost:3000/auth/callback
   
   Production:
     - https://your-domain.com/auth/callback
     - https://api.your-domain.com/auth/callback
   ```

3. **Allowed Origins**
   ```
   Development:
     - http://localhost:8000
     - http://localhost:3000
   
   Production:
     - https://your-domain.com
     - https://api.your-domain.com
   ```

### Step 3: Scope Configuration

Configure the following scopes for tool authorization:

```yaml
# Legendary Tool Scopes
legendary:autonomous_architect:
  description: "Access to Autonomous Architect agent"
  required_for: ["create_autonomous_architecture", "analyze_system_requirements"]

legendary:quality_framework:
  description: "Access to Proactive Quality Framework"
  required_for: ["proactive_quality_analysis", "generate_quality_metrics"]

legendary:prompt_engine:
  description: "Access to Evolutionary Prompt Engine"
  required_for: ["evolutionary_prompt_optimization", "context_aware_prompting"]

legendary:cloud_agent:
  description: "Access to Last Mile Cloud Agent"
  required_for: ["cloud_deployment_automation", "infrastructure_optimization"]

legendary:app_generator:
  description: "Access to Legendary Application Generator"
  required_for: ["generate_legendary_application", "full_stack_architecture"]

# Standard Tool Scopes
tools:basic:
  description: "Access to basic tools"
  required_for: ["echo_tool", "status_check", "help_tool"]

tools:generation:
  description: "Access to generation tools"
  required_for: ["generate_code", "create_template", "generate_docs"]

tools:infrastructure:
  description: "Access to infrastructure tools"
  required_for: ["deploy_service", "manage_containers", "monitor_health"]

tools:quality:
  description: "Access to quality tools"
  required_for: ["run_tests", "code_analysis", "security_scan"]

# Admin Scopes
admin:full:
  description: "Full administrative access"
  required_for: ["all_tools", "user_management", "system_configuration"]

admin:analytics:
  description: "Access to analytics and monitoring"
  required_for: ["view_analytics", "export_metrics", "system_monitoring"]
```

### Step 4: User Roles Configuration

```yaml
# User Roles
roles:
  legendary_user:
    description: "Access to all legendary agents"
    scopes:
      - legendary:autonomous_architect
      - legendary:quality_framework
      - legendary:prompt_engine
      - legendary:cloud_agent
      - legendary:app_generator
      - tools:basic
      - tools:generation
      - tools:infrastructure
      - tools:quality

  standard_user:
    description: "Access to standard tools only"
    scopes:
      - tools:basic
      - tools:generation
      - tools:infrastructure
      - tools:quality

  admin_user:
    description: "Full system access"
    scopes:
      - admin:full
      - admin:analytics
      - legendary:*
      - tools:*

  developer:
    description: "Development and testing access"
    scopes:
      - tools:basic
      - tools:generation
      - tools:quality
      - legendary:prompt_engine
      - legendary:quality_framework
```

## 🔧 Environment Configuration

### Production Environment Variables

```bash
# Descope Configuration
DESCOPE_PROJECT_ID=your_project_id_here
DESCOPE_MANAGEMENT_KEY=your_management_key_here
DESCOPE_PUBLIC_KEY=your_public_key_here
DESCOPE_ISSUER=https://api.descope.com/v1/projects/your_project_id
DESCOPE_AUDIENCE=mcp-server

# OAuth 2.1 + PKCE Configuration
OAUTH_CLIENT_ID=your_client_id_here
OAUTH_REDIRECT_URI=https://your-domain.com/auth/callback
OAUTH_SCOPE=openid profile email legendary:* tools:*
OAUTH_PKCE_ENABLED=true
OAUTH_PKCE_CODE_CHALLENGE_METHOD=S256

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here_minimum_32_characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
JWT_REFRESH_EXPIRATION=86400
JWT_ISSUER=https://your-domain.com
JWT_AUDIENCE=mcp-server

# Security Configuration
SECURITY_RATE_LIMIT_ENABLED=true
SECURITY_RATE_LIMIT_REQUESTS=100
SECURITY_RATE_LIMIT_WINDOW=60
SECURITY_CORS_ENABLED=true
SECURITY_CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Session Configuration
SESSION_SECRET=your_session_secret_here_minimum_32_characters
SESSION_TIMEOUT=1800
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict
```

### Development Environment Variables

```bash
# Descope Configuration (Development)
DESCOPE_PROJECT_ID=your_dev_project_id_here
DESCOPE_MANAGEMENT_KEY=your_dev_management_key_here
DESCOPE_PUBLIC_KEY=your_dev_public_key_here
DESCOPE_ISSUER=https://api.descope.com/v1/projects/your_dev_project_id
DESCOPE_AUDIENCE=mcp-server-dev

# OAuth 2.1 + PKCE Configuration (Development)
OAUTH_CLIENT_ID=your_dev_client_id_here
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
OAUTH_SCOPE=openid profile email legendary:* tools:*
OAUTH_PKCE_ENABLED=true
OAUTH_PKCE_CODE_CHALLENGE_METHOD=S256

# JWT Configuration (Development)
JWT_SECRET=dev_secret_key_for_testing_only_minimum_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
JWT_REFRESH_EXPIRATION=86400
JWT_ISSUER=http://localhost:8000
JWT_AUDIENCE=mcp-server-dev

# Security Configuration (Development)
SECURITY_RATE_LIMIT_ENABLED=false
SECURITY_CORS_ENABLED=true
SECURITY_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Session Configuration (Development)
SESSION_SECRET=dev_session_secret_for_testing_only_32_chars
SESSION_TIMEOUT=3600
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
```

## 🔐 Security Best Practices

### JWT Token Validation

```python
# Example JWT validation configuration
JWT_VALIDATION_CONFIG = {
    "algorithms": ["RS256", "HS256"],
    "verify_signature": True,
    "verify_exp": True,
    "verify_nbf": True,
    "verify_iat": True,
    "verify_aud": True,
    "verify_iss": True,
    "require": ["exp", "iat", "sub", "scope"]
}
```

### Rate Limiting Configuration

```yaml
rate_limits:
  legendary_tools:
    requests_per_minute: 10
    burst_limit: 3
    scope_required: "legendary:*"
  
  standard_tools:
    requests_per_minute: 30
    burst_limit: 10
    scope_required: "tools:*"
  
  admin_tools:
    requests_per_minute: 100
    burst_limit: 20
    scope_required: "admin:*"
```

### CORS Configuration

```python
CORS_CONFIG = {
    "allow_origins": ["https://your-domain.com"],
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": [
        "Authorization",
        "Content-Type",
        "X-Correlation-ID",
        "X-Request-ID"
    ],
    "expose_headers": [
        "X-Correlation-ID",
        "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset"
    ],
    "allow_credentials": True,
    "max_age": 3600
}
```

## 🧪 Testing Authentication

### Test Script

```python
#!/usr/bin/env python3
"""
Descope Authentication Test Script
Tests OAuth 2.1 + PKCE flow and JWT validation
"""

import asyncio
import aiohttp
import base64
import hashlib
import secrets
import urllib.parse
from typing import Dict, Any

class DescopeAuthTester:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def generate_pkce_challenge(self) -> Dict[str, str]:
        """Generate PKCE code challenge and verifier"""
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        return {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
    
    async def test_auth_flow(self) -> Dict[str, Any]:
        """Test complete OAuth 2.1 + PKCE flow"""
        print("🔐 Testing Descope Authentication Flow...")
        
        # Generate PKCE parameters
        pkce = self.generate_pkce_challenge()
        
        # Step 1: Authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "scope": self.config["scope"],
            "code_challenge": pkce["code_challenge"],
            "code_challenge_method": pkce["code_challenge_method"],
            "state": secrets.token_urlsafe(32)
        }
        
        auth_url = f"{self.config['auth_endpoint']}?" + urllib.parse.urlencode(auth_params)
        print(f"📋 Authorization URL: {auth_url}")
        
        # In a real test, you would:
        # 1. Navigate to auth_url
        # 2. Complete login
        # 3. Get authorization code from callback
        # 4. Exchange code for tokens
        
        return {
            "auth_url": auth_url,
            "pkce_challenge": pkce["code_challenge"],
            "state": auth_params["state"]
        }
    
    async def test_token_validation(self, token: str) -> Dict[str, Any]:
        """Test JWT token validation"""
        print("🔍 Testing JWT Token Validation...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test token validation endpoint
        async with self.session.get(
            f"{self.config['api_base']}/auth/validate",
            headers=headers
        ) as response:
            return {
                "status": response.status,
                "valid": response.status == 200,
                "data": await response.json() if response.status == 200 else None
            }
    
    async def test_scope_access(self, token: str, tool_endpoint: str, required_scope: str) -> Dict[str, Any]:
        """Test scope-based tool access"""
        print(f"🛠️ Testing scope access for {tool_endpoint}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Required-Scope": required_scope
        }
        
        async with self.session.post(
            f"{self.config['api_base']}/tools/{tool_endpoint}",
            headers=headers,
            json={"test": True}
        ) as response:
            return {
                "endpoint": tool_endpoint,
                "required_scope": required_scope,
                "status": response.status,
                "authorized": response.status != 403,
                "data": await response.json() if response.status == 200 else None
            }

# Test configuration
TEST_CONFIG = {
    "client_id": "your_client_id_here",
    "redirect_uri": "http://localhost:8000/auth/callback",
    "scope": "openid profile email legendary:* tools:*",
    "auth_endpoint": "https://api.descope.com/v1/projects/your_project_id/oauth2/authorize",
    "token_endpoint": "https://api.descope.com/v1/projects/your_project_id/oauth2/token",
    "api_base": "http://localhost:8000"
}

async def run_auth_tests():
    """Run comprehensive authentication tests"""
    async with DescopeAuthTester(TEST_CONFIG) as tester:
        # Test 1: OAuth flow
        auth_result = await tester.test_auth_flow()
        print(f"✅ Auth flow test completed: {auth_result}")
        
        # Test 2: Token validation (requires actual token)
        # token_result = await tester.test_token_validation("your_jwt_token_here")
        # print(f"✅ Token validation test: {token_result}")
        
        # Test 3: Scope access tests
        scope_tests = [
            ("legendary/autonomous_architect", "legendary:autonomous_architect"),
            ("legendary/quality_framework", "legendary:quality_framework"),
            ("tools/generate_code", "tools:generation"),
            ("tools/echo", "tools:basic")
        ]
        
        # for endpoint, scope in scope_tests:
        #     scope_result = await tester.test_scope_access("your_jwt_token_here", endpoint, scope)
        #     print(f"✅ Scope test {endpoint}: {scope_result}")

if __name__ == "__main__":
    print("🧪 Descope Authentication Test Suite")
    print("=" * 50)
    asyncio.run(run_auth_tests())
```

## 🚀 Deployment Steps

### 1. Environment Setup

```bash
# Copy production environment template
cp .env.production.template .env.production

# Update with your Descope configuration
nano .env.production
```

### 2. Descope Configuration Validation

```bash
# Run configuration validation
python scripts/validate_deployment.py --check-auth

# Test Descope connectivity
python scripts/test_descope_auth.py
```

### 3. Middleware Verification

```bash
# Verify middleware integration
python -c "
from src.middleware.auth_integration import AuthenticationMiddleware
print('✅ Authentication middleware imported successfully')
"

# Test scope decorators
python -c "
from src.middleware.auth_integration import require_scope
print('✅ Scope decorators imported successfully')
"
```

### 4. Production Deployment

```bash
# Start MCP server with authentication
python mcp_server.py --enable-auth --production

# Verify authentication endpoints
curl -X GET http://localhost:8000/auth/status
curl -X GET http://localhost:8000/auth/config
```

## 🔍 Troubleshooting

### Common Issues

1. **JWT Validation Failures**
   ```
   Error: Invalid JWT signature
   Solution: Verify DESCOPE_PUBLIC_KEY is correct
   ```

2. **Scope Authorization Failures**
   ```
   Error: Insufficient scope for tool access
   Solution: Check user role assignments in Descope console
   ```

3. **PKCE Validation Failures**
   ```
   Error: Invalid code challenge
   Solution: Ensure PKCE is enabled in Descope application settings
   ```

4. **Rate Limiting Issues**
   ```
   Error: Too many requests
   Solution: Adjust rate limits or implement exponential backoff
   ```

### Debug Commands

```bash
# Check authentication status
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/auth/validate

# Test specific tool access
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/tools/legendary/autonomous_architect \
     -d '{"action": "test"}'

# View authentication logs
tail -f logs/auth.log

# Check middleware performance
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/metrics/auth
```

## 📚 Additional Resources

### Documentation Links
- [Descope Documentation](https://docs.descope.com)
- [OAuth 2.1 Specification](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
- [PKCE Specification](https://datatracker.ietf.org/doc/html/rfc7636)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

### Support Resources
- **Descope Support**: support@descope.com
- **OAuth 2.1 Community**: [oauth.net](https://oauth.net)
- **JWT.io**: [jwt.io](https://jwt.io) for token debugging

### Security Considerations
- **Token Storage**: Use secure, httpOnly cookies for web clients
- **Scope Validation**: Always validate scopes server-side
- **Rate Limiting**: Implement proper rate limiting per user/scope
- **Audit Logging**: Log all authentication and authorization events
- **Token Rotation**: Implement automatic token refresh
- **Security Headers**: Use proper CORS and security headers

---

## 🎯 Configuration Checklist

- [ ] Descope project created and configured
- [ ] OAuth application registered with correct settings
- [ ] Scopes and roles properly configured
- [ ] Environment variables set correctly
- [ ] Middleware integration verified
- [ ] Authentication endpoints tested
- [ ] Scope-based authorization validated
- [ ] Rate limiting configured and tested
- [ ] Security headers implemented
- [ ] Audit logging enabled
- [ ] Production deployment successful
- [ ] All authentication tests passing

**🚀 Your Descope authentication is now fully configured and ready for legendary AI capabilities!**