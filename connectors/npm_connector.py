"""
NPM & Artifactory Registry Connector
Inspects workstation ~/.npmrc configuration and validates enterprise package routing.
"""

from pathlib import Path
from typing import Dict, Any
from config import ARTIFACTORY_NPM_REGISTRY


class NpmRegistryConnector:
    """Checks user-level .npmrc and registry connectivity."""

    def __init__(self, registry_url: str = ARTIFACTORY_NPM_REGISTRY):
        self.registry_url = registry_url
        self.user_npmrc_path = Path.home() / ".npmrc"

    def get_npmrc_status(self) -> Dict[str, Any]:
        """Returns details on the developer's workstation .npmrc file."""
        exists = self.user_npmrc_path.exists()
        has_auth_entry = False

        if exists:
            try:
                content = self.user_npmrc_path.read_text(encoding="utf-8")
                has_auth_entry = "_authToken" in content or "always-auth" in content
            except Exception:
                pass

        return {
            "user_npmrc_exists": exists,
            "path": str(self.user_npmrc_path),
            "registry_target": self.registry_url,
            "has_auth_entry": has_auth_entry,
        }
