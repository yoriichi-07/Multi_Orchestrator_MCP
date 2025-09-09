## Multi-Agent Orchestrator MCP - Revolutionary Edition

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Smithery Ready](https://img.shields.io/badge/Smithery-Ready-blue)](https://smithery.ai)
[![Access Key Auth](https://img.shields.io/badge/Auth-Access%20Key-green)](https://docs.descope.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Revolutionary AI](https://img.shields.io/badge/AI-Revolutionary-red)](https://github.com)

A Model Context Protocol (MCP) server that provides **revolutionary autonomous software development** through intelligent multi-agent orchestration, self-healing code generation, and enterprise-grade integrations. This server coordinates specialized AI agents to handle complete application development workflows with **legendary AI upgrades** that demonstrate the future of autonomous software engineering.

### 🚀 Revolutionary Features

#### 🌟 Legendary AI Agents
- **🤖 Autonomous Architect Agent**: Dynamic strategy generation with self-improving DAG execution
- **🛡️ Proactive Quality Agent**: Policy-as-code quality framework with auto-remediation  
- **🧬 Evolutionary Prompt Engine**: Self-improving AI communication with performance optimization
- **☁️ Last Mile Cloud Agent**: Autonomous deployment with intelligent verification and rollback

#### 🎯 Core Capabilities
- **Multi-agent coordination**. Orchestrates Frontend, Backend, DevOps, and QA agents for complete application development.
- **Self-healing code generation**. Automatically detects and fixes issues during development with intelligent error recovery.
- **Enterprise authentication**. Descope Access Key authentication with Bearer tokens supporting Non-Human Identity for secure API access.
- **Real-time analytics**. Comprehensive monitoring and insights through Cequence AI Gateway integration.
- **Production-ready deployment**. Built on FastMCP framework with seamless Smithery platform deployment.

#### ✨ Revolutionary Innovations
- **Autonomous Intelligence**: Self-learning and self-improving AI agents
- **Proactive Automation**: Predictive problem prevention and resolution
- **Evolutionary Optimization**: Continuous self-improvement across all systems  
- **Last Mile Automation**: Complete end-to-end autonomous deployment

### Requirements

- Python 3.11 or newer
- VS Code, Cursor, Windsurf, Claude Desktop, Goose or any other MCP client
- Valid Descope project credentials (provided for demo)
- Optional: Cequence AI Gateway access for production analytics

### 🎯 Legendary Tools

The revolutionary MCP server provides 5 legendary tools that demonstrate the future of autonomous software engineering:

#### 🌟 `legendary_generate_application`
Revolutionary application generation using all 4 legendary AI agents working in concert.
- **Autonomous Architecture**: Dynamic system design with self-adapting execution plans
- **Proactive Quality**: Policy-driven quality assurance with auto-remediation
- **Evolutionary Prompts**: Self-optimizing AI communication that improves over time
- **Last Mile Deployment**: Autonomous cloud deployment with intelligent verification

#### 🤖 `autonomous_architect`
Activate the Autonomous Architect Agent for dynamic system design that learns and improves.
- Creates intelligent execution DAGs based on project goals
- Self-adapts strategies based on constraints and learning objectives
- Generates autonomous architecture recommendations

#### 🛡️ `proactive_quality_assurance`
Activate proactive quality framework with policy-as-code implementation.
- Dynamic quality policy generation and enforcement
- Automatic violation detection and remediation
- Continuous quality improvement with predictive analysis

#### 🧬 `evolutionary_prompt_optimization`
Activate evolutionary prompt engine for self-improving AI communication.
- Automatic prompt optimization based on performance metrics
- AI-to-AI communication evolution and learning
- Performance tracking and adaptive improvement

#### ☁️ `last_mile_cloud_deployment`
Activate Last Mile Cloud Agent for autonomous deployment and verification.
- Intelligent deployment strategy planning
- Automated verification and rollback capabilities
- Multi-cloud optimization and monitoring setup

### Getting started

First, add the Multi-Agent Orchestrator MCP server to your client configuration.

**Standard config** works in most MCP clients:

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "python",
      "args": [
        "mcp_server.py"
      ],
      "cwd": "/path/to/multi-agent-orchestrator-mcp"
    }
  }
}
```

**Cequence AI Gateway deployment** (recommended for production):

Access our enterprise deployment with OAuth 2.0 protection: `https://ztaip-0qdv9d3o-4xp4r634bq-uc.a.run.app/mcp`

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "url": "https://ztaip-0qdv9d3o-4xp4r634bq-uc.a.run.app/mcp"
    }
  }
}
```

**Direct Smithery deployment** (for development/testing):

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "url": "https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp/mcp"
    }
  }
}
```

<details>
<summary>Claude Desktop</summary>

Follow the MCP install [guide](https://modelcontextprotocol.io/quickstart/user), use the standard config above.

</details>

<details>
<summary>Cursor</summary>

#### Click the button to install:

[<img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Install in Cursor">](cursor://anysphere.cursor-deeplink/mcp/install?name=Multi-Agent%20Orchestrator&config=eyJjb21tYW5kIjoicHl0aG9uIG1jcF9zZXJ2ZXIucHkifQ%3D%3D)

#### Or install manually:

Go to `Cursor Settings` -> `MCP` -> `Add new MCP Server`. Name to your liking, use `command` type with the command `python mcp_server.py` in the project directory.

</details>

<details>
<summary>VS Code</summary>

#### Click the button to install:

[<img src="https://img.shields.io/badge/VS_Code-VS_Code?style=flat-square&label=Install%20Server&color=0098FF" alt="Install in VS Code">](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522python%2522%252C%2522args%2522%253A%255B%2522mcp_server.py%2522%255D%257D) [<img alt="Install in VS Code Insiders" src="https://img.shields.io/badge/VS_Code_Insiders-VS_Code_Insiders?style=flat-square&label=Install%20Server&color=24bfa5">](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522python%2522%252C%2522args%2522%253A%255B%2522mcp_server.py%2522%255D%257D)

#### Or install manually:

Follow the MCP install [guide](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server), use the standard config above.

</details>

<details>
<summary>Windsurf</summary>

Follow Windsurf MCP [documentation](https://docs.windsurf.com/windsurf/cascade/mcp). Use the standard config above.

</details>

### Configuration

The Multi-Agent Orchestrator MCP server supports configuration through environment variables:

```bash
# Authentication (Descope Access Key)
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_ACCESS_KEY=your_access_key
DESCOPE_MANAGEMENT_KEY=your_management_key

# Analytics (Cequence AI Gateway)
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key
ENABLE_ANALYTICS=true

# Server Configuration
SERVER_PORT=8000
DEBUG=false
```

#### 🔧 Cursor IDE Authentication Setup

If you're experiencing authorization issues with Cursor IDE, see our comprehensive setup guide:

**📖 [Cursor IDE MCP Setup Guide](docs/cursor-mcp-setup.md)**

This guide covers:
- ✅ **Quick Fix**: Converting Descope Access Key to JWT token
- ✅ **Automatic Solution**: Authentication proxy with token refresh
- ✅ **Troubleshooting**: Common issues and debugging steps
- ✅ **Production Setup**: Best practices for deployment

**🔧 Authentication Tools**: The `scripts/` directory contains authentication utilities:
- `get_jwt_token.py` - Convert Access Key to JWT token
- `mcp_client_with_auth.py` - Authentication proxy with auto-refresh
- `validate_auth.py` - Test authentication setup
- See `scripts/README.md` for detailed usage instructions

### Tools

The Multi-Agent Orchestrator provides 6 powerful development tools:

<details>
<summary><b>Agent Orchestration</b></summary>

- **orchestrate_task**
  - Description: Coordinate multiple agents for software development tasks
  - Parameters:
    - `task_description` (string): Description of the development task
    - `task_type` (string, optional): Type of task (development, deployment, testing)
    - `priority` (string, optional): Task priority level
  - Use case: Build complete applications from requirements

- **generate_architecture**
  - Description: Create system architecture diagrams and specifications
  - Parameters:
    - `project_description` (string): Description of the project
    - `tech_stack` (array): Preferred technology stack
    - `requirements` (array): System requirements
  - Use case: Design scalable software systems

</details>

<details>
<summary><b>Self-Healing Development</b></summary>

- **auto_fix_code**
  - Description: Apply intelligent fixes to code issues
  - Parameters:
    - `code` (string): Code to analyze and fix
    - `error_message` (string): Error description
    - `context` (string, optional): Additional context
  - Use case: Automatically resolve bugs and errors

</details>

<details>
<summary><b>System Monitoring</b></summary>

- **get_system_status**
  - Description: Retrieve comprehensive system health information
  - Parameters: None
  - Use case: Monitor server performance and component health

- **list_capabilities**
  - Description: Get available agent capabilities and supported technologies
  - Parameters: None
  - Use case: Discover available development tools and frameworks

</details>

### Resources

Access real-time system data through these MCP resources:

- **mcp://capabilities** - Agent capabilities and supported technologies from live system registry
- **mcp://analytics** - Real-time dashboard data from Cequence AI Gateway
- **mcp://health** - System health and component status with comprehensive monitoring

### Local Development Setup

#### Prerequisites
- Python 3.11 or newer
- Git

#### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/yoriichi-07/Multi_Orchestrator_MCP.git
cd Multi_Orchestrator_MCP

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the MCP server (STDIO mode)
python mcp_server.py

# Or run HTTP server for production
python main.py
```

#### Docker Deployment
```bash
# Build and run with Docker
docker build -t multi-orchestrator-mcp .
docker run -p 8000:8000 --env-file .env multi-orchestrator-mcp
```

### Authentication Setup

This server implements Access Key authentication using Descope:

#### Required Environment Variables
```bash
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_ACCESS_KEY=your_access_key
DESCOPE_MANAGEMENT_KEY=your_management_key
```

#### Supported Scopes
- `full_access` - Complete access to all agent capabilities
- `tools:ping` - Basic connectivity testing
- `tools:generate` - Code generation capabilities
- `tools:review` - Testing and quality analysis capabilities

#### 🚨 Troubleshooting Authentication Issues

**Problem**: Getting authorization errors in Cursor IDE?  
**Solution**: Cursor IDE requires JWT tokens, not raw Access Keys.

**📖 [Complete Fix Guide](docs/cursor-mcp-setup.md)** - Step-by-step instructions  
**🔧 [Authentication Scripts](scripts/README.md)** - Ready-to-use tools

**Quick Fix Example:**
```bash
# Get JWT token from your Access Key
python scripts/get_jwt_token.py YOUR_ACCESS_KEY

# Use the JWT token in Cursor IDE configuration
{
  "mcpServers": {
    "multi-orchestrator": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "YOUR_MCP_SERVER_URL"],
      "env": {
        "AUTHORIZATION": "Bearer YOUR_JWT_TOKEN_HERE"
      }
    }
  }
}
```

### Analytics & Monitoring

Integration with Cequence AI Gateway provides:

- Real-time request analytics and performance monitoring
- Security event detection and threat analysis
- Agent operation tracking for workflow optimization
- Comprehensive audit logging and compliance reporting

#### Configuration
```bash
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key
ENABLE_ANALYTICS=true
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_mcp_server.py -v         # MCP protocol compliance
pytest tests/test_descope_auth.py -v       # Authentication tests
pytest tests/test_cequence_integration.py -v # Analytics integration

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Team

**Team Name**: Multi-Agent Orchestrator  
**Members**: 
- yoriichi-07 - Lead Developer & System Architecture
- Multi-Agent Orchestrator Team - AI Agent Coordination Specialists

## Demo Video

🎥 **Watch our 5-minute demo**: *[Demo video coming soon - currently being recorded]*

*The demo showcases our Multi-Agent Orchestrator MCP server in action, demonstrating autonomous software development, self-healing capabilities, and seamless integration with Cequence AI Gateway and Descope authentication.*

## What We'd Do With More Time

Given additional development time, we would focus on the following enhancements:

### 🤖 **Enhanced Agent Intelligence**
- **Machine Learning Optimization**: Implement reinforcement learning to improve agent coordination and decision-making over time
- **Context-Aware Agents**: Develop agents that learn from previous projects and adapt their strategies based on historical success patterns
- **Multi-Modal Agents**: Expand agents to handle design assets, documentation, and multimedia content beyond just code

### 🌐 **Expanded Platform Support**
- **Additional Programming Languages**: Support for Go, Rust, Java, C#, and other modern development stacks
- **Cloud Platform Integration**: Native support for AWS, Azure, GCP with automated resource provisioning and optimization
- **Mobile Development**: Specialized agents for iOS, Android, and cross-platform mobile app development

### 📊 **Advanced Analytics & Insights**
- **Predictive Development Metrics**: AI-powered predictions of development time, potential issues, and resource requirements
- **Quality Prediction Models**: Advanced static analysis to predict code maintainability and technical debt
- **Performance Optimization**: Automated performance profiling and optimization recommendations

### 🔧 **Developer Experience Enhancements**
- **Visual Development Interface**: Web-based GUI for non-technical users to interact with the agent system
- **Custom Agent Marketplace**: Community-driven platform for sharing and discovering specialized development agents
- **Integration Ecosystem**: Deeper integrations with popular development tools like Jira, Slack, GitHub Actions

### 🚀 **Enterprise Features**
- **Multi-Tenant Architecture**: Support for multiple organizations with isolated environments and billing
- **Advanced Compliance**: SOC2, HIPAA, and other enterprise compliance standards
- **Custom Training**: Ability to train agents on organization-specific coding standards and practices

### 🔬 **Research & Innovation**
- **Autonomous Testing Strategies**: Agents that generate comprehensive test suites including edge cases and performance tests
- **Self-Improving Architecture**: System that continuously refines its own codebase and deployment strategies
- **Cross-Project Learning**: Knowledge sharing between different projects to accelerate development patterns

### Competition Entry

This MCP server was developed for the **Model Context Protocol Competition** and demonstrates:

- **Required Integration**: Cequence AI Gateway for analytics and monitoring
- **Descope Access Key Authentication**: Implemented via Descope for enterprise security
- **Smithery Platform Deployment**: Production-ready cloud hosting
- **Complete MCP Protocol Compliance**: Tools, resources, and prompts with full schema validation
- **Innovation**: First-of-its-kind multi-agent orchestration for autonomous software development

**Live Demo**: [Cequence Production](https://ztaip-0qdv9d3o-4xp4r634bq-uc.a.run.app/mcp) | [Smithery Backend](https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp/mcp)
**Repository**: [GitHub](https://github.com/yoriichi-07/Multi_Orchestrator_MCP)

### License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/yoriichi-07/Multi_Orchestrator_MCP/issues)
- **Documentation**: [Browse our comprehensive docs](docs/)
- **Authentication Help**: [Cursor IDE Setup Guide](docs/cursor-mcp-setup.md)
- **Authentication Tools**: [Scripts Documentation](scripts/README.md)

---

**Multi-Agent Orchestrator MCP** - Autonomous software development through intelligent agent coordination.

*Built for the Model Context Protocol Competition by Team Multi-Agent Orchestrator*