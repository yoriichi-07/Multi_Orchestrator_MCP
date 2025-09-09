#!/usr/bin/env python3
"""
Simple Descope Management Key Test
Tests if the current Management Key is valid by making a simple API call
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_management_key():
    """Test the Management Key validity"""
    project_id = os.getenv("DESCOPE_PROJECT_ID")
    management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
    
    print(f"🔐 Testing Management Key for Project: {project_id}")
    print(f"Management Key (first 10 chars): {management_key[:10] if management_key else 'None'}...")
    
    if not project_id or not management_key:
        print("❌ Missing DESCOPE_PROJECT_ID or DESCOPE_MANAGEMENT_KEY")
        return
    
    # Test with the correct Management API endpoint for searching users
    url = "https://api.descope.com/v1/mgmt/user/search"
    headers = {
        "Authorization": f"Bearer {project_id}:{management_key}",
        "Content-Type": "application/json"
    }
    
    # Simple search payload
    payload = {
        "limit": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                status = response.status
                text = await response.text()
                
                print(f"Response Status: {status}")
                
                if status == 200:
                    print("✅ Management Key is valid!")
                    result = await response.json()
                    user_count = len(result.get("users", []))
                    print(f"   Found {user_count} users in search")
                elif status == 401:
                    print("❌ Management Key is invalid or expired")
                    print("   You need to get a valid Management Key from:")
                    print("   1. Go to https://app.descope.com")
                    print("   2. Navigate to Company > Management Keys")
                    print("   3. Create or copy a valid Management Key")
                    print("   4. Update your .env file with the correct key")
                elif status == 403:
                    print("⚠️ Management Key valid but lacks permissions")
                    print("   Make sure the Management Key has user management permissions")
                else:
                    print(f"⚠️ Unexpected response: {status}")
                    print(f"Response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_management_key())