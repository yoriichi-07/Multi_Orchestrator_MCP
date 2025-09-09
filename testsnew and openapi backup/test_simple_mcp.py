#!/usr/bin/env python3
"""
Simple MCP Server Test - Minimal FastMCP Server
"""
from fastmcp import FastMCP

# Create a simple FastMCP instance
mcp = FastMCP("Simple Test Server")

@mcp.tool()
async def ping() -> str:
    """Simple ping tool"""
    return "pong"

@mcp.tool()
async def hello(name: str) -> str:
    """Simple hello tool"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("Starting simple MCP server...")
    mcp.run(transport="http", host="0.0.0.0", port=9000)