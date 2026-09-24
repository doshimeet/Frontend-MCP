"""
Unit tests for Python FastMCP server tools and Clean Architecture services.
"""

import sys
from pathlib import Path

# Add packages/mcp-server to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from services.token_service import TokenService
from connectors.storybook_connector import OFFLINE_CARBON_CATALOG
from services.requirements_service import RequirementsService
from core.router_detector import detect_project_router


def test_token_service_retrieval():
    svc = TokenService()
    tokens = svc.get_theme_tokens("default")
    assert "primary" in tokens.color
    assert tokens.color["primary"].value == "#002244"
    assert "md" in tokens.spacing


def test_storybook_connector_catalog():
    assert "Button" in OFFLINE_CARBON_CATALOG
    assert "DataTable" in OFFLINE_CARBON_CATALOG
    assert "Modal" in OFFLINE_CARBON_CATALOG
    assert "TextInput" in OFFLINE_CARBON_CATALOG
    assert "Tag" in OFFLINE_CARBON_CATALOG
    assert "SkeletonText" in OFFLINE_CARBON_CATALOG

    button = OFFLINE_CARBON_CATALOG["Button"]
    assert "props" in button
    assert "kind" in button["props"]
    assert "example" in button


def test_requirements_service_planning():
    svc = RequirementsService()
    prd = "Build an executive analytics dashboard with KPI metrics, performance charts, and an audit table."
    blueprint = svc.plan_architecture(prd, "enterprise-dark")

    assert len(blueprint.recommended_routes) >= 1
    paths = [r.path for r in blueprint.recommended_routes]
    assert "/" in paths
    assert blueprint.target_theme == "enterprise-dark"


def test_router_detector_fallback():
    # Non-existent path returns unknown
    res = detect_project_router(Path("/non/existent/path/for/testing"))
    assert res["router_type"] == "unknown"
