# Multi-Agent Orchestrator MCP Server - Project Structure

This document describes the organization of the Multi-Agent Orchestrator MCP Server repository.

## 📁 Root Directory

```
Multi_Orchestrator_MCP/
├── README.md                      # Main project documentation
├── server.py                      # Main MCP server entry point
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── LICENSE                        # Apache 2.0 License
```

## 📁 Core Application (`src/`)

```
src/
├── main.py                        # Application entry point
├── __init__.py                    # Package initialization
├── agents/                        # Multi-agent system
│   ├── orchestrator.py           # Main orchestration logic
│   ├── frontend_agent.py         # Frontend development agent
│   ├── backend_agent.py          # Backend development agent
│   ├── devops_agent.py           # DevOps automation agent
│   └── reviewer.py               # Quality assurance agent
├── core/                          # Core system components
│   ├── config.py                 # Configuration management
│   ├── auth.py                   # Authentication middleware
│   ├── descope_auth.py           # Descope OAuth 2.1 integration
│   ├── cequence_integration.py   # Cequence AI Gateway
│   ├── mcp_server.py             # MCP protocol implementation
│   └── llm_manager.py            # LLM provider management
├── healing/                       # Self-healing system
│   ├── health_monitor.py         # Health monitoring
│   ├── healing_loop.py           # Healing orchestration
│   └── solution_generator.py     # Fix generation
├── tools/                         # MCP tools implementation
├── resources/                     # MCP resources
└── middleware/                    # HTTP middleware
```

## 📁 Documentation (`docs/`)

```
docs/
├── ARCHITECTURE.md               # Technical architecture
├── competition/                  # Competition-specific docs
│   ├── COMPETITION_SUMMARY.md    # Complete entry overview
│   ├── COMPLETION_GUIDE.md       # Final setup steps
│   ├── DEPLOYMENT_GUIDE.md       # Smithery deployment
│   └── ENVIRONMENT_SETUP.md      # Environment configuration
└── archive/                      # Historical documents
    └── ...                       # Previous iterations
```

## 📁 Testing (`tests/`)

```
tests/
├── conftest.py                   # Test configuration
├── unit/                         # Unit tests
├── integration/                  # Integration tests
├── e2e/                          # End-to-end tests
├── fixtures/                     # Test data
└── test_*.py                     # Specific test modules
```

## 📁 Configuration (`config/`)

```
config/
├── cequence-gateway-config.yml   # Cequence Gateway setup
└── ...                          # Other configuration files
```

## 📁 Scripts (`scripts/`)

```
scripts/
├── create_access_key.py          # Generate Descope access keys
├── create_machine_token.py       # Create machine tokens
├── test_auth_flow.py             # Test authentication
└── ...                          # Utility scripts
```

## 📁 Static Assets (`static/`)

```
static/
├── dashboard.html                # Analytics dashboard
├── cequence_dashboard.html       # Cequence-specific dashboard
└── ...                          # Other static files
```

## 📁 GitHub Configuration (`.github/`)

```
.github/
├── workflows/                    # CI/CD workflows
│   └── deploy.yml               # Deployment automation
└── ...                          # GitHub configuration
```

## 🔧 Key Files

### Entry Points
- **`server.py`** - Main MCP server with FastMCP + Smithery integration
- **`src/main.py`** - Core application logic
- **`src/core/mcp_server.py`** - MCP protocol implementation

### Configuration
- **`.env`** - Environment variables (not in repository)
- **`.env.example`** - Environment template
- **`pyproject.toml`** - Project metadata and dependencies
- **`requirements.txt`** - Python package requirements

### Documentation
- **`README.md`** - Main project documentation
- **`docs/ARCHITECTURE.md`** - Technical architecture overview
- **`docs/competition/`** - Competition-specific documentation

## 🏗️ Architecture Overview

The project follows a modular architecture:

1. **MCP Server Layer** (`server.py`) - FastMCP server with Smithery compatibility
2. **Agent Orchestration** (`src/agents/`) - Multi-agent coordination system
3. **Core Services** (`src/core/`) - Authentication, analytics, configuration
4. **Self-Healing** (`src/healing/`) - Automated error detection and fixing
5. **Protocol Implementation** (`src/tools/`, `src/resources/`) - MCP tools and resources

## 📋 File Naming Conventions

- **Python modules**: `snake_case.py`
- **Configuration files**: `kebab-case.yml` or `kebab-case.json`
- **Documentation**: `UPPERCASE.md` for important docs, `Title_Case.md` for guides
- **Test files**: `test_feature_name.py`
- **Script files**: `snake_case.py`

## 🧹 Maintenance

To keep the project clean:

1. **Remove cache files**: `find . -name "__pycache__" -type d -exec rm -rf {} +`
2. **Clean build artifacts**: `rm -rf build/ dist/ *.egg-info/`
3. **Archive old documents**: Move completed documents to `docs/archive/`
4. **Update dependencies**: Regularly update `requirements.txt` and `pyproject.toml`

This structure ensures clear separation of concerns, easy navigation, and maintainable code organization.