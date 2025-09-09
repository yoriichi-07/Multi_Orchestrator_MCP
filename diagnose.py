#!/usr/bin/env python3
"""
MCP Server Diagnostic Tool
Checks server configuration and helps debug deployment issues
"""
import json
import os
import sys
from datetime import datetime, timezone

def check_environment():
    """Check environment variables and configuration"""
    print("🔍 Environment Check")
    print("-" * 30)
    
    # Check critical environment variables
    env_vars = {
        "PORT": os.environ.get("PORT", "Not Set"),
        "DESCOPE_PROJECT_ID": "Set" if os.environ.get("DESCOPE_PROJECT_ID") else "Not Set",
        "DESCOPE_MANAGEMENT_KEY": "Set" if os.environ.get("DESCOPE_MANAGEMENT_KEY") else "Not Set",
        "CEQUENCE_GATEWAY_ID": "Set" if os.environ.get("CEQUENCE_GATEWAY_ID") else "Not Set",
        "CEQUENCE_API_KEY": "Set" if os.environ.get("CEQUENCE_API_KEY") else "Not Set",
    }
    
    for var, value in env_vars.items():
        status = "✅" if value != "Not Set" else "⚠️"
        print(f"{status} {var}: {value}")
    
    print()

def check_imports():
    """Check if all required modules can be imported"""
    print("📦 Import Check")
    print("-" * 20)
    
    modules = {
        "fastmcp": "FastMCP",
        "structlog": "Structured Logging",
        "starlette": "Starlette ASGI",
        "uvicorn": "Uvicorn Server",
    }
    
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✅ {description} ({module})")
        except ImportError as e:
            print(f"❌ {description} ({module}): {e}")
    
    print()

def check_fastmcp_version():
    """Check FastMCP version and capabilities"""
    print("🚀 FastMCP Version Check")
    print("-" * 25)
    
    try:
        import fastmcp
        print(f"✅ FastMCP version: {getattr(fastmcp, '__version__', 'Unknown')}")
        
        # Test FastMCP initialization
        from fastmcp import FastMCP
        test_mcp = FastMCP("DiagnosticTest")
        
        # Check if http_app method exists
        if hasattr(test_mcp, 'http_app'):
            print("✅ HTTP transport supported")
        else:
            print("❌ HTTP transport not available")
            
        # Test creating HTTP app
        try:
            app = test_mcp.http_app(path="/mcp", transport="streamable-http")
            print("✅ Streamable HTTP transport working")
        except Exception as e:
            print(f"❌ Streamable HTTP transport error: {e}")
            
    except Exception as e:
        print(f"❌ FastMCP check failed: {e}")
    
    print()

def check_server_config():
    """Check server configuration"""
    print("⚙️ Server Configuration")
    print("-" * 23)
    
    try:
        # Import and check settings
        from src.core.config import settings
        
        print(f"✅ Descope Project ID: {'Set' if settings.descope_project_id else 'Not Set'}")
        print(f"✅ Cequence Gateway: {'Set' if settings.cequence_gateway_id else 'Not Set'}")
        
        # Check if orchestrator can be imported
        from src.agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        print("✅ AgentOrchestrator initialized")
        
        # Check if required methods exist
        if hasattr(orchestrator, 'advanced_generate_application'):
            print("✅ Advanced methods available")
        else:
            print("❌ Advanced methods missing")
            
    except Exception as e:
        print(f"❌ Server config check failed: {e}")
    
    print()

def main():
    """Run all diagnostic checks"""
    print(f"🏥 MCP Server Diagnostic Report")
    print(f"📅 Generated: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    print()
    
    check_environment()
    check_imports()
    check_fastmcp_version()
    check_server_config()
    
    print("=" * 60)
    print("🎯 Diagnostic Complete")
    print()
    print("💡 If all checks pass, the server should work in Smithery.")
    print("💡 If any checks fail, those areas need attention before deployment.")

if __name__ == "__main__":
    main()