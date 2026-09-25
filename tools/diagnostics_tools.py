"""
Diagnostics & Quality FastMCP Tools
Wrappers delegating to HealthService and A11yService.
Equipped with step-by-step stderr logging for operational observability.
"""

import logging
import time
from typing import Optional
from mcp.server.fastmcp import FastMCP
from services.health_service import HealthService
from services.a11y_service import A11yService
from models.health import HealthReport, ApplicationHealthReport
from models.a11y import A11yAuditReport

logger = logging.getLogger("nexus-mcp.tools.diagnostics")
health_service = HealthService()
a11y_service = A11yService()


def register_diagnostics_tools(mcp: FastMCP) -> None:
    """Registers health diagnostics, accessibility auditing, and live application verification tools on FastMCP server."""

    @mcp.tool()
    def check_system_health() -> HealthReport:
        """
        Run comprehensive diagnostic checks on developer workstation or cloud container.
        Verifies Python, Node.js, npm, system Microsoft Edge browser, and Azure token status.
        """
        start = time.time()
        logger.info("[tool:check_system_health] Initiating diagnostic health check...")
        report = health_service.run_diagnostics()
        logger.info("[tool:check_system_health] Health check finished in %.2fs. Result: %s", time.time() - start, report.status)
        return report

    @mcp.tool()
    def run_environment_health_check() -> HealthReport:
        """
        [Alias for check_system_health] Run comprehensive workstation and cloud diagnostics.
        """
        return check_system_health()

    @mcp.tool()
    def audit_accessibility(url: str = "http://localhost:4200") -> A11yAuditReport:
        """
        Perform an automated headless accessibility & WCAG 2.1 Level AA compliance audit.
        Evaluates contrast ratios, ARIA roles, form labels, and interactive landmarks using Playwright + axe-core.
        Args:
            url: The active application URL to audit (defaults to 'http://localhost:4200').
        Returns detailed violations, impacted DOM nodes, and design system remediation advice.
        """
        start = time.time()
        logger.info("[tool:audit_accessibility] Auditing accessibility for URL: %s", url)
        report = a11y_service.audit_url(url=url)
        logger.info("[tool:audit_accessibility] Audit finished in %.2fs. Status: %s, Violations: %d", time.time() - start, report.status, len(report.violations))
        return report

    @mcp.tool()
    def verify_application_health(url: Optional[str] = None) -> ApplicationHealthReport:
        """
        Verify live frontend application health, console exceptions, network failures, and WCAG 2.1 AA a11y.
        Automatically probes candidate dev ports [4200, 3000, 3001, 5173] if URL is not explicitly passed.
        Framework and starter-kit agnostic: compatible with Next.js, CRA, Vite, and Angular/micro-frontends.
        Args:
            url: Optional explicit target URL (e.g. 'http://localhost:4200'). Defaults to auto-probing candidate ports.
        Returns:
            ApplicationHealthReport detailing HTTP status, console exceptions, network errors, interactive count, and a11y.
        """
        start = time.time()
        logger.info("[tool:verify_application_health] Verifying application health (target: %s)...", url or "auto-probe")
        report = a11y_service.verify_health(url=url)
        logger.info("[tool:verify_application_health] Health verification finished in %.2fs. HTTP: %s", time.time() - start, report.http_status)
        return report
