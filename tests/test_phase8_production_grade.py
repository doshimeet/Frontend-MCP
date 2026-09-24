"""
Phase 8: Production-Grade Architectural Hardening Master Test Suite
Validates:
1. Multi-environment 3-mode auto-detection (carbon, wbg, cloud).
2. Dynamic dev server port probing across [3000, 3001, 4200, 5173].
3. Unbiased requirement planning with input modality detection (PRD vs Visual Mockup).
4. Anti-force-fitting logic (emitting recipe=None and open composition guide).
5. All 6 canonical recipes and their companion Playwright .spec.ts files.
6. FastMCP tools: get_page_recipe, get_recipe_test, and verify_application_health.
"""

import json
import os
import sys
from pathlib import Path
import pytest

# Ensure server package is importable
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from config import RECIPES_DIR, REPO_ROOT, CANDIDATE_DEV_PORTS
from core.environment import (
    resolve_active_mode,
    find_active_dev_port,
    find_active_dev_url,
    is_port_listening,
)
from services.requirements_service import RequirementsService
from services.a11y_service import A11yService
from server import mcp


def test_environment_mode_resolution():
    """Verify 3-mode resolution: carbon, wbg, cloud, and manual overrides."""
    # 1. Explicit override to carbon
    os.environ["DESIGN_SYSTEM_MODE"] = "carbon"
    assert resolve_active_mode() == "carbon"

    # 2. Explicit override to wbg
    os.environ["DESIGN_SYSTEM_MODE"] = "wbg"
    assert resolve_active_mode() == "wbg"

    # 3. Explicit override to cloud
    os.environ["DESIGN_SYSTEM_MODE"] = "cloud"
    assert resolve_active_mode() == "cloud"

    # Clean up override
    del os.environ["DESIGN_SYSTEM_MODE"]

    # 4. Simulated Azure Cloud container
    os.environ["WEBSITE_SITE_NAME"] = "app-enterprise-mcp-prod"
    assert resolve_active_mode() == "cloud"
    del os.environ["WEBSITE_SITE_NAME"]

    # 5. Non-enterprise laptop fallback (defaults to carbon)
    # Ensure no enterprise credentials are in test env
    old_pat = os.environ.pop("AZURE_DEVOPS_PAT", None)
    try:
        mode = resolve_active_mode()
        assert mode in ("carbon", "wbg")
    finally:
        if old_pat:
            os.environ["AZURE_DEVOPS_PAT"] = old_pat


def test_candidate_dev_ports_includes_4200():
    """Verify candidate port probing includes 3000, 3001, 4200, 5173."""
    assert 3000 in CANDIDATE_DEV_PORTS
    assert 3001 in CANDIDATE_DEV_PORTS
    assert 4200 in CANDIDATE_DEV_PORTS
    assert 5173 in CANDIDATE_DEV_PORTS
    assert len(CANDIDATE_DEV_PORTS) == 4


def test_requirements_service_input_modality_detection():
    """Verify RequirementsService detects PRD vs Visual Mockup modalities."""
    service = RequirementsService()

    # Text PRD
    prd_plan = service.plan_from_text(
        "Product Requirement Document: Create an institutional loan disbursement ledger.",
        theme="enterprise-dark",
    )
    assert prd_plan.input_modality in ("prd", "text_prd")
    assert prd_plan.active_mode in ("carbon", "wbg", "cloud")

    # Visual Mockup
    mockup_plan = service.plan_from_text(
        "Attached Figma screenshot mockup showing split screen inspector and telemetry trail.",
        theme="default",
    )
    assert mockup_plan.input_modality == "visual_mockup"


def test_requirements_anti_force_fitting_bespoke_intent():
    """Verify non-standard/bespoke layouts are NOT force-fit into canonical recipes."""
    service = RequirementsService()

    # Bespoke prompt describing custom workflow
    blueprint = service.plan_from_text(
        "Design a custom interactive drag and drop canvas workflow editor for network topologies.",
        theme="default",
    )

    # Must contain at least one route with recipe = None and layout_type = 'open_composition'
    bespoke_routes = [r for r in blueprint.recommended_routes if r.recipe is None]
    assert len(bespoke_routes) >= 1
    bespoke_route = bespoke_routes[0]
    assert bespoke_route.layout_type == "open_composition"
    assert bespoke_route.composition_guide is not None
    assert "atomic" in bespoke_route.composition_guide.lower()
    assert "tokens" in bespoke_route.composition_guide.lower()


def test_all_six_canonical_recipes_and_specs_exist():
    """Verify all 6 canonical TSX recipes and their companion Playwright .spec.ts exist."""
    catalog_file = RECIPES_DIR / "recipes.json"
    assert catalog_file.exists()

    with open(catalog_file, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    assert len(recipes) == 6
    expected_recipes = [
        "CrudTableRecipe",
        "MetricsDashboardRecipe",
        "FormWizardRecipe",
        "MasterDetailRecipe",
        "SettingsTabsRecipe",
        "AuditTimelineRecipe",
    ]

    catalog_names = [r["name"] for r in recipes]
    for expected in expected_recipes:
        assert expected in catalog_names

        # Check TSX file
        tsx_file = RECIPES_DIR / f"{expected}.tsx"
        assert tsx_file.exists(), f"Missing {tsx_file}"
        tsx_content = tsx_file.read_text(encoding="utf-8")
        assert len(tsx_content) > 500

        # Check Companion Spec file
        spec_file = RECIPES_DIR / f"{expected}.spec.ts"
        assert spec_file.exists(), f"Missing companion spec {spec_file}"
        spec_content = spec_file.read_text(encoding="utf-8")
        assert "@playwright/test" in spec_content
        assert "getByRole" in spec_content


@pytest.mark.anyio
async def test_fastmcp_get_page_recipe_typed_response():
    """Verify FastMCP get_page_recipe returns PageRecipeResponse with TSX and test spec."""
    # Test MasterDetailRecipe
    contents, result = await mcp.call_tool("get_page_recipe", {"recipe_name": "MasterDetailRecipe"})
    assert result["name"] == "MasterDetailRecipe"
    assert "MasterDetailRecipe" in result["component_code"]
    assert "test_spec_code" in result
    assert "getByRole" in result["test_spec_code"]
    assert len(result["required_components"]) >= 3
    assert len(result["states_handled"]) >= 3


@pytest.mark.anyio
async def test_fastmcp_get_recipe_test():
    """Verify FastMCP get_recipe_test returns Playwright spec directly."""
    contents, result = await mcp.call_tool("get_recipe_test", {"recipe_name": "SettingsTabsRecipe"})
    code = result.get("result", result) if isinstance(result, dict) else result
    assert "SettingsTabsRecipe Component Spec" in code
    assert "getByRole" in code
    assert "test.describe" in code


@pytest.mark.anyio
async def test_fastmcp_verify_application_health_tool():
    """Verify FastMCP verify_application_health tool executes and probes candidate ports."""
    contents, report = await mcp.call_tool("verify_application_health", {})
    assert "url" in report
    assert "detected_port" in report
    assert report["detected_port"] in [3000, 3001, 4200, 5173]
    assert "is_healthy" in report
    assert "console_errors" in report
    assert "remediations" in report
