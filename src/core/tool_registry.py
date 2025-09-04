"""
MCP tool registration and management system
"""
import inspect
import asyncio
import time
from typing import Dict, Any, List, Optional, get_type_hints
from functools import wraps
import structlog

from src.core.mcp_server import get_mcp_server
from src.middleware.auth_middleware import require_scopes

logger = structlog.get_logger()


def mcp_tool(
    name: str,
    description: str,
    required_scopes: Optional[List[str]] = None,
    timeout_seconds: int = 300
):
    """
    Decorator to register function as MCP tool with automatic schema generation
    
    Args:
        name: Tool name for MCP protocol
        description: Human-readable tool description
        required_scopes: Required OAuth scopes for authorization
        timeout_seconds: Maximum execution time
    """
    def decorator(func):
        # Generate JSON schema from function signature
        input_schema = _generate_input_schema(func)
        
        # Create wrapper with authentication and error handling
        @wraps(func)
        async def wrapper(request, **kwargs):
            # Apply scope-based authorization if required
            if required_scopes:
                auth_dependency = require_scopes(*required_scopes)
                auth_context = await auth_dependency(request)
                kwargs['auth_context'] = auth_context
            
            # Add request context
            kwargs['request'] = request
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    func(**kwargs),
                    timeout=timeout_seconds
                )
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"Tool '{name}' timed out after {timeout_seconds} seconds")
        
        # Try to register with MCP server if available
        try:
            mcp_server = get_mcp_server()
            mcp_server.register_tool(
                name=name,
                description=description,
                input_schema=input_schema,
                required_scopes=required_scopes
            )(wrapper)
        except RuntimeError:
            # MCP server not initialized yet, store registration info for later
            wrapper._mcp_registration = {
                'name': name,
                'description': description,
                'input_schema': input_schema,
                'required_scopes': required_scopes
            }
            # Store the tool globally for later registration
            if not hasattr(mcp_tool, '_deferred_tools'):
                mcp_tool._deferred_tools = {}
            mcp_tool._deferred_tools[name] = wrapper
        
        return wrapper
    
    return decorator


def register_deferred_tools():
    """Register tools that were decorated before MCP server was initialized"""
    if hasattr(mcp_tool, '_deferred_tools'):
        mcp_server = get_mcp_server()
        for name, tool_func in mcp_tool._deferred_tools.items():
            reg_info = tool_func._mcp_registration
            mcp_server.register_tool(
                name=reg_info['name'],
                description=reg_info['description'],
                input_schema=reg_info['input_schema'],
                required_scopes=reg_info['required_scopes']
            )(tool_func)
        
        # Clear the deferred tools
        mcp_tool._deferred_tools.clear()


def mcp_resource(
    uri: str,
    name: str,
    description: str,
    mime_type: str = "application/json"
):
    """Decorator to register function as MCP resource"""
    def decorator(func):
        try:
            mcp_server = get_mcp_server()
            mcp_server.register_resource(
                uri=uri,
                name=name,
                description=description,
                mime_type=mime_type
            )(func)
        except RuntimeError:
            # MCP server not initialized yet, store registration info for later
            func._mcp_resource_registration = {
                'uri': uri,
                'name': name,
                'description': description,
                'mime_type': mime_type
            }
            # Store the resource globally for later registration
            if not hasattr(mcp_resource, '_deferred_resources'):
                mcp_resource._deferred_resources = {}
            mcp_resource._deferred_resources[uri] = func
        
        return func
    return decorator


def register_deferred_resources():
    """Register resources that were decorated before MCP server was initialized"""
    if hasattr(mcp_resource, '_deferred_resources'):
        mcp_server = get_mcp_server()
        for uri, resource_func in mcp_resource._deferred_resources.items():
            reg_info = resource_func._mcp_resource_registration
            mcp_server.register_resource(
                uri=reg_info['uri'],
                name=reg_info['name'],
                description=reg_info['description'],
                mime_type=reg_info['mime_type']
            )(resource_func)
        
        # Clear the deferred resources
        mcp_resource._deferred_resources.clear()


def _generate_input_schema(func) -> Dict[str, Any]:
    """Generate JSON schema from function signature"""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        # Skip special parameters
        if param_name in ['request', 'auth_context']:
            continue
        
        param_type = type_hints.get(param_name, str)
        schema_type = _python_type_to_json_schema(param_type)
        
        properties[param_name] = {
            "type": schema_type["type"],
            "description": f"Parameter {param_name}"
        }
        
        # Add additional schema properties
        if "format" in schema_type:
            properties[param_name]["format"] = schema_type["format"]
        if "items" in schema_type:
            properties[param_name]["items"] = schema_type["items"]
        
        # Check if parameter is required
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def _python_type_to_json_schema(python_type) -> Dict[str, Any]:
    """Convert Python type hints to JSON schema types"""
    if python_type == str:
        return {"type": "string"}
    elif python_type == int:
        return {"type": "integer"}
    elif python_type == float:
        return {"type": "number"}
    elif python_type == bool:
        return {"type": "boolean"}
    elif hasattr(python_type, '__origin__'):
        # Handle generic types like List[str], Dict[str, Any]
        origin = python_type.__origin__
        if origin == list:
            args = getattr(python_type, '__args__', ())
            item_type = args[0] if args else str
            return {
                "type": "array",
                "items": _python_type_to_json_schema(item_type)
            }
        elif origin == dict:
            return {"type": "object"}
    
    # Default to string for unknown types
    return {"type": "string"}


class AnalyticsTracker:
    """Helper class for tracking tool operations with Cequence integration"""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.start_time = time.time()
    
    async def track_operation(
        self,
        operation_type: str,
        agent_type: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track an operation with Cequence analytics"""
        try:
            from src.core.cequence_integration import track_agent_operation
            
            duration_ms = (time.time() - self.start_time) * 1000
            
            await track_agent_operation(
                operation_type=operation_type,
                agent_type=agent_type,
                correlation_id=self.correlation_id,
                duration_ms=duration_ms,
                success=success,
                metadata=metadata or {}
            )
        except ImportError:
            # Graceful degradation if Cequence integration is not available
            logger.debug(
                "operation_tracked_locally",
                operation_type=operation_type,
                agent_type=agent_type,
                success=success,
                correlation_id=self.correlation_id
            )
    
    async def track_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        client_ip: str,
        user_id: Optional[str] = None
    ):
        """Track a security event"""
        try:
            from src.core.cequence_integration import track_security_event
            
            await track_security_event(
                event_type=event_type,
                severity=severity,
                description=description,
                correlation_id=self.correlation_id,
                client_ip=client_ip,
                user_id=user_id
            )
        except ImportError:
            # Graceful degradation
            logger.warning(
                "security_event_tracked_locally",
                event_type=event_type,
                severity=severity,
                correlation_id=self.correlation_id
            )