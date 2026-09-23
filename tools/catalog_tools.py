"""
Component Catalog FastMCP Tool
Thin wrapper delegating to StorybookConnector.
"""

from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from connectors.storybook_connector import StorybookConnector
from models.component import ComponentCatalogSummary, ComponentSpec, PropDefinition

storybook_connector = StorybookConnector()


def register_catalog_tools(mcp: FastMCP) -> None:
    """Registers component catalog and Storybook inspection tools."""

    @mcp.tool()
    def get_components(source: str = "carbon") -> ComponentCatalogSummary:
        """
        List all available components in the design system catalog with summary descriptions.
        Args:
            source: 'carbon' for IBM Carbon testbed | 'enterprise' for internal Artifactory package.
        """
        summary = storybook_connector.get_catalog_summary(source)
        return ComponentCatalogSummary(
            source=source,
            total_components=len(summary),
            components=summary,
        )

    @mcp.tool()
    def get_component_props(component_name: str) -> Optional[ComponentSpec]:
        """
        Fetch full TypeScript prop interface, import statement, and canonical example for a component.
        Args:
            component_name: e.g. 'Button', 'DataTable', 'Modal', 'TextInput', 'Tag', 'SkeletonText'.
        Always verify props with this tool before generating JSX to prevent invalid attributes.
        """
        raw_spec = storybook_connector.get_component_spec(component_name)
        if not raw_spec:
            return None

        props = {
            k: PropDefinition(
                type=v.get("type", "any"),
                required=v.get("required") == "true" or v.get("required") is True,
                default=v.get("default"),
                description=v.get("description"),
            )
            for k, v in raw_spec.get("props", {}).items()
        }

        return ComponentSpec(
            name=component_name,
            import_statement=raw_spec["import_statement"],
            description=raw_spec["description"],
            props=props,
            example=raw_spec["example"],
        )
