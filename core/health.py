"""
Pre-Flight Diagnostic Health Check Module
Validates runtime environment, Node, npm, system Edge browser, and cloud connectivity.
Hardened with subprocess timeouts and Windows batch shim resolution to prevent stalls.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from config import ARTIFACTORY_NPM_REGISTRY, AZURE_DEVOPS_ORG
from core.auth import get_azure_devops_token

logger = logging.getLogger("nexus-mcp.health")


def resolve_binary(binary_name: str) -> str | None:
    """
    Resolves executable path cross-platform.
    On Windows, explicitly prioritizes .cmd / .exe to prevent CreateProcess hangs on shell scripts.
    """
    if sys.platform == "win32":
        for ext in [".cmd", ".exe", ".bat", ""]:
            cand = shutil.which(f"{binary_name}{ext}")
            if cand:
                return cand
    return shutil.which(binary_name)


def check_command_version(binary_path: str, timeout: float = 3.0) -> tuple[bool, str | None, str | None]:
    """
    Safely executes <binary_path> --version with timeout protection.
    Returns (success, version_str, error_message).
    """
    start_time = time.time()
    try:
        logger.debug("[health:exec] Executing '%s --version' (timeout=%.1fs)...", binary_path, timeout)
        output = subprocess.check_output(
            [binary_path, "--version"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        ).strip()
        elapsed = time.time() - start_time
        logger.info("[health:exec] '%s' returned version '%s' in %.2fs", binary_path, output, elapsed)
        return True, output, None
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        msg = f"Timed out after {timeout:.1f}s executing '{binary_path} --version'"
        logger.warning("[health:exec:timeout] %s (elapsed %.2fs)", msg, elapsed)
        return False, None, msg
    except Exception as exc:
        elapsed = time.time() - start_time
        msg = f"Failed executing '{binary_path} --version': {exc}"
        logger.warning("[health:exec:error] %s (elapsed %.2fs)", msg, elapsed)
        return False, None, msg


def find_system_edge_browser() -> str | None:
    """
    Detects if Microsoft Edge is installed on the host system.
    Supports Windows, macOS, and Linux standard paths.
    """
    logger.debug("[health:browser] Probing for Microsoft Edge or Chrome system browser...")
    # 1. Check PATH executable
    edge_in_path = shutil.which("msedge") or shutil.which("microsoft-edge")
    if edge_in_path:
        logger.debug("[health:browser] Found Edge in PATH: %s", edge_in_path)
        return edge_in_path

    # 2. macOS standard location
    mac_edge = Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
    if mac_edge.exists():
        logger.debug("[health:browser] Found Edge at macOS standard path: %s", mac_edge)
        return str(mac_edge)

    # 3. Windows standard locations
    win_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Microsoft\Edge\Application\msedge.exe",
    ]
    for win_path in win_paths:
        if win_path.exists():
            logger.debug("[health:browser] Found Edge at Windows path: %s", win_path)
            return str(win_path)

    # 4. Fallback to Google Chrome if Edge is absent
    chrome_in_path = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome_in_path:
        logger.debug("[health:browser] Found Chrome in PATH: %s", chrome_in_path)
        return chrome_in_path

    mac_chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac_chrome.exists():
        logger.debug("[health:browser] Found Chrome at macOS standard path: %s", mac_chrome)
        return str(mac_chrome)

    logger.debug("[health:browser] Neither Edge nor Chrome detected on host.")
    return None


def check_environment_health() -> dict[str, Any]:
    """
    Runs a full diagnostic check across all system dependencies.
    All subprocess calls are timeout-guarded (3.0s) and Windows-shim aware.
    """
    start_time = time.time()
    logger.info("[health] Starting environment diagnostic health check...")

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
    node_bin = resolve_binary("node")
    if node_bin:
        success, node_ver, error_msg = check_command_version(node_bin, timeout=3.0)
        diagnostics["runtimes"]["node"] = {
            "available": success,
            "version": node_ver if success else f"degraded: {error_msg}",
            "path": node_bin,
        }
        if not success:
            diagnostics["status"] = "degraded"
    else:
        logger.warning("[health] Node.js executable not found in PATH")
        diagnostics["runtimes"]["node"] = {"available": False, "error": "Executable not found"}
        diagnostics["status"] = "degraded"

    # 2. Check npm (Windows .cmd aware)
    npm_bin = resolve_binary("npm")
    if npm_bin:
        success, npm_ver, error_msg = check_command_version(npm_bin, timeout=3.0)
        diagnostics["runtimes"]["npm"] = {
            "available": success,
            "version": npm_ver if success else f"degraded: {error_msg}",
            "path": npm_bin,
        }
        if not success:
            diagnostics["status"] = "degraded"
    else:
        logger.warning("[health] npm executable not found in PATH")
        diagnostics["runtimes"]["npm"] = {"available": False, "error": "Executable not found"}
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

    logger.info("[health] Health check completed in %.2fs. Overall status: %s", time.time() - start_time, diagnostics["status"])
    return diagnostics
