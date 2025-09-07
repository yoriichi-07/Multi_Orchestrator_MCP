## Multi-Agent Orchestrator MCP

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Smithery Ready](https://img.shields.io/badge/Smithery-Ready-blue)](https://smithery.ai)
[![OAuth 2.1](https://img.shields.io/badge/OAuth-2.1%20%2B%20PKCE-green)](https://oauth.net/2.1/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)

A Model Context Protocol (MCP) server that provides autonomous software development through intelligent multi-agent orchestration, self-healing code generation, and enterprise-grade integrations. This server coordinates specialized AI agents to handle complete application development workflows with OAuth 2.1 + PKCE authentication via Descope and comprehensive monitoring through Cequence AI Gateway.

### Key Features

- **Multi-agent coordination**. Orchestrates Frontend, Backend, DevOps, and QA agents for complete application development.
- **Self-healing code generation**. Automatically detects and fixes issues during development with intelligent error recovery.
- **Enterprise authentication**. OAuth 2.1 + PKCE with Descope integration supporting Non-Human Identity for secure API access.
- **Real-time analytics**. Comprehensive monitoring and insights through Cequence AI Gateway integration.
- **Production-ready deployment**. Built on FastMCP framework with seamless Smithery platform deployment.

### Requirements

- Python 3.11 or newer
- VS Code, Cursor, Windsurf, Claude Desktop, Goose or any other MCP client
- Valid Descope project credentials (provided for demo)
- Optional: Cequence AI Gateway access for production analytics

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

**Smithery deployment** (recommended for production):

Access our live deployment at: `https://your-mcp-server.smithery.com`

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "url": "https://your-mcp-server.smithery.com/mcp"
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
# Authentication (Descope OAuth 2.1 + PKCE)
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_CLIENT_SECRET=your_client_secret
DESCOPE_MANAGEMENT_KEY=your_management_key

# Analytics (Cequence AI Gateway)
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key
ENABLE_ANALYTICS=true

# Server Configuration
SERVER_PORT=8000
DEBUG=false
```

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

This server implements OAuth 2.1 + PKCE authentication using Descope:

#### Required Environment Variables
```bash
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_CLIENT_SECRET=your_client_secret
DESCOPE_MANAGEMENT_KEY=your_management_key
```

#### Supported Scopes
- `full_access` - Complete access to all agent capabilities
- `tools:ping` - Basic connectivity testing
- `tools:generate` - Code generation capabilities
- `tools:review` - Testing and quality analysis capabilities

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

### Competition Entry

This MCP server was developed for the **Model Context Protocol Competition** and demonstrates:

- **Required Integration**: Cequence AI Gateway for analytics and monitoring
- **OAuth 2.1 + PKCE Authentication**: Implemented via Descope for enterprise security
- **Smithery Platform Deployment**: Production-ready cloud hosting
- **Complete MCP Protocol Compliance**: Tools, resources, and prompts with full schema validation
- **Innovation**: First-of-its-kind multi-agent orchestration for autonomous software development

**Live Demo**: [Smithery Deployment](https://your-mcp-server.smithery.com)
**Repository**: [GitHub](https://github.com/yoriichi-07/Multi_Orchestrator_MCP)

### License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/yoriichi-07/Multi_Orchestrator_MCP/issues)
- **Documentation**: [Browse our comprehensive docs](docs/)

---

**Multi-Agent Orchestrator MCP** - Autonomous software development through intelligent agent coordination.

*Built for the Model Context Protocol Competition by Team Multi-Agent Orchestrator*