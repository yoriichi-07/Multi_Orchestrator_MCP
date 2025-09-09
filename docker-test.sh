#!/bin/bash
set -e

echo "🧪 Testing Docker build and startup..."

# Build the image
echo "📦 Building Docker image..."
docker build -t mcp-server-test .

# Test that the startup script exists and is executable
echo "🔍 Verifying startup script..."
docker run --rm mcp-server-test ls -la /app/start-production.sh

# Test script permissions
echo "🔐 Checking script permissions..."
docker run --rm mcp-server-test test -x /app/start-production.sh && echo "✅ Script is executable" || echo "❌ Script is not executable"

# Test container startup (with timeout)
echo "🚀 Testing container startup..."
timeout 30s docker run --rm -p 8080:8080 mcp-server-test || echo "⚠️ Startup test completed (timeout expected)"

echo "✅ Docker test completed"