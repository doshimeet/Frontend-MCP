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

# Resolve repository root directory (supports flat root, /home/site/wwwroot on Azure, or explicit REPO_ROOT)
SERVER_DIR = Path(__file__).resolve().parent
if os.getenv("REPO_ROOT"):
    REPO_ROOT = Path(os.environ["REPO_ROOT"]).resolve()
else:
    REPO_ROOT = SERVER_DIR

# Load .env file from repository root or current working directory
load_dotenv(REPO_ROOT / ".env")
load_dotenv(Path.cwd() / ".env")

# Server Transport Configuration
SYSTEM_NAME: str = "nexus"
SYSTEM_DISPLAY_NAME: str = "Nexus Design System"
SYSTEM_VERSION: str = "2.0.0"

MCP_MODE: Literal["stdio", "uvicorn"] = os.getenv("MCP_MODE", "stdio").lower()  # type: ignore
MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT: int = int(os.getenv("PORT", os.getenv("WEBSITES_PORT", os.getenv("MCP_PORT", "8000"))))
MCP_API_KEY: str | None = os.getenv("MCP_API_KEY")

# Multi-Environment Operational Mode (3 Modes: carbon, wbg, cloud)
from core.environment import (
    EnvironmentMode,
    CANDIDATE_DEV_PORTS,
    resolve_active_mode,
    find_active_dev_port,
    find_active_dev_url,
)
ACTIVE_MODE: EnvironmentMode = resolve_active_mode()

# Nexus Design System Single Source of Truth Constants
NEXUS_PACKAGE_NAME: str = os.getenv("DESIGN_SYSTEM_PACKAGE", "@wbg/nexus")
NEXUS_PACKAGE_VERSION: str = "^2.0.0"
NEXUS_STYLESHEET: str = "@wbg/nexus/styles.css"

# Azure DevOps Configuration
AZURE_DEVOPS_ORG: str = os.getenv("AZURE_DEVOPS_ORG", "https://dev.azure.com/operations-and-corporate")
AZURE_DEVOPS_PROJECT: str = os.getenv("AZURE_DEVOPS_PROJECT", "ITSDA-DATAEXPLORER")
AZURE_DEVOPS_STARTER_REPO_ID: str = os.getenv("AZURE_DEVOPS_STARTER_REPO_ID", "ITSDA-DATAEXPLORER-FE")
AZURE_DEVOPS_STARTER_BRANCH: str = os.getenv("AZURE_DEVOPS_BRANCH", "starter-kit")
AZURE_DEVOPS_PAT: str | None = os.getenv("AZURE_DEVOPS_PAT")

# Pre-flight Configuration Validation (Degraded Mode Detection)
IS_LIVE_ADO_CONFIGURED: bool = bool(
    AZURE_DEVOPS_ORG and not AZURE_DEVOPS_ORG.endswith("enterprise-org")
)

# Artifactory / NPM Registry Configuration
ARTIFACTORY_NPM_REGISTRY: str = os.getenv(
    "ARTIFACTORY_NPM_REGISTRY",
    "https://artifactory.internal.company.com/artifactory/api/npm/virtual/"
)

# Workspace Directories & Catalogs
TEMPLATES_DIR = REPO_ROOT / "templates" / "frontend-starter"
RECIPES_DIR = REPO_ROOT / "packages" / "recipes"
TOKENS_DIR = REPO_ROOT / "packages" / "tokens"
APPS_DIR = REPO_ROOT / "apps"
COMPONENTS_JSON_PATH = REPO_ROOT / "components.json"

# Storybook Catalog Endpoints
STORYBOOK_URL = os.getenv("STORYBOOK_URL", "https://storybook.internal.company.com")
STORYBOOK_MANIFEST_PATH = os.getenv("STORYBOOK_MANIFEST_PATH", "/design-system/index.json")

IS_LIVE_STORYBOOK_CONFIGURED: bool = bool(
    os.getenv("STORYBOOK_URL") and not "storybook.internal.company.com" in os.getenv("STORYBOOK_URL", "")
)


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
