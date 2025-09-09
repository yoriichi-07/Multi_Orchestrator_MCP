"""
Multi-Agent Orchestrator MCP Server - Smithery Compatible
FastMCP Server with HTTP transport for Smithery deployment

This server provides:
- Multi-agent orchestration capabilities 
- Self-healing code generation
- Descope Access Key authentication with Bearer tokens
- Analytics integration with Cequence AI Gateway
- Full MCP protocol compliance with HTTP transport
"""

import os
import sys
import json
import asyncio
import structlog
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Import core components
from src.core.config import settings
from src.core.auth import AuthenticationMiddleware # Using the correct consolidated middleware
from src.core.descope_auth import get_descope_client, AuthContext, TokenValidationError
from src.core.cequence_integration import get_cequence_analytics, track_agent_operation, CequenceMiddleware
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


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to inject correlation IDs for request tracking"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID if not present
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["x-correlation-id"] = correlation_id
        
        return response


# Note: AuthenticationMiddleware is now imported from src.core.auth
# Scope validation is handled by the consolidated middleware

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
        
        # Execute orchestration using the correct method
        result = await orchestrator.generate_complete_application(
            description=task_description,
            project_type=task_type,
            technology_stack=None,  # Could be enhanced to parse from task_description
            user_context={
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        return {
            "success": result.get("success", False),
            "task_id": result.get("project_id"),
            "status": "completed" if result.get("success") else "failed",
            "agents_used": result.get("agents_used", []),
            "execution_time": result.get("total_duration_seconds"),
            "output": {
                "project_id": result.get("project_id"),
                "generation_timestamp": result.get("generation_timestamp"),
                "task_breakdown": result.get("task_breakdown"),
                "execution_summary": result.get("execution_summary"),
                "files_generated": result.get("files_generated", []),
                "recommendations": result.get("recommendations", [])
            },
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
    """List all available capabilities and agent types including advanced upgrades"""
    return {
        "standard_agents": {
            "frontend": "React, Vue, Angular, UI/UX development",
            "backend": "APIs, databases, server-side logic",
            "devops": "CI/CD, infrastructure, deployment",
            "quality": "Testing, code review, validation"
        },
        "advanced_agents": {
            "autonomous_architect": "Dynamic strategy generation with self-improving DAG execution",
            "proactive_quality": "Policy-as-code quality framework with auto-remediation",
            "evolutionary_prompt": "Self-improving AI communication with performance optimization", 
            "last_mile_cloud": "Autonomous deployment with intelligent verification and rollback"
        },
        "enterprise_features": {
            "autonomous_intelligence": "Self-learning and self-improving AI agents",
            "proactive_automation": "Predictive problem prevention and resolution",
            "evolutionary_optimization": "Continuous self-improvement across all systems",
            "last_mile_automation": "Complete end-to-end autonomous deployment"
        },
        "standard_features": {
            "orchestration": "Multi-agent task coordination",
            "self_healing": "Automatic error detection and fixing",
            "authentication": "Descope Access Key authentication",
            "analytics": "Real-time monitoring with Cequence"
        },
        "advanced_tools": [
            "advanced_generate_application - Enterprise application generation",
            "autonomous_architect - Dynamic system design",
            "proactive_quality_assurance - Policy-driven quality framework",
            "evolutionary_prompt_optimization - Self-improving AI communication",
            "last_mile_cloud_deployment - Autonomous deployment & verification"
        ],
        "supported_tasks": [
            "Enterprise application development",
            "Autonomous system architecture",
            "Self-improving code quality",
            "Evolutionary AI optimization",
            "Last-mile cloud deployment",
            "Web application development",
            "API design and implementation", 
            "Database schema design",
            "Testing strategy creation",
            "Deployment automation",
            "Code review and optimization"
        ],
        "innovation_level": "Enterprise Advanced",
        "ai_sophistication": "Autonomous Self-Improving"
    }

@mcp.tool()
async def get_system_status() -> Dict[str, Any]:
    """Get current system status and health metrics"""
    try:
        # Check orchestrator status
        orchestrator_status = await orchestrator.get_status()
        
        # Get advanced status
        advanced_status = await orchestrator.advanced_get_status()
        
        # Check authentication status
        auth_status = "enabled" if settings.descope_project_id else "disabled"
        
        # Check analytics status
        analytics_status = "enabled" if settings.cequence_gateway_id else "disabled"
        
        return {
            "server": "healthy",
            "orchestrator": orchestrator_status,
            "advanced_agents": advanced_status,
            "authentication": auth_status,
            "analytics": analytics_status,
            "agents_available": orchestrator.available_agents,
            "healing_enabled": bool(code_fixer),
            "enterprise_capabilities": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("status_check_failed", error=str(e))
        return {
            "server": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@mcp.tool()
async def advanced_generate_application(
    description: str,
    complexity_level: str = "advanced",
    innovation_requirements: List[str] = None,
    deployment_strategy: str = "cloud-native"
) -> Dict[str, Any]:
    """
    Enterprise application generation using advanced AI agents
    
    Args:
        description: Detailed description of the application to build
        complexity_level: Target complexity (simple, advanced, enterprise, professional)
        innovation_requirements: List of innovative features to include
        deployment_strategy: Deployment approach (local, cloud-native, multi-cloud, edge)
    """
    try:
        # Track the advanced operation
        if settings.cequence_gateway_id:
            await track_agent_operation("advanced_generate_application", {
                "complexity_level": complexity_level,
                "deployment_strategy": deployment_strategy,
                "innovation_count": len(innovation_requirements or [])
            })
        
        # Execute advanced orchestration
        result = await orchestrator.advanced_generate_application(
            description=description,
            complexity_level=complexity_level,
            innovation_requirements=innovation_requirements or [],
            deployment_strategy=deployment_strategy
        )
        
        return {
            "success": result.get("success", False),
            "enterprise_features": result.get("enterprise_features", []),
            "autonomous_architecture": result.get("autonomous_architecture"),
            "proactive_quality_policies": result.get("proactive_quality_policies"),
            "evolutionary_prompts": result.get("evolutionary_prompts"),
            "cloud_deployment_plan": result.get("cloud_deployment_plan"),
            "execution_timeline": result.get("execution_timeline"),
            "innovation_score": result.get("innovation_score", 0),
            "advanced_agents_used": result.get("advanced_agents_used", []),
            "self_improvement_suggestions": result.get("self_improvement_suggestions", []),
            "future_evolution_path": result.get("future_evolution_path")
        }
        
    except Exception as e:
        logger.error("advanced_generation_failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "standard_fallback": "Standard orchestration available"
        }

@mcp.tool()
async def autonomous_architect(
    project_goals: List[str],
    constraints: List[str] = None,
    learning_objectives: List[str] = None
) -> Dict[str, Any]:
    """
    Activate the Autonomous Architect Agent for dynamic system design
    
    Args:
        project_goals: List of high-level project objectives
        constraints: Technical, business, or resource constraints
        learning_objectives: Areas where the agent should learn and improve
    """
    try:
        # Use the orchestrator's architect agent
        from src.agents.orchestrator import AgentOrchestrator
        orchestrator_instance = AgentOrchestrator()
        
        # Access the architect agent directly
        architect = orchestrator_instance.architect_agent
        
        # Generate autonomous architecture
        result = await architect.generate_execution_strategy(
            goals=project_goals,
            constraints=constraints or [],
            context={
                "learning_objectives": learning_objectives or [],
                "autonomous_mode": True
            }
        )
        
        return {
            "success": True,
            "execution_dag": result.get("execution_dag"),
            "autonomous_strategy": result.get("strategy"),
            "learning_insights": result.get("learning_insights"),
            "dynamic_adaptations": result.get("adaptations"),
            "self_improvement_plan": result.get("self_improvement"),
            "confidence_score": result.get("confidence", 0.85)
        }
        
    except Exception as e:
        logger.error("autonomous_architect_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def proactive_quality_assurance(
    code_context: str,
    quality_standards: List[str] = None,
    auto_remediation: bool = True
) -> Dict[str, Any]:
    """
    Activate proactive quality framework with policy-as-code
    
    Args:
        code_context: Code or project context to analyze
        quality_standards: Custom quality policies to apply
        auto_remediation: Whether to automatically fix violations
    """
    try:
        # Use the orchestrator's quality agent
        orchestrator_instance = AgentOrchestrator()
        quality_agent = orchestrator_instance.quality_agent
        
        # Run proactive quality analysis
        result = await quality_agent.analyze_and_improve(
            context=code_context,
            policies=quality_standards or [],
            auto_fix=auto_remediation
        )
        
        return {
            "success": True,
            "quality_score": result.get("quality_score"),
            "policy_violations": result.get("violations"),
            "auto_remediations": result.get("remediations"),
            "quality_improvements": result.get("improvements"),
            "dynamic_policies": result.get("dynamic_policies"),
            "prevention_strategies": result.get("prevention")
        }
        
    except Exception as e:
        logger.error("proactive_quality_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def evolutionary_prompt_optimization(
    base_prompt: str,
    optimization_goals: List[str] = None,
    performance_metrics: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Activate evolutionary prompt engine for self-improving AI communication
    
    Args:
        base_prompt: Initial prompt to optimize
        optimization_goals: Specific areas to improve (clarity, effectiveness, etc.)
        performance_metrics: Current performance data for optimization
    """
    try:
        # Use the orchestrator's prompt engine
        orchestrator_instance = AgentOrchestrator()
        prompt_engine = orchestrator_instance.prompt_engine
        
        # Create and optimize prompt
        template = await prompt_engine.create_template(
            name="user_optimization",
            base_content=base_prompt,
            optimization_goals=optimization_goals or []
        )
        
        # Evolve the prompt
        result = await prompt_engine.evolve_template(
            template_name="user_optimization",
            performance_data=performance_metrics or {}
        )
        
        return {
            "success": True,
            "optimized_prompt": result.get("optimized_content"),
            "evolution_history": result.get("evolution_history"),
            "performance_improvements": result.get("improvements"),
            "learning_insights": result.get("insights"),
            "adaptation_strategies": result.get("strategies")
        }
        
    except Exception as e:
        logger.error("evolutionary_prompt_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def last_mile_cloud_deployment(
    application_context: str,
    target_environments: List[str] = None,
    verification_requirements: List[str] = None
) -> Dict[str, Any]:
    """
    Activate Last Mile Cloud Agent for autonomous deployment and verification
    
    Args:
        application_context: Application details and requirements
        target_environments: Target deployment environments
        verification_requirements: Custom verification criteria
    """
    try:
        # Use the orchestrator's cloud agent
        orchestrator_instance = AgentOrchestrator()
        cloud_agent = orchestrator_instance.cloud_agent
        
        # Plan and execute deployment
        result = await cloud_agent.plan_deployment(
            context=application_context,
            environments=target_environments or ["production"],
            verification_criteria=verification_requirements or []
        )
        
        return {
            "success": True,
            "deployment_plan": result.get("deployment_plan"),
            "environment_strategies": result.get("environment_strategies"),
            "verification_results": result.get("verification_results"),
            "rollback_plan": result.get("rollback_plan"),
            "monitoring_setup": result.get("monitoring"),
            "autonomous_optimizations": result.get("optimizations")
        }
        
    except Exception as e:
        logger.error("last_mile_deployment_failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def debug_server_config() -> Dict[str, Any]:
    """
    🔧 TEMPORARY DEBUG TOOL - No authentication required
    
    This tool bypasses authentication to help diagnose server-side configuration issues.
    Returns environment variables and configuration status for troubleshooting.
    
    ⚠️ Remove this tool after debugging is complete!
    """
    try:
        # Get environment variables that are critical for authentication
        descope_project_id = os.environ.get("DESCOPE_PROJECT_ID")
        descope_mgmt_key = os.environ.get("DESCOPE_MANAGEMENT_KEY")
        cequence_gateway_id = os.environ.get("CEQUENCE_GATEWAY_ID")
        cequence_api_key = os.environ.get("CEQUENCE_API_KEY")
        
        # Check if settings are loaded
        settings_project_id = getattr(settings, 'descope_project_id', None)
        settings_mgmt_key = getattr(settings, 'descope_management_key', None)
        
        # Try to get Descope client status
        descope_client_status = "unknown"
        try:
            descope_client = get_descope_client()
            descope_client_status = "initialized" if descope_client else "failed"
        except Exception as e:
            descope_client_status = f"error: {str(e)}"
        
        debug_info = {
            "status": "debug_info_retrieved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment_variables": {
                "DESCOPE_PROJECT_ID": {
                    "is_set": descope_project_id is not None,
                    "value_preview": descope_project_id[:8] + "..." if descope_project_id and len(descope_project_id) > 8 else descope_project_id,
                    "length": len(descope_project_id) if descope_project_id else 0
                },
                "DESCOPE_MANAGEMENT_KEY": {
                    "is_set": descope_mgmt_key is not None,
                    "length": len(descope_mgmt_key) if descope_mgmt_key else 0
                },
                "CEQUENCE_GATEWAY_ID": {
                    "is_set": cequence_gateway_id is not None,
                    "value": cequence_gateway_id  # This one is safe to show
                },
                "CEQUENCE_API_KEY": {
                    "is_set": cequence_api_key is not None,
                    "length": len(cequence_api_key) if cequence_api_key else 0
                }
            },
            "settings_object": {
                "descope_project_id": {
                    "is_set": settings_project_id is not None,
                    "matches_env": settings_project_id == descope_project_id
                },
                "descope_management_key": {
                    "is_set": settings_mgmt_key is not None,
                    "matches_env": settings_mgmt_key == descope_mgmt_key
                }
            },
            "descope_client_status": descope_client_status,
            "server_info": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "deployment_platform": "smithery" if "smithery" in os.environ.get("HOSTNAME", "").lower() else "unknown"
            }
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "status": "debug_error",
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

@mcp.prompt("revolutionary-development")
async def revolutionary_development_prompt(
    project_vision: str,
    innovation_level: str = "revolutionary",
    target_impact: str = "industry-changing"
) -> str:
    """Generate a revolutionary development strategy using legendary agents"""
    return f"""# Revolutionary Development Strategy

## Project Vision: {project_vision}

### Innovation Level: {innovation_level}
### Target Impact: {target_impact}

### Legendary AI Agent Orchestration

I'll coordinate our revolutionary AI agents to deliver unprecedented results:

## 🤖 Autonomous Architect Agent
- **Dynamic Strategy Generation**: Creates self-adapting execution plans
- **Goal Analysis**: Breaks down complex objectives into intelligent DAGs
- **Self-Improvement**: Learns from each project to enhance future performance

## 🛡️ Proactive Quality Agent  
- **Policy-as-Code**: Implements dynamic quality frameworks
- **Auto-Remediation**: Fixes issues before they become problems
- **Continuous Improvement**: Evolves quality standards based on project outcomes

## 🧬 Evolutionary Prompt Engine
- **Self-Optimizing Communication**: AI-to-AI communication that improves over time
- **Performance Tracking**: Monitors and optimizes all AI interactions
- **Adaptive Learning**: Evolves prompts based on success metrics

## ☁️ Last Mile Cloud Agent
- **Autonomous Deployment**: Handles complete deployment pipeline
- **Intelligent Verification**: Validates deployments with AI-driven testing
- **Rollback Strategies**: Implements smart rollback with learning integration

### Revolutionary Execution Plan

Use the `legendary_generate_application` tool with:
- Description: "{project_vision}"
- Complexity level: "{innovation_level}"
- Innovation requirements: ["autonomous-ai", "self-improving", "predictive-automation"]
- Deployment strategy: "revolutionary-cloud-native"

This will activate all legendary agents working in concert to deliver a solution that demonstrates the future of autonomous software engineering.

### Expected Revolutionary Outcomes
- ✨ Self-improving AI architecture
- 🔮 Predictive problem prevention
- 🚀 Autonomous deployment pipeline
- 🎯 Industry-leading innovation
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

### Revolutionary Enhancement Available
For advanced quality assurance, use `proactive_quality_assurance` with:
- Code context: Your code
- Quality standards: Custom policies
- Auto remediation: true

This activates our Proactive Quality Agent for policy-driven analysis and automatic improvements.
"""

def main():
    """Main entry point for Smithery deployment with enhanced error handling"""
    try:
        print("Multi-Agent Orchestrator MCP Server starting... v3.0.1")
        print("Configuration Status:")
        print(f"   • Descope Project ID: {'Set' if settings.descope_project_id else 'Not set'}")
        print(f"   • Descope Management Key: {'Set' if settings.descope_management_key else 'Not set'}")
        print(f"   • Demo Mode: {'Enabled' if settings.descope_demo_mode else 'Disabled'}")
        print(f"   • Cequence Gateway: {'Set' if settings.cequence_gateway_id else 'Not set'}")
        
        # Get port from environment (Smithery deployment)
        port = int(os.environ.get("PORT", 8080))
        print(f"Server will start on port {port}")
        
        # Create FastMCP app with streamable-http transport for Smithery  
        mcp_app = mcp.http_app(transport="streamable-http")  # No path - will be handled by mounting
        
        # Create parent Starlette app with proper lifespan handling
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route, Mount
        
        async def health_check(request):
            """Health check endpoint for Smithery with detailed authentication status"""
            try:
                # Get authentication initialization status
                from src.core.descope_auth import get_initialization_error
                auth_init_error = get_initialization_error()
                
                # Try to get Descope client status
                auth_client_status = "unknown"
                demo_mode_active = settings.descope_demo_mode
                try:
                    descope_client = await get_descope_client()
                    auth_client_status = "initialized" if descope_client else "failed"
                except Exception as e:
                    auth_client_status = f"error: {str(e)}"
                
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "3.0.1",
                    "server": "Multi-Agent Orchestrator MCP",
                    "port": port,
                    "authentication": {
                        "configured": bool(settings.descope_project_id),
                        "client_status": auth_client_status,
                        "demo_mode": demo_mode_active,
                        "initialization_error": auth_init_error,
                        "middleware_enabled": bool(settings.descope_project_id)
                    },
                    "mcp_endpoints": {
                        "discovery_accessible": True,  # Always true with our robust middleware
                        "tool_execution_requires_auth": bool(settings.descope_project_id) and auth_client_status == "initialized"
                    },
                    "environment": {
                        "descope_project_id_set": bool(os.environ.get("DESCOPE_PROJECT_ID")),
                        "descope_management_key_set": bool(os.environ.get("DESCOPE_MANAGEMENT_KEY")),
                        "deployment_platform": "smithery" if "smithery" in os.environ.get("HOSTNAME", "").lower() else "unknown"
                    }
                }
                
                return JSONResponse(health_data)
                
            except Exception as e:
                return JSONResponse({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": "Health check failed but MCP discovery endpoints should still work"
                }, status_code=500)
        
        # Create the main Starlette app with FastMCP lifespan
        app = Starlette(
            routes=[
                Route("/health", health_check, methods=["GET"]),
                Mount("/", app=mcp_app),  # Mount MCP app at root - it has its own /mcp path
            ],
            lifespan=mcp_app.lifespan,  # CRITICAL: Pass FastMCP lifespan for proper initialization
        )
        
        # Add middleware stack (order matters - reverse of execution order)
        
        # 1. CORS middleware (outermost) - handles preflight requests
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "*", 
                "authorization", 
                "content-type",
                "x-correlation-id",
                "mcp-session-id", 
                "mcp-protocol-version"
            ],
            expose_headers=[
                "x-correlation-id", 
                "mcp-session-id", 
                "mcp-protocol-version"
            ],
            max_age=86400,
        )
        
        # 2. Cequence Analytics middleware (if configured)
        if settings.cequence_gateway_id and settings.cequence_api_key:
            app.add_middleware(
                CequenceMiddleware,
                gateway_id=settings.cequence_gateway_id,
                api_key=settings.cequence_api_key
            )
            print("Cequence analytics middleware enabled")
        else:
            print("Cequence analytics not configured")
        
        # 3. Authentication middleware (ALWAYS added, but with graceful degradation)
        app.add_middleware(AuthenticationMiddleware)
        if settings.descope_project_id:
            print("Descope authentication middleware enabled (with graceful fallback)")
        else:
            print("Authentication middleware enabled in passthrough mode")
        
        # 4. Correlation middleware (innermost) - tracks requests
        app.add_middleware(CorrelationMiddleware)
        
        print(f"Starting HTTP server on 0.0.0.0:{port}")
        print("MCP Discovery endpoints are ALWAYS accessible for Smithery scanning")
        print("Tool execution will require authentication if credentials are configured")
        
        # Run the server
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
    except Exception as startup_error:
        print(f"CRITICAL SERVER STARTUP FAILURE: {startup_error}")
        print("This should not happen with the robust error handling implemented!")
        print("Check your environment variables and system configuration.")
        # Log the error but don't crash completely
        logger.critical("server_startup_failed", error=str(startup_error))
        
        # Try to start a minimal server for debugging
        try:
            print("Attempting emergency startup for debugging...")
            import uvicorn
            from starlette.applications import Starlette
            from starlette.responses import JSONResponse
            from starlette.routing import Route
            
            async def emergency_health(request):
                return JSONResponse({
                    "status": "emergency_mode",
                    "error": str(startup_error),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": "Server started in emergency mode for debugging"
                })
            
            emergency_app = Starlette(routes=[Route("/health", emergency_health, methods=["GET"])])
            port = int(os.environ.get("PORT", 8080))
            print(f"Emergency server starting on port {port}")
            uvicorn.run(emergency_app, host="0.0.0.0", port=port, log_level="info")
            
        except Exception as emergency_error:
            print(f"Complete failure: {emergency_error}")
            sys.exit(1)

# Initialize the server
if __name__ == "__main__":
    logger.info("mcp_server_starting", version="2.0.0", mode="http")
    main()  # Call the main function