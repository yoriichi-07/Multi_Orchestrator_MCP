
# 🚀 Descope Access Key Configuration Guide for Legendary AI Capabilities

## Step 1: Create Access Key in Your Descope Console

1. Go to https://app.descope.com/
2. Navigate to your project dashboard
3. Go to "Access Keys" section in the left sidebar
4. Click "Create Access Key"
5. Configure the Access Key with required scopes:

### Permission Scopes to Add:

**legendary:autonomous_architect**
- Description: Access to Autonomous Architect agent for revolutionary system design
- Type: Permission Scope
- Roles: legendary_user, admin_user
- Mandatory: No

**legendary:quality_framework**
- Description: Access to Proactive Quality Framework for intelligent QA
- Type: Permission Scope
- Roles: legendary_user, admin_user
- Mandatory: No

**legendary:prompt_engine**
- Description: Access to Evolutionary Prompt Engine for self-improving prompts
- Type: Permission Scope
- Roles: legendary_user, developer, admin_user
- Mandatory: No

**legendary:cloud_agent**
- Description: Access to Last Mile Cloud Agent for seamless deployment
- Type: Permission Scope
- Roles: legendary_user, admin_user
- Mandatory: No

**legendary:app_generator**
- Description: Access to Legendary Application Generator for full-stack creation
- Type: Permission Scope
- Roles: legendary_user, admin_user
- Mandatory: No

**tools:basic**
- Description: Access to basic connectivity and health check tools
- Type: Permission Scope
- Roles: standard_user, legendary_user, developer, admin_user
- Mandatory: Yes

**tools:generation**
- Description: Access to standard code generation tools
- Type: Permission Scope
- Roles: standard_user, legendary_user, developer, admin_user
- Mandatory: No

**tools:infrastructure**
- Description: Access to infrastructure management tools
- Type: Permission Scope
- Roles: legendary_user, admin_user
- Mandatory: No

**tools:quality**
- Description: Access to standard quality assurance tools
- Type: Permission Scope
- Roles: standard_user, legendary_user, developer, admin_user
- Mandatory: No

**admin:analytics**
- Description: Access to analytics dashboard and performance monitoring
- Type: Permission Scope
- Roles: admin_user
- Mandatory: No

**admin:full**
- Description: Full administrative access to all system features
- Type: Permission Scope
- Roles: admin_user
- Mandatory: No

### User Information Scopes to Add:

**profile**
- Description: Access to user profile information
- Type: User Information Scope  
- User Attribute: email
- Mandatory: Yes

**email**
- Description: Access to user email address
- Type: User Information Scope  
- User Attribute: email
- Mandatory: Yes

## Step 2: Configure Access Key Settings

When creating your Access Key:
- Set expiration to appropriate duration (recommended: 1 year for development)
- Ensure all required scopes are included in the Access Key
- Download or copy the Access Key securely (it won't be shown again)
- Note the Access Key ID for reference

## Step 3: Extract Your Configuration Values

From your Descope console, note these values:
- Project ID: P31WC6A6Vybbt7N5NhnH4dZLQgXY
- Access Key: (the generated Access Key from Step 2)
- Management Key: (from Project Settings → Access Keys)

## Step 4: Update Your Environment Variables

Copy these values to your .env file:
```
DESCOPE_PROJECT_ID=P31WC6A6Vybbt7N5NhnH4dZLQgXY
DESCOPE_ACCESS_KEY=your_access_key_here
DESCOPE_MANAGEMENT_KEY=your_management_key_here
DESCOPE_ISSUER=https://api.descope.com/v1/projects/P31WC6A6Vybbt7N5NhnH4dZLQgXY
DESCOPE_AUDIENCE=mcp-server
```
# Additional Configuration (Keep existing values)
SECURITY_RATE_LIMIT_ENABLED=true
SECURITY_RATE_LIMIT_REQUESTS=100
SECURITY_RATE_LIMIT_WINDOW=60
SECURITY_CORS_ENABLED=true
SECURITY_CORS_ORIGINS=http://localhost:8000,http://localhost:3000
LEGENDARY_FEATURE_FLAG=true
REQUIRE_LEGENDARY_SCOPES=true
LEGENDARY_AUDIT_LOGGING=true
LEGENDARY_SECURITY_MODE=enhanced
DESCOPE_LEGENDARY_SCOPES=legendary:autonomous_architect,legendary:quality_framework,legendary:prompt_engine,legendary:cloud_agent,legendary:app_generator
DESCOPE_STANDARD_SCOPES=tools:basic,tools:generation,tools:infrastructure,tools:quality
DESCOPE_ADMIN_SCOPES=admin:full,admin:analytics

## Step 5: Test Your Access Key Configuration

Run the validation script:
```bash
python scripts/test_descope_config.py
```

## Access Key Benefits

✅ **Simplified Authentication**: No complex OAuth flows required
✅ **Machine-to-Machine**: Perfect for server-to-server communication
✅ **Cequence Compatible**: Works seamlessly with passthrough mode
✅ **JWT Security**: All scopes embedded in secure JWT tokens
✅ **Demo Ready**: Clear, simple authentication for presentations

🎯 Your legendary AI capabilities with Access Key authentication are ready!
