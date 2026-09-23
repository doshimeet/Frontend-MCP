"""
Page Recipes FastMCP Tool
Serves pre-composed, tested layout templates (CrudTable, Dashboard, FormWizard).
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from config import RECIPES_DIR


def register_recipes_tools(mcp: FastMCP) -> None:
    """Registers recipe retrieval tools on the FastMCP server."""

    @mcp.tool()
    def list_page_recipes() -> List[Dict[str, Any]]:
        """
        List all available canonical page recipes with descriptions and component composition.
        Use this tool when planning a page to choose the best pre-composed layout pattern.
        """
        catalog_file = RECIPES_DIR / "recipes.json"
        if catalog_file.exists():
            try:
                with open(catalog_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return [
            {
                "name": "CrudTableRecipe",
                "description": "Enterprise table view with search bar, status badges, bulk actions, and pagination.",
                "best_for": "Lists, logs, audit trails, entity management, and tabular data.",
                "file": "CrudTableRecipe.tsx",
            },
            {
                "name": "MetricsDashboardRecipe",
                "description": "Executive dashboard with primary KPI cards, trend charts, and recent activity log.",
                "best_for": "Analytics, performance monitoring, operations overviews.",
                "file": "MetricsDashboardRecipe.tsx",
            },
            {
                "name": "FormWizardRecipe",
                "description": "Multi-step form layout with progress indicator, inline validation, and sticky actions.",
                "best_for": "Registration, complex checkout, data entry intake wizards.",
                "file": "FormWizardRecipe.tsx",
            }
        ]

    @mcp.tool()
    def get_page_recipe(recipe_name: str) -> str:
        """
        Fetch the complete boilerplate TSX code for a pre-composed page recipe.
        Args:
            recipe_name: e.g. 'CrudTableRecipe', 'MetricsDashboardRecipe', 'FormWizardRecipe'.
        Always use this code as your starting foundation rather than inventing layout from scratch.
        """
        clean_name = recipe_name.removesuffix(".tsx")
        target_file = RECIPES_DIR / f"{clean_name}.tsx"

        if target_file.exists():
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as exc:
                return f"Error reading recipe file: {exc}"

        return (
            f"Recipe '{recipe_name}' not found on disk. Available recipes: "
            f"CrudTableRecipe, MetricsDashboardRecipe, FormWizardRecipe."
        )
