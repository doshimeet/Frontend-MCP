"""
Accessibility Audit Service
Dual-Engine Architecture:
1. Engine A (Semantic DOM & WCAG Inspector in pure Python): Fast, zero-OS-dependency
   inspector for Azure App Service Linux Oryx and lightweight server scans.
2. Engine B (Headless Playwright + axe-core): Deep dynamic browser scanner for local
   developer workstations and containerized CI/CD environments.
"""

import json
import os
import shutil
import subprocess
import tempfile
import html.parser
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import httpx

from config import REPO_ROOT
from models.a11y import A11yAuditReport, A11yViolation, A11yNode
from models.health import ApplicationHealthReport
from core.environment import CANDIDATE_DEV_PORTS


class SemanticDOMInspector(html.parser.HTMLParser):
    """Pure-Python semantic DOM and accessibility auditor for WCAG 2.1 AA compliance."""

    def __init__(self):
        super().__init__()
        self.violations: List[A11yViolation] = []
        self.h1_count = 0
        self.heading_stack: List[int] = []
        self.has_main = False
        self.html_has_lang = False
        self._current_tag_attrs: Dict[str, str] = {}
        self._button_text: List[str] = []
        self._in_button = False

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower == "html":
            if "lang" in attr_dict and attr_dict["lang"].strip():
                self.html_has_lang = True

        elif tag_lower == "main":
            self.has_main = True

        elif tag_lower.startswith("h") and len(tag_lower) == 2 and tag_lower[1].isdigit():
            level = int(tag_lower[1])
            if level == 1:
                self.h1_count += 1
            if self.heading_stack:
                prev = self.heading_stack[-1]
                if level > prev + 1:
                    self.violations.append(
                        A11yViolation(
                            id="heading-order",
                            impact="moderate",
                            description=f"Heading level skipped: h{prev} followed by h{level}",
                            help="Ensure heading levels are structured hierarchically (e.g. h1 followed by h2).",
                            nodes=[A11yNode(html=f"<{tag_lower}>", target=[tag_lower], failureSummary="Heading level skipped")],
                        )
                    )
            self.heading_stack.append(level)

        elif tag_lower == "img":
            if "alt" not in attr_dict:
                self.violations.append(
                    A11yViolation(
                        id="image-alt",
                        impact="critical",
                        description="Image element is missing an alt attribute",
                        help="Images must have an alt attribute or aria-hidden='true' if decorative.",
                        nodes=[A11yNode(html=f"<img src='{attr_dict.get('src', '')}'>", target=["img"], failureSummary="Missing alt attribute")],
                    )
                )

        elif tag_lower == "input":
            input_type = attr_dict.get("type", "text").lower()
            if input_type not in ("hidden", "submit", "button", "reset"):
                has_label = bool(attr_dict.get("aria-label") or attr_dict.get("aria-labelledby") or attr_dict.get("id"))
                if not has_label:
                    self.violations.append(
                        A11yViolation(
                            id="label-missing",
                            impact="critical",
                            description=f"Input element (type='{input_type}') lacks an accessible label or id binding",
                            help="Form inputs must have an associated <label> element or aria-label.",
                            nodes=[A11yNode(html=f"<input type='{input_type}'>", target=["input"], failureSummary="Missing accessible name")],
                        )
                    )

        elif tag_lower == "button":
            self._in_button = True
            self._button_text = []
            self._current_tag_attrs = attr_dict

    def handle_data(self, data: str):
        if self._in_button:
            self._button_text.append(data.strip())

    def handle_endtag(self, tag: str):
        if tag.lower() == "button" and self._in_button:
            text = "".join(self._button_text).strip()
            has_name = bool(text or self._current_tag_attrs.get("aria-label") or self._current_tag_attrs.get("title"))
            if not has_name:
                self.violations.append(
                    A11yViolation(
                        id="button-name",
                        impact="critical",
                        description="Button element has no accessible text or aria-label",
                        help="Buttons must have discernible text or an aria-label.",
                        nodes=[A11yNode(html="<button>", target=["button"], failureSummary="Button without accessible name")],
                    )
                )
            self._in_button = False

    def finalize_violations(self) -> List[A11yViolation]:
        if not self.html_has_lang:
            self.violations.append(
                A11yViolation(
                    id="html-has-lang",
                    impact="serious",
                    description="<html> element is missing a lang attribute",
                    help="Add lang='en' to the top-level <html> element.",
                    nodes=[A11yNode(html="<html>", target=["html"], failureSummary="Missing lang attribute")],
                )
            )
        if self.h1_count == 0:
            self.violations.append(
                A11yViolation(
                    id="page-has-heading-one",
                    impact="moderate",
                    description="Page is missing an <h1> main heading",
                    help="Ensure every page includes exactly one <h1> title element.",
                    nodes=[A11yNode(html="<body>", target=["body"], failureSummary="Missing h1 element")],
                )
            )
        return self.violations


class A11yService:
    """Enterprise Dual-Engine Accessibility Audit & Diagnostics Service."""

    def __init__(self, script_path: Optional[Path] = None):
        self.script_path = script_path or (REPO_ROOT / "scripts" / "verify-a11y.mjs")

    def _can_run_headless_browser(self) -> bool:
        """Determines if the runtime environment can execute headless Chromium."""
        # Standard Azure App Service Linux does not include Chromium OS shared libraries
        if os.getenv("WEBSITE_SITE_NAME") or os.getenv("WEBSITE_INSTANCE_ID"):
            return False
        return shutil.which("node") is not None and self.script_path.exists()

    def audit_url(self, url: str = "http://localhost:3000", timeout_sec: int = 30) -> A11yAuditReport:
        """
        Executes accessibility scan using dual-engine architecture:
        - Engine B (Playwright + axe-core) if Node & browser binaries are available.
        - Engine A (Semantic DOM Inspector) on pure-Python App Service Linux or when headless fails.
        """
        # Try Engine B (Headless Playwright) if supported
        if self._can_run_headless_browser():
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
                report_file_path = tmp_file.name

            try:
                cmd = ["node", str(self.script_path), "--url", url, "--report", report_file_path]
                env = os.environ.copy()
                env.setdefault("PLAYWRIGHT_BROWSER_CHANNEL", "msedge")

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
            except Exception:
                pass
            finally:
                if os.path.exists(report_file_path):
                    try:
                        os.remove(report_file_path)
                    except OSError:
                        pass

        # Fallback to Engine A: Pure Python Semantic DOM & WCAG Inspector
        return self._audit_semantic_dom(url, timeout_sec)

    def _audit_semantic_dom(self, url: str, timeout_sec: int) -> A11yAuditReport:
        """Executes Engine A: Fast semantic HTML inspection over HTTP without browser binaries."""
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            with httpx.Client(timeout=min(5.0, float(timeout_sec)), follow_redirects=True) as client:
                resp = client.get(url)

            if resp.status_code != 200:
                return A11yAuditReport(
                    url=url,
                    timestamp=now_iso,
                    success=False,
                    violationsCount=1,
                    criticalCount=1,
                    violations=[
                        A11yViolation(
                            id="http-error",
                            impact="critical",
                            description=f"Target URL returned HTTP status {resp.status_code}",
                            help="Ensure the server is running and accessible.",
                        )
                    ],
                    remediations=[f"Verify server at {url} returns HTTP 200."],
                    browserChannel="python-semantic-engine",
                )

            parser = SemanticDOMInspector()
            parser.feed(resp.text)
            violations = parser.finalize_violations()
            critical_count = sum(1 for v in violations if v.impact == "critical")

            return A11yAuditReport(
                url=url,
                timestamp=now_iso,
                success=(len(violations) == 0),
                violationsCount=len(violations),
                criticalCount=critical_count,
                violations=violations,
                remediations=[v.help for v in violations if v.help],
                browserChannel="python-semantic-engine",
            )
        except Exception as exc:
            return A11yAuditReport(
                url=url,
                timestamp=now_iso,
                success=False,
                violationsCount=1,
                criticalCount=1,
                violations=[
                    A11yViolation(
                        id="audit-unreachable",
                        impact="critical",
                        description=f"Could not connect to target URL {url}: {str(exc)}",
                        help="Ensure application dev server is running on the target port.",
                    )
                ],
                remediations=[f"Run 'npm run dev' to start the application server and try again."],
                browserChannel="python-semantic-engine",
            )

    def verify_health(self, url: Optional[str] = None, timeout_sec: int = 30) -> ApplicationHealthReport:
        """
        Executes application health verification with dynamic candidate port probing [3000, 3001, 4200, 5173].
        Employs Playwright verify-health.mjs when available, falling back gracefully to Python HTTP probing.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        script = REPO_ROOT / "scripts" / "verify-health.mjs"

        # Try Engine B (Node / Playwright verify-health.mjs) if supported
        if self._can_run_headless_browser() and script.exists():
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
            except Exception:
                pass

        # Fallback to Engine A: Pure Python Candidate Port Probing
        return self._probe_ports_python(url, now_iso)

    def _probe_ports_python(self, url: Optional[str], now_iso: str) -> ApplicationHealthReport:
        """Pure Python candidate dev port probe scanning [3000, 3001, 4200, 5173]."""
        target_urls = [url] if url else [f"http://localhost:{p}" for p in CANDIDATE_DEV_PORTS]
        detected_port = 3000

        for probe_url in target_urls:
            try:
                with httpx.Client(timeout=1.5, follow_redirects=True) as client:
                    resp = client.get(probe_url)
                from urllib.parse import urlparse
                port = urlparse(probe_url).port or 3000
                detected_port = port

                if resp.status_code == 200:
                    parser = SemanticDOMInspector()
                    parser.feed(resp.text)
                    violations = parser.finalize_violations()
                    return ApplicationHealthReport(
                        url=probe_url,
                        detected_port=detected_port,
                        timestamp=now_iso,
                        http_status=200,
                        is_healthy=(len(violations) == 0),
                        console_errors=[],
                        accessibility_violations=[v.description for v in violations],
                        remediations=[v.help for v in violations if v.help],
                    )
            except Exception:
                continue

        # If no port responded
        first_port = 3000 if not url else (httpx.URL(url).port or 3000)
        return ApplicationHealthReport(
            url=url or f"http://localhost:{first_port}",
            detected_port=first_port,
            timestamp=now_iso,
            http_status=0,
            is_healthy=False,
            console_errors=["No active development server detected on candidate ports [3000, 3001, 4200, 5173]"],
            accessibility_violations=[],
            remediations=["Start the frontend application via 'npm run dev'."],
        )


