"""
Enhanced Descope authentication integration for MCP server
Implements Access Key authentication with JWT validation
"""
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import httpx
import jwt
import structlog

from src.core.config import settings
from src.core.demo_auth import DemoDescopeAuth

logger = structlog.get_logger()


class DescopeConfig:
    """Descope configuration constants for Access Key authentication"""
    BASE_URL = "https://api.descope.com"
    JWKS_URL = f"{BASE_URL}/v1/keys"
    ACCESS_KEY_EXCHANGE_URL = f"{BASE_URL}/v1/auth/accesskey/exchange"  # Access Key Exchange endpoint


class TokenValidationError(Exception):
    """Token validation specific errors"""
    pass


class ScopeValidationError(Exception):
    """Scope validation specific errors"""
    pass


class DescopeClient:
    """Descope client for Access Key authentication and JWT validation"""
    
    def __init__(
        self, 
        project_id: str, 
        management_key: Optional[str] = None,
        cache_ttl: int = 3600,
        demo_mode: bool = False
    ):
        self.project_id = project_id
        self.demo_mode = demo_mode
        
        # Use demo auth if in demo mode
        if self.demo_mode:
            self.demo_client = DemoDescopeAuth(project_id)
            logger.info("🚧 Demo mode enabled - using mock authentication")
        else:
            self.demo_client = None
        self.management_key = management_key
        self.cache_ttl = cache_ttl
        self._jwks_cache: Dict[str, Any] = {}
        self._jwks_cache_expiry = 0
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set for token validation"""
        current_time = time.time()
        
        if current_time < self._jwks_cache_expiry and self._jwks_cache:
            return self._jwks_cache
        
        try:
            response = await self.http_client.get(
                f"{DescopeConfig.JWKS_URL}/{self.project_id}"
            )
            response.raise_for_status()
            
            self._jwks_cache = await response.json()
            self._jwks_cache_expiry = current_time + self.cache_ttl
            
            logger.info(
                "jwks_refreshed",
                project_id=self.project_id,
                keys_count=len(self._jwks_cache.get("keys", []))
            )
            
            return self._jwks_cache
            
        except httpx.HTTPError as e:
            logger.error(
                "jwks_fetch_failed",
                project_id=self.project_id,
                error=str(e)
            )
            raise TokenValidationError(f"Failed to fetch JWKS: {str(e)}")
    
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token using Descope public keys"""
        # Use demo mode if enabled
        if self.demo_mode:
            return await self.demo_client.validate_jwt_token(token)
        
        try:
            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise TokenValidationError("Token missing key ID")
            
            # Get public keys
            jwks = await self.get_jwks()
            
            # Find matching key
            public_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                raise TokenValidationError(f"Public key not found for kid: {kid}")
            
            # Validate and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.project_id,
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "require": ["exp", "iat", "sub"]
                }
            )
            
            logger.info(
                "token_validated",
                subject=payload.get("sub"),
                scopes=payload.get("permissions", []),
                expires_at=payload.get("exp")
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenValidationError("Token has expired")
        except jwt.InvalidAudienceError:
            raise TokenValidationError("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise TokenValidationError("Invalid token issuer")
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {str(e)}")
    
    async def create_machine_token(
        self, 
        access_key: str, 
        custom_claims: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Exchange Access Key for JWT token for Non-Human Identity using Descope Access Key approach"""
        # Use demo mode if enabled
        if self.demo_mode:
            return await self.demo_client.create_machine_token(access_key, custom_claims)
        
        try:
            payload = {
                "loginOptions": {
                    "customClaims": custom_claims or {}
                }
            }
            
            response = await self.http_client.post(
                DescopeConfig.ACCESS_KEY_EXCHANGE_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_key}"
                }
            )
            response.raise_for_status()
            
            token_data = await response.json()
            
            logger.info(
                "access_key_exchanged",
                key_id=token_data.get("keyId", "unknown"),
                session_jwt=bool(token_data.get("sessionJwt"))
            )
            
            return {
                "access_token": token_data.get("sessionJwt"),
                "token_type": "Bearer",
                "key_id": token_data.get("keyId")
            }
            
        except httpx.HTTPError as e:
            logger.error(
                "access_key_exchange_failed",
                error=str(e)
            )
            raise TokenValidationError(f"Failed to exchange access key: {str(e)}")
    

class AuthContext:
    """Enhanced authentication context with detailed claims"""
    
    def __init__(self, token_claims: Dict[str, Any]):
        self.token_claims = token_claims
        self.user_id = token_claims.get("sub", "unknown")
        self.scopes = token_claims.get("permissions", [])
        self.client_id = token_claims.get("aud", "unknown")
        self.issued_at = datetime.fromtimestamp(token_claims.get("iat", 0), tz=timezone.utc)
        self.expires_at = datetime.fromtimestamp(token_claims.get("exp", 0), tz=timezone.utc)
        self.correlation_id = token_claims.get("jti", "unknown")
        
        # Non-Human Identity specific claims
        self.is_machine = token_claims.get("type") == "machine"
        self.tenant_id = token_claims.get("tenantId")
        self.custom_claims = token_claims.get("customClaims", {})
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if context has required scope"""
        return required_scope in self.scopes
    
    def has_any_scope(self, required_scopes: List[str]) -> bool:
        """Check if context has any of the required scopes"""
        return any(scope in self.scopes for scope in required_scopes)
    
    def has_all_scopes(self, required_scopes: List[str]) -> bool:
        """Check if context has all required scopes"""
        return all(scope in self.scopes for scope in required_scopes)
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def time_until_expiry(self) -> timedelta:
        """Get time until token expires"""
        return self.expires_at - datetime.now(timezone.utc)


# Global Descope client instance
descope_client: Optional[DescopeClient] = None


async def get_descope_client() -> DescopeClient:
    """Get singleton Descope client instance"""
    global descope_client
    
    if descope_client is None:
        descope_client = DescopeClient(
            project_id=settings.descope_project_id,
            management_key=settings.descope_management_key,
            demo_mode=settings.descope_demo_mode
        )
    
    return descope_client
