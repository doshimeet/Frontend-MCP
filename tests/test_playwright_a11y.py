"""
Playwright & Headless Accessibility Verification Test Suite
Tests configuration, automated axe-core scanning, and self-healing loop.
"""

import json
import os
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_vscode_playwright_mcp_configuration():
    """Validates that .vscode/settings.json properly registers the Playwright MCP server."""
    settings_file = REPO_ROOT / ".vscode" / "settings.json"
    assert settings_file.exists(), ".vscode/settings.json must exist"

    with open(settings_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "mcpServers" in data
    assert "playwright" in data["mcpServers"]
    playwright_cfg = data["mcpServers"]["playwright"]
    assert playwright_cfg.get("command") == "npx"
    assert "@modelcontextprotocol/server-playwright" in playwright_cfg.get("args", [])
    assert playwright_cfg.get("env", {}).get("PLAYWRIGHT_BROWSER_CHANNEL") == "msedge"


def test_playwright_config_files():
    """Validates root and template playwright.config.ts exist and configure msedge channel."""
    root_cfg = REPO_ROOT / "playwright.config.ts"
    template_cfg = REPO_ROOT / "templates" / "frontend-starter" / "playwright.config.ts"

    assert root_cfg.exists(), "Root playwright.config.ts must exist"
    assert template_cfg.exists(), "templates/frontend-starter/playwright.config.ts must exist"

    root_content = root_cfg.read_text(encoding="utf-8")
    assert "msedge" in root_content
    assert "defineConfig" in root_content
    assert "headless: true" in root_content

    template_content = template_cfg.read_text(encoding="utf-8")
    assert "msedge" in template_content
    assert "defineConfig" in template_content


def test_verify_a11y_script_structure():
    """Validates that verify-a11y.mjs exists and contains axe-core injection and audit exports."""
    script_path = REPO_ROOT / "scripts" / "verify-a11y.mjs"
    assert script_path.exists(), "scripts/verify-a11y.mjs must exist"

    content = script_path.read_text(encoding="utf-8")
    assert "axe-core" in content
    assert "launchEnterpriseBrowser" in content
    assert "auditHtml" in content
    assert "auditUrl" in content
    assert "color-contrast" in content


def test_self_healing_script_structure():
    """Validates that test-self-healing.mjs exists and defines selfHealUI."""
    script_path = REPO_ROOT / "scripts" / "test-self-healing.mjs"
    assert script_path.exists(), "scripts/test-self-healing.mjs must exist"

    content = script_path.read_text(encoding="utf-8")
    assert "selfHealUI" in content
    assert "runSelfHealingLoop" in content
    assert "$text-primary" in content


def test_headless_a11y_scan_execution():
    """Executes verify-a11y.mjs against compliant HTML and asserts clean pass."""
    node_bin = "node"
    test_snippet = """
    import('./scripts/verify-a11y.mjs').then(async ({ auditHtml }) => {
        const html = '<!DOCTYPE html><html lang="en"><head><title>Test Page</title></head><body><header><nav aria-label="Main"><a href="#">Home</a></nav></header><main><h1>Test Heading</h1><button type="button">Action</button></main></body></html>';
        const res = await auditHtml(html);
        if (!res.success || res.violationsCount !== 0) {
            console.error('Failed:', res.violations);
            process.exit(1);
        }
        process.exit(0);
    }).catch(err => {
        console.error(err);
        process.exit(1);
    });
    """
    env = dict(os.environ)
    node_modules_path = Path("/Users/meetketankumardoshi/Design System/node_modules")
    if node_modules_path.exists():
        existing_node_path = env.get("NODE_PATH", "")
        env["NODE_PATH"] = f"{node_modules_path}:{existing_node_path}" if existing_node_path else str(node_modules_path)

    result = subprocess.run([node_bin, "-e", test_snippet], cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"A11y scan failed: {result.stderr}"


def test_self_healing_loop_execution():
    """Executes the automated self-healing feedback loop and asserts 100% repair success."""
    script_path = REPO_ROOT / "scripts" / "test-self-healing.mjs"
    env = dict(os.environ)
    node_modules_path = Path("/Users/meetketankumardoshi/Design System/node_modules")
    if node_modules_path.exists():
        existing_node_path = env.get("NODE_PATH", "")
        env["NODE_PATH"] = f"{node_modules_path}:{existing_node_path}" if existing_node_path else str(node_modules_path)

    result = subprocess.run(["node", str(script_path)], cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"Self-healing loop execution failed: {result.stderr}\n{result.stdout}"
    assert "SELF-HEALING LOOP VERIFIED: 100% REPAIR SUCCESS" in result.stdout
