#!/usr/bin/env python3
"""
Descope JWT Token Exchange Script

This script exchanges a Descope Access Key for a proper JWT token that can be used
with Cursor IDE MCP configuration. The JWT token provides the correct authentication
format that Cursor IDE expects for Bearer token authentication.

Usage:
    python get_jwt_token.py [access_key]
    
Environment Variables:
    DESCOPE_ACCESS_KEY - The access key to exchange (if not provided as argument)
    DESCOPE_PROJECT_ID - Your Descope project ID (default: P32RbAyKnfcvEJYS69SfSEk6GPKk)

Output:
    Prints the JWT token that should be used in your Cursor IDE mcp.json configuration
"""

# Set demo mode BEFORE any imports to ensure it's picked up by pydantic settings
import os
if not os.getenv('DESCOPE_DEMO_MODE'):
    os.environ['DESCOPE_DEMO_MODE'] = 'true'

import asyncio
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.descope_auth import get_descope_client


async def exchange_access_key_for_jwt(access_key: str, project_id: str = None) -> dict:
    """
    Exchange a Descope Access Key for a JWT token.
    
    Args:
        access_key: The Descope Access Key to exchange
        project_id: The Descope project ID (optional)
        
    Returns:
        Dictionary containing the JWT token and metadata
    """
    try:
        # Use default project ID if not provided
        if not project_id:
            project_id = os.getenv('DESCOPE_PROJECT_ID', 'P32RbAyKnfcvEJYS69SfSEk6GPKk')
        
        # Get the Descope client
        descope_client = await get_descope_client()
        
        # Exchange the access key for a JWT token
        result = await descope_client.create_machine_token(access_key)
        
        return {
            'success': True,
            'jwt_token': result.get('access_token'),
            'expires_in': result.get('expires_in'),
            'token_type': result.get('token_type', 'Bearer'),
            'scopes': result.get('scope', '').split(' ') if result.get('scope') else []
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def print_token_info(result: dict):
    """
    Print the token exchange result in a user-friendly format.
    """
    print("\n" + "="*60)
    print("🔐 DESCOPE JWT TOKEN EXCHANGE RESULT")
    print("="*60)
    
    if result['success']:
        print("✅ Token exchange successful!\n")
        
        print("📋 JWT Token (copy this to your mcp.json):")
        print("-" * 50)
        print(result['jwt_token'])
        print("-" * 50)
        
        print(f"\n📊 Token Information:")
        print(f"   • Token Type: {result['token_type']}")
        print(f"   • Expires In: {result['expires_in']} seconds")
        print(f"   • Scopes: {', '.join(result['scopes']) if result['scopes'] else 'None'}")
        
        print(f"\n📝 Usage Instructions:")
        print(f"   1. Copy the JWT token above")
        print(f"   2. Update your Cursor IDE mcp.json file")
        print(f"   3. Use 'Bearer <JWT_TOKEN>' as the authorization header")
        
        print(f"\n💡 Example mcp.json configuration:")
        example_config = {
            "mcpServers": {
                "multi-orchestrator": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-fetch", "https://your-server-url"],
                    "env": {
                        "AUTHORIZATION": f"Bearer {result['jwt_token'][:20]}..."
                    }
                }
            }
        }
        print(json.dumps(example_config, indent=2))
        
    else:
        print("❌ Token exchange failed!\n")
        print(f"Error Type: {result['error_type']}")
        print(f"Error Message: {result['error']}")
        
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Verify your Descope Access Key is correct")
        print(f"   • Check that your Descope project ID is valid")
        print(f"   • Ensure your access key has the required scopes")
        print(f"   • Verify network connectivity to Descope")
    
    print("\n" + "="*60)


async def main():
    """
    Main function to handle command line arguments and execute token exchange.
    """
    # Get access key from command line or environment
    access_key = None
    
    if len(sys.argv) > 1:
        access_key = sys.argv[1]
    else:
        access_key = os.getenv('DESCOPE_ACCESS_KEY')
    
    if not access_key:
        print("❌ Error: No access key provided")
        print("\nUsage:")
        print("   python get_jwt_token.py <access_key>")
        print("   OR set DESCOPE_ACCESS_KEY environment variable")
        print("\nExample:")
        print("   python get_jwt_token.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo")
        sys.exit(1)
    
    # Get project ID from environment (optional)
    project_id = os.getenv('DESCOPE_PROJECT_ID')
    
    print(f"🔄 Exchanging access key for JWT token...")
    print(f"   Project ID: {project_id or 'P32RbAyKnfcvEJYS69SfSEk6GPKk (default)'}")
    print(f"   Access Key: {access_key[:10]}...{access_key[-10:]}")
    
    # Exchange the token
    result = await exchange_access_key_for_jwt(access_key, project_id)
    
    # Print the result
    print_token_info(result)
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    asyncio.run(main())