# Smithery Compatible MCP Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project configuration
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy source code
COPY . .

# Ensure the MCP server script is available at root level for easy access
COPY mcp_server.py ./main.py

# Start the MCP server - Smithery sets PORT=8081
CMD ["uv", "run", "python", "main.py"]