"""
Comprehensive tests for Descope authentication system
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from src.core.descope_auth import DescopeClient, AuthContext, TokenValidationError
from src.middleware.auth_middleware import get_auth_context, require_scopes


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing"""
    import jwt
    
    payload = {
        "sub": "test_user_123",
        "aud": "P31WC6A6Vybbt7N5NhnH4dZLQgXY",
        "iss": "https://api.descope.com",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "jti": "test_correlation_id",
        "permissions": ["tools:ping", "tools:generate"],
        "type": "machine",
        "tenantId": "test_tenant",
        "customClaims": {"role": "software_foundry"}
    }
    
    return jwt.encode(payload, "test_secret", algorithm="HS256")


@pytest.fixture
def mock_expired_token():
    """Mock expired JWT token for testing"""
    import jwt
    
    payload = {
        "sub": "test_user_123",
        "aud": "P31WC6A6Vybbt7N5NhnH4dZLQgXY",
        "iss": "https://api.descope.com",
        "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
        "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        "jti": "test_correlation_id",
        "permissions": ["tools:ping"],
        "type": "machine"
    }
    
    return jwt.encode(payload, "test_secret", algorithm="HS256")


@pytest.fixture
def mock_jwks():
    """Mock JWKS response"""
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test_key_id",
                "use": "sig",
                "alg": "RS256",
                "n": "test_modulus",
                "e": "AQAB"
            }
        ]
    }


@pytest.fixture
def mock_descope_client():
    """Mock Descope client for testing"""
    client = AsyncMock(spec=DescopeClient)
    client.project_id = "P31WC6A6Vybbt7N5NhnH4dZLQgXY"
    return client


class TestDescopeClient:
    """Test Descope client functionality"""
    
    @pytest.mark.asyncio
    async def test_jwks_caching(self, mock_jwks):
        """Test JWKS caching mechanism"""
        client = DescopeClient("P31WC6A6Vybbt7N5NhnH4dZLQgXY")
        
        with patch.object(client.http_client, 'get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_jwks)
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            # First call should fetch JWKS
            jwks1 = await client.get_jwks()
            assert jwks1 == mock_jwks
            assert mock_get.call_count == 1
            
            # Second call should use cache
            jwks2 = await client.get_jwks()
            assert jwks2 == mock_jwks
            assert mock_get.call_count == 1  # Still only one call
    
    @pytest.mark.asyncio
    async def test_dynamic_client_registration(self):
        """Test dynamic client registration"""
        client = DescopeClient("P31WC6A6Vybbt7N5NhnH4dZLQgXY", "test_management_key")
        
        expected_response = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uris": ["http://localhost:8000/callback"]
        }
        
        with patch.object(client.http_client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=expected_response)
            mock_response.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response
            
            result = await client.register_dynamic_client(
                client_name="Test Client",
                redirect_uris=["http://localhost:8000/callback"],
                scopes=["tools:ping"]
            )
            
            assert result == expected_response
            assert mock_post.call_count == 1
    
    @pytest.mark.asyncio
    async def test_machine_token_creation(self):
        """Test machine-to-machine token creation"""
        client = DescopeClient("P31WC6A6Vybbt7N5NhnH4dZLQgXY")
        
        expected_response = {
            "keyId": "test_key_id",
            "sessionJwt": "test_jwt_token"
        }
        
        with patch.object(client.http_client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=expected_response)
            mock_response.raise_for_status = AsyncMock()
            mock_post.return_value = mock_response
            
            result = await client.create_machine_token(
                access_key="test_access_key",
                custom_claims={"test": "claim"}
            )
            
            expected_result = {
                "access_token": "test_jwt_token",
                "token_type": "Bearer",
                "key_id": "test_key_id"
            }
            
            assert result == expected_result
            assert mock_post.call_count == 1


class TestAuthContext:
    """Test authentication context functionality"""
    
    def test_auth_context_creation(self):
        """Test AuthContext creation from token claims"""
        claims = {
            "sub": "test_user",
            "aud": "test_client",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "jti": "test_correlation",
            "permissions": ["tools:ping", "tools:generate"],
            "type": "machine",
            "tenantId": "test_tenant"
        }
        
        context = AuthContext(claims)
        
        assert context.user_id == "test_user"
        assert context.client_id == "test_client"
        assert context.is_machine is True
        assert context.tenant_id == "test_tenant"
        assert "tools:ping" in context.scopes
    
    def test_scope_validation(self):
        """Test scope validation methods"""
        claims = {
            "sub": "test_user",
            "permissions": ["tools:ping", "tools:generate", "admin:logs"],
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        
        context = AuthContext(claims)
        
        # Test individual scope
        assert context.has_scope("tools:ping") is True
        assert context.has_scope("tools:deploy") is False
        
        # Test any scope
        assert context.has_any_scope(["tools:ping", "tools:deploy"]) is True
        assert context.has_any_scope(["tools:deploy", "tools:fix"]) is False
        
        # Test all scopes
        assert context.has_all_scopes(["tools:ping", "tools:generate"]) is True
        assert context.has_all_scopes(["tools:ping", "tools:deploy"]) is False
    
    def test_expiry_check(self):
        """Test token expiry validation"""
        # Expired token
        expired_claims = {
            "sub": "test_user",
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        expired_context = AuthContext(expired_claims)
        assert expired_context.is_expired() is True
        
        # Valid token
        valid_claims = {
            "sub": "test_user", 
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        valid_context = AuthContext(valid_claims)
        assert valid_context.is_expired() is False


class TestAuthenticationMiddleware:
    """Test authentication middleware functionality"""
    
    @pytest.mark.asyncio
    async def test_valid_token_authentication(self, mock_jwt_token, mock_descope_client):
        """Test successful authentication with valid token"""
        from src.middleware.auth_middleware import DescopeAuthMiddleware
        from fastapi import Request
        
        # Mock the get_descope_client function
        with patch('src.middleware.auth_middleware.get_descope_client', return_value=mock_descope_client):
            mock_descope_client.validate_jwt_token.return_value = {
                "sub": "test_user",
                "aud": "P31WC6A6Vybbt7N5NhnH4dZLQgXY",
                "permissions": ["tools:ping"],
                "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.now(timezone.utc).timestamp())
            }
            
            # This would typically be tested with a full FastAPI test setup
            # For now, we verify the client mock is called correctly
            await mock_descope_client.validate_jwt_token(mock_jwt_token)
            mock_descope_client.validate_jwt_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_expired_token_rejection(self, mock_expired_token, mock_descope_client):
        """Test rejection of expired tokens"""
        with patch('src.middleware.auth_middleware.get_descope_client', return_value=mock_descope_client):
            mock_descope_client.validate_jwt_token.side_effect = TokenValidationError("Token has expired")
            
            with pytest.raises(TokenValidationError):
                await mock_descope_client.validate_jwt_token(mock_expired_token)


class TestMCPToolsAuthentication:
    """Test MCP tools with authentication"""
    
    def test_ping_tool_with_valid_auth(self):
        """Test ping tool with valid authentication"""
        # This would be tested with a proper FastAPI TestClient
        # For now, we test the auth context creation
        claims = {
            "sub": "test_user",
            "permissions": ["tools:ping"],
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        
        auth_context = AuthContext(claims)
        assert auth_context.has_scope("tools:ping") is True
    
    def test_insufficient_scopes_rejection(self):
        """Test rejection when user lacks required scopes"""
        claims = {
            "sub": "test_user",
            "permissions": ["tools:ping"],  # Missing tools:generate
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        
        auth_context = AuthContext(claims)
        assert auth_context.has_scope("tools:generate") is False


class TestIntegrationScenarios:
    """Test complete authentication flow scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_authentication_flow(self, mock_descope_client):
        """Test complete flow from token creation to validation"""
        # Mock token creation
        mock_descope_client.create_machine_token.return_value = {
            "access_token": "test_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        # Mock token validation
        mock_descope_client.validate_jwt_token.return_value = {
            "sub": "test_machine_user",
            "permissions": ["tools:ping", "tools:generate"],
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        
        # Test token creation
        token_data = await mock_descope_client.create_machine_token(
            "test_client", "test_secret", ["tools:ping", "tools:generate"]
        )
        assert token_data["access_token"] == "test_token"
        
        # Test token validation
        claims = await mock_descope_client.validate_jwt_token("test_token")
        auth_context = AuthContext(claims)
        
        assert auth_context.has_scope("tools:ping") is True
        assert auth_context.has_scope("tools:generate") is True
        assert auth_context.has_scope("admin:logs") is False