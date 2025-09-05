"""
MCP tools for agent orchestrator with healing integration
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from src.core.tool_registry import mcp_tool, AnalyticsTracker
from src.agents.orchestrator import AgentOrchestrator

logger = structlog.get_logger()

# Global orchestrator instance (initialized on first use)
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


@mcp_tool(
    name="generate_application_with_healing",
    description="Generate a complete application with automatic self-healing enabled",
    required_scopes=["orchestration:generate", "healing:monitor"]
)
async def generate_application_with_healing(
    description: str,
    project_type: str = "fullstack",
    technology_stack: Optional[str] = None,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Generate a complete application with self-healing enabled"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = get_orchestrator()
        
        # Generate application with built-in healing
        result = await orchestrator.generate_complete_application(
            description=description,
            project_type=project_type,
            technology_stack=technology_stack,
            user_context={"enable_healing": True}
        )
        
        await tracker.track_operation(
            operation_type="generate_application_with_healing",
            agent_type="orchestrator",
            success=True,
            metadata={
                "project_type": project_type,
                "project_id": result.get("project_id"),
                "healing_enabled": True
            }
        )
        
        return {
            "success": True,
            **result,
            "healing_enabled": True,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="generate_application_with_healing",
            agent_type="orchestrator",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="enable_project_healing",
    description="Enable self-healing monitoring for an existing project",
    required_scopes=["healing:monitor"]
)
async def enable_project_healing(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Enable self-healing for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.enable_healing_for_project(project_id)
        
        await tracker.track_operation(
            operation_type="enable_project_healing",
            agent_type="orchestrator",
            success=result["success"],
            metadata={"project_id": project_id}
        )
        
        return {
            **result,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="enable_project_healing",
            agent_type="orchestrator",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="disable_project_healing",
    description="Disable self-healing monitoring for a project",
    required_scopes=["healing:monitor"]
)
async def disable_project_healing(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Disable self-healing for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.disable_healing_for_project(project_id)
        
        await tracker.track_operation(
            operation_type="disable_project_healing",
            agent_type="orchestrator",
            success=result["success"],
            metadata={"project_id": project_id}
        )
        
        return {
            **result,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="disable_project_healing",
            agent_type="orchestrator",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="get_orchestrator_health_status",
    description="Get health status of a project managed by the orchestrator",
    required_scopes=["healing:read"]
)
async def get_orchestrator_health_status(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Get project health status from orchestrator perspective"""
    correlation_id = str(uuid.uuid4())
    
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.get_project_health_status(project_id)
        
        return {
            "success": True,
            **result,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="trigger_orchestrator_healing",
    description="Manually trigger healing for orchestration issues",
    required_scopes=["healing:heal"]
)
async def trigger_orchestrator_healing(
    project_id: str,
    issue_description: str,
    task_context: Optional[Dict[str, Any]] = None,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Manually trigger healing for orchestration issues"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        from src.healing.health_monitor import HealthIssue, IssueType
        from src.agents.orchestrator import Task, TaskStatus, AgentType
        
        orchestrator = get_orchestrator()
        
        # Create a mock task for the healing trigger
        mock_task = Task(
            id=str(uuid.uuid4()),
            type="manual_healing_trigger",
            description=issue_description,
            agent_type=AgentType.REVIEWER,  # Default to reviewer for manual triggers
            priority=1,
            dependencies=[],
            parameters={"project_id": project_id, **(task_context or {})},
            status=TaskStatus.FAILED,
            error=issue_description
        )
        
        # Trigger healing
        healing_triggered = await orchestrator.trigger_healing_on_failure(
            project_id, mock_task, issue_description
        )
        
        await tracker.track_operation(
            operation_type="trigger_orchestrator_healing",
            agent_type="orchestrator",
            success=healing_triggered,
            metadata={
                "project_id": project_id,
                "healing_triggered": healing_triggered
            }
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "healing_triggered": healing_triggered,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="trigger_orchestrator_healing",
            agent_type="orchestrator",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="get_orchestrator_status",
    description="Get current status of the agent orchestrator system",
    required_scopes=["orchestration:read"]
)
async def get_orchestrator_status(
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Get orchestrator system status"""
    correlation_id = str(uuid.uuid4())
    
    try:
        orchestrator = get_orchestrator()
        
        active_sessions_count = len(orchestrator.active_sessions)
        total_tasks = len(orchestrator.tasks)
        
        # Get healing status for all projects
        healing_projects = {}
        for project_id in orchestrator.project_health_status:
            healing_projects[project_id] = await orchestrator.get_project_health_status(project_id)
        
        return {
            "success": True,
            "orchestrator_status": {
                "active_sessions": active_sessions_count,
                "total_tasks": total_tasks,
                "healing_enabled": orchestrator.healing_enabled,
                "healing_threshold": orchestrator.auto_healing_threshold,
                "projects_with_healing": len(orchestrator.project_health_status),
                "healing_projects": healing_projects
            },
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="configure_healing_settings",
    description="Configure orchestrator healing settings",
    required_scopes=["healing:configure"]
)
async def configure_healing_settings(
    auto_healing_threshold: Optional[int] = None,
    healing_enabled: Optional[bool] = None,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Configure orchestrator healing settings"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        orchestrator = get_orchestrator()
        
        # Update settings
        changes = {}
        if auto_healing_threshold is not None:
            old_threshold = orchestrator.auto_healing_threshold
            orchestrator.auto_healing_threshold = auto_healing_threshold
            changes["auto_healing_threshold"] = {
                "old": old_threshold,
                "new": auto_healing_threshold
            }
        
        if healing_enabled is not None:
            old_enabled = orchestrator.healing_enabled
            orchestrator.healing_enabled = healing_enabled
            changes["healing_enabled"] = {
                "old": old_enabled,
                "new": healing_enabled
            }
        
        await tracker.track_operation(
            operation_type="configure_healing_settings",
            agent_type="orchestrator",
            success=True,
            metadata={"changes": changes}
        )
        
        return {
            "success": True,
            "changes": changes,
            "current_settings": {
                "healing_enabled": orchestrator.healing_enabled,
                "auto_healing_threshold": orchestrator.auto_healing_threshold
            },
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="configure_healing_settings",
            agent_type="orchestrator",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }