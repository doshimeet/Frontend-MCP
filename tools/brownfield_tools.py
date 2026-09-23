"""
Brownfield Integration FastMCP Tool
Thin wrapper delegating to BrownfieldService.
"""

from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from services.brownfield_service import BrownfieldService

brownfield_service = BrownfieldService()


def register_brownfield_tools(mcp: FastMCP) -> None:
    """Registers brownfield integration tools on the FastMCP server."""

    @mcp.tool()
    def extend_existing_app(project_path: str, page_route: str) -> Dict[str, Any]:
        """
        Safely inspects an existing frontend application before adding a new page or feature.
        Detects Next.js App Router vs Pages Router and checks if the destination file already exists.
        Args:
            project_path: Path to the existing frontend application root.
            page_route: Desired URL route (e.g. '/invoices', '/settings', '/patients').
        Returns target file path and warns if a file conflict exists.
        """
        result = brownfield_service.inspect_and_plan(project_path_str=project_path, page_route=page_route)
        return result.model_dump()

    @mcp.tool()
    def integrate_into_existing_app(project_path: str, page_route: str) -> Dict[str, Any]:
        """
        [Alias for extend_existing_app] Safely inspects an existing frontend application before adding a page.
        """
        result = brownfield_service.inspect_and_plan(project_path_str=project_path, page_route=page_route)
        return result.model_dump()
