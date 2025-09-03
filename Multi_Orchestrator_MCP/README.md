# � Autonomous Software Foundry - MCP Server

A sophisticated Model Context Protocol (MCP) server for autonomous software generation with self-healing capabilities.

## � Features

- **� Security-First**: OAuth 2.1 + PKCE authentication with Descope
- **� Observable**: Complete request tracing and structured logging
- **� Resilient**: Self-healing capabilities and graceful degradation
- **� Modular**: Loosely coupled agents with clear interfaces
- **� Scalable**: Designed for production deployment

## �️ Architecture

### Core Components
- **FastAPI Server**: High-performance async MCP server
- **Authentication**: Descope OAuth 2.1 + PKCE with Non-Human Identity
- **Multi-Agent System**: Specialized Frontend, Backend, and Reviewer agents
- **Self-Healing Engine**: LLM-powered failure analysis and automated fixes
- **Observability**: Cequence AI Gateway integration

### Key Innovation: Self-Healing Loop
```
Code Generation → Testing → Failure Analysis → Automated Fixes → Re-testing
```

## � Quick Start

### Prerequisites
- Python 3.11+
- Poetry for dependency management
- Docker (optional)

### Installation

1. **Clone and Setup**
```bash
git clone <repository>
cd autonomous-software-foundry
poetry install
```

2. **Configure Environment**
```bash
cp .env.production.template .env
# Edit .env with your API keys and configuration
```

3. **Run Tests**
```bash
poetry run pytest
```

4. **Start Development Server**
```bash
poetry run uvicorn src.main:app --reload
```

### Docker Deployment

```bash
docker-compose up --build
```

## � Testing

### Unit Tests
```bash
poetry run pytest tests/ -v --cov=src
```

### Health Check
```bash
curl http://localhost:8000/health
```

### MCP Capabilities
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/mcp/capabilities
```

## � Authentication

The server uses Descope OAuth 2.1 + PKCE for authentication. Each request requires:
- Valid JWT token in Authorization header
- Appropriate scopes for the requested operation

### Supported Scopes
- `tools:ping` - Basic connectivity testing
- `tools:generate` - Code generation operations
- `tools:review` - Testing and quality analysis
- `tools:fix` - Automated code correction

## � API Endpoints

### Core Endpoints
- `GET /health` - Server health check
- `GET /mcp/capabilities` - MCP server capabilities

### Tool Endpoints
- `POST /mcp/v1/tools/ping` - Connectivity test
- `POST /mcp/v1/tools/health_check` - Comprehensive health check
- `POST /mcp/v1/tools/echo` - Echo test for request/response flow

## �️ Development

### Code Quality
```bash
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run mypy src/
```

### Pre-commit Hooks
```bash
poetry run pre-commit install
```

## � Production Deployment

### Environment Variables
See `.env.production.template` for required configuration.

### Monitoring
- Structured JSON logging with correlation IDs
- Health check endpoints for load balancers
- Metrics collection (when enabled)

## � Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## � License

MIT License - see LICENSE file for details.

---

**Built for the MCP Hackathon 2024** �
