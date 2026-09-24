"""
Accessibility Audit Service
Coordinates headless browser execution (Playwright + axe-core) to evaluate WCAG 2.1 AA compliance.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import REPO_ROOT
from models.a11y import A11yAuditReport, A11yViolation, A11yNode
from models.health import ApplicationHealthReport


class A11yService:
    """Enterprise Accessibility Audit Service."""

    def __init__(self, script_path: Optional[Path] = None):
        self.script_path = script_path or (REPO_ROOT / "scripts" / "verify-a11y.mjs")

    def audit_url(self, url: str = "http://localhost:3000", timeout_sec: int = 30) -> A11yAuditReport:
        """
        Executes headless browser scan against the provided URL.
        Returns a strongly typed A11yAuditReport.
        """
        if not self.script_path.exists():
            return A11yAuditReport(
                url=url,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                violationsCount=1,
                criticalCount=1,
                violations=[
                    A11yViolation(
                        id="script-missing",
                        impact="critical",
                        description=f"Accessibility audit script not found at {self.script_path}",
                        help="Ensure scripts/verify-a11y.mjs is present in the repository root.",
                    )
                ],
                remediations=["Verify the verify-a11y.mjs script exists in scripts/ directory."],
                browserChannel="msedge",
            )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            report_file_path = tmp_file.name

        try:
            cmd = ["node", str(self.script_path), "--url", url, "--report", report_file_path]
            # Run node script with system browser channel
            env = os.environ.copy()
            env.setdefault("PLAYWRIGHT_BROWSER_CHANNEL", "msedge")
            
            # Note: script exits 1 if critical/serious violations exist, but still writes the full report
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=env,
                cwd=str(REPO_ROOT),
            )

            if os.path.exists(report_file_path) and os.path.getsize(report_file_path) > 0:
                with open(report_file_path, "r", encoding="utf-8") as rf:
                    data = json.load(rf)
                return A11yAuditReport.model_validate(data)

            # Fallback if report wasn't generated
            return A11yAuditReport(
                url=url,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                violationsCount=1,
                criticalCount=1,
                violations=[
                    A11yViolation(
                        id="audit-unreachable",
                        impact="critical",
                        description=f"Could not connect to target URL {url}. Ensure application dev server is running.",
                        help="Start the application dev server (e.g. `npm run dev`) before running an accessibility audit.",
                    )
                ],
                remediations=[f"Run 'npm run dev' to start the server at {url} and try again."],
                browserChannel="msedge",
            )
        except subprocess.TimeoutExpired:
            return A11yAuditReport(
                url=url,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                violationsCount=1,
                criticalCount=1,
                violations=[
                    A11yViolation(
                        id="audit-timeout",
                        impact="critical",
                        description=f"Accessibility audit timed out after {timeout_sec}s connecting to {url}.",
                        help="Check if the application server is responsive.",
                    )
                ],
                remediations=["Check server logs and ensure localhost is responding."],
                browserChannel="msedge",
            )
        except Exception as e:
            return A11yAuditReport(
                url=url,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                violationsCount=1,
                criticalCount=1,
                violations=[
                    A11yViolation(
                        id="audit-error",
                        impact="critical",
                        description=f"Audit execution encountered error: {str(e)}",
                        help="Review system Node and browser configuration.",
                    )
                ],
                remediations=[f"Error detail: {str(e)}"],
                browserChannel="msedge",
            )
        finally:
            if os.path.exists(report_file_path):
                try:
                    os.remove(report_file_path)
                except OSError:
                    pass

    def verify_health(self, url: Optional[str] = None, timeout_sec: int = 30) -> ApplicationHealthReport:
        """
        Executes verify-health.mjs with dynamic candidate port probing [3000, 3001, 4200, 5173].
        Traps browser console errors, HTTP 4xx/5xx network failures, and runs axe-core a11y audit.
        """
        script = REPO_ROOT / "scripts" / "verify-health.mjs"
        now_iso = datetime.now(timezone.utc).isoformat()
        if not script.exists():
            return ApplicationHealthReport(
                url=url or "http://localhost:3000",
                detected_port=3000,
                timestamp=now_iso,
                http_status=0,
                is_healthy=False,
                console_errors=[f"verify-health.mjs not found at {script}"],
                remediations=["Ensure scripts/verify-health.mjs is present in the repository root."],
            )

        cmd = ["node", str(script)]
        if url:
            cmd.extend(["--url", url])

        env = os.environ.copy()
        env.setdefault("PLAYWRIGHT_BROWSER_CHANNEL", "msedge")

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=env,
                cwd=str(REPO_ROOT),
            )
            stdout = res.stdout.strip()
            if stdout:
                start_idx = stdout.find("{")
                end_idx = stdout.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    raw_json = stdout[start_idx : end_idx + 1]
                    data = json.loads(raw_json)
                    return ApplicationHealthReport.model_validate(data)

            return ApplicationHealthReport(
                url=url or "http://localhost:3000",
                detected_port=3000,
                timestamp=now_iso,
                http_status=res.returncode if res.returncode != 0 else 500,
                is_healthy=False,
                console_errors=[res.stderr.strip() or "No output from verify-health.mjs"],
                remediations=["Check Node.js and Playwright installation."],
            )
        except subprocess.TimeoutExpired:
            return ApplicationHealthReport(
                url=url or "http://localhost:3000",
                detected_port=3000,
                timestamp=now_iso,
                http_status=504,
                is_healthy=False,
                console_errors=[f"Health verification timed out after {timeout_sec}s"],
                remediations=["Ensure dev server is responding quickly to HTTP requests."],
            )
        except Exception as e:
            return ApplicationHealthReport(
                url=url or "http://localhost:3000",
                detected_port=3000,
                timestamp=now_iso,
                http_status=500,
                is_healthy=False,
                console_errors=[str(e)],
                remediations=[f"Unexpected error: {str(e)}"],
            )

