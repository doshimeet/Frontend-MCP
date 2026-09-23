"""
Pre-Flight Diagnostic Health Check Module
Validates runtime environment, Node, npm, system Edge browser, and cloud connectivity.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from config import ARTIFACTORY_NPM_REGISTRY, AZURE_DEVOPS_ORG
from core.auth import get_azure_devops_token


def find_system_edge_browser() -> str | None:
    """
    Detects if Microsoft Edge is installed on the host system.
    Supports Windows, macOS, and Linux standard paths.
    """
    # 1. Check PATH executable
    edge_in_path = shutil.which("msedge") or shutil.which("microsoft-edge")
    if edge_in_path:
        return edge_in_path

    # 2. macOS standard location
    mac_edge = Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
    if mac_edge.exists():
        return str(mac_edge)

    # 3. Windows standard locations
    win_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Microsoft\Edge\Application\msedge.exe",
    ]
    for win_path in win_paths:
        if win_path.exists():
            return str(win_path)

    # 4. Fallback to Google Chrome if Edge is absent
    chrome_in_path = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome_in_path:
        return chrome_in_path

    mac_chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac_chrome.exists():
        return str(mac_chrome)

    return None


def check_environment_health() -> dict[str, Any]:
    """
    Runs a full diagnostic check across all system dependencies.
    """
    diagnostics: dict[str, Any] = {
        "status": "healthy",
        "system": {
            "os": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        "runtimes": {},
        "browser_automation": {},
        "enterprise_auth": {},
    }

    # 1. Check Node.js
    node_bin = shutil.which("node")
    if node_bin:
        try:
            node_ver = subprocess.check_output([node_bin, "--version"], text=True).strip()
            diagnostics["runtimes"]["node"] = {"available": True, "version": node_ver, "path": node_bin}
        except Exception:
            diagnostics["runtimes"]["node"] = {"available": False}
    else:
        diagnostics["runtimes"]["node"] = {"available": False}
        diagnostics["status"] = "degraded"

    # 2. Check npm
    npm_bin = shutil.which("npm")
    if npm_bin:
        try:
            npm_ver = subprocess.check_output([npm_bin, "--version"], text=True).strip()
            diagnostics["runtimes"]["npm"] = {"available": True, "version": npm_ver, "path": npm_bin}
        except Exception:
            diagnostics["runtimes"]["npm"] = {"available": False}
    else:
        diagnostics["runtimes"]["npm"] = {"available": False}
        diagnostics["status"] = "degraded"

    # 3. Check System Browser for Playwright
    edge_path = find_system_edge_browser()
    if edge_path:
        diagnostics["browser_automation"]["browser"] = {
            "detected": True,
            "channel": "msedge" if "Edge" in edge_path or "msedge" in edge_path else "chrome",
            "path": edge_path,
        }
    else:
        diagnostics["browser_automation"]["browser"] = {
            "detected": False,
            "warning": "Neither Microsoft Edge nor Chrome detected. Playwright will need system browser.",
        }

    # 4. Check Azure DevOps Token Status
    ado_token = get_azure_devops_token()
    diagnostics["enterprise_auth"]["azure_devops"] = {
        "authenticated": ado_token is not None,
        "token_source": "explicit_pat" if os.getenv("AZURE_DEVOPS_PAT") else ("msal_session" if ado_token else "none"),
        "org_configured": AZURE_DEVOPS_ORG,
    }

    # 5. Check User-Level .npmrc Existence
    user_npmrc = Path.home() / ".npmrc"
    diagnostics["enterprise_auth"]["artifactory"] = {
        "user_npmrc_exists": user_npmrc.exists(),
        "path": str(user_npmrc),
        "registry_target": ARTIFACTORY_NPM_REGISTRY,
    }

    return diagnostics
