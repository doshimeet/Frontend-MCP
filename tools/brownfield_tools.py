"""
Brownfield Integration FastMCP Tool
Thin wrapper delegating to BrownfieldService.
"""

from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from services.brownfield_service import BrownfieldService

brownfield_service = BrownfieldService()


def register_brownfield_tools(mcp: FastMCP) -> None:
    """Registers brownfield integration tools on the FastMCP server."""

    @mcp.tool()
    def extend_existing_app(
        project_path: str,
        page_route: str,
        inject_design_system: bool = False,
    ) -> Dict[str, Any]:
        """
        Safely inspects an existing frontend application before adding a new page or feature.
        Detects Next.js App Router vs Pages Router and checks if the destination file already exists.
        Args:
            project_path: Path to the existing frontend application root.
            page_route: Desired URL route (e.g. '/invoices', '/settings', '/patients').
            inject_design_system: If True, non-destructively bootstraps tokens and micro-primitives.
        Returns target file path and warns if a file conflict exists.
        """
        result = brownfield_service.inspect_and_plan(
            project_path_str=project_path,
            page_route=page_route,
            inject_design_system=inject_design_system,
        )
        return result.model_dump()

    @mcp.tool()
    def integrate_into_existing_app(
        project_path: str,
        page_route: str,
        inject_design_system: bool = False,
    ) -> Dict[str, Any]:
        """
        [Alias for extend_existing_app] Safely inspects an existing frontend application before adding a page.
        """
        result = brownfield_service.inspect_and_plan(
            project_path_str=project_path,
            page_route=page_route,
            inject_design_system=inject_design_system,
        )
        return result.model_dump()

    @mcp.tool()
    def inject_nexus_into_app(
        project_path: str,
        inject_tokens: bool = True,
        inject_primitives: bool = True,
        inject_skills: bool = True,
    ) -> Dict[str, Any]:
        """
        Non-destructively injects Nexus design tokens, composable micro-primitives,
        and enterprise anti-slop skills into any existing brownfield repository.
        Args:
            project_path: Path to target frontend application.
            inject_tokens: Whether to inject master CSS variables into project.
            inject_primitives: Whether to inject StatCard, FilterToolbar, EmptyState.
            inject_skills: Whether to inject design-taste-frontend, impeccable, and wbg-enterprise-rules.md.
        """
        return brownfield_service.inject_design_system(
            project_path_str=project_path,
            inject_tokens=inject_tokens,
            inject_primitives=inject_primitives,
            inject_skills=inject_skills,
        )
