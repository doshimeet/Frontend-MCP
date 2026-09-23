"""
Azure DevOps REST API Client
Downloads starter repository as clean .zip archive with local template fallback.
"""

from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path
from typing import Any
import httpx

from config import (
    AZURE_DEVOPS_ORG,
    AZURE_DEVOPS_PROJECT,
    AZURE_DEVOPS_STARTER_REPO_ID,
    TEMPLATES_DIR,
)
from core.auth import get_ado_headers


def download_ado_starter_kit(target_directory: Path) -> dict[str, Any]:
    """
    Downloads the starter kit repository from Azure DevOps via REST API.
    If Azure DevOps is not configured or unreachable, falls back to the
    local template in `templates/frontend-starter`.
    """
    target_directory.mkdir(parents=True, exist_ok=True)

    # 1. Attempt Azure DevOps REST API download if configured with real org
    is_real_ado = not AZURE_DEVOPS_ORG.endswith("enterprise-org")
    if is_real_ado:
        clean_org = AZURE_DEVOPS_ORG.rstrip("/")
        api_url = (
            f"{clean_org}/{AZURE_DEVOPS_PROJECT}/_apis/git/repositories/"
            f"{AZURE_DEVOPS_STARTER_REPO_ID}/items?recursionLevel=full&$format=zip&api-version=6.0"
        )
        headers = get_ado_headers()

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(api_url, headers=headers)
                if response.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        z.extractall(target_directory)
                    return {
                        "status": "success",
                        "source": "azure_devops_rest_api",
                        "target_directory": str(target_directory),
                        "message": "Successfully downloaded starter kit from Azure DevOps REST API.",
                    }
        except Exception as exc:
            # Fall back to local template on network error
            pass

    # 2. Local Template Fallback (for POC & offline development)
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
            "status": "success",
            "source": "local_starter_template",
            "target_directory": str(target_directory),
            "message": "Scaffolded application using standard enterprise starter template.",
        }

    return {
        "status": "error",
        "message": f"Neither Azure DevOps nor local template directory ({TEMPLATES_DIR}) could be found.",
    }
