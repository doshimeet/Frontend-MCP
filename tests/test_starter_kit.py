"""
Unit and integration tests for Phase 3: Next.js Starter Kit Template (Carbon POC).
Verifies starter kit file tree, dependency contracts, security rules, and FastMCP scaffolding.
"""

import json
import shutil
import sys
from pathlib import Path
import pytest

# Add repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from config import TEMPLATES_DIR
from server import mcp


def test_starter_kit_structure():
    """Verify that templates/frontend-starter contains all required enterprise files."""
    assert TEMPLATES_DIR.exists(), f"Templates directory {TEMPLATES_DIR} does not exist"

    required_files = [
        TEMPLATES_DIR / "package.json",
        TEMPLATES_DIR / "tsconfig.json",
        TEMPLATES_DIR / "next.config.mjs",
        TEMPLATES_DIR / "web.config",
        TEMPLATES_DIR / "copymain.js",
        TEMPLATES_DIR / "app.config.ts",
        TEMPLATES_DIR / "src" / "app" / "layout.tsx",
        TEMPLATES_DIR / "src" / "app" / "page.tsx",
        TEMPLATES_DIR / "src" / "app" / "globals.css",
        TEMPLATES_DIR / "src" / "components" / "Base.tsx",
        TEMPLATES_DIR / "src" / "components" / "MsalAuthentication.tsx",
        TEMPLATES_DIR / "src" / "components" / "AdobeAnalytics.tsx",
        TEMPLATES_DIR / "src" / "components" / "AppInsights.tsx",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"Missing required starter kit file: {file_path}"


def test_starter_kit_package_json_dependencies():
    """Verify package.json includes Next.js, React, @wbg/design-system, and TanStack Query."""
    pkg_file = TEMPLATES_DIR / "package.json"
    with open(pkg_file, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    deps = pkg.get("dependencies", {})
    assert "next" in deps
    assert "react" in deps
    assert "react-dom" in deps
    assert "@wbg/nexus" in deps
    assert "@tanstack/react-query" in deps


def test_starter_kit_npmrc_security():
    """Verify zero .npmrc file policy: No .npmrc exists in template (prevents Git credential leaks)."""
    npmrc_file = TEMPLATES_DIR / ".npmrc"
    assert not npmrc_file.exists(), ".npmrc file must NOT exist in the repository (violates corporate zero-token Git policy)"


@pytest.mark.anyio
async def test_scaffold_greenfield_end_to_end():
    """Verify scaffolding a greenfield app from the starter template via FastMCP tool."""
    test_dir = Path(__file__).resolve().parent.parent / "apps" / "test-verify-scaffold"
    if test_dir.exists():
        shutil.rmtree(test_dir)

    try:
        contents, result = await mcp.call_tool(
            "scaffold_greenfield_app",
            {
                "app_name": "test-verify-scaffold",
                "target_directory": str(test_dir.resolve()),
            },
        )

        assert result["success"] is True
        assert result["app_name"] == "test-verify-scaffold"
        assert (test_dir / "package.json").exists()
        assert (test_dir / "src" / "app" / "page.tsx").exists()
        assert (test_dir / "src" / "components" / "AppShell.tsx").exists()
    finally:
        if test_dir.exists():
            shutil.rmtree(test_dir)
