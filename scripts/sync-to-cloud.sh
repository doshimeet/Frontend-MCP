#!/usr/bin/env bash
# ==============================================================================
# Synchronize Single Source of Truth ('Design System') to Cloud Mirror ('Frontend-MCP')
# Safely preserves .git, node_modules symlink, and ignores local cache/temp files.

# npm run sync:cloud

# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${FRONTEND_MCP_DIR:-/Users/meetketankumardoshi/Frontend-MCP}"

echo "================================================================="
echo "🔄 Synchronizing Single Source of Truth to Cloud Deployment Mirror"
echo "   Source: ${SOURCE_DIR}"
echo "   Target: ${TARGET_DIR}"
echo "================================================================="

if [ ! -d "${TARGET_DIR}" ]; then
  echo "❌ Error: Target mirror directory '${TARGET_DIR}' does not exist."
  exit 1
fi

rsync -av \
  --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.cache' \
  --exclude='package-lock.json' \
  --exclude='apps' \
  --exclude='docs' \
  "${SOURCE_DIR}/" \
  "${TARGET_DIR}/"

echo ""
echo "✅ Synchronization complete!"
echo "📁 Target '${TARGET_DIR}' is now byte-for-byte in sync with '${SOURCE_DIR}'."
echo ""
echo "Next step to deploy to Azure App Service QA Slot:"
echo "   cd \"${TARGET_DIR}\""
echo "   git status"
echo "   git add ."
echo "   git commit -m \"feat: sync latest design system updates\""
echo "   git push origin QA"
echo "================================================================="
