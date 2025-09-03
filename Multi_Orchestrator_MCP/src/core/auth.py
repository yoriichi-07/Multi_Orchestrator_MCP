"""
Authentication and authorization for MCP server
"""
import jwt
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.core.config import settings


class AuthContext(BaseModel):
    """Authentication context for verified requests"""
    user_id: str
    scopes: List[str]
    token_claims: Dict[str, Any]
    correlation_id: str


class DescopeAuth:
    """Descope authentication handler"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        # In production, this would validate against Descope's public keys
        self.secret_key = "your-descope-secret"  # Replace with actual validation
    
    async def validate_token(self, token: str) -> AuthContext:
        """Validate JWT token and extract claims"""
        try:
            # Decode and validate JWT
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=["HS256"],
                options={"verify_exp": False}  # Disable expiry for testing
            )
            
            # Extract relevant claims
            user_id = payload.get("sub", "unknown")
            scopes = payload.get("permissions", [])
            
            return AuthContext(
                user_id=user_id,
                scopes=scopes,
                token_claims=payload,
                correlation_id=payload.get("jti", "unknown")
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# Initialize auth handler
auth_handler = DescopeAuth(settings.descope_project_id)
security = HTTPBearer()


async def verify_token(token = Security(security)) -> AuthContext:
    """Verify and extract authentication context"""
    try:
        return await auth_handler.validate_token(token.credentials)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def require_scopes(*required_scopes: str):
    """Decorator to require specific scopes"""
    def decorator(auth_context: AuthContext = Depends(verify_token)):
        missing_scopes = set(required_scopes) - set(auth_context.scopes)
        if missing_scopes:
            raise HTTPException(
                status_code=403, 
                detail=f"Missing required scopes: {', '.join(missing_scopes)}"
            )
        return auth_context
    return decorator
