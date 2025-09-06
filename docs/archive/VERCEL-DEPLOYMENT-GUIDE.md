# Vercel Deployment Guide - Autonomous Software Foundry

This guide provides step-by-step instructions for deploying the Autonomous Software Foundry MCP server to Vercel.

## Why Vercel?

- **No Docker Required**: Direct Python deployment without containerization
- **Serverless Functions**: Automatic scaling and cost efficiency
- **Built-in Analytics**: Request monitoring and performance metrics
- **Simple Environment Management**: Easy configuration through dashboard
- **Global Edge Network**: Fast response times worldwide
- **Windows-Friendly**: No virtualization issues

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Node.js**: For Vercel CLI (https://nodejs.org)
3. **Git Repository**: Your code should be in GitHub/GitLab/Bitbucket

## Step 1: Prepare Your Project

Ensure you have these files in your project root:
- `vercel.json` ✅ (Already created)
- `requirements.txt` ✅ (Already created) 
- `src/main.py` ✅ (Your FastAPI app)
- `.env.production.template` ✅ (Environment template)

## Step 2: Install Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to your Vercel account
vercel login
```

## Step 3: Set Up External Services

Since Vercel is serverless, you need external services for persistent data:

### Database Options (Choose One):

**Option A: Supabase (Recommended)**
1. Go to https://supabase.com
2. Create new project
3. Get connection string from Settings > Database
4. Format: `postgresql://postgres:password@host:5432/postgres`

**Option B: PlanetScale**
1. Go to https://planetscale.com
2. Create new database
3. Get connection string from dashboard

**Option C: Neon**
1. Go to https://neon.tech
2. Create new project
3. Get connection string from dashboard

### Redis Cache Options (Choose One):

**Option A: Upstash (Recommended for Vercel)**
1. Go to https://upstash.com
2. Create Redis database
3. Get connection string: `redis://username:password@host:port`

**Option B: Redis Cloud**
1. Go to https://redis.com/cloud
2. Create free database
3. Get connection string

## Step 4: Configure Environment Variables

### Method A: Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Import your GitHub repository
3. Go to Settings > Environment Variables
4. Add these variables:

```
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_MANAGEMENT_KEY=your_management_key
DESCOPE_CLIENT_ID=your_client_id
DESCOPE_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DATABASE_URL=your_database_connection_string
REDIS_URL=your_redis_connection_string
```

### Method B: Vercel CLI

```bash
# Set environment variables via CLI
vercel env add DESCOPE_PROJECT_ID
vercel env add OPENAI_API_KEY
vercel env add DATABASE_URL
vercel env add REDIS_URL
# ... add all other variables
```

## Step 5: Deploy to Vercel

### Option A: Git Integration (Recommended)

1. Push your code to GitHub/GitLab/Bitbucket
2. Import the repository in Vercel dashboard
3. Vercel will automatically deploy on every push to main branch

### Option B: CLI Deployment

```bash
# Navigate to your project directory
cd "d:\intel\projects\global mcp hack"

# Deploy to production
vercel --prod

# Follow the prompts:
# ? Set up and deploy? Yes
# ? Which scope? (select your account)
# ? Link to existing project? No
# ? What's your project's name? autonomous-software-foundry
# ? In which directory is your code located? ./
```

## Step 6: Verify Deployment

After deployment, you'll get a URL like: `https://autonomous-software-foundry.vercel.app`

Test these endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# MCP capabilities (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-app.vercel.app/mcp/capabilities
```

## Step 7: Set Up Custom Domain (Optional)

1. Go to Vercel dashboard > Your Project > Domains
2. Add your custom domain
3. Update DNS records as instructed by Vercel
4. Update CORS_ORIGINS in environment variables

## Troubleshooting

### Common Issues:

**1. Function Timeout**
- Vercel functions have 10-30 second timeout (depending on plan)
- Optimize long-running operations
- Consider using Vercel Pro for 300s timeout

**2. Cold Starts**
- First request after inactivity may be slow
- Consider keeping function warm with health checks

**3. File System Access**
- Vercel functions have read-only file system except `/tmp`
- Use `/tmp` for temporary files
- Consider external storage for persistent files

**4. Memory Limits**
- Free plan: 1024MB
- Pro plan: 3008MB
- Monitor memory usage in Vercel dashboard

**5. Database Connection Issues**
- Use connection pooling
- Check DATABASE_URL format
- Ensure database allows external connections

### Debugging Steps:

1. **Check Function Logs**:
   ```bash
   vercel logs https://your-app.vercel.app
   ```

2. **Test Locally**:
   ```bash
   vercel dev
   ```

3. **Check Environment Variables**:
   ```bash
   vercel env ls
   ```

## Monitoring and Analytics

### Built-in Vercel Analytics:
- Go to dashboard > Your Project > Analytics
- View request metrics, response times, errors

### Application Monitoring:
- Health endpoint: `/health`
- Metrics endpoint: `/metrics` (if implemented)
- Use structured logging for debugging

## Scaling Considerations

### Performance Optimization:
- Use Redis caching for frequent requests
- Optimize database queries
- Consider edge functions for better global performance

### Cost Management:
- Free tier: 100GB-hours of compute time
- Pro tier: $20/month for higher limits
- Monitor usage in Vercel dashboard

## Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Automatically enabled by Vercel
3. **CORS**: Configure properly for your domain
4. **Rate Limiting**: Implement in your application
5. **Input Validation**: Validate all inputs

## Continuous Deployment

### Automatic Deployments:
- Production: Push to `main` branch
- Preview: Push to any other branch
- Rollback: Use Vercel dashboard or CLI

### Manual Deployments:
```bash
# Deploy specific branch
vercel --prod --git-commit-sha=abc123

# Rollback to previous deployment
vercel rollback https://your-app.vercel.app
```

## Environment-Specific Configurations

### Development:
```bash
vercel dev  # Runs locally with Vercel environment
```

### Staging:
- Use preview deployments for testing
- Set different environment variables for staging

### Production:
- Use production environment variables
- Enable analytics and monitoring

## Support and Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Community**: https://github.com/vercel/vercel/discussions
- **FastAPI on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Vercel CLI Reference**: https://vercel.com/docs/cli

## Quick Reference Commands

```bash
# Install and setup
npm install -g vercel
vercel login

# Deploy
vercel --prod

# Check logs
vercel logs

# Local development
vercel dev

# Environment variables
vercel env add VARIABLE_NAME
vercel env ls

# Rollback
vercel rollback
```

Your Autonomous Software Foundry is now ready for Vercel deployment! 🚀