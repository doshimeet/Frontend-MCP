"""
Pydantic Schemas for Environment Diagnostics & Health Reports
"""

from typing import Dict, Any, Optional, List
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


class ApplicationHealthReport(BaseModel):
    url: str = Field(description="Audited application URL")
    detected_port: int = Field(default=3000, description="Active local dev port (3000, 3001, 4200, 5173)")
    timestamp: str = Field(description="Audit timestamp in ISO format")
    http_status: int = Field(default=200, description="HTTP status response code from frontend server")
    is_healthy: bool = Field(description="Overall pass/fail status (True if HTTP 200, no fatal console exceptions, and no critical a11y violations)")
    console_errors: List[str] = Field(default_factory=list, description="Trapped browser console.error and unhandled exception messages")
    failing_requests: List[str] = Field(default_factory=list, description="List of failing HTTP 4xx/5xx network requests")
    interactive_elements_tested: int = Field(default=0, description="Count of interactive landmarks (buttons, links, inputs) verified for focusability")
    a11y_violations_count: int = Field(default=0, description="Total accessibility violations found by axe-core")
    a11y_critical_count: int = Field(default=0, description="Critical severity accessibility violations")
    design_slop_violations: List[str] = Field(default_factory=list, description="Visual taste & anti-slop violations (raw inline styles, stacked headings, badge overload)")
    design_quality_score: int = Field(default=100, description="Design quality score (100 = impeccable, < 70 = degraded)")
    remediations: List[str] = Field(default_factory=list, description="Actionable remediation suggestions")
