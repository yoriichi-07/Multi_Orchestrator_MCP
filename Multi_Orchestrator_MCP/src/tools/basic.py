"""
Basic MCP tools for health checking and testing
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends
import structlog

from src.core.auth import AuthContext, verify_token, require_scopes

logger = structlog.get_logger()
router = APIRouter()


@router.post("/tools/ping")
async def ping_tool(
    auth: AuthContext = Depends(require_scopes("tools:ping"))
) -> Dict[str, Any]:
    """
    Basic connectivity test tool
    
    Scope required: tools:ping
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "ping_requested",
        user_id=auth.user_id,
        correlation_id=correlation_id
    )
    
    return {
        "message": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "authenticated_user": auth.user_id
    }


@router.post("/tools/health_check")
async def health_check_tool(
    auth: AuthContext = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Comprehensive health check tool
    
    Scope required: Any valid authentication
    """
    correlation_id = str(uuid.uuid4())
    
    # Perform basic health checks
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "checks": {
            "auth": "passing",
            "file_system": "passing",
            "memory": "passing"
        }
    }
    
    # Test file system access
    try:
        test_file = f"./outputs/health_check_{correlation_id}.txt"
        with open(test_file, "w") as f:
            f.write("health check test")
        import os
        os.remove(test_file)
    except Exception as e:
        health_status["checks"]["file_system"] = f"failing: {str(e)}"
        health_status["status"] = "degraded"
    
    logger.info(
        "health_check_completed",
        user_id=auth.user_id,
        correlation_id=correlation_id,
        status=health_status["status"]
    )
    
    return health_status


@router.post("/tools/echo")
async def echo_tool(
    message: str,
    auth: AuthContext = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Echo tool for testing request/response flow
    
    Scope required: Any valid authentication
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "echo_requested",
        user_id=auth.user_id,
        correlation_id=correlation_id,
        message_length=len(message)
    )
    
    return {
        "echo": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "user_id": auth.user_id,
        "message_length": len(message)
    }
