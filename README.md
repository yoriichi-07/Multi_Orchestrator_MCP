## Multi Agent Orchestrator

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Smithery Ready](https://img.shields.io/badge/Smithery-Ready-blue)](https://smithery.ai)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)

A Model Context Protocol (MCP) server that provides autonomous software development through intelligent multi-agent orchestration. This server coordinates specialized AI agents to handle complete application development workflows with self-healing capabilities and enterprise-grade integrations.

### Key Features

- **Multi-agent coordination**. Orchestrates Frontend, Backend, DevOps, and QA agents for complete application development.
- **Self-healing code generation**. Automatically detects and fixes issues during development with intelligent error recovery.  
- **Enterprise authentication**. Descope Access Key authentication with Bearer tokens for secure API access.
- **Real-time analytics**. Comprehensive monitoring through Cequence AI Gateway integration.
- **Advanced AI agents**. Autonomous architect, proactive quality, evolutionary prompts, and cloud deployment agents.

### Requirements

- Python 3.11 or newer
- VS Code, Cursor, Windsurf, Claude Desktop, or any other MCP client
- Optional: Descope project credentials for authentication
- Optional: Cequence AI Gateway access for analytics

### Getting started

First, add the Multi Agent Orchestrator MCP server to your client configuration.

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

**Production deployment** (recommended):

```json
{
  "mcpServers": {
    "multi-orchestrator": {
      "url": "https://smithery.ai/server/@yoriichi-07/multi_orchestrator_mcp"
    }
  }
}
```
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

Follow the MCP install [guide](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server), use the standard config above.

</details>

<details>
<summary>Windsurf</summary>

Follow Windsurf MCP [documentation](https://docs.windsurf.com/windsurf/cascade/mcp). Use the standard config above.

</details>

### Configuration

The Multi Agent Orchestrator MCP server supports configuration through environment variables:

```bash
# Authentication (optional)
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_MANAGEMENT_KEY=your_management_key

# Analytics (optional)
CEQUENCE_GATEWAY_ID=your_gateway_id
CEQUENCE_API_KEY=your_api_key

# Server Configuration
SERVER_PORT=8000
DEBUG=false
```

### Tools

The Multi Agent Orchestrator provides powerful development tools:

<details>
<summary><b>Application Development</b></summary>

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
<summary><b>Code Quality & Healing</b></summary>

- **auto_fix_code**
  - Description: Apply intelligent fixes to code issues
  - Parameters:
    - `code` (string): Code to analyze and fix
    - `error_message` (string): Error description
    - `context` (string, optional): Additional context
  - Use case: Automatically resolve bugs and errors

</details>

<details>
<summary><b>Advanced AI Agents</b></summary>

- **autonomous_architect**
  - Description: Dynamic system design with self-improving execution
  - Parameters:
    - `project_goals` (array): High-level project objectives
    - `constraints` (array, optional): Technical or business constraints
    - `learning_objectives` (array, optional): Areas for agent improvement
  - Use case: Intelligent architecture planning

- **proactive_quality_assurance**
  - Description: Policy-driven quality framework with auto-remediation
  - Parameters:
    - `code_context` (string): Code or project context to analyze
    - `quality_standards` (array, optional): Custom quality policies
    - `auto_remediation` (boolean, optional): Enable automatic fixes
  - Use case: Continuous quality improvement

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

- **mcp://capabilities** - Agent capabilities and supported technologies
- **mcp://analytics** - Real-time analytics data from Cequence AI Gateway
- **mcp://health** - System health and component status

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

# Configure environment variables (optional)
cp .env.example .env
# Edit .env with your credentials

# Run the MCP server
python mcp_server.py
```

#### Docker Deployment
```bash
# Build and run with Docker
docker build -t multi-orchestrator-mcp .
docker run -p 8000:8000 --env-file .env multi-orchestrator-mcp
```

### Testing

Run the test suite to validate functionality:

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

## Hackathon Project

**Team**: UpsideDown  
**Member**: Shreesaanth R  
**Theme**: Theme 2 - Multi-Agent Orchestration and Enterprise Integration

### What we built

The Multi Agent Orchestrator is a sophisticated Model Context Protocol server that demonstrates the power of coordinated AI agents in software development. The system can autonomously:

- Generate complete applications by coordinating Frontend, Backend, DevOps, and QA agents
- Self-heal code issues through intelligent error detection and automatic fixes
- Provide enterprise-grade authentication and analytics through Descope and Cequence integrations
- Adapt and improve through advanced AI agents that learn from each interaction

### How to run it

1. **Quick Start (Smithery)**:
   ```json
   {
     "mcpServers": {
       "multi-orchestrator": {
         "url": "https://smithery.ai/server/@yoriichi-07/multi_orchestrator_mcp"
       }
     }
   }
   ```

2. **Local Development**:
   ```bash
   git clone https://github.com/yoriichi-07/Multi_Orchestrator_MCP.git
   cd Multi_Orchestrator_MCP
   pip install -r requirements.txt
   python mcp_server.py
   ```

3. **Try it**: Use the `orchestrate_task` tool with a description like "Build a REST API for a todo application" and watch the agents work together.

### Tech Stack

- **Framework**: FastMCP for Model Context Protocol implementation
- **Language**: Python 3.11+ with asyncio for concurrent agent coordination
- **Authentication**: Descope Access Key authentication with JWT tokens
- **Analytics**: Cequence AI Gateway for real-time monitoring and insights
- **Deployment**: Docker containers with Smithery platform integration
- **AI Integration**: Support for OpenAI and Anthropic models
- **Architecture**: Multi-agent system with specialized Frontend, Backend, DevOps, and QA agents
- **Monitoring**: Structured logging with health monitoring and self-healing capabilities

### Demo Video

*Demo video will be added here*

### What we'd do with more time

**Enhanced Agent Intelligence**
- Implement reinforcement learning for agent coordination optimization
- Add context-aware agents that learn from project history and patterns
- Develop specialized agents for mobile, ML, and blockchain development

**Advanced Automation**
- Build predictive analytics to forecast development challenges
- Create automated testing strategies with comprehensive edge case generation
- Implement intelligent resource optimization for cloud deployments

**Enterprise Features**
- Add multi-tenant architecture with organization-specific agent training
- Implement advanced compliance standards (SOC2, HIPAA, PCI-DSS)
- Create custom agent marketplace for domain-specific development patterns

**Developer Experience**
- Build visual development interface for non-technical users
- Add integration with popular development tools (Jira, GitHub Actions, Slack)
- Create real-time collaboration features for distributed development teams