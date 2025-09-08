# 🚀 Smithery Deployment Guide - Multi-Agent Orchestrator MCP

## 📋 **Prerequisites**

Before deploying to Smithery, ensure you have:

- ✅ Smithery account created at [smithery.ai](https://smithery.ai)
- ✅ Repository pushed to GitHub: `yoriichi-07/Multi_Orchestrator_MCP`
- ✅ Descope project configured (Project ID: `P31WC6A6Vybbt7N5NhnH4dZLQgXY`)
- ✅ Cequence AI Gateway credentials obtained
- ✅ Environment variables configured (see [Environment Setup](ENVIRONMENT_SETUP.md))
- ✅ Node.js 18+ installed (for Smithery CLI)

## 🔧 **Step 1: Prepare Environment Variables**

Create your production environment configuration:

```bash
# Competition Requirements
DESCOPE_PROJECT_ID=P31WC6A6Vybbt7N5NhnH4dZLQgXY
DESCOPE_CLIENT_SECRET=your-client-secret-from-descope-dashboard
DESCOPE_MANAGEMENT_KEY=your-management-key-from-descope
CEQUENCE_GATEWAY_ID=your-cequence-gateway-id
CEQUENCE_API_KEY=your-cequence-api-key

# Server Configuration
DEBUG=false
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=production

# AI Providers (Optional but Recommended)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
DEFAULT_LLM_PROVIDER=openai

# Orchestrator Settings
MAX_AGENTS=5
HEALING_ENABLED=true
ANALYTICS_ENABLED=true
ENABLE_METRICS=true
LOG_LEVEL=INFO

# Security
MAX_REQUEST_SIZE_MB=10
RATE_LIMIT_PER_MINUTE=100
MAX_GENERATION_TIME_SECONDS=300

# Analytics
ANALYTICS_BUFFER_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60
```

⚠️ **Important**: Never commit these values to your repository. Use Smithery's environment variable management.

## 🌐 **Step 2: Deploy to Smithery Platform**

### **Option A: Smithery CLI (Recommended for Developers)**

1. **Install Smithery CLI**
```bash
npm install -g @smithery/cli
```

2. **Login to Smithery**
```bash
smithery login
# Follow the authentication flow in your browser
```

3. **Initialize Your Project**
```bash
cd "d:\intel\projects\global mcp hack"
smithery init
# This will create smithery.json configuration
```

4. **Configure for FastMCP**
Update `smithery.json`:
```json
{
  "name": "multi-orchestrator-mcp",
  "version": "1.0.0",
  "framework": "fastmcp",
  "entry": "server.py",
  "python": {
    "version": "3.11",
    "requirements": "requirements.txt"
  },
  "environment": {
    "variables": [
      "DESCOPE_PROJECT_ID",
      "DESCOPE_CLIENT_SECRET",
      "DESCOPE_MANAGEMENT_KEY",
      "CEQUENCE_GATEWAY_ID",
      "CEQUENCE_API_KEY",
      "OPENAI_API_KEY",
      "ANTHROPIC_API_KEY"
    ]
  },
  "health_check": "/health",
  "scaling": {
    "min_instances": 1,
    "max_instances": 5,
    "auto_scale": true
  }
}
```

5. **Deploy to Smithery**
```bash
smithery deploy
# This will build, package, and deploy your MCP server
```

6. **Set Environment Variables**
```bash
# Set each environment variable securely
smithery env set DESCOPE_PROJECT_ID P31WC6A6Vybbt7N5NhnH4dZLQgXY
smithery env set DESCOPE_CLIENT_SECRET your-secret --secret
smithery env set CEQUENCE_GATEWAY_ID your-gateway-id
smithery env set CEQUENCE_API_KEY your-api-key --secret
# Continue for all variables...
```

### **Option B: Smithery Web Dashboard (Recommended for Quick Setup)**

1. **Access Smithery Dashboard**
   - Go to [dashboard.smithery.ai](https://dashboard.smithery.ai)
   - Sign in with your account

2. **Create New Project**
   - Click **"New Project"**
   - Select **"Import from GitHub"**
   - Connect your GitHub account if needed
   - Select repository: `yoriichi-07/Multi_Orchestrator_MCP`
   - Choose branch: `main`

3. **Configure Project Settings**
   - **Framework**: FastMCP
   - **Python Version**: 3.11
   - **Entry Point**: `server.py`
   - **Build Command**: `pip install -r requirements.txt`
   - **Health Check**: `/health`

4. **Set Environment Variables**
   - Navigate to **"Environment Variables"**
   - Add all variables from Step 1
   - **Important**: Mark sensitive variables (API keys, secrets) as "Secret"
   - This ensures they're encrypted and not visible in logs

5. **Deploy**
   - Click **"Deploy"** button
   - Monitor deployment logs in real-time
   - Wait for "Deployment Successful" message

### **Option C: GitHub Integration (Automatic Deployments)**

1. **Connect GitHub Repository**
   - In Smithery dashboard, enable GitHub integration
   - Select your repository and branch
   - Configure deployment triggers (e.g., on push to main)

2. **Automatic Deployment Pipeline**
   - Every push to main branch triggers deployment
   - Automatic testing and validation
   - Zero-downtime rolling updates

## 🔍 **Step 3: Verify Deployment**

### **Health Check**
```bash
curl https://your-deployment-url.smithery.ai/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "components": {
    "mcp_server": {"status": "up"},
    "descope_auth": {"status": "configured"},
    "cequence_analytics": {"status": "configured"},
    "orchestrator": {"status": "active"}
  }
}
```

### **MCP Capabilities**
```bash
curl https://your-deployment-url.smithery.ai/mcp/capabilities
```

### **Test Authentication**
```bash
curl -H "Authorization: Bearer test-token" \
     https://your-deployment-url.smithery.ai/mcp/tools/ping
```

## 🔧 **Step 4: Configure MCP Clients**

### **VS Code Configuration**
Add to your `mcp.json`:
```json
{
  "servers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest",
        "--endpoint",
        "https://your-deployment-url.smithery.ai"
      ]
    }
  }
}
```

### **Claude Desktop Configuration**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest",
        "--endpoint", 
        "https://your-deployment-url.smithery.ai"
      ]
    }
  }
}
```

### **Cursor Configuration**
Add to Cursor settings:
```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest",
        "--endpoint",
        "https://your-deployment-url.smithery.ai"
      ]
    }
  }
}
```

## 📊 **Step 5: Monitor Deployment**

### **Smithery Dashboard**
- Monitor server health and performance
- View deployment logs and errors
- Check resource usage and scaling

### **Cequence Analytics**
- Log into your Cequence dashboard
- Verify request tracking is working
- Monitor security events and analytics

### **Descope Authentication**
- Check your Descope dashboard for authentication events
- Verify OAuth flows are working correctly
- Monitor user activity and token usage

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Deployment Fails**
- Check requirements.txt has all dependencies
- Verify Python version compatibility (3.11+)
- Review deployment logs in Smithery dashboard

#### **Environment Variables Not Loading**
- Ensure all required variables are set
- Check variable names match exactly
- Verify sensitive variables are marked as "Secret"

#### **MCP Client Can't Connect**
- Verify deployment URL is correct
- Check server health endpoint
- Ensure authentication is properly configured

#### **Descope Authentication Errors**
- Verify project ID matches your dashboard
- Check client secret and management key
- Confirm OAuth scopes are properly configured

#### **Cequence Analytics Not Working**
- Verify gateway ID and API key
- Check Cequence dashboard configuration
- Ensure analytics are enabled in environment

### **Debug Commands**

```bash
# Check deployment status
smithery status

# View deployment logs
smithery logs --tail

# Test server health
curl https://your-deployment-url.smithery.ai/health

# Check environment variables
smithery env list

# Restart deployment
smithery restart
```

## 🎯 **Competition Checklist**

Before submitting your competition entry:

- ✅ **Deployment Status**: Server is running and accessible
- ✅ **Health Check**: All endpoints responding correctly
- ✅ **Authentication**: Descope OAuth 2.1 + PKCE working
- ✅ **Analytics**: Cequence AI Gateway tracking requests
- ✅ **MCP Compliance**: All tools, resources, and prompts functional
- ✅ **Documentation**: README and guides are complete
- ✅ **Testing**: All tests passing
- ✅ **Demo Ready**: Can demonstrate all features

## 🚀 **Success Criteria**

Your deployment is ready for competition judging when:

1. **MCP Server Responds**: Health check returns 200 OK
2. **Tools Function**: All 6 tools respond correctly
3. **Authentication Works**: Descope tokens validate properly
4. **Analytics Track**: Cequence dashboard shows request data
5. **Multi-Agent Works**: Can orchestrate development tasks
6. **Self-Healing Works**: Can auto-fix code issues

## 📞 **Support**

If you need help:

1. **Smithery Support**: [support@smithery.ai](mailto:support@smithery.ai)
2. **Repository Issues**: [GitHub Issues](https://github.com/yoriichi-07/Multi_Orchestrator_MCP/issues)
3. **Competition Support**: Follow competition guidelines for support channels

---

**🏆 You're Ready for Competition Success!** 🎉

Your Multi-Agent Orchestrator MCP Server is now deployed and ready to showcase the future of autonomous development!