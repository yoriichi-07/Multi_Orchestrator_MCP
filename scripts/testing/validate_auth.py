#!/usr/bin/env python3
"""
Authentication Validation Script

This script tests the complete authentication flow and verifies that all components
are working correctly. It helps users troubleshoot authentication problems and
ensures the complete flow is functioning before configuring Cursor IDE.

Usage:
    python validate_auth.py [access_key]
    
Environment Variables:
    DESCOPE_ACCESS_KEY - The access key to test (if not provided as argument)
    DESCOPE_PROJECT_ID - Your Descope project ID (default: P32RbAyKnfcvEJYS69SfSEk6GPKk)
    MCP_SERVER_URL - MCP server URL to test against (optional)

Example:
    python validate_auth.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo
"""

# Set demo mode BEFORE any imports to ensure it's picked up by pydantic settings
import os
if not os.getenv('DESCOPE_DEMO_MODE'):
    os.environ['DESCOPE_DEMO_MODE'] = 'true'
    print("🚧 Demo mode auto-enabled for testing purposes")

import asyncio
import aiohttp
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.descope_auth import get_descope_client
from src.core.config import settings


class AuthValidator:
    """
    Authentication validation class that tests all components of the auth flow.
    """
    
    def __init__(self, access_key: str, project_id: str = None, mcp_server_url: str = None):
        self.access_key = access_key
        self.project_id = project_id or 'P32RbAyKnfcvEJYS69SfSEk6GPKk'
        self.mcp_server_url = mcp_server_url
        self.test_results: List[Dict[str, Any]] = []
        
    def add_test_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Add a test result to the results list."""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': time.time()
        })
    
    async def test_descope_client_initialization(self) -> bool:
        """Test that the Descope client can be initialized."""
        try:
            descope_client = await get_descope_client()
            if descope_client:
                self.add_test_result(
                    "Descope Client Initialization",
                    True,
                    f"Client initialized successfully for project {self.project_id}"
                )
                return True
            else:
                self.add_test_result(
                    "Descope Client Initialization", 
                    False, 
                    "", 
                    "Failed to get Descope client"
                )
                return False
        except Exception as e:
            self.add_test_result(
                "Descope Client Initialization", 
                False, 
                "", 
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_access_key_exchange(self) -> Optional[str]:
        """Test exchanging the access key for a JWT token."""
        try:
            descope_client = await get_descope_client()
            result = await descope_client.create_machine_token(self.access_key)
            
            jwt_token = result.get('access_token')
            expires_in = result.get('expires_in')
            scopes = result.get('scope', '').split(' ') if result.get('scope') else []
            
            if jwt_token:
                self.add_test_result(
                    "Access Key to JWT Exchange",
                    True,
                    f"Token obtained (expires in {expires_in}s), Scopes: {', '.join(scopes) if scopes else 'None'}"
                )
                return jwt_token
            else:
                self.add_test_result(
                    "Access Key to JWT Exchange",
                    False,
                    "",
                    "No access token in response"
                )
                return None
                
        except Exception as e:
            self.add_test_result(
                "Access Key to JWT Exchange",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return None
    
    async def test_jwt_token_format(self, jwt_token: str) -> bool:
        """Test that the JWT token has the correct format."""
        try:
            # Basic JWT format check (should have 3 parts separated by dots)
            parts = jwt_token.split('.')
            
            if len(parts) != 3:
                self.add_test_result(
                    "JWT Token Format",
                    False,
                    "",
                    f"Invalid JWT format - expected 3 parts, got {len(parts)}"
                )
                return False
            
            # Check that each part is base64-like (contains valid characters)
            import base64
            import string
            
            valid_chars = string.ascii_letters + string.digits + '+/='
            for i, part in enumerate(parts):
                if not all(c in valid_chars for c in part):
                    self.add_test_result(
                        "JWT Token Format",
                        False,
                        "",
                        f"Part {i+1} contains invalid base64 characters"
                    )
                    return False
            
            self.add_test_result(
                "JWT Token Format",
                True,
                f"Valid JWT format with {len(parts)} parts, token length: {len(jwt_token)} chars"
            )
            return True
            
        except Exception as e:
            self.add_test_result(
                "JWT Token Format",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests and return a summary."""
        print("🔍 Starting authentication validation...")
        print(f"   Project ID: {self.project_id}")
        print(f"   Access Key: {self.access_key[:10]}...{self.access_key[-10:]}")
        if self.mcp_server_url:
            print(f"   MCP Server: {self.mcp_server_url}")
        print()
        
        # Run tests in sequence
        client_ok = await self.test_descope_client_initialization()
        if not client_ok:
            return self.generate_summary()
        
        jwt_token = await self.test_access_key_exchange()
        if not jwt_token:
            return self.generate_summary()
        
        await self.test_jwt_token_format(jwt_token)
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all test results."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'overall_success': failed_tests == 0,
            'test_results': self.test_results
        }
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary of the validation results."""
        print("\n" + "="*70)
        print("🔐 AUTHENTICATION VALIDATION RESULTS")
        print("="*70)
        
        # Overall status
        if summary['overall_success']:
            print("✅ Overall Status: ALL TESTS PASSED")
        else:
            print("❌ Overall Status: SOME TESTS FAILED")
        
        print(f"\n📊 Test Summary:")
        print(f"   • Total Tests: {summary['total_tests']}")
        print(f"   • Passed: {summary['passed_tests']}")
        print(f"   • Failed: {summary['failed_tests']}")
        print(f"   • Success Rate: {summary['success_rate']:.1f}%")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in summary['test_results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            
            if result['details']:
                print(f"      └─ {result['details']}")
            
            if result['error']:
                print(f"      └─ ⚠️  {result['error']}")
        
        # Recommendations
        print(f"\n💡 Next Steps:")
        if summary['overall_success']:
            print("   • Authentication is working correctly!")
            print("   • You can now configure Cursor IDE with confidence")
            print("   • Use 'python scripts/get_jwt_token.py' to get your JWT token")
            print("   • Or use 'python scripts/mcp_client_with_auth.py' for automatic auth")
        else:
            print("   • Review the failed tests above")
            print("   • Check your Descope configuration and access key")
            print("   • Verify network connectivity to Descope and MCP server")
            print("   • Ensure all required environment variables are set")
            print("   • Consider running with DESCOPE_DEMO_MODE=true for local testing")
        
        print("\n" + "="*70)


async def main():
    """Main function to handle command line arguments and run validation."""    
    # Check demo mode
    if settings.descope_demo_mode:
        print("🚧 Demo mode enabled - using mock authentication")
    
    # Get access key from command line or environment
    access_key = None
    
    if len(sys.argv) > 1:
        access_key = sys.argv[1]
    else:
        access_key = os.getenv('DESCOPE_ACCESS_KEY')
    
    if not access_key:
        print("❌ Error: No access key provided")
        print("\nUsage:")
        print("   python validate_auth.py <access_key>")
        print("   OR set DESCOPE_ACCESS_KEY environment variable")
        print("\nExample:")
        print("   python validate_auth.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo")
        print("\nOptional Environment Variables:")
        print("   DESCOPE_PROJECT_ID - Your Descope project ID")
        print("   MCP_SERVER_URL - MCP server URL to test against")
        sys.exit(1)
    
    # Get optional parameters
    project_id = os.getenv('DESCOPE_PROJECT_ID')
    mcp_server_url = os.getenv('MCP_SERVER_URL')
    
    # Create validator and run tests
    validator = AuthValidator(access_key, project_id, mcp_server_url)
    summary = await validator.run_all_tests()
    validator.print_summary(summary)
    
    # Exit with appropriate code
    sys.exit(0 if summary['overall_success'] else 1)


if __name__ == "__main__":
    asyncio.run(main())