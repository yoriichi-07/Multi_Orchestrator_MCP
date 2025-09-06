#!/bin/bash
# Multi-Agent Orchestrator MCP - Quick Deployment Script

echo "🚀 Starting deployment of Multi-Agent Orchestrator MCP Server..."

# Check if Node.js is installed (required for Smithery CLI)
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found"

# Install Smithery CLI if not already installed
if ! command -v smithery &> /dev/null; then
    echo "📦 Installing Smithery CLI..."
    npm install -g @smithery/cli
fi

echo "✅ Smithery CLI ready"

# Login to Smithery (interactive)
echo "🔐 Please login to Smithery..."
smithery login

# Initialize project if not already done
if [ ! -f "smithery.json" ]; then
    echo "🔧 Initializing Smithery project..."
    smithery init
fi

echo "✅ Project initialized"

# Deploy to Smithery
echo "🚀 Deploying to Smithery platform..."
smithery deploy

echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Smithery dashboard"
echo "2. Test the deployed server"
echo "3. Submit your competition entry"
echo ""
echo "🔗 Smithery Dashboard: https://dashboard.smithery.ai"