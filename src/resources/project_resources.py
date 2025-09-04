"""
MCP resources for project data access
"""
import json
import psutil
from typing import Dict, Any, List
from datetime import datetime
from fastapi import Request

from src.core.tool_registry import mcp_resource
from src.core.file_manager import SecureFileManager, ProjectManager
import structlog

logger = structlog.get_logger()


@mcp_resource(
    uri="project://*/structure",
    name="Project Structure",
    description="Get complete project file structure and organization",
    mime_type="application/json"
)
async def project_structure_resource(request: Request) -> Dict[str, Any]:
    """
    Provide project structure information as MCP resource
    """
    # Extract project ID from URI
    uri_parts = request.url.path.split('/')
    project_id = uri_parts[-2] if len(uri_parts) >= 2 else None
    
    if not project_id:
        raise ValueError("Project ID not found in URI")
    
    try:
        project_manager = ProjectManager()
        structure = await project_manager.get_project_structure(project_id)
        
        logger.info(
            "project_structure_accessed",
            project_id=project_id,
            file_count=structure.get("file_count", 0)
        )
        
        return {
            "uri": f"project://{project_id}/structure",
            "mimeType": "application/json",
            "text": json.dumps(structure, indent=2)
        }
        
    except Exception as e:
        logger.error(
            "project_structure_access_failed",
            project_id=project_id,
            error=str(e)
        )
        
        return {
            "uri": f"project://{project_id}/structure",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }


@mcp_resource(
    uri="project://*/code/*",
    name="Project Code Files", 
    description="Access individual code files within projects",
    mime_type="text/plain"
)
async def project_code_resource(request: Request) -> Dict[str, Any]:
    """
    Provide access to individual project files
    """
    # Parse URI to extract project ID and file path
    uri_parts = request.url.path.split('/')
    if len(uri_parts) < 4:
        raise ValueError("Invalid file URI format")
    
    project_id = uri_parts[-3]
    file_path = '/'.join(uri_parts[-2:])
    
    try:
        file_manager = SecureFileManager()
        file_content = await file_manager.read_project_file(project_id, file_path)
        
        logger.info(
            "project_file_accessed",
            project_id=project_id,
            file_path=file_path,
            content_length=len(file_content)
        )
        
        return {
            "uri": f"project://{project_id}/code/{file_path}",
            "mimeType": "text/plain",
            "text": file_content
        }
        
    except Exception as e:
        logger.error(
            "project_file_access_failed",
            project_id=project_id,
            file_path=file_path,
            error=str(e)
        )
        
        return {
            "uri": f"project://{project_id}/code/{file_path}",
            "mimeType": "text/plain",
            "text": f"Error accessing file: {str(e)}"
        }


@mcp_resource(
    uri="project://structure",
    name="Project Structure",
    description="Get complete project file structure and organization",
    mime_type="application/json"
)
async def project_structure_resource_simple(request: Request) -> Dict[str, Any]:
    """
    Provide project structure information as MCP resource (simple URI)
    """
    try:
        project_manager = ProjectManager()
        structure = await project_manager.get_project_structure("default")
        
        logger.info(
            "project_structure_accessed",
            project_id="default",
            file_count=structure.get("file_count", 0)
        )
        
        return {
            "uri": "project://structure",
            "mimeType": "application/json",
            "text": json.dumps(structure, indent=2)
        }
        
    except Exception as e:
        logger.error(
            "project_structure_access_failed",
            project_id="default",
            error=str(e)
        )
        
        return {
            "uri": "project://structure",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "project_id": "default",
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }


@mcp_resource(
    uri="project://files/src/main.py",
    name="Main Project File", 
    description="Access main project file",
    mime_type="text/plain"
)
async def project_main_file_resource(request: Request) -> Dict[str, Any]:
    """
    Provide access to main project file
    """
    try:
        file_manager = SecureFileManager()
        file_content = await file_manager.read_project_file("default", "src/main.py")
        
        logger.info(
            "project_file_accessed",
            project_id="default",
            file_path="src/main.py",
            content_length=len(file_content)
        )
        
        return {
            "uri": "project://files/src/main.py",
            "mimeType": "text/plain",
            "text": file_content
        }
        
    except Exception as e:
        logger.error(
            "project_file_access_failed",
            project_id="default",
            file_path="src/main.py",
            error=str(e)
        )
        
        return {
            "uri": "project://files/src/main.py",
            "mimeType": "text/plain",
            "text": f"Error accessing file: {str(e)}"
        }


@mcp_resource(
    uri="system://metrics",
    name="System Metrics",
    description="Real-time system performance and usage metrics",
    mime_type="application/json"
)
async def system_metrics_resource(request: Request) -> Dict[str, Any]:
    """
    Provide real-time system metrics
    """
    try:
        # Collect system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        project_manager = ProjectManager()
        active_projects = await project_manager.get_active_project_count()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_performance": {
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
            "application_metrics": {
                "active_projects": active_projects,
                "generation_queue_size": 0,  # TODO: Implement queue monitoring
                "server_status": "healthy"
            },
            "network_stats": dict(psutil.net_io_counters()._asdict()) if hasattr(psutil, 'net_io_counters') else {}
        }
        
        logger.debug(
            "system_metrics_accessed",
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            active_projects=active_projects
        )
        
        return {
            "uri": "system://metrics",
            "mimeType": "application/json", 
            "text": json.dumps(metrics, indent=2)
        }
        
    except Exception as e:
        logger.error("system_metrics_access_failed", error=str(e))
        
        return {
            "uri": "system://metrics",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }


@mcp_resource(
    uri="server://capabilities",
    name="MCP Server Capabilities",
    description="Complete list of MCP server capabilities and tools",
    mime_type="application/json"
)
async def server_capabilities_resource(request: Request) -> Dict[str, Any]:
    """
    Provide comprehensive MCP server capabilities
    """
    try:
        from src.core.mcp_server import get_mcp_server
        
        mcp_server = get_mcp_server()
        
        tools_info = []
        for name, tool_func in mcp_server.tools.items():
            if hasattr(tool_func, '_mcp_tool_info'):
                tool_info = tool_func._mcp_tool_info
                required_scopes = getattr(tool_func, '_required_scopes', [])
                
                tools_info.append({
                    "name": name,
                    "description": tool_info.description,
                    "required_scopes": required_scopes,
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
        
        capabilities = {
            "server_info": {
                "name": mcp_server.server_info.name,
                "version": mcp_server.server_info.version,
                "protocol_version": "2024-11-05"
            },
            "capabilities": {
                "tools": {
                    "count": len(tools_info),
                    "tools": tools_info
                },
                "resources": {
                    "count": len(resources_info),
                    "resources": resources_info
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(
            "server_capabilities_accessed",
            tools_count=len(tools_info),
            resources_count=len(resources_info)
        )
        
        return {
            "uri": "server://capabilities",
            "mimeType": "application/json",
            "text": json.dumps(capabilities, indent=2)
        }
        
    except Exception as e:
        logger.error("server_capabilities_access_failed", error=str(e))
        
        return {
            "uri": "server://capabilities",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }


@mcp_resource(
    uri="mcp://capabilities",
    name="MCP Server Capabilities",
    description="Complete list of MCP server capabilities and tools",
    mime_type="application/json"
)
async def mcp_capabilities_resource(request: Request) -> Dict[str, Any]:
    """
    Provide comprehensive MCP server capabilities
    """
    try:
        from src.core.mcp_server import get_mcp_server
        
        mcp_server = get_mcp_server()
        
        tools_info = []
        for name, tool_func in mcp_server.tools.items():
            if hasattr(tool_func, '_mcp_tool_info'):
                tool_info = tool_func._mcp_tool_info
                required_scopes = getattr(tool_func, '_required_scopes', [])
                
                tools_info.append({
                    "name": name,
                    "description": tool_info.description,
                    "required_scopes": required_scopes,
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
        
        capabilities = {
            "server_info": {
                "name": mcp_server.server_info.name,
                "version": mcp_server.server_info.version,
                "protocol_version": "2024-11-05"
            },
            "capabilities": {
                "tools": {
                    "count": len(tools_info),
                    "tools": tools_info
                },
                "resources": {
                    "count": len(resources_info),
                    "resources": resources_info
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(
            "mcp_capabilities_accessed",
            tools_count=len(tools_info),
            resources_count=len(resources_info)
        )
        
        return {
            "uri": "mcp://capabilities",
            "mimeType": "application/json",
            "text": json.dumps(capabilities, indent=2)
        }
        
    except Exception as e:
        logger.error("mcp_capabilities_access_failed", error=str(e))
        
        return {
            "uri": "mcp://capabilities",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }


@mcp_resource(
    uri="analytics://dashboard",
    name="Analytics Dashboard Data",
    description="Real-time analytics data for dashboard visualization",
    mime_type="application/json"
)
async def analytics_dashboard_resource(request: Request) -> Dict[str, Any]:
    """
    Provide real-time analytics data for dashboard
    """
    try:
        # This would integrate with actual Cequence analytics in production
        # For now, providing simulated dashboard data
        
        analytics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "real_time_metrics": {
                "active_requests": 8,
                "requests_per_minute": 34,
                "average_response_time_ms": 187,
                "success_rate": 99.2,
                "active_agents": {
                    "infrastructure": 1,
                    "generator": 2,
                    "reviewer": 1,
                    "tester": 1
                }
            },
            "security_status": {
                "threat_level": "low",
                "blocked_requests": 0,
                "rate_limited_requests": 1,
                "authentication_failures": 0,
                "security_events_last_hour": 1
            },
            "generation_stats": {
                "total_projects_generated": 89,
                "successful_generations": 85,
                "self_healing_events": 12,
                "average_generation_time_seconds": 38,
                "code_reviews_completed": 67,
                "tests_generated": 892
            },
            "system_health": {
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 1),
                "uptime_hours": 24.5  # Simulated
            }
        }
        
        logger.debug("analytics_dashboard_accessed")
        
        return {
            "uri": "analytics://dashboard",
            "mimeType": "application/json",
            "text": json.dumps(analytics_data, indent=2)
        }
        
    except Exception as e:
        logger.error("analytics_dashboard_access_failed", error=str(e))
        
        return {
            "uri": "analytics://dashboard",
            "mimeType": "application/json",
            "text": json.dumps({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
        }