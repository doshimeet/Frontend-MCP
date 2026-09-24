"""
Unit & Integration Tests for Phase 6: Enterprise Production Hardening & Alignment
Validates tool renaming, backward-compatible aliases, native a11y auditing,
dynamic Storybook harvesting, WBG token theme, and starter kit enhancements.
"""

import sys
import json
from pathlib import Path
import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from config import REPO_ROOT, TOKENS_DIR
from services.token_service import TokenService
from services.requirements_service import RequirementsService
from services.a11y_service import A11yService
from connectors.storybook_connector import StorybookConnector
from models.a11y import A11yAuditReport, A11yViolation
from server import mcp


@pytest.mark.anyio
async def test_tool_renaming_and_aliases_registered():
    """Verify that all friendly tool names and their aliases are actively registered on FastMCP."""
    tool_defs = await mcp.list_tools()
    tool_names = [tool.name for tool in tool_defs]

    # Scaffolding tools
    assert "create_enterprise_app" in tool_names
    assert "scaffold_greenfield_app" in tool_names

    # Brownfield integration tools
    assert "extend_existing_app" in tool_names
    assert "integrate_into_existing_app" in tool_names

    # Health & diagnostics tools
    assert "check_system_health" in tool_names
    assert "run_environment_health_check" in tool_names

    # Requirements & planning tools
    assert "plan_application_architecture" in tool_names
    assert "plan_application_from_requirements" in tool_names

    # Native accessibility tool
    assert "audit_accessibility" in tool_names


def test_wbg_enterprise_token_theme():
    """Verify that the World Bank Group DTCG token theme loads with official tokens."""
    token_service = TokenService()
    tokens = token_service.get_theme_tokens("wbg-enterprise")

    assert tokens.theme_name == "wbg-enterprise"
    assert tokens.color.get("primary").value == "#002244"
    assert tokens.color.get("brand_blue").value == "#0071bc"
    assert tokens.color.get("accent_cyan").value == "#00a3e0"
    assert tokens.color.get("classification_banner").value == "#ffcc00"


def test_dynamic_entity_route_discovery():
    """Verify RequirementsService dynamically discovers domain entities for routes."""
    req_service = RequirementsService()

    # Case 1: Tenders / Procurement
    blueprint = req_service.plan_architecture(
        "Build a procurement system to audit vendor tenders and display annual metrics."
    )
    paths = [r.path for r in blueprint.recommended_routes]
    assert "/" in paths
    assert "/tenders" in paths

    # Case 2: Disbursements
    blueprint2 = req_service.plan_architecture(
        "We need a finance tool to review disbursements and monitor transfer logs."
    )
    paths2 = [r.path for r in blueprint2.recommended_routes]
    assert "/disbursements" in paths2



def test_dynamic_storybook_harvester_fallback_and_caching(tmp_path):
    """Verify StorybookConnector harvests catalog and caches to disk properly."""
    connector = StorybookConnector(endpoint_url=None, cache_dir=tmp_path)
    catalog = connector.harvest_catalog()

    assert "Button" in catalog
    assert "DataTable" in catalog
    assert "Header" in catalog
    assert "Select" in catalog
    assert "Tile" in catalog

    # Verify disk cache was written
    cache_file = tmp_path / "storybook_catalog.json"
    assert cache_file.exists()


def test_a11y_service_handles_unreachable_gracefully():
    """Verify A11yService produces a valid structured report even if server is unreachable."""
    a11y_service = A11yService()
    # Query a non-existent port
    report = a11y_service.audit_url(url="http://localhost:59999", timeout_sec=5)

    assert isinstance(report, A11yAuditReport)
    assert report.success is False
    assert report.violationsCount >= 1
    assert len(report.remediations) > 0


def test_starter_kit_phase6_artifacts():
    """Verify starter kit files for i18n, query provider, auth provider, and Playwright test."""
    starter_dir = REPO_ROOT / "templates" / "frontend-starter"

    # Package.json dependencies
    pkg_json_path = starter_dir / "package.json"
    with open(pkg_json_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    assert "@tanstack/react-query" in pkg["dependencies"]
    assert "@playwright/test" in pkg["devDependencies"]
    assert "axe-core" in pkg["devDependencies"]
    assert "test:report" in pkg["scripts"]

    # Providers and hooks
    assert (starter_dir / "src" / "providers" / "QueryProvider.tsx").exists()
    assert (starter_dir / "src" / "components" / "auth" / "AuthProvider.tsx").exists()
    assert (starter_dir / "src" / "hooks" / "useTranslation.ts").exists()

    # Locale files
    assert (starter_dir / "messages" / "en.json").exists()
    assert (starter_dir / "messages" / "fr.json").exists()
    assert (starter_dir / "messages" / "es.json").exists()

    # E2E test suite in corporate location
    assert (starter_dir / "src" / "tests" / "home.spec.ts").exists()
    assert (starter_dir / "scripts" / "generate-scorecard.mjs").exists()
