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
    AZURE_DEVOPS_STARTER_BRANCH,
    TEMPLATES_DIR,
)
from core.auth import get_ado_headers, get_azure_devops_token


class AzureDevOpsConnector:
    """Connects to Azure DevOps Git REST API using MSAL or PAT authentication."""

    def __init__(
        self,
        org_url: Optional[str] = None,
        project: Optional[str] = None,
        repo_id: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        self.org_url = (org_url or AZURE_DEVOPS_ORG).rstrip("/")
        self.project = project or AZURE_DEVOPS_PROJECT
        self.repo_id = repo_id or AZURE_DEVOPS_STARTER_REPO_ID
        self.branch = branch or AZURE_DEVOPS_STARTER_BRANCH

    def is_authenticated(self) -> bool:
        """Returns True if a valid MSAL or PAT token is available."""
        return get_azure_devops_token() is not None

    def refresh_starter_snapshot(self) -> bool:
        """
        Attempts to refresh the local fallback starter snapshot from Azure DevOps during cloud startup.
        Uses POSIX atomic directory staging and swap (.staging -> .bak) to guarantee:
        1. No partially copied/corrupt template states on download or extraction failure.
        2. Upstream deleted files are properly removed.
        3. Automatic rollback to previous valid snapshot if validation fails.
        """
        from config import IS_LIVE_ADO_CONFIGURED
        if not (IS_LIVE_ADO_CONFIGURED and self.is_authenticated()):
            return False

        staging_dir = TEMPLATES_DIR.parent / f"{TEMPLATES_DIR.name}.staging"
        backup_dir = TEMPLATES_DIR.parent / f"{TEMPLATES_DIR.name}.bak"

        try:
            # 1. Clean any leftover staging directory
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            staging_dir.mkdir(parents=True, exist_ok=True)

            # 2. Download and unpack directly into staging
            res = self.download_starter_archive(staging_dir)
            if not (res.get("success") and res.get("source") == "azure_devops_rest_api"):
                if staging_dir.exists():
                    shutil.rmtree(staging_dir)
                return False

            # 3. Integrity validation: verify essential files exist and are non-empty
            essential_files = ["package.json", "src/app/layout.tsx"]
            for rel_file in essential_files:
                target_check = staging_dir / rel_file
                if not target_check.exists() or target_check.stat().st_size == 0:
                    shutil.rmtree(staging_dir)
                    return False

            # 4. Atomic directory swap
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            if TEMPLATES_DIR.exists():
                shutil.move(str(TEMPLATES_DIR), str(backup_dir))

            shutil.move(str(staging_dir), str(TEMPLATES_DIR))

            # 5. Clean up backup on confirmed success
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            return True

        except Exception:
            # Rollback if backup exists and TEMPLATES_DIR was displaced
            if backup_dir.exists() and not TEMPLATES_DIR.exists():
                shutil.move(str(backup_dir), str(TEMPLATES_DIR))
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            return False

    def download_starter_archive(self, target_directory: Path) -> Dict[str, Any]:
        """
        Downloads starter template from Azure DevOps REST API as .zip and extracts it.
        Falls back to local `templates/frontend-starter` for offline/POC execution.
        """
        target_directory.mkdir(parents=True, exist_ok=True)

        from config import IS_LIVE_ADO_CONFIGURED
        if IS_LIVE_ADO_CONFIGURED and self.is_authenticated():
            api_url = (
                f"{self.org_url}/{self.project}/_apis/git/repositories/"
                f"{self.repo_id}/items?recursionLevel=full&$format=zip"
                f"&versionDescriptor.version={self.branch}"
                f"&versionDescriptor.versionType=branch"
                f"&api-version=6.0"
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
                            "message": f"Successfully downloaded starter kit from Azure DevOps repo '{self.repo_id}' branch '{self.branch}'.",
                        }
            except Exception:
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
