"""
Enterprise Multi-Environment & Mode Auto-Detection Module
Supports 3 operational modes:
1. 'carbon': Local non-enterprise / personal laptop (public npm @carbon/react, zero corporate VPN/Artifactory needed)
2. 'wbg': Local enterprise World Bank Group workstation (@wbg/design-system, private Artifactory)
3. 'cloud': Hosted in Azure App Service Linux Python 3.11 container (Oryx, SSE, ADO REST)
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Literal, Optional, List
import urllib.request

EnvironmentMode = Literal["carbon", "wbg", "cloud"]

CANDIDATE_DEV_PORTS: List[int] = [3000, 3001, 4200, 5173]


def is_port_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Checks whether a local port is actively accepting TCP connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def find_active_dev_port(preferred_port: Optional[int] = None) -> Optional[int]:
    """
    Probes candidate frontend ports in priority order:
    1. Preferred port (if provided)
    2. Candidate list: 3000, 3001, 4200, 5173
    Returns the first port actively listening, or None if none are reachable.
    """
    if preferred_port and is_port_listening(preferred_port):
        return preferred_port

    for port in CANDIDATE_DEV_PORTS:
        if is_port_listening(port):
            return port

    return None


def find_active_dev_url(default_url: str = "http://localhost:3000") -> str:
    """
    Resolves the active local application URL by checking candidate ports.
    If default_url is active, returns it. Otherwise probes 3000, 3001, 4200, 5173.
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(default_url)
        if parsed.port and is_port_listening(parsed.port, host=parsed.hostname or "127.0.0.1"):
            return default_url
    except Exception:
        pass

    active_port = find_active_dev_port()
    if active_port:
        return f"http://localhost:{active_port}"

    return default_url


def is_wbg_artifactory_reachable(timeout: float = 1.0) -> bool:
    """Checks if the internal World Bank Group Artifactory is reachable."""
    artifactory_url = os.getenv(
        "ARTIFACTORY_NPM_REGISTRY",
        "https://artifactory.internal.company.com/artifactory/api/npm/virtual/"
    )
    if "internal.company.com" in artifactory_url:
        return False
    try:
        req = urllib.request.Request(artifactory_url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status in (200, 401, 403)
    except Exception:
        return False


def has_wbg_credentials() -> bool:
    """Checks if Azure DevOps PAT or WBG corporate authentication is present."""
    pat = os.getenv("AZURE_DEVOPS_PAT")
    if pat and len(pat) > 10:
        return True
    return False


def resolve_active_mode() -> EnvironmentMode:
    """
    Resolves the active operational mode across 3 environments:
    - Manual override via DESIGN_SYSTEM_MODE ('carbon', 'wbg', 'cloud')
    - Cloud: Detected via WEBSITE_SITE_NAME or MCP_MODE == 'uvicorn'
    - Local WBG: Detected via reachable Artifactory or active Azure DevOps PAT
    - Local Carbon (Fallback): For personal laptops / non-enterprise machines without Artifactory
    """
    explicit = os.getenv("DESIGN_SYSTEM_MODE", "auto").strip().lower()
    if explicit in ("carbon", "wbg", "cloud"):
        return explicit  # type: ignore

    # 1. Cloud Mode (Azure App Service)
    if os.getenv("WEBSITE_SITE_NAME") or os.getenv("MCP_MODE", "").lower() == "uvicorn":
        return "cloud"

    # 2. Local WBG Enterprise Mode
    if is_wbg_artifactory_reachable() or has_wbg_credentials():
        return "wbg"

    # 3. Local Carbon Mode (Fallback for personal laptops and offline development)
    return "carbon"
