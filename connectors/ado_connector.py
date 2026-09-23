"""
Azure DevOps REST API Connector
Handles MSAL bearer authentication and downloads starter repository .zip archives.
"""

import io
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from config import (
    AZURE_DEVOPS_ORG,
    AZURE_DEVOPS_PROJECT,
    AZURE_DEVOPS_STARTER_REPO_ID,
    TEMPLATES_DIR,
)
from core.auth import get_ado_headers, get_azure_devops_token


class AzureDevOpsConnector:
    """Connects to Azure DevOps Git REST API using MSAL or PAT authentication."""

    def __init__(self, org_url: Optional[str] = None, project: Optional[str] = None, repo_id: Optional[str] = None):
        self.org_url = (org_url or AZURE_DEVOPS_ORG).rstrip("/")
        self.project = project or AZURE_DEVOPS_PROJECT
        self.repo_id = repo_id or AZURE_DEVOPS_STARTER_REPO_ID

    def is_authenticated(self) -> bool:
        """Returns True if a valid MSAL or PAT token is available."""
        return get_azure_devops_token() is not None

    def download_starter_archive(self, target_directory: Path) -> Dict[str, Any]:
        """
        Downloads starter template from Azure DevOps REST API as .zip and extracts it.
        Falls back to local `templates/frontend-starter` for offline/POC execution.
        """
        target_directory.mkdir(parents=True, exist_ok=True)

        is_real_ado = not self.org_url.endswith("enterprise-org")
        if is_real_ado and self.is_authenticated():
            api_url = (
                f"{self.org_url}/{self.project}/_apis/git/repositories/"
                f"{self.repo_id}/items?recursionLevel=full&$format=zip&api-version=6.0"
            )
            headers = get_ado_headers()

            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.get(api_url, headers=headers)
                    if response.status_code == 200:
                        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                            z.extractall(target_directory)
                        return {
                            "success": True,
                            "source": "azure_devops_rest_api",
                            "message": f"Successfully downloaded starter kit from Azure DevOps repo '{self.repo_id}'.",
                        }
            except Exception as exc:
                pass

        # Local Template Fallback (POC & Offline development)
        if TEMPLATES_DIR.exists() and any(TEMPLATES_DIR.iterdir()):
            for item in TEMPLATES_DIR.iterdir():
                dest = target_directory / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

            return {
                "success": True,
                "source": "local_starter_template",
                "message": "Scaffolded application using enterprise starter template.",
            }

        return {
            "success": False,
            "source": "none",
            "message": f"Neither Azure DevOps nor local template directory ({TEMPLATES_DIR}) could be found.",
        }
