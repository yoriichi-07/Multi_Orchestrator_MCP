"""
Test authentication flow manually
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.descope_auth import get_descope_client, AuthContext
from src.middleware.auth_middleware import get_auth_context, require_scopes
from src.tools.authenticated_tools import ping_tool


async def test_authentication_flow():
    """Test the complete authentication flow"""
    print("🧪 Testing Complete Authentication Flow")
    print("=" * 50)
    
    # 1. Get Descope client
    print("1️⃣ Getting Descope client...")
    client = await get_descope_client()
    print(f"✅ Client initialized (demo_mode: {client.demo_mode})")
    
    # 2. Create machine token
    print("\n2️⃣ Creating machine token...")
    token_data = await client.create_machine_token(
        access_key="test_access_key",
        custom_claims={"environment": "test"}
    )
    access_token = token_data["access_token"]
    print(f"✅ Token created: {access_token[:50]}...")
    
    # 3. Validate token
    print("\n3️⃣ Validating token...")
    claims = await client.validate_jwt_token(access_token)
    print(f"✅ Token valid - Subject: {claims['sub']}")
    print(f"   Permissions: {claims.get('permissions', [])}")
    
    # 4. Create AuthContext
    print("\n4️⃣ Creating AuthContext...")
    auth_context = AuthContext(claims)
    print(f"✅ AuthContext created - User: {auth_context.user_id}")
    print(f"   Is machine: {auth_context.is_machine}")
    print(f"   Scopes: {auth_context.scopes}")
    
    # 5. Test scope validation
    print("\n5️⃣ Testing scope validation...")
    required_scopes = ["tools:ping"]
    has_scope = auth_context.has_all_scopes(required_scopes)
    print(f"✅ Has required scopes {required_scopes}: {has_scope}")
    
    # 6. Test authenticated tool
    print("\n6️⃣ Testing authenticated tool...")
    try:
        # Mock the request context for testing
        mock_context = {
            "auth_context": auth_context,
            "arguments": {}
        }
        
        result = await ping_tool(mock_context)
        print(f"✅ Ping tool result: {result}")
    except Exception as e:
        print(f"❌ Ping tool failed: {e}")
    
    print("\n🎉 Authentication flow test completed!")


if __name__ == "__main__":
    asyncio.run(test_authentication_flow())