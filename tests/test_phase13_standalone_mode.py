"""
Phase 13 Test Suite: Dual-Engine Environment Auto-Detection & Standalone Taste-Tailwind Architecture
Validates:
1. Autonomous environment mode resolution to 'standalone' when offline
2. Anti-mock policy in requirements planning and design rules
3. Complete elimination of legacy @carbon/react imports from starter kit
4. Native Tailwind CSS and PostCSS configuration
5. Multi-page App Router route stubs (/projects, /disbursements)
"""

import json
from pathlib import Path
import pytest
from core.environment import resolve_active_mode
from services.requirements_service import RequirementsService
from config import REPO_ROOT, TEMPLATES_DIR
from server import mcp


def test_environment_mode_defaults_to_standalone_when_offline(monkeypatch):
    """Verify resolve_active_mode() defaults to 'standalone' on local machines without corporate VPN."""
    monkeypatch.delenv("DESIGN_SYSTEM_MODE", raising=False)
    monkeypatch.delenv("WEBSITE_SITE_NAME", raising=False)
    monkeypatch.delenv("MCP_MODE", raising=False)
    monkeypatch.delenv("AZURE_DEVOPS_PAT", raising=False)
    monkeypatch.setenv("ARTIFACTORY_NPM_REGISTRY", "https://artifactory.internal.company.com/artifactory/api/npm/virtual/")

    mode = resolve_active_mode()
    assert mode == "standalone"

    # Explicit override test
    monkeypatch.setenv("DESIGN_SYSTEM_MODE", "standalone")
    assert resolve_active_mode() == "standalone"


def test_requirements_service_standalone_instructions_and_anti_mock():
    """Verify RequirementsService emits anti-mock guidelines and pure Tailwind instructions in standalone mode."""
    svc = RequirementsService()
    plan = svc.plan_architecture("Build an operations 360 portal for global development financing", mode="standalone")

    assert plan.active_mode == "standalone"
    rules_text = " ".join(plan.design_rules_summary)
    assert "Active mode is 'standalone'" in rules_text
    assert "Tailwind CSS" in rules_text
    assert "NEVER synthesize fake mock packages or symlinks" in rules_text
    assert "Do NOT import '@wbg/nexus'" in rules_text


def test_starter_kit_purged_carbon_and_valid_tailwind():
    """Verify templates/frontend-starter has zero @carbon/react references and valid Tailwind configuration."""
    app_shell_path = TEMPLATES_DIR / "src" / "components" / "AppShell.tsx"
    page_path = TEMPLATES_DIR / "src" / "app" / "page.tsx"
    globals_css_path = TEMPLATES_DIR / "src" / "app" / "globals.css"
    tailwind_cfg_path = TEMPLATES_DIR / "tailwind.config.ts"
    postcss_cfg_path = TEMPLATES_DIR / "postcss.config.mjs"

    # 1. Zero Carbon in AppShell
    app_shell_content = app_shell_path.read_text(encoding="utf-8")
    assert "@carbon/react" not in app_shell_content
    assert "<Theme" not in app_shell_content
    assert "HeaderGlobalBar" not in app_shell_content

    # 2. Zero Carbon in page.tsx
    page_content = page_path.read_text(encoding="utf-8")
    assert "@carbon/react" not in page_content
    assert "IBM Carbon v11" not in page_content

    # 3. Valid Tailwind Directives in globals.css
    globals_css = globals_css_path.read_text(encoding="utf-8")
    assert "@tailwind base;" in globals_css
    assert "@tailwind components;" in globals_css
    assert "@tailwind utilities;" in globals_css

    # 4. Valid Tailwind config
    assert tailwind_cfg_path.exists()
    tailwind_cfg = tailwind_cfg_path.read_text(encoding="utf-8")
    assert "var(--nexus-color-primary)" in tailwind_cfg

    # 5. Valid PostCSS config
    postcss_cfg = postcss_cfg_path.read_text(encoding="utf-8")
    assert "tailwindcss:" in postcss_cfg


def test_starter_kit_routes_exist():
    """Verify multi-page App Router stub routes exist to prevent 404 navigation errors."""
    projects_page = TEMPLATES_DIR / "src" / "app" / "projects" / "page.tsx"
    disbursements_page = TEMPLATES_DIR / "src" / "app" / "disbursements" / "page.tsx"

    assert projects_page.exists(), "src/app/projects/page.tsx missing"
    assert disbursements_page.exists(), "src/app/disbursements/page.tsx missing"

    projects_content = projects_page.read_text(encoding="utf-8")
    assert "Projects & Operations Directory" in projects_content

    disbursements_content = disbursements_page.read_text(encoding="utf-8")
    assert "Disbursement Inspector" in disbursements_content


def test_anti_mock_rule_in_wbg_enterprise_rules():
    """Verify Section 1.4 Strict Zero-Mock Policy is codified in wbg-enterprise-rules.md."""
    root_rules = (REPO_ROOT / ".agents" / "skills" / "wbg-enterprise-rules.md").read_text(encoding="utf-8")
    template_rules = (TEMPLATES_DIR / ".agents" / "skills" / "wbg-enterprise-rules.md").read_text(encoding="utf-8")

    for doc in [root_rules, template_rules]:
        assert "### 1.4 Strict Zero-Mock & Anti-Artificial Package Policy" in doc
        assert "Under NO circumstances may an AI agent synthesize artificial mock packages" in doc
        assert "Standalone Engine Fallback" in doc


@pytest.mark.anyio
async def test_get_page_recipe_standalone_mode(monkeypatch):
    """Verify get_page_recipe tool in standalone mode returns typed response with standalone mode."""
    monkeypatch.setenv("DESIGN_SYSTEM_MODE", "standalone")
    contents, res = await mcp.call_tool("get_page_recipe", {"recipe_name": "CrudTableRecipe"})

    assert res["target_mode"] == "standalone"
    assert "Active Mode: Standalone" in res["component_code"]
