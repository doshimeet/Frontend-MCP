"""
Enterprise Design System MCP Server - Configuration Module
Cross-platform environment, paths, and defaults resolution.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Resolve repository root directory (supports monorepo root, container WORKDIR, or explicit REPO_ROOT)
SERVER_DIR = Path(__file__).resolve().parent
if os.getenv("REPO_ROOT"):
    REPO_ROOT = Path(os.environ["REPO_ROOT"]).resolve()
elif (SERVER_DIR.parent.parent / "packages").exists():
    REPO_ROOT = SERVER_DIR.parent.parent
elif (SERVER_DIR / "templates").exists():
    REPO_ROOT = SERVER_DIR
else:
    REPO_ROOT = SERVER_DIR.parent.parent

# Load .env file from repository root or current working directory
load_dotenv(REPO_ROOT / ".env")
load_dotenv(Path.cwd() / ".env")

# Server Transport Configuration
MCP_MODE: Literal["stdio", "uvicorn"] = os.getenv("MCP_MODE", "stdio").lower()  # type: ignore
MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT: int = int(os.getenv("MCP_PORT", os.getenv("WEBSITES_PORT", "8000")))
MCP_API_KEY: str | None = os.getenv("MCP_API_KEY")

# Azure DevOps Configuration
AZURE_DEVOPS_ORG: str = os.getenv("AZURE_DEVOPS_ORG", "https://dev.azure.com/enterprise-org")
AZURE_DEVOPS_PROJECT: str = os.getenv("AZURE_DEVOPS_PROJECT", "EnterpriseDigital")
AZURE_DEVOPS_STARTER_REPO_ID: str = os.getenv("AZURE_DEVOPS_STARTER_REPO_ID", "frontend-starter-kit")
AZURE_DEVOPS_PAT: str | None = os.getenv("AZURE_DEVOPS_PAT")

# Artifactory / NPM Registry Configuration
ARTIFACTORY_NPM_REGISTRY: str = os.getenv(
    "ARTIFACTORY_NPM_REGISTRY",
    "https://artifactory.internal.company.com/artifactory/api/npm/virtual/"
)

# Workspace Directories
TEMPLATES_DIR = REPO_ROOT / "templates" / "frontend-starter"
RECIPES_DIR = REPO_ROOT / "packages" / "recipes"
TOKENS_DIR = REPO_ROOT / "packages" / "tokens"
APPS_DIR = REPO_ROOT / "apps"

# Public IBM Carbon Storybook Endpoint (for POC component testing)
CARBON_STORYBOOK_URL = "https://react.carbondesignsystem.com"


def get_target_workspace(target_path: str | None = None) -> Path:
    """
    Safely resolves a workspace path cross-platform.
    If target_path is not specified, defaults to the current working directory.
    """
    if target_path:
        path = Path(target_path).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        return path
    return Path.cwd().resolve()
