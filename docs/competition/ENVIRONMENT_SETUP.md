# 🔧 Environment Variables Setup Guide

## 📋 **Competition Requirements**

For MCP competition compliance, you need credentials from both **Cequence AI Gateway** and **Descope Authentication**. This guide helps you obtain and configure them properly.

---

## 🎯 **Current Configuration Status**

Your `.env` file currently contains:

### ✅ **Descope Authentication (Complete)**
```bash
DESCOPE_PROJECT_ID=P31WC6A6Vybbt7N5NhnH4dZLQgXY
DESCOPE_MANAGEMENT_KEY=K32CQXzMl9O0OAq83EOMRzQIWS9PLkmz8oGFh0dkGgOyXz0E9HA1WA7nNvSuJGbNFBo3EBZ
DESCOPE_CLIENT_ID=TPA32BuPmTYXCbmbAj4JpAqOrKh5Ao
DESCOPE_CLIENT_SECRET=bGHOuAXycXfMDlo6HUKnVWb2G925JGYf26EB70KHg75
```

### ⚠️ **Cequence AI Gateway (Missing)**
```bash
# You need to add these:
CEQUENCE_GATEWAY_ID=your_gateway_id_here
CEQUENCE_API_KEY=your_api_key_here
CEQUENCE_GATEWAY_URL=your_gateway_url_here  # Optional
```

---

## 🚀 **Step 1: Complete Cequence AI Gateway Setup**

### **Option A: Get Trial Access**
1. **Visit Cequence Security**: https://www.cequence.ai/
2. **Request Demo/Trial**: Contact their sales team for AI Gateway access
3. **Mention MCP Competition**: This may expedite the process
4. **Get Credentials**: Once approved, you'll receive:
   - Gateway ID
   - API Key
   - Dashboard access

### **Option B: Use Competition Preview (If Available)**
If Cequence provides competition-specific credentials:
1. Check competition announcement for Cequence credentials
2. Use provided test gateway for development
3. Ensure you're authorized to use them

### **Option C: Mock Integration (Development)**
For initial development/testing without real Cequence access:
```bash
# Add these to your .env for development:
CEQUENCE_GATEWAY_ID=demo_gateway_12345
CEQUENCE_API_KEY=demo_api_key_67890
ENABLE_ANALYTICS=false  # Disable actual analytics calls
```

---

## 🔧 **Step 2: Update Your Environment File**

Add the missing Cequence variables to your `.env` file:

```bash
# Cequence AI Gateway (ADD THESE)
CEQUENCE_GATEWAY_ID=your_actual_gateway_id
CEQUENCE_API_KEY=your_actual_api_key
CEQUENCE_GATEWAY_URL=https://your-gateway.cequence.ai  # Optional

# Analytics Configuration
ENABLE_ANALYTICS=true
ANALYTICS_BUFFER_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60

# Security Monitoring
ENABLE_SECURITY_MONITORING=true
MAX_REQUEST_SIZE_MB=10
RATE_LIMIT_PER_MINUTE=100
```

Your complete `.env` should look like:

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false  # Set to false for production

# Descope Authentication ✅ CONFIGURED
DESCOPE_PROJECT_ID=P31WC6A6Vybbt7N5NhnH4dZLQgXY
DESCOPE_MANAGEMENT_KEY=K32CQXzMl9O0OAq83EOMRzQIWS9PLkmz8oGFh0dkGgOyXz0E9HA1WA7nNvSuJGbNFBo3EBZ
DESCOPE_CLIENT_ID=TPA32BuPmTYXCbmbAj4JpAqOrKh5Ao
DESCOPE_CLIENT_SECRET=bGHOuAXycXfMDlo6HUKnVWb2G925JGYf26EB70KHg75
DESCOPE_DEMO_MODE=false  # Set to false for production

# Cequence AI Gateway ⚠️ NEEDS CONFIGURATION
CEQUENCE_GATEWAY_ID=your_gateway_id_here
CEQUENCE_API_KEY=your_api_key_here
CEQUENCE_GATEWAY_URL=your_gateway_url_here

# LLM Configuration (Optional but Recommended)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
DEFAULT_LLM_PROVIDER=openai

# Competition Settings
ENABLE_ANALYTICS=true
ENABLE_SECURITY_MONITORING=true
ENABLE_METRICS=true
LOG_LEVEL=INFO

# File Management
OUTPUT_BASE_PATH=./outputs
MAX_PROJECT_SIZE_MB=100
MAX_GENERATION_TIME_SECONDS=300

# Security
MAX_REQUEST_SIZE_MB=10
RATE_LIMIT_PER_MINUTE=100
ANALYTICS_BUFFER_SIZE=100
ANALYTICS_FLUSH_INTERVAL=60
```

---

## 🧪 **Step 3: Test Your Configuration**

### **Verify Descope Authentication**
```bash
# Test with your configured Descope project
curl -X POST "https://api.descope.com/v1/auth/accesskey/exchange" \
  -H "Authorization: Bearer YOUR_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"loginOptions": {"customClaims": {}}}'
```

### **Verify Environment Loading**
```bash
# Run the server and check logs
python server.py

# Look for these log entries:
# ✅ "mcp_server_initializing" with correct settings
# ✅ "descope_auth" status: "configured"
# ✅ "cequence_analytics" status: "configured"
```

### **Test Health Endpoint**
```bash
curl http://localhost:8000/health

# Expected response:
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

---

## 🔍 **Step 4: Troubleshooting Common Issues**

### **Descope Issues**
- ✅ **Already Configured**: Your Descope setup is complete
- **If authentication fails**: Check that demo mode is disabled in production
- **Token validation errors**: Verify project ID matches exactly

### **Cequence Issues**
- **Missing credentials**: Most common issue - get actual credentials from Cequence
- **API key invalid**: Ensure you're using the correct API key format
- **Gateway ID format**: Usually alphanumeric, check dashboard for exact format

### **Environment Loading Issues**
- **Variables not loaded**: Ensure `.env` file is in project root
- **Docker issues**: Mount `.env` file or use Docker secrets
- **Case sensitivity**: Variable names are case-sensitive

### **Debug Commands**
```bash
# Check environment variables are loaded
python -c "from src.core.config import settings; print(f'Descope: {settings.descope_project_id}, Cequence: {settings.cequence_gateway_id}')"

# Test Descope connection
python -c "
import asyncio
from src.core.descope_auth import get_descope_client
async def test():
    client = await get_descope_client()
    print('Descope client initialized successfully')
asyncio.run(test())
"

# Test Cequence connection
python -c "
import asyncio  
from src.core.cequence_integration import get_cequence_analytics
async def test():
    analytics = await get_cequence_analytics()
    print('Cequence analytics initialized successfully')
asyncio.run(test())
"
```

---

## 🎯 **Competition Readiness Checklist**

- ✅ **Descope OAuth 2.1 + PKCE**: Already configured
- ⚠️ **Cequence AI Gateway**: Needs real credentials
- ✅ **Smithery Compatibility**: Server has @smithery decorators
- ✅ **FastMCP Framework**: Fully implemented
- ✅ **Environment Configuration**: Structure is ready

### **Priority Actions**

1. **🚨 HIGH PRIORITY**: Get Cequence AI Gateway credentials
2. **📝 MEDIUM**: Configure production environment variables
3. **🧪 LOW**: Test end-to-end with real credentials

---

## 🆘 **Getting Help**

### **Cequence Support**
- **Sales/Demo**: https://www.cequence.ai/contact/
- **Support Email**: support@cequence.ai
- **Documentation**: https://docs.cequence.ai/ (if available)

### **Descope Support**
- **Dashboard**: https://app.descope.com/
- **Documentation**: https://docs.descope.com/
- **Support**: support@descope.com

### **Competition Support**
- Follow competition guidelines for technical support
- Check if organizers provide Cequence test credentials

---

## 🎉 **Next Steps**

Once you have Cequence credentials:

1. **Update `.env`** with real Cequence values
2. **Test authentication flows** 
3. **Deploy to Smithery** using deployment guide
4. **Run final validation** with all components
5. **Submit competition entry** with confidence!

Your Multi-Agent Orchestrator MCP Server is 95% ready for competition. Just need those Cequence credentials to complete the integration! 🚀