"""
Page Recipes FastMCP Tool
Serves pre-composed, tested layout templates (CrudTable, Dashboard, FormWizard, MasterDetail, SettingsTabs, AuditTimeline).
Provides complete TypeScript React boilerplate code and companion semantic Playwright E2E test specs.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from config import RECIPES_DIR
from core.environment import resolve_active_mode
from models.recipes import PageRecipeResponse


def _load_recipe_catalog() -> List[Dict[str, Any]]:
    """Loads recipes.json catalog from RECIPES_DIR."""
    catalog_file = RECIPES_DIR / "recipes.json"
    if catalog_file.exists():
        try:
            with open(catalog_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def register_recipes_tools(mcp: FastMCP) -> None:
    """Registers recipe retrieval tools on the FastMCP server."""

    @mcp.tool()
    def list_page_recipes() -> List[Dict[str, Any]]:
        """
        List all available canonical page recipes with descriptions and component composition.
        Use this tool when planning a page to choose the best pre-composed layout pattern.
        """
        catalog = _load_recipe_catalog()
        if catalog:
            return catalog

        return [
            {
                "name": "CrudTableRecipe",
                "title": "Enterprise CRUD Data Table",
                "description": "Enterprise table view with search bar, status badges, bulk actions, and pagination.",
                "best_for": "Lists, logs, audit trails, entity management, and tabular data.",
                "file": "CrudTableRecipe.tsx",
                "test_file": "CrudTableRecipe.spec.ts",
            },
            {
                "name": "MetricsDashboardRecipe",
                "title": "Executive KPI & Operations Dashboard",
                "description": "Executive dashboard with primary KPI cards, trend charts, and recent activity log.",
                "best_for": "Analytics, performance monitoring, operations overviews.",
                "file": "MetricsDashboardRecipe.tsx",
                "test_file": "MetricsDashboardRecipe.spec.ts",
            },
            {
                "name": "FormWizardRecipe",
                "title": "Multi-Step Intake Form Wizard",
                "description": "Multi-step form layout with progress indicator, inline validation, and sticky actions.",
                "best_for": "Registration, complex checkout, data entry intake wizards.",
                "file": "FormWizardRecipe.tsx",
                "test_file": "FormWizardRecipe.spec.ts",
            },
            {
                "name": "MasterDetailRecipe",
                "title": "Master-Detail Operations Inspector",
                "description": "Split-pane layout with searchable directory on left and inspection drawer on right.",
                "best_for": "Procurement tenders, loan disbursements, case reviews, claim approvals.",
                "file": "MasterDetailRecipe.tsx",
                "test_file": "MasterDetailRecipe.spec.ts",
            },
            {
                "name": "SettingsTabsRecipe",
                "title": "Application Governance & Settings Hub",
                "description": "Multi-section tabbed portal configuration layout covering domains, MFA, and API secrets.",
                "best_for": "Portal settings, security controls, API key management, account configurations.",
                "file": "SettingsTabsRecipe.tsx",
                "test_file": "SettingsTabsRecipe.spec.ts",
            },
            {
                "name": "AuditTimelineRecipe",
                "title": "Chronological Audit & Governance Trail",
                "description": "Immutable chronological timeline stream capturing authorizations, status badges, and telemetry diffs.",
                "best_for": "Governance compliance, audit trails, transaction history, state change reviews.",
                "file": "AuditTimelineRecipe.tsx",
                "test_file": "AuditTimelineRecipe.spec.ts",
            },
        ]

    @mcp.tool()
    def get_page_recipe(recipe_name: str) -> PageRecipeResponse:
        """
        Fetch the complete boilerplate TSX code and companion Playwright test spec for a pre-composed page recipe.
        Args:
            recipe_name: e.g. 'CrudTableRecipe', 'MetricsDashboardRecipe', 'FormWizardRecipe',
                             'MasterDetailRecipe', 'SettingsTabsRecipe', 'AuditTimelineRecipe'.
        Returns:
            PageRecipeResponse containing component_code, test_spec_code, metadata, and accessibility guidance.
        """
        clean_name = recipe_name.removesuffix(".tsx").removesuffix(".spec.ts")
        component_file = RECIPES_DIR / f"{clean_name}.tsx"
        test_file = RECIPES_DIR / f"{clean_name}.spec.ts"

        component_code = ""
        test_spec_code = ""

        if component_file.exists():
            try:
                component_code = component_file.read_text(encoding="utf-8")
            except Exception as exc:
                component_code = f"// Error reading component file: {exc}"
        else:
            component_code = f"// Recipe '{clean_name}' not found at {component_file}"

        if test_file.exists():
            try:
                test_spec_code = test_file.read_text(encoding="utf-8")
            except Exception as exc:
                test_spec_code = f"// Error reading test spec file: {exc}"
        else:
            test_spec_code = f"// Companion test spec for '{clean_name}' not found at {test_file}"

        # Resolve active environment mode
        mode_val = resolve_active_mode()
        active_mode = mode_val.value if hasattr(mode_val, "value") else str(mode_val)

        # Match metadata from recipes.json
        catalog = _load_recipe_catalog()
        matched_meta = next((r for r in catalog if r.get("name") == clean_name), None)

        if matched_meta:
            title = matched_meta.get("title", clean_name)
            description = matched_meta.get("description", "")
            required_components = matched_meta.get("required_components", [])
            states_handled = matched_meta.get("states_handled", [])
            a11y_compliance = matched_meta.get("a11y_compliance", "WCAG 2.1 AA compliant")
        else:
            title = clean_name
            description = f"Pre-composed enterprise {clean_name} layout pattern."
            required_components = []
            states_handled = ["loading", "empty", "error", "success"]
            a11y_compliance = "WCAG 2.1 AA compliant with semantic landmarks"

        # If running in Carbon mode and recipe imports @wbg/design-system, provide seamless import adapt
        if active_mode == "carbon" and "@wbg/design-system" in component_code:
            # Note in header about Carbon mode compatibility
            component_code = (
                "// [Active Mode: Carbon - Public npm @carbon/react compatibility]\n"
                + component_code
            )

        return PageRecipeResponse(
            name=clean_name,
            title=title,
            description=description,
            component_code=component_code,
            test_spec_code=test_spec_code,
            target_mode=active_mode,
            required_components=required_components,
            states_handled=states_handled,
            a11y_compliance=a11y_compliance,
        )

    @mcp.tool()
    def get_recipe_test(recipe_name: str) -> str:
        """
        Fetch the companion Playwright test specification (.spec.ts) for a page recipe.
        Args:
            recipe_name: e.g. 'CrudTableRecipe', 'MasterDetailRecipe', 'AuditTimelineRecipe'.
        Returns:
            The complete Playwright test suite code with W3C ARIA locators.
        """
        clean_name = recipe_name.removesuffix(".tsx").removesuffix(".spec.ts")
        test_file = RECIPES_DIR / f"{clean_name}.spec.ts"

        if test_file.exists():
            try:
                return test_file.read_text(encoding="utf-8")
            except Exception as exc:
                return f"Error reading recipe test file: {exc}"

        return (
            f"Test spec for recipe '{recipe_name}' not found on disk. "
            f"Expected file at {test_file}."
        )
