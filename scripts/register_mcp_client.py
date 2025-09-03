"""
Script to register a new MCP client dynamically with Descope
"""
import asyncio
import json
from pathlib import Path
from src.core.descope_auth import DescopeClient
from src.core.config import settings


async def register_mcp_client():
    """Register a new MCP client for testing"""
    print("🔄 Registering new MCP client with Descope...")
    
    async with DescopeClient(
        project_id=settings.descope_project_id,
        management_key=settings.descope_management_key
    ) as client:
        
        try:
            client_data = await client.register_dynamic_client(
                client_name="MCP Test Client",
                redirect_uris=[
                    "http://localhost:8000/auth/callback",
                    "https://your-domain.fly.dev/auth/callback"
                ],
                scopes=[
                    "tools:ping",
                    "tools:generate", 
                    "tools:review",
                    "tools:fix",
                    "tools:deploy"
                ]
            )
            
            print("✅ Client registered successfully!")
            print(f"📋 Client ID: {client_data['client_id']}")
            print(f"🔑 Client Secret: {client_data['client_secret']}")
            print(f"🔗 Redirect URIs: {client_data['redirect_uris']}")
            
            # Save client credentials for testing
            credentials_file = Path("client_credentials.json")
            with open(credentials_file, "w") as f:
                json.dump(client_data, f, indent=2)
            
            print(f"💾 Credentials saved to: {credentials_file}")
            
            return client_data
            
        except Exception as e:
            print(f"❌ Client registration failed: {str(e)}")
            raise


async def main():
    """Main function"""
    try:
        await register_mcp_client()
        print("🎉 Dynamic client registration completed successfully!")
    except Exception as e:
        print(f"💥 Registration failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())