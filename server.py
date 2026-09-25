"""
Enterprise Design System & Application Scaffolding Engine
Dual-Transport Model Context Protocol (MCP) Server
Gold-Standard Clean Architecture with Tools, Resources, Prompts, and Azure Probes.
"""

import json
import logging
import os
import sys

# Ensure server package directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import (
    MCP_HOST,
    MCP_MODE,
    MCP_PORT,
    MCP_API_KEY,
    SYSTEM_NAME,
    SYSTEM_DISPLAY_NAME,
    SYSTEM_VERSION,
)

# Import Tools
from tools.diagnostics_tools import register_diagnostics_tools
from tools.tokens_tools import register_tokens_tools
from tools.recipes_tools import register_recipes_tools
from tools.catalog_tools import register_catalog_tools
from tools.requirements_tools import register_requirements_tools
from tools.scaffolding_tools import register_scaffolding_tools
from tools.brownfield_tools import register_brownfield_tools

# Import Resources
from resources.tokens_resource import register_tokens_resources
from resources.recipes_resource import register_recipes_resources

# Import Prompts
from prompts.plan_prd_prompt import register_plan_prd_prompt
from prompts.critique_ui_prompt import register_critique_ui_prompt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,  # Logs to stderr so stdio JSON-RPC remains clean
)
logger = logging.getLogger("nexus-mcp.server")

# 1. Initialize FastMCP Server
mcp = FastMCP(
    SYSTEM_NAME,
    instructions=(
        f"{SYSTEM_DISPLAY_NAME} (v{SYSTEM_VERSION}) & Frontend Scaffolding Engine. "
        "Provides design tokens, Nexus Enterprise component schemas, page recipes, "
        "Azure DevOps starter kit scaffolding, and brownfield conflict detection."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
)

# 2. Cloud Security Middleware & Azure Liveness Probe
class CloudAuthMiddleware(BaseHTTPMiddleware):
    """
    Cloud security middleware for Azure App Service / container deployments.
    Protects SSE and message endpoints with API Key / Bearer token authentication
    when MCP_API_KEY is configured in the environment.
    Always allows unauthenticated access to /health for Azure ALB liveness probes.
    """

    async def dispatch(self, request, call_next):
        # Dedicated bypass for Azure ALB / App Service health check
        if request.url.path == "/health":
            return await call_next(request)

        api_key = os.getenv("MCP_API_KEY")
        if api_key:
            auth_header = request.headers.get("Authorization", "")
            x_api_key = request.headers.get("x-api-key", "")
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
            elif x_api_key:
                token = x_api_key.strip()

            if not token or token != api_key:
                return JSONResponse(
                    {
                        "error": "Unauthorized",
                        "message": "Invalid or missing API key. Provide 'Authorization: Bearer <key>' or 'x-api-key: <key>'.",
                    },
                    status_code=401,
                )

        return await call_next(request)


@mcp.custom_route("/health", methods=["GET"])
async def liveness_probe(request):
    """
    Dedicated HTTP health check endpoint for Azure App Service Application Load Balancer.
    Returns HTTP 200 OK without requiring authentication.
    """
    return JSONResponse({
        "status": "UP",
        "service": f"{SYSTEM_NAME}-mcp",
        "version": SYSTEM_VERSION,
        "transport": os.getenv("MCP_MODE", MCP_MODE),
    })


def create_cloud_app():
    """Builds and returns the Starlette application with cloud security middleware attached."""
    app = mcp.sse_app()
    app.add_middleware(CloudAuthMiddleware)
    return app


# 3. Register All Domain Tools
register_diagnostics_tools(mcp)
register_tokens_tools(mcp)
register_recipes_tools(mcp)
register_catalog_tools(mcp)
register_requirements_tools(mcp)
register_scaffolding_tools(mcp)
register_brownfield_tools(mcp)

# 4. Register Passive Context Resources (design://, recipe://)
register_tokens_resources(mcp)
register_recipes_resources(mcp)

# 5. Register Guided Agent Prompts (/plan_prd_feature, /impeccable_design_critique)
register_plan_prd_prompt(mcp)
register_critique_ui_prompt(mcp)

# 6. Top-Level ASGI Application Export (for Azure App Service / Uvicorn / Gunicorn)
app = create_cloud_app()


# 7. Dual-Transport Execution
def main():
    mode = os.getenv("MCP_MODE", MCP_MODE).lower()

    if mode in ("uvicorn", "sse", "cloud"):
        import anyio
        import uvicorn
        from connectors.ado_connector import AzureDevOpsConnector

        # Attempt cloud startup refresh of starter-kit snapshot with resilient fallback
        try:
            logger.info("Checking Azure DevOps for starter-kit updates...")
            refreshed = AzureDevOpsConnector().refresh_starter_snapshot()
            if refreshed:
                logger.info("Successfully refreshed starter-kit snapshot from Azure DevOps.")
            else:
                logger.info("Using cached local starter-kit snapshot.")
        except Exception as exc:
            logger.warning("Startup starter-kit refresh skipped: %s (keeping local snapshot)", exc)

        logger.info("Starting Enterprise MCP Server in CLOUD mode (SSE) on %s:%s", MCP_HOST, MCP_PORT)
        config = uvicorn.Config(
            app,
            host=MCP_HOST,
            port=MCP_PORT,
            log_level="info",
        )
        server = uvicorn.Server(config)
        anyio.run(server.serve)
    else:
        logger.info("Starting Enterprise MCP Server in LOCAL mode (stdio)")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

