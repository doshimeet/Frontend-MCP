"""
PRD Planning MCP Prompt Template
Pre-engineered prompt guiding AI agents to convert PRDs into design system architectures.
"""

from mcp.server.fastmcp import FastMCP


def register_plan_prd_prompt(mcp: FastMCP) -> None:
    """Registers the PRD planning prompt template on FastMCP server."""

    @mcp.prompt("plan_prd_feature")
    def plan_prd_feature(prd_content: str, target_theme: str = "default") -> str:
        """
        Guided workflow to transform a PRD into an enterprise frontend implementation.
        """
        return f"""You are an Enterprise Solutions Architect specializing in Frontend Design Systems.
Review the following Product Requirements Document (PRD) and generate a comprehensive architecture plan.

### Requirements Document:
{prd_content}

### Target Theme:
{target_theme}

### Instructions:
1. Call tool `plan_application_from_requirements` to extract domain entities and recommended routes.
2. Call tool `get_design_tokens` to retrieve approved styling constraints for the `{target_theme}` theme.
3. Call tool `get_components` to verify available UI controls in the catalog.
4. Output a step-by-step implementation checklist adhering strictly to DESIGN.md principles.
"""
