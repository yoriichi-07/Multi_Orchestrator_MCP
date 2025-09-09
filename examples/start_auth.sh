# Start the authentication proxy (Demo mode enabled for testing)
DESCOPE_DEMO_MODE=true DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo python scripts/mcp_client_with_auth.py https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp/mcp

# OR generate a manual JWT token (Demo mode enabled for testing)
DESCOPE_DEMO_MODE=true DESCOPE_ACCESS_KEY=K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo python scripts/get_jwt_token.py

# Note: For production use, remove DESCOPE_DEMO_MODE=true and use your real access key