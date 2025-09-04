"""
Core MCP server implementation with full protocol compliance
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core.config import settings

logger = structlog.get_logger()


class MCPMessageType(Enum):
    """MCP message types according to specification"""
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    COMPLETE = "completion/complete"
    NOTIFICATION = "notification"
    PROGRESS = "progress"


@dataclass
class MCPCapabilities:
    """MCP server capabilities"""
    experimental: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None


@dataclass
class MCPServerInfo:
    """MCP server information"""
    name: str
    version: str


@dataclass
class MCPToolCall:
    """MCP tool call request"""
    name: str
    arguments: Dict[str, Any]


@dataclass
class MCPToolResult:
    """MCP tool call result"""
    content: List[Dict[str, Any]]
    isError: Optional[bool] = None


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP resource definition"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class MCPPrompt(BaseModel):
    """MCP prompt definition"""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPServer:
    """Core MCP server implementation"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.tools: Dict[str, Callable] = {}
        self.resources: Dict[str, Callable] = {}
        self.prompts: Dict[str, Callable] = {}
        self.capabilities = MCPCapabilities(
            experimental={},
            logging={},
            prompts={"listChanged": True},
            resources={"subscribe": True, "listChanged": True},
            tools={"listChanged": True}
        )
        self.server_info = MCPServerInfo(
            name="autonomous-software-foundry",
            version="1.0.0"
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup MCP protocol routes"""
        
        @self.app.post("/mcp/initialize")
        async def initialize(request: Request):
            """MCP initialization handshake"""
            try:
                body = await request.json()
                
                # Validate initialization request
                if body.get("method") != "initialize":
                    logger.error("mcp_initialization_failed", error="Invalid initialization method")
                    raise HTTPException(status_code=400, detail="Invalid initialization method")
                
                # Extract client capabilities
                client_capabilities = body.get("params", {}).get("capabilities", {})
                client_info = body.get("params", {}).get("clientInfo", {})
                
                logger.info(
                    "mcp_client_initialized",
                    client_name=client_info.get("name", "unknown"),
                    client_version=client_info.get("version", "unknown"),
                    client_capabilities=list(client_capabilities.keys())
                )
                
                # Return server capabilities
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": asdict(self.capabilities),
                        "serverInfo": asdict(self.server_info)
                    }
                }
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                logger.error("mcp_initialization_failed", error=str(e))
                raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")
        
        @self.app.post("/mcp/tools/list")
        async def list_tools(request: Request):
            """List available MCP tools"""
            try:
                body = await request.json()
                
                tools_list = []
                for name, tool_func in self.tools.items():
                    if hasattr(tool_func, '_mcp_tool_info'):
                        tool_info = tool_func._mcp_tool_info
                        tools_list.append({
                            "name": name,
                            "description": tool_info.description,
                            "inputSchema": tool_info.inputSchema
                        })
                
                logger.info("mcp_tools_listed", tools_count=len(tools_list))
                
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "tools": tools_list
                    }
                }
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is  
                raise
            except Exception as e:
                logger.error("mcp_tools_list_failed", error=str(e))
                raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(request: Request):
            """Execute MCP tool call"""
            try:
                body = await request.json()
                params = body.get("params", {})
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                if not tool_name or tool_name not in self.tools:
                    logger.error("mcp_tool_call_failed", error=f"Tool '{tool_name}' not found")
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                # Get correlation ID from request state
                correlation_id = getattr(request.state, 'correlation_id', 'unknown')
                
                logger.info(
                    "mcp_tool_called",
                    tool_name=tool_name,
                    arguments_keys=list(tool_arguments.keys()),
                    correlation_id=correlation_id
                )
                
                # Execute tool
                tool_func = self.tools[tool_name]
                try:
                    result = await tool_func(request, **tool_arguments)
                    
                    # Format result according to MCP spec
                    if isinstance(result, dict) and "content" in result:
                        tool_result = result
                    else:
                        tool_result = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2, default=str)
                                }
                            ]
                        }
                    
                    logger.info(
                        "mcp_tool_completed",
                        tool_name=tool_name,
                        correlation_id=correlation_id,
                        success=True
                    )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": tool_result
                    }
                    
                except Exception as tool_error:
                    logger.error(
                        "mcp_tool_execution_failed",
                        tool_name=tool_name,
                        error=str(tool_error),
                        correlation_id=correlation_id
                    )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tool execution failed: {str(tool_error)}"
                                }
                            ],
                            "isError": True
                        }
                    }
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise  
            except Exception as e:
                logger.error("mcp_tool_call_failed", error=str(e))
                raise HTTPException(status_code=500, detail=f"Tool call failed: {str(e)}")
        
        @self.app.post("/mcp/resources/list") 
        async def list_resources(request: Request):
            """List available MCP resources"""
            try:
                body = await request.json()
                
                resources_list = []
                for uri, resource_func in self.resources.items():
                    if hasattr(resource_func, '_mcp_resource_info'):
                        resource_info = resource_func._mcp_resource_info
                        resources_list.append({
                            "uri": uri,
                            "name": resource_info.name,
                            "description": resource_info.description,
                            "mimeType": resource_info.mimeType
                        })
                
                logger.info("mcp_resources_listed", resources_count=len(resources_list))
                
                return {
                    "jsonrpc": "2.0", 
                    "id": body.get("id"),
                    "result": {
                        "resources": resources_list
                    }
                }
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                logger.error("mcp_resources_list_failed", error=str(e))
                raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")
        
        @self.app.post("/mcp/resources/read")
        async def read_resource(request: Request):
            """Read MCP resource content"""
            try:
                body = await request.json()
                params = body.get("params", {})
                resource_uri = params.get("uri")
                
                if not resource_uri or resource_uri not in self.resources:
                    logger.error("mcp_resource_read_failed", error=f"Resource '{resource_uri}' not found")
                    raise HTTPException(status_code=404, detail=f"Resource '{resource_uri}' not found")
                
                correlation_id = getattr(request.state, 'correlation_id', 'unknown')
                
                logger.info(
                    "mcp_resource_read",
                    resource_uri=resource_uri,
                    correlation_id=correlation_id
                )
                
                # Read resource
                resource_func = self.resources[resource_uri]
                content = await resource_func(request)
                
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "contents": content if isinstance(content, list) else [content]
                    }
                }
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                logger.error("mcp_resource_read_failed", error=str(e))
                raise HTTPException(status_code=500, detail=f"Resource read failed: {str(e)}")
    
    def register_tool(
        self, 
        name: str, 
        description: str, 
        input_schema: Dict[str, Any],
        required_scopes: Optional[List[str]] = None
    ):
        """Decorator to register MCP tools"""
        def decorator(func: Callable):
            # Store tool metadata
            func._mcp_tool_info = MCPTool(
                name=name,
                description=description,
                inputSchema=input_schema
            )
            func._required_scopes = required_scopes or []
            
            # Register tool
            self.tools[name] = func
            
            logger.info(
                "mcp_tool_registered",
                tool_name=name,
                required_scopes=required_scopes
            )
            
            return func
        return decorator
    
    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str = "application/json"
    ):
        """Decorator to register MCP resources"""
        def decorator(func: Callable):
            func._mcp_resource_info = MCPResource(
                uri=uri,
                name=name,
                description=description,
                mimeType=mime_type
            )
            
            self.resources[uri] = func
            
            logger.info(
                "mcp_resource_registered",
                resource_uri=uri,
                resource_name=name
            )
            
            return func
        return decorator


# Global MCP server instance
mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get global MCP server instance"""
    global mcp_server
    if mcp_server is None:
        raise RuntimeError("MCP server not initialized")
    return mcp_server


def initialize_mcp_server(app: FastAPI) -> MCPServer:
    """Initialize global MCP server"""
    global mcp_server
    mcp_server = MCPServer(app)
    return mcp_server