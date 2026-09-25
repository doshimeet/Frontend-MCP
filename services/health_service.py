"""
Health & Environment Diagnostics Service
Runs comprehensive pre-flight verification on developer workstations or cloud containers.
Hardened with subprocess timeouts and Windows batch shim resolution to prevent stalls.
"""

import logging
import os
import sys
import time
from pathlib import Path

from config import ARTIFACTORY_NPM_REGISTRY, AZURE_DEVOPS_ORG
from core.auth import get_azure_devops_token
from core.health import find_system_edge_browser, resolve_binary, check_command_version
from models.health import (
    RuntimeInfo,
    BrowserInfo,
    EnterpriseAuthInfo,
    ArtifactoryAuthInfo,
    HealthReport,
)

logger = logging.getLogger("nexus-mcp.health")


class HealthService:
    """Performs diagnostic checks on system dependencies and enterprise authentication."""

    def run_diagnostics(self) -> HealthReport:
        """Collects runtime diagnostics and returns a typed HealthReport."""
        start_time = time.time()
        logger.info("[service:health] Collecting runtime diagnostics...")

        # 1. Node.js check (timeout-guarded)
        node_bin = resolve_binary("node")
        node_ver = None
        node_available = False
        if node_bin:
            success, ver, err = check_command_version(node_bin, timeout=3.0)
            if success:
                node_ver = ver
                node_available = True
            else:
                node_ver = f"degraded: {err}"
                node_available = False
        else:
            logger.warning("[service:health] Node.js binary not resolved in PATH")

        node_info = RuntimeInfo(available=node_available, version=node_ver, path=node_bin)

        # 2. npm check (Windows-shim and timeout-guarded)
        npm_bin = resolve_binary("npm")
        npm_ver = None
        npm_available = False
        if npm_bin:
            success, ver, err = check_command_version(npm_bin, timeout=3.0)
            if success:
                npm_ver = ver
                npm_available = True
            else:
                npm_ver = f"degraded: {err}"
                npm_available = False
        else:
            logger.warning("[service:health] npm binary not resolved in PATH")

        npm_info = RuntimeInfo(available=npm_available, version=npm_ver, path=npm_bin)

        # 3. System Browser check
        edge_path = find_system_edge_browser()
        if edge_path:
            browser_info = BrowserInfo(
                detected=True,
                channel="msedge" if "Edge" in edge_path or "msedge" in edge_path else "chrome",
                path=edge_path,
                warning=None,
            )
        else:
            browser_info = BrowserInfo(
                detected=False,
                channel=None,
                path=None,
                warning="Neither Microsoft Edge nor Chrome detected on system.",
            )

        # 4. Azure DevOps Auth check
        ado_token = get_azure_devops_token()
        token_source = "explicit_pat" if os.getenv("AZURE_DEVOPS_PAT") else ("msal_session" if ado_token else "none")
        ado_info = EnterpriseAuthInfo(
            authenticated=ado_token is not None,
            token_source=token_source,
            org_configured=AZURE_DEVOPS_ORG,
        )

        # 5. Artifactory ~/.npmrc check
        user_npmrc = Path.home() / ".npmrc"
        artifactory_info = ArtifactoryAuthInfo(
            user_npmrc_exists=user_npmrc.exists(),
            path=str(user_npmrc),
            registry_target=ARTIFACTORY_NPM_REGISTRY,
        )

        status = "healthy" if (node_available and npm_available) else "degraded"
        logger.info("[service:health] HealthReport generated in %.2fs. Overall status: %s", time.time() - start_time, status)

        return HealthReport(
            status=status,
            system_os=sys.platform,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            node=node_info,
            npm=npm_info,
            browser=browser_info,
            azure_devops=ado_info,
            artifactory=artifactory_info,
        )
