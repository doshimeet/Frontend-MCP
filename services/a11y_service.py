"""
Accessibility Audit Service & Dual-Gate Design Verification
Dual-Engine Architecture:
1. Engine A (Semantic DOM & WCAG Inspector in pure Python): Fast, zero-OS-dependency
   inspector for Azure App Service Linux Oryx and lightweight server scans.
2. Engine B (Headless Playwright + axe-core): Deep dynamic browser scanner for local
   developer workstations and containerized CI/CD environments.

Dual-Gate Enforcement:
- Gate 1: WCAG 2.1 AA Compliance (axe-core / SemanticDOMInspector)
- Gate 2: Programmatic Anti-Slop Design Linter (inline styles, heading hierarchy, status-chip overload)
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import html.parser
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import httpx

from config import REPO_ROOT
from models.a11y import A11yAuditReport, A11yViolation, A11yNode
from models.health import ApplicationHealthReport
from core.environment import CANDIDATE_DEV_PORTS


class SemanticDOMInspector(html.parser.HTMLParser):
    """Pure-Python semantic DOM, accessibility, and anti-slop design auditor."""

    def __init__(self):
        super().__init__()
        self.violations: List[A11yViolation] = []
        self.h1_count = 0
        self.heading_stack: List[int] = []
        self.headings_recorded: List[Tuple[int, str]] = []
        self.has_main = False
        self.html_has_lang = False
        self._current_tag_attrs: Dict[str, str] = {}
        self._button_text: List[str] = []
        self._heading_text: List[str] = []
        self._in_button = False
        self._in_heading = False
        self._current_heading_level = 0

        # Anti-slop telemetry
        self.inline_style_count = 0
        self.inline_style_spaghetti = 0
        self.badge_count = 0
        self.table_badge_count = 0
        self.clustered_badge_count = 0
        self._in_table_cell = False
        self._cell_badge_count = 0
        self.max_badges_per_cell = 0
        self.has_yellow_banner = False
        self.low_contrast_inline_colors = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower in ("td", "th"):
            self._in_table_cell = True
            self._cell_badge_count = 0

        # Gate 2 Telemetry: Inspect inline styles
        if "style" in attr_dict:
            style_val = attr_dict["style"].lower()
            self.inline_style_count += 1
            # Flag complex layout in inline styles
            if any(prop in style_val for prop in ["display:", "border:", "box-shadow:", "padding:", "flex-direction:"]):
                self.inline_style_spaghetti += 1
            if "#ffcc00" in style_val or "rgb(255, 204, 0)" in style_val:
                self.has_yellow_banner = True
            if any(c in style_val for c in ["#888", "#999", "#aaa", "#8d8d8d", "#9ca3af", "rgb(156, 163, 175)"]):
                self.low_contrast_inline_colors += 1

        # Gate 2 Telemetry: Count badges
        classes = attr_dict.get("class", "").lower()
        if any(b in classes for b in ["badge", "tag", "chip", "cds--tag", "nexus-badge"]):
            self.badge_count += 1
            if self._in_table_cell:
                self.table_badge_count += 1
                self._cell_badge_count += 1
            else:
                self.clustered_badge_count += 1

        if tag_lower == "html":
            if "lang" in attr_dict and attr_dict["lang"].strip():
                self.html_has_lang = True

        elif tag_lower == "main":
            self.has_main = True

        elif tag_lower.startswith("h") and len(tag_lower) == 2 and tag_lower[1].isdigit():
            level = int(tag_lower[1])
            self._in_heading = True
            self._current_heading_level = level
            self._heading_text = []

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
        if self._in_heading:
            self._heading_text.append(data.strip())

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower == "button" and self._in_button:
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

        elif tag_lower.startswith("h") and len(tag_lower) == 2 and tag_lower[1].isdigit() and self._in_heading:
            clean_text = " ".join("".join(self._heading_text).split())
            if clean_text:
                self.headings_recorded.append((self._current_heading_level, clean_text))
            self._in_heading = False

        elif tag_lower in ("td", "th"):
            self._in_table_cell = False
            if self._cell_badge_count > self.max_badges_per_cell:
                self.max_badges_per_cell = self._cell_badge_count
            self._cell_badge_count = 0

    def finalize_violations(self) -> List[A11yViolation]:
        """Gate 1: WCAG 2.1 AA Violations."""
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

    def audit_design_slop(self) -> List[str]:
        """Gate 2: Programmatic Anti-Slop & Visual Quality Audit."""
        slop_issues: List[str] = []

        # 1. Multiple H1s
        if self.h1_count > 1:
            slop_issues.append(
                f"[Hierarchy Slop] Multiple <h1> headings detected ({self.h1_count}). Exactly one <h1> is permitted per page."
            )

        # 2. Stacked Redundant Headings
        for i in range(len(self.headings_recorded) - 1):
            lvl1, text1 = self.headings_recorded[i]
            lvl2, text2 = self.headings_recorded[i + 1]
            words1 = set(w.lower() for w in re.findall(r"\w+", text1) if len(w) > 3)
            words2 = set(w.lower() for w in re.findall(r"\w+", text2) if len(w) > 3)
            overlap = words1.intersection(words2)
            if len(overlap) >= 2:
                slop_issues.append(
                    f"[Hierarchy Slop] Stacked redundant headings: <h{lvl1}> '{text1}' followed by <h{lvl2}> '{text2}'. Combine or clarify visual hierarchy."
                )

        # 3. Raw Inline Style Spaghetti
        if self.inline_style_spaghetti > 4:
            slop_issues.append(
                f"[Styling Slop] Excessive raw inline styles ({self.inline_style_spaghetti} elements with complex inline layout CSS). Use predefined Nexus token classes (.nexus-card, .nexus-kpi-card, .nexus-table)."
            )

        # 4. Yellow Banner Slop
        if self.has_yellow_banner:
            slop_issues.append(
                "[Institutional Brand Slop] Unrefined full-width yellow caution-tape banner detected (#ffcc00). Replace with integrated header classification pill (.nexus-classification-pill)."
            )

        # 5. Status-Chip Overload (Context-Aware)
        if self.clustered_badge_count > 4:
            slop_issues.append(
                f"[Badge Overload] Excessive non-tabular status chips detected ({self.clustered_badge_count} badges in cards/headers). Reserve badges strictly for operational lifecycle states; use tabular figures for metrics."
            )
        elif self.max_badges_per_cell > 3:
            slop_issues.append(
                f"[Badge Overload] Clustered status chips detected inside a single table cell ({self.max_badges_per_cell} badges in one cell). Limit cell metadata density."
            )

        # 6. Low Contrast Grey Text
        if self.low_contrast_inline_colors > 0:
            slop_issues.append(
                f"[Contrast Slop] Low-contrast inline typography ({self.low_contrast_inline_colors} occurrences of light grey text). Ensure text uses --nexus-color-text-primary or --nexus-color-text-secondary."
            )

        return slop_issues


class A11yService:
    """Enterprise Dual-Engine Accessibility Audit & Diagnostics Service."""

    def __init__(self, script_path: Optional[Path] = None):
        self.script_path = script_path or (REPO_ROOT / "scripts" / "verify-a11y.mjs")

    def _can_run_headless_browser(self) -> bool:
        """Determines if local workstation environment supports headless browser execution."""
        return bool(shutil.which("node"))

    def audit_url(self, url: str, timeout_sec: int = 45) -> A11yAuditReport:
        """Audits accessibility via headless Playwright or fallback SemanticDOMInspector."""
        now_iso = datetime.now(timezone.utc).isoformat()

        if self._can_run_headless_browser() and self.script_path.exists():
            cmd = ["node", str(self.script_path), "--url", url]
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
                        return A11yAuditReport.model_validate(data)
            except Exception:
                pass

        # Fallback to Python HTTP inspection
        try:
            with httpx.Client(timeout=float(timeout_sec), follow_redirects=True) as client:
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
                            help="Ensure the development server is active and serving 200 OK responses.",
                        )
                    ],
                    remediations=[f"Verify page exists and dev server is running on {url}."],
                    browserChannel="python-semantic-engine",
                )

            parser = SemanticDOMInspector()
            parser.feed(resp.text)
            violations = parser.finalize_violations()
            crit_count = sum(1 for v in violations if v.impact == "critical")
            serious_count = sum(1 for v in violations if v.impact == "serious")

            return A11yAuditReport(
                url=url,
                timestamp=now_iso,
                success=(crit_count == 0 and serious_count == 0),
                violationsCount=len(violations),
                criticalCount=crit_count,
                seriousCount=serious_count,
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
        Executes Dual-Gate application health verification across candidate ports [3000, 3001, 4200, 5173].
        Gate 1: WCAG 2.1 AA Accessibility
        Gate 2: Programmatic Anti-Slop Design Linter
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

        # Fallback to Engine A: Pure Python Candidate Port Probing with Dual-Gate
        return self._probe_ports_python(url, now_iso)

    def _probe_ports_python(self, url: Optional[str], now_iso: str) -> ApplicationHealthReport:
        """Pure Python candidate dev port probe scanning with Dual-Gate verification."""
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
                    slop_issues = parser.audit_design_slop()
                    design_score = max(0, 100 - len(slop_issues) * 15)

                    remediations = [v.help for v in violations if v.help]
                    remediations.extend(slop_issues)

                    # Dual-Gate pass criteria:
                    is_healthy = (len(violations) == 0) and (len(slop_issues) == 0)

                    return ApplicationHealthReport(
                        url=probe_url,
                        detected_port=detected_port,
                        timestamp=now_iso,
                        http_status=200,
                        is_healthy=is_healthy,
                        console_errors=[],
                        accessibility_violations=[v.description for v in violations],
                        design_slop_violations=slop_issues,
                        design_quality_score=design_score,
                        remediations=remediations,
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
            design_slop_violations=[],
            design_quality_score=0,
            remediations=["Start the frontend application via 'npm run dev'."],
        )
