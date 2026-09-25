"""
Component Catalog FastMCP Tool
Thin wrapper delegating to StorybookConnector.
"""

import logging
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from connectors.storybook_connector import StorybookConnector, normalize_component_name
from models.component import ComponentCatalogSummary, ComponentSpec, PropDefinition

logger = logging.getLogger("nexus-mcp.tools.catalog")
storybook_connector = StorybookConnector()


def register_catalog_tools(mcp: FastMCP) -> None:
    """Registers component catalog and Storybook inspection tools."""

    @mcp.tool()
    def get_components(source: str = "nexus") -> ComponentCatalogSummary:
        """
        List all available components in the design system catalog with summary descriptions.
        Args:
            source: 'nexus' for official World Bank Group design system | 'enterprise' for internal Artifactory package.
        """
        logger.info("[tool:get_components] Fetching catalog for source='%s'", source)
        summary = storybook_connector.get_catalog_summary(source)
        logger.info("[tool:get_components] Returning %d components", len(summary))
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
            component_name: e.g. 'Button', 'Table', 'Card', 'Dialog', 'Input', 'Tabs', 'Sheet', 'Select', 'Badge'.
        Always verify props with this tool before generating JSX to prevent invalid attributes.
        """
        logger.info("[tool:get_component_props] Resolving spec for '%s'", component_name)
        raw_spec = storybook_connector.get_component_spec(component_name)
        if not raw_spec:
            logger.warning("[tool:get_component_props] Component '%s' not found in catalog", component_name)
            return None

        props = {
            k: PropDefinition(
                type=v.get("type", "any"),
                required=v.get("required") == "true" or v.get("required") is True,
                default=v.get("default"),
                description=v.get("description"),
            )
            for k, v in raw_spec.get("props", {}).items()
            if isinstance(v, dict)
        }

        canonical_name = normalize_component_name(component_name)
        import_stmt = raw_spec.get("import_statement") or f"import {{ {canonical_name} }} from '@wbg/nexus';"
        desc = raw_spec.get("description") or f"Nexus design system {canonical_name} component."
        example = raw_spec.get("example") or f"<{canonical_name} />"

        logger.info("[tool:get_component_props] Successfully resolved '%s' (%d props)", canonical_name, len(props))
        return ComponentSpec(
            name=canonical_name,
            import_statement=import_stmt,
            description=desc,
            props=props,
            example=example,
        )
