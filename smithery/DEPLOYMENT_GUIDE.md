# 🚀 Smithery Deployment Guide

## Multi-Agent Orchestrator MCP Server - Competition Ready

This guide walks you through deploying the competition-ready MCP server on the Smithery platform using the mandatory technology stack.

## 📋 Prerequisites

### Required Competition Integrations

1. **Descope Account**: [Sign up at descope.com](https://www.descope.com/)
   - Create a new project
   - Configure OAuth 2.1 + PKCE flow
   - Note your Project ID and credentials

2. **Cequence AI Gateway**: [Get access to Cequence](https://cequence.ai/)
   - Set up AI Gateway instance
   - Obtain Gateway ID and API key
   - Configure request monitoring

3. **Smithery Account**: [Create account at smithery.ai](https://smithery.ai/)
   - Connect your GitHub account
   - Prepare for repository deployment

4. **GitHub Repository**: Public or private repository for deployment

## 🔧 Step 1: Repository Setup

### Clone and Prepare Repository

```bash
# Create new GitHub repository
gh repo create your-username/multi-orchestrator-mcp --public

# Clone this Smithery-ready code
cd path/to/smithery/
git init
git add .
git commit -m "Initial commit: Competition-ready MCP server"
git remote add origin https://github.com/your-username/multi-orchestrator-mcp.git
git push -u origin main
```

### Verify Repository Structure

Your repository should contain:

```
├── src/
│   └── multi_orchestrator_mcp/
│       ├── __init__.py
│       └── server.py              # Main FastMCP server
├── tests/
│   ├── test_mcp_server.py         # Basic functionality tests
│   └── mcp_protocol_validation.py # MCP compliance validation
├── pyproject.toml                 # Smithery build configuration
├── requirements.txt               # Python dependencies
├── README.md                      # Comprehensive documentation
├── LICENSE                        # MIT license
├── .env.template                  # Environment variable template
├── .gitignore                     # Git ignore patterns
└── DEPLOYMENT_GUIDE.md           # This file
```

## 🔐 Step 2: Configure Credentials

### Create Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.template .env.local
   ```

2. Fill in your credentials:
   ```bash
   # Descope Authentication
   DESCOPE_PROJECT_ID=P2xxx...your-project-id
   DESCOPE_CLIENT_SECRET=CS_xxx...your-client-secret  
   DESCOPE_MANAGEMENT_KEY=K_xxx...your-management-key
   
   # Cequence AI Gateway
   CEQUENCE_GATEWAY_ID=gateway-xxx
   CEQUENCE_API_KEY=ck_xxx...your-api-key
   
   # Optional AI Providers
   OPENAI_API_KEY=sk-xxx...your-openai-key
   ANTHROPIC_API_KEY=sk-ant-xxx...your-anthropic-key
   ```

3. **Important**: Never commit `.env.local` to Git. Use Smithery's configuration management instead.

## 🚀 Step 3: Deploy to Smithery

### Option A: Web Interface (Recommended)

1. **Visit Smithery**: Go to [smithery.ai/new](https://smithery.ai/new)

2. **Connect Repository**: 
   - Click "Deploy from GitHub"
   - Select your repository: `your-username/multi-orchestrator-mcp`
   - Choose the `main` branch

3. **Configure Environment Variables**:
   - Add your Descope credentials
   - Add your Cequence Gateway configuration
   - Add optional AI provider keys

4. **Deploy**: Click "Deploy" for one-click deployment

5. **Verify**: Your MCP server will be available at:
   ```
   https://your-server-id.smithery.app
   ```

### Option B: Smithery CLI

1. **Install Smithery CLI**:
   ```bash
   npm install -g @smithery/cli
   ```

2. **Login and Deploy**:
   ```bash
   smithery login
   smithery deploy --repo your-username/multi-orchestrator-mcp
   ```

3. **Configure Environment**:
   ```bash
   smithery env set DESCOPE_PROJECT_ID "P2xxx..."
   smithery env set CEQUENCE_GATEWAY_ID "gateway-xxx"
   smithery env set CEQUENCE_API_KEY "ck_xxx..."
   # Add other variables as needed
   ```

## ✅ Step 4: Verify Deployment

### Test MCP Server Health

```bash
# Check server status
curl https://your-server-id.smithery.app/health

# Expected response:
{
  "status": "healthy",
  "service": "multi-agent-orchestrator",
  "version": "2.0.0",
  "authentication": "Descope OAuth 2.1 + PKCE",
  "analytics": "Cequence AI Gateway",
  "mcp_protocol": "2024-11-05"
}
```

### Test MCP Protocol Endpoints

```bash
# Initialize MCP connection
curl -X POST https://your-server-id.smithery.app/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'

# List available tools
curl -X POST https://your-server-id.smithery.app/mcp/tools/list \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

## 🔗 Step 5: Connect to MCP Clients

### Claude Desktop

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "multi-orchestrator-mcp",
        "--key",
        "<your-smithery-key>",
        "--profile", 
        "<your-smithery-profile>"
      ]
    }
  }
}
```

### Cursor IDE

Add to your MCP settings:

```json
{
  "mcp.servers": {
    "multi-orchestrator": {
      "url": "https://your-server-id.smithery.app",
      "type": "http"
    }
  }
}
```

### Custom Integration

Use the Smithery NPX command or direct HTTP calls:

```bash
# Using Smithery CLI
npx @smithery/cli run multi-orchestrator-mcp \
  --key your-smithery-key \
  --profile your-profile

# Direct HTTP (requires authentication)
curl -X POST https://your-server-id.smithery.app/mcp/tools/call \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "orchestrate_development",
      "arguments": {
        "project_description": "Build a task management app",
        "requirements": ["user auth", "real-time updates", "mobile responsive"]
      }
    }
  }'
```

## 📊 Step 6: Monitor and Analytics

### Cequence Dashboard

Access your analytics at:
- Cequence Console: Monitor request patterns and security
- Performance metrics: Response times and error rates
- Usage analytics: Most popular tools and user behavior

### Smithery Monitoring

- **Server Logs**: View in Smithery dashboard
- **Performance**: Monitor response times and uptime
- **Scaling**: Automatic scaling based on load

## 🛠️ Step 7: Testing and Validation

### Run MCP Protocol Validation

```bash
# Local testing before deployment
python tests/mcp_protocol_validation.py

# Expected output:
# 🎉 EXCELLENT - Server is fully compliant with MCP specification
# 🏆 COMPETITION READY - Server meets all mandatory technology stack requirements
```

### Test Competition Features

```bash
# Test multi-agent orchestration
python -c "
import requests
response = requests.post('https://your-server-id.smithery.app/mcp/tools/call', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {
        'name': 'orchestrate_development',
        'arguments': {
            'project_description': 'E-commerce platform',
            'requirements': ['product catalog', 'shopping cart', 'payment processing']
        }
    }
})
print(response.json())
"
```

## 🏆 Competition Submission

### Verification Checklist

- ✅ **Descope Authentication**: OAuth 2.1 + PKCE implemented
- ✅ **Cequence AI Gateway**: Analytics and monitoring active
- ✅ **Smithery Platform**: Successfully deployed and accessible
- ✅ **MCP Protocol**: 100% compliance verified
- ✅ **Multi-Agent Orchestration**: Advanced AI coordination features
- ✅ **Self-Healing**: Automatic code fixing capabilities
- ✅ **Documentation**: Comprehensive guides and examples

### Competition URLs

Provide these URLs for judging:

1. **Smithery Server**: `https://your-server-id.smithery.app`
2. **GitHub Repository**: `https://github.com/your-username/multi-orchestrator-mcp`
3. **Health Check**: `https://your-server-id.smithery.app/health`
4. **Analytics Dashboard**: `https://your-server-id.smithery.app/dashboard`

### Competition Statement

> "This MCP server demonstrates advanced autonomous software development capabilities using the mandatory competition technology stack (Descope + Cequence + Smithery). It features multi-agent orchestration, self-healing code generation, and full enterprise integration while maintaining 100% MCP protocol compliance."

## 🔧 Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**:
   ```bash
   # Check Smithery environment configuration
   smithery env list
   
   # Update if needed
   smithery env set DESCOPE_PROJECT_ID "your-value"
   ```

2. **MCP Client Connection Issues**:
   ```bash
   # Test direct HTTP connection
   curl https://your-server-id.smithery.app/health
   
   # Verify authentication
   curl https://your-server-id.smithery.app/mcp/capabilities
   ```

3. **Analytics Not Working**:
   - Verify Cequence Gateway ID and API key
   - Check Cequence console for connection status
   - Review server logs in Smithery dashboard

### Support Resources

- **Smithery Documentation**: [smithery.ai/docs](https://smithery.ai/docs)
- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Descope Guides**: [docs.descope.com](https://docs.descope.com)
- **Cequence Documentation**: [docs.cequence.ai](https://docs.cequence.ai)

## 🎯 Next Steps

1. **Test Thoroughly**: Use all tools and resources to verify functionality
2. **Monitor Performance**: Keep an eye on analytics and server health
3. **Optimize**: Based on usage patterns from Cequence analytics
4. **Scale**: Smithery automatically handles scaling as usage grows
5. **Iterate**: Use feedback to improve agent coordination and capabilities

---

**🏆 Competition Ready!** Your Multi-Agent Orchestrator MCP Server is now deployed on the mandatory technology stack and ready for judging.