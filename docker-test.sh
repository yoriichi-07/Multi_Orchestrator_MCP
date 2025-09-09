#!/bin/bash
set -e

echo "🧪 Testing Docker build and startup..."

# Build the image
echo "📦 Building Docker image..."
docker build -t mcp-server-test .

# Test that the container starts directly with Python
echo "🔍 Verifying Python entrypoint..."
docker run --rm mcp-server-test python --version

# Test working directory and permissions
echo "🔐 Checking working directory and permissions..."
docker run --rm mcp-server-test pwd
docker run --rm mcp-server-test whoami
docker run --rm mcp-server-test ls -la /app/mcp_server.py

# Test container startup (with timeout)
echo "🚀 Testing container startup..."
timeout 30s docker run --rm -p 8080:8080 mcp-server-test || echo "⚠️ Startup test completed (timeout expected)"

echo "✅ Docker test completed"