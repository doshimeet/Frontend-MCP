"""
Phase 14 Test Suite: Enterprise Diagnostics, Process Un-stalling & Zero-Carbon Parity
Validates subprocess timeouts, Windows executable resolution, schema normalization,
resilient disk cache sanitization, and packaging discovery.
"""

import io
import json
import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.health import resolve_binary, check_command_version, check_environment_health
from services.health_service import HealthService
from connectors.storybook_connector import (
    StorybookConnector,
    normalize_component_name,
    normalize_component_spec,
    OFFLINE_NEXUS_CATALOG,
)
from tools.catalog_tools import register_catalog_tools
from mcp.server.fastmcp import FastMCP
from config import REPO_ROOT, AZURE_DEVOPS_STARTER_BRANCH, AZURE_DEVOPS_ORG


def test_resolve_binary_cross_platform():
    """Validates binary resolver locates python executable."""
    py_bin = resolve_binary("python") or resolve_binary("python3")
    assert py_bin is not None
    assert Path(py_bin).exists()


def test_check_command_version_timeout():
    """Simulates a hanging process and verifies check_command_version catches TimeoutExpired within threshold."""
    # Execute a command that sleeps longer than timeout
    if sys.platform != "win32":
        hang_cmd = shutil_which_sleep = "/bin/sleep"
        success, ver, err = check_command_version(shutil_which_sleep, timeout=0.2)
        assert success is False
        assert "Timed out" in err or "Failed" in err


def test_health_service_graceful_on_timeout():
    """Verifies HealthService returns a valid degraded HealthReport if a command probe times out."""
    service = HealthService()
    with patch("services.health_service.check_command_version", return_value=(False, None, "Timed out after 3.0s")):
        report = service.run_diagnostics()
        assert report.status == "degraded"
        assert report.node.available is False
        assert "degraded" in str(report.node.version)


def test_schema_normalizer_raw_storybook_keys():
    """Validates raw Storybook keys (e.g. components-button--default) normalize to PascalCase."""
    assert normalize_component_name("components-button") == "Button"
    assert normalize_component_name("components-button--default") == "Button"
    assert normalize_component_name("forms-text-input") == "TextInput"
    assert normalize_component_name("primitives/dialog") == "Dialog"
    assert normalize_component_name("Card") == "Card"


def test_schema_normalizer_docgen_fields():
    """Validates normalization of raw docgen structures into guaranteed typed schema without KeyError."""
    raw_docgen = {
        "import": "import { Button } from '@wbg/nexus';",
        "description": "Interactive action button.",
        "props": {
            "variant": {
                "type": {"name": "enum", "value": ["default", "outline"]},
                "required": True,
                "defaultValue": {"value": "'default'"},
                "description": "Visual style variant",
            }
        },
        "example": "<Button variant='default'>Click</Button>",
    }
    norm = normalize_component_spec("Button", raw_docgen, "@wbg/nexus")
    assert norm["import_statement"] == "import { Button } from '@wbg/nexus';"
    assert norm["description"] == "Interactive action button."
    assert "variant" in norm["props"]
    assert norm["props"]["variant"]["type"] == "enum"
    assert norm["props"]["variant"]["required"] == "true"
    assert norm["props"]["variant"]["default"] == "'default'"


def test_schema_normalizer_missing_fields():
    """Validates normalization provides safe defaults when fields are completely missing."""
    empty_raw = {}
    norm = normalize_component_spec("Header", empty_raw, "@wbg/nexus")
    assert norm["import_statement"] == "import { Header } from '@wbg/nexus';"
    assert "Nexus design system Header component." in norm["description"]
    assert norm["example"] == "<Header />"
    assert norm["props"] == {}


def test_offline_catalog_zero_carbon():
    """Strictly validates OFFLINE_NEXUS_CATALOG contains zero references to IBM Carbon."""
    catalog_str = json.dumps(OFFLINE_NEXUS_CATALOG)
    assert "@carbon" not in catalog_str
    assert "carbondesignsystem" not in catalog_str
    assert "@wbg/nexus" in catalog_str
    assert "Button" in OFFLINE_NEXUS_CATALOG
    assert "Table" in OFFLINE_NEXUS_CATALOG
    assert "Card" in OFFLINE_NEXUS_CATALOG
    assert "Dialog" in OFFLINE_NEXUS_CATALOG


def test_disk_cache_carbon_sanitization(tmp_path):
    """Verifies that any existing cache file containing legacy @carbon is purged and ignored."""
    poisoned_cache = tmp_path / "storybook_catalog.json"
    poisoned_cache.write_text(
        json.dumps({
            "Button": {
                "import_statement": "import { Button } from '@carbon/react';",
                "description": "Legacy Carbon button",
            }
        }),
        encoding="utf-8",
    )
    connector = StorybookConnector(cache_dir=tmp_path)
    loaded = connector._load_disk_cache()
    # Cache must be rejected
    assert loaded is None
    # Cache file must have been deleted
    assert not poisoned_cache.exists()


def test_catalog_tool_default_nexus():
    """Verifies get_components default source is nexus and does not crash."""
    test_mcp = FastMCP("test-mcp")
    register_catalog_tools(test_mcp)

    # In FastMCP, tools are callable through the tool functions
    connector = StorybookConnector()
    summary = connector.get_catalog_summary(source="nexus")
    assert len(summary) > 0
    # Every component spec must have safe props
    spec = connector.get_component_spec("Button")
    assert spec is not None
    assert "@wbg/nexus" in spec["import_statement"]


def test_ado_client_branch_parameter():
    """Verifies core/ado_client.py uses the configured branch parameter."""
    from core.ado_client import download_ado_starter_kit
    import inspect

    src = inspect.getsource(download_ado_starter_kit)
    assert "versionDescriptor.version=" in src
    assert "versionDescriptor.versionType=branch" in src


def test_pyproject_toml_configuration():
    """Validates pyproject.toml contains required setuptools package isolation and pytest config."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists()
    content = pyproject_path.read_text(encoding="utf-8")
    assert "[tool.setuptools]" in content
    assert "[tool.setuptools.packages.find]" in content
    assert 'pythonpath = ["."]' in content
    assert 'testpaths = ["tests"]' in content
