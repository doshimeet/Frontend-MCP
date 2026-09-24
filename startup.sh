#!/bin/bash
# ==============================================================================
# Azure App Service Linux Startup Script
# Enterprise FastMCP Server
# ==============================================================================

set -e

PORT="${PORT:-8000}"
HOST="${MCP_HOST:-0.0.0.0}"
export MCP_MODE="${MCP_MODE:-uvicorn}"

echo "[startup] Booting Enterprise FastMCP Server on ${HOST}:${PORT} (Mode: ${MCP_MODE})..."

# Launch server with python server.py
exec python server.py
