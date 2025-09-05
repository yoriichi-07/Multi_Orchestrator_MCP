# 🤖 Multi-Agent Orchestrator MCP Server

A competition-ready Model Context Protocol (MCP) server with autonomous multi-agent orchestration, self-healing capabilities, and enterprise integrations.

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
- **📈 Real-time Analytics**: Cequence-powered insights and security monitoring

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

## 🏗️ Architecture

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
- **Analytics**: Cequence AI Gateway integration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- FastMCP framework
- Smithery account

### Local Development

1. **Clone and Setup**
```bash
git clone <repository>
cd multi-agent-orchestrator-mcp
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
# DESCOPE_PROJECT_ID=your_project_id
# CEQUENCE_GATEWAY_ID=your_gateway_id
# CEQUENCE_API_KEY=your_api_key
```

3. **Run Tests**
```bash
pytest tests/ -v
```

4. **Start Development Server**
```bash
fastmcp dev server.py
```

### Smithery Deployment

The server is ready for direct deployment to Smithery:

```bash
# Install Smithery CLI
pip install smithery

# Deploy to Smithery platform
smithery deploy
```

Configuration is handled through the FastMCP framework with @smithery decorators.

## 🔧 Available Tools

### 1. orchestrate_development
Coordinates multiple AI agents to build complete software projects.
```python
# Automatically generates frontend, backend, DevOps, and testing components
result = orchestrate_development(
    project_description="E-commerce platform with user auth",
    requirements=["User registration", "Product catalog", "Shopping cart"],
    tech_stack="FastAPI + React",
    include_tests=True
)
```

### 2. generate_architecture
Creates comprehensive system architecture for any scale.
```python
# Generates cloud architecture, components, and deployment strategy
architecture = generate_architecture(
    project_type="web_application",
    scale="medium",
    cloud_provider="AWS"
)
```

### 3. auto_fix_code
Automatically fixes code issues using self-healing algorithms.
```python
# Intelligently analyzes and fixes code problems
fixed_code = auto_fix_code(
    code="def broken_function():\n    return undefined_var",
    error_message="NameError: name 'undefined_var' is not defined",
    language="python"
)
```

### 4. generate_tests
Creates comprehensive test suites with high coverage.
```python
# Generates unit tests, integration tests, and fixtures
test_suite = generate_tests(
    code="class User: ...",
    test_type="unit", 
    framework="pytest"
)
```

### 5. get_cequence_analytics
Retrieves real-time analytics from Cequence AI Gateway.
```python
# Gets detailed usage metrics and security insights
analytics = get_cequence_analytics()
```

### 6. validate_authentication
Validates Descope authentication tokens.
```python
# Verifies JWT tokens and returns user context
auth_result = validate_authentication("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...")
```

## 📚 Available Resources

### orchestrator://capabilities
Complete capabilities overview of the multi-agent system.

### orchestrator://analytics  
Real-time analytics dashboard data from Cequence.

### orchestrator://health
Comprehensive health status of all system components.

## 💬 Available Prompts

### build_fullstack_app
Pre-configured workflow for building complete applications.

### debug_and_fix
Automated debugging and fixing workflow with self-healing.

## 🧪 Testing

### MCP Protocol Compliance
```bash
# Run full MCP test suite
pytest tests/test_mcp_compliance.py -v
```

### Component Tests
```bash
# Test authentication
pytest tests/test_descope_auth.py -v

# Test analytics
pytest tests/test_cequence_integration.py -v

# Test self-healing
pytest tests/test_self_healing.py -v
```

### Health Check
```bash
# Check server health
curl http://localhost:8000/health
```

## 🔐 Authentication & Security

### Descope OAuth 2.1 + PKCE
The server implements enterprise-grade authentication:

- **OAuth 2.1**: Latest OAuth standard with security enhancements
- **PKCE**: Proof Key for Code Exchange for added security
- **Non-Human Identity**: Support for service-to-service authentication
- **JWT Validation**: Stateless token verification

### Cequence AI Gateway
Comprehensive security and analytics monitoring:

- **Request Tracking**: Every API call monitored
- **Anomaly Detection**: Real-time threat detection
- **Performance Metrics**: Response times and error rates
- **Security Events**: Automated security incident tracking

## 📊 Analytics & Monitoring

### Real-time Metrics
- Total requests and response times
- Error rates and success patterns
- Tool usage analytics
- Agent performance metrics

### Security Intelligence
- Anomaly score tracking
- Security event monitoring
- Risk assessment automation
- Threat pattern detection

## 🌐 Deployment

### Smithery Platform
The server is optimized for Smithery deployment:

1. **FastMCP Framework**: Native Smithery compatibility
2. **Configuration Schema**: Automatic config validation
3. **Resource Management**: Efficient resource utilization
4. **Monitoring Integration**: Built-in observability

### Environment Configuration
Required environment variables for production:

```env
# Authentication
DESCOPE_PROJECT_ID=your_descope_project_id
DESCOPE_CLIENT_SECRET=your_client_secret
DESCOPE_MANAGEMENT_KEY=your_management_key

# Analytics
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key

# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
DEBUG=false
MAX_AGENTS=5
HEALING_ENABLED=true
ANALYTICS_ENABLED=true
```

## 🔄 Self-Healing Capabilities

### Automated Error Recovery
The system includes sophisticated self-healing mechanisms:

1. **Error Analysis**: LLM-powered error understanding
2. **Fix Generation**: Intelligent code corrections
3. **Testing**: Automated validation of fixes
4. **Learning**: Improvement from past fixes

### Supported Fix Types
- Syntax error corrections
- Logic bug resolution
- Performance optimizations
- Security vulnerability patches
- Import and dependency fixes

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black . && isort . && mypy src/
```

### Testing Guidelines
- Write tests for all new tools and resources
- Ensure MCP protocol compliance
- Test authentication and authorization
- Validate analytics integration

## 📄 License

MIT License - see LICENSE file for details.

---

**🏆 Built for MCP Hackathon 2024**

Ready for deployment to Smithery platform with full enterprise integration support.