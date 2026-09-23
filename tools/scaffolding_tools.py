"""
Greenfield Scaffolding FastMCP Tool
Thin wrapper delegating to ScaffoldingService with path sandboxing.
"""

from mcp.server.fastmcp import FastMCP
from services.scaffolding_service import ScaffoldingService
from models.scaffolding import ScaffoldResult

scaffolding_service = ScaffoldingService()


def register_scaffolding_tools(mcp: FastMCP) -> None:
    """Registers greenfield scaffolding tools on the FastMCP server."""

    @mcp.tool()
    def create_enterprise_app(app_name: str, target_directory: str) -> ScaffoldResult:
        """
        Scaffold a brand-new Next.js enterprise application from the corporate starter kit.
        Configures IBM Carbon / Design System components, DTCG design tokens, accessibility testing, and routing.
        Args:
            app_name: Name of the application (e.g. 'dental-patient-portal', 'invoice-audit-app').
            target_directory: Target path where the project should be created.
        CRITICAL: Confirm destination path with user in chat before invoking this tool.
        """
        return scaffolding_service.scaffold(app_name=app_name, target_directory_str=target_directory)

    @mcp.tool()
    def scaffold_greenfield_app(app_name: str, target_directory: str) -> ScaffoldResult:
        """
        [Alias for create_enterprise_app] Scaffold a brand-new Next.js application from the starter kit.
        """
        return scaffolding_service.scaffold(app_name=app_name, target_directory_str=target_directory)
