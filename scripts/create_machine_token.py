"""
Create machine-to-machine token for Non-Human Identity testing
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.descope_auth import DescopeClient
from src.core.config import settings


async def create_machine_token():
    """Exchange Access Key for JWT token for testing"""
    print("🔄 Exchanging Access Key for JWT token...")
    
    # Use the client secret as an Access Key
    access_key = settings.descope_client_secret
    
    # If not in config, try to load from saved credentials
    if not access_key:
        credentials_file = Path("client_credentials.json")
        if credentials_file.exists():
            print("📂 Loading access key from file...")
            with open(credentials_file, "r") as f:
                client_data = json.load(f)
                access_key = client_data.get("client_secret") or client_data.get("access_key")
        else:
            print("❌ No access key found. Please check your .env file.")
            return
    
    print(f"🔑 Using Access Key: {access_key[:10]}...{access_key[-10:]}")
    
    async with DescopeClient(
        project_id=settings.descope_project_id,
        demo_mode=settings.descope_demo_mode
    ) as client:
        
        try:
            token_data = await client.create_machine_token(
                access_key=access_key,
                custom_claims={"test_claim": "mcp_server"}
            )
            
            print("✅ Access Key exchanged successfully!")
            print(f"🎫 JWT Token: {token_data['access_token'][:50]}...")
            print(f"🔖 Token Type: {token_data.get('token_type', 'Bearer')}")
            print(f"🆔 Key ID: {token_data.get('key_id', 'unknown')}")
            
            # Save token for testing
            token_file = Path("machine_token.json")
            with open(token_file, "w") as f:
                json.dump(token_data, f, indent=2)
            
            print(f"💾 Token saved to: {token_file}")
            
            # Test the token by validating it
            print("\n🧪 Testing token validation...")
            claims = await client.validate_jwt_token(token_data["access_token"])
            print(f"✅ Token valid! Subject: {claims['sub']}")
            print(f"🔐 Scopes: {claims.get('permissions', [])}")
            print(f"⏳ Expires at: {claims.get('exp')}")
            
            return token_data
            
        except Exception as e:
            print(f"❌ Token creation failed: {str(e)}")
            raise


async def test_authenticated_request():
    """Test making an authenticated request to the MCP server"""
    import httpx
    
    token_file = Path("machine_token.json")
    if not token_file.exists():
        print("❌ No token found. Create one first.")
        return
    
    with open(token_file, "r") as f:
        token_data = json.load(f)
    
    access_token = token_data["access_token"]
    
    print("\n🧪 Testing authenticated MCP request...")
    
    async with httpx.AsyncClient() as http_client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test ping tool
            response = await http_client.post(
                "http://localhost:8000/mcp/v1/tools/ping",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ping successful! Response: {result['message']}")
                print(f"👤 Authenticated as: {result['authentication']['user_id']}")
                print(f"🔐 Scopes: {result['authentication']['scopes']}")
            else:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")


async def main():
    """Main function"""
    try:
        # Create machine token
        await create_machine_token()
        
        # Test the token with an actual request
        print("\n" + "="*50)
        await test_authenticated_request()
        
        print("\n🎉 Machine token creation and testing completed!")
        
    except Exception as e:
        print(f"💥 Operation failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())