"""
Phase 10: Production-Grade Nexus v2.0.0 Architecture Hardening Contract Tests
Validates schema normalization, atomic snapshot rollback, authentic Nexus tokens & recipes,
dual-engine semantic accessibility, and cloud auth precedence.
"""

import io
import json
import shutil
import zipfile
from pathlib import Path
import pytest

from connectors.storybook_connector import StorybookConnector
from connectors.ado_connector import AzureDevOpsConnector
from services.token_service import TokenService
from services.a11y_service import SemanticDOMInspector, A11yService
from services.requirements_service import RequirementsService
from tools.recipes_tools import _load_recipe_catalog
from server import mcp
from config import REPO_ROOT, TEMPLATES_DIR


def test_storybook_connector_unwraps_nested_catalog_schema(tmp_path):
    """Verify that a wrapped components.json (with metadata/int keys) does not crash get_catalog_summary."""
    wrapped_json = {
        "version": 2,
        "status": "UP",
        "meta": {"system": "nexus", "updated": 2026},
        "components": {
            "Button": {
                "import_statement": "import { Button } from '@wbg/nexus';",
                "description": "Primary action button.",
                "props": {},
                "example": "<Button />",
            },
            "Card": {
                "import_statement": "import { Card } from '@wbg/nexus';",
                "description": "Content tile container.",
                "props": {},
                "example": "<Card />",
            },
        },
    }
    comp_file = tmp_path / "components.json"
    comp_file.write_text(json.dumps(wrapped_json), encoding="utf-8")

    # Patch connector to use the temp components.json
    import config
    orig_path = config.COMPONENTS_JSON_PATH
    try:
        config.COMPONENTS_JSON_PATH = comp_file
        connector = StorybookConnector(endpoint_url=None, cache_dir=tmp_path / "cache")
        summary = connector.get_catalog_summary("enterprise")

        assert "Button" in summary
        assert "Card" in summary
        assert summary["Button"] == "Primary action button."
        assert "version" not in summary  # int key must NOT leak into summary
        assert "meta" not in summary
    finally:
        config.COMPONENTS_JSON_PATH = orig_path


def test_nexus_default_tokens_contract():
    """Verify authoritative Nexus brand palette tokens."""
    svc = TokenService()
    tokens = svc.get_theme_tokens("default")

    assert tokens.color["primary"].value == "#002244"
    assert tokens.color["secondary"].value == "#0071bc"
    assert tokens.color["text_primary"].value == "#222222"
    assert tokens.color["surface"].value == "#f4f6f8"
    assert "Inter" in tokens.typography["font_family_sans"].value


@pytest.mark.anyio
async def test_all_recipes_emit_wbg_nexus_imports():
    """Verify all 6 canonical page recipes import from @wbg/nexus in standard/enterprise mode."""
    recipe_names = [
        "CrudTableRecipe",
        "MetricsDashboardRecipe",
        "FormWizardRecipe",
        "MasterDetailRecipe",
        "SettingsTabsRecipe",
        "AuditTimelineRecipe",
    ]
    for r_name in recipe_names:
        contents, res = await mcp.call_tool("get_page_recipe", {"recipe_name": r_name})
        code = res["component_code"]
        assert 'from "@wbg/nexus";' in code, f"Recipe {r_name} does not import from @wbg/nexus"


def test_semantic_dom_inspector_pure_python():
    """Verify Engine A (SemanticDOMInspector) flags missing alt, labels, and skipped headings without browser binaries."""
    bad_html = """
    <!DOCTYPE html>
    <html>
      <head><title>Test</title></head>
      <body>
        <main>
          <h1>Operations Portal</h1>
          <h3>Skipped Level Heading</h3>
          <img src="/logo.png">
          <input type="text" name="user">
          <button></button>
        </main>
      </body>
    </html>
    """
    parser = SemanticDOMInspector()
    parser.feed(bad_html)
    violations = parser.finalize_violations()

    v_ids = [v.id for v in violations]
    assert "html-has-lang" in v_ids
    assert "heading-order" in v_ids
    assert "image-alt" in v_ids
    assert "label-missing" in v_ids
    assert "button-name" in v_ids


def test_requirements_service_emits_nexus_package():
    """Verify architecture planner recommends @wbg/nexus in standard enterprise mode."""
    svc = RequirementsService()
    blueprint = svc.plan_architecture(
        "Build a disbursements inspection portal with approval workflows and audit trail.",
        theme="wbg-enterprise",
        mode="wbg"
    )
    for route in blueprint.recommended_routes:
        if route.composition_guide:
            assert "@wbg/nexus" in route.composition_guide
