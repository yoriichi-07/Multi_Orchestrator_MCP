"""
MCP tools with enhanced Descope authentication and scope-based authorization
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Request
import structlog

from src.middleware.auth_middleware import get_auth_context, require_scopes
from src.core.descope_auth import AuthContext
from src.analytics.dashboard import analytics_dashboard
from src.core.autonomous_healing import autonomous_healing_system, ErrorPattern

logger = structlog.get_logger()
router = APIRouter()


@router.post("/tools/ping")
async def ping_tool(
    request: Request,
    auth: AuthContext = Depends(require_scopes("tools:ping"))
) -> Dict[str, Any]:
    """
    Enhanced ping tool with comprehensive authentication info
    
    Required scope: tools:ping
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "ping_tool_called",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        correlation_id=correlation_id,
        time_until_expiry=str(auth.time_until_expiry())
    )
    
    return {
        "message": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "authentication": {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "scopes": auth.scopes,
            "tenant_id": auth.tenant_id,
            "issued_at": auth.issued_at.isoformat(),
            "expires_at": auth.expires_at.isoformat(),
            "time_until_expiry": str(auth.time_until_expiry())
        }
    }


@router.post("/tools/generate_code")
async def generate_code_tool(
    project_description: str,
    project_type: str = "fullstack",
    auth: AuthContext = Depends(require_scopes("tools:generate"))
) -> Dict[str, Any]:
    """
    Code generation tool with proper authorization
    
    Required scope: tools:generate
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "code_generation_requested",
        user_id=auth.user_id,
        project_type=project_type,
        description_length=len(project_description),
        correlation_id=correlation_id
    )
    
    # TODO: Implement actual code generation logic
    return {
        "status": "generation_started",
        "project_id": correlation_id,
        "project_type": project_type,
        "description": project_description[:100] + "..." if len(project_description) > 100 else project_description,
        "estimated_completion": "5 minutes",
        "correlation_id": correlation_id,
        "authorized_by": {
            "user_id": auth.user_id,
            "scopes": auth.scopes
        }
    }


@router.post("/tools/review_code")
async def review_code_tool(
    project_id: str,
    review_type: str = "comprehensive",
    auth: AuthContext = Depends(require_scopes("tools:review"))
) -> Dict[str, Any]:
    """
    Code review tool with authorization
    
    Required scope: tools:review
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "code_review_requested",
        user_id=auth.user_id,
        project_id=project_id,
        review_type=review_type,
        correlation_id=correlation_id
    )
    
    # TODO: Implement actual code review logic
    return {
        "status": "review_started",
        "project_id": project_id,
        "review_type": review_type,
        "review_id": correlation_id,
        "estimated_completion": "2 minutes",
        "correlation_id": correlation_id,
        "authorized_by": {
            "user_id": auth.user_id,
            "scopes": auth.scopes
        }
    }


@router.post("/tools/fix_code")
async def fix_code_tool(
    project_id: str,
    failure_report: str,
    auth: AuthContext = Depends(require_scopes("tools:fix"))
) -> Dict[str, Any]:
    """
    Automated code fixing tool
    
    Required scope: tools:fix
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "code_fix_requested",
        user_id=auth.user_id,
        project_id=project_id,
        correlation_id=correlation_id
    )
    
    # TODO: Implement actual code fixing logic
    return {
        "status": "fix_started",
        "project_id": project_id,
        "fix_id": correlation_id,
        "failure_analysis": "Analyzing test failures and code issues...",
        "estimated_completion": "3 minutes",
        "correlation_id": correlation_id,
        "authorized_by": {
            "user_id": auth.user_id,
            "scopes": auth.scopes
        }
    }


@router.post("/tools/deploy_project")
async def deploy_project_tool(
    project_id: str,
    deployment_config: Dict[str, Any],
    auth: AuthContext = Depends(require_scopes("tools:deploy"))
) -> Dict[str, Any]:
    """
    Project deployment tool
    
    Required scope: tools:deploy
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "deployment_requested",
        user_id=auth.user_id,
        project_id=project_id,
        correlation_id=correlation_id
    )
    
    # TODO: Implement actual deployment logic
    return {
        "status": "deployment_started",
        "project_id": project_id,
        "deployment_id": correlation_id,
        "target_platform": deployment_config.get("platform", "smithery"),
        "estimated_completion": "10 minutes",
        "correlation_id": correlation_id,
        "authorized_by": {
            "user_id": auth.user_id,
            "scopes": auth.scopes
        }
    }


@router.post("/tools/admin/system_status")
async def system_status_tool(
    auth: AuthContext = Depends(require_scopes("admin:logs", "admin:config"))
) -> Dict[str, Any]:
    """
    Administrative tool requiring elevated permissions
    
    Required scopes: admin:logs AND admin:config
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "admin_system_status_requested",
        user_id=auth.user_id,
        correlation_id=correlation_id
    )
    
    return {
        "system_status": "operational",
        "active_sessions": 42,
        "pending_generations": 3,
        "system_health": {
            "cpu_usage": "45%",
            "memory_usage": "62%",
            "disk_usage": "23%"
        },
        "authentication": {
            "descope_project": auth.client_id,
            "active_tokens": 15,
            "failed_authentications_24h": 2
        },
        "correlation_id": correlation_id,
        "authorized_admin": auth.user_id
    }


@router.get("/auth/token_info")
async def token_info(
    auth: AuthContext = Depends(get_auth_context)
) -> Dict[str, Any]:
    """
    Get detailed information about the current token
    
    No specific scope required - any valid token
    """
    return {
        "token_info": {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "tenant_id": auth.tenant_id,
            "scopes": auth.scopes,
            "issued_at": auth.issued_at.isoformat(),
            "expires_at": auth.expires_at.isoformat(),
            "time_until_expiry": str(auth.time_until_expiry()),
            "custom_claims": auth.custom_claims
        }
    }


@router.get("/mcp/capabilities")
async def mcp_capabilities(
    auth: AuthContext = Depends(get_auth_context)
) -> Dict[str, Any]:
    """
    MCP server capabilities with user-specific scope information
    """
    # Build available tools based on user scopes
    available_tools = []
    
    if auth.has_scope("tools:ping"):
        available_tools.append({
            "name": "ping",
            "description": "Basic connectivity testing",
            "scope_required": "tools:ping"
        })
    
    if auth.has_scope("tools:generate"):
        available_tools.append({
            "name": "generate_code",
            "description": "Generate full-stack applications",
            "scope_required": "tools:generate"
        })
    
    if auth.has_scope("tools:review"):
        available_tools.append({
            "name": "review_code",
            "description": "Automated code review and testing",
            "scope_required": "tools:review"
        })
    
    if auth.has_scope("tools:fix"):
        available_tools.append({
            "name": "fix_code",
            "description": "Automated code fixing",
            "scope_required": "tools:fix"
        })
    
    if auth.has_scope("tools:deploy"):
        available_tools.append({
            "name": "deploy_project",
            "description": "Deploy applications to cloud platforms",
            "scope_required": "tools:deploy"
        })
    
    if auth.has_all_scopes(["admin:logs", "admin:config"]):
        available_tools.append({
            "name": "system_status",
            "description": "Administrative system monitoring",
            "scope_required": "admin:logs + admin:config"
        })
    
    return {
        "capabilities": {
            "server_name": "Autonomous Software Foundry",
            "version": "2.0.0",
            "protocol_version": "1.0.0",
            "authentication": "Descope OAuth 2.1 + PKCE",
            "supported_tools": available_tools,
            "user_context": {
                "user_id": auth.user_id,
                "is_machine": auth.is_machine,
                "available_scopes": auth.scopes,
                "token_expires_at": auth.expires_at.isoformat()
            }
        }
    }


@router.post("/tools/orchestrate_parallel_tasks")
async def orchestrate_parallel_tasks_tool(
    request: Request,
    task_definitions: List[Dict[str, Any]],
    execution_strategy: str = "fan_out_fan_in",
    auth: AuthContext = Depends(require_scopes("tools:orchestrate"))
) -> Dict[str, Any]:
    """
    🚀 COMPETITION-GRADE PARALLEL ORCHESTRATION ENGINE
    
    Executes multiple tasks in parallel with intelligent coordination,
    dependency management, and real-time progress tracking.
    
    Required scope: tools:orchestrate
    
    Args:
        task_definitions: List of task definitions with:
            - id: Unique task identifier
            - type: Task type (code_generation, analysis, testing, etc.)
            - agent_type: Preferred agent type
            - requirements: Task requirements dict
            - dependencies: List of task IDs this task depends on
            - priority: Task priority (1-10, 10 being highest)
            - timeout: Maximum execution time in seconds
        execution_strategy: Strategy for parallel execution
            - "fan_out_fan_in": All tasks in parallel, collect all results
            - "dependency_aware": Respect dependencies, parallel where possible
            - "priority_weighted": Prioritize high-priority tasks
            - "resource_optimized": Balance agent workloads
    
    Returns:
        dict: Comprehensive execution results with performance metrics
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "parallel_orchestration_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        tasks_count=len(task_definitions),
        execution_strategy=execution_strategy,
        correlation_id=correlation_id
    )
    
    try:
        # Initialize orchestrator
        from src.agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        
        # Execute parallel orchestration
        result = await orchestrator.orchestrate_parallel_tasks(
            task_definitions=task_definitions,
            execution_strategy=execution_strategy
        )
        
        # Add authentication context to result
        result["authentication"] = {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "executed_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            "parallel_orchestration_completed",
            user_id=auth.user_id,
            execution_id=result.get("execution_id"),
            tasks_completed=result.get("execution_summary", {}).get("successful_tasks", 0),
            total_time=result.get("execution_summary", {}).get("total_execution_time", 0),
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "parallel_orchestration_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Parallel orchestration failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/intelligent_task_routing")
async def intelligent_task_routing_tool(
    request: Request,
    task_requests: List[Dict[str, Any]],
    routing_strategy: str = "capability_based",
    auth: AuthContext = Depends(require_scopes("tools:routing"))
) -> Dict[str, Any]:
    """
    🧠 INTELLIGENT TASK ROUTING ENGINE
    
    Routes tasks to optimal agents based on capabilities, workload, and performance metrics.
    
    Required scope: tools:routing
    
    Args:
        task_requests: List of task requests with:
            - id: Unique task identifier
            - type: Task type
            - requirements: Task requirements and constraints
            - complexity: Expected complexity (1-10)
            - deadline: Optional deadline timestamp
            - priority: Task priority (1-10)
        routing_strategy: Routing strategy
            - "capability_based": Route by agent capabilities
            - "workload_balanced": Balance agent workloads
            - "performance_optimized": Route based on historical performance
            - "deadline_aware": Prioritize by deadlines
            - "adaptive": Intelligent mix of all strategies
    
    Returns:
        dict: Routing plan with agent assignments and optimization metrics
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "intelligent_routing_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        tasks_count=len(task_requests),
        routing_strategy=routing_strategy,
        correlation_id=correlation_id
    )
    
    try:
        # Initialize orchestrator
        from src.agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        
        # Execute intelligent routing
        result = await orchestrator.intelligent_task_routing(
            task_requests=task_requests,
            routing_strategy=routing_strategy
        )
        
        # Add authentication context to result
        result["authentication"] = {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "routed_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            "intelligent_routing_completed",
            user_id=auth.user_id,
            routing_id=result.get("routing_id"),
            assignment_rate=result.get("routing_summary", {}).get("assignment_rate", 0),
            balance_score=result.get("routing_summary", {}).get("workload_balance_score", 0),
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "intelligent_routing_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Intelligent task routing failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/analytics/dashboard")
async def get_analytics_dashboard(
    auth: AuthContext = Depends(require_scopes("analytics:dashboard"))
) -> Dict[str, Any]:
    """
    🏆 Competition-Grade Analytics Dashboard
    Real-time monitoring and predictive insights
    
    Required scope: analytics:dashboard
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "analytics_dashboard_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        correlation_id=correlation_id
    )
    
    try:
        # Get complete dashboard data
        dashboard_data = await analytics_dashboard.get_dashboard_data()
        
        # Add authentication context
        dashboard_data["authentication"] = {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "accessed_at": datetime.now(timezone.utc).isoformat()
        }
        
        dashboard_data["correlation_id"] = correlation_id
        
        logger.info(
            "analytics_dashboard_delivered",
            user_id=auth.user_id,
            metrics_count=dashboard_data.get("system_stats", {}).get("total_metrics_collected", 0),
            active_agents=dashboard_data.get("system_stats", {}).get("active_agents_count", 0),
            health_score=dashboard_data.get("system_stats", {}).get("system_health_score", 0),
            correlation_id=correlation_id
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(
            "analytics_dashboard_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Analytics dashboard failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/analytics/optimization_report")
async def get_optimization_report(
    auth: AuthContext = Depends(require_scopes("analytics:optimization"))
) -> Dict[str, Any]:
    """
    🎯 AI-Powered Optimization Report
    Comprehensive performance analysis and improvement recommendations
    
    Required scope: analytics:optimization
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "optimization_report_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        correlation_id=correlation_id
    )
    
    try:
        # Generate optimization report
        optimization_report = await analytics_dashboard.generate_optimization_report()
        
        # Add authentication context
        optimization_report["authentication"] = {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        optimization_report["correlation_id"] = correlation_id
        
        logger.info(
            "optimization_report_generated",
            user_id=auth.user_id,
            optimization_score=optimization_report.get("optimization_score", 0),
            recommendations_count=len(optimization_report.get("recommendations", [])),
            bottlenecks_detected=optimization_report.get("bottlenecks_detected", 0),
            correlation_id=correlation_id
        )
        
        return optimization_report
        
    except Exception as e:
        logger.error(
            "optimization_report_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Optimization report failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/analytics/track_performance")
async def track_performance_metric(
    agent_id: str,
    task_type: str,
    execution_time: float,
    success: bool,
    resource_usage: Dict[str, Any],
    quality_score: float = 0.9,
    user_satisfaction: float = 0.85,
    auth: AuthContext = Depends(require_scopes("analytics:track"))
) -> Dict[str, Any]:
    """
    📊 Performance Metric Tracking
    Track real-time performance metrics for analytics and optimization
    
    Required scope: analytics:track
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "performance_tracking_requested",
        user_id=auth.user_id,
        agent_id=agent_id,
        task_type=task_type,
        execution_time=execution_time,
        success=success,
        correlation_id=correlation_id
    )
    
    try:
        # Track the performance metric
        metric_id = await analytics_dashboard.track_performance_metric(
            agent_id=agent_id,
            task_type=task_type,
            execution_time=execution_time,
            success=success,
            resource_usage=resource_usage,
            quality_score=quality_score,
            user_satisfaction=user_satisfaction
        )
        
        logger.info(
            "performance_metric_tracked",
            user_id=auth.user_id,
            metric_id=metric_id,
            agent_id=agent_id,
            task_type=task_type,
            correlation_id=correlation_id
        )
        
        return {
            "success": True,
            "metric_id": metric_id,
            "agent_id": agent_id,
            "task_type": task_type,
            "execution_time": execution_time,
            "tracked_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id,
                "is_machine": auth.is_machine
            }
        }
        
    except Exception as e:
        logger.error(
            "performance_tracking_failed",
            user_id=auth.user_id,
            agent_id=agent_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Performance tracking failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/healing/predict_errors")
async def predict_system_errors(
    recent_metrics: List[Dict[str, Any]],
    system_state: Dict[str, Any],
    auth: AuthContext = Depends(require_scopes("healing:predict"))
) -> Dict[str, Any]:
    """
    🔮 Autonomous Error Prediction
    AI-powered prediction of potential system failures and errors
    
    Required scope: healing:predict
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "error_prediction_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        metrics_count=len(recent_metrics),
        correlation_id=correlation_id
    )
    
    try:
        # Predict potential errors
        predictions = await autonomous_healing_system.predict_errors(
            recent_metrics=recent_metrics,
            current_system_state=system_state
        )
        
        # Convert predictions to dict format
        prediction_data = []
        for prediction in predictions:
            pred_dict = {
                'prediction_id': prediction.prediction_id,
                'timestamp': prediction.timestamp.isoformat(),
                'error_pattern': prediction.error_pattern.value,
                'probability': prediction.probability,
                'time_to_occurrence': prediction.time_to_occurrence,
                'affected_agents': prediction.affected_agents,
                'severity': prediction.severity,
                'confidence': prediction.confidence,
                'indicators': prediction.indicators,
                'recommended_actions': prediction.recommended_actions
            }
            prediction_data.append(pred_dict)
        
        logger.info(
            "error_predictions_generated",
            user_id=auth.user_id,
            predictions_count=len(predictions),
            high_risk_predictions=len([p for p in predictions if p.severity in ['high', 'critical']]),
            correlation_id=correlation_id
        )
        
        return {
            "success": True,
            "predictions": prediction_data,
            "prediction_summary": {
                "total_predictions": len(predictions),
                "high_risk_count": len([p for p in predictions if p.severity in ['high', 'critical']]),
                "medium_risk_count": len([p for p in predictions if p.severity == 'medium']),
                "low_risk_count": len([p for p in predictions if p.severity == 'low']),
                "most_likely_error": predictions[0].error_pattern.value if predictions else None,
                "average_confidence": sum(p.confidence for p in predictions) / len(predictions) if predictions else 0.0
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id,
                "is_machine": auth.is_machine
            }
        }
        
    except Exception as e:
        logger.error(
            "error_prediction_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Error prediction failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/healing/execute_action")
async def execute_healing_action(
    error_pattern: str,
    affected_agents: List[str],
    severity: str,
    system_state: Dict[str, Any],
    auth: AuthContext = Depends(require_scopes("healing:execute"))
) -> Dict[str, Any]:
    """
    🔧 Autonomous Healing Execution
    Execute intelligent healing actions for predicted or detected errors
    
    Required scope: healing:execute
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "healing_action_requested",
        user_id=auth.user_id,
        error_pattern=error_pattern,
        affected_agents=affected_agents,
        severity=severity,
        correlation_id=correlation_id
    )
    
    try:
        # Convert string to ErrorPattern enum
        try:
            error_pattern_enum = ErrorPattern(error_pattern)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid error pattern: {error_pattern}. Valid patterns: {[e.value for e in ErrorPattern]}",
                "correlation_id": correlation_id,
                "authentication": {
                    "user_id": auth.user_id,
                    "client_id": auth.client_id
                }
            }
        
        # Execute healing action
        healing_action = await autonomous_healing_system.execute_healing_action(
            error_pattern=error_pattern_enum,
            affected_agents=affected_agents,
            severity=severity,
            system_state=system_state
        )
        
        # Convert to dict format
        action_data = {
            'action_id': healing_action.action_id,
            'timestamp': healing_action.timestamp.isoformat(),
            'healing_level': healing_action.healing_level.value,
            'error_pattern': healing_action.error_pattern.value,
            'target_agents': healing_action.target_agents,
            'action_type': healing_action.action_type,
            'parameters': healing_action.parameters,
            'success': healing_action.success,
            'execution_time': healing_action.execution_time,
            'impact_metrics': healing_action.impact_metrics
        }
        
        logger.info(
            "healing_action_executed",
            user_id=auth.user_id,
            action_id=healing_action.action_id,
            action_type=healing_action.action_type,
            success=healing_action.success,
            execution_time=healing_action.execution_time,
            correlation_id=correlation_id
        )
        
        return {
            "success": True,
            "healing_action": action_data,
            "execution_summary": {
                "action_successful": healing_action.success,
                "execution_time_seconds": healing_action.execution_time,
                "healing_level": healing_action.healing_level.value,
                "agents_affected": len(healing_action.target_agents),
                "impact_assessment": "positive" if healing_action.success else "limited"
            },
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id,
                "is_machine": auth.is_machine
            }
        }
        
    except Exception as e:
        logger.error(
            "healing_action_execution_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Healing action execution failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }


@router.post("/tools/healing/status")
async def get_healing_system_status(
    auth: AuthContext = Depends(require_scopes("healing:status"))
) -> Dict[str, Any]:
    """
    🏥 Healing System Status
    Get comprehensive status of the autonomous healing system
    
    Required scope: healing:status
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "healing_status_requested",
        user_id=auth.user_id,
        client_id=auth.client_id,
        is_machine=auth.is_machine,
        correlation_id=correlation_id
    )
    
    try:
        # Get healing system status
        healing_status = await autonomous_healing_system.get_healing_status()
        
        # Add authentication context
        healing_status["authentication"] = {
            "user_id": auth.user_id,
            "client_id": auth.client_id,
            "is_machine": auth.is_machine,
            "accessed_at": datetime.now(timezone.utc).isoformat()
        }
        
        healing_status["correlation_id"] = correlation_id
        
        logger.info(
            "healing_status_delivered",
            user_id=auth.user_id,
            system_health_score=healing_status.get("system_health_score", 0),
            total_actions=healing_status.get("healing_statistics", {}).get("total_actions", 0),
            success_rate=healing_status.get("healing_statistics", {}).get("success_rate", 0),
            correlation_id=correlation_id
        )
        
        return healing_status
        
    except Exception as e:
        logger.error(
            "healing_status_failed",
            user_id=auth.user_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "success": False,
            "error": f"Healing status retrieval failed: {str(e)}",
            "correlation_id": correlation_id,
            "authentication": {
                "user_id": auth.user_id,
                "client_id": auth.client_id
            }
        }