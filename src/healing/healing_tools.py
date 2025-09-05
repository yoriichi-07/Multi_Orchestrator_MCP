"""
MCP tools for the self-healing loop system
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from src.core.tool_registry import mcp_tool, mcp_resource, AnalyticsTracker
from src.healing.health_monitor import HealthMonitor
from src.healing.error_analyzer import ErrorAnalyzer
from src.healing.solution_generator import SolutionGenerator
from src.healing.healing_loop import HealingLoop

logger = structlog.get_logger()

# Global healing components (initialized on first use)
_health_monitor: Optional[HealthMonitor] = None
_healing_loop: Optional[HealingLoop] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def get_healing_loop() -> HealingLoop:
    """Get or create healing loop instance"""
    global _healing_loop
    if _healing_loop is None:
        _healing_loop = HealingLoop()
    return _healing_loop


@mcp_tool(
    name="start_health_monitoring",
    description="Start continuous health monitoring for a project",
    required_scopes=["healing:monitor"]
)
async def start_health_monitoring(
    project_id: str,
    interval_seconds: int = 60,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Start continuous health monitoring for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        health_monitor = get_health_monitor()
        
        # Start monitoring
        monitor_task = await health_monitor.start_continuous_monitoring(
            project_id=project_id,
            interval_seconds=interval_seconds
        )
        
        await tracker.track_operation(
            operation_type="start_health_monitoring",
            agent_type="health_monitor",
            success=True,
            metadata={
                "project_id": project_id,
                "interval_seconds": interval_seconds
            }
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "monitoring_started": True,
            "interval_seconds": interval_seconds,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="start_health_monitoring",
            agent_type="health_monitor",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="stop_health_monitoring",
    description="Stop health monitoring for a project",
    required_scopes=["healing:monitor"]
)
async def stop_health_monitoring(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Stop health monitoring for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        health_monitor = get_health_monitor()
        
        # Stop monitoring
        await health_monitor.stop_monitoring(project_id)
        
        await tracker.track_operation(
            operation_type="stop_health_monitoring",
            agent_type="health_monitor",
            success=True,
            metadata={"project_id": project_id}
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "monitoring_stopped": True,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="stop_health_monitoring",
            agent_type="health_monitor",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="get_health_status",
    description="Get current health status for a project",
    required_scopes=["healing:read"]
)
async def get_health_status(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Get current health status for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        health_monitor = get_health_monitor()
        
        # Get current health status
        health_report = await health_monitor.get_current_health_status(project_id)
        
        if health_report:
            result = {
                "success": True,
                "project_id": project_id,
                "health_status": health_report.overall_status.value,
                "health_score": health_report.health_score,
                "issues_count": len(health_report.issues),
                "last_check": health_report.timestamp.isoformat(),
                "recommendations": health_report.recommendations,
                "correlation_id": correlation_id
            }
        else:
            result = {
                "success": True,
                "project_id": project_id,
                "health_status": "unknown",
                "health_score": 0.0,
                "issues_count": 0,
                "last_check": None,
                "message": "No health data available",
                "correlation_id": correlation_id
            }
        
        await tracker.track_operation(
            operation_type="get_health_status",
            agent_type="health_monitor",
            success=True,
            metadata={"project_id": project_id}
        )
        
        return result
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="get_health_status",
            agent_type="health_monitor",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="perform_health_check",
    description="Perform immediate comprehensive health check",
    required_scopes=["healing:monitor"]
)
async def perform_health_check(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Perform immediate comprehensive health check"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        health_monitor = get_health_monitor()
        
        # Perform health check
        health_report = await health_monitor.perform_comprehensive_health_check(project_id)
        
        await tracker.track_operation(
            operation_type="perform_health_check",
            agent_type="health_monitor",
            success=True,
            metadata={
                "project_id": project_id,
                "health_score": health_report.health_score,
                "issues_count": len(health_report.issues)
            }
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "health_status": health_report.overall_status.value,
            "health_score": health_report.health_score,
            "issues_count": len(health_report.issues),
            "issues": [
                {
                    "id": issue.id,
                    "type": issue.type.value,
                    "severity": issue.severity,
                    "description": issue.description,
                    "location": issue.location
                }
                for issue in health_report.issues
            ],
            "recommendations": health_report.recommendations,
            "check_timestamp": health_report.timestamp.isoformat(),
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="perform_health_check",
            agent_type="health_monitor",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="start_healing_loop",
    description="Start the self-healing loop for a project",
    required_scopes=["healing:heal"]
)
async def start_healing_loop(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Start the self-healing loop for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        healing_loop = get_healing_loop()
        
        # Start healing loop
        healing_task = await healing_loop.start_healing_loop(project_id)
        
        await tracker.track_operation(
            operation_type="start_healing_loop",
            agent_type="healing_loop",
            success=True,
            metadata={"project_id": project_id}
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "healing_loop_started": True,
            "status": healing_loop.status.value,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="start_healing_loop",
            agent_type="healing_loop",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="stop_healing_loop",
    description="Stop the self-healing loop for a project",
    required_scopes=["healing:heal"]
)
async def stop_healing_loop(
    project_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Stop the self-healing loop for a project"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        healing_loop = get_healing_loop()
        
        # Stop healing loop
        await healing_loop.stop_healing_loop(project_id)
        
        await tracker.track_operation(
            operation_type="stop_healing_loop",
            agent_type="healing_loop",
            success=True,
            metadata={"project_id": project_id}
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "healing_loop_stopped": True,
            "status": healing_loop.status.value,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="stop_healing_loop",
            agent_type="healing_loop",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="trigger_healing_session",
    description="Manually trigger a healing session for an issue",
    required_scopes=["healing:heal"]
)
async def trigger_healing_session(
    project_id: str,
    issue_description: str,
    issue_severity: int = 5,
    error_message: Optional[str] = None,
    stack_trace: Optional[str] = None,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Manually trigger a healing session for an issue"""
    correlation_id = str(uuid.uuid4())
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        from src.healing.health_monitor import HealthIssue, IssueType
        
        healing_loop = get_healing_loop()
        
        # Create a health issue
        trigger_issue = HealthIssue(
            id=str(uuid.uuid4()),
            type=IssueType.RUNTIME_ERROR,
            severity=issue_severity,
            description=issue_description,
            location="manual_trigger",
            error_message=error_message,
            stack_trace=stack_trace,
            first_detected=datetime.utcnow()
        )
        
        # Trigger healing session
        session_id = await healing_loop.trigger_healing_session(project_id, trigger_issue)
        
        await tracker.track_operation(
            operation_type="trigger_healing_session",
            agent_type="healing_loop",
            success=bool(session_id),
            metadata={
                "project_id": project_id,
                "session_id": session_id,
                "issue_severity": issue_severity
            }
        )
        
        if session_id:
            return {
                "success": True,
                "project_id": project_id,
                "session_id": session_id,
                "healing_session_triggered": True,
                "correlation_id": correlation_id
            }
        else:
            return {
                "success": False,
                "project_id": project_id,
                "error": "Failed to trigger healing session (may be at session limit)",
                "correlation_id": correlation_id
            }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="trigger_healing_session",
            agent_type="healing_loop",
            success=False,
            metadata={"error": str(e)}
        )
        
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="get_healing_status",
    description="Get current status of the healing loop system",
    required_scopes=["healing:read"]
)
async def get_healing_status(
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Get current status of the healing loop system"""
    correlation_id = str(uuid.uuid4())
    
    try:
        healing_loop = get_healing_loop()
        status = healing_loop.get_healing_status()
        
        return {
            "success": True,
            **status,
            "correlation_id": correlation_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


@mcp_tool(
    name="get_healing_session_details",
    description="Get details of a specific healing session",
    required_scopes=["healing:read"]
)
async def get_healing_session_details(
    session_id: str,
    request=None,
    auth_context=None
) -> Dict[str, Any]:
    """Get details of a specific healing session"""
    correlation_id = str(uuid.uuid4())
    
    try:
        healing_loop = get_healing_loop()
        session_details = healing_loop.get_session_details(session_id)
        
        if session_details:
            return {
                "success": True,
                "session_details": session_details,
                "correlation_id": correlation_id
            }
        else:
            return {
                "success": False,
                "error": f"Healing session {session_id} not found",
                "correlation_id": correlation_id
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "correlation_id": correlation_id
        }


# MCP Resources for healing system data

@mcp_resource(
    uri="healing://health_trends/{project_id}",
    name="Health Trends",
    description="Historical health trends for a project"
)
async def get_health_trends_resource(project_id: str) -> Dict[str, Any]:
    """Get health trends resource for a project"""
    try:
        health_monitor = get_health_monitor()
        history = health_monitor.get_health_history(project_id, limit=50)
        
        return {
            "project_id": project_id,
            "health_history": [
                {
                    "timestamp": report.timestamp.isoformat(),
                    "health_status": report.overall_status.value,
                    "health_score": report.health_score,
                    "issues_count": len(report.issues)
                }
                for report in history
            ],
            "total_reports": len(history)
        }
    except Exception as e:
        return {
            "error": str(e),
            "project_id": project_id
        }


@mcp_resource(
    uri="healing://system_metrics",
    name="Healing System Metrics",
    description="Overall healing system performance metrics"
)
async def get_healing_metrics_resource() -> Dict[str, Any]:
    """Get healing system metrics resource"""
    try:
        healing_loop = get_healing_loop()
        status = healing_loop.get_healing_status()
        
        # Add additional metrics
        analytics_data = status.get("learning_data", {})
        
        return {
            "system_status": status["status"],
            "active_sessions": status["active_sessions"],
            "completed_sessions": status["completed_sessions"],
            "performance_metrics": {
                "total_sessions": analytics_data.get("total_sessions", 0),
                "success_rate": analytics_data.get("success_rate", 0.0),
                "average_healing_time": analytics_data.get("average_healing_time", 0.0),
                "common_failure_reasons": analytics_data.get("common_failure_reasons", {}),
                "most_effective_solutions": analytics_data.get("most_effective_solutions", {})
            },
            "last_updated": analytics_data.get("last_updated", datetime.utcnow().isoformat())
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }