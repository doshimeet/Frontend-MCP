"""
Design Tokens MCP Resource
Exposes design://tokens/{theme} for passive context attachment.
"""

import json
from mcp.server.fastmcp import FastMCP
from services.token_service import TokenService

token_service = TokenService()


def register_tokens_resources(mcp: FastMCP) -> None:
    """Registers passive token resources on FastMCP server."""

    @mcp.resource("design://tokens/{theme}")
    def get_theme_tokens_resource(theme: str) -> str:
        """
        Stream full DTCG design tokens for a requested theme directly into LLM context.
        Example URIs: design://tokens/default, design://tokens/enterprise-dark, design://tokens/client-warm-sage
        """
        theme_tokens = token_service.get_theme_tokens(theme)
        return theme_tokens.model_dump_json(indent=2)
