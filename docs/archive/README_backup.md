# 🤖 Multi-Agent Orchestrator MCP Server

A competition## 🏗️ Architecture

### FastMCP + Smithery Integration
```
Smithery Platform
├── FastMCP Server (server.py)
├── Descope Authentication
├── Cequence Analytics
└── Multi-Agent Orchestrator
    ├── Frontend Agent (React/Vue/Angular)
    ├── Backend Agent (FastAPI/Django/Express)
    ├── DevOps Agent (Docker/K8s/Cloud)
    └── QA Agent (Testing/Quality Assurance)
```

### Self-Healing Loop
```
Request → Agent Orchestration → Code Generation → Testing → 
Failure Analysis → Automated Fixes → Re-testing → Response
```

### Competition Compliance
- **MCP Protocol**: 100% compliant (21/21 tests passed)
- **Smithery Ready**: FastMCP framework with @smithery decorators
- **Enterprise Auth**: Descope OAuth 2.1 + PKCE
- **Analytics**: Cequence AI Gateway integrationContext Protocol (MCP) server with autonomous multi-agent orchestration, self-healing capabilities, and enterprise integrations.

## 🏆 Competition Features

### Mandatory Requirements ✅
- **🔐 Authentication**: Descope OAuth 2.1 + PKCE with Non-Human Identity
- **📊 Analytics**: Cequence AI Gateway for comprehensive monitoring
- **🚀 Hosting**: Smithery platform deployment ready

### Core Capabilities
- **🤖 Multi-Agent Orchestration**: Coordinates specialized Frontend, Backend, DevOps, and QA agents
- **🔧 Self-Healing**: LLM-powered automatic code fixes and error recovery
- **🏗️ Architecture Generation**: Intelligent system design for any scale
- **🧪 Test Generation**: Comprehensive test suite creation
- **📈 Real-time Analytics**: Cequence-powered insights and security monitoringtware Foundry - MCP Server

A sophisticated Model Context Protocol (MCP) server for autonomous software generation with self-healing ## 🚀 Production Deployment

### Vercel Deployment
See [VERCEL-DEPLOYMENT-GUIDE.md](VERCEL-DEPLOYMENT-GUIDE.md) for complete instructions.

### Environment Variables
Environment variables should be configured in the Vercel dashboard. See `.env.production.template` for required configuration.

### External Services
- **Database**: Supabase, PlanetScale, or Neon
- **Redis Cache**: Upstash or Redis Cloud
- **Authentication**: Descope OAuth 2.1 + PKCE
- **Monitoring**: Cequence AI Gateway integration

### Monitoring
- Structured JSON logging with correlation IDs
- Health check endpoints for serverless functions
- Metrics collection via external monitoring servicesies.

## 🛠️ Technology Stack

### Core Framework
- **FastMCP**: Smithery-compatible MCP server framework
- **FastAPI**: High-performance async HTTP server
- **Pydantic**: Data validation and serialization
- **Structlog**: Structured JSON logging

### Enterprise Integrations
- **Descope**: OAuth 2.1 + PKCE authentication
- **Cequence AI Gateway**: Request analytics and security monitoring
- **Smithery Platform**: Competition hosting environment

### Agent Technologies
- **OpenAI GPT**: Advanced reasoning and code generation
- **Anthropic Claude**: Alternative LLM provider support
- **Custom Agents**: Specialized Frontend, Backend, DevOps, and QA agents

## ���️ Architecture

### Core Components
- **FastAPI Server**: High-performance async MCP server
- **Authentication**: Descope OAuth 2.1 + PKCE with Non-Human Identity
- **Multi-Agent System**: Specialized Frontend, Backend, and Reviewer agents
- **Self-Healing Engine**: LLM-powered failure analysis and automated fixes
- **Observability**: Cequence AI Gateway integration for analytics and security monitoring

### Key Innovation: Self-Healing Loop
```
Code Generation → Testing → Failure Analysis → Automated Fixes → Re-testing
```

## ��� Quick Start

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
# Review environment template (do not copy to .env)
# Environment variables should be configured in Vercel dashboard
cat .env.production.template
```

3. **Run Tests**
```bash
poetry run pytest
```

4. **Start Development Server**
```bash
poetry run uvicorn src.main:app --reload
```

### Vercel Deployment

See [VERCEL-DEPLOYMENT-GUIDE.md](VERCEL-DEPLOYMENT-GUIDE.md) for complete deployment instructions.

```bash
# Validate deployment configuration
powershell scripts/validate-vercel-deployment.ps1

# Deploy to Vercel
vercel --prod
```

## ��� Testing

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

## ��� Authentication

The server uses Descope OAuth 2.1 + PKCE for authentication. Each request requires:
- Valid JWT token in Authorization header
- Appropriate scopes for the requested operation

### Supported Scopes
- `tools:ping` - Basic connectivity testing
- `tools:generate` - Code generation operations
- `tools:review` - Testing and quality analysis
- `tools:fix` - Automated code correction

## ��� API Endpoints

### Core Endpoints
- `GET /health` - Server health check
- `GET /mcp/capabilities` - MCP server capabilities

### Tool Endpoints
- `POST /mcp/v1/tools/ping` - Connectivity test
- `POST /mcp/v1/tools/health_check` - Comprehensive health check
- `POST /mcp/v1/tools/echo` - Echo test for request/response flow

## 📊 Analytics & Monitoring

### Cequence AI Gateway Integration
The system includes comprehensive analytics and security monitoring through Cequence AI Gateway:

- **Request Analytics**: Every API call is tracked with performance metrics
- **Security Monitoring**: Real-time detection of suspicious patterns
- **Agent Operations**: Detailed tracking of LLM agent activities
- **Risk Scoring**: Automatic risk assessment for all requests

### Real-time Dashboard
Access the analytics dashboard at `/static/demo_dashboard.html` for:
- Live metrics visualization
- Performance trends
- Security event monitoring
- Operational intelligence

### Configuration
```bash
# Add to your .env file
CEQUENCE_GATEWAY_URL=https://your-gateway.com
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key
```

See `docs/cequence-integration.md` for detailed configuration and usage information.

## ���️ Development

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

## ��� Production Deployment

### Environment Variables
See `.env.production.template` for required configuration.

### Monitoring
- Structured JSON logging with correlation IDs
- Health check endpoints for load balancers
- Metrics collection (when enabled)

## ��� Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## ��� License

MIT License - see LICENSE file for details.

---

**Built for the MCP Hackathon 2024** ���
