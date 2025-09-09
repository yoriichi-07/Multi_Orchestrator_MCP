# Authentication Scripts

This directory contains scripts for handling authentication between Cursor IDE and the Multi-Agent Orchestrator MCP server using Descope.

## 📁 Scripts Overview

### `get_jwt_token.py`
**Purpose:** Exchange Descope Access Key for JWT token  
**Usage:** Manual token generation for direct authentication  
**When to use:** Testing, demos, or one-time setups

```bash
python get_jwt_token.py YOUR_ACCESS_KEY
```

**Features:**
- ✅ Secure access key to JWT token exchange
- ✅ User-friendly formatted output
- ✅ Error handling and validation
- ✅ Copy-paste ready JWT tokens
- ✅ Example configuration snippets

### `mcp_client_with_auth.py`
**Purpose:** Authentication proxy with automatic token refresh  
**Usage:** Production-ready authentication solution  
**When to use:** Development, regular usage, production deployments

```bash
# Set environment variable first
export DESCOPE_ACCESS_KEY=your_access_key_here
python mcp_client_with_auth.py https://your-mcp-server-url
```

**Features:**
- ✅ Automatic JWT token refresh
- ✅ Health check endpoints
- ✅ Request forwarding with authentication
- ✅ Error handling and recovery
- ✅ Local proxy server (port 8090)

### `validate_auth.py`
**Purpose:** Comprehensive authentication validation and testing  
**Usage:** Troubleshooting and health checks  
**When to use:** Debugging authentication issues, validating setup

```bash
python validate_auth.py YOUR_ACCESS_KEY
```

**Features:**
- ✅ Complete authentication flow testing
- ✅ Descope client validation
- ✅ JWT token format verification
- ✅ Detailed error reporting
- ✅ Health check summaries

## 🚀 Quick Start Guide

### 1. Test Your Setup
First, validate that your authentication setup works:

```bash
python validate_auth.py K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ
```

### 2. Choose Your Authentication Method

#### Option A: Manual JWT Token (Simple)
Best for: Testing, demos, short-term usage

```bash
# Get JWT token
python get_jwt_token.py K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ

# Copy the JWT token and use it directly in your Cursor IDE configuration
```

#### Option B: Authentication Proxy (Recommended)
Best for: Development, production, regular usage

```bash
# Set environment variable
export DESCOPE_ACCESS_KEY=K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ

# Start the authentication proxy
python mcp_client_with_auth.py https://your-smithery-deployment.smithery.ai

# Configure Cursor IDE to use localhost:8090 as the MCP server URL
```

## 📖 Detailed Usage

### get_jwt_token.py

**Command Format:**
```bash
python get_jwt_token.py <access_key>
```

**Example Output:**
```
🔐 JWT Token Generation
====================

✅ Successfully obtained JWT token!

🎯 Your JWT Token:
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.EkN-DOsnsuRjRO6BxXemmJDm3HbxrbRzXglbN2S4sOkopdU4IsDxTI8jO19W_A4K8ZPJijNLis4EZsHeY559a4DFOd50_OqgHs_Qxg...

📋 Cursor IDE Configuration Example:
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "YOUR_MCP_SERVER_URL"],
      "env": {
        "AUTHORIZATION": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
  }
}

⚠️  Note: This token will expire in about 1 hour. Run this script again to get a fresh token.
```

**Error Handling:**
- Invalid access key validation
- Network connectivity issues
- Descope service errors
- Missing dependencies

### mcp_client_with_auth.py

**Command Format:**
```bash
python mcp_client_with_auth.py <mcp_server_url> [--port PORT]
```

**Environment Variables:**
- `DESCOPE_ACCESS_KEY` - Your Descope access key (required)
- `DESCOPE_PROJECT_ID` - Descope project ID (defaults to P32RbAyKnfcvEJYS69SfSEk6GPKk)

**Example Usage:**
```bash
# Windows
set DESCOPE_ACCESS_KEY=K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ
python mcp_client_with_auth.py https://smithery-deployment.smithery.ai

# Linux/Mac
export DESCOPE_ACCESS_KEY=K32SfHHiOdaoMEde4r7cvBd7gYfdY3UPQccGHkh5gMyMwcrjfHMETV8RqzeXdrRg0dDrbMZ
python mcp_client_with_auth.py https://smithery-deployment.smithery.ai --port 8090
```

**Features:**
- Automatic JWT token refresh before expiration
- Health check endpoint at `/health`
- Request forwarding with proper authentication headers
- Error handling and recovery
- Graceful shutdown handling

**Health Check:**
```bash
curl http://localhost:8090/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "token_valid": true,
  "target_server": "https://smithery-deployment.smithery.ai",
  "proxy_version": "1.0.0"
}
```

### validate_auth.py

**Command Format:**
```bash
python validate_auth.py <access_key>
```

**Example Output:**
```
🔍 Authentication Validation Report
=================================

📋 Test Results:
✅ Descope Client Initialization: PASSED
✅ Access Key to JWT Exchange: PASSED  
✅ JWT Token Format Validation: PASSED
✅ Token Claims Validation: PASSED

📊 Summary:
- Total Tests: 4
- Passed: 4
- Failed: 0
- Success Rate: 100%

🎉 All authentication tests passed! Your setup is working correctly.

🔐 Generated JWT Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
⏰ Token Expires: 2024-01-15 15:30:45 UTC (in 59 minutes)

💡 Next Steps:
1. Use this JWT token directly in Cursor IDE, or
2. Set up the authentication proxy for automatic token management
```

**Test Coverage:**
- Descope client initialization
- Access key validation
- JWT token exchange
- Token format verification
- Token claims validation
- Expiration time checks

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" errors
**Solution:** Install required dependencies
```bash
pip install -r requirements.txt
```

#### "Invalid access key" errors
**Solution:** 
- Verify the access key is correct
- Check access key permissions in Descope console
- Ensure access key hasn't expired

#### "Connection refused" errors
**Solution:**
- Check your internet connection
- Verify Descope service status
- Try with a different network

#### "Port already in use" errors (mcp_client_with_auth.py)
**Solution:**
- Use a different port: `--port 8091`
- Kill the existing process using port 8090
- Wait a few seconds and try again

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export DEBUG=1
python script_name.py
```

### Getting Help

1. **Run validation script first:**
   ```bash
   python validate_auth.py YOUR_ACCESS_KEY
   ```

2. **Check error logs** in the script output

3. **Verify environment variables** are set correctly

4. **Test network connectivity** to Descope services

## 🔐 Security Best Practices

### Access Key Management
- **Never commit access keys** to version control
- **Use environment variables** for credentials
- **Rotate access keys** regularly
- **Use scoped permissions** in Descope

### Token Security
- **JWT tokens expire** automatically (usually 1 hour)
- **Don't store JWT tokens** in persistent storage
- **Use HTTPS** for all communications
- **Monitor token usage** in Descope console

### Network Security
- **Authentication proxy** runs on localhost only
- **Use firewall rules** to restrict access
- **Monitor proxy logs** for unusual activity
- **Use secure URLs** (HTTPS) for target servers

## 📊 Performance Considerations

### Token Refresh Strategy
The authentication proxy refreshes tokens:
- **5 minutes before expiration** (configurable)
- **On authentication failures** (automatic retry)
- **On startup** (ensures fresh token)

### Resource Usage
- **Memory:** ~50MB per proxy instance
- **CPU:** Minimal (token refresh is infrequent)
- **Network:** Light (only auth requests to Descope)

### Scaling
- **Multiple proxies:** Use different ports
- **Load balancing:** Not required for typical usage
- **High availability:** Run proxy as a service

## 🚀 Production Deployment

### Recommended Setup
1. **Use authentication proxy** for automatic token management
2. **Run as a system service** (systemd, Windows Service, etc.)
3. **Configure logging** to files
4. **Set up monitoring** for proxy health
5. **Use environment files** for configuration

### Service Configuration Example (systemd)
```ini
[Unit]
Description=MCP Authentication Proxy
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/mcp-auth
ExecStart=/usr/bin/python3 mcp_client_with_auth.py https://your-server.com
EnvironmentFile=/opt/mcp-auth/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ ./scripts/
COPY src/ ./src/

ENV DESCOPE_ACCESS_KEY=""
EXPOSE 8090

CMD ["python", "scripts/mcp_client_with_auth.py", "--port", "8090"]
```

## 📈 Monitoring and Logging

### Health Checks
- **Proxy health:** `GET /health`
- **Token validity:** Checked automatically
- **Target server:** Forwarded health checks

### Logging Levels
- **INFO:** Normal operations
- **WARN:** Token refresh events
- **ERROR:** Authentication failures
- **DEBUG:** Detailed request/response logging

### Metrics to Monitor
- Token refresh frequency
- Authentication success rate
- Request forwarding latency
- Error rates and types

## 📝 Development

### Adding New Features
1. **Fork the repository**
2. **Create feature branch**
3. **Add tests** for new functionality
4. **Update documentation**
5. **Submit pull request**

### Testing
```bash
# Run all authentication tests
python validate_auth.py YOUR_ACCESS_KEY

# Test individual components
python -m pytest tests/

# Load testing (if implemented)
python scripts/load_test_auth.py
```

### Contributing
- Follow existing code style
- Add type hints for new functions
- Include error handling
- Update documentation
- Add test coverage

---

For more detailed setup instructions, see `docs/cursor-mcp-setup.md`.