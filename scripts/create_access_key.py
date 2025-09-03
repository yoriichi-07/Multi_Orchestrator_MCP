"""
Create Access Key using Descope Management API
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import settings
import httpx


async def create_access_key():
    """Create an Access Key for machine-to-machine authentication"""
    print("🔄 Creating Access Key...")
    
    management_key = settings.descope_management_key
    project_id = settings.descope_project_id
    
    if not management_key or not project_id:
        print("❌ Missing management key or project ID. Check your .env file.")
        return
    
    print(f"🔑 Using Management Key: {management_key[:10]}...{management_key[-10:]}")
    print(f"📁 Project ID: {project_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Create Access Key payload
            payload = {
                "name": "MCP Server Access Key",
                "expireTime": "0",  # Never expires (as string)
                "roleNames": [],  # No specific roles
                "keyTenants": [],  # No tenants
                "customClaims": {
                    "purpose": "mcp_server",
                    "environment": "development"
                },
                "description": "Access key for MCP Server authentication"
            }
            
            url = f"https://api.descope.com/v1/mgmt/accesskey/create"
            headers = {
                "Authorization": f"Bearer {project_id}:{management_key}",
                "Content-Type": "application/json"
            }
            
            print(f"🌐 Making request to: {url}")
            
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Access Key created successfully!")
                print(f"🆔 Key ID: {data.get('key', {}).get('id')}")
                print(f"🔑 Key Value: {data.get('cleartext')[:20]}...{data.get('cleartext')[-10:]}")
                
                # Save the access key
                access_key_file = Path("access_key.json")
                with open(access_key_file, "w") as f:
                    json.dump({
                        "id": data.get("key", {}).get("id"),
                        "cleartext": data.get("cleartext"),
                        "name": "MCP Server Access Key"
                    }, f, indent=2)
                
                print(f"💾 Access Key saved to: {access_key_file}")
                
                # Update .env file
                print("📝 Update your .env file with:")
                print(f"DESCOPE_ACCESS_KEY={data.get('cleartext')}")
                
                return data.get("cleartext")
            else:
                print(f"❌ Failed to create access key: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"💥 Error creating access key: {e}")


if __name__ == "__main__":
    asyncio.run(create_access_key())