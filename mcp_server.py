"""
Multi-Agent Orchestrator MCP Server - Smithery Compatible
FastMCP Server with HTTP transport for Smithery deployment

This server provides:
- Multi-agent orchestration capabilities 
- Self-healing code generation
- OAuth 2.1 + PKCE authentication with Descope
- Analytics integration with Cequence AI Gateway
- Full MCP protocol compliance with HTTP transport
"""

import os
import json
import asyncio
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

# Import core components
from src.core.config import settings
from src.core.descope_auth import get_descope_client
from src.core.cequence_integration import get_cequence_analytics, track_agent_operation
from src.agents.orchestrator import AgentOrchestrator
from src.healing.solution_generator import SolutionGenerator

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
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create the FastMCP server instance
mcp = FastMCP("Multi-Agent Orchestrator MCP")

# Initialize global components
orchestrator = AgentOrchestrator()
code_fixer = SolutionGenerator("mcp-server")

@mcp.tool()
async def ping() -> str:
    """Simple health check ping"""
    return "pong"

@mcp.tool()
async def orchestrate_task(
    task_description: str,
    task_type: str = "development",
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Orchestrate a complex development task using multiple AI agents
    
    Args:
        task_description: Description of the task to be completed
        task_type: Type of task (development, architecture, testing, deployment)
        priority: Task priority (low, normal, high, critical)
    """
    try:
        # Track the operation if analytics enabled
        if settings.cequence_gateway_id:
            await track_agent_operation("orchestrate_task", {
                "task_type": task_type,
                "priority": priority,
                "description_length": len(task_description)
            })
        
        # Execute orchestration
        result = await orchestrator.execute_task({
            "description": task_description,
            "type": task_type,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": True,
            "task_id": result.get("task_id"),
            "status": result.get("status", "completed"),
            "agents_used": result.get("agents_used", []),
            "execution_time": result.get("execution_time"),
            "output": result.get("output"),
            "healing_applied": result.get("healing_applied", False)
        }
        
    except Exception as e:
        logger.error("orchestration_failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "task_type": task_type
        }

@mcp.tool()
async def generate_architecture(
    project_description: str,
    tech_stack: List[str],
    requirements: List[str]
) -> Dict[str, Any]:
    """
    Generate software architecture recommendations
    
    Args:
        project_description: Description of the project
        tech_stack: List of technologies to use
        requirements: List of functional and non-functional requirements
    """
    try:
        result = await orchestrator.generate_architecture({
            "description": project_description,
            "tech_stack": tech_stack,
            "requirements": requirements
        })
        
        return {
            "success": True,
            "architecture": result.get("architecture"),
            "components": result.get("components", []),
            "recommendations": result.get("recommendations", []),
            "estimated_complexity": result.get("complexity", "medium")
        }
        
    except Exception as e:
        logger.error("architecture_generation_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def auto_fix_code(
    code: str,
    error_message: str,
    context: str = ""
) -> Dict[str, Any]:
    """
    Automatically fix code issues using self-healing capabilities
    
    Args:
        code: The code that has issues
        error_message: The error message encountered
        context: Additional context about the code
    """
    try:
        if not code_fixer:
            return {
                "success": False,
                "error": "Self-healing is not enabled"
            }
        
        # Generate a fix
        fix_result = await code_fixer.generate_fix({
            "code": code,
            "error": error_message,
            "context": context
        })
        
        return {
            "success": True,
            "fixed_code": fix_result.get("fixed_code"),
            "explanation": fix_result.get("explanation"),
            "confidence": fix_result.get("confidence", 0.8),
            "changes_made": fix_result.get("changes", [])
        }
        
    except Exception as e:
        logger.error("code_fix_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def list_capabilities() -> Dict[str, Any]:
    """List all available capabilities and agent types"""
    return {
        "agents": {
            "frontend": "React, Vue, Angular, UI/UX development",
            "backend": "APIs, databases, server-side logic",
            "devops": "CI/CD, infrastructure, deployment",
            "quality": "Testing, code review, validation"
        },
        "features": {
            "orchestration": "Multi-agent task coordination",
            "self_healing": "Automatic error detection and fixing",
            "authentication": "OAuth 2.1 + PKCE with Descope",
            "analytics": "Real-time monitoring with Cequence"
        },
        "supported_tasks": [
            "Web application development",
            "API design and implementation", 
            "Database schema design",
            "Testing strategy creation",
            "Deployment automation",
            "Code review and optimization"
        ]
    }

@mcp.tool()
async def get_system_status() -> Dict[str, Any]:
    """Get current system status and health metrics"""
    try:
        # Check orchestrator status
        orchestrator_status = await orchestrator.get_status()
        
        # Check authentication status
        auth_status = "enabled" if settings.descope_project_id else "disabled"
        
        # Check analytics status
        analytics_status = "enabled" if settings.cequence_gateway_id else "disabled"
        
        return {
            "server": "healthy",
            "orchestrator": orchestrator_status,
            "authentication": auth_status,
            "analytics": analytics_status,
            "agents_available": orchestrator.available_agents,
            "healing_enabled": bool(code_fixer),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("status_check_failed", error=str(e))
        return {
            "server": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@mcp.resource("mcp://capabilities")
async def get_capabilities_resource() -> str:
    """Resource containing detailed capability information"""
    capabilities = await list_capabilities()
    return json.dumps(capabilities, indent=2)

@mcp.resource("mcp://analytics")
async def get_analytics_resource() -> str:
    """Resource containing analytics and metrics data"""
    try:
        if settings.cequence_gateway_id:
            analytics = await get_cequence_analytics()
            return json.dumps(analytics, indent=2)
        else:
            return json.dumps({
                "status": "Analytics not configured",
                "message": "Cequence gateway credentials needed"
            }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "Analytics unavailable"
        }, indent=2)

@mcp.resource("mcp://health")
async def get_health_resource() -> str:
    """Resource containing system health information"""
    status = await get_system_status()
    return json.dumps(status, indent=2)

@mcp.prompt("project-setup")
async def project_setup_prompt(
    project_type: str,
    tech_stack: str = "",
    requirements: str = ""
) -> str:
    """Generate a comprehensive project setup guide"""
    return f"""# Project Setup Guide

## Project Type: {project_type}

### Technology Stack
{tech_stack or "Please specify your preferred technologies"}

### Requirements
{requirements or "Please provide your specific requirements"}

### Recommended Architecture

I'll help you set up a {project_type} project with the following approach:

1. **Project Structure**: Create organized directory structure
2. **Dependencies**: Install and configure required packages
3. **Configuration**: Set up environment variables and configs
4. **Development Environment**: Configure development tools
5. **Testing Setup**: Implement testing framework
6. **Deployment Strategy**: Plan deployment pipeline

Use the `orchestrate_task` tool to begin implementation with:
- Task description: "Set up {project_type} project with {tech_stack}"
- Task type: "development"  
- Priority: "normal"

The multi-agent system will coordinate frontend, backend, DevOps, and QA specialists to deliver a complete solution.
"""

@mcp.prompt("code-review")
async def code_review_prompt(
    code: str,
    focus_areas: str = "all"
) -> str:
    """Generate a comprehensive code review"""
    return f"""# Code Review Analysis

## Code to Review:
```
{code}
```

## Focus Areas: {focus_areas}

### Automated Review Process

I'll perform a comprehensive code review covering:

1. **Code Quality**: Structure, readability, maintainability
2. **Security**: Vulnerability scanning and best practices
3. **Performance**: Optimization opportunities
4. **Testing**: Coverage and test quality
5. **Documentation**: Code comments and documentation
6. **Standards**: Coding conventions and style guidelines

Use the `orchestrate_task` tool with:
- Task description: "Perform code review focusing on {focus_areas}"
- Task type: "review"
- Priority: "normal"

The quality assurance agent will provide detailed feedback and improvement suggestions.

### Self-Healing Available
If issues are found, use the `auto_fix_code` tool to automatically apply fixes.
"""

def main():
    """Main entry point for Smithery deployment"""
    print("Multi-Agent Orchestrator MCP Server starting...")
    
    # Get port from environment (Smithery sets PORT=8081)
    port = int(os.environ.get("PORT", 8080))
    
    # Create Starlette app with MCP HTTP transport
    app = mcp.http_app()
    
    # Add CORS middleware for cross-origin requests (required for MCP)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
        max_age=86400,
    )
    
    print(f"Starting HTTP server on port {port}")
    
    # Run the server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

# Initialize the server
if __name__ == "__main__":
    logger.info("mcp_server_starting", version="2.0.0", mode="http")
    main()