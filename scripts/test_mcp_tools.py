#!/usr/bin/env python3
"""
Simple MCP Tool Test Script

This script connects directly to the local MCP server and lists available tools.
"""

# Set demo mode BEFORE any imports
import os
if not os.getenv('DESCOPE_DEMO_MODE'):
    os.environ['DESCOPE_DEMO_MODE'] = 'true'

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.descope_auth import get_descope_client

async def test_mcp_server():
    """Test the MCP server and list available tools."""
    
    server_url = "http://localhost:8080"
    
    try:
        print("🔄 Connecting to MCP server...")
        print(f"📡 Server URL: {server_url}")
        
        # Get JWT token
        print("\n🔐 Getting JWT token...")
        descope_client = await get_descope_client()
        
        # In demo mode, the access key is ignored
        token_result = await descope_client.create_machine_token("demo_access_key")
        jwt_token = token_result.get('access_token')
        
        print(f"✅ JWT Token: {jwt_token[:20]}...")
        
        # Test the MCP server endpoints
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            
            # Test health endpoint
            print("\n🏥 Testing health endpoint...")
            async with session.get(f"{server_url}/health", headers=headers) as response:
                health_data = await response.json()
                print(f"Status: {response.status}")
                print(f"Health: {json.dumps(health_data, indent=2)}")
            
            # Test tools endpoint
            print("\n🛠️  Testing tools endpoint...")
            async with session.get(f"{server_url}/tools", headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    tools_data = await response.json()
                    print(f"Available tools: {len(tools_data.get('tools', []))}")
                    
                    for tool in tools_data.get('tools', []):
                        print(f"  - {tool.get('name')}: {tool.get('description', '')[:80]}...")
                else:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
            
            # Test prompts endpoint
            print("\n💬 Testing prompts endpoint...")
            async with session.get(f"{server_url}/prompts", headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    prompts_data = await response.json()
                    print(f"Available prompts: {len(prompts_data.get('prompts', []))}")
                    
                    for prompt in prompts_data.get('prompts', []):
                        print(f"  - {prompt.get('name')}: {prompt.get('description', '')[:80]}...")
                else:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
    
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 MCP Server Tool Test")
    print("=" * 50)
    
    asyncio.run(test_mcp_server())