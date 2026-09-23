"""
Requirements FastMCP Tool
Thin wrapper delegating to RequirementsService.
"""

from mcp.server.fastmcp import FastMCP
from services.requirements_service import RequirementsService
from models.requirements import RequirementBlueprint

requirements_service = RequirementsService()


def register_requirements_tools(mcp: FastMCP) -> None:
    """Registers requirements parsing tools on the FastMCP server."""

    @mcp.tool()
    def plan_application_architecture(requirements_text: str, theme: str = "default") -> RequirementBlueprint:
        """
        Analyze a Product Requirements Document (PRD), user story, or feature prompt.
        Outputs an actionable architectural blueprint with domain routes, entity models, and design system recipes.
        Args:
            requirements_text: The full text of the PRD, user prompt, or Jira ticket.
            theme: Target theme ('default', 'enterprise-dark', 'client-warm-sage', or 'wbg-enterprise').
        Always execute this tool first when starting a new feature or application.
        """
        return requirements_service.plan_architecture(requirements_text, theme)

    @mcp.tool()
    def plan_application_from_requirements(requirements_text: str, theme: str = "default") -> RequirementBlueprint:
        """
        [Alias for plan_application_architecture] Analyze requirements into an architectural blueprint.
        """
        return requirements_service.plan_architecture(requirements_text, theme)
