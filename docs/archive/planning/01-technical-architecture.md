# 🏗️ Technical Architecture - Autonomous Software Foundry

## 🎯 Architecture Overview

### System Design Philosophy
- **Security-First**: Every component authenticated and authorized from day one
- **Observable**: Complete request tracing and agent interaction monitoring
- **Resilient**: Self-healing capabilities and graceful degradation
- **Modular**: Loosely coupled agents with clear interfaces
- **Scalable**: Designed for production deployment and load

### High-Level Data Flow
```
User Request → Cequence Gateway → Authenticated MCP Server → Agent Orchestrator
                                        ↓
Prompt Library ← Agent Specialization ← Task Analysis
                                        ↓
Frontend Agent → Code Generation → Output Directory (/frontend)
Backend Agent → Code Generation → Output Directory (/backend)
                                        ↓
Project Assembly → Docker Compose → Runnable Application
                                        ↓
Reviewer Agent → Testing Pipeline → Failure Analysis
                                        ↓
Fix Generation → Code Patching → Re-testing → Success/Failure Report
```

## 🔧 Technology Stack Decisions

### Core Infrastructure

#### MCP Server Framework
**Choice**: Python FastAPI + MCP TypeScript SDK patterns
**Rationale**: 
- FastAPI provides excellent async support for long-running operations
- Built-in OpenAPI documentation for tool discovery
- Easy middleware integration for authentication
- Strong typing support for reliability

**Key Dependencies**:
```python
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.2  # For LLM API calls
aiofiles==23.2.1  # For file operations
python-multipart==0.0.6  # For file uploads
```

#### Authentication Layer
**Choice**: Descope OAuth 2.1 + PKCE with Non-Human Identity
**Rationale**:
- Specifically designed for AI agent authentication
- Handles complex OAuth flows automatically
- Granular scope management for different tool categories
- Enterprise-grade security out of the box

**Implementation Pattern**:
```python
from descope import DescopeClient
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

descope_client = DescopeClient(project_id="your_project_id")
security = HTTPBearer()

async def verify_token(token: str = Security(security)):
    try:
        jwt_response = descope_client.validate_jwt(token.credentials)
        return jwt_response
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")
```

#### Observability and Monitoring
**Choice**: Cequence AI Gateway + Structured Logging
**Rationale**:
- Purpose-built for AI agent interactions
- Automatic request/response logging
- Rate limiting and abuse protection
- Real-time monitoring dashboard

**Logging Strategy**:
```python
import structlog
import uuid

logger = structlog.get_logger()

async def log_agent_interaction(agent_type: str, operation: str, correlation_id: str):
    logger.info(
        "agent_interaction",
        agent_type=agent_type,
        operation=operation,
        correlation_id=correlation_id,
        timestamp=datetime.utcnow().isoformat()
    )
```

### Agent Architecture

#### LLM Provider Abstraction
**Choice**: Multi-provider support with OpenAI as primary
**Rationale**:
- Provider independence for cost optimization
- Fallback options for reliability
- Different models for different agent types

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.1
    ) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return response.choices[0].message.content
```

#### Agent Specialization Framework
**Choice**: Role-based agents with specialized prompt libraries
**Rationale**:
- Clear separation of concerns
- Optimized prompts for specific tasks
- Easier testing and validation

```python
class AgentSpecialization(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    REVIEWER = "reviewer"
    ORCHESTRATOR = "orchestrator"

class Agent:
    def __init__(
        self, 
        specialization: AgentSpecialization,
        llm_provider: LLMProvider,
        prompt_library: PromptLibrary
    ):
        self.specialization = specialization
        self.llm_provider = llm_provider
        self.prompt_library = prompt_library
        self.correlation_id = str(uuid.uuid4())
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> AgentResult:
        system_prompt = self.prompt_library.get_prompt(
            self.specialization, 
            task_type=context.get("task_type")
        )
        
        enhanced_prompt = self._enhance_prompt(task, context)
        
        result = await self.llm_provider.generate(
            prompt=enhanced_prompt,
            system_prompt=system_prompt
        )
        
        return AgentResult(
            agent_type=self.specialization,
            task=task,
            result=result,
            correlation_id=self.correlation_id,
            metadata=context
        )
```

### File System and Code Management

#### Secure File Operations
**Choice**: Sandboxed file system with path validation
**Rationale**:
- Prevent path traversal attacks
- Isolate agent outputs
- Enable easy cleanup and rollback

```python
import os
from pathlib import Path
from typing import Dict, List

class SecureFileManager:
    def __init__(self, base_path: str = "/tmp/mcp_outputs"):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def validate_path(self, file_path: str) -> Path:
        """Ensure path is within allowed directory"""
        full_path = (self.base_path / file_path).resolve()
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Path {file_path} is outside allowed directory")
        return full_path
    
    async def write_agent_output(
        self, 
        agent_type: str, 
        file_path: str, 
        content: str,
        correlation_id: str
    ) -> str:
        agent_dir = self.base_path / correlation_id / agent_type
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        safe_path = self.validate_path(f"{correlation_id}/{agent_type}/{file_path}")
        
        async with aiofiles.open(safe_path, 'w') as f:
            await f.write(content)
        
        logger.info(
            "file_written",
            agent_type=agent_type,
            file_path=str(safe_path),
            correlation_id=correlation_id
        )
        
        return str(safe_path)
```

#### Code Generation Templates
**Choice**: Structured templates with dependency management
**Rationale**:
- Consistent project structure
- Proper dependency declarations
- Easy containerization

```python
class ProjectTemplate:
    def __init__(self):
        self.templates = {
            "docker-compose.yml": self._docker_compose_template,
            "backend/requirements.txt": self._backend_requirements,
            "frontend/package.json": self._frontend_package_json,
            ".env.example": self._env_template
        }
    
    def _docker_compose_template(self) -> str:
        return """
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
"""

    def generate_project_structure(self, correlation_id: str) -> Dict[str, str]:
        """Generate complete project structure"""
        structure = {}
        for file_path, template_func in self.templates.items():
            structure[file_path] = template_func()
        return structure
```

### Testing and Quality Assurance

#### Multi-Layer Testing Strategy
**Choice**: Integrated testing pipeline with multiple validation types
**Rationale**:
- Catch different types of issues
- Provide specific feedback for fixes
- Enable automated quality gates

```python
class TestingSuite:
    def __init__(self):
        self.test_runners = {
            "backend_unit": self._run_pytest,
            "backend_security": self._run_bandit,
            "frontend_lint": self._run_eslint,
            "frontend_type": self._run_typescript_check,
            "dependency_security": self._run_safety_check,
            "docker_build": self._test_docker_build
        }
    
    async def run_comprehensive_tests(
        self, 
        project_path: str,
        correlation_id: str
    ) -> TestResults:
        """Run all test suites and aggregate results"""
        results = TestResults(correlation_id=correlation_id)
        
        for test_name, test_runner in self.test_runners.items():
            try:
                test_result = await test_runner(project_path)
                results.add_test_result(test_name, test_result)
                
                logger.info(
                    "test_completed",
                    test_name=test_name,
                    status=test_result.status,
                    correlation_id=correlation_id
                )
            except Exception as e:
                results.add_test_error(test_name, str(e))
                logger.error(
                    "test_failed",
                    test_name=test_name,
                    error=str(e),
                    correlation_id=correlation_id
                )
        
        return results
    
    async def _run_pytest(self, project_path: str) -> TestResult:
        """Run backend unit tests"""
        backend_path = Path(project_path) / "backend"
        if not (backend_path / "tests").exists():
            return TestResult(status="skipped", reason="No tests directory")
        
        result = await asyncio.create_subprocess_exec(
            "python", "-m", "pytest", "--json-report", "--json-report-file=test_results.json",
            cwd=backend_path,
            capture_output=True,
            text=True
        )
        
        stdout, stderr = await result.communicate()
        
        if result.returncode == 0:
            return TestResult(status="passed", output=stdout)
        else:
            return TestResult(status="failed", output=stderr, exit_code=result.returncode)
```

### Self-Healing Architecture

#### Failure Analysis Engine
**Choice**: LLM-powered failure analysis with structured output
**Rationale**:
- Understands complex error messages
- Provides actionable fix suggestions
- Learns from common failure patterns

```python
class FailureAnalyzer:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.analysis_prompt = self._load_analysis_prompt()
    
    async def analyze_failures(
        self, 
        test_results: TestResults,
        source_code: Dict[str, str]
    ) -> AnalysisResult:
        """Analyze test failures and generate fix suggestions"""
        
        failure_context = self._build_failure_context(test_results, source_code)
        
        analysis_response = await self.llm_provider.generate(
            prompt=failure_context,
            system_prompt=self.analysis_prompt,
            temperature=0.1  # Low temperature for consistency
        )
        
        try:
            # Parse structured response
            analysis = json.loads(analysis_response)
            return AnalysisResult(
                root_causes=analysis["root_causes"],
                fix_suggestions=analysis["fix_suggestions"],
                confidence_score=analysis["confidence_score"],
                estimated_complexity=analysis["estimated_complexity"]
            )
        except json.JSONDecodeError:
            # Fallback to unstructured analysis
            return AnalysisResult(
                root_causes=["Parse error in analysis"],
                fix_suggestions=[analysis_response],
                confidence_score=0.5,
                estimated_complexity="unknown"
            )
    
    def _load_analysis_prompt(self) -> str:
        return """
You are an expert software engineer analyzing test failures and code issues.

Your task is to:
1. Identify the root cause of failures
2. Suggest specific, actionable fixes
3. Provide confidence scores for your analysis

Response format (JSON):
{
    "root_causes": ["cause1", "cause2"],
    "fix_suggestions": [
        {
            "file": "path/to/file",
            "line_number": 42,
            "current_code": "broken code",
            "fixed_code": "corrected code",
            "explanation": "why this fixes the issue"
        }
    ],
    "confidence_score": 0.9,
    "estimated_complexity": "low|medium|high"
}
"""
```

#### Fix Application Engine
**Choice**: Targeted code patching with validation
**Rationale**:
- Precise fixes without breaking working code
- Validation before applying changes
- Rollback capability for failed fixes

```python
class FixApplicator:
    def __init__(self, file_manager: SecureFileManager):
        self.file_manager = file_manager
    
    async def apply_fixes(
        self, 
        fixes: List[FixSuggestion], 
        project_path: str,
        correlation_id: str
    ) -> FixApplicationResult:
        """Apply fixes with backup and validation"""
        
        # Create backup
        backup_path = await self._create_backup(project_path, correlation_id)
        
        applied_fixes = []
        failed_fixes = []
        
        for fix in fixes:
            try:
                await self._apply_single_fix(fix, project_path)
                applied_fixes.append(fix)
                
                logger.info(
                    "fix_applied",
                    file=fix.file,
                    line=fix.line_number,
                    correlation_id=correlation_id
                )
            except Exception as e:
                failed_fixes.append((fix, str(e)))
                logger.error(
                    "fix_failed",
                    file=fix.file,
                    error=str(e),
                    correlation_id=correlation_id
                )
        
        return FixApplicationResult(
            applied_fixes=applied_fixes,
            failed_fixes=failed_fixes,
            backup_path=backup_path
        )
    
    async def _apply_single_fix(self, fix: FixSuggestion, project_path: str):
        """Apply a single fix to a file"""
        file_path = Path(project_path) / fix.file
        
        # Read current content
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        lines = content.split('\n')
        
        # Validate line exists and matches expected content
        if fix.line_number <= len(lines):
            current_line = lines[fix.line_number - 1]
            if fix.current_code.strip() in current_line:
                # Apply fix
                lines[fix.line_number - 1] = current_line.replace(
                    fix.current_code, 
                    fix.fixed_code
                )
                
                # Write back
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write('\n'.join(lines))
            else:
                raise ValueError(f"Expected code not found at line {fix.line_number}")
        else:
            raise ValueError(f"Line {fix.line_number} does not exist in file")
```

## 🔒 Security Architecture

### Authentication Flow
1. **Client Registration**: MCP client registers with Descope using Dynamic Client Registration
2. **Token Request**: Client requests access token with specific scopes
3. **Token Validation**: Every MCP tool call validates JWT and checks scopes
4. **Request Logging**: All interactions logged through Cequence Gateway
5. **Scope Enforcement**: Tools reject requests without required permissions

### Authorization Scopes
```python
SCOPE_DEFINITIONS = {
    "tools:ping": "Basic connectivity testing",
    "tools:generate": "Code generation and project creation",
    "tools:review": "Testing and quality analysis",
    "tools:fix": "Automated code correction",
    "tools:deploy": "Project deployment and management",
    "admin:logs": "Access to system logs and monitoring",
    "admin:config": "Modify system configuration"
}
```

### Data Protection
- **Input Sanitization**: All user inputs validated and sanitized
- **Output Filtering**: Generated code scanned for secrets and vulnerabilities
- **Path Traversal Protection**: All file operations sandboxed
- **Resource Limits**: Memory and CPU limits for agent operations

## 📊 Performance Considerations

### Async Operations
- All LLM calls are asynchronous to prevent blocking
- File operations use async I/O for better throughput
- Testing operations run in parallel where possible

### Caching Strategy
```python
from functools import lru_cache
import redis

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    async def cache_prompt_result(
        self, 
        prompt_hash: str, 
        result: str, 
        ttl: int = 3600
    ):
        """Cache LLM responses for identical prompts"""
        await self.redis_client.setex(
            f"prompt:{prompt_hash}", 
            ttl, 
            result
        )
    
    async def get_cached_result(self, prompt_hash: str) -> Optional[str]:
        """Retrieve cached LLM response"""
        return await self.redis_client.get(f"prompt:{prompt_hash}")
```

### Resource Management
- **Memory Limits**: 2GB max per agent operation
- **Timeout Limits**: 5 minutes max per generation task
- **Concurrent Limits**: Max 3 agents running simultaneously
- **Storage Limits**: 1GB max project size

## 🚀 Deployment Architecture

### Production Environment
- **Hosting**: Fly.io with auto-scaling enabled
- **Database**: PostgreSQL for persistent state
- **File Storage**: S3-compatible storage for generated projects
- **Monitoring**: Cequence dashboard + custom metrics

### Development Environment
- **Local Testing**: Docker Compose for full stack
- **Mock Services**: Local LLM proxy for development
- **Test Database**: SQLite for rapid iteration

---

**Next Steps**: Proceed to `02-environment-setup.md` for detailed development environment configuration and initial project scaffolding.