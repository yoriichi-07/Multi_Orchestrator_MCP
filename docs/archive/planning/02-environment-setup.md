# ⚙️ Environment Setup - Development Foundation

## 🎯 Objectives
- Set up a clean, reproducible development environment
- Initialize project structure following MCP best practices
- Configure all necessary tools and dependencies
- Verify basic MCP server functionality before adding complexity

## 🛠️ Prerequisites

### System Requirements
```bash
# Verify required versions
python --version  # 3.11+ required
node --version    # 18+ required for MCP client testing
docker --version  # Latest stable
git --version     # Latest stable
```

### Required Accounts & API Keys
```markdown
- [ ] **Descope Account**: Sign up at https://www.descope.com/sign-up
- [ ] **Cequence AI Gateway**: Request access at https://www.cequence.ai/products/ai-gateway/
- [ ] **OpenAI API Key**: For LLM provider (or Anthropic Claude)
- [ ] **Fly.io Account**: For production deployment
- [ ] **GitHub Account**: For code repository
```

### Development Tools Installation
```bash
# Install Python development tools
pip install poetry  # For dependency management
pip install black isort mypy  # Code formatting and type checking
pip install pytest pytest-asyncio  # Testing framework

# Install Node.js tools for MCP client testing
npm install -g @modelcontextprotocol/cli
npm install -g typescript ts-node

# Install Docker and Docker Compose
# Platform-specific installation - see https://docs.docker.com/
```

## 📁 Project Structure Setup

### Initialize Repository
```bash
# Create project directory
mkdir autonomous-software-foundry
cd autonomous-software-foundry

# Initialize git repository
git init
git branch -M main

# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
/outputs/
/temp/
/logs/
/test_results/
.pytest_cache/
.coverage
htmlcov/

# Secrets
*.key
*.pem
secrets.json
.env.local
.env.production

# Generated files
/dist/
/build/
*.log
EOF
```

### Core Directory Structure
```bash
# Create main project structure
mkdir -p {src,tests,docs,config,scripts,outputs}
mkdir -p src/{agents,core,tools,middleware}
mkdir -p tests/{unit,integration,e2e}
mkdir -p config/{prompts,templates}
mkdir -p outputs/{frontend,backend,projects}

# Create initial file structure
touch src/__init__.py
touch src/main.py
touch src/core/__init__.py
touch src/agents/__init__.py
touch src/tools/__init__.py
touch src/middleware/__init__.py
touch tests/__init__.py
touch README.md
touch ARCHITECTURE.md
touch DEPLOYMENT.md
```

### Python Environment Setup
```bash
# Initialize Poetry project
poetry init --name autonomous-software-foundry \
           --version 0.1.0 \
           --description "MCP server for autonomous software generation" \
           --author "Your Name <your.email@example.com>" \
           --license MIT \
           --no-interaction

# Add core dependencies
poetry add fastapi uvicorn python-multipart
poetry add httpx aiofiles pydantic-settings
poetry add structlog python-json-logger
poetry add asyncio-mqtt redis
poetry add openai anthropic  # LLM providers

# Add development dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov
poetry add --group dev black isort mypy
poetry add --group dev pre-commit
poetry add --group dev httpx-mock

# Install dependencies
poetry install
```

### Configuration Management
```bash
# Create pyproject.toml configuration
cat >> pyproject.toml << 'EOF'

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing"
]
asyncio_mode = "auto"
EOF
```

## 🏗️ Basic MCP Server Implementation

### Core Server Structure
```python
# src/main.py
"""
Autonomous Software Foundry - MCP Server Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.core.config import Settings
from src.core.auth import verify_token, AuthContext
from src.tools.basic import router as basic_router
from src.core.mcp_protocol import MCPServer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting Autonomous Software Foundry MCP Server")
    
    # Initialize services
    await initialize_services()
    
    yield
    
    # Cleanup
    logger.info("Shutting down MCP Server")
    await cleanup_services()


# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Software Foundry",
    description="MCP server for autonomous software generation with self-healing capabilities",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(basic_router, prefix="/mcp/v1", dependencies=[Security(verify_token)])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "autonomous-software-foundry"}


@app.get("/mcp/capabilities")
async def mcp_capabilities(auth: AuthContext = Depends(verify_token)):
    """MCP server capabilities endpoint"""
    return {
        "apiVersion": "2024-11-05",
        "capabilities": {
            "logging": {},
            "prompts": {
                "listChanged": True
            },
            "resources": {
                "subscribe": True,
                "listChanged": True
            },
            "tools": {
                "listChanged": True
            }
        },
        "serverInfo": {
            "name": "autonomous-software-foundry",
            "version": "0.1.0"
        }
    }


async def initialize_services():
    """Initialize all required services"""
    settings = Settings()
    logger.info("Services initialized", settings=settings.dict())


async def cleanup_services():
    """Cleanup services on shutdown"""
    logger.info("Services cleaned up")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use structlog instead
    )
```

### Configuration Management
```python
# src/core/config.py
"""
Configuration management for the MCP server
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server configuration
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Authentication
    descope_project_id: str = Field(..., description="Descope project ID")
    descope_management_key: Optional[str] = Field(None, description="Descope management key")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    
    # File management
    output_base_path: str = Field(default="/tmp/mcp_outputs", description="Base path for outputs")
    max_project_size_mb: int = Field(default=100, description="Maximum project size in MB")
    
    # Security
    allowed_file_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".yml", ".yaml"],
        description="Allowed file extensions for generation"
    )
    max_generation_time_seconds: int = Field(default=300, description="Max time for generation")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
```

### Authentication Middleware
```python
# src/core/auth.py
"""
Authentication and authorization for MCP server
"""
import jwt
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.core.config import settings


class AuthContext(BaseModel):
    """Authentication context for verified requests"""
    user_id: str
    scopes: List[str]
    token_claims: Dict[str, Any]
    correlation_id: str


class DescopeAuth:
    """Descope authentication handler"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        # In production, this would validate against Descope's public keys
        self.secret_key = "your-descope-secret"  # Replace with actual validation
    
    async def validate_token(self, token: str) -> AuthContext:
        """Validate JWT token and extract claims"""
        try:
            # Decode and validate JWT
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Extract relevant claims
            user_id = payload.get("sub", "unknown")
            scopes = payload.get("permissions", [])
            
            return AuthContext(
                user_id=user_id,
                scopes=scopes,
                token_claims=payload,
                correlation_id=payload.get("jti", "unknown")
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# Initialize auth handler
auth_handler = DescopeAuth(settings.descope_project_id)
security = HTTPBearer()


async def verify_token(token = Security(security)) -> AuthContext:
    """Verify and extract authentication context"""
    try:
        return await auth_handler.validate_token(token.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def require_scopes(*required_scopes: str):
    """Decorator to require specific scopes"""
    def decorator(auth_context: AuthContext = Depends(verify_token)):
        missing_scopes = set(required_scopes) - set(auth_context.scopes)
        if missing_scopes:
            raise HTTPException(
                status_code=403, 
                detail=f"Missing required scopes: {', '.join(missing_scopes)}"
            )
        return auth_context
    return decorator
```

### Basic MCP Tools
```python
# src/tools/basic.py
"""
Basic MCP tools for health checking and testing
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
import structlog

from src.core.auth import AuthContext, verify_token, require_scopes

logger = structlog.get_logger()
router = APIRouter()


@router.post("/tools/ping")
async def ping_tool(
    auth: AuthContext = Depends(require_scopes("tools:ping"))
) -> Dict[str, Any]:
    """
    Basic connectivity test tool
    
    Scope required: tools:ping
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "ping_requested",
        user_id=auth.user_id,
        correlation_id=correlation_id
    )
    
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "authenticated_user": auth.user_id
    }


@router.post("/tools/health_check")
async def health_check_tool(
    auth: AuthContext = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Comprehensive health check tool
    
    Scope required: Any valid authentication
    """
    correlation_id = str(uuid.uuid4())
    
    # Perform basic health checks
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "checks": {
            "auth": "passing",
            "file_system": "passing",
            "memory": "passing"
        }
    }
    
    # Test file system access
    try:
        test_file = f"/tmp/health_check_{correlation_id}.txt"
        with open(test_file, "w") as f:
            f.write("health check test")
        import os
        os.remove(test_file)
    except Exception as e:
        health_status["checks"]["file_system"] = f"failing: {str(e)}"
        health_status["status"] = "degraded"
    
    logger.info(
        "health_check_completed",
        user_id=auth.user_id,
        correlation_id=correlation_id,
        status=health_status["status"]
    )
    
    return health_status


@router.post("/tools/echo")
async def echo_tool(
    message: str,
    auth: AuthContext = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Echo tool for testing request/response flow
    
    Scope required: Any valid authentication
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "echo_requested",
        user_id=auth.user_id,
        correlation_id=correlation_id,
        message_length=len(message)
    )
    
    return {
        "echo": message,
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "user_id": auth.user_id,
        "message_length": len(message)
    }
```

## 🔧 Development Environment Configuration

### Environment Variables
```bash
# Create .env file for development
cat > .env << 'EOF'
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true

# Authentication
DESCOPE_PROJECT_ID=your_project_id_here
DESCOPE_MANAGEMENT_KEY=your_management_key_here

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEFAULT_LLM_PROVIDER=openai

# File Management
OUTPUT_BASE_PATH=./outputs
MAX_PROJECT_SIZE_MB=100

# Security
MAX_GENERATION_TIME_SECONDS=300

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=DEBUG
EOF

# Create production environment template
cat > .env.production.template << 'EOF'
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# Authentication
DESCOPE_PROJECT_ID=
DESCOPE_MANAGEMENT_KEY=

# LLM Configuration
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEFAULT_LLM_PROVIDER=openai

# File Management
OUTPUT_BASE_PATH=/app/outputs
MAX_PROJECT_SIZE_MB=500

# Security
MAX_GENERATION_TIME_SECONDS=600

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
EOF
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create outputs directory
RUN mkdir -p /app/outputs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "src.main"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - OUTPUT_BASE_PATH=/app/outputs
    volumes:
      - ./outputs:/app/outputs
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## 🧪 Testing Setup

### Basic Test Structure
```python
# tests/conftest.py
"""
Pytest configuration and shared fixtures
"""
import asyncio
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app
from src.core.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings override"""
    return Settings(
        debug=True,
        descope_project_id="test_project",
        output_base_path="/tmp/test_outputs",
        openai_api_key="test_key"
    )


@pytest.fixture
def test_client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing"""
    import jwt
    payload = {
        "sub": "test_user",
        "permissions": ["tools:ping", "tools:generate"],
        "exp": 9999999999  # Far future
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")
```

```python
# tests/test_basic_tools.py
"""
Tests for basic MCP tools
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "autonomous-software-foundry"


def test_ping_tool_without_auth(test_client: TestClient):
    """Test ping tool without authentication"""
    response = test_client.post("/mcp/v1/tools/ping")
    assert response.status_code == 401


def test_ping_tool_with_auth(test_client: TestClient, mock_auth_token: str):
    """Test ping tool with authentication"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    response = test_client.post("/mcp/v1/tools/ping", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
    assert "correlation_id" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_tool(async_client, mock_auth_token: str):
    """Test health check tool"""
    headers = {"Authorization": f"Bearer {mock_auth_token}"}
    response = await async_client.post("/mcp/v1/tools/health_check", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "checks" in data
```

## 🚀 Running and Validation

### Development Server
```bash
# Activate poetry environment
poetry shell

# Run development server
python -m src.main

# Or with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Basic Validation Tests
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test MCP capabilities (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/mcp/capabilities

# Run unit tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html
```

### MCP Client Testing
```bash
# Test with MCP CLI (if available)
npx @modelcontextprotocol/cli connect http://localhost:8000

# Or test with Claude Desktop configuration
cat > claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "autonomous-foundry": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Authorization: Bearer YOUR_TOKEN",
        "http://localhost:8000/mcp/v1/tools/ping"
      ]
    }
  }
}
EOF
```

## ✅ Validation Checklist

```markdown
- [ ] **Environment Setup**
  - [ ] Python 3.11+ installed and verified
  - [ ] Poetry dependency management working
  - [ ] All required packages installed without errors
  - [ ] Environment variables properly configured

- [ ] **Basic Server Functionality**
  - [ ] FastAPI server starts without errors
  - [ ] Health endpoint responds correctly
  - [ ] MCP capabilities endpoint returns proper structure
  - [ ] Server handles graceful shutdown

- [ ] **Authentication System**
  - [ ] Unauthenticated requests properly rejected
  - [ ] Valid tokens allow access to protected endpoints
  - [ ] Scope validation working correctly
  - [ ] Authentication errors provide clear feedback

- [ ] **Basic Tools**
  - [ ] Ping tool responds correctly
  - [ ] Health check tool performs system validation
  - [ ] Echo tool handles input/output properly
  - [ ] All tools include proper correlation IDs

- [ ] **Development Workflow**
  - [ ] Code formatting (black) works correctly
  - [ ] Import sorting (isort) works correctly
  - [ ] Type checking (mypy) passes
  - [ ] Unit tests run and pass
  - [ ] Docker build completes successfully

- [ ] **Logging and Monitoring**
  - [ ] Structured logs output properly formatted JSON
  - [ ] Correlation IDs present in all log entries
  - [ ] Log levels respect configuration
  - [ ] No sensitive data leaked in logs
```

## 📝 Environment Variables Reference

```bash
# Complete environment variables documentation
cat > ENV_REFERENCE.md << 'EOF'
# Environment Variables Reference

## Server Configuration
- `SERVER_HOST`: Server bind address (default: 0.0.0.0)
- `SERVER_PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)

## Authentication
- `DESCOPE_PROJECT_ID`: Descope project identifier (required)
- `DESCOPE_MANAGEMENT_KEY`: Descope management API key (optional)

## LLM Configuration
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `DEFAULT_LLM_PROVIDER`: Primary LLM provider (openai|anthropic)

## File Management
- `OUTPUT_BASE_PATH`: Base directory for generated files
- `MAX_PROJECT_SIZE_MB`: Maximum size limit for projects
- `ALLOWED_FILE_EXTENSIONS`: Comma-separated allowed extensions

## Security
- `MAX_GENERATION_TIME_SECONDS`: Timeout for generation operations

## Monitoring
- `ENABLE_METRICS`: Enable metrics collection
- `LOG_LEVEL`: Logging level (DEBUG|INFO|WARNING|ERROR)
EOF
```

---

**Next Steps**: Proceed to `03-descope-authentication.md` for detailed implementation of Descope authentication with Non-Human Identity and granular scoping.