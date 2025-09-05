# Autonomous Software Foundry - Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the Autonomous Software Foundry MCP server to Vercel without Docker, optimized for Windows development environments.

## Overview

Our deployment strategy uses:
- **Platform**: Vercel (chosen for serverless deployment without Docker)
- **Deployment Method**: Direct Python serverless functions
- **Database**: External managed PostgreSQL (Supabase/PlanetScale/Neon)
- **Cache**: External managed Redis (Upstash/Redis Cloud)
- **CI/CD**: Git integration with automated deployment
- **Monitoring**: Vercel Analytics with application health checks

## Prerequisites

Before deploying, ensure you have:

1. **Python 3.11+** installed
2. **Poetry** for dependency management
3. **Node.js 18+** for Vercel CLI
4. **Git** for version control
5. **Vercel account** (free tier available)

## Step 1: Validate Your Environment

Run our validation script:

```powershell
.\scripts\test-deployment-simple.ps1
```

This script checks:
- ✅ Prerequisites (Python, Poetry, required files)
- ✅ Project structure and dependencies
- ✅ Vercel configuration
- ✅ Environment setup

## Step 2: Set Up External Services

Since Vercel is serverless, set up external services:

### Database Setup (Choose One):

**Option A: Supabase (Recommended)**
1. Visit https://supabase.com and create account
2. Create new project
3. Get database URL from Settings > Database
4. Format: `postgresql://postgres:[password]@[host]:5432/postgres`

**Option B: PlanetScale**
1. Visit https://planetscale.com
2. Create new database
3. Get connection string from dashboard

### Cache Setup (Choose One):

**Option A: Upstash (Recommended)**
1. Visit https://upstash.com
2. Create Redis database
3. Get connection string: `redis://[user]:[password]@[host]:[port]`

## Step 3: Install and Configure Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

## Step 4: Configure Environment Variables

In your Vercel dashboard, add these environment variables:

```bash
DESCOPE_PROJECT_ID=your_project_id_here
DESCOPE_MANAGEMENT_KEY=your_management_key_here
DESCOPE_CLIENT_ID=your_client_id_here
DESCOPE_CLIENT_SECRET=your_client_secret_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=your_database_connection_string_here
REDIS_URL=your_redis_connection_string_here
JWT_SECRET_KEY=your_very_secure_random_string_here
ENCRYPTION_KEY=your_32_byte_encryption_key_here
```

## Step 5: Deploy to Vercel

### Method A: Git Integration (Recommended)

1. Push your code to GitHub/GitLab/Bitbucket
2. Import repository in Vercel dashboard
3. Automatic deployments on every push to main

### Method B: CLI Deployment

```bash
# Navigate to project directory
cd "d:\intel\projects\global mcp hack"

# Deploy to production
vercel --prod
```

## Step 6: Verify Deployment

Test your deployed application:

```bash
# Health check
curl https://your-app.vercel.app/health

# MCP capabilities (with authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-app.vercel.app/mcp/capabilities
```

For complete deployment instructions, see **VERCEL-DEPLOYMENT-GUIDE.md**.