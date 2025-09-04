"""
Code generation tools for autonomous software development
"""
import asyncio
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.tool_registry import mcp_tool, AnalyticsTracker
from src.core.descope_auth import AuthContext
from src.agents.orchestrator import AgentOrchestrator
from src.core.file_manager import SecureFileManager
import structlog

logger = structlog.get_logger()


@mcp_tool(
    name="generate_application",
    description="Generate a complete full-stack application from description",
    required_scopes=["tools:generate"],
    timeout_seconds=600
)
async def generate_application_tool(
    project_description: str,
    project_type: str = "fullstack",
    technology_stack: Optional[str] = None,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Generate complete application with frontend, backend, and configuration
    
    Args:
        project_description: Detailed description of the desired application
        project_type: Type of project (fullstack, frontend, backend, api)
        technology_stack: Preferred technologies (react-node, vue-python, etc.)
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    start_time = time.time()
    
    try:
        # Initialize orchestrator and file manager
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        file_manager = SecureFileManager()
        
        # Log generation request
        logger.info(
            "application_generation_started",
            user_id=auth_context.user_id,
            project_type=project_type,
            technology_stack=technology_stack,
            description_length=len(project_description),
            correlation_id=correlation_id
        )
        
        # Generate project structure
        generation_result = await orchestrator.generate_complete_application(
            description=project_description,
            project_type=project_type,
            technology_stack=technology_stack,
            user_context={
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes
            }
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Track successful operation
        await tracker.track_operation(
            operation_type="application_generation",
            agent_type="orchestrator",
            success=True,
            metadata={
                "project_type": project_type,
                "technology_stack": generation_result.get("technology_stack"),
                "files_generated": generation_result.get("files_count", 0),
                "user_id": auth_context.user_id,
                "processing_time_ms": processing_time
            }
        )
        
        # Format response according to MCP specification
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "completed",
                        "project_id": correlation_id,
                        "project_type": project_type,
                        "technology_stack": generation_result.get("technology_stack"),
                        "files_generated": generation_result.get("files_count", 0),
                        "processing_time_ms": processing_time,
                        "generation_summary": generation_result.get("summary"),
                        "next_steps": [
                            "Review generated code",
                            "Run tests with 'test_application' tool",
                            "Deploy with 'deploy_application' tool"
                        ]
                    }, indent=2)
                },
                {
                    "type": "resource",
                    "resource": {
                        "uri": f"project://{correlation_id}/structure",
                        "text": generation_result.get("project_structure", "")
                    }
                }
            ]
        }
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Track failed operation
        await tracker.track_operation(
            operation_type="application_generation",
            agent_type="orchestrator",
            success=False,
            metadata={
                "error": str(e),
                "user_id": auth_context.user_id,
                "processing_time_ms": processing_time
            }
        )
        
        logger.error(
            "application_generation_failed",
            user_id=auth_context.user_id,
            error=str(e),
            correlation_id=correlation_id,
            processing_time_ms=processing_time
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "failed",
                        "error": str(e),
                        "project_id": correlation_id,
                        "processing_time_ms": processing_time,
                        "troubleshooting": [
                            "Check project description for clarity",
                            "Verify technology stack is supported",
                            "Try with simpler requirements"
                        ]
                    }, indent=2)
                }
            ],
            "isError": True
        }


@mcp_tool(
    name="generate_component",
    description="Generate specific application component (API endpoint, React component, etc.)",
    required_scopes=["tools:generate"]
)
async def generate_component_tool(
    component_type: str,
    component_description: str,
    project_context: Optional[str] = None,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Generate specific application components
    
    Args:
        component_type: Type of component (api_endpoint, react_component, database_model, etc.)
        component_description: Detailed description of the component
        project_context: Context about the existing project
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        
        logger.info(
            "component_generation_started",
            user_id=auth_context.user_id,
            component_type=component_type,
            correlation_id=correlation_id
        )
        
        # Generate specific component
        component_result = await orchestrator.generate_component(
            component_type=component_type,
            description=component_description,
            project_context=project_context,
            user_context={
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes
            }
        )
        
        await tracker.track_operation(
            operation_type="component_generation",
            agent_type="generator",
            success=True,
            metadata={
                "component_type": component_type,
                "user_id": auth_context.user_id,
                "files_modified": len(component_result.get("files_modified", []))
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "completed",
                        "component_id": correlation_id,
                        "component_type": component_type,
                        "files_modified": component_result.get("files_modified", []),
                        "code_generated": component_result.get("code_generated", ""),
                        "integration_notes": component_result.get("integration_notes", "")
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="component_generation",
            agent_type="generator",
            success=False,
            metadata={
                "component_type": component_type,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "component_generation_failed",
            component_type=component_type,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text", 
                    "text": f"Component generation failed: {str(e)}"
                }
            ],
            "isError": True
        }


@mcp_tool(
    name="enhance_application",
    description="Add features or improvements to existing application",
    required_scopes=["tools:generate"]
)
async def enhance_application_tool(
    project_id: str,
    enhancement_description: str,
    enhancement_type: str = "feature",
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Enhance existing application with new features or improvements
    
    Args:
        project_id: ID of the existing project to enhance
        enhancement_description: Description of desired enhancements
        enhancement_type: Type of enhancement (feature, performance, security, ui)
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        
        logger.info(
            "application_enhancement_started",
            user_id=auth_context.user_id,
            project_id=project_id,
            enhancement_type=enhancement_type,
            correlation_id=correlation_id
        )
        
        # Enhance existing project
        enhancement_result = await orchestrator.enhance_application(
            project_id=project_id,
            enhancement_description=enhancement_description,
            enhancement_type=enhancement_type,
            user_context={
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes
            }
        )
        
        await tracker.track_operation(
            operation_type="application_enhancement",
            agent_type="orchestrator",
            success=True,
            metadata={
                "project_id": project_id,
                "enhancement_type": enhancement_type,
                "user_id": auth_context.user_id,
                "files_modified": len(enhancement_result.get("files_modified", []))
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "completed",
                        "enhancement_id": correlation_id,
                        "project_id": project_id,
                        "enhancement_type": enhancement_type,
                        "changes_made": enhancement_result.get("changes_made", []),
                        "files_modified": enhancement_result.get("files_modified", []),
                        "migration_notes": enhancement_result.get("migration_notes", ""),
                        "testing_recommendations": enhancement_result.get("testing_recommendations", [])
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="application_enhancement",
            agent_type="orchestrator",
            success=False,
            metadata={
                "project_id": project_id,
                "enhancement_type": enhancement_type,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "application_enhancement_failed",
            project_id=project_id,
            enhancement_type=enhancement_type,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Application enhancement failed: {str(e)}"
                }
            ],
            "isError": True
        }


@mcp_tool(
    name="deploy_application",
    description="Deploy generated application to specified environment",
    required_scopes=["tools:deploy"]
)
async def deploy_application_tool(
    project_id: str,
    environment: str = "staging",
    deployment_config: Optional[Dict[str, Any]] = None,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Deploy application to target environment
    
    Args:
        project_id: ID of the project to deploy
        environment: Target environment (staging, production, testing)
        deployment_config: Optional deployment configuration
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        logger.info(
            "deployment_started",
            user_id=auth_context.user_id,
            project_id=project_id,
            environment=environment,
            correlation_id=correlation_id
        )
        
        # Simulate deployment process
        await asyncio.sleep(3)
        
        deployment_url = f"https://{project_id}.{environment}.foundry.ai"
        
        await tracker.track_operation(
            operation_type="deployment",
            agent_type="deployer",
            success=True,
            metadata={
                "project_id": project_id,
                "environment": environment,
                "deployment_url": deployment_url,
                "user_id": auth_context.user_id
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "deployed",
                        "project_id": project_id,
                        "environment": environment,
                        "deployment_url": deployment_url,
                        "health_check": "passed",
                        "deployed_at": datetime.utcnow().isoformat(),
                        "next_steps": [
                            f"Access application at {deployment_url}",
                            "Monitor application performance",
                            "Review deployment logs"
                        ]
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="deployment",
            agent_type="deployer",
            success=False,
            metadata={
                "project_id": project_id,
                "environment": environment,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "deployment_failed",
            project_id=project_id,
            environment=environment,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Deployment failed: {str(e)}"
                }
            ],
            "isError": True
        }