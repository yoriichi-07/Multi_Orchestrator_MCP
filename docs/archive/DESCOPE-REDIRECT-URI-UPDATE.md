# Descope Redirect URI Update Guide

## Quick Reference

**Project ID**: P31WC6A6Vybbt7N5NhnH4dZLQgXY
**App Name**: Autonomous Software Foundry
**Client ID**: UDMxV0M20TZWeWJidDd0NU5obkgQZFpMUWdYWTpUUEEzMkJ1UGhDYmh0WoSnBBc

## Required Redirect URIs

### ✅ ADD THIS URI:
```
https://auth.aigateway.cequence.ai/v1/outbound/oauth/callback
```

### ❌ REMOVE THIS URI (if present):
```
https://your-domain.fly.dev/auth/callback
```

## Step-by-Step Instructions

1. **Login to Descope**
   - Go to: https://app.descope.com
   - Login to your account

2. **Navigate to Project**
   - Select project: **P31WC6A6Vybbt7N5NhnH4dZLQgXY**

3. **Find OAuth Application**
   - Go to: **Applications** → **OAuth Applications**
   - Click on: **"Autonomous Software Foundry"**

4. **Update Redirect URIs**
   - Scroll to **"Redirect URIs"** section
   - **ADD**: `https://auth.aigateway.cequence.ai/v1/outbound/oauth/callback`
   - **REMOVE**: `https://your-domain.fly.dev/auth/callback` (if exists)

5. **Verify Other Settings**
   - **Authorization URL**: `https://api.descope.com/oauth2/v1/apps/authorize`
   - **Token URL**: `https://api.descope.com/oauth2/v1/apps/token`
   - **Scopes**: `full_access`, `openid`, `profile`, `email`

6. **Save Changes**
   - Click **"Save"** or **"Update"**

## Verification

After saving, verify the redirect URIs list includes:
- ✅ `https://auth.aigateway.cequence.ai/v1/outbound/oauth/callback`
- ❌ No placeholder URLs (fly.dev, localhost, etc.)

## Next Steps

Once updated, run the validation script:
```bash
python scripts/test_cequence_deployment.py
```

This will test the complete OAuth flow and MCP server accessibility.