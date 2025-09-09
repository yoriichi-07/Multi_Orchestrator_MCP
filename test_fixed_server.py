#!/usr/bin/env python3
"""
Test the fixed MCP server locally with the exact same configuration
"""
import os
import sys
from pathlib import Path

# Add the project root to path for imports  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set required environment variables for testing
os.environ.setdefault("DESCOPE_PROJECT_ID", "P32RbAyKnfcvEJYS69SfSEk6GPKk")
os.environ.setdefault("DESCOPE_MANAGEMENT_KEY", "test-key") 
os.environ.setdefault("PORT", "8081")

# Import our fixed server
from mcp_server import main

if __name__ == "__main__":
    print("🧪 Testing fixed MCP server locally...")
    print("This will start the server on port 8081")
    print("You can test it with: curl -X POST http://localhost:8081/mcp ...")
    main()