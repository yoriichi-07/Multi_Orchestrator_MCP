# Multi Agent Orchestrator MCP


An enterprise‑grade Model Context Protocol (MCP) server for autonomous software engineering. It coordinates specialized agents (Architecture, Quality, Cloud, Prompt) to plan, build, test, and deploy applications with self‑healing, authentication, and analytics.

Check out!

Smithery Platfrom Deployed Link: https://smithery.ai/server/@yoriichi-07/multi_orchestrator_mcp

## Team

- Team Name : UpsideDown
- Member : Shreesaanth R

## Hackathon

- Theme 2: Build a Secure MCP Server for Agents (w/ Cequence)
- Challenge addressed: Build a production‑ready MCP server that orchestrates multiple agents with authentication (Descope), hosting (Cequence), and self‑healing to reliably execute end‑to‑end development workflows, deployable on Smithery.

---

## Requirements
- Python 3.11+
- Git
- An MCP‑compatible client (VS Code, Cursor, Windsurf, Claude Desktop, etc.)

---

## Getting started

First, install the server with your MCP client. For an overview of client support and mechanics, see the official MCP quickstart: https://modelcontextprotocol.io/quickstart/user

### Standard config (works in most clients)

```json
{
  "mcpServers": {
    "multi_orchestrator_mcp": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@smithery/cli@latest",
        "run",
        "@yoriichi-07/multi_orchestrator_mcp",
        "--key",
        "70fd8cf1-9dd3-4556-8a43-78916f617fb2"
      ]
    }
  }
}
```

<details>
<summary>VS Code</summary>

- One Click installation

[<img src="https://img.shields.io/badge/VS_Code-VS_Code?style=flat-square&label=Install%20Server&color=0098FF" alt="Install in VS Code">](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi_orchestrator_mcp%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%2Fcli%2540latest%2522%252C%2522run%2522%252C%2522%2540yoriichi-07%252Fmulti_orchestrator_mcp%2522%252C%2522--key%2522%252C%252270fd8cf1-9dd3-4556-8a43-78916f617fb2%2522%255D%257D)
[<img alt="Install in VS Code Insiders" src="https://img.shields.io/badge/VS_Code_Insiders-VS_Code_Insiders?style=flat-square&label=Install%20Server&color=24bfa5">](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522multi_orchestrator_mcp%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522-y%2522%252C%2522%2540smithery%2Fcli%2540latest%2522%252C%2522run%2522%252C%2522%2540yoriichi-07%252Fmulti_orchestrator_mcp%2522%252C%2522--key%2522%252C%252270fd8cf1-9dd3-4556-8a43-78916f617fb2%2522%255D%257D)


- Follow the MCP install guide: https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server
- Or via CLI:

```bash
# VS Code (stable)
npx -y @smithery/cli@latest install @yoriichi-07/multi_orchestrator_mcp --client vscode --key 70fd8cf1-9dd3-4556-8a43-78916f617fb2

# VS Code Insiders
npx -y @smithery/cli@latest install @yoriichi-07/multi_orchestrator_mcp --client vscode-insiders --key 70fd8cf1-9dd3-4556-8a43-78916f617fb2
```

</details>

<details>
<summary>Cursor</summary>

Click the button to install (if the deeplink is not supported on your OS, use the manual steps below):

[<img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Install in Cursor">](cursor://anysphere.cursor-deeplink/mcp/install?name=Multi%20Orchestrator&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBzbWl0aGVyeS9jbGlAbGF0ZXN0IiwicnVuIiwiQHlvcmlpY2hpLTA3L211bHRpX29yY2hlc3RyYXRvcl9tY3AiLCItLWtleSIsIjcwZmQ4Y2YxLTlkZDMtNDU1Ni04YTQzLTc4OTE2ZjYxN2ZiMiJdfQ==)

Manual: Go to `Cursor Settings` → `MCP` → `Add new MCP Server`. Choose `command` type and set:

```text
npx -y @smithery/cli@latest install @yoriichi-07/multi_orchestrator_mcp --client cursor --key 70fd8cf1-9dd3-4556-8a43-78916f617fb2
```

</details>

<details>
<summary>Claude Code</summary>

Use the CLI then paste the standard config above:

```bash
claude mcp add --transport http yoriichi-07-multi-orchestrator-mcp "https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp/mcp"
```

</details>

<details>
<summary>Claude Desktop</summary>

Follow the MCP quickstart: https://modelcontextprotocol.io/quickstart/user. Use the standard config above.

</details>

<details>
<summary>LM Studio</summary>

Use the Install → Edit `mcp.json`, paste the standard config. One-click: [![Add MCP](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=multi-orchestrator&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBtb2RlbGNvbnRleHRwcm90b2NvbC9zZXJ2ZXItZmV0Y2giLCJodHRwczovL3NtaXRoZXJ5LmFpL3NlcnZlci9AeW9yaWljaGktMDcvbXVsdGlfb3JjaGVzdHJhdG9yX21jcCJdfQ==)

</details>

<details>
<summary>Windsurf</summary>

Docs: https://docs.windsurf.com/windsurf/cascade/mcp. Use the standard config above (replace URL with `http://localhost:8080` for local).

</details>

<details>
<summary>Run locally</summary>

```bash
# Clone and install
git clone https://github.com/yoriichi-07/Multi_Orchestrator_MCP.git
cd Multi_Orchestrator_MCP
pip install -r requirements.txt

# Configure (optional)
cp config/env.template .env
# edit .env with DESCOPE_* if you want auth and analytics

# Start the MCP server (HTTP transport)
python mcp_server.py

# Default: http://localhost:8080
# MCP discovery path is served by FastMCP under the mounted app
```

</details>

<details>
<summary>Docker</summary>

```bash
docker build -t multi-orchestrator-mcp .
docker run --rm -p 8080:8080 --env-file .env multi-orchestrator-mcp
```

</details>

---

## Configuration

Environment variables (see `config/env.template`):
- `DESCOPE_PROJECT_ID`, `DESCOPE_MANAGEMENT_KEY`, `DESCOPE_ACCESS_KEY` – enable Descope authentication (optional for local/dev).
- `PORT` – server port (default `8080`).
- `DESCOPE_DEMO_MODE` – set `true` for local testing without full auth.
- `CEQUENCE_GATEWAY_ID`, `CEQUENCE_API_KEY` – enable Cequence analytics (optional).
- `JWT_SECRET_KEY`, `CORS_ORIGINS`, `RATE_LIMIT_REQUESTS`, logging toggles.

Client configuration templates are provided in `config/mcp.json.template` (direct JWT or auto‑refresh proxy modes).

---

## Capabilities

<details>
<summary><b>Tools (12)</b></summary>

- **orchestrate_task**
  - Title: Orchestrate multi‑agent task
  - Description: Coordinate Frontend/Backend/DevOps/QA agents for development, testing, or deployment.
  - Parameters: `task_description` (string), `task_type` (enum: development|architecture|testing|deployment), `priority` (enum)
- **generate_architecture**
  - Title: Generate architecture
  - Description: Produce system architecture with components and recommendations.
  - Parameters: `project_description` (string), `tech_stack` (string[]), `requirements` (string[])
- **auto_fix_code**
  - Title: Self‑healing fix
  - Description: Generate fixes for code using error context and explanations.
  - Parameters: `code` (string), `error_message` (string), `context` (string)
- **list_capabilities**
  - Title: Catalog
  - Description: Summarize available agents, tools, enterprise features, and supported tasks.
  - Parameters: none
- **get_system_status**
  - Title: System status
  - Description: Returns server health, agent availability, analytics/auth status, and timestamp.
  - Parameters: none
- **advanced_generate_application**
  - Title: Enterprise app generation
  - Description: Plan and generate an application using advanced agents and deployment strategies.
  - Parameters: `description` (string), `complexity_level` (enum), `innovation_requirements` (string[]), `deployment_strategy` (enum)
- **autonomous_architect**
  - Title: Autonomous architect
  - Description: Builds an execution DAG and adaptive strategy from goals and constraints.
  - Parameters: `project_goals` (string[]), `constraints` (string[]), `learning_objectives` (string[])
- **proactive_quality_assurance**
  - Title: Proactive quality
  - Description: Applies policy‑as‑code checks with optional auto‑remediation.
  - Parameters: `code_context` (string), `quality_standards` (string[]), `auto_remediation` (bool)
- **evolutionary_prompt_optimization**
  - Title: Prompt evolution
  - Description: Creates and evolves prompts based on goals and performance metrics.
  - Parameters: `base_prompt` (string), `optimization_goals` (string[]), `performance_metrics` (object)
- **last_mile_cloud_deployment**
  - Title: Cloud deployment
  - Description: Plans deployment, verifies environments, and returns rollback/monitoring setup.
  - Parameters: `application_context` (string), `target_environments` (string[]), `verification_requirements` (string[])
- **ping**
  - Title: Health check
  - Description: Simple liveness probe.
  - Parameters: none
- **debug_server_config**
  - Title: Debug configuration (temporary)
  - Description: Exposes non‑secret configuration metadata for diagnostics.
  - Parameters: none

</details>

<details>
<summary><b>Resources (3)</b></summary>

- `mcp://capabilities` — capabilities and catalog (JSON)
- `mcp://analytics` — analytics snapshot (requires Cequence)
- `mcp://health` — system health snapshot

</details>

<details>
<summary><b>Prompts (3)</b></summary>

- `project-setup` — guided setup plan
- `code-review` — structured review outline
- `revolutionary-development` — advanced strategy plan using autonomous agents

</details>

---

## Tech stack


<p align="center">
  <a href="https://www.descope.com"><img alt="Descope" src="https://img.shields.io/badge/Auth-Descope-orange?style=for-the-badge"></a>
  <a href="https://www.cequence.ai"><img alt="Cequence" src="https://img.shields.io/badge/Analytics-Cequence-6a5acd?style=for-the-badge"></a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="FastMCP" src="https://img.shields.io/badge/FastMCP-HTTP%20Transport-555?style=for-the-badge">
</p>

<p align="center">
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-SDK-000000?style=for-the-badge&logo=openai&logoColor=white">
  <img alt="Anthropic" src="https://img.shields.io/badge/Anthropic-Client-222?style=for-the-badge">
</p>

<p align="center">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white">
</p>

Full dependencies are declared in `requirements.txt` and `pyproject.toml`.

---

## Demo video

Link: (coming soon)

---

## Future Roadmap

<details open>
<summary>Detailed plan</summary>

### Enhanced Agent Intelligence
- Implement reinforcement learning for agent coordination optimization
- Add context‑aware agents that learn from project history and patterns
- Develop specialized agents for mobile, ML, and blockchain development

### Advanced Automation
- Build predictive analytics to forecast development challenges
- Create automated testing strategies with comprehensive edge case generation
- Implement intelligent resource optimization for cloud deployments

### Enterprise Features
- Add multi‑tenant architecture with organization‑specific agent training
- Implement advanced compliance standards (SOC2, HIPAA, PCI‑DSS)
- Create custom agent marketplace for domain‑specific development patterns

### Developer Experience
- Build a visual development interface for non‑technical users
- Integrate with Jira, GitHub Actions, Slack, and incident tooling
- Enable real‑time collaboration for distributed development teams

</details>

---
