"""
Phase 11: Production-Grade Design Quality, Taste Skill Integration & Composable Architecture Engine Tests
Verifies:
1. Official Taste Skill and Impeccable Engine file integrity in .agents/skills/
2. Enterprise bridge rulebook (wbg-enterprise-rules.md)
3. Layered elevation tokens and DTCG CSS generation in TokenService
4. Composable pattern anatomy and micro-primitive models
5. Non-destructive brownfield design system and skill injection
6. Dual-Gate Programmatic Anti-Slop Linter in SemanticDOMInspector
"""

import json
import tempfile
import pytest
from pathlib import Path
from config import REPO_ROOT
from services.token_service import TokenService
from services.brownfield_service import BrownfieldService
from services.a11y_service import SemanticDOMInspector
from models.patterns import PatternAnatomy, PatternSlot


def test_taste_skill_and_impeccable_engine_installed():
    """Verify official Taste Skill and Impeccable skills are installed in .agents/skills/."""
    skills_dir = REPO_ROOT / ".agents" / "skills"
    assert skills_dir.exists(), "Missing .agents/skills directory"

    # 1. Taste Skill
    taste_skill = skills_dir / "design-taste-frontend" / "SKILL.md"
    assert taste_skill.exists(), "Missing design-taste-frontend/SKILL.md"
    content = taste_skill.read_text(encoding="utf-8")
    assert len(content) > 50000, f"Taste Skill appears incomplete (size: {len(content)} bytes)"
    assert "Design System" in content or "typography" in content

    # 2. Impeccable Engine & Manuals
    impeccable_skill = skills_dir / "impeccable" / "SKILL.md"
    assert impeccable_skill.exists(), "Missing impeccable/SKILL.md"
    assert len(impeccable_skill.read_text(encoding="utf-8")) > 5000

    ref_dir = skills_dir / "impeccable" / "reference"
    assert ref_dir.exists(), "Missing impeccable reference directory"
    ref_files = list(ref_dir.glob("*.md"))
    assert len(ref_files) >= 20, f"Expected >= 20 reference manuals, found {len(ref_files)}"

    # 3. Enterprise Bridge Rulebook
    bridge_rules = skills_dir / "wbg-enterprise-rules.md"
    assert bridge_rules.exists(), "Missing wbg-enterprise-rules.md"
    bridge_content = bridge_rules.read_text(encoding="utf-8")
    assert "WCAG 2.1 AA" in bridge_content
    assert "#002244" in bridge_content
    assert "nexus-card" in bridge_content


def test_elevation_tokens_and_css_generation():
    """Verify TokenService parses elevation tokens and serializes CSS variables."""
    token_service = TokenService()
    tokens = token_service.get_theme_tokens("default")

    assert "elevation" in tokens.__class__.model_fields
    assert "subtle" in tokens.elevation
    assert "raised" in tokens.elevation
    assert "floating" in tokens.elevation
    assert "0 1px 3px" in tokens.elevation["subtle"].value

    css_vars = token_service.to_css_variables("default")
    assert "--nexus-color-primary: #002244;" in css_vars
    assert "--nexus-elevation-subtle: 0 1px 3px" in css_vars
    assert "--nexus-elevation-raised: 0 4px 12px" in css_vars


def test_composable_pattern_anatomy():
    """Verify PatternAnatomy validates slot composition and anti-slop rules."""
    anatomy = PatternAnatomy(
        pattern_id="operations_dashboard",
        title="Operations 360 Dashboard",
        description="High-density executive operational cockpit",
        category="dashboard",
        slots=[
            PatternSlot(
                slot_id="header_slot",
                name="Header & Actions",
                description="Single H1 with context breadcrumb and time filters",
                recommended_primitives=["NexusPageHeader"],
            ),
            PatternSlot(
                slot_id="kpi_grid_slot",
                name="Key Metrics Grid",
                description="Financial KPIs with tabular figures",
                recommended_primitives=["StatCard"],
            ),
        ],
    )

    assert anatomy.pattern_id == "operations_dashboard"
    assert len(anatomy.slots) == 2
    assert ".nexus-kpi-card" in anatomy.applied_elevation_classes
    assert any("Exactly one <h1>" in rule for rule in anatomy.anti_slop_rules)


def test_brownfield_non_destructive_injection():
    """Verify BrownfieldService safely injects tokens, primitives, and skills into a target project."""
    service = BrownfieldService()
    tmp_path = REPO_ROOT / ".cache" / "test_brownfield_tmp"
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)

    try:
        # Create dummy project
        pkg_json = tmp_path / "package.json"
        pkg_json.write_text(json.dumps({"name": "legacy-app", "dependencies": {"react": "^18.0.0"}}), encoding="utf-8")
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        res = service.inject_design_system(str(tmp_path), inject_tokens=True, inject_primitives=True, inject_skills=True)

        assert res["status"] == "success"
        # Check tokens CSS injected
        assert (tmp_path / "src" / "styles" / "nexus-tokens.css").exists()
        # Check primitives injected
        assert (tmp_path / "src" / "components" / "nexus" / "StatCard.tsx").exists()
        assert (tmp_path / "src" / "components" / "nexus" / "FilterToolbar.tsx").exists()
        assert (tmp_path / "src" / "components" / "nexus" / "EmptyState.tsx").exists()
        # Check skills injected
        assert (tmp_path / ".agents" / "skills" / "wbg-enterprise-rules.md").exists()
        assert (tmp_path / ".agents" / "skills" / "design-taste-frontend" / "SKILL.md").exists()
        # Check Copilot instructions injected
        assert (tmp_path / ".github" / "copilot-instructions.md").exists()
        # Check package.json dependencies updated non-destructively
        updated_pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
        assert "@wbg/nexus" in updated_pkg["dependencies"]
        assert "react" in updated_pkg["dependencies"]
    finally:
        import shutil
        if tmp_path.exists():
            shutil.rmtree(tmp_path)


def test_table_badges_exempt_from_overload_linter():
    """Verify standard tabular status badges in <td> are exempt from badge overload."""
    table_rows = "".join(
        f"<tr><td>Project {i}</td><td><span class='nexus-badge'>Active</span></td></tr>"
        for i in range(1, 15)
    )
    table_html = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head><title>Operations Table</title></head>
      <body>
        <main>
          <h1>Operations 360</h1>
          <table>
            <thead><tr><th>Project</th><th>Status</th></tr></thead>
            <tbody>{table_rows}</tbody>
          </table>
        </main>
      </body>
    </html>
    """
    parser = SemanticDOMInspector()
    parser.feed(table_html)
    assert parser.table_badge_count == 14
    assert parser.clustered_badge_count == 0
    slop_issues = parser.audit_design_slop()
    assert len(slop_issues) == 0, f"Table badges should not trigger slop, got: {slop_issues}"

    # Verify that clustered badges in a card still trigger overload
    clustered_html = """
    <!DOCTYPE html>
    <html lang="en">
      <head><title>Clustered Badges</title></head>
      <body>
        <main>
          <h1>Badges</h1>
          <div class="card">
            <span class="nexus-badge">Alpha</span>
            <span class="nexus-badge">Beta</span>
            <span class="nexus-badge">Gamma</span>
            <span class="nexus-badge">Delta</span>
            <span class="nexus-badge">Epsilon</span>
          </div>
        </main>
      </body>
    </html>
    """
    parser2 = SemanticDOMInspector()
    parser2.feed(clustered_html)
    assert parser2.clustered_badge_count == 5
    slop2 = parser2.audit_design_slop()
    assert any("[Badge Overload]" in issue for issue in slop2)


def test_brownfield_copilot_instructions_never_overwrites():
    """Verify BrownfieldService never overwrites existing team .github/copilot-instructions.md."""
    service = BrownfieldService()
    tmp_path = REPO_ROOT / ".cache" / "test_brownfield_overwrite_tmp"
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)

    try:
        pkg_json = tmp_path / "package.json"
        pkg_json.write_text(json.dumps({"name": "custom-team-app"}), encoding="utf-8")
        github_dir = tmp_path / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        custom_copilot = github_dir / "copilot-instructions.md"
        custom_content = "# Team Custom Rules\nDo not overwrite me."
        custom_copilot.write_text(custom_content, encoding="utf-8")

        res = service.inject_design_system(str(tmp_path), inject_tokens=False, inject_primitives=False, inject_skills=False)
        assert res["status"] == "success"
        # Verify custom content preserved 100%
        assert custom_copilot.read_text(encoding="utf-8") == custom_content
        assert ".github/copilot-instructions.md" not in res.get("created_files", [])
    finally:
        import shutil
        if tmp_path.exists():
            shutil.rmtree(tmp_path)



def test_gate2_anti_slop_linter_detects_slop():
    """Verify Gate 2 SemanticDOMInspector detects AI slop (inline style spaghetti, redundant headings, yellow banner)."""
    slop_html = """
    <!DOCTYPE html>
    <html lang="en">
      <head><title>Slop Dashboard</title></head>
      <body>
        <main>
          <!-- Slop 1: Stacked redundant headings -->
          <h1>Operations 360 Platform</h1>
          <h2>Operations 360 Platform Overview</h2>

          <!-- Slop 2: Yellow caution tape banner -->
          <div style="background-color: #ffcc00; height: 40px; display: flex; align-items: center;">
            OFFICIAL USE ONLY
          </div>

          <!-- Slop 3: Excessive raw inline style spaghetti -->
          <div style="display: flex; border: 1px solid #e0e0e0; padding: 16px; box-shadow: none;">
            <div style="display: block; border: 1px solid #ccc; padding: 8px;">Card 1</div>
            <div style="display: block; border: 1px solid #ccc; padding: 8px;">Card 2</div>
            <div style="display: block; border: 1px solid #ccc; padding: 8px;">Card 3</div>
            <div style="display: block; border: 1px solid #ccc; padding: 8px;">Card 4</div>
            <div style="display: block; border: 1px solid #ccc; padding: 8px;">Card 5</div>
          </div>

          <!-- Slop 4: Low contrast grey inline text -->
          <p style="color: #999999;">Faded secondary metadata</p>
        </main>
      </body>
    </html>
    """

    parser = SemanticDOMInspector()
    parser.feed(slop_html)
    slop_issues = parser.audit_design_slop()

    assert len(slop_issues) >= 3, f"Expected multiple slop issues, got {slop_issues}"
    issue_text = " ".join(slop_issues)
    assert "Stacked redundant headings" in issue_text
    assert "yellow caution-tape banner" in issue_text
    assert "Excessive raw inline styles" in issue_text
    assert "Low-contrast inline typography" in issue_text


def test_gate2_anti_slop_linter_passes_clean_design():
    """Verify Gate 2 SemanticDOMInspector gives 100% clean pass on disciplined Nexus code."""
    clean_html = """
    <!DOCTYPE html>
    <html lang="en">
      <head><title>Clean Dashboard</title></head>
      <body>
        <header class="nexus-page-header">
          <div class="nexus-page-header__meta">
            <span class="nexus-breadcrumb">Global Operations / East Asia</span>
            <h1 class="nexus-page-title">Operations 360</h1>
          </div>
          <div class="nexus-page-header__actions">
            <span class="nexus-classification-pill">OFFICIAL USE ONLY</span>
          </div>
        </header>

        <main>
          <section class="nexus-kpi-grid">
            <div class="nexus-kpi-card">
              <span class="nexus-kpi-label">Active Disbursements</span>
              <div class="nexus-kpi-value">$4,250,000</div>
              <div class="nexus-kpi-subtext">
                <span class="nexus-trend-up">↑ +12.4%</span>
                <span>vs previous 30 days</span>
              </div>
            </div>
          </section>

          <section class="nexus-data-section">
            <div class="nexus-card">
              <h2 class="nexus-section-title">Institutional Portfolio</h2>
              <div class="nexus-table-container">
                <table class="nexus-table">
                  <thead>
                    <tr><th>Project</th><th class="nexus-col-number">Budget</th></tr>
                  </thead>
                  <tbody>
                    <tr><td>Clean Energy Transition</td><td class="nexus-col-number">$12,000,000</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </main>
      </body>
    </html>
    """

    parser = SemanticDOMInspector()
    parser.feed(clean_html)
    a11y_violations = parser.finalize_violations()
    slop_issues = parser.audit_design_slop()

    assert len(a11y_violations) == 0, f"Expected 0 a11y violations, got {a11y_violations}"
    assert len(slop_issues) == 0, f"Expected 0 slop issues on clean design, got {slop_issues}"
