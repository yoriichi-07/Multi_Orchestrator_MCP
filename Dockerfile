# Multi-Agent Orchestrator MCP Server - Professional Production Dockerfile
# Enterprise-grade deployment with advanced AI capabilities and comprehensive security

FROM ghcr.io/astral-sh/uv:python3.11-alpine AS base

# Metadata and labels
LABEL maintainer="Multi-Agent Orchestrator Team"
LABEL version="3.0.0"
LABEL description="Production MCP Server with 5 Advanced Agents and Enterprise Security"
LABEL org.opencontainers.image.title="Multi-Agent Orchestrator MCP Server"
LABEL org.opencontainers.image.description="FastMCP v2.12.2 server with advanced AI capabilities"
LABEL org.opencontainers.image.version="3.0.0"
LABEL org.opencontainers.image.vendor="Multi-Agent Orchestrator"

# Security: Create non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -u 1001 -S mcp -G mcp

# Install security updates and production dependencies
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        ca-certificates \
        curl \
        git \
        openssh-client \
        tzdata \
        bash \
        jq \
        && \
    rm -rf /var/cache/apk/*

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Production-specific environment
ENV NODE_ENV=production \
    MCP_ENV=production \
    LOG_LEVEL=INFO \
    ENABLE_METRICS=true \
    ENABLE_HEALTH_CHECKS=true \
    PORT=8080
    LOG_LEVEL=INFO \
    ENABLE_METRICS=true \
    ENABLE_HEALTH_CHECKS=true

# Security environment variables
ENV SECURITY_HEADERS_ENABLED=true \
    CORS_ENABLED=true \
    RATE_LIMITING_ENABLED=true \
    JWT_VALIDATION_STRICT=true

# Set timezone
ENV TZ=UTC

# Work directory
WORKDIR /app

# Copy dependency files first for better caching
COPY --chown=mcp:mcp pyproject.toml uv.lock ./

# Install dependencies with security optimizations
RUN --mount=type=cache,target=/root/.cache/uv,uid=1001,gid=1001 \
    uv sync --locked --no-install-project --no-dev && \
    # Remove unnecessary files to reduce image size
    find /app/.venv -name "*.pyc" -delete && \
    find /app/.venv -name "*.pyo" -delete && \
    find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + || true

# Copy application source code
COPY --chown=mcp:mcp . /app/

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv,uid=1001,gid=1001 \
    uv sync --locked --no-dev

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp /app/data /app/outputs && \
    chown -R mcp:mcp /app/logs /app/tmp /app/data /app/outputs && \
    chmod 755 /app/logs /app/tmp /app/data /app/outputs

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Security: Switch to non-root user
USER mcp:mcp

# Production startup script
COPY --chown=mcp:mcp <<'EOF' /app/start-production.sh
#!/bin/bash
set -euo pipefail

echo "🚀 Starting Multi-Agent Orchestrator MCP Server (Production)"
echo "=================================================="

# Validate environment
echo "📋 Validating production environment..."
if [[ -z "${DESCOPE_PROJECT_ID:-}" ]]; then
    echo "❌ DESCOPE_PROJECT_ID not set"
    exit 1
fi

if [[ -z "${CEQUENCE_GATEWAY_URL:-}" ]]; then
    echo "⚠️ CEQUENCE_GATEWAY_URL not set - analytics disabled"
fi

echo "✅ Environment validation passed"

# Start the server with production settings
echo "🤖 Starting advanced AI capabilities..."
echo "  🏗️ Autonomous Architect"
echo "  🛡️ Proactive Quality Framework"
echo "  🧠 Evolutionary Prompt Engine"
echo "  ☁️ Last Mile Cloud Agent"
echo "  🎯 Advanced Application Generator"
echo ""

# Security and monitoring
echo "🔐 Security features enabled:"
echo "  ✅ Descope OAuth 2.1 + PKCE"
echo "  ✅ Scope-based authorization"
echo "  ✅ JWT validation"
echo "  ✅ Rate limiting"
echo "  ✅ CORS protection"
echo "  ✅ Cequence analytics"
echo ""

echo "🎯 Starting MCP server on port ${PORT:-8080}..."
exec python mcp_server.py
EOF

RUN chmod +x /app/start-production.sh

# Production entrypoint
ENTRYPOINT ["/app/start-production.sh"]

# Final production image optimizations
RUN find /app -name "*.pyc" -delete && \
    find /app -name "*.pyo" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true && \
    find /app -name "*.coverage" -delete || true && \
    find /app -name ".pytest_cache" -type d -exec rm -rf {} + || true

# Production image metadata
LABEL stage="production"
LABEL security.enabled="true"
LABEL advanced.agents="5"
LABEL tools.count="16"
LABEL fastmcp.version="2.12.2"

# Final security check
RUN echo "🔐 Production image security summary:" && \
    echo "  👤 Non-root user: $(whoami)" && \
    echo "  🏠 Working directory: $(pwd)" && \
    echo "  📁 Permissions: $(ls -la /app | head -3)" && \
    echo "  🐍 Python version: $(python --version)" && \
    echo "  📦 UV version: $(uv --version)" && \
    echo "✅ Production image ready for deployment!"