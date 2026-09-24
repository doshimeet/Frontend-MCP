"""
Unit tests for the environment health check diagnostic module.
"""

import sys
from pathlib import Path

# Add packages/mcp-server to sys.path
SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from core.health import check_environment_health, find_system_edge_browser


def test_environment_health_returns_valid_dict():
    result = check_environment_health()
    assert isinstance(result, dict)
    assert "status" in result
    assert "system" in result
    assert "runtimes" in result
    assert "browser_automation" in result
    assert "enterprise_auth" in result


def test_node_runtime_detected():
    result = check_environment_health()
    node_info = result["runtimes"].get("node", {})
    assert node_info.get("available") is True
    assert "version" in node_info


def test_npm_runtime_detected():
    result = check_environment_health()
    npm_info = result["runtimes"].get("npm", {})
    assert npm_info.get("available") is True
    assert "version" in npm_info
