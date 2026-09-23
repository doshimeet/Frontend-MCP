"""
Design Tokens FastMCP Tool
Thin wrapper delegating to TokenService.
"""

from mcp.server.fastmcp import FastMCP
from services.token_service import TokenService
from models.tokens import TokenCategoryResponse

token_service = TokenService()


def register_tokens_tools(mcp: FastMCP) -> None:
    """Registers design token tools on FastMCP server."""

    @mcp.tool()
    def get_design_tokens(category: str = "all", theme: str = "default") -> TokenCategoryResponse:
        """
        Fetch approved design tokens (colors, spacing, typography, radii).
        Args:
            category: 'all', 'color', 'spacing', 'typography', or 'radius'.
            theme: 'default', 'enterprise-dark', or client theme name (e.g. 'client-warm-sage').
        Use this tool before writing any styling code to guarantee token compliance.
        """
        return token_service.get_category_tokens(category=category, theme=theme)
