"""
Health & Environment Diagnostics Service
Runs comprehensive pre-flight verification on developer workstations or cloud containers.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from config import ARTIFACTORY_NPM_REGISTRY, AZURE_DEVOPS_ORG
from core.auth import get_azure_devops_token
from core.health import find_system_edge_browser
from models.health import (
    RuntimeInfo,
    BrowserInfo,
    EnterpriseAuthInfo,
    ArtifactoryAuthInfo,
    HealthReport,
)


class HealthService:
    """Performs diagnostic checks on system dependencies and enterprise authentication."""

    def run_diagnostics(self) -> HealthReport:
        """Collects runtime diagnostics and returns a typed HealthReport."""
        # 1. Node.js check
        node_bin = shutil.which("node")
        node_ver = None
        if node_bin:
            try:
                node_ver = subprocess.check_output([node_bin, "--version"], text=True).strip()
            except Exception:
                pass
        node_info = RuntimeInfo(available=node_bin is not None, version=node_ver, path=node_bin)

        # 2. npm check
        npm_bin = shutil.which("npm")
        npm_ver = None
        if npm_bin:
            try:
                npm_ver = subprocess.check_output([npm_bin, "--version"], text=True).strip()
            except Exception:
                pass
        npm_info = RuntimeInfo(available=npm_bin is not None, version=npm_ver, path=npm_bin)

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

        status = "healthy" if (node_bin and npm_bin) else "degraded"

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
