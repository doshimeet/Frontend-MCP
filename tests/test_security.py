"""
Unit tests for Path Sandboxing & Security Enforcement.
"""

import sys
from pathlib import Path
import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent / "packages" / "mcp-server"
sys.path.insert(0, str(SERVER_DIR))

from services.security_service import SecurityService, SecurityException
from services.scaffolding_service import ScaffoldingService


def test_security_blocks_empty_path():
    sec = SecurityService()
    with pytest.raises(SecurityException):
        sec.sanitize_and_validate_path("")


def test_security_blocks_system_etc():
    sec = SecurityService()
    with pytest.raises(SecurityException, match="protected system directory"):
        sec.sanitize_and_validate_path("/etc/passwd")


def test_security_blocks_system_root_bin():
    sec = SecurityService()
    with pytest.raises(SecurityException, match="protected system directory"):
        sec.sanitize_and_validate_path("/bin/sh")


def test_security_allows_safe_relative_workspace_path():
    sec = SecurityService(allowed_root=Path("/Users/user/workspace"))
    resolved = sec.sanitize_and_validate_path("apps/new-portal")
    assert str(resolved).endswith("apps/new-portal")


def test_scaffolding_blocks_traversal_gracefully():
    scaffolder = ScaffoldingService()
    result = scaffolder.scaffold("malicious-app", "/etc/malicious")
    assert result.success is False
    assert result.source == "security_blocked"
    assert "protected system directory" in result.error_message
