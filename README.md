# Multi-Agent Orchestrator MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Smithery Ready](https://img.shields.io/badge/Smithery-Ready-blue)](https://smithery.ai)
[![OAuth 2.1](https://img.shields.io/badge/OAuth-2.1%20%2B%20PKCE-green)](https://oauth.net/2.1/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)

A revolutionary Model Context Protocol (MCP) server that provides **autonomous software development** through intelligent multi-agent orchestration, self-healing code generation, and enterprise-grade integrations.

## 🚀 Key Features

- **🤖 Multi-Agent Orchestration**: Coordinate specialized AI agents (Frontend, Backend, DevOps, QA) for complete application development
- **🔧 Self-Healing Code Generation**: Automatically detect and fix issues during development with intelligent error recovery
- **🔐 Enterprise Authentication**: OAuth 2.1 + PKCE with Descope integration and Non-Human Identity support
- **📊 Real-Time Analytics**: Comprehensive monitoring and insights through Cequence AI Gateway
- **☁️ Cloud-Ready Deployment**: Seamless deployment on Smithery platform with one-click setup
- **⚡ FastMCP Framework**: Built for performance and scalability with modern Python async architecture

## 🎯 What Makes This Special

This MCP server is the **first of its kind** to offer:

1. **True Multi-Agent Coordination** - Multiple specialized AI agents working together
2. **Autonomous Development Workflows** - Build complete applications from descriptions
3. **Intelligent Self-Healing** - Automatically fix code issues as they occur
4. **Enterprise Integration Stack** - Production-ready with authentication and monitoring

## 📦 Quick Start

### One-Click Installation

Choose your preferred MCP client for instant setup:

#### VS Code & VS Code Insiders
[![Install in VS Code](https://img.shields.io/badge/Install%20in-VS%20Code-007ACC?style=for-the-badge&logo=visual-studio-code)](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%252Fmulti-orchestrator-mcp%2540latest%2522%255D%257D)
[![Install in VS Code Insiders](https://img.shields.io/badge/Install%20in-VS%20Code%20Insiders-1C479B?style=for-the-badge&logo=visual-studio-code)](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%252Fmulti-orchestrator-mcp%2540latest%2522%255D%257D&quality=insiders)

#### Cursor
[![Install in Cursor](https://img.shields.io/badge/Install%20in-Cursor-000000?style=for-the-badge&logo=cursor)](https://cursor.sh/mcp/install?name=multi-orchestrator&command=npx&args=-y,@smithery/multi-orchestrator-mcp@latest)

### Manual Configuration

For advanced users, add this to your MCP client configuration:

#### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest"
      ]
    }
  }
}
```

#### VS Code (`mcp.json`)
```json
{
  "servers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest"
      ]
    }
  }
}
```

#### Cursor (`cursor_mcp_config.json`)
```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/multi-orchestrator-mcp@latest"
      ]
    }
  }
}
```

## 🛠️ Tools

The Multi-Agent Orchestrator provides 6 powerful tools for autonomous development:

| Tool | Description | Use Case |
|------|-------------|----------|
| `orchestrate_development` | Coordinate multiple agents for full-stack development | Build complete applications from requirements |
| `generate_architecture` | Create system architecture diagrams and specifications | Design scalable software systems |
| `auto_fix_code` | Apply self-healing fixes to code issues | Automatically resolve bugs and errors |
| `generate_tests` | Create comprehensive test suites | Ensure code quality and coverage |
| `get_cequence_analytics` | Retrieve real-time usage analytics | Monitor server performance and usage |
| `validate_authentication` | Verify Descope JWT tokens | Secure API access control |

## 📚 Resources

Access real-time system data through these resources:

| Resource | Description | Data Source |
|----------|-------------|-------------|
| `orchestrator://capabilities` | Agent capabilities and supported technologies | Live system registry |
| `orchestrator://analytics` | Real-time dashboard data | Cequence AI Gateway |
| `orchestrator://health` | System health and component status | Comprehensive monitoring |

## 💬 Prompts

Use these workflow prompts for complex development tasks:

| Prompt | Description | Workflow |
|--------|-------------|----------|
| `build_fullstack_app` | Complete application development workflow | Orchestrate all agents for end-to-end development |
| `debug_and_fix` | Automated debugging and fixing workflow | Apply self-healing to resolve issues |

## 🎯 Example Usage

### Build a Complete Application
```typescript
// Ask your MCP client to use the build_fullstack_app prompt:
"Build a task management application with user authentication, real-time updates, and a REST API"

// The orchestrator will:
// 1. Analyze requirements and create architecture
// 2. Generate backend API with FastAPI + PostgreSQL
// 3. Create React frontend with TypeScript
// 4. Set up Docker deployment configuration
// 5. Generate comprehensive test suites
// 6. Apply quality assurance and security review
```

### Automatic Code Fixing
```typescript
// Use the auto_fix_code tool:
"Fix this Python function that has a syntax error and optimize its performance"

// The system will:
// 1. Detect and analyze the error
// 2. Apply intelligent fixes
// 3. Optimize code performance
// 4. Generate tests to prevent regression
// 5. Provide detailed explanation of changes
```

### System Architecture Generation
```typescript
// Use the generate_architecture tool:
"Design a microservices architecture for an e-commerce platform with high availability"

// The system will:
// 1. Create detailed system diagrams
// 2. Define microservices breakdown
// 3. Design database architecture
// 4. Plan deployment and scaling strategies
// 5. Include security and monitoring considerations
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smithery Platform                       │
├─────────────────────────────────────────────────────────────┤
│                    FastMCP Server                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Descope OAuth   │  │ Cequence        │  │ Multi-Agent │  │
│  │ 2.1 + PKCE      │  │ AI Gateway      │  │ Orchestrator│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Frontend  │  Backend   │  DevOps    │  QA Agent           │
│  Agent     │  Agent     │  Agent     │                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Development Setup

### Prerequisites
- Python 3.11 or newer
- Node.js 18+ (for Smithery deployment)
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/yoriichi-07/Multi_Orchestrator_MCP.git
cd Multi_Orchestrator_MCP

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
python server.py
```

### Docker Deployment
```bash
# Build the container
docker build -t multi-orchestrator-mcp .

# Run with environment variables
docker run -p 8000:8000 --env-file .env multi-orchestrator-mcp
```

## 🔐 Authentication Setup

This server uses **Descope OAuth 2.1 + PKCE** for enterprise-grade authentication:

### Required Environment Variables
```bash
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_CLIENT_SECRET=your_client_secret
DESCOPE_MANAGEMENT_KEY=your_management_key
```

### Supported Scopes
- `tools:*` - Access to all development tools
- `tools:generate` - Code generation capabilities
- `tools:review` - Testing and quality analysis
- `tools:fix` - Automated code correction
- `tools:deploy` - Project deployment
- `admin:*` - Administrative functions
- `admin:logs` - Access system logs
- `admin:config` - Modify configuration

## 📊 Analytics & Monitoring

Integration with **Cequence AI Gateway** provides:

- **Real-time Request Analytics** - Monitor API usage and performance
- **Security Event Detection** - Identify and respond to threats
- **Agent Operation Tracking** - Analyze development workflow efficiency
- **Performance Metrics** - Track response times and success rates

### Required Environment Variables
```bash
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key
```

## 🚀 Deployment on Smithery

Deploy your MCP server to production with one command:

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Deploy to Smithery
smithery deploy --config server.py
```

See our [Deployment Guide](docs/competition/DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
pytest tests/test_mcp_compliance.py -v   # MCP protocol compliance

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📖 Documentation

- [**Competition Summary**](docs/competition/COMPETITION_SUMMARY.md) - Complete overview of our competition entry
- [**Architecture Guide**](docs/ARCHITECTURE.md) - Technical architecture details
- [**Deployment Guide**](docs/competition/DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [**Environment Setup**](docs/competition/ENVIRONMENT_SETUP.md) - Configuration guide
- [**Completion Guide**](docs/competition/COMPLETION_GUIDE.md) - Final setup steps

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/yoriichi-07/Multi_Orchestrator_MCP/issues)
- **Documentation**: [Browse our comprehensive docs](docs/)
- **Community**: [Join our discussions](https://github.com/yoriichi-07/Multi_Orchestrator_MCP/discussions)

## 🏆 Competition Entry

This MCP server was created for the **Model Context Protocol Competition** featuring:

- ✅ **Cequence AI Gateway Integration** - Real-time analytics and security monitoring
- ✅ **Descope OAuth 2.1 + PKCE** - Enterprise authentication with Non-Human Identity
- ✅ **Smithery Platform Deployment** - Production-ready cloud hosting
- ✅ **Complete MCP Protocol Compliance** - Tools, resources, prompts, and schemas
- ✅ **Innovation in Multi-Agent Orchestration** - First-of-its-kind autonomous development

---

**🚀 Experience the Future of Autonomous Software Development**

*Built with ❤️ by the Multi-Agent Orchestrator team*