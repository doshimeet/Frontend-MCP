"""
Accessibility Audit Domain Models
Pydantic contracts representing axe-core WCAG 2.1 Level AA compliance audits.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class A11yNode(BaseModel):
    """Specific DOM element that triggered a rule evaluation."""
    target: List[str] = Field(default_factory=list, description="CSS selector path to the DOM element")
    html: str = Field(..., description="HTML snippet of the offending element")
    failureSummary: Optional[str] = Field(None, description="Concise explanation of the accessibility failure")


class A11yViolation(BaseModel):
    """An accessibility rule violation detected by axe-core."""
    id: str = Field(..., description="Rule ID (e.g. 'color-contrast', 'button-name', 'label')")
    impact: Optional[str] = Field(None, description="Severity: 'critical', 'serious', 'moderate', 'minor'")
    description: Optional[str] = Field(None, description="Detailed description of the violated WCAG guideline")
    help: Optional[str] = Field(None, description="Human-friendly explanation of how to fix the issue")
    helpUrl: Optional[str] = Field(None, description="Direct URL to Deque University / W3C documentation")
    nodes: List[A11yNode] = Field(default_factory=list, description="List of DOM nodes violating this rule")


class A11yAuditReport(BaseModel):
    """Complete Accessibility Audit Report."""
    url: str = Field(..., description="Target URL audited")
    timestamp: str = Field(..., description="ISO 8601 audit execution timestamp")
    success: bool = Field(..., description="True if 0 critical or serious violations detected")
    passesCount: int = Field(0, description="Total number of WCAG checks that passed")
    violationsCount: int = Field(0, description="Total number of violations detected")
    criticalCount: int = Field(0, description="Count of critical severity violations")
    seriousCount: int = Field(0, description="Count of serious severity violations")
    moderateCount: int = Field(0, description="Count of moderate severity violations")
    minorCount: int = Field(0, description="Count of minor severity violations")
    violations: List[A11yViolation] = Field(default_factory=list, description="Detailed list of detected violations")
    remediations: List[str] = Field(default_factory=list, description="Actionable design system remediation advice")
    browserChannel: Optional[str] = Field("msedge", description="Browser engine utilized (e.g. 'msedge', 'chrome')")
