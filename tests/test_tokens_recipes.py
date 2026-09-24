"""
Unit and integration tests for Phase 2: Design Tokens & Page Recipes.
Verifies DTCG token schemas, multi-tenant themes, recipe catalog, and FastMCP integration.
"""

import json
import sys
from pathlib import Path
import pytest

# Add packages/mcp-server to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from config import TOKENS_DIR, RECIPES_DIR
from services.token_service import TokenService
from server import mcp


def test_dtcg_tokens_json_structure():
    """Verify packages/tokens/tokens.json exists and conforms to DTCG standard format."""
    tokens_file = TOKENS_DIR / "tokens.json"
    assert tokens_file.exists(), f"Missing tokens.json at {tokens_file}"

    with open(tokens_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "color" in data
    assert "spacing" in data
    assert "typography" in data
    assert "radius" in data

    # Verify DTCG $value attributes
    assert data["color"]["primary"]["$value"] == "#002244"
    assert data["color"]["primary"]["$type"] == "color"
    assert data["spacing"]["md"]["$value"] == "1rem"
    assert data["typography"]["font_family_sans"]["$value"] != ""


def test_theme_tokens_loading():
    """Verify TokenService loads both enterprise-dark and client-warm-sage theme overrides."""
    svc = TokenService()

    # 1. Default Theme
    default_tokens = svc.get_theme_tokens("default")
    assert default_tokens.color["primary"].value == "#002244"
    assert default_tokens.color["background"].value == "#ffffff"

    # 2. Enterprise Dark Theme
    dark_tokens = svc.get_theme_tokens("enterprise-dark")
    assert dark_tokens.color["primary"].value == "#4589ff"
    assert dark_tokens.color["background"].value == "#161616"
    assert dark_tokens.color["text_primary"].value == "#f4f4f4"

    # 3. Client Warm Sage Theme
    sage_tokens = svc.get_theme_tokens("client-warm-sage")
    assert sage_tokens.color["primary"].value == "#2e5339"
    assert sage_tokens.color["background"].value == "#fbfaf7"
    assert sage_tokens.color["text_primary"].value == "#1f2420"


def test_recipes_json_catalog():
    """Verify packages/recipes/recipes.json catalog contains all 6 canonical recipes."""
    catalog_file = RECIPES_DIR / "recipes.json"
    assert catalog_file.exists(), f"Missing recipes.json at {catalog_file}"

    with open(catalog_file, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    assert len(recipes) == 6
    recipe_names = [r["name"] for r in recipes]
    assert "CrudTableRecipe" in recipe_names
    assert "MetricsDashboardRecipe" in recipe_names
    assert "FormWizardRecipe" in recipe_names
    assert "MasterDetailRecipe" in recipe_names
    assert "SettingsTabsRecipe" in recipe_names
    assert "AuditTimelineRecipe" in recipe_names

    for r in recipes:
        assert "required_components" in r
        assert len(r["required_components"]) >= 3
        assert "states_handled" in r
        assert "loading" in r["states_handled"] or "initial" in r["states_handled"]


def test_recipe_files_exist_and_contain_required_patterns():
    """Verify each recipe TSX file exists and contains resilient state handling patterns."""
    recipes = [
        "CrudTableRecipe.tsx",
        "MetricsDashboardRecipe.tsx",
        "FormWizardRecipe.tsx",
        "MasterDetailRecipe.tsx",
        "SettingsTabsRecipe.tsx",
        "AuditTimelineRecipe.tsx",
    ]

    for recipe_name in recipes:
        recipe_file = RECIPES_DIR / recipe_name
        assert recipe_file.exists(), f"Missing recipe file {recipe_file}"

        content = recipe_file.read_text(encoding="utf-8")
        assert '"use client";' in content or "'use client';" in content
        assert "@wbg/nexus" in content
        assert "export const" in content or "export function" in content
        assert "export default" in content


@pytest.mark.anyio
async def test_fastmcp_resources_tokens_and_recipes():
    """Verify FastMCP streams token and recipe resources via design:// and recipe:// URIs."""
    # 1. Stream tokens via design://
    token_contents = await mcp.read_resource("design://tokens/client-warm-sage")
    assert len(token_contents) == 1
    assert "#2e5339" in token_contents[0].content
    assert "client-warm-sage" in token_contents[0].content

    # 2. Stream recipe via recipe://
    recipe_contents = await mcp.read_resource("recipe://CrudTableRecipe")
    assert len(recipe_contents) == 1
    assert "CrudTableRecipe" in recipe_contents[0].content
    assert "DataTable" in recipe_contents[0].content


@pytest.mark.anyio
async def test_fastmcp_tools_recipes():
    """Verify FastMCP list_page_recipes and get_page_recipe tools."""
    # 1. list_page_recipes tool
    contents, result = await mcp.call_tool("list_page_recipes", {})
    recipes_list = result["result"] if "result" in result else result
    assert len(recipes_list) == 6
    names = [r["name"] for r in recipes_list]
    assert "CrudTableRecipe" in names
    assert "MetricsDashboardRecipe" in names
    assert "FormWizardRecipe" in names
    assert "MasterDetailRecipe" in names
    assert "SettingsTabsRecipe" in names
    assert "AuditTimelineRecipe" in names

    # 2. get_page_recipe tool
    contents, result = await mcp.call_tool("get_page_recipe", {"recipe_name": "MetricsDashboardRecipe"})
    code = result.get("component_code", result.get("result", ""))
    assert "export const MetricsDashboardRecipe" in code
    assert "DEFAULT_KPIS" in code
    assert "test_spec_code" in result
    assert "getByRole" in result["test_spec_code"]

    # 3. get_recipe_test tool
    contents, test_result = await mcp.call_tool("get_recipe_test", {"recipe_name": "CrudTableRecipe"})
    test_code = test_result.get("result", test_result) if isinstance(test_result, dict) else test_result
    assert "getByRole" in test_code
    assert "CrudTableRecipe Component Spec" in test_code
