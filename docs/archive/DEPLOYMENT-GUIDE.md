# Deployment Guide - REDIRECTED# Serverless Deployment Guide for Autonomous Software Foundry



## ⚠️ **IMPORTANT: Updated Deployment Information**This guide provides comprehensive instructions for deploying the Autonomous Software Foundry MCP server to Vercel with external services, optimized for Windows development environments.



This deployment guide has been **superseded** by the new serverless Vercel deployment approach.## 🎯 Why Vercel + External Services?



## 🔄 **Migration Complete**After migration analysis, **Vercel with external services is the optimal choice** for this MCP server deployment:



The Autonomous Software Foundry MCP Server has been successfully migrated from Fly.io to Vercel serverless deployment to resolve Windows Docker virtualization issues.### ✅ Vercel Advantages

- **Perfect for FastAPI**: Native Python support with serverless functions

## 📖 **Current Deployment Guide**- **No Docker Required**: Eliminates Windows virtualization issues

- **Auto-scaling**: Scales to zero when not in use, scales up automatically

Please refer to the **main deployment guide** in the project root:- **Global Edge Deployment**: Multi-region support with low latency

- **Modern CI/CD**: Seamless GitHub integration

👉 **[VERCEL-DEPLOYMENT-GUIDE.md](../VERCEL-DEPLOYMENT-GUIDE.md)**- **Cost-effective**: Pay only for usage, generous free tier



This comprehensive guide includes:### ✅ External Service Benefits

- ✅ Complete Vercel setup instructions- **Specialized Providers**: Database and Redis experts (Supabase, Upstash)

- ✅ External service configuration (Supabase, Upstash)- **Better Performance**: Optimized for their specific services

- ✅ Environment variable setup- **Enhanced Reliability**: 99.9%+ uptime guarantees

- ✅ Step-by-step deployment process- **Easier Management**: Dedicated dashboards and monitoring

- ✅ Monitoring and troubleshooting

## 🛠️ Prerequisites

## 🎯 **Key Changes**

### System Requirements

### **Before: Fly.io + Docker**- **Windows 10/11** with PowerShell 5.1+ or PowerShell Core 7+

- Required Docker virtualization on Windows- **Python 3.11+** installed and in PATH

- Single platform deployment- **Poetry** for dependency management

- Built-in database/Redis services- **Git** for version control

- **Node.js 18+** for Vercel CLI

### **After: Vercel + External Services**- **Vercel CLI** for deployment

- ✅ No Docker required - eliminates Windows issues

- ✅ Serverless auto-scaling### Accounts Needed

- ✅ Specialized external services (Supabase, Upstash)- [Fly.io Account](https://fly.io/app/sign-up) (free tier available)

- ✅ Better performance and reliability- [GitHub Account](https://github.com) for CI/CD

- [Descope Account](https://www.descope.com) for authentication

## 🚀 **Quick Start**- [Cequence Account](https://www.cequence.ai) for analytics (optional)

- [OpenAI API Key](https://platform.openai.com) for LLM services

1. **Follow the main guide**: [VERCEL-DEPLOYMENT-GUIDE.md](../VERCEL-DEPLOYMENT-GUIDE.md)

2. **Validate deployment**: Run `scripts/validate-vercel-deployment.ps1`## 🚀 Quick Start Deployment

3. **Deploy**: `vercel --prod`

### Step 1: Initial Setup

---```powershell

# Clone and setup project

**This file is maintained for historical reference only. All current deployment instructions are in the main project root.**git clone <your-repository-url>
cd autonomous-software-foundry

# Install dependencies
poetry install

# Install Vercel CLI
npm install -g vercel
```

### Step 2: External Services Setup
```bash
# Database Setup (choose one):
# Supabase: https://supabase.com/
# PlanetScale: https://planetscale.com/
# Neon: https://neon.tech/

# Redis Setup (choose one):
# Upstash: https://upstash.com/
# Redis Cloud: https://redis.com/try-free/
```

### Step 3: Configuration
```powershell
# Copy environment template (keep as template, don't create .env.production)
# Configure environment variables in Vercel dashboard instead

# Review environment template for required variables
notepad .env.production.template
```

### Step 4: Deploy
```powershell
# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Or deploy to preview first
vercel
```

### Step 5: Monitor
```powershell
# Check deployment status in Vercel dashboard
# https://vercel.com/dashboard

# View function logs
vercel logs

# Check application health
# Visit your deployed URL /health endpoint
```

## 📁 Deployment Files Overview

### Core Configuration Files

#### `fly.toml` - Main Fly.io configuration
```toml
app = "autonomous-software-foundry"
primary_region = "ord"

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[build.env]
  BP_CPYTHON_VERSION = "~3.11.0"

[env]
  APP_ENV = "production"
  PORT = "8080"
  PYTHONUNBUFFERED = "1"
```

#### `Procfile` - Process definitions
```
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
```

#### `runtime.txt` - Python version specification
```
python-3.11.10
```

### Database & Cache Configuration

#### Fly.io PostgreSQL Setup
```powershell
# Create PostgreSQL database
flyctl postgres create --name asf-db --region ord --vm-size shared-cpu-1x

# Attach to your application
flyctl postgres attach asf-db --app autonomous-software-foundry
```

#### Fly.io Redis Setup
```powershell
# Create Redis cache
flyctl redis create --name asf-redis --region ord

# Connection details are available via:
flyctl redis status asf-redis
```

## 🔧 Advanced Configuration

### Multi-Region Deployment
```powershell
# Deploy to multiple regions for global availability
flyctl scale count --region ams 1  # Amsterdam
flyctl scale count --region sin 1  # Singapore  
flyctl scale count --region lax 1  # Los Angeles
```

### Scaling Configuration
```powershell
# Scale memory (for higher loads)
flyctl scale memory 1gb --app autonomous-software-foundry

# Scale VM count (for high availability)
flyctl scale count 2 --app autonomous-software-foundry

# Change VM type (for better performance)
flyctl scale vm performance-1x --app autonomous-software-foundry
```

### Environment Variables Management
```powershell
# Set individual secrets
flyctl secrets set OPENAI_API_KEY=your-key-here --app autonomous-software-foundry

# Set multiple secrets from file
flyctl secrets import --app autonomous-software-foundry < secrets.txt

# List current secrets
flyctl secrets list --app autonomous-software-foundry
```

## 📊 Monitoring & Observability

### Built-in Monitoring
```powershell
# View application metrics
flyctl metrics --app autonomous-software-foundry

# Monitor logs in real-time
flyctl logs --app autonomous-software-foundry --follow

# Check application status
flyctl status --app autonomous-software-foundry
```

### Custom Metrics Endpoints
- **Health Check**: `https://autonomous-software-foundry.fly.dev/health`
- **Prometheus Metrics**: `https://autonomous-software-foundry.fly.dev/metrics`
- **MCP Capabilities**: `https://autonomous-software-foundry.fly.dev/mcp/capabilities`
- **Analytics Dashboard**: `https://autonomous-software-foundry.fly.dev/dashboard`

### Log Analysis
```powershell
# Search logs for errors
flyctl logs --app autonomous-software-foundry | findstr "ERROR"

# Filter logs by timestamp
flyctl logs --app autonomous-software-foundry --since 1h

# Export logs for analysis
flyctl logs --app autonomous-software-foundry > app-logs.txt
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
The deployment includes a comprehensive CI/CD pipeline that:

1. **Runs Tests**: Executes pytest suite with coverage reporting
2. **Security Scanning**: Trivy vulnerability scanning and bandit security analysis  
3. **Code Quality**: Black formatting, isort imports, mypy type checking
4. **Buildpack Deployment**: Docker-free deployment using Python buildpacks
5. **Health Validation**: Post-deployment health checks and smoke tests
6. **Multi-Environment**: Separate staging and production deployments

### Deployment Triggers
- **Production**: Deploys on push to `main` branch
- **Staging**: Deploys on push to `staging` branch
- **Pull Requests**: Runs tests and security scans only

## 🔐 Security Best Practices

### Environment Security
```powershell
# Use Fly.io secrets for sensitive data
flyctl secrets set JWT_SECRET_KEY=$(openssl rand -base64 32) --app autonomous-software-foundry

# Rotate secrets regularly
flyctl secrets set OPENAI_API_KEY=new-key-here --app autonomous-software-foundry
```

### Network Security
- **HTTPS Enforced**: All traffic automatically redirected to HTTPS
- **CORS Configuration**: Properly configured for allowed origins
- **Rate Limiting**: Built-in request rate limiting
- **Security Headers**: HSTS, CSP, and other security headers enabled

### Authentication Security
- **Descope OAuth 2.1**: Modern authentication with PKCE flow
- **JWT Tokens**: Short-lived access tokens with refresh capability
- **Scope-based Authorization**: Granular permission control

## 🚨 Troubleshooting

### Common Issues

#### Deployment Failures
```powershell
# Check build logs
flyctl logs --app autonomous-software-foundry

# Validate configuration
flyctl config validate

# Restart application
flyctl restart --app autonomous-software-foundry
```

#### Database Connection Issues
```powershell
# Check database status
flyctl postgres status asf-db

# Test database connection
flyctl ssh console --app autonomous-software-foundry
# Then run: python -c "from src.database.fly_config import *; print('DB OK')"
```

#### Performance Issues
```powershell
# Check resource usage
flyctl metrics --app autonomous-software-foundry

# Scale up if needed
flyctl scale memory 1gb --app autonomous-software-foundry
flyctl scale count 2 --app autonomous-software-foundry
```

### Getting Help
- **Fly.io Documentation**: https://fly.io/docs/
- **Community Support**: https://community.fly.io/
- **Project Issues**: Use GitHub issues for project-specific problems

## 💰 Cost Optimization

### Fly.io Free Tier Limits
- **3 shared-cpu-1x VMs** with 256MB RAM each
- **3GB persistent volume storage**
- **160GB bandwidth per month**

### Optimization Strategies
1. **Start Small**: Begin with shared-cpu-1x and 512MB RAM
2. **Monitor Usage**: Use built-in metrics to track resource consumption
3. **Scale on Demand**: Only scale up when metrics indicate need
4. **Multi-region Gradually**: Start single-region, expand based on user geography

### Cost Monitoring
```powershell
# Check current billing
flyctl dashboard billing

# Monitor resource usage
flyctl metrics --app autonomous-software-foundry

# Review scaling history
flyctl history --app autonomous-software-foundry
```

## 🎯 Next Steps

After successful deployment:

1. **Configure Monitoring**: Set up alerts and dashboards
2. **Load Testing**: Validate performance under expected load
3. **Backup Strategy**: Implement automated backups
4. **Documentation**: Create runbooks for operational procedures
5. **Team Access**: Configure team access and permissions

This Docker-free deployment strategy provides a robust, scalable, and cost-effective solution for the Autonomous Software Foundry MCP server while maintaining compatibility with Windows development environments.