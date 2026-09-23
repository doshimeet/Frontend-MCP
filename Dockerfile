# ==============================================================================
# ENTERPRISE DESIGN SYSTEM MCP SERVER - AZURE APP SERVICE DOCKERFILE
# Linux Container for Azure App Service / Azure Container Apps deployment
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cloud Mode configuration
ENV MCP_MODE=uvicorn
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV WEBSITES_PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition and install packages
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application source code
COPY . .

# Expose port for Azure App Service
EXPOSE 8000

# Health check endpoint probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch the MCP server in cloud SSE mode via uvicorn
CMD ["python", "server.py"]
