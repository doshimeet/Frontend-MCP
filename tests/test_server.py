"""
Unit and integration tests for the FastMCP Server entrypoint,
Cloud Security Middleware, Azure ALB Health Probe, and MCP Primitives.
"""

import os
import sys
from pathlib import Path
import pytest
import httpx

# Add packages/mcp-server to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from server import mcp, create_cloud_app


@pytest.mark.anyio
async def test_health_probe_returns_200():
    """Verify that Azure ALB / App Service liveness probe responds with HTTP 200."""
    app = create_cloud_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert data["service"] == "enterprise-design-system-mcp"


@pytest.mark.anyio
async def test_cloud_auth_middleware_enforcement():
    """Verify that CloudAuthMiddleware enforces authentication when MCP_API_KEY is configured."""
    test_key = "test-enterprise-secret-key-456"
    os.environ["MCP_API_KEY"] = test_key

    try:
        app = create_cloud_app()
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. Health endpoint MUST always bypass authentication
            health_res = await client.get("/health")
            assert health_res.status_code == 200

            # 2. Protected endpoint without token returns 401
            unauth_res = await client.get("/messages")
            assert unauth_res.status_code == 401
            assert unauth_res.json()["error"] == "Unauthorized"

            # 3. Protected endpoint with invalid token returns 401
            bad_token_res = await client.get(
                "/messages",
                headers={"Authorization": "Bearer invalid-wrong-token"},
            )
            assert bad_token_res.status_code == 401

            # 4. Protected endpoint with valid Bearer token passes auth
            bearer_res = await client.get(
                "/messages",
                headers={"Authorization": f"Bearer {test_key}"},
            )
            assert bearer_res.status_code != 401

            # 5. Protected endpoint with valid x-api-key header passes auth
            api_key_res = await client.get(
                "/messages",
                headers={"x-api-key": test_key},
            )
            assert api_key_res.status_code != 401
    finally:
        del os.environ["MCP_API_KEY"]


@pytest.mark.anyio
async def test_fastmcp_call_tool_catalog():
    """Verify invoking get_components through FastMCP protocol handler."""
    contents, result = await mcp.call_tool("get_components", {"source": "carbon"})
    assert result["source"] == "carbon"
    assert result["total_components"] >= 5
    assert "Button" in result["components"]
    assert "DataTable" in result["components"]


@pytest.mark.anyio
async def test_fastmcp_call_tool_requirements():
    """Verify invoking plan_application_from_requirements through FastMCP protocol handler."""
    contents, result = await mcp.call_tool(
        "plan_application_from_requirements",
        {
            "requirements_text": "Create an invoice processing system with search filter and status badge",
            "theme": "enterprise-dark",
        },
    )
    assert result["target_theme"] == "enterprise-dark"
    assert len(result["recommended_routes"]) >= 1


@pytest.mark.anyio
async def test_fastmcp_get_prompt_plan_prd():
    """Verify rendering plan_prd_feature prompt template through FastMCP."""
    prompt_result = await mcp.get_prompt(
        "plan_prd_feature",
        {"prd_content": "Customer claims portal", "target_theme": "client-warm-sage"},
    )
    assert len(prompt_result.messages) == 1
    assert "Customer claims portal" in prompt_result.messages[0].content.text
    assert "client-warm-sage" in prompt_result.messages[0].content.text


@pytest.mark.anyio
async def test_fastmcp_read_resource_tokens():
    """Verify streaming token definitions through FastMCP resource URI."""
    contents = await mcp.read_resource("design://tokens/default")
    assert len(contents) >= 1
    assert "primary" in contents[0].content
    assert "#0f62fe" in contents[0].content
