"""
Demo Descope Authentication for Development/Testing
"""
import jwt
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List


class DemoDescopeAuth:
    """Demo authentication client for development"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.demo_secret = "demo_secret_key_for_development_only"
    
    async def create_machine_token(
        self, 
        access_key: str, 
        custom_claims: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a demo JWT token"""
        
        # Create demo JWT payload
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "demo_machine_user",
            "iss": f"https://api.descope.com/{self.project_id}",
            "aud": self.project_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "permissions": [
                "tools:ping", 
                "tools:generate", 
                "tools:review", 
                "tools:fix", 
                "tools:deploy",
                "admin:logs",
                "admin:config"
            ],
            "type": "machine",
            "tenantId": "demo_tenant",
            "customClaims": custom_claims or {},
            "jti": f"demo_token_{int(time.time())}"
        }
        
        # Create demo JWT token
        token = jwt.encode(payload, self.demo_secret, algorithm="HS256")
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "key_id": "demo_key_id"
        }
    
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate demo JWT token"""
        try:
            # For demo mode, we don't verify audience to keep it simple
            payload = jwt.decode(
                token, 
                self.demo_secret, 
                algorithms=["HS256"],
                options={"verify_aud": False}  # Skip audience verification in demo mode
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise Exception(f"Token has expired: {e}")
        except jwt.InvalidTokenError as e:
            raise Exception(f"Invalid token: {e}")
        except Exception as e:
            raise Exception(f"Token validation error: {e}")