@echo off
echo Starting MCP Authentication Proxy...
echo.

rem Set environment variables
set DESCOPE_DEMO_MODE=true
set DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo

echo Choose authentication method:
echo 1. Start Authentication Proxy (Recommended)
echo 2. Generate Manual JWT Token
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting authentication proxy...
    python scripts/mcp_client_with_auth.py https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp/mcp
) else if "%choice%"=="2" (
    echo Generating JWT token...
    python scripts/get_jwt_token.py
) else (
    echo Invalid choice. Please run the script again.
)

pause