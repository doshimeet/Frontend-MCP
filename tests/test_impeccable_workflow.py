"""
Unit and integration tests for Phase 4: AI Agent Rules & Impeccable Integration.
Verifies the existence, YAML frontmatter, anti-slop rules, and FastMCP prompt hooks.
"""

import sys
from pathlib import Path
import pytest

# Add packages/mcp-server to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from server import mcp

REPO_ROOT = Path(__file__).resolve().parent.parent
IMPECCABLE_DIR = REPO_ROOT / ".agents" / "skills" / "impeccable"
WORKFLOW_FILE = REPO_ROOT / ".agents" / "workflows" / "build-ui.md"


def test_impeccable_skill_files_exist():
    """Verify all 5 Impeccable skill rule files exist in .agents/skills/impeccable/."""
    assert IMPECCABLE_DIR.exists(), f"Missing directory: {IMPECCABLE_DIR}"

    required_files = ["SKILL.md", "distill.md", "polish.md", "clarify.md", "harden.md"]
    for filename in required_files:
        filepath = IMPECCABLE_DIR / filename
        assert filepath.exists(), f"Missing Impeccable file: {filepath}"
        assert filepath.stat().st_size > 100, f"File {filepath} is unexpectedly empty"


def test_impeccable_skill_yaml_frontmatter():
    """Verify that SKILL.md contains required Antigravity YAML frontmatter."""
    skill_md = IMPECCABLE_DIR / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    assert content.startswith("---")
    assert "name: impeccable" in content
    assert "description:" in content


def test_master_workflow_structure():
    """Verify that .agents/workflows/build-ui.md defines the full 5-stage pipeline."""
    assert WORKFLOW_FILE.exists(), f"Missing workflow file: {WORKFLOW_FILE}"
    content = WORKFLOW_FILE.read_text(encoding="utf-8")

    assert "Stage 1: Ingestion & Architectural Planning" in content
    assert "Stage 2: Project Context & Safety Check" in content
    assert "Stage 3: Canonical Recipe Assembly" in content
    assert "Stage 4: The 4-Pass Impeccable Critique Loop" in content
    assert "Stage 5: Verification & Compilation" in content

    # Verify safety check requirement is documented
    assert "integrate_into_existing_app" in content
    assert "HALT EXECUTION IMMEDIATELY" in content


@pytest.mark.anyio
async def test_fastmcp_impeccable_critique_prompt():
    """Verify FastMCP impeccable_design_critique prompt renders with all 4 passes."""
    sample_candidate_tsx = "<button onClick={doSomething}>Click</button>"
    prompt_result = await mcp.get_prompt(
        "impeccable_design_critique",
        {"tsx_code": sample_candidate_tsx},
    )

    assert len(prompt_result.messages) == 1
    prompt_text = prompt_result.messages[0].content.text

    assert sample_candidate_tsx in prompt_text
    assert "/distill" in prompt_text
    assert "/polish" in prompt_text
    assert "/clarify" in prompt_text
    assert "/harden" in prompt_text
