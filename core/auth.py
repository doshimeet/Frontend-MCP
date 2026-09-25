"""
Azure MSAL & Enterprise Authentication Provider
Supports DefaultAzureCredential (az login, Managed Identity, App Registration)
with fallback to personal access tokens.
Strictly hardened against link-local IMDS hangs on enterprise developer laptops.
"""

from __future__ import annotations

import os
import time
import logging
from typing import Optional
from config import AZURE_DEVOPS_PAT

logger = logging.getLogger("nexus-mcp.auth")

# Azure DevOps Default OAuth2 Scope
AZURE_DEVOPS_RESOURCE_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"

# Token cache: (token_str, expiry_epoch)
_TOKEN_CACHE: tuple[str, float] | None = None


def get_azure_devops_token() -> Optional[str]:
    """
    Acquires an Azure DevOps bearer token.
    1. Checks in-memory cache for valid unexpired token.
    2. In Cloud mode (Azure App Service): Managed Identity via DefaultAzureCredential is primary.
    3. In Local mode: Fast-path AZURE_DEVOPS_PAT avoids probe hangs; otherwise local az login session.
    4. Caches acquired tokens with 5-minute safety margin.
    """
    global _TOKEN_CACHE
    now = time.time()

    if _TOKEN_CACHE:
        cached_token, expiry = _TOKEN_CACHE
        if now < expiry - 300:  # 5 minute safety buffer
            return cached_token

    is_cloud_runtime = bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("WEBSITE_INSTANCE_ID"))

    # In Cloud runtime: Managed Identity is strictly primary
    if is_cloud_runtime:
        logger.info("[auth] Cloud runtime detected (%s). Acquiring token via Managed Identity...", os.getenv("WEBSITE_SITE_NAME", "AppService"))
        token = _acquire_default_azure_credential_token(is_cloud=True)
        if token:
            _TOKEN_CACHE = (token, now + 3600)
            return token
        if AZURE_DEVOPS_PAT:
            logger.info("[auth] Falling back to configured AZURE_DEVOPS_PAT in cloud runtime.")
            return AZURE_DEVOPS_PAT
        logger.warning("[auth] No valid Azure DevOps token acquired in cloud runtime.")
        return None

    # In Local runtime: PAT is fast-path if provided
    if AZURE_DEVOPS_PAT:
        logger.info("[auth] Local runtime: Fast-path AZURE_DEVOPS_PAT detected. Skipping Azure IMDS probe.")
        return AZURE_DEVOPS_PAT

    logger.info("[auth] Local runtime: No PAT configured. Probing developer tools (az login / VS Code session)...")
    token = _acquire_default_azure_credential_token(is_cloud=False)
    if token:
        _TOKEN_CACHE = (token, now + 3600)
        logger.info("[auth] Successfully acquired token from developer login session.")
        return token

    logger.info("[auth] Local runtime: No Azure DevOps credentials available. Continuing in unauthenticated mode.")
    return None


def _acquire_default_azure_credential_token(is_cloud: bool = False) -> Optional[str]:
    """
    Attempts to acquire token from DefaultAzureCredential without interactive popup.
    On local workstations, suppresses ManagedIdentity / WorkloadIdentity to avoid
    stalling behind corporate firewalls on link-local IMDS (169.254.169.254).
    """
    try:
        from azure.identity import DefaultAzureCredential
        if is_cloud:
            credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        else:
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=True,
                exclude_managed_identity_credential=True,
                exclude_workload_identity_credential=True,
            )
        access_token = credential.get_token(AZURE_DEVOPS_RESOURCE_SCOPE)
        if access_token and access_token.token:
            return access_token.token
    except Exception as exc:
        logger.debug("[auth] DefaultAzureCredential token acquisition unavailable: %s", exc)
    return None


def get_ado_headers() -> dict[str, str]:
    """
    Returns standard HTTP headers for Azure DevOps REST API calls.
    """
    token = get_azure_devops_token()
    headers = {
        "Accept": "application/zip, application/json",
        "User-Agent": "Enterprise-Design-System-MCP/2.0",
    }
    if token:
        # If token is standard PAT, basic auth is supported, or Bearer for OAuth2/MSAL
        if len(token) > 100 or token.startswith("eyJ"):
            headers["Authorization"] = f"Bearer {token}"
        else:
            # Personal Access Token format
            import base64
            b64_pat = base64.b64encode(f":{token}".encode()).decode()
            headers["Authorization"] = f"Basic {b64_pat}"

    return headers
