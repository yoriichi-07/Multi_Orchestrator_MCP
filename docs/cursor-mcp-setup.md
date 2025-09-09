# Cursor IDE MCP Setup Guide

## Overview

This guide provides step-by-step instructions for fixing the authorization issue between Cursor IDE and your Multi-Agent Orchestrator MCP server. The problem occurs when trying to use a Descope Access Key directly as a Bearer token, when Cursor IDE requires a proper JWT token format.

## 🔍 Problem Diagnosis

### The Issue
Cursor IDE expects JWT tokens in Bearer authentication, but you're providing a Descope Access Key directly. The Access Key needs to be exchanged for a proper JWT token first.

### Error Symptoms
- Authorization errors in Cursor IDE when trying to connect to MCP server
- "Invalid token" or "Authentication failed" messages
- MCP server shows authentication rejection in logs

## 🛠️ Solution Overview

There are two approaches to fix this issue:

1. **Manual JWT Token** - Get a JWT token once and use it directly
2. **Automatic Authentication Proxy** - Use a proxy that handles token refresh automatically

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] Descope Project ID: `P32RbAyKnfcvEJYS69SfSEk6GPKk`
- [ ] Valid Descope Access Key (the one you currently have)
- [ ] Python 3.8+ installed
- [ ] Access to your MCP server deployment
- [ ] Cursor IDE installed and configured

## 🚀 Quick Start (Recommended)

### Option 1: Manual JWT Token (Simple)

1. **Get your JWT token (using demo mode for testing):**
   ```bash
   cd "d:\intel\projects\global mcp hack"
   set DESCOPE_DEMO_MODE=true
   python scripts/get_jwt_token.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
   ```

   **For production with a real access key:**
   ```bash
   python scripts/get_jwt_token.py YOUR_REAL_ACCESS_KEY
   ```

2. **Copy the JWT token** from the output

3. **Update your Cursor IDE mcp.json:**
   ```json
   {
     "mcpServers": {
       "multi-orchestrator": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch", "YOUR_MCP_SERVER_URL"],
         "env": {
           "AUTHORIZATION": "Bearer YOUR_JWT_TOKEN_HERE"
         }
       }
     }
   }
   ```

4. **Restart Cursor IDE**

### Option 2: Automatic Authentication Proxy (Advanced)

1. **Start the authentication proxy (demo mode for testing):**
   ```bash
   cd "d:\intel\projects\global mcp hack"
   set DESCOPE_DEMO_MODE=true
   set DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
   python scripts/mcp_client_with_auth.py YOUR_MCP_SERVER_URL
   ```

   **For production with a real access key:**
   ```bash
   set DESCOPE_ACCESS_KEY=YOUR_REAL_ACCESS_KEY
   python scripts/mcp_client_with_auth.py YOUR_MCP_SERVER_URL
   ```

2. **Update your Cursor IDE mcp.json:**
   ```json
   {
     "mcpServers": {
       "multi-orchestrator": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch", "http://localhost:8090"],
         "env": {}
       }
     }
   }
   ```

3. **Restart Cursor IDE**

## 📖 Detailed Instructions

### Step 1: Validate Your Setup

Before making changes, validate that your authentication setup is working. **For testing purposes, use demo mode:**

```bash
cd "d:\intel\projects\global mcp hack"
# Test with demo mode (recommended for validation)
set DESCOPE_DEMO_MODE=true
python scripts/validate_auth.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
```

**Note:** If you get a 401 Unauthorized error without demo mode, this is expected since the demo access key may not be valid with the live Descope service. Demo mode allows you to test the complete authentication flow locally.

This will test:
- ✅ Descope client initialization
- ✅ Access key to JWT token exchange
- ✅ JWT token format validation
- ✅ Basic connectivity tests

### Step 2: Choose Your Authentication Method

#### Method A: Manual JWT Token

**Pros:**
- Simple setup
- No additional processes
- Direct connection

**Cons:**
- Tokens expire (usually 1 hour)
- Manual refresh required
- Need to update config when token expires

**When to use:** For testing, demos, or short-term usage

#### Method B: Authentication Proxy

**Pros:**
- Automatic token refresh
- No manual intervention
- Seamless experience

**Cons:**
- Additional process to manage
- Slightly more complex setup
- Local proxy dependency

**When to use:** For development, regular usage, or production scenarios

### Step 3: Implementation

#### For Manual JWT Token:

1. **Generate JWT Token (test with demo mode first):**
   ```bash
   # For testing/demo
   set DESCOPE_DEMO_MODE=true
   python scripts/get_jwt_token.py [YOUR_ACCESS_KEY]
   
   # For production
   python scripts/get_jwt_token.py [YOUR_REAL_ACCESS_KEY]
   ```

2. **Copy the output token** (starts with `eyJ...`)

3. **Create/update mcp.json** in your Cursor IDE configuration directory:
   ```json
   {
     "mcpServers": {
       "multi-orchestrator": {
         "command": "npx",
         "args": [
           "-y", 
           "@modelcontextprotocol/server-fetch", 
           "https://your-smithery-deployment.smithery.ai"
         ],
         "env": {
           "AUTHORIZATION": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
         }
       }
     }
   }
   ```

#### For Authentication Proxy:

1. **Set environment variables:**
   ```bash
   # Windows (for testing with demo mode)
   set DESCOPE_DEMO_MODE=true
   set DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
   
   # Windows (for production)
   set DESCOPE_ACCESS_KEY=YOUR_REAL_ACCESS_KEY
   
   # Linux/Mac (for testing with demo mode)
   export DESCOPE_DEMO_MODE=true
   export DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
   
   # Linux/Mac (for production)
   export DESCOPE_ACCESS_KEY=YOUR_REAL_ACCESS_KEY
   ```

2. **Start the proxy:**
   ```bash
   python scripts/mcp_client_with_auth.py https://your-smithery-deployment.smithery.ai
   ```

3. **Update mcp.json:**
   ```json
   {
     "mcpServers": {
       "multi-orchestrator": {
         "command": "npx",
         "args": [
           "-y", 
           "@modelcontextprotocol/server-fetch", 
           "http://localhost:8090"
         ],
         "env": {}
       }
     }
   }
   ```

### Step 4: Test the Connection

1. **Restart Cursor IDE** to apply the new configuration

2. **Test MCP connection** by trying to use MCP features in Cursor IDE

3. **Check for errors** in Cursor IDE's output/console

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "Token expired" or "Invalid token"
**Solution:** 
- For manual method: Run `get_jwt_token.py` again to get a fresh token
- For proxy method: Restart the authentication proxy

#### Issue: "Connection refused" or "Cannot connect"
**Solution:**
- Verify the MCP server URL is correct and accessible
- For proxy method: Ensure the proxy is running on port 8090
- Check firewall settings

#### Issue: "Access key invalid"
**Solution:**
- Verify your Descope Access Key is correct
- Check that the access key has not expired
- Ensure the access key has the required scopes

#### Issue: Authentication proxy stops working
**Solution:**
- Check the terminal running the proxy for error messages
- Restart the proxy with the correct environment variables
- Verify network connectivity to Descope

### Debug Commands

1. **Test access key exchange (demo mode recommended for testing):**
   ```bash
   set DESCOPE_DEMO_MODE=true
   python scripts/get_jwt_token.py YOUR_ACCESS_KEY
   ```

2. **Validate complete auth flow (demo mode recommended for testing):**
   ```bash
   set DESCOPE_DEMO_MODE=true
   python scripts/validate_auth.py YOUR_ACCESS_KEY
   ```

3. **Test proxy health:**
   ```bash
   curl http://localhost:8090/health
   ```

4. **Test MCP server directly:**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" YOUR_MCP_SERVER_URL/health
   ```

### Important Notes for Demo Access Key

⚠️ **If you're getting 401 Unauthorized errors:** This is expected when using the demo access key `K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo` with the live Descope service, as this key is for demonstration purposes only.

✅ **Solution:** Always use `DESCOPE_DEMO_MODE=true` when testing with the demo access key. This enables a local mock authentication system that demonstrates the complete workflow without requiring a valid Descope service connection.

## 📁 Configuration Files

### Cursor IDE mcp.json Location

The mcp.json file should be placed in your Cursor IDE configuration directory:

- **Windows:** `%APPDATA%\Cursor\User\mcp.json`
- **macOS:** `~/Library/Application Support/Cursor/User/mcp.json`
- **Linux:** `~/.config/cursor/User/mcp.json`

### Template Files

Use these template files as starting points:

- `config/mcp.json.template` - Complete MCP configuration examples
- `config/env.template` - Environment variable configuration

## 🔐 Security Considerations

### Token Management
- JWT tokens are temporary (usually expire in 1 hour)
- Never commit Access Keys or JWT tokens to version control
- Use environment variables for sensitive credentials
- Rotate Access Keys regularly

### Network Security
- Authentication proxy runs on localhost only
- Use HTTPS for production MCP server URLs
- Consider firewall rules for proxy port (8090)

### Descope Security
- Enable MFA on your Descope account
- Monitor access logs for unusual activity
- Use scoped Access Keys with minimal required permissions

## 📈 Production Recommendations

### For Production Use:
1. **Use the Authentication Proxy** for automatic token management
2. **Set up monitoring** for the proxy process
3. **Use environment variables** for all credentials
4. **Implement proper logging** and error handling
5. **Consider containerization** of the proxy

### For Development:
1. **Manual JWT tokens** are sufficient for testing
2. **Use validation script** regularly to check auth health
3. **Keep backups** of working configurations

## 🆘 Getting Help

If you're still experiencing issues:

1. **Run the validation script** with verbose output
2. **Check the authentication proxy logs** if using that method
3. **Verify your Descope configuration** in the Descope console
4. **Test with a fresh Access Key** if authentication fails

### Support Resources:
- Descope Documentation: https://docs.descope.com/
- MCP Documentation: https://modelcontextprotocol.io/
- Project Repository: https://github.com/yoriichi-07/Multi_Orchestrator_MCP

## ✅ Success Checklist

After following this guide, you should have:

- [ ] Working JWT token generation
- [ ] Properly configured Cursor IDE mcp.json
- [ ] Successful MCP server connection
- [ ] No authentication errors in Cursor IDE
- [ ] Access to all MCP tools and features

Your Cursor IDE should now successfully authenticate with your Multi-Agent Orchestrator MCP server! 🎉