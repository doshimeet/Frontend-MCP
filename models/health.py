"""
Pydantic Schemas for Environment Diagnostics & Health Reports
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RuntimeInfo(BaseModel):
    available: bool = Field(description="Whether the runtime is found on PATH")
    version: Optional[str] = Field(default=None, description="Installed version string")
    path: Optional[str] = Field(default=None, description="Executable path on system")


class BrowserInfo(BaseModel):
    detected: bool = Field(description="Whether Microsoft Edge or Chrome was detected")
    channel: Optional[str] = Field(default=None, description="Playwright channel ('msedge' or 'chrome')")
    path: Optional[str] = Field(default=None, description="Binary path on system")
    warning: Optional[str] = Field(default=None, description="Warning if missing")


class EnterpriseAuthInfo(BaseModel):
    authenticated: bool = Field(description="Whether Azure DevOps credentials are valid")
    token_source: str = Field(description="msal_session, explicit_pat, or none")
    org_configured: str = Field(description="Configured Azure DevOps organization URL")


class ArtifactoryAuthInfo(BaseModel):
    user_npmrc_exists: bool = Field(description="Whether ~/.npmrc exists on workstation")
    path: str = Field(description="User npmrc file path")
    registry_target: str = Field(description="Target corporate Artifactory registry URL")


class HealthReport(BaseModel):
    status: str = Field(description="'healthy' or 'degraded'")
    system_os: str = Field(description="Operating system (darwin, win32, linux)")
    python_version: str = Field(description="Installed Python version")
    node: RuntimeInfo = Field(description="Node.js status")
    npm: RuntimeInfo = Field(description="npm status")
    browser: BrowserInfo = Field(description="Playwright system browser status")
    azure_devops: EnterpriseAuthInfo = Field(description="Azure DevOps authentication status")
    artifactory: ArtifactoryAuthInfo = Field(description="Artifactory npmrc configuration status")
