"""
Page Recipes MCP Resource
Exposes recipe://{recipe_name} for passive template attachment.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from config import RECIPES_DIR


def register_recipes_resources(mcp: FastMCP) -> None:
    """Registers passive recipe layout resources on FastMCP server."""

    @mcp.resource("recipe://{recipe_name}")
    def get_recipe_resource(recipe_name: str) -> str:
        """
        Stream pre-composed layout template code directly into LLM context.
        Example URIs: recipe://CrudTableRecipe, recipe://MetricsDashboardRecipe, recipe://FormWizardRecipe
        """
        clean_name = recipe_name.removesuffix(".tsx")
        target_file = RECIPES_DIR / f"{clean_name}.tsx"

        if target_file.exists():
            try:
                return target_file.read_text(encoding="utf-8")
            except Exception as exc:
                return f"Error reading recipe: {exc}"

        return f"Recipe '{recipe_name}' template not found on disk."
