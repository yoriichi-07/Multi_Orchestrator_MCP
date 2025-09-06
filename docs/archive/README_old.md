# Multi-Agent Orchestrator MCP Server

A Model Context Protocol (MCP) server that provides advanced autonomous software development capabilities through multi-agent orchestration. This server enables LLMs to coordinate specialized AI agents for complete full-stack application development, with enterprise-grade authentication and analytics.

## 🏆 Competition Entry: Enterprise MCP Stack

Built with the mandatory competition technology stack:
- **🔐 Authentication**: Descope OAuth 2.1 + PKCE  
- **📊 Analytics**: Cequence AI Gateway Integration
- **🚀 Hosting**: Smithery Platform Deployment

## 🌟 Key Features

**Multi-Agent Coordination**. Uses specialized AI agents for different aspects of development.  
**Self-Healing Code**. Automatically detects and fixes issues in generated code.  
**Enterprise Security**. Full OAuth 2.1 + PKCE authentication with real-time monitoring.

## 🔧 Requirements

- Node.js 18 or newer
- VS Code, Cursor, Windsurf, Claude Desktop, Goose or any other MCP client

## 🚀 Getting started

First, install the Multi-Agent Orchestrator MCP server with your client.

**Standard config** works in most of the tools:

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

[Install Server VS Code](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%252Fmulti-orchestrator-mcp%2540latest%2522%255D%257D) [Install Server VS Code Insiders](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi-orchestrator%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%252Fmulti-orchestrator-mcp%2540latest%2522%255D%257D)

### ▶ Claude Code

Click the button to install the Claude Code extension. Name to your liking, use `command` type with the command `npx @smithery/multi-orchestrator-mcp@latest`. You can also verify config or add command like arguments via clicking `edit`.

#### ▶ Claude Desktop  

Click the button to install:

**[⬇ Add to Claude](https://claude.ai/mcp-config/install?name=multi-orchestrator&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40smithery%2Fmulti-orchestrator-mcp%40latest%22%5D%7D)**

Or install manually:

Go to `Claude Desktop Settings` -> `MCP` -> `Add new MCP Server`. Name to your liking, use `command` type with the command `npx @smithery/multi-orchestrator-mcp@latest`. You can also verify config or add command like arguments via clicking `edit`.

#### ▶ Codex

#### ▶ Cursor

Click the button to install:

**[⬇ Add to Cursor](https://cursor.sh/mcp-config/install?name=multi-orchestrator&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40smithery%2Fmulti-orchestrator-mcp%40latest%22%5D%7D)**

Or install manually:

Go to `Cursor Settings` -> `Features` -> `Model Context Protocol` -> `Add new MCP Server`. Name to your liking, use `command` type with the command `npx @smithery/multi-orchestrator-mcp@latest`. You can also verify config or add command like arguments via clicking `edit`.

#### ▶ Gemini CLI

#### ▶ Goose

Add the following to your `profiles.yaml`:

```yaml
default:
  providers:
    - mcp:
        server_name: multi-orchestrator
        server_params:
          command: npx
          args: ["-y", "@smithery/multi-orchestrator-mcp@latest"]
```

#### ▶ LM Studio

#### ▶ opencode

#### ▶ Qodo Gen

#### ▶ VS Code

For quick installation, click one of the installation buttons below...

[Install with NPX in VS Code](https://insiders.vscode.dev/redirect/mcp/install?name=multi-orchestrator&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40smithery%2Fmulti-orchestrator-mcp%40latest%22%5D%7D) [Install with NPX in VS Code Insiders](https://insiders.vscode.dev/redirect/mcp/install?name=multi-orchestrator&config=%7B%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40smithery%2Fmulti-orchestrator-mcp%40latest%22%5D%7D&quality=insiders)

For manual installation, you can configure the MCP server using one of these methods:

**Method 1: User Configuration (Recommended)**  
Add the configuration to your user-level MCP configuration file. Open the Command Palette (`Ctrl + Shift + P`) and run `MCP: Open User Configuration`. This will open your user `mcp.json` file where you can add the server configuration.

**Method 2: Workspace Configuration**  
Alternatively, you can add the configuration to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> For more details about MCP configuration in VS Code, see the [official VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/mcp).

For NPX installation:

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

#### ▶ Windsurf

## ⚙️ Configuration

The Multi-Agent Orchestrator MCP server supports the following configuration arguments. They can be provided in the JSON configuration above, as a part of the `"args"` list:

```bash
> npx @smithery/multi-orchestrator-mcp@latest --help
  --descope-project-id <id>        Descope project ID for OAuth 2.1 + PKCE authentication
  --cequence-gateway-id <id>       Cequence AI Gateway ID for analytics
  --cequence-api-key <key>         Cequence API key for gateway integration
  --openai-api-key <key>           OpenAI API key for GPT models
  --anthropic-api-key <key>        Anthropic API key for Claude models
  --max-agents <number>            Maximum number of concurrent agents (default: 5)
  --debug                          Enable debug logging
  --healing-enabled                Enable self-healing capabilities (default: true)
  --analytics-enabled              Enable Cequence analytics (default: true)
```

### Configuration file

The Multi-Agent Orchestrator MCP server can be configured using environment variables or a configuration file. You can specify the configuration file using the `--config` command line option:

```bash
npx @smithery/multi-orchestrator-mcp@latest --config path/to/config.json
```

**Configuration file schema:**

```json
{
  "descope_project_id": "P2xxx...",
  "descope_client_secret": "CS_xxx...",
  "descope_management_key": "K_xxx...",
  "cequence_gateway_id": "gateway-xxx",
  "cequence_api_key": "ck_xxx...",
  "openai_api_key": "sk-xxx...",
  "anthropic_api_key": "sk-ant-xxx...",
  "debug": false,
  "max_agents": 5,
  "healing_enabled": true,
  "analytics_enabled": true
}
```

## 🛠️ Tools

### Core orchestration

**orchestrate_development**: Coordinate multiple AI agents to build complete software projects  
**generate_architecture**: Create comprehensive system architecture for any scale  
**auto_fix_code**: Automatically fix code issues using self-healing algorithms  
**generate_tests**: Create comprehensive test suites with high coverage  

### Enterprise integrations

**get_cequence_analytics**: Retrieve real-time analytics from Cequence AI Gateway  
**validate_authentication**: Validate Descope authentication tokens  

## 📊 Resources

**orchestrator://capabilities**: Complete capabilities overview of the multi-agent system  
**orchestrator://analytics**: Real-time analytics dashboard data from Cequence  
**orchestrator://health**: Comprehensive health status of all system components  

## 💬 Prompts

**build_fullstack_app**: Pre-configured workflow for building complete applications  
**debug_and_fix**: Automated debugging and fixing workflow with self-healing  

## 💡 Example Usage

### Build a Complete Application

```typescript
// Using the build_fullstack_app prompt
await mcp.prompt("build_fullstack_app", {
  app_name: "TaskTracker Pro",
  description: "Project management app with real-time collaboration",
  features: [
    "User authentication with Descope",
    "Real-time task updates", 
    "Team collaboration tools",
    "Analytics dashboard",
    "Mobile responsive design"
  ]
});
```

### Orchestrate Development

```typescript
// Using the orchestrate_development tool
await mcp.call("orchestrate_development", {
  project_description: "E-commerce platform with user auth",
  requirements: ["User registration", "Product catalog", "Shopping cart"],
  tech_stack: "FastAPI + React",
  include_tests: true
});
```

### Generate System Architecture

```typescript
// Using the generate_architecture tool
await mcp.call("generate_architecture", {
  project_type: "microservices",
  scale: "medium",
  cloud_provider: "AWS"
});
```

### Auto-Fix Code Issues

```typescript
// Using the auto_fix_code tool
await mcp.call("auto_fix_code", {
  code: `
    def calculate_total(items):
        total = 0
        for item in items:
            total += item.price * item.quantity
        return total
  `,
  error_message: "AttributeError: 'dict' object has no attribute 'price'",
  language: "python"
});
```

## 🏗️ Architecture

### Multi-Agent System

```
Multi-Agent Orchestrator
├── Frontend Agent (React/Vue/Angular)
│   ├── Component Generation
│   ├── State Management
│   └── Responsive Design
├── Backend Agent (FastAPI/Django/Express)
│   ├── API Development
│   ├── Database Modeling
│   └── Authentication
├── DevOps Agent (Docker/K8s/Cloud)
│   ├── Containerization
│   ├── CI/CD Pipelines
│   └── Infrastructure as Code
└── QA Agent (Testing/Quality)
    ├── Unit Testing
    ├── Integration Testing
    └── Performance Testing
```

### Self-Healing Loop

```
Request → Agent Orchestration → Code Generation → Testing → 
Failure Analysis → Automated Fixes → Re-testing → Response
```

### Enterprise Integrations

- **Descope OAuth 2.1 + PKCE**: Enterprise-grade authentication
- **Cequence AI Gateway**: Real-time analytics and security monitoring  
- **Smithery Platform**: One-click deployment and scaling

## 🔐 Security & Analytics

### Authentication Features
- OAuth 2.1 with PKCE for enhanced security
- Non-Human Identity support for service-to-service auth
- JWT token validation with configurable claims
- Session management with refresh tokens

### Analytics & Monitoring
- Real-time request tracking and performance metrics
- Anomaly detection and security event monitoring
- Agent operation analytics and success rates
- Custom dashboards with operational intelligence

## 🚀 Competition Advantages

### Innovation Points
- **Multi-Agent Coordination**: First MCP server to orchestrate specialized AI agents
- **Self-Healing Code**: Automatic error detection and resolution
- **Enterprise Integration**: Full Descope + Cequence stack implementation
- **Comprehensive MCP Protocol**: Tools, resources, and prompts for complete workflows

### Technical Excellence
- **Full MCP Compliance**: Implements complete protocol specification
- **Scalable Architecture**: Designed for enterprise-grade usage
- **Security First**: OAuth 2.1 + PKCE with real-time monitoring
- **Developer Experience**: Intuitive tools and clear documentation

## 📚 Documentation

- [Competition Summary](./docs/competition/COMPETITION_SUMMARY.md)
- [Deployment Guide](./docs/competition/DEPLOYMENT_GUIDE.md)
- [API Documentation](./docs/api/)
- [Architecture Overview](./ARCHITECTURE.md)

## 🧪 Building

Docker:

```bash
docker build -t mcp/multi-orchestrator -f Dockerfile .
```

Local development:

```bash
# Clone repository
git clone https://github.com/yoriichi-07/Multi_Orchestrator_MCP.git
cd Multi_Orchestrator_MCP

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
python server.py
```

## 📄 License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.

---

**🏆 Built for MCP Competition 2024** | **Enterprise-Ready** | **Production-Tested**