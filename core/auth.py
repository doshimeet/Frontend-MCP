"""
Azure MSAL & Enterprise Authentication Provider
Supports DefaultAzureCredential (az login, Managed Identity, App Registration)
with fallback to personal access tokens.
"""

from __future__ import annotations

import logging
from typing import Optional
from config import AZURE_DEVOPS_PAT

logger = logging.getLogger("enterprise-mcp.auth")

# Azure DevOps Default OAuth2 Scope
AZURE_DEVOPS_RESOURCE_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"


def get_azure_devops_token() -> Optional[str]:
    """
    Acquires an Azure DevOps bearer token.
    1. Checks if AZURE_DEVOPS_PAT is explicitly set in environment.
    2. Attempts DefaultAzureCredential (inheriting local `az login` MSAL session or Managed Identity).
    3. Returns None if unauthenticated (allowing local fallback to offline template).
    """
    if AZURE_DEVOPS_PAT:
        return AZURE_DEVOPS_PAT

    try:
        from azure.identity import DefaultAzureCredential
        # Set exclude_interactive_browser_credential=True to prevent popup browser windows
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        access_token = credential.get_token(AZURE_DEVOPS_RESOURCE_SCOPE)
        if access_token and access_token.token:
            return access_token.token
    except Exception as exc:
        logger.debug("DefaultAzureCredential token acquisition unavailable: %s", exc)

    return None


def get_ado_headers() -> dict[str, str]:
    """
    Returns standard HTTP headers for Azure DevOps REST API calls.
    """
    token = get_azure_devops_token()
    headers = {
        "Accept": "application/zip, application/json",
        "User-Agent": "Enterprise-Design-System-MCP/1.0",
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
