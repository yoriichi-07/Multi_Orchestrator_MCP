"""
Core infrastructure tools for MCP server
"""
import asyncio
import uuid
import time
import platform
import psutil
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.core.tool_registry import mcp_tool, AnalyticsTracker
from src.core.descope_auth import AuthContext
from src.core.mcp_server import get_mcp_server
import structlog

logger = structlog.get_logger()


@mcp_tool(
    name="ping",
    description="Test connectivity and basic server health",
    required_scopes=["tools:ping"]
)
async def ping_tool(auth_context: AuthContext, request=None) -> Dict[str, Any]:
    """
    Basic connectivity test with comprehensive system info
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        result = {
            "status": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "server_info": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            },
            "authentication": {
                "user_id": auth_context.user_id,
                "is_machine": auth_context.is_machine,
                "scopes": auth_context.scopes,
                "time_until_expiry": str(auth_context.time_until_expiry())
            },
            "correlation_id": correlation_id
        }
        
        await tracker.track_operation(
            operation_type="ping",
            agent_type="infrastructure",
            success=True,
            metadata={
                "user_id": auth_context.user_id,
                "memory_gb": result["server_info"]["memory_gb"]
            }
        )
        
        logger.info(
            "ping_successful",
            user_id=auth_context.user_id,
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="ping",
            agent_type="infrastructure",
            success=False,
            metadata={"error": str(e)}
        )
        raise


@mcp_tool(
    name="system_status",
    description="Get comprehensive system status and performance metrics",
    required_scopes=["tools:ping"]
)
async def system_status_tool(auth_context: AuthContext, request=None) -> Dict[str, Any]:
    """
    Detailed system status for monitoring and debugging
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        mcp_server = get_mcp_server()
        
        result = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 1)
                }
            },
            "mcp_metrics": {
                "active_tools": len(mcp_server.tools),
                "active_resources": len(mcp_server.resources),
                "server_uptime": "unknown"  # TODO: Implement uptime tracking
            },
            "auth_info": {
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes
            },
            "correlation_id": correlation_id
        }
        
        await tracker.track_operation(
            operation_type="system_status",
            agent_type="infrastructure",
            success=True,
            metadata={
                "user_id": auth_context.user_id,
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "active_tools": len(mcp_server.tools)
            }
        )
        
        logger.info(
            "system_status_retrieved",
            user_id=auth_context.user_id,
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="system_status",
            agent_type="infrastructure",
            success=False,
            metadata={"error": str(e)}
        )
        raise


@mcp_tool(
    name="list_capabilities",
    description="List all available MCP tools and their capabilities",
    required_scopes=["tools:ping"]
)
async def list_capabilities_tool(auth_context: AuthContext, request=None) -> Dict[str, Any]:
    """
    Return comprehensive list of server capabilities
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        mcp_server = get_mcp_server()
        
        tools_info = []
        for name, tool_func in mcp_server.tools.items():
            if hasattr(tool_func, '_mcp_tool_info'):
                tool_info = tool_func._mcp_tool_info
                required_scopes = getattr(tool_func, '_required_scopes', [])
                
                # Check if user can access this tool
                can_access = all(scope in auth_context.scopes for scope in required_scopes)
                
                tools_info.append({
                    "name": name,
                    "description": tool_info.description,
                    "required_scopes": required_scopes,
                    "accessible": can_access,
                    "input_schema": tool_info.inputSchema
                })
        
        resources_info = []
        for uri, resource_func in mcp_server.resources.items():
            if hasattr(resource_func, '_mcp_resource_info'):
                resource_info = resource_func._mcp_resource_info
                resources_info.append({
                    "uri": uri,
                    "name": resource_info.name,
                    "description": resource_info.description,
                    "mime_type": resource_info.mimeType
                })
        
        result = {
            "server_capabilities": {
                "name": mcp_server.server_info.name,
                "version": mcp_server.server_info.version,
                "protocol_version": "2024-11-05"
            },
            "available_tools": tools_info,
            "available_resources": resources_info,
            "user_access": {
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes,
                "accessible_tools": sum(1 for tool in tools_info if tool["accessible"]),
                "total_tools": len(tools_info)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }
        
        await tracker.track_operation(
            operation_type="list_capabilities",
            agent_type="infrastructure",
            success=True,
            metadata={
                "user_id": auth_context.user_id,
                "total_tools": len(tools_info),
                "accessible_tools": result["user_access"]["accessible_tools"],
                "total_resources": len(resources_info)
            }
        )
        
        logger.info(
            "capabilities_listed",
            user_id=auth_context.user_id,
            total_tools=len(tools_info),
            accessible_tools=result["user_access"]["accessible_tools"],
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="list_capabilities",
            agent_type="infrastructure",
            success=False,
            metadata={"error": str(e)}
        )
        raise


@mcp_tool(
    name="server_metrics",
    description="Get real-time server performance and usage metrics",
    required_scopes=["admin:metrics"]
)
async def server_metrics_tool(auth_context: AuthContext, request=None) -> Dict[str, Any]:
    """
    Advanced server metrics for administrators
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    try:
        # Get detailed system metrics
        cpu_stats = psutil.cpu_stats()
        network_stats = psutil.net_io_counters()
        process = psutil.Process()
        
        result = {
            "performance_metrics": {
                "cpu": {
                    "usage_percent": psutil.cpu_percent(interval=0.1),
                    "per_core": psutil.cpu_percent(percpu=True),
                    "context_switches": cpu_stats.ctx_switches,
                    "interrupts": cpu_stats.interrupts
                },
                "memory": {
                    "process_memory_mb": round(process.memory_info().rss / (1024 * 1024), 2),
                    "process_memory_percent": process.memory_percent(),
                    "system_memory": dict(psutil.virtual_memory()._asdict())
                },
                "network": {
                    "bytes_sent": network_stats.bytes_sent,
                    "bytes_recv": network_stats.bytes_recv,
                    "packets_sent": network_stats.packets_sent,
                    "packets_recv": network_stats.packets_recv
                },
                "process": {
                    "pid": process.pid,
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections())
                }
            },
            "mcp_statistics": {
                "total_tools": len(get_mcp_server().tools),
                "total_resources": len(get_mcp_server().resources),
                "server_version": get_mcp_server().server_info.version
            },
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }
        
        await tracker.track_operation(
            operation_type="server_metrics",
            agent_type="infrastructure",
            success=True,
            metadata={
                "user_id": auth_context.user_id,
                "process_memory_mb": result["performance_metrics"]["memory"]["process_memory_mb"],
                "cpu_percent": result["performance_metrics"]["cpu"]["usage_percent"]
            }
        )
        
        logger.info(
            "server_metrics_retrieved",
            user_id=auth_context.user_id,
            correlation_id=correlation_id
        )
        
        return result
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="server_metrics",
            agent_type="infrastructure",
            success=False,
            metadata={"error": str(e)}
        )
        raise