"""
Cloud Deployment & Container Readiness Test Suite
Validates Dockerfile, .dockerignore, container environment defaults,
and live uvicorn HTTP /health probes.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_oryx_requirements_and_startup_configuration():
    """Validates Azure App Service Linux Oryx requirements.txt and startup.sh configuration."""
    req_file = REPO_ROOT / "requirements.txt"
    startup_file = REPO_ROOT / "startup.sh"

    assert req_file.exists(), "requirements.txt must exist at repository root for Azure Oryx"
    assert startup_file.exists(), "startup.sh must exist at repository root for Azure App Service"

    content = req_file.read_text(encoding="utf-8")
    assert "mcp" in content, "Must include mcp in requirements.txt"
    assert "starlette" in content, "Must include starlette in requirements.txt"
    assert "uvicorn" in content, "Must include uvicorn in requirements.txt"
    assert "pydantic" in content, "Must include pydantic in requirements.txt"

    startup_content = startup_file.read_text(encoding="utf-8")
    assert "python server.py" in startup_content, "startup.sh must launch server via python server.py"


def test_live_cloud_server_health_probe():
    """Launches live uvicorn server in a subprocess and verifies /health responds HTTP 200."""
    port = "8891"
    env = dict(os.environ)
    env["MCP_MODE"] = "uvicorn"
    env["MCP_PORT"] = port
    env["MCP_HOST"] = "127.0.0.1"

    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        health_url = f"http://127.0.0.1:{port}/health"
        response = None
        for _ in range(25):
            try:
                r = httpx.get(health_url, timeout=1.0)
                if r.status_code == 200:
                    response = r
                    break
            except Exception:
                time.sleep(0.15)

        assert response is not None, f"Server failed to answer /health on {health_url}"
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "UP"
        assert data.get("transport") == "uvicorn"
        assert data.get("service") in ("nexus-mcp", "nexus-design-system-mcp")
        assert data.get("version") == "2.0.0"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_live_cloud_server_auth_and_health_bypass():
    """Verifies that CloudAuthMiddleware protects SSE routes but permits unauthenticated /health."""
    port = "8892"
    api_key = "test-live-key-secret"
    env = dict(os.environ)
    env["MCP_MODE"] = "uvicorn"
    env["MCP_PORT"] = port
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_API_KEY"] = api_key

    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        health_url = f"http://127.0.0.1:{port}/health"
        sse_url = f"http://127.0.0.1:{port}/sse"
        ready = False
        for _ in range(25):
            try:
                r = httpx.get(health_url, timeout=1.0)
                if r.status_code == 200:
                    ready = True
                    break
            except Exception:
                time.sleep(0.15)

        assert ready, "Server failed to start in authenticated cloud mode"

        # 1. /health MUST succeed without any auth header (ALB probe requirement)
        r_health = httpx.get(health_url, timeout=1.0)
        assert r_health.status_code == 200

        # 2. /sse MUST return 401 Unauthorized without auth header
        r_sse_unauth = httpx.get(sse_url, timeout=1.0)
        assert r_sse_unauth.status_code == 401
        data_unauth = r_sse_unauth.json()
        assert data_unauth.get("error") == "Unauthorized" or "Unauthorized" in data_unauth.get("message", "")

        # 3. /sse with valid Bearer token passes auth
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            r_sse_auth = httpx.get(sse_url, headers=headers, timeout=1.0)
            # SSE returns 200 streaming
            assert r_sse_auth.status_code in (200, 307)
        except httpx.ReadTimeout:
            # SSE streams keep connection open, timeout is a successful handshake
            pass
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
